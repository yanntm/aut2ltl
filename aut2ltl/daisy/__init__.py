"""
aut2ltl.daisy — the daisy combinator Translator.

`Daisy(child)` peels a single **daisy** — the initial state of a TGBA whose only
incoming edges are self-loops, a center with petal self-loops and stem exits — into
the closed-form `STAY∞ ∨ LEAVE`, delegating each stem target to `child`. It labels
the very-weak (1-weak) fragment exactly and declines (by construction) elsewhere: a
local, context-free production over one self-loop center. Defined entirely against
the Translator contract; imports only `spot`, the floor (`aut2ltl.language`,
`aut2ltl.result`), and its own `shape` helpers.

Public entry: `Daisy`. See algorithm.md for the construction.
"""

from .daisy import Daisy

__all__ = ["Daisy"]
