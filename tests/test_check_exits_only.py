from __future__ import annotations

import importlib.util
import sys

from watchdog.core.paths import repo_root
from watchdog.db.models import Market, Trade

SCRIPT_PATH = repo_root() / "scripts" / "check_exits_only.py"


def _load_script():
    spec = importlib.util.spec_from_file_location("check_exits_only", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _trade(*, order_id: str) -> Trade:
    return Trade(
        market_id=1,
        side="YES",
        size=10.0,
        entry_price=0.5,
        kelly_fraction=0.1,
        order_id=order_id,
        is_paper=True,
        status="open",
    )


def test_infer_platform_prefers_order_id_prefix() -> None:
    script = _load_script()
    market = Market(slug="test-market", question="Test?", domain="other")
    assert script._infer_platform(_trade(order_id="paper-polymarket-test-market-1"), market) == "polymarket"


def test_infer_platform_prefers_manifold_order_id_prefix() -> None:
    script = _load_script()
    market = Market(slug="test-market", question="Test?", domain="other")
    assert script._infer_platform(_trade(order_id="paper-manifold-test-market-1"), market) == "manifold"


def test_infer_platform_falls_back_to_condition_id() -> None:
    script = _load_script()
    market = Market(
        slug="test-market",
        question="Test?",
        domain="other",
        condition_id="0xcondition",
    )
    assert script._infer_platform(_trade(order_id="arb-yes-test-market-1"), market) == "polymarket"


def test_infer_platform_falls_back_to_manifold_without_condition_id() -> None:
    script = _load_script()
    market = Market(slug="test-market", question="Test?", domain="other")
    assert script._infer_platform(_trade(order_id="arb-yes-test-market-1"), market) == "manifold"
