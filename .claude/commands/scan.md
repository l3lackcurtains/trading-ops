---
description: Universal scan — auto-detects asset class (stock / crypto / index / FX / commodity) and runs the matching protocol. With no args, regenerates scanned/INDEX.md.
---

Run a scan for: **$ARGUMENTS**

The protocol lives in `guide/scan/`. **Read these before starting if you haven't this session:**
- [`guide/scan/protocol.md`](../../guide/scan/protocol.md) — read-before-scan, knowledge-base boundary, rescan rotation, outcome resolution log
- [`guide/scan/structure.md`](../../guide/scan/structure.md) — folder layout, snapshot template, **Action verdict format (verb + slug + ASCII ladder + trade table)**, INDEX.md format
- [`guide/scan/tiers.md`](../../guide/scan/tiers.md) — coverage tiers (Pos / Swing / Day)
- [`guide/scan/scorecard.md`](../../guide/scan/scorecard.md) — 6-pillar definitions and gates
- [`guide/scan/style.md`](../../guide/scan/style.md) — tone, citation, scope, self-improvement loop

Plus the **technical-read knowledge base** (Step 6 below):
- [`docs/volume-profile.md`](../../docs/volume-profile.md) — POC / VAH / VAL / HVN / LVN, profile shapes, naked POC
- [`docs/vwap.md`](../../docs/vwap.md) — session / weekly / monthly / quarterly / anchored VWAP, ±σ bands

Plus the **flow doc that matches the asset class** (route via Step 0 below):
- [`guide/scan/data.md`](../../guide/scan/data.md) — STOCK sourcing chain
- [`guide/scan/crypto-flow.md`](../../guide/scan/crypto-flow.md) — CRYPTO flow & positioning
- [`guide/scan/index-flow.md`](../../guide/scan/index-flow.md) — INDEX flow & positioning + GAMMA
- [`guide/scan/fx-flow.md`](../../guide/scan/fx-flow.md) — FX flow & positioning (COT-centric)
- [`guide/scan/commodity-flow.md`](../../guide/scan/commodity-flow.md) — COMMODITY flow & positioning

If a step here ever conflicts with the guide, the guide wins. Open the fix there.

---

## Step 0 — No-args mode: regenerate INDEX.md

If `$ARGUMENTS` is empty:

1. Run `python3 scripts/regen_index.py` — parses every `current.md`'s `**Coverage tier:**` line + catalyst date, regenerates the master coverage table + focus blocks + catalyst monitor in `scanned/INDEX.md`.
2. Manually verify the Coverage changes log + Performance audit log are still intact (the script doesn't overwrite those — they're append-only).
3. Report what changed (added rows / tier transitions / new catalysts).

If the script fails, regenerate by hand per `structure.md` § INDEX.md format — walk every `scanned/<asset-class>/<TICKER>/current.md` for the Coverage tier line + last-scan date + score + next catalyst, and rebuild the tables.

**Stop here when in no-args mode. The remaining steps apply only when scanning a specific symbol.**

---

## Step 1 — Asset-class detection

Parse `$ARGUMENTS`:

- **Optional `--type` flag**: if present (`--type=stock`, `--type=crypto`, `--type=index`, `--type=fx`, `--type=commodity`), use it as an explicit override. Strip the flag from the symbol.
- **Otherwise auto-detect** by symbol shape:

| Heuristic | Asset class | Folder | Flow doc |
|---|---|---|---|
| Pair ends in `USDT` / `USD` / `USDC` / `BTC` / `ETH` (e.g. `BTCUSDT`, `ETHUSD`, `SOLUSDC`) | crypto | `scanned/crypto/<SYMBOL>/` | [`crypto-flow.md`](../../guide/scan/crypto-flow.md) |
| 6-letter pair where each half is a known currency code (`EURUSD`, `USDJPY`, `GBPCHF`, etc.) | FX | `scanned/fx/<SYMBOL>/` | [`fx-flow.md`](../../guide/scan/fx-flow.md) |
| `SPX` / `NDX` / `RUT` / `DJI` / `NDQ` / `IXIC` / `COMP` / `OEX` / `VIX` / `VVIX` / `SKEW` / `DXY`, OR broad-market ETFs (`SPY` / `QQQ` / `IWM` / `DIA` / `VTI` / `VOO`) | index | `scanned/indices/<SYMBOL>/` | [`index-flow.md`](../../guide/scan/index-flow.md) |
| Commodity futures (`CL` / `BZ` / `NG` / `GC` / `SI` / `HG` / `ZC` / `ZS` / `ZW`) OR commodity ETFs (`USO` / `BNO` / `UNG` / `USL` / `GLD` / `IAU` / `SLV` / `PPLT` / `GDX` / `GDXJ` / `DBA` / `CORN` / `SOYB` / `WEAT` / `JJG` / `DBB` / `COPX` / `CPER`) | commodity | `scanned/commodities/<SYMBOL>/` | [`commodity-flow.md`](../../guide/scan/commodity-flow.md) |
| Sector ETFs (`XLE` / `XLK` / `XLF` / `XLV` / `XLI` / `XLP` / `XLY` / `XLU` / `XLRE` / `XLB` / `XLC`) | stock-template (no 6-pillar applies via underlying) | `scanned/indices/<SYMBOL>/` | use [`data.md`](../../guide/scan/data.md) but skip 6-pillar/earnings |
| Anything else (1–5 letter US ticker, dual-class with dot suffix like `BRK.B`) | stock | `scanned/stocks/<TICKER>/` | [`data.md`](../../guide/scan/data.md) |

