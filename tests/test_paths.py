from __future__ import annotations

from pathlib import Path

from watchdog.core.paths import (
    data_dir,
    log_dir,
    output_dir,
    repo_root,
    resolve_database_url,
    resolve_user_path,
    seed_sql_candidates,
    sqlite_file_path,
)


def test_repo_root_points_at_checkout() -> None:
    root = repo_root()
    assert (root / "pyproject.toml").is_file()
    assert (root / "src" / "watchdog").is_dir()


def test_data_dir_defaults_to_repo_data() -> None:
    assert data_dir() == repo_root() / "data"


def test_output_dir_defaults_to_repo_outputs() -> None:
    assert output_dir() == repo_root() / "outputs"


def test_log_dir_defaults_to_repo_logs() -> None:
    assert log_dir() == repo_root() / "logs"


def test_repo_root_env_override(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("POLY_RESEARCH_ROOT", str(tmp_path))
    assert repo_root() == tmp_path.resolve()


def test_log_dir_env_override(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("POLY_RESEARCH_LOG_DIR", str(tmp_path / "logs"))
    assert log_dir() == (tmp_path / "logs").resolve()


def test_data_dir_env_override(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("POLY_RESEARCH_DATA_DIR", str(tmp_path))
    assert data_dir() == tmp_path.resolve()


def test_output_dir_env_override(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("POLY_RESEARCH_OUTPUT_DIR", str(tmp_path / "out"))
    assert output_dir() == (tmp_path / "out").resolve()


def test_resolve_user_path_relative_uses_repo_root() -> None:
    resolved = resolve_user_path("data/example.csv")
    assert resolved == (repo_root() / "data" / "example.csv").resolve()


def test_resolve_user_path_absolute_unchanged(tmp_path: Path) -> None:
    target = tmp_path / "abs.csv"
    assert resolve_user_path(target) == target


def test_resolve_user_path_relative_to_explicit_base(tmp_path: Path) -> None:
    resolved = resolve_user_path("nested/file.csv", base=tmp_path)
    assert resolved == (tmp_path / "nested" / "file.csv").resolve()


def test_resolve_database_url_relative_sqlite() -> None:
    resolved = resolve_database_url("sqlite:///watchdog.db")
    expected = (repo_root() / "watchdog.db").resolve()
    assert resolved == f"sqlite:///{expected.as_posix()}"


def test_resolve_database_url_memory_unchanged() -> None:
    assert resolve_database_url("sqlite:///:memory:") == "sqlite:///:memory:"


def test_resolve_database_url_absolute_unchanged() -> None:
    url = "sqlite:////var/tmp/research.db"
    assert resolve_database_url(url) == url


def test_resolve_database_url_non_sqlite_unchanged() -> None:
    url = "postgresql://user:pass@localhost/research"
    assert resolve_database_url(url) == url


def test_resolve_database_url_empty_sqlite_rest_unchanged() -> None:
    assert resolve_database_url("sqlite:///") == "sqlite:///"


def test_sqlite_file_path_default_when_env_unset(monkeypatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    expected = (repo_root() / "watchdog.db").resolve()
    assert sqlite_file_path() == expected


def test_seed_sql_candidates_include_github_workspace(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("GITHUB_WORKSPACE", str(tmp_path))
    candidates = seed_sql_candidates()
    assert tmp_path / "db" / "seed_data.sql" in candidates


def test_sqlite_file_path_honors_database_url(monkeypatch, tmp_path: Path) -> None:
    db = tmp_path / "custom.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db.as_posix()}")
    assert sqlite_file_path() == db


def test_seed_sql_candidates_are_repo_relative() -> None:
    candidates = seed_sql_candidates()
    assert repo_root() / "db" / "seed_data.sql" in candidates
    assert all("poly-what" not in str(path) for path in candidates)
    assert all(str(path).find("/" + "Users/") < 0 for path in candidates)


def test_tracked_sources_have_no_machine_specific_roots() -> None:
    """Regression: no developer-home or hardcoded CI checkout paths in code."""
    root = repo_root()
    skip_names = {"SECURITY_AUDIT.md", "test_paths.py"}
    forbidden = ("C:" + "\\Users\\", "/" + "Users/", "/" + "home/runner/")
    offenders: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix not in {".py", ".sh", ".yml", ".md", ".example"}:
            continue
        if any(part in {".git", ".venv", "outputs"} for part in path.parts):
            continue
        if path.name in skip_names:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if any(token in text for token in forbidden):
            offenders.append(str(path.relative_to(root)))
    assert offenders == []
