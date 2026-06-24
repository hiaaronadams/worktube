#!/usr/bin/env python3
"""Generate a self-contained static HTML RFP report.

    python generate_report.py                 # live sources, falls back to demo
    python generate_report.py --demo          # force sample data
    python generate_report.py --sources sam   # only specific sources
    python generate_report.py --out public    # write into ./public instead

Output: <out>/worktube-YYYY-MM-DD.html and <out>/index.html (the latest).
Open index.html in a browser, or host the folder anywhere (it's just files).
"""
from __future__ import annotations

import argparse
import logging

from worktube.pipeline import LIVE_ADAPTERS, build_report
from worktube.render import write_report


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a Worktube RFP report")
    parser.add_argument("--demo", action="store_true", help="use sample data")
    parser.add_argument("--sources", nargs="+", choices=sorted(LIVE_ADAPTERS),
                        help="limit to specific live sources (default: all)")
    parser.add_argument("--out", default="reports", help="output directory (default: reports)")
    parser.add_argument("--lookback-days", type=int, default=None, help="SAM.gov lookback window")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING)

    report = build_report(sources=args.sources, demo=args.demo, lookback_days=args.lookback_days)
    dated, latest = write_report(report, args.out)

    print(f"Report written:")
    print(f"  {latest}   (latest)")
    print(f"  {dated}")
    print(f"  {report.total} opportunities, {report.high_fit_count} high-fit "
          f"(≥{report.high_fit_threshold:g})" + ("  [DEMO DATA]" if report.demo else ""))
    for w in report.warnings:
        print(f"  ! {w}")


if __name__ == "__main__":
    main()
