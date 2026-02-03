# godscore_ci/autoscore_v1.py
from __future__ import annotations

import os
import re
import subprocess
from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class AutoScoreV1Result:
    penalties: Dict[str, float]   # normalized 0.0–1.0 (higher = worse)
    signals: Dict[str, object]    # raw values (for logs/dashboard)
    notes: List[str]              # simple human-readable reasons


def _run(cmd: List[str]) -> str:
    return subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT).strip()


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def _guess_base_head() -> Tuple[str, str]:
    head = os.getenv("GITHUB_SHA") or "HEAD"

    base = os.getenv("GITHUB_EVENT_BEFORE")
    if not base or base == "0000000000000000000000000000000000000000":
        # fallback to previous commit if event payload doesn't provide base
        try:
            base = _run(["git", "rev-parse", "HEAD~1"])
        except Exception:
            base = head  # single-commit repo edge case

    return base, head


def _diff_numstat(base: str, head: str) -> Tuple[int, int, List[str]]:
    """
    Returns: (added_lines, deleted_lines, changed_files)
    """
    try:
        out = _run(["git", "diff", "--numstat", f"{base}..{head}"])
    except Exception:
        return 0, 0, []

    added = 0
    deleted = 0
    files: List[str] = []

    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) < 3:
            continue

        a, d, path = parts[0], parts[1], parts[2]

        # binary files show "-"
        if a.isdigit():
            added += int(a)
        if d.isdigit():
            deleted += int(d)

        files.append(path)

    return added, deleted, files


def _commit_message_lower() -> str:
    try:
        return _run(["git", "log", "-1", "--pretty=%B"]).lower()
    except Exception:
        return ""


def _docs_only(files: List[str]) -> bool:
    if not files:
        return False
    for f in files:
        f_low = f.lower()
        if f_low.startswith(("docs/", "doc/", ".github/")):
            continue
        if f_low.endswith((".md", ".rst", ".txt")):
            continue
        return False
    return True


def _risky_paths_hit(files: List[str]) -> Tuple[bool, bool]:
    """
    Returns: (risky, high_risk)
    """
    risky_prefixes = ("src/", "lib/", "app/", "api/", "infra/", "server/", "services/")
    high_risk_markers = ("auth", "security", "payments", "billing", "crypto", "secrets")

    risky = any(f.lower().startswith(risky_prefixes) for f in files)
    high_risk = any(any(m in f.lower() for m in high_risk_markers) for f in files)
    return risky, high_risk


def _has_test_signals(files: List[str]) -> bool:
    # broad cross-ecosystem “do you even have tests” heuristic
    markers = (
        "tests/",
        "test/",
        "pytest.ini",
        "tox.ini",
        "pyproject.toml",
        "package.json",
        "go.mod",
        "pom.xml",
        "build.gradle",
    )
    return any(any(m in f for m in markers) for f in files)


def _penalty_from_loc_changed(changed_loc: int) -> float:
    """
    Convert LOC changed -> normalized risk penalty 0..1
    """
    if changed_loc <= 50:
        return 0.05
    if changed_loc <= 200:
        return 0.15
    if changed_loc <= 500:
        return 0.30
    if changed_loc <= 1000:
        return 0.50
    return 0.75


def compute_autoscore_v1(base_sha: str | None = None, head_sha: str | None = None) -> AutoScoreV1Result:
    base, head = (base_sha, head_sha) if base_sha and head_sha else _guess_base_head()
    added, deleted, files = _diff_numstat(base, head)
    changed_loc = added + deleted

    msg = _commit_message_lower()
    docs_only = _docs_only(files)
    risky, high_risk = _risky_paths_hit(files)
    tests_detected = _has_test_signals(files)

    # --- penalties (0..1, higher = worse) ---
    penalties: Dict[str, float] = {}

    # 1) diff_risk: bigger diffs are harder to reason about / recover from
    diff_risk = _penalty_from_loc_changed(changed_loc)
    # docs-only gets a discount because it's usually lower risk
    if docs_only:
        diff_risk *= 0.25
    penalties["diff_risk"] = _clamp01(diff_risk)

    # 2) path_risk: sensitive areas amplify risk
    path_risk = 0.0
    if risky:
        path_risk += 0.20
    if high_risk:
        path_risk += 0.30
    if docs_only:
        path_risk = 0.0
    penalties["path_risk"] = _clamp01(path_risk)

    # 3) process_risk: WIP, no tests, etc. are “recoverability killers”
    process_risk = 0.0
    if re.search(r"\bwip\b|\btmp\b|\bdraft\b", msg):
        process_risk += 0.30
    if "revert" in msg:
        process_risk -= 0.10  # reverts often improve recoverability
    if files and not tests_detected and not docs_only:
        process_risk += 0.20
    penalties["process_risk"] = _clamp01(process_risk)

    # Optional: if nothing changed (rare), keep low penalties
    if changed_loc == 0 and not files:
        penalties["diff_risk"] = 0.05
        penalties["path_risk"] = 0.00
        penalties["process_risk"] = 0.00

    # --- signals + notes for explainability ---
    signals: Dict[str, object] = {
        "base": base,
        "head": head,
        "added": added,
        "deleted": deleted,
        "changed_loc": changed_loc,
        "files_changed": len(files),
        "docs_only": docs_only,
        "risky_paths": risky,
        "high_risk_area": high_risk,
        "tests_detected": tests_detected,
    }

    notes: List[str] = []
    notes.append(f"Diff changed LOC={changed_loc} (added={added}, deleted={deleted})")
    if docs_only:
        notes.append("Docs-only change detected (risk discounted).")
    if risky:
        notes.append("Risky code paths touched (src/lib/app/api/infra/...).")
    if high_risk:
        notes.append("High-risk area touched (auth/security/payments/billing/etc.).")
    if re.search(r"\bwip\b|\btmp\b|\bdraft\b", msg):
        notes.append("Commit message suggests WIP/tmp/draft.")
    if "revert" in msg:
        notes.append("Commit message indicates revert (small recoverability credit).")
    if files and not tests_detected and not docs_only:
        notes.append("No obvious test signals detected in changed set.")

    return AutoScoreV1Result(penalties=penalties, signals=signals, notes=notes)
