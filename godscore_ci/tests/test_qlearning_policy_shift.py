from godscore_ci.envs import BridgeOrchardEnv
from godscore_ci.rl.q_learning import QLearningConfig, train_q_learning, greedy_policy_from_q


def test_qlearning_policy_shift_start_state():
    """
    Deterministic-ish proof that learning + Gv penalty changes behavior.
    Fixed seed + enough episodes should make this stable.
    """
    env = BridgeOrchardEnv(T=20, r_harvest=1.0, c_repair=-0.2, r_burn=6.0)
    cfg = QLearningConfig(episodes=6000, seed=11, alpha=0.25, gamma=0.98, epsilon_start=0.6, epsilon_end=0.05)

    s0 = env.start_state()

    Q0 = train_q_learning(env, lam=0.0, cfg=cfg)
    pi0 = greedy_policy_from_q(env, Q0)

    Qg = train_q_learning(env, lam=3.0, cfg=cfg)
    pig = greedy_policy_from_q(env, Qg)

    assert pig[s0] == "REPAIR"
    assert pi0[s0] != pig[s0]
