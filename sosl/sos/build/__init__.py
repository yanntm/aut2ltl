"""build — constructors for the sos invariant from a known automaton or formula.

Re-exports; see README.md. Spot-backed adapter over the in-repo definability
pipeline, normalized to the shared canonical form.
"""
from .builder import ReferenceError, reference_of_hoa, reference_of_ltl
from .importer import canonical, import_hoa
from .residuals import residuals_of_hoa

__all__ = [
    "reference_of_hoa",
    "reference_of_ltl",
    "ReferenceError",
    "residuals_of_hoa",
    "canonical",
    "import_hoa",
]
