from godscore_ci.envs import BridgeOrchardEnv
from godscore_ci.planning.value_iteration import backward_value_iteration


def run():
    env = BridgeOrchardEnv(
        T=20,
        r_harvest=1.0,
        c_repair=-0.2,
        r_burn=6.0,  # tuned so baseline prefers burn
    )
    gamma = 0.98

    # Baseline (no Gv penalty)
    _, pi_base = backward_value_iteration(env, gamma=gamma, lam=0.0)

    # Gv-shaped
    _, pi_gv = backward_value_iteration(env, gamma=gamma, lam=3.0)

    s0 = env.start_state()

    print("Start state:", s0)
    print("Baseline action:", pi_base[s0])
    print("Gv-shaped action:", pi_gv[s0])


if __name__ == "__main__":
    run()

