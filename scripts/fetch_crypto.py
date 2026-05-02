#!/usr/bin/env python3
"""
fetch_crypto.py — local crypto context fetcher for /scan <crypto-symbol>.

Consolidates the free crypto-data sources used in `guide/scan/crypto-flow.md`
into a single local call. Replaces ~5 WebFetches per crypto scan with one
Python loop. Existing WebFetch sources stay as documented fallback.

Sources (all free, no keys required):
    - **CoinGecko** — spot, market cap, rank, dominance, 24h/7d/30d returns,
      24h volume, top 5 exchange venues by share. Aggregated across the entire
      market, not just one exchange.
    - **alternative.me Fear & Greed** — daily crypto F&G index + 7-day trend
    - **Binance public klines** — high-quality OHLC for the perpetual / spot pair
      (alternative to yfinance, which has crypto support but less reliable)
    - **CoinGecko derivatives** — aggregated funding rate + open interest across
      all listed perpetual exchanges (proxy for OKX/Deribit chain when those
      WebFetches fail)
    - **mempool.space** (BTC only) — mempool size, recommended fees, network state
    - **DeFiLlama** (alts) — chain TVL trend for ETH/SOL/etc.

Usage:
    .venv/bin/python scripts/fetch_crypto.py BTCUSDT
    .venv/bin/python scripts/fetch_crypto.py ETHUSDT
    .venv/bin/python scripts/fetch_crypto.py SOLUSDT --json

The pair format is the standard `<BASE><QUOTE>` (e.g., BTCUSDT, ETHUSDT) used
in the rest of the project; the script extracts the base asset for CoinGecko
lookup and the full pair for Binance.

Exit codes:
    0 — success
    1 — symbol not resolved
    2 — runtime error
"""

import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

UA = "trading-ops crypto-fetcher"
HEADERS = {"User-Agent": UA, "Accept-Encoding": "gzip, deflate"}
THROTTLE = 0.4  # ~CoinGecko free tier safe pace

CACHE_DIR = Path.home() / ".cache" / "trading-ops-crypto"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
COINS_LIST_CACHE = CACHE_DIR / "coingecko_coins_list.json"
COINS_LIST_TTL_DAYS = 7


def _http_get(url, accept_json=True, throttle=True):
    if throttle:
        time.sleep(THROTTLE)
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as r:
        data = r.read()
    return json.loads(data.decode("utf-8")) if accept_json else data.decode("utf-8")


# ---- Symbol resolution -----------------------------------------------------

# Hardcoded shortcuts for the common pairs — avoids the ambiguity in /coins/list
# (e.g., 'BTC' alone resolves to many wrapped/forked variants).
SYMBOL_TO_CG_ID = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
    "BNB": "binancecoin",
    "XRP": "ripple",
    "ADA": "cardano",
    "DOGE": "dogecoin",
    "AVAX": "avalanche-2",
    "LINK": "chainlink",
    "MATIC": "matic-network",
    "DOT": "polkadot",
    "LTC": "litecoin",
    "ATOM": "cosmos",
    "NEAR": "near",
    "TON": "the-open-network",
    "TRX": "tron",
    "BCH": "bitcoin-cash",
    "ARB": "arbitrum",
    "OP": "optimism",
    "SUI": "sui",
    "APT": "aptos",
    "INJ": "injective-protocol",
    "TIA": "celestia",
    "SEI": "sei-network",
    "PEPE": "pepe",
    "SHIB": "shiba-inu",
    "WLD": "worldcoin-wld",
}


def parse_pair(symbol):
    """BTCUSDT -> ('BTC', 'USDT'); BTC -> ('BTC', None)."""
    s = symbol.upper().replace("/", "").replace("-", "")
    for quote in ("USDT", "USDC", "USD", "EUR", "BTC", "ETH"):
        if s.endswith(quote) and s != quote:
            return s[:-len(quote)], quote
    return s, None


def resolve_cg_id(base):
    """Return CoinGecko coin ID for a base symbol (BTC -> 'bitcoin')."""
    base_u = base.upper()
    if base_u in SYMBOL_TO_CG_ID:
        return SYMBOL_TO_CG_ID[base_u]

    # Cache the full /coins/list so we don't refetch every run
    if COINS_LIST_CACHE.exists():
        age = (time.time() - COINS_LIST_CACHE.stat().st_mtime) / 86400
        if age < COINS_LIST_TTL_DAYS:
            coins = json.loads(COINS_LIST_CACHE.read_text())
        else:
            coins = _http_get("https://api.coingecko.com/api/v3/coins/list")
            COINS_LIST_CACHE.write_text(json.dumps(coins))
    else:
        coins = _http_get("https://api.coingecko.com/api/v3/coins/list")
        COINS_LIST_CACHE.write_text(json.dumps(coins))

    matches = [c for c in coins if c["symbol"].upper() == base_u]
    if not matches:
        return None
    # Prefer non-wrapped, non-staked variants
    for prefer in (matches, [m for m in matches if "wrapped" not in m["id"]]):
        if prefer:
            return prefer[0]["id"]
    return matches[0]["id"]


