# SECURITY AUDIT - poly-what (pre-PolyTutor transform)

## 1. Repo identity and audit date

| Field | Value |
|---|---|
| Original repository | https://github.com/daniel-st3/poly-what |
| Future target (not created) | PolyTutor-Labs/polymarket-research-lab |
| Local clone path | /workspace/polytutor-labs/poly-what-audit |
| Audit branch | security-audit-before-polytutor (local only; not pushed) |
| Audited commit (HEAD at clone) | bde5dc49cb73848570d9cabf83ebc37bbfbe3b24 |
| Default remote branch | main |
| Audit date | **2026-09-08** |
| Auditor role | Pre-transform security audit only (no code changes, no rebrand, no packaging) |

**Project summary:** Python package watchdog - dual-agent prediction-market intelligence / paper-trading research bot (Polymarket + Manifold), with LLM routing, news ingest, risk gates, and optional live trading behind a feature flag.

---

## 2. Scope / method

**In scope**
- All tracked source under src/, scripts/, tests/, configs, Docker/Railway, GitHub Actions, db/seed_data.sql, data samples, Readings (filenames only; PDFs not reverse-engineered)
- Dependency manifests (pyproject.toml)
- Network URL / webhook / outbound call patterns in text sources and strings from the bundled binary
- Secrets / credential / private-key patterns in working tree and targeted git-history searches
- Malicious-pattern review: drainers, seed/key theft, clipboard stealers, obfuscated RCE, shady install hooks, unauthorized wallet access
- Git history authorship, bot auto-commits, binary introduction

**Method**
- Fresh git clone of the original repo; local branch security-audit-before-polytutor
- Full tree inventory; manual review of critical modules (config, order executor, Polymarket CLI/REST, circuit breaker, CI)
- Regex scans for URLs, secrets, eval/exec/pickle/shell=True/clipboard/webhook patterns
- strings + SHA-256 of .local/bin/polymarket
- Git log / pickaxe searches for .env, PEM keys, and non-empty POLYMARKET_PRIVATE_KEY assignments
- No application code modified; no remote push; no PolyTutor-Labs repo created

**Out of scope / limits**
- Dynamic malware sandbox execution of the Mach-O binary (Linux box cannot run it natively)
- Full decompilation of the ~9.1 MB CLI
- Verification of upstream PyPI package integrity beyond declared version ranges
- Live GitHub Actions secret values (only references via secrets context)

---

## 3. Findings

### Critical

_None observed._ No drainers, clipboard stealers, obfuscated RCE, credential exfiltration to attacker-controlled hosts, or committed live secret values were found in the working tree.

### High

| ID | Finding | Path(s) | Notes |
|---|---|---|---|
| H1 | **Unverified trading CLI binary committed to git** | .local/bin/polymarket (~9,179,040 bytes; SHA-256 a55f6a08661a4d7f14aabe09c0f98697eeeb72bb1a615f30ed57103678d1adbb) | Mach-O (macOS) binary introduced in commit f0d0191 (2026-03-01). Embedded endpoints include Polymarket CLOB/Gamma/data/bridge APIs and https://polygon.drpc.org. Strings reference wallet create/import and private-key handling. Not runnable on Linux CI; trust rests on opaque binary rather than a documented, pinned official install. Supply-chain / wallet-risk if PATH picks this up on a Mac with keys configured. |
| H2 | **CI job with contents:write + automated git push** | .github/workflows/daily_run.yml | Job permissions include contents: write and actions: write. Step Update seed data commits db/seed_data.sql and git pushes with [skip ci]. Compromised workflow or third-party action could push to main. Also causes extreme history noise (hundreds of bot commits). |

### Medium

