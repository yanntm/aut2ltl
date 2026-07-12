"""
bls/operators/support.py — non-recursive support for the reachability operators.

The five reachability formulas (reach / wreach / solid / wsolid / dashed) are mutually
recursive and live one per file; everything they SHARE that is not itself recursive
lives here:
  - the native spot.formula builders, re-exported under their short names;
  - tracing (KR_TRACE) and the runaway guard (KR_REACH_GUARD);
  - the per-build memo decorator for the solid/dashed helpers;
  - the combined-letter enumeration (Enter/Stay/Leave primitives) and letter fusion.

Depends only on `aut2ltl.ltl.builders`; imports none of the operator modules, so it is
the DAG floor beneath the recursive layer.
"""

from __future__ import annotations
from typing import List, Tuple
import functools
import os

# support uses only these for its own helpers (the memo decorator, instantiation and
# letter fusion); the operator modules import the builders they need directly from
# aut2ltl.ltl.builders.
from aut2ltl.ltl.builders import _ff, _tt, _to_f, _ap, _letters_to_f, _fuse_or, _subst_f

# Tracing (enable with KR_TRACE=1): verbose level-by-level construction traces.
TRACE_ON = os.getenv("KR_TRACE", "0").lower() in ("1", "true", "yes", "on")

# Runaway guard on DISTINCT reach subproblems (holder.reach_calls = memo misses,
# not raw calls). Legitimate big builds stay finite; an infinite same-level
# recursion grows without bound and still trips it. Wall-clock budgets belong to
# the callers.
REACH_GUARD = int(os.getenv("KR_REACH_GUARD", "5000000"))

# --- context placeholders + skeleton templates ------------------------------
# The β/τ continuation parameters are NOT part of any memo key: the recursion
# manufactures a fresh context at every step (solid⁺ pushes σ ∧ Xτ / ρ ∧ Xβ,
# dashed swaps them into wsolid, …), so keying on them makes every key
# path-unique and multiplies machine positions by contexts — exponential in
# cascade height. Instead each operator is built ONCE per machine skeleton
# (S, B, T, level) as a template whose β/τ positions hold the two reserved
# placeholder APs below; concrete (or manufactured) contexts are plugged in by
# a per-node-memoized substitution pass (`_instantiate`). Total cost:
# O(#skeletons × template DAG) instead of positions × contexts.
PH_BETA: "spot.formula" = _ap("_krbeta_")
PH_TAU: "spot.formula" = _ap("_krtau_")


def _instantiate(
    tmpl: "spot.formula", beta_f: "spot.formula", tau_f: "spot.formula", casc: "Cascade"
) -> "spot.formula":
    """Plug concrete β/τ into a skeleton template: simultaneous substitution of
    the two placeholder APs, per-node memoized on the holder's `inst_memo`
    (one node-memo per distinct (β, τ) plug pair, shared across templates).
    The identity plug returns the template itself — this is what nested calls
    hit while a template is being built. Plugs may themselves contain the
    placeholders (manufactured contexts like σ ∧ Xτ̂, or dashed's swapped
    wsolid): substitution is single-pass, so they denote the CALLER's
    parameters, never re-substituted."""
    if beta_f == PH_BETA and tau_f == PH_TAU:
        return tmpl
    pair = (beta_f, tau_f)
    memo = casc.inst_memo.get(pair)
    if memo is None:
        memo = {}
        casc.inst_memo[pair] = memo
    return _subst_f(tmpl, {PH_BETA: beta_f, PH_TAU: tau_f}, memo)


