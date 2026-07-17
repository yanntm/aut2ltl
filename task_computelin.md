# task_computelin — compute `~lin` on our own table, drop Spot from the construction

## Why

The `~lin` base (residual equality of states of `D`) is currently delegated
to `spot.language_map` inside the construction pipeline. It is recoverable
from data the pipeline already computes, at no added asymptotic cost: after
closure we hold the loop-verdict matrix `A : Q × EM₊ → bool` (the `prof`
array), and by lasso density `L(p) = L(q)` iff `A(st_s(p), c) = A(st_s(q), c)`
for all `s ∈ EM¹`, `c ∈ EM₊`. The construction becomes self-contained.

## The algorithm (state-level Moore refinement)

A twin of `refine`, on the states of `D` instead of the elements:

1. **Seed.** `p ≡₀ q` iff the profile *columns* agree: `A(p, c) = A(q, c)`
   for every word element `c` — a transpose-read of `prof`.
2. **Refine.** Split a block whenever a letter separates two members:
   `δ(p, x)` and `δ(q, x)` in distinct blocks of the current partition.
   Iterate to fixpoint; at most `|Q|` splits.

Correctness: the seed handles empty stems (pure loops from `p`); refinement
closes under letter stems, hence — `EM¹` letter-generated — under all stems.
The fixpoint is exactly language equivalence of states. Classical
right-congruence computation seeded by loop verdicts; no rotation involved.

## The edit

In `sosl/sosl/sos/core/`: replace `residual_classes` (congruence.py) by the
refinement above; reorder `pipeline` (quotient.py) so `prof` is computed
before the state partition. Keep `algorithm.md` in sync. Fingerprint tests
must pass unchanged.

## Validation

Rebuild the invariant of each of the 6222 `flat_canon` models from its `det/`
automaton and compare **byte equality** against the stored `.sos`, model by
model: the replacement must not functionally affect the tool. Expected
6222/6222 identical; any mismatch is a stop-and-report finding.
