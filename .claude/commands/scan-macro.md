---
description: Top-down macro/regime scan. Saves to scanned/MACRO/current.md
---

Run a macro / regime scan.

Protocol in [`guide/scan/`](../../guide/scan/). Read [`structure.md`](../../guide/scan/structure.md), [`data.md`](../../guide/scan/data.md), [`style.md`](../../guide/scan/style.md) before starting if not loaded.

## Steps

1. **Read-before-scan** per `protocol.md` — read prior `scanned/MACRO/current.md` fully. Capture prior quadrant, key gauges, scenario tree, and any "watch for" triggers. Identify if prior triggers fired (NFP / CPI / FOMC dates passed).

2. **Rotate** prior `scanned/MACRO/current.md` to `scanned/MACRO/archive/<prior-scan-date>.md` and prune per `protocol.md` § Retention policy.

3. **Pull macro data** per `data.md` — one source per gauge:
   - **SPX / NDX / Russell** — TradingView or MarketWatch
   - **VIX** — Cboe / TradingEconomics
   - **CNN F&G** — cnn.com/markets/fear-and-greed
   - **DXY** — TradingEconomics / Investing
   - **10Y / 2Y / curve** — FRED (US10Y, US02Y) or Treasury.gov
   - **Fed funds + dot plot** — Federal Reserve / CNBC FOMC summary
   - **CPI / PCE / NFP / GDPNow** — BLS / BEA / Atlanta Fed
   - **Recent prints** — WebSearch for `<event> <month> <year>`

   No-duplication rule applies (`data.md`).

4. **Run framework** per [`docs/macro.md`](../../docs/macro.md) — sections in order:
   - TL;DR (quadrant + index-tape read + bias)
   - Key gauges table
   - Macro pillars (Growth × Inflation × Liquidity)
   - Quadrant placement + best/worst assets
   - Index-tape read (W/D of SPX or NDX — trend, MA structure, key levels)
   - Context modifiers (rate cycle, geopolitics, anchoring, election)
   - Bubble / fragility flags — per `docs/macro.md` § Bubble indicators: Buffett Indicator with bands (75–90% reasonable, >120% overvalued, >146% pre-dot-com peak), margin debt / GDP trend, Mag-7 concentration, equal-weight (RSP) vs cap-weighted (SPY), AI capex contribution to GDP.
   - NDX/SPX scenario tree (3 scenarios with prob + targets)
   - Sector preferences (favored / underweight)
   - Catalysts watch list (next 30 days)
   - Trade framework
   - Sources

5. **Optional charts** — if a chart capture is useful, save to `scanned/MACRO/charts/` and embed inline.

6. **Δ marker** if the regime / quadrant / scenario probabilities changed since prior scan. See `structure.md`.

7. **Save** to `scanned/MACRO/current.md`, dated today.

8. **Update `scanned/INDEX.md`** Macro / Indices / FX section with new quadrant + key bias note. MACRO doesn't get Pos/Swing/Day tiers (it's a tracker, not a tradeable name).
