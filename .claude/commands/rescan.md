---
description: Refresh existing scan, rotating prior snapshot to archive/. Args: <TICKER> or "macro"
---

Rescan: **$ARGUMENTS**

The full protocol is in [`guide/scan/`](../../guide/scan/). Read [`protocol.md`](../../guide/scan/protocol.md) and [`tiers.md`](../../guide/scan/tiers.md) before starting if not loaded this session.

## Steps

1. **Identify target folder:**
   - If `$ARGUMENTS` is `macro` / `MACRO` → target = `scanned/MACRO/`
   - Else if folder exists at `scanned/stocks/$ARGUMENTS/` → that's the target (stock)
   - Else if `scanned/fx/$ARGUMENTS/` → target (FX)
   - Else if `scanned/indices/$ARGUMENTS/` or `scanned/crypto/$ARGUMENTS/` → target
   - Else: tell the user no `current.md` exists for this ticker and stop

2. **Verify `current.md` exists** in the target folder. If not, this isn't a rescan — tell the user to run `/scan` (stock), `/scan-macro`, or `/scan <SYMBOL>` first, and stop.

3. **Read-before-scan** per `protocol.md` § Read-before-scan protocol. Address prior triggers explicitly — did the level get tested? did the catalyst fire? did our verdict track? Log to INDEX.md § Performance / audit log if relevant.

4. **Rotate**: save existing `current.md` content verbatim to `<target>/archive/<prior-scan-date>.md`. Same-day rescan? Overwrites prior same-day archive (git history preserves the morning version).

5. **Prune archive** per `protocol.md` § Retention policy — or run `scripts/prune-archive.py <target>`.

6. **Pull fresh data and re-run framework**:
   - For macro: same data pulls as `/scan-macro`
   - For stock: same as `/scan` (full 6-pillar + multi-horizon technical read + earnings if within 90d)
   - For FX/index/commodity/crypto: same as `/scan <SYMBOL>` (Mode B — no 6-pillar/earnings)
   - Detect type by inspecting the prior `current.md` structure.

7. **Write new snapshot** to `<target>/current.md`, dated today.

8. **Δ marker**: prepend the new TL;DR with `**Δ since last scan (YYYY-MM-DD):** <what changed>` if verdict, regime, score, or key technical state changed materially. See `structure.md` § Δ marker.

9. **Update `scanned/INDEX.md`** per `tiers.md` § Tier-change protocol — log per-horizon changes if any.

## Style

Same as the underlying scan command — exact framework terminology, cited numbers, direct verdicts.

The archive is a **write-only audit trail**. Never edit prior snapshots — they're frozen at the date they were written. If you spot an error in a prior snapshot, leave it; the audit value comes from preserving what we believed at the time.
