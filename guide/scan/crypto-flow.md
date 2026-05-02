# Crypto Flow & Positioning — derivative + on-chain + ETF lens for crypto scans

> Part of the [scan protocol](../scan-rules.md). See also: [data](data.md).

---

This doc is the **crypto analogue** of the stock-side ChartExchange Flow & Squeeze section in [data.md](data.md). It defines what positioning + flow data we pull on every `/scan` run against a tradeable crypto symbol (BTCUSDT, ETHUSDT, etc.), where to fetch it, and how it maps to existing framework concepts.

The technical read on the chart is still the primary lens. This section is **supplementary** — strongest when it CONFIRMS the chart read (e.g. weakening right-edge weekly + neg funding + post-flush OI drop = real distribution, not just retrace). When flow diverges from the chart, note the divergence as a watch-item.

---

## Three-tier capture (Tier 0 local · Tier A WebFetch · Tier B screenshot)

The free crypto APIs we use (CoinGecko, alternative.me, Binance public, mempool.space, DeFiLlama) are all consolidatable into **one local Python call** (`scripts/fetch_crypto.py`). That's Tier 0. Where APIs aren't enough — JS-rendered dashboards where the spatial layout IS the data (heatmap clusters, OI by strike) — use Tier B chrome-devtools. Tier A WebFetch is the documented fallback for when Tier 0 has gaps or you need the granular per-exchange breakdown (e.g. specific OKX/Deribit endpoints).

### Tier 0 — Local script (run first, replaces ~5 WebFetches)

```bash
.venv/bin/python scripts/fetch_crypto.py BTCUSDT      # full context for BTC
.venv/bin/python scripts/fetch_crypto.py ETHUSDT      # ETH-specific, plus DeFiLlama TVL
.venv/bin/python scripts/fetch_crypto.py SOLUSDT      # SOL TVL via DeFiLlama
.venv/bin/python scripts/fetch_crypto.py BTCUSDT --json
```

Returns ~400–600 tokens of structured markdown:
- **Spot + price changes** (24h / 7d / 30d / 1y) + ATH/ATL distance — from CoinGecko `/coins/{id}`
- **Market cap, rank, dominance** — CoinGecko `/coins/{id}` + `/global` (BTC dominance % across the entire crypto market)
- **Fear & Greed** — alternative.me `/fng/?limit=8`, today's value + 7-day trend
- **Aggregated funding & OI** across all listed perpetual exchanges — CoinGecko `/derivatives` filtered to the symbol's perps; reports mean / min / max funding rate, total OI, top 5 venues by OI with their individual funding
- **Bitcoin network state** (BTC only) — mempool.space `/api/v1/fees/recommended` + `/api/mempool` for fee tiers and mempool size
- **DeFi TVL** (alts only) — DeFiLlama `/v2/historicalChainTvl/<chain>` with 7d/30d Δ
- **Daily OHLC** — Binance public klines (last 120 bars by default), no auth, no geo-block on the public endpoint

Symbol resolution: hardcoded shortcuts for the top 30 names, fall through to CoinGecko `/coins/list` cached locally for 7 days.

**Known failure modes:**
- **CoinGecko gzip error** — if `fetch_crypto.py` exits with `'utf-8' codec can't decode byte 0x8b`, the CoinGecko endpoint returned gzip-compressed data that the script isn't decompressing. Fall back to Tier A WebFetch for the affected fields. The fix in the script is to add `Accept-Encoding: identity` to the request headers or decode via `gzip.decompress`.
- **`fetch_ohlc.py` symbol format** — Yahoo Finance uses `BTC-USD`, `ETH-USD`, `SOL-USD` (hyphen + USD suffix), not the exchange pair format. Always pass the Yahoo-format symbol: `.venv/bin/python scripts/fetch_ohlc.py BTC-USD --timeframes W,D,4H,1H`. The scan command's display symbol (BTCUSDT) and the OHLC script symbol (BTC-USD) are different.

**Tier A WebFetch sources below stay as documented fallback** — pull them when Tier 0 fails or when you need granular per-exchange detail (e.g. specific OKX vs Bybit funding curve cross-confirmation).

### Tier A — WebFetch (fallback / per-exchange granularity)

