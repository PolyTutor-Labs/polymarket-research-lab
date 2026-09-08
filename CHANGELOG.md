# Changelog

All notable public-release changes to this PolyTutor Labs educational packaging
are recorded here.

This project is a prediction-market **research and analysis laboratory**.
Entries describe repository, documentation, and packaging work only. They do
not claim profitability, live trading success, or guaranteed results.

## [0.1.0] — 2026-09-08

First PolyTutor Labs public educational release of
`polymarket-research-lab` (installable package `watchdog` version `0.1.0`).

The default path remains paper research and offline backtests. Optional
live-execution flags exist in configuration for studying risk gates. They are
not the product identity of this repository.

### PolyTutor transformation

- Educational packaging of the existing open-source research codebase
  ([daniel-st3/poly-what](https://github.com/daniel-st3/poly-what)).
- Attribution, disclaimer, and research-not-trading framing added for public
  learners.
- Upstream git history is intentionally not retained in this packaging.

### Organization

- Repository layout cleaned for study: installable package under `src/watchdog/`,
  offline analysis under `research/analysis/`, extra studies under `backtests/`.
- Public readings live under `docs/readings/`.

### Portability

- Runtime paths resolve from the repository root (or `POLY_RESEARCH_*` env
  overrides).
- Local research is not tied to a developer machine home directory.

### Security

- `SECURITY.md` policy for secrets, datasets, and reporting.
- `SECURITY_AUDIT.md` is a preserved historical pre-transform audit of the
  upstream repository (not a live operations runbook).
- `.env*` gitignored except `.env.example` placeholders.
- `python scripts/security/check_secrets.py` plus CI quality gates.

### Testing

- Pytest suite under `tests/` for configuration, paths, parsers, metrics
  helpers, and existing research utilities.
- Public quality commands: `pytest`, `python -m compileall`,
  `python scripts/security/check_secrets.py`, `ruff check src`.

### Documentation

- Learner docs: getting started, architecture, research workflow, backtesting,
  learning path, and a retired-strategy retrospective.
- `CONTRIBUTING.md` and `DISCLAIMER.md`.
- Residual operational leftovers (Docker / Railway still default to the
  retired `run-btc-scalp` command) remain **documented, not redesigned**.

### Release packaging

- `pyproject.toml` metadata aligned with the public GitHub repository and
  research-lab identity.
- This changelog and a license / attribution file for the public tree.

[0.1.0]: https://github.com/PolyTutor-Labs/polymarket-research-lab/releases/tag/v0.1.0
