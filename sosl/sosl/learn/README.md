# sosl.learn — the query learner

Given a `Teacher` for an unknown ω-regular language `L`, reconstruct its
canonical invariant `I(L)`. This is the intellectual core of the tool and the
deliverable behind `sos_learn`.

## Services

- **`learn(teacher, alphabet, stats=None) → Invariant`.** Drive membership
  and equivalence queries until the belief is certified equivalent to `L`.
  Every hypothesis posed is a well-formed `Invariant` — the canonical form of
  the learner's current belief language — and the certified belief is `I(L)`,
  byte-equal to the reference construction. `stats`, when given, receives the
  run counters (class count, membership/equivalence queries, counterexamples,
  legality escalations).
- **Determinism.** Given the teacher's answers, a run is reproducible
  bit-for-bit: every scan order is pinned (shortlex / id / first-query order)
  and counterexamples arrive minimized.
- **Query economy.** All queries thread through the evidence ledger: one
  teacher query per distinct infinite word per run, replays free.

## The one hard constraint

This module depends on **`sosl.contract` and `sosl.sos` only** — never
`teacher` internals, never spot or `aut2ltl`. Its only knowledge of `L` is
what the teacher answers. Any import that widens this is a layering bug: it
would let automaton structure leak into a "learned" result.

## Orientation map

    evidence    the run-wide lasso -> bit ledger (canonical omega-word keys)
    table       the observation table (rows, frontier, linear/omega columns)
    columns     the two column sorts and their lasso shapes
    partition   classes from bit-rows; keys (reps); step; fold
    chains      one discordance -> one witnessed class split
    saturate    stamp legality: the two-sided-congruence sweep + escalation
    pairs       pair legality: P saturated under conjugacy + escalation
    export      partition -> canonical Invariant (the belief)
    learner     bootstrap, probe sweep, the normal-form loop, alternation

## See also

`algorithm.md` — the learner algorithm proper: the state, the four-constraint
normal form, the chain, the bootstrap, the pinned orders, and the counting
conventions. The theory is the paper, `research_notes/sos_learning.md` §3–§5.
