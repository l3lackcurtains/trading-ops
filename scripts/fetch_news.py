#!/usr/bin/env python3
"""
fetch_news.py — local news + analyst context fetcher.

Replaces ad-hoc WebSearches in the scan flow with a structured pull. Designed
to satisfy the depth requirements in `guide/scan/data.md` § Step 8 — 4–6
distinct sources organized by category (catalyst / analyst / sector / macro /
insider-13F / earnings-call).

**Works with NO API keys by default.** Tiered sources, primary-to-fallback:

    Tier 1 (keyless, universal — works for stocks, crypto, FX, indices, commodities):
      - Google News RSS — `news.google.com/rss/search?q=<query>` (XML, ~30 items)

    Tier 2 (keyless, stock-specific):
      - Finviz quote page news widget — HTML scrape, often surfaces Benzinga
        "Analyst Notes" with named-bank price-target changes
      - yfinance Ticker.news — last ~10 headlines (calls Yahoo)

    Tier 3 (key, optional — richer analyst data when available):
      - Finnhub `/stock/price-target` — high/low/mean/median targets + analyst count
      - Finnhub `/stock/recommendation` — Strong-Buy/Buy/Hold/Sell/Strong-Sell
        distribution and trend
      - Finnhub `/calendar/earnings` — next earnings WITH AMC/BMO timing
        (closes the Yahoo gap)
      Set `FINNHUB_TOKEN` env var. Free key at https://finnhub.io/register.

Usage:
    .venv/bin/python scripts/fetch_news.py RIVN
    .venv/bin/python scripts/fetch_news.py BTC --asset-class=crypto
    .venv/bin/python scripts/fetch_news.py WTI --asset-class=commodity
    .venv/bin/python scripts/fetch_news.py RIVN --days=14 --json

Exit codes:
    0 — success
    1 — no news returned from any tier
    2 — runtime error
"""

import argparse
import html
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from xml.etree import ElementTree as ET

FINNHUB_TOKEN = os.environ.get("FINNHUB_TOKEN")

UA_BROWSER = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)
HEADERS_JSON = {"User-Agent": "trading-ops news-fetcher", "Accept": "application/json"}
HEADERS_HTML = {"User-Agent": UA_BROWSER, "Accept": "text/html,application/xhtml+xml"}


# ---- Asset-class auto-detect (matches /scan routing) ----------------------

def detect_asset_class(symbol):
    s = symbol.upper().replace("/", "").replace("-", "")
    if any(s.endswith(q) for q in ("USDT", "USDC")) or s in (
        "BTC", "ETH", "SOL", "BNB", "XRP", "ADA", "DOGE", "AVAX", "LINK", "DOT",
        "MATIC", "LTC", "ATOM", "NEAR", "TON", "TRX", "BCH", "ARB", "OP", "SUI",
    ):
        return "crypto"
    if len(s) == 6 and all(
        s[i:i + 3] in ("EUR", "USD", "GBP", "JPY", "AUD", "CAD", "CHF", "NZD", "SEK", "NOK")
        for i in (0, 3)
    ):
        return "forex"
    if s in ("SPX", "NDX", "RUT", "DJI", "VIX", "VVIX", "SKEW", "DXY",
             "SPY", "QQQ", "IWM", "DIA", "VTI", "VOO"):
        return "index"
    if s in ("CL", "BZ", "NG", "GC", "SI", "HG", "ZC", "ZS", "ZW",
             "WTI", "BRENT", "USO", "BNO", "UNG", "GLD", "IAU", "SLV", "GDX", "DBA", "CORN"):
        return "commodity"
    return "stock"


# ---- Tier 1: Google News RSS (keyless, universal) -------------------------

