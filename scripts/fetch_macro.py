#!/usr/bin/env python3
"""
fetch_macro.py — local macro gauges fetcher for /scan-macro.

Pulls the key-gauges table from authoritative free sources:
    - **FRED** (St. Louis Fed) for: Fed funds, 10Y / 2Y / 3M Treasuries, CPI YoY,
      Core PCE YoY, NFP, U-3 unemployment, GDPNow proxy (latest GDP), DXY, M2,
      VIX (CBOE via FRED mirror), Industrial Production, Initial Claims
    - **Treasury / FiscalData** for: full daily yield curve (cross-check FRED)

Replaces ~6 WebFetches per `/scan-macro` with one Python loop. Series IDs are
canonical — see https://fred.stlouisfed.org/ to look up additional series.

Auth: FRED requires a free API key. Set via env var:
    export FRED_API_KEY="<your-key>"
Get one at https://fredaccount.stlouisfed.org/apikeys (instant, free).
Treasury FiscalData has no auth.

Usage:
    .venv/bin/python scripts/fetch_macro.py
    .venv/bin/python scripts/fetch_macro.py --series=DGS10,VIXCLS
    .venv/bin/python scripts/fetch_macro.py --json

Exit codes:
    0 — success
    1 — FRED key missing or all fetches failed
    2 — runtime error
"""

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

FRED_KEY = os.environ.get("FRED_API_KEY")

# Default macro panel — the gauges that drive regime placement (Goldilocks / Reflation / Stagflation / Risk-Off)
DEFAULT_SERIES = {
    # Rates / curve
    "DFF":     "Fed funds effective",
    "DGS10":   "10Y Treasury",
    "DGS2":    "2Y Treasury",
    "DGS3MO":  "3M Treasury",
    "T10Y2Y":  "10Y–2Y spread (un-inversion = recession trigger)",
    "T10Y3M":  "10Y–3M spread",
    # Inflation
    "CPIAUCSL":   "CPI All Items (SA, level)",
    "CPILFESL":   "Core CPI (ex food/energy, SA, level)",
    "PCEPILFE":   "Core PCE (ex food/energy, SA, level)",
    # Labor / growth
    "PAYEMS":     "Total nonfarm payrolls (NFP, level)",
    "UNRATE":     "Unemployment rate (U-3)",
    "ICSA":       "Initial jobless claims (weekly)",
    "INDPRO":     "Industrial production (level)",
    # Liquidity / dollar
    "DTWEXBGS":   "Trade-Weighted USD Index (broad)",
    "M2SL":       "M2 money supply",
    # Vol
    "VIXCLS":     "VIX",
}


def fred_observations(series_id, latest_n=2):
    """Return last `latest_n` observations for a FRED series. Skips 'NaN' values."""
    if not FRED_KEY:
        return None
    params = {
        "series_id": series_id,
        "api_key": FRED_KEY,
        "file_type": "json",
        "sort_order": "desc",
        "limit": str(max(latest_n + 5, 10)),  # buffer for NaN skips
    }
    url = "https://api.stlouisfed.org/fred/series/observations?" + urllib.parse.urlencode(params)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "trading-ops macro-fetcher"})
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read().decode("utf-8"))
    except Exception as e:
        sys.stderr.write(f"WARN: FRED fetch {series_id} failed: {e}\n")
        return None
    obs = []
    for o in data.get("observations", []):
        try:
            v = float(o["value"])
        except (ValueError, KeyError):
            continue
        obs.append({"date": o["date"], "value": v})
        if len(obs) >= latest_n:
            break
    return obs


def yoy_pct(current, year_ago):
    if current is None or year_ago is None or year_ago == 0:
        return None
    return (current - year_ago) / year_ago * 100


def fred_latest_with_yoy(series_id):
    """Return latest value + YoY % change (using values 12 months prior)."""
    if not FRED_KEY:
        return None
    # Pull a year of monthly observations
    params = {
        "series_id": series_id,
        "api_key": FRED_KEY,
        "file_type": "json",
        "sort_order": "desc",
        "limit": "14",
    }
    url = "https://api.stlouisfed.org/fred/series/observations?" + urllib.parse.urlencode(params)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "trading-ops macro-fetcher"})
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read().decode("utf-8"))
    except Exception:
        return None
    obs = []
    for o in data.get("observations", []):
        try:
            v = float(o["value"])
        except (ValueError, KeyError):
            continue
        obs.append({"date": o["date"], "value": v})
    if len(obs) < 2:
        return None
    latest = obs[0]
    year_ago = obs[12] if len(obs) > 12 else None
    return {
        "date": latest["date"],
        "value": latest["value"],
        "yoy_pct": yoy_pct(latest["value"], year_ago["value"] if year_ago else None),
        "year_ago_date": year_ago["date"] if year_ago else None,
    }


def treasury_yield_curve():
    """FiscalData daily Treasury yield curve — last available date."""
    url = (
        "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/"
        "v2/accounting/od/avg_interest_rates?sort=-record_date&limit=10"
    )
    # Note: this endpoint gives weighted-avg interest rates, not the daily nominal curve.
    # The daily nominal curve is at /v2/accounting/od/daily_treasury_yield_curve_rates
    url = (
        "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/"
        "v2/accounting/od/daily_treasury_yield_curve_rates?sort=-record_date&limit=1"
    )
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            data = json.loads(r.read().decode("utf-8"))
    except Exception as e:
        sys.stderr.write(f"WARN: Treasury yield curve fetch failed: {e}\n")
        return None
    rows = data.get("data", [])
    if not rows:
        return None
    return rows[0]


