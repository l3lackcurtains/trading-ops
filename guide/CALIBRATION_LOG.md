# Calibration log — protocol alignment audit trail

Append-only audit trail for `/calibrate` events. Each entry records what drift was detected between the framework (`docs/`) and the protocol (`guide/` + `.claude/commands/`), what was fixed, and what was deferred.

**Newest entries at the top.** Read top-down for the recent history of how the protocol was pulled back into alignment with the framework.

**Boundary recap:** `/calibrate` audits the protocol against `docs/`. It writes to `guide/` and `.claude/commands/` only — never to `docs/`. When a drift item requires a docs change, it surfaces a `/ingest` recommendation and defers. See [`.claude/commands/calibrate.md`](../.claude/commands/calibrate.md) for the protocol.

---

## 2026-05-01 — Full audit + 4 ingests applied + protocol fixes

- **Scope:** full audit (5 docs · 13 guide · 9 commands)
- **Drift detected:** missing=6 · stale=1 · contradictions=1 · orphans=3 · duplicates=2
- **Ingests run (in order):** Q→R rename · Equity squeeze tier · Dealer gamma · CFTC COT
- **Fixes applied:** scan.md Step 6 (M1-M5: AVWAP reclaim/lose, cohort, profile shape, developing POC drift, session character) · scan-macro.md Step 4 (M6: bubble indicators with thresholds) · index-flow.md (C1: sector ETF 6-pillar reconciliation) · discover-rules.md (D1: regime-quadrant duplication collapsed to link) · scorecard.md (D2: moat-types collapsed to link)
- **Deferred:** none
- **Recommended follow-ups:** re-run /calibrate in 2 weeks after the protocol shakes down with the new docs/positioning.md anchor

---

<!-- New entries below this line, newest first. Each entry uses the format:
## YYYY-MM-DD — <one-line summary>

- **Scope:** full audit | <docs file> | "<concept>"
- **Drift detected:** missing=<N> · stale=<N> · contradictions=<N> · orphans=<N> · duplicates=<N>
- **Fixes applied:** <list of files edited + what changed>
- **Deferred:** <items the user said "no" to or marked "needs /ingest">
- **Recommended follow-ups:** <e.g., "Run /ingest on <concept> — surfaced as orphan but appears legitimate">

Empty so far — add an entry every time `/calibrate` runs and the user confirms one or more fixes (or defers items worth tracking).
-->
