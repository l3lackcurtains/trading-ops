#!/usr/bin/env python3
"""Prune scanned/<asset-class>/<TICKER>/archive/ per the retention policy.

Policy (from guide/scan/protocol.md § Retention policy):
- Keep the latest snapshot per calendar month
- Drop snapshots older than 12 months (> 365 days before today)
- Always keep current.md (this script never touches it)

Usage:
  python3 scripts/prune_archive.py <ticker-folder>
  python3 scripts/prune_archive.py scanned/stocks/NIO
  python3 scripts/prune_archive.py --all   # prune every ticker folder under scanned/

Safe by default: dry-run unless --apply is passed.
"""
from __future__ import annotations

import argparse
import datetime as dt
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCANNED = ROOT / "scanned"
ASSET_CLASSES = ["stocks", "fx", "indices", "crypto", "commodities"]
DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})\.md$")


def prune_one(folder: pathlib.Path, today: dt.date, apply: bool) -> int:
    archive = folder / "archive"
    if not archive.is_dir():
        return 0
    files = []
    for p in archive.iterdir():
        m = DATE_RE.match(p.name)
        if not m:
            continue
        try:
            d = dt.date.fromisoformat(m.group(1))
        except ValueError:
            continue
        files.append((d, p))
    if not files:
        return 0

    to_delete = []

    # Drop > 365 days old
    for d, p in files:
        if (today - d).days > 365:
            to_delete.append(p)

    # Keep only newest per month
    by_month: dict[str, list[tuple[dt.date, pathlib.Path]]] = {}
    for d, p in files:
        if (today - d).days > 365:
            continue
        key = f"{d.year}-{d.month:02d}"
        by_month.setdefault(key, []).append((d, p))
    for key, group in by_month.items():
        group.sort(key=lambda x: x[0], reverse=True)
        for d, p in group[1:]:
            to_delete.append(p)

    if not to_delete:
        return 0

    label = "DELETING" if apply else "[dry-run] would delete"
    for p in to_delete:
        print(f"  {label}: {p.relative_to(ROOT)}")
        if apply:
            p.unlink()
    return len(to_delete)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", nargs="?", help="path to a ticker folder (e.g. scanned/stocks/NIO)")
    parser.add_argument("--all", action="store_true", help="prune every ticker folder under scanned/")
    parser.add_argument("--apply", action="store_true", help="actually delete (default is dry-run)")
    args = parser.parse_args()

    today = dt.date.today()
    targets: list[pathlib.Path] = []

    if args.all:
        for cls in ASSET_CLASSES:
            cls_dir = SCANNED / cls
            if cls_dir.is_dir():
                targets.extend(p for p in cls_dir.iterdir() if p.is_dir())
        macro = SCANNED / "MACRO"
        if macro.is_dir():
            targets.append(macro)
    elif args.target:
        targets.append(pathlib.Path(args.target).resolve())
    else:
        parser.print_help()
        return 2

    total = 0
    for t in targets:
        n = prune_one(t, today, apply=args.apply)
        if n:
            print(f"{t.relative_to(ROOT)}: {n} file(s)")
        total += n

    if not args.apply and total:
        print(f"\nDry-run total: {total} file(s) would be deleted. Re-run with --apply to actually delete.")
    elif args.apply and total:
        print(f"\nDeleted {total} file(s).")
    elif total == 0:
        print("Nothing to prune.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