def render_markdown(snapshot, curve):
    lines = []
    add = lines.append
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    add(f"# Macro key gauges — local pre-compute ({now})")
    add("")
    add("## FRED rates / curve")
    add("| Series | Description | Latest | As of |")
    add("|---|---|---|---|")
    for sid in ("DFF", "DGS10", "DGS2", "DGS3MO", "T10Y2Y", "T10Y3M"):
        d = snapshot.get(sid)
        if d:
            add(f"| `{sid}` | {DEFAULT_SERIES[sid]} | {d['value']:.2f}% | {d['date']} |")
    add("")
    add("## FRED inflation (level series + YoY %)")
    add("| Series | Description | Level | YoY % | As of |")
    add("|---|---|---|---|---|")
    for sid in ("CPIAUCSL", "CPILFESL", "PCEPILFE"):
        d = snapshot.get(sid)
        if d and d.get("yoy_pct") is not None:
            add(f"| `{sid}` | {DEFAULT_SERIES[sid]} | {d['value']:,.2f} | **{d['yoy_pct']:+.2f}%** | {d['date']} |")
    add("")
    add("## FRED labor / growth")
    add("| Series | Description | Latest | YoY % | As of |")
    add("|---|---|---|---|---|")
    for sid in ("PAYEMS", "UNRATE", "ICSA", "INDPRO"):
        d = snapshot.get(sid)
        if d:
            yoy = f"{d['yoy_pct']:+.2f}%" if d.get("yoy_pct") is not None else "—"
            unit = "%" if sid == "UNRATE" else ""
            add(f"| `{sid}` | {DEFAULT_SERIES[sid]} | {d['value']:,.2f}{unit} | {yoy} | {d['date']} |")
    add("")
    add("## FRED dollar / liquidity / vol")
    add("| Series | Description | Latest | As of |")
    add("|---|---|---|---|")
    for sid in ("DTWEXBGS", "M2SL", "VIXCLS"):
        d = snapshot.get(sid)
        if d:
            add(f"| `{sid}` | {DEFAULT_SERIES[sid]} | {d['value']:,.2f} | {d['date']} |")
    add("")

    if curve:
        add("## Treasury daily yield curve (FiscalData)")
        add(f"_As of {curve.get('record_date')}_")
        add("")
        add("| Tenor | Yield |")
        add("|---|---|")
        for k, label in (
            ("bc_1month", "1M"), ("bc_3month", "3M"), ("bc_6month", "6M"),
            ("bc_1year", "1Y"), ("bc_2year", "2Y"), ("bc_3year", "3Y"),
            ("bc_5year", "5Y"), ("bc_7year", "7Y"), ("bc_10year", "10Y"),
            ("bc_20year", "20Y"), ("bc_30year", "30Y"),
        ):
            v = curve.get(k)
            if v not in (None, ""):
                add(f"| {label} | {v}% |")
        add("")

    add("## Regime placement helpers")
    add("- **Growth** ↑/↓: read `INDPRO` YoY + `PAYEMS` momentum + `ICSA` direction")
    add("- **Inflation** ↑/↓: `CPILFESL` YoY (Core CPI) + `PCEPILFE` YoY (Core PCE)")
    add("- **Liquidity** tight/loose: `DFF` direction × `M2SL` YoY change × `DTWEXBGS` (DXY) × `T10Y2Y` curve")
    add("- **Volatility regime**: `VIXCLS` level (Stagflation/Risk-Off typically > 20)")
    add("")
    add("## Fallback (when FRED key missing or rate-limited)")
    add("- WebFetch CPI/PCE/NFP from BLS press releases")
    add("- WebFetch GDPNow from `atlantafed.org/cqer/research/gdpnow`")
    add("- WebFetch VIX from TradingEconomics or CBOE")
    add("- WebFetch yield curve from `home.treasury.gov`")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__.strip().split("\n")[0])
    ap.add_argument("--series", help="comma-separated FRED series IDs to fetch (default: full panel)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if not FRED_KEY:
        print("ERROR: FRED_API_KEY env var not set.", file=sys.stderr)
        print("Get a free key at https://fredaccount.stlouisfed.org/apikeys, then:", file=sys.stderr)
        print("  export FRED_API_KEY=\"<your-key>\"", file=sys.stderr)
        return 1

    if args.series:
        series_ids = [s.strip().upper() for s in args.series.split(",")]
    else:
        series_ids = list(DEFAULT_SERIES.keys())

    snapshot = {}
    for sid in series_ids:
        # Use YoY-aware fetch for level-series; rate-series get straight latest
        if sid in ("CPIAUCSL", "CPILFESL", "PCEPILFE", "PAYEMS", "INDPRO", "M2SL"):
            data = fred_latest_with_yoy(sid)
        else:
            obs = fred_observations(sid, latest_n=1)
            data = obs[0] if obs else None
        snapshot[sid] = data

    curve = treasury_yield_curve()

    if args.json:
        print(json.dumps({"snapshot": snapshot, "yield_curve": curve}, default=str, indent=2))
        return 0

    print(render_markdown(snapshot, curve))
    return 0


if __name__ == "__main__":
    sys.exit(main())
