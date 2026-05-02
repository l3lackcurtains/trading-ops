# trading-ops — Project Rules

This file is auto-loaded by Claude Code for every session in this project. It enforces cross-cutting rules globally so every slash command and every freeform conversation inherits them.

For a full repo map, see [`STRUCTURE.md`](STRUCTURE.md).

## Authoritative protocols

Two rule areas in `guide/`. Pick the right one for the task:

- **[`guide/scan-rules.md`](guide/scan-rules.md)** — index pointing into [`guide/scan/`](guide/scan/), the protocol for `/scan` (universal — auto-detects stock/crypto/index/FX/commodity), `/scan-macro`, `/scan-fundamentals`, `/scan-earnings`, `/rescan`. Split into focused files: [structure](guide/scan/structure.md), [protocol](guide/scan/protocol.md), [tiers](guide/scan/tiers.md), [scorecard](guide/scan/scorecard.md), [data](guide/scan/data.md), [crypto-flow](guide/scan/crypto-flow.md), [index-flow](guide/scan/index-flow.md), [fx-flow](guide/scan/fx-flow.md), [commodity-flow](guide/scan/commodity-flow.md), [style](guide/scan/style.md).
- **[`guide/discover-rules.md`](guide/discover-rules.md)** — protocol for `/discover`. SCREENS folder, screen file structure, retention, verified Finviz filter prefix reference, all preset filter sets (q1/q2/q3/q4/quality/growth/value/defense), 0-results fallback.

**Conflict resolution:**
- If a `.claude/commands/*.md` file and a guide file conflict, the guide wins. Open the fix in the guide.
- Within `guide/scan/`, see the conflict-resolution table in `guide/scan-rules.md`.

## Hard boundaries (never cross)

These apply to every command and every freeform action:

1. **`docs/` is read-only knowledge base — `/ingest` is the only writer.** Never edit `docs/` directly. Never create files in it from a scan, freeform action, agent, or self-improvement-loop. The `/ingest` slash command ([`.claude/commands/ingest.md`](.claude/commands/ingest.md)) is the single authorized entry point for adding or extending framework knowledge in `docs/`, and it always shows a write plan and waits for user consent before applying. If during a scan the framework itself seems incomplete, raise it as a "framework question" — don't write; suggest the user run `/ingest` if appropriate.

2. **`input/` is read-only.** Original PDFs and reference material. Never modify. Gitignored.

3. **`scanned/` is read-write.** Living state. Organized by asset class:
   - `scanned/MACRO/` — regime tracker
   - `scanned/stocks/<TICKER>/` — stock coverage
   - `scanned/fx/<PAIR>/`, `scanned/indices/<SYM>/`, `scanned/crypto/<SYM>/`, `scanned/commodities/<SYM>/`
   - `scanned/SCREENS/` — `/discover` output
   - `scanned/INDEX.md` — auto-generated coverage report

4. **`guide/` and `.claude/commands/`** can be edited — but only with explicit user consent via the self-improvement loop, an `/ingest` write plan, or a `/calibrate` drift-fix proposal. Never auto-modify.

5. **`/ingest` and `/calibrate` are sibling carve-outs.** `/ingest` is the only writer inside `docs/` (brings new framework knowledge in, recalibrates `guide/` immediately). `/calibrate` is the auditor that pulls `guide/` back to match `docs/` when drift accumulates — it never writes to `docs/`. When in doubt about which to use: new knowledge → `/ingest`; protocol-vs-framework alignment check → `/calibrate`.

## Self-improvement loop (applies to every command)

End every scan by checking whether the process itself had problems — broken links, wrong filter codes, ambiguous instructions, missing edge cases, source-priority gaps, inefficient ordering.

If problems were found, append a `## Process improvement suggestions` block to the response (NOT to the saved scan file) with:
- Concrete file path + step number
- Exact proposed fix
- Impact statement
- A "Apply these? (yes / no / pick which)" prompt

**Wait for user consent before editing `guide/**` or `.claude/commands/`.**

If no problems were found, stay silent — don't add a suggestions block. Signal value comes from the silence.

The scope of the loop is `guide/` and `.claude/commands/` only. Never `docs/`.

Full protocol: [`guide/scan/style.md`](guide/scan/style.md) § Process self-improvement.

## Automation scripts

`scripts/` contains Python utilities. Prefer these over LLM-driven manual work where possible:

