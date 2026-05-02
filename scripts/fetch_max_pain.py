#!/usr/bin/env python3
"""
fetch_max_pain.py — local max-pain calculator using Yahoo options chains.

Replaces the ChartExchange max-pain WebFetch in the Flow & Squeeze section.
Pulls options chains for upcoming OPEX dates, computes max pain (the strike
that would inflict the largest aggregate dollar loss on long-option holders
at expiry), and reports the magnetic level + total OI per OPEX.

Definition of max pain:
    For each candidate strike K, compute Σ_calls max(S−K, 0) × OI_call
                                       + Σ_puts  max(K−S, 0) × OI_put
    where S = candidate strike. The strike that minimizes this total is max pain
    — where option writers (dealers) lose the least and longs lose the most.

Real-time freshness: max pain is computed live from current OI; no FINRA / SEC
lag floor. Use the value as-of the data fetch.

Usage:
    .venv/bin/python scripts/fetch_max_pain.py RIVN
    .venv/bin/python scripts/fetch_max_pain.py RIVN --opex=4   # next 4 expiries
    .venv/bin/python scripts/fetch_max_pain.py RIVN --json

Exit codes:
    0 — success
    1 — no options chain available
    2 — dependency / runtime error
"""

import argparse
import json
import re
import sys
import urllib.request
from datetime import datetime, timezone


UA_BROWSER = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)
HEADERS_HTML = {"User-Agent": UA_BROWSER, "Accept": "text/html,application/xhtml+xml"}


def _import_deps():
    try:
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent))
        import _yfdata as yf
        return yf
    except ImportError as e:
        print(f"ERROR: dependency missing — {e}", file=sys.stderr)
        sys.exit(2)


def _try_yfinance_direct(ticker, opex_count):
    """Fallback: use the `yfinance` package directly (different backend than
    yahooquery). Returns (results_list, current_price) or (None, None)."""
    try:
        import yfinance as yfin
    except ImportError:
        return None, None
    try:
        t = yfin.Ticker(ticker)
        info = t.info or {}
        expiries = t.options or []
        if not expiries:
            return None, None
        price = info.get("currentPrice") or info.get("regularMarketPrice")
        results = []
        for opex in expiries[:opex_count]:
            try:
                chain = t.option_chain(opex)
                mp, call_oi, put_oi, pc = compute_max_pain(chain.calls, chain.puts)
                results.append({
                    "opex": opex, "max_pain": mp,
                    "call_oi": call_oi, "put_oi": put_oi, "pc_oi": pc,
                })
            except Exception as e:
                results.append({"opex": opex, "error": str(e)})
        return results, price
    except Exception as e:
        sys.stderr.write(f"WARN: yfinance-direct fallback failed: {e}\n")
        return None, None


# ChartExchange options-summary regex patterns.
# The page prints max-pain values with their OPEX dates inside table-ish HTML.
# We search for "$XX.XX" amounts that appear near a date string and the
# "Max Pain" / "MaxPain" label. Patterns tried in order of specificity.
CE_MAXPAIN_INLINE_JSON_RE = re.compile(
    r'["\']max[_-]?pain["\']\s*:\s*(\d+(?:\.\d+)?)',
    re.IGNORECASE
)
# Pattern: <date> ... <max-pain $value> within a small HTML window
CE_MAXPAIN_PAIRED_RE = re.compile(
    r'(\d{4}-\d{2}-\d{2})[^<]{0,40}.{0,400}?\$\s*(\d+(?:\.\d+)?)',
    re.IGNORECASE | re.DOTALL
)
# Total OI patterns
CE_TOTAL_CALL_OI_RE = re.compile(
    r'(?:total\s*calls?|call\s*OI)[^<]{0,80}([\d,]+)',
    re.IGNORECASE | re.DOTALL
)
CE_TOTAL_PUT_OI_RE = re.compile(
    r'(?:total\s*puts?|put\s*OI)[^<]{0,80}([\d,]+)',
    re.IGNORECASE | re.DOTALL
)


