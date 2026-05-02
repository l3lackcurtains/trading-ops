#!/usr/bin/env python3
"""
fetch_quote.py — local Yahoo Finance quote fetcher for /scan stocks.

Replaces the Finviz + Stockanalysis WebFetches in the scan flow for ~98% of
fields. Returns structured markdown ready to paste into a scan, plus a numeric
auto-reject pre-check so the LLM can short-circuit Pillar 1 failures.

Backed by Yahoo Finance via `scripts/_yfdata.py`.

Output sections (markdown by default):
    - Auto-reject check (Pillar 1 numeric gate)
    - 3-consecutive-Q growth check (Pillar 2 + Pillar 6 high-conviction gate input)
    - Price & valuation
    - Profitability & returns
    - Growth metrics
    - Balance sheet
    - Shares & ownership
    - Short interest
    - Computed technicals (SMA20/RSI/ATR/RelVol)
    - Dividend
    - Analyst
    - Calendar (next earnings)
    - Recent news (last 5 headlines)
    - Yahoo gaps (what still needs Finviz/other fallback if relevant)

Usage:
    python3 scripts/fetch_quote.py RIVN
    python3 scripts/fetch_quote.py RIVN --json
    python3 scripts/fetch_quote.py RIVN --auto-reject-only

Exit codes:
    0 — success
    1 — ticker not found / no data returned
    2 — dependency missing or runtime error
    3 — auto-reject triggered (only with --auto-reject-only)
"""

import argparse
import json
import math
import sys
from datetime import datetime, timezone


def _import_deps():
    try:
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent))
        import _yfdata as yf
        import pandas as pd
        return yf, pd
    except ImportError as e:
        print(f"ERROR: dependency missing — {e}", file=sys.stderr)
        print("Install with: uv pip install yahooquery pandas", file=sys.stderr)
        sys.exit(2)


# --- formatters ---

def _pct(x, digits=2):
    """Format a fraction (0.45) or percent (45.0) as a percent string."""
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "n/a"
    # yfinance uses fractions for most ratio fields (0.45 = 45%)
    return f"{x * 100:+.{digits}f}%" if abs(x) < 5 else f"{x:+.{digits}f}%"


def _num(x, digits=2, prefix="", suffix=""):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "n/a"
    return f"{prefix}{x:,.{digits}f}{suffix}"


def _money(x, digits=2):
    if x is None:
        return "n/a"
    if abs(x) >= 1e9:
        return f"${x / 1e9:.{digits}f}B"
    if abs(x) >= 1e6:
        return f"${x / 1e6:.{digits}f}M"
    if abs(x) >= 1e3:
        return f"${x / 1e3:.{digits}f}K"
    return f"${x:.{digits}f}"


def _ratio_pct(x, digits=2):
    """For values yfinance returns as decimals representing %, like grossMargins=0.42."""
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "n/a"
    return f"{x * 100:+.{digits}f}%"


# --- compute helpers ---

def compute_rsi(close, period=14):
    """Wilder's RSI — return last value or None."""
    if len(close) < period + 1:
        return None
    delta = close.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.ewm(alpha=1 / period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, 1e-10)
    rsi = 100 - (100 / (1 + rs))
    val = rsi.iloc[-1]
    return float(val) if val == val else None


def compute_atr(history, period=14):
    """Standard ATR — return last value or None. Expects DataFrame with High/Low/Close."""
    if len(history) < period + 1:
        return None
    h, l, c = history["High"], history["Low"], history["Close"]
    tr1 = h - l
    tr2 = (h - c.shift()).abs()
    tr3 = (l - c.shift()).abs()
    import pandas as pd
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1 / period, adjust=False).mean().iloc[-1]
    return float(atr) if atr == atr else None


def compute_sma(close, period):
    if len(close) < period:
        return None
    val = close.rolling(period).mean().iloc[-1]
    return float(val) if val == val else None


