"""
aut2ltl.bls.operators — the paper's inductive reachability operators.

The five reachability formulas live one per file — `reach` / `wreach` / `solid` /
`wsolid` / `dashed` (plus the `solid_plus` / `wsolid_plus` cores and `Fin(C)` in
`fin.py`); their shared, non-recursive machinery is in `support.py`. This package is
the **facade**: it re-exports the whole surface so callers import from here and need
not know the file split. See algorithm.md.
"""

from aut2ltl.ltl.builders import letters_to_prop, make_guard, simplify_ltl, normalize_ltl
from .support import TRACE_ON
from .reach import reach
from .wreach import wreach
from .solid import solid, solid_plus
from .wsolid import wsolid, wsolid_plus
from .dashed import dashed
from .fin import fin_c

__all__ = [
    "letters_to_prop",
    "make_guard",
    "simplify_ltl",
    "normalize_ltl",
    "reach",
    "wreach",
    "solid",
    "solid_plus",
    "wsolid",
    "wsolid_plus",
    "dashed",
    "fin_c",
    "TRACE_ON",
]