- `python3 scripts/regen_index.py` — regenerate `scanned/INDEX.md` from each `current.md`'s Coverage tier line
- `python3 scripts/prune_archive.py [<folder> | --all] [--apply]` — apply retention policy (dry-run by default)
- `python3 scripts/validate_tiers.py` — lint Coverage tier syntax across every `current.md`
- `python3 scripts/validate_links.py` — project-wide markdown link audit; exits non-zero if any link is broken (skips code blocks and `<placeholder>` template paths)
- `.venv/bin/python scripts/fetch_quote.py <TICKER>` — local Yahoo (`yfinance`) quote fetcher; replaces Finviz+Stockanalysis WebFetches in `/scan` for ~98% of fields, pre-computes the Pillar 1 numeric auto-reject and 3-consecutive-Q growth check. Use `--auto-reject-only` for a fast pre-check (exit 3 = reject), `--json` for piped consumption. Source priority chain: see [`guide/scan/data.md`](guide/scan/data.md).
- `.venv/bin/python scripts/fetch_ohlc.py <TICKER> [--anchor YYYY-MM-DD]` — local OHLC + indicator pre-compute via yfinance. Pulls multi-timeframe OHLCV (default W/D/4H/1H), computes EMAs (default 20/50/200), ATR(14), RSI(14), vol×20avg, **VWAP family** (session / weekly / monthly / quarterly / anchored, with ±1σ / ±2σ bands), and **Volume Profile** (POC, VAH, VAL, HVN, LVN, current position vs Value Area, optional ASCII histogram with `--vp-ascii`). VP+VWAP are the operational backbone of the scan technical-read step — see [`docs/volume-profile.md`](docs/volume-profile.md) and [`docs/vwap.md`](docs/vwap.md). `--json` for piped consumption, `--out <path>` to write.
- `.venv/bin/python scripts/fetch_sec.py <TICKER>` — local SEC EDGAR fetcher; **primary source for Form 4 insider transactions** (replaces OpenInsider/Finviz-insider chain), cluster detection, filings freshness (10-K/10-Q/8-K), and **precise ROIC computed from XBRL company-facts** (closes the Yahoo ROIC-precise gap). Set `SEC_USER_AGENT="Name <email>"` env var (SEC fair-access policy). WebFetch chain in `data.md` § 5 stays as fallback. See [`guide/scan/data.md`](guide/scan/data.md) § Step 0a.
- `.venv/bin/python scripts/fetch_max_pain.py <TICKER>` — computes max pain locally from yfinance options chain across N upcoming OPEX dates (default 4). Replaces the ChartExchange max-pain WebFetch on most stock scans; ChartExchange stays as cross-confirmation fallback. See [`guide/scan/data.md`](guide/scan/data.md) § Step 0b.
- `.venv/bin/python scripts/fetch_macro.py` — local macro gauges fetcher; pulls FRED (rates / curve / CPI / PCE / NFP / U-3 / claims / IP / DXY / M2 / VIX) + Treasury daily yield curve. Requires `FRED_API_KEY` env var (free key at fredaccount.stlouisfed.org/apikeys). Replaces ~6 WebFetches per `/scan-macro`; existing WebFetch sources stay as fallback when FRED is unavailable.
- `.venv/bin/python scripts/fetch_crypto.py <SYMBOL>` — local crypto context fetcher; consolidates CoinGecko + alternative.me F&G + Binance klines + mempool.space (BTC) + DeFiLlama (alts) into one call. Replaces ~5 WebFetches per crypto scan; Tier A/B sources in `crypto-flow.md` stay as fallback. See [`guide/scan/crypto-flow.md`](guide/scan/crypto-flow.md) § Tier 0.
- `.venv/bin/python scripts/fetch_news.py <SYMBOL>` — local news + analyst-context fetcher; **required pre-step before writing the scan's News & Analyst Context section** per [`guide/scan/data.md`](guide/scan/data.md) § Step 8. **Works with NO API keys by default.** Tier 1 (keyless, universal): Google News RSS — works for stocks, crypto, FX, indices, commodities. Tier 2 (keyless, stock-specific): Finviz news widget HTML scrape + yfinance.news fallback. Tier 3 (optional upgrade): Finnhub `/stock/price-target` + `/stock/recommendation` + `/calendar/earnings` (with **AMC/BMO timing** — closes the Yahoo gap) when `FINNHUB_TOKEN` is set (free key at finnhub.io/register, 60 req/min). Categorizes headlines into catalyst / analyst / sector / macro buckets and emits a per-asset-class required-coverage checklist the scan must satisfy.
- `scripts/hooks/pre-commit` — git pre-commit hook that runs `validate_links.py` + `validate_tiers.py` when markdown is staged. Install once per clone: `ln -s ../../scripts/hooks/pre-commit .git/hooks/pre-commit`

## Tone

Direct, framework-aligned, numeric. No hedging in verdicts. "Wait" and "skip" are valid positions. See [`guide/scan/style.md`](guide/scan/style.md) § Tone for full rules.
