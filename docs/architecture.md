# Architecture

This document describes the research package as implemented under `src/watchdog/`. It does not invent extra services.

This laboratory is for **study**. The diagrams show how data moves through research code. They are not a live-trading operations map.

## Application structure

The installable package name is `watchdog` (historical). The CLI entry point is `watchdog = watchdog.cli:app` in `pyproject.toml`.

- **Library:** `src/watchdog/` — news, LLM agents, calibration, pipeline, risk, backtest, database.
- **CLI:** `src/watchdog/cli.py` — Typer commands used in lessons and scripts.
- **Offline analysis:** `research/analysis/` — BTC-scalp evaluation that is not part of the installable CLI surface.
- **Extra studies:** `backtests/` — standalone arbitrage replay scripts and saved CSV results.

```text
src/watchdog/
├── cli.py              # Typer research CLI
├── core/               # settings, paths, logging
├── db/                 # SQLAlchemy models and sessions
├── news/               # ingest + source adapters
├── llm/                # router + executor (default: mock)
├── signals/            # calibration surface
├── services/           # pipeline + market sync
├── risk/               # Kelly, VPIN, circuit breaker
├── strategies/         # research scanners (incl. retired btc_scalp)
├── execution/          # order helper used by paper / optional live paths
├── market_data/        # Polymarket CLI/REST + Manifold client
├── backtest/           # loader, backtester, metrics, go-live gate
├── trading/            # maker-model helpers
└── scripts/            # library-side runners invoked by the CLI
```

## Data flow

```text
Public news and market data
        ↓
Router (relevance + market link)
        ↓
Calibration C(p, t) + domain bias
        ↓
Executor (paper decision + risk checks)
        ↓
Research database and telemetry
        ↓
Backtests, analysis, and reports
```

Expanded:

```text
GDELT / RSS / optional Reddit, Marketaux, volume spikes
           │
           ▼
  src/watchdog/news/ingest.py
           │
           ▼
  src/watchdog/llm/router.py     (default MockRouterAgent)
           │
           ▼
  src/watchdog/signals/calibration.py
           │
           ▼
  src/watchdog/llm/executor.py   (default mock executor)
           │
           ├─ risk/kelly.py, risk/vpin.py, risk/circuit_breaker.py
           ▼
  src/watchdog/services/pipeline.py
           │
           ├─ db/          markets, signals, trades, telemetry
           └─ backtest/    historical replay and gate metrics
```

## Research lifecycle

1. **Initialize.** `watchdog init-db` creates SQLAlchemy tables. Default URL is `sqlite:///watchdog.db`, resolved against the repository root.
2. **Optional seed.** `watchdog restore-baseline` can load `db/seed_data.sql` when the trade table is nearly empty. That file is **paper research history**, not customer data.
3. **Ingest.** `watchdog ingest-news-once` or `ingest-news-loop` pulls public headlines into `news_events`.
4. **Route.** The router decides whether an item looks relevant and which market slugs to consider. Mock routing is keyword-based (`crypto`, `election`, `fed`, …).
5. **Calibrate.** `CalibrationSurfaceService` looks up an adjustment by price bucket, hours-to-resolution bucket, and domain. Time buckets are `(1, 6, 24, 72, 168, 336, 720, 2160)` hours.
6. **Decide.** The executor (mock by default) emits a research decision. Risk helpers can reject or size a paper intent.
7. **Record.** Pipeline code writes signals, optional paper trades, and telemetry timestamps for later study.
8. **Evaluate.** Backtests and `go-live-check` score stored or historical outcomes. A “pass” is a **research control**, not permission to trade live.

## Calibration layer

`src/watchdog/signals/calibration.py` builds and queries a 2D surface often written `C(p, t)`:

- **Price bucket:** model probability rounded to 1–99.
- **Time bucket:** hours remaining to resolution, snapped to the class-level list above.
- **Domain:** stored with each surface row.

`watchdog build-calibration --dataset-path …` loads Becker-style Parquet through DuckDB. Bundled samples live in `data/becker/` (synthetic / public-safe). A full historical extract is optional and large; see [backtesting.md](backtesting.md).

Calibration is a **historical frequency adjustment**. It is not a guarantee that the next market is mispriced.

## Agent layer

| Agent | Module | Default provider | Role |
| --- | --- | --- | --- |
| Router | `llm/router.py` | `mock` | Relevance + market link |
| Executor | `llm/executor.py` | `mock` | Selective trade / no-trade style decision |

Settings: `ROUTER_PROVIDER` / `EXECUTOR_PROVIDER` in `.env`. Real OpenAI or Anthropic keys are optional and must never be committed. Mock agents keep local study offline and free.

## Risk and paper-execution layer

These helpers are **research controls**:

| Helper | Module | What it studies |
| --- | --- | --- |
| Empirical Kelly | `risk/kelly.py` | Fractional sizing from model vs market prices |
| VPIN | `risk/vpin.py` | Flow-toxicity halt for maker-style quotes |
| Circuit breaker | `risk/circuit_breaker.py` | Daily-loss trip; optional webhook if configured |
| Order helper | `execution/order_executor.py` | Pre-checks before a paper or optional live path |

`ENABLE_LIVE_TRADING` defaults to `false`. The educational identity of this repository is paper research. Do not treat leftover live flags as a product feature.

## Persistence / state layer

| Piece | Default | Role |
| --- | --- | --- |
| SQLite research DB | `watchdog.db` via `DATABASE_URL` | Markets, news, signals, trades, snapshots |
| Seed SQL | `db/seed_data.sql` | Paper-trade history for restore/study |
| Becker samples | `data/becker/*.parquet` | Small public-safe calibration/backtest inputs |
| Outputs | `./outputs` or `POLY_RESEARCH_OUTPUT_DIR` | Generated reports (gitignored) |
| Logs | `./logs` or `POLY_RESEARCH_LOG_DIR` | Local logs (gitignored) |

`src/watchdog/core/paths.py` resolves the repo by walking for `pyproject.toml`. Paths are not tied to a developer home directory.

## Market-data layer

| Client | Module | Notes |
| --- | --- | --- |
| Polymarket CLI wrapper | `market_data/polymarket_cli.py` | Subprocess argument list (`shell=True` not used) |
| Polymarket REST | `market_data/polymarket_rest.py` | Public HTTP reads |
| Manifold | `market_data/manifold_client.py` | Optional paper venue; needs user id for some loops |

CLI path and expected version are settings (`POLYMARKET_CLI_PATH`, `POLYMARKET_EXPECTED_VERSION`). A local unverified binary must not be committed (see [SECURITY.md](../SECURITY.md)).

## Strategy and analysis layer

`src/watchdog/strategies/` holds research scanners (arbitrage, OFI, whale watch, ensemble, resolution filter, **retired** `btc_scalp`). Feature flags in `Settings` turn modules on or off. `enable_btc_scalp` defaults to `false`.

Offline evaluation for that retirement lives in `research/analysis/` and is written up in [BTC_SCALP_RETROSPECTIVE.md](BTC_SCALP_RETROSPECTIVE.md). Negative results are first-class lab output.

## What this architecture is not

- Not a guaranteed profit system.
- Not a trading signal service.
- Not a live trading product.
- Not an official Polymarket product.
- Not investment advice.
