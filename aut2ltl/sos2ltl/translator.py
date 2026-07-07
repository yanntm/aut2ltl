"""The sos2ltl `Translator` — certificate or formula, off the invariant.

Flow: bridge the `Language` to its canonical invariant `𝓘(L)`; scan for a
group (step 0) — on a group, extract the counting family and replay it
against the input automaton, absorbing `NOT_LTL` only on a certified
replay; on an aperiodic invariant, synthesize the formula (dg local-divisor
induction). Faithful-or-NOK: every cap and every inconsistency is a
decline, never a wrong formula and never an uncertified verdict.
"""
from __future__ import annotations

from typing import List, TYPE_CHECKING

import spot

from aut2ltl.result import LTLResult
from aut2ltl.verifier import member
from aut2ltl.witness import Witness

from .bridge import BridgeDecline, invariant_of_language
from .dg import DgDecline, synthesize
from .witness import Family, extract_family, toggles

if TYPE_CHECKING:
    from aut2ltl.language import Language
    from sosl.sos import Invariant, Lasso

TAG = "sos2ltl"
TAG_DG = "sos2ltl.dg"


def _cubes(inv: "Invariant") -> List[str]:
    """Letter cubes in mask order: the Spot rendering of each letter."""
    ab = inv.alphabet
    return ["&".join(p if p in ab.true_aps(a) else "!" + p for p in ab.aps)
            for a in ab.letters()]


def _floor_witness(inv: "Invariant", fam: Family) -> Witness:
    """The counting family as the floor `Witness` value (letter cubes)."""
    cubes = _cubes(inv)

    def words(word) -> List[str]:
        return [cubes[a] for a in word]

    if fam.omega_power:
        return Witness(p=fam.period, v=words(fam.v), factor=[],
                       u=words(fam.u), y=words(fam.y))
    return Witness(p=fam.period, v=words(fam.v), factor=[], u=words(fam.u),
                   x_prefix=words(fam.x_prefix), x_cycle=words(fam.x_loop))


def _lasso_str(inv: "Invariant", lasso: "Lasso") -> str:
    """A `sosl` lasso in Spot word syntax, for the verifier's `member`."""
    cubes = _cubes(inv)
    parts = [cubes[a] for a in lasso.stem]
    parts.append("cycle{" + "; ".join(cubes[a] for a in lasso.loop) + "}")
    return "; ".join(parts)


def sos2ltl(lang: "Language") -> LTLResult:
    """Translate via the syntactic ω-semigroup (`README.md` pipeline)."""
    try:
        inv = invariant_of_language(lang)
    except BridgeDecline as e:
        return LTLResult.decline(f"sos2ltl: {e}", TAG)

    fam = extract_family(inv)
    if fam is not None:
        aut = lang.det_generic_minimal()
        certified: bool = toggles(
            fam, lambda l: member(aut, _lasso_str(inv, l)))
        if certified:
            shape = "omega-power" if fam.omega_power else "linear"
            return LTLResult.not_definable(
                f"sos2ltl: group in the syntactic algebra; {shape} counting "
                f"family (p'={fam.period}) replayed against the input",
                TAG, witness=_floor_witness(inv, fam))
        return LTLResult.decline(
            "sos2ltl: counting family failed replay against the input "
            "(internal inconsistency)", TAG)

    try:
        ast, phi, _ = synthesize(inv)
    except DgDecline as e:
        return LTLResult.decline(f"sos2ltl: {e}", TAG, TAG_DG)
    return LTLResult.success(
        spot.formula(ast.to_spot(phi, _cubes(inv))), TAG, TAG_DG)
