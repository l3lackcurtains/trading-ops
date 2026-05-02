# HOOD — Robinhood Markets, Inc.

## Snapshot — 2026-05-02 (Friday)

- **Price:** $73.66 (+1.06%, May 1 close EDT)
- **Market cap:** $66.33B · Float: 783.63M · Shares out: 791.18M · Avg vol: ≈25M/day · Beta: 2.46
- **52W range:** $45.56 – $153.86 · Current: 52% below 52W high, 62% above 52W low
- **Sector / Industry:** Financial Services / Capital Markets
- **Regime:** R2 Reflation (growth ↑, inflation ↑) — sector OW financials; crypto-revenue dependency is a mixed fit
- **Next catalyst:** Q2 2026 earnings ≈2026-07-29 AMC (~88 days; confirm with IR closer to date)
- **Coverage tier:** Pos **S** (sub-200d EMA daily) · Swing **W** · Day **W**

---

## Action — 2026-05-02

- **Pos: WAIT** *(pattern: `sub-200ema-no-position`)* — price 19% below daily 200-EMA ($91.07); no positional entry until 200-EMA reclaim AND two consecutive quarters of revenue growth ≥20% YoY
- **Swing: LONG** *(pattern: `post-earnings-washout-vwap-reclaim`)* — trigger: daily close above $75.16 (weekly VWAP) on volume; $74 triple confluence (post-print AVWAP $74.06 / daily HVN $74.22 / weekly VP VAH $74.21) is the support floor while trigger forms; defined-risk call spread concurrent option
- **Day: LONG** *(pattern: `vwap-reclaim-intraday`)* — entry on 1H close above session VWAP (≈$74–75 zone) with volume ≥1.3× 20-session avg; targets VWAP +1σ then $75 max pain; skip on sub-average volume sessions

### Price ladder

```text
       HOOD  -  2026-05-02  -  spot $73.66 (May 1 close EDT)
       ====================================================

       UPSIDE  (bull resolution path)
$91.07  ===  Daily 200-EMA  [positional ceiling]
$86.50  ===  Weekly EMA20
$85.00       Swing T2 / positional watch
$80.00  ===  Monthly VWAP (D) / May 15 max pain  [T1 Swing]
$79.34       Quarterly VWAP (D)
$78.35       Post-print AVWAP +2σ (D)
$76.56  ===  Short-term VP POC (1H)
$76.20       Post-print AVWAP +1σ (D)
$75.16  ===  --> SWING LONG entry  (weekly VWAP reclaim)
$75.00  ===  May 8 max pain  [Day T2]
- - - - - - - - - - - - - - - - - - - - - - - -
$74.65       Session VWAP +1σ (1H ref)  [Day T1]
$74.22  ###  HVN / post-print AVWAP / weekly VP VAH  [key $74 cluster]
>> $73.66  ***  CURRENT  ***
$73.82       Session VWAP -1σ (1H ref)  [Day stop]
$71.92  -X-  Post-print AVWAP -1σ (D)  [Swing stop]
$70.35  ===  Short-term HVN (1H)
$69.78       Post-print AVWAP -2σ (D)
- - - - - - - - - - - - - - - - - - - - - - - -
       DOWNSIDE  (bear resolution path)
$66.00  ===  Short-term VP VAL (1H)
$63.52       Short-term VP floor (1H)
$55.05  ===  Weekly 200-EMA  [structural floor]
$45.56       52W low
```

### Trade table