**Ambiguous cases — ask the user before proceeding:**
- Bare 3-letter symbol that could be currency or stock (`USD`, `EUR`, `JPY`)
- Symbol that overlaps a known stock and a known commodity (e.g. `GOLD` = Barrick Gold the stock; `GLD` = the gold ETF — these are different but if user types `GOLD` ambiguously, ask)
- Symbol you don't recognize — ask, don't guess

The detection test: *"Does the 6-pillar fundamentals scorecard apply?"* If yes → stock template; if no → asset-class flow doc applies.

**Once asset class is determined**, the rest of the steps differ. Stocks follow the full 6-pillar + Flow & Squeeze + earnings path; crypto/index/fx/commodity follow the asset-class flow doc with NO 6-pillar/earnings.

---

## Step 2 — Read-before-scan (all asset classes)

Per [`protocol.md`](../../guide/scan/protocol.md) § Read-before-scan:

1. Read prior `current.md` (if exists) and 2–3 most recent archive snapshots. Capture prior **Coverage tier** + **Action verdict** + **trigger specs** for tier-change comparison and outcome resolution.
2. Read `scanned/MACRO/current.md` for current regime context. If older than 7 days, warn user and offer `/rescan macro` first.

---

## Step 3 — Rotate + create folder

- If prior `current.md` exists: rotate to `archive/<prior-scan-date>.md` and prune per `protocol.md` § Retention policy (or `scripts/prune_archive.py`).
- If folder doesn't exist: create `<target-folder>/archive/`.

---

## Step 4 — Pull data (asset-class-specific)

### Stock (`/scan AAPL`, `/scan NIO`, etc.)

Per [`data.md`](../../guide/scan/data.md):
- **Finviz quote page** (one WebFetch) — price, MAs, 6-pillar inputs, ownership, short interest, next earnings, analyst rec
- **Stockanalysis** for FCF / balance-sheet detail
- **13F holders** — WhaleWisdom → HedgeFollow → Fintel; if all fail, mark `unavailable`
- **Dataroma** for superinvestor coverage
- **Insider Form 4** — OpenInsider → Finviz insider page
- **WebSearch** for catalysts / news
- **ChartExchange Flow & Squeeze** in parallel (5 URLs: dark pool, max pain, short interest, FTD, borrow fee)

### Crypto (`/scan BTCUSDT`, `/scan ETHUSDT`, etc.)

Per [`crypto-flow.md`](../../guide/scan/crypto-flow.md):
- **Tier A (WebFetch in parallel)**: alternative.me F&G, CoinGecko global + per-coin, OKX funding rate + open interest, Deribit options OI, Bitbo daily ETF flows, mempool.space difficulty/hashrate
- **Tier B (chrome-devtools captures)**: Coinglass funding dashboard, liquidation heatmap, options max pain by expiry

### Index (`/scan SPX`, `/scan NDX`, etc.)

Per [`index-flow.md`](../../guide/scan/index-flow.md):
- **Tier A**: AAII Sentiment Survey, CFTC COT (equity index futures), MACRO cross-ref
- **Tier B (chrome-devtools)**: VIX term structure, VVIX, SKEW, breadth, **gamma exposure** (SpotGamma free daily blog, Tier1 Alpha weekly PDF, MenthorQ free dashboards, Convex Value, GammaScalpers Twitter)

### FX (`/scan EURUSD`, `/scan USDJPY`, etc.)

