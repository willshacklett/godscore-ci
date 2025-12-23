from __future__ import annotations

from statistics import mean

from godscore_ci.toy_sim import ToySystem, run_trial


def test_ablation_error_correction_reduces_survival():
    """
    Ablation: hold redundancy/coherence/adaptability fixed, remove error correction.
    Expect survival to drop substantially on average.
    """

    base = ToySystem(
        redundancy=0.70,
        repair_rate=0.60,        # has error correction
        coherence_penalty=0.30,
        adaptability=0.35,
    )

    ablated = ToySystem(
        redundancy=0.70,
        repair_rate=0.00,        # error correction removed
        coherence_penalty=0.30,
        adaptability=0.35,
    )

    seeds = list(range(40))
    base_steps = [run_trial(ToySystem(**base.__dict__), seed=s) for s in seeds]
    ablated_steps = [run_trial(ToySystem(**ablated.__dict__), seed=s) for s in seeds]

    base_mean = mean(base_steps)
    ablated_mean = mean(ablated_steps)

    # Strong expectation: removing repair should meaningfully reduce survival.
    assert ablated_mean < base_mean * 0.70, (
        f"Expected ablation to reduce survival by >=30%. "
        f"base_mean={base_mean:.2f}, ablated_mean={ablated_mean:.2f}"
    )


def test_ablation_lowers_gv_score():
    base = ToySystem(redundancy=0.70, repair_rate=0.60, coherence_penalty=0.30, adaptability=0.35)
    ablated = ToySystem(redundancy=0.70, repair_rate=0.00, coherence_penalty=0.30, adaptability=0.35)

    assert ablated.score() < base.score()
