# Scan protocol — read-before-scan, knowledge boundary, rescan rotation

> Part of the [scan protocol](../scan-rules.md). See also: [structure](structure.md), [tiers](tiers.md), [data](data.md), [style](style.md).

---

## Read-before-scan protocol

**Before pulling fresh data on any scan or rescan, read what we already know.** This is non-optional.

For any `/scan*` or `/rescan` command on `<TICKER>`:

1. **Check `<ticker-folder>/current.md`** — if it exists, read it fully:
   - Capture the prior verdict, score, regime fit, key levels, trade plan
   - Note the prior scan date (used for Δ comparison + archive rotation)
   - Identify what was previously called out as "watch for" or "trigger"
   - Note prior `**Coverage tier:**` (Pos / Swing / Day) for tier-change comparison

2. **Skim `<ticker-folder>/archive/`** — if files exist:
   - Read at least the 2–3 most recent archived snapshots
   - For EACH archived snapshot, extract the **Action verdict** line and any **trigger spec** (entry / stop / target prices, dates, conditions). These are the calls we made.
   - Compare those calls against what price actually did between then and now — did the trigger fire? did price go through the stop? did the target hit?
   - Classify each prior call as: **tracked** (still valid, trigger pending), **fired correctly** (trigger spec hit, position would be in expected direction), **invalidated** (price negated the setup before trigger fired), **stale** (>14 days, no resolution).
   - This populates the **Prior-scan track record** section per [structure.md](structure.md). It is non-optional when archive is non-empty.
   - Use these findings to inform the new scan's framing (e.g., "we've been watching the 50d retest for 3 weeks — it fired green +5% then reversed; level is no longer clean").

3. **Read `<ticker-folder>/notes.md`** if it exists — freeform observations between scans.

4. **Read `scanned/MACRO/current.md`** for current regime context (always — even when scanning a stock, the regime sets the lens). If older than 7 days when running a stock scan, **warn the user** and offer to run `/scan-macro` first.

**Why:** Each scan is a delta on prior knowledge, not a clean-room analysis. The audit trail is only valuable if we actually use it. Re-deriving from zero each time wastes work and breaks the evolution narrative. The Δ marker in the new TL;DR depends on knowing the old state.

If the prior scan flagged a specific trigger ("watch for break of $5.77 on volume"), the new scan must address that trigger explicitly — did it happen? what did price do? Log to INDEX.md § Performance / audit log if it fired or failed (per [tiers](tiers.md)).

## Outcome resolution log (rescan duty)

When a rescan resolves a prior trigger (fires correctly, fires-stopped, invalidated, or goes stale), append ONE row to `INDEX.md § Performance / audit log` in this exact format so `compute_hit_rates.py` can parse it:

```
YYYY-MM-DD <TICKER> [Pos|Swing|Day] pattern:<slug> outcome:<fired-correct|fired-stopped|invalidated|stale> — <1-line resolution narrative>
```

Examples:
```
2026-05-13 NIO [Swing] pattern:cloud-rejection-short outcome:fired-correct — Daily close $5.40 (-7.2% from entry), target hit
2026-05-08 BBAI [Swing] pattern:binary-earnings-put outcome:invalidated — Earnings beat consensus by 11¢, gap up +24%, put expired worthless
2026-05-30 BTCUSDT [Day] pattern:fomc-fade-short outcome:fired-stopped — Stop $77.3K hit on overnight ramp before $75.5K target
```

**Outcomes are appended PER HORIZON, PER PATTERN.** A single rescan can produce 0–3 outcome rows. If no prior trigger resolved, write nothing to the audit log — the silence is the signal.

**The audit log is the system's memory.** `compute_hit_rates.py` reads it. If you skip the outcome log on a rescan, you've broken the tracking loop for that ticker.

---

## Knowledge base — read-only (except via `/ingest`)

**`docs/` is the framework knowledge base. Never modify it during a scan.** The only entry point that writes inside `docs/` is the `/ingest` slash command ([`.claude/commands/ingest.md`](../../.claude/commands/ingest.md)) — every other path (scans, freeform actions, agents, the self-improvement loop) treats `docs/` as read-only.

