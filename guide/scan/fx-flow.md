# FX Flow & Positioning — COT, retail sentiment, rate differentials

> Part of the [scan protocol](../scan-rules.md). See also: [data](data.md), [crypto-flow.md](crypto-flow.md), [index-flow.md](index-flow.md), [commodity-flow.md](commodity-flow.md).

---

This doc is the **FX analogue** of `crypto-flow.md`. Triggered when `/scan` runs against any 6-letter FX pair (`EURUSD`, `USDJPY`, `GBPUSD`, `AUDUSD`, `USDCHF`, `USDCAD`, `NZDUSD`, exotic crosses).

The chart read on the FX pair is still primary. Flow & positioning is supplementary — strongest when COT institutional positioning + retail sentiment extreme + rate-differential trend ALL agree with the chart.

---

## Why COT is the prime FX signal

Per [`docs/positioning.md` § CFTC Commitments of Traders](../../docs/positioning.md#cftc-commitments-of-traders-cot) — trader categories (non-commercial / commercial / spread / non-reportable), standard reads (3-yr extremes contrarian, commercial vs spec divergence, ΔWoW), sources, and what COT does and doesn't capture.

FX has no exchange-listed options market that compares to crypto/equity, no centralized liquidity venue, no max-pain analogue. CME FX futures COT proxies spot FX positioning for the major pairs and is the desk-standard institutional signal — the operational FX-specific reading procedure (sources, lag, table format) lives in Tier A/B below.

The second-tier signal is **retail sentiment** — published by IG, OANDA, FXBlue, MyFXBook. Useful as a **contrarian** read at extremes (when retail is 80%+ long, fade it).

The third-tier signal is **rate differentials** — the carry-trade engine. EUR-USD, USD-JPY, etc. — the 2yr / 10yr yield gap drives long-cycle trends.

---

## Two-tier capture

### Tier A — WebFetch (always pull)

| Metric | Source | URL pattern | Lag |
|---|---|---|---|
| **CFTC COT (CME FX futures)** | CFTC | `https://www.cftc.gov/dea/futures/deacmesf.htm` (links to current Friday CSV; or use `https://publicreporting.cftc.gov/api/views/...` with the dataset ID) | weekly Tue 3:30pm ET (T+3 day lag for data dated prior Tue) |
| **Macro regime cross-ref** | scanned/MACRO/current.md | local | last MACRO scan |
| **Forex Factory calendar** | forexfactory.com | `https://www.forexfactory.com/calendar` (sometimes blocked; fall back to chrome-devtools) | live |
| **Rate differentials (2yr / 10yr)** *(when both currencies have public yield endpoints)* | TradingEconomics search | `https://tradingeconomics.com/<country>/government-bond-yield` | varies |

**Notes on gaps:**
- **Yahoo Finance FX endpoints** rate-limit (503). Use the chart pipeline (TradingView) for spot rate.
- **DailyFX SSI / IG sentiment** typically 403. Sentiment via Tier B.
- **TradingEconomics** often works for rate diffs but sometimes 403 — fall back to chart screenshot of the 2yr yield futures.
- **OANDA position book** is broker-specific and requires login.

### Tier B — chrome-devtools screenshot

| Metric | Source URL | What we capture |
|---|---|---|
| **IG Client Sentiment** | [ig.com/en/forex/markets-forex/client-sentiment](https://www.ig.com/en/forex/markets-forex/client-sentiment) | Long % vs short % per pair |
| **MyFXBook community outlook** | [myfxbook.com/community/outlook](https://www.myfxbook.com/community/outlook) | Per-pair retail positioning |
| **OANDA orderbook + positionbook** | [oanda.com/forex-trading/analysis/order-book](https://www.oanda.com/forex-trading/analysis/order-book) | Where retail orders sit (limit + stop clusters) |
| **Forex Factory calendar** (when WebFetch 403) | [forexfactory.com/calendar](https://www.forexfactory.com/calendar) | High-impact catalyst dates |
| **TradingView 2yr yield differential chart** | TV custom symbol like `US02Y-DE02Y` | Visual carry-trade engine read |

---

## Squeeze tiering for FX

FX doesn't squeeze the way crypto/stocks do (no leveraged-perp market with funding rates). But **positioning extremes + sentiment extremes + carry pressure** create directional vulnerabilities. Adapted tier:

| Tier | Conditions |
|---|---|
| **Crowded long (mean-reversion risk)** | COT non-commercial net long at 3-yr high AND retail long > 70% AND rate differential narrowing → **likely correction lower** |
| **Crowded short (mean-reversion risk)** | COT non-commercial net short at 3-yr low AND retail short > 70% AND rate differential widening (against shorts) → **likely correction higher** |
| **Aligned trend** | COT institutional + retail same direction AND rate differential agrees → **trend continuation likely** |
| **Divergent positioning** | COT non-commercial vs retail opposite (institutional long, retail short, or vice versa) → **follow institutional** |
| **Neutral / range** | COT and retail both within 1-yr norms; rate diff stable → **range trading / mean revert** |

---

## Section template (paste into `current.md` for FX scans)

```markdown
### FX Flow & Positioning

#### Institutional positioning (CFTC COT — Tier A)

| Metric | Value | As of | Read |
|---|---|---|---|
| Non-commercial NET (longs − shorts) | <X> contracts | YYYY-MM-DD (T+3 lag) | Long-extreme (3y high) / short-extreme / neutral |
| Non-commercial 4-week change | +/-X | — | Building or unwinding |
| Commercial NET | <X> contracts | — | Usually opposite of non-comm |
| Open interest 4-week change | +/-X% | — | OI rising = trend confirmation; falling = de-leverage |

#### Retail sentiment (Tier B — chrome-devtools)

![IG Client Sentiment — YYYY-MM-DD](charts/<PAIR>_<YYYY-MM-DD>_ig_sentiment.png)

| Source | Long % | Short % | Read |
|---|---|---|---|
| IG Client Sentiment | X% | X% | — |
| MyFXBook outlook | X% | X% | — |
| OANDA orderbook clusters | (cite levels) | — | Where stops/limits cluster — magnetic |

**Retail extremes** (>70% one-side) → contrarian.

#### Rate differential (carry engine)

| Spread | Value | 4w trend | Read |
|---|---|---|---|
| Currency-A 2yr − Currency-B 2yr | X bp | widening / narrowing | Carry pressure direction |
| Currency-A 10yr − Currency-B 10yr | X bp | widening / narrowing | Long-cycle trend driver |
| Real-rate diff (2yr − CPI) | X bp | — | Capital-flow attraction |

#### Catalyst calendar (next 30 days)

| Date | Event | Currency | Tier |
|---|---|---|---|
| YYYY-MM-DD | (rate decision, NFP, CPI, etc.) | Currency-A or B | high / med / low |

#### Composite tier

**[Crowded long / Crowded short / Aligned trend / Divergent / Neutral]**

#### Cross-confluence with the chart read

[Does COT institutional bias agree with the chart's right-edge candle? Is retail sentiment opposite to chart? Does the rate-diff trend confirm any reversal pattern in progress?]
```

---

## Source-priority chain

- **Positioning**: CFTC COT > IG Client Sentiment > MyFXBook (CFTC is the ground truth; retail signals are contrarian-only)
- **Rate diffs**: TradingEconomics > TradingView 2yr/10yr chart screenshot
- **Calendar**: Forex Factory > Investing.com (latter often blocks)

---

## Rules

- **CFTC COT is non-optional on every FX scan.** It's the desk-standard signal.
- **Retail sentiment is contrarian-only.** Never use it as a directional confirmation in the same direction; only as a fade signal at extremes.
- **State the COT data date.** Always T+3 days lagged from the report-date Tuesday. A scan dated Friday reads Tue's report which describes the prior Tue's positioning — that's a 10-day-old number on Friday. Don't pretend it's fresh.
- **FX scans don't get Crypto Flow or Index Flow sections.** They get THIS section. Mutually exclusive.
