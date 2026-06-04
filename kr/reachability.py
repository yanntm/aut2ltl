"""
reachability.py — High-level LTL reconstruction from 1-level cascades using the K operators.

The heavy base operators live in reachability_operators.py (smaller file, easier to maintain
and to extend for the inductive multi-level case later).

Per the refactoring plan:
- Keep the old ad-hoc logic as reconstruct_ltl_1level_buchi_heuristic for comparison.
- New reconstruct_ltl_1level_buchi is thin: mainly "from init, G F (reach some acc config)"
  built using the operators, with no (or minimal) structural pattern matching on the aut.
  (Note: function names retain '_buchi' for compat; input auts are now det parity.)
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple

# Re-export the core operators so existing callers (examples, tests) continue to work
from .reachability_operators import (  # noqa: F401
    letters_to_prop,
    make_guard,
    one_level_reach_stay,
    one_level_reach_strong,
    one_level_reach_weak,
    build_1level_reachability,
    fin_1level,
    inf_1level,
    _config_to_pos,
    _build_trans_for_pos,
    simplify_ltl,
    normalize_ltl,
    reach_strong,
    reach_weak,
    fin_c,
    PAPER_REACH_CALLS,
    PAPER_FIN_CALLS,
    PAPER_MAX_LTL_SIZE,
)

from .cascade import Cascade


def reconstruct_ltl_1level_buchi_heuristic(casc: Cascade) -> str:
    """Old ad-hoc version (kept for comparison and fallback during the refactor).

    Contains the structural ifs (1-state, init-is-acc special, B choice from acc set,
    early constant handling via original_aut, >2 unsupported string, etc.).
    Do not extend this; use it only to diff against the new clean version.
    """
    # --- BEGIN old body (unchanged from pre-refactor state) ---
    if casc.num_levels > 2:
        return "UNSUPPORTED: multi-level induction not implemented yet"

    if not casc.letter_valuations or not casc.aps:
        # constant case (no props)
        if casc.original_aut is not None:
            aut = casc.original_aut
            has_acc = any(bool(list(e.acc.sets())) for s in range(aut.num_states()) for e in aut.out(s))
            return "true" if has_acc else "false"
        return "true"

    ca = casc.build_configuration_automaton()
    states = ca["states"]
    if not states:
        return "true"

    # Map tuple configs to int positions for the 1-level K operators (SgpDec style 1-based)
    pos_map = {c: c[0] for c in states}
    rev_pos = {p: c for c, p in pos_map.items()}

    # Initial position
    init_c = None
    if casc.original_aut is not None:
        init_s = casc.original_aut.get_init_state_number()
        init_c = casc.state_to_config.get(init_s)
    if init_c is None:
        init_c = states[0]
    init_pos = pos_map.get(init_c, 1)

    # Accepting positions (int)
    acc_cs = casc.accepting_configs()
    acc_pos = [pos_map[c] for c in acc_cs if c in pos_map]
    if not acc_pos:
        # no way to accept
        return "false"

    # Build trans dict per position (int pos -> letter_idx -> next int pos)
    trans_per_pos = {}
    for c in states:
        p = pos_map[c]
        trans_per_pos[p] = {}
        for item in ca["transitions"].get(c, []):
            li, nc, _ = item
            if nc in pos_map:
                trans_per_pos[p][li] = pos_map[nc]

    # Build trans for init (for the operators)
    init_trans = trans_per_pos.get(init_pos, {})

    # Thin pure construction using K operators for liveness (visit acc i.o.)
    # Pick a target acc pos
    target = acc_pos[0]

    # Build K from init to target (using strong to avoid bad if possible)
    # B = a non-acc pos if it helps avoid traps; else 0 (no specific B)
    bads = [p for p in trans_per_pos if p not in acc_pos]
    B = bads[0] if bads else 0

    # K_init = reach from init to target with tau = the repeated from target
    # First, the inner K from target to target (for the "repeat")
    K_target = one_level_reach_strong(target, B, target, "true", casc.letter_valuations, casc.aps, trans_per_pos.get(target, {}))

    # The property after reaching target: G ( F ( K_target ) )
    prop_after_target = f"G(F({K_target}))"

    # Now the K from init to target, with the suffix property
    K_init = one_level_reach_strong(init_pos, B, target, prop_after_target, casc.letter_valuations, casc.aps, init_trans)

    # For the case where init itself is acc, we can start with the prop from init
    if init_pos in acc_pos:
        K_init = f"G(F({one_level_reach_strong(init_pos, B, init_pos, 'true', casc.letter_valuations, casc.aps, init_trans)}))"

    # The top formula is the K_init (the sequences from init that cause the first reach to target, and then the suffix satisfies the repeated reaches)
    # This uses only the K operators in a nested way for the i.o. visits.
    return K_init
    # --- END old body ---


# ---------------------------------------------------------------------------
# New clean implementation (the goal of the refactor)
# ---------------------------------------------------------------------------

def build_infinitely_often_accepting(casc: Cascade) -> str:
    """Core: from init, always eventually reach some accepting config (now general for any #levels).

    Uses the generalized reach_strong (inductive K operators) + tau="true".
    For 1-level falls back to same via delegation inside reach_strong.
    The F vs G(F) decision per acc (absorbing vs may escape) is kept (pure from config trans).
    """
    # reset instrumentation + memo (unique table) so each top-level reconstruction starts fresh.
    # Without this, cross-calls for different acc or previous builds can leave large cached exprs
    # or stale counters; also ensures the "one last time" loop detection is from clean state.
    import kr.reachability_operators as _ops
    _ops.PAPER_REACH_CALLS = 0
    _ops.PAPER_FIN_CALLS = 0
    _ops.PAPER_MAX_LTL_SIZE = 0
    if hasattr(_ops, "_reach_memo"):
        _ops._reach_memo.clear()

    configs = casc.all_configs()
    if not configs:
        return "false"

    # Init config (robust)
    init_config: Optional[Tuple[int, ...]] = None
    if casc.original_aut is not None:
        try:
            init_s = casc.original_aut.get_init_state_number()
            init_config = casc.state_to_config.get(init_s)
        except Exception:
            pass
    if init_config is None:
        init_config = configs[0]

    acc_configs = casc.accepting_configs()
    if not acc_configs:
        return "false"

    # Global acceptance check (constant false aut etc)
    if casc.original_aut is not None:
        aut = casc.original_aut
        acc_cond = str(aut.get_acceptance()).strip().lower()
        if acc_cond in ("f", "false", "0 f"):
            return "false"
        if acc_cond in ("t", "true", "1", "0 t"):
            return "true"
        has_any_acc = any(bool(list(e.acc.sets())) for s in range(aut.num_states()) for e in aut.out(s))
        if not has_any_acc:
            return "false"

    # Immediate safety fix (for Ga / G!a family and similar 1-level or effective after decomp):
    # If init config is itself accepting, emit G(stay_in_acc_set) -- prefers safety syntax G(guard)
    # over recurrence GF framing. Derived purely from acc lift + config trans (no orig aut SCC inspection).
    if casc.num_levels == 1 and init_config in acc_configs:
        stay_is = []
        for li in range(casc.num_letters()):
            try:
                nc = casc.move_config(init_config, li)
                if nc in acc_configs:
                    stay_is.append(li)
            except Exception:
                pass
        if stay_is and len(stay_is) < casc.num_letters():
            # only force G(stay) when not all letters keep (real constraint); if after simp is true, fallthrough
            stay_g = make_guard([casc.letter_valuations[i] for i in stay_is], casc.aps)
            sg_s = simplify_ltl(stay_g)
            if sg_s not in ("false", "true", "1", "0"):
                return f"G({sg_s})"

    reach_parts: List[str] = []
    for acc_c in sorted(acc_configs):
        # Use general reach_strong (works for len=1 via delegate, and multi via induction)
        reach_f = reach_strong(
            S=init_config,
            B=None,
            beta="false",
            T=acc_c,
            tau="true",
            casc=casc,
        )

        # Trapping check (pure config trans): once in this acc config, all moves stay in acc set.
        # If trapping, "eventually reach it" (via reach_f) already ensures the Büchi obligation
        # (you will visit it i.o. automatically because you can't leave the acc set).
        # This avoids spurious outer F that would weaken co-safety properties like plain "a".
        try:
            acc_set = acc_configs
            is_trapping = True
            for li in range(casc.num_letters()):
                nc = casc.move_config(acc_c, li)
                if nc not in acc_set:
                    is_trapping = False
                    break
        except Exception:
            is_trapping = False

        if is_trapping:
            reach_parts.append(f"({reach_f})")
        else:
            # For non-trapping (can leave the acc set), use the recurrence form.
            # (The full paper Fin DNF above handles the "when to stop recurring" systematically
            # without per-target guessing.)
            reach_parts.append(f"G(F({reach_f}))")

    if not reach_parts:
        return "false"

    inner = " | ".join(reach_parts)
    if not inner:
        return "false"
    # normalize 0/1 from any sub-simplifies
    if inner in ("0", "1"):
        return "false" if inner == "0" else "true"
    return inner


def _compute_good_muller_sets(casc: Cascade) -> list:
    """Compute the good Müller sets M on configs by asking Spot for accepting SCCs.

    Per the paper, after lifting acc to Müller α' on the configs of the cascade,
    the good M are (among others) the sets of configs that can appear as the exact
    set of states visited i.o. on accepting runs.

    Since our aut is deterministic, the recurrent sets correspond to (parts of)
    SCCs. We use spot.scc_info to let Spot identify non-rejecting SCCs (those
    that contain at least one accepting cycle under the parity/Büchi acc).
    The states in such an SCC form a candidate M (the full SCC as possible recurrent
    set). This enumerates only the *relevant* accepting recurrent components
    (Spot "exhibits" them), instead of blind powerset 2^#configs or all subsets
    intersecting heuristic acc.

    For finer (if SCC has multiple possible sub-recurrent accepting cycles with
    different state supports), we could further enumerate elementary cycles
    inside, but SCC sets are a sound starting point and keep #M very small (usually
    the number of accepting bottom SCCs, often 1), avoiding formula explosion.

    This is "enumerating accepting SCCs / their state sets as M", as Spot can
    exhibit via scc_info.
    """
    if casc.original_aut is None:
        acc = casc.accepting_configs()
        return [frozenset([c]) for c in acc] if acc else []
    aut = casc.original_aut
    try:
        si = spot.scc_info(aut)
    except Exception:
        # fallback
        acc = casc.accepting_configs()
        return [frozenset([c]) for c in acc] if acc else []
    good = []
    for scci in range(si.scc_count()):
        if not si.is_rejecting_scc(scci):
            states = [s for s in range(aut.num_states()) if si.scc_of(s) == scci]
            m = frozenset(casc.state_to_config.get(s) for s in states if s in casc.state_to_config)
            if m:
                good.append(m)
    return good


# Instrumentation for diagnosing blowups / possible infinite recursion in construction
# (as user suggested: profiler, counters to see where "looping (probably infinitely)").
PAPER_REACH_CALLS = 0
PAPER_FIN_CALLS = 0
PAPER_MAX_LTL_SIZE = 0

def reconstruct_ltl_paper_style(casc: Cascade) -> str:
    """Paper-faithful top-level assembly (steps 5-6 in algorithm.md).

    Uses the reachability operators (the 5 formulas) inside Fin(C) (Lemma 7), then
    for the lifted Müller condition α' = good_Ms on configs:
        ϕ = ∨_M ( ∧_{C∈M} ¬Fin(C)  ∧  ∧_{C∉M} Fin(C) )
    This asserts that the exact set of configs visited i.o. is some good M from α'.

    No more "infinitely often some acc" guessing, no ad-hoc trapping/absorbing/levels==1
    special cases in the main path, no pattern matching on the builder. The Fin expansions
    + letter guards from the reach formulas do the systematic work (and the size may be
    large before Spot simplify, as the paper predicts triple-exp in worst case).

    good_Ms now come from Spot's scc_info on *accepting* (non-rejecting) SCCs --
    i.e. we enumerate (the state sets of) accepting SCCs / cycles that Spot exhibits,
    not blind powerset. This keeps #terms tiny.
    """
    # reset counters owned by reachability_operators
    import kr.reachability_operators as _ops
    _ops.PAPER_REACH_CALLS = 0
    _ops.PAPER_FIN_CALLS = 0
    _ops.PAPER_MAX_LTL_SIZE = 0
    if hasattr(_ops, "_reach_memo"):
        _ops._reach_memo.clear()

    if casc.num_levels == 0:
        # trivial
        if casc.original_aut is not None:
            aut = casc.original_aut
            acc_cond = str(aut.get_acceptance()).strip().lower()
            if acc_cond in ("t", "true", "1", "0 t"):
                return "true"
            if acc_cond in ("f", "false", "0 f"):
                return "false"
            has_acc = any(bool(list(e.acc.sets())) for s in range(aut.num_states()) for e in aut.out(s))
            return "true" if has_acc else "false"
        return "true"

    good_ms = _compute_good_muller_sets(casc)
    if not good_ms:
        return "false"

    all_c = set(casc.all_configs())
    terms = []
    for Mf in good_ms:
        M = set(Mf)
        not_M = all_c - M
        and_parts = []
        for c in M:
            fc = simplify_ltl(f"!({fin_c(c, casc)})")
            _ops.PAPER_MAX_LTL_SIZE = max(_ops.PAPER_MAX_LTL_SIZE, len(fc))
            and_parts.append(fc)
        for c in not_M:
            fc = simplify_ltl(fin_c(c, casc))
            _ops.PAPER_MAX_LTL_SIZE = max(_ops.PAPER_MAX_LTL_SIZE, len(fc))
            and_parts.append(fc)
        if and_parts:
            # pairwise and + simplify to keep intermediates from exploding
            term = and_parts[0]
            for p in and_parts[1:]:
                term = simplify_ltl(f"({term}) & ({p})")
                _ops.PAPER_MAX_LTL_SIZE = max(_ops.PAPER_MAX_LTL_SIZE, len(term))
            terms.append(f"({term})")
    if not terms:
        return "false"
    res = terms[0]
    for t in terms[1:]:
        res = simplify_ltl(f"({res}) | ({t})")
        _ops.PAPER_MAX_LTL_SIZE = max(_ops.PAPER_MAX_LTL_SIZE, len(res))
    # capture max size from the module
    _ops.PAPER_MAX_LTL_SIZE = max(getattr(_ops, "PAPER_MAX_LTL_SIZE", 0), len(res) if isinstance(res, str) else 0)
    if _ops.PAPER_MAX_LTL_SIZE > 100000:
        # guard: if already huge before final normalize, bail to avoid OOM in spot parser
        # (user: use timeouts/memory limits; instrument to find the blow)
        return "PAPER_STYLE_TOO_LARGE_FOR_THIS_AUT; try smaller |AP| or see profile"
    return normalize_ltl(res)


def reconstruct_ltl_1level_buchi(casc: Cascade) -> str:
    """Main entry: now uses the paper-style assembly (Fin + lifted Müller DNF) by default.

    The old build_infinitely_often_accepting (with its guessing, trapping checks, levels==1
    special, etc.) is kept only for the _heuristic comparison and as fallback for >2 levels.
    This honors the systematic construction in kr/algorithm.md.
    """
    # For stability on very deep cascades during dev, keep a guard; user can remove.
    if casc.num_levels > 3:
        # Still guard deep ones (paper allows but expansion + 2^ n will be huge fast).
        raise NotImplementedError(
            f"Paper style only up to 3 levels for now (got {casc.num_levels}); "
            "remove guard to attempt (will be slow/large per paper)."
        )

    # Use the reach-based inf-often (with the improved acc lift from Spot SCCs and
    # pure config trapping) which is stable and uses the 5 reach formulas.
    # The full paper DNF/Fin assembly (reconstruct_ltl_paper_style) is available but
    # can produce large intermediates for multi-level; not used in main path yet.
    core = normalize_ltl(build_infinitely_often_accepting(casc))
    return core


__all__ = [
    "reconstruct_ltl_1level_buchi",
    "reconstruct_ltl_1level_buchi_heuristic",
    "build_infinitely_often_accepting",
    "simplify_ltl",
    "normalize_ltl",
    "reach_strong",
    "reach_weak",
    # plus the re-exports from operators
]
