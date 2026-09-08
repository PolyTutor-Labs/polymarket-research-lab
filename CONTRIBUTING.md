# Contributing

Thank you for helping improve this **PolyTutor Labs educational research laboratory**.

This repository is a learning resource built on an existing open-source project. See [README.md](README.md) Attribution and [DISCLAIMER.md](DISCLAIMER.md). Contributions should make the lab easier to study, safer to run as paper research, or clearer to operate — not turn it into a “profit bot” or signal service.

## Accept

We welcome:

- **Documentation** — accuracy, architecture notes, learning guides, educational framing
- **Tests** — pytest coverage for paths, configuration, parsers, metrics helpers, and existing research utilities
- **Educational improvements** — comments, examples, and explanations that do not claim guaranteed returns
- **Research improvements** — clearer experiment logs, portable `POLY_RESEARCH_*` workflows, reproducible paper or backtest runs
- **Bug fixes** — including security issues reported without embedding secret values

## Require

Every contribution must:

- **Include no secrets** — no API tokens, Telegram credentials, `.env` values, or webhook secrets
- **Include no private keys** — no seed phrases, mnemonics, PEM/key material, or exchange credentials
- **Include no guaranteed profit claims** — no “always profitable,” “risk-free,” “signals,” or “will make money” language in code, docs, or comments
- **Explain behavior changes** — the PR description should say what a learner will observe differently (commands, metrics, files, defaults)

Do not add live order routing, wallet signing, or custody as if this were a trading product. Optional live flags already exist as a residual research surface; do not expand them without updating the disclaimer and security docs.

## How to work

1. Read [docs/getting-started.md](docs/getting-started.md) and [docs/architecture.md](docs/architecture.md).
2. Keep paths repo-relative; do not hardcode a personal machine home directory.
3. Put generated reports under `outputs/` or `POLY_RESEARCH_OUTPUT_DIR` (gitignored).
4. Match existing Python style; keep imports at the top of the file.
5. For switches on unions/enums, handle every variant (exhaustive `never` / `assert_never` style).

## Checks to run

```bash
pytest tests/
python -m compileall -q .
python scripts/security/check_secrets.py
ruff check src/
```

Use `python3` if `python` is not available.

Do not change research formulas or historical results just to make a test pass.

## Pull requests

- Describe the problem and the verified behavior after the change.
- Link any docs you updated (`README.md`, `docs/*`, `SECURITY.md`, `CHANGELOG.md`).
- If you change calibration, backtest, or strategy behavior, say so explicitly — those are not “docs-only.”
- Do not claim official Polymarket affiliation or investment advice.
- Do not treat paper PnL or `go-live-check` as a live-trading endorsement.

## Security reports

Do not open a public issue that includes credential values or exploit details. Follow [SECURITY.md](SECURITY.md).
