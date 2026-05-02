---
description: Ingest new framework knowledge into docs/ and recalibrate guide/. The ONLY command authorized to write inside docs/.
---

# /ingest — knowledge intake + protocol recalibration

`/ingest <source>` is the single authorized writer inside `docs/`. Every other command, freeform action, scan, and the self-improvement loop treats `docs/` as read-only. This command is the carve-out.

## What it does

1. Parse the source — file path / URL / inline text or idea
2. Read or fetch the content
3. Classify the knowledge — new framework doc · extension of existing doc · pure protocol/data-source change (which doesn't belong in docs/)
4. Propose a write plan — what gets created/edited in `docs/`, what gets recalibrated in `guide/`, what cross-references update
5. Apply only after user consent
6. Run link validation
7. Append an entry to `docs/INGEST_LOG.md`

## Argument forms

| Form | Example | Behavior |
|---|---|---|
| File path | `/ingest input/spotgamma-2026.pdf` | Read local file (PDF, MD, TXT). For PDFs, use the Read tool's `pages` param for files > 10 pages. |
| URL | `/ingest https://example.com/paper` | WebFetch the URL. Use chrome-devtools for dynamic pages. |
| Inline text or idea | `/ingest "Add dealer-positioning section to macro.md — when SPX gamma flips negative, dealers buy rallies and sell dips. Source: Nomura/McElligott."` | The argument itself is the knowledge to ingest |
| No args | `/ingest` | Show help + last 5 entries from `docs/INGEST_LOG.md` |

## Steps

### Step 1 — Parse + classify the source

Determine:
- **Source type** — file / URL / inline
- **Content domain** — macro · long-term-investing · technical (VWAP/VP) · options/dealer flow · news-trading · new asset class · new tool/methodology
- **Scope** — new doc · append to existing doc · cross-cutting (touches multiple docs)
- **Where it lands** — does this *create* knowledge (docs/), or only change *how we apply* it (guide/)? If the latter, this is a self-improvement-loop change, not an `/ingest`. Don't write to docs/ if the change is purely procedural.

If the classification is ambiguous, ask the user before continuing.

### Step 2 — Read or fetch the content

- File: `Read` tool. PDFs > 10 pages need `pages` param.
- URL: `WebFetch`. If the page is JS-heavy or paywalled, escalate to chrome-devtools or ask the user for an alternative source.
- Inline: the argument is the content. If it's a single sentence, ask for the supporting reasoning before writing.

### Step 3 — Write plan (REQUIRED before any edit)

Output a write plan in this format and **wait for user consent**:

```
## Ingest plan — <one-line title>

Source: <file / URL / "inline idea">
Domain: <macro / long-term-investing / technical / options-flow / new asset class / ...>

docs/ changes:
  - <NEW | APPEND>: docs/<filename>.md
    - <NEW only> Outline:
        1. <section heading>
        2. <section heading>
        3. ...
    - <APPEND only> Target section: § <section name>
    - Approximate size: <N lines>

guide/ recalibration:
  - guide/scan/<file>.md § <section> — <what changes>
  - <repeat per affected file>

cross-references:
  - STRUCTURE.md — <update file map / boundary table>
  - README.md — <if a new "Authoritative protocol" entry is needed>
  - other docs/ files — <see-also links to add>

risk flags:
  - <conflict with existing doc? supersede vs augment?>
  - <single source vs multiple? freshness?>
  - <speculative vs validated?>

Apply this plan? (yes / no / edit)
```

If the user says "edit", iterate the plan until aligned.

### Step 4 — Write to docs/

This is the only step in the entire codebase authorized to write inside `docs/`.

- New file: `Write` tool. Use the same heading + table-of-contents conventions as existing docs (see `macro.md`, `long-term-investing.md`).
- Edits/appends: `Edit` tool. Preserve existing structure — never rewrite a section without showing the diff first.
- Use the user's exact source attributions; cite externally with markdown links.
- Never auto-translate the user's framework choices into different terminology.

### Step 5 — Recalibrate guide/

The guide is what applies the framework. When the framework changes, the guide must follow. Common recalibration patterns:

| Knowledge type | Likely guide changes |
|---|---|
| New asset class | new `guide/scan/<asset-class>-flow.md` · update `.claude/commands/scan.md` Step 1 (asset detection) · update `tiers.md` if tradeable |
| New macro indicator or regime concept | update `guide/scan/data.md` § macro · update `.claude/commands/scan-macro.md` Step 3 source list |
| New 6-pillar lens or moat type | update `guide/scan/scorecard.md` |
| New options/flow source or signal | update `guide/scan/data.md` § flow · update relevant `<asset-class>-flow.md` |
| New analytical tool (VWAP variant, indicator, model) | update `guide/scan/protocol.md` § Step 6 if it's part of the technical read |
| New scoring rule or gate | update `guide/scan/scorecard.md` + `tiers.md` |
| New terminology | update `guide/scan/style.md` § Tone (or Readability translation table if it replaces a jargon phrase) |

Always show the diff per file. **Wait for user consent** before applying guide/ edits.

### Step 6 — Cross-references

After the write:
- If a new doc/ file was created → add it to `STRUCTURE.md` § file map
- If the new doc is referenced from a scan path → add it to `README.md` § Authoritative protocols
- Add `see also` links between the new doc and adjacent docs (e.g., a new options-flow doc should link to `macro.md` § Market regime framework if relevant)

### Step 7 — Validate

```
python3 scripts/validate_links.py
```

Exits non-zero on any broken link. Fix before completing the ingest.

### Step 8 — Log the ingest

Append to `docs/INGEST_LOG.md`:

```markdown
## YYYY-MM-DD — <one-line title>

- **Source:** <file path / URL / "inline idea">
- **Files written:** docs/<file>.md (NEW | APPEND, +N lines)
- **Guide recalibration:** <list of guide/ files edited>
- **Why:** <user's stated motivation, one sentence>
- **Risk flags:** <any conflicts, supersessions, single-source caveats>
```

Newest entries at the top. This is the audit trail for "how the framework evolved."

## Hard rules

1. **`/ingest` is the ONLY entry point that can write inside `docs/`.** Other commands, freeform sessions, agents, and the self-improvement loop cannot edit `docs/`. If they need a docs/ change, they must surface it as an `/ingest` proposal — never write directly.
2. **`docs/` writes always require user consent.** Even inside `/ingest`. Show the write plan first; apply only on confirmation.
3. **Guide-only edits don't need `/ingest`.** If the change is purely protocol mechanics (better source priority, tighter scan step, terminology cleanup with no new framework concept), use the self-improvement loop in `guide/scan/style.md` directly. `/ingest` is for *new framework knowledge*, not procedural tweaks.
4. **One concept per ingest.** If the source covers multiple distinct concepts, run `/ingest` once per concept so each gets its own audit-log entry.
5. **Don't silently supersede.** If the new content contradicts an existing doc, surface the conflict explicitly and ask the user: supersede / augment / reject. Never auto-resolve a framework conflict.
6. **No orphan files.** Every new doc in `docs/` must be linked from at least one of: `STRUCTURE.md`, `README.md`, or another doc's "see also" section.

## Failure modes

- **Source unreachable** (404, paywall, auth wall) → don't proceed. Tell the user, ask for an alternative.
- **Inline text too vague** ("add something about options pinning") → ask for the framework specifics before writing. Don't fabricate a doc from a one-liner.
- **Source contradicts an existing doc** → surface the conflict; let the user decide.
- **Source is a screenshot/image** → describe what's needed in text form first; don't OCR-and-infer silently.
- **Source is a competitor's framework with different terminology** → ask whether to translate to our vocabulary or keep the source's verbatim.

## Examples

### Example 1 — PDF whitepaper

```
/ingest input/dealer-gamma-positioning-2026.pdf
```

Reads PDF → classifies as macro/options-flow extension → proposes APPEND to `docs/macro.md` § Liquidity (new sub-section: "Dealer gamma positioning") → proposes update to `guide/scan/index-flow.md` § Tier B with new gamma sources → confirms with user → writes both → logs.

### Example 2 — Article URL

```
/ingest https://www.fidenzamacro.com/p/the-four-quadrant-global-macro-framework
```

WebFetches → recognizes existing `docs/macro.md § Market regime framework` already covers the 2×2 → proposes minor APPEND with concrete examples (not a new doc) → confirms → writes → logs.

### Example 3 — Inline idea (new section)

```
/ingest "When SPX dealer gamma flips negative, dealers become buyers on rallies and sellers on dips, accelerating moves. Threshold rule: gamma < $-500M = negative regime. Source: Nomura/McElligott daily, Apr 2026."
```

Treats the argument as the source → proposes new sub-section in `docs/macro.md` (not a separate file — too small) → proposes update to `guide/scan/index-flow.md` § GAMMA section adding the threshold rule → confirms → writes → logs.

### Example 4 — New asset class

```
/ingest "We're adding rates/futures scans. Need docs/rates.md covering eurodollar curve, OIS spreads, MOVE index, and the inflation breakeven cross-references. Source: my own notes from desk experience + BIS bulletin."
```

Proposes new `docs/rates.md` with detailed outline → proposes new `guide/scan/rates-flow.md` (asset-class flow doc) → proposes update to `.claude/commands/scan.md` Step 1 (asset detection adds rates path) → proposes STRUCTURE.md update → confirms each file → writes → logs.

### Example 5 — Pure procedural change (rejected — not for /ingest)

```
/ingest "Use Yahoo before Finviz when both have the next-earnings date."
```

This is a source-priority tweak, no new framework concept. Reply: "This is a guide/ procedural change, not new framework knowledge. Use the self-improvement loop in `guide/scan/style.md` to update `data.md` § Priority order directly. /ingest is for docs/ changes."

## After-ingest hygiene

- Run `python3 scripts/validate_links.py` (Step 7 enforces this)
- Note the new doc in your next reply context if it changes how upcoming commands work
- If the ingest added a new asset class, the user may want to run a fresh `/scan` against it to validate the protocol round-trip
