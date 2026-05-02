---
description: Audit guide/ + .claude/commands/ against docs/ knowledge base. Pull the protocol back to match the framework when it drifts. Never writes to docs/.
---

# /calibrate — protocol-vs-framework alignment audit

`/calibrate` is the integrity check between the framework knowledge base (`docs/`) and the protocol that applies it (`guide/` + `.claude/commands/`). It detects drift, proposes corrective edits to the protocol, and waits for consent. **It never edits `docs/`** — `docs/` is canonical and the only writer is `/ingest`.

The discipline: **don't deviate from the KB**. The framework grows through `/ingest`; the protocol stays aligned through `/calibrate`.

## Direction of authority

| Source of truth | Audited target |
|---|---|
| `docs/` (framework) | `guide/scan/*.md` + `guide/discover-rules.md` + `.claude/commands/*.md` |

When `docs/` and `guide/` disagree, `docs/` always wins. `guide/` is amended to match — never the reverse.

If `/calibrate` finds a `guide/` reference to something that doesn't exist in `docs/`, that's a flag — either the protocol invented something the framework hasn't sanctioned (remove from `guide/`), or the framework is genuinely missing a concept (route to `/ingest`).

## Argument forms

| Form | Example | Behavior |
|---|---|---|
| No args | `/calibrate` | Full audit across all of `docs/` + `guide/` + `.claude/commands/` |
| Doc-scoped | `/calibrate macro.md` | Audit only the protocol surfaces touched by `docs/macro.md` |
| Concept-scoped | `/calibrate "regime quadrant"` | Audit a specific term/concept's usage consistency across the protocol |

All forms are interactive: surface the drift report → wait for consent → apply only the approved fixes.

## Steps

### Step 1 — Read scope

- Read every `docs/*.md` file in scope (full content, not just headings)
- Read every `guide/scan/*.md`, `guide/discover-rules.md`, `guide/scan-rules.md`
- Read every `.claude/commands/*.md`
- Read [`docs/INGEST_LOG.md`](../../docs/INGEST_LOG.md) — recent ingest events tell you what *should* have been recalibrated and may have been missed
- Read [`guide/CALIBRATION_LOG.md`](../../guide/CALIBRATION_LOG.md) — what the last calibration found / fixed / deferred

### Step 2 — Build a concept inventory from `docs/`

For each in-scope docs/ file, extract:
- Section headings (`##`, `###`) — these are the framework's first-class concepts
- Defined terms (POC, VAH, VAL, HVN, LVN, "regime quadrant", "Goldilocks", "moat type", "Pillar 1–6", "anchored VWAP", etc.)
- Threshold rules (e.g., "ROIC < 0 = auto-reject", "VIX > 30 = contrarian buy")
- Cross-doc references (`see also` links between docs/)

This inventory is the truth set against which the protocol is checked.

### Step 3 — Detect drift across five categories

For each item in the inventory, check the protocol surfaces and flag any of:

| Category | Definition | Where it usually shows up |
|---|---|---|
| **Missing application** | A `docs/` concept exists but no `guide/` step or scan-command actually applies it | "Anchored VWAP" in `docs/vwap.md` not referenced in any scan command's Step 6 |
| **Stale terminology** | `guide/` uses an old term that `docs/` has renamed/clarified | Old "Q1/Q2/Q3/Q4" labels surviving after the docs adopted "Goldilocks/Reflation/Stagflation/Risk-Off" |
| **Contradiction** | `guide/` makes an assertion that conflicts with `docs/` | `guide/scorecard.md` says "ROIC < 5% triggers auto-reject" but `docs/long-term-investing.md` says "< 0%" |
| **Orphan reference** | `guide/` references a concept that doesn't exist in `docs/` | Protocol invents a "Pillar 7 — ESG" without the framework backing it |
| **Verbatim duplication** | `guide/` restates `docs/` content rather than linking to it | Two paragraphs of the regime-quadrant table copied into `guide/scan/protocol.md` |

### Step 4 — Surface the drift report

Output structured per category:

```
## Calibration drift report — YYYY-MM-DD

Scope: <full audit | <docs file> | "<concept>">

### Missing application (N items)
1. **<concept>** — defined in `docs/<file>.md § <section>`. No application found in:
   - guide/scan/<file>.md (expected per <reasoning>)
   - .claude/commands/<file>.md Step <N>
   - **Proposed fix:** add reference at <specific location>

### Stale terminology (N items)
1. **<old term>** → **<new term>** — `docs/<file>.md § <section>` uses <new>; protocol uses <old> in:
   - guide/scan/<file>.md (line <N>)
   - **Proposed fix:** replace_all "<old>" → "<new>" in <file>

### Contradiction (N items)
1. **<topic>** — `docs/<file>.md` says <X>; `guide/<file>.md` says <Y>
   - **Proposed fix:** update guide to match docs (`<change>`)

### Orphan reference (N items)
1. **<concept>** referenced in `guide/<file>.md` line <N>; not present in any `docs/` file
   - **Triage:** is this real framework knowledge missing from docs (route to `/ingest`) or invented protocol cruft (remove)?

### Verbatim duplication (N items)
1. `guide/<file>.md § <section>` duplicates `docs/<file>.md § <section>`
   - **Proposed fix:** replace duplicated paragraph with a link

---

Apply these fixes? (yes / no / pick which / per-category)
```

