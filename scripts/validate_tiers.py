#!/usr/bin/env python3
"""Validate Coverage tier syntax across every scanned/**/current.md.

Catches:
- Missing **Coverage tier:** line in stock scans
- Wrong tier letters (anything not in T / W / B / S / X / —)
- Wrong horizon order (must be Pos / Swing / Day)
- Plain `T` instead of `**T**` (tier letters should be bold in tables but the snapshot-line format accepts either)

Usage:
  python3 scripts/validate_tiers.py            # validate every current.md, exit non-zero on error
  python3 scripts/validate_tiers.py --fix      # auto-fix what we can (e.g., bold the letters)
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCANNED = ROOT / "scanned"
ASSET_CLASSES = ["stocks", "fx", "indices", "crypto", "commodities"]
VALID_TIERS = {"T", "W", "B", "S", "X", "—"}

TIER_LINE_RE = re.compile(
    r"\*\*Coverage tier:\*\*\s*Pos\s*\*?\*?([TWBSX—])\*?\*?\s*(\([^)]*\))?\s*[·•∙]\s*"
    r"Swing\s*\*?\*?([TWBSX—])\*?\*?\s*(\([^)]*\))?\s*[·•∙]\s*"
    r"Day\s*\*?\*?([TWBSX—])\*?\*?\s*(\([^)]*\))?",
)


def validate_file(p: pathlib.Path, asset_class: str) -> list[str]:
    """Return list of error messages. Empty list = clean."""
    body = p.read_text(encoding="utf-8")

    # FX/indices/crypto trackers don't need a tier line
    if asset_class != "stocks":
        return []

    m = TIER_LINE_RE.search(body)
    if not m:
        # Soft check: maybe Coverage tier line exists but in a non-canonical form
        if re.search(r"\*\*Coverage tier:\*\*", body):
            return [f"{p}: Coverage tier line present but doesn't match the canonical Pos · Swing · Day format"]
        return [f"{p}: missing **Coverage tier:** line in snapshot header"]

    pos, _, swing, _, day, _ = m.groups()
    errors = []
    for label, t in [("Pos", pos), ("Swing", swing), ("Day", day)]:
        if t not in VALID_TIERS:
            errors.append(f"{p}: invalid {label} tier '{t}' (must be one of T/W/B/S/X/—)")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fix", action="store_true", help="auto-fix tier-letter bolding (not implemented yet)")
    args = parser.parse_args()
    _ = args.fix  # placeholder

    all_errors: list[str] = []
    files_checked = 0

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
            files_checked += 1
            errors = validate_file(cur, asset_class=cls)
            all_errors.extend(errors)

    print(f"Checked {files_checked} current.md file(s).")

    if all_errors:
        print(f"\n{len(all_errors)} error(s) found:")
        for e in all_errors:
            print(f"  - {e}")
        return 1

    print("All Coverage tier lines valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
