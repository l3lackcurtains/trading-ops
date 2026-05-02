---
description: Partial scan — refresh ONLY the asset-class flow & positioning section of an existing current.md (Flow & Squeeze for stocks, Crypto/Index/FX/Commodity Flow for non-stocks). Does not re-run charts, 6-pillar, or earnings.
---

Refresh flow & positioning for: **$ARGUMENTS**

Use this when fresh flow data dropped (ETF flows post-close, weekly COT release Tuesday afternoon, EIA inventory Wednesday, OPEX gamma rebalance) but the chart hasn't moved enough to warrant a full re-scan.

The protocol lives in `guide/scan/`. **Read these before starting:**
- [`guide/scan/protocol.md`](../../guide/scan/protocol.md) — read-before-scan, partial-scan pattern
- [`guide/scan/structure.md`](../../guide/scan/structure.md) — Action verdict format (flow may shift triggers)
- The asset-class flow doc that matches the symbol:
  - **Stock** → [`guide/scan/data.md`](../../guide/scan/data.md) § ChartExchange Flow & Squeeze
  - **Crypto** → [`guide/scan/crypto-flow.md`](../../guide/scan/crypto-flow.md)
  - **Index** → [`guide/scan/index-flow.md`](../../guide/scan/index-flow.md)
  - **FX** → [`guide/scan/fx-flow.md`](../../guide/scan/fx-flow.md)
  - **Commodity** → [`guide/scan/commodity-flow.md`](../../guide/scan/commodity-flow.md)

Plus `scanned/LESSONS.md` (required).

## Steps

### 1. Pre-flight

1. Detect asset class from symbol — stock (`scanned/stocks/`), crypto (`scanned/crypto/`), index (`scanned/indices/`), FX (`scanned/fx/`), commodity (`scanned/commodities/`).
2. Locate `<target-folder>` (`scanned/<asset-class>/<SYMBOL>/`).
3. **Verify `current.md` exists.** If not, tell the user to run `/scan <SYMBOL>` first, and stop.
4. Read existing `current.md` — capture header, Action verdict, TL;DR, **the existing flow section** (so we know what to replace), and everything else.
5. Read `scanned/MACRO/current.md` and `scanned/LESSONS.md`.

### 2. Pull flow data (asset-class-specific)

Apply EXACTLY ONE flow protocol based on Step 1's detection:

**Stock** — per `data.md`:
- ChartExchange in parallel: dark pool, max pain, short interest, FTD, borrow fee
- State "as of" dates and lag floors

**Crypto** — per `crypto-flow.md`:
- Tier A WebFetch in parallel: alternative.me F&G, CoinGecko, OKX funding/OI, Deribit options, Bitbo ETF flows, mempool.space
- Tier B chrome-devtools captures: Coinglass funding dashboard, liquidation heatmap, options max pain

**Index** — per `index-flow.md`:
- Tier A: AAII Sentiment Survey, CFTC COT (equity index futures)
- Tier B chrome-devtools: VIX term structure, VVIX, SKEW, SpotGamma free daily blog, Tier1 Alpha, MenthorQ, Convex Value, breadth chart

**FX** — per `fx-flow.md`:
- Tier A: CFTC COT (CME FX futures), Forex Factory calendar, rate differentials
- Tier B: IG / MyFXBook retail sentiment

**Commodity** — per `commodity-flow.md`:
- Tier A: CFTC COT, EIA petroleum/NG storage (energy), USDA WASDE (grains), WGC Goldhub (gold)
- Tier B: futures curve, COMEX/LME warehouse, Baker Hughes rigs, seasonality

### 3. Replace flow section in `current.md`

- Find the existing flow section (titled `### Flow & Squeeze (ChartExchange)` for stocks, or `### Crypto Flow & Positioning`, `### Index Flow & Positioning`, `### FX Flow & Positioning`, `### Commodity Flow & Positioning` for non-stocks).
- Replace with the freshly populated section per the matching flow doc's section template.
- Leave **everything else** in `current.md` verbatim (technical read, 6-pillar, earnings, trade plan, etc.).

### 4. Recompute Action verdict if flow triggered

If the new flow data changes the calculus (post-flush state confirmed → bear cascade case softens; squeeze tier upgrades from Moderate to High → asymmetric upside; max-pain expiry passed → magnetic level changed):

- Update the **Action verdict** section per `structure.md`.
- Update **Coverage tier** if a horizon's tier changed.

If flow data confirms existing read with no material change, leave Action + tier alone.

### 5. Update header + Δ marker

- Update `## Snapshot — YYYY-MM-DD` date.
- If flow read materially changed, prepend TL;DR:
  ```
  **Δ since prior section update (YYYY-MM-DD HH:MM):** Flow & positioning updated — <what changed>
  ```

### 6. Append to Section update log

In the `## Section update log` block at the bottom (create if absent):

| Date (UTC) | Section refreshed | Trigger | Outcome |
|---|---|---|---|
| YYYY-MM-DD HH:MM | Flow & Positioning | <why ran — e.g. "Tue COT release" / "EIA Wed inventory" / "post-OPEX gamma reset" / "ETF flow daily print"> | <verdict change or "no change"> |

Cap log at 10 entries; drop oldest.

### 7. Save + skip rotation

Replace flow section in `current.md`. Do NOT rotate to archive (full-state archive is `/rescan` only).

### 8. Update INDEX.md only if tier changed

Per `tiers.md` § Tier-change protocol. Otherwise INDEX.md untouched.

### 9. Self-improvement loop

Per `style.md`.

---

## Quick reference

| Invocation | What it pulls |
|---|---|
| `/scan-flow AAPL` | ChartExchange Flow & Squeeze (max pain, dark pool, SI, FTD, borrow fee) |
| `/scan-flow BTCUSDT` | F&G, ETF flows, perp funding/OI, options max pain, liquidation heatmap, network state |
| `/scan-flow SPX` | Gamma exposure (zero-flip / call / put walls), VIX structure, AAII / NAAIM, breadth, COT |
| `/scan-flow EURUSD` | CFTC COT, retail sentiment, rate diffs, Forex Factory calendar |
| `/scan-flow USO` | CFTC COT, EIA petroleum status, futures curve, Baker Hughes rigs, seasonality |

When to use:
- Tuesday 3:30pm ET — fresh CFTC COT release (FX, commodity, index)
- Wednesday 10:30am ET — EIA petroleum inventory (energy commodities)
- Thursday 10:30am ET — EIA NG storage report (NG)
- Daily after-hours — Bitbo ETF flow update for crypto
- Daily — SpotGamma blog refresh for indices
- Post-OPEX (3rd Friday or end-of-month) — gamma reset for indices

When NOT to use:
- Chart shifted intraday → `/rescan` instead
- Brand new symbol with no `current.md` yet → `/scan <SYMBOL>`
- Major macro catalyst → `/rescan` for full state refresh