# --- per-build memo decorator + tracing -------------------------------------
def _memo_reach_helper(tag: str):
    """Memoize a helper on the CascadeHolder's `helper_memo` (per build; `casc` is the
    holder), keyed by the machine SKELETON `(tag, S, B, T, level)` — β/τ deliberately
    excluded (see the placeholder note above). On a miss the body runs once with the
    placeholder APs in the β/τ positions, producing the skeleton's template; every
    call then returns `_instantiate(template, β, τ)`. `beta`/`tau` are normalized to
    hash-consed spot.formula (str spellings accepted). The helpers fan in heavily
    (the same skeleton is reached along many call paths under many contexts), so this
    memo is what keeps the mutually-recursive expansion a DAG build rather than a
    tree blow-up. One template per distinct skeleton; fresh per holder."""
    def deco(fn):
        @functools.wraps(fn)
        def wrapper(S, B, beta, T, tau, casc, level=0):
            beta_f = _ff() if beta is None else _to_f(beta)
            tau_f = _tt() if tau is None else _to_f(tau)
            key = (tag, S, B, T, level)
            memo = casc.helper_memo
            tmpl = memo.get(key)
            if tmpl is None:
                tmpl = fn(S, B, PH_BETA, T, PH_TAU, casc, level)
                memo[key] = tmpl
            return _instantiate(tmpl, beta_f, tau_f, casc)
        return wrapper
    return deco

def _trace(msg: str) -> None:
    if TRACE_ON:
        print("[KR] " + msg)

# --- combined-letter enumeration (Enter/Stay/Leave) + letter fusion ---------
def _combined_letters_at_level(casc: "Cascade", level: int) -> List[Tuple[int, Tuple[int, ...], Tuple[int, ...]]]:
    """Observable combined letters at layer `level`: list of (li, pre, arrived)
    over every h-image config `pre` and letter li. The paper's combined letter
    ⟨σ, L⟩ for this layer corresponds to (li, pre[level+1:]); pre[level] is the
    layer state it is observed from. Enumerating h-image configs is the
    observable approximation of the full product cascade (exact when h covers
    the reachable configs, which decompose_aut's state_to_config provides).
    """
    out: List[Tuple[int, Tuple[int, ...], Tuple[int, ...]]] = []
    for pre in casc.all_configs():
        if len(pre) <= level:
            continue
        for li in range(casc.num_letters()):
            try:
                arr = casc.move_config(pre, li)
            except Exception:
                continue
            if li >= len(casc.letter_valuations):
                continue
            out.append((li, pre, arr))
    return out


def _dedupe(
    triples: List[Tuple[int, Tuple[int, ...], Tuple[int, ...]]],
    level: int,
) -> List[Tuple[int, Tuple[int, ...], Tuple[int, ...]]]:
    """Collapse triples by the paper's combined-letter identity `(letter, lower-config
    suffix)` — the observable enumeration can present the same combined letter from
    several configs; the first occurrence is the structural representative."""
    seen: dict = {}
    for li, pre, arr in triples:
        key = (li, pre[level + 1:])
        if key not in seen:
            seen[key] = (li, pre, arr)
    return list(seen.values())


# Letter fusion (dag_folding.md counter-measure B): at every enumeration
# site the summand reads the letter ONLY through its guard, so letters with
# an equal group key are fused into one summand whose guard is the
# Minato-minimized OR. KR_FUSE_LETTERS=0 restores the per-letter literal
# paper shape (grounding comparisons).
_FUSE_LETTERS = os.getenv("KR_FUSE_LETTERS", "1").lower() not in ("0", "false", "no", "off")


def _fuse_letters(
    triples: List[Tuple[int, Tuple[int, ...], Tuple[int, ...]]],
    casc: "Cascade",
    level: int,
    with_arr: bool = False,
) -> List[Tuple["spot.formula", Tuple[int, ...], Tuple[int, ...]]]:
    """Group (li, pre, arr) triples whose summand is identical up to the
    guard. Key = the _dedupe key minus li (pre suffix; + arr when the
    summand reads the arrival — enter_t/enter_b). Returns
    [(fused_guard, pre, arr)] with the first triple of each group as the
    structural representative (same convention as _dedupe). Soundness:
    dag_folding.md "Letter fusion"."""
    groups: dict = {}
    for li, pre, arr in triples:
        g_f = _letters_to_f(casc.letter_valuations[li], casc.aps)
        if g_f.is_ff():
            continue
        key: tuple = (pre[level + 1:], arr) if with_arr else pre[level + 1:]
        if not _FUSE_LETTERS:
            key = (li, key)
        ent = groups.get(key)
        if ent is None:
            groups[key] = ([g_f], pre, arr)
        else:
            ent[0].append(g_f)
    return [(_fuse_or(gs), pre, arr) for (gs, pre, arr) in groups.values()]
