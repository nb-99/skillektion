#!/usr/bin/env python3
# dump.py — quick text dump of a spreadsheet: cell address, stored formula,
# cached value. Use it to read a workbook without opening Excel, and to see
# whether formula cells carry cached values (openpyxl-written files do not
# until something recalculates and saves).
#
# Usage:
#   python3 dump.py FILE [--sheet NAME] [--limit N] [--all] [--values-only]
#
# Each line: `ADDR  formula ->  cached` for formulas, `ADDR  value` otherwise.
# `<no cached value>` marks a formula cell that no reader can evaluate yet.
# Exit 0 normally; exit 2 on unreadable file/missing sheet.

import argparse
import sys

from openpyxl import load_workbook
from openpyxl.cell.cell import MergedCell


def fmt(v):
    if v is None:
        return ""
    if isinstance(v, str) and ("\n" in v or v.strip() == ""):
        return repr(v)
    if isinstance(v, float) and v.is_integer():
        return str(int(v))
    return str(v)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1] if __doc__ else "dump a spreadsheet")
    ap.add_argument("file")
    ap.add_argument("--sheet", help="dump only this sheet (name must match exactly)")
    ap.add_argument("--limit", type=int, default=200,
                    help="max non-empty cells printed per sheet (default 200)")
    ap.add_argument("--all", action="store_true", help="no cell limit")
    ap.add_argument("--values-only", action="store_true",
                    help="print plain values, skip formulas and the second pass")
    args = ap.parse_args()

    try:
        wbf = load_workbook(args.file, data_only=False)
    except Exception as e:
        print(f"error: cannot open {args.file}: {e}", file=sys.stderr)
        sys.exit(2)
    wbv = None if args.values_only else load_workbook(args.file, data_only=True)

    if args.sheet:
        if args.sheet not in wbf.sheetnames:
            print(f"error: no sheet named {args.sheet!r} "
                  f"(have: {', '.join(wbf.sheetnames)})", file=sys.stderr)
            sys.exit(2)

    for name in wbf.sheetnames:
        if args.sheet and name != args.sheet:
            continue
        ws = wbf[name]
        print(f"=== {name}  dims={ws.dimensions}"
              f"{'  (merged: ' + ', '.join(str(r) for r in ws.merged_cells.ranges) + ')' if ws.merged_cells.ranges else ''}")
        shown = 0
        for row in ws.iter_rows():
            for cell in row:
                if isinstance(cell, MergedCell):
                    continue  # non-anchor part of a merged range: read-only, no own value
                v = cell.value
                if v is None:
                    continue
                if not args.all and shown >= args.limit:
                    print(f"    ... (limit {args.limit} reached; use --all)")
                    break
                shown += 1
                if isinstance(v, str) and v.startswith("=") and not args.values_only:
                    cached = wbv[name][cell.coordinate].value if wbv else None
                    tail = f" ->  {fmt(cached)}" if cached is not None \
                        else " ->  <no cached value — not recalculated>"
                    print(f"    {cell.coordinate:<6} {v}{tail}")
                else:
                    print(f"    {cell.coordinate:<6} {fmt(v)}")
        print(f"    ({shown} non-empty cells)")
    sys.exit(0)


if __name__ == "__main__":
    main()
