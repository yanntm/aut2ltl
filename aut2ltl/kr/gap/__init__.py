"""
kr.gap — Focused sub-services for the GAP/SgpDec bridge.

Contains:
- bridge : GAP script generation, subprocess execution, and the high-level
           decompose_aut / decompose_gens orchestration.
- parse  : parsing of structured GAP output into Cascade objects.

This subpackage keeps the individual files small and each module
focused on one service (generation, execution, parsing).
"""

from .bridge import (
    decompose_gens,
    decompose_aut,
    generate_gap_script,
    run_gap_script,
    check_gap_available,
)
from .parse import parse_cascade_output

__all__ = [
    "decompose_gens",
    "decompose_aut",
    "generate_gap_script",
    "run_gap_script",
    "check_gap_available",
    "parse_cascade_output",
]
