from __future__ import annotations

from statistics import mean

from godscore_ci.toy_sim import ToySystem, run_trial


def test_robust_outlives_fragile_on_average():
    fragile = ToySystem(
        redundancy=0.10,
        repair_rate=0.10,
        coherence_penalty=0.80,
        adaptability=0.05,
    )

    robust = ToySystem(
        redundancy=0.70,
        repair_rate=0.60,
        coherence_penalty=0.30,
        adaptability=0.35,
    )

    seeds = list(range(30))

    fragile_steps = [
        run_trial(ToySystem(**fragile.__dict__), seed=s) for s in seeds
    ]
    robust_steps = [
        run_trial(ToySystem(**robust.__dict__), seed=s) for s in seeds
    ]

    assert mean(robust_steps) > mean(fragile_steps), (
        f"Expected robust to outlive fragile on average. "
        f"fragile_mean={mean(fragile_steps):.2f}, "
        f"robust_mean={mean(robust_steps):.2f}"
    )


def test_gv_score_higher_for_robust_baseline():
    fragile = ToySystem(
        redundancy=0.10,
        repair_rate=0.10,
        coherence_penalty=0.80,
        adaptability=0.05,
    )

    robust = ToySystem(
        redundancy=0.70,
        repair_rate=0.60,
        coherence_penalty=0.30,
        adaptability=0.35,
    )

    assert robust.score() > fragile.score()
