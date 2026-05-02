# Project structure — trading-ops

A one-page map of where everything lives. For day-to-day usage, see [`README.md`](README.md). For the trading framework itself, see [`docs/`](docs/). For the scan protocol, see [`guide/scan-rules.md`](guide/scan-rules.md).

```
trading-ops/
├── CLAUDE.md                    ← project rules auto-loaded by Claude Code each session
├── README.md                    ← project intro + how-to-use
├── STRUCTURE.md                 ← THIS FILE — repo map
├── .editorconfig                ← markdown / python conventions
├── .gitignore                   ← input/, .venv/, editor noise
│
├── .claude/                     ← Claude Code config + slash commands
│   ├── commands/                ← slash commands (thin wrappers — protocol lives in guide/)
│   │   ├── scan.md              ← /scan [<SYMBOL>] [--type=X]  — universal: auto-detects asset class; no args = regen INDEX.md
│   │   ├── scan-macro.md        ← /scan-macro             — macro / regime scan
│   │   ├── scan-flow.md         ← /scan-flow <SYMBOL>     — partial: refresh asset-class flow & positioning only
│   │   ├── scan-fundamentals.md ← /scan-fundamentals <T>  — partial: 6-pillar only (stocks)
│   │   ├── scan-earnings.md     ← /scan-earnings <T>      — partial: earnings setup only (stocks)
│   │   ├── rescan.md            ← /rescan <T> | macro     — full refresh + rotate archive
│   │   └── discover.md          ← /discover [<preset>]    — Finviz screener
│   ├── settings.json            ← project allowlist (tracked in git)
│   └── settings.local.json      ← personal overrides (not tracked)
│
├── guide/                       ← scan + discover protocol (read-only during scans)
│   ├── scan-rules.md            ← thin index → guide/scan/*
│   ├── scan/                    ← scan protocol, split by concern
│   │   ├── structure.md         ← folder layout, snapshot template, INDEX.md format, Action verdict spec
│   │   ├── protocol.md          ← read-before-scan, KB boundary, archive rotation, outcome resolution log
│   │   ├── tiers.md             ← coverage tiers (Pos / Swing / Day × T/W/B/S/X)
│   │   ├── scorecard.md         ← 6-pillar scoring conventions: Pillar 0 gate, moat tag, 3-Q growth + 13F high-conviction rule
│   │   ├── data.md              ← STOCK sourcing priorities (Finviz / Stockanalysis / ChartExchange…)
│   │   ├── crypto-flow.md       ← CRYPTO flow (F&G / ETF / funding / OI / options max-pain / heatmap)
│   │   ├── index-flow.md        ← INDEX flow + GAMMA (zero-flip / call wall / put wall / VIX structure)
│   │   ├── fx-flow.md           ← FX flow (CFTC COT + retail sentiment + rate diffs)
│   │   ├── commodity-flow.md    ← COMMODITY flow (COT + EIA/USDA + futures curve + seasonality)
│   │   └── style.md             ← tone, citation, scope, self-improvement loop
│   └── discover-rules.md        ← /discover protocol (Finviz filter prefixes, presets, fallbacks)
│
├── docs/                        ← framework knowledge base (read-only EXCEPT via /ingest)
│   ├── macro.md                 ← top-down macro / regime framework
│   ├── long-term-investing.md   ← long-term-investing reference layer (6-pillar fundamentals, moat types, etc.)
│   ├── positioning.md           ← cross-asset positioning: equity squeeze tier, dealer gamma, CFTC COT
│   ├── volume-profile.md        ← POC / VAH / VAL / HVN / LVN, profile shapes, naked POC
│   ├── vwap.md                  ← session / weekly / monthly / quarterly / anchored VWAP, ±σ bands
│   └── assets/                  ← reference images for the docs (per-doc subfolders)
│
├── scanned/                     ← live coverage state (read/write during scans)
│   ├── INDEX.md                 ← auto-generated coverage report (regenerate with scripts/regen_index.py)
│   ├── LESSONS.md               ← rolling lesson file — always loaded at scan start
│   ├── MACRO/                   ← regime tracker (top-level, not under stocks/)
│   │   ├── current.md
│   │   ├── archive/
│   │   └── charts/
│   ├── stocks/                  ← stock coverage
│   │   ├── BBAI/
│   │   ├── NIO/
│   │   ├── ORCL/
│   │   ├── RIVN/
│   │   ├── SOUN/
│   │   ├── USAR/
│   │   └── WWD/
│   ├── fx/                      ← FX trackers + tradeables
│   │   └── EURUSD/
│   ├── indices/                 ← (created when first index is scanned — uses index-flow.md)
│   ├── crypto/                  ← crypto coverage (uses crypto-flow.md)
│   │   └── BTCUSDT/
│   ├── commodities/             ← (created when first commodity is scanned — uses commodity-flow.md)
│   └── SCREENS/                 ← /discover output
│
├── scripts/                     ← automation
│   ├── regen_index.py           ← regenerate scanned/INDEX.md from current.md tier lines
│   ├── prune_archive.py         ← apply retention policy (keep latest per month, drop > 365d)
│   ├── validate_tiers.py        ← lint Coverage tier syntax across every current.md
│   ├── validate_links.py        ← project-wide markdown link audit (skips code blocks + template placeholders)
│   ├── _yfdata.py               ← Yahoo data adapter (yahooquery-backed)
│   ├── fetch_quote.py           ← local Yahoo Finance fetcher (yfinance) — replaces Finviz+Stockanalysis WebFetches; pre-computes Pillar 1 auto-reject + 3-Q growth gate
│   ├── fetch_ohlc.py            ← OHLC + indicator pre-compute (EMAs, ATR, RSI, vol×20avg, VWAP family + ±σ bands, Volume Profile POC/VAH/VAL/HVN/LVN); markdown or JSON
│   ├── fetch_sec.py             ← SEC EDGAR fetcher: Form 4 insider tx + cluster detection + 10-K/10-Q/8-K freshness + precise ROIC from XBRL (closes Yahoo gap)
│   ├── fetch_max_pain.py        ← local max-pain calc from yfinance options chain (replaces ChartExchange WebFetch on most scans)
│   ├── fetch_macro.py           ← FRED + Treasury macro gauges fetcher (rates / curve / CPI / PCE / NFP / DXY / VIX); needs FRED_API_KEY
│   ├── fetch_crypto.py          ← crypto context: CoinGecko + alt.me F&G + Binance klines + mempool (BTC) + DeFiLlama (alts) — replaces ~5 crypto WebFetches
│   ├── fetch_news.py            ← news + analyst context: Tier 1 Google News RSS (keyless, universal) + Tier 2 Finviz widget + yfinance.news (keyless, stocks) + Tier 3 optional Finnhub upgrade (price-target / recommendation / earnings AMC-BMO); emits required-category checklist per asset class
│   ├── extract_pdfs.py          ← convert input/*.pdf → docs/*.md (generic; JOBS list configured per use)
│   ├── clean_md.py              ← strip footer noise from extracted markdown
│   └── hooks/
│       └── pre-commit           ← runs validate_links.py + validate_tiers.py when .md files are staged
│                                  install: ln -s ../../scripts/hooks/pre-commit .git/hooks/pre-commit
│
└── input/                       ← source PDFs + ancillary references (gitignored)
    └── youtube-sources.txt
```

