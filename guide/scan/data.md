# Data sourcing — single-source-per-fact, priority chain, freshness strategy

> Part of the [scan protocol](../scan-rules.md). See also: [style](style.md).

---

**Don't pull the same fact from multiple sources.** Each fact in a scan should cite exactly one source. The framework prefers depth over redundancy.

## Priority order for stock data

Use the first source that has the fact:

0. **Local: `scripts/fetch_quote.py <TICKER>`** (Yahoo Finance via the local `_yfdata` adapter, run BEFORE any WebFetch) — primary source for: price, market cap, 52w range, beta, P/E, forward P/E, P/S, P/B, PEG, gross / operating / net margins, ROE, ROA, EPS (TTM + growth), revenue growth, debt/equity, current/quick ratio, total cash, total debt, FCF, EBITDA, shares outstanding/float, insider%, institutional%, short% / DTC, SMA50/200 (plus locally computed SMA20, RSI(14), ATR(14), rel volume), dividend yield + payout, analyst rec mean + target, next earnings date, last 5 news headlines. **Also pre-computes:** numeric auto-reject (negative gross margin / negative ROIC estimate), 3-consecutive-Q growth check (Pillar 2 + Pillar 6 high-conviction gate input).

   Run as: `.venv/bin/python scripts/fetch_quote.py <TICKER>` (or `--auto-reject-only` for a fast pre-check, `--json` for piped consumption). Returns ~300–500 tokens of structured markdown — paste-ready into the scan, replaces ~5K tokens of Finviz+Stockanalysis WebFetches.

   **Auto-reject shortcut:** if `fetch_quote.py --auto-reject-only` exits 3, the entire 6-pillar scoring block can be written as `Pos S — numeric auto-reject (gross margin <0 / ROIC <0)` without further LLM scoring. Swing/Day horizons still scan if a binary catalyst exists (per [scorecard.md](scorecard.md) § Pillar 0 gate rule).

0a. **Local: `scripts/fetch_sec.py <TICKER>`** (SEC EDGAR direct, no auth required, ~10 req/sec courtesy throttle). Run alongside `fetch_quote.py` for stock scans.
   - **Form 4 insider transactions** — every Form 4 filing in the last 90 days (configurable via `--days`) parsed for non-derivative transactions: owner name, role, transaction code (P=open-market purchase, S=sale, A=grant, M=exercise, etc.), shares, price, value. Authoritative; replaces OpenInsider (frequently `ECONNREFUSED`) and the truncated Finviz insider page as primary.
   - **Cluster detection** — flags ≥2 distinct insiders making open-market purchases within 2 days of each other → emits a 🚨 cluster signal in the output.
   - **ROIC components from XBRL** (`data.sec.gov/api/xbrl/companyfacts/CIK<NNN>.json`) — Operating Income, Total Debt, Stockholders' Equity, tax provision → computes precise ROIC. **Closes the Yahoo ROIC-precise gap without Finviz fallback.**
   - **Filings freshness** — latest 10-K, 10-Q, earnings 8-K (Item 2.02) dates so you know if the data you're scoring is from a recent print or stale.
   - Set the User-Agent: `export SEC_USER_AGENT="YourName <you@example.com>"` (SEC fair-access policy mandates a real contact).

0b. **Local: `scripts/fetch_max_pain.py <TICKER>`** (computes max pain locally from yfinance options chain, no WebFetch). Run when the scan needs max pain — the most-common ChartExchange call. Iterates over the next N OPEX dates (default 4), for each computes the strike that minimizes total long-option dollar loss at expiry, returns a per-OPEX table with max-pain strike, total Call OI, total Put OI, P/C OI ratio. Real-time freshness (computed live from current OI; no FINRA / SEC lag).

1. **Finviz quote page** (`finviz.com/quote.ashx?t=<TICKER>`) — **fallback only**, for the few fields Yahoo doesn't expose:
   - **ROIC precise** (Finviz `ROI` row) — fetch only when the Pillar 1 verdict is borderline (ROIC near zero) AND the EBIT/IC estimate from Step 0 isn't decisive
   - **AMC / BMO earnings timing** — fetch only when next earnings is within 7 days and a Day-trade tier depends on knowing pre-open vs post-close
   - **Insider Trans % / Inst Trans %** aggregates — usually skipped (we use OpenInsider Form-4 detail + Fintel 13F Q/Q delta which are sharper signals)
   - **Sales growth 5Y** — if needed for a long-cycle compounder read
   - One WebFetch when triggered.

