# PolyTutor Labs — Polymarket Research Lab

**Version:** [v0.1.0](CHANGELOG.md)
**Category:** Research / Analysis Laboratory
**Level:** Intermediate
**Package:** `watchdog` 0.1.0 (Python 3.11+)

An educational Polymarket research and analysis laboratory for studying prediction-market data, calibration, paper experiments, and offline backtests.

> Upstream attribution: derived from [daniel-st3/poly-what](https://github.com/daniel-st3/poly-what).
> Educational and research use only. Not financial advice. See [DISCLAIMER.md](DISCLAIMER.md).

## What this repository is

This repository is a **Polymarket research and analysis laboratory**.

It is a learning resource for inspecting how a research pipeline:

- ingests public news and market data
- links events to markets
- applies a historical calibration surface
- records paper-trade and telemetry outcomes
- evaluates hypotheses with backtests and offline analysis

## What this repository is not

This repository is **not**:

- a guaranteed profit system
- a trading signal service
- a live trading product
- investment, legal, or tax advice

Historical, paper, and backtest results do **not** predict live results. Nothing here is a recommendation to trade with real funds.

## PolyTutor Labs

This project is maintained by **PolyTutor Labs** as an educational packaging of an existing open-source research codebase.

PolyTutor work on this repository includes:

- repository organization
- portability (repository-relative paths)
- security hardening and a published security audit
- test and quality-gate stabilization
- educational documentation
- public-release packaging (changelog, license, metadata)

The original application code was not authored from scratch here. See [Attribution](#attribution).

This lab is **not affiliated with Polymarket**.

## About This Project

The installable Python package is still named `watchdog` (CLI: `watchdog`). That name is historical. Treat the project as a **research lab**, not as a production bot.

The default path is paper research:

- `ENABLE_LIVE_TRADING=false`
- LLM router and executor providers default to `mock`
- credential fields in `.env.example` are empty placeholders

Optional live-execution flags exist in configuration for studying risk gates. They are **not** the product identity of this repository. Enabling them can put real funds at risk. See [SECURITY.md](SECURITY.md).

A short-term BTC-updown experiment (`btc_scalp`) was **retired** after offline evaluation found no profitable regime. That negative result is part of the curriculum: [docs/BTC_SCALP_RETROSPECTIVE.md](docs/BTC_SCALP_RETROSPECTIVE.md).

## What You Will Learn

- How a prediction-market research loop is structured: data → relevance routing → calibration → paper or offline evaluation → persistence.
- How a 2D calibration surface `C(p, t)` is built from historical trades and used as a research adjustment, not as a promised edge.
- How paper trading, telemetry timestamps, and a go-live *research gate* are used as study controls.
- How backtests report win rate, Brier score, drawdown, and Sharpe — and why those numbers are not live performance.
- How to read a documented **negative result** and narrow a hypothesis instead of forcing a strategy to look profitable.

This project does **not** teach a profitable trading method.

## Features

Verified in the current tree:

- Typer CLI (`watchdog`) for database init, health checks, news ingest, paper loops, backtests, and analysis helpers
- Dual-agent research pipeline: cheap router + selective executor (both default to mock providers)
- Calibration surface service over DuckDB / Parquet Becker-style datasets
- SQLAlchemy models for markets, snapshots, news, signals, trades, and telemetry
- Paper-trading loop with risk helpers (Kelly fraction, VPIN halt, circuit breaker)
- Historical backtester and go-live *research gate* (thresholds are study controls, not a license to trade)
- Offline BTC-scalp analysis scripts and a written retirement retrospective
- Portable path helpers (`POLY_RESEARCH_*`) so the same checkout works on any machine
- Secret scanner and CI quality gates (pytest, ruff, compile)

## Architecture Overview

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

| Layer | Location | Responsibility |
| --- | --- | --- |
| CLI | `src/watchdog/cli.py` | Research commands (`init-db`, paper, backtest, scans) |
| News ingest | `src/watchdog/news/` | GDELT, RSS, optional Reddit / Marketaux / volume spikes |
| LLM agents | `src/watchdog/llm/` | Router and executor; default `mock` |
| Calibration | `src/watchdog/signals/calibration.py` | 2D surface `C(p, t)` by price, time, domain |
| Pipeline | `src/watchdog/services/pipeline.py` | News → signal → optional paper execution |
| Risk | `src/watchdog/risk/` | Kelly sizing, VPIN, circuit breaker |
| Backtest | `src/watchdog/backtest/` | Historical loader, metrics, go-live gate |
| Persistence | `src/watchdog/db/` | SQLite by default (`DATABASE_URL`) |
| Analysis | `research/analysis/` | Offline BTC-scalp evaluation and charts |
| Paths | `src/watchdog/core/paths.py` | Repo-relative data / output / log roots |

Details: [docs/architecture.md](docs/architecture.md).

## Repository Structure

```text
polymarket-research-lab/
├── README.md
├── CHANGELOG.md
├── LICENSE
├── CONTRIBUTING.md
├── DISCLAIMER.md
├── SECURITY.md
├── SECURITY_AUDIT.md
├── pyproject.toml
├── .env.example
├── docs/
│   ├── architecture.md
│   ├── getting-started.md
│   ├── research-workflow.md
│   ├── backtesting.md
│   ├── learning-path.md
│   ├── BTC_SCALP_RETROSPECTIVE.md
│   └── readings/                 # public background PDFs
├── src/watchdog/                 # installable research package
├── research/analysis/            # offline evaluation scripts
├── backtests/                    # extra arb studies + saved CSVs
├── data/becker/                  # small synthetic Becker-style samples
├── db/seed_data.sql              # paper-trade research history
├── scripts/                      # operational + security helpers
└── tests/
```

Generated reports go under `$POLY_RESEARCH_OUTPUT_DIR` (default `./outputs`, gitignored). Logs go under `$POLY_RESEARCH_LOG_DIR` (default `./logs`, gitignored).

## Getting Started

Requirements: Python 3.11+ (CI uses 3.12).

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e '.[dev]'
cp .env.example .env
watchdog init-db && watchdog healthcheck
```

Full setup, environment variables, and commands: [docs/getting-started.md](docs/getting-started.md).

## Research Workflow

1. Form a testable hypothesis (for example: “does calibration divergence survive fees and slippage on this domain?”).
2. Load public or bundled historical data. Do not invent labels to force a result.
3. Run paper loops or offline backtests. Record metrics and telemetry.
4. Evaluate with the published gates and bucket tables. Negative results count.
5. Write down what was tested and what was *not* tested.

Paper and backtest results do **not** guarantee live performance. See [docs/research-workflow.md](docs/research-workflow.md).

## Backtesting

```bash
watchdog run-backtest --platform polymarket --domain politics
```

The backtester loads Becker-style Parquet when available and falls back to a tiny synthetic sample so the command can be studied without a multi-gigabyte download. Metrics include win rate, Brier score, max drawdown, and Sharpe. The go-live gate is a **research checklist**, not approval to trade live.

Details: [docs/backtesting.md](docs/backtesting.md).

## Testing

```bash
pytest tests/
python -m compileall -q .
python scripts/security/check_secrets.py
ruff check src/
```

CI on pull requests runs the secret scan, ruff on `src/`, a non-blocking mypy pass, and pytest with coverage. See [.github/workflows/ci.yml](.github/workflows/ci.yml).

## Documentation

| Document | Topic |
| --- | --- |
| [docs/getting-started.md](docs/getting-started.md) | Install, environment, first commands |
| [docs/architecture.md](docs/architecture.md) | Layers, data flow, persistence |
| [docs/research-workflow.md](docs/research-workflow.md) | How to run a study in this lab |
| [docs/backtesting.md](docs/backtesting.md) | Historical replay, metrics, gates |
| [docs/learning-path.md](docs/learning-path.md) | Suggested study order |
| [docs/BTC_SCALP_RETROSPECTIVE.md](docs/BTC_SCALP_RETROSPECTIVE.md) | Retired strategy, negative result |
| [SECURITY.md](SECURITY.md) | Secrets policy, dataset classification, reporting |
| [SECURITY_AUDIT.md](SECURITY_AUDIT.md) | Historical pre-transform audit of the upstream repo |
| [CHANGELOG.md](CHANGELOG.md) | Version history (v0.1.0) |
| [LICENSE](LICENSE) | MIT license and attribution |
| [CONTRIBUTING.md](CONTRIBUTING.md) | What contributions are accepted |
| [DISCLAIMER.md](DISCLAIMER.md) | Educational-use disclaimer |

## Risks and Limitations

- **Research ≠ live trading.** Defaults are paper and mock LLMs. Optional live flags and wallet-key settings exist in code; treating them as a product is out of scope for this educational lab.
- **Calibration is historical.** A surface built from past trades can be wrong on new regimes. Divergence after fees is a *filter*, not a signal service.
- **Paper fills are modeled.** Slippage, spread, and fee proxies are assumptions. They do not reproduce CLOB matching, latency, or outages.
- **Go-live gate is not permission.** `watchdog go-live-check` scores paper-trade history against fixed thresholds. Passing it does not make live trading safe or advisable.
- **Retired work is still in the tree.** `btc_scalp` defaults to off. `railway.json` / Docker may still mention that command — treat that as leftover operations config, not an active strategy.
- **Third-party APIs can fail or change.** News sources, Manifold, and Polymarket endpoints are external. Mock providers avoid network and paid-LLM dependence for local study.
- **No official affiliation.** This is not a Polymarket product and is not investment advice.

## Security

See [SECURITY.md](SECURITY.md) for secret handling, the tracked-file scanner, dataset classification, and how to report issues.

The historical pre-transform audit of the upstream repository is preserved at [SECURITY_AUDIT.md](SECURITY_AUDIT.md). It is a frozen record. Do not treat it as a live operations runbook.

```bash
python scripts/security/check_secrets.py
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Documentation, tests, educational improvements, research notes, and bug fixes are welcome. Do not add secrets, private keys, or claims of guaranteed profit.

## Disclaimer

Educational and research use only. Trading involves risk. Historical or simulated performance does not guarantee future results. Paper trading differs from live trading.

Full text: [DISCLAIMER.md](DISCLAIMER.md).

## Attribution

This repository is an educational packaging by **PolyTutor Labs** of research software originally published as:

**[https://github.com/daniel-st3/poly-what](https://github.com/daniel-st3/poly-what)**

Upstream authors retain credit for the original Watchdog research codebase. PolyTutor Labs organized, hardened, documented, and packaged this checkout for classroom and self-study use. We are not affiliated with Polymarket or with the original authors unless they participate here separately.

## License

MIT. See [LICENSE](LICENSE). PolyTutor Labs does not claim authorship of the original application code.