| ID | Finding | Path(s) | Notes |
|---|---|---|---|
| M1 | **Third-party Actions not SHA-pinned** | .github/workflows/daily_run.yml (dawidd6/action-download-artifact@v6); also floating @v4/@v5 for official actions | Tag pins can move. Prefer commit SHAs. Third-party artifact download widens CI supply-chain surface. |
| M2 | **Live trading + wallet private key surface** | .env.example (POLYMARKET_PRIVATE_KEY, ENABLE_LIVE_TRADING); src/watchdog/core/config.py; src/watchdog/execution/order_executor.py; src/watchdog/market_data/polymarket_cli.py; src/watchdog/scripts/run_live_validation.py; src/watchdog/scripts/run_market_maker.py | Defaults are safe (ENABLE_LIVE_TRADING=false). Live path shells out to Polymarket CLI for orders/cancel-all when enabled. polymarket_private_key is loaded into Settings but not referenced elsewhere in Python (likely intended for CLI/env consumption). Misconfiguration risk for real funds - design hazard, not malware. |
| M3 | **Unpinned / wide dependency ranges** | pyproject.toml | All runtime deps use >= lower bounds only. No lockfile (uv.lock / poetry.lock / requirements.txt pin set). Future malicious or broken releases could be pulled on install. |
| M4 | **Configurable outbound webhook (SSRF / data leak if env poisoned)** | src/watchdog/risk/circuit_breaker.py (n8n_webhook_url); src/watchdog/core/config.py | POSTs JSON {event, daily_pnl_usd, threshold_usd, tripped_at} to whatever URL is in env. No hardcoded attacker URL. Risk only if env/secrets compromised or user points webhook at an untrusted receiver. |

### Low

| ID | Finding | Path(s) | Notes |
|---|---|---|---|
| L1 | **Declared but unused / lightly used heavy deps** | pyproject.toml (google-generativeai, py-clob-client); config keys deepseek_api_key, gemini_api_key unused in code paths reviewed | Increases install attack surface without clear benefit (ClobClient / generativeai imports not found). |
| L2 | **Dockerfile runs as root; installs editable package then copies all** | Dockerfile | No non-root user; pip install -e . then COPY . . Acceptable for research image but weak for production. |
| L3 | **Local absolute paths / username disclosure in scripts** | scripts/daily_validation.sh, scripts/check_exits_only.sh | Comments reference /Users/danielstevenrodriguezsandoval/poly-agent/... (local username + path). PII / environment disclosure. |
| L4 | **Large paper-trading seed committed and continuously rewritten** | db/seed_data.sql (~1.9 MB, ~3567 INSERTs); bot-authored history | Paper trades only (is_paper flags); no API keys found in seed. Still bloats clone and is operational data, not source. |
| L5 | **Subprocess wrapper around external CLI** | src/watchdog/market_data/polymarket_cli.py | Uses argument list form (shell=True not used). Injection risk is low if callers pass structured args; residual risk if POLYMARKET_CLI_PATH points at a malicious binary (ties to H1). |

### Info