| Metric | Source | URL pattern | Lag |
|---|---|---|---|
| **Crypto Fear & Greed** (alt to CNN F&G) | alternative.me | `https://api.alternative.me/fng/?limit=8` | T+0 (daily) |
| **Total crypto mcap, BTC dominance, 24h vol, 24h change** | CoinGecko | `https://api.coingecko.com/api/v3/global` | Real-time |
| **Per-coin spot price + ATH/ATL + 7d/24h change** | CoinGecko | `https://api.coingecko.com/api/v3/coins/<coin-id>` | Real-time |
| **Daily Spot ETF net flow** (BTC; ETH where listed) | Bitbo | `https://bitbo.io/treasuries/etf-flows/` | T+1 day |
| **Perp funding rate** (current 8h period) | OKX public API | `https://www.okx.com/api/v5/public/funding-rate?instId=<COIN>-USDT-SWAP` | Real-time |
| **Perp open interest** (single-exchange notional) | OKX public API | `https://www.okx.com/api/v5/public/open-interest?instType=SWAP&instId=<COIN>-USDT-SWAP` | Real-time |
| **Options OI, max pain calc** (BTC + ETH only — Deribit dominates) | Deribit public API | `https://www.deribit.com/api/v2/public/get_book_summary_by_currency?currency=BTC&kind=option` | Real-time |
| **Network state** (BTC: difficulty cycle, hashrate, fee tier, mempool) | mempool.space | `https://mempool.space/api/v1/difficulty-adjustment`, `…/fees/recommended`, `…/mining/hashrate/3d` | Real-time |

**Don't bother with these — they're geo-blocked from this IP (HTTP 451):**
- `fapi.binance.com/*` — US 451
- `api.bybit.com/v5/market/*` — currently 403 (varies)

If the OKX endpoint goes down, fall back to Hyperliquid public API (`https://api.hyperliquid.xyz/info`) or Coinbase Advanced Trade public endpoints — both no-auth, both return funding/OI for the perpetuals listed there.

### Tier B — chrome-devtools screenshot (when the spatial pattern matters)

| Metric | Source | URL | Why screenshot, not API |
|---|---|---|---|
| **Liquidation heatmap** (forced-covering magnet zones) | Coinglass | `https://www.coinglass.com/pro/futures/LiquidationHeatMap?coin=<COIN>` | Heatmap clusters are spatial — yellow/cyan bands around price levels. The Coinglass free API is auth-walled; the chart IS the readable signal. |
| **Aggregate funding-rate dashboard** (cross-exchange comparison) | Coinglass | `https://www.coinglass.com/FundingRate` | Per-exchange variance is the signal (e.g. Binance neg + Bybit neutral = exchange-specific squeeze pressure) |
| **Options max pain by expiry** | Coinglass | `https://www.coinglass.com/pro/options/max-pain` | Calculated max pain vs notional value across expiries. Computable from Deribit API but visual confirmation is faster. |

**Don't waste a capture on:**
- **Coinank** (`coinank.com/chart/derivatives/liq-heat-map`) — the heatmap, max pain, and most chart features are **login-walled** (showing "Please log in to use chart features"). The header strip exposes Volume/OI/Liq/L-S aggregates without login but those numbers also live on Coinglass; pick one. Coinank is otherwise just the same data rebranded.
- **Coinglass detailed pages requiring Pro tier** — pricing-banner pages.

The Coinglass header on any of its pages already shows global aggregates (24h Vol, OI, 24h Liq, L/S ratio) without login — those become "free metadata" on every Tier B capture.

---

## Squeeze tiering for crypto

Adapted from [data.md § Squeeze tiering rules](data.md). Crypto thresholds run tighter because there's no FINRA cycle and funding/OI move minute-to-minute.

| Tier | Conditions (any one of) |
|---|---|
| **Extreme squeeze (long unwind risk)** | Funding > +0.05%/8h AND aggregate OI rising for ≥7 days AND liquidation cluster within 2% above price AND F&G > 80 |
| **High squeeze (long unwind risk)** | Funding > +0.02%/8h AND OI rising 3+ days AND F&G > 70 |
| **Extreme squeeze (short unwind risk)** | Funding < −0.05%/8h AND aggregate OI rising AND liquidation cluster within 2% below price AND F&G < 20 |
| **High squeeze (short unwind risk)** | Funding < −0.02%/8h AND OI rising 3+ days AND F&G < 30 |
| **Moderate** | Funding 0–0.02%/8h, no clustered liquidations, F&G 30–70 |
| **Low / post-flush** | Funding flat (≤±0.001%) AND OI **dropped** ≥10% in last 24–72h AND large 24h liquidation print already happened. **This is the de-leveraged-reset state** — squeeze risk in either direction is low because the leverage that would fuel it just got cleared. |

The "post-flush" tier matters: a chart that LOOKS bearish but flow shows neg funding + collapsed OI + already-done liquidation spike often means the bear move is over (forced sellers gone), not starting.

---

## ChartExchange-style section template (paste into `current.md`)

