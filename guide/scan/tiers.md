# Coverage tiers — three horizons, five letters

> Part of the [scan protocol](../scan-rules.md). See also: [structure](structure.md), [protocol](protocol.md).

---

The framework operates on three horizons. A name's verdict often differs by horizon — auto-reject positionally is compatible with a tradeable swing or scalp around a catalyst. We track tiers per horizon, not as a single number, so the audit trail and INDEX.md surface what's actually actionable at what timescale.

## Three horizons

| Horizon | Hold | Primary timeframes | Drives what |
|---|---|---|---|
| **Positional** | Weeks to months | Weekly + Monthly + 200d Daily | Investment thesis; 6-pillar fundamentals dominate; regime fit critical |
| **Swing** | 3–15 days | Daily + 4H | Trade setup post-catalyst, structural breaks/reversals; fundamentals secondary, levels primary |
| **Day-trade / Intraday** | Hours, same-day | 1H + 15m + session boxes | Today's price character, max-pain magnet, session liquidity, catalyst-day flow; fundamentals largely irrelevant |

## Five tiers per horizon

| Letter | Tier | Meaning |
|---|---|---|
| **T** | Top Pick | Full conviction at this horizon; deploy capital on the next trigger |
| **W** | Watchlist | Live trigger spec ready at this horizon; act when conditions hit |
| **B** | Bench | Followed but inactive at this horizon; rescan on regime shift or catalyst (rare for day-trade — by tomorrow it's irrelevant) |
| **S** | Skip / Avoid | Auto-reject or hostile setup at this horizon |
| **X** | Dropped | Removed from coverage entirely (applies across all horizons) |
| `—` | N/A | Horizon not applicable or not read this scan (e.g., illiquid name → no day-trade; 1H chart not captured → no day-trade read) |

## Mapping rules per horizon

| Tier | Positional rule | Swing rule | Day-trade rule |
|---|---|---|---|
| **T** | Buy AND score ≥5/6 AND weekly bullish posture AND regime favored/mixed | Daily/4H bullish setup AND clean entry+stop AND active catalyst pending | 1H bullish setup AND today is a setup day AND name has intraday liquidity (>1M avg vol) |
| **W** | Watchlist AND positional thesis intact AND clear positional trigger near-term | Daily/4H setup forming AND explicit "if X breaks/holds, act" within 1–2 weeks | Setup forming intraday today / pending catalyst this session |
| **B** | Long-cycle thesis but no near-term trigger (hostile regime, score 2–3/6, long-cycle compounder) | Range-bound, no swing setup right now, follow on rescan | (Rare) intraday range with no edge today |
| **S** | Auto-reject flag fires (negative ROIC, P/S extreme on declining sales, sub-200d, etc.) | Daily/4H structure broken or no valid setup; drift expected | No intraday edge AND/OR illiquid AND/OR price distribution against position |
| `—` | Horizon doesn't apply (rare for stocks; common for some illiquid OTCs) | (rare) | Common: 1H chart not pulled, or avg vol <1M, or no session-relevant action |

## Format in `current.md`

One line, all three horizons, in the snapshot header right after the price/regime block:

```markdown
**Coverage tier:** Pos **S** · Swing **W** · Day —
```

Add a brief parenthetical reason when useful:

```markdown
**Coverage tier:** Pos **S** (auto-reject) · Swing **W** (May 5 binary) · Day — (no 1H captured)
```

This single line is the source of truth that `INDEX.md` rolls up into its 3-column tier table. `scripts/regen-index.py` parses it.

**Tradeable instruments get tiers; pure regime trackers don't.**

- **Stocks, crypto (BTCUSDT, ETHUSDT…), single FX pairs, individual indices/ETFs we trade (SPY, QQQ, GLD…)** = full Pos / Swing / Day tier line in `current.md`. They roll into INDEX.md's master coverage table OR the "Macro / Indices / FX" table — both tables share the same tier columns.
- **Pure regime trackers** (`MACRO/`) do NOT get tiers — they live in the "Macro / Indices / FX" section of INDEX.md with `—` across all three tier columns. The macro doc is a lens, not a position.
- **An FX pair we monitor without trading** (purely for cross-asset context) sits in Macro/Indices/FX with `—` tiers; flip it to real tiers the moment you start writing trade plans against it.

The line in `current.md` is identical regardless of asset class — `**Coverage tier:** Pos · Swing · Day` — so `scripts/regen-index.py` can parse all of them uniformly.

---

## When a `/scan` or `/rescan` triggers a tier change

Tier comparison is **per horizon** (Pos / Swing / Day) — a single rescan can produce zero, one, two, or three coverage-change rows in INDEX.md.

1. Compute the new tier per horizon using fresh data + the mapping rules above.
2. Parse the prior `current.md`'s `**Coverage tier:**` line (if it exists) into Pos / Swing / Day.
3. For each horizon where the tier differs (or this is a first scan = `Initiated` for all three):
   - Append ONE row to `INDEX.md` § Coverage changes — last 30 days with: date, ticker, horizon name (Pos / Swing / Day / All for first scans), action verb, prior-tier → new-tier, one-line reason.
   - If the prior scan flagged a horizon-specific trigger ("daily close above $X with green vector for swing entry") and that trigger fired or failed in this rescan, ALSO append a row to `INDEX.md` § Performance / audit log tagged with the horizon.
4. Update the `**Coverage tier:**` line in the new `current.md` with all three current tiers (whether or not they changed).
5. If no horizon changed, do not write to the change log — the signal value is in the silence.

**Action verb mapping:**
- First scan (no prior `current.md`) → `Initiated` with Horizon=All
- Tier moving up the conviction stack (**S** → **W**, **W** → **T**, **B** → **W**) → `Upgraded`
- Tier moving down the stack → `Downgraded`
- Manual delisting → `Dropped`
- Coverage suspended pending data → `Suspended`

---

## When to flag X Dropped

Move a name to Dropped (manually edit INDEX.md) when:
- Ticker delisted or changed (M&A, bankruptcy, restructuring)
- Framework no longer applies (e.g., became an SPAC, reverse-merged into something different, went private)
- We've decided not to follow the name anymore for explicit reasons (note them)

Never delete a Dropped row — the audit trail is the value. The folder under `scanned/<ASSET-CLASS>/<TICKER>/` can stay or be archived elsewhere; the row in INDEX.md persists.
