# Long-term investing — fundamental research, business quality, capital allocation

A consolidated reference for the long-term / fundamental side of the framework: research workflow, business-quality reads, valuation discipline, capital-allocation evaluation, portfolio architecture, and the macro-vs-business-focus tension. The 6-pillar scorecard used by `/scan` (defined in [`guide/scan/scorecard.md`](../guide/scan/scorecard.md)) draws its definitions directly from this material.

## Contents

- [Research process](#research-process)
  - [Three stages of stock research](#three-stages-of-stock-research)
  - [The research funnel](#the-research-funnel)
  - [Long-term research workflow (13 steps)](#long-term-research-workflow-13-steps)
  - [How to read a 10-K efficiently](#how-to-read-a-10-k-efficiently)
  - [How to read financial statements](#how-to-read-financial-statements)
  - [Every income statement tells a story](#every-income-statement-tells-a-story)
- [Business quality](#business-quality)
  - [Economic moat and profit margins](#economic-moat-and-profit-margins)
  - [High-margin vs low-margin businesses](#high-margin-vs-low-margin-businesses)
  - [Why margins matter more than revenue](#why-margins-matter-more-than-revenue)
- [Valuation](#valuation)
  - [Reasonable P/E ratio based on growth](#reasonable-pe-ratio-based-on-growth)
- [Capital allocation](#capital-allocation)
  - [How great management compounds wealth](#how-great-management-compounds-wealth)
  - [How great management creates long-term returns](#how-great-management-creates-long-term-returns)
- [Portfolio strategy](#portfolio-strategy)
  - [Portfolio management — diversification, sizing, risk](#portfolio-management--diversification-sizing-risk)
  - [Consistent investing vs high-conviction bets](#consistent-investing-vs-high-conviction-bets)
  - [Should you sell after a stock doubles?](#should-you-sell-after-a-stock-doubles)
  - [What is a good annual return?](#what-is-a-good-annual-return)
  - [Wealth roadmap](#wealth-roadmap)
  - [Knowledge must grow with your portfolio](#knowledge-must-grow-with-your-portfolio)
- [Macro and market timing](#macro-and-market-timing)
  - [Ignore macro forecasting, focus on businesses](#ignore-macro-forecasting-focus-on-businesses)
  - [The IPO cycle](#the-ipo-cycle)

---

## Research process

### Three stages of stock research

Most investors research in the wrong order — checking valuation before understanding the business. The correct order is **qualitatives first, quantitatives second, projections last**. Each stage gates the next; if the qualitatives fail, you don't waste time on a DCF model.

- Understand the business model, moat, and management *before* opening the financials
- Qualitatives drive everything else — that's where major analytical edges live
- Financial metrics need business context — low multiples can be opportunities or warnings
- Projections are valuable only after the business and financials check out
- Catching a red flag early saves the entire research budget — move on, don't model the failure
- Repeatable process beats raw analytical horsepower

| Stage | Coverage | Gate to advance |
|---|---|---|
| **1. Qualitatives** | Business model · product · customers · industry dynamics · management · long-term viability | Business must make logical sense; no major red flags in quality or leadership |
| **2. Quantitatives** | Balance sheet · income statement · cash flow · margins · debt · ROIC · valuation multiples | Financials must support the qualitative thesis — no declining margins, weak FCF, or excessive debt |
| **3. Projections** | Bull/base/bear scenarios for revenue · margins · earnings · valuation | Proceed only after stages 1–2 confirm investment merit |

**Maps onto the 6-pillar scan flow:**
- **Stage 1** ≈ Pillars 1, 5, 6 (Quality, Capital Allocation, Smart Money)
- **Stage 2** ≈ Pillars 2, 3, 4 (Growth, Valuation, Balance Sheet)
- **Stage 3** ≈ The trade-plan section of `/scan` — entries, stops, targets

The auto-reject discipline is Stage 1 gating: if Pillar 1 fails (negative ROIC, negative gross margin), mark **Pos S** and don't bother modeling.

### The research funnel

Successful investors don't deep-dive every company — they build a funnel that applies progressively more rigor at each stage. The output is a manageable set of high-conviction ideas; the discipline is in the rejection rate at the early stages.

- Use fast judgment to reject most of the market before any deep work
- Reserve intensive research for names that pass the cheap filters
- "Good company" ≠ "good fit" — strategy alignment matters
- Position size should drive research depth (bigger size → deeper work)
- Develop the muscle to say "yes," "not yet," or "no" decisively

| Stage | Purpose | Criteria |
|---|---|---|
| **Initial screen** | Quick rejection | Highly speculative · unprofitable with no path · outside strategy |
| **Watchlist** | Surface monitoring | Understand model, notice changes, build optionality |
| **Potential investments** | Surface research | Revenue direction, margins, profitability, balance sheet, valuation range, portfolio fit |
| **Deep analysis** | Serious consideration | 10-Ks, projections, bull/base/bear cases, segment analysis, management commentary, valuation models |

**Maps onto the `/discover` → `/scan` workflow:**
- **Initial screen** = `/discover` (Finviz screener with Q1–Q4 presets)
- **Watchlist** = Coverage tier **B** (bench)
- **Potential investments** = Coverage tier **W** (watchlist with live trigger)
- **Deep analysis** = `/scan` full 6-pillar + technical + flow report

### Long-term research workflow (13 steps)

Long-term investing requires deep fundamental research before purchase — not tips, social media, or chart-reading. The framing: "long-term investing works best when you know exactly what you own and why you own it." Conviction built from research is what gets you through the volatility that tests every thesis.

- Start with the business model — if you can't explain it simply, don't invest yet
- Prioritize primary sources (filings, earnings calls) over secondary commentary
- Focus on durable signals: revenue consistency · margins · FCF · balance-sheet strength
- Identify competitive advantages: brand · switching costs · network effects · recurring revenue
- Evaluate management's capital-allocation track record
- Only assess valuation *after* business fundamentals check out
- Build conviction before the volatility tests it — not during

The full ordered checklist:

1. Define what the company actually does and how it makes money
2. Read the most recent 10-K
3. Review recent 10-Qs
4. Listen to earnings calls + management commentary
5. Study investor presentations for strategic context
6. Analyze revenue growth trends for consistency
7. Examine profit margins and their sustainability
8. Assess balance sheet health (cash, debt, liquidity)
9. Calculate free cash flow generation
10. Track share-count trend (dilution check)
11. Evaluate competitive moats and durability
12. Compare valuation multiples to growth and peers
13. Build projection models (bull/base/bear)

`/scan` covers steps 6–12 in structured form via the 6-pillar scorecard. Steps 2–5 (10-K + 10-Q + earnings-call deep dive) are added **manually** for high-conviction names where the auto-reject didn't fire and a position is being considered. Step 13 lives in the trade-plan section.

### How to read a 10-K efficiently

Most of a 10-K is generic legal boilerplate. The 80/20 move is to identify the 20–30 pages that carry the company-specific signal, skim the rest, and use the document as a sharpening tool — not a starting point.

- Don't open with the 10-K — get basic company familiarity first
- Apply 80/20: which pages carry company-specific information?
- Skim legal/generic content; slow down for company-specific content
- Annotate as you go for later valuation work
- Don't try to master every footnote on first pass — you'll never finish

| Section | What to look for |
|---|---|
| **Business overview** | Factual operations, products, business model |
| **Key operating metrics** | Internal management metrics (users, subscribers, retention, ARPU) |
| **Risk factors** | Company-specific risks, not boilerplate |
| **Business model details** | How revenue is generated, pricing mechanics, unit economics |

The "key operating metrics" section is where Pillar 2 (Growth) and Pillar 1 (Quality) signals live. Finviz exposes top-line P&L, but the 10-K is where the *durability* signal hides — cohort retention, ARPU trends, customer concentration. When a 6-pillar verdict is borderline, this is the source to reach for next.

### How to read financial statements

Financial-statement analysis lets investors evaluate companies on empirical evidence rather than market sentiment. The three statements — income, balance sheet, cash flow — must be read **together**, not in isolation, because each tells a different part of the same story.

- Read all three statements together — none is sufficient alone
- Stock price tells you what the market feels today; financial statements tell you what the business is doing
- Distinguish reported profits from actual cash generation (income vs cash-flow gap)
- Free cash flow represents real options for management to allocate
- **Red flags:** rising debt + weak cash flow · declining margins · excessive share dilution · adjusted earnings far from actual profits
- **Green flags:** consistent revenue growth · stable margins · strong capital returns · manageable debt

| Statement | Tells you | Key signals |
|---|---|---|
| **Income** (performance) | Whether the business performs over a period | Revenue growth consistency · gross profit & operating leverage trends · net income & EPS sustainability |
| **Balance sheet** (strength) | Financial position at a point in time | Liquidity & cash · debt & flexibility · current asset/liability coverage · shareholder equity over time |
| **Cash flow** (reality) | Whether reported profits become cash | Operating cash from core business · capex requirements · free cash flow available |

**Maps onto multiple pillars of the 6-pillar scorecard:**
- Income statement → Pillars 1 (Quality), 2 (Growth)
- Balance sheet → Pillar 4 (Balance Sheet) directly
- Cash flow → Pillar 5 (Capital Allocation) — FCF is what management has to allocate

In `/scan`, Finviz quote-page covers the income statement headline numbers; Stockanalysis covers FCF + balance-sheet detail. The two-source split in [`guide/scan/data.md`](../guide/scan/data.md) is the read-together principle in operation.

### Every income statement tells a story

The income statement is a narrative read top-to-bottom, not a set of headlines. A healthy business shows alignment — revenue, gross profit, operating income, net income, and EPS all move together in the right direction. Misalignment between these lines is where the actual signal lives.

- Read line-by-line top to bottom — don't cherry-pick metrics
- Strong businesses show alignment across the whole P&L
- Not all growth is equal — revenue gains are weak signal if profit doesn't follow
- Flat or declining lower-line metrics warrant skepticism
- Watch for expense growth outpacing revenue, shrinking margins, losses despite revenue narrative
- Simpler, more transparent progressions usually indicate better operations

| Line | What it reveals |
|---|---|
| Revenue | Demand direction — increasing, flat, or eroding |
| Gross profit | Product economics + pricing power are intact (or not) |
| Operating income | Expense discipline relative to growth |
| Net income | Actual profit reaching the owner after everything |
| EPS | Per-share value creation (dilution-adjusted) |

**The story to look for:** each line moves the same direction at roughly the same magnitude.
**The story to fear:** revenue grows, gross profit flat, operating income declining, EPS falling — that's "growth funded by margin destruction."

The "alignment" check is what separates a 6-pillar PASS Pillar 2 from a "decel + margin compression" FAIL.

---

## Business quality

### Economic moat and profit margins

Identifying exceptional businesses requires reading two interconnected signals together: the **economic moat** (competitive durability) and the **profit margin** (financial strength). High margins signal moat, but only if durable; revenue growth without margin maintenance is a major warning sign.

- High margins signal pricing power, efficiency, customer loyalty, or differentiation — when durable
- Three margin types to read: **gross** (product profitability) · **operating** (efficiency) · **net** (final value)
- Low-margin industries leave no room for error
- Revenue growth + declining margins = a major warning, not a success signal
- Sustainable businesses combine: healthy growth + strong margins + competitive advantage + disciplined management
- Examine consistency over time, peer comparison, and behavioral evidence (do customers actually behave as if locked in?)

The 7 moat types:

| Moat type | Identification |
|---|---|
| **Brand strength** | Customers pay premium prices because of the name |
| **Switching costs** | Customers locked in for years (enterprise software, payment rails) |
| **Network effects** | Value increases with scale (payment networks, marketplaces) |
| **Cost advantages** | Lower production economics than competitors (scale, geography, process) |
| **Intellectual property** | Patents or proprietary tech blocking competitors |
| **Regulatory advantages** | Legal protections or licensing barriers |
| **Premium positioning** | Differentiation justifying higher prices (luxury, specialization) |

The "moat type" taxonomy is a useful lens to add when scoring Pillar 1 (Quality) — instead of just "high margins PASS," ask *why* the margins are high and whether the answer points to a durable structural advantage. That's the difference between margins that compound (Mastercard's network effect) and margins that evaporate (cyclical-peak commodity producers).

### High-margin vs low-margin businesses

Margin structure reveals competitive durability. High-margin businesses have defensible advantages — brand, switching costs, network effects, IP, cost — and retain investment capacity through downturns. Low-margin businesses are fragile: a small revenue decline can wipe the profit pool entirely.

- Margins signal underlying moats, not just operational skill
- High-margin businesses can weather pricing pressure and reinvest through cycles
- Low-margin industries collapse fast on modest revenue declines
- Margin **stability and trend** matter more than absolute level
- Some intentionally-low-margin models still work — volume + recurring revenue can substitute for headline margins
- Always compare margins against direct industry peers
- Red flags: declining margins on rising revenue · reliance on adjusted profitability · interchangeable competitor positioning

There are no absolute thresholds — margin context is industry-specific. A 5% net margin in groceries is durable; a 5% net margin in software is broken. The framework:

1. Compare to peers in same industry
2. Track stability over multi-year window
3. Ask whether the margin is structural (moat-driven) or cyclical (boom-time)

The auto-reject "negative gross margin" trigger comes directly from this idea — gross margin is the most upstream margin and the cleanest read on whether the product itself is economically viable.

### Why margins matter more than revenue

Revenue gets attention; margins create wealth. Strong profit margins are a more reliable signal of business quality and competitive advantage than top-line growth. High-margin businesses compound; low-margin ones are fragile to small setbacks.

- Track three margin types: **gross**, **operating**, **net** — each tells a different story
- Strong margins typically signal pricing power, brand, switching costs, network effects, IP, or cost advantages
- Low-margin businesses require perfect execution and constant cost control — there's no margin for error
- Compare margins to peers and track stability over time
- Premium valuations on durable margins are justified — durable margins convert growth into actual cash
- The right question: "How good is this business?" — not just "How fast is it growing?"

Revenue measures size. Margins measure quality. A slower-growing high-margin business will often outperform a faster-growing low-margin business because the high-margin business converts each dollar of revenue into more shareholder value, with more cash to reinvest at high ROIC.

The auto-reject flags trigger on negative gross margin (and not, say, negative revenue growth) because a margin failure is more diagnostic of business quality than a growth slowdown. A growing-revenue, shrinking-margin company is signal that the growth is being bought rather than earned.

---

## Valuation

### Reasonable P/E ratio based on growth

A P/E in isolation tells you nothing — it must be evaluated against the company's realistic future earnings power and the durability of those earnings. The discipline is to match the multiple to the growth rate the business can credibly deliver under conservative assumptions, not under perfect-execution scenarios.

- P/E should track earnings growth as a directional rule of thumb
- Growth must be real (revenue, margins, durable demand) — not narrative
- Use conservative assumptions; don't price perfect execution
- Two companies with identical growth rates can deserve different multiples based on earnings predictability
- Stretched valuations imply perfect execution — that's the red flag, not the multiple itself
- Green flag: credible growth + conservative assumptions + sensible multiple

Directional P/E vs growth rule of thumb:

| Earnings growth | Justifiable P/E direction |
|---|---|
| Slow / mature growers | "Ordinary" multiples |
| ~25% EPS growth | "Meaningfully higher" multiples |
| ~35% earnings growth | A P/E "in that neighborhood" — the PEG-adjacent intuition |

Quality and predictability tilt the multiple up; cyclicality and customer concentration tilt it down at the same growth rate.

The growth-adjusted lens is what separates an auto-reject (negative gross margin + 3.7x P/S = expensive for what you get) from a justifiable premium multiple (35%+ EPS growth on durable demand → premium P/E earned).

---

## Capital allocation

### How great management compounds wealth

Strong revenue and profits don't guarantee strong returns to shareholders. Management's deployment of free cash flow — capital allocation — is the underappreciated driver of long-term value. Two companies with identical earnings can diverge dramatically based on what they do with the cash.

- Every dollar can only be used once — allocation choices are zero-sum
- Growth without high return on invested capital adds size, not substance
- Buybacks, dividends, and M&A require contextual evaluation — none are universally good or bad
- Management quality reveals itself through allocation decisions more than through growth rhetoric
- Strong balance sheets create optionality during downturns — that itself is a capital allocation choice

| Option | Works when | Fails when |
|---|---|---|
| **Reinvestment** | High ROIC; >$1 future value per $1 invested | Low-return projects that just inflate size |
| **Buybacks** | Stock reasonably valued; strong FCF; limited better opportunities | Inflated share price; masking weakness |
| **Dividends** | Mature business; stable cash flows; limited reinvestment paths | Misleading signal about lifecycle stage |
| **M&A** | Disciplined, strategic fit, realistic synergies | Overpayment, weak integration, empire-building |
| **Debt reduction** | Strengthens balance sheet optionality | Rarely problematic when prudent |

The signals already tracked in `/scan` — share-count change YoY, ROIC, dividend policy, recent M&A — map directly onto this evaluation framework. 17% YoY dilution + negative ROIC is a Pillar 5 FAIL by every test in this matrix.

### How great management creates long-term returns

Management's decisions about deploying cash are as important as earnings generation itself. Two companies with identical financial surfaces can diverge dramatically based on capital allocation quality.

- Every dollar of cash has only one use — allocation creates or destroys value
- Reinvestment at high ROIC compounds better than distributions
- Buybacks only create value when the stock is reasonably priced AND the business is strong
- Dividends signal business maturity but may cap compounding potential
- Acquisitions frequently destroy value through overpayment + poor integration
- Debt reduction provides optionality and balance sheet strength
- Share-count trends, ROIC, and management discipline matter more than growth rate alone

**Five questions to ask of management's allocation decisions:**

1. Can the company reinvest at attractive returns? (ROIC > WACC)
2. Is the balance sheet adequately strong?
3. Are buybacks executed at sensible valuations?
4. Are dividends appropriate for the business stage?
5. Are acquisitions strategic and disciplined?

Run these as a checklist when scoring Pillar 5 — treat it as a capital-discipline audit, not just a "did they buy back stock" yes/no.

---

## Portfolio strategy

### Portfolio management — diversification, sizing, risk

A portfolio is an intentional system, not a collection of stocks. Strong architecture lets quality ideas compound while protecting against individual mistakes. Position sizing should reflect conviction and quality, every holding should have a clear role, and diversification should be enough to survive errors but not so much that knowledge gets diluted.

- Build around cornerstone positions — durable models, high conviction
- Distinguish helpful diversification from harmful "diworsification"
- Size by conviction × business quality × valuation × downside risk
- Every holding has a role: compounder · growth driver · value/dividend · speculative
- Excessive concentration blinds you to deteriorating fundamentals
- Risk = business-quality risk + capital-impairment risk, NOT just price volatility
- Review holdings as an owner — thesis still valid? capital-allocation discipline intact?
- Growth investing requires: durable demand · reasonable valuation · business quality

**Position counts:** the principle is "enough to be protected from mistakes, few enough to stay informed about each holding." Most disciplined long-term investors operate in the 8–25 position range, but the right number depends on time available for monitoring.

The [tier system](../guide/scan/tiers.md) provides the position-role assignment vocabulary:

- **T** (Top Pick) → cornerstone / compounder
- **W** (Watchlist) → growth-driver candidates
- **B** (Bench) → value/dividend or thematic optionality
- **S** (Skip) / **X** (Dropped) → not in the portfolio

The "review as an owner" cadence maps onto the rescan protocol (`/rescan`) — testing whether the thesis is still valid each cycle.

### Consistent investing vs high-conviction bets

The strongest investors do both — steady contributions through compounding plus occasional larger deployments when truly unusual opportunities appear. Consistency is the engine; conviction-sized bets are the multiplier when the rare setup arrives.

- Regular contributions and time in market are the wealth engine
- Not every opportunity is equal — the rare "unusual setup" deserves more capital
- Conviction must come from research, not excitement or social momentum
- Price determines whether a great company is a great investment
- Discipline guards against impulsive size in normal markets and passivity in exceptional ones
- Do the work first — only upsize after deep business research

| Mode | When |
|---|---|
| **Steady building** | Most of the time — adds to quality businesses, stays patient |
| **Aggressive sizing** | Rare setups: improved fundamentals · inflected profitability · attractive valuation · backed by rigorous research |

Most names live at **B** or **W** (steady-state monitoring) most of the time. **T** (Top Pick) is the conviction tier reserved for moments when 6-pillar score, regime fit, and technical posture all align — exactly the "unusual setup" the principle describes. The discipline of [tier-change protocol](../guide/scan/tiers.md) prevents emotional upgrades to **T**.

### Should you sell after a stock doubles?

The decision to sell is forward-looking, not anchored to your cost basis. The relevant question is not "what has this stock done for me?" but "what return is available from here?" — purchase price is a sunk reference, not a sell signal.

- Cost basis is irrelevant to the sell decision — a stock doesn't know what you paid
- Re-evaluate fundamentals quarterly or after material developments
- Forward projections drive the decision; historical performance does not
- Hard stop-losses often hurt long-term investors by exiting on temporary volatility
- Lower prices can be opportunities if the business thesis is intact
- Conviction (built from research) replaces automated triggers

This is a counterweight to swing/day-trade `Stop:` discipline — those triggers are valid for short-horizon trades but apply weakly to a Positional thesis where the question is durability of the underlying business. A Positional **T** doesn't downgrade to **S** because the stock doubled, only because the business or regime changed.

### What is a good annual return?

Set return expectations to be repeatable, not exceptional. Targeting too low (index returns) means active research isn't justified; targeting too high (50–100% per year) breeds reckless behavior and bad bets. The aim is sustainable outperformance built from quality businesses and disciplined process.

- Two failure modes: bar too low (just match indices) or bar too high (50–100%/yr expectations)
- Outperformance must be earned by repeatable process, not single big years
- Small differences in CAGR compound enormously over decades
- Anchor expectations to what the *process* can deliver, not what one good year delivered

| Tier | CAGR | Description |
|---|---|---|
| Market baseline | ~9% | Long-run broad-market historical |
| Respectable floor | 15% | A solid long-term result for an active investor |
| Solid target | 20% | Strong consistent performance |
| Excellent | 25% | Top-tier, hard to sustain |
| North-star ambition | 30% | Reference: Buffett Partnership 29.5% CAGR |

This sets the realistic expectation framework for the Positional horizon. It also frames why auto-reject discipline matters — most names fail to clear a 15%+ CAGR bar over multi-year holds; the screen exists to surface the few that can.

### Wealth roadmap

Wealth-building progresses through stages — first reducing financial fragility, then creating stability, finally enabling life optionality. Early on, contributions matter more than returns; later, decision quality matters more than savings rate. The goal is practical optionality (employment becomes optional), not extreme outcomes.

- Early stage: aggressive saving + consistent investing dominates over optimization
- When account balances are low, contributions matter more than gains
- Hitting early milestones provides psychological momentum — don't underrate it
- Stages: reduce fragility → create stability → enable optionality
- Decision quality scales with capital — bigger portfolios, bigger consequences
- Convert goals into plans: timeline · monthly contribution · realistic CAGR assumption
- Target practical optionality, not fantasy outcomes

$100K is a key early milestone — the implicit progression: save aggressively to reach the first material number, build skill and consistency through middle stages, then reach optionality tiers where employment becomes optional. At small portfolio scale you're learning; at larger scale, the protocol guards against costly mistakes.

### Knowledge must grow with your portfolio

Capital and competence must scale together. A small portfolio can absorb mistakes; a large one cannot. The early years of investing set a trajectory — building skill before the dollar value is high is the asymmetric path.

- Small portfolios tolerate mistakes; large portfolios do not
- The first few years establish long-term patterns
- Large capital + low competence → oversized mistakes, emotional decisions, expensive experimentation
- Essential skill stack: portfolio management · position sizing · diversification · financial-statement analysis · valuation · emotional discipline
- Phase capital in gradually if competence lags experience
- Structure beats stock-picking on social media

The 6-pillar + technical system embeds this scaling. By enforcing rigor (auto-reject flags, regime fit, multi-horizon read) before any size goes on, the protocol enforces this discipline. The [self-improvement loop](../guide/scan/style.md) compounds knowledge through the audit trail.

---

## Macro and market timing

### Ignore macro forecasting, focus on businesses

Macro variables interact in non-linear ways that defy reliable forecasting. Long-term investors should redirect that effort toward business-level analysis — observable metrics like margins, cash flow, and management quality are far more trackable than rate cuts or recessions. The goal is to own businesses that *endure* environments, not predict them.

- Macro forecasting fails because the variables interact non-linearly
- Business metrics (revenue, margins, FCF, management) are observable and trackable
- The right question: "can this business endure difficult environments?" — not "will the environment be favorable?"
- Strong margin businesses can capitalize during downturns by outcompeting weaker rivals
- Research priorities: business model durability · FCF quality · balance sheet · competitive moats
- Over long timeframes, business execution dominates macro timing in returns

**Useful tension with the macro/regime work in [`docs/macro.md`](macro.md):**

This principle is **directly counterposed** to the Q1–Q4 regime framework — and that tension is productive, not contradictory. The resolution is **horizon-specific**:

| Horizon | Macro relevance |
|---|---|
| **Positional** (weeks-to-months) | This principle applies — business durability dominates; regime is context not driver |
| **Swing** (3–15 days) | Regime gates moderately — Q3 hostile to long-duration tech is a real headwind |
| **Day-trade** (today) | Regime barely matters — max-pain magnet, IV crush, session flow take over |

The framework doesn't *abandon* macro — it scopes it. Stock-pickers shouldn't predict the macro. Swing/day timers shouldn't ignore it. Both can be true.

### The IPO cycle

Companies go public on terms favorable to insiders, not investors — IPOs price in optimism, not value. The disciplined move is to add new listings to a watchlist and wait through the post-IPO consolidation, where business performance (or its absence) does the filtering.

- Don't feel pressured to buy at listing — distinguish hype from durable value
- Add new IPOs to a watchlist; reserve capital for after the consolidation phase
- Track margins, execution, guidance credibility quarter-by-quarter
- The "boring period" after the hype fades is often the better entry
- Reframe the question from "should I buy now?" to "could this be materially better in 2–3 years?"

A **2–3-year hold-and-observe window** is the suggested cycle for letting the post-IPO noise resolve into either a real business case or a clear pass.

This is the research-funnel "watchlist" stage applied to IPOs specifically. Maps to a **Positional `B` (bench)** tier in the [coverage tier system](../guide/scan/tiers.md) — followed but inactive — until the business proves itself.
