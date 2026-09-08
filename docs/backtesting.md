# Backtesting

Backtests in this laboratory are **offline studies**. They estimate how a rule might have behaved under modeled costs. They are not a trading signal and they do not guarantee future results.

## What the main backtester does

`watchdog run-backtest` calls `src/watchdog/scripts/run_backtest.py`, which uses:

| Piece | Module | Role |
| --- | --- | --- |
| Historical loader | `watchdog.backtest.historical_loader.BeckerHistoricalLoader` | Reads Parquet under `BECKER_DATASET_PATH` via DuckDB |
| Engine | `watchdog.backtest.backtester.Backtester` | Applies divergence filters, fee/slippage/spread proxies, Kelly-style size |
| Metrics | `watchdog.backtest.metrics` | Win rate, Brier, drawdown, Sharpe, calibration error, Monte Carlo drawdown helper |
| Gate helper | `evaluate_pass_fail` | Threshold checklist used by reports and `go-live-check` |

Default CLI wrapper:

```bash
watchdog run-backtest --platform polymarket --domain politics
```

The CLI currently runs the taker-style mode with `min_trades_per_bucket=100`. Library code also accepts a maker-style mode; that is a modeling switch, not a live quoting product.

## Data

### Bundled samples

`data/becker/` contains small **synthetic / public-safe** Parquet files so the loader and calibration path can be studied without a multi-gigabyte download.

### Full Becker extract (optional)

`BeckerHistoricalLoader` documents a one-time extract from the public [Jon-Becker/prediction-market-analysis](https://github.com/Jon-Becker/prediction-market-analysis) project. That extract is large (tens of gigabytes compressed). It is **not** required to learn the code.

If the configured directory is missing, the loader raises `FileNotFoundError`. If columns are incomplete, `run_backtest.py` can fall back to a **tiny synthetic** train/test/surface so students can still read a report shape.

Set the directory with `BECKER_DATASET_PATH` or:

```bash
watchdog build-calibration --dataset-path ./data/becker
```

`python -m watchdog.scripts.download_becker_data` writes into `$POLY_RESEARCH_DATA_DIR/becker` or `./data/becker`.

### Other saved results

`backtests/results/` holds example CSVs from earlier studies (capital simulations, monthly arb tables). They are historical artifacts. Do not treat them as current live performance.

Standalone scripts `backtests/backtest_arb.py` and `backtests/run_arb_backtest_clob.py` are extra experiments, not the main CLI path.

## Cost model (assumptions)

`Backtester` defaults (overridable via settings / constructor):

| Assumption | Typical default | Meaning |
| --- | --- | --- |
| Fee rate | `0.005` | Taker-style cost proxy |
| Slippage proxy | `0.005` | Extra adverse price move |
| Spread proxy | `0.01` | Half-spread style friction |
| Min divergence (backtest) | `0.15` | Skip unless model/market gap exceeds this |
| Kelly fraction | `0.25` | Fractional size, not full Kelly |
| Maker fill rate | `0.70` | Only in maker-style mode: not every quote fills |

These are **model knobs**. They are not exchange truth. Changing them changes the study; it does not create a real edge.

## Metrics to read carefully

Printed report fields include:

- `n_total_markets` / `n_traded`
- wins / losses and win rate
- Brier score (lower is better calibration of probabilities)
- max drawdown and Sharpe
- total and average PnL in USDC units of the *simulation*
- average slippage
- `pass_go_live` from the threshold helper

`evaluate_pass_fail` currently fails when:

- fewer than 50 trades
- win rate &lt; 0.55
- Brier ≥ 0.22
- max drawdown ≥ 0.25

`check_go_live_gate` in `src/watchdog/backtest/go_live_gate.py` applies those ideas to the last 50 **closed paper** trades and also requires total PnL &gt; 0.

**Passing the gate is not a recommendation to trade live.** It is a research checklist baked into this codebase. Markets change. Paper fills are not live fills.

## How to run a careful study

1. Fix the dataset path and record its identity (bundled sample vs full extract vs synthetic fallback).
2. Fix platform, domain filter, and cost knobs. Write them down *before* looking at PnL.
3. Run:

   ```bash
   watchdog run-backtest --platform polymarket --domain politics
   ```

4. If you persist JSON, put it under `$POLY_RESEARCH_OUTPUT_DIR` rather than scattering files in the repo root.
5. Compare in-sample vs later periods when you have enough data. The loader API supports year filters for that kind of split.
6. If no bucket is robust, **retire or redesign** the hypothesis. See the BTC scalp evaluation:

   ```bash
   python research/analysis/btc_scalp_edge_eval.py
   ```

   That script’s own thresholds (for example win rate &gt; 0.55 and positive average PnL) are study rules, not proof of a market anomaly.

## Interpreting results

Educational reading order:

1. Sample size and filters — did the rule almost never trade?
2. Costs — would a slightly worse fill wipe the PnL?
3. Calibration (Brier / ECE) — is the probability even meaningful?
4. Bucket tables — one lucky bin is not a strategy.
5. What was disabled (one side, one venue, one week).

Do not publish backtest PnL as a performance track record.

## Related commands

```bash
watchdog build-calibration --dataset-path ./data/becker
watchdog run-backtest --platform polymarket --domain politics
watchdog go-live-check
python -m watchdog.scripts.run_becker_analysis --platform polymarket
```

Maker dry-run (quotes modeled locally; not a live desk):

```bash
watchdog run-market-maker --dry-run
```

## What backtesting here is not

- Not a guaranteed profit system.
- Not a signal service.
- Not evidence that live execution would match the CSV.
- Not investment advice.
