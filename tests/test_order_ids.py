from __future__ import annotations

from watchdog.core.order_ids import normalize_platform_order_id


def test_normalize_platform_order_id_wraps_raw_exchange_ids() -> None:
    assert normalize_platform_order_id(
        platform="manifold",
        provider_order_id="abc123",
        fallback_order_id="paper-manifold-fallback",
    ) == "paper-manifold-abc123"


def test_normalize_platform_order_id_preserves_fallback_mode_prefix() -> None:
    assert normalize_platform_order_id(
        platform="polymarket",
        provider_order_id="live-123",
        fallback_order_id="live-polymarket-fallback",
    ) == "live-123"

    assert normalize_platform_order_id(
        platform="polymarket",
        provider_order_id="book-456",
        fallback_order_id="live-polymarket-fallback",
    ) == "live-polymarket-book-456"


def test_normalize_platform_order_id_empty_provider_uses_fallback() -> None:
    assert (
        normalize_platform_order_id(
            platform="manifold",
            provider_order_id="",
            fallback_order_id="paper-manifold-fallback",
        )
        == "paper-manifold-fallback"
    )
    assert (
        normalize_platform_order_id(
            platform="manifold",
            provider_order_id=None,
            fallback_order_id="paper-manifold-fallback",
        )
        == "paper-manifold-fallback"
    )


def test_normalize_platform_order_id_preserves_sim_and_arb_prefixes() -> None:
    assert (
        normalize_platform_order_id(
            platform="polymarket",
            provider_order_id="sim-99",
            fallback_order_id="paper-polymarket-fallback",
        )
        == "sim-99"
    )
    assert (
        normalize_platform_order_id(
            platform="polymarket",
            provider_order_id="arb-99",
            fallback_order_id="paper-polymarket-fallback",
        )
        == "arb-99"
    )


def test_normalize_platform_order_id_without_mode_prefix() -> None:
    assert (
        normalize_platform_order_id(
            platform="manifold",
            provider_order_id="abc123",
            fallback_order_id="plain-fallback",
        )
        == "manifold-abc123"
    )