| ID | Finding | Path(s) | Notes |
|---|---|---|---|
| I1 | README CI badge points at poly-agent not poly-what | README.md | Stale branding / wrong repo name in badge URL. |
| I2 | Author email visible in git history | git metadata | steven3102@hotmail.com (plus github-actions[bot]). Expected for public repos; note for privacy if rebranding. |
| I3 | Railway start command still watchdog run-btc-scalp while strategy retired | railway.json; README notes | Operational inconsistency; not a malware finding. |
| I4 | Synthetic Becker parquet samples present | data/becker/*.parquet | Small (~35 KB each); download script pulls from public GitHub raw URL. |
| I5 | Safety defaults observed | multiple | ENABLE_LIVE_TRADING=false; paper mode forced when live disabled; geoblock check present on CLI wrapper; Kelly/VPIN/circuit-breaker guards exist. |

---

## 4. Dependencies review

**Manifest:** pyproject.toml only (setuptools; Python >=3.11).

**Runtime dependencies (declared):** alembic, anthropic, aiosqlite, duckdb, feedparser, google-generativeai, httpx, numpy, openai, pandas, psycopg2-binary, praw, py-clob-client, pyarrow, pydantic, pydantic-settings, python-telegram-bot, python-dateutil, SQLAlchemy, tenacity, typer, vaderSentiment, websockets, aiohttp.

**Dev:** mypy, pytest, pytest-asyncio, pytest-cov, ruff.

**Assessment**
- Mix of reputable libraries for HTTP, DB, LLMs, Telegram, Reddit, sentiment, Polymarket CLOB client.
- No unsafe package lifecycle scripts found. Console entry: watchdog = watchdog.cli:app.
- Gaps: no lockfile; unused deps (L1); py-clob-client declared but not imported in application code reviewed.
- Bundled binary (H1) is outside the Python dependency graph and is the highest trust concern.

---

## 5. Network endpoints observed

Legitimate / expected destinations in source (and binary strings):

| Endpoint / host | Purpose |
|---|---|
| https://api.manifold.markets/v0 | Manifold markets / paper bets |
| https://gamma-api.polymarket.com | Polymarket market/event discovery |
| https://clob.polymarket.com | Polymarket order books / CLOB |
| https://data-api.polymarket.com | Holders / whale data |
| https://polymarket.com/event/... | Human-readable event links |
| https://bridge.polymarket.com | (binary strings) Polymarket bridge |
| https://polygon.drpc.org | (binary) Polygon RPC |
| https://api.openai.com/v1/chat/completions | Router LLM |
| https://api.anthropic.com/v1/messages | Executor LLM |
| https://api.telegram.org/bot.../sendMessage | Alerts / daily summaries |
| https://api.gdeltproject.org/api/v2/doc/doc | News (GDELT) |
| https://api.marketaux.com/v1/news/all | News |
| https://api.search.brave.com/res/v1/web/search | Optional Brave search |
| RSS: Reuters, AP, NYT | News feeds |
| https://www.metaculus.com/api2/questions/ | Ensemble signal |
| wss://advanced-trade-ws.coinbase.com | BTC price (retired scalp strategy) |
| https://api.coingecko.com/api/v3/simple/price | BTC price fallback |
| https://raw.githubusercontent.com/RupertMa/polymarket-analysis/... | Becker dataset download |
| https://api.github.com/repos/ / https://github.com/ | (binary / docs) |
| https://polygonscan.com/tx/ | (binary) tx links |
| User-configured n8n_webhook_url | Optional circuit-breaker alert POST |

**Not observed:** Discord webhooks, random ngrok tunnels, paste sites, clipboard APIs, keylogger endpoints, or hardcoded attacker C2 URLs.

**Outbound POST classes:** Telegram sendMessage; OpenAI/Anthropic chat; optional n8n webhook; Manifold authenticated bets (when API key set); CLI-mediated live orders (when live enabled).

---

## 6. Secrets scan summary (no values)

| Check | Result |
|---|---|
| Working-tree .env | **Absent** (gitignored); only .env.example with **empty** placeholders |
| PEM / OpenSSH private keys in tree | **None** |
| Live token-shaped strings in tree | **None** (tests use obvious dummies like test-key) |
| Hex-64 / wallet private keys in seed SQL | **None** |
| Non-empty POLYMARKET_PRIVATE_KEY= historically in .env* | **No matches** in targeted history search |
| GitHub Actions secrets | Referenced only via secrets context (OPENAI, ANTHROPIC, MANIFOLD_*, TELEGRAM_*, GITHUB_TOKEN) - values not in repo |
| Seed DB | Paper-trade history only; no credential columns |

**Placeholder names in .env.example (empty):** MANIFOLD_API_KEY, MANIFOLD_USER_ID, OPENAI_API_KEY, ANTHROPIC_API_KEY, Reddit OAuth pair, MARKETAUX_API_KEY, BRAVE_API_KEY, DEEPSEEK_API_KEY, GEMINI_API_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, POLYMARKET_PRIVATE_KEY.

**Recommendation:** Rotate any previously used live keys in the original author local/CI environment before reuse under PolyTutor (cannot verify remote GH secret store from this audit).

---

## 7. Git history notes

- About 870 commits on main at audit time.
- Authorship: github-actions[bot] ~738 (mostly [skip ci] update seed ...); human author Daniel Steven Rodriguez Sandoval ~132.
- First commit 1febde7 (2026-02-25) Initial Watchdog implementation.
- Binary .local/bin/polymarket added f0d0191 (2026-03-01).
- No evidence of committed .env or PEM files via path-based history search.
- Daily workflow auto-push of seed creates continuous rewrite noise and elevates blast radius of CI compromise (see H2).
- Commit 3b0be94 discusses secrets only in CI env-hoisting sense, not leak remediation.
- Co-authored-by Claude appears on some human commits (tooling metadata only).

---

## 8. Overall risk rating

**Medium** (for adopting the repo as-is into a teaching/research org), driven primarily by:

1. Opaque committed trading binary (H1), and
2. Privileged auto-push CI (H2) + unpinned Actions/deps (M1/M3),

**not** by evidence of intentional malware. Application Python code appears consistent with a research/paper-trading bot with explicit live-trading kill switches.

**Malware / drainer / exfil verdict:** No indicators of intentional wallet drainers, seed theft, clipboard stealers, or obfuscated remote code execution in reviewed sources.

---

## 9. Approval

Approved for PolyTutor transformation: YES

Rationale: No Critical malware or committed live-secret findings; network destinations match declared product behavior; live trading defaults off. Proceed only after completing the remediations below (especially remove/replace the bundled CLI binary and harden or disable write-capable CI before publishing under PolyTutor-Labs).

---

## 10. Recommended remediation before transform

1. Remove .local/bin/polymarket from the transformed tree; document installing the official Polymarket CLI from a pinned upstream release/checksum instead of shipping a Mach-O blob.
2. Disable or rewrite .github/workflows/daily_run.yml for PolyTutor: drop contents:write auto-push; stop committing db/seed_data.sql on a schedule; pin Actions to full commit SHAs (especially replace or pin dawidd6/action-download-artifact).
3. Add a lockfile (e.g. uv lock / pip-tools) and drop unused deps (google-generativeai, unused API key settings, reassess py-clob-client vs CLI).
4. Keep ENABLE_LIVE_TRADING=false for the research lab default; document that POLYMARKET_PRIVATE_KEY enables real-fund risk via external CLI; consider omitting live-order paths from the teaching fork or gating behind an explicit lab profile.
5. Strip or relocate db/seed_data.sql and local absolute path comments (/Users/danielstevenrodriguezsandoval/...) before public PolyTutor branding.
6. Rotate any GitHub Actions / API credentials that will be reused under the new org if prior collaborators or public forks could have observed workflow logs.
7. Dockerfile: run as non-root; avoid baking credentials; align start command with non-retired strategies.
8. Do not force-push or rewrite upstream daniel-st3/poly-what history as part of transform unless separately approved; prefer clean history on the new PolyTutor-Labs repo.

---

*End of pre-transform security audit. No application source was modified. Only this file was added for audit output.*


---

## Remediation applied 2026-09-08

Local-only hardening on branch `security-audit-before-polytutor` (not pushed). No trading/strategy logic changes, no package upgrades, no history rewrite, no upstream push.

| ID | Action taken |
|---|---|
| **H1** | Deleted tracked unverified binary `.local/bin/polymarket` from tree and index; removed empty `.local/` dirs; added `.local/bin/` to `.gitignore`. **No replacement binary added.** |
| **H2** | In `.github/workflows/daily_run.yml`: changed `contents: write` → `contents: read`; removed the Step 6 seed auto-commit / remote-update job that mutated `db/seed_data.sql`. Left SECURITY comments explaining why. Artifact upload/restore retained. |
| **M1** | Reviewed only (no mass CI redesign). Unpinned Actions remain; see table below for recommended SHA pins. |
| **M2** | Verified: `enable_live_trading: bool = False` in `src/watchdog/core/config.py`; `.env.example` has `ENABLE_LIVE_TRADING=false` and empty `POLYMARKET_PRIVATE_KEY=`; no private keys / live credentials in tree. Doc-only confirmation; trading logic untouched. |
| **M3** | Reported: dependency manifest is `pyproject.toml` only; **no lockfile** (`uv.lock` / `poetry.lock` / pinned `requirements.txt` absent). Lockfile generation skipped (would require full network install). No upgrades performed. |
| **M4** | Verified: `n8n_webhook_url` comes from Settings/env only (`None` default); circuit breaker POSTs only if env-provided; **no committed webhook URLs**. |

### M1 — Unpinned Actions inventory (report)

| Action | Current pin | Recommended change |
|---|---|---|
| `actions/checkout` | `@v4` (ci.yml, daily_run.yml) | Prefer full commit SHA of current v4.x release (`uses: actions/checkout@<40-char-sha> # v4.x.y`); major-tag `@v4` is acceptable interim for official Actions. |
| `actions/setup-python` | `@v5` | Prefer SHA of current v5.x; `@v5` interim OK for official Actions. |
| `actions/upload-artifact` | `@v4` | Prefer SHA of current v4.x; `@v4` interim OK for official Actions. |
| `dawidd6/action-download-artifact` | `@v6` (**third-party**) | **Must** pin to immutable 40-char commit SHA of the intended v6 release (`uses: dawidd6/action-download-artifact@<sha> # v6`). Resolve via `gh api repos/dawidd6/action-download-artifact/git/ref/tags/v6` (or newer maintained tag). Highest priority among Actions pins. |

### Post-remediation blocker status

| Blocker | Cleared? |
|---|---|
| H1 unverified binary in tree/index | **YES** |
| H2 contents:write + auto repo mutation | **YES** |
| M1 SHA pins | **NO** (reported; deferred) |
| M3 lockfile | **NO** (reported; deferred) |

**Security blockers cleared for PolyTutor transform gate (H1/H2): YES.** Residual medium items (M1/M3) remain recommended follow-ups, not hard stoppers after H1/H2.

