#!/usr/bin/env python3
"""Regenerate scanned/INDEX.md master coverage table from each current.md's Coverage tier line.

Reads:
  scanned/<asset-class>/<TICKER>/current.md  (stocks, fx, indices, crypto, ...)
  scanned/MACRO/current.md
  scanned/INDEX.md (preserved sections: Coverage changes log, Performance audit log, Recent screens, Dropped)

Writes:
  scanned/INDEX.md (regenerated master coverage table + per-horizon focus blocks + catalyst monitor + Macro/FX section)

Append-only sections (Coverage changes, Performance, Dropped) are PRESERVED verbatim — this script does not touch them.

Run: python3 scripts/regen_index.py
"""
from __future__ import annotations

import datetime as dt
import pathlib
import re
import sys
from dataclasses import dataclass, field
from typing import Optional

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCANNED = ROOT / "scanned"
INDEX = SCANNED / "INDEX.md"

ASSET_CLASSES = ["stocks", "fx", "indices", "crypto", "commodities"]
TIER_LETTERS = ["T", "W", "B", "S", "X"]


@dataclass
class Scan:
    ticker: str
    asset_class: str
    path: pathlib.Path
    last_scan: str = ""
    pos_tier: str = "—"
    swing_tier: str = "—"
    day_tier: str = "—"
    pos_reason: str = ""
    swing_reason: str = ""
    day_reason: str = ""
    score: str = "—"
    next_catalyst: str = ""
    quadrant: str = ""  # macro / FX trackers
    is_tracker: bool = False  # MACRO + FX-tracker EURUSD-style
    body: str = ""

    @property
    def link(self) -> str:
        return f"{self.asset_class}/{self.ticker}/current.md" if self.asset_class else f"{self.ticker}/current.md"


SNAPSHOT_DATE_RE = re.compile(r"^##\s*Snapshot\s*[—-]\s*(\d{4}-\d{2}-\d{2})", re.MULTILINE)
DATE_FALLBACK_RE = re.compile(r"\*\*Date scanned:\*\*\s*(\d{4}-\d{2}-\d{2})", re.IGNORECASE)
TIER_LINE_RE = re.compile(
    r"\*\*Coverage tier:\*\*\s*Pos\s*\*?\*?([TWBSX—])\*?\*?\s*(\([^)]*\))?\s*[·•∙]\s*"
    r"Swing\s*\*?\*?([TWBSX—])\*?\*?\s*(\([^)]*\))?\s*[·•∙]\s*"
    r"Day\s*\*?\*?([TWBSX—])\*?\*?\s*(\([^)]*\))?",
)
SCORE_RE = re.compile(r"\b(\d/6)\b")
CATALYST_RE = re.compile(r"\*\*Next\s*(?:catalyst|earnings)\b[^:]*:\*\*\s*(.+?)(?:\s*\(|$|\n)", re.IGNORECASE)


def parse_scan(path: pathlib.Path, asset_class: str, ticker: str) -> Scan:
    body = path.read_text(encoding="utf-8")
    s = Scan(ticker=ticker, asset_class=asset_class, path=path, body=body)

    m = SNAPSHOT_DATE_RE.search(body)
    if m:
        s.last_scan = m.group(1)
    else:
        m = DATE_FALLBACK_RE.search(body)
        if m:
            s.last_scan = m.group(1)

    m = TIER_LINE_RE.search(body)
    if m:
        s.pos_tier = m.group(1)
        s.pos_reason = (m.group(2) or "").strip("()").strip()
        s.swing_tier = m.group(3)
        s.swing_reason = (m.group(4) or "").strip("()").strip()
        s.day_tier = m.group(5)
        s.day_reason = (m.group(6) or "").strip("()").strip()

    # Score (X/6) — first occurrence usually in TL;DR or scorecard aggregate
    m = SCORE_RE.search(body)
    if m:
        s.score = m.group(1)

    m = CATALYST_RE.search(body)
    if m:
        s.next_catalyst = m.group(1).strip().rstrip("·").strip()

    return s


