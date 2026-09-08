#!/usr/bin/env python3
"""Scan git-tracked files for committed secrets.

Reports only path, line number, and rule id. Never prints secret contents.
Exit codes: 0 clean, 1 findings, 2 scanner error.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

BINARY_SUFFIXES = {
    ".pdf",
    ".parquet",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".ico",
    ".woff",
    ".woff2",
    ".so",
    ".dylib",
    ".bin",
    ".exe",
    ".whl",
    ".zip",
    ".gz",
    ".tgz",
    ".xz",
}

SKIP_DIR_NAMES = {".git", ".venv", "venv", "__pycache__", ".mypy_cache", ".pytest_cache", ".ruff_cache"}

PLACEHOLDER_VALUES = {
    "",
    "none",
    "null",
    "undefined",
    "false",
    "true",
    "dummy",
    "changeme",
    "changeme!",
    "placeholder",
    "your-key-here",
    "your_key_here",
    "xxx",
    "xxxx",
    "todo",
    "test-key",
    "mani-key",
    "sk-ant",
}

SECRET_ASSIGN_NAMES = re.compile(
    r"^(?:[A-Z][A-Z0-9_]*_)?(?:API_KEY|CLIENT_SECRET|SECRET|TOKEN|PASSWORD|PASSWD|PRIVATE_KEY|BEARER|WEBHOOK_URL)$"
)

# High-confidence value shapes. Patterns must not require printing the match.
RULES: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("pem_private_key", re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----")),
    ("openai_api_key", re.compile(r"sk-(?:proj-)?[A-Za-z0-9_-]{20,}")),
    ("anthropic_api_key", re.compile(r"sk-ant-[A-Za-z0-9_-]{20,}")),
    ("github_token", re.compile(r"(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}")),
    ("github_fine_grained_pat", re.compile(r"github_pat_[A-Za-z0-9_]{20,}")),
    ("slack_token", re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}")),
    ("aws_access_key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("google_api_key", re.compile(r"AIza[0-9A-Za-z_-]{35}")),
    ("telegram_bot_token", re.compile(r"\b\d{8,10}:[A-Za-z0-9_-]{35}\b")),
    ("discord_webhook", re.compile(r"discord(?:app)?\.com/api/webhooks/\d+/[A-Za-z0-9_-]+")),
    ("slack_webhook", re.compile(r"hooks\.slack\.com/services/[A-Za-z0-9/_-]+")),
    ("jwt", re.compile(r"eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}")),
    (
        "wallet_private_key",
        re.compile(
            r"(?i)(?:private[_-]?key|wallet[_-]?key)\s*[:=]\s*['\"]?(?:0x)?[a-f0-9]{64}['\"]?"
        ),
    ),
)

ENV_ASSIGN = re.compile(
    r"""(?x)
    ^\s*(?:export\s+)?
    (?P<name>[A-Za-z_][A-Za-z0-9_]*)
    \s*=\s*
    (?P<value>.+?)\s*$
    """
)


@dataclass(frozen=True, slots=True)
class Finding:
    path: str
    line: int
    rule_id: str


def _repo_root(explicit: Path | None) -> Path:
    if explicit is not None:
        return explicit.resolve()
    return Path(__file__).resolve().parents[2]


def _is_placeholder(value: str) -> bool:
    stripped = value.strip().strip("\"'").strip()
    if stripped.lower() in PLACEHOLDER_VALUES:
        return True
    if stripped.startswith("<") and stripped.endswith(">") and len(stripped) > 2:
        return True
    if stripped.startswith("${{") and "secrets." in stripped:
        return True
    if stripped.startswith("${") or stripped.startswith("$"):
        return True
    return False


def _looks_like_secret_assignment(name: str, value: str) -> bool:
    # Env-style assignments only (OPENAI_API_KEY=...). Ignore Python locals
    # such as yes_token = ... that are market identifiers, not credentials.
    if name != name.upper() or not SECRET_ASSIGN_NAMES.search(name):
        return False
    if _is_placeholder(value):
        return False
    # Ignore documented empty / commented examples and obvious non-secrets.
    if value.startswith("#"):
        return False
    if re.fullmatch(r"[\w./:-]+", value) and value.lower() in {
        "watchdog/0.1",
        "sqlite:///watchdog.db",
    }:
        return False
    # Require some entropy so names like LOG_LEVEL=INFO are not adjacent false hits.
    compact = re.sub(r"[^A-Za-z0-9]", "", value)
    return len(compact) >= 12


def scan_text(rel_path: str, text: str) -> list[Finding]:
    findings: list[Finding] = []
    for lineno, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.rstrip("\n")
        for rule_id, pattern in RULES:
            if pattern.search(line):
                findings.append(Finding(path=rel_path, line=lineno, rule_id=rule_id))
                break
        else:
            env_match = ENV_ASSIGN.match(line)
            if env_match and _looks_like_secret_assignment(
                env_match.group("name"), env_match.group("value")
            ):
                findings.append(Finding(path=rel_path, line=lineno, rule_id="secret_assignment"))
    return findings


def _tracked_files(root: Path) -> list[Path]:
    try:
        completed = subprocess.run(
            ["git", "ls-files", "-z"],
            cwd=root,
            check=True,
            capture_output=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise RuntimeError("unable to list git-tracked files") from exc

    files: list[Path] = []
    for raw in completed.stdout.split(b"\0"):
        if not raw:
            continue
        files.append(root / raw.decode("utf-8", errors="surrogateescape"))
    return files


def _should_skip(path: Path) -> bool:
    if any(part in SKIP_DIR_NAMES for part in path.parts):
        return True
    if path.suffix.lower() in BINARY_SUFFIXES:
        return True
    return False


def _read_text_file(path: Path) -> str | None:
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if b"\x00" in data:
        return None
    return data.decode("utf-8", errors="replace")


def scan_paths(root: Path, paths: Iterable[Path]) -> list[Finding]:
    findings: list[Finding] = []
    for path in paths:
        if _should_skip(path):
            continue
        if not path.is_file():
            continue
        text = _read_text_file(path)
        if text is None:
            continue
        rel = path.relative_to(root).as_posix()
        findings.extend(scan_text(rel, text))
    return findings


def format_report(findings: list[Finding]) -> str:
    if not findings:
        return "secret scan: clean (0 findings)"
    lines = [f"secret scan: {len(findings)} finding(s)"]
    for finding in findings:
        lines.append(f"{finding.path}:{finding.line} [{finding.rule_id}]")
    lines.append("values omitted")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scan tracked files for committed secrets")
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Repository root (default: inferred from this script)",
    )
    args = parser.parse_args(argv)

    try:
        root = _repo_root(args.root)
        findings = scan_paths(root, _tracked_files(root))
    except Exception as exc:  # noqa: BLE001 - fail closed without dumping internals
        print(f"secret scan: error ({type(exc).__name__})", file=sys.stderr)
        return 2

    print(format_report(findings))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
