"""Shared pytest fixtures. Isolates cached settings between tests."""

from __future__ import annotations

from collections.abc import Iterator

import pytest

from watchdog.core.config import get_settings


@pytest.fixture(autouse=True)
def _clear_settings_cache() -> Iterator[None]:
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