def parse_macro(path: pathlib.Path) -> Scan:
    s = parse_scan(path, asset_class="", ticker="MACRO")
    s.is_tracker = True
    # Find the regime name on any line that labels itself as Regime or Quadrant
    # (docs/macro.md uses both terms). Tolerates nested `**` markdown emphasis like
    # `**Quadrant:** **Quad 2 — Reflation**`.
    regime_re = re.compile(r"\b(Goldilocks|Reflation|Stagflation|Risk-Off)\b", re.IGNORECASE)
    label_re = re.compile(r"\b(Regime|Quadrant)\s*:", re.IGNORECASE)
    for line in s.body.splitlines():
        if not label_re.search(line):
            continue
        m = regime_re.search(line)
        if m:
            s.quadrant = m.group(1).capitalize() if m.group(1).lower() != "risk-off" else "Risk-Off"
            break
    return s


def find_all_scans() -> tuple[list[Scan], list[Scan]]:
    """Return (stock_scans, tracker_scans). Trackers = MACRO + any non-stock instrument that didn't get tiers."""
    stocks: list[Scan] = []
    trackers: list[Scan] = []

    macro = SCANNED / "MACRO" / "current.md"
    if macro.exists():
        trackers.append(parse_macro(macro))

    for cls in ASSET_CLASSES:
        cls_dir = SCANNED / cls
        if not cls_dir.is_dir():
            continue
        for ticker_dir in sorted(cls_dir.iterdir()):
            if not ticker_dir.is_dir():
                continue
            cur = ticker_dir / "current.md"
            if not cur.exists():
                continue
            scan = parse_scan(cur, asset_class=cls, ticker=ticker_dir.name)
            # FX/indices/crypto/commodities without Pos/Swing/Day tiers = tracker
            if cls != "stocks" and scan.pos_tier == "—" and scan.swing_tier == "—" and scan.day_tier == "—":
                scan.is_tracker = True
                trackers.append(scan)
            else:
                stocks.append(scan)

    return stocks, trackers


def tier_priority(t: str) -> int:
    return {"T": 0, "W": 1, "B": 2, "S": 3, "X": 4, "—": 5}.get(t, 5)


def best_tier(s: Scan) -> str:
    return min((s.pos_tier, s.swing_tier, s.day_tier), key=tier_priority)


def format_tier(t: str) -> str:
    return f"**{t}**" if t in TIER_LETTERS else "—"


def fresh_marker(date_str: str, today: dt.date) -> str:
    if not date_str:
        return ""
    try:
        d = dt.date.fromisoformat(date_str)
    except ValueError:
        return ""
    if (today - d).days > 14:
        return " ⚠"
    return ""


def catalyst_within_7(date_str: str, today: dt.date) -> str:
    if not date_str:
        return ""
    m = re.search(r"(\d{4}-\d{2}-\d{2})", date_str)
    if not m:
        return ""
    try:
        d = dt.date.fromisoformat(m.group(1))
    except ValueError:
        return ""
    if 0 <= (d - today).days <= 7:
        return "🔥 "
    return ""


def render_master_table(stocks: list[Scan], today: dt.date) -> str:
    rows = sorted(stocks, key=lambda s: (tier_priority(best_tier(s)), s.last_scan), reverse=False)
    lines = [
        "| Ticker | Pos | Swing | Day | Score | Last Scan | Best near-term trigger | Next Catalyst |",
        "|---|:-:|:-:|:-:|:-:|---|---|---|",
    ]
    for s in rows:
        # Pick the best-tier reason as "near-term trigger" hint
        triggers = []
        if s.swing_tier in ("T", "W") and s.swing_reason:
            triggers.append(f"Swing: {s.swing_reason}")
        elif s.pos_tier in ("T", "W") and s.pos_reason:
            triggers.append(f"Pos: {s.pos_reason}")
        elif s.day_tier in ("T", "W") and s.day_reason:
            triggers.append(f"Day: {s.day_reason}")
        trig = " · ".join(triggers) or "(see scan)"
        catalyst_pref = catalyst_within_7(s.next_catalyst, today)
        lines.append(
            f"| [{s.ticker}]({s.link}) | {format_tier(s.pos_tier)} | {format_tier(s.swing_tier)} | "
            f"{format_tier(s.day_tier)} | {s.score} | {s.last_scan}{fresh_marker(s.last_scan, today)} | {trig} | "
            f"{catalyst_pref}{s.next_catalyst} |"
        )
    return "\n".join(lines)