def compute_roic_estimate(info, fin_stmt, balance_sheet):
    """ROIC ≈ NOPAT / Invested Capital where NOPAT = EBIT × (1 - tax_rate),
    IC = totalDebt + totalEquity. Returns fraction or None."""
    try:
        # Try to get EBIT from income statement
        ebit = None
        for label in ("EBIT", "Operating Income", "OperatingIncome"):
            if label in fin_stmt.index:
                ebit = fin_stmt.loc[label].iloc[0]
                break
        if ebit is None or ebit != ebit:
            ebit = info.get("ebitda")
            if ebit:
                # crude: EBIT ≈ EBITDA × 0.7 if no D&A available; mark as rough
                ebit = ebit * 0.7

        # Tax rate — try to compute from income statement; default to 21% (US corp)
        tax_rate = 0.21
        try:
            pretax = fin_stmt.loc["Pretax Income"].iloc[0] if "Pretax Income" in fin_stmt.index else None
            tax = fin_stmt.loc["Tax Provision"].iloc[0] if "Tax Provision" in fin_stmt.index else None
            if pretax and tax and pretax > 0:
                tax_rate = max(0.0, min(0.5, tax / pretax))
        except Exception:
            pass

        nopat = ebit * (1 - tax_rate) if ebit is not None else None

        # Invested capital = totalDebt + totalEquity
        ic = (info.get("totalDebt") or 0) + (info.get("totalStockholderEquity") or info.get("bookValue", 0) * (info.get("sharesOutstanding") or 0))
        if not ic or ic <= 0:
            return None

        if nopat is None:
            return None
        return float(nopat / ic)
    except Exception:
        return None


def consecutive_quarters_growth(quarterly_inc_stmt, rev_threshold=0.20, eps_threshold=0.25):
    """Check the 3 most-recent quarters vs the same quarter prior year.
    Returns dict: {quarters_meeting_both: int, details: [(date, rev_growth, eps_growth, both_met)]}"""
    if quarterly_inc_stmt is None or quarterly_inc_stmt.empty:
        return None
    df = quarterly_inc_stmt
    rev_label = next((l for l in ("Total Revenue", "TotalRevenue", "Revenue") if l in df.index), None)
    eps_label = next((l for l in ("Diluted EPS", "DilutedEPS", "Basic EPS", "BasicEPS") if l in df.index), None)
    if not rev_label:
        return None

    cols = list(df.columns)  # quarters, most-recent first
    if len(cols) < 5:  # need 4 quarters of history + 1 to compare = 5 total
        return None

    details = []
    for i in range(min(3, len(cols) - 4)):
        cur, prev = cols[i], cols[i + 4]
        try:
            rev_cur, rev_prev = df.loc[rev_label, cur], df.loc[rev_label, prev]
            rev_g = (rev_cur - rev_prev) / abs(rev_prev) if rev_prev else None
        except Exception:
            rev_g = None
        eps_g = None
        if eps_label:
            try:
                eps_cur, eps_prev = df.loc[eps_label, cur], df.loc[eps_label, prev]
                if eps_prev and eps_prev != 0:
                    eps_g = (eps_cur - eps_prev) / abs(eps_prev)
            except Exception:
                pass
        rev_ok = rev_g is not None and rev_g >= rev_threshold
        eps_ok = eps_g is not None and eps_g >= eps_threshold
        details.append({
            "quarter_end": str(cur)[:10],
            "rev_yoy": rev_g,
            "eps_yoy": eps_g,
            "rev_meets": rev_ok,
            "eps_meets": eps_ok,
            "both_met": rev_ok and eps_ok,
        })
    quarters_meeting_both = sum(1 for d in details if d["both_met"])
    return {"quarters_meeting_both": quarters_meeting_both, "details": details}


# --- main fetch ---

def fetch_all(ticker_str, yf, pd):
    t = yf.Ticker(ticker_str)
    info = {}
    try:
        info = t.info or {}
    except Exception as e:
        print(f"WARN: info fetch failed: {e}", file=sys.stderr)
    if not info or not info.get("symbol"):
        return None

    history = t.history(period="1y", auto_adjust=False)
    quarterly_inc_stmt = None
    annual_inc_stmt = None
    balance_sheet = None
    try:
        quarterly_inc_stmt = t.quarterly_income_stmt
    except Exception:
        pass
    try:
        annual_inc_stmt = t.income_stmt
    except Exception:
        pass
    try:
        balance_sheet = t.balance_sheet
    except Exception:
        pass

    news = []
    try:
        raw_news = t.news or []
        for n in raw_news[:5]:
            content = n.get("content", n)
            news.append({
                "title": content.get("title"),
                "publisher": (content.get("provider") or {}).get("displayName") if isinstance(content.get("provider"), dict) else content.get("publisher"),
                "date": content.get("pubDate") or content.get("providerPublishTime"),
                "url": (content.get("canonicalUrl") or {}).get("url") if isinstance(content.get("canonicalUrl"), dict) else content.get("link"),
            })
    except Exception:
        pass

    # technicals
    sma20 = sma50 = sma200 = rsi = atr = rel_vol = None
    if history is not None and not history.empty:
        close = history["Close"]
        sma20 = compute_sma(close, 20)
        sma50 = compute_sma(close, 50) or info.get("fiftyDayAverage")
        sma200 = compute_sma(close, 200) or info.get("twoHundredDayAverage")
        rsi = compute_rsi(close, 14)
        atr = compute_atr(history, 14)
        avg_vol = info.get("averageVolume") or info.get("averageVolume10days")
        today_vol = info.get("volume") or (history["Volume"].iloc[-1] if len(history) else None)
        if avg_vol and today_vol:
            rel_vol = today_vol / avg_vol

    # ROIC estimate
    roic = compute_roic_estimate(info, annual_inc_stmt if annual_inc_stmt is not None else pd.DataFrame(), balance_sheet)

    # 3-consec-Q growth
    growth_check = consecutive_quarters_growth(quarterly_inc_stmt)

    return {
        "ticker": ticker_str.upper(),
        "info": info,
        "sma20": sma20,
        "sma50": sma50,
        "sma200": sma200,
        "rsi": rsi,
        "atr": atr,
        "rel_vol": rel_vol,
        "roic_estimate": roic,
        "growth_check": growth_check,
        "news": news,
    }


