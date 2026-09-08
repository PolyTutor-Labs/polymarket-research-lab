# Research Workflow

Use this repository as a **study bench**, not as a signal booth.

The goal of a session is a documented, reproducible observation — including “no edge found.” The goal is not profit.

## Recommended loop

```text
Question
   ↓
Data
   ↓
Method (paper, backtest, or offline eval)
   ↓
Metrics
   ↓
Write-up (including negative results)
```

### 1. Write a question

Good questions are falsifiable:

- Does a calibration adjustment of size X survive the configured fee and slippage proxies on domain Y?
- Do paper fills after news routing occur before or after the public price move (telemetry timestamps)?
- Does any bucket of a retired strategy show win rate and average PnL above the published thresholds?

Poor questions for this lab:

- “How do I make money on Polymarket?”
- “Give me today’s trades.”
- “Which setting guarantees a win?”

### 2. Choose data you can defend

| Source | Where | Use |
| --- | --- | --- |
| Bundled Becker-style samples | `data/becker/*.parquet` | Fast local calibration / loader tests |
| Full Becker extract | optional external clone; `BECKER_DATASET_PATH` | Larger historical study (not required) |
| Paper seed | `db/seed_data.sql` | Inspect stored paper history |
| Saved CSVs | `backtests/results/*.csv` | Read-only examples of prior runs |
| Live public news | GDELT / RSS / optional adapters | Ingest study; not a signal feed |

Do not relabel outcomes to force a prettier table. If a file is missing, record that limitation.

### 3. Pick a method that matches the question

| Question type | Starting command or script |
| --- | --- |
| Historical calibration | `watchdog build-calibration --dataset-path ./data/becker` |
| Offline replay | `watchdog run-backtest --platform polymarket --domain politics` |
| Paper loop behavior | `watchdog run-paper-trading … --iterations 1` |
| News → decision path | `watchdog ingest-news-once` then `watchdog run-pipeline-once` |
| Gate as a *control* | `watchdog go-live-check` |
| Retired BTC-updown family | `python research/analysis/btc_scalp_edge_eval.py` |

Keep `ENABLE_LIVE_TRADING=false` and LLM providers at `mock` unless the question is specifically about those integrations.

### 4. Record metrics, not slogans

Typical research outputs in this tree:

- Win rate, Brier score, max drawdown, Sharpe, average PnL (`src/watchdog/backtest/metrics.py`)
- Bucket tables (price, time, domain, drift)
- Telemetry timestamps on pipeline events (`ts_news_received`, router / calibration / executor completion)
- Sample size and **what was not tested** (for example: BTC scalp Down-only)

A result without sample size, fees/slippage assumptions, and a time window is incomplete.

### 5. Write the result down

Prefer a short note that states:

1. Hypothesis
2. Data and date range
3. Filters and guards
4. Metrics
5. Verdict: continue / redesign / retire
6. Threats to validity

The BTC scalp write-up is the in-repo example of a finished negative study: [BTC_SCALP_RETROSPECTIVE.md](BTC_SCALP_RETROSPECTIVE.md).

## Paper versus historical versus live

| Mode | What it is | What it is not |
| --- | --- | --- |
| Historical backtest | Replay with fee/slippage/spread *proxies* | A live fill tape |
| Paper trading | Virtual bankroll and modeled execution | Proof you would have been filled |
| Go-live check | Thresholds on recent paper closes | Authorization to trade real funds |
| Optional live flags | Dangerous configuration surface | The purpose of this repository |

Paper trading does **not** guarantee live performance.

## Suggested daily study rhythm

The scheduled workflow `.github/workflows/daily_run.yml` is an example of **paper** restore → healthcheck → validation style automation. It is not a signal service. If you run `scripts/daily_validation.sh` locally, treat logs as research artifacts under `POLY_RESEARCH_LOG_DIR`.

A lightweight local rhythm:

1. `watchdog healthcheck`
2. One ingest or one backtest — not both until you can explain each
3. Inspect the DB or JSON/CSV output
4. Note one observation and one limitation

## Hypothesis hygiene

- **Validate the signal before adding guards.** Guards on a null edge only shrink sample size. The BTC scalp retrospective documents this failure mode.
- **Do not disable half the experiment** (for example only Down) and then generalize.
- **Watch pinned floors** (`realized_vol` at 0.001 was a model smell in the retired strategy).
- **Document negative results.** They shrink the next search.

## Safety rules for experiments

Safe:

- Mock LLMs, bundled Parquet, paper bankrolls, dry-run maker
- Isolated `POLY_RESEARCH_OUTPUT_DIR` so reports do not overwrite someone else’s files
- Tests in `tests/` when you change documented helper behavior

Unsafe or out of scope:

- Enabling live trading or loading a wallet private key “to see if it works”
- Publishing “today’s picks” from router/executor output
- Claiming a backtest Sharpe or paper PnL will continue
- Committing `.env`, databases, or secrets

If you extend the lab, follow [CONTRIBUTING.md](../CONTRIBUTING.md).