```markdown
### Crypto Flow & Positioning

| Signal | Reading | As of | Interpretation |
|---|---|---|---|
| Crypto F&G | <value> (<label>) — yesterday <v>, last week <v> | YYYY-MM-DD | Crypto sentiment vs CNN macro F&G — divergence is itself a signal |
| BTC dominance / total mcap | <D>% / $<X>T (<Δ24h>%) | real-time | Rising D = defensive crypto regime; falling = alts-on |
| Spot ETF flow (5d) | Day-1 +/−$XM, Day-2…, Day-5… | T+1 | Institutional positioning analogue of dark-pool % |
| OKX BTC perp funding | <X.XX%>/8h (annualized ≈<Y>%) | real-time | Cost of carry for perp longs; >0 = bull crowd, <0 = bear crowd |
| OKX BTC perp OI | $<X>B (<Δ24h>%) | real-time | Single-exchange OI; track direction more than absolute |
| 24h aggregate liquidations | $<X>M (<Δ%>) longs/shorts | T+0 (Coinglass header) | Forced-covering volume; spike = flush already happened |
| Long/short ratio (24h) | <L>%/<S>% | T+0 (Coinglass header) | Retail-sentiment proxy; extremes are contrarian |
| Options OI top strikes | Put <strike>@<exp>, Call <strike>@<exp> | real-time (Deribit) | Where MM hedging concentrates |
| Max pain — next OPEX, next quarterly, year-end | $<n>K / $<q>K / $<y>K | real-time | Magnetic pull into expiry; multi-expiry view shows term structure |
| Liquidation heatmap clusters | <cluster level + density>; <cluster level + density> | T+0 | Magnet zones above + below — read off Coinglass heatmap screenshot |
| BTC network — difficulty / hashrate | <progress>% through cycle, <Δ%> projected; <X> EH/s | T+0 | Hashprice trend; hashrate falling into a flat-tape = miner capitulation |

**Composite squeeze tier:** Low / Moderate / High / Extreme (long-unwind | short-unwind | post-flush)

**Cross-confluence with the chart read:** [does the heatmap magnet align with the chart's swing target? does funding direction confirm the right-edge candle? does OI drop confirm a flush before a bullish setup, or reset before a continuation?]
```

---

## Crypto signal → stock framework analogue (cheat sheet)

For readers transferring from the stock-side framework:

| Stock-side signal | Crypto analogue | Why |
|---|---|---|
| Dark pool % off-exchange | Spot ETF daily net flow | Institutional positioning; both lag price by ~T+1 |
| Max pain (next monthly OPEX) | Deribit max pain (next monthly) | Direct analogue — only crypto where this works real-time |
| Short interest | Perpetual funding rate (sign + magnitude) | Bear positioning; neg funding = shorts crowded |
| Days-to-cover | OI ÷ avg liquidation rate | Rough proxy; less standardized than equities |
| FTD / forced covering | Liquidation heatmap clusters | Where stops/liquidations cluster = forced-flow target |
| Borrow fee | Funding rate (perp = synthetic borrow) | Cost-of-carry; positive funding ≈ borrow cost for shorts |
| Insider cluster buying | (no clean analogue) | Whale on-chain wallets are the closest but lag and aren't reliable; mostly use ETF flow + futures premium instead |
| 13F count + holdings | ETF holdings + Strategy/MSTR/MARA disclosed BTC stack | Slow-moving institutional book |
| Earnings catalyst | (no analogue for BTC) | Macro catalysts (FOMC, CPI, NFP) substitute |
| Sector rotation context | BTC dominance + alt market cap split | Defensive vs risk-on within crypto |

The cheat sheet is descriptive, not prescriptive — don't force an analogue when none exists. Some signals only apply to one side.

---

## Source-priority chain (when you have to pick one)

For metrics where multiple sources work:

- **Funding rate**: OKX public > Hyperliquid > screenshot Coinglass dashboard. Single-exchange pulls are fine — direction matters more than aggregate magnitude.
- **OI**: OKX public for single-exchange notional; Coinglass screenshot for cross-exchange aggregate.
- **ETF flows**: Bitbo first (works via WebFetch), Farside second (often 403). CryptoTimes/AInvest are weekly summaries, less granular — only use them if Bitbo is down.
- **Sentiment**: alternative.me API is the only one that returns clean JSON; never substitute the CNN macro F&G — they measure different things.

---

## Rules

- **Don't pull the same fact from two crypto sources.** OKX funding + Bybit funding for the same coin = duplication.
- **Always state the lag floor.** Crypto data is mostly real-time but ETF flows are T+1 and difficulty cycle prints every 2 weeks. Don't pretend a 24h-old number is live.
- **Omit, don't fabricate.** If every API for a metric fails, mark it `unavailable` and let the verdict run on the chart + the working signals.
- **Tier B captures cost a chrome-devtools tab.** Track and close them — open one screenshot at a time, close before opening the next.
- **Don't include this section in stock scans.** It's strictly the crypto template; stock scans use the ChartExchange Flow & Squeeze section in [data.md](data.md).
