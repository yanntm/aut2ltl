# sosl.learn — the query learner

Given a `Teacher` for an unknown ω-regular language `L`, reconstruct its
canonical invariant `I(L)`. This is the intellectual core of the tool and the
deliverable behind `sos_learn`.

## Services

- **`learn(teacher) → Invariant`.** Drive membership and equivalence queries
  until the hypothesis is certified equivalent to `L`, then export the
  canonical invariant. Emits, alongside the invariant:
  - **run statistics** (query counts by phase, splits, table dimensions, …);
  - a replayable **audit transcript** — every class split records the column
    and the two differing membership bits that justified it.
- **Determinism.** Given the teacher's answers, a run is reproducible
  bit-for-bit (ties are broken by shortlex, and counterexamples arrive
  minimized). Re-running with the same teacher reproduces the transcript.
- **Ablation switch.** The saturation phase can be disabled; the learner then
  still reaches an *acceptance-correct* fixpoint but may miss canonicity — the
  object of the saturation experiment.

## The one hard constraint

This module depends on **`sosl.contract` and `sosl.objects` only** — never
`reference`, never `teacher` internals, never spot or `aut2ltl`. Its only
knowledge of `L` is what the teacher answers. Any import that widens this is a
layering bug: it would let automaton structure leak into a "learned" result.

## Orientation map

    table       the observation table (rows, frontier, linear/omega columns)
    partition   classes from bit-rows; representatives; the step relation
    fold        ψ(w): letterwise step from [ε]; the ψ == class coherence check
    pcache      lazy accepting-pair verdicts, never invalidated
    procedures  fill / close / consist / saturate / counterexample chains
    export      fixpoint → M, re-key, fill P → canonical Invariant

## See also

`algorithm.md` — the learner algorithm proper (the procedures, saturation, the
counterexample chains, the loop, and the invariants asserted throughout). The
specification of record is `research_notes/sos_learner_spec.md` §3.2.