def google_news_query_for(symbol, asset_class):
    """Build a query string Google News will resolve well across asset classes."""
    s = symbol.upper()
    if asset_class == "stock":
        return f"{s} stock"
    if asset_class == "crypto":
        # Strip USDT/USDC suffix for search; "BTCUSDT crypto" is noisier than "BTC crypto"
        base = s.replace("USDT", "").replace("USDC", "").replace("USD", "")
        return f"{base} crypto"
    if asset_class == "commodity":
        commodity_aliases = {
            "WTI": "WTI crude oil", "CL": "WTI crude oil", "BRENT": "Brent crude oil",
            "BZ": "Brent crude oil", "NG": "natural gas",
            "GC": "gold price", "GLD": "gold price", "IAU": "gold price",
            "SI": "silver price", "SLV": "silver price",
            "HG": "copper price",
            "ZC": "corn futures", "ZS": "soybean futures", "ZW": "wheat futures",
            "USO": "WTI crude oil", "UNG": "natural gas",
            "GDX": "gold miners",
        }
        return commodity_aliases.get(s, f"{s} commodity")
    if asset_class == "forex":
        if len(s) == 6:
            return f"{s[:3]}/{s[3:]} forex"
        return f"{s} forex"
    if asset_class == "index":
        index_aliases = {
            "SPX": "S&P 500", "SPY": "S&P 500", "NDX": "Nasdaq 100",
            "QQQ": "Nasdaq 100", "RUT": "Russell 2000", "IWM": "Russell 2000",
            "DJI": "Dow Jones", "DIA": "Dow Jones", "VIX": "VIX volatility",
        }
        return index_aliases.get(s, s)
    return s


def google_news_rss(query, max_items=30):
    q = urllib.parse.quote_plus(query)
    url = f"https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"
    try:
        req = urllib.request.Request(url, headers=HEADERS_HTML)
        with urllib.request.urlopen(req, timeout=15) as r:
            data = r.read()
    except Exception as e:
        sys.stderr.write(f"WARN: Google News RSS '{query}' failed: {e}\n")
        return []
    try:
        root = ET.fromstring(data)
    except ET.ParseError as e:
        sys.stderr.write(f"WARN: Google News RSS XML parse failed: {e}\n")
        return []

    items = []
    for item in root.findall(".//item")[:max_items]:
        title_raw = item.findtext("title") or ""
        # Google News titles are formatted "Headline - Source"; split on last " - "
        if " - " in title_raw:
            headline, source = title_raw.rsplit(" - ", 1)
        else:
            headline, source = title_raw, ""
        items.append({
            "headline": html.unescape(headline.strip()),
            "url": (item.findtext("link") or "").strip(),
            "datetime": (item.findtext("pubDate") or "").strip(),
            "source": source.strip(),
            "summary": "",  # description is HTML-formatted, skip for terseness
        })
    return items


# ---- Tier 2a: Finviz news widget (keyless, stock-specific) ----------------

# Finviz news rows have a date cell + anchor. Class names drift over time, so
# we anchor on the date FORMAT itself ("Apr-29-26 09:32AM" or "09:32AM"),
# which is distinctive enough to find anywhere in the HTML. Each anchor
# inherits the most-recent date pattern seen above it; time-only cells
# inherit the previous full-date row.

FINVIZ_NEWS_ANCHOR_RE = re.compile(
    r'<a[^>]*class="[^"]*tab-link-news[^"]*"[^>]*href="([^"]+)"[^>]*>([^<]+)</a>',
    re.IGNORECASE
)
FINVIZ_NEWS_SOURCE_RE = re.compile(
    r'<div[^>]*class="[^"]*news-link-right[^"]*"[^>]*>\s*<span[^>]*>\s*([^<]+?)\s*</span>',
    re.IGNORECASE
)
# Inline date patterns — match anywhere in the HTML (no class dependency).
# Full date: "Apr-29-26 09:32AM" — inside a > and < (text inside a tag)
FINVIZ_FULL_DATE_RE = re.compile(
    r'>\s*([A-Z][a-z]{2})-(\d{1,2})-(\d{2})\s+(\d{1,2}:\d{2}[AP]M)\s*<'
)
# Time-only: ">09:32AM<" — same-day continuation of the previous full date
FINVIZ_TIME_ONLY_RE = re.compile(r'>\s*(\d{1,2}:\d{2}[AP]M)\s*<')


