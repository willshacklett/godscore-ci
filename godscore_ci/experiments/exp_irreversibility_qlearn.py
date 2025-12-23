from godscore_ci.envs import BridgeOrchardEnv
from godscore_ci.rl.q_learning import QLearningConfig, train_q_learning, greedy_policy_from_q


def main():
    env = BridgeOrchardEnv(
        T=20,
        r_harvest=1.0,
        c_repair=-0.2,
        r_burn=6.0,  # makes burn tempting
    )

    cfg = QLearningConfig(episodes=5000, seed=7)

    # Baseline learner (no penalty)
    Q0 = train_q_learning(env, lam=0.0, cfg=cfg)
    pi0 = greedy_policy_from_q(env, Q0)

    # Gv-shaped learner
    Qg = train_q_learning(env, lam=3.0, cfg=cfg)
    pig = greedy_policy_from_q(env, Qg)

    s0 = env.start_state()
    print("Start state:", s0)
    print("Q-learn baseline action @ s0 (lam=0):", pi0[s0])
    print("Q-learn Gv-shaped action @ s0 (lam=3):", pig[s0])


if __name__ == "__main__":
    main()
