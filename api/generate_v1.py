#!/usr/bin/env python3
"""
api/generate_v1.py

Minimal generator for godscore-ci API v1 output.
- Reads a base template JSON (schema/example)
- Injects context from env vars (GitHub Actions-friendly)
- Optionally reads signals from a JSON file (GODSCORE_SIGNALS_PATH)
- Optionally reads declared policies from a JSON file (GODSCORE_POLICY_PATH)
- Emits:
  - outputs.explanations[] (machine-readable)
  - outputs.evidence[] (proof pointers)
  - outputs.metrics{} (stable aggregates)
  - outputs.metrics.chi_* (Constraint Honesty metrics + status)
  - outputs.recommendations[] (policy-specific next steps)
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict


def load_json_obj(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("root must be a JSON object")
    return data


def save_json(path: str, data: Dict[str, Any]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=False)
        f.write("\n")


def iso_utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def env(name: str, default: str = "") -> str:
    v = os.getenv(name)
    return v if (v is not None and v != "") else default


def load_signals(path: str) -> list[dict[str, Any]]:
    if not path:
        return []
    try:
        data = load_json_obj(path)
        if isinstance(data.get("signals"), list):
            return [s for s in data["signals"] if isinstance(s, dict)]
    except FileNotFoundError:
        return []
    except Exception:
        return []
    return []


def load_policies(path: str) -> list[dict[str, Any]]:
    if not path:
        return []
    try:
        data = load_json_obj(path)
        if isinstance(data.get("policies"), list):
            return [p for p in data["policies"] if isinstance(p, dict)]
    except FileNotFoundError:
        return []
    except Exception:
        return []
    return []


def _signal_ids(signals: list[dict[str, Any]]) -> list[str]:
    ids: list[str] = []
    for s in signals:
        sid = s.get("id")
        if isinstance(sid, str) and sid:
            ids.append(sid)
    return ids


def compute_metrics(signals: list[dict[str, Any]]) -> dict[str, Any]:
    by_sev = {
        "info": 0,
        "low": 0,
        "medium": 0,
        "high": 0,
        "critical": 0,
        "unknown": 0,
    }

    for s in signals:
        sev = s.get("severity")
        if isinstance(sev, str):
            sev_norm = sev.strip().lower()
        else:
            sev_norm = "unknown"
        if sev_norm not in by_sev:
            sev_norm = "unknown"
        by_sev[sev_norm] += 1

    return {
        "signal_count": len(signals),
        "signals_by_severity": by_sev,
    }


def chi_status(chi_policy_count: int, chi_ratio: float, honest_threshold: float) -> str:
    if chi_policy_count <= 0:
        return "unknown"
    if chi_ratio >= honest_threshold:
        return "honest"
    return "drifting"


def compute_chi_metrics(policies: list[dict[str, Any]], evidence: list[dict[str, Any]]) -> dict[str, Any]:
    policy_count = len(policies)

    ev_index = set()
    for ev in evidence:
        kind = ev.get("kind")
        locator = ev.get("locator")
        if isinstance(kind, str) and isinstance(locator, str):
            ev_index.add((kind, locator))

    enforced = 0
    drifted: list[str] = []

    for p in policies:
        pid = p.get("id") if isinstance(p.get("id"), str) else "unknown"
        ek = p.get("evidence_kind")
        el = p.get("evidence_locator")
        if isinstance(ek, str) and isinstance(el, str) and (ek, el) in ev_index:
            enforced += 1
        else:
            drifted.append(pid)

    drift_count = policy_count - enforced
    ratio = enforced / (policy_count if policy_count > 0 else 1)

    thresholds = {"honest_ratio_gte": 0.90}
    status = chi_status(policy_count, ratio, thresholds["honest_ratio_gte"])

    return {
        "chi_policy_count": policy_count,
        "chi_enforced_count": enforced,
        "chi_drift_count": drift_count,
        "chi_ratio": ratio,
        "chi_drift_policy_ids": drifted,
        "chi_status": status,
        "chi_thresholds": thresholds
    }


def baseline_evidence(signals: list[dict[str, Any]], signals_path: str, policy_path: str) -> list[dict[str, Any]]:
    signal_ids = _signal_ids(signals)
    metrics = compute_metrics(signals)

    evidence: list[dict[str, Any]] = []

    evidence.append(
        {
            "id": "evidence.output.file",
            "kind": "file",
            "source": "ci",
            "locator": "api/out/godscore.output.v1.json",
            "summary": "Generated API v1 output JSON.",
            "details": {},
            "signals": []
        }
    )

    if signals_path:
        evidence.append(
            {
                "id": "evidence.inputs.signals.file",
                "kind": "file",
                "source": "repo",
                "locator": signals_path,
                "summary": "Signals JSON ingested into inputs.signals.",
                "details": {"signal_count": metrics["signal_count"]},
                "signals": signal_ids
            }
        )
    else:
        evidence.append(
            {
                "id": "evidence.inputs.signals.none",
                "kind": "metric",
                "source": "system",
                "locator": "inputs.signals",
                "summary": "No signals file provided; inputs.signals is empty.",
                "details": {"signal_count": 0},
                "signals": []
            }
        )

    if policy_path:
        evidence.append(
            {
                "id": "evidence.policies.file",
                "kind": "file",
                "source": "repo",
                "locator": policy_path,
                "summary": "Declared policies used for CHI metrics.",
                "details": {},
                "signals": []
            }
        )

    evidence.append(
        {
            "id": "evidence.enforcement.api_contract_check",
            "kind": "ci_check",
            "source": "ci",
            "locator": "API Contract (v1)",
            "summary": "CI validates output against API v1 contract.",
            "details": {},
            "signals": []
        }
    )

    return evidence


def baseline_explanations(signals: list[dict[str, Any]], chi: dict[str, Any]) -> list[dict[str, Any]]:
    signal_ids = _signal_ids(signals)

    return [
        {
            "id": "explain.api.contract.v1",
            "kind": "system",
            "severity": "info",
            "message": "API v1 contract output generated.",
            "details": {"contract_version": "1.0.0"},
            "signals": []
        },
        {
            "id": "explain.inputs.signals.ingested",
            "kind": "system",
            "severity": "info",
            "message": "Signals ingested into inputs.signals.",
            "details": {"signal_count": len(signals)},
            "signals": signal_ids
        },
        {
            "id": "explain.score.placeholder",
            "kind": "system",
            "severity": "info",
            "message": "Score is placeholder (0). Scoring logic not enabled yet.",
            "details": {"score": 0, "status": "placeholder"},
            "signals": []
        },
        {
            "id": "explain.enforcement.disabled",
            "kind": "enforcement",
            "severity": "info",
            "message": "Enforcement is not applied by this generator.",
            "details": {"enforcement": "disabled"},
            "signals": []
        },
        {
            "id": "explain.chi.status",
            "kind": "compliance",
            "severity": "info",
            "message": "CHI status computed from declared policies vs enforcement evidence.",
            "details": {
                "chi_status": chi.get("chi_status", "unknown"),
                "chi_ratio": chi.get("chi_ratio", 0.0),
                "chi_policy_count": chi.get("chi_policy_count", 0),
                "chi_enforced_count": chi.get("chi_enforced_count", 0),
                "chi_drift_count": chi.get("chi_drift_count", 0),
                "chi_thresholds": chi.get("chi_thresholds", {}),
                "chi_drift_policy_ids": chi.get("chi_drift_policy_ids", [])
            },
            "signals": []
        }
    ]


def build_recommendations(
    chi: dict[str, Any],
    policies: list[dict[str, Any]],
    evidence: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """
    Policy-specific recommendations:
    - For each drifted policy, suggest adding matching evidence (kind + locator).
    """
    drifted = chi.get("chi_drift_policy_ids", [])
    if not isinstance(drifted, list):
        drifted = []

    # index policies by id
    pol_index: dict[str, dict[str, Any]] = {}
    for p in policies:
        pid = p.get("id")
        if isinstance(pid, str) and pid:
            pol_index[pid] = p

    evidence_ids: list[str] = []
    for ev in evidence:
        if isinstance(ev, dict):
            eid = ev.get("id")
            if isinstance(eid, str) and eid:
                evidence_ids.append(eid)

    recs: list[dict[str, Any]] = []

    if len(policies) == 0:
        recs.append(
            {
                "id": "rec.chi.add_policies",
                "kind": "compliance",
                "severity": "low",
                "message": "No declared policies found. Add api/policy.v1.json entries to enable CHI measurement.",
                "details": {"policy_path_default": "api/policy.v1.json"},
                "policies": [],
                "evidence": evidence_ids
            }
        )
        return recs

    if len(drifted) == 0:
        recs.append(
            {
                "id": "rec.chi.maintain_alignment",
                "kind": "compliance",
                "severity": "low",
                "message": "Declared policies appear aligned with enforcement evidence. Maintain this alignment as policies evolve.",
                "details": {},
                "policies": [],
                "evidence": evidence_ids
            }
        )
        return recs

    for pid in drifted:
        if not isinstance(pid, str) or not pid:
            continue

        p = pol_index.get(pid, {})
        ek = p.get("evidence_kind")
        el = p.get("evidence_locator")

        suggested = {}
        if isinstance(ek, str) and isinstance(el, str):
            suggested = {"kind": ek, "locator": el}

        safe_id = pid.replace(" ", "_").replace("/", "_").replace(":", "_")

        recs.append(
            {
                "id": f"rec.chi.policy.{safe_id}.add_evidence",
                "kind": "compliance",
                "severity": "medium",
                "message": f"Policy '{pid}' lacks matching enforcement evidence. Add or emit the suggested evidence entry to close CHI drift.",
                "details": {
                    "policy_id": pid,
                    "suggested_evidence": suggested
                },
                "policies": [pid],
                "evidence": evidence_ids
            }
        )

    # also include a roll-up recommendation
    recs.insert(
        0,
        {
            "id": "rec.chi.close_drift",
            "kind": "compliance",
            "severity": "high" if len(drifted) > 3 else "medium",
            "message": "Close CHI drift by adding enforcement evidence for each drifted policy.",
            "details": {"drift_policy_count": len(drifted)},
            "policies": drifted,
            "evidence": evidence_ids
        }
    )

    return recs


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("Usage: python api/generate_v1.py <template.json> <output.json>")
        return 1

    template_path, output_path = argv[1], argv[2]
    data = load_json_obj(template_path)

    repo = env("GITHUB_REPOSITORY", data.get("context", {}).get("repo", ""))
    ref = env("GITHUB_REF", data.get("context", {}).get("ref", ""))
    sha = env("GITHUB_SHA", data.get("context", {}).get("sha", ""))
    run_id = env("GITHUB_RUN_ID", data.get("context", {}).get("run_id", "local"))

    signals_path = env("GODSCORE_SIGNALS_PATH", "")
    signals = load_signals(signals_path) if signals_path else []

    policy_path = env("GODSCORE_POLICY_PATH", "api/policy.v1.json")
    policies = load_policies(policy_path)

    # Fill timestamps + context
    data["generated_at"] = iso_utc_now()
    data.setdefault("context", {})
    data["context"]["repo"] = repo
    data["context"]["ref"] = ref
    data["context"]["sha"] = sha
    data["context"]["run_id"] = run_id

    # Keep subject aligned with repo by default
    data.setdefault("subject", {})
    data["subject"]["type"] = data["subject"].get("type", "repo") or "repo"
    data["subject"]["id"] = repo or data["subject"].get("id", "unknown")

    # Inputs: signals
    data.setdefault("inputs", {})
    data["inputs"]["signals"] = signals

    # Outputs: build evidence first (CHI uses it)
    data.setdefault("outputs", {})
    evidence = baseline_evidence(signals, signals_path, policy_path)
    chi = compute_chi_metrics(policies, evidence)

    # Explanations + evidence
    data["outputs"]["explanations"] = baseline_explanations(signals, chi)
    data["outputs"]["evidence"] = evidence

    # Recommendations (policy-specific)
    data["outputs"]["recommendations"] = build_recommendations(chi, policies, evidence)

    # Metrics: base + CHI
    metrics = compute_metrics(signals)
    metrics.update(chi)
    data["outputs"]["metrics"] = metrics

    save_json(output_path, data)
    print(f"[ok] wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
