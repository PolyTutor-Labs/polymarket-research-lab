"""Database session helper tests. Does not change research queries."""

from __future__ import annotations

from watchdog.core.config import Settings
from watchdog.core.paths import resolve_database_url
from watchdog.db.session import build_engine, build_session_factory


def test_build_engine_resolves_relative_sqlite_url() -> None:
    settings = Settings(_env_file=None, database_url="sqlite:///watchdog.db")
    engine = build_engine(settings)
    try:
        expected = resolve_database_url("sqlite:///watchdog.db")
        database = engine.url.database or ""
        assert database.endswith("watchdog.db")
        assert expected.endswith(database.replace("\\", "/"))
    finally:
        engine.dispose()


def test_build_engine_memory_sqlite_unchanged() -> None:
    settings = Settings(_env_file=None, database_url="sqlite:///:memory:")
    engine = build_engine(settings)
    assert ":memory:" in str(engine.url)
    engine.dispose()


def test_session_factory_binds_to_engine() -> None:
    settings = Settings(_env_file=None, database_url="sqlite:///:memory:")
    engine = build_engine(settings)
    factory = build_session_factory(engine)
    session = factory()
    try:
        assert session.bind is engine
    finally:
        session.close()
        engine.dispose()
