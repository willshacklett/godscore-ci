from __future__ import annotations

import argparse
from pathlib import Path

from .core import score_project
from .reporters import write_json, write_markdown


def main() -> int:
    parser = argparse.ArgumentParser(prog="godscore", description="Compute GodScore (Gv) for a project folder.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    score = sub.add_parser("score", help="Score a folder and emit reports.")
    score.add_argument("path", nargs="?", default=".", help="Project path (default: .)")
    score.add_argument("--outdir", default="gv_out", help="Output directory (default: gv_out)")

    args = parser.parse_args()

    if args.cmd == "score":
        report = score_project(args.path)
        outdir = Path(args.outdir)
        write_json(report, outdir / "gv_report.json")
        write_markdown(report, outdir / "gv_report.md")

        print(f"Gv Score: {report['gv_score']}")
        print(f"Wrote: {outdir / 'gv_report.json'}")
        print(f"Wrote: {outdir / 'gv_report.md'}")
        return 0

    return 2


