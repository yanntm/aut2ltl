"""
kr — Experimental Krohn-Rhodes (holonomy cascade) support for Buchi → LTL.

Public API (first milestone):
    from kr import Cascade, decompose_gens, decompose_aut, generate_gap_script
    from kr.extract import extract_generators
    from kr.cascade import LevelInfo

See kr/README.md and the top-level project README for context and status.
"""

from .cascade import Cascade, LevelInfo, make_trivial_cascade
from .gap_bridge import (
    decompose_gens,
    decompose_aut,
    generate_gap_script,
    parse_cascade_output,
    run_gap_script,
    check_gap_available,
)
from .extract import extract_generators, ExtractionError, is_deterministic

__all__ = [
    "Cascade",
    "LevelInfo",
    "make_trivial_cascade",
    "decompose_gens",
    "decompose_aut",
    "generate_gap_script",
    "parse_cascade_output",
    "run_gap_script",
    "check_gap_available",
    "extract_generators",
    "ExtractionError",
    "is_deterministic",
]
