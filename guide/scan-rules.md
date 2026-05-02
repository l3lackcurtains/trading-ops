# Scan Rules — index

Scans are the working memory of the trading system: dated snapshots of stocks, indices, FX, commodities, and macro regime. They evolve with each rescan; we preserve a bounded audit trail so we can see how our reads change against what actually happened.

All `/scan*` and `/rescan` slash commands MUST follow these rules.

The protocol is split into focused files in [`guide/scan/`](scan/):

| File | What it covers |
|---|---|
| [structure.md](scan/structure.md) | Folder layout, file naming, snapshot template, snapshot dating, Δ marker, notes file, **INDEX.md format spec**, multi-horizon Trade plan + price-ladder structure |
| [protocol.md](scan/protocol.md) | Read-before-scan procedure, knowledge-base boundary (`docs/` read-only), rescan rotation + retention policy, same-day rescan handling |
| [tiers.md](scan/tiers.md) | **Coverage tiers** — three horizons (Pos / Swing / Day), five letters (T / W / B / S / X), per-horizon mapping rules, tier-change protocol, X-Dropped rules |
| [scorecard.md](scan/scorecard.md) | **6-pillar scoring conventions** — Pillar 0 qualitative gate, moat-type tag (Pillar 1), high-conviction confirmation rule (3 consecutive Q growth + 13F holders rising), Smart Money one-sentence convention, optional P/E-vs-growth + capital-allocation lenses |
| [data.md](scan/data.md) | Single-source-per-fact rule, source priority chain (Finviz → Stockanalysis → 13F sources → Dataroma → insider sources → ChartExchange → Seeking Alpha → WebSearch), freshness-first strategy, ChartExchange section template, squeeze tiering rules |
| [crypto-flow.md](scan/crypto-flow.md) | **Crypto Flow & Positioning** — Tier A WebFetch APIs (alternative.me F&G, CoinGecko, OKX funding/OI, Deribit options, mempool.space, Bitbo ETF) + Tier B chrome-devtools captures (Coinglass heatmap / funding / max pain), crypto squeeze tiering, stock-side analogue cheat sheet |
| [index-flow.md](scan/index-flow.md) | **Index Flow & Positioning** — gamma exposure (zero-gamma flip / call wall / put wall — SpotGamma + Tier1 + MenthorQ + Convex Value), VIX term structure + VVIX + SKEW, AAII / NAAIM / Cboe P/C sentiment, breadth, COT equity-index futures. Squeeze tiering by gamma regime. Optional Tier C compute-gamma-from-options-chain (deferred). |
| [fx-flow.md](scan/fx-flow.md) | **FX Flow & Positioning** — CFTC COT (CME FX futures) as prime signal, IG / MyFXBook / OANDA retail sentiment as contrarian, rate differentials (2yr/10yr) as carry engine, Forex Factory calendar. Squeeze tiering by positioning extremes. |
| [commodity-flow.md](scan/commodity-flow.md) | **Commodity Flow & Positioning** — CFTC COT (commercials = producers/end-users smart-money), EIA petroleum/NG inventory, USDA WASDE grains, futures curve shape (backwardation/contango), Baker Hughes rigs, COMEX/LME warehouse, seasonality. Squeeze tiering by supply/storage state. |
| [style.md](scan/style.md) | Tone, terminology, what-never-goes-in, source citation, cross-references, scope separation (info flows down, not up), self-improvement loop |

## Conflict resolution

If two files in `guide/scan/` ever conflict:
- [tiers.md](scan/tiers.md) wins for anything tier-related.
- [scorecard.md](scan/scorecard.md) wins for 6-pillar scoring conventions, gates, and high-conviction rules.
- [data.md](scan/data.md) wins for sourcing decisions on stock scans.
- [crypto-flow.md](scan/crypto-flow.md) wins for sourcing decisions on crypto scans.
- [index-flow.md](scan/index-flow.md) wins for sourcing decisions on index scans (SPX, NDX, RUT, broad-market ETFs).
- [fx-flow.md](scan/fx-flow.md) wins for sourcing decisions on FX-pair scans.
- [commodity-flow.md](scan/commodity-flow.md) wins for sourcing decisions on commodity / commodity-ETF scans.
- [structure.md](scan/structure.md) wins for folder layout, INDEX.md format, snapshot template, and Trade plan / price-ladder structure.
- [protocol.md](scan/protocol.md) wins for rescan rotation, retention, read-before-scan order.
- [style.md](scan/style.md) wins for tone, citation, what-never.

If a `.claude/commands/*.md` file ever conflicts with one of these, the `guide/scan/` file wins. Open a fix in the guide first.