### Step 5 — Apply approved fixes

- Use `Edit` tool with `replace_all: true` for terminology fixes when the term is unambiguous
- Use `Edit` tool with `replace_all: false` for surgical changes
- Never write to `docs/` from this command. If a fix requires a doc edit, output: *"This requires `/ingest` because the docs need updating; deferring."*
- For orphan-reference items where the user picks "needs ingest", surface the recommended `/ingest` invocation and do not apply anything.

### Step 6 — Validate

```
python3 scripts/validate_links.py
```

Exits non-zero on any broken link. Fix before completing the calibration.

### Step 7 — Log the calibration

Append to `guide/CALIBRATION_LOG.md`:

```markdown
## YYYY-MM-DD — <one-line summary>

- **Scope:** full audit | <docs file> | "<concept>"
- **Drift detected:** missing=<N> · stale=<N> · contradictions=<N> · orphans=<N> · duplicates=<N>
- **Fixes applied:** <list of files edited + what changed>
- **Deferred:** <items the user said "no" to or marked "needs /ingest">
- **Recommended follow-ups:** <e.g., "Run /ingest on <concept> — surfaced as orphan but appears legitimate">
```

Newest entries at the top.

## Hard rules

1. **`/calibrate` never writes inside `docs/`.** Only `/ingest` does. If a drift item requires updating the framework knowledge base, surface it as a `/ingest` recommendation and stop — don't smuggle docs/ edits into `guide/` or vice versa.
2. **`docs/` is canonical.** When in doubt about which side is correct, the framework wins; the protocol is amended to match.
3. **Drift is detected, not corrected silently.** Always show the drift report first; apply only after consent. Per-item or per-category granularity ("apply only stale-terminology fixes; defer the rest" must work).
4. **Don't bulk-rewrite.** Surgical edits only. The fewer lines moved, the better. If the proposed fix is "rewrite this section", that's a flag — break it into smaller diffs or recommend a separate `/ingest`.
5. **Don't loosen the framework to match the protocol.** The instinct to "make the docs more flexible to fit how the guide is written" is exactly the deviation `/calibrate` is meant to prevent.

## When to run

- **After a sequence of `/ingest` events** — verify the immediate recalibration was complete; catch second-order drift the in-line ingest recalibration missed
- **Before a framework version-lock or release tag** — establishes baseline alignment
- **When two different commands seem to disagree** — usually points to drift in one of them
- **As a periodic hygiene sweep** — quarterly is reasonable; weekly is overkill

## What `/calibrate` does NOT do

- ❌ Edit `docs/` (use `/ingest`)
- ❌ Add new knowledge — only realigns existing
- ❌ Change scoring rules, thresholds, or framework definitions — those live in `docs/`
- ❌ Auto-resolve contradictions without showing them — the user always sees the choice

## Examples

### Example 1 — full audit, all green

```
/calibrate
```

Reads everything. No drift detected. Reply: *"All protocol surfaces aligned with docs/. No fixes needed. Last log entry was 2026-04-15; no `/ingest` events since then."* No log entry written (silence is the signal — same convention as the self-improvement loop).

### Example 2 — terminology drift after an ingest

Say `/ingest` recently added a "naked POC" formal definition to `docs/volume-profile.md`. The scan commands still say "untested high-volume level" loosely.

```
/calibrate
```

Detects: stale terminology in `.claude/commands/scan.md` Step 6, `guide/scan/structure.md` § ASCII visualizations. Proposes: standardize on "naked POC" with a one-line plain-English gloss for trader readability (per `style.md` § Readability). User approves. Edits applied, log written.

### Example 3 — orphan needs `/ingest`

```
/calibrate
```

Detects: `guide/scan/data.md § Step 5` references "dealer gamma threshold" with a specific number, but no `docs/` file defines what "dealer gamma" is or where the threshold comes from.

Surfaces it as: *"Orphan: 'dealer gamma threshold' in guide/scan/data.md not backed by docs/. Triage: real framework concept (run `/ingest` to add) or invented protocol cruft (remove)?"*

User says "real, ingest it" → reply: `Recommended invocation: /ingest "Add dealer-gamma section to docs/macro.md — when SPX gamma flips negative, dealers buy rallies and sell dips. Threshold: gamma < $-500M = negative regime."` Defers the protocol fix; logs the deferral.

### Example 4 — scoped to one doc

```
/calibrate volume-profile.md
```

Audits only the surfaces that apply `docs/volume-profile.md`: `.claude/commands/scan.md` Step 6 (Positional / Swing / Day-trade VP usage), `guide/scan/protocol.md` § Step 6, `guide/scan/style.md` translation table. Skips macro / fundamentals / FX / commodity / crypto guides as out of scope.

### Example 5 — duplicate content collapsed

```
/calibrate
```

Detects: `guide/scan/protocol.md § Knowledge base` reproduces three paragraphs from `docs/macro.md § Market regime framework`. Proposes: replace duplicated content with a single link to the source. User approves. Diff is small, signal is preserved, drift surface eliminated.

## After-calibrate hygiene

- Run `python3 scripts/validate_links.py` (Step 6 enforces this)
- If any items were deferred for `/ingest`, surface them in the closing reply so the user can act on them in the next session
- If the calibration produced a non-trivial set of fixes, mention which scan commands' next runs may behave slightly differently
