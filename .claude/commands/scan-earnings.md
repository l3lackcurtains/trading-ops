---
description: Earnings setup analysis for ticker. 8-point checklist + pre-print read.
---

Run an earnings-only scan for: **$ARGUMENTS**

Partial scan — updates only the Earnings setup section. Use during the 7–14 days before a print, or immediately post-print to record the reaction.

Protocol in [`guide/scan/`](../../guide/scan/) — see [`structure.md`](../../guide/scan/structure.md) for the section format and [`data.md`](../../guide/scan/data.md) for sourcing.

## Steps

1. **Verify `scanned/stocks/$ARGUMENTS/current.md` exists.** If not, tell the user to run `/scan $ARGUMENTS` first.

2. **Read-before-scan** per `protocol.md` — capture prior earnings setup notes if any (especially the 8-point checklist if it was already partly filled).

3. **Pull earnings data** per `data.md`:
   - Finviz quote page (next earnings date, EPS estimate)
   - Seeking Alpha for transcripts, guidance, capital allocation tone (`seekingalpha.com/symbol/$ARGUMENTS/earnings`)
   - WebSearch for analyst-revision direction post-prior-print, whisper number, post-print 1–3 day reaction history
   - ChartExchange for max-pain magnetic interplay around the print date

4. **Run 8-point pre-print checklist:**
   1. EPS ≥ 25% YoY accelerating
   2. Revenue ≥ 25% YoY 3rd consecutive quarter
   3. FCF up alongside net income
   4. Margins expanding or holding
   5. Mgmt raised guidance
   6. Inst holders increased (per Pillar 6 from prior `current.md` or fresh fetch)
   7. Inst ownership < 70% (room for marginal buyer)
   8. Stock reaction +1–3 days post

   Status: ✅ confirmed, ⚠ warning, ❌ fail, ❓ TBD pending print.

5. **Max-pain interplay note** — pull weekly + monthly max pain (`chartexchange.com/symbol/<EX>-$ARGUMENTS/optionchain/summary/`). State whether the magnetic level pulls into or away from the print, and the post-print magnet for the following month.

6. **Pre-print read** — synthesize: Constructive / Neutral / Bearish into the print. Cite which checklist items drive the read.

7. **Edit only the Earnings setup section** of `scanned/stocks/$ARGUMENTS/current.md`. Leave 6-Pillar / Technical Read / Trade plan untouched.

8. **If a horizon-specific trigger fires post-print** (e.g., a Swing-tier "watch close above $X on green vector" that the print delivered or failed to), log to `scanned/INDEX.md` § Performance / audit log. The earnings outcome may also force a tier transition — apply per `tiers.md` § Tier-change protocol.

9. **No archive rotation, no rescan rotation** — in-place update. Full audit trail comes from `/rescan` only.
