"""The sos2ltl `Translator` — certificate or formula, off the invariant.

Flow: bridge the `Language` to its canonical invariant `𝓘(L)`; scan for a
group (step 0) — on a group, extract the counting family and replay it
against the input automaton, absorbing `NOT_LTL` only on a certified
replay. On an aperiodic invariant, the transcription engine runs first and its
formula ships directly; the dg local-divisor induction is the fallback
where the flat-brick stratum's preconditions fail. Every cap on the
certificate or dg side is a decline, never a wrong verdict.
"""
from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING

import spot

from aut2ltl.result import LTLResult
from aut2ltl.verifier import member
from aut2ltl.witness import Witness

from sosl.sos.classify.aperiodic import first_group

from .bridge import BridgeDecline, invariant_of_language
from .census import CENSUS, CENSUS_FH, census_line
from .dg import DgDecline, synthesize
from .engine import transcribe
from .witness import Family, extract_family, toggles

if TYPE_CHECKING:
    from aut2ltl.language import Language
    from sosl.sos import Invariant, Lasso
    from .dg.formulas import Ast

TAG = "sos2ltl"
TAG_ENGINE = "sos2ltl.engine"
TAG_DG = "sos2ltl.dg"


def _cubes(inv: "Invariant") -> List[str]:
    """Letter cubes in mask order: the Spot rendering of each letter. An
    atom-free alphabet has a single letter constraining nothing — the `true`
    cube, rendered `1` (the empty conjunction is not valid Spot syntax)."""
    ab = inv.alphabet
    return ["&".join(p if p in ab.true_aps(a) else "!" + p for p in ab.aps) or "1"
            for a in ab.letters()]


def _to_formula(ast: "Ast", root: int, letters: List[str]) -> "spot.formula":
    """A `spot.formula` built bottom-up over the dg arena — one Spot node per
    arena node (Spot hash-conses internally), so shared subterms stay shared.
    Never the O(unfolded-tree) flat string that `Ast.to_spot` renders."""
    atoms = [spot.formula(s) for s in letters]
    memo: dict = {}

    def go(i: int) -> "spot.formula":
        f = memo.get(i)
        if f is None:
            n = ast.node(i)
            if n[0] == "top":
                f = spot.formula.tt()
            elif n[0] == "atom":
                f = atoms[n[1]]
            elif n[0] == "not":
                f = spot.formula.Not(go(n[1]))
            elif n[0] == "or":
                f = spot.formula.Or([go(n[1]), go(n[2])])
            else:
                f = spot.formula.X(spot.formula.U(go(n[1]), go(n[2])))
            memo[i] = f
        return f

    return go(root)


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
    if CENSUS:
        print(census_line(inv, fam is None), file=CENSUS_FH)
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

    phi: Optional["spot.formula"] = transcribe(inv)
    if phi is not None:
        return LTLResult.success(phi, TAG, TAG_ENGINE)

    try:
        ast, phi, _ = synthesize(inv)
    except DgDecline as e:
        return LTLResult.decline(f"sos2ltl: {e}", TAG, TAG_DG)
    return LTLResult.success(
        _to_formula(ast, phi, _cubes(inv)), TAG, TAG_DG)


def sos2ltl_dg(lang: "Language") -> LTLResult:
    """The E4(b) DG baseline: bridge to `𝓘(L)`, then the dg local-divisor
    induction with no walk+window engine and no simplifier — the naive
    transcription whose flat form is the paper's §3 explosion. Declines on a
    group (the certificate side is not part of this baseline) and on a dg
    cap; never the engine's compact bricks."""
    try:
        inv = invariant_of_language(lang)
    except BridgeDecline as e:
        return LTLResult.decline(f"sos2ltl_dg: {e}", TAG_DG)
    if first_group(inv) is not None:
        return LTLResult.decline("sos2ltl_dg: group-bearing (baseline is "
                                 "aperiodic-only)", TAG_DG)
    try:
        ast, phi, _ = synthesize(inv)
    except DgDecline as e:
        return LTLResult.decline(f"sos2ltl_dg: {e}", TAG_DG)
    return LTLResult.success(
        _to_formula(ast, phi, _cubes(inv)), TAG_DG, TAG_DG)