## Folder boundaries (during a scan)

| Folder | Role | During a scan | Authorized writer |
|---|---|---|---|
| `docs/` | framework (rules of the game) | **read-only** | `/ingest` only — see [`.claude/commands/ingest.md`](.claude/commands/ingest.md) |
| `guide/` | scan protocol (rules of how we scan) | **read-only** | self-improvement loop · `/ingest` recalibration · `/calibrate` drift fixes (all with user consent) |
| `input/` | original PDFs + references | **read-only always** | user-managed manually |
| `scanned/` | applications (game state today) | **read/write** | scan commands |
| `scripts/` | automation utilities | run via `python3 scripts/<name>.py` | manual development |
| `.claude/commands/` | slash command thin wrappers | edited only with user consent | self-improvement loop · `/ingest` · `/calibrate` |

## Common entry points

| Goal | Command |
|---|---|
| Scan anything (stock / crypto / index / FX / commodity — auto-detected) | `/scan <SYMBOL>` |
| Override asset-class detection | `/scan <SYMBOL> --type=stock\|crypto\|index\|fx\|commodity` |
| Full refresh + archive rotate | `/rescan <TICKER>` or `/rescan macro` |
| Refresh flow data only (COT / ETF / EIA / gamma) | `/scan-flow <SYMBOL>` |
| Refresh 6-pillar only (stock 10-Q / 13F drop) | `/scan-fundamentals <TICKER>` |
| Refresh earnings setup only | `/scan-earnings <TICKER>` |
| Macro regime read | `/scan-macro` |
| Run a Finviz screener | `/discover [<preset>]` |
| Regenerate `scanned/INDEX.md` | `/scan` (no args) — or `python3 scripts/regen_index.py` |
| Prune archive folders | `python3 scripts/prune_archive.py --all --apply` |
| Lint tier syntax | `python3 scripts/validate_tiers.py` |
| Audit markdown links | `python3 scripts/validate_links.py` |
| Fetch local quote (replaces Finviz/Stockanalysis WebFetches) | `.venv/bin/python scripts/fetch_quote.py <TICKER>` |
| Fetch OHLC + indicators + VWAP family + Volume Profile | `.venv/bin/python scripts/fetch_ohlc.py <TICKER> [--timeframes=W,D,4H,1H] [--anchor=YYYY-MM-DD]` |
| Fetch SEC EDGAR (Form 4 + ROIC + filings) | `.venv/bin/python scripts/fetch_sec.py <TICKER>` |
| Compute max pain locally (yfinance options chain) | `.venv/bin/python scripts/fetch_max_pain.py <TICKER>` |
| Fetch macro gauges (FRED + Treasury) | `FRED_API_KEY=... .venv/bin/python scripts/fetch_macro.py` |
| Fetch crypto context (CoinGecko + F&G + Binance + mempool + DeFiLlama) | `.venv/bin/python scripts/fetch_crypto.py <SYMBOL>` |
| Fetch news + analyst context (Google News RSS + Finviz + yfinance, keyless) | `.venv/bin/python scripts/fetch_news.py <SYMBOL>` |

