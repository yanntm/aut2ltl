"""
aut2ltl.bls.gate.aperiodic — the LTL-definability screen for a `Language`.

`label_ltl_definable` decides `(definable, conclusive)` from the aperiodicity of
the deterministic transition monoid and caches it on the Language. See
aperiodic.py.
"""

from .aperiodic import label_ltl_definable

__all__ = ["label_ltl_definable"]
