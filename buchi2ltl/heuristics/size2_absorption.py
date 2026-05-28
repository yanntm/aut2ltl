"""
Size-2 Non-Accepting SCC Absorption Heuristic (the "Fusion Test").

This module contains the programmatic implementation of the absorption
heuristic for size-2 non-accepting SCCs. The goal is to "unfold" small
cycles once so that the resulting automaton becomes pseudo-linear
(only size-1 SCCs) and can be fed to the normal backward-labeling rules.

Current status: Work in progress. The detection works, but producing a
language-equivalent unfolded automaton for arbitrary size-2 SCCs is
subtle and still being refined.
"""

import spot


def find_size2_nonaccepting_scc(aut):
    """Return (scc_idx, [s0, s1]) or (None, None)."""
    si = spot.scc_info(aut)
    for scc_idx in range(si.scc_count()):
        if si.is_accepting_scc(scc_idx):
            continue
        states = list(si.states_of(scc_idx))
        if len(states) == 2:
            return scc_idx, states
    return None, None


def get_true_bdd(aut):
    """Return a bdd representing constant true for this automaton's dict."""
    f = spot.formula("1")
    tmp = f.translate()
    for e in tmp.out(tmp.get_init_state_number()):
        return e.cond
    # Should never be reached
    raise RuntimeError("Could not synthesize a true bdd")


def try_absorb_size2_nonaccepting_scc(aut):
    """
    Programmatic "fusion test".

    Tries to unfold a size-2 non-accepting SCC once according to the
    concrete algorithm:
        1. Detect {A, B}
        2. Create fresh copies A' and B' for the first iteration
        3. Relabel self-loop on the "first return" copy to true
        4. Drop the return edge between the primed copies
        5. Redirect the return-condition from the primed copy to the
           accepting sink
        6. Build new automaton + check spot.are_equivalent

    Returns the massaged automaton on success, None otherwise.
    """
    scc_idx, states = find_size2_nonaccepting_scc(aut)
    if states is None:
        return None

    print("  → Size-2 non-accepting SCC detected, trying absorption (fusion test)...")

    # For now we still fall back to a more careful (but still experimental)
    # implementation in testing/fusion_heuristic.py while we iterate on
    # the exact edge-rewiring logic.
    try:
        from testing.fusion_heuristic import try_absorb_size2_nonaccepting_scc as _impl
        result = _impl(aut)
        if result is not None:
            print("  → Absorption succeeded (via testing implementation).")
        return result
    except Exception as e:
        print(f"  → Heuristic raised during development: {e}")
        return None