2. **Stockanalysis** — **fallback only**, for: extended balance-sheet detail (debt maturity ladder), FCF conversion ratio, deeper historical statements when yfinance returns gaps. `stockanalysis.com/stocks/<TICKER>/statistics/`. Skip on most scans — Step 0 covers FCF, net debt, EBITDA directly.

3. **13F holder count + top-holder quality** — try in this order; **stop at the first that returns populated data**. Each often fails for thin-coverage names: WhaleWisdom (`whalewisdom.com/stock/<TICKER>`) → HedgeFollow (`hedgefollow.com/stocks/<TICKER>`) → Fintel (`fintel.io/so/us/<TICKER>`). If all three fail or return empty templates, mark the 13F count-change Q-over-Q as **unavailable** in Pillar 6 and lean on Dataroma + insider data instead. Don't block the scan on a missing 13F count. **yfinance does NOT have this** — WebFetch is required.

4. **Dataroma** (`dataroma.com/m/stock.php?sym=<TICKER>`) — for: superinvestor holdings (Buffett / Burry / Ackman / Klarman / Tepper / Icahn / Marks / Loeb / Greenblatt / Li Lu). Single page covers all legend portfolios. A "Symbol or Name not found" response is meaningful data — it confirms zero superinvestor coverage; cite it. **yfinance does NOT have this** — WebFetch required.

5. **Insider Form 4 detail** (cluster buys, transaction-level) — **`scripts/fetch_sec.py` (Step 0a) is the primary**; the WebFetch chain below is fallback only when EDGAR is unreachable or the LLM needs to cross-confirm a specific transaction.
   - **Fallback order**: OpenInsider (`openinsider.com/screener?s=<TICKER>`, frequently `ECONNREFUSED` — skip without retry) → Finviz insider trading page (`finviz.com/insidertrading.ashx?tc=1&t=<TICKER>`, also exposes Form 4 transactions). If both fail, fall back to the Finviz quote-page aggregate `Insider Trans %` (a fallback-on-the-fallback Finviz field).
   - **Finviz insider page truncation rule:** Finviz's public insider page shows only the most recent N rows (no full history exposed). If every row returned is dated >180 days old, treat that as **"no recent insider activity in last 90 days"** and rely on the aggregate `Insider Trans %` from the Finviz quote page — do NOT misread the truncated stale list as evidence of zero buys ever.

6. **ChartExchange** — primary source for **dark pool, short interest, FTD, borrow fee** (4 of the 5 Flow & Squeeze metrics). The 5th (max pain) is now computed locally via Step 0b — only WebFetch ChartExchange max pain when cross-confirmation is needed. URLs:
   - Dark pool: `chartexchange.com/symbol/<EX>-<TICKER>/exchange-volume/dark-pool-levels/`
   - Max pain: `chartexchange.com/symbol/<EX>-<TICKER>/optionchain/summary/` _(usually skip — Step 0b covers this)_
   - Short interest: `chartexchange.com/symbol/<EX>-<TICKER>/short-interest/`
   - FTD: `chartexchange.com/symbol/<EX>-<TICKER>/failure-to-deliver/`
   - Borrow fee: `chartexchange.com/symbol/<EX>-<TICKER>/borrow-fee/`
   - `<EX>` = `nyse` / `nasdaq` / `nyseamerican`
   - **Always note "as of" date** — dark pool 1–2 day lag, SI 2 weeks (FINRA), FTD 30+ days (SEC). Stale data shouldn't drive trade-plan triggers.
   - **Compute FTD `% of float` manually** as `total FTD ÷ float (Finviz)` — ChartExchange paywalls the float-% calc on its free FTD page.

7. **Seeking Alpha** — for: earnings call transcripts, guidance language, capital allocation reads (Pillar 5).

