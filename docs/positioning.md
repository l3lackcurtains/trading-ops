# Positioning — cross-asset short-interest, dealer-gamma, and futures-trader frameworks

This doc anchors the positioning concepts the scan flow sections rely on. Each asset class has its own positioning vocabulary (equity short interest, crypto perp funding, index dealer gamma, futures COT) but the underlying logic — *who is crowded, who is forced, what catalyst flips the bid* — is shared. The framework lives here; the per-asset application lives in `guide/scan/<asset-class>-flow.md`.

## Table of contents

1. [Equity squeeze tier](#equity-squeeze-tier)
2. [Dealer gamma exposure](#dealer-gamma-exposure)
3. [CFTC Commitments of Traders (COT)](#cftc-commitments-of-traders-cot)

---

## Equity squeeze tier

The squeeze tier composite combines four numeric inputs into a Low / Moderate / High / Extreme classification. It tells you whether shorts are *crowded* (positioning signal), *forced* (mechanical squeeze fuel), or both.

### Inputs

| Input | What it measures | Where to read |
|---|---|---|
| Short interest (% of float) | Crowdedness — how much of the float is sold short | FINRA bi-monthly, ChartExchange / Finviz |
| Days to cover (DTC) | How long shorts need to unwind at average daily volume | Computed: SI shares ÷ avg daily volume |
| Borrow fee (CTB %) | Mechanical pressure — what shorts pay daily to stay short | iBorrowDesk, Fintel, ChartExchange |
| Failures-to-deliver (FTD %) | Settlement strain — broker/clearing-firm dislocation | SEC FTD biweekly, ChartExchange |

### Tier thresholds

| Tier | Conditions (ALL must hold for upgrade unless `OR` noted) |
|---|---|
| **Extreme** | SI > 20% AND DTC > 5 AND borrow > 50% AND FTD > 0.5% of float |
| **High** | SI > 15% AND borrow > 20% (any two of the four extreme conditions) |
| **Moderate** | SI 10–15% OR borrow 5–20% |
| **Low** | SI < 10% AND borrow < 5% |

### How to read it

- **High SI alone is sentiment, not fuel.** A 20% SI with 0.25% borrow and 1.5 DTC is bearish positioning — there's no mechanical squeeze pressure because shorts can roll cheaply and cover quickly.
- **Borrow + DTC are the squeeze fuel.** When borrow rips above 20% annualized AND DTC exceeds 5, shorts pay real money and cannot exit on a single day's volume. That's mechanical pressure.
- **FTDs are the dislocation tell.** Spikes above ~0.5% of float (or several × the rolling daily average) signal clearing-firm strain — usually a precursor to forced cover or a regulatory event.
- **The catalyst is everything.** A High/Extreme tier without a catalyst is a slow bleed. With a binary catalyst (earnings, FDA, M&A) crowded shorts are the squeeze ammo. The tier flags potential energy; the catalyst lights it.

### What it does NOT measure

- Dark pool venue read (separate signal — see flow doc per asset class)
- Insider transactions (separate — Form 4)
- Options dealer positioning (see § Dealer gamma below — different mechanism)

### Operational use

The protocol uses the tier to size and pace short / long thesis on stocks. See `guide/scan/data.md` § Squeeze tier for the per-scan reading procedure and `data.md` § ChartExchange section template for the Flow & Squeeze block format. Crypto / index / FX / commodity have asset-class-specific positioning composites — see § (later sections) and the matching flow doc.

---

## Dealer gamma exposure

Options dealers (market-makers) are flow-neutral in aggregate but their hedge requirements drive significant intraday and intra-week price action. The "gamma regime" is whether their hedge bias is amplifying or dampening price moves.

### The two regimes

**Positive gamma regime** (price > zero-gamma flip level)
- Dealers are net long gamma → they sell rallies and buy dips
- **Tape character: mean-reverting, low-vol, range-bound.** Pinning toward strikes with the heaviest open interest is the signature.
- VIX tends to compress; intraday ranges tighten.

**Negative gamma regime** (price < zero-gamma flip)
- Dealers are net short gamma → they buy rallies and sell dips
- **Tape character: trend-amplifying, high-vol.** Moves get accelerated; gap risk rises; "gamma squeezes" run higher than fundamentals justify.
- VIX expands as moves self-reinforce.

### Key levels

| Level | What it is | How to use |
|---|---|---|
| **Zero-gamma flip** | Price at which net dealer gamma = 0 | Above = mean-revert; below = trend-amplify. Watch crosses |
| **Call wall** | Strike with the heaviest call open interest | Resistance — dealers sell to hedge. Pinning target |
| **Put wall** | Strike with the heaviest put open interest | Support — dealers buy to hedge. Pinning target |
| **Volatility trigger** (Vol Trigger) | Threshold where dealer hedging accelerates | Crossing it shifts the regime regardless of zero-gamma calc |

### VIX-complex confirmation

The VIX-complex (VIX, VVIX, VIX3M, MOVE for rates) confirms or contradicts the gamma regime read.

| Reading | Interpretation |
|---|---|
| VVIX > 100 | Real tail-risk premium being paid; insurance demand high |
| VVIX < 85 | Complacency; tail hedges abandoned |
| VIX3M / VIX > 1.05 | Contango (normal regime) |
| VIX3M / VIX < 1.00 | Backwardation = stress (front-month panic) |
| MOVE > 120 | Rate-vol elevated; cross-asset risk premium widening |

### Sources

The gamma calculation is not free; the published levels come from desk dealers and specialist providers:
- [SpotGamma](https://spotgamma.com) — daily blog (free) + premium dashboard
- [MenthorQ](https://www.menthorq.com) — free dashboards covering gamma, OI, and walls
- [Tier1 Alpha](https://www.tier1alpha.com) — weekly PDF covering positioning
- [Convex Value](https://www.convexvalue.com) — gamma + skew dashboards
- [GammaScalpers](https://twitter.com/GammaScalpers) — Twitter daily reads

### Operational use

Index scans (`/scan SPX`, `/scan NDX`, `/scan SPY`, `/scan QQQ`) read the gamma regime as part of the asset-class flow section per `guide/scan/index-flow.md`. Single-stock scans pick up gamma indirectly via max-pain (per the ChartExchange options block) — single-name dealer-gamma data is harder to get without paid tooling.

---

## CFTC Commitments of Traders (COT)

The CFTC publishes a weekly report (Tuesdays for previous Friday's positions) breaking down futures + options open interest by trader category. It's the prime positioning signal for FX (CME currency futures) and commodities (NYMEX crude, COMEX metals, ICE coffee/sugar/cotton, CBOT grains).

### Trader categories

| Category | Who | What they signal |
|---|---|---|
| **Non-commercial** (Large Spec / Funds) | Hedge funds, CTAs, asset managers using futures for directional bets | Positioning extremes are **contrarian** — when funds are at a 3-year crowded long, the next move is usually down |
| **Commercial** (Producers / End-users) | Physical-market participants hedging real exposure (oil producers, grain mills, FX corporates) | Slow but smart — commercials are usually right at multi-year extremes; their net position vs spec net is the read |
| **Spread positioning** | Relative-value desks holding both sides | Less directional; useful for term-structure interpretation |
| **Non-reportable** (Small Spec / Retail) | Below CFTC reporting threshold | Often crowded into the wrong side; contrarian at extremes |

### Standard reads

- **3-year extreme** — when non-commercial net (long minus short) prints at a 3-year high or low, the position is crowded; the next leg is usually counter-trend.
- **Non-commercial vs non-reportable divergence** — when funds and retail are positioned opposite, follow the funds (they win the cycle, retail does not).
- **Commercial-extreme reversal** — when commercials accumulate against the prevailing trend (e.g., oil commercials net long while price still falling), it precedes a turn within ~4–8 weeks.
- **Net-change week-on-week** — the ΔWoW in non-commercial net is more actionable than absolute level for catching turns.

### Sources

- [CFTC weekly Commitments of Traders report](https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm) — primary, free
- Aggregated views: [Tradingster](https://www.tradingster.com), [Barchart COT](https://www.barchart.com/futures/commitment-of-traders)
- Visualizations: TradingView built-in COT indicator, [TimingCharts COT](https://www.timingcharts.com)

### Operational use

- **FX scans** (`/scan EURUSD`, `/scan USDJPY`, etc.) read CFTC FX-futures COT per `guide/scan/fx-flow.md`. The CME futures positioning is the institutional read; spot retail-FX brokers like IG / MyFXBook offer the contrarian retail layer.
- **Commodity scans** (`/scan CL`, `/scan GC`, `/scan ZW`, etc.) read commodity COT per `guide/scan/commodity-flow.md`. Combine with curve shape + inventory data for the full positioning picture.

### What COT does NOT capture

- Spot OTC positioning (FX market is mostly OTC; CME captures only the futures slice — meaningful but partial)
- Options-only books (separate from futures COT; the disaggregated report covers some of this but coverage varies)
- Intraday positioning (weekly snapshot only)

---
