"""
bls/operators/reach.py — Formula 1: reach (the main, strong operator).

reach(S, B, β, T, τ): reach configuration T (suffix ⊨ τ) at cascade level `level`
WITHOUT first hitting bad B (suffix ⊨ β). Base case (level == num_levels, the empty
config): (¬β) U τ. Otherwise split on whether the top-level state stays or changes:

    reach  =  solid ∨ dashed

Reference: paper/automata-to-ltl-construction.md §7 Formula 1 (intended semantics §6 (1)).
Memoised per build on casc.reach_memo; guarded by REACH_GUARD on DISTINCT subproblems.
"""

from __future__ import annotations
from typing import Optional, Tuple

import spot

from . import solid, dashed
from .support import TRACE_ON, _trace, REACH_GUARD
from aut2ltl.ltl.builders import _tt, _ff, _to_f, _Not, _Or, _U, _simp_f, _short_f

def reach(
    S: Tuple[int, ...],
    B: Optional[Tuple[int, ...]],
    beta: "str | spot.formula",
    T: Tuple[int, ...],
    tau: "str | spot.formula",
    casc: "Cascade",
    level: int = 0,
) -> "spot.formula":
    """Formula 1 (main strong): reach(S, B, β, T, τ) at the given cascade level.

    Recursion advances the level cursor while always passing full-length config tuples
    (so move_config and partition helpers always see correct context for higher coords).
    Base: when level == num_levels, plain (¬β) U τ .

    Native spot.formula end-to-end: accepts beta/tau as str or formula, RETURNS a
    spot.formula (hash-consed → DAG sharing across all subterms; stringify only at
    the very top via reconstruct, or with _str_f in tests/traces).

    Memoized per build on `casc.reach_memo` (key = the normalized
    (S, B, beta_f, T, tau_f, level)); `casc` is the CascadeHolder owning the memo.
    """
    beta_f = _ff() if beta is None else _to_f(beta)
    tau_f = _tt() if tau is None else _to_f(tau)

    # Dead-tail early-out: reach(S,B,β,T,τ≡false) ≡ false — Table 1 base case
    # is ¬β U false ≡ false and every inductive line conjoins τ at the claim
    # point. With per-node simplify folding tails (σ ∧ X(0) → 0), this deletes
    # the subproblem AND every wrapped descendant it would seed deeper down.
    if tau_f.is_ff():
        return _ff()

    # Per-build memo lookup (the "unique table of visited" that prevents the
    # exponential re-expansion of identical subproblems). One entry per distinct
    # (S, B, beta_f, T, tau_f, level); lives on the holder, fresh per build.
    key = (S, B, beta_f, T, tau_f, level)
    memo = casc.reach_memo
    hit = memo.get(key)
    if hit is not None:
        return hit

    # Guard counts MISSES only (distinct expansions; the body below runs once per key).
    casc.reach_calls += 1
    if casc.reach_calls > REACH_GUARD:
        raise RuntimeError(
            f"Too many DISTINCT reach subproblems (>{REACH_GUARD}) -- "
            f"genuine blowup (not memo fan-in; hits are not counted). "
            f"KR_REACH_GUARD to tune.")

    n = getattr(casc, "num_levels", 0)
    if level == n:
        negb = _tt() if beta_f.is_ff() else _Not(beta_f)
        res_f = _simp_f(_U(negb, tau_f))
        if TRACE_ON:
            _trace(f"base level reached (level={level}): returning {_short_f(res_f)}")
        memo[key] = res_f
        return res_f

    if TRACE_ON:
        _trace(f"reach level={level}/{n} S={S} T={T} beta={_short_f(beta_f)} tau={_short_f(tau_f)}")

    # 0-step only for trivial tau=true
    suffix_S = S[level:]
    suffix_T = T[level:]
    if suffix_S == suffix_T and tau_f.is_tt():
        _trace(f"  suffix from level {level} already matches target -> return tau early")
        memo[key] = _tt()
        return _tt()

    # Current level's value (for solid/dashed decision at this layer)
    s_val = S[level]
    t_val = T[level]
    b_val = B[level] if B is not None else None
    source_is_target = (suffix_S == suffix_T)
    source_is_bad = (B is not None and s_val == b_val)

    _trace(f"  at level {level}: s_val={s_val} t_val={t_val} source_is_target={source_is_target} source_is_bad={source_is_bad}")

    solid_f = solid.solid(S, B, beta_f, T, tau_f, casc, level)
    dashed_f = dashed.dashed(S, B, beta_f, T, tau_f, casc, level)
    if TRACE_ON:
        _trace(f"    solid={_short_f(solid_f)}")
        _trace(f"    dashed={_short_f(dashed_f)}")

    res_f = _simp_f(_Or(solid_f, dashed_f))
    if TRACE_ON:
        _trace(f"    reach res (pre-memo, post-simp)={_short_f(res_f, 150)}")
    memo[key] = res_f
    return res_f