| Plan | Side | Trigger | Entry | Stop | T1 | T2 | T3 | R:R (T1/T2) | Size | Time stop |
|---|---|---|---|---|---|---|---|---|---|---|
| Swing-A | LONG | D close > $75.16 on vol | $75.16 | $71.92 | $80.00 | $85.00 | — | 1.5 / 3.0 | half | 2026-05-17 |
| Swing-B | CALL | D close > $74.50 + AVWAP hold | $75/$82.50 call spread May 15 | max debit | $80.00 (pin) | $82.50 | — | ≈3.0 | half | 2026-05-15 |
| Day-A | LONG | 1H close > session VWAP + vol ≥1.3× | ≈session VWAP | VWAP −1σ | VWAP +1σ | $75.00 | — | ≈1.0 / 1.9 | quarter | 2026-05-02 close |
| Pos | WAIT | Daily 200-EMA reclaim + 2Q revenue ≥20% | — | — | — | — | — | — | — | — |

**Lessons applied:** First scan for HOOD — no prior entries in desk lessons file. Seed conventions applied: triple confluence at $74 cited inline with components labeled (HVN + AVWAP + W-VP-VAH, all within 16 cents); all data points carry timeframe labels; earnings-driven AVWAP used with cohort named ("post-print institutional cost basis").

---

## TL;DR

- **Pos S / Swing W / Day W.** Price 19% below daily 200-EMA: no positional entry. Post-earnings washout from $85 to $74 has landed at the most confluent support cluster on the chart.
- **$74 is the structural line.** Post-print AVWAP $74.06, daily HVN $74.22, and weekly VP VAH $74.21 are within 16 cents of each other — triple-source support. Hold → swing to $80 (monthly VWAP / May 15 max pain). Lose → $70 and potentially $66.
- **Gamma pull above on all near-term OPEXes** ($75 May 8, $80 May 15, $80 May 22). Spot below max pain = upward magnetic pull while price stays under the pin.
- **Q1 miss was crypto-driven.** Revenue -8.5% vs estimates, EPS -7.3%; crypto trading revenue fell 47% YoY. Underlying platform metrics are healthy: Gold subscribers +36% (4.3M, record), net deposits $18B at 22% annualized growth.
- **Institutional exit is the key risk.** 13F holder count fell 25.29% Q/Q; zero insider buys vs 151 sells ($416.9M) in 6 months. The platform works; smart-money conviction is not there yet.

---

## Business

Robinhood earns revenue from three sources: (1) payment for order flow on equity and options trades, (2) interest income from cash deposits (Gold subscription sweep accounts, margin lending), and (3) Gold subscription fees ($5/month). Crypto trading is a volatile fourth revenue stream that was the primary driver of Q1 2026's earnings miss when cryptocurrency trading volume dropped sharply. The platform targets younger retail investors with a mobile-first UI and has been expanding into prediction markets and tokenized assets.

---

## 6-Pillar Scorecard

**Aggregate:** PASS 2 · NEUTRAL 3 · FAIL 1

| # | Pillar | Reading | Verdict |
|---|---|---|---|
| 1 | Quality / Moat | Gross margin 92.24%, operating margin 38.52%, ROIC ≈+7.59% (estimate from company filings); **Moat: network + switching** (user stickiness, PFOF + Gold ecosystem integration) | **PASS** |
| 2 | Growth | Revenue +15.1% TTM; Q1 2026 revenue $1.07B vs $1.17B est (−8.5%); EPS $0.38 vs $0.41 (−7.3%); crypto revenue −47% YoY; Gold subscribers +36% YoY (4.3M), net deposits 22% annualized, ARPU +8% | **NEUTRAL** |
| 3 | Valuation | P/E 35.76 TTM / 28.82 forward; P/S 14.38; P/B 7.12; cash/share $21.40 = 29% of price; forward P/E discounts recovery but EPS growth trajectory (2.7% TTM) doesn't support current multiple on fundamentals alone | **NEUTRAL** |
| 4 | Balance Sheet | Net cash +$5.66B; cash/share $21.40; debt $13.61B (normal for financial services firm); current ratio 1.11; well-capitalized | **PASS** |
| 5 | Management | Gold subscriber execution strong (4.3M record, +36%); CEO called April "already improving" post-print; 0 insider buys / 151 insider sells ($416.9M) last 6 months; NYSE 24/7 trading = structural tailwind for core model | **NEUTRAL** |
| 6 | Smart Money | 13F holders 1,359 (−25.29% Q/Q); shares held −9.89% Q/Q; no superinvestors on tracked lists; Vanguard increasing, FMR LLC −22.36%; insider selling one-sided. Declining holder count + zero buys → institutional confidence absent | **FAIL** |

