"""sosl.reference — the reference invariant from a known automaton.

Re-exports; see README.md. Spot-backed adapter over the in-repo definability
pipeline; used by the teacher and validator, never by the learner.
"""
from sosl.reference.builder import ReferenceError, reference_of_hoa, reference_of_ltl
from sosl.reference.residuals import residuals_of_hoa

__all__ = ["reference_of_hoa", "reference_of_ltl", "ReferenceError", "residuals_of_hoa"]
