---
description: 6-pillar fundamental scorecard for ticker. Updates fundamentals section in scanned/stocks/<TICKER>/current.md
---

Run a fundamentals-only scan for: **$ARGUMENTS**

Partial scan — updates only the 6-pillar scorecard section. Use when fundamentals changed (earnings print, guidance update) but the technical setup is unchanged. For a full refresh, use `/rescan $ARGUMENTS`.

Protocol in [`guide/scan/`](../../guide/scan/) — see [`scorecard.md`](../../guide/scan/scorecard.md) for the 6-pillar definitions and [`structure.md`](../../guide/scan/structure.md) for the section format.

## Steps

1. **Verify `scanned/stocks/$ARGUMENTS/current.md` exists.** If not, tell the user to run `/scan $ARGUMENTS` first.

2. **Read-before-scan** per `protocol.md` — capture prior 6-pillar score + auto-reject flags.

3. **Pull fundamentals data** per `data.md`:
   - Finviz quote page (one WebFetch — covers most pillars)
   - Stockanalysis for FCF / Net Debt / EBITDA detail
   - 13F holders chain (WhaleWisdom → HedgeFollow → Fintel) for Pillar 6
   - Dataroma for superinvestor coverage
   - Insider Form 4 (OpenInsider → Finviz insider page)

4. **Re-run 6-pillar** per [`scorecard.md`](../../guide/scan/scorecard.md):
   - Quality (ROIC) / Growth (rev/EPS) / Valuation (P/S, EV/EBIT, FCF yield) / Balance Sheet (Net Debt/EBITDA) / Capital Allocation / Smart Money
   - Score each PASS / FAIL / NEUTRAL with explicit numbers
   - Aggregate /6; check auto-reject flags

5. **Edit only the 6-Pillar Scorecard section** of `scanned/stocks/$ARGUMENTS/current.md`. Leave Technical Read / Trade plan / Coverage tier untouched unless the score change forces a tier transition (Pos S → B requires the auto-reject flags to clear, etc.).

6. **If the Pos tier changes** because the score change is material:
   - Update the `**Coverage tier:**` header line
   - Append a row to `scanned/INDEX.md` § Coverage changes — last 30 days
   - Per `tiers.md` § Tier-change protocol

7. **No archive rotation, no rescan rotation** — this is an in-place update. The full audit trail comes from `/rescan` only.

8. **Update INDEX.md** master coverage table row's Score column if it changed.