def finviz_news(ticker):
    """Scrape the Finviz quote-page news widget. Position-aware: each anchor
    inherits the most-recent date pattern seen above it. Robust to class
    drift — anchors on the date FORMAT, not the cell class."""
    url = f"https://finviz.com/quote.ashx?t={ticker.upper()}"
    try:
        req = urllib.request.Request(url, headers=HEADERS_HTML)
        with urllib.request.urlopen(req, timeout=15) as r:
            page = r.read().decode("utf-8", errors="replace")
    except Exception as e:
        sys.stderr.write(f"WARN: Finviz news scrape {ticker} failed: {e}\n")
        return []

    # Find all news anchors (position + url + headline)
    anchors = [(m.start(), m.group(1), m.group(2)) for m in FINVIZ_NEWS_ANCHOR_RE.finditer(page)]
    if not anchors:
        return []

    # Restrict the date hunt to the news section. Use the first anchor's start
    # as a lower bound (dates above the news widget aren't relevant).
    news_section_start = max(0, anchors[0][0] - 5000)  # 5KB upstream window for the first row's date
    news_section = page[news_section_start:]

    # Build a list of (absolute_pos, iso_date) — full dates anchor the
    # date-context for following time-only entries. We resolve time-only
    # entries to the most-recent full date.
    date_events = []  # list of (abs_pos, iso_or_blank, is_full)
    for m in FINVIZ_FULL_DATE_RE.finditer(news_section):
        try:
            d = datetime.strptime(f"{m.group(1)}-{m.group(2)}-{m.group(3)}", "%b-%d-%y")
            date_events.append((news_section_start + m.start(), d.strftime("%Y-%m-%d"), True))
        except ValueError:
            continue
    for m in FINVIZ_TIME_ONLY_RE.finditer(news_section):
        # Skip if this time-only match overlaps a full-date match
        abs_pos = news_section_start + m.start()
        if any(abs(abs_pos - dp) < 25 for dp, _, _ in date_events):
            continue
        date_events.append((abs_pos, "", False))
    date_events.sort(key=lambda x: x[0])

    sources = [(m.start(), m.group(1)) for m in FINVIZ_NEWS_SOURCE_RE.finditer(page)]

    items = []
    last_full_date = ""
    src_idx = 0
    de_idx = 0
    for anchor_pos, link, title in anchors:
        # Walk date_events up to the anchor; pick the most-recent full date
        while de_idx < len(date_events) and date_events[de_idx][0] < anchor_pos:
            if date_events[de_idx][2]:  # full date — update context
                last_full_date = date_events[de_idx][1]
            de_idx += 1

        # Pair with the next source span at/after the anchor
        source = "Finviz"
        while src_idx < len(sources) and sources[src_idx][0] < anchor_pos:
            src_idx += 1
        if src_idx < len(sources):
            source = sources[src_idx][1].strip() or "Finviz"

        items.append({
            "headline": html.unescape(title.strip()),
            "url": link.strip(),
            "source": source,
            "datetime": last_full_date,
            "summary": "",
        })
    return items


# ---- Tier 2b: yfinance Ticker.news (keyless, stock-friendly) --------------

def yfinance_news(symbol):
    try:
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent))
        import _yfdata as yf
        t = yf.Ticker(symbol)
        raw = t.news or []
        out = []
        for n in raw[:20]:
            content = n.get("content", n)
            out.append({
                "headline": content.get("title"),
                "source": (
                    (content.get("provider") or {}).get("displayName")
                    if isinstance(content.get("provider"), dict)
                    else content.get("publisher")
                ),
                "datetime": content.get("pubDate") or content.get("providerPublishTime"),
                "url": (
                    (content.get("canonicalUrl") or {}).get("url")
                    if isinstance(content.get("canonicalUrl"), dict)
                    else content.get("link")
                ),
                "summary": content.get("summary") or content.get("description"),
            })
        return out
    except Exception as e:
        sys.stderr.write(f"WARN: yfinance news fallback failed: {e}\n")
        return []


# ---- Tier 3: Finnhub (key, optional) --------------------------------------

