#!/usr/bin/env python3
"""
fetch_sec.py — local SEC EDGAR fetcher for /scan stocks.

Goes straight to the source for what EDGAR genuinely owns:
    - Form 4 insider transactions (replaces OpenInsider / Finviz-insider WebFetches)
    - Cluster detection (multiple insiders on adjacent days = positioning signal)
    - Recent material 8-Ks (earnings announcements, M&A, guidance updates)
    - Latest 10-K / 10-Q filing dates (freshness check for fundamentals)
    - Company-facts XBRL slice for ROIC components (EBIT, total debt, equity) —
      closes the Yahoo ROIC-precise gap without needing Finviz fallback

What EDGAR does NOT do (keep WebFetch fallback per `guide/scan/data.md`):
    - 13F holder COUNT Q/Q for a specific stock — EDGAR is filer-indexed, not
      stock-indexed. WhaleWisdom / HedgeFollow / Fintel still required.
    - Dataroma superinvestor coverage — not an EDGAR concept.

Auth: SEC requires a User-Agent string with a real contact. Set via env var
SEC_USER_AGENT, e.g. `export SEC_USER_AGENT="YourName <you@example.com>"`.
Fair-access policy is ~10 req/sec; we throttle modestly under that.

Usage:
    .venv/bin/python scripts/fetch_sec.py RIVN
    .venv/bin/python scripts/fetch_sec.py RIVN --days=90
    .venv/bin/python scripts/fetch_sec.py RIVN --json

Exit codes:
    0 — success
    1 — ticker not resolved or no filings
    2 — dependency / network error
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from xml.etree import ElementTree as ET

UA = os.environ.get("SEC_USER_AGENT", "trading-ops")
# Don't request gzip — urllib.request doesn't auto-decompress, and SEC happily
# serves uncompressed when Accept-Encoding is omitted. Asking for gzip and not
# decompressing returns binary 0x8b... bytes that crash the json.loads path.
HEADERS = {"User-Agent": UA, "Accept": "application/json,text/plain,*/*"}
THROTTLE_SECONDS = 0.12  # ~8 req/sec, under SEC's 10/sec courtesy cap

CACHE_DIR = Path.home() / ".cache" / "trading-ops-sec"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
TICKERS_CACHE = CACHE_DIR / "company_tickers.json"
TICKERS_CACHE_TTL_DAYS = 7


def _http_get(url, accept_json=False):
    """GET with SEC-required headers; returns text. Raises on HTTP error."""
    req = urllib.request.Request(url, headers=HEADERS)
    time.sleep(THROTTLE_SECONDS)
    with urllib.request.urlopen(req, timeout=30) as r:
        data = r.read()
    if accept_json:
        return json.loads(data.decode("utf-8"))
    return data.decode("utf-8", errors="replace")


def _load_ticker_cik_map():
    """Cached ticker → CIK lookup table."""
    if TICKERS_CACHE.exists():
        age_days = (time.time() - TICKERS_CACHE.stat().st_mtime) / 86400
        if age_days < TICKERS_CACHE_TTL_DAYS:
            return json.loads(TICKERS_CACHE.read_text())
    raw = _http_get("https://www.sec.gov/files/company_tickers.json", accept_json=True)
    TICKERS_CACHE.write_text(json.dumps(raw))
    return raw


def resolve_cik(ticker):
    """Return (cik_str_zero_padded_10, name) or (None, None)."""
    m = _load_ticker_cik_map()
    t = ticker.upper()
    for entry in m.values():
        if entry.get("ticker") == t:
            return f"{entry['cik_str']:010d}", entry.get("title")
    return None, None


def fetch_submissions(cik10):
    return _http_get(f"https://data.sec.gov/submissions/CIK{cik10}.json", accept_json=True)


def fetch_companyfacts(cik10):
    try:
        return _http_get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik10}.json", accept_json=True)
    except Exception:
        return None


# --- Form 4 parsing -----------------------------------------------------------

# SEC Form 4 transaction codes — the ones that actually matter
TX_CODE_MEANING = {
    "P": "open-market purchase",
    "S": "open-market sale",
    "A": "grant/award",
    "D": "disposition to issuer",
    "F": "tax withholding (sale)",
    "G": "gift",
    "M": "option exercise",
    "X": "option exercise (cash)",
    "C": "conversion of derivative",
    "I": "discretionary transaction",
    "J": "other",
}


def _extract_text(elem, path):
    """ET helper — return text of first matching child or None."""
    found = elem.find(path)
    return found.text.strip() if found is not None and found.text else None


def parse_form4(xml_text):
    """Parse a Form 4 XML; return list of transaction dicts (non-derivative only)."""
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return []

    # Reporting owner identity
    owner_name = _extract_text(root, ".//reportingOwner/reportingOwnerId/rptOwnerName") or "?"
    rel = root.find(".//reportingOwner/reportingOwnerRelationship")
    role_parts = []
    if rel is not None:
        for tag, label in (
            ("isDirector", "Director"),
            ("isOfficer", "Officer"),
            ("isTenPercentOwner", "10%-owner"),
        ):
            t = rel.find(tag)
            if t is not None and (t.text or "").strip() in ("1", "true"):
                role_parts.append(label)
        title = _extract_text(rel, "officerTitle")
        if title:
            role_parts.append(title)
    role = " · ".join(role_parts) if role_parts else "?"

    txs = []
    for tx in root.findall(".//nonDerivativeTable/nonDerivativeTransaction"):
        tx_date = _extract_text(tx, "transactionDate/value")
        tx_code = _extract_text(tx, "transactionCoding/transactionCode")
        shares = _extract_text(tx, "transactionAmounts/transactionShares/value")
        price = _extract_text(tx, "transactionAmounts/transactionPricePerShare/value")
        ad_code = _extract_text(tx, "transactionAmounts/transactionAcquiredDisposedCode/value")
        try:
            shares_f = float(shares) if shares else None
            price_f = float(price) if price else None
        except ValueError:
            shares_f = price_f = None
        txs.append({
            "owner": owner_name,
            "role": role,
            "date": tx_date,
            "code": tx_code,
            "code_meaning": TX_CODE_MEANING.get(tx_code, "?"),
            "shares": shares_f,
            "price": price_f,
            "value": (shares_f or 0) * (price_f or 0),
            "acquired_disposed": ad_code,  # A or D
        })
    return txs


def fetch_recent_form4s(cik10, submissions, days_back=90):
    """Return list of all Form 4 transactions filed in the last `days_back` days."""
    recent = submissions.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    accs = recent.get("accessionNumber", [])
    dates = recent.get("filingDate", [])
    docs = recent.get("primaryDocument", [])

    cutoff = (datetime.now(timezone.utc) - timedelta(days=days_back)).strftime("%Y-%m-%d")
    out = []
    for form, acc, dt, primary in zip(forms, accs, dates, docs):
        if form != "4" or dt < cutoff:
            continue
        acc_no_dashes = acc.replace("-", "")
        url = f"https://www.sec.gov/Archives/edgar/data/{int(cik10)}/{acc_no_dashes}/{primary}"
        try:
            xml = _http_get(url)
        except Exception as e:
            sys.stderr.write(f"WARN: failed Form 4 {acc}: {e}\n")
            continue
        for tx in parse_form4(xml):
            tx["filing_date"] = dt
            tx["accession"] = acc
            out.append(tx)
    return out


def detect_clusters(txs, max_gap_days=2, min_buyers=2):
    """A cluster = ≥`min_buyers` distinct insiders BUYING (code P) within `max_gap_days`."""
    buys = [t for t in txs if t["code"] == "P" and t["date"]]
    buys.sort(key=lambda t: t["date"])
    clusters = []
    cur = []
    for t in buys:
        if not cur:
            cur = [t]
            continue
        delta = (datetime.fromisoformat(t["date"]) - datetime.fromisoformat(cur[-1]["date"])).days
        if delta <= max_gap_days:
            cur.append(t)
        else:
            if len({c["owner"] for c in cur}) >= min_buyers:
                clusters.append(cur)
            cur = [t]
    if cur and len({c["owner"] for c in cur}) >= min_buyers:
        clusters.append(cur)
    return clusters


# --- 8-K and 10-Q/10-K filing dates ------------------------------------------

EARNINGS_8K_PATTERN = re.compile(r"item\s*2\.02|results.?of.?operations", re.IGNORECASE)


def recent_filings_summary(submissions, days_back=180):
    recent = submissions.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    dates = recent.get("filingDate", [])
    items = recent.get("items", [""] * len(forms))
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days_back)).strftime("%Y-%m-%d")

    summary = {
        "latest_10K": None,
        "latest_10Q": None,
        "latest_8K_earnings": None,
        "recent_8Ks": [],
    }
    for form, dt, item_str in zip(forms, dates, items):
        if dt < cutoff:
            continue
        if form == "10-K" and (summary["latest_10K"] is None or dt > summary["latest_10K"]):
            summary["latest_10K"] = dt
        elif form == "10-Q" and (summary["latest_10Q"] is None or dt > summary["latest_10Q"]):
            summary["latest_10Q"] = dt
        elif form == "8-K":
            entry = {"date": dt, "items": item_str}
            summary["recent_8Ks"].append(entry)
            if EARNINGS_8K_PATTERN.search(item_str or "") and (
                summary["latest_8K_earnings"] is None or dt > summary["latest_8K_earnings"]
            ):
                summary["latest_8K_earnings"] = dt
    summary["recent_8Ks"] = summary["recent_8Ks"][:10]
    return summary


# --- Company facts → ROIC components ----------------------------------------

ROIC_FACTS = {
    "ebit": ["OperatingIncomeLoss"],
    "total_debt": ["LongTermDebt", "LongTermDebtNoncurrent"],
    "current_debt": ["LongTermDebtCurrent", "DebtCurrent"],
    "equity": ["StockholdersEquity", "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"],
    "tax_provision": ["IncomeTaxExpenseBenefit"],
    "pretax_income": ["IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest", "IncomeLossFromContinuingOperationsBeforeIncomeTaxes"],
}


def latest_xbrl_value(facts, candidates, units=("USD",)):
    """Return latest annual or quarterly USD figure across candidate fact names."""
    if not facts:
        return None, None
    us_gaap = facts.get("facts", {}).get("us-gaap", {})
    best = None
    for name in candidates:
        block = us_gaap.get(name)
        if not block:
            continue
        for unit in units:
            entries = block.get("units", {}).get(unit, [])
            if not entries:
                continue
            # Prefer 10-K (annual, fp == "FY") if present, else most-recent 10-Q
            sorted_entries = sorted(entries, key=lambda x: x.get("end", ""), reverse=True)
            for e in sorted_entries:
                if best is None or e.get("end", "") > best.get("end", ""):
                    best = e
    if best:
        return best.get("val"), best.get("end")
    return None, None


def compute_roic_from_facts(facts):
    """Returns dict with components + ROIC fraction or None."""
    ebit, ebit_end = latest_xbrl_value(facts, ROIC_FACTS["ebit"])
    debt_long, _ = latest_xbrl_value(facts, ROIC_FACTS["total_debt"])
    debt_curr, _ = latest_xbrl_value(facts, ROIC_FACTS["current_debt"])
    equity, _ = latest_xbrl_value(facts, ROIC_FACTS["equity"])
    tax, _ = latest_xbrl_value(facts, ROIC_FACTS["tax_provision"])
    pretax, _ = latest_xbrl_value(facts, ROIC_FACTS["pretax_income"])

    total_debt = (debt_long or 0) + (debt_curr or 0)
    if equity is None or total_debt + equity <= 0 or ebit is None:
        return {"ebit": ebit, "debt": total_debt, "equity": equity, "roic": None, "as_of": ebit_end}

    tax_rate = 0.21
    if tax is not None and pretax and pretax > 0:
        tax_rate = max(0.0, min(0.5, tax / pretax))
    nopat = ebit * (1 - tax_rate)
    ic = total_debt + equity
    return {
        "ebit": ebit,
        "debt": total_debt,
        "equity": equity,
        "tax_rate": tax_rate,
        "nopat": nopat,
        "invested_capital": ic,
        "roic": nopat / ic,
        "as_of": ebit_end,
    }


# --- Rendering ---------------------------------------------------------------

def _money(n):
    if n is None:
        return "n/a"
    n = float(n)
    if abs(n) >= 1e9:
        return f"${n / 1e9:.2f}B"
    if abs(n) >= 1e6:
        return f"${n / 1e6:.2f}M"
    if abs(n) >= 1e3:
        return f"${n / 1e3:.2f}K"
    return f"${n:.2f}"


def render_markdown(ticker, cik10, name, txs, clusters, filings, roic, days):
    lines = []
    add = lines.append
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    add(f"# {ticker} — SEC EDGAR pre-compute ({now})")
    add(f"_{name}, CIK {cik10}_")
    add("")

    # Form 4 summary
    purchases = [t for t in txs if t["code"] == "P"]
    sales = [t for t in txs if t["code"] == "S"]
    add(f"## Form 4 insider transactions — last {days} days")
    add(f"- Purchases: **{len(purchases)}** filings, total value {_money(sum(t['value'] for t in purchases))}")
    add(f"- Sales: {len(sales)} filings, total value {_money(sum(t['value'] for t in sales))}")
    add(f"- Other transactions: {len(txs) - len(purchases) - len(sales)} (grants, exercises, withholding, etc.)")
    add("")

    if purchases:
        add("### Recent open-market purchases (code P)")
        add("| Date | Owner | Role | Shares | Price | Value |")
        add("|---|---|---|---|---|---|")
        for t in sorted(purchases, key=lambda x: x["date"] or "", reverse=True)[:10]:
            add(f"| {t['date']} | {t['owner']} | {t['role']} | {t['shares']:,.0f} | ${t['price']:.2f} | {_money(t['value'])} |")
        add("")

    if clusters:
        add(f"### 🚨 Cluster detection — {len(clusters)} cluster(s) of insider buying")
        for i, cl in enumerate(clusters, 1):
            owners = sorted({c["owner"] for c in cl})
            total = sum(c["value"] for c in cl)
            d_min = min(c["date"] for c in cl)
            d_max = max(c["date"] for c in cl)
            add(f"- **Cluster {i}** ({d_min} → {d_max}): {len(owners)} insiders, total {_money(total)}")
            for o in owners:
                add(f"  - {o}")
        add("")
    else:
        add("- _No insider buying clusters in window (≥2 distinct insiders within 2 days)_")
        add("")

    # Filings freshness
    add("## Filings freshness")
    add(f"- Latest **10-K**: {filings['latest_10K'] or 'n/a (none in window)'}")
    add(f"- Latest **10-Q**: {filings['latest_10Q'] or 'n/a'}")
    add(f"- Latest earnings 8-K (Item 2.02): {filings['latest_8K_earnings'] or 'n/a'}")
    if filings["recent_8Ks"]:
        add(f"- Recent 8-Ks (last {len(filings['recent_8Ks'])}):")
        for k in filings["recent_8Ks"]:
            add(f"  - {k['date']} — items: {k['items'] or '(none)'}")
    add("")

    # ROIC from XBRL
    add("## ROIC from XBRL company-facts (closes Yahoo precise-ROIC gap)")
    if roic and roic.get("roic") is not None:
        add(f"- EBIT (Operating Income): {_money(roic['ebit'])}")
        add(f"- Total debt: {_money(roic['debt'])}")
        add(f"- Stockholders' equity: {_money(roic['equity'])}")
        add(f"- Tax rate (computed): {roic.get('tax_rate', 0.21) * 100:.1f}%")
        add(f"- NOPAT = EBIT × (1 − tax) = {_money(roic['nopat'])}")
        add(f"- Invested capital = debt + equity = {_money(roic['invested_capital'])}")
        add(f"- **ROIC = {roic['roic'] * 100:+.2f}% (as-of {roic['as_of']})**")
    else:
        add("- _Insufficient XBRL data to compute ROIC; fall back to Finviz `ROI` row_")
    add("")

    # Fallback notes
    add("## EDGAR gaps — keep WebFetch fallback per `guide/scan/data.md`")
    add("- **13F holder count Q/Q** — EDGAR is filer-indexed not stock-indexed; use WhaleWisdom/HedgeFollow/Fintel chain")
    add("- **Dataroma superinvestor coverage** — not an EDGAR concept; WebFetch `dataroma.com/m/stock.php?sym=<TICKER>`")
    add("- **Aggregated insider/institutional Trans %** — Finviz quote-page rows if needed (usually skipped — Form 4 cluster detail above is sharper)")
    add("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__.strip().split("\n")[0])
    ap.add_argument("ticker")
    ap.add_argument("--days", type=int, default=90, help="Form 4 lookback window (default 90)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    try:
        cik10, name = resolve_cik(args.ticker)
    except Exception as e:
        print(f"ERROR: ticker→CIK lookup failed: {e}", file=sys.stderr)
        return 2
    if not cik10:
        print(f"ERROR: ticker {args.ticker} not found in SEC EDGAR ticker map", file=sys.stderr)
        return 1

    try:
        submissions = fetch_submissions(cik10)
    except Exception as e:
        print(f"ERROR: SEC submissions fetch failed: {e}", file=sys.stderr)
        return 2

    try:
        txs = fetch_recent_form4s(cik10, submissions, days_back=args.days)
    except Exception as e:
        sys.stderr.write(f"WARN: Form 4 fetch partial failure: {e}\n")
        txs = []
    clusters = detect_clusters(txs)

    filings = recent_filings_summary(submissions)
    facts = fetch_companyfacts(cik10)
    roic = compute_roic_from_facts(facts) if facts else None

    if args.json:
        print(json.dumps({
            "ticker": args.ticker.upper(),
            "cik": cik10,
            "name": name,
            "form4_transactions": txs,
            "clusters": [[t for t in cl] for cl in clusters],
            "filings": filings,
            "roic": roic,
        }, default=str, indent=2))
        return 0

    print(render_markdown(args.ticker.upper(), cik10, name, txs, clusters, filings, roic, args.days))
    return 0


if __name__ == "__main__":
    sys.exit(main())
