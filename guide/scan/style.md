# Style — tone, citation, scope, self-improvement

> Part of the [scan protocol](../scan-rules.md). See also: [structure](structure.md), [data](data.md).

---

## Tone

- Direct, framework-aligned. Use the docs' exact terminology:
  - "Goldilocks", "Reflation", "Stagflation", "Risk-Off" (the four growth × inflation regime quadrants — refer to as R1/R2/R3/R4 or by name; the Q-prefix is reserved for calendar quarters)
- No hedging language ("could potentially maybe") — give a verdict
- If the answer is "wait", say "wait" — that IS a position
- Numbers, not adjectives

---

## What never goes in

- Generic boilerplate copied from `docs/` — link to the doc instead
- Speculative price predictions without a framework anchor
- Single-source unverified data points — require ≥ 2 sources for any number that drives the verdict (with the [freshness exception](data.md#freshness-first-strategy-free-sources-only-no-premium-services))
- Emojis (unless the user explicitly requests them)
- **Internal scaffolding** — see [Readability](#readability--write-for-the-trader-not-the-framework) for the full rule

---

## Readability — write for the trader, not the framework

The audience for every saved `scanned/**/current.md` is a **medium-skilled trader**, not the framework author. Three hard rules:

### 1. No internal references inside the saved file

Never name internal tooling or protocol files in the body of a saved scan. The reader doesn't have them, doesn't need them, and they rot when files move.

**Forbidden inside the saved file:**
- Script names: `fetch_quote.py`, `fetch_ohlc.py`, `fetch_sec.py`, `fetch_max_pain.py`, `fetch_news.py`, `fetch_macro.py`, `fetch_crypto.py`, `regen_index.py`, `prune_archive.py`, `validate_*.py`
- Internal protocol-path references: `per data.md § Step 8`, `per scorecard.md`, `per protocol.md`, `per CANSLIM rule`, `per guide/scan/structure.md`
- Internal-section labels: `(8-point checklist)`, `Stage-2 ROIC fail`, `Pillar 2 + Pillar 6 confluence`, `R2 lens`, `auto-reject gate fires`, `XBRL` (use "from filings" / "company-reported" instead)
- Window/method labels for our scripts: `fetch_sec.py window`, `local fetch_max_pain.py output`, `yfinance via fetch_quote.py`

**Allowed:** public source URLs (Yahoo, SEC EDGAR, ChartExchange, BLS, Atlanta Fed, FOMC, Circle IR, etc.). Cite by canonical name + link, not by the script that scraped them.

### 2. Plain language over framework jargon

Translate framework-internal phrases into the underlying trading observation. The trader knows VWAP, POC, ATR, RSI, EMA, R:R, P/E, EPS, max pain, gamma, days-to-cover, SI, FTD. They do not need or want the framework's pillar/rule/gate vocabulary.

**Replace:**

| Framework phrase | Plain rewrite |
|---|---|
| "Auto-reject ROIC fires; Pos S locked" | "Returns negative on invested capital — no long-term position" |
| "Pillar 2 + Pillar 6 confluence rule (CANSLIM-I)" | "Both earnings momentum AND institutional accumulation needed for top-pick" |
| "Stage-2 ROIC fail" | "Negative ROIC" |
| "R2 lens / regime gating" | "In a Reflation regime, we OW cyclicals + UW bonds" |
| "Naked POC" | "Untested high-volume price level" |
| "VWAP-band rejection" / "vwap-band-fade" | "Sell rallies into the day's average price" |
| "fired-correct / invalidated / stale" | (these are audit-log values, not scan-body terms — keep them in the audit log only) |
| "ROIC computed from XBRL company-facts" | "Returns from company filings" |

Pattern slugs (`earnings-binary-twosided`, `vwap-band-rejection`, etc.) belong inside the *Action verdict structured fields* (`*(pattern: \`<slug>\`)*`) where they are machine-readable for hit-rate aggregation. They do **not** belong in narrative paragraphs.

### 3. No duplication — every fact lives in exactly one place

Each fact has one canonical home in the snapshot. Restating the same finding in TL;DR + scorecard table + auto-reject-gate table + verdict line is noise, not emphasis.

**Canonical homes:**

| Fact | Lives in (only) |
|---|---|
| Auto-reject finding (negative ROIC, etc.) | Pillar 1 row of the scorecard, plus Action verb if it gates the horizon |
| Earnings date + timing | Vitals (`Next catalyst`) and Earnings setup section. Not also TL;DR + verdict-per-horizon + scenario tree header. |
| Tier letters (Pos / Swing / Day) | The `**Coverage tier:**` line in vitals, and the Verdict-per-horizon table. The Action verbs imply them; don't restate. |
| Aggregate score (X/6) | Scorecard summary line only |
| Trade entries / stops / targets | Trade table only. The price ladder shows them positionally; do not restate the numbers in narrative. |
| Regime quadrant | Vitals one-liner + Regime-fit table. Not the technical read, not the TL;DR. |

If a fact is already stated, the next reference cross-links to its location instead of repeating.

### Pre-save filter

Before writing the snapshot, walk the draft once with these three filters:

1. Search for `fetch_*` and any `*.md` framework path → strip or replace with a public URL.
2. Search for the framework-jargon phrases listed above → rewrite as the underlying trading observation.
3. Search for any number or finding that appears twice → keep the most actionable instance, delete the rest.

---

## Source citation

- Every numeric claim that drives the verdict must be cited
- Live data (price, MAs, F&G, VIX) cited inline where used
- All sources listed at file bottom under `## Sources` as markdown links

---

## Cross-references

- Stock scans MUST reference current `MACRO/current.md` regime by name (Goldilocks / Reflation / Stagflation / Risk-Off)
- Stock scans MUST note regime fit (favored / hostile / neutral) with one-line reasoning
- If `MACRO/current.md` is older than 7 days when running a stock scan, **warn the user** and offer to run `/scan-macro` first

---

## Scope separation — info flows down, not up

The reference direction is asymmetric:

- **Stock / index / instrument scans use MACRO as the lens.** Cite the regime, key gauges, catalysts — that's the whole point of having a macro doc.
- **MACRO does not derive its read from individual stock scans.** The regime read comes from index/breadth/cross-asset evidence. Single names don't justify a macro pattern call.

Use judgment on what's actually appropriate inside each scan:
- A MACRO scan can mention specific names where they genuinely move the tape — e.g., "NVDA / Mag-7 earnings tail" in the catalyst list, "OpenAI revenue report broke Russell + NDX" as a market-event reference. That's reporting facts about index drivers, not borrowing a single-stock's pattern as macro evidence.
- A MACRO scan should NOT use single-name analogies for index pattern calls ("same setup as CRCL/NIO") — that inverts the hierarchy.
- Sector / asset preference lists ("favored" / "avoid") generally name categories, not tickers as exemplars — but a benchmark ETF for the category (GLD for gold, TLT for long bonds, GDX for miners) is fine when it's the canonical proxy.
- A stock scan can cite cohort peers when describing relative behavior (NDX vs SPX divergence in an SPX scan, GDX in a GLD scan, EUR/JPY context in an EUR/USD scan) — that's correlation evidence.

**Why the asymmetry:** Macro is the lens; everything else applies it. If individual names back-flow into MACRO, the regime read becomes circular — derived from things the regime is supposed to explain. Keep the dependency graph one-way.

---

## Process self-improvement

The scan protocol itself evolves. When running a command, if you encounter a problem with **our process** (not with market data — that's the scan's content), surface it.

### What counts as a process problem

**Bugs** (broken or incorrect):
- **Broken link/URL** — a WebFetch returns 404, redirect to login, or wrong page
- **Wrong filter code** — a Finviz filter you used returned 0 results or rejected the query
- **Missing data source** — the framework requires a fact the listed sources don't provide
- **Ambiguous step** — the command instruction is open to two readings and you had to guess
- **Outdated reference** — a `docs/` file points to a moved/renamed external resource
- **Missing edge case** — the command doesn't say what to do when (e.g.) the ticker has no options chain, or is pre-revenue, or is dual-listed
- **Source-priority gap** — the priority chain ([data](data.md)) needs to be updated

**Inefficiencies** (works but wastes effort):
- **Duplicate fetches for the same fact** — pulling next-earnings date from both Finviz and Yahoo. Violates the no-duplication rule.
- **Sequential fetches that should be parallel** — when independent data fetches are issued one at a time instead of as parallel WebFetch calls.
- **Re-fetched in same scan** — a page was fetched, then re-fetched later for another fact. Should have been one comprehensive fetch.
- **Over-fetching for stale-tolerant data** — for facts that don't change minute-to-minute (P/E, ROIC, sector), querying multiple sources for "freshness" is wasted; one source suffices.

### The freshness exception (don't conflate with duplication)

**Single fact, fixed value** (P/E, ROE, market cap, sector, EPS estimate, next earnings date) → **ONE source, no parallel duplication.** Picking the right source per [data](data.md) § Priority order is enough.

**Single fact, freshness-sensitive value** (short interest, dark pool %, FTD, borrow fee) → **MULTIPLE sources in parallel is correct,** because each may have a different "as of" date and we pick the freshest. This is NOT duplication — it's a deliberate freshness check. See [data](data.md) § Freshness-first strategy.

The optimization test:
- "Did I fetch the same number from two sources?" → if the number is fixed, that's waste; if it's freshness-sensitive, that's correct.
- "Did I fetch all the freshness-sensitive sources in parallel?" → if not, that's missed parallelization.

### How to surface it

At the end of the scan output (after the saved file path is reported, separate from the scan content itself), add a section:

```markdown
---

## Process improvement suggestions

While running this scan I noticed:

1. **<short title>** — <one-line description>
   - Type: `bug` / `optimization` / `clarification`
   - Where: `<file path>` step <N>
   - Current: <what happens now>
   - Suggested fix: <concrete change>
   - Impact: <what this enables / fixes / saves>

(repeat for each issue)

Apply these to the guide / commands? (yes / no / pick which)
```

### Rules

- **Do NOT auto-apply.** Wait for user consent before editing `guide/` or `.claude/commands/`.
- **Be specific.** "The Finviz filter `fa_opmargin_o15` returned 0 results because the correct prefix is `fa_opermargin`" beats "Finviz filter didn't work."
- **Cite the file path and step number** so the user can verify before approving.
- **Tag each suggestion with a type**: `bug` / `optimization` / `clarification`.
- **Don't surface non-issues.** If the scan ran clean, don't add the section. The signal is broken when every scan ends with a "suggestions" block.
- **Don't surface market issues.** "Stock fell 5% today" is not a process problem.
- **Don't propose duplication just to be safe** — if a fact is already cleanly sourced, don't suggest a "backup source." Suggesting MORE fetches is rarely an improvement.
- **Don't propose dropping freshness fetches** — for stale-prone data (SI, dark pool, FTD), parallel fetches across sources to find the freshest are correct.
- **Suggestions are about `guide/` and `.claude/commands/`** — never about `docs/` (read-only knowledge base). If the framework itself seems incomplete, mention it but flag it as "framework question, not protocol fix" — the user decides whether to update `docs/`.

The audit value of these suggestions compounds: each broken link caught is one less wasted fetch on the next scan; each wrong filter code fixed is one less bad screen; each duplicate fetch removed shaves seconds off every future run. The protocol becomes anti-fragile.
