# Index Flow & Positioning — gamma, VIX structure, sentiment, breadth

> Part of the [scan protocol](../scan-rules.md). See also: [data](data.md), [crypto-flow.md](crypto-flow.md), [fx-flow.md](fx-flow.md), [commodity-flow.md](commodity-flow.md).

---

This doc is the **indices analogue** of `crypto-flow.md`. Triggered when `/scan` runs against SPX, NDX, RUT, DJI, or major broad-market ETFs (SPY, QQQ, IWM, DIA). Specifically NOT for sector ETFs (those skip the 6-pillar — basket-level scoring isn't valid — and read constituent narrative qualitatively instead).

The technical read on the index chart is still primary. Flow & positioning is supplementary — strongest when it CONFIRMS the chart (e.g. weekly rejection at descending MA + dealer short-gamma + VIX backwardation = real risk-off, not noise).

---

## Why gamma matters most (index-specific)

Per [`docs/positioning.md` § Dealer gamma exposure](../../docs/positioning.md#dealer-gamma-exposure) — positive vs negative regime, walls, vol trigger, VIX-complex confirmation.

For indices, dealer gamma exposure (GEX) is the single most important structural signal a day-trader can read — the zero-gamma flip is the framework's most important single index level. Operational reading procedure (chrome-devtools captures + source URLs) lives in Tier A/B below.

---

## Two-tier capture (mirrors crypto)

### Tier A — WebFetch (always pull, parallel)

| Metric | Source | URL pattern | Lag |
|---|---|---|---|
| **AAII Sentiment Survey** (bull / neutral / bear %) | aaii.com | `https://www.aaii.com/sentimentsurvey/sent_results` | weekly Wed |
| **CFTC COT — equity index futures** (S&P 500, NDX, RUT non-commercial net) | CFTC | `https://www.cftc.gov/dea/futures/deacmesf.htm` (links to Friday CSV) | weekly Tue 3:30pm ET (T+3 day lag) |
| **Macro regime cross-ref** | scanned/MACRO/current.md | local | last MACRO scan date |
| **Mempool / on-chain note** *(if you're scanning index near a regime-shift catalyst — useful breadth proxy via crypto correlation)* | mempool.space | `https://mempool.space/api/v1/difficulty-adjustment` | real-time |

**Notes on gaps:**
- **VIX, VIX9D, VIX3M, VIX6M term structure** — Yahoo VIX endpoints rate-limit (HTTP 503), Cboe dashboards are JS-only. **Pull these from the chart pipeline** instead — capture the Cboe VIX Central or TradingView VIX9D/VIX/VIX3M chart via chrome-devtools (Tier B). Cite values off the screenshot.
- **NAAIM Exposure Index** — the public page rotates URL paths; if `/programs/naaim-exposure-index/` 404s, search `naaim.org` for the current path or capture via screenshot.
- **Breadth (% above 50d/200d, advance/decline)** — finviz futures page sometimes works, but the most reliable read is from a TradingView TVC:MMTH / TVC:MMTW / TVC:UPVOL chart screenshot.
- **DailyFX / IG sentiment / TradingEconomics** all 403 / 503 frequently. Don't depend on them.

### Tier B — chrome-devtools screenshot (the bulk of index flow)

Index flow data lives in JS dashboards. Screenshot is the way.

| Metric | Source URL | Why screenshot |
|---|---|---|
| **VIX term structure** | [vixcentral.com](http://vixcentral.com/) (renders to volchart.io); fallback [TradingView VX1!/VX2! chart](https://www.tradingview.com/symbols/CBOE-VX1!/) | JS-rendered curve; values pulled from screenshot |
| **VVIX (vol of vol)** | [TradingView VVIX](https://www.tradingview.com/symbols/CBOE-VVIX/) | Real-time chart |
| **Cboe SKEW Index** | [Cboe SKEW dashboard](https://www.cboe.com/us/indices/dashboard/skew/) | JS-rendered |
| **Cboe equity P/C ratio** | [Cboe pcr-equity](https://www.cboe.com/us/options/market_statistics/daily/) | JS table |
| **SpotGamma free daily blog** | [spotgamma.com — daily article](https://spotgamma.com/) | Free article often cites zero-gamma + call/put walls in headline; full chart paid |
| **MenthorQ free dashboards** | [menthorq.com](https://menthorq.com/) | Rotating free reads — check homepage for current public dashboard |
| **Convex Value gamma dashboard** | [convexvalue.com](https://convexvalue.com/) | Free public visualizations of dealer GEX |
| **Tier1 Alpha weekly report** | [tier1alpha.com](https://tier1alpha.com/) | Free weekly PDF — gamma flip levels, dealer positioning summary |
| **GammaScalpers Twitter** | [twitter.com/GammaScalpers](https://twitter.com/GammaScalpers) | Daily gamma levels in tweets — chrome-devtools capture if the user wants it |
| **Breadth panel** | TradingView MMTH / MMTW / TICK / TRIN / VIX charts | Chart screenshot |

### Tier C — compute gamma ourselves (deferred build)

If we hit the limits of free reads, we can approximate dealer GEX from public SPX options data:

1. Fetch SPX options chain by strike (Yahoo Finance free with delay; Cboe DataShop public CSVs)
2. For each strike: compute Γ (Black-Scholes second derivative) × OI × 100 multiplier
3. Sign by call/put assumption: dealers long calls (positive gamma above price), short puts (negative below)
4. Integrate to find the zero-gamma flip level + visualize as a curve

**Output**: `scripts/compute_index_gamma.py <SYMBOL>` → writes `scanned/indices/<SYMBOL>/charts/<SYMBOL>_<YYYY-MM-DD>_gamma_computed.png` + a JSON of {flip_level, call_wall, put_wall, gamma_by_strike[]}.

**Not built yet.** Defer until indices are in active coverage and the Tier A + Tier B reads are insufficient. Tier B (SpotGamma / MenthorQ / Convex Value free reads) covers most cases.

---

## Squeeze tiering for indices

Adapted from `crypto-flow.md` § Squeeze tiering. Indices don't have "squeezes" the way crypto perps do, but **gamma regime + VIX structure + sentiment extremes** combine into an analogous structural-risk reading.

| Tier | Conditions |
|---|---|
| **High-vol risk-on** (gamma regime favors trend-up) | Positive-gamma regime AND VIX > VIX3M (backwardation) AND AAII bears > 50% AND breadth > 70% above 50d. **Counter-trend long bias** — fading the panic is positive-EV. |
| **High-vol risk-off** (gamma favors trend-down) | Negative-gamma regime AND VIX > VIX3M AND VVIX > 100 AND AAII bears > 50%. **Don't catch the knife** — moves extend; trend-aligned shorts work, counter-trend longs get run over. |
| **Stable range** (positive gamma + VIX contango) | Positive-gamma regime AND VIX3M > VIX (contango) AND VVIX < 90 AND AAII bulls 30–60%. **Mean-reversion regime** — sell tops, buy bottoms inside the call/put wall range. |
| **Squeeze risk** (positive gamma but stretched bull sentiment) | Positive-gamma + AAII bulls > 60% + put/call < 0.6 + VVIX rising into the print. Sentiment-driven reversal risk; cap directional sizing. |
| **Trend-up grind** (positive gamma + low vol + neutral sentiment) | Positive-gamma + VIX 12–15 + AAII bulls 30–50% + breadth healthy. **Default bullish drift regime.** Wait for catalysts, don't fight tape. |

The composite tier feeds the Action verdict's pattern slug. E.g.:
- **High-vol risk-off** → `200d-loss-trend-down` or `failed-bounce-short` short on the index, not counter-trend long
- **Stable range** → `range-no-edge` (Action = WAIT) or sell-top / buy-bottom inside walls
- **Squeeze risk** → `distribution-short` short on rejection

---

## Section template (paste into `current.md` for index scans)

```markdown
### Index Flow & Positioning

#### Gamma & dealer positioning (Tier B — captured via chrome-devtools)

![SpotGamma daily snapshot — YYYY-MM-DD](charts/<SYM>_<YYYY-MM-DD>_spotgamma.png)

| Level | Value | Source | Interpretation |
|---|---|---|---|
| Zero-gamma flip | $X | SpotGamma / Tier1 / Convex | Above = stabilizing dealer hedging; below = destabilizing |
| Call wall | $X | (same) | Magnetic resistance into nearest OPEX |
| Put wall | $X | (same) | Magnetic support into nearest OPEX |
| Volatility trigger | $X | (same) | Vol regime flip — accelerating vs damping |
| Current price vs flip | $X (above / below by Δ) | computed | Determines today's regime |

**Gamma regime read:** positive / negative / neutral (price within ±0.5% of flip).

#### VIX structure + skew (Tier B)

![VIX term structure — YYYY-MM-DD](charts/<SYM>_<YYYY-MM-DD>_vix_term.png)

| Gauge | Value | As of | Read |
|---|---|---|---|
| VIX9D | $X | T+0 | — |
| VIX | $X | T+0 | — |
| VIX3M | $X | T+0 | — |
| VIX6M | $X | T+0 | — |
| Term structure | contango / backwardation / flat | T+0 | Backwardation = stress regime |
| VVIX | $X | T+0 | >100 = real tail premium; <85 = complacency |
| SKEW | $X | T+0 | >130 = hedging demand for OTM puts |

#### Sentiment + positioning (Tier A)

| Gauge | Value | Source | As of | Read |
|---|---|---|---|---|
| AAII Bull / Neutral / Bear | X% / X% / X% | aaii.com | weekly Wed | Bear extreme > 50% = contrarian long; bull > 60% = squeeze risk |
| NAAIM Exposure | X% | naaim.org | weekly Thu | Active manager %; >100% = leveraged long, <30% = de-risked |
| CFTC COT — S&P 500 net non-commercial | <long-short> contracts | CFTC | weekly Tue (T+3 lag) | Net long extreme = positioning crowded |
| Cboe equity P/C ratio | X | Cboe | T+0 | <0.5 = bull extreme; >1.0 = bear extreme |

#### Breadth (Tier B chart screenshot)

| Gauge | Value | Read |
|---|---|---|
| % > 50d MA | X% | <30% = washout, >80% = overheated |
| % > 200d MA | X% | <40% = bear regime, >70% = bull regime |
| McClellan Oscillator | X | <-100 oversold, >+100 overbought |
| Advance/Decline ratio | X | <0.5 weak breadth, >2.0 strong |

#### Composite squeeze tier

**[High-vol risk-on / High-vol risk-off / Stable range / Squeeze risk / Trend-up grind]**

#### Cross-confluence with the chart read

[Does the chart's right-edge candle agree with the gamma regime? Does VIX backwardation confirm the chart's weekly rejection? If gamma flip is above price, do we expect a chart-based recovery to stall here?]
```

---

## Source-priority chain

For metrics with multiple sources:

- **Gamma flip + walls**: SpotGamma free article > Tier1 Alpha weekly PDF > MenthorQ free dashboard > Convex Value > GammaScalpers Twitter > compute via Tier C
- **VIX structure**: TradingView chart screenshot > vixcentral/volchart.io screenshot > Yahoo Finance (often 503)
- **Sentiment extreme**: AAII (works via WebFetch) > NAAIM > Cboe P/C
- **Positioning**: CFTC COT (Tue 3:30pm ET update; we get the prior Tue's data with 3-day lag — the only weekly free positioning source for indices)

---

## Rules

- **Capture gamma data on every index scan.** It IS the most important structural signal — skipping it is skipping the lens.
- **State the as-of date for every gamma level.** SpotGamma daily blog updates daily; Tier1 weekly. The level you cite must have a date.
- **Don't pretend Tier C exists yet.** When SpotGamma/MenthorQ/Convex are all unavailable, write `Gamma data unavailable this scan — chart-only read; flag for next rescan.` Don't fabricate levels.
- **Index scans don't get the Crypto Flow & Positioning section.** They get THIS section instead. Mutually exclusive.