def _try_chartexchange(ticker, opex_count):
    """Fallback: scrape ChartExchange options-summary page. Returns
    (results_list, None) or (None, None). Tries nasdaq, then nyse, then nyseamerican."""
    for exchange in ("nasdaq", "nyse", "nyseamerican"):
        url = f"https://chartexchange.com/symbol/{exchange}-{ticker.lower()}/optionchain/summary/"
        try:
            req = urllib.request.Request(url, headers=HEADERS_HTML)
            with urllib.request.urlopen(req, timeout=20) as r:
                page = r.read().decode("utf-8", errors="replace")
        except Exception as e:
            sys.stderr.write(f"WARN: ChartExchange {exchange}-{ticker} failed: {e}\n")
            continue
        # Verify the page is for this ticker (not a 404 fallback)
        if ticker.lower() not in page.lower():
            continue
        return _parse_chartexchange(page, opex_count, url)
    return None, None


def _parse_chartexchange(page, opex_count, source_url):
    """Best-effort regex extraction of max-pain values from a ChartExchange page."""
    results = []
    # First try inline JSON (cleanest)
    inline = CE_MAXPAIN_INLINE_JSON_RE.findall(page)
    if inline:
        for i, val in enumerate(inline[:opex_count]):
            try:
                results.append({"opex": f"OPEX-{i+1}", "max_pain": float(val),
                                "call_oi": None, "put_oi": None, "pc_oi": None,
                                "source": "ChartExchange (inline JSON)"})
            except ValueError:
                continue
        if results:
            return results, None

    # Otherwise try date-paired search — date YYYY-MM-DD followed by a $ value
    paired = CE_MAXPAIN_PAIRED_RE.findall(page[:200_000])  # cap at 200KB
    seen = set()
    for date_str, val_str in paired[:50]:
        if date_str in seen:
            continue
        seen.add(date_str)
        try:
            results.append({"opex": date_str, "max_pain": float(val_str),
                            "call_oi": None, "put_oi": None, "pc_oi": None,
                            "source": "ChartExchange (date-paired regex)"})
        except ValueError:
            continue
        if len(results) >= opex_count:
            break

    if not results:
        return None, None

    # Try to capture total Call/Put OI for the page (single values across whole chain)
    call_oi_match = CE_TOTAL_CALL_OI_RE.search(page)
    put_oi_match = CE_TOTAL_PUT_OI_RE.search(page)
    if call_oi_match and put_oi_match:
        try:
            call_oi = float(call_oi_match.group(1).replace(",", ""))
            put_oi = float(put_oi_match.group(1).replace(",", ""))
            pc = put_oi / call_oi if call_oi else None
            # Backfill on first row only (page-level totals, not per-OPEX)
            results[0]["call_oi"] = call_oi
            results[0]["put_oi"] = put_oi
            results[0]["pc_oi"] = pc
        except ValueError:
            pass

    return results, None


def compute_max_pain(calls, puts):
    """Given calls & puts DataFrames with `strike` and `openInterest`, return
    (max_pain_strike, total_oi_calls, total_oi_puts, pc_ratio_oi)."""
    strikes = sorted(set(calls["strike"].tolist()) | set(puts["strike"].tolist()))
    if not strikes:
        return None, 0, 0, None

    call_oi = dict(zip(calls["strike"], calls["openInterest"].fillna(0)))
    put_oi = dict(zip(puts["strike"], puts["openInterest"].fillna(0)))

    best_strike = None
    best_loss = None
    for k in strikes:
        # Total dollar loss to longs if expires at strike k
        loss = 0.0
        for s, oi in call_oi.items():
            if s < k:
                loss += (k - s) * oi
        for s, oi in put_oi.items():
            if s > k:
                loss += (s - k) * oi
        if best_loss is None or loss < best_loss:
            best_loss = loss
            best_strike = k

    total_call_oi = float(sum(call_oi.values()))
    total_put_oi = float(sum(put_oi.values()))
    pc = total_put_oi / total_call_oi if total_call_oi else None
    return best_strike, total_call_oi, total_put_oi, pc