## Adding a new ticker

1. Run `/scan <SYMBOL>` — asset class is auto-detected; the right folder gets created.
2. The command auto-creates `scanned/<asset-class>/<SYMBOL>/{archive,charts}/` if it doesn't exist.
3. Drop a TradingView screenshot in `~/Downloads/` if you want Tier 1 chart pickup.
4. INDEX.md updates automatically per `tiers.md` § Tier-change protocol.

## Adding a new asset class

E.g., adding `commodities/`:
1. First scan via `/scan <SYMBOL>` (the command auto-detects commodity type and creates `scanned/commodities/<SYMBOL>/` if missing).
2. `scripts/regen_index.py` already knows how to walk `commodities/` (listed in `ASSET_CLASSES`); no code changes needed.
3. If you want a dedicated focus block in INDEX.md, add to `regen_index.py` `render_focus_block` callsites.

## Asset-class flow doc routing

`/scan <SYMBOL>` auto-routes to the right flow doc by symbol type. The four flow docs are mutually exclusive — exactly one applies per scan.

| Symbol type | Flow doc | Key signals |
|---|---|---|
| Crypto (BTCUSDT, ETHUSDT, etc.) | [`guide/scan/crypto-flow.md`](guide/scan/crypto-flow.md) | F&G, ETF flows, perp funding, OI, options max pain, liquidation heatmap, network state |
| Indices (SPX, NDX, RUT, SPY/QQQ/IWM/DIA) | [`guide/scan/index-flow.md`](guide/scan/index-flow.md) | **Gamma exposure** (zero-flip / call wall / put wall), VIX term structure, sentiment, breadth |
| FX pairs (6-letter, EURUSD/USDJPY/etc.) | [`guide/scan/fx-flow.md`](guide/scan/fx-flow.md) | CFTC COT (primary), retail sentiment (contrarian), rate differentials |
| Commodities (USO, GLD, GDX, CL, GC, etc.) | [`guide/scan/commodity-flow.md`](guide/scan/commodity-flow.md) | CFTC COT, EIA/USDA inventory, futures curve, Baker Hughes rigs, seasonality |
| Sector ETFs (XLE, XLK, XLF, etc.) | falls back to stock template | stock-side `data.md` chain (no 6-pillar via underlying) |

Routing logic lives in [`.claude/commands/scan.md`](.claude/commands/scan.md) § Step 1 — Asset-class detection.

## Lesson loop

Every Action verdict carries a verb + 1-line trigger spec. On rescan, prior triggers get classified (`fired-correct` / `fired-stopped` / `invalidated` / `stale`) and logged to `scanned/INDEX.md § Performance / audit log`. Concrete dated lessons accumulate in `scanned/LESSONS.md`, which is loaded at the start of every subsequent scan.

Aggregation script (`scripts/compute_hit_rates.py`) and `/review-track-record` slash command are deferred — they activate once archive depth ≥ ~4 weeks per ticker.
