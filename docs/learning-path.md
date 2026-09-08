# Learning Path

Use this repository as a **study sequence**, not as a profit playbook. None of the modules, paper loops, or backtests are presented as guaranteed or recommended live methods.

## Stage 1 — Prediction-market concepts

Before changing code, make sure these ideas are clear:

- Binary contracts with prices typically in `(0, 1)`, interpreted as implied probabilities plus trading frictions.
- **Taker** vs **maker**: paying the spread vs posting liquidity and taking inventory risk.
- **Calibration**: how often does a stated probability of 0.70 actually resolve yes?
- **Paper vs live**: a modeled fill is not an exchange match.
- **Negative results**: a retired rule is still a successful experiment if it was honestly measured.

Then skim [DISCLAIMER.md](../DISCLAIMER.md) and [SECURITY.md](../SECURITY.md) so the lab’s limits are explicit.

## Stage 2 — Repository architecture

Read [architecture.md](architecture.md) and walk:

1. `src/watchdog/core/paths.py` — how the checkout stays portable.
2. `src/watchdog/core/config.py` — defaults (`ENABLE_LIVE_TRADING=false`, mock LLMs).
3. `src/watchdog/db/models.py` — markets, news, signals, trades, telemetry.
4. `src/watchdog/cli.py` — command names only; you do not need every handler yet.

Goal: you can explain “public data in, research records out” without assuming a hidden live broker.

## Stage 3 — Get a local lab running

Follow [getting-started.md](getting-started.md):

1. Virtualenv + `pip install -e '.[dev]'`
2. Copy `.env.example` → `.env` (leave secrets empty)
3. `watchdog init-db && watchdog healthcheck`
4. `watchdog run-backtest --platform polymarket --domain politics`

Ask:

- Which SQLite file did `init-db` print?
- Did the backtest use bundled Parquet, a full extract, or the synthetic fallback?
- Which metrics would still look fine if slippage doubled?

## Stage 4 — Calibration and the pipeline

Study, in order:

1. `src/watchdog/signals/calibration.py` — buckets and surface lookup
2. `src/watchdog/llm/router.py` — mock keyword routing
3. `src/watchdog/services/pipeline.py` — news → decision → persistence
4. `tests/test_calibration.py` and `tests/test_pipeline.py` — documented behavior

Run:

```bash
watchdog build-calibration --dataset-path ./data/becker
watchdog ingest-news-once
watchdog run-pipeline-once --max-news 5
```

Remember: a mock executor is a **teaching double**, not a silent alpha model.

## Stage 5 — Backtests and research controls

Read [backtesting.md](backtesting.md), then:

1. `src/watchdog/backtest/backtester.py`
2. `src/watchdog/backtest/metrics.py` (`evaluate_pass_fail`)
3. `src/watchdog/backtest/go_live_gate.py`
4. `tests/test_backtester.py`, `tests/test_go_live_gate.py`

Study questions:

- Why might `pass_go_live` be the least interesting field in the report?
- What does a 0.55 win-rate cutoff do to small samples?
- How would you cheat the gate if you treated it as a product KPI? (Do not. Notice the incentive.)

Paper trading does **not** guarantee live performance.

## Stage 6 — Read a finished negative result

Open [BTC_SCALP_RETROSPECTIVE.md](BTC_SCALP_RETROSPECTIVE.md) and `research/analysis/btc_scalp_edge_eval.py`.

Track:

- Original hypothesis (slow binary BTC-updown vs spot)
- What was actually tested (Down-only, short window, 332 closed paper trades)
- Why guards suppressed rather than created edge
- Recommended *next research* (baseline resolution rates, real volatility) — not “turn live back on”

Optional: run the evaluator if you have the CSVs it expects; otherwise read the script and the retrospective as the lesson.

## Stage 7 — Experiment safely

Safe experiments stay inside paper and offline tools:

- Change a documented setting (`MIN_DIVERGENCE_BACKTEST`, mock vs real LLM) and re-run one command.
- Point `POLY_RESEARCH_OUTPUT_DIR` at a throwaway folder.
- Add a test next to existing helpers when behavior is specified.
- Keep a lab notebook: hypothesis, command, result, limitation.

Unsafe or out of scope:

- Loading `POLYMARKET_PRIVATE_KEY` or setting `ENABLE_LIVE_TRADING=true` for class demos
- Shipping router output as “signals”
- Claiming any module is validated for real capital
- Re-enabling `btc_scalp` to chase the same failed regime

If you extend the project, follow [CONTRIBUTING.md](../CONTRIBUTING.md) and keep [DISCLAIMER.md](../DISCLAIMER.md) intact.

## Suggested file order

| Order | File | Why |
| --- | --- | --- |
| 1 | `src/watchdog/core/config.py` | Defaults and research flags |
| 2 | `src/watchdog/core/paths.py` | Portability |
| 3 | `src/watchdog/db/models.py` | Domain model |
| 4 | `src/watchdog/signals/calibration.py` | `C(p, t)` |
| 5 | `src/watchdog/llm/router.py` | Mock relevance |
| 6 | `src/watchdog/services/pipeline.py` | End-to-end research loop |
| 7 | `src/watchdog/backtest/backtester.py` | Offline evaluation |
| 8 | `src/watchdog/backtest/go_live_gate.py` | Control, not permission |
| 9 | `research/analysis/btc_scalp_edge_eval.py` | Negative-result practice |
| 10 | `docs/BTC_SCALP_RETROSPECTIVE.md` | How to write the study up |

## Optional background readings

`docs/readings/` contains public PDFs that shipped with the upstream checkout. They are background material. They are **not** instructions to operate a live bot and they are not PolyTutor investment advice.

## What this path does not teach

- How to make money on Polymarket.
- That any calibration surface, paper loop, or gate is validated for live trading.
- Official Polymarket operations or support procedures.
- That PolyTutor Labs or this repository provides trading signals.
