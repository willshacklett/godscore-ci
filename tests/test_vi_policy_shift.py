from godscore_ci.envs import BridgeOrchardEnv
from godscore_ci.planning.value_iteration import backward_value_iteration


def test_gv_penalty_changes_start_action():
    env = BridgeOrchardEnv(
        T=20,
        r_harvest=1.0,
        c_repair=-0.2,
        r_burn=6.0,
    )
    gamma = 0.98
    s0 = env.start_state()

    _, pi_base = backward_value_iteration(env, gamma=gamma, lam=0.0)
    _, pi_gv = backward_value_iteration(env, gamma=gamma, lam=3.0)

    assert pi_gv[s0] == "REPAIR"
    assert pi_base[s0] != pi_gv[s0]