def auto_reject_check(data):
    """Returns (triggered: bool, reasons: list[str])."""
    reasons = []
    info = data["info"]
    gm = info.get("grossMargins")
    if gm is not None and gm < 0:
        reasons.append(f"gross margin {_ratio_pct(gm)} < 0")
    roic = data.get("roic_estimate")
    if roic is not None and roic < 0:
        reasons.append(f"ROIC estimate {_ratio_pct(roic)} < 0 (Yahoo gap; computed from EBIT/IC)")
    return (len(reasons) > 0, reasons)


def render_markdown(data):
    info = data["info"]
    ticker = data["ticker"]
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    triggered, reasons = auto_reject_check(data)
    g = data.get("growth_check") or {}
    gd = g.get("details", []) if g else []

    lines = []
    add = lines.append
    add(f"# {ticker} — Yahoo quote ({now})")
    add(f"_{info.get('longName') or info.get('shortName') or ''} · {info.get('sector') or ''} / {info.get('industry') or ''}_")
    add("")

    # ---------- Auto-reject ----------
    add("## Auto-reject pre-check (Pillar 1 numeric gate)")
    if triggered:
        add(f"**🚨 AUTO-REJECT TRIGGERED** — Pos S (numeric)")
        for r in reasons:
            add(f"- {r}")
    else:
        add("**No numeric auto-reject** — Pillar 1 needs full LLM scoring.")
        add(f"- Gross margin: {_ratio_pct(info.get('grossMargins'))}")
        add(f"- ROIC estimate: {_ratio_pct(data.get('roic_estimate'))} _(Yahoo gap; computed from EBIT/IC; Finviz fallback if borderline)_")
    add("")

    # ---------- 3-Q growth ----------
    add("## 3-consecutive-Q growth check (Pillar 2 high-conviction gate input)")
    if not g:
        add("- _Quarterly statements unavailable from yfinance_")
    else:
        add(f"**Quarters meeting both rev ≥ +20% AND EPS ≥ +25% YoY:** {g['quarters_meeting_both']} of {len(gd)}")
        for d in gd:
            add(f"- Q-end {d['quarter_end']}: rev {_ratio_pct(d['rev_yoy'])} {'✓' if d['rev_meets'] else '✗'} · EPS {_ratio_pct(d['eps_yoy'])} {'✓' if d['eps_meets'] else '✗'}")
        add("- Combined with 13F holder-count rising MRQ → eligible for Positional **T** (per `guide/scan/scorecard.md` § High-conviction)")
    add("")

    # ---------- Price & valuation ----------
    add("## Price & valuation")
    add("| Field | Value |")
    add("|---|---|")
    add(f"| Price | {_money(info.get('currentPrice'))} |")
    add(f"| Day change | {_pct(info.get('regularMarketChangePercent'))} |")
    add(f"| Market cap | {_money(info.get('marketCap'))} |")
    add(f"| 52w range | {_money(info.get('fiftyTwoWeekLow'))} – {_money(info.get('fiftyTwoWeekHigh'))} |")
    add(f"| Beta | {_num(info.get('beta'))} |")
    add(f"| P/E (TTM) | {_num(info.get('trailingPE'))} |")
    add(f"| Forward P/E | {_num(info.get('forwardPE'))} |")
    add(f"| P/S | {_num(info.get('priceToSalesTrailing12Months'))} |")
    add(f"| P/B | {_num(info.get('priceToBook'))} |")
    add(f"| PEG | {_num(info.get('pegRatio'))} |")
    add("")

    # ---------- Profitability ----------
    add("## Profitability & returns")
    add("| Field | Value |")
    add("|---|---|")
    add(f"| Gross margin | {_ratio_pct(info.get('grossMargins'))} |")
    add(f"| Operating margin | {_ratio_pct(info.get('operatingMargins'))} |")
    add(f"| Net margin | {_ratio_pct(info.get('profitMargins'))} |")
    add(f"| ROE | {_ratio_pct(info.get('returnOnEquity'))} |")
    add(f"| ROA | {_ratio_pct(info.get('returnOnAssets'))} |")
    add(f"| ROIC (estimate) | {_ratio_pct(data.get('roic_estimate'))} _Yahoo gap_ |")
    add(f"| EBITDA | {_money(info.get('ebitda'))} |")
    add(f"| FCF | {_money(info.get('freeCashflow'))} |")
    add(f"| EPS (TTM) | {_money(info.get('trailingEps'))} |")
    add("")

    # ---------- Growth ----------
    add("## Growth metrics")
    add("| Field | Value |")
    add("|---|---|")
    add(f"| Revenue growth (TTM) | {_ratio_pct(info.get('revenueGrowth'))} |")
    add(f"| Revenue Q/Q YoY | {_ratio_pct(info.get('revenueQuarterlyGrowth'))} |")
    add(f"| Earnings growth | {_ratio_pct(info.get('earningsGrowth'))} |")
    add(f"| Earnings Q/Q YoY | {_ratio_pct(info.get('earningsQuarterlyGrowth'))} |")
    add("")

    # ---------- Balance sheet ----------
    add("## Balance sheet")
    add("| Field | Value |")
    add("|---|---|")
    debt_to_eq = info.get("debtToEquity")
    add(f"| Total cash | {_money(info.get('totalCash'))} |")
    add(f"| Total debt | {_money(info.get('totalDebt'))} |")
    if info.get("totalCash") and info.get("totalDebt"):
        net_debt = info["totalDebt"] - info["totalCash"]
        add(f"| Net debt | {_money(net_debt)} |")
    add(f"| Debt/Equity | {_num(debt_to_eq / 100 if debt_to_eq and debt_to_eq > 5 else debt_to_eq)} |")
    add(f"| Current ratio | {_num(info.get('currentRatio'))} |")
    add(f"| Quick ratio | {_num(info.get('quickRatio'))} |")
    add(f"| Book value/share | {_money(info.get('bookValue'))} |")
    add(f"| Cash/share | {_money(info.get('totalCashPerShare'))} |")
    add("")

    # ---------- Shares & ownership ----------
    add("## Shares & ownership")
    add("| Field | Value |")
    add("|---|---|")
    so = info.get("sharesOutstanding")
    add(f"| Shares outstanding | {_num(so / 1e6, 2, suffix='M') if so else 'n/a'} |")
    fl = info.get("floatShares")
    add(f"| Float | {_num(fl / 1e6, 2, suffix='M') if fl else 'n/a'} |")
    add(f"| Insider% (held) | {_ratio_pct(info.get('heldPercentInsiders'))} |")
    add(f"| Institutional% (held) | {_ratio_pct(info.get('heldPercentInstitutions'))} |")
    add("")

    # ---------- Short ----------
    add("## Short interest")
    add("| Field | Value |")
    add("|---|---|")
    add(f"| Short% of float | {_ratio_pct(info.get('shortPercentOfFloat'))} |")
    ss = info.get("sharesShort")
    add(f"| Short shares | {_num(ss / 1e6, 2, suffix='M') if ss else 'n/a'} |")
    add(f"| Short ratio (DTC) | {_num(info.get('shortRatio'))} |")
    add(f"| Short date | {info.get('dateShortInterest') or 'n/a'} |")
    add("")

    # ---------- Computed technicals ----------
    price = info.get("currentPrice")
    add("## Computed technicals")
    add("| Field | Value | vs price |")
    add("|---|---|---|")
    for label, val in (("SMA20", data["sma20"]), ("SMA50", data["sma50"]), ("SMA200", data["sma200"])):
        diff = ((price - val) / val * 100) if val and price else None
        add(f"| {label} | {_money(val)} | {_pct(diff / 100) if diff is not None else 'n/a'} |")
    add(f"| RSI(14) | {_num(data['rsi'], 1)} | — |")
    add(f"| ATR(14) | {_num(data['atr'])} | — |")
    add(f"| Rel volume | {_num(data['rel_vol'])} | — |")
    add("")

    # ---------- Dividend ----------
    if info.get("dividendYield"):
        add("## Dividend")
        add(f"- Yield: {_ratio_pct(info.get('dividendYield'))}")
        add(f"- TTM rate: {_money(info.get('trailingAnnualDividendRate'))}")
        add(f"- Payout ratio: {_ratio_pct(info.get('payoutRatio'))}")
        add("")

    # ---------- Analyst ----------
    add("## Analyst")
    add("| Field | Value |")
    add("|---|---|")
    add(f"| Recommendation mean | {_num(info.get('recommendationMean'))} (1=strong buy, 5=strong sell) |")
    add(f"| Target mean | {_money(info.get('targetMeanPrice'))} |")
    add(f"| Number of analysts | {info.get('numberOfAnalystOpinions') or 'n/a'} |")
    add("")

    # ---------- Calendar ----------
    cal = info.get("nextEarningsDate") or info.get("earningsTimestamp")
    add("## Earnings calendar")
    if cal:
        try:
            dt = datetime.fromtimestamp(cal, tz=timezone.utc) if isinstance(cal, (int, float)) else cal
            add(f"- Next earnings: **{dt.strftime('%Y-%m-%d') if hasattr(dt, 'strftime') else dt}** _AMC/BMO timing not in Yahoo — Finviz fallback if within 7 days_")
        except Exception:
            add(f"- Next earnings: {cal} _AMC/BMO timing requires Finviz fallback_")
    else:
        add("- _Yahoo did not return a next-earnings date_")
    add("")

    # ---------- News ----------
    add("## Recent news (Yahoo, last 5)")
    if not data["news"]:
        add("- _none returned_")
    else:
        for n in data["news"]:
            title = n.get("title") or "(untitled)"
            pub = n.get("publisher") or "?"
            url = n.get("url") or ""
            add(f"- [{title}]({url}) — {pub}")
    add("")

    # ---------- Yahoo gaps ----------
    add("## Yahoo gaps — when to fall back to Finviz / others")
    add("- **ROIC precise** (Yahoo gives ROE/ROA only; we estimate from EBIT/IC). Fall back to Finviz `ROI` row if Pillar 1 verdict is borderline.")
    add("- **AMC/BMO earnings timing** — use Finviz next-earnings field if scan is within 7 days of print.")
    add("- **Insider Trans % / Institutional Trans %** (6-mo / Q aggregates) — Finviz-unique. Use OpenInsider Form 4 cluster detail and Fintel 13F Q/Q delta instead (sharper signals anyway).")
    add("- **13F holder count Q/Q** — yfinance does NOT have. Use Fintel `/so/us/<TICKER>` (per `guide/scan/data.md`).")
    add("- **ChartExchange flow** (dark pool, max pain, FTD, borrow fee) — yfinance does NOT have. Keep WebFetch chain.")
    add("- **Superinvestor coverage (Dataroma)** — yfinance does NOT have. Keep WebFetch.")
    add("")

    return "\n".join(lines)


