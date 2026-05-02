# 6-Pillar scoring conventions — gates, tags, high-conviction rules

> Part of the [scan protocol](../scan-rules.md). See also: [tiers](tiers.md), [data](data.md), [style](style.md).
>
> This file is the authoritative source for the **6-pillar definitions** and the scan-output conventions layered on top — what fields to render, how to gate, and when to upgrade to high-conviction. Background context on long-term investing (3 stages, moat types, capital allocation, P/E vs growth, income-statement alignment) lives in [`../../docs/long-term-investing.md`](../../docs/long-term-investing.md).

---

## Pillar 0 — Qualitative gate (run BEFORE the 6-pillar scorecard)

A one-line check before any quantitative work. Mirrors Stage 1 of the [3-stages of stock research](../../docs/long-term-investing.md#three-stages-of-stock-research) — qualitatives first.

**Field in the snapshot:**

```markdown
**Pillar 0 — Business:** <one sentence: what the company does and how it makes money>
```

**Gate rule:**
- If you cannot write that sentence after the data pull, mark **Pos S — don't understand business** and stop the scan. No 6-pillar, no technical read, no trade plan.
- Swing/Day horizons can still be scored if a binary catalyst exists (earnings, FDA, etc.) — Stage 1 failure scopes Positional only.

**Why:** A 6-pillar scorecard for a business you don't understand is theatre. The gate forces you to articulate the model before pretending to value it.

---

## Pillar 1 — Quality with moat-type tag

Pillar 1 currently scores Quality from margins + ROIC. Add a single-field moat classification that names *why* the margin holds (or why it doesn't).

**Field in the snapshot Pillar 1 row:**

```markdown
| 1 | Quality | <margins + ROIC numbers>; **Moat: brand / network / switching / cost / IP / regulatory / premium / none** | PASS / NEUTRAL / FAIL |
```

**The 7 moat types**

Tags: `brand` / `network` / `switching` / `cost` / `IP` / `regulatory` / `premium` / `none`. Definitions in [`docs/long-term-investing.md` § Economic moat and profit margins](../../docs/long-term-investing.md#economic-moat-and-profit-margins).

**Gate rule:**
- `Moat: none` + Pillar 1 FAIL → reinforces the auto-reject; no margin recovery without structural change.
- `Moat: brand/network/switching/cost/IP/regulatory/premium` + Pillar 1 NEUTRAL → margin can recover; watchlist tier valid.

**Why:** Two companies with -3% gross margin can have very different futures — one is pre-scale with a network moat building, the other is commoditized with no defense. The tag forces that distinction.

---

## High-conviction confirmation rule (Pillar 2 + Pillar 6 confluence)

A scan reaches **Positional T (Top Pick)** only when BOTH of these are true alongside a clean 6-pillar score:

1. **3 consecutive quarters** of revenue growth ≥ 20–25% YoY *and* EPS growth ≥ 25% YoY
2. **Institutional holders increasing** in the latest 13F (count growing, not just dollar-weighted)

This is the CANSLIM "I" rule. The conventions above (3 consecutive Q growth ≥ 20–25% YoY rev + 25% YoY EPS, 13F holder count rising MRQ, and the 8-point earnings checklist row 6 "institutional holders increased in latest 13F?") are authoritative here — this file is the source of truth.

**How to apply in the scan:**

| Pillar 2 + Pillar 6 reading | Positional tier ceiling |
|---|---|
| 3 consecutive Q growth (rev + EPS ≥ thresholds) AND 13F holder count rising | Eligible for **T** if other Pillars + regime support |
| 3 consecutive Q growth, but 13F holder count flat or falling | Cap at **W** — wait for institutional confirmation |
| Mixed Q growth (1–2 quarters), 13F rising | Cap at **W** — wait for the third confirmation |
| Decelerating growth OR 13F count falling MRQ | Cap at **B** regardless of other Pillars |
| Auto-reject Pillar 1 numbers (negative ROIC, negative gross margin) | **S** — confirmation rule doesn't override Stage 2 gate |

**Why both gates:** Earnings momentum without institutional confirmation is retail-driven and unstable; institutional accumulation without earnings backing is value-trap territory. The framework requires both before sizing positionally.

---

## Smart Money — one-sentence verdict convention

Pillar 6 used to render as 4 sub-bullets (13F count, Dataroma, insider Form 4, inst transactions). Collapse to **one verdict sentence** with the data inline, and let the Pillar 6 row of the scorecard table carry the numbers.

**Old (verbose):**
```
- Inst ownership 45.32%, +1.81% net inst transactions
- 13F holders -23.34% MRQ on Fintel
- No superinvestor on Dataroma
- Insider transactions -0.08% (no recent buying)
```

**New (one sentence):**
```
Inst flow soft (+1.81% trans on falling holder count -23.34% MRQ); zero superinvestor; no recent insider buys → **NEUTRAL**, not a long-side confluence.
```

The numbers go in the scorecard table row; the *read* goes in one sentence. Restating the same data four ways adds no signal.

---

## P/E vs growth check (Pillar 3 lens — optional one-line)

When P/E is the dominant valuation read, add one sentence to Pillar 3 testing whether the multiple is consistent with credible growth. Rough directional rule (per [`../../docs/long-term-investing.md#reasonable-pe-ratio-based-on-growth`](../../docs/long-term-investing.md#reasonable-pe-ratio-based-on-growth)):

| Earnings growth | Justifiable P/E direction |
|---|---|
| Slow / mature growers | Ordinary multiples (12–18) |
| ~25% EPS growth | Meaningfully higher (25–35) |
| ~35%+ growth | P/E in that neighborhood (PEG ~1) |

Quality and predictability tilt up; cyclicality and concentration tilt down at the same growth rate. Use this when scoring borderline Pillar 3 verdicts.

---

## Income statement alignment check (Pillars 1 + 2 lens)

When reading Pillars 1 and 2 together, ask whether revenue, gross profit, operating income, net income, and EPS are all moving the **same direction**. Misalignment is the signal.

| Pattern | Read |
|---|---|
| All five up at similar magnitude | Healthy growth — pillars likely PASS together |
| Revenue up, gross profit flat | Pricing under pressure or input-cost squeeze — Pillar 1 risk |
| Revenue up, operating income flat | Opex outpacing growth — efficiency problem |
| Revenue up, net income down | Below-the-line drag (interest, tax, dilution) |
| Revenue up, EPS flat | Dilution funding the growth — Pillar 5 red flag |

Reference: [`../../docs/long-term-investing.md#every-income-statement-tells-a-story`](../../docs/long-term-investing.md#every-income-statement-tells-a-story).

---

## Capital allocation 5-question check (Pillar 5 lens — optional)

When scoring Pillar 5, run through these 5 yes/no/N/A questions for sharper output (per [`../../docs/long-term-investing.md#how-great-management-compounds-wealth`](../../docs/long-term-investing.md#how-great-management-compounds-wealth)):

1. Can the company reinvest at attractive returns? (ROIC > WACC)
2. Is the balance sheet adequately strong?
3. Are buybacks executed at sensible valuations?
4. Are dividends appropriate for the business stage?
5. Are acquisitions strategic and disciplined?

Three or more "no" → Pillar 5 FAIL regardless of headline buyback yield. Three or more "yes" with no "no" → PASS.

---

## What NOT to add to the 6-pillar output

- Do not list every Pillar 6 sub-source separately — the table row carries the data, the one-sentence verdict carries the read
- Do not write the same number twice (e.g., gross margin as both a Pillar 1 line item AND a separate "margin commentary" line)
- Do not auto-reject on a single soft signal (e.g., one quarter of decel) — auto-reject is Pillar 1 numerics only
- Do not write capital-allocation paragraphs when the company has no FCF — the question collapses to "is the balance sheet still funded?" (Pillar 4)