def _finnhub_get(path, **params):
    if not FINNHUB_TOKEN:
        return None
    params["token"] = FINNHUB_TOKEN
    url = f"https://finnhub.io/api/v1/{path}?" + urllib.parse.urlencode(params)
    try:
        req = urllib.request.Request(url, headers=HEADERS_JSON)
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:
        sys.stderr.write(f"WARN: Finnhub {path} failed: {e}\n")
        return None


def finnhub_price_target(symbol):
    return _finnhub_get("stock/price-target", symbol=symbol)


def finnhub_recommendation(symbol):
    return _finnhub_get("stock/recommendation", symbol=symbol)


def finnhub_earnings_calendar(symbol):
    today = datetime.now(timezone.utc).date()
    return _finnhub_get(
        "calendar/earnings",
        symbol=symbol,
        **{"from": today.isoformat(), "to": (today + timedelta(days=180)).isoformat()},
    )


# ---- Categorization heuristic ---------------------------------------------

ANALYST_KEYWORDS = (
    "upgrade", "downgrade", "initiate", "price target", "raises target",
    "cuts target", "buy rating", "sell rating", "outperform", "underperform",
    "analyst", "consensus", "estimate", "reiterates",
)
MACRO_KEYWORDS = (
    "fed", "fomc", "cpi", "ppi", "pce", "nfp", "jobs", "unemployment", "rate cut",
    "rate hike", "inflation", "recession", "treasury", "yield", "powell", "chair",
    "hawkish", "dovish", "central bank", "ecb", "boj", "boe",
)
SECTOR_KEYWORDS = ("sector", "peer", "industry", "competitor", "rivals", "compete")
CATALYST_KEYWORDS = (
    "earnings", "guidance", "guides", "raises", "misses", "beats",
    "merger", "acquir", "buyback", "dividend", "split",
    "approval", "fda", "lawsuit", "settlement", "subpoena", "regulatory",
    "ceo", "cfo", "executive", "board", "resign", "appoint",
    "launch", "product", "partnership", "deal", "contract",
)


def categorize(headline):
    if not headline:
        return "uncategorized"
    h = headline.lower()
    if any(k in h for k in ANALYST_KEYWORDS):
        return "analyst"
    if any(k in h for k in MACRO_KEYWORDS):
        return "macro"
    if any(k in h for k in SECTOR_KEYWORDS):
        return "sector"
    if any(k in h for k in CATALYST_KEYWORDS):
        return "catalyst"
    return "other"


def dedupe_by_headline(items):
    seen = set()
    out = []
    for n in items:
        key = (n.get("headline") or "").lower().strip()[:80]
        if key and key not in seen:
            seen.add(key)
            out.append(n)
    return out


# ---- Rendering ------------------------------------------------------------

def _fmt_dt(s):
    if s is None or s == "":
        return ""
    try:
        if isinstance(s, (int, float)):
            return datetime.fromtimestamp(s, tz=timezone.utc).strftime("%Y-%m-%d")
        ss = str(s)
        # Try common formats
        for fmt in ("%a, %d %b %Y %H:%M:%S %Z",  # RFC 822 (Google News)
                    "%Y-%m-%dT%H:%M:%S%z",       # ISO
                    "%Y-%m-%d %H:%M:%S",
                    "%Y-%m-%d"):
            try:
                return datetime.strptime(ss[:len(fmt) + 5], fmt).strftime("%Y-%m-%d")
            except ValueError:
                continue
        if "T" in ss:
            return ss.split("T")[0]
        if " " in ss:
            return ss.split(" ")[0]
        return ss[:10]
    except Exception:
        return str(s)[:10]


