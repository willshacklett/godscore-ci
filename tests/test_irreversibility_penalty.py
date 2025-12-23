from godscore_ci.envs import BridgeOrchardEnv


def test_burn_live_orchard_has_penalty():
    env = BridgeOrchardEnv()
    s = (0, 0, 1)
    assert env.delta_omega(s, "BURN") == 1.0


def test_burn_dead_orchard_no_penalty():
    env = BridgeOrchardEnv()
    s = (0, 0, 0)
    assert env.delta_omega(s, "BURN") == 0.0
