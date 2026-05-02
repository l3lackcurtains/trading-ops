# Macro framework — regime quadrants, key indicators, and regime gating

Authoritative macro / regime layer for the framework. This document is consumed directly by `/scan-macro` (which writes `scanned/MACRO/current.md`) and acts as the regime gate for `/scan` swing and day-trade horizons. It has two jobs: (1) define the four growth × inflation quadrants and the indicators that locate the current regime on that 2×2; (2) document the news-trading playbook — how specific macro releases (CPI, NFP, JOLTS, FOMC) move USD, gold, oil, crypto, and the Nasdaq, with the context overlays that override the textbook reactions. For the bottom-up complement (single-name fundamentals — ROIC, moat, growth, valuation, balance sheet, institutional flow), see [`long-term-investing.md`](long-term-investing.md).

## Doc roles

| Doc | Question it answers | Use when |
| --- | --- | --- |
| **`macro.md`** *(this doc)* | What regime are we in? Where is the market? How will this specific news print move USD / gold / oil / crypto / Nasdaq? | Top-down: regime read, asset allocation, risk-on/off bias, trading around scheduled releases (CPI, NFP, JOLTS, FOMC) |
| [`long-term-investing.md`](long-term-investing.md) | Is this individual stock worth owning? | Bottom-up: ROIC, moat, growth, valuation, balance sheet, institutional flow on a single name |

**Workflow:** this doc sets the regime → bottom-up analysis picks the names that fit the regime → the news-trading playbook below times entries around catalysts.

---

## Table of contents

