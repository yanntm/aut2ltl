"""
aut2ltl.simplify_ltl — the `Simplify` Translator decorator.

`Simplify(child, level)` forwards to `child` and simplifies an OK result's formula
(a NOK result passes through). `level='lo'` runs our DAG-size-aware rules only;
`'hi'` adds Spot's LTL simplifier after them. The rules themselves live in
`aut2ltl/ltl/simplify/`; this is the thin Translator seam over them — placed here,
not in `ltl/`, to respect the dependency graph (see README.md).

Public entry: `Simplify`.
"""

from .simplify import Simplify

__all__ = ["Simplify"]