The `docs/` folder contains the framework reference documents:
- [`docs/macro.md`](../../docs/macro.md) — top-down macro / regime framework (key indicators, regime quadrants, scenario logic)
- [`docs/long-term-investing.md`](../../docs/long-term-investing.md) — long-term-investing reference layer (6-pillar fundamentals, moat types, capital allocation, P/E vs growth, IPO cycle)
- [`docs/volume-profile.md`](../../docs/volume-profile.md) — volume profile methodology (POC / VAH / VAL / HVN / LVN, profile shapes, naked POC)
- [`docs/vwap.md`](../../docs/vwap.md) — VWAP family (session / weekly / monthly / quarterly / anchored, ±σ bands)
- [`docs/INGEST_LOG.md`](../../docs/INGEST_LOG.md) — append-only audit trail of every `/ingest` event

It is the source of truth.

**Rules:**
- ✅ **Read** `docs/**/*.md` to apply the framework
- ✅ **Quote** terminology from `docs/` exactly ("Stagflation", "regime quadrant")
- ❌ **Never edit** files in `docs/` as part of a scan
- ❌ **Never create** new files in `docs/` from scan output
- ✅ **Use `/ingest`** when new framework knowledge needs to enter `docs/` — it's the authorized writer and always asks for consent before applying

If a scan reveals something genuinely new about the framework itself (a clarification, a missing concept, a new pattern variant), tell the user — let them decide whether to run `/ingest`. Don't update it autonomously.

**Boundary summary:**

| Folder | Role | During a scan | Authorized writer |
|---|---|---|---|
| `docs/` | framework (rules of the game) | read-only | `/ingest` only |
| `scanned/` | applications (game state today) | read/write | scan commands |
| `guide/` | scan protocol (rules of how we scan) | read-only | self-improvement loop OR `/ingest` (with consent) |
| `input/` | original PDFs + ancillary references | read-only always | manual user-managed |

---

## Rescan rotation + retention

On `/rescan` (or any `/scan*` command against an existing `current.md`):

1. Read existing `current.md`.
2. Extract its scan date (from the `## Snapshot — YYYY-MM-DD` header).
3. **Save** the existing content as `archive/<YYYY-MM-DD>.md` — verbatim, except rewrite sibling-folder relative links to walk one level up (`]( charts/` → `]( ../charts/`, `]( notes.md` → `]( ../notes.md`). External, anchor, and absolute links are untouched. This is the only edit allowed on archived content.
4. **Prune `archive/`** per retention policy (below).
5. Pull fresh data, run framework, write new snapshot to `current.md`.
6. Update `scanned/INDEX.md` (and log per-horizon tier changes per [tiers](tiers.md)).

### Retention policy

The archive is bounded — old snapshots get pruned automatically:

- **Keep the latest snapshot per calendar month.** If multiple files exist for a month (e.g., `2026-04-15.md` and `2026-04-29.md`), delete the older one(s) and keep the newest.
- **Drop snapshots older than 12 months.** Anything dated > 365 days before today is removed.
- **Always keep `current.md`.** Never delete it.

This caps `archive/` at ≤ 12 files per ticker. Long-term evolution stays browsable; clutter doesn't accumulate.

The pruning happens *as part of* every rescan. Either run inline or via `scripts/prune-archive.py <ticker-folder>`:

```
1. ls archive/*.md
2. group by YYYY-MM
3. for each group with >1 file, delete all but the newest
4. delete any file dated > 365 days ago
```

### Same-day rescan handling

If today's date matches the prior scan's date (a same-day rescan, common when refreshing under a new spec or after intraday news):
- Archive the prior `current.md` to `archive/<today>.md` — overwrites any prior same-day archive
- Git history preserves the morning version if it becomes load-bearing later
- Don't suffix the file (`_am`, `_v1`, etc.) — keep the archive shape clean