# ---- CoinGecko -------------------------------------------------------------

def coingecko_coin(cg_id):
    """Full coin endpoint — market data, tickers, sentiment, dev activity."""
    url = (
        f"https://api.coingecko.com/api/v3/coins/{cg_id}"
        "?localization=false&tickers=true&market_data=true&community_data=false&developer_data=false&sparkline=false"
    )
    return _http_get(url)


def coingecko_global():
    return _http_get("https://api.coingecko.com/api/v3/global")


def coingecko_derivatives_for(symbol):
    """Filter the /derivatives endpoint for the given base symbol's perp pairs."""
    try:
        all_d = _http_get("https://api.coingecko.com/api/v3/derivatives?include_tickers=unexpired")
    except Exception:
        return []
    base = symbol.upper()
    return [d for d in all_d if d.get("symbol", "").upper().startswith(base)][:20]


# ---- alternative.me Fear & Greed ------------------------------------------

def alt_me_fear_greed():
    try:
        d = _http_get("https://api.alternative.me/fng/?limit=8&format=json", throttle=False)
        return d.get("data", [])
    except Exception as e:
        sys.stderr.write(f"WARN: alternative.me F&G failed: {e}\n")
        return []


# ---- Binance public klines -------------------------------------------------

BINANCE_INTERVALS = {"1d": "1d", "1w": "1w", "4h": "4h", "1h": "1h"}


def binance_klines(pair, interval="1d", limit=200):
    if interval not in BINANCE_INTERVALS:
        return None
    url = f"https://api.binance.com/api/v3/klines?symbol={pair}&interval={BINANCE_INTERVALS[interval]}&limit={limit}"
    try:
        return _http_get(url, throttle=False)
    except Exception as e:
        sys.stderr.write(f"WARN: Binance klines {pair} {interval} failed: {e}\n")
        return None


# ---- mempool.space (BTC only) ---------------------------------------------

def mempool_state():
    try:
        fees = _http_get("https://mempool.space/api/v1/fees/recommended", throttle=False)
        mempool = _http_get("https://mempool.space/api/mempool", throttle=False)
        return {"fees": fees, "mempool": mempool}
    except Exception as e:
        sys.stderr.write(f"WARN: mempool.space failed: {e}\n")
        return None


# ---- DeFiLlama (alts / chain TVL) -----------------------------------------

CG_ID_TO_LLAMA_CHAIN = {
    "ethereum": "Ethereum",
    "solana": "Solana",
    "binancecoin": "BSC",
    "avalanche-2": "Avalanche",
    "polygon-pos": "Polygon",
    "matic-network": "Polygon",
    "arbitrum": "Arbitrum",
    "optimism": "Optimism",
    "near": "Near",
    "cosmos": "Cosmos",
    "the-open-network": "Ton",
    "sui": "Sui",
    "aptos": "Aptos",
    "injective-protocol": "Injective",
    "celestia": "Celestia",
    "sei-network": "Sei",
    "tron": "Tron",
}


def defillama_chain_tvl(cg_id):
    chain = CG_ID_TO_LLAMA_CHAIN.get(cg_id)
    if not chain:
        return None
    try:
        hist = _http_get(f"https://api.llama.fi/v2/historicalChainTvl/{chain}", throttle=False)
    except Exception as e:
        sys.stderr.write(f"WARN: DeFiLlama TVL {chain} failed: {e}\n")
        return None
    if not hist:
        return None
    latest = hist[-1]
    week_ago = hist[-8] if len(hist) >= 8 else None
    month_ago = hist[-31] if len(hist) >= 31 else None
    out = {"chain": chain, "tvl_usd": latest["tvl"], "as_of": latest["date"]}
    if week_ago:
        out["change_7d_pct"] = (latest["tvl"] - week_ago["tvl"]) / week_ago["tvl"] * 100
    if month_ago:
        out["change_30d_pct"] = (latest["tvl"] - month_ago["tvl"]) / month_ago["tvl"] * 100
    return out


# ---- Aggregated funding / OI ----------------------------------------------