Per [`fx-flow.md`](../../guide/scan/fx-flow.md):
- **Tier A**: CFTC COT (CME FX futures — primary), Forex Factory calendar, rate differentials (TradingEconomics)
- **Tier B**: IG / MyFXBook retail sentiment, OANDA orderbook, TradingView 2yr yield differential chart

### Commodity (`/scan USO`, `/scan GLD`, etc.)

Per [`commodity-flow.md`](../../guide/scan/commodity-flow.md):
- **Tier A**: CFTC COT, EIA inventory (energy), USDA WASDE (grains), WGC Goldhub (gold), MACRO cross-ref
- **Tier B**: futures curve shape, COMEX/LME warehouse, Baker Hughes rigs, seasonality chart

---

## Step 5 — 6-Pillar Scorecard (STOCKS ONLY — skip for non-stocks)

Per [`scorecard.md`](../../guide/scan/scorecard.md). Score each PASS / FAIL / NEUTRAL with explicit numbers; aggregate /6; check auto-reject flags.

---

## Step 6 — Technical read: Volume Profile + VWAP

Methodology lives in [`docs/volume-profile.md`](../../docs/volume-profile.md) and [`docs/vwap.md`](../../docs/vwap.md). Read both if you haven't this session.

**Pre-compute the numeric layer first.** Run:
```
.venv/bin/python scripts/fetch_ohlc.py <SYMBOL> --timeframes W,D,4H,1H [--anchor YYYY-MM-DD]
```
This returns per-timeframe: EMAs, ATR, RSI, vol×20avg, **VWAP family** (session / weekly / monthly / quarterly / anchored, with ±1σ / ±2σ bands), and **Volume Profile** (POC, VAH, VAL, HVN, LVN, current position vs Value Area). Pass `--anchor <date>` for the most relevant pivot (recent swing high/low, earnings gap, FOMC, IPO, YTD open, post-split).

**Three horizon sub-sections required.** Each uses the timeframes most relevant to its hold period:

