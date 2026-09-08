"""Deterministic parser and payload-helper tests. No algorithm or dataset changes."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from watchdog.core.config import Settings
from watchdog.llm.executor import MockExecutorAgent, build_executor
from watchdog.llm.router import MockRouterAgent, build_router
from watchdog.llm.types import ExecutorDecision, RouterDecision
from watchdog.market_data.manifold_client import ManifoldClient
from watchdog.news.source_polymarket_volume import _safe_float
from watchdog.scripts.run_paper_trading import _extract_markets_payload, _parse_resolution_time


def test_safe_float_converts_or_defaults() -> None:
    assert _safe_float("1.5") == 1.5
    assert _safe_float(2) == 2.0
    assert _safe_float(None) == 0.0
    assert _safe_float("not-a-number") == 0.0


def test_extract_markets_payload_from_list() -> None:
    assert _extract_markets_payload([{"slug": "a"}, "skip"]) == [{"slug": "a"}]


def test_extract_markets_payload_from_known_keys() -> None:
    assert _extract_markets_payload({"markets": [{"slug": "a"}]}) == [{"slug": "a"}]
    assert _extract_markets_payload({"items": [{"slug": "b"}]}) == [{"slug": "b"}]
    assert _extract_markets_payload({"data": [{"slug": "c"}]}) == [{"slug": "c"}]


def test_extract_markets_payload_empty_or_unknown() -> None:
    assert _extract_markets_payload({}) == []
    assert _extract_markets_payload("nope") == []
    assert _extract_markets_payload(None) == []


def test_parse_resolution_time_none_and_aware_datetime() -> None:
    assert _parse_resolution_time(None) is None
    aware = datetime(2024, 1, 2, 3, 4, tzinfo=UTC)
    assert _parse_resolution_time(aware) is aware


def test_parse_resolution_time_naive_datetime_gets_utc() -> None:
    naive = datetime(2024, 1, 2, 3, 4)
    parsed = _parse_resolution_time(naive)
    assert parsed is not None
    assert parsed.tzinfo is UTC


def test_parse_resolution_time_epoch_seconds_and_millis() -> None:
    seconds = _parse_resolution_time(1_700_000_000)
    millis = _parse_resolution_time(1_700_000_000_000)
    assert seconds is not None
    assert millis is not None
    assert seconds.tzinfo is UTC
    assert millis.tzinfo is UTC
    assert abs((seconds - millis).total_seconds()) < 1


def test_manifold_to_float_and_normalize_outcome() -> None:
    assert ManifoldClient._to_float("3.25") == 3.25
    assert ManifoldClient._to_float("bad", default=1.5) == 1.5
    assert ManifoldClient._normalize_outcome("YES") == 1
    assert ManifoldClient._normalize_outcome("true") == 1
    assert ManifoldClient._normalize_outcome("no") == 0
    assert ManifoldClient._normalize_outcome("0") == 0
    assert ManifoldClient._normalize_outcome("maybe") is None
    assert ManifoldClient._normalize_outcome(None) is None


def test_manifold_parse_time_none_seconds_and_millis() -> None:
    assert ManifoldClient._parse_time(None) is None
    seconds = ManifoldClient._parse_time(1_700_000_000)
    millis = ManifoldClient._parse_time(1_700_000_000_000)
    assert seconds is not None
    assert millis is not None
    assert seconds.tzinfo is not None
    assert abs((seconds - millis).total_seconds()) < 1


def test_manifold_parse_time_iso_naive_is_utc() -> None:
    parsed = ManifoldClient._parse_time("2024-01-01T00:00:00")
    assert parsed is not None
    assert parsed.tzinfo is UTC


def test_manifold_infer_domain_keyword_and_fallback() -> None:
    assert ManifoldClient._infer_domain({"question": "Who wins the election?"}) == "politics"
    assert ManifoldClient._infer_domain({"question": "Bitcoin ETF approval"}) == "crypto"
    assert ManifoldClient._infer_domain({"question": "zzzz no keywords"}) == "other"


def test_manifold_to_market_model_clamps_probability() -> None:
    market = ManifoldClient._to_market_model(
        {
            "id": "m1",
            "slug": "example",
            "question": "Will it rain?",
            "probability": 1.7,
            "volume": "12.5",
        }
    )
    assert market.market_id == "m1"
    assert market.slug == "example"
    assert market.probability == 1.0
    assert market.volume == 12.5
    assert market.is_resolved is False


def test_router_decision_parses_valid_payload() -> None:
    decision = RouterDecision.model_validate(
        {
            "relevant": True,
            "market_slugs": ["btc"],
            "impact_direction": "up",
            "confidence": 0.5,
            "rationale": "ok",
        }
    )
    assert decision.relevant is True
    assert decision.market_slugs == ["btc"]
    assert decision.impact_direction == "up"


def test_router_decision_rejects_unknown_direction() -> None:
    with pytest.raises(ValidationError):
        RouterDecision(relevant=False, impact_direction="sideways")


def test_executor_decision_requires_reason_fields() -> None:
    with pytest.raises(ValidationError):
        ExecutorDecision(trade=False)


def test_build_router_and_executor_honor_mock_providers() -> None:
    settings = Settings(_env_file=None, router_provider="mock", executor_provider="mock")
    assert isinstance(build_router(settings), MockRouterAgent)
    assert isinstance(build_executor(settings), MockExecutorAgent)
