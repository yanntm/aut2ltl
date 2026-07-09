"""Guard synthesis — a letter set as a minimized Boolean formula over `AP`.

A letter of the alphabet `Σ = 2^AP` is a valuation of the propositions, so a
letter *set* `S ⊆ Σ` is a Boolean function and the set-as-formula convention
writes it as any propositional formula whose models are exactly `S`. The
disjunction of the members' cubes is one such formula, but a needlessly large
one: it never contracts `{a&b, a&!b}` to `a`, and it only ever yields `⊤` when
`S` literally enumerates all `2^|AP|` letters.

`render` hands the cube union to the BDD + Minato ISOP pass of
`aut2ltl.ltl.builders` (`fuse_or`: `formula_to_bdd` then `bdd_to_formula`),
returning an irredundant sum of products as a hash-consed `spot.formula`. The
propositions are registered with the shared `bdd_dict` in the alphabet's
canonical order when a `Guards` is built, so the BDD variable order — hence
the shape of every ISOP read off it — is a function of the alphabet alone:
two presentations of one language render identically.
"""
from __future__ import annotations

from typing import Dict, FrozenSet, Iterable, List

import spot

from aut2ltl.ltl.builders import fuse_or, register_aps

from sosl.sos import Alphabet, Letter


class Guards:
    """Letter sets over one alphabet, rendered as minimized AP formulas.

    Memoized per set: one guard (a class's exit fan grouped by target, a
    λ-class window position) is rendered at every occurrence, and the ISOP is
    the only non-linear step of a transcription."""

    def __init__(self, alphabet: Alphabet, minimize: bool = True) -> None:
        self.alphabet = alphabet
        self.size: int = alphabet.size
        self.minimize = minimize
        self._memo: Dict[FrozenSet[Letter], "spot.formula"] = {}
        register_aps(list(alphabet.aps))

    def cube(self, a: Letter) -> "spot.formula":
        """The full cube of one letter — every proposition fixed. The atom-free
        alphabet has one letter, constraining nothing: the empty conjunction."""
        trues = set(self.alphabet.true_aps(a))
        atoms = [spot.formula.ap(p) if p in trues
                 else spot.formula.Not(spot.formula.ap(p))
                 for p in self.alphabet.aps]
        return spot.formula.And(atoms) if atoms else spot.formula.tt()

    def render(self, letters: Iterable[Letter]) -> "spot.formula":
        """A formula whose models are exactly `letters`: `⊥` for the empty set,
        else the Minato ISOP of the cube union — `⊤` whenever the set is all of
        `Σ`. Without `minimize`, the bare cube union: sound, unreduced, and
        never `⊤` on a proper subset of the propositions (the baseline E10's
        ledger prices the minimization against)."""
        key = frozenset(letters)
        out = self._memo.get(key)
        if out is None:
            if not key:
                out = spot.formula.ff()
            elif len(key) == self.size:
                out = spot.formula.tt()
            else:
                cubes: List["spot.formula"] = [self.cube(a) for a in sorted(key)]
                out = (fuse_or(cubes) if self.minimize
                       else spot.formula.Or(cubes))
            self._memo[key] = out
        return out
