# VWAP — volume-weighted average price as institutional benchmark

VWAP (Volume-Weighted Average Price) is the volume-weighted intraday average a security has traded at across a session. Unlike a simple or exponential moving average — which weights each bar equally or by time-decay — VWAP assigns weight by **volume**, so heavy-volume bars pull the line toward themselves and quiet bars barely move it. Pension funds, mutual funds, and execution desks use VWAP as the **passive-execution benchmark**: filling a 500k-share order *below* the day's VWAP means the desk beat the market average and bought "well"; filling above VWAP means underperformance. Because that benchmark drives trillions of dollars of order flow, the line itself becomes a self-fulfilling magnet — institutions defend it, scale into pullbacks toward it, and treat distance from VWAP as their P&L mark. For a discretionary trader, VWAP is therefore not "another moving average." It is the price institutions are forced to care about.

## Contents

- [Core concept](#core-concept)
- [Calculation in detail](#calculation-in-detail)
- [VWAP variants](#vwap-variants)
- [Reading VWAP in practice](#reading-vwap-in-practice)
- [Anchored VWAP — when and how](#anchored-vwap--when-and-how)
- [Standard deviation bands](#standard-deviation-bands)
- [Trading applications](#trading-applications)
- [Confluence techniques](#confluence-techniques)
- [Common pitfalls](#common-pitfalls)
- [When VWAP is most reliable](#when-vwap-is-most-reliable)
- [When VWAP is less reliable](#when-vwap-is-less-reliable)
- [Combining with Volume Profile](#combining-with-volume-profile)
- [How `/scan` uses VWAP](#how-scan-uses-vwap)
- [References](#references)

---

## Core concept

VWAP is the dynamic fair value of a session, weighted by where actual money changed hands. It answers a simple question: **at what average price has the market truly transacted, accounting for size?**

- **Weighting is by volume, not time.** A 1-million-share trade at $100.20 moves VWAP more than a 10k-share trade at $100.50. An EMA can't see that — it sees two bars and weights by recency. VWAP sees liquidity.
- **It resets on session boundaries.** Standard intraday VWAP starts fresh at the cash open (09:30 ET on US equities) and accumulates across the day. The next session, the cumulative sums reset to zero. This is why classic VWAP is **intraday-only** by default — extending the calculation across days without re-anchoring dilutes it into noise.
- **It is path-dependent.** Two days that close at the same price but distribute volume differently (e.g., heavy volume at the lows then a low-volume drift up vs. heavy volume at the highs then a low-volume drift down) will print very different VWAPs. The line encodes intraday positioning.
- **It is a "fair value" line, not a trend line.** Price above VWAP = the average buyer is in profit, the average seller is at a loss. Price below = the inverse. That asymmetry is why VWAP acts as a magnet on retraces — institutions average down toward it, and short sellers fade rallies away from it.

VWAP differs from moving averages in three ways: (1) volume weighting (already covered), (2) anchored start point (resets per session, or anchored to a chosen event), and (3) institutional execution mandate — there is no pension fund tasked with executing relative to a 50-EMA.

## Calculation in detail

The standard intraday formula:

```
                Σ ( typical_priceᵢ × volumeᵢ )
VWAP_t  =  ────────────────────────────────────
                       Σ ( volumeᵢ )

where i runs from session start (or anchor bar) to bar t
typical_priceᵢ = ( Hᵢ + Lᵢ + Cᵢ ) / 3
```

Step by step (the textbook five-step recipe):

1. For each intraday bar, compute the **typical price** = (high + low + close) / 3.
2. Multiply typical price by the bar's volume → bar's "price-volume" contribution.
3. Maintain a **running cumulative sum** of price-volume from session/anchor start.
4. Maintain a **running cumulative sum** of volume from session/anchor start.
5. VWAP at bar *t* = cumulative price-volume / cumulative volume.

Because the running sums grow monotonically through the session, **VWAP becomes more stable as the day progresses** — a 09:35 VWAP is dominated by the opening bar; a 15:55 VWAP reflects the entire day's volume. Early-session VWAP is noisy and easily distorted by an opening drive; late-session VWAP is a stable fair-value reference. Most VWAP edge appears after the first 30–60 minutes when the cumulative volume base is large enough to absorb a single hot bar.

### Why intraday-only by default

If you let VWAP run continuously across multiple sessions without re-anchoring, the cumulative sums grow so large that any single new bar barely moves the line. Within a few weeks the indicator becomes effectively flat — a long-run average that lags every meaningful pivot. The institutional execution mandate also resets daily (no fund benchmarks against last week's VWAP), so the indicator is structurally a one-session tool unless you re-anchor it deliberately.

### VWAP vs. TWAP

The closest cousin to VWAP is **TWAP (Time-Weighted Average Price)** — the simple time-equal average of price across an interval, with no volume weighting. TWAP is used by execution desks that want to disguise size by spreading equally across time regardless of where liquidity is. VWAP is used by desks benchmarked against the market's actual fill profile. For a discretionary trader, VWAP carries far more signal: it tells you where money *actually* moved, not where the clock said it should have. TWAP can be useful as an execution algorithm in thinly-traded names where there isn't enough volume to weight against; for chart-reading, VWAP wins on every metric.

### Calendar-anchored variants

To extend VWAP usefully beyond a single session, anchor to a **calendar period** rather than running it continuously:

- **Weekly VWAP** — anchored to Monday open, accumulates through Friday close. Useful for swing traders on the daily chart.
- **Monthly VWAP** — anchored to the first trading day of each month. A common institutional rebalance benchmark.
- **Quarterly VWAP** — anchored to the start of the calendar quarter. Often coincides with earnings cycles and 13F windows; relevant for position-sized work.
- **Yearly VWAP / YTD-anchored VWAP** — anchored to the first trading day of January. The "year's average buyer" cost basis.

### Anchored VWAP (AVWAP)

Instead of a calendar boundary, the user picks a **specific bar** as the anchor — typically the bar of a meaningful event (earnings gap, FOMC release, swing high, swing low, IPO). The cumulative sums begin at that bar and accumulate forward. AVWAP is treated separately below; it's the most flexible and arguably the most powerful form of the indicator.

## VWAP variants

| Variant | Anchor | Reset cadence | Primary use |
| --- | --- | --- | --- |
| **Session / Daily VWAP** | Session open (09:30 ET cash) | Every session | Intraday execution benchmark; day-trade S/R |
| **Weekly VWAP** | Monday open | Every Monday | Swing-trade trend reference on daily chart |
| **Monthly VWAP** | 1st trading day of month | Monthly | Institutional rebalance benchmark |
| **Quarterly VWAP** | 1st trading day of quarter | Quarterly | Earnings-cycle / 13F window reference |
| **Yearly / YTD VWAP** | 1st trading day of year | Yearly | Long-term cost-basis reference |
| **Anchored VWAP (AVWAP)** | User-chosen event bar | Manual / event-driven | Cost-basis read for a specific cohort of buyers/sellers |
| **VWAP ± σ Bands** | Same as parent VWAP | Same as parent | Volatility envelope for mean-reversion / breakout reads |

The first four are deterministic (you don't choose the anchor — the calendar does). AVWAP is discretionary — and that's where Brian Shannon's framework matters.

## Reading VWAP in practice

The four core reads, applied to whichever VWAP variant matches the trading horizon:

1. **Side of VWAP**
   - Price **above** session VWAP → intraday bulls in control; the average buyer is profitable.
   - Price **below** session VWAP → intraday bears in control; the average seller is profitable.
   - Use this as the trade-direction filter, not as a fade signal.

2. **Slope**
   - **Rising** VWAP → demand has been accumulating throughout the session; long bias.
   - **Falling** VWAP → supply has been distributed; short bias.
   - **Flat** VWAP → range / two-sided session; reduce size, fade extremes.
   - Slope inflections (rising → flat → falling) often precede price inflections by minutes.

3. **Distance from VWAP**
   - Small distance (price hugging VWAP) = balanced two-way flow, equilibrium.
   - Large distance (price extended above/below) = trending session; mean-reversion to VWAP becomes increasingly probable as distance grows beyond ±2σ.
   - Distance is best measured in **σ-band units**, not absolute dollars — this normalizes across volatility regimes.

4. **Behavior at the line**
   - Multiple touches that **hold** = VWAP is acting as S/R; the institutional bid/offer is real.
   - First test breaks **decisively** = change of character; expect a regime shift (long → short side, or vice versa).
   - Whipsaw across VWAP = range / chop; sit out or fade the σ-band extremes.

A common rookie error is treating any cross of VWAP as a signal. It isn't — only **the first decisive cross after a clear trend, on volume** is a reliable change-of-character read. Random whipsaws across a flat VWAP are noise.

## Anchored VWAP — when and how

AVWAP is Brian Shannon's signature contribution to the modern technical-analysis literature (codified in *Maximum Trading Gains With Anchored VWAP*, CMT Association, 2022). The premise: not every bar matters equally. Certain bars — earnings prints, FOMC announcements, IPO opens, gap days, decisive swing pivots — re-set the cohort of buyers and sellers in a stock. Anchoring VWAP to those bars reveals the **cost basis** of the cohort that entered at the event, and that cost basis becomes a real S/R level.

### Anchor selection criteria

Anchor to bars that meet **at least one** of these criteria:

- **Significant swing high** — the AVWAP from a major swing high is the average price every buyer who chased the top is now sitting at. While price stays below it, those buyers are underwater; reclaiming the AVWAP from above signals they've been made whole and are no longer forced sellers.
- **Significant swing low** — the AVWAP from a flush low is the average cost basis of dip-buyers. While price stays above it, those buyers are profitable and act as defenders on retests.
- **Earnings gap** — anchor to the bar of the earnings release. Reaction to the print sets the new cohort; the AVWAP from earnings is the institutional fair value implied by the post-print volume.
- **FOMC / CPI / NFP release** — anchor to the bar of the macro print. Useful on indices, FX, and rates-sensitive equities.
- **IPO date** — the AVWAP from the IPO is the literal average cost basis of every public shareholder. A loss of this line is a generational change-of-character signal.
- **Gap up / gap down** — anchor to the bar that contains the gap. Gap-fill behavior is best read against this AVWAP.
- **Year-to-date open / quarter open / month open** — calendar-anchored variants act like AVWAPs by default. The YTD AVWAP is the fair value of the year's flows.
- **Post-split adjustment date** — relevant for splits and reverse-splits where the share count changes the dollar-volume profile.
- **Major news / FDA / product launch** — biotech and pharma especially. The bar of a binary catalyst is a clean AVWAP anchor.

### Anchor-selection rule of thumb

If you can't articulate, in one sentence, **why** the cohort that traded at that bar is structurally meaningful, the anchor is wrong. Random pivots don't produce useful AVWAPs. Earnings, decisive swings, and macro catalysts do.

### Multi-AVWAP confluence

Stacking multiple AVWAPs (e.g., from the prior swing high + last earnings + YTD open) creates a **confluence map**: zones where two or more AVWAPs cluster within a few percent of each other. Those zones are high-probability S/R because multiple cohorts are defending the same price.

A clean institutional setup: AVWAP-from-swing-low rises to meet AVWAP-from-earnings, both at a Fibonacci 0.618 retrace, with Volume Profile POC at the same price. That is a four-way confluence — the kind of level that holds on the first test 70%+ of the time.

### Reclaim and lose

- **Reclaim** of an AVWAP from a swing high (price moves from below back above) = the trapped chasers are made whole; supply pressure releases. Often the best long-side change-of-character signal in the entire toolkit.
- **Lose** of an AVWAP from a swing low (price moves from above back below) = the dip-buyers are now underwater; defensive bid evaporates. Forced-selling cascade risk; trim longs aggressively.

The reclaim/lose framing only works for AVWAPs anchored to **meaningful** events. A reclaim of an AVWAP from a random Tuesday tells you nothing.

### Cohort interpretation — who is on each AVWAP

The deepest insight from Brian Shannon's work is that every AVWAP encodes the cost basis of an identifiable cohort. Reading AVWAPs is therefore a positioning read, not just a chart read:

- **AVWAP from a major high** → the cohort that bought the top. While price < AVWAP, that cohort is at a loss; expect supply at the line on rallies as trapped longs exit at break-even.
- **AVWAP from a major low** → the cohort that bought the flush. While price > AVWAP, that cohort is profitable; expect demand at the line on retests as profitable longs add or new buyers anchor against the same level.
- **AVWAP from earnings** → the cohort that re-priced the stock against the new fundamentals. The post-earnings AVWAP is "the new institutional fair value" — losing it suggests the print is being un-priced (downgrade narrative); reclaiming it from below suggests the print is being re-priced higher (analyst follow-through).
- **AVWAP from IPO** → every public shareholder ever. Loss of the IPO AVWAP is one of the cleanest "broken stock" signals in the equity market — the median public buyer is now underwater.
- **AVWAP from FOMC / CPI** → rate-sensitive cohorts. Useful on indices, long-duration tech, and rate-sensitive financials.

The general framing: ask **whose money is on this line?** If the answer is a coherent, sized cohort, the AVWAP will respect itself. If the answer is "no one in particular," the line is decorative.

## Standard deviation bands

VWAP ± σ bands wrap the line in a volatility envelope — analogous to Bollinger Bands wrapping an SMA, but volume-weighted instead of time-weighted. The bands are computed from the volume-weighted standard deviation of typical price around VWAP across the same accumulation window.

### Standard band thresholds

- **±1σ band** — typical containment. Roughly 68% of intraday price action stays within ±1σ in a normal-volatility session. Mean-reversion targets when price overshoots, magnets back to VWAP itself.
- **±2σ band** — extreme. Roughly 95% of intraday price action stays within ±2σ. Touches of the 2σ band on declining momentum are high-probability counter-trend rejection points; touches on **expanding** momentum signal a trend day in progress, not a fade.
- **±3σ band** (less common, sometimes shown) — outlier zone. Touches almost always coincide with news catalysts or stop runs.

### Band width as volatility gauge

Band width expands during trending, high-volume sessions and contracts during quiet ranges. Sustained narrow-band conditions (a "VWAP squeeze") often precede session-scale breakouts — analogous to a Bollinger squeeze, but volume-weighted.

### Standard band-trading rules

- **Pullback long** in an uptrend: enter on a tag of VWAP or +1σ from above; first target = prior swing or +2σ; stop = below VWAP by ATR/3.
- **Pullback short** in a downtrend: mirror — enter on tag of VWAP or −1σ from below; target prior swing or −2σ.
- **Range-day fade**: tag of +2σ on stalling momentum → short toward VWAP; tag of −2σ on stalling momentum → long toward VWAP. Skip if VWAP slope is non-flat.
- **Trend-day ride**: price holds above +1σ for extended periods → don't fade the strength; pullbacks to VWAP are buys, not tops.

The σ-band rules are conditional on session character. **Trend day → ride; range day → fade.** Misreading the session character is the single biggest source of band-trading losses.

## Trading applications

The four canonical session archetypes and the VWAP play that fits each:

### 1. Trend day (directional, expanding bands, above-average volume)

- Price opens with conviction, drives away from VWAP, and never closes back through it.
- VWAP slope is steep and consistent.
- Best play: **pullback to rising VWAP = long entry** (or pullback to falling VWAP = short entry). Stop = ATR/3 beyond VWAP. Target = prior session swing or +2σ band.
- Avoid fading the +2σ band — on a trend day, 2σ is the new VWAP.

### 2. Range day (oscillating, flat VWAP, contracting or stable bands)

- Price oscillates around a flat VWAP through the day.
- VWAP slope ≈ 0; bands stable or narrowing.
- Best play: **fade the 2σ extremes back to VWAP**. Skip the VWAP touches themselves (no edge in the middle of a range).
- Avoid breakout entries — on a range day, breaks of VWAP fail; mean-reversion wins.

### 3. Breakout day (consolidation → directional break)

- Morning consolidation builds within ±1σ.
- Price breaks decisively above (or below) VWAP **on volume expansion** mid-session.
- Best play: enter on the breakout retest of VWAP from the strong side; stop on a clean re-entry to the range.
- The breakout signal requires a **volume confirmation** — price-only crosses of a flat VWAP are noise.

### 4. Reclaim / lose day (change-of-character)

- Price has trended one side of VWAP for hours, then crosses decisively to the other side and holds.
- The reclaim (or lose) is the **change-of-character bar** — bias for the rest of the session flips.
- Best play: enter on the first pullback to VWAP from the new strong side; stop on a re-cross.
- Reclaims/losses are most reliable late-session (after 11:00 ET) when the cumulative volume base makes VWAP stable.

### Divergence

When price extends to new highs (or lows) but VWAP slope **flattens or reverses**, the new extreme is being made on declining volume — a textbook divergence. Treat as a warning, not an entry trigger; wait for VWAP to confirm with a slope shift before flipping bias.

### Session character — the meta-read

Before any specific VWAP play, classify the session character in the first 30–60 minutes:

| Character | VWAP slope | Band width | Side-of-VWAP | Best plays |
| --- | --- | --- | --- | --- |
| **Trend day up** | Steep + rising | Expanding | Sustained above | Pullback long to VWAP / +1σ; ride to +2σ |
| **Trend day down** | Steep + falling | Expanding | Sustained below | Rally short to VWAP / −1σ; ride to −2σ |
| **Range day** | Flat | Stable / contracting | Whips both sides | Fade ±2σ tags back to VWAP |
| **Consolidation → breakout** | Flat → directional | Contracting → expanding | Tight, then break | Enter on retest of VWAP from new strong side |
| **Reversal / change-of-character** | Reverses mid-session | Variable | Flips decisively | Fade exhaustion at σ-band; new bias after VWAP reclaim/lose |

Misclassifying the session is the dominant source of VWAP losses. A "fade the 2σ" rule applied to a trend day is a recipe for repeated stop-outs; a "ride pullbacks to VWAP" rule applied to a range day is a recipe for slow bleeding. The session character read comes first, the trade rule comes second.

## Confluence techniques

VWAP gains its highest signal when it co-locates with another independent technical level. The five highest-quality confluence patterns:

1. **Anchored VWAP + horizontal level** — AVWAP from a swing high meets a prior consolidation high. Two independent reasons for resistance at the same price.
2. **Anchored VWAP + Fibonacci retracement** — AVWAP from a low meets the 0.618 retrace of the parent move. Common pullback-entry zone.
3. **Daily VWAP + previous-day high/low (PDH/PDL)** — session VWAP rising into PDH adds a second resistance reference; rejection there is a clean short.
4. **Multi-AVWAP cluster** — three or more AVWAPs (e.g., from swing low + earnings + YTD open) converging within 1–2% of each other = high-conviction zone, often holds 70%+ on first test.
5. **VWAP + Volume Profile POC** — the session POC (highest-volume price node, see [`volume-profile.md`](volume-profile.md)) sitting within a few cents of VWAP = double-confirmed fair value. Reversion to that price is the highest-probability intraday play.

The general rule: a single VWAP touch is a setup; a VWAP touch with one independent confluence is a **trade**; a VWAP touch with two independent confluences and macro/regime alignment is a **size-up trade**.

## Common pitfalls

1. **Pre-market / extended-hours data inclusion** — platforms differ. Some include pre-market in the cumulative sums (distorts the open VWAP); some start at 09:30 ET cash open. Verify on your platform — the wrong setting will give you a VWAP that doesn't match the institutional benchmark every desk is trading against.
2. **Thin-volume distortion** — VWAP is unreliable on illiquid tickers. A few hundred shares at an outlier price can shift the line by full percent. Below ~500k average daily volume, treat VWAP outputs with suspicion.
3. **Using session VWAP on multi-day charts without anchoring** — a daily-bar chart with a session-VWAP overlay shows nothing useful. Either switch to intraday or convert to weekly/monthly/anchored.
4. **Treating session VWAP as significant after the close** — once the session closes, that VWAP is locked. The institutional benchmark for the next day starts fresh. Yesterday's VWAP is at best a horizontal reference, not a live indicator.
5. **Assuming mean reversion is automatic** — "price always returns to VWAP" is myth. On a strong trend day, price extends from VWAP and never comes back. Mean reversion is a **conditional** read (range day, declining momentum at σ-band), not a rule.
6. **Treating the first 30 minutes of VWAP as reliable** — the cumulative volume base is too small early; one big bar dominates the line. VWAP becomes a stable read after the first 30–60 minutes, not at 09:31.
7. **Trading VWAP alone** — VWAP is a high-quality reference, not a complete system. Without confluence (volume, structure, macro, regime), VWAP-only entries underperform.
8. **Ignoring news / catalysts** — earnings, FDA, FOMC blow up the volume distribution. VWAP through a news bar is statistically meaningless until the new cohort stabilizes (typically 30–60 minutes post-event).
9. **Fading the 2σ band on a trend day** — by far the most expensive mistake. On a trend day, the 2σ band is a momentum confirmation, not an exhaustion signal.

## When VWAP is most reliable

- **Liquid instruments** — large-cap equities (>$5B market cap, >2M ADV), index futures (ES, NQ, RTY), major FX pairs (EUR/USD, USD/JPY, GBP/USD), and major crypto (BTC, ETH, SOL).
- **Regular trading hours** — for US equities, 09:30–16:00 ET cash session. Pre-market and post-market VWAP is noisy and rarely respected.
- **Trending or clearly ranging environments** — VWAP works in both, but the *trade* changes (ride pullbacks vs. fade extremes). Fails in chaotic, news-driven sessions where there's no coherent regime.
- **Mid- to late-session reads** — after 11:00 ET, cumulative volume is high enough that VWAP is stable and respected.
- **AVWAP from major events** — earnings, FOMC, IPO, decisive swing pivots. These produce S/R that holds across weeks.

## When VWAP is less reliable

- **News-gap opens** — when the open is far from prior close, the volume distribution is distorted; VWAP early in the session is dominated by the gap-bar volume spike.
- **Pre/post-market** — thin volume = unstable cumulative sums. Don't trade off pre-market VWAP except on liquid futures.
- **Illiquid micro-caps / low-float names** — sub-500k ADV, the line is too easily moved by a single retail print. Volume-weighting loses meaning when volume is sparse.
- **First 15–30 minutes of any session** — too few bars in the cumulative base; an opening drive dominates the line.
- **Earnings / FDA / binary-event days** — through the catalyst, volume is one-sided and VWAP becomes a meaningless rolling average. Wait for the new cohort to settle.
- **Random non-event AVWAP anchors** — anchoring to a random Tuesday produces a line with no institutional cohort behind it; price ignores it.

## Combining with Volume Profile

Volume Profile (covered in detail in [`volume-profile.md`](volume-profile.md)) is the structural complement to VWAP. Where VWAP is a single dynamic line — the time-evolving fair value — Volume Profile is a static distribution that shows **how volume is distributed across price levels** across a chosen window.

The three highest-value VWAP × Volume Profile interactions:

- **POC near VWAP = high-conviction fair value.** When the session POC (highest-volume price level) sits within a fraction of a percent of VWAP, both indicators agree on fair value. Reversion to that price on a tag of ±2σ is the highest-probability intraday mean-reversion play.
- **AVWAP-from-event near a Volume Profile HVN (High-Volume Node).** AVWAP says "this is the cohort's cost basis"; HVN says "this is where institutions accumulated significant inventory." Same price = strong S/R. The intersection often defines multi-week consolidation floors and ceilings.
- **POC vs. VWAP divergence reveals positioning bias.** If POC is meaningfully above VWAP, late-session volume came in higher (distribution at the highs → potential top). If POC is below VWAP, late-session volume came in lower (accumulation at the lows → potential bottom). The gap between POC and VWAP is a positioning tell.

For full Volume Profile mechanics — POC, VAH, VAL, HVN, LVN, value area calculations, and migration patterns — see the dedicated companion doc.

## How `/scan` uses VWAP

VWAP enters the scan as a per-horizon overlay, scaled to the timeframe each horizon trades against:

- **Day-trade horizon** — reads **session VWAP + 1σ/2σ bands** on the intraday chart. Side-of-VWAP filters trade direction; σ-band tags drive mean-reversion vs. trend-ride decisions; reclaim/lose of session VWAP is a change-of-character flag.
- **Swing horizon** — reads **weekly VWAP and monthly VWAP** on the daily chart. Side-of-weekly-VWAP sets the swing bias; weekly VWAP slope reinforces or contradicts the EMA-cluster trend read; monthly VWAP serves as the "is this still in trend?" reference.
- **Positional horizon** — reads **quarterly VWAP, YTD VWAP, and key AVWAPs** (last earnings, prior swing high, prior swing low, IPO if recent). The AVWAP-from-last-earnings is the institutional cost basis for the post-print cohort; loss of YTD VWAP is the headline "year is broken" signal.

The scan's numeric data layer (`scripts/fetch_ohlc.py`) computes the full VWAP family (session / weekly / monthly / quarterly / anchored, with ±1σ / ±2σ bands) on every scan. Per-horizon usage is wired in [`.claude/commands/scan.md`](../.claude/commands/scan.md) § Step 6 and [`guide/scan/structure.md`](../guide/scan/structure.md). This doc is the **authoritative reference** for how VWAP itself behaves; the scan-side wiring is the consumer.

> **Note on images.** Reference chart screenshots (session-VWAP labeled, ±2σ bands, AVWAP from a swing high, multi-AVWAP stack, VWAP reclaim, VWAP × Volume Profile confluence) live in `docs/assets/vwap/` once added. Direct image fetch was unavailable in the research session that produced this doc; the conceptual descriptions above are the source of truth and any later-added screenshots should illustrate the patterns named in [Trading applications](#trading-applications) and [Confluence techniques](#confluence-techniques).

## References

1. **Brian Shannon, CMT — *Maximum Trading Gains With Anchored VWAP*** (CMT Association, 2022). The definitive modern reference on AVWAP. Anchor-selection criteria, multi-anchor confluence, and the reclaim/lose framework all originate here. [AlphaTrends — book page](https://alphatrends.net/anchored-vwap-book/) · [CMT Association PDF excerpt](https://cmtassociation.org/wp-content/uploads/2024/01/Shannon-Specific-Anchored-VWAP-Strategies-1.pdf).
2. **StockCharts ChartSchool — Volume-Weighted Average Price (VWAP)**. Canonical retail-education reference for the calculation, intraday behavior, and S/R reads. [chartschool.stockcharts.com — VWAP](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/volume-weighted-average-price-vwap) · [chartschool.stockcharts.com — Anchored VWAP](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/anchored-vwap).
3. **Wikipedia — Volume-Weighted Average Price**. Formal definition, mathematical formula, institutional execution-benchmark history, and TWAP comparison. [en.wikipedia.org/wiki/Volume-weighted_average_price](https://en.wikipedia.org/wiki/Volume-weighted_average_price).
4. **Charles Schwab — How to Use Volume-Weighted Indicators in Trading**. Broker-grade education on VWAP setup in thinkorswim, ±σ band display, and intraday S/R reads. [schwab.com/learn/story/how-to-use-volume-weighted-indicators-trading](https://www.schwab.com/learn/story/how-to-use-volume-weighted-indicators-trading).
5. **TrendSpider — VWAP with St.Dev Bands & Anchored VWAP guides**. Practical band-trading rules (1σ/2σ thresholds, mean-reversion vs. trend-ride decision tree) and AVWAP anchor-selection patterns. [help.trendspider.com — VWAP with St.Dev Bands](https://help.trendspider.com/kb/indicators/vwap-with-st-dot-dev-bands) · [trendspider.com — Anchored VWAP guide](https://trendspider.com/learning-center/anchored-vwap-trading-strategies/).
6. **TradingView — Volume Weighted Average Price documentation**. Calendar-anchored variants (weekly/monthly/quarterly/yearly), pre-market inclusion settings, and σ-band multiplier conventions. [tradingview.com — VWAP solution](https://www.tradingview.com/support/solutions/43000502018-volume-weighted-average-price-vwap/).
7. **Britannica Money — Volume-Weighted Average Price**. Concise institutional-benchmark definition and the pension-fund passive-execution use case. [britannica.com/money/volume-weighted-average-price](https://www.britannica.com/money/volume-weighted-average-price).
8. **Warrior Trading — VWAP Indicator Trading Strategies** & **Bulls on Wall Street — VWAP for Day Trading**. Practical day-trade applications: trend-day pullback entries, range-day fades, reclaim patterns, and the most common rookie pitfalls. [warriortrading.com/vwap](https://www.warriortrading.com/vwap/) · [bullsonwallstreet.com — VWAP day trading](https://www.bullsonwallstreet.com/post/what-is-the-vwap-trading-indicator-and-how-to-use-it-as-a-day-trader).
