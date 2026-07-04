"""
aut2ltl.bls.gate — gate a translator on the LTL-definability screen.

`cascade_gate` (in gate.py) admits its wrapped translator only behind a
proved-aperiodic transition monoid and declines PROBABLY_NOT_LTL otherwise. The
screen it runs is the `aperiodic` subpackage.
"""

from .gate import cascade_gate

__all__ = ["cascade_gate"]
