# Discovery Rules — `/discover` and `scanned/SCREENS/`

**Purpose:** Discovery is the funnel — Finviz screener runs that produce candidate lists matching the framework's 6-pillar criteria, regime-aware. `/scan <TICKER>` is the diligence step that follows.

`/discover` follows these rules. The command file at `.claude/commands/discover.md` orchestrates; this file holds the protocol.

## Framework alignment (the first rule)

Every filter applied here MUST map to something in `docs/`:

- **6-Pillar fundamentals** ([`guide/scan/scorecard.md`](scan/scorecard.md)) — Quality, Growth, Valuation, Balance Sheet, Capital Allocation, Smart Money
- **Price Behavior Filter** (same doc) — price > 50d > 200d, near 52w high, RS rank
- **Macro regime** ([`docs/macro.md`](../docs/macro.md)) — regime-aware leverage / quality floors
- **MA structure** — 50d / 200d positioning, golden cross

**What's deliberately out of scope:** RSI, MACD, oscillators, beta, ATR, volatility, candlestick patterns, gaps. These are either chart-read concepts (the framework reads them on the chart during `/scan`, not as screener inputs) or outside our methodology. See § Out of scope below for the full list and redirect rules.

**The discovery screener is the framework's funnel, not a generic stock-screening tool.** If a filter doesn't trace back to `docs/`, it doesn't belong here.

---

## SCREENS folder structure

```
scanned/
└── SCREENS/
    ├── 2026-04-29.md           ← one file per screen run
    ├── 2026-04-29-quality.md   ← multiple presets same day get suffixed
    ├── 2026-05-06.md
    └── ...
```

- One folder: `scanned/SCREENS/`
- One file per run: `<YYYY-MM-DD>.md` (no preset suffix if only one preset run that day) or `<YYYY-MM-DD>-<preset>.md` (when multiple presets run the same day)
- Files are dated, not rotated — they accumulate. Retention is age-based (see below).

## Snapshot file structure (every screen file)

```markdown
# Screen — YYYY-MM-DD (PRESET)

**Regime:** Stagflation (cross-ref MACRO/current.md YYYY-MM-DD)
**Preset:** r3 (Stagflation defensive)
**Filter rationale:** quality + pricing power, low leverage, defensive sectors
**Finviz URL:** <full URL>

## Candidates (N)

| # | Ticker | Sector | Mkt Cap | P/E | Price | 52w% | Vol | Notes |
|---|---|---|---|---|---|---|---|---|
| 1 | ABC | Healthcare | $50B | 18 | $120 | +25% | 5M | * |

`*` = persistent (appeared in a prior screen within 30 days)

## Suggested next steps

Deep-scan candidates with `/scan`:
```
/scan ABC
/scan XYZ
```

## Sources
- [Finviz screener — full URL](URL)
- [MACRO/current.md regime](../scanned/MACRO/current.md)
```

## Retention policy

The audit trail of "what we were looking at on date X." Bounded:

- **Last 90 days**: keep all screen files
- **Older than 90 days**: prune to monthly (one screen per month for older history — keep the latest of each month)
- **Older than 24 months**: drop entirely

Pruning happens at the end of every `/discover` run. Implementation:

1. List `scanned/SCREENS/*.md`
2. Files within last 90 days: keep all
3. Files between 90 days and 24 months: group by `YYYY-MM`, keep newest per month
4. Files older than 24 months: delete

## Persistence marker

Tickers that appear in multiple recent screens are stronger candidates per the framework's "confluence to confluence" rule. Mark with `*` in the Notes column:

