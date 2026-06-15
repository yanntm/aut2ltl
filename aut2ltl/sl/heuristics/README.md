# aut2ltl.sl.heuristics — verify-before-use SCC rescuers

A SEPARATE layer inside the `sl` engine that PROPOSES an LTL fragment for an SCC
the pure backward labeling cannot handle, then VALIDATES it by language
equivalence before `sl` may use it. A wrong guess is simply not adopted, so these
heuristics never weaken `sl`'s by-construction soundness — they only widen the set
of inputs on which it succeeds instead of declining.

## Modules

- **`size2_overapprox.py`** — the **f2** heuristic: a non-accepting SCC of exactly
  two states is "unfolded" once by relabeling a self-loop with `true` (full
  alphabet). This is a deliberate over-approximation, accepted ONLY when
  `spot.are_equivalent(original, transformed)` still holds; on success the
  automaton has only size-1 SCCs and feeds the core labeler.
  Entry: `try_size2_overapprox`.
- **`terminal_2scc.py`** — the **t2** heuristic for "nice" terminal accepting SCCs
  (generalized): detects the pattern (`find_nice_terminal_2sccs`), proposes a
  fragment, and validates it (`validate_terminal_2scc`) before adoption.
  Entry: `try_terminal_2scc_with_validation`.

Both honor `RECONSTRUCT_TRACE=1` (or the per-heuristic `F2_TRACE` / `T2_TRACE`).

## Layering

Leaf of the `sl` engine: imported by `sl/reconstruction.py`, imports `spot` /
`buddy` (t2 optionally `sympy` for constant-atom detection). Each entry point is
self-contained — propose-then-validate, no shared mutable state.
