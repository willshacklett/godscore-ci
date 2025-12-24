from godscore import GodVariable


def test_gv_no_penalties_returns_base_score():
    gv = GodVariable(base_score=1.0)
    result = gv.evaluate({})
    assert result.score == 1.0
    assert result.penalties == {}


def test_gv_irreversible_harm_penalty_applied():
    gv = GodVariable(base_score=1.0)
    result = gv.evaluate({"irreversible_harm": 1.0})
    assert result.score < 1.0
    assert "irreversible_harm" in result.penalties