- Ticker appeared in any screen within last 30 days (excluding today's run) → `*`
- Ticker appeared in 3+ screens within 60 days → `**`
- New ticker (first appearance) → no marker

Persistence is a quality signal — a name that screens repeatedly across multiple runs has more conviction than a one-off.

## Read-before-discover protocol

Before constructing the Finviz URL:

1. **Read `scanned/MACRO/current.md`** — capture current regime + key gauges. If no preset arg was provided, set preset = current regime.
2. **Skim `scanned/SCREENS/`** — read the 2 most recent screen files (any preset). Note tickers that appeared persistently. The new run's results will be cross-referenced against these for the persistence marker.
3. **If `MACRO/current.md` is older than 7 days** — warn the user; offer to run `/scan-macro` first.

`docs/` and `guide/` are read-only — never modified during a discovery run.

## Finviz URL construction

Format:
```
https://finviz.com/screener.ashx?v=<view>&f=<comma-separated-filters>&o=<sort>
```

- **`v=111`** — overview view (default; gives ticker, sector, mcap, P/E, price, change, volume)
- **`v=152`** — financial view (margins, ROI, ROE, debt/equity)
- **`v=141`** — performance view (1w through 1y returns)
- **`f=`** — filters, comma-separated
- **`o=`** — sort field; prefix `-` for descending. Examples: `-marketcap`, `-roi`, `-grossmargin`, `-perf13w`

## Verified Finviz filter prefixes

All codes verified against [finvizfinance/constants.py](https://github.com/lit26/finvizfinance/blob/master/finvizfinance/constants.py) (authoritative reverse-engineered Finviz spec).

### Common base (all presets)

| Filter | Code | Meaning |
|---|---|---|
| Market cap | `cap_smallover` | > $300M (skip illiquid micro-caps) |
| Avg volume | `sh_avgvol_o500` | > 500K daily |
| Price > 50d SMA | `ta_sma50_pa` | uptrend short-term |
| Price > 200d SMA | `ta_sma200_pa` | uptrend long-term |
| 50d > 200d | `ta_sma50_sa200` | golden cross intact |

### Pillar 1 — Quality

| Metric | Prefix | Common values |
|---|---|---|
| ROI (proxy for ROIC) | `fa_roi` | `o15`, `o20`, `o25` (5%-step increments only; **no `o12`**) |
| Gross margin | `fa_grossmargin` | `o20`, `o30`, `o35`, `o40`, `o50` (5%-step) |
| Operating margin | `fa_opermargin` | `o15`, `o20` — **NOT `fa_opmargin`** (common typo) |
| Net margin | `fa_netmargin` | `o10`, `o15`, `o20` |

### Pillar 2 — Growth

| Metric | Prefix | Common values |
|---|---|---|
| EPS 5y | `fa_eps5years` | `o15`, `o20`, `o25` |
| EPS QoQ | `fa_epsqoq` | `o15`, `o20`, `o25`, `o30` |
| Sales QoQ | `fa_salesqoq` | `o10`, `o15`, `o20`, `o25` |
| Sales 5y | `fa_sales5years` | `o15`, `o20` |

### Pillar 3 — Valuation

| Metric | Prefix | Common values |
|---|---|---|
| P/E | `fa_pe` | `u15`, `u20`, `u25`, `u30` |
| Forward P/E | `fa_fpe` | `u15`, `u20` |
| PEG | `fa_peg` | `u1`, `u2`, `u3` — **integer-only**; Lynch's 1.5 falls into `u2` |
| P/S | `fa_ps` | `u1`, `u2`, `u5` |
| P/B | `fa_pb` | `u1`, `u2`, `u3` |

### Pillar 4 — Balance Sheet

| Metric | Prefix | Common values |
|---|---|---|
| Debt/Equity | `fa_debteq` | `u0.3`, `u0.4`, `u0.5`, `u1` |
| LT Debt/Equity | `fa_ltdebteq` | similar |
| Quick Ratio | `fa_quickratio` | `o1`, `o1.5`, `o2` |
| Current Ratio | `fa_curratio` | `o1`, `o1.5`, `o2` |

### Pillar 5 — Capital Allocation (limited)

| Metric | Prefix | Common values |
|---|---|---|
| Dividend yield | `fa_div` | `o1`, `o2`, `o3`, `o5` |
| Payout ratio | `fa_payoutratio` | `u50`, `u60` |
| Insider ownership | `sh_insiderown` | `o10`, `o20`, `o30` |

### Pillar 6 — Smart Money

| Metric | Prefix | Common values |
|---|---|---|
| Inst ownership | `sh_instown` | `u80` (avoid over-owned), `o30` (institutional interest) — see caveat below |
| Inst transactions | `sh_insttrans` | `pos`, `neg`, `verypos`, `veryneg` (last 3mo aggregate; coarse) |
| Insider transactions | `sh_insidertrans` | `pos`, `neg`, `verypos`, `veryneg` (last 6mo) |
| Float short | `sh_short` | `low`, `high`, `u5`, `o20` |

**Caveat — `sh_instown_u80` silently excludes mega-cap quality.** Defense majors (LMT, NOC, RTX), large pharma, mega-cap tech, and most mature compounders are structurally >80% institutional. The regime presets carry `sh_instown_u80` to flag genuinely over-owned mid-caps where the smart-money trade is already crowded — but applied to a query that targets large-cap quality (defense, healthcare, mega-cap tech, blue-chip dividend names), it removes most of the natural universe. **When the query implies large-cap quality**, drop `sh_instown_u80` or raise to `u95`. Note the override in the screen file's TL;DR.

### Trend & Relative Strength (framework-aligned only)

Only filters mapping to the **Price Behavior Filter** (per [`scorecard.md`](scan/scorecard.md)) and the framework's MA structure (50d / 200d positioning, golden cross) are used. No oscillators, no candlestick patterns, no beta — those are chart-read concepts in our framework, not screener inputs.

| Metric | Prefix | Common values | Framework anchor |
|---|---|---|---|
| Price > 50-day SMA | `ta_sma50_pa` | (boolean) | Price filter: > 50d MA |
| Price > 200-day SMA | `ta_sma200_pa` | (boolean) | Price filter: > 200d MA |
| 50d > 200d (golden cross) | `ta_sma50_sa200` | (boolean) | Price filter: 50d > 200d uptrend |
| 52w high distance | `ta_highlow52w` | `b0to3h`, `b0to5h`, `b0to10h` | CANSLIM "N" — within 5–15% of 52w high |
| Performance (RS proxy) | `ta_perf` | `13w20o`, `26w50o`, `52w20o` | CANSLIM "L" / RS rank ≥ 80 (Finviz has no IBD RS rank; performance window is the closest approximation) |

### Sectors

| Sector | Code |
|---|---|
| Basic Materials | `sec_basicmaterials` |
| Communication Services | `sec_communicationservices` |
| Consumer Cyclical | `sec_consumercyclical` |
| Consumer Defensive | `sec_consumerdefensive` |
| Energy | `sec_energy` |
| Financial | `sec_financial` |
| Healthcare | `sec_healthcare` |
| Industrials | `sec_industrials` |
| Real Estate | `sec_realestate` |
| Technology | `sec_technology` |
| Utilities | `sec_utilities` |

### Sort fields (used in `&o=`)

`marketcap`, `pe`, `peg`, `roi`, `roe`, `grossmargin`, `opermargin`, `dividendyield`, `perf4w`, `perf13w`, `perf26w`, `perfytd`, `perf1y`, `change`, `volume`. Prefix `-` for descending.

### Known framework gaps Finviz can't screen

- **True ROIC** (vs WACC, 5y trend) — Finviz only has ROI as proxy. Use `fa_roi_o15` and verify true ROIC during `/scan`.
- **FCF margin / FCF conversion** — Finviz shows Price/FCF only.
- **13F holder COUNT change QoQ** — Finviz `sh_insttrans` is dollar-weighted aggregate, not the count change CANSLIM "I" requires.
- **Insider cluster buys** — Finviz `sh_insidertrans` is aggregate, not transaction-level.
- **Net Debt / EBITDA** — only Debt/Equity available.
- **Capital allocation history** (Pillar 5) — qualitative; not screenable.

These verify during `/scan`. Discovery filters narrow the universe; deep diligence catches what Finviz can't see.

### Out of scope — never screen on these

The framework deliberately doesn't use these for stock selection. They're either chart-read concepts (the framework reads them on the chart, not as filters) or simply outside our methodology. **Do not add these Finviz filters even if the user asks for them.**

| Out-of-scope | Why | Redirect if user asks |
|---|---|---|
| **RSI** (`ta_rsi`) | RSI is for chart reading, not screening | "RSI isn't in our screener — for oversold/overbought reads, run `/scan <TICKER>` and the technical section will read it from the chart" |
| **MACD** | Not in framework | Same — chart concept, not screener |
| **Beta** (`ta_beta`) | Volatility-adjusted concept; not in framework | "Beta isn't a framework filter. If you want stable names, use low D/E + high gross margin (Pillar 1+4)" |
| **ATR** (`ta_averagetruerange`) | Position-sizing concept, not a selection filter | Same — used in trade plan, not discovery |
| **Volatility** (`ta_volatility`) | Same | Same |
| **Candlestick patterns** (`ta_candlestick`) | Chart-read concept — done by eye on the chart | "Patterns are read on the chart during `/scan`, not screened" |
| **Generic chart patterns** (`ta_pattern`) | Same | Same |
| **Gap** (`ta_gap`) | Gap behavior is read on the chart | Same |
| **Change today** (`ta_change`) | Day-trading filter, not framework | "Today's move isn't a selection criterion — we look at 6-pillar + technical setup, not single-bar action" |

**Rule:** if a user asks for an out-of-scope filter, **don't silently include it**. State the redirect in the screen file's TL;DR — explain that the filter isn't framework-aligned and what the closest framework equivalent is. The user can override by asking again explicitly, but the default is: stay aligned.

## Argument parsing — one mode, freeform

`$ARGUMENTS` is whatever the user typed — a sentence, a sector word, a ticker reference, or empty. There is no fixed argument grammar. Always **parse intent** rather than matching specific keywords.

### Parse the message by extracting tokens

| Token type | Examples | Action |
|---|---|---|
| **Ticker references** | `AAPL`, `like NVDA`, `similar to USAR`, `match X` | Fetch Finviz quote page; extract sector/industry, ROI, gross margin, P/E, market cap. Use as match anchors. |
| **Sector / industry keywords** | `defense`, `tech`, `semis`, `oil`, `biotech`, `gold miners` | Map via § Sector / industry alias table |
| **Regime hints** | `r1` / `r2` / `r3` / `r4`, `stagflation`, `goldilocks`, `reflation`, `risk-off`, `defensive` | Use that regime's preset filter set as the base |
| **Style hints** | `quality`, `growth`, `value`, `near 52w high`, `golden cross`, `momentum`, `dividend payers`, `cheap` | Apply matching preset filters from § Preset filter sets |
| **Numeric constraints** | `ROI > 20`, `P/E < 15`, `D/E under 0.5`, `gross margin > 30%`, `dividend > 3%` | Map to verified Finviz code; **snap to nearest available tier** |
| **Empty** | `/discover` with no message | Use current `MACRO/current.md` regime preset |

### Always-anchor rules (apply automatically)

- **Read `MACRO/current.md` regardless** — it sets the regime context, even if the user's request is regime-agnostic.
- **Apply the current regime preset's leverage/quality floor** as a baseline (e.g., r3's `fa_debteq_u0.4` is always added unless user explicitly overrides). This prevents accidentally screening for over-levered junk.
- **Add common-base filters** (cap > $300M, vol > 500K, price > 50d > 200d) unless the user asks for something pre-trend (e.g., "below 200d" — then drop the trend filters and note the override).

### Combination & conflict rules

- **Combine, don't override.** Sector + ROI constraint + ticker reference all stack. Filters are intersected, not unioned.
- **Snap numeric constraints to the nearest tier.** "ROI > 22" → `fa_roi_o20` (snapped down because we want strictly-greater intent preserved). "P/E < 23" → `fa_pe_u25` (snapped up because we want strictly-less). State the snap in the screen file.
- **Regime conflicts**: if the user contradicts the regime (e.g., asks for tech in Stagflation), honor the user's explicit ask but flag it in the TL;DR: `Regime divergence: tech longs in Stagflation are not regime-favored — verify thesis.`
- **Unresolvable phrasing**: if a token has no clean mapping (e.g., "AI plays" — no Finviz AI category), ask the user to clarify rather than guessing.

### TL;DR audit format (mandatory)

Every screen file's TL;DR must state the parsed interpretation in plain English:

```
**Parsed query:** "<original user message>"
- Sector / industry: aerospacedefense (from "defense")
- ROI floor: o25 (from "similar ROI to AAPL", AAPL ≈ 28%, snapped 28 → 25)
- Regime base: r3 (current MACRO regime: Stagflation)
- Debt floor: u0.4 (r3 preset baseline)
- Common base: cap > $300M, vol > 500K, price > 50d > 200d
```

The user reads this to verify Claude understood them. If wrong, they re-run with clearer phrasing.

## Sector / industry alias table

Common user terms → Finviz codes. Add to this list as new aliases come up.

| User term | Finviz code | Type |
|---|---|---|
| **defense, defence, military** | `ind_aerospacedefense` | industry |
| **aerospace** | `ind_aerospacedefense` | industry |
| **semis, semi, semiconductor, chips** | `ind_semiconductors` | industry |
| **chip equipment** | `ind_semiconductorequipmentmaterials` | industry |
| **oil, oil & gas, O&G** | combine: `ind_oilgasep` OR `ind_oilgasintegrated` OR `ind_oilgasrefiningmarketing` | industry (multi) |
| **biotech** | `ind_biotechnology` | industry |
| **pharma** | `ind_drugmanufacturersgeneral` OR `ind_drugmanufacturersspecialtygeneric` | industry |
| **banks** | `ind_banksdiversified` OR `ind_banksregional` | industry |
| **insurance** | `ind_insurancediversified` OR `ind_insurancelife` OR `ind_insurancepropertycasualty` | industry |
| **retail (general)** | `ind_discountstores` OR `ind_departmentstores` OR `ind_specialtyretail` | industry (multi) |
| **e-commerce, online retail** | `ind_internetretail` | industry |
| **airlines** | `ind_airlines` | industry |
| **autos, auto, automakers** | `ind_autoanmanufacturers` | industry |
| **EV, electric vehicles** | `ind_autoanmanufacturers` + filter by name/keyword (no clean Finviz EV code) | industry + manual |
| **REITs, real estate** | `sec_realestate` | sector |
| **utilities** | `sec_utilities` | sector |
| **healthcare** | `sec_healthcare` | sector |
| **tech, technology** | `sec_technology` | sector |
| **AI, machine learning** | `sec_technology` + flag candidates manually (no Finviz AI category) | sector + manual |
| **cyber, cybersecurity** | `ind_softwareinfrastructure` (closest; verify per ticker) | industry |
| **gold miners** | `ind_goldminers` | industry (verify exact code) |
| **silver miners** | `ind_silverminers` | industry (verify) |
| **steel** | `ind_steel` | industry |
| **copper** | `ind_coppermining` | industry (verify) |
| **lithium** | `ind_otherindustrialmetalsmining` (no clean lithium code) | industry + manual |
| **uranium** | `ind_uraniumminingexploration` (verify) | industry |
| **clean energy, renewables** | `ind_solar` OR industry-specific | industry (multi) |
| **shipping, tankers** | `ind_marineshipping` | industry |
| **gambling, casinos** | `ind_gambling` | industry |
| **cannabis** | `ind_drugmanufacturersspecialtygeneric` (limited Finviz coverage) | industry + manual |
| **food, packaged food** | `ind_packagedfoods` | industry |
| **beverages** | `ind_beveragesnonalcoholic` OR `ind_beveragesbrewers` | industry (multi) |

When the alias maps to multiple industry codes (multi), Finviz only allows one industry filter at a time. Two options:
1. Pick the dominant industry for the query (default)
2. Drop to sector level (e.g., `sec_consumerdefensive` instead of multiple food/bev industries)

State the choice in the screen file.

For aliases not in this table, search Finviz's industry dropdown values via the [verified constants spec](https://github.com/lit26/finvizfinance/blob/master/finvizfinance/constants.py). If still unresolvable, ask the user.

## Reference-ticker mode (similar-to-X)

When `/discover` includes a ticker reference (`similar to AAPL`, `like NVDA`, `match X`):

1. **Fetch the reference ticker's Finviz quote page** (`https://finviz.com/quote.ashx?t=<TICKER>`).
2. **Extract:**
   - Sector + Industry (use industry if specific enough, sector if industry is too narrow)
   - ROI (use as floor: snap to nearest 5% tier, e.g., AAPL ROI 28% → `fa_roi_o25`)
   - Gross margin (snap to nearest 5% tier)
   - P/E (use as ceiling, snapped UP — generous; e.g., reference P/E 24 → `fa_pe_u25`)
   - Market cap tier (large = `cap_largeover`, mid = `cap_midover`, small = `cap_smallover`)
3. **Build the filter** combining the reference ticker's profile + the current regime's leverage floor (debt/equity etc. from regime preset).
4. **Note the reference** in the screen file's TL;DR: `Reference: AAPL (ROI 28%, GM 47%, P/E 24)`.

The reference ticker is excluded from results (we want similar names, not the reference itself). Filter `&fmh=` or post-process the result list to drop it.

## Preset filter sets

These are **internal filter compositions** — building blocks Claude uses when parsing messages with regime hints (`r3`, `goldilocks`, `defensive`) or style hints (`quality`, `growth`, `value`). The user doesn't need to know them by name; phrasing like "stagflation defensive" or "cheap with high return on capital" maps to these compositions.

When the parsed message names a regime explicitly OR matches a regime via style hints, use the corresponding set as the filter base. When the message is empty, use the regime matching `MACRO/current.md`.

### `r1` / `goldilocks`

Per [`docs/macro.md` § Market regime framework](../docs/macro.md#market-regime-framework) — see best/worst assets table.

- Pillar 1: `fa_roi_o15`
- Pillar 2: `fa_eps5years_o20`, `fa_epsqoq_o25`, `fa_salesqoq_o20`
- Pillar 3: `fa_peg_u2`
- Pillar 4: `fa_debteq_u0.5`
- Sector tilt (optional): `sec_technology` / `sec_communicationservices`
- Sort: `&o=-perf13w`

### `r2` / `reflation`

Per [`docs/macro.md` § Market regime framework](../docs/macro.md#market-regime-framework) — see best/worst assets table.

- Pillar 1: `fa_roi_o15`
- Pillar 2: `fa_epsqoq_o20`, `fa_salesqoq_o15`
- Pillar 3: `fa_pe_u20`
- Pillar 4: `fa_debteq_u1`
- Sector tilt: `sec_energy` / `sec_basicmaterials` / `sec_industrials` / `sec_financial`
- Sort: `&o=-perf4w`

### `r3` / `stagflation`

Per [`docs/macro.md` § Market regime framework](../docs/macro.md#market-regime-framework) — see best/worst assets table.

- Pillar 1 (strict): `fa_roi_o20`, `fa_grossmargin_o35`, `fa_opermargin_o15`
- Pillar 2: `fa_eps5years_o15`, `fa_salesqoq_o10`
- Pillar 3: `fa_pe_u25`, `fa_peg_u2`
- Pillar 4 (strict): `fa_debteq_u0.4`, `fa_quickratio_o1`
- Pillar 6: `sh_instown_u80`
- Sector tilt: `sec_consumerdefensive` / `sec_utilities` / `sec_healthcare` / `sec_energy`
- Sort: `&o=-grossmargin`

### `r4` / `risk-off`

Per [`docs/macro.md` § Market regime framework](../docs/macro.md#market-regime-framework) — see best/worst assets table.

- Pillar 1: `fa_roi_o15`, `fa_grossmargin_o30`
- Pillar 4 (very strict): `fa_debteq_u0.3`, `fa_curratio_o2`, `fa_quickratio_o1.5`
- Pillar 5: `fa_div_o2`
- Sector tilt: `sec_consumerdefensive` / `sec_utilities` / `sec_healthcare`
- Sort: `&o=-dividendyield`

### `quality` (regime-agnostic 6-pillar)

- `fa_roi_o20`, `fa_grossmargin_o40`, `fa_opermargin_o20`
- `fa_eps5years_o15`, `fa_epsqoq_o20`
- `fa_debteq_u0.5`, `fa_quickratio_o1.5`
- `sh_instown_u80`
- Sort: `&o=-roi`

### `growth` (CANSLIM-style)

- `fa_epsqoq_o25`, `fa_salesqoq_o25`, `fa_eps5years_o25`
- `ta_highlow52w_b0to10h` (within 0–10% of 52w high — CANSLIM "N")
- `ta_perf_13w20o` (13-week perf > 20% — RS proxy)
- `sh_avgvol_o500`
- Sort: `&o=-perf4w`

### `value` (Greenblatt Magic Formula proxy)

- `fa_roi_o15`
- `fa_pe_u15`
- `fa_debteq_u1`
- Sort: `&o=-roi`

## Fallback: 0-results handling

If a screen returns 0 candidates:

1. **Loosen one filter at a time**, starting with the strictest:
   - `fa_debteq_u0.3` → `u0.4` → `u0.5`
   - `fa_grossmargin_o40` → `o35` → `o30`
   - `fa_roi_o20` → `o15`
2. **Note the relaxation** in the screen file: `Filter relaxed: fa_debteq_u0.3 → u0.4 (0 results at strict level)`
3. **Don't loosen below the framework floor** — e.g., never drop ROI below `o10` or PEG above `u3`.
4. If 3+ relaxations still return 0, output the screen with `0 candidates — regime-fit universe is empty this week` and stop.

Empty screens in stagflation are common — Stagflation wants strict quality, and most growth/cyclical names don't pass. That's a feature, not a bug.

### Industry-profile relaxations (start here when the query names an industry)

The regime presets are calibrated for general consumer-defensive / healthcare quality. Several industries have structurally different profitability + leverage + ownership profiles and **systematically fail strict regime presets even when the industry is regime-favored.** When a query names one of these industries, start from the relaxed defaults below instead of going through the full 0-result fallback chain.

| Industry / segment | Why strict regime fails | Recommended starting relaxations |
|---|---|---|
| **Aerospace & defense** | Premium multiples on geopolitical bid; mature low growth; service-revenue dilutes GM; >80% inst-owned; inventory-heavy | Drop `fa_grossmargin_o35`, `fa_eps5years_o15`, `fa_salesqoq_o10`, `fa_pe_u25`, `fa_peg_u2`, `fa_quickratio_o1`, `sh_instown_u80`. Loosen `fa_roi_o20` → `o15`, `fa_opermargin_o15` → `o10`, `fa_debteq_u0.4` → `u1`. Keep trend gates. |
| **Energy (E&P, integrated)** | Cyclical earnings → P/E volatile; capital-intensive → high D/E norm; commodity-tied margins | Drop `fa_eps5years_o15` (cyclical), `fa_pe_u25` (boom-bust). Loosen `fa_debteq_u0.4` → `u1`. Keep ROI / op margin floors. |
| **Utilities** | Regulated returns → ROI 6–10% (below o15 floor); high D/E by structure (regulated capital base); >80% inst-owned | Loosen `fa_roi_o15` → `o10` (or drop), `fa_debteq_u0.4` → `u1.5`. Drop `sh_instown_u80`. Keep margin filters. |
| **Banks & insurance** | Different unit economics — ROI/D/E don't translate. ROE is the better measure. | Use sector-specific filters. Drop `fa_debteq` entirely (banks have liabilities, not "debt"). Use `fa_roe_o15` instead of `fa_roi`. Keep trend gates. |
| **REITs** | FFO ≠ EPS; high D/E; high payout. Most fundamental filters mis-fire. | Use `sec_realestate` + `fa_div_o3` + trend gates. Drop quality filters; verify per name in `/scan`. |
| **Mature mega-cap tech / quality compounders** (HEI, TDG, MA, V, COST, etc.) | Premium multiples (P/E 30-50); >80% inst-owned; PEG inflated by mature growth | Drop `fa_pe_u25`, `fa_peg_u2`, `sh_instown_u80`. Keep ROI + margin + trend gates. |
| **Biotech (pre-revenue)** | No P/E, no FCF; pipeline-driven | Drop all valuation + profitability filters. Use market-cap floor + cash-runway proxy + trend gates. Verify per name. |

These are **starting defaults**, not fixed presets. Every relaxation must be logged in the screen file's TL;DR with the specific reason. Never loosen below the framework floor (ROI < `o10`, debt/equity > `u1.5` for non-banks/non-REITs, PEG > `u3`).

When the user names an industry not in this table, default to strict regime preset + industry filter and let the fallback chain run; document any patterns that emerge so this table can grow.

## When to run

- **Weekly** (e.g., every Sunday) on the current regime preset to refresh the watchlist.
- **After a regime change** (Δ in `MACRO/current.md`) — old screens go stale fast when Goldilocks → Stagflation.
- **Before earnings season** — discover names that fit the regime AND have an upcoming catalyst.
- **For a different angle**: `quality` for diligence, `growth` for momentum, `value` for cheap-and-good — regardless of regime.

## Style

- **Don't run `/scan` automatically on every candidate.** Discovery produces a list; the user picks names to deep-dive. Auto-running scans is wasted work.
- **Cite the live Finviz URL** so the user can re-run / tweak in their browser.
- **Note relaxations** — if you loosened a filter, say so explicitly. Don't silently weaken the framework.
- **Persistence > one-shot** — when listing candidates, sort persistent (`*`/`**`) names to the top of the table.
- **Include MACRO date** — every screen file references the MACRO scan date used for regime context (so we know which regime informed the preset).

## Process self-improvement

Per `guide/scan-rules.md` § Process self-improvement, end every `/discover` run by checking whether any of the protocol or filter codes failed. If a Finviz filter returned 0 unexpectedly, or a sort field rejected, surface a `## Process improvement suggestions` block with concrete fixes — file path + step + proposed change. Wait for user consent before editing `guide/discover-rules.md` or `.claude/commands/discover.md`.

Never propose changes to `docs/`.
