
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from godscore.moral_field import DEFAULT_CONFIG, phi_G, value, choose_action

def test_phi_G_monotone_in_good():
    w = DEFAULT_CONFIG.weights
    s1 = {"good": 0.5, "evil":0.1, "hope":0.5, "fear":0.2, "coherence":0.6, "harm":0.2}
    s2 = dict(s1, good=0.8)
    assert phi_G(s2, w) > phi_G(s1, w)

def test_choose_action_prefers_better_moral_potential():
    cfg = DEFAULT_CONFIG

    def eval_fn(state, a):
        # Hard constraints satisfied for both
        constraints = {"nonmaleficence":0.8, "autonomy":0.7, "justice":0.7, "truthfulness":0.9}

        if a == "a1":
            scores = {"good":0.58, "evil":0.10, "hope":0.55, "fear":0.22, "coherence":0.60, "harm":0.25}
            env_reward = 1.0
        else:
            scores = {"good":0.82, "evil":0.06, "hope":0.78, "fear":0.15, "coherence":0.85, "harm":0.18}
            env_reward = 1.0
        return {"env_reward": env_reward, "scores": scores, "constraints": constraints}

    best, val = choose_action(None, ["a1","a2"], eval_fn, cfg)
    assert best == "a2"

def test_hard_constraints_block_invalid_action():
    cfg = DEFAULT_CONFIG

    def eval_fn(state, a):
        if a == "bad":
            constraints = {"nonmaleficence":0.2, "autonomy":0.2, "justice":0.2, "truthfulness":0.2}
            scores = {"good":0.99, "evil":0.0, "hope":0.9, "fear":0.0, "coherence":0.9, "harm":0.0}
        else:
            constraints = {"nonmaleficence":0.9, "autonomy":0.9, "justice":0.9, "truthfulness":0.9}
            scores = {"good":0.6, "evil":0.2, "hope":0.6, "fear":0.2, "coherence":0.6, "harm":0.3}
        return {"env_reward": 0.0, "scores": scores, "constraints": constraints}

    best, _ = choose_action(None, ["bad","ok"], eval_fn, cfg)
    assert best == "ok"