def render_focus_block(stocks: list[Scan], horizon: str, header: str) -> str:
    field_map = {"Pos": ("pos_tier", "pos_reason"),
                 "Swing": ("swing_tier", "swing_reason"),
                 "Day": ("day_tier", "day_reason")}
    tier_attr, reason_attr = field_map[horizon]
    candidates = [s for s in stocks if getattr(s, tier_attr) in ("T", "W")]
    if not candidates:
        return f"## {header}\n\n*None currently — wait IS a position.*"
    lines = [
        f"## {header}",
        "",
        f"| Ticker | Tier | Score | Trigger | Stop / Invalidation |",
        f"|---|:-:|:-:|---|---|",
    ]
    for s in sorted(candidates, key=lambda s: (tier_priority(getattr(s, tier_attr)), s.last_scan)):
        reason = getattr(s, reason_attr) or "(see scan)"
        lines.append(
            f"| [{s.ticker}]({s.link}) | {format_tier(getattr(s, tier_attr))} | {s.score} | {reason} | (see scan) |"
        )
    return "\n".join(lines)


def render_catalyst_monitor(stocks: list[Scan], trackers: list[Scan], today: dt.date) -> str:
    rows = []
    for s in stocks + trackers:
        if not s.next_catalyst:
            continue
        m = re.search(r"(\d{4}-\d{2}-\d{2})", s.next_catalyst)
        if not m:
            continue
        try:
            d = dt.date.fromisoformat(m.group(1))
        except ValueError:
            continue
        if (d - today).days > 30 or d < today:
            continue
        marker = catalyst_within_7(m.group(1), today)
        if s.is_tracker:
            row = f"| {marker}{m.group(1)} | {s.ticker} | — | — | — | {s.next_catalyst.replace(m.group(1), '').strip()} |"
        else:
            row = (f"| {marker}{m.group(1)} | {s.ticker} | {format_tier(s.pos_tier)} | "
                   f"{format_tier(s.swing_tier)} | {format_tier(s.day_tier)} | "
                   f"{s.next_catalyst.replace(m.group(1), '').strip()} |")
        rows.append((d, row))
    rows.sort(key=lambda r: r[0])
    if not rows:
        return "## Catalyst monitor — next 30 days\n\n*No catalysts within the next 30 days.*"
    lines = [
        "## Catalyst monitor — next 30 days",
        "",
        "Sorted by date. 🔥 = within 7 days.",
        "",
        "| Date | Ticker | Pos | Swing | Day | Event |",
        "|---|---|:-:|:-:|:-:|---|",
    ]
    lines.extend(r[1] for r in rows)
    return "\n".join(lines)


def render_macro_section(trackers: list[Scan]) -> str:
    if not trackers:
        return "## Macro / Indices / FX\n\n*No trackers.*"
    lines = [
        "## Macro / Indices / FX",
        "",
        "| Ticker | Last Scan | Regime / Bias | Notes |",
        "|---|---|---|---|",
    ]
    for s in trackers:
        link = "MACRO/current.md" if s.ticker == "MACRO" else s.link
        bias = s.quadrant or "(see scan)"
        lines.append(f"| [{s.ticker}]({link}) | {s.last_scan} | {bias} | (see scan) |")
    return "\n".join(lines)


