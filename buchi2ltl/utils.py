"""
Small utilities for the BuchiToLTL prototype.
"""

import spot


def simplify_ltl(formula_str: str) -> str:
    """
    Run Spot's LTL simplification on a formula string (equivalent to ltlfilt --simplify).
    Returns the simplified formula as a string.
    """
    if not formula_str or formula_str.startswith("UNSUPPORTED"):
        return formula_str

    try:
        f = spot.formula(formula_str)
        simplified = f.simplify()
        return str(simplified)
    except Exception as e:
        return f"{formula_str}   [simplification failed: {e}]"
