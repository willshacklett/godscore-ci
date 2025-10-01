import math
import godscore

# If your function has a different name or signature,
# change `godscore.god_variable(x)` accordingly.
def _call(x):
    return godscore.god_variable(x)

def test_bounds_on_typical_inputs():
    inputs = [0, 1, -1, 10, -10, 0.123, 12345, -9999]
    for x in inputs:
        y = _call(x)
        # Must be a finite real number
        assert isinstance(y, (int, float))
        assert math.isfinite(y)
        # Must be normalized in [0, 1]
        assert 0.0 <= y <= 1.0
# CLAIM: GLB-1 (Global coherence — outputs stay within normalized bounds)