def render_markdown(ticker, current_price, results):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        f"# {ticker} — Max pain pre-compute ({now})",
        f"_Spot ${current_price:.2f} (yfinance)_" if current_price else "_Spot price unavailable_",
        "",
        "Max pain is the strike at which **dealers lose the least** and **longs lose the most** "
        "if every option expires at that price. Acts as a magnetic level into OPEX.",
        "",
        "| OPEX | Max pain | Spot vs MP | Total Call OI | Total Put OI | P/C OI ratio |",
        "|---|---|---|---|---|---|",
    ]
    for r in results:
        if not r:
            continue
        if r.get("error"):
            lines.append(f"| {r['opex']} | _{r['error']}_ | — | — | — | — |")
            continue
        spot_vs_mp = ""
        if current_price and r["max_pain"]:
            diff_pct = (current_price - r["max_pain"]) / r["max_pain"] * 100
            spot_vs_mp = f"{diff_pct:+.2f}%"
        lines.append(
            f"| {r['opex']} | **${r['max_pain']:.2f}** | {spot_vs_mp} | "
            f"{r['call_oi']:,.0f} | {r['put_oi']:,.0f} | "
            f"{r['pc_oi']:.2f}" if r["pc_oi"] is not None else "n/a"
        )
        # Append last column manually since we use a conditional
        if r["pc_oi"] is None:
            lines[-1] = lines[-1].rsplit("|", 1)[0] + "| n/a |"
        else:
            lines[-1] = lines[-1] + " |"
    lines.append("")
    lines.append("## Interpretation guide")
    lines.append("- **Spot above max pain** → magnetic pull DOWN into OPEX (dealer hedging gravity)")
    lines.append("- **Spot below max pain** → magnetic pull UP into OPEX")
    lines.append("- **P/C OI > 1.0** → puts outweigh calls; bearish positioning OR hedging demand")
    lines.append("- **P/C OI < 0.7** → calls outweigh puts; bullish positioning OR call-walls forming")
    lines.append("")
    lines.append("## Fallback")
    lines.append("- ChartExchange (`chartexchange.com/symbol/<EX>-<TICKER>/optionchain/summary/`) — same data, separate compute, useful for cross-confirmation")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__.strip().split("\n")[0])
    ap.add_argument("ticker")
    ap.add_argument("--opex", type=int, default=4, help="number of upcoming OPEX dates to compute (default 4)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    yf = _import_deps()
    source_used = "yahooquery"
    try:
        t = yf.Ticker(args.ticker)
        info = t.info or {}
    except Exception as e:
        print(f"ERROR: ticker fetch failed: {e}", file=sys.stderr)
        return 2

    current_price = info.get("currentPrice") or info.get("regularMarketPrice")

    try:
        expiries = t.options or []
    except Exception:
        expiries = []

    results = []
    if expiries:
        for opex in expiries[:args.opex]:
            try:
                chain = t.option_chain(opex)
                mp, call_oi, put_oi, pc = compute_max_pain(chain.calls, chain.puts)
                results.append({
                    "opex": opex, "max_pain": mp,
                    "call_oi": call_oi, "put_oi": put_oi, "pc_oi": pc,
                })
            except Exception as e:
                results.append({"opex": opex, "error": str(e)})

    # Tier 2 fallback: yfinance package directly (different backend)
    if not results or all(r.get("max_pain") is None for r in results):
        sys.stderr.write("INFO: yahooquery options chain empty/failed; trying yfinance direct...\n")
        yfres, yfprice = _try_yfinance_direct(args.ticker, args.opex)
        if yfres:
            results = yfres
            source_used = "yfinance-direct"
            if not current_price and yfprice:
                current_price = yfprice

    # Tier 3 fallback: scrape ChartExchange
    if not results or all(r.get("max_pain") is None for r in results):
        sys.stderr.write("INFO: yfinance options unavailable; trying ChartExchange scrape...\n")
        ceres, _ = _try_chartexchange(args.ticker, args.opex)
        if ceres:
            results = ceres
            source_used = "ChartExchange"

    if not results:
        print(
            f"ERROR: no max-pain data for {args.ticker} from any source.\n"
            f"       Manual fallback — WebFetch:\n"
            f"       https://chartexchange.com/symbol/nasdaq-{args.ticker.lower()}/optionchain/summary/",
            file=sys.stderr,
        )
        return 1

    if args.json:
        print(json.dumps({
            "ticker": args.ticker.upper(),
            "spot": current_price,
            "source": source_used,
            "results": results,
        }, default=str, indent=2))
        return 0

    md = render_markdown(args.ticker.upper(), current_price, results)
    md = md.replace(
        "_Spot ${:.2f} (yfinance)_".format(current_price) if current_price else "_Spot price unavailable_",
        f"_Spot ${current_price:.2f} ({source_used})_" if current_price else f"_Spot price unavailable · source: {source_used}_",
    )
    print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
