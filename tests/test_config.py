"""Configuration loading tests. Does not change research defaults or formulas."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from watchdog.core.config import Settings, get_settings
from watchdog.core.paths import data_dir


def test_safe_runtime_defaults_when_env_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (
        "ENABLE_LIVE_TRADING",
        "WATCHDOG_ENV",
        "ROUTER_PROVIDER",
        "EXECUTOR_PROVIDER",
        "DATABASE_URL",
        "BECKER_DATASET_PATH",
    ):
        monkeypatch.delenv(name, raising=False)

    settings = Settings(_env_file=None)

    assert settings.enable_live_trading is False
    assert settings.watchdog_env == "dev"
    assert settings.router_provider == "mock"
    assert settings.executor_provider == "mock"
    assert settings.database_url == "sqlite:///watchdog.db"
    assert settings.becker_dataset_path == str(data_dir() / "becker")


def test_settings_read_environment_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WATCHDOG_ENV", "test")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("ENABLE_LIVE_TRADING", "false")

    settings = Settings(_env_file=None)

    assert settings.watchdog_env == "test"
    assert settings.log_level == "DEBUG"
    assert settings.enable_live_trading is False


def test_unknown_settings_fields_are_ignored() -> None:
    settings = Settings(_env_file=None, totally_unknown_future_flag="ignored")
    assert not hasattr(settings, "totally_unknown_future_flag")


def test_invalid_watchdog_env_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, watchdog_env="staging")


def test_get_settings_is_cached() -> None:
    get_settings.cache_clear()
    first = get_settings()
    second = get_settings()
    assert first is second

    get_settings.cache_clear()
    third = get_settings()
    assert third is not first
