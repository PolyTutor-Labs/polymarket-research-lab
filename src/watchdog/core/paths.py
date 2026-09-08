"""Portable filesystem roots for the research repository.

Defaults are repo-relative so the same checkout works on any machine.
Override with environment variables when data or outputs live elsewhere.

This module only resolves locations. It does not change research calculations.
"""
from __future__ import annotations

import os
from pathlib import Path

ENV_ROOT = "POLY_RESEARCH_ROOT"
ENV_DATA_DIR = "POLY_RESEARCH_DATA_DIR"
ENV_OUTPUT_DIR = "POLY_RESEARCH_OUTPUT_DIR"
ENV_LOG_DIR = "POLY_RESEARCH_LOG_DIR"


def repo_root() -> Path:
    """Return the repository root (directory containing pyproject.toml)."""
    override = os.environ.get(ENV_ROOT, "").strip()
    if override:
        return Path(override).expanduser().resolve()

    here = Path(__file__).resolve()
    for candidate in (here, *here.parents):
        if (candidate / "pyproject.toml").is_file():
            return candidate
    return here.parents[3]


def _env_or_default(name: str, default: Path) -> Path:
    raw = os.environ.get(name, "").strip()
    if raw:
        return Path(raw).expanduser().resolve()
    return default


def data_dir() -> Path:
    """Research inputs (CSVs, parquet, price history). Does not move datasets."""
    return _env_or_default(ENV_DATA_DIR, repo_root() / "data")


def output_dir() -> Path:
    """Generated results, reports, and cache-style artifacts."""
    return _env_or_default(ENV_OUTPUT_DIR, repo_root() / "outputs")


def log_dir() -> Path:
    """Local log files. Never a user-specific absolute path."""
    return _env_or_default(ENV_LOG_DIR, repo_root() / "logs")


def resolve_user_path(path: str | Path, *, base: Path | None = None) -> Path:
    """Resolve a path. Relative values are interpreted from *base* or repo root."""
    parsed = Path(path).expanduser()
    if parsed.is_absolute():
        return parsed
    root = base if base is not None else repo_root()
    return (root / parsed).resolve()


def seed_sql_candidates() -> list[Path]:
    """Ordered locations for db/seed_data.sql. No machine-specific fallbacks."""
    candidates: list[Path] = []

    def _add(path: Path) -> None:
        if path not in candidates:
            candidates.append(path)

    github_workspace = os.environ.get("GITHUB_WORKSPACE", "").strip()
    if github_workspace:
        _add(Path(github_workspace) / "db" / "seed_data.sql")
    _add(repo_root() / "db" / "seed_data.sql")
    _add(Path.cwd() / "db" / "seed_data.sql")
    return candidates


def resolve_database_url(url: str) -> str:
    """Resolve relative SQLite file URLs against the repo root.

    Leaves :memory:, absolute paths, and non-SQLite URLs unchanged.
    """
    if ":memory:" in url:
        return url
    prefix = "sqlite:///"
    if not url.startswith(prefix):
        return url
    rest = url[len(prefix) :]
    if not rest:
        return url
    location = Path(rest)
    if location.is_absolute():
        return url
    resolved = (repo_root() / rest).resolve()
    return f"sqlite:///{resolved.as_posix()}"


def sqlite_file_path() -> Path:
    """Path of the default SQLite research DB, honoring DATABASE_URL when set."""
    url = os.environ.get("DATABASE_URL", "").strip() or "sqlite:///watchdog.db"
    resolved = resolve_database_url(url)
    prefix = "sqlite:///"
    if resolved.startswith(prefix) and ":memory:" not in resolved:
        return Path(resolved[len(prefix) :])
    return repo_root() / "watchdog.db"
