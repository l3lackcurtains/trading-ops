---
description: Run a Finviz screener aligned with the framework + current macro regime. Saves a dated candidate list to scanned/SCREENS/.
---

Run a screener: **$ARGUMENTS**

Protocol in [`guide/discover-rules.md`](../../guide/discover-rules.md). Read it before starting if you haven't this session — it has the verified Finviz filter prefix reference, all preset filter sets (r1/r2/r3/r4/quality/growth/value/defense), 0-results fallback strategy, and the SCREENS folder structure.

## Steps

1. **Read** `guide/discover-rules.md` for the filter syntax and presets.

2. **Read** `scanned/MACRO/current.md` to anchor the screen to the current quadrant. If MACRO is older than 7 days, warn the user and offer to run `/scan-macro` first.

3. **Determine preset** from `$ARGUMENTS`:
   - Bare regime tag (`r1` / `r2` / `r3` / `r4`) → use the strict-regime preset
   - Theme tag (`quality` / `growth` / `value` / `defense`) → use the named preset
   - Mixed (`r3-defense`) → combine, document the mix
   - Empty → use the regime-default preset (whatever regime MACRO currently flags)

4. **Build the Finviz screener URL** per `discover-rules.md` filter prefix reference. Validate filter codes — the doc has the verified prefixes (`fa_opmargin` not `fa_opermargin`, etc.). A wrong prefix returns 0 silently.

5. **Run the screen** via WebFetch on the constructed URL. Extract candidates with their filter-relevant metrics.

6. **0-results fallback** per `discover-rules.md` § 0-results fallback — if the strict preset returns 0 results, document the strict run, then progressively relax filters (per the documented relaxation order) and re-run. Note every relaxation step in the saved file.

7. **Save** to `scanned/SCREENS/<YYYY-MM-DD>-<preset>.md` (or `<YYYY-MM-DD>.md` for the default preset). Use the screen-file structure spec in `discover-rules.md`.

8. **Update `scanned/INDEX.md`** § Recent screens — append the new screen entry.

9. **Self-improvement loop** per `guide/scan/style.md` § Process self-improvement — surface any process problems (broken filter codes, ambiguous instructions, missing edge cases) at the end of your reply. Wait for user consent before editing the rules.
