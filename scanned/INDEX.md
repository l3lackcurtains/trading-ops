# Scanned — Coverage Index

**Last regenerated:** 2026-05-02
**Macro regime:** [MACRO](MACRO/current.md) — Reflation
**Coverage universe:** 4 names (1 macro + 0 FX/index + 3 stocks)
**Per-horizon active counts:** Pos **T**/**W** = 0 · Swing **T**/**W** = 3 · Day **T**/**W** = 2

This is the trader-desk equivalent of an institutional research coverage list — every name we scan, with **a tier per horizon** (Positional / Swing / Day-trade) so the framework matches reality: a name can be auto-reject long-term but a clean swing or scalp.

Full mapping rules in [`guide/scan/tiers.md`](../guide/scan/tiers.md).

---

## Coverage tiers — quick legend

**Horizons:** Pos = weeks-to-months · Swing = 3–15 days · Day = same-day intraday

**Tiers:** **T** Top Pick · **W** Watchlist (live trigger) · **B** Bench (no live trigger) · **S** Skip (auto-reject / hostile) · **X** Dropped · `—` N/A (horizon not read or doesn't apply)

---

## Master coverage table

| Ticker | Pos | Swing | Day | Score | Last Scan | Best near-term trigger | Next Catalyst |
|---|:-:|:-:|:-:|:-:|---|---|---|
| [CRCL](stocks/CRCL/current.md) | **S** | **W** | **W** | 1/6 | 2026-05-01 | (see scan) | 🔥 **Q1 earnings Mon 2026-05-11 |
| [HOOD](stocks/HOOD/current.md) | **S** | **W** | **W** | 2/6 | 2026-05-02 | Swing: D close >$75.16 (weekly VWAP) on vol | Q2 earnings ≈2026-07-29 AMC |
| [NIO](stocks/NIO/current.md) | **S** | **W** | **B** | 0/6 | 2026-05-01 | (see scan) | Q1'26 deliveries already reported |

---

## Positional Top Picks + Watchlist

*None currently — wait IS a position.*

---

## Swing Top Picks + Watchlist

| Ticker | Tier | Score | Trigger | Stop / Invalidation |
|---|:-:|:-:|---|---|
| [CRCL](stocks/CRCL/current.md) | **W** | 1/6 | (see scan) | (see scan) |
| [HOOD](stocks/HOOD/current.md) | **W** | 2/6 | D close >$75.16 (weekly VWAP) on vol → long to $80/$85; or $75/$82.50 call spread May 15 | D close <$71.92 (AVWAP −1σ) |
| [NIO](stocks/NIO/current.md) | **W** | 0/6 | (see scan) | (see scan) |

---

## Day-trade / Intraday Top Picks + Watchlist

| Ticker | Tier | Score | Trigger | Stop / Invalidation |
|---|:-:|:-:|---|---|
| [CRCL](stocks/CRCL/current.md) | **W** | 1/6 | (see scan) | (see scan) |
| [HOOD](stocks/HOOD/current.md) | **W** | 2/6 | VWAP reclaim (≈$74–75) + vol ≥1.3× avg on catalyst session (NFP May 8) | Volume stays sub-avg → no edge |

---

## X Dropped

*None.*

---

## Macro / Indices / FX

| Ticker | Last Scan | Regime / Bias | Notes |
|---|---|---|---|
| [MACRO](MACRO/current.md) | 2026-05-01 | Reflation | (see scan) |

---

## Catalyst monitor — next 30 days

Sorted by date. 🔥 = within 7 days.

| Date | Ticker | Pos | Swing | Day | Event |
|---|---|:-:|:-:|:-:|---|
| 2026-05-11 | CRCL | **S** | **W** | **W** | 🔥 **Q1 earnings Mon |
| 2026-07-29 | HOOD | **S** | **W** | **W** | Q2 2026 earnings ≈AMC |

---

## Coverage changes — last 30 days

| Date | Ticker | Horizon | Action | Tier change | Reason |
|---|---|---|---|---|---|
| 2026-05-02 | HOOD | All | Initiated | — → Pos **S** / Swing **W** / Day **W** | First scan: sub-200d daily EMA; post-earnings washout at $74 triple confluence; gamma pull to $80 |
| 2026-05-01 | NIO | All | Initiated | — → Pos **S** / Swing **W** / Day **B** | First scan: First scan |
| 2026-05-01 | CRCL | All | Initiated | — → Pos **S** / Swing **W** / Day **B** | First scan: auto-reject ROIC -2.29%; May 11 binary; VWAP-band fade |

---

## Performance / audit log

*Empty for now.*

---

## Recent screens

*None.*

---

**Legend:** ⚠ stale (> 14 days)  ·  🔥 catalyst within 7 days
