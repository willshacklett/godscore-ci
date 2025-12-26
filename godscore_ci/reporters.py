from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


def write_json(report: Dict[str, Any], out_path: str | Path) -> Path:
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out


def write_markdown(report: Dict[str, Any], out_path: str | Path) -> Path:
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    gv = report.get("gv_score", None)
    comps = report.get("components", {})

    lines = []
    lines.append("# GodScore CI Report")
    lines.append("")
    lines.append(f"**Gv Score:** `{gv}`")
    lines.append("")
    lines.append("## Components")
    for k, v in comps.items():
        lines.append(f"- **{k}**: `{v}`")
    lines.append("")

    notes = report.get("notes", [])
    if notes:
        lines.append("## Notes")
        for n in notes:
            lines.append(f"- {n}")
        lines.append("")

    out.write_text("\n".join(lines), encoding="utf-8")
    return out