def render_summary(stocks: list[Scan], trackers: list[Scan]) -> str:
    pos_active = sum(1 for s in stocks if s.pos_tier in ("T", "W"))
    swing_active = sum(1 for s in stocks if s.swing_tier in ("T", "W"))
    day_active = sum(1 for s in stocks if s.day_tier in ("T", "W"))
    fx_count = sum(1 for s in trackers if s.ticker != "MACRO")
    return (
        f"**Coverage universe:** {len(stocks) + len(trackers)} names "
        f"({1 if any(t.ticker == 'MACRO' for t in trackers) else 0} macro + {fx_count} FX/index + {len(stocks)} stocks)\n"
        f"**Per-horizon active counts:** Pos **T**/**W** = {pos_active} · "
        f"Swing **T**/**W** = {swing_active} · Day **T**/**W** = {day_active}"
    )


def extract_preserved_section(text: str, header: str) -> str:
    """Extract a top-level section by header so we can preserve it verbatim.

    Strips trailing horizontal rules and the Legend footer because the body template
    re-emits both — leaving them in causes triple-`---` and 3× Legend duplication.
    """
    pattern = re.compile(rf"(^##\s*{re.escape(header)}.*?)(?=^##\s|\Z)", re.MULTILINE | re.DOTALL)
    m = pattern.search(text)
    if not m:
        return ""
    content = m.group(1).rstrip()
    while True:
        new = re.sub(r"\n+\*\*Legend:\*\*[^\n]*$", "", content)
        if new != content:
            content = new.rstrip()
            continue
        new = re.sub(r"\n+---\s*$", "", content)
        if new != content:
            content = new.rstrip()
            continue
        break
    return content + "\n"


PRIOR_TICKER_LINK_RE = re.compile(r"\|\s*\[([A-Z][A-Z0-9.\-]*)\]\(")


def parse_prior_tickers(prior_index_text: str) -> set[str]:
    """Extract every ticker that already appears in the prior INDEX.md master coverage table.

    Used to detect newly-initiated coverage so we can auto-append Initiated rows to the
    Coverage changes log per `guide/scan/structure.md` § INDEX.md format.
    """
    if not prior_index_text:
        return set()
    section_re = re.compile(
        r"##\s*Master coverage table.*?(?=^---\s*$|^##\s)",
        re.MULTILINE | re.DOTALL,
    )
    m = section_re.search(prior_index_text)
    if not m:
        return set()
    return set(PRIOR_TICKER_LINK_RE.findall(m.group(0)))


def inject_initiated_rows(
    preserved_changes: str,
    newly_initiated: list[Scan],
    today: dt.date,
) -> str:
    """Prepend `Initiated` rows for newly-initiated tickers into the Coverage changes section.

    Idempotent by construction: a ticker is only "new" if it didn't appear in the prior
    INDEX master coverage table, so a re-run after the index is regenerated won't re-add.
    """
    if not newly_initiated:
        return preserved_changes

    table_header = (
        "| Date | Ticker | Horizon | Action | Tier change | Reason |\n"
        "|---|---|---|---|---|---|"
    )

    new_rows = []
    for s in sorted(newly_initiated, key=lambda x: x.ticker):
        tier_change = (
            f"— → Pos **{s.pos_tier}** / Swing **{s.swing_tier}** / Day **{s.day_tier}**"
        )
        reason_bits = [b for b in (s.pos_reason, s.swing_reason, s.day_reason) if b]
        reason = "; ".join(reason_bits) if reason_bits else "First scan"
        new_rows.append(
            f"| {today.isoformat()} | {s.ticker} | All | Initiated | {tier_change} | First scan: {reason} |"
        )

    new_block = "\n".join(new_rows)

    # Case 1: existing section is the empty placeholder → replace with a fresh table
    if "*Empty.*" in preserved_changes or not preserved_changes.strip():
        return (
            "## Coverage changes — last 30 days\n\n"
            f"{table_header}\n{new_block}\n"
        )

    # Case 2: existing section already has a table → insert new rows directly under the header
    header_re = re.compile(
        r"(\|\s*Date\s*\|\s*Ticker\s*\|\s*Horizon\s*\|\s*Action\s*\|\s*Tier change\s*\|\s*Reason\s*\|\s*\n"
        r"\|[^\n]*\|)",
        re.IGNORECASE,
    )
    if header_re.search(preserved_changes):
        return header_re.sub(lambda m: m.group(1) + "\n" + new_block, preserved_changes, count=1)

    # Case 3: section exists but no table found → append a fresh table at the end of section
    return preserved_changes.rstrip() + f"\n\n{table_header}\n{new_block}\n"