def render_auto_reject_only(data):
    triggered, reasons = auto_reject_check(data)
    if triggered:
        return f"AUTO-REJECT: {' · '.join(reasons)}", 3
    return "OK: no numeric auto-reject", 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.strip().split("\n")[0])
    ap.add_argument("ticker", help="Stock ticker (e.g. RIVN)")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of markdown")
    ap.add_argument("--auto-reject-only", action="store_true",
                    help="just print PASS/FAIL on numeric auto-reject; exit 3 if reject")
    args = ap.parse_args()

    yf, pd = _import_deps()
    data = fetch_all(args.ticker, yf, pd)
    if not data:
        print(f"ERROR: no data returned for {args.ticker} from Yahoo", file=sys.stderr)
        return 1

    if args.auto_reject_only:
        msg, code = render_auto_reject_only(data)
        print(msg)
        return code

    if args.json:
        # serialize info dict carefully — drop non-JSON-safe fields
        safe = {
            "ticker": data["ticker"],
            "auto_reject": auto_reject_check(data)[0],
            "auto_reject_reasons": auto_reject_check(data)[1],
            "growth_check": data.get("growth_check"),
            "info": {k: v for k, v in data["info"].items()
                     if isinstance(v, (str, int, float, bool, list, dict)) or v is None},
            "technicals": {
                "sma20": data["sma20"],
                "sma50": data["sma50"],
                "sma200": data["sma200"],
                "rsi": data["rsi"],
                "atr": data["atr"],
                "rel_vol": data["rel_vol"],
            },
            "roic_estimate": data["roic_estimate"],
            "news": data["news"],
        }
        print(json.dumps(safe, default=str, indent=2))
        return 0

    print(render_markdown(data))
    return 0


if __name__ == "__main__":
    sys.exit(main())
