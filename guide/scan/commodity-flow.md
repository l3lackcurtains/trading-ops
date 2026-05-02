# Commodity Flow & Positioning — COT, inventory cycles, futures curve, seasonality

> Part of the [scan protocol](../scan-rules.md). See also: [data](data.md), [crypto-flow.md](crypto-flow.md), [fx-flow.md](fx-flow.md), [index-flow.md](index-flow.md).

---

This doc is the **commodities analogue** of `crypto-flow.md`. Triggered when `/scan` runs against:

- **Energy**: USO, BNO, UNG, USL, CL futures, BZ futures, NG futures
- **Metals**: GLD, IAU, SLV, PPLT, GDX, GDXJ, HG futures, GC futures, SI futures
- **Agricultural**: DBA, CORN, SOYB, WEAT, JJG
- **Industrial**: DBB, COPX, CPER

The chart read is still primary. Commodity-specific positioning + inventory cycles + curve shape supplement it. **Commodities have stronger seasonality than equities or crypto** — always note the calendar context.

---

## Why commodity flow looks different

Per [`docs/positioning.md` § CFTC Commitments of Traders](../../docs/positioning.md#cftc-commitments-of-traders-cot) — trader categories, standard reads, and what COT does and doesn't capture.

Commodities have three structural signals that don't exist for equities/crypto:

1. **COT** (same source as FX, different report) — for commodities, **commercials ARE the producers/end-users** (oil majors, grain elevators, miners) hedging actual physical exposure; that's the asset-class twist on the COT framework. The commercial-vs-non-commercial divergence read is the high-signal commodity-specific lens.
2. **Physical inventory cycles** — EIA weekly petroleum status (Wed 10:30am ET), USDA WASDE monthly, COMEX/LME warehouse stocks. Inventory builds = bearish for spot; draws = bullish.
3. **Futures curve shape** — backwardation (front-month > back-month) signals supply tightness; contango signals oversupply or storage demand. Curve flips are major regime signals.

Plus seasonality: heating oil in winter, gasoline in summer driving season, grains around planting/harvest, gold around Diwali/Lunar New Year.

---

## Two-tier capture

### Tier A — WebFetch (always pull)

| Metric | Source | URL pattern | Lag |
|---|---|---|---|
| **CFTC COT** (commodity-specific) | CFTC | `https://www.cftc.gov/dea/futures/deacmesf.htm` (CME); for non-CME (NYMEX, COMEX, ICE), `deanybtsf.htm` / `deacmsf.htm` etc. | weekly Tue 3:30pm ET (T+3 lag) |
| **EIA Weekly Petroleum Status** *(crude/products only)* | EIA dnav direct (primary) | `https://www.eia.gov/dnav/pet/pet_stoc_wstk_dcu_nus_w.htm` (commercial crude inventory + 4-week trend); fallback `https://www.eia.gov/petroleum/supply/weekly/` for the analyst-commentary side-text only — the `/petroleum/weekly/` index page returns navigation, not data | weekly Wed 10:30am ET (T+1 day from Fri) |
| **EIA Natural Gas Storage Report** *(NG only)* | EIA | `https://ir.eia.gov/ngs/ngs.html` | weekly Thu 10:30am ET |
| **USDA WASDE** *(grains only)* | USDA | `https://www.usda.gov/oce/commodity/wasde` | monthly (typically 9th-12th) |
| **WGC Goldhub** *(gold only)* | World Gold Council | `https://www.gold.org/goldhub/data` | quarterly demand/supply, monthly ETF flows |
| **Macro regime cross-ref** | scanned/MACRO/current.md | local | last MACRO scan |

### Tier B — chrome-devtools screenshot

| Metric | Source URL | What we capture |
|---|---|---|
| **Futures curve shape** | [Barchart futures curve](https://www.barchart.com/futures/quotes/CL*0/futures-prices) (primary — substitute the symbol root for non-crude: `NG*0`, `GC*0`, `SI*0`, `HG*0`, `ZC*0`, etc.); fallback TradingView CME/ICE futures chain. **Avoid** `cmegroup.com/markets/energy/crude-oil/light-sweet-crude.quotes.html` — heavy JS render, frequently 60s timeouts | Front-month → 12mo curve; flag backwardation/contango |
| **COMEX warehouse stocks** *(metals only)* | [comex.cmegroup.com](https://www.cmegroup.com/markets/metals.html) | Daily warehouse changes |
| **LME warehouse stocks** *(industrial metals)* | [LME data](https://www.lme.com/Market-data) | Stock cancellations + cancelled warrants |
| **Seasonality chart** | Seasonax / Equityclock for the specific commodity | Visual seasonal pattern overlay |
| **Baker Hughes rig count** *(oil/gas only)* | [oilprice.com/rig-count](https://oilprice.com/rig-count) (primary — clean aggregator, returns total US / oil / gas rigs + WoW change reliably); fallback [bakerhughesrigcount.gcs-web.com](https://bakerhughesrigcount.gcs-web.com/rig-count-overview) — the IR site frequently 60s-times out | Weekly Fri 1pm ET; activity proxy |
| **Goldhub ETF flows visual** *(gold)* | [gold.org goldhub](https://www.gold.org/goldhub/data) | Monthly ETF inflow/outflow chart |

---

## Squeeze tiering for commodities

Adapted from `crypto-flow.md`. Commodity squeezes are real but slow — they unfold over weeks (storage hoarding, OPEC supply shocks), not minutes. Tiers:

| Tier | Conditions |
|---|---|
| **Supply squeeze (bullish)** | Backwardation deepening AND inventory drawing >2σ for 3+ consecutive weeks AND non-commercial net rising | Trend-up continuation; long-bias |
| **Storage glut (bearish)** | Contango widening AND inventory building >2σ for 3+ consecutive weeks AND non-commercial net falling | Trend-down continuation; short-bias |
| **Crowded long (mean-revert risk)** | Non-commercial net at 3-yr high AND retail/spec long extreme AND no fresh fundamental driver | Pullback risk |
| **Crowded short (mean-revert risk)** | Non-commercial net at 3-yr low AND inventory turning vs trend | Squeeze higher possible |
| **Range** | COT and curve both stable; range-bound chart | Wait |

---

## Section template (paste into `current.md` for commodity scans)

```markdown
### Commodity Flow & Positioning

#### Institutional positioning (CFTC COT — Tier A)

| Metric | Value | As of | Read |
|---|---|---|---|
| Non-commercial NET (longs − shorts) | <X> contracts | YYYY-MM-DD (T+3 lag) | Long-extreme / short-extreme / neutral |
| Non-commercial 4-week change | +/-X | — | Building or unwinding |
| Commercial NET (producers/end-users) | <X> contracts | — | Smart-money hedge direction |
| Open interest 4-week change | +/-X% | — | OI rising = conviction; falling = de-leverage |

#### Inventory + supply (Tier A — when applicable)

| Report | Value | Δ vs prior | vs 5y avg | Read |
|---|---|---|---|---|
| EIA crude inventory | <X> kbbl | +/-X | +/-X% | Build/draw |
| EIA gasoline inventory | <X> kbbl | +/-X | +/-X% | — |
| EIA NG storage | <X> bcf | +/-X | +/-X% | — |
| USDA ending stocks (corn/soy/wheat) | <X> mbu | +/-X | +/-X% | — |
| Baker Hughes rig count | <X> | +/-X | — | Activity proxy |
| COMEX/LME warehouse | <X> | +/-X | — | Physical tightness |

#### Futures curve (Tier B — screenshot)

![<COMMODITY> futures curve — YYYY-MM-DD](charts/<SYM>_<YYYY-MM-DD>_curve.png)

| Spread | Value | Read |
|---|---|---|
| M1 − M2 | $X | Backwardation if >0; contango if <0 |
| M1 − M6 | $X | Term-structure premium |
| M1 − M12 | $X | Long-cycle anchor |
| Curve regime | backwardation / contango / mixed | Supply-tightness signal |

#### Seasonality

![<COMMODITY> seasonal pattern — YYYY-MM-DD](charts/<SYM>_<YYYY-MM-DD>_seasonal.png)

- Current calendar position: <quarter / month / season>
- Typical seasonal bias: <bullish/bearish> Δ in this window over last 5y
- Current vs seasonal: tracking / diverging

#### Composite tier

**[Supply squeeze / Storage glut / Crowded long / Crowded short / Range]**

#### Cross-confluence with the chart read

[Does COT institutional positioning agree with chart's right-edge candle? Does inventory cycle confirm chart's base or peak structure? Does curve shape match seasonality?]
```

---

## Source-priority chain

- **Positioning**: CFTC COT (one source, one report — don't duplicate)
- **Inventory**: EIA (energy), USDA (grains), COMEX/LME (metals) — use the asset-specific official source
- **Curve**: TradingView futures chain screenshot > Barchart > CME website
- **Seasonality**: Seasonax > Equityclock > computed from your own back data

---

## Rules

- **COT is non-optional** for every commodity scan.
- **Inventory cycle is non-optional when applicable** — energy and grain scans without an EIA/USDA read are incomplete.
- **Note seasonality calendar position.** Commodity chart reads without seasonal context miss the structural driver.
- **Commercial COT direction overrides non-commercial extremes** when the spot driver is fundamental — producers selling forward into a price spike is a real distribution signal even if specs are flat.
- **Commodity scans don't get Crypto Flow / Index Flow / FX Flow sections.** They get THIS section. Mutually exclusive.
