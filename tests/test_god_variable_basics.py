# tests/test_god_variable_basics.py
import numpy as np

# This assumes you expose a function named `god_variable` in godscore.py.
# If it's in a different module/name, tell me and I'll tweak the import.
from godscore import god_variable

# CLAIM: GLB-1 (Global coherence — outputs stay finite and increase monotonically with inputs)
def test_finiteness_and_monotonicity():
    m = 1.0
    gv1 = god_variable(1.0, m)   # smaller energy
    gv2 = god_variable(2.0, m)   # larger energy
    assert np.isfinite(gv1) and np.isfinite(gv2)
    assert gv2 > gv1, "God Variable should increase with energy (basic monotonicity)"
