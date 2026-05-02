# trading-ops

A systematic trading workspace that runs inside [Claude Code](https://claude.ai/code). One command scans any asset — stock, crypto, index, FX, commodity — and produces a dated, framework-aligned analysis with structured verdicts, ASCII price ladders, and trade tables. Everything saves as local Markdown: auditable, greppable, version-controlled, and yours.

```
/scan AAPL        → 6-pillar fundamentals + Volume Profile + VWAP + trade plan
/scan BTCUSDT     → F&G + ETF flows + perp funding/OI + liquidation heatmap
/scan SPX         → gamma exposure + VIX term structure + AAII + breadth
/scan EURUSD      → CFTC COT + retail sentiment + rate differentials
/scan-macro       → regime quadrant (Goldilocks / Reflation / Stagflation / Risk-Off)
/discover         → Finviz screener anchored to current macro regime
```

---

## What you get

**Structured verdicts — no prose triggers.** Every scan ends with a verb (`LONG` / `SHORT` / `WAIT` / `SKIP` / ...), an ASCII price ladder with every level marked, and a trade table with Entry / Stop / T1 / T2 / T3 / R:R / Sizing / Time-stop:

```
              BTCUSDT  -  2026-04-29  -  spot $76,335
              ==========================================

              UPSIDE  (bull resolution path)
   $84,000   ===   [T2]  heatmap cluster (forced-cover magnet)
   $80,000   ===   [T1]  heatmap density + May 30 max pain
   $79,500         -->   LONG entry  (Swing-B)
   $79,200   ===    ^^   trigger: daily close ≥ + green vector
   $78,200   ###         supply zone bottom (3-wk rejection)
   - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
>> $76,335   ***   CURRENT   ***
   $75,500   ===   [t]   Day target / counter-trend entry
   - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
              DOWNSIDE  (bear resolution path)
   $73,800         -->   SHORT entry  (Swing-A)
   $66,000   ===   [T3]  long-dated max pain (Sept/Dec OPEX)
```

**Three horizons per name.** Positional (weeks–months), Swing (3–15 days), Day (intraday). Different verdict per horizon — positional auto-reject is compatible with a tradeable swing.

**Audit trail built in.** Every scan is dated and archived. Rescans delta-compare against prior snapshots (`Δ since last scan`), classify prior triggers as `fired-correct / fired-stopped / invalidated / stale`, and accumulate in a rolling `LESSONS.md` loaded before every scan.

**Mostly no API keys required.** Nine Python scripts pre-compute data locally (Yahoo Finance, SEC EDGAR, CoinGecko, alternative.me, Binance, mempool.space, Google News RSS). Optional free keys for FRED macroeconomics and Finnhub analyst data upgrade the output further.

---

## Prerequisites

- **[Claude Code](https://claude.ai/code)** — the CLI that runs the slash commands
- **Python 3.10+** — for the data pre-compute scripts
- **Free TradingView account** (optional) — for chart screenshots via chrome-devtools MCP

No paid data subscriptions required at any tier.

---

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/trading-ops.git
cd trading-ops

python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Then open the folder in Claude Code:

```bash
claude .
```

The slash commands are immediately available. Start with:

```
/scan-macro
```

---

## Optional API keys

Set these as environment variables (e.g. in `~/.bashrc` or a `.env`):

| Variable | Source | What it unlocks |
|---|---|---|
| `FRED_API_KEY` | [fredaccount.stlouisfed.org/apikeys](https://fredaccount.stlouisfed.org/apikeys) (free) | Full macro data via `fetch_macro.py` — replaces ~6 WebFetches per `/scan-macro` |
| `FINNHUB_TOKEN` | [finnhub.io/register](https://finnhub.io/register) (free, 60 req/min) | Analyst price targets, recommendations, earnings AMC/BMO timing |
| `SEC_USER_AGENT` | Any string: `"Name <email>"` | SEC EDGAR fair-access policy for `fetch_sec.py` — Form 4 insider data + ROIC from XBRL |

Everything works without keys. The keys are upgrades.

---

## Quick start (first 5 minutes)

**1. Set the macro regime.**
```
/scan-macro
```
Pulls rates, curve, CPI, PCE, NFP, DXY, VIX. Places the market in one of four quadrants (Goldilocks / Reflation / Stagflation / Risk-Off). Saves to `scanned/MACRO/current.md`. Run this first — the regime gates every downstream verdict.

**2. Scan a ticker.**
```
/scan AAPL
```
Auto-detects asset class (stock → 6-pillar + Volume Profile + VWAP + ChartExchange flow). Saves to `scanned/stocks/AAPL/current.md`. For crypto, FX, indices, or commodities — same command, different symbol.

**3. Find new names.**
```
/discover
```
Parses your intent into Finviz filters, anchors to the current regime, saves a candidate list to `scanned/SCREENS/`. Then `/scan <TICKER>` on anything promising.

**4. Rescan when things move.**
```
/rescan AAPL
```
Rotates the prior snapshot to `archive/`, pulls fresh data, marks the TL;DR with `Δ` if the verdict changed.

---

## All commands

| Command | What it does |
|---|---|
| `/scan-macro` | Top-down regime read. Sets the quadrant for all downstream scans. |
| `/scan [SYMBOL]` | Universal scan — auto-detects stock / crypto / index / FX / commodity. No args = regenerate `scanned/INDEX.md`. |
| `/rescan SYMBOL\|macro` | Full refresh — rotate archive, pull fresh data, mark deltas. |
| `/scan-flow SYMBOL` | Partial: refresh asset-class flow & positioning only (COT / ETF / gamma). |
| `/scan-fundamentals TICKER` | Partial: refresh 6-pillar scorecard only (stocks). Run after new 10-Q / 13F. |
| `/scan-earnings TICKER` | Partial: earnings setup 8-point checklist. Run 4–6 weeks pre-print. |
| `/discover [intent]` | Finviz screener. Natural language: `/discover cheap semis with ROI > 20`. |
| `/ingest source` | Add new framework knowledge to `docs/`. PDF / URL / inline text. |
| `/calibrate [scope]` | Audit `guide/` against `docs/` for drift. |

### Asset-class auto-detection

| Symbol shape | Routed as | Extra data |
|---|---|---|
| 1–5 letter US ticker | Stock | 6-pillar + ChartExchange + earnings |
| ends in `USDT`/`USD` | Crypto | F&G + ETF + perp funding/OI + max pain + heatmap |
| `SPX` / `NDX` / `SPY` / `QQQ` | Index | Gamma + VIX structure + AAII + breadth + COT |
| 6-letter pair (`EURUSD`) | FX | CFTC COT + retail sentiment + rate diffs |
| `CL` / `GC` / `USO` / `GLD` | Commodity | COT + EIA/USDA + curve + seasonality |

Override ambiguous cases: `/scan MSTR --type=crypto`

---

## Folder layout

```
trading-ops/
├── docs/                    ← framework knowledge base (read-only)
│   ├── macro.md             ← 4-regime model, key indicators, news-trading playbook
│   ├── long-term-investing.md  ← 6-pillar fundamentals, moat types, 10-K reading
│   ├── positioning.md       ← squeeze tier, dealer gamma, CFTC COT
│   ├── volume-profile.md    ← POC / VAH / VAL / HVN / LVN, profile shapes
│   └── vwap.md              ← session / weekly / monthly / quarterly / anchored VWAP
├── guide/                   ← scan protocol (read-only during scans)
│   ├── scan-rules.md        ← index into guide/scan/
│   └── scan/                ← per-concern protocol files
├── .claude/commands/        ← slash command definitions
├── scripts/                 ← Python data-fetch utilities
├── scanned/                 ← living analyses — your trading desk
│   ├── INDEX.md             ← auto-generated coverage navigator
│   ├── LESSONS.md           ← rolling lessons, loaded before every scan
│   ├── MACRO/               ← regime tracker
│   ├── stocks/<TICKER>/     ← per-stock coverage (current.md + archive/ + charts/)
│   ├── crypto/<SYMBOL>/
│   ├── indices/<SYMBOL>/
│   ├── fx/<PAIR>/
│   └── commodities/<SYMBOL>/
└── requirements.txt
```

`docs/` and `guide/` are read-only during scans — the framework is enforced, not improvised. `/ingest` is the only command that writes to `docs/`. `/calibrate` audits `guide/` for drift against the knowledge base.

---

## Python scripts

The scripts replace WebFetches with local pre-computation. All keyless by default; optional keys shown in parentheses:

| Script | What it pre-computes |
|---|---|
| `fetch_quote.py TICKER` | Yahoo Finance quote — price, valuation, profitability, growth, balance sheet, short interest, analyst consensus. Includes Pillar-1 numeric auto-reject check. |
| `fetch_ohlc.py TICKER` | Multi-timeframe OHLCV + EMAs (20/50/200) + ATR + RSI + VWAP family (session/weekly/monthly/quarterly/anchored, ±σ bands) + Volume Profile (POC/VAH/VAL/HVN/LVN + ASCII histogram). |
| `fetch_sec.py TICKER` | SEC EDGAR Form 4 insider transactions, cluster detection, ROIC from XBRL company facts. Requires `SEC_USER_AGENT`. |
| `fetch_max_pain.py TICKER` | Options max pain across next N OPEX dates from yfinance options chain. |
| `fetch_macro.py` | FRED macro gauges + Treasury yield curve. Requires `FRED_API_KEY`. |
| `fetch_crypto.py SYMBOL` | CoinGecko + alternative.me F&G + Binance klines + mempool.space + DeFiLlama. |
| `fetch_news.py SYMBOL` | Google News RSS (keyless) + Finviz widget + optional Finnhub analyst data (`FINNHUB_TOKEN`). |
| `regen_index.py` | Regenerate `scanned/INDEX.md` from every `current.md`. |
| `prune_archive.py [--apply]` | Retention policy — keep latest per month, drop >12 months. Dry-run by default. |
| `validate_links.py` | Project-wide markdown link audit. Exits non-zero on broken links. |
| `validate_tiers.py` | Lint coverage tier syntax across all `current.md` files. |

Run any script with `--help` for full options. Use `.venv/bin/python scripts/<script>.py` if the venv is not activated.

---

## Coverage tiers

Every scan tags one tier per horizon (Pos / Swing / Day). `INDEX.md` rolls them up:

| Tier | Meaning |
|---|---|
| **T** — Top Pick | Full conviction, deploy on next trigger |
| **W** — Watchlist | Live trigger spec ready, act when conditions hit |
| **B** — Bench | Followed but no near-term trigger |
| **S** — Skip | Auto-reject or hostile setup |
| **X** — Dropped | Removed from coverage |

A name's verdict can differ by horizon — positional S is compatible with a swing W around a catalyst.

---

## The framework (in `docs/`)

All scans draw from four documents in `docs/`. They are read-only during scans — the framework is the anchor.

- **`macro.md`** — Four growth × inflation quadrants (Goldilocks / Reflation / Stagflation / Risk-Off), key indicators, FOMC/CPI/NFP news-trading playbook, bubble indicators.
- **`long-term-investing.md`** — 6-pillar scorecard (Quality / Growth / Valuation / Balance Sheet / Capital Allocation / Smart Money), moat types, how to read a 10-K, capital allocation discipline.
- **`volume-profile.md`** — POC / VAH / VAL / HVN / LVN, profile shapes (D / P / b / B / multi-modal), naked POCs as forward targets. The backbone of the technical read.
- **`vwap.md`** — Session / weekly / monthly / quarterly / anchored VWAP, ±1σ / ±2σ bands, reclaim / lose patterns. The second leg of the technical core.

Add new knowledge via `/ingest`. The command shows a write plan and waits for consent before touching `docs/`.

---

## Extending the framework

**New framework knowledge** (new indicator, new macro model, new positioning concept):
```
/ingest input/new-paper.pdf
/ingest "Add dealer delta positioning section to macro.md"
```

**Protocol improvements** (better source priority, new data source, fixed filter code): handled by the self-improvement loop — Claude surfaces suggestions at the end of every scan and waits for your consent before editing `guide/` or `.claude/commands/`.

**New asset class or data source**: add a `guide/scan/<class>-flow.md` file following the pattern of the existing flow docs, then run `/calibrate` to sync.

---

## Pre-commit validation

A git hook runs `validate_links.py` and `validate_tiers.py` on every staged markdown commit. Install once per clone:

```bash
ln -s ../../scripts/hooks/pre-commit .git/hooks/pre-commit
```

---

## Rules in four bullets

1. **`docs/` is read-only.** `/ingest` is the only writer. Never modify during a scan.
2. **Read before you scan.** Every command loads `current.md`, recent archives, `MACRO/current.md`, and `LESSONS.md` first.
3. **Cite numbers, not vibes.** Every claim that drives a verdict gets a markdown link. ROIC -38.6% beats "ROIC is poor."
4. **Action verdicts are structured, not prose.** Verbs from a fixed list, ASCII ladder for levels, trade table for triggers / stops / targets / R:R / sizing.

---

## License

MIT — do whatever you want with it, including adding your own framework docs and protocols.