**Auto-reject gate:**

| Gate | Threshold | Reading | Fires? |
|---|---|---|---|
| Negative gross margin | <0% | +92.24% | No |
| Negative ROIC | <0% | +7.59% (estimate) | No |
| P/S extreme on declining sales | P/S >10 + revenue falling | P/S 14.38, revenue +15% | No |
| Sub-200d daily | Price < daily 200-EMA | $73.66 vs EMA200 $91.07 (−19%) | **Yes → Pos S** |

No Pillar 1 numeric auto-reject. Positional blocked by sub-200d condition. Full scorecard retained for swing/day context and future positional reassessment on 200-EMA reclaim.

**High-conviction check (Positional T eligibility):**
- 3 consecutive quarters revenue ≥20% + EPS ≥25% YoY: 0/3 ✗
- 13F holder count rising MRQ: No (−25.29%) ✗
→ Not eligible for Pos T or W regardless; Pos S locked by sub-200d.

---

## Technical Read

### Positional (Weekly + Daily)

**EMA stack:**

| EMA | Weekly | Daily | Read |
|---|---|---|---|
| EMA20 | $86.50 | $78.75 | Price well below on both |
| EMA50 | $88.41 | $80.56 | Price well below on both |
| EMA200 | $55.05 | $91.07 | Above W-200 (structural), below D-200 (correcting) |

Weekly chart: price above the weekly 200-EMA ($55.05) = long-term structural trend intact. The current drawdown from $154 to $73 is a correction, not a structural breakdown. Daily chart: price below all three EMAs = active downtrend on the primary trading timeframe.

**VWAP (positional):**
- Daily monthly VWAP $74.00 — price $73.66 is essentially AT the monthly mean
- Daily quarterly VWAP $79.34 — price 7.3% below; quarterly trend is down
- Post-print AVWAP anchor 2026-04-28 $74.06 — cohort: every buyer since the Q1 print. Price −0.55% = flat vs post-print cost basis, meaning post-earnings buyers are barely underwater

**Volume Profile (Daily, 400 bars, range $22–$154):**
- POC: $41.27 — historical center of gravity from years of post-IPO trading at lower prices
- VAH: $104.40 / VAL: $22.05 → price IN VALUE
- HVN: **$74.22** — major prior-volume cluster; current price is resting directly on it

**Volume Profile (Weekly, 249 bars, range $7–$154):**
- POC: $9.87 (IPO-era accumulation, far below)
- VAH: **$74.21** / VAL: $6.81 → price is AT the weekly value-area high
- HVN: $40.51 (next structural support if $74 fails)

**Profile shape (Weekly):** Skewed-b — heavy volume base below with price extended to the upper edge. At the weekly VAH is the defining line: hold it and new value starts building above $74; lose it and price reverts toward the $40–66 range.

**$74 cluster — three sources within 16 cents (high-conviction support):**
1. Post-print AVWAP $74.06 (post-earnings institutional cost basis)
2. Daily HVN $74.22 (historical high-volume cluster)
3. Weekly VP VAH $74.21 (top of 249-bar value area)

**Positional posture:** Active correction within structural uptrend. Sub-200d daily: Pos S. Floor at $71.92 (AVWAP −1σ) then $55 (weekly 200-EMA). No positional entry until daily EMA200 reclaimed.

---

### Swing (Daily + 1H)

**EMA stack (1H, last ≈3 months):** EMA20 $74.64 / EMA50 $77.78 / EMA200 $78.26 — all three above price. Short-term bearish stack; EMA200 at $78.26 is the first structural ceiling.

