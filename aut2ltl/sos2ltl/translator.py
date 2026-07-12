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

from typing import List, Optional, Tuple, TYPE_CHECKING

import spot

from aut2ltl.ltl.builders import _FLATTEN_TREE_LIMIT, _Not, _Or, _simp_f
from aut2ltl.ltl.metrics import tree_node_count
from aut2ltl.result import LTLResult
from aut2ltl.verifier import member
from aut2ltl.witness import Witness

from sosl.sos.classify.aperiodic import first_group

from .bridge import BridgeDecline, invariant_of_language
from .census import CENSUS, CENSUS_FH, census_line
from .dg import DgDecline, synthesize
from .engine import transcribe
from .pairsplit import SplitPlan, split_plan
from .witness import Family, extract_family, toggles

if TYPE_CHECKING:
    from aut2ltl.language import Language
    from sosl.sos import Invariant, Lasso
    from .dg.formulas import Ast
    from .engine import LayerFallback

TAG = "sos2ltl"
TAG_CASC = "sos2ltl_casc"
TAG_PAIRS = "sos2ltl_pairs"
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


def _piece_formula(piece: "Invariant") -> "Optional[Tuple[spot.formula, str]]":
    """One pairsplit piece: engine first, dg as the floor; (formula, tag of
    the technique that produced it), or None when both decline. Pieces of an
    aperiodic invariant are aperiodic (reduce only merges classes —
    pairsplit/algorithm.md "Verdicts inherit"), so no group scan re-runs
    here; the cascade delegate is not threaded to pieces (v1 — the per-piece
    acceptor presentation is the open interface point)."""
    phi = transcribe(piece, fallback=None)
    if phi is not None:
        return phi, TAG_ENGINE
    try:
        ast, root, _ = synthesize(piece)
    except DgDecline:
        return None
    return _to_formula(ast, root, _cubes(piece)), TAG_DG


def _split_translate(plan: "SplitPlan", tag: str) -> LTLResult:
    """Translate a `SplitPlan`: every piece must label (a decline poisons the
    split — algorithm.md "Verdicts inherit"); the labels recombine as ⋁, with
    an outer ¬ iff the complement side was taken."""
    fs: List["spot.formula"] = []
    tags = {tag, TAG_PAIRS}
    for piece in plan.pieces:
        got = _piece_formula(piece)
        if got is None:
            return LTLResult.decline(
                f"{tag}: pairsplit piece declined by engine and dg "
                f"(|C|={piece.n})", tag, TAG_PAIRS)
        fs.append(got[0])
        tags.add(got[1])
    f = _simp_f(_Or(*fs))
    if plan.negate:
        f = _simp_f(_Not(f))
    # The oracle gate (algorithm.md "Cost"): a label the conformance oracle
    # cannot flatten validates nothing — decline it so the assembly falls
    # through to the cascade path instead of shipping unverifiable size.
    if 0 <= _FLATTEN_TREE_LIMIT < tree_node_count(f, limit=_FLATTEN_TREE_LIMIT + 1):
        return LTLResult.decline(
            f"{tag}: split label above the flatten gate "
            f"({_FLATTEN_TREE_LIMIT} tree nodes)", tag, TAG_PAIRS)
    return LTLResult.success(f, *sorted(tags))


def _sos2ltl(lang: "Language", tag: str,
             fallback: Optional["LayerFallback"],
             pairsplit: bool = False) -> LTLResult:
    """The shared assembly: bridge, step-0 witness scan, optionally the SoS
    pair decomposition (pairsplit/algorithm.md; aperiodic invariants only —
    the group scan has already spoken for L itself), engine (with an optional
    per-layer delegate), dg where the engine declines."""
    try:
        inv = invariant_of_language(lang)
    except BridgeDecline as e:
        return LTLResult.decline(f"{tag}: {e}", tag)

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
                f"{tag}: group in the syntactic algebra; {shape} counting "
                f"family (p'={fam.period}) replayed against the input",
                tag, witness=_floor_witness(inv, fam))
        return LTLResult.decline(
            f"{tag}: counting family failed replay against the input "
            "(internal inconsistency)", tag)

    if pairsplit:
        # The inflation gate (pairsplit/algorithm.md "Cost"): the pure engine
        # (no delegate) is tried whole first — where it succeeds the split
        # could only inflate the label. The split is an ENABLER: it runs only
        # where the whole-language engine declines; a poisoned split falls
        # through to the full cascade assembly below.
        phi0: Optional["spot.formula"] = transcribe(inv, fallback=None)
        if phi0 is not None:
            return LTLResult.success(phi0, tag, TAG_ENGINE)
        plan = split_plan(inv)
        if plan is not None:
            r = _split_translate(plan, tag)
            if r.ok:
                return r

    phi: Optional["spot.formula"] = transcribe(inv, fallback=fallback)
    if phi is not None:
        return LTLResult.success(phi, tag, TAG_ENGINE)

    try:
        ast, phi, _ = synthesize(inv)
    except DgDecline as e:
        return LTLResult.decline(f"{tag}: {e}", tag, TAG_DG)
    return LTLResult.success(
        _to_formula(ast, phi, _cubes(inv)), tag, TAG_DG)


def sos2ltl(lang: "Language") -> LTLResult:
    """Translate via the syntactic ω-semigroup (`README.md` pipeline)."""
    return _sos2ltl(lang, TAG, None)


def sos2ltl_casc(lang: "Language") -> LTLResult:
    """`sos2ltl` with the decomposition fallback below the engine (paper §6,
    `cascade/`): a no-width or window-undetermined layer is delegated to the
    per-layer KR cascade instead of failing the whole engine; dg remains the
    floor when the delegate itself declines."""
    from .cascade.delegate import CascadeFallback
    return _sos2ltl(lang, TAG_CASC,
                    CascadeFallback(lambda: lang.det_parity_sbacc()))


def sos2ltl_pairs(lang: "Language") -> LTLResult:
    """`sos2ltl_casc` under the SoS pair decomposition (paper-side doc:
    `pairsplit/algorithm.md`): an aperiodic invariant whose accepting pair
    set — or its free complement — splits into ≥ 2 saturation atoms is
    translated piecewise over the same table (engine + dg per piece) and
    recombined `⋁` (outer `¬` iff complemented); otherwise the full cascade
    assembly runs unchanged."""
    from .cascade.delegate import CascadeFallback
    return _sos2ltl(lang, TAG_PAIRS,
                    CascadeFallback(lambda: lang.det_parity_sbacc()),
                    pairsplit=True)


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
