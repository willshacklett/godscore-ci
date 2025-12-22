import numpy as np

from godscore.identity_signature import compute_identity_signature, compute_ics


def make_coupled_system(T=1500, N=5, seed=0):
    rng = np.random.default_rng(seed)
    X = np.zeros((T, N))
    A = np.eye(N) * 0.7
    for i in range(N - 1):
        A[i, i + 1] = 0.15
        A[i + 1, i] = 0.05

    noise = 0.4
    for t in range(1, T):
        X[t] = X[t - 1] @ A + rng.normal(0, noise, size=N)
    return X


def shuffle_time(X, seed=1):
    rng = np.random.default_rng(seed)
    Y = X.copy()
    for j in range(Y.shape[1]):
        rng.shuffle(Y[:, j])
    return Y


def test_signature_returns_finite_values():
    X = make_coupled_system()
    sig = compute_identity_signature(X)
    vec = sig.as_vector()

    assert vec.shape == (4,)
    assert np.isfinite(vec).all()


def test_structured_system_has_higher_recurrence_than_shuffled():
    X = make_coupled_system()
    Xs = shuffle_time(X)

    sig_struct = compute_identity_signature(X)
    sig_shuf = compute_identity_signature(Xs)

    assert sig_struct.recurrence > sig_shuf.recurrence


def test_identity_continuity_is_high_for_same_system():
    X = make_coupled_system()

    a = compute_identity_signature(X)
    b = compute_identity_signature(X)

    assert a.continuity_to(b) > 0.95


def test_ics_penalizes_high_decay():
    X = make_coupled_system()
    sig = compute_identity_signature(X)

    ics = compute_ics(sig)
    from godscore.identity_signature import IdentitySignature

    bad = IdentitySignature(
        sig.integration,
        sig.recurrence,
        sig.feedback,
        sig.decay + 5.0,
    )

    assert compute_ics(bad) < ics