1. [Market-wide sentiment gauges](#market-wide-sentiment-gauges)
2. [Growth, inflation and liquidity (macro pillars)](#growth-inflation-and-liquidity-macro-pillars)
3. [Economic outlook](#economic-outlook)
4. [Market regime framework — growth × inflation quadrants](#market-regime-framework--growth--inflation-quadrants)
5. [Definitions — the underlying indicator vocabulary](#definitions--the-underlying-indicator-vocabulary)
6. [News impact matrix](#news-impact-matrix)
7. [How macro news impacts different assets](#how-macro-news-impacts-different-assets)
8. [Context modifiers — when the standard reactions break down](#context-modifiers--when-the-standard-reactions-break-down)
9. [The metagame of macros — pre-news positioning](#the-metagame-of-macros--pre-news-positioning)
10. [Bubble indicators](#bubble-indicators)
11. [Additional indicators worth watching](#additional-indicators-worth-watching)
12. [Reference dashboards](#reference-dashboards)

---

## Market-wide sentiment gauges

- **[FINRA margin debt](https://www.finra.org/rules-guidance/key-topics/margin-accounts/margin-statistics)** — Track margin-debt / GDP. Historically rises into bubble peaks (2000, 2008, 2021). Sharp YoY acceleration = leverage bubble; rolling over from extremes = de-risking phase. Live chart: [Advisor Perspectives](https://www.advisorperspectives.com/dshort/updates/2026/04/20/margin-debt-down-2-6-in-march-second-straight-decline) · [GuruFocus — Margin Debt / GDP](https://www.gurufocus.com/economic_indicators/4266/finra-investor-margin-debt-relative-to-gdp).

- **[Smart Money / Dumb Money Confidence (SentimenTrader)](https://sentimentrader.com/indicators/smart-money-dumb-money-confidence-spread)** — 0–100% scale. Bullish: Smart > 60 AND Dumb < 40. Bearish/topping: Dumb > 60 AND Smart < 40. **Divergence is the signal**, not absolute level.

- **Stock–bond ratio** — Above 2 → stocks overvalued vs. bonds. Below -2 → bonds overvalued vs. stocks. Track via [SPY/TLT chart on TradingView](https://www.tradingview.com/symbols/SPY-TLT/).

- **[Yield spread (10y minus 2y) — FRED T10Y2Y](https://fred.stlouisfed.org/series/T10Y2Y)** — Tight/positive = good. Inversion (negative) = recession warning; the **un-inversion itself** typically precedes recession by 6–18 months. Backup: [10y-3m, FRED T10Y3M](https://fred.stlouisfed.org/series/T10Y3M) (NY Fed's preferred series).

- **[High-yield credit spread (HY OAS) — FRED BAMLH0A0HYM2](https://fred.stlouisfed.org/series/BAMLH0A0HYM2)** — Junk-vs-investment-grade yield gap. **Narrow** = greed / risk-on. **Wide / spiking** = fear, credit stress, often precedes equity selloffs. One of the cleanest "real money" risk gauges.

- **[Put/Call ratio (Cboe)](https://www.cboe.com/us/options/market_statistics/daily/)** — > 1 = bearish/hedging; < 0.7 = greedy/speculative. Watch extremes for contrarian reversals.

- **[CNN Fear & Greed Index](https://www.cnn.com/markets/fear-and-greed)** — Composite (0–100) of 7 sub-indicators (momentum, breadth, put/call, junk-bond demand, VIX, safe-haven demand, price strength). **< 25** = Extreme Fear (often a buy zone). **> 75** = Extreme Greed (often a top zone).

- **[VIX (CBOE Volatility Index)](https://www.cboe.com/tradable-products/vix/)** — directional read ([explainer](https://volatilitybox.com/research/how-to-trade-the-vix-complete-strategy-guide-for-2026/)):
  - **Above 30** → fear / crisis. Historically a contrarian BUY (mean-reverts < 20 within 1–3 months).
  - **20–30** → elevated. HOLD / hedge.
  - **15–20** → normal regime. Neutral.
  - **Below 15** → complacency. Trim longs / consider hedges.
  - **VIX through its 200-day MA** → strongest single regime-change signal.

---

## Growth, inflation and liquidity (macro pillars)

The three forces that drive every regime: **growth**, **inflation**, and **liquidity**. Every other indicator in this doc is downstream of these three.

### Growth

- **[GDP — BEA](https://www.bea.gov/data/gdp/gross-domestic-product)** — quarterly, lagging. The headline gauge for economic activity. Watch real GDP YoY and QoQ annualized.
- **[Atlanta Fed GDPNow](https://www.atlantafed.org/cqer/research/gdpnow)** — real-time GDP nowcast that updates with each new data release. Closes the lag gap.
- **[NY Fed Nowcast](https://www.newyorkfed.org/research/policy/nowcast)** — alternative GDP nowcast.
- **[Industrial Production (FRED INDPRO)](https://fred.stlouisfed.org/series/INDPRO)** — coincident measure of factory/utility/mining output.
- **[Retail Sales (FRED RSAFS)](https://fred.stlouisfed.org/series/RSAFS)** — consumer-spending proxy; consumer is ~70% of US GDP.
- **[Personal Consumption Expenditures (FRED PCE)](https://fred.stlouisfed.org/series/PCE)** — broader consumer-spending series.
- **[Conference Board Consumer Confidence Index](https://www.conference-board.org/topics/consumer-confidence)** — household optimism about jobs and income; precedes spending shifts.
- **[University of Michigan Consumer Sentiment (FRED UMCSENT)](https://fred.stlouisfed.org/series/UMCSENT)** — second consumer-mood gauge; combine with CCI to filter signal noise.
- **[Unemployment Rate (FRED UNRATE)](https://fred.stlouisfed.org/series/UNRATE)** — the headline labor reading. Combine with SAHM rule (below) for recession context.
- **[Housing Starts (FRED HOUST)](https://fred.stlouisfed.org/series/HOUST)** & **[Building Permits (FRED PERMIT)](https://fred.stlouisfed.org/series/PERMIT)** — housing leads the cycle. Building permits is in the Conference Board LEI for a reason.
- **[New Home Sales (FRED HSN1F)](https://fred.stlouisfed.org/series/HSN1F)** & **[Existing Home Sales (FRED EXHOSLUSM495S)](https://fred.stlouisfed.org/series/EXHOSLUSM495S)** — direct demand reads on housing; sensitive to mortgage rates.
- **[NAHB Housing Market Index](https://www.nahb.org/news-and-economics/housing-economics/indices/housing-market-index)** — homebuilder sentiment, leads housing starts.
- **[Case-Shiller Home Price Index (FRED CSUSHPISA)](https://fred.stlouisfed.org/series/CSUSHPISA)** — wealth-effect input.

### Inflation

- **[CPI — Headline (FRED CPIAUCSL)](https://fred.stlouisfed.org/series/CPIAUCSL)** — the headline number markets react to.
- **[Core CPI (FRED CPILFESL)](https://fred.stlouisfed.org/series/CPILFESL)** — ex food & energy; less noisy.
- **[PCE Price Index (FRED PCEPI)](https://fred.stlouisfed.org/series/PCEPI)** & **[Core PCE (FRED PCEPILFE)](https://fred.stlouisfed.org/series/PCEPILFE)** — **the Fed's preferred inflation gauge**. This is what drives the dot plot.
- **[PPI — Producer Price Index (FRED PPIACO)](https://fred.stlouisfed.org/series/PPIACO)** — leads CPI by 1–3 months (input prices flow through to output prices).
- **[5-Year Breakeven Inflation (FRED T5YIE)](https://fred.stlouisfed.org/series/T5YIE)** & **[10-Year Breakeven (FRED T10YIE)](https://fred.stlouisfed.org/series/T10YIE)** — market-implied inflation expectations.
- **[University of Michigan 1y Inflation Expectations](https://data.sca.isr.umich.edu/)** — consumer side; the Fed watches this for "anchoring."
- **[Atlanta Fed Sticky CPI](https://www.atlantafed.org/research/inflationproject/stickyprice)** — slow-moving prices (rents, services) that take longer to come down.

### Liquidity (the most underappreciated driver)

- **[M2 Money Supply (FRED M2SL)](https://fred.stlouisfed.org/series/M2SL)** — broad money. Rising M2 = inflation/risk-asset fuel; contracting M2 (rare) = severe tightening.
- **[Fed Balance Sheet (FRED WALCL)](https://fred.stlouisfed.org/series/WALCL)** — total assets. Rising = QE; falling = QT.
- **[Treasury General Account / TGA (FRED WTREGEN)](https://fred.stlouisfed.org/series/WTREGEN)** — Treasury's checking account at the Fed. **TGA up = liquidity drained from system.**
- **[Reverse Repo / RRP (FRED RRPONTSYD)](https://fred.stlouisfed.org/series/RRPONTSYD)** — money parked at the Fed earning IORB. **RRP draining = liquidity flowing back into markets.**
- **Net liquidity** ≈ Fed balance sheet − TGA − RRP. Rising net liquidity historically correlates with rising risk assets.
- **[Bank Reserves (FRED RESPPLLOPNWW)](https://fred.stlouisfed.org/series/RESPPLLOPNWW)** — bank reserves at the Fed; functional liquidity for the banking system.
- **[Senior Loan Officer Survey (SLOOS)](https://www.federalreserve.gov/data/sloos.htm)** — bank lending standards. Tightening standards precede credit contractions.
- **[Global central-bank balance sheets (Yardeni)](https://www.yardeni.com/pub/balsheetwk.pdf)** — Fed + ECB + BOJ + PBOC. Global liquidity matters too.

---

## Economic outlook

### Rates and the Fed

- **FOMC pause vs. cut regime** — Pause keeps liquidity tight; cut adds liquidity. Track via [CME FedWatch Tool](https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html) and the [Fed's Summary of Economic Projections (SEP / dot plot)](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm).
- **Why cuts come** — rate cuts typically require labor weakening first. Cutting IR adds liquidity, letting companies hire again.
- **Required for stock strength** — bond yields should fall (prices up, money rotates out of cash/bonds into equities). Watch **[10y Treasury yield (FRED DGS10)](https://fred.stlouisfed.org/series/DGS10)** — the discount rate for risk assets.
- **Fed-chair turnover risk** — a dovish replacement biases policy toward easier liquidity → potential generational risk-on catalyst. Hawkish replacement does the opposite.

### Recession signals

- **[SAHM Rule (FRED SAHMREALTIME)](https://fred.stlouisfed.org/series/SAHMREALTIME)** — triggers when 3-month MA of U3 unemployment rises **≥ 0.50 pp** above its prior-12-month low. Below 0.50 = no signal; break above = recession likely already started ([Wikipedia — Sahm Rule](https://en.wikipedia.org/wiki/Sahm_rule)).
- **Labor deterioration checklist**:
  - **[JOLTS — Quits Rate (FRED JTSQUR)](https://fred.stlouisfed.org/series/JTSQUR)** — falling quits = workers losing confidence.
  - **[JOLTS — Job Openings (FRED JTSJOL)](https://fred.stlouisfed.org/series/JTSJOL)** — falling openings = hiring slowdown.
  - **[Non-Farm Payrolls (FRED PAYEMS)](https://fred.stlouisfed.org/series/PAYEMS)** — negative monthly prints = recession trigger.
  - **[Initial Jobless Claims (FRED ICSA)](https://fred.stlouisfed.org/series/ICSA)** — sustained breakouts above ~280k historically precede recessions.
- **[Yield-curve un-inversion (FRED T10Y2Y)](https://fred.stlouisfed.org/series/T10Y2Y)** — the un-inversion (curve steepening from negative back through zero) is the actual recession trigger — not the initial inversion. Lead time: 6–18 months. Probability model: [NY Fed Recession Probability](https://www.newyorkfed.org/research/capital_markets/ycfaq).
- **Banking-stress watch** — bank failures, regional-bank deposit flight, emergency Fed liquidity facilities (BTFP-style), widening credit spreads ([HY OAS](https://fred.stlouisfed.org/series/BAMLH0A0HYM2)).
- **Political angle** — incumbent administrations are typically blamed for recessions on their watch; political pressure intensifies the call for cuts.

### Tariff scenario — likely chain of effects

- USD goes up ([DXY](https://www.marketwatch.com/investing/index/dxy)) on relative-strength flight.
- US debt service eases as bond prices rise.
- Flight to safety → investors move into US bonds.
- US bond prices up → yields down (still high overall).
- Curve dynamics: 2y up (Fed stays hawkish on tariff-driven inflation), 10y down (growth fear). Spread widens via that mix.
- Liquidity tightens; investors get concerned.
- If BTC tracks the stock market, it grinds higher with risk assets.

**Watch-outs (the script doesn't always play out cleanly):**

- Tariffs are **inflationary** in the short term — the Fed may stay tight, blocking the easing leg of the thesis.
- Foreign holders (Asia, EU) can **sell** USTs in retaliation — that pushes long yields **up**, the opposite of flight-to-safety.
- Heavy Treasury issuance to fund deficits is a **bearish technical** for long bonds even when growth slows.
- A bond-market revolt (sudden 10y spike) is historically what forces tariff pauses — bonds, not stocks, are the political pain point.

---

## Market regime framework — growth × inflation quadrants

We use R-prefix (Regime 1–4) for the four growth × inflation quadrants to avoid collision with calendar-quarter notation (Q1, Q2 …).

Used by Bridgewater (Dalio), Hedgeye, 42 Macro, and most global-macro shops. **80% of macro is identifying which regime you are in** ([explainer — Fidenza Macro](https://www.fidenzamacro.com/p/the-four-quadrant-global-macro-framework)). Every signal in this doc serves one purpose: locating you on this 2×2.

```
                 Inflation FALLING    Inflation RISING
              ┌─────────────────────┬─────────────────────┐
   Growth     │         R1          │         R2          │
   RISING     │  Goldilocks /       │  Reflation /        │
              │  Disinflation       │  Boom               │
              │  Stocks +++,        │  Stocks ++,         │
              │  Bonds ++,          │  Commodities +++,   │
              │  USD neutral        │  USD weaker         │
              ├─────────────────────┼─────────────────────┤
   Growth     │         R4          │         R3          │
   FALLING    │  Deflation /        │  Stagflation        │
              │  Risk-Off           │                     │
              │  Bonds +++,         │  Gold +++,          │
              │  Cash +,            │  Commodities ++,    │
              │  Stocks ---         │  Stocks --          │
              └─────────────────────┴─────────────────────┘
```

### How to identify the regime

- **Growth axis** — Atlanta Fed GDPNow + ISM PMI + Retail Sales + Industrial Production + Initial Claims (inverted). Rate-of-change is what matters, not absolute level.
- **Inflation axis** — Core PCE + Core CPI + PPI + breakeven inflation. Rate-of-change again.

### What works in each regime

| Regime | Name | Best assets | Worst assets |
| --- | --- | --- | --- |
| **R1** | Goldilocks (growth ↑, inflation ↓) | US equities, long-duration tech, long Treasuries | Cash, commodities |
| **R2** | Reflation (growth ↑, inflation ↑) | Cyclicals, energy, materials, small caps, EM | Long-duration bonds, defensives |
| **R3** | Stagflation (growth ↓, inflation ↑) | Gold, commodities, TIPS, cash | Long-duration tech, long bonds |
| **R4** | Deflation / Risk-Off (growth ↓, inflation ↓) | Long Treasuries, USD, cash, defensives | Equities (esp. cyclicals), commodities, credit |

### Regime gating — when the regime overrides per-name signal

The framework overlay: trade direction with technicals, but **size and asset selection** with the regime. An R4 setup demands smaller equity longs and bigger duration exposure than an R1 setup, regardless of what the chart looks like.

Concretely, the regime acts as a hard gate on `/scan` swing/day-trade horizons:

1. **Asset-class fit** — a clean per-name technical setup in an asset class that the current regime penalises (e.g. long-duration tech in R3 stagflation) is downgraded automatically. The chart can be perfect; the regime still wins on sizing.
2. **Direction bias** — when the regime is decisively risk-off (R4) or stagflationary (R3), long-equity setups need a higher bar (cleaner reclaim, deeper liquidity) and shorts pay more. The reverse holds in R1.
3. **Position size** — out-of-regime longs cap at half the in-regime size. Out-of-regime shorts in a clear R1 cap the same way.
4. **Tension with the bottom-up book** — a name can be a long-term ROIC compounder *and* a wrong-regime trade right now. The bottom-up book in [`long-term-investing.md`](long-term-investing.md) decides whether to *own* it; this doc decides whether to *add* to it at the current regime moment. The two layers don't compete — they answer different questions.

When in doubt, the regime read in `scanned/MACRO/current.md` is authoritative for sizing and pacing on swing/day-trade horizons; per-name conviction from the bottom-up book is authoritative for whether the name belongs in the book at all.

---

## Definitions — the underlying indicator vocabulary

The vocabulary that the news-trading playbook below is built on. These are the prints that move markets when they're released; the dashboards above are how you check the trend that frames each print.

**Gross Domestic Product (GDP)** — how well a country's economy is doing. The value of goods and services produced. Measured over a year and quarter.

### Inflation — key readings

1. **CPI – Consumer Price Index** — variation in the price of retail goods.
2. **Producer Price Index (PPI)** — the price change which impacts producers' profit margins.
3. **Core inflation** — change in price for goods and services excluding food and energy.

### Labor market — key readings

1. **Unemployment rate** — changes in the rate of employment/unemployment.
2. **Non-Farm Payrolls (NFP)** — changes in the number of people employed in the US in construction, manufacturing and goods companies.
3. **JOLTS (Job Openings and Labor Turnover Survey)** — insight into the demand for labor and hiring offered by companies.

### Consumer sentiment and spending

1. **Consumer Confidence Index** — trends in consumer behaviour and perception of overall economic conditions.
2. **Retail Sales** — sectors within retail that are performing or struggling.

### Housing market

1. **Existing Home Sales and New Home Sales** — the impact that interest rates have on the demand for housing.
2. **Housing Starts and Building Permits** — a measure that forecasts the future supply of housing.

### Federal Reserve policy

**Fed Funds Rate and FOMC** — monetary policy changes that respond to economic conditions.

---

## News impact matrix

Quick-reference for the *default* dollar/euro reaction to each release. These reactions assume no overriding context (no active war, no inflation re-anchoring fear, no extreme positioning). The [Context Modifiers](#context-modifiers--when-the-standard-reactions-break-down) section below lists the conditions under which they flip.

| Release | Reading direction | USD reaction | EUR reaction |
| --- | --- | --- | --- |
| CPI / Core CPI | Higher than expected | USD up (hawkish Fed) | EUR down |
| CPI / Core CPI | Lower than expected | USD down (dovish Fed) | EUR up |
| PPI | Higher than expected | USD up (CPI lead) | EUR down |
| PPI | Lower than expected | USD down | EUR up |
| Core PCE | Higher than expected | USD up (Fed's preferred gauge) | EUR down |
| Core PCE | Lower than expected | USD down | EUR up |
| Non-Farm Payrolls | Stronger than expected | USD up | EUR down |
| Non-Farm Payrolls | Weaker than expected | USD down | EUR up |
| Unemployment Rate | Lower than expected | USD up | EUR down |
| Unemployment Rate | Higher than expected | USD down | EUR up |
| JOLTS Job Openings | Higher than expected | USD up | EUR down |
| JOLTS Job Openings | Lower than expected | USD down | EUR up |
| Retail Sales | Stronger than expected | USD up | EUR down |
| Retail Sales | Weaker than expected | USD down | EUR up |
| FOMC | Hawkish (hold/hike, dot plot up) | USD up | EUR down |
| FOMC | Dovish (cut, dot plot down) | USD down | EUR up |
| Fed Chair speeches | Hawkish tone | USD up | EUR down |
| Fed Chair speeches | Dovish tone | USD down | EUR up |

**Initial jobless claims is intentionally excluded.** It's a short-term reading that effectively leads to the headline unemployment rate. There are ways to trade claims, but the moves are very short-term — not recommended for new traders.

---

## How macro news impacts different assets

Default reactions to macro releases — these are the *textbook* responses. The [Context Modifiers](#context-modifiers--when-the-standard-reactions-break-down) section below explains when these patterns *don't* hold.

### USD (DXY)

- **Strong jobs / hot CPI / hawkish Fed** → USD up.
- **Weak jobs / cooling inflation / dovish Fed** → USD down.
- USD is the master key — it sets the direction for almost every other asset's reaction.

### EUR / USD

When the dollar is strong the euro starts to weaken. The trade is the **interest-rate differential** between the Fed and the ECB, not absolute rates. Investors chase yield.

- **Hawkish ECB vs. dovish Fed** → EUR up. **Reverse** → EUR down.
- A strong US economy and higher Fed rates naturally draw foreign and domestic investors to the yield of the dollar.
- If the European economy struggles and the ECB cuts rates (**dovish stance**), the euro stays under pressure and continues to drop.
- If European rates rise (**hawkish stance**), investors seek euro yield over dollar yield and the euro appreciates.
- Rule of thumb: when the EUR is overextended on a dovish-Fed narrative, hedge funds will fade it. The "obvious" trade often reverses.

### Gold

- **Strong USD** → gold normally drops (gold is priced in USD, becomes more expensive abroad).
- **Inflation hedge** — high inflation + low real yields → gold rallies *even with strong USD*. Investors buy gold as an inflation hedge regardless of dollar direction.
- **Safe-haven status** — geopolitical stress → gold *and* USD both rally (dual safe-haven bid).
- Watch the **10y real yield (TIPS)** — gold's strongest single inverse correlation.

### Oil (WTI / Brent)

Oil is priced in dollars. When the dollar is stronger, oil becomes more expensive for international buyers, which depresses prices and demand. (This is the structural reason behind the BRICS de-dollarization push for oil pricing.)

- **Strong USD** → oil normally drops.
- **OPEC+ supply cuts** can override USD strength — even with a rising dollar, OPEC output discipline can push oil up.
- **Demand-destruction recession signal** (weak China PMI, collapsing global PMIs) → oil down regardless of USD.
- The BRICS de-dollarization narrative is a structural risk factor for oil pricing.

### Bitcoin / ETH / Solana

Bitcoin is a risk-on asset. You buy bitcoin by selling dollars. When the dollar rises, crypto tends to struggle — investors don't favor crypto when borrowing costs are high because crypto generates no yield.

- **Strong USD** → crypto headwind. Risk-on assets bought by selling USD.
- **No yield** → loses to bonds when rates are high. Crypto is not a fixed-income instrument; volatility and regulatory/concentration risk make it unattractive to yield-seeking capital.
- **Tight global liquidity** (high USD borrowing cost) → institutional capital avoids crypto due to rising cost of borrowing.
- **Strong NDX correlation** in liquidity-driven phases. Diverges in regime-change events (BTC sometimes leads risk-off).

### Nasdaq / long-duration equities

- **Cool inflation + dovish Fed** → NDX rips (long-duration discounted-cashflow trade).
- **Hot inflation + hawkish Fed** → NDX struggles even with strong earnings.
- **Falling 10y yield** → NDX up; **rising 10y yield** → NDX under pressure (multiple compression).

### Banks / cyclicals

- **Steepening yield curve** (especially un-inversion in a growth context) → banks benefit (NIM expansion).
- **Inverted curve** → bank profitability squeezed.
- **Rising oil + commodities** → energy & materials lift, defensives lag.

---

## Context modifiers — when the standard reactions break down

The textbook reactions above are the *base case*. They flip or distort when the broader context overrides the immediate print. Always check these four overlays before sizing a news trade.

### 1. Rate cycle phase

- **Easing cycle (cuts in progress)**: bad-news-is-good-news for equities (more cuts coming = liquidity). NDX can rally on weak NFP.
- **Hiking cycle (raises in progress)**: good-news-is-bad-news for equities (Fed has cover to keep tightening). Strong NFP sells off NDX.
- **Pause regime**: market cycles between the two depending on which side the data leans.

### 2. Geopolitical stress

- **Active war / conflict** → safe-haven flows override growth/inflation logic. Both gold and USD rally; risk assets sell off; oil spikes.
- Persistent geopolitical premium can keep gold elevated even through hawkish Fed cycles (inverts the "high USD = low gold" rule).

### 3. Inflation anchoring risk

- When the Fed is openly worried about inflation re-acceleration, **good labor data is bad for stocks** (Fed holds tight). Cooling labor is good (cuts back on the table).
- Watch breakevens + UMich inflation expectations to gauge whether the anchor is holding.

### 4. Election cycle / fiscal politics

- Election years amplify volatility around fiscal-related releases (deficit, employment, gas prices, tariffs).
- Pre-election **stimulus / dovish bias** is often priced into risk assets; post-election repricing can be sharp.

### Practical resolution

When the textbook reaction conflicts with the context overlay, the overlay wins. Concretely:

- A "good" jobs print in an active hiking cycle is bearish for equities, not bullish.
- A "bad" CPI print during a war can still rally gold and USD simultaneously; don't expect the inverse correlation to hold.
- A tariff escalation can override every other signal for a window of days; back off size until the curve and credit spreads stabilise.

---

## The metagame of macros — pre-news positioning

The matrix and asset-reaction tables above describe the *general* impact of news on price. Reality is messier. Even when a release is unambiguously dollar-positive, the dollar can drop. When it does, ask why — usually the answer is positioning.

**What the metagame means:** think in terms of what institutional investors are positioning for, not what the headline will literally say. When the euro is overextended and the dollar is weak, hedge funds start asking *"can we start buying dollars with a strong euro?"* — and the print becomes the trigger for the position they already wanted.

### Pattern: pre-news price action as institutional tells

The *real* signal before a release is often in **price action 1–4 hours before the print** — wide-range bars on heavy volume, range expansion, accumulation/distribution at key levels.

A live example from a JOLTS release: two hours before the print, the dollar ran up aggressively. A wide-range bearish bar hit the highs on heavy volume, and the next hour reversed the dollar lower — *before the JOLTS reading was public*. Bitcoin printed a wide-range bullish bar one hour before the same release at a key area, and continued up through the news candle.

Did pre-positioned players know the data? You can't prove it. But the dollar gave a clue with the bullish bar two hours before release. The data did come out negative for the dollar — and the pre-news price action had already telegraphed that move. *"There are those who know, and those who don't."*

### Pattern: when the chart is "set up" against the data

A second example, from an NFP week. On the Thursday before the print:

- Unemployment claims came in **lower** — good news.
- Employment cost came in **lower** — good news.
- Core price came in **higher** than the previous reading — hawkish for the dollar, technically good for the dollar.

By the matrix: dollar should rally, Nasdaq should be neutral-to-positive. Instead Nasdaq took a nose dive and the DXY also dropped — then DXY recovered the entire range when New York opened. Why? **Because they were buying** at the lows. The print was the cover; the position was already built.

Friday's NFP came in at 12k jobs vs. ~100k expected. Word on the street had been for a higher print. With the JOLTS higher and unemployment claims reduced, the macro-ideal scenario was a strong NFP and lower unemployment rate. The actual print was the opposite.

Why did Nasdaq go up on a weak NFP? **Because rate cuts were back on the table.** A clear drop in jobs offered + an unemployment rate at 4.1% with risk of going up = stronger Fed cut bias = NDX rallies on the weak print. Plus Amazon was pumping into earnings and Nvidia was moving up. Thursday's red wide-range drop was an imbalance, and price returned to recover it.

The point: the data didn't reflect the price action. Claims lower → companies hiring → demand for labor → expansion → NDX should have been up Thursday. Instead it dropped, *then* recovered on a print that "should have" sent it down further. Someone was buying NDX into the imbalance with a view that wasn't visible in the headline data.

### What to assume about news and macros

Are macros valid? Yes — banks and non-banks must move money where they generate the best yield. Rate differentials drive currency flows. Inflation reads drive central-bank policy. The chain is real.

But there are days when the chart is "set up," the news comes out, and price moves back to recover earlier imbalances regardless of what the headline says. Treat suspicious pre-news price action as the institutional tell, not the headline number.

**Practical rule:** wait for the news to release, run the dialogue against all four context modifiers above, then trade the *reaction*, not the prediction. The news is a catalyst; the setup matters more than the number.

When the regime is in one of these four scenarios, "good news is good news, bad news is bad news" stops working cleanly:

1. **New rate cycle** — easing or tightening cycle still shifting; reactions flip with the cycle phase.
2. **Active war / geopolitical stress** — safe-haven flows override the regime.
3. **Inflation re-acceleration fear** — Fed openly worried inflation is un-anchoring; good labor data becomes bearish.
4. **Election cycle** — fiscal politics distort fiscal-sensitive prints.

Outside of those four overlays, the textbook reactions hold and you can trade them. Inside any of them, the print is just a catalyst — wait, react, position around the *price*, not the headline.

> **Survival rule:** always wait for the news to release. Run the dialogue with yourself on where we are across the four overlays. You will never know fully what price will do on release — sometimes the textbook works, sometimes it doesn't. Sizing should reflect that.

---

## Bubble indicators

- **[Buffett Indicator (Market Cap / GDP)](https://www.currentmarketvaluation.com/models/buffett-indicator.php)** — Buffett's benchmarks: 75–90% reasonable, > 120% overvalued. Historical reference peaks: **~146% pre-dot-com**, **~109% pre-GFC**. Track distance from long-run trendline (in σ). Backup: [Longtermtrends](https://www.longtermtrends.com/market-cap-to-gdp-the-buffett-indicator/), [GuruFocus](https://www.gurufocus.com/stock-market-valuations.php).
- **[Margin debt extremes](https://www.advisorperspectives.com/dshort/updates/2026/04/20/margin-debt-down-2-6-in-march-second-straight-decline)** — track margin/GDP. Sustained record highs = leverage bubble; rolling over from extremes = de-risking.
- **[Wealth concentration (Fed DFA)](https://www.federalreserve.gov/releases/z1/dataviz/dfa/distribute/chart/)** — ~90% of US stocks held by the top 10% richest → fragility through narrow ownership.
- **[Mag 7 concentration (Visual Capitalist)](https://www.visualcapitalist.com/sp/charted-magnificent-7-market-cap-as-a-share-of-the-sp-500/)** — share of S&P 500 held by Apple, Nvidia, Microsoft, Amazon, Tesla, Alphabet, Meta. Record-high concentration vs. ~12% a decade prior. Tiny share by company count, dominant share of weight = breadth fragility. Live: [MacroMicro](https://en.macromicro.me/charts/123469/us-magnificent-seven-total-market-cap-and-share-of-sp-500). *(The correct measure is share of S&P 500 cap, not share of GDP — common conflation.)*
- **Ten Titans** — ~38% of the [S&P 100](https://www.spglobal.com/spdji/en/indices/equity/sp-100/), heavily invested in AI capex.
- **[Equal-weight vs cap-weighted divergence (RSP vs SPY)](https://www.tradingview.com/symbols/SPY-RSP/)** — cap-weighted outrunning equal-weight by a wide margin = narrow breadth = fragile rally.
- **AI pilots failure rate** — ~95% of enterprise generative AI pilots fail to deliver measurable P&L impact (MIT NANDA, *State of AI in Business*) ([Fortune coverage](https://fortune.com/2025/08/18/mit-report-95-percent-generative-ai-pilots-at-companies-failing-cfo/)). Internal builds succeed ~1/3 as often as buying from specialized vendors. Implication: AI capex boom loosely tied to revenue conversion.
- **[BofA Fund Manager Survey](https://www.bofaml.com/en-us/content/global-research-fund-manager-survey.html)** — track % saying US stocks are overvalued; readings > 80% are historically late-cycle.
- **Global market-cap concentration** — US holds ~60% of global stock cap — highest concentration since the 1960s ([SIFMA Capital Markets Fact Book](https://www.sifma.org/resources/research/fact-book/)).
- **GDP at PPP** — China GDP exceeds US GDP on a PPP basis ([World Bank PPP data](https://data.worldbank.org/indicator/NY.GDP.MKTP.PP.CD)), yet US equity cap dwarfs China's → US equity premium is structural but stretched.
- **Cap inflation in US tech** — US giants carry far larger caps than non-US peers with similar revenue.
  - Meta vs. ByteDance: ~6× cap.
  - Tesla vs. BYD: ~13× cap difference at comparable unit volumes.
- **AI macro contribution** — AI capex adds ~0.5 pp to US GDP — fragility if capex normalizes ([BEA GDP detail](https://www.bea.gov/data/gdp/gross-domestic-product)).
- **Underlying capex** — investment in info-processing equipment & software is ~4% of activity but contributes a disproportionate share of recent GDP growth.
- **AI data-center spend** — bigger chunk of GDP growth than consumer shopping; if it rolls over, the macro impulse goes negative fast.

---

## Additional indicators worth watching

| Indicator | What it signals | Source |
| --- | --- | --- |
| **ISM Manufacturing PMI** | < 50 = contraction. Leading indicator for earnings cycles. | [ISM Report](https://www.ismworld.org/supply-management-news-and-reports/reports/ism-report-on-business/) |
| **ISM Services PMI** | Services-side equivalent; broader economy gauge. | [ISM Report](https://www.ismworld.org/supply-management-news-and-reports/reports/ism-report-on-business/) |
| **Conference Board LEI** | Composite of 10 leading series; sustained YoY decline historically precedes recession. | [Conference Board](https://www.conference-board.org/topics/us-leading-indicators) |
| **NFIB Small Business Optimism** | Small-cap earnings proxy; tracks Russell 2000 well. | [NFIB Index](https://www.nfib.com/news/monthly-reports/) |
| **MOVE Index** | VIX for the bond market. Rising MOVE = rate vol = risk-off. | [Yahoo — ^MOVE](https://finance.yahoo.com/quote/%5EMOVE/) |
| **DXY (US Dollar Index)** | Strong USD pressures EM, commodities, multinational earnings. | [MarketWatch DXY](https://www.marketwatch.com/investing/index/dxy) |
| **10y Real Yield (TIPS)** | Real cost of capital. Rising real yields compress equity multiples. | [FRED DFII10](https://fred.stlouisfed.org/series/DFII10) |
| **Copper / Gold ratio** | Risk-on/off macro proxy. Falling = risk-off / growth fear. | [TradingView HG/GC](https://www.tradingview.com/symbols/HG1!-GC1!/) |
| **Oil (WTI)** | Inflation pass-through; consumer-discretionary headwind. | [FRED DCOILWTICO](https://fred.stlouisfed.org/series/DCOILWTICO) |
| **Initial Jobless Claims (4-wk MA)** | Highest-frequency labor signal. | [FRED IC4WSA](https://fred.stlouisfed.org/series/IC4WSA) |
| **JOLTS — Quits & Openings** | Worker confidence + hiring demand. | [FRED JTSQUR](https://fred.stlouisfed.org/series/JTSQUR), [JTSJOL](https://fred.stlouisfed.org/series/JTSJOL) |
| **Earnings Revisions Breadth** | % of S&P 500 with upward vs. downward EPS revisions; turns negative before drawdowns. | [FactSet Earnings Insight](https://www.factset.com/earningsinsight) |
| **NAAIM Exposure Index** | Active-manager equity exposure (0–200%). Extremes are contrarian. | [NAAIM](https://www.naaim.org/programs/naaim-exposure-index/) |
| **AAII Sentiment Survey** | Retail bull/bear; often a contrarian fade at extremes. | [AAII](https://www.aaii.com/sentimentsurvey) |
| **Insider Buy/Sell Ratio** | Form 4 corporate insiders; net buying at lows = strong long signal. | [OpenInsider](http://openinsider.com/) |
| **Buyback-Announcement Dollars** | Corporate bid for own stock; declines = lost marginal buyer. | [S&P Buyback Index](https://www.spglobal.com/spdji/en/indices/equity/sp-500-buyback-index/) |

---

## Reference dashboards

Quick links to live data, grouped by category.

### Valuation & bubble gauges
- [Buffett Indicator — Current Market Valuation](https://www.currentmarketvaluation.com/models/buffett-indicator.php)
- [Buffett Indicator — Longtermtrends](https://www.longtermtrends.com/market-cap-to-gdp-the-buffett-indicator/)
- [Stock Market Valuations — GuruFocus](https://www.gurufocus.com/stock-market-valuations.php)
- [Market Concentration — Mag 7 Share](https://www.visualcapitalist.com/sp/charted-magnificent-7-market-cap-as-a-share-of-the-sp-500/)

### Sentiment & positioning
- [CNN Fear & Greed Index](https://www.cnn.com/markets/fear-and-greed)
- [SentimenTrader — Smart/Dumb Money](https://sentimentrader.com/indicators/smart-money-dumb-money-confidence-spread)
- [AAII Sentiment Survey](https://www.aaii.com/sentimentsurvey)
- [NAAIM Exposure Index](https://www.naaim.org/programs/naaim-exposure-index/)
- [Cboe Put/Call Ratio](https://www.cboe.com/us/options/market_statistics/daily/)

### Volatility & credit
- [VIX — Cboe](https://www.cboe.com/tradable-products/vix/)
- [MOVE Index — Yahoo](https://finance.yahoo.com/quote/%5EMOVE/)
- [HY OAS — FRED](https://fred.stlouisfed.org/series/BAMLH0A0HYM2)

### Rates & yield curve
- [10y-2y Spread — FRED](https://fred.stlouisfed.org/series/T10Y2Y)
- [10y-3m Spread — FRED](https://fred.stlouisfed.org/series/T10Y3M)
- [10y Treasury Yield — FRED](https://fred.stlouisfed.org/series/DGS10)
- [10y Real Yield (TIPS) — FRED](https://fred.stlouisfed.org/series/DFII10)
- [CME FedWatch Tool](https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html)
- [Fed FOMC Calendar / SEP](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm)

### Growth (real activity)
- [BEA — GDP](https://www.bea.gov/data/gdp/gross-domestic-product)
- [Atlanta Fed GDPNow](https://www.atlantafed.org/cqer/research/gdpnow)
- [NY Fed Nowcast](https://www.newyorkfed.org/research/policy/nowcast)
- [Industrial Production — FRED INDPRO](https://fred.stlouisfed.org/series/INDPRO)
- [Retail Sales — FRED RSAFS](https://fred.stlouisfed.org/series/RSAFS)
- [PCE — FRED](https://fred.stlouisfed.org/series/PCE)
- [Conference Board Consumer Confidence](https://www.conference-board.org/topics/consumer-confidence)
- [UMich Consumer Sentiment — FRED UMCSENT](https://fred.stlouisfed.org/series/UMCSENT)
- [Unemployment Rate — FRED UNRATE](https://fred.stlouisfed.org/series/UNRATE)
- [Housing Starts — FRED HOUST](https://fred.stlouisfed.org/series/HOUST)
- [Building Permits — FRED PERMIT](https://fred.stlouisfed.org/series/PERMIT)
- [New Home Sales — FRED HSN1F](https://fred.stlouisfed.org/series/HSN1F)
- [Existing Home Sales — FRED EXHOSLUSM495S](https://fred.stlouisfed.org/series/EXHOSLUSM495S)
- [NAHB Housing Market Index](https://www.nahb.org/news-and-economics/housing-economics/indices/housing-market-index)
- [Case-Shiller — FRED CSUSHPISA](https://fred.stlouisfed.org/series/CSUSHPISA)

### Inflation
- [CPI Headline — FRED CPIAUCSL](https://fred.stlouisfed.org/series/CPIAUCSL)
- [Core CPI — FRED CPILFESL](https://fred.stlouisfed.org/series/CPILFESL)
- [PCE Price Index — FRED PCEPI](https://fred.stlouisfed.org/series/PCEPI)
- [Core PCE — FRED PCEPILFE](https://fred.stlouisfed.org/series/PCEPILFE) ← Fed's preferred gauge
- [PPI — FRED PPIACO](https://fred.stlouisfed.org/series/PPIACO)
- [5y Breakeven — FRED T5YIE](https://fred.stlouisfed.org/series/T5YIE)
- [10y Breakeven — FRED T10YIE](https://fred.stlouisfed.org/series/T10YIE)
- [Atlanta Fed Sticky CPI](https://www.atlantafed.org/research/inflationproject/stickyprice)
- [UMich Inflation Expectations](https://data.sca.isr.umich.edu/)

### Liquidity & money supply
- [M2 — FRED M2SL](https://fred.stlouisfed.org/series/M2SL)
- [Fed Balance Sheet — FRED WALCL](https://fred.stlouisfed.org/series/WALCL)
- [Treasury General Account — FRED WTREGEN](https://fred.stlouisfed.org/series/WTREGEN)
- [Reverse Repo — FRED RRPONTSYD](https://fred.stlouisfed.org/series/RRPONTSYD)
- [Bank Reserves — FRED RESPPLLOPNWW](https://fred.stlouisfed.org/series/RESPPLLOPNWW)
- [Senior Loan Officer Survey (SLOOS)](https://www.federalreserve.gov/data/sloos.htm)
- [Global Central Bank Balance Sheets — Yardeni](https://www.yardeni.com/pub/balsheetwk.pdf)

### Labor & recession
- [Sahm Rule — FRED](https://fred.stlouisfed.org/series/SAHMREALTIME)
- [Initial Jobless Claims — FRED](https://fred.stlouisfed.org/series/ICSA)
- [Non-Farm Payrolls — FRED](https://fred.stlouisfed.org/series/PAYEMS)
- [JOLTS Quits — FRED](https://fred.stlouisfed.org/series/JTSQUR)
- [JOLTS Openings — FRED](https://fred.stlouisfed.org/series/JTSJOL)
- [NY Fed Recession Probability](https://www.newyorkfed.org/research/capital_markets/ycfaq)

### Leverage & flow of funds
- [FINRA Margin Statistics](https://www.finra.org/rules-guidance/key-topics/margin-accounts/margin-statistics)
- [Margin Debt / GDP — GuruFocus](https://www.gurufocus.com/economic_indicators/4266/finra-investor-margin-debt-relative-to-gdp)
- [Fed DFA — Wealth Distribution](https://www.federalreserve.gov/releases/z1/dataviz/dfa/distribute/chart/)

### Earnings & institutional flow (quarterly workflow)
- [FactSet Earnings Insight](https://www.factset.com/earningsinsight)
- [Earnings Whispers](https://www.earningswhispers.com/)
- [Zacks Earnings](https://www.zacks.com/)
- [Stockanalysis.com](https://stockanalysis.com/) — fundamentals & ratios
- [WhaleWisdom — 13F tracker](https://whalewisdom.com/)
- [Fintel](https://fintel.io/)
- [HedgeFollow](https://hedgefollow.com/)
- [OpenInsider — Insider buys/sells](http://openinsider.com/)
- [SEC EDGAR — 13F filings](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&type=13F)

### Macro & economy
- [BEA — GDP](https://www.bea.gov/data/gdp/gross-domestic-product)
- [Conference Board LEI](https://www.conference-board.org/topics/us-leading-indicators)
- [ISM Reports](https://www.ismworld.org/supply-management-news-and-reports/reports/ism-report-on-business/)
- [NFIB Small Business Optimism](https://www.nfib.com/news/monthly-reports/)
- [BofA Fund Manager Survey](https://www.bofaml.com/en-us/content/global-research-fund-manager-survey.html)
- [World Bank PPP GDP](https://data.worldbank.org/indicator/NY.GDP.MKTP.PP.CD)

### Concept explainers
- [CANSLIM — Wikipedia](https://en.wikipedia.org/wiki/CAN_SLIM)
- [CANSLIM Strategy Guide — Deepvue](https://deepvue.com/fundamentals/canslim-strategy/)
- [PEAD — Wikipedia](https://en.wikipedia.org/wiki/Post%E2%80%93earnings-announcement_drift)
- [Sahm Rule — Wikipedia](https://en.wikipedia.org/wiki/Sahm_rule)
- [VIX trading guide — Volatility Box](https://volatilitybox.com/research/how-to-trade-the-vix-complete-strategy-guide-for-2026/)
- [Free Cash Flow — Investopedia](https://www.investopedia.com/terms/f/freecashflow.asp)
- [Whisper Numbers explained](https://www.heygotrade.com/en/blog/whisper-numbers-vs-consensus-why-stocks-drop-on-beats/)
- [Four-Quadrant Macro Framework — Fidenza Macro](https://www.fidenzamacro.com/p/the-four-quadrant-global-macro-framework)
- [Dalio Bubble Indicator — Bridgewater](https://www.bridgewater.com/research-and-insights/ray-dalio-stock-market-bubble)
- [Ray Dalio Investment Principles — Allio](https://www.alliocapital.com/macroscope/the-macro-masterpiece)
- [Rosenberg — Key Macro Indicators](https://www.rosenbergresearch.com/2025/05/19/key-macroeconomic-indicators-every-investor-should-track/)
- [PIMCO — Significance of Economic Indicators](https://www.pimco.com/us/en/resources/education/learning-the-significance-of-the-key-economic-indicators)