def main() -> int:
    today = dt.date.today()
    stocks, trackers = find_all_scans()

    # Preserve append-only sections from existing INDEX.md
    existing = INDEX.read_text(encoding="utf-8") if INDEX.exists() else ""
    preserved_dropped = extract_preserved_section(existing, "X Dropped") or extract_preserved_section(existing, r"\*\*X\*\* Dropped") or "## X Dropped\n\n*None.*"
    preserved_changes = extract_preserved_section(existing, "Coverage changes — last 30 days") or "## Coverage changes — last 30 days\n\n*Empty.*"
    preserved_performance = extract_preserved_section(existing, "Performance / audit log") or "## Performance / audit log\n\n*Empty for now.*"
    preserved_screens = extract_preserved_section(existing, "Recent screens") or "## Recent screens\n\n*None.*"

    # Detect newly-initiated coverage by diffing against the prior INDEX master table.
    # See guide/scan/structure.md § INDEX.md format (Coverage changes — last 30 days).
    prior_tickers = parse_prior_tickers(existing)
    new_scans: list[Scan] = []
    for s in stocks:
        if s.ticker not in prior_tickers:
            new_scans.append(s)
    for s in trackers:
        if s.ticker == "MACRO":
            continue
        if s.ticker not in prior_tickers:
            new_scans.append(s)
    if new_scans:
        preserved_changes = inject_initiated_rows(preserved_changes, new_scans, today)

    summary = render_summary(stocks, trackers)
    macro = next((t for t in trackers if t.ticker == "MACRO"), None)
    if macro:
        macro_link_line = f"**Macro regime:** [MACRO](MACRO/current.md)"
        if macro.quadrant:
            macro_link_line += f" — {macro.quadrant}"
    else:
        macro_link_line = "**Macro regime:** *not yet scanned — run `/scan-macro`*"

    body = f"""# Scanned — Coverage Index

**Last regenerated:** {today.isoformat()}
{macro_link_line}
{summary}

This is the trader-desk equivalent of an institutional research coverage list — every name we scan, with **a tier per horizon** (Positional / Swing / Day-trade) so the framework matches reality: a name can be auto-reject long-term but a clean swing or scalp.

Full mapping rules in [`guide/scan/tiers.md`](../guide/scan/tiers.md).

---

## Coverage tiers — quick legend

**Horizons:** Pos = weeks-to-months · Swing = 3–15 days · Day = same-day intraday

**Tiers:** **T** Top Pick · **W** Watchlist (live trigger) · **B** Bench (no live trigger) · **S** Skip (auto-reject / hostile) · **X** Dropped · `—` N/A (horizon not read or doesn't apply)

---

## Master coverage table

{render_master_table(stocks, today)}

---

{render_focus_block(stocks, "Pos", "Positional Top Picks + Watchlist")}

---

{render_focus_block(stocks, "Swing", "Swing Top Picks + Watchlist")}

---

{render_focus_block(stocks, "Day", "Day-trade / Intraday Top Picks + Watchlist")}

---

{preserved_dropped.rstrip()}

---

{render_macro_section(trackers)}

---

{render_catalyst_monitor(stocks, trackers, today)}

---

{preserved_changes.rstrip()}

---

{preserved_performance.rstrip()}

---

{preserved_screens.rstrip()}

---

**Legend:** ⚠ stale (> 14 days)  ·  🔥 catalyst within 7 days
"""

    INDEX.write_text(body, encoding="utf-8")
    print(f"Regenerated {INDEX.relative_to(ROOT)}")
    print(f"  Stocks: {len(stocks)} ({sum(1 for s in stocks if s.pos_tier in ('T','W'))} Pos active / "
          f"{sum(1 for s in stocks if s.swing_tier in ('T','W'))} Swing active / "
          f"{sum(1 for s in stocks if s.day_tier in ('T','W'))} Day active)")
    print(f"  Trackers: {len(trackers)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
