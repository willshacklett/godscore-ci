#!/usr/bin/env python3
"""
v0_run.py — tiny local runner for the v0_runtime demo.

This file is intentionally defensive:
- It works even if GVState's constructor signature changes (positional vs keyword args).
- It works whether scenarios are callables (that mutate state) OR pre-baked event lists.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

# Local v0_runtime modules
from gv_runtime import GVState  # type: ignore
import scenarios  # type: ignore


ScenarioType = Union[
    Callable[..., Any],           # e.g. def stable(state): ...
    List[Dict[str, Any]],         # e.g. [{"component":"x","penalty":0.1}, ...]
    Dict[str, Any],               # e.g. {"events":[...], ...}
]


def _utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _safe_state_to_dict(state: Any) -> Dict[str, Any]:
    if is_dataclass(state):
        return asdict(state)
    if hasattr(state, "to_dict") and callable(getattr(state, "to_dict")):
        try:
            return state.to_dict()
        except Exception:
            pass
    # Fallback: best-effort public attrs
    out: Dict[str, Any] = {}
    for k in dir(state):
        if k.startswith("_"):
            continue
        try:
            v = getattr(state, k)
        except Exception:
            continue
        if callable(v):
            continue
        # Keep it JSON-ish
        if isinstance(v, (str, int, float, bool, type(None), list, dict)):
            out[k] = v
    return out


def _set_threshold_best_effort(state: Any, threshold: float) -> None:
    """
    If GVState doesn't accept threshold in __init__, set it after creation
    using a few common attribute names.
    """
    for attr in ("threshold", "gv_threshold", "limit", "max_gv", "max_allowed", "risk_threshold"):
        if hasattr(state, attr):
            try:
                setattr(state, attr, threshold)
                return
            except Exception:
                pass


def _make_state(threshold: float) -> Any:
    """
    Create GVState robustly across signature changes.
    """
    # 1) Try keyword
    try:
        return GVState(threshold=threshold)
    except TypeError:
        pass

    # 2) Try positional
    try:
        return GVState(threshold)
    except TypeError:
        pass

    # 3) No-arg + set attribute best-effort
    state = GVState()
    _set_threshold_best_effort(state, threshold)
    return state


def _extract_events_from_scenario_result(result: Any) -> List[Dict[str, Any]]:
    """
    Normalize whatever a scenario returns into an event list.
    """
    if result is None:
        return []

    if isinstance(result, list):
        # Ensure list of dicts
        out: List[Dict[str, Any]] = []
        for item in result:
            if isinstance(item, dict):
                out.append(item)
            else:
                out.append({"event": str(item)})
        return out

    if isinstance(result, dict):
        # Common pattern: {"events":[...]}
        if "events" in result and isinstance(result["events"], list):
            return _extract_events_from_scenario_result(result["events"])
        return [result]

    # Anything else -> one event
    return [{"result": str(result)}]


def _compute_gv_from_state_or_events(state: Any, events: List[Dict[str, Any]]) -> Tuple[float, Dict[str, Any]]:
    """
    Prefer GV provided by the state; else estimate from event penalties.
    Returns (gv, explanation).
    """
    # If state already exposes gv / score
    for attr in ("gv", "GV", "gv_total", "total_gv", "risk", "risk_total"):
        if hasattr(state, attr):
            try:
                v = float(getattr(state, attr))
                return v, {"source": f"state.{attr}"}
            except Exception:
                pass

    # If state has a method to compute gv
    for meth in ("compute_gv", "gv_value", "score", "compute"):
        if hasattr(state, meth) and callable(getattr(state, meth)):
            try:
                v = float(getattr(state, meth)())
                return v, {"source": f"state.{meth}()"}
            except Exception:
                pass

    # Fallback: sum up anything that looks like a penalty
    penalty_sum = 0.0
    components: Dict[str, float] = {}
    for ev in events:
        # Common keys: penalty, delta, gv, risk
        p = None
        for key in ("penalty", "delta", "gv", "risk", "dgv"):
            if key in ev:
                try:
                    p = float(ev[key])
                    break
                except Exception:
                    pass
        if p is None:
            continue
        penalty_sum += p
        comp = str(ev.get("component", ev.get("name", "unknown")))
        components[comp] = components.get(comp, 0.0) + p

    return penalty_sum, {"source": "events", "components": components}


def run(name: str, scenario_obj: ScenarioType, threshold: float = 1.0) -> Dict[str, Any]:
    state = _make_state(threshold)

    # scenario can be:
    # - callable expecting (state) or (state, threshold) or nothing
    # - list/dict representing events
    events: List[Dict[str, Any]] = []

    if callable(scenario_obj):
        # Try a few invocation patterns
        try:
            result = scenario_obj(state, threshold)
        except TypeError:
            try:
                result = scenario_obj(state)
            except TypeError:
                result = scenario_obj()

        events = _extract_events_from_scenario_result(result)
    else:
        events = _extract_events_from_scenario_result(scenario_obj)

    gv, gv_meta = _compute_gv_from_state_or_events(state, events)

    # GodScore (simple: 1 - GV). Clamp to [0,1] then provide 0-100 too.
    godscore_01 = max(0.0, min(1.0, 1.0 - gv))
    godscore_100 = round(godscore_01 * 100.0, 2)

    # Flag if GV crosses threshold (best-effort)
    crossed = None
    try:
        crossed = bool(gv > float(threshold))
    except Exception:
        crossed = None

    record = {
        "ts_utc": _utc_iso(),
        "scenario": name,
        "threshold": float(threshold),
        "gv": float(gv),
        "godscore": godscore_100,
        "godscore_01": godscore_01,
        "crossed_threshold": crossed,
        "events": events,
        "gv_meta": gv_meta,
        "state": _safe_state_to_dict(state),
    }
    return record


def _default_scenarios() -> List[Tuple[str, ScenarioType]]:
    """
    If scenarios.py changes, this still tries to find something runnable.
    """
    pairs: List[Tuple[str, ScenarioType]] = []

    # Preferred, explicit
    for name in ("stable", "thrble", "trouble", "recover", "drift", "attack"):
        if hasattr(scenarios, name):
            obj = getattr(scenarios, name)
            # If it's a factory function (stable()), call it. If it's a scenario callable, keep it.
            try:
                # Heuristic: if it's callable with zero args and returns list/dict, treat it as factory.
                if callable(obj):
                    try:
                        res = obj()
                        if isinstance(res, (list, dict)):
                            pairs.append((name, res))
                        else:
                            pairs.append((name, obj))
                    except TypeError:
                        pairs.append((name, obj))
                else:
                    pairs.append((name, obj))
            except Exception:
                pairs.append((name, obj))

    # Fallback: grab any public callables in scenarios.py that look like scenarios
    if not pairs:
        for k in dir(scenarios):
            if k.startswith("_"):
                continue
            obj = getattr(scenarios, k)
            if callable(obj):
                pairs.append((k, obj))

    return pairs


def main() -> None:
    threshold = float(os.environ.get("GV_THRESHOLD", "1.0"))

    results: List[Dict[str, Any]] = []
    for name, scen in _default_scenarios():
        results.append(run(name, scen, threshold=threshold))

    # Pretty print summary
    print("\n=== v0_runtime results ===")
    for r in results:
        print(f"- {r['scenario']:<10}  GV={r['gv']:.4f}  GodScore={r['godscore']:.2f}  crossed={r['crossed_threshold']}")

    # Write JSONL + CSV-ish (no pandas needed)
    out_dir = os.path.join(os.path.dirname(__file__), "out")
    os.makedirs(out_dir, exist_ok=True)

    jsonl_path = os.path.join(out_dir, "v0_results.jsonl")
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # Minimal CSV summary
    csv_path = os.path.join(out_dir, "v0_results.csv")
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write("ts_utc,scenario,threshold,gv,godscore,godscore_01,crossed_threshold\n")
        for r in results:
            f.write(
                f"{r['ts_utc']},{r['scenario']},{r['threshold']},{r['gv']},{r['godscore']},{r['godscore_01']},{r['crossed_threshold']}\n"
            )

    print(f"\nWrote:\n- {jsonl_path}\n- {csv_path}\n")


if __name__ == "__main__":
    main()