def render_markdown(symbol, asset_class, news, price_targets, recommendations, earnings_cal, days, sources_used):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        f"# {symbol} — News & Analyst Context ({now})",
        f"_Asset class: {asset_class} · lookback: {days} days · sources used: {' + '.join(sources_used) or '(none — all tiers failed)'}_",
        "",
    ]
    add = lines.append

    buckets = {"catalyst": [], "analyst": [], "sector": [], "macro": [], "other": []}
    if news:
        for n in news:
            cat = categorize(n.get("headline", ""))
            buckets[cat].append(n)

    # Catalysts
    add("## Catalysts (last 30 days)")
    if buckets["catalyst"]:
        for n in buckets["catalyst"][:8]:
            d = _fmt_dt(n.get("datetime"))
            src = n.get("source") or "?"
            url = n.get("url") or "#"
            add(f"- {d}: [{n.get('headline')}]({url}) — {src}")
    else:
        add("- _No catalyst-tagged headlines surfaced. Use WebSearch to fill: '<TICKER> earnings', '<TICKER> guidance', '<TICKER> news'._")
    add("")

    # Analyst
    add("## Analyst targets / sentiment")
    if price_targets and isinstance(price_targets, dict) and price_targets.get("targetMean"):
        pt = price_targets
        add(f"- **Consensus mean target:** ${pt.get('targetMean'):.2f} "
            f"(median ${pt.get('targetMedian', 0):.2f}, high ${pt.get('targetHigh', 0):.2f}, low ${pt.get('targetLow', 0):.2f})")
        add(f"- {pt.get('numberOfAnalysts', '?')} analysts · last update {_fmt_dt(pt.get('lastUpdated'))}")
    if recommendations and isinstance(recommendations, list) and recommendations:
        latest = recommendations[0]
        add(f"- **Recommendation distribution ({_fmt_dt(latest.get('period'))}):** "
            f"Strong Buy {latest.get('strongBuy', 0)} · Buy {latest.get('buy', 0)} · "
            f"Hold {latest.get('hold', 0)} · Sell {latest.get('sell', 0)} · "
            f"Strong Sell {latest.get('strongSell', 0)}")
        if len(recommendations) >= 2:
            prior = recommendations[1]
            buy_now = (latest.get('strongBuy', 0) + latest.get('buy', 0))
            buy_prior = (prior.get('strongBuy', 0) + prior.get('buy', 0))
            add(f"- Trend vs {_fmt_dt(prior.get('period'))}: Buy/Strong-Buy {buy_prior} → {buy_now} "
                f"({'+' if buy_now > buy_prior else ''}{buy_now - buy_prior})")
    if buckets["analyst"]:
        add("- Recent analyst-tagged headlines:")
        for n in buckets["analyst"][:6]:
            d = _fmt_dt(n.get("datetime"))
            src = n.get("source") or "?"
            url = n.get("url") or "#"
            add(f"  - {d}: [{n.get('headline')}]({url}) — {src}")
    if not (price_targets or recommendations or buckets["analyst"]):
        add("- _No analyst data surfaced. Use WebSearch: 'Goldman <TICKER> price target', 'JPM <TICKER> rating', or check Yahoo Finance analyst tab._")
    add("")

    # Sector / peer
    add("## Sector / peer context")
    if buckets["sector"]:
        for n in buckets["sector"][:4]:
            d = _fmt_dt(n.get("datetime"))
            src = n.get("source") or "?"
            url = n.get("url") or "#"
            add(f"- {d}: [{n.get('headline')}]({url}) — {src}")
    else:
        add("- _Use WebSearch to fill: name 1–2 closest peers and check their recent price-relevant news._")
    add("")

    # Macro overlay
    add("## Macro overlay")
    if buckets["macro"]:
        for n in buckets["macro"][:5]:
            d = _fmt_dt(n.get("datetime"))
            src = n.get("source") or "?"
            url = n.get("url") or "#"
            add(f"- {d}: [{n.get('headline')}]({url}) — {src}")
    else:
        add("- _Cross-reference `scanned/MACRO/current.md` for the regime + active modifiers._")
    add("")

    # Earnings calendar (Finnhub-only)
    if asset_class == "stock" and earnings_cal:
        add("## Next earnings (with AMC/BMO timing — closes Yahoo gap)")
        cal = earnings_cal.get("earningsCalendar", []) if isinstance(earnings_cal, dict) else []
        if cal:
            next_e = cal[0]
            hour_map = {"bmo": "BMO (pre-market)", "amc": "AMC (after-close)", "dmh": "during market hours"}
            hour_text = hour_map.get((next_e.get("hour") or "").lower(), next_e.get("hour") or "?")
            add(f"- **Next earnings:** {next_e.get('date')} **{hour_text}**")
            if next_e.get("epsEstimate") is not None:
                add(f"- Consensus EPS estimate: ${next_e.get('epsEstimate'):.2f}")
            if next_e.get("revenueEstimate") is not None:
                add(f"- Consensus revenue estimate: ${next_e.get('revenueEstimate') / 1e9:.2f}B")
        else:
            add("- _No earnings within 180 days._")
        add("")
    elif asset_class == "stock":
        add("## Next earnings")
        add("- _AMC/BMO timing requires `FINNHUB_TOKEN` (free at finnhub.io/register). Without it, fall back to Finviz `Earnings` row on the quote page._")
        add("")

    # Other / uncategorized
    if buckets["other"]:
        add("## Other recent headlines")
        for n in buckets["other"][:6]:
            d = _fmt_dt(n.get("datetime"))
            src = n.get("source") or "?"
            url = n.get("url") or "#"
            add(f"- {d}: [{n.get('headline')}]({url}) — {src}")
        add("")

    # Required-coverage checklist
    add("## Required-category coverage check (per `guide/scan/data.md` § Step 8)")
    required_per_class = {
        "stock": ["catalyst", "analyst", "sector", "macro", "insider-13F", "earnings-call"],
        "crypto": ["ETF-flow", "regulatory", "on-chain", "macro", "sector-peer", "major-holder"],
        "index": ["Fed", "breadth", "VIX", "earnings-tail", "geopolitical", "sentiment-surveys"],
        "forex": ["central-bank-speak", "rate-diff", "data-prints", "geopolitical", "positioning"],
        "commodity": ["supply-side", "demand-side", "geopolitical", "analyst-target", "inventory-curve", "seasonality"],
    }
    for cat in required_per_class.get(asset_class, []):
        add(f"- [ ] {cat}")
    add("")
    add("**The scan author (LLM)** must walk this list and either cite a source for each, or explicitly mark `N/A — <reason>` per item. Missing categories without a justification = scan incomplete.")

    return "\n".join(lines)


