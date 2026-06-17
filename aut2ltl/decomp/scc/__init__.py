"""
aut2ltl.decomp.scc — the accepting-SCC decomposition composite Translator.

`SccDecompose(leaf)` splits a language by its accepting SCCs (the exact,
determinism-free union `L(A) = ⋃ over accepting SCCs of L(A↾C)`), labels each part by
recursion on itself, and recombines with ∨ — delegating an atomic part (≤1 accepting
SCC) to `leaf`. Imports only spot, the contract floor, and the engine-agnostic
`own_simplify`.

Public entry: `SccDecompose`. See algorithm.md for the construction.
"""

from .sccdecompose import SccDecompose

__all__ = ["SccDecompose"]
