# Security

This repository is an educational prediction-market research lab. It is not a
production trading system. The defaults are intended for paper research, not
live funds.

## Safe defaults

- `ENABLE_LIVE_TRADING=false`
- LLM providers default to `mock`
- Credential fields in `.env.example` are empty placeholders
- Local `.env`, SQLite files, and logs are gitignored
- Daily CI no longer has `contents: write` and does not push to the repo

Live trading, wallet private keys, and third-party API tokens are optional local
or CI secrets. Do not commit them.

## Secrets and credentials

Copy `.env.example` to `.env` for local work. Keep real values out of git.

Typical secret names (values must stay empty in the example file):

- `POLYMARKET_PRIVATE_KEY` — wallet / exchange key; real-fund risk
- `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `DEEPSEEK_API_KEY`, `GEMINI_API_KEY`
- `MANIFOLD_API_KEY`, `MANIFOLD_USER_ID`
- `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`
- `MARKETAUX_API_KEY`, `BRAVE_API_KEY`
- `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`
- `N8N_WEBHOOK_URL` — optional circuit-breaker POST target

GitHub Actions should receive these only through repository secrets
(`${{ secrets.* }}`), never as plaintext workflow values.

## Secret scanning

Scan tracked files (never prints secret values):

```bash
python scripts/security/check_secrets.py
```

The scanner looks for common key/token shapes, PEM private-key headers, webhook
URLs, and non-empty credential assignments. It reports path, line, and rule id
only. CI runs the same command on every pull request.

## Dataset and privacy classification

| Path | Classification | Notes |
|------|----------------|-------|
| `data/becker/*.parquet` | SAFE | Small synthetic Becker-style samples; no customer data |
| `backtests/results/*.csv` | SAFE | Aggregate public-market backtest metrics |
| `db/seed_data.sql` | SAFE | Paper-trade research history on public markets; no API keys or emails found |
| `docs/readings/*.pdf` | SAFE | Public research readings; binary, not executed |
| `.env.example` | SAFE | Placeholders only |
| `SECURITY_AUDIT.md` | SAFE-WITH-NOTES | Historical pre-transform audit. Records original-repo metadata and a redacted local path/email from that audit. No live credentials. |

No notebooks (`.ipynb`) are tracked. Shell helpers use `subprocess` argument
lists, not `shell=True`. No `!curl` / `!wget` notebook cells exist.

## CI

- Default token permission is `contents: read`
- Actions are pinned to commit SHAs
- `daily_run.yml` may use `actions: write` only to rotate the paper-trade DB artifact
- Do not re-enable CI git push / seed auto-commit

## Dependencies

Runtime deps are declared in `pyproject.toml` with lower bounds only. This task
does not upgrade packages. Residual risk: no lockfile; unused declared packages
(`google-generativeai`, `py-clob-client`) increase install surface but were not
removed here (out of scope).

## Residual notes (not blockers)

- Docker / Railway still default to `watchdog run-btc-scalp` (retired strategy).
  The image now runs as a non-root user.
- `n8n_webhook_url` POSTs only if configured in the environment.
- `[DEBUG]` log text in `src/watchdog/strategies/btc_scalp.py` is research
  instrumentation, not a secret or leftover credential.

## Reporting a vulnerability

Open a private report to the repository maintainers. Do not file a public issue
that includes secret values, wallet keys, or production tokens.