**VWAP (swing):**
- Daily weekly VWAP $75.16 → the trigger line; reclaim = swing long activated
- Daily monthly VWAP $74.00 → price hugging the monthly mean (consolidation signal)
- 1H weekly VWAP $74.56 → just above current; holding below = slight distribution

**VWAP slope:** Daily quarterly VWAP ($79.34) declining → residual quarterly downward pressure. Distance to quarterly VWAP is 7.3% = significant gap to close before trend turns.

**Volume Profile (1H, 400 bars — last ≈3 months, range $64–$93):**
- POC: $76.56 — the short-term mean price; 7-handle above current → mean-reversion target if buyers show
- VAH: $79.66 / VAL: $66.00 → price IN VALUE
- HVN: $72.83 · $70.35 (below, structural support shelf)
- LVN: $80.28 — thin zone above $79.66 → price travels fast through this band once $80 is cleared

**AVWAP (post-print, 2026-04-28):**
- AVWAP: $74.06 · 1σ: [$71.92 – $76.20] · 2σ: [$69.78 – $78.35]
- Price at AVWAP −0.55% = flat. Post-print buyers at breakeven.
- Reclaim above $74.06 on volume = first confirmation of swing bounce

**Swing posture:** Post-earnings washout consolidating at a defined support cluster. The entry trigger (daily close above $75.16 weekly VWAP) confirms that post-print sellers are absorbed. Stop below the post-print AVWAP −1σ ($71.92) = losing the post-print cost basis entirely. Target: $80 (monthly VWAP + May 15 max pain), then $85 (weekly EMA20 zone).

**Best entry/stop framed:** enter at $75.16 VWAP reclaim, stop $71.92, R:R to $80 = 1.5:1.

---

### Day-trade (1H / Session)

**Reference session: 2026-05-01 EDT (most recent complete session)**

| Level | Value | Notes |
|---|---|---|
| Session VWAP | $74.23 | May 1 session reference; resets at 9:30 AM EDT each day |
| Session VWAP +1σ | $74.65 | Day T1 reference |
| Session VWAP +2σ | $75.07 | Near May 8 max pain |
| Session VWAP −1σ | $73.82 | Day stop reference |
| Session VWAP −2σ | $73.40 | Hard stop reference |

**Session character (May 1):** Consolidation — price ranged $0.98 (3.01% D range, body 5.2%) around VWAP in a tight band. Volume 0.71× 20-session avg. Below-average volume = no edge forcing intraday trades.

**Developing POC (1H session, May 1):** Price oscillated near the $74.22 HVN cluster, consistent with value building at this level.

**VP × VWAP confluence:** Session VWAP ($74.23) co-located with the $74.22 HVN and the post-print AVWAP ($74.06) — all three mark the same structural level. This is where sessions are finding their intraday anchor.

**Day posture:** Below-average volume sessions offer no directional edge. Optimal day setup: (1) NFP May 8 creates a directional session with volume expansion — long on VWAP reclaim above the post-print cluster on a risk-on read; (2) Any session where volume hits ≥1.3× average and price closes an hourly bar above session VWAP. Session VWAP numbers will reset daily; the $74 cluster remains the structural anchor.

---

## Regime Fit

| Horizon | Lean | Reason |
|---|---|---|
| Pos | Neutral | R2 OW financials = sector tailwind; but daily EMA stack fully bearish and crypto-revenue drag not resolved; Pos S locked on technical condition |
| Swing | Favorable | Post-earnings washout at oversold weekly RSI (30.5); max pain pull toward $80; R2 dip-buy thesis in financials; $74 triple confluence defined risk point |
| Day | Neutral | VIX 16.81 = contained moves; NFP May 8 is the nearest binary catalyst; below-avg volume (0.71×) on recent sessions limits intraday edge |

---

## News & Analyst Context

