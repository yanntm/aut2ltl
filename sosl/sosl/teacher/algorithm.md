# teacher — membership by simulation, equivalence by scan

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

The hypothesis is a well-formed `Invariant`, so its side of any comparison is
its own algebraic lasso read-off — total and normative. Two strategies,
selected by `eq_mode`; whatever fires, the returned counterexample is
**minimal** (shortest stem, then shortest loop, then shortlex) — the whole
run's determinism depends on this.

- **`exact`** — decide against the language's reference invariant `R` in the
  SoS calculus: `align` the two stamps into the letter-generated node set
  (the pairs `(fold_H(w), fold_R(w))`, at most `n_H·n_R` nodes, each keyed by
  its shortlex-least word), then scan the cells `(stem node, loop node)` in
  the counterexample discipline, reading one algebraic verdict per side per
  cell — each side's `Val` on its own component, which by the factoring
  theorem speaks for every lasso of the cell. The first disagreeing cell's
  canonical lasso is the globally minimal counterexample (Proposition W of
  `sosl.sos.calculus.decide`). Complete, polynomial, and **zero membership
  queries**: the decision reads the two algebras alone. `R` is built once
  from `D` (or supplied precomputed); after that the automaton leaves the
  equivalence loop. A language whose algebra blew the construction's cap has
  no `R` and no exact decision — the query raises, or answers bounded under
  `cap_escape`.
- **`bounded:B`** — exhaustive over lassos with `|u| ≤ B`, `1 ≤ |v| ≤ B`,
  enumerated in the counterexample order (so the first mismatch found is
  already minimal), each decided by `Invariant.member` against `D`'s
  simulation. Complete only in the limit; a work cap stops a hopeless sweep
  and reports the answer as inconclusive rather than certifying. This is the
  honest strategy for a black-box or referenceless teacher, and the
  certifying-strategy tag on `Equivalent` is what flags such runs.