def funding_oi_summary(derivs):
    """Aggregate stats across all listed perp tickers for the symbol."""
    if not derivs:
        return None
    fundings = [d.get("funding_rate") for d in derivs if d.get("funding_rate") is not None]
    ois = [d.get("open_interest") for d in derivs if d.get("open_interest") is not None]
    return {
        "perp_count": len(derivs),
        "funding_min": min(fundings) if fundings else None,
        "funding_max": max(fundings) if fundings else None,
        "funding_mean": sum(fundings) / len(fundings) if fundings else None,
        "oi_total": sum(ois) if ois else None,
        "top_exchanges": [
            {"exchange": d.get("market"), "oi": d.get("open_interest"), "funding": d.get("funding_rate")}
            for d in sorted(derivs, key=lambda x: x.get("open_interest") or 0, reverse=True)[:5]
        ],
    }


# ---- Rendering ------------------------------------------------------------

def _money(n, digits=2):
    if n is None:
        return "n/a"
    n = float(n)
    if abs(n) >= 1e12:
        return f"${n / 1e12:.{digits}f}T"
    if abs(n) >= 1e9:
        return f"${n / 1e9:.{digits}f}B"
    if abs(n) >= 1e6:
        return f"${n / 1e6:.{digits}f}M"
    if abs(n) >= 1e3:
        return f"${n / 1e3:.{digits}f}K"
    return f"${n:,.{digits}f}"


