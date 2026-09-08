from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

from watchdog.core.paths import repo_root

SCANNER_PATH = repo_root() / "scripts" / "security" / "check_secrets.py"


def _load_scanner():
    spec = importlib.util.spec_from_file_location("check_secrets", SCANNER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_repo_tracked_scan_is_clean() -> None:
    scanner = _load_scanner()
    findings = scanner.scan_paths(repo_root(), scanner._tracked_files(repo_root()))
    assert findings == []


def test_cli_on_repo_exits_clean() -> None:
    completed = subprocess.run(
        [sys.executable, str(SCANNER_PATH)],
        cwd=repo_root(),
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0
    assert "clean" in completed.stdout
    assert completed.stderr == ""


def test_detects_pem_header_without_printing_material() -> None:
    scanner = _load_scanner()
    header = "-----BEGIN " + "RSA PRIVATE KEY-----"
    secret_line = f"{header}\nMASKED_MATERIAL\n"
    findings = scanner.scan_text("unit.env", secret_line)
    assert [item.rule_id for item in findings] == ["pem_private_key"]
    report = scanner.format_report(findings)
    assert "unit.env:1 [pem_private_key]" in report
    assert header not in report
    assert "MASKED_MATERIAL" not in report


def test_detects_openai_style_assignment_without_printing_value() -> None:
    scanner = _load_scanner()
    value = "sk-" + ("x" * 40)
    findings = scanner.scan_text("local.env", f"OPENAI_API_KEY={value}\n")
    assert findings
    assert findings[0].rule_id in {"openai_api_key", "secret_assignment"}
    report = scanner.format_report(findings)
    assert value not in report


def test_ignores_python_market_token_locals() -> None:
    scanner = _load_scanner()
    text = "\n".join(
        [
            "yes_token = clob_ids[0] if clob_ids else None",
            "token = market.yes_token_id or market.slug",
            "n8n_webhook_url=settings.n8n_webhook_url",
        ]
    )
    assert scanner.scan_text("src/watchdog/example.py", text) == []


def test_ignores_empty_and_placeholder_assignments() -> None:
    scanner = _load_scanner()
    text = "\n".join(
        [
            "OPENAI_API_KEY=",
            "TELEGRAM_BOT_TOKEN=<token>",
            "ANTHROPIC_API_KEY=${{ secrets.ANTHROPIC_API_KEY }}",
            "MANIFOLD_API_KEY=test-key",
        ]
    )
    assert scanner.scan_text(".env.example", text) == []


def test_skips_binary_suffixes(tmp_path: Path) -> None:
    scanner = _load_scanner()
    blob = tmp_path / "notes.parquet"
    blob.write_bytes(b"PK\x00not-a-secret")
    assert scanner.scan_paths(tmp_path, [blob]) == []
