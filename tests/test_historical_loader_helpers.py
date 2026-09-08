"""Historical loader plumbing tests. Does not change backtest calculations."""

from __future__ import annotations

from pathlib import Path

import pytest

from watchdog.backtest.historical_loader import BeckerHistoricalLoader


def test_sql_identifier_quoting_is_deterministic() -> None:
    assert BeckerHistoricalLoader._q("price") == '"price"'
    assert BeckerHistoricalLoader._q('col"name') == '"col""name"'


def test_missing_dataset_path_raises(tmp_path: Path) -> None:
    missing = tmp_path / "absent-dataset"
    with pytest.raises(FileNotFoundError, match="Becker dataset path not found"):
        BeckerHistoricalLoader(missing)
