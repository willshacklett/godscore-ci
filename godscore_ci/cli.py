from __future__ import annotations

import argparse
from pathlib import Path

# We’ll hook this into your existing scorer logic next.
# For now, it prints a placeholder and proves the CLI plumbing works.
def main() -> int:
    parser = argparse.ArgumentParser(prog="godscore")
    sub = parser.add_subparsers(dest="cmd", required=True)

    score = sub.add_parser("score", help="Score a folder and emit reports.")
    score.add_argument("path", nargs="?", default=".", help="Project path (default: .)")
    score.add_argument("--outdir", default="gv_out", help="Output directory (default: gv_out)")

    args = parser.parse_args()

    if args.cmd == "score":
        outdir = Path(args.outdir)
        outdir.mkdir(parents=True, exist_ok=True)

        # placeholder report files (we’ll replace with real output next step)
        (outdir / "gv_report.json").write_text('{\n  "gv_score": 0.5,\n  "note": "CLI wiring OK. Next: connect real scoring."\n}\n', encoding="utf-8")
        (outdir / "gv_report.md").write_text("# GodScore CI Report\n\n**Gv Score:** `0.5`\n\nCLI wiring OK. Next: connect real scoring.\n", encoding="utf-8")

        print("Gv Score: 0.5")
        print(f"Wrote: {outdir / 'gv_report.json'}")
        print(f"Wrote: {outdir / 'gv_report.md'}")
        return 0

    return 2

