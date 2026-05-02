# Volume Profile — distribution-based price levels

Volume Profile is a horizontal histogram that maps total volume traded at every price level over a defined window — flipping the view from the candle-volume bar (volume per unit of *time*) to volume per unit of *price*. The output is a side-of-chart distribution that exposes where business actually got done versus where price merely passed through. Two days with identical OHLC ranges can have completely different profiles; the profile is what reveals which prices the market accepted as fair and which prices it rejected. This doc is the authoritative reference for how `/scan` reads volume distribution. Companion doc: [`vwap.md`](vwap.md) for the volume-weighted average-price layer.

## Contents

1. [Core concept](#core-concept)
2. [Key terminology](#key-terminology)
3. [Profile shapes — read these](#profile-shapes--read-these)
4. [Profile types](#profile-types)
5. [How to read it on a chart — the practitioner's checklist](#how-to-read-it-on-a-chart--the-practitioners-checklist)
6. [Trading applications](#trading-applications)
7. [Common pitfalls](#common-pitfalls)
8. [When VP is most reliable](#when-vp-is-most-reliable)
9. [When VP is less reliable](#when-vp-is-less-reliable)
10. [Combining with VWAP](#combining-with-vwap)
11. [How `/scan` uses Volume Profile](#how-scan-uses-volume-profile)
12. [References](#references)

---

## Core concept

Volume Profile rotates the volume axis 90 degrees. A standard volume bar shows total contracts/shares traded *during a candle*; a Volume Profile shows total contracts/shares traded *at a price* across the window. The chart now answers a different question: **at what price did size actually transact?**

This matters because price discovery in any liquid auction is a search for fair value. The market spends time and volume where buyers and sellers agree (acceptance); it spends almost nothing where they don't (rejection). Candles give you the path price walked. The profile gives you where it stopped to do business. The gap between those two reads is where most amateur S/R levels fail and where institutional levels — the prices large books had to clear inventory at — show up.

The framework derives from Auction Market Theory (Steidlmayer, CBOT, late-1980s): price moves vertically through time, but value forms horizontally as volume stacks at acceptance levels. The wider parts of the histogram are zones of agreement; the narrow parts are zones of disagreement. A trader using profile is asking *where did the auction find efficiency, and where is the next inefficiency I can lean on?*

Volume Profile is distinct from Market Profile (TPO). Market Profile counts **time** at each price (30-min letter bars); Volume Profile counts **executed contracts** at each price. TPO answers "how long did price stay here?"; VP answers "how much size cleared here?" — same auction-theory backbone, different counter. Volume is the cleaner read on liquid futures, indices, large-cap equities, and BTC perps; TPO can outperform on instruments where exchange-reported volume is unreliable or fragmented.

---

## Key terminology

**POC (Point of Control)** — the single price level with the highest traded volume in the window. The fattest bar in the histogram. POC = market consensus on fair value during that period. Acts as a magnet on intraday revisits and a pivot on first test from new range. POC is a level, not a zone.

**Value Area (VA)** — the price range that contains a target percentage (default **70%**, ≈ 1 standard deviation) of total volume, centered on the POC. VA is the "fair-value envelope" for the period. Trading inside VA = acceptance; trading outside VA = potential excess or breakout.

**VAH (Value Area High)** — the upper bound of VA. Acts as resistance from inside, support from outside on retest.

**VAL (Value Area Low)** — the lower bound of VA. Mirror role: support from inside, resistance from outside on retest.

**HVN (High Volume Node)** — a price (or thin band) with a local volume bulge — a "shelf" sticking out of the profile. HVNs are zones where the market repeatedly transacted; they behave as magnets on approach and sticky support/resistance on test. Multiple HVNs on the same chart create a ladder of expected reaction levels. Treat HVNs as pools of liquidity, not walls — a pool gets consumed on second/third test.

**LVN (Low Volume Node)** — a price with very thin volume — a valley between two HVNs. LVNs are rejection zones: the market moved through them quickly, found no acceptance, and left them as gaps in the auction. Price tends to slice back through LVNs in the same fast manner — they are trade-through zones, not stopping zones. A clean LVN on the path of least resistance is a higher-probability target than a measured-move projection.

**Naked POC / Virgin POC (NPOC / VPOC)** — a prior-period POC that price has not retraced to since it formed. Empirically, ~80% of NPOCs get revisited within ~10 trading sessions. Treats NPOCs as forward-leaning targets — the market "owes" liquidity at that level. Daily, weekly, and monthly NPOCs all qualify; the higher the timeframe, the bigger the magnet but the longer the time-to-fill.

**Composite Profile** — a single profile aggregated across many sessions (week, month, quarter, full uptrend leg). Smooths session noise and exposes the dominant HVN/LVN structure that single-session profiles miss. Used for swing and positional context.

**Developing POC / VPOC drift** — the POC of the *current, in-progress* session, recalculated bar by bar as new volume arrives. Watching where the developing POC moves through the day exposes intraday acceptance: an **upward-drifting** POC = buyers are accepting higher prices (bullish migration); a **downward-drifting** POC = sellers are forcing acceptance lower (bearish migration); a **stable** POC = balance.

**Value Area Migration** — the day-over-day shift of the value area. Today's VA higher than yesterday's = acceptance trending up (one of the more reliable trend reads). Today's VA lower = trending down. Today's VA inside yesterday's = consolidation; today's VA fully outside = breakout from balance.

**Excess** — single-print rejection at a profile extreme; tails on the profile. Excess = the auction tried to discover at that price and was rejected immediately. Excess highs/lows are higher-conviction reversal levels than rotational highs/lows.

**Single Print** — a price level visited by only one TPO/very thin volume slice; effectively an LVN inside a session. Single-print zones are the "fair-value gap" of profile work.

---

## Profile shapes — read these

The shape of yesterday's profile is the strongest single read on what to expect today. Four base patterns cover ~90% of sessions.

### Normal / Balanced (D-shape)

A symmetric bell: thick belly in the middle (POC roughly centered), tapering tails top and bottom. Volume distributed evenly around fair value. Indicates **balance** — neither side dominated; the auction rotated.

- **What it implies for next session:** range-bound expectation. Yesterday's VAH/VAL act as the working range; high-probability fade setups at the extremes until the range breaks.
- **Default trade structure:** sell VAH, buy VAL, target POC. Stop on acceptance (multiple closes) outside the value area.
- **Failure mode:** clean break of VAH or VAL with acceptance outside → range has expired; switch to trend-day playbook.

### Trend day (P-shape, b-shape)

Asymmetric profile with a single fat distribution at one end and a long thin tail to the other. Indicates **directional conviction** — one side controlled the auction.

- **P-shape** — fat top, thin bottom tail. Forms after a sharp rise into consolidation; the bulk of volume traded high in the range. Most common at the **end of a downtrend** (short-cover rally) or as **continuation in an uptrend**. Bias: bullish until the bulb fails.
- **b-shape** — fat bottom, thin top tail. The mirror — sharp decline into consolidation, bulk of volume traded low. Most common at the **end of an uptrend** (long liquidation) or as **continuation in a downtrend**. Bias: bearish until the bulb fails.
- **What it implies for next session:** trend-continuation tilt. The thin tail is a rejection zone; price rarely settles back into it without a regime change.
- **Failure mode:** acceptance back into the tail = the trend conviction was wrong; expect mean-reversion toward the opposite extreme of the prior range.

### Double distribution (B-shape)

Two distinct bulges separated by an LVN gap. The session traded two ranges, transitioned via a fast move, and built fresh value at the new level.

- **What it implies for next session:** the LVN gap between the two bulges is a key pivot — price either fills it (collapse back to single distribution = D-shape) or holds the new range. Both bulges become S/R; the one price is currently leaning on takes priority.
- **Default trade structure:** fade the active bulge's extreme back toward the LVN; if the LVN fills, target the opposite bulge.
- **Statistical tendency:** double distributions often resolve into a D-shape over the following 1–3 sessions as the LVN gap fills and value compresses.

### Neutral / Non-trend (multi-modal)

Choppy profile with multiple small bulges, no dominant POC, broad VA. Indicates **indecision** — no consensus on fair value, multiple competing micro-distributions.

- **What it implies for next session:** lower conviction, wider noise envelope. Skip mean-reversion at the VAs (they're not real edges) and wait for the next clean shape to form.
- **Trade rule:** size down or stand aside until a single dominant distribution emerges. Neutral profiles are the cleanest "do less" signal in the framework.

### Quick-reference table

| Shape | POC location | Bias | Default play |
| --- | --- | --- | --- |
| **D / Balanced** | Centered | Range | Fade VAH/VAL, target POC |
| **P** | High in range | Bullish | Buy retest of upper bulge / VAL holds |
| **b** | Low in range | Bearish | Sell retest of lower bulge / VAH rejects |
| **B / Double dist.** | Two POCs | Pivot on LVN | Fade active bulge, target LVN, then opposite bulge |
| **Neutral / multi-modal** | Diffuse | No conviction | Skip / wait |

---

## Profile types

Different windowing methods serve different horizons. Pick the one that matches the question.

**Session / TPO Volume Profile (SVP)** — one profile per trading session (default RTH or 24h). Tactical; resets daily. Used for day-trade and short-swing setups. Yesterday's SVP gives today's reference levels (yPOC, yVAH, yVAL).

**Daily / Weekly / Monthly Profile** — single-period profile aggregated at higher timeframe. Weekly profile is the workhorse for swing-trade context; monthly profile for positional context. Holds NPOC reference for forward targets.

**Visible Range Volume Profile (VRVP / VPVR)** — TradingView's default. Computes the profile across whatever window is currently visible on screen. Re-computes on every zoom/scroll. Use for big-picture S/R when you don't want to commit to a fixed anchor; downside is the read changes with the viewport.

**Fixed Range Volume Profile (FRVP)** — manually selected start and end bar. Locks the profile to a specific structure: one trend leg, one consolidation, one earnings reaction, one campaign accumulation zone. Best tool for studying a discrete event in isolation.

**Composite (multi-session)** — many sessions stacked into one histogram. Smooths daily noise; the dominant HVN/LVN ladder that emerges is the structural map for swing levels. Use when single-session profiles are giving conflicting reads.

**Anchored Volume Profile (AVP)** — fixed start bar, but extends continuously to the current bar. Anchored from a specific event (earnings print, FOMC, all-time high, breakout pivot, regime shift). The AVP from a high-conviction event is often the cleanest forward S/R map for the move that follows.

**Selection rule of thumb:**
- Day trade: SVP (today + previous 1–3 days).
- Swing: weekly + composite of last 4–8 weeks.
- Position: monthly + AVP from the originating catalyst.

### Session boundaries — what counts as "the session"

The profile period is only as good as the session boundary you draw. Defaults that work:

- **US equities / ETFs:** RTH only (09:30–16:00 ET) for SVP. Pre-market and post-market volume distort the histogram with thin-print levels that don't reflect institutional acceptance.
- **US index futures (ES, NQ, YM, RTY):** RTH (09:30–16:15 ET) for the cleanest read; ETH (full 23-hour session) only when needed for overnight context.
- **Crude / metals futures (CL, GC, SI):** primary trading hours of the contract; otherwise the Asia session noise dominates.
- **Crypto (BTC, ETH, perps):** 24h sessions with day boundaries at 00:00 UTC. Crypto has no organic close, so the boundary is a convention — keep it consistent across all profiles or weekly comparisons fall apart.
- **FX:** London open to NY close window for the day-trade SVP; full 24h for swing composite. The Asia-only session is structurally low-volume and should rarely be used standalone.

Mismatched boundaries are the #1 source of profile read errors — yesterday's "POC" calculated on a 24h window vs an RTH window can sit 50+ basis points apart on the same chart.

---

## How to read it on a chart — the practitioner's checklist

Run this in order. Skipping steps produces hindsight noise.

1. **Identify POC, VAH, VAL on the current period** — mark them. Note where price sits relative to the value area: inside (rotational), at the edge (decision point), or outside (out-of-balance / breakout candidate).
2. **Note prior-period naked POCs** — daily NPOCs from the last 5–10 sessions, weekly NPOCs from the last 4–8 weeks, monthly NPOC from the prior month if not yet revisited. These are forward magnets and de-facto targets.
3. **Identify HVN clusters and LVN gaps** — mark them on the chart. HVNs above price = resistance ladder; HVNs below = support ladder. LVNs in the path of least resistance are pass-through zones — price tends to traverse them quickly.
4. **Read the profile shape vs the prior session's shape** — a P-shape after a D-shape signals trend kicking off; a D-shape after a P-shape signals trend exhaustion / new balance. The transition is where the actionable read lives.
5. **Watch for value-area migration** — overlay yesterday's VA on today's developing VA. Up-migration (today's VAL > yesterday's VAH) = bullish acceptance, breakout. Overlap = consolidation. Down-migration = bearish acceptance.
6. **Track the developing POC during the session** — drifting up = buyers paying up; drifting down = sellers hitting bids; stable = balance. POC migration in the *opposite* direction of the price move is a divergence — usually a warning that the move lacks volume conviction.
7. **Confluence with trend / S&R from price action** — a VP level (NPOC, HVN, VAH/VAL) that lines up with a horizontal S/R, a moving average, or a Fibonacci level is the high-probability node. Levels with no confluence get smaller size.

### A worked example — reading a balanced day after a trend day

Hypothetical sequence: yesterday closed as a clean **P-shape** (ES futures rallied hard from 4500 to 4540 in the morning, then chopped between 4530–4540 the rest of the day). Yesterday's POC = 4536, VAH = 4540, VAL = 4530, lower tail = 4500–4530 (the thin path the rally walked).

Today opens at 4538, inside yesterday's value area. The chart-reading sequence:

1. POC/VAH/VAL marked: 4536 / 4540 / 4530.
2. NPOCs above price: none from last 5 sessions. NPOCs below: 4485 (4 sessions ago, daily), 4420 (weekly NPOC from 3 weeks ago).
3. HVNs: 4536 (yesterday's POC), 4505 (HVN from a 5-session composite), 4470 (deeper HVN). LVN gap: 4505–4530 (the thin region of yesterday's tail).
4. Shape transition: yesterday P-shape, today opening inside its VA = potential transition to D-shape balance day. Bias: range expectation between 4530 and 4540 unless something forces a break.
5. Migration: today's developing VAL at 4533 vs yesterday's VAL 4530 → mild up-migration, modest bullish tilt.
6. Developing POC: drifting between 4536 and 4538 through the morning — stable, consistent with balance.
7. Trade plan: fade 4540 (yVAH + today's developing VAH) with stop above 4543, target 4536 (yPOC). If 4540 accepts above (multiple closes, fresh volume bulge, developing POC drifts up), thesis is wrong — flip to long with target = next NPOC up (none in 5 sessions, so the next round-number magnet). If 4530 breaks down with acceptance, target = the LVN traverse to 4505 HVN.

This is the standard read shape. Every variable in the trade plan above is either a profile feature or a confluence with one — that's the point.

---

## Trading applications

**VAH / VAL as targets and reversal zones** — the cleanest mean-reversion play in profile work. Inside a balanced (D-shape) range, sell VAH / buy VAL with stops on acceptance outside, target POC. Win rate is range-dependent; the edge dies the moment the range breaks. Use developing-VA migration as the kill signal.

**POC as magnet** — when price is far from POC, especially on lower timeframes, POC is a mean-reversion target. Strongest when the move toward POC has volume confirmation. Weakest when the move is a parabolic blow-off — POC is still the eventual target but timing is treacherous.

**LVN as trade-through** — when price enters an LVN with momentum, expect a fast traverse. Trade structure: enter on the breach, target the next HVN above (long) or below (short). Stop just inside the LVN — if price stalls there, the trade is wrong and the LVN is becoming an HVN.

**HVN as support/resistance** — first test of an HVN from outside the value area is a higher-probability reaction than a generic horizontal level (institutional inventory sits there). Second test is materially weaker (liquidity gets consumed). Third test is roughly a coin flip — by then the level is "weak" and price is more likely to break through than bounce.

**Naked POC as forward-leaning target** — ~80% of NPOCs fill within ~10 sessions. Use as profit targets for swing positions; use as catalyst zones — when price approaches a high-timeframe NPOC, expect reaction (either bounce or violent absorption into next range).

**Acceptance / rejection trades** — a clean breakout from balance into a prior LVN, followed by acceptance (multiple closes, fresh volume bulge, developing POC drifting in the direction of the break) = trend-continuation entry. A breakout that fails to build acceptance and rotates back into VA = failed-breakout fade.

**Stop placement** — beyond the next HVN, not at a clean number. HVNs are where the level genuinely fails; round numbers are where retail stops cluster and get harvested. LVNs are valid stop *zones* (price moves through fast) but not stop *levels* (no liquidity to fill on adverse moves).

---

## Common pitfalls

**Treating POC as a permanent wall.** POC is a pool of liquidity, not a brick wall. First test = high-probability reaction. By the second or third test, large books have already executed; the level becomes weak and breaks more often than it holds. Trade fresh levels first, faded ones with smaller size.

**Confusing volume with liquidity.** A high-volume bar doesn't guarantee depth at every price within it — a single absorption print can fatten a candle's volume reading without creating real two-sided liquidity. When in doubt, cross-check the profile against order-book depth or session highs/lows where slippage actually got tested.

**Ignoring profile shape.** Reading POC and VAH/VAL without reading the *shape* misses the most informative signal. A P-shape and a D-shape can have identical POC/VAH/VAL coordinates and require completely opposite trade structures.

**Time-frame mismatch.** Using a daily-profile signal to manage a 5-minute trade is a coordination problem — the daily signal moves slower than the trade. Match the profile period to the trade horizon: SVP for day trades, weekly composite for swings.

**Over-fitting LVNs as supports.** LVNs are rejection zones, not support. Buying an LVN because "price has to stop somewhere" is a category error — the *defining feature* of an LVN is that price doesn't stop there. LVNs are stop-loss territory, not entry territory.

**Reading profile in news-distorted sessions.** A session whose volume is dominated by a single news-driven minute (FOMC, NFP, earnings) produces a distorted profile. The POC may sit at the news-impact bar rather than at any organic acceptance level. Treat news-day profiles as suspect; weight the prior session's profile more heavily for next-day reference.

**Mistaking VRVP shifts for real-level shifts.** The VRVP recalculates every time you scroll or zoom. The "POC" you see can change just because you panned the chart. For stable references, pin a Fixed Range or Anchored profile rather than relying on the visible-range default.

**Trading every NPOC.** Not all NPOCs are equal. A daily NPOC from a low-volume holiday session has weaker pulling power than a daily NPOC from a high-volume FOMC reaction. Weight by the session volume that produced it.

**Static-zoom trap on VRVP.** A trader who keeps a default VRVP on the chart and never re-zooms ends up reading a stale profile that was relevant a month ago, not today. Either re-zoom intentionally (every session, every swing) or replace VRVP with a Fixed Range / Anchored profile that won't drift on you.

**Reading shape without reading volume.** Two profiles with identical D-shapes can have very different total volume. A high-volume D-shape is a strong consensus (the levels mean something); a low-volume D-shape is a coincidence (the levels are noise). Always glance at total session volume before sizing a profile-based trade.

**Forgetting that "balance" can be a continuation pattern.** A D-shape *inside* a clear uptrend is not a reversal signal — it's a digestion phase before the next leg. Profile shape gives you the *intra-period* read; the *inter-period* trend context still matters.

---

## When VP is most reliable

- **High-liquidity instruments** — ES, NQ, CL futures; SPY/QQQ; top-50 large-cap US equities; BTC/ETH on top-3 exchanges. Volume read is genuine.
- **Sessions with clear open/close** — futures RTH sessions, forex London/NY overlap windows. Defined session boundaries make the profile period unambiguous.
- **Multi-day aggregation** — a composite of 5–10 sessions reveals structural HVN/LVN clusters that any single session misses. Most actionable for swing horizons.
- **Range-bound regimes** — D-shape profiles repeat; VAH/VAL fades work with high frequency until the range breaks. Profile work shines in chop.
- **Post-news session settling** — once the news-impact spike is behind, the profile that builds during the rest of the session is high-quality acceptance data.

## When VP is less reliable

- **Thin / illiquid markets** — small-cap stocks, low-volume crypto alts, off-hours forex. Single large prints distort the histogram; HVNs are statistical noise rather than institutional inventory.
- **News-driven gap days** — gap-and-go opens skip the auction in the gap zone. The profile shows zero volume across a wide price band, creating an artificial LVN that has no auction-theory meaning. Treat the gap as an exogenous event, not a profile feature.
- **Low-volume holidays / overnight thin sessions** — Christmas week, Friday afternoons in summer, Asian-only crypto sessions. The POC of a low-volume session is often a coincidence rather than a real consensus level.
- **First few hours after listing / structural change** — an instrument with a new ticker, a post-split chart, or a freshly-anchored profile (post-earnings AVP started < 1 day ago) hasn't had time to build statistically meaningful nodes.
- **Composite-period whipsaw** — composites that span a regime change (e.g., spanning across an FOMC pivot or a war catalyst) blend two different auctions and produce a misleading "fair value." Re-anchor the composite at the regime-change bar.

---

## Cross-asset application notes

The framework is universal but liquidity structure differs by asset class. Adjustments worth making per class:

- **Large-cap US equities** — RTH-only SVP. Earnings reactions distort the next session's profile severely; weight the post-earnings AVP for at least 3–5 sessions before treating the new range as accepted. Insider-driven gap days produce LVN cliffs that get filled later — hold those NPOCs as forward targets.
- **Small/mid-cap equities** — VP becomes noisy below ~$20M average daily dollar volume. Switch to higher-timeframe composites (weekly/monthly) and de-emphasize SVP entirely; the daily auction is too thin to produce meaningful fair-value reads.
- **Index futures (ES/NQ/YM)** — gold-standard VP instrument. Deep liquidity, 24h trade with a clean RTH window, institutional benchmarking against POC and VWAP. Every level matters; size up the confluence trades.
- **Crypto majors (BTC, ETH)** — 24h sessions; weekly anchors at Sunday/Monday UTC week-roll work. Beware spot-vs-perps profile divergence — perps profile dominates short-term flow but spot profile shows where real custody-level positioning sits. Both matter.
- **Crypto alts** — VP gets unreliable fast outside the top 20–30 by liquidity. Aggregate across exchanges if the platform supports it; single-exchange profiles can be wash-trade contaminated.
- **FX majors** — London/NY overlap is the cleanest window. Asia-only sessions produce structurally different (thinner, more rotational) profiles — don't mix the two without explicit context flagging.
- **Commodities (CL, GC)** — RTH-equivalent windows produce the cleanest reads. Inventory-report days (EIA Wednesday for crude, COT release Friday) distort the profile via news-impact volume; treat those sessions like equities earnings-reaction days.

The terminology, shapes, and reading checklist above hold across all of these — only the session boundary, liquidity threshold, and event-distortion overlay change.

---

## Combining with VWAP

VWAP is covered in the companion doc [`vwap.md`](vwap.md). The short version of the interaction:

- **POC near VWAP = high conviction.** Two independent measures of fair value agreeing. Levels where POC and VWAP converge are higher-probability reaction zones than either alone. Combo: trade-direction signal from VWAP, S/R level from POC.
- **POC far from VWAP = unbalanced flow.** Tells you the volume distribution is heavy on one side of the average — either accumulation (POC below VWAP, price still elevated) or distribution (POC above VWAP, price holding up). Indicates an unresolved auction; expect resolution through one of them moving toward the other.
- **VAH/VAL + anchored VWAP confluence.** When yesterday's VAH/VAL aligns with today's anchored VWAP from a key event, that price is doing structural and benchmark work simultaneously — a top-tier confluence node.
- **Direction from VWAP slope, levels from VP.** The cleanest combo: VWAP gives you trend bias (price above rising VWAP = bullish regime); profile gives you the discrete S/R prices to enter and target on.

---

## How `/scan` uses Volume Profile

`/scan` integrates Volume Profile across all three coverage tiers:

- **Universal application** — VP is read on every asset class (stocks, crypto, indices, FX, commodities). Liquidity and session structure modify the *type* of profile used; the framework stays the same.
- **Default profile per horizon:**
  - Day-trade: today's developing SVP + previous 1–2 days' SVP for reference levels (yPOC, yVAH, yVAL, NPOCs from last 5 sessions).
  - Swing: weekly composite (last 4–8 weeks) + AVP from the originating swing catalyst (earnings, breakout, regime shift).
  - Position: monthly composite + AVP from the dominant macro catalyst (FOMC pivot, war catalyst, sector rotation pivot).
- **Fields that go into the technical-read section:**
  - Current-period POC, VAH, VAL.
  - Nearest unfilled NPOC above and below (with date of formation).
  - Nearest HVN above and below acting as S/R.
  - Nearest LVN in the path of least resistance (forward target).
  - Profile shape of last completed session (D / P / b / B / neutral) + comment on next-session bias.
  - Value-area migration read (up / down / overlap / outside).
- **What the scan does with the read:**
  - Identifies high-confidence S/R levels (HVN clusters, NPOCs, VAH/VAL retests with confluence).
  - Gauges acceptance / rejection of new ranges (developing-VA position relative to prior-period VA).
  - Locates naked POCs as forward-leaning targets and risk-reward references.
  - Calls out shape transitions (P → D, D → B) as regime-of-day signals.
  - Skips profile-based setups when the asset is in the "less reliable" buckets above (thin liquidity, gap-distorted, post-news instability) and notes the skip reason.

The scan integration is being wired separately; this doc is the authoritative source for the *vocabulary* and *reads* the integration consumes. Any change to terminology, default thresholds (Value Area = 70%, NPOC fill window ≈ 10 sessions), or shape definitions belongs in this doc first.

---

## References

- [TradingView — Volume Profile indicators: basic concepts](https://www.tradingview.com/support/solutions/43000502040-volume-profile-indicators-basic-concepts/) — canonical definitions for POC, VAH, VAL, value-area calculation defaults.
- [TradingView — Visible Range Volume Profile](https://www.tradingview.com/support/solutions/43000703076-visible-range-volume-profile/) — VRVP/VPVR documentation, viewport behavior.
- [TradingView — Anchored Volume Profile drawing tool](https://www.tradingview.com/support/solutions/43000707989-anchored-volume-profile/) — AVP construction from event anchor.
- [TradingView — Time Price Opportunity (TPO) indicator](https://www.tradingview.com/support/solutions/43000713306-time-price-opportunity-tpo-indicator/) — TPO vs Volume Profile distinction.
- [NinjaTrader — Understanding the 4 Common Volume Profile Shapes in Futures Trading](https://ninjatrader.com/futures/blogs/trade-futures-understanding-the-4-common-volume-profile-shapes/) — D / P / b / B shape definitions and futures-session context.
- [Overcharts — Volume Profile distribution types](https://www.overcharts.com/en/helpcenter/docs/volume-profile-distribution-types/) — cross-reference on shape taxonomy.
- [Overcharts — Volume Profile Value Area](https://www.overcharts.com/en/helpcenter/docs/volume-profile-value-area/) — value-area calculation, 70% default.
- [mypivots — Naked Point of Control (NPOC)](https://www.mypivots.com/dictionary/definition/442/naked-point-of-control-npoc) and [Virgin Point of Control (VPOC)](https://www.mypivots.com/dictionary/definition/158/virgin-point-of-control-vpoc) — naked-POC definitions, ~80% fill stat.
- [Optimus Futures — Spotting Market Trends with Volume Profile Trading](https://optimusfutures.com/blog/volume-profile-trading/) — practitioner-side applications across futures.
- [Charles Schwab — Volume Profile Indicator: How Does It Work?](https://www.schwab.com/learn/story/using-volume-profile-indicator) — equities-side overview from a major retail broker.
- [Bookmap — Value Migration Explained](https://bookmap.com/blog/value-migration-explained-how-markets-shift-from-one-area-of-acceptance-to-another) — value-area migration, acceptance vs rejection mechanics.
- [International Trading Institute — Reading the Volume Profile from Acceptance to Rejection](https://internationaltradinginstitute.com/blog/reading-the-volume-profile-from-acceptance-to-rejection/) — auction-theory framing.
- [Wikipedia — Market profile](https://en.wikipedia.org/wiki/Market_profile) — Steidlmayer / CBOT historical reference.
- [Trader Dale — 3 Common Volume Profile Mistakes](https://www.trader-dale.com/volume-profile-mistakes/) — pitfalls / liquidity-pool framing.
- [Trader Dale — VWAP + Volume Profile: The Cleanest Support/Resistance Combo](https://www.trader-dale.com/vwap-volume-profile-the-cleanest-support-resistance-combo-27th-jan-26/) — confluence with VWAP.
