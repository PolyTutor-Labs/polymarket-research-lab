# Getting Started

Run this repository as a **local research study environment**. You do not need live-trading credentials for the default path.

This is an educational laboratory, not a live trading product. See [DISCLAIMER.md](../DISCLAIMER.md).

## Requirements

Verified from `pyproject.toml` and CI:

- **Python 3.11+** (`requires-python = ">=3.11"`; GitHub Actions uses 3.12 for CI and 3.11 for the scheduled paper job)
- **pip** and a virtual environment
- Network only if you install packages, pull live news, or call optional paid APIs

No Polymarket account, wallet, or LLM API key is required for `init-db`, `healthcheck`, mock agents, or the bundled synthetic Becker samples.

## Installation

From the repository root (any clone; paths are repo-relative):

```bash
python -m venv .venv
source .venv/bin/activate
# Windows: .venv\Scripts\activate
pip install -e '.[dev]'
```

This installs the `watchdog` package from `src/` and development extras (`pytest`, `ruff`, `mypy`).

## Environment setup

```bash
cp .env.example .env
```

`.env` is gitignored. Keep real tokens out of git. Credential fields in `.env.example` must stay empty.

Useful defaults already in the example file:

| Variable | Default | Purpose |
| --- | --- | --- |
| `DATABASE_URL` | `sqlite:///watchdog.db` | Research DB (relative SQLite is resolved from repo root) |
| `BECKER_DATASET_PATH` | `./data/becker` | Parquet directory for calibration / backtests |
| `ENABLE_LIVE_TRADING` | `false` | Keep paper/research mode |
| `ROUTER_PROVIDER` | `mock` | No paid LLM required |
| `EXECUTOR_PROVIDER` | `mock` | No paid LLM required |
| `POLY_RESEARCH_ROOT` | empty | Override checkout root if needed |
| `POLY_RESEARCH_DATA_DIR` | empty → `<repo>/data` | Research inputs |
| `POLY_RESEARCH_OUTPUT_DIR` | empty → `<repo>/outputs` | Generated reports |
| `POLY_RESEARCH_LOG_DIR` | empty → `<repo>/logs` | Local logs |

Optional keys (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `MANIFOLD_API_KEY`, `TELEGRAM_*`, `POLYMARKET_PRIVATE_KEY`, …) stay blank unless you are deliberately studying those integrations. A non-empty `POLYMARKET_PRIVATE_KEY` is a **real-fund risk**. See [SECURITY.md](../SECURITY.md).

## First research commands

```bash
watchdog init-db
watchdog healthcheck
```

`init-db` creates schema and prints the resolved SQLite path. `healthcheck` confirms the process can load settings and talk to the configured database.

Optional paper baseline (only seeds when the trade table is nearly empty):

```bash
watchdog restore-baseline
```

## Suggested first study session

Stay on mock providers and bundled data:

```bash
# Calibration over the small tracked samples
watchdog build-calibration --dataset-path ./data/becker

# Historical replay (uses Becker files if present; otherwise a tiny synthetic set)
watchdog run-backtest --platform polymarket --domain politics

# One news ingest + one pipeline pass (public HTTP; no orders)
watchdog ingest-news-once
watchdog run-pipeline-once --max-news 5
```

Paper loop (virtual bankroll; still not live trading):

```bash
watchdog run-paper-trading --platform manifold --virtual-bankroll 500 --iterations 1
```

Manifold paper trading expects `MANIFOLD_USER_ID` for some paths. If you do not have one, skip this command and use backtests plus `run-pipeline-once` instead.

## Quality checks

```bash
pytest tests/
python -m compileall -q .
python scripts/security/check_secrets.py
ruff check src/
```

Use `python3` if `python` is not on your PATH.

## Common commands (research)

```bash
watchdog init-db
watchdog healthcheck
watchdog build-calibration --dataset-path /path/to/becker.parquet
watchdog run-paper-trading --platform manifold --virtual-bankroll 500 --iterations 1
watchdog go-live-check
watchdog run-snapshot-collector
watchdog run-backtest --platform polymarket --domain politics
watchdog run-market-maker --dry-run
watchdog ingest-news-loop --interval-seconds 30
watchdog run-pipeline-loop --iterations 0 --interval-seconds 60
```

`go-live-check` is a **paper-history checklist**. Passing it is not a recommendation to enable live trading.

`run-btc-scalp` is retired (`ENABLE_BTC_SCALP` / `enable_btc_scalp` defaults to false). Study [BTC_SCALP_RETROSPECTIVE.md](BTC_SCALP_RETROSPECTIVE.md) instead of turning it back on.

## Portability notes

The same checkout should run on any machine:

- Do not hardcode a personal machine home directory in scripts or notes you contribute.
- Prefer `POLY_RESEARCH_*` overrides when data or outputs live outside the repo.
- Activate `.venv` on Unix or Windows, or call the environment’s `python` directly.

## What you should not do in getting started

- Do not set `ENABLE_LIVE_TRADING=true` to “try the product.” There is no product.
- Do not commit `.env`, SQLite files, or API keys.
- Do not treat a green backtest or paper loop as a trading signal.
- Do not publish Telegram or GitHub secrets into issues or screenshots.

Next: [architecture.md](architecture.md), then [research-workflow.md](research-workflow.md) and [learning-path.md](learning-path.md).