def render_markdown(symbol, base, quote, cg_id, coin, glob, fng, mempool, tvl, deriv_summary, klines_d):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    md = coin.get("market_data", {}) if coin else {}

    lines = []
    add = lines.append
    add(f"# {symbol} — Crypto context pre-compute ({now})")
    add(f"_{coin.get('name')} ({base}) · CoinGecko id `{cg_id}` · pair traded as {symbol}_")
    add("")

    # Price
    add("## Spot & price action")
    price_usd = md.get("current_price", {}).get("usd")
    add(f"- **Spot:** {_money(price_usd, 2)} USD")
    for label, key in (("24h", "price_change_percentage_24h"),
                       ("7d", "price_change_percentage_7d"),
                       ("30d", "price_change_percentage_30d"),
                       ("1y", "price_change_percentage_1y")):
        v = md.get(key)
        if v is not None:
            add(f"- {label:>3}: **{v:+.2f}%**")
    ath = md.get("ath", {}).get("usd")
    ath_chg = md.get("ath_change_percentage", {}).get("usd")
    if ath:
        add(f"- ATH: {_money(ath)} ({ath_chg:+.1f}% vs ATH)")
    atl = md.get("atl", {}).get("usd")
    if atl:
        atl_chg = md.get("atl_change_percentage", {}).get("usd")
        add(f"- ATL: {_money(atl)} ({atl_chg:+.1f}% vs ATL)")
    add("")

    # Market cap + dominance
    add("## Market cap, rank, dominance")
    mcap = md.get("market_cap", {}).get("usd")
    rank = md.get("market_cap_rank")
    add(f"- Market cap: {_money(mcap)} (rank #{rank})")
    add(f"- Fully diluted: {_money(md.get('fully_diluted_valuation', {}).get('usd'))}")
    add(f"- 24h volume: {_money(md.get('total_volume', {}).get('usd'))}")
    if glob:
        gd = glob.get("data", {})
        dom = gd.get("market_cap_percentage", {}).get(base.lower())
        if dom is not None:
            add(f"- **{base} dominance: {dom:.2f}%** of total crypto mcap")
        total = gd.get("total_market_cap", {}).get("usd")
        if total:
            add(f"- Total crypto mcap: {_money(total)}; 24h vol {_money(gd.get('total_volume', {}).get('usd'))}")
    add("")

    # Fear & Greed
    if fng:
        add("## Fear & Greed (alternative.me, last 8 days)")
        cur = fng[0]
        add(f"- **Today: {cur.get('value')} ({cur.get('value_classification')})**")
        add(f"- 7d trend: " + " → ".join(f"{f.get('value')}" for f in reversed(fng[1:])))
        add("")

    # Derivatives
    if deriv_summary:
        ds = deriv_summary
        add("## Derivatives — aggregated funding & OI (CoinGecko)")
        add(f"- {ds['perp_count']} perpetual contracts listed across exchanges")
        if ds.get("funding_mean") is not None:
            add(f"- Funding rate: mean **{ds['funding_mean'] * 100:+.4f}%** "
                f"(range {ds['funding_min'] * 100:+.4f}% / {ds['funding_max'] * 100:+.4f}%)")
        if ds.get("oi_total"):
            add(f"- Total open interest: {_money(ds['oi_total'])}")
        if ds["top_exchanges"]:
            add("- Top 5 venues by OI:")
            for v in ds["top_exchanges"]:
                fr = f"{v['funding'] * 100:+.4f}%" if v.get("funding") is not None else "—"
                add(f"  - {v['exchange']}: OI {_money(v.get('oi'))}, funding {fr}")
        add("")

    # Mempool (BTC only)
    if mempool and base.upper() == "BTC":
        f = mempool.get("fees", {})
        m = mempool.get("mempool", {})
        add("## Bitcoin network state (mempool.space)")
        add(f"- Recommended fees: fastest **{f.get('fastestFee')} sat/vB**, "
            f"30min {f.get('halfHourFee')}, 60min {f.get('hourFee')}, eco {f.get('economyFee')}, min {f.get('minimumFee')}")
        if m.get("count") is not None:
            add(f"- Mempool: {m.get('count'):,} txs, {_money(m.get('vsize') or 0, 0)} vbytes total ({m.get('total_fee'):,} sat fees pending)")
        add("")

    # TVL
    if tvl:
        add(f"## DeFi TVL — {tvl['chain']} (DeFiLlama)")
        add(f"- TVL: {_money(tvl['tvl_usd'])} (as-of {datetime.fromtimestamp(tvl['as_of'], tz=timezone.utc).strftime('%Y-%m-%d')})")
        if "change_7d_pct" in tvl:
            add(f"- 7d Δ: {tvl['change_7d_pct']:+.2f}%")
        if "change_30d_pct" in tvl:
            add(f"- 30d Δ: {tvl['change_30d_pct']:+.2f}%")
        add("")

    # Daily klines
    if klines_d:
        add(f"## Recent OHLC — {symbol} daily (Binance, last 10)")
        add("| Date | Open | High | Low | Close | Vol |")
        add("|---|---|---|---|---|---|")
        for k in klines_d[-10:]:
            ts = datetime.fromtimestamp(k[0] / 1000, tz=timezone.utc).strftime("%Y-%m-%d")
            o, h, l, c = float(k[1]), float(k[2]), float(k[3]), float(k[4])
            v = float(k[5])
            add(f"| {ts} | {o:,.2f} | {h:,.2f} | {l:,.2f} | {c:,.2f} | {v:,.0f} |")
        add("")

    add("## Fallback (when this script fails or needs cross-confirmation)")
    add("- Coinglass via chrome-devtools — heatmap / max pain / aggregated funding visual (per `guide/scan/crypto-flow.md` § Tier B)")
    add("- OKX/Deribit direct WebFetch — granular per-exchange funding curves and options chains")
    add("- Bitbo ETF flows — BTC spot ETF net flows (BTC only)")
    add("- TradingView for chart overlays")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__.strip().split("\n")[0])
    ap.add_argument("symbol", help="Crypto pair (e.g. BTCUSDT, ETHUSDT) or bare base (BTC)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    base, quote = parse_pair(args.symbol)
    cg_id = resolve_cg_id(base)
    if not cg_id:
        print(f"ERROR: could not resolve CoinGecko id for base {base}", file=sys.stderr)
        return 1

    pair = args.symbol.upper().replace("/", "").replace("-", "")
    if quote is None:
        # Default quote for klines is USDT
        pair = f"{base}USDT"

    try:
        coin = coingecko_coin(cg_id)
    except Exception as e:
        print(f"ERROR: CoinGecko coin fetch failed: {e}", file=sys.stderr)
        return 2

    try:
        glob = coingecko_global()
    except Exception:
        glob = None

    try:
        derivs = coingecko_derivatives_for(base)
    except Exception:
        derivs = []
    deriv_summary = funding_oi_summary(derivs)

    fng = alt_me_fear_greed()
    mempool = mempool_state() if base.upper() == "BTC" else None
    tvl = defillama_chain_tvl(cg_id)
    klines_d = binance_klines(pair, "1d", limit=120)

    if args.json:
        print(json.dumps({
            "symbol": args.symbol.upper(),
            "base": base, "quote": quote, "cg_id": cg_id,
            "coin_market_data": coin.get("market_data") if coin else None,
            "global": glob,
            "fear_greed": fng,
            "derivatives_summary": deriv_summary,
            "mempool": mempool,
            "tvl": tvl,
            "klines_daily": klines_d,
        }, default=str, indent=2))
        return 0

    print(render_markdown(args.symbol.upper(), base, quote, cg_id, coin, glob, fng, mempool, tvl, deriv_summary, klines_d))
    return 0


if __name__ == "__main__":
    sys.exit(main())