# ---- Main -----------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__.strip().split("\n")[0])
    ap.add_argument("symbol")
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--asset-class", choices=("stock", "crypto", "forex", "index", "commodity", "auto"), default="auto")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    sym = args.symbol.upper()
    asset_class = detect_asset_class(sym) if args.asset_class == "auto" else args.asset_class
    sources_used = []

    # Tier 1: Google News RSS (always try first — universal, keyless)
    query = google_news_query_for(sym, asset_class)
    news = google_news_rss(query, max_items=30)
    if news:
        sources_used.append("Google News RSS")

    # Tier 2: stock-specific keyless additions
    if asset_class == "stock":
        finviz_items = finviz_news(sym)
        if finviz_items:
            news = dedupe_by_headline(news + finviz_items)
            sources_used.append("Finviz")
        if not news:
            # Last keyless fallback
            yf_items = yfinance_news(sym)
            if yf_items:
                news = yf_items
                sources_used.append("yfinance")

    # Tier 3: Finnhub (optional richer analyst data)
    price_targets = recommendations = earnings_cal = None
    if FINNHUB_TOKEN and asset_class == "stock":
        price_targets = finnhub_price_target(sym)
        recommendations = finnhub_recommendation(sym)
        earnings_cal = finnhub_earnings_calendar(sym)
        if any((price_targets, recommendations, earnings_cal)):
            sources_used.append("Finnhub")

    if not news and not (price_targets or recommendations or earnings_cal):
        print(f"WARN: no news returned for {sym} from any tier", file=sys.stderr)
        # Don't exit 1 — still emit the checklist scaffold so the LLM knows what to fill

    if args.json:
        print(json.dumps({
            "symbol": sym,
            "asset_class": asset_class,
            "days": args.days,
            "sources_used": sources_used,
            "news": news,
            "price_targets": price_targets,
            "recommendations": recommendations,
            "earnings_calendar": earnings_cal,
        }, default=str, indent=2))
        return 0

    print(render_markdown(sym, asset_class, news, price_targets, recommendations, earnings_cal, args.days, sources_used))
    return 0


if __name__ == "__main__":
    sys.exit(main())
