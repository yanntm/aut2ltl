# teacher — membership by simulation, equivalence by search

Dev-facing. The two answers a white-box teacher must produce correctly, and
cheaply enough for a learning campaign.

## Membership on a lasso

To decide `(u, v)` — the word `u.v^ω` — on a deterministic complete Emerson-Lei
automaton `D = (Σ, Q, ι, δ, α)`:

1. simulate `D` on the stem `u` from `ι`, reaching a state `q0`;
2. simulate the loop `v` repeatedly from `q0`, tracking the pair
   `(state, position-in-v)`. Determinism + finiteness force this pair to repeat;
   at the first repeat a cycle over the loop has closed;
3. collect the acceptance marks seen on that closed cycle (the marks that occur
   *infinitely often* on `u.v^ω` are exactly those on the cycle);
4. evaluate the Emerson-Lei condition `α` (a positive Boolean formula over
   `Inf(c)` / `Fin(c)`) against that mark set; the verdict is membership.

Cost `O(|u| + |Q|·|v|)`. No external tools, no timeouts — a membership query is
pure automaton walking.

## Equivalence

Three strategies, combinable via `--eq-mode`; default is `reps`, then
`bounded:8`, then `exact`. Whatever fires, the counterexample is **minimized**
(shortest stem, then shortest loop, then shortlex) before return — the whole
run's determinism depends on this.

- **`reps`** — audit lassos built from pairs of hypothesis keys and pairs of
  reference keys (`key(s), key(e)` for linked `(s, e)`). Fast, incomplete; a
  first pass that catches most early errors.
- **`bounded:B`** — exhaustive over lassos with `|u| ≤ B`, `|v| ≤ B`, enumerated
  through the product of `D` and the hypothesis step automaton so only
  *distinguishable* candidates are materialized; `B` doubles on demand. Complete
  in the limit.
- **`exact`** — decide via the product of `D` with the *transformation closure*
  of the hypothesis: loop words act on hypothesis classes as functions; close
  the function monoid under the letters; a mismatchable pair
  (stem-value, loop-transformation) yields a concrete counterexample. Complete;
  can be expensive; intended for the small campaign instances.

The teacher records which strategy certified each `eq`; a run certified only by
`bounded` is flagged in the stats (it is not a full proof of equivalence).

## Self-check (harness layer 1)

Two independent membership implementations — the simulator above and the
invariant read-off through the reference builder (`sosl.sos.build`) — are
compared on many seeded random lassos per corpus automaton. Any disagreement is
a build-stopping bug: it means either the simulator or the reference invariant
is wrong, and nothing downstream can be trusted until it is resolved.