**Catalysts (last 30 days):**
- 2026-04-28: Q1 2026 results — revenue $1.07B vs $1.17B estimate (−8.5%); EPS $0.38 vs $0.41 (−7.3%); crypto trading revenue −47% YoY = primary driver of miss. Gold subscribers 4.3M (+36% YoY, record high); net deposits $18B (22% annualized growth); funded customers 27.4M (+6% YoY) ([Robinhood IR](https://investors.robinhood.com/news-releases/news-release-details/robinhood-reports-first-quarter-2026-results) · [GlobeNewswire](https://www.globenewswire.com/news-release/2026/04/28/3283181/0/en/Robinhood-Reports-First-Quarter-2026-Results.html))
- 2026-04-29: Stock fell ≈11% on the print day. CEO Vladimir Tenev cited a "tokenization supercycle" underway and flagged April as already improving vs Q1 ([Fortune](https://fortune.com/2026/04/29/robinhood-ceo-tokenization-supercycle/))
- 2026-04-30: NYSE is moving toward 24/7 trading — a structural tailwind for HOOD's retail-brokerage model ([24/7 Wall St.](https://247wallst.com/))
- 2026-03-24: HOOD entered a new material financing agreement (8-K items 1.01, 2.03 — debt/agreement; total debt $13.61B reflects this)

**Analyst targets / sentiment:**
- Post-print consensus: multiple targets cut but consensus remains Buy; mean target $98.85 (Yahoo Finance, 24 analysts) = +34% from current $73.66 ([Yahoo Finance analyst tab](https://finance.yahoo.com/quote/HOOD/analysis/))
- 2026-05-02: Analysts cut targets on Q1 miss but universally cited "April already better" as the key offset. Street is pricing a Q2 recovery — consensus Q2 revenue $1.234B (+15.4% QoQ), EPS $0.45 (+18.4% QoQ)
- Range of targets is wide ($48 low – $180 high); tighter institutional cluster in the $90–$130 range

**Sector / peer context:**
- Coinbase (COIN) fell 8% and Webull fell 5% on the same April 29 session — crypto revenue correlation across retail brokers is real ([24/7 Wall St.](https://247wallst.com/investing/2026/04/29/robinhood-tumbles-11-webull-drops-5-coinbase-slides-8-heres-why/))
- HOOD vs Schwab: analyst commentary argues HOOD retains structural advantage with younger demographic; Schwab's older user base doesn't compete for the same cohort ([Yahoo Finance](https://finance.yahoo.com/video/melker-theres-no-way-schwab-can-compete-with-robinhood-to-attract-younger-users-162734283.html))

**Macro overlay:**
- NFP 2026-05-08 (Thursday): strong print = rates up = mixed for financials (brokerage benefits from trading activity; margin pressure from rates). Weak print = cut expectations reignited = equity-favorable, HOOD benefits
- R2 regime OW financials overall; the sector tailwind provides a floor bid ([MACRO/current.md](../../MACRO/current.md))

**Insider / 13F narrative:**
- 13F holder count −25.29% Q/Q (1,359 holders). Likely driven by: FMR LLC (Fidelity) trimming 22.36% of position + broad rebalancing off the $153 high. Vanguard is increasing (passive index effect on float weighting)
- 151 insider sells totaling $416.9M vs zero buys in 6 months. Most likely pre-planned 10b5-1 programs from management post-lockup expiry, but the one-sided skew is a yellow flag on conviction ([Dataroma](https://www.dataroma.com/m/stock.php?sym=HOOD) · [Fintel](https://fintel.io/so/us/HOOD))
- No superinvestors hold HOOD in any tracked portfolio

**Earnings-call language (Q1 2026, post-print):**
- CEO key quotes: "tokenization supercycle" (new market), "April already improving," Gold growth as the durable recurring-revenue engine
- Management framed crypto revenue as cyclical, not structural deterioration
- $18B net deposits at 22% annualized growth = strongest counter-narrative to the headline revenue miss ([GlobeNewswire Q1 release](https://www.globenewswire.com/news-release/2026/04/28/3283181/0/en/Robinhood-Reports-First-Quarter-2026-Results.html))

---

## Flow & Squeeze

| Signal | Reading | As of | Interpretation |
|---|---|---|---|
| Off-Exchange % | 48.62% (30d avg 50.42%) | 2026-05-01 EDT | Slightly below avg — institutions not aggressively accumulating via dark venues |
| Max Pain (May 8 OPEX) | $75.00 (spot 1.79% below) | 2026-05-02 | Mild upward gamma pull into May 8 |
| Max Pain (May 15 OPEX) | $80.00 (spot 7.93% below) | 2026-05-02 | Strong upward pull; dominant near-term magnet |
| Max Pain (May 22) | $80.00 (spot 7.93% below) | 2026-05-02 | Confirms $80 is the structural pin zone for the month |
| P/C OI (May 8) | 0.52 (call-heavy) | 2026-05-02 | Bullish options positioning; dealers net short calls above $75 |
| P/C OI (May 15) | 0.75 | 2026-05-02 | Still call-heavy; $80 pin behavior likely |
| Short Interest | 4.08% float, DTC 1.10 | 2026-04-15 (FINRA 2-wk lag) | Low short pressure; no squeeze dynamics |
| FTD | ≈50K shares/day avg (Apr) | 2026-04-14 (30+ day lag) | Negligible vs 783M float; not a factor |
| Borrow Fee | 0.25% annualized | 2026-05-02 EDT | Easy-to-borrow; no squeeze thesis |

**Composite squeeze score: Low** — SI 4.08%, DTC 1.10, borrow 0.25%, FTDs negligible. Flow thesis is purely gamma-driven, not short-squeeze.

```text
Force diagram — net direction into May 15 OPEX:

      spot $73.66
           ●
           │
           ▲  ▲  ▲  gamma pull (max pain $80.00 — spot 7.9% below pin)
           ▲  ▲  ▲  dealer hedge (P/C 0.52 — net short calls; buy-hedge fires on any push past $75)
           │  (dark pool 48.6% vs 50.4% avg — neutral, no institutional force)
           │
           △
      $80.00 ──── target by 2026-05-15

      Low squeeze tier (SI 4.08%, borrow 0.25%) — no amplification
      → gamma pull active; dealer covering reinforces any push toward $80
```

**Flow → trade decision:**
1. **Gamma pull:** spot is below max pain on every upcoming OPEX through May 29. The May 15 $80 pin is dominant. Any sustained daily close above $75.16 engages the call-hedging feedback loop.
2. **Dealer gamma (P/C 0.52, May 8):** call-heavy OI means dealers are net short calls and long delta above $75. As price rises toward $75, dealer buy-hedging increases — the $75 wall becomes a magnet, not a ceiling.
3. **Dark pool:** 48.6% vs 50.4% 30-day avg = slightly quiet. Institutions are not pressing the accumulation button yet at $74. Neutral.
4. **Implied trade:** $75/$82.50 call spread expiring May 15 captures the gamma drift toward the $80 pin with defined risk (max loss = debit paid). Entry valid at current levels or on VWAP reclaim trigger (Swing-B in trade table above).

---

## Earnings Setup — Q2 2026 (≈88 days)

Next print: ≈2026-07-29 AMC. Within 90-day window; actionable pre-print read valid by late June.

| Point | Reading |
|---|---|
| Q1 surprise | MISS — revenue −8.5% vs est, EPS −7.3% vs est; stock −11% on print day |
| Miss driver | Crypto trading revenue −47% YoY (cyclical slump, not structural loss of platform). CEO flagged April improving |
| Platform metrics trending | Gold subscribers 4.3M (+36% YoY, record); net deposits $18B at 22% annualized; ARPU +8% |
| Q2 consensus | Revenue $1.234B (+15.4% QoQ recovery); EPS $0.45 (+18.4% QoQ) |
| Post-print settling | Stock found a floor at $74 cluster; absorbed the miss without breaking weekly 200-EMA |
| Institutional holder trend | Declining (−25% Q/Q). Key watch: does holder count stabilize in Q2 13F filings? |
| Options positioning | P/C 0.52–0.83 across May expirations = call-heavy throughout; market expecting recovery |
| Key Q2 risk | If crypto volumes stay depressed through May–June, the $1.234B consensus misses again. Recovery requires crypto revenue or Gold/PFOF to compensate the ≈$164M Q-over-Q gap |

**Max pain for Q2:** July options OI not yet built. Revisit in the rescan as the print approaches and July OPEX accumulates OI.

---

## Verdict per horizon

| Horizon | Tier | Verb | Dominant | Upgrade condition | Downgrade condition |
|---|---|---|---|---|---|
| Pos | S | WAIT | — | Daily EMA200 reclaim ($91) + 2 consecutive quarters revenue ≥20%; 13F holder count stabilizing → assess for B or W | N/A (already S) |
| Swing | W | LONG | **Yes** | Daily close >$75.16 on volume fires trigger → entry confirmed, tier T for the trade | Daily close <$71.92 (AVWAP −1σ) invalidates the $74 support thesis → S until $80 recovered |
| Day | W | LONG | — | Volume ≥1.3× avg + VWAP reclaim on a catalyst session (NFP May 8 or similar) → T for that session | Volume stays sub-avg → B (no intraday edge) |

**Dominant horizon: Swing.** The $74 triple-confluence provides a well-defined risk point for a 3–10 day trade to $80 with 1.5:1 R:R on shares (≈3:1 via call spread). Positional is blocked by the technical condition; day-trade requires volume to materialize.

---

## Sources

- [Yahoo Finance — HOOD quote](https://finance.yahoo.com/quote/HOOD/)
- [SEC EDGAR — HOOD filings CIK 0001783879](https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001783879)
- [Robinhood IR — Q1 2026 Results](https://investors.robinhood.com/news-releases/news-release-details/robinhood-reports-first-quarter-2026-results)
- [GlobeNewswire — Q1 2026 Full Release](https://www.globenewswire.com/news-release/2026/04/28/3283181/0/en/Robinhood-Reports-First-Quarter-2026-Results.html)
- [CNBC — Q1 earnings miss](https://www.cnbc.com/2026/04/28/robinhood-shares-fall-after-earnings-revenue-miss.html)
- [Fortune — Tokenization supercycle](https://fortune.com/2026/04/29/robinhood-ceo-tokenization-supercycle/)
- [Fintel — HOOD institutional ownership](https://fintel.io/so/us/HOOD)
- [Dataroma — HOOD superinvestors](https://www.dataroma.com/m/stock.php?sym=HOOD)
- [ChartExchange — HOOD dark pool](https://chartexchange.com/symbol/nasdaq-hood/exchange-volume/dark-pool-levels/)
- [ChartExchange — HOOD short interest](https://chartexchange.com/symbol/nasdaq-hood/short-interest/)
- [ChartExchange — HOOD FTD](https://chartexchange.com/symbol/nasdaq-hood/failure-to-deliver/)
- [ChartExchange — HOOD borrow fee](https://chartexchange.com/symbol/nasdaq-hood/borrow-fee/)
- [Yahoo Finance — HOOD analyst ratings](https://finance.yahoo.com/quote/HOOD/analysis/)
- [24/7 Wall St. — Q1 peer reaction](https://247wallst.com/investing/2026/04/29/robinhood-tumbles-11-webull-drops-5-coinbase-slides-8-heres-why/)
- [Barron's — Q1 earnings preview](https://www.barrons.com/articles/robinhood-stock-price-earnings-7e6a6a18)
