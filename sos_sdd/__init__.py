"""sos_sdd — the symbolic SoS engine: a libDDD C++ core behind a
coarse-grained Python API. The IO contract is README.md in this
directory; the pure-Python layer (digests, errors, contract, façade)
imports without the built extension."""

from .contract import Lasso, SoS, Word
from .engine import Engine, align
from .errors import DiagramBudget, Finding, StopTheLine, TimeBudget
from .model import Automaton, Input, Product, Transition

__all__ = [
    "Automaton",
    "DiagramBudget",
    "Engine",
    "Finding",
    "Input",
    "Lasso",
    "Product",
    "SoS",
    "StopTheLine",
    "TimeBudget",
    "Transition",
    "Word",
    "align",
]
