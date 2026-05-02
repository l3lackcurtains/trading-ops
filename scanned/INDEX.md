# Scanned — Coverage Index

**Last regenerated:** 2026-05-02
**Macro regime:** [MACRO](MACRO/current.md) — Reflation
**Coverage universe:** 5 names (1 macro + 1 crypto + 3 stocks)
**Per-horizon active counts:** Pos **T**/**W** = 1 · Swing **T**/**W** = 4 · Day **T**/**W** = 2

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

| Ticker | Tier | Trigger | Invalidation |
|---|:-:|---|---|
| [BTCUSDT](crypto/BTCUSDT/current.md) | **W** | D close >$82,800 (200d EMA) sustained ≥2 days | D close <$75,320 (weekly LVN) |

---

## Swing Top Picks + Watchlist

| Ticker | Tier | Score | Trigger | Stop / Invalidation |
|---|:-:|:-:|---|---|
| [CRCL](stocks/CRCL/current.md) | **W** | 1/6 | (see scan) | (see scan) |
| [HOOD](stocks/HOOD/current.md) | **W** | 2/6 | D close >$75.16 (weekly VWAP) on vol → long to $80/$85; or $75/$82.50 call spread May 15 | D close <$71.92 (AVWAP −1σ) |
| [NIO](stocks/NIO/current.md) | **W** | 0/6 | (see scan) | (see scan) |
| [BTCUSDT](crypto/BTCUSDT/current.md) | **W** | — | LONG: D close >$80,740 (LVN) + vol ≥1.0× → T1 $82.6K / T2 $86K; SHORT: D close <$77,970 (mVWAP) → T1 $76K / T2 $75.3K | Long stop $79,400 · Short stop $79,400 |

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

## Macro / Indices / FX / Crypto

| Ticker | Pos | Swing | Day | Last Scan | Regime / Bias | Notes |
|---|:-:|:-:|:-:|---|---|---|
| [MACRO](MACRO/current.md) | — | — | — | 2026-05-01 | R2 Reflation | (see scan) |
| [BTCUSDT](crypto/BTCUSDT/current.md) | **W** | **W** | **B** | 2026-05-02 | R2 neutral-to-mild-bull; soft DXY tailwind, below 200d EMA | Swing WAIT: long >$80,740 LVN on vol / short <$77,970 mVWAP |

---

## Catalyst monitor — next 30 days

Sorted by date. 🔥 = within 7 days.

| Date | Ticker | Pos | Swing | Day | Event |
|---|---|:-:|:-:|:-:|---|
| 🔥 2026-05-08 | BTCUSDT | **W** | **W** | **B** | NFP April — macro volatility event; swing trigger watch |
| 2026-05-11 | CRCL | **S** | **W** | **W** | 🔥 **Q1 earnings Mon |
| 2026-05-12 | BTCUSDT | **W** | **W** | **B** | CPI April — core CPI trajectory; rate / BTC cross-asset |
| 2026-05-15 | BTCUSDT | **W** | **W** | **B** | Monthly OPEX — BTC options max pain pull (~$78K–$80K) |
| ≈2026-05-16 | BTCUSDT | **W** | **W** | **B** | BTC difficulty retarget (est. -1.33%) |
| 2026-07-29 | HOOD | **S** | **W** | **W** | Q2 2026 earnings ≈AMC |

---

## Coverage changes — last 30 days

| Date | Ticker | Horizon | Action | Tier change | Reason |
|---|---|---|---|---|---|
| 2026-05-02 | BTCUSDT | All | Initiated | — → Pos **W** / Swing **W** / Day **B** | First scan: below 200d EMA ($82.8K); two-sided swing around monthly VWAP; neutral funding |
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
