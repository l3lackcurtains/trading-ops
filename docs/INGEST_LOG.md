# Ingest log — framework knowledge audit trail

This file is the append-only audit trail for `docs/` evolution. Every change to the `docs/` knowledge base goes through `/ingest` and leaves an entry here.

**Newest entries at the top.** Read top-down for the recent history of how the framework changed.

**Boundary recap:** `/ingest` is the only authorized writer inside `docs/`. All other commands, freeform actions, agents, and the self-improvement loop treat `docs/` as read-only. See [`.claude/commands/ingest.md`](../.claude/commands/ingest.md) for the protocol.

---

## 2026-05-01 — CFTC Commitments of Traders (appended to positioning.md)

- **Source:** "inline idea" — user feedback (3rd of 4 ingests for cross-asset positioning umbrella)
- **Files written:** docs/positioning.md (APPEND, +~40 lines), guide/scan/fx-flow.md (EDIT — § Why COT is the prime FX signal collapsed to link), guide/scan/commodity-flow.md (EDIT — § Why commodity flow looks different collapsed to link on COT bullet)
- **Guide recalibration:** fx-flow.md "Why COT is the prime FX signal" conceptual block (trader-category definitions) collapsed to a one-line docs link with FX-specific framing preserved; commodity-flow.md COT bullet rewritten to anchor on docs/positioning.md while keeping the commodity-specific commercial-vs-non-commercial read; per-scan reading procedure (Tier A/B sources, lag) preserved verbatim in both flow docs
- **Why:** COT trader-category definitions (non-commercial / commercial / spread / non-reportable) and standard reads (3-yr extremes, ΔWoW) are cross-asset framework concepts duplicated across fx-flow.md and commodity-flow.md. Move definitions to docs/positioning.md so the protocol carries only the asset-class-specific application.
- **Risk flags:** none — content moved, not changed; both flow docs link to the same canonical definitions

---

## 2026-05-01 — Dealer gamma exposure (appended to positioning.md)

- **Source:** "inline idea" — user feedback (2nd of 4 ingests for cross-asset positioning umbrella)
- **Files written:** docs/positioning.md (APPEND, +~50 lines), guide/scan/index-flow.md (EDIT — § Why gamma matters most collapsed to link)
- **Guide recalibration:** index-flow.md "Why gamma matters most" conceptual block (positive/negative regime, walls, vol trigger definitions) collapsed to a one-line docs link; Tier A/B capture procedures, source URLs, and squeeze-tiering composite (operational) preserved verbatim
- **Why:** The dealer-gamma conceptual definitions were duplicated in the protocol where the docs should be the source of truth. Move definitions to docs/positioning.md so the protocol carries only the per-scan reading procedure.
- **Risk flags:** none — content moved, not changed; index-flow.md still references the same gamma concepts via link

---

## 2026-05-01 — Equity squeeze tier composite (positioning.md created)

- **Source:** "inline idea" — user feedback (umbrella positioning doc)
- **Files written:** docs/positioning.md (NEW, ~50 lines), guide/scan/data.md (EDIT — squeeze tiering rules collapsed to link), STRUCTURE.md (EDIT — added positioning.md to file map), README.md (EDIT — added positioning.md to docs layer + folder layout)
- **Guide recalibration:** data.md § Squeeze tiering rules collapsed from 4-line threshold table to one-line link to positioning.md § Equity squeeze tier; per-scan reading procedure preserved
- **Why:** Squeeze-tier definitions were duplicated between protocol (data.md) and the implicit framework knowledge. Move the canonical definition to docs/positioning.md so the protocol can link rather than restate; positions positioning.md as the umbrella anchor for upcoming dealer-gamma + CFTC COT sections.
- **Risk flags:** none — content moved, not changed; data.md still cites the same thresholds via link

---

## 2026-05-01 — Rename quadrant labels Q1–Q4 → R1–R4

- **Source:** "inline idea" — user feedback
- **Files written:** docs/macro.md (EDIT, terminology rename), guide/scan/style.md (EDIT), guide/discover-rules.md (EDIT, preset keys), .claude/commands/discover.md (EDIT), scanned/MACRO/current.md (EDIT)
- **Guide recalibration:** style.md Q-prefix rule updated; discover.md preset arg-tokens renamed; discover-rules.md preset section headings + arg-tokens renamed
- **Why:** Q-prefix collided with calendar-quarter notation (Q1 / Q2 / etc). R = Regime. Eliminates ambiguity instead of carving exceptions.
- **Risk flags:** none — pure terminology rename, no semantic change

---

## 2026-05-01 — System bootstrap (this file created)

- **Source:** N/A — initial bootstrap of the `/ingest` audit-log file
- **Files written:** `docs/INGEST_LOG.md` (NEW, ~20 lines)
- **Guide recalibration:** none (this entry is the seed; the command itself is in `.claude/commands/ingest.md`)
- **Why:** Establish the audit trail. From this point forward, only `/ingest` writes inside `docs/`.
- **Risk flags:** none — bootstrap entry only

---

<!-- New entries below this line, newest first. Each entry uses the format:
## YYYY-MM-DD — <one-line title>

- **Source:** <file path / URL / "inline idea">
- **Files written:** docs/<file>.md (NEW | APPEND, +N lines)
- **Guide recalibration:** <list of guide/ files edited>
- **Why:** <user's stated motivation, one sentence>
- **Risk flags:** <any conflicts, supersessions, single-source caveats>
-->
