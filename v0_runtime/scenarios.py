import numpy as np

def stable(T=80, mu=0.0, sigma=0.02, risk=0.0, seed=1):
    rng = np.random.default_rng(seed)
    for t in range(T):
        signal = rng.normal(mu, sigma)
        yield signal, risk, True  # update baseline

def gradual_drift(T=120, start=0.0, slope=0.01, sigma=0.03, risk_start=0.0, risk_slope=0.002, seed=2):
    rng = np.random.default_rng(seed)
    for t in range(T):
        signal = start + slope * t + rng.normal(0.0, sigma)
        risk = min(1.0, risk_start + risk_slope * t)
        yield signal, risk, False # do not “learn” baseline during drift

def abrupt_violation(T=80, jump_at=40, jump=1.5, sigma=0.02, seed=3):
    rng = np.random.default_rng(seed)
    for t in range(T):
        base = rng.normal(0.0, sigma)
        if t >= jump_at:
            signal = base + jump
            risk = 1.0
        else:
            signal = base
            risk = 0.0
        yield signal, risk, False