8. **News & analyst context — REQUIRED depth, not a single WebSearch.**

   Run `scripts/fetch_news.py <SYMBOL>` first as the structured primary source, then **WebSearch to fill the gaps** below. **Minimum 4–6 news sources from distinct outlets** must be cited per scan, organized by category. The scan must answer: *"What's actually happening with this name in the market RIGHT NOW, and what do the people who set prices believe?"*

   ### Required news categories per asset class

   **Stocks** — at minimum, cite one source per category (skip any genuinely N/A):
   1. **Catalyst news** (last 30 days) — earnings, guidance updates, M&A, regulatory, product launches, lawsuits, executive changes
   2. **Analyst price-target context** — recent upgrades / downgrades / initiations from named banks (Goldman, Morgan Stanley, JPM, Wells, etc.) with the new target + rationale; also the consensus `targetMeanPrice` from yfinance/Finviz
   3. **Sector / peer context** — what's happening to direct competitors (e.g., RIVN reads need TSLA + LCID + GM EV-segment commentary)
   4. **Macro overlay** — what regime catalysts (Fed, CPI, NFP) are within 7 days that could move this name
   5. **Insider / 13F narrative** — context behind any cluster Form 4 buys or notable 13F position changes (often comes from secondary financial press)
   6. **Earnings-call language** (within 90 days of last print) — guidance language, forward commentary, Q&A pushback

   **Crypto** — cite at minimum:
   1. **ETF flow news** (BTC + ETH) — daily / weekly net flows from Bitbo, plus narrative around it
   2. **Regulatory news** — SEC actions, CFTC, congressional moves, foreign-jurisdiction developments
   3. **On-chain / network news** — halving cycle (BTC), staking / supply (ETH), exchange hacks, validator changes
   4. **Macro overlay** — risk-on/off backdrop, USD direction, Fed rate path
   5. **Sector / peer narrative** — what BTC dominance + Mag-7 / NDX correlation is doing
   6. **Major-holder commentary** — Saylor, BlackRock IBIT comments, sovereign reserves, ETF issuer statements

   **Indices** (SPX/NDX/RUT/etc.) — cite at minimum:
   1. **Fed / FOMC commentary** — most recent statement, dot-plot read, Fed-speakers since the last meeting, blackout-period status
   2. **Breadth narrative** — A/D line, new-highs-vs-new-lows, Mag-7 concentration commentary
   3. **VIX / vol regime news** — what's driving curve shape, gamma positioning narratives (SpotGamma daily blog, MenthorQ)
   4. **Earnings season tail** — current beat rate, guidance trends, Mag-7 prints
   5. **Geopolitical / fiscal** — debt ceiling, shutdown risk, war / sanctions, trade
   6. **Sentiment surveys** — AAII, NAAIM, ISI, II — direction of change since last reading

   **FX** — cite at minimum:
   1. **Central-bank speak** — last decision + speakers from the central banks of the two currencies in the pair
   2. **Rate-differential narrative** — 2yr / 10yr yield spread direction commentary
   3. **Major data prints** within 7 days — CPI, employment, GDP for both currencies
   4. **Geopolitical / fiscal stress** — anything moving safe-haven flow (DXY, JPY, CHF) or commodity flow (CAD, AUD, NOK)
   5. **Positioning narratives** — IG / MyFXBook retail-sentiment commentary, hedge-fund flow stories

   **Commodities** — cite at minimum:
   1. **Supply-side news** — OPEC+ decisions (oil), USDA WASDE (grains), mine output / recall (metals), production guidance from majors
   2. **Demand-side news** — China import / inventory data, refinery utilization, industrial demand commentary
   3. **Geopolitical** — sanctions, war, shipping-route disruptions, trade-route news
   4. **Analyst price-target context** — sell-side targets from energy banks (Goldman, JPM, MS, RBC) with rationale
   5. **Inventory / curve narrative** — what's driving backwardation vs contango shifts
   6. **Seasonality + weather** — driving-season demand (energy), planting / harvest (grains), heating / cooling (NG)

   ### How to organize in the saved scan

   **Add a `## News & Analyst Context` section** to the scan output (between Regime fit and Flow & Squeeze / asset-class flow). Format: 4–8 bulleted items, each citing the source URL inline, grouped under the categories above. Lead with the most price-relevant 1–2 items; the rest provide context for the trade-plan stops/targets.

   **Example structure:**
   ```markdown
   ## News & Analyst Context

   **Catalysts (last 30 days):**
   - 2026-04-29: <event> (source)
   - ...

   **Analyst targets / sentiment:**
   - Goldman raised target to $X (Apr 22, source)
   - Consensus mean target $X (Yahoo Finance)

   **Sector / peer:**
   - <peer development that affects this name>

   **Macro overlay:**
   - Next 7-day catalyst: <Fed/CPI/NFP/etc.>
   ```

   **The verdict must be defensible from the cited news.** If the trade plan triggers off "war supply shock," there must be a war-supply-shock news citation. If the verdict is WAIT pre-print, there must be earnings-date + analyst-consensus citations.

---

## Freshness-first strategy (free sources only, no premium services)