### Positional (W + M + D)
- **EMA stack** posture: 20 / 50 / 200 alignment
- **VWAP**: monthly + quarterly + anchored (e.g. anchor to YTD open or last earnings gap; name the cohort behind the anchor: "earnings = post-print institutional cost basis"; "IPO = every public shareholder"; "YTD open = the calendar-year cohort")
- **Volume Profile**: composite over 250+ days (lookback flag in fetch_ohlc.py: `--bars 250 --timeframes D`); POC / VAH / VAL; naked POCs from prior years
- **Profile shape** (D / P / b / B / multi-modal per [`docs/volume-profile.md` § Profile shapes](../../docs/volume-profile.md#profile-shapes) — the section anchor must be verified) and the next-session bias from the shape. **Value-area migration** vs prior session (up / down / overlap / outside).
- **Position vs value area**: above VAH / in value / below VAL — informs thesis durability
- If `--anchor` was set, evaluate **AVWAP reclaim / lose** since prior scan.
- **Posture verdict** (1 line)

### Swing (D + 4H)
- **EMAs**, **VWAP** (weekly + monthly), **Volume Profile** (last 4–6 weeks daily VRVP)
- **Key levels**: nearest HVN above, nearest HVN below, any LVN gap that would cause fast travel
- **VWAP slope** + distance from VWAP in σ-units
- **Reclaim / lose** of weekly or monthly VWAP since last scan. If `--anchor` was set, evaluate **AVWAP reclaim / lose** since prior scan.
- **Profile shape** (D / P / b / B / multi-modal per [`docs/volume-profile.md` § Profile shapes](../../docs/volume-profile.md#profile-shapes) — the section anchor must be verified) and the next-session bias from the shape. **Value-area migration** vs prior session (up / down / overlap / outside).
- **Posture verdict** + best entry/stop framed against POC, VAH, VAL, or AVWAP

### Day-trade (1H + 15m / session)
- **Session VWAP** + ±1σ / ±2σ bands (intraday only — session resets at the cash open). **Session character** (Trend up / Trend down / Range / Consolidation→breakout / Reclaim per `docs/vwap.md` § Session character) — determines whether to fade or ride σ-band tags.
- **Volume Profile** of the current session — developing POC (note **drift** up/down/stable), value area position vs yesterday's (**migration**: up / down / overlap / outside).
- **VWAP × VP confluence**: where the session VWAP sits relative to the developing POC; band touches as fade or continuation
- **Posture verdict** + intraday entry/stop framed in σ-units of session VWAP

**Anchor every observation** to timeframe + date. **Use `≈$X` (not `~$X`)** for approximate values inside tables to avoid strikethrough rendering.

**Confluence is the unit of conviction.** A level becomes high-conviction when at least two of {anchored VWAP, session VWAP, POC, VAH, VAL, HVN, prior-period naked POC} cluster within ~0.3 ATR of each other. Cite the cluster components inline.

---

## Step 7 — Regime fit

Read `scanned/MACRO/current.md` quadrant; note favored / hostile / neutral with one-line reason per horizon. Regime gates Pos strongly, Swing moderately, Day-trade barely.

---

## Step 8 — Asset-class flow & positioning section

Apply EXACTLY ONE flow doc based on Step 1's asset-class detection:

- **Stock** → `data.md` § ChartExchange section template
- **Crypto** → `crypto-flow.md` § section template (Tier A numerics + Tier B captures)
- **Index** → `index-flow.md` § section template (gamma, VIX structure, sentiment, breadth)
- **FX** → `fx-flow.md` § section template (COT, retail sentiment, rate diffs)
- **Commodity** → `commodity-flow.md` § section template (COT, inventory, curve, seasonality)

The four non-stock flow docs are **mutually exclusive** — never apply two. Stocks don't get any of the four — they use ChartExchange.

---

## Step 9 — Earnings setup (STOCKS ONLY, when next earnings within 90 days)

8-point checklist + max-pain interplay.

---

## Step 10 — Trade plan: three parallel mini-plans

Per `structure.md` § Trade plan structure. Any horizon can be `N/A` when its tier is **S** / `—`. Use absolute dates everywhere.

---

## Step 11 — Action verdict (REQUIRED, structured format per `structure.md`)

Three components in order:

**(a) Per-horizon verb + 1-line trigger spec.** Verbs: `LONG` / `SHORT` / `HOLD` / `ADD` / `TRIM` / `HEDGE` / `CALL` / `PUT` / `WAIT` / `N/A`.

**(b) ASCII price ladder** — fenced ` ```text` block, prices descending top→bottom, current price marked with `>>` and `***`, upside/downside paths separated by `- - -`. ASCII-only glyphs.

**(c) Trade table** — explicit Entry / Stop / T1 / T2 / T3 / R:R (computed) / Sizing / Time-stop columns, one row per actionable plan.

---

## Step 12 — Coverage tier per horizon

Per [`tiers.md`](../../guide/scan/tiers.md). Tradeable instruments get full Pos/Swing/Day tiers (stocks AND crypto AND single FX pairs we trade AND single indices/commodities we trade). Pure trackers get `—` across.

Write the line in the snapshot header:
```markdown
**Coverage tier:** Pos **S** (auto-reject) · Swing **W** (May 5 binary) · Day — (no 1H)
```

---

## Step 13 — Verdict per horizon + dominant horizon

Name the dominant horizon for this scan and list upgrade/downgrade conditions per horizon.

---

## Step 14 — Save

Save new snapshot to `<target-folder>/current.md` (Step 1 determined the target).

---

## Step 15 — Update `scanned/INDEX.md`

Per `tiers.md` § Tier-change protocol:
- Always update master coverage table row + per-horizon focus blocks (or Macro/Indices/FX section for non-stocks)
- For each horizon where the tier changed, append a row to § Coverage changes — last 30 days
- For each prior trigger that resolved (fired-correct / fired-stopped / invalidated / stale), append a row to § Performance / audit log per `protocol.md` § Outcome resolution log format
- First scans = `Initiated` with Horizon=All
- Or run `python3 scripts/regen_index.py` to rebuild the master table from all `current.md` Coverage tier lines

---

## Step 16 — Self-improvement loop

Per `style.md` § Process self-improvement — if you encountered a process problem during the scan (broken URL, wrong filter, ambiguous step), surface it as `## Process improvement suggestions` at the end of your reply (NOT in the saved scan file). Wait for user consent before editing `guide/` or `.claude/commands/`.

---

## Quick reference

| Invocation | What it does |
|---|---|
| `/scan` | Regenerate `scanned/INDEX.md` |
| `/scan AAPL` | Stock scan (auto-detected) |
| `/scan BTCUSDT` | Crypto scan (auto-detected) |
| `/scan SPX` | Index scan with gamma (auto-detected) |
| `/scan EURUSD` | FX scan with COT (auto-detected) |
| `/scan GLD` | Commodity scan (auto-detected) |
| `/scan MSTR --type=crypto` | Override — treat as crypto-correlated proxy |
| `/scan UNKNOWN_TICKER` | Asks before proceeding |