The freshness floor for each metric is set by the official reporting cycle — no free site can beat that, and we don't have premium services (Ortex, Cheddar Flow, IBKR API) to fake real-time. So the strategy is: try multiple free sources for the same metric, compare their "as of" dates, and use whichever has the most recent print.

| Metric | Free sources to try (in parallel) | Inherent lag floor | Notes |
|---|---|---|---|
| **Max pain** | [ChartExchange](https://chartexchange.com/symbol/<EX>-<TICKER>/optionchain/summary/) · [OptionStrat](https://optionstrat.com/build/max-pain/<TICKER>) · [MaxPain.com](https://maxpain.com/options/<TICKER>) · [Yahoo options chain](https://finance.yahoo.com/quote/<TICKER>/options) | **Real-time** (live options chain) | All sources compute from same OI data; pick whichever loads cleanly. Yahoo can be computed manually if no max-pain site works. |
| **Dark pool / off-exchange %** | [ChartExchange dark pool](https://chartexchange.com/symbol/<EX>-<TICKER>/exchange-volume/dark-pool-levels/) · [QuiverQuant dark pool](https://www.quiverquant.com/stock/<TICKER>/dark-pools) · [Stockgrid dark pool](https://stockgrid.io/darkpool) | **T+1 day** (FINRA ATS reports next-day) | Try all three in parallel; use the source with the most recent date. |
| **Short interest** | [ChartExchange SI](https://chartexchange.com/symbol/<EX>-<TICKER>/short-interest/) · [Fintel SI](https://fintel.io/ss/us/<TICKER>) · [Nasdaq SI](https://www.nasdaq.com/market-activity/stocks/<TICKER>/short-interest) · [Stockanalysis SI](https://stockanalysis.com/stocks/<TICKER>/short-interest/) | **~2 weeks** (FINRA bi-monthly cycle) | All free sources hit the same FINRA wall. State the lag explicitly in the scan. |
| **FTD** | [ChartExchange FTD](https://chartexchange.com/symbol/<EX>-<TICKER>/failure-to-deliver/) · [Stockgrid FTD](https://stockgrid.io/) · [FTDList.com](https://ftdlist.com/) · [SEC FTD data](https://www.sec.gov/data/foiadocsfailsdatahtm) | **30+ days** (SEC monthly release) | Bounded by SEC publication cycle. The T+35 forced-covering window is calculated from the FTD date, so even stale data is actionable for upcoming dates. |
| **Borrow fee** | [ChartExchange borrow](https://chartexchange.com/symbol/<EX>-<TICKER>/borrow-fee/) · [iborrowdesk.com](https://iborrowdesk.com/report/<TICKER>) · [Fintel borrow](https://fintel.io/sos/us/<TICKER>) | **T+1 day** (IBKR public stock loan) | All three pull from IBKR's public stock loan data. Try in parallel; pick the freshest timestamp. |

### Strategy

1. **Try multiple sources in parallel** (single message, multiple WebFetch calls) — not sequentially. Costs the same in time as fetching one.
2. **Compare "as of" dates** across sources. Pick the most recent.
3. **Cite the source you used** in the Flow & Squeeze table row.
4. **State the lag floor.** If SI is "as of 14 days ago" because that's the FINRA cycle, say so. Don't pretend a 2-week SI number is fresh.
5. **Omit, don't fabricate.** If every source for a metric fails or all returns are >60 days old, mark it `unavailable` and don't let it drive a trigger. State directly: "Flow data thin on this scan; verdict driven by 6-pillar + chart read alone."
6. **No premium services in the chain.** Ortex, Cheddar Flow, IBKR API, paid Bloomberg/Refinitiv — never include in this list. We work with what's free.

### What lag floors mean for trade triggers

- **Real-time freshness** (max pain) → can drive intraday and same-week triggers
- **T+1 freshness** (dark pool, borrow fee) → drives week-ahead triggers
- **2-week-lagged** (SI) → directional confluence only, not a trigger by itself
- **30-day-lagged** (FTD) → useful for the T+35 forced-covering window calculation but never a same-day trigger

The trade plan should weight signals by their freshness — never let a 30-day-old number override a fresh price action read.

---

## ChartExchange section template

```markdown
### Flow & Squeeze (ChartExchange)

| Signal | Reading | As of | Interpretation |
|---|---|---|---|
| Off-Exchange % | 48% (30d avg 42%) | YYYY-MM-DD | Elevated dark pool — institutions positioning |
| Max Pain (next OPEX) | $X.XX (price Y% above) | YYYY-MM-DD | Magnetic pull DOWN into OPEX |
| P/C Ratio | 1.45 | YYYY-MM-DD | Bullish positioning |
| Short Interest | 18% float, DTC 6.2 | YYYY-MM-DD (FINRA 2wk lag) | Moderate squeeze potential |
| FTD | 0.8% float, T+35 due in 3 days | YYYY-MM-DD (30+ day lag) | Forced covering window |
| Borrow Fee | 35% annualized | YYYY-MM-DD | High squeeze tier |

**Composite squeeze score:** Low / Moderate / High / Extreme

**Cross-confluence with Pillar 6:** [does dark pool accumulation align with rising 13F count? does insider cluster buying align with falling FTDs? note alignment or divergence]

### Flow → trade decision (REQUIRED)

End the section with an interpretive paragraph that names what the flow data MEANS for the next 1–10 trading days, then proposes the option trade(s) the read implies:

1. **Gamma pull direction** — spot vs nearest weekly + monthly max pain. Spot below pin → upward magnet; above pin → downward magnet. State the % distance.
2. **Dealer gamma read from P/C** — P/C < 1.0 = call-heavy OI = dealers likely net short calls = short gamma above max pain (price pinned). P/C > 1.0 = put-heavy = pin upward. Cite the implication.
3. **Dark pool venue read** — % vs 30d avg. Elevated + reducing inst trans = trimming on strength via dark venue. Suppressed = quiet.
4. **Implied option trade(s):**
   - Pre-OPEX gamma-pin → CALL or PUT spread expiring Friday
   - Pre-binary-event (earnings/FDA/Fed) → defined-risk PUT or CALL spread expiring just after the event
   - Neutral on direction → iron condor or short strangle
```

### Option-plan rows in the Trade table (REQUIRED for stock scans)

Every stock scan with Swing tier **T** or **W** must include at least one defined-risk option plan row in the Trade table alongside any share plans. Through any binary catalyst within 14 days, **defined-risk options are the framework default** — share-shorts/longs through a binary pay overnight gap risk for full notional; spreads cap loss at the debit paid. Use Action verdict verbs **CALL** or **PUT** (already in the allowed list per [structure.md](structure.md)) with descriptive pattern slugs such as `earnings-binary-call`, `binary-earnings-put`, `earnings-iron-condor`, `catalyst-binary-options`.

### Squeeze tiering rules

Per [`docs/positioning.md` § Equity squeeze tier](../../docs/positioning.md#equity-squeeze-tier) — Extreme / High / Moderate / Low classification combining SI, DTC, borrow, FTD.

---

## Rules

- If Finviz has the fact, don't fetch Yahoo / CNBC / Investing.com / TipRanks for the same number.
- If a gap-fill source provides multiple facts, fetch once and use all of them.
- For macro / index / FX scans, the same principle applies — one source per gauge (FRED for rates, CNN for F&G, Cboe/TradingEconomics for VIX, BLS/BEA for prints).
- "Triangulation" (citing 3 sources for one number) is noise unless they materially disagree.

For commodities / crypto / FX / indices (`/scan`), the priority order shifts to instrument-specific sources — but the no-duplication rule is identical. Each asset class has its own flow doc; pick exactly one based on the symbol type:

- **Crypto** (BTCUSDT, ETHUSDT, etc.) → [crypto-flow.md](crypto-flow.md): alternative.me F&G, CoinGecko, OKX funding/OI, Deribit options, mempool.space, Bitbo ETF + chrome-devtools Coinglass captures.
- **Indices** (SPX, NDX, RUT, SPY/QQQ/IWM/DIA) → [index-flow.md](index-flow.md): **gamma exposure** (SpotGamma / Tier1 / MenthorQ / Convex Value), VIX term structure, AAII / NAAIM sentiment, COT equity-index futures.
- **FX pairs** (EURUSD, USDJPY, etc.) → [fx-flow.md](fx-flow.md): CFTC COT primary, IG / MyFXBook retail sentiment contrarian, rate differentials, Forex Factory calendar.
- **Commodities** (USO, GLD, SLV, GDX, DBA, CL, GC, etc.) → [commodity-flow.md](commodity-flow.md): CFTC COT, EIA / USDA inventory, futures curve shape, Baker Hughes rigs, seasonality.

These four flow docs are **mutually exclusive** — never apply two on the same scan. They replace the ChartExchange Flow & Squeeze block from stock scans (which uses max pain / dark pool / SI / FTD / borrow fee — none of which apply directly to non-stocks). Don't try to apply the stock chain to a non-stock scan.
