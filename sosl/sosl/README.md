# sosl — learning the syntactic ω-semigroup of an ω-regular language

`sosl` reconstructs the **canonical algebraic invariant** of an unknown
ω-regular language `L` from queries alone — lasso membership queries and
equivalence queries, Angluin-style. The invariant it learns is

    I(L) = (C, key, λ, M, P)

the finite congruence classes `C`, their canonical shortlex keys `key`, the
letter map `λ`, the class multiplication table `M`, and the accepting
**linked pairs** `P`. From `I(L)` alone the membership of *any* lasso is
decidable, and structural questions about `L` (e.g. "is it LTL-definable?")
are read off the algebra directly.

This is a distinct tool from `aut2ltl`. It reuses some of `aut2ltl`'s
primitives (HOA loading, the definability pipeline that already computes a
reference invariant) but its intent is orthogonal: `aut2ltl` *translates* a
known automaton to a formula; `sosl` *learns* an unknown language's algebra
through a query interface.

## Services this package offers

- **`sos_learn`** — given a *teacher* for an unknown `L` (a white-box HOA
  automaton, or a black-box process over a JSON wire protocol), emit the
  learned invariant as a canonical serialized file, plus run statistics and a
  full query/decision audit transcript. This is the deliverable.
- **`sos_validate`** — check a learned invariant against a reference: exact
  byte-equality of the canonical serialization (the soundness criterion), or a
  weaker *acceptor* check (does its membership read-off agree with direct
  automaton simulation on all lassos up to a bound).
- **A teacher over any HOA automaton** — a correct membership + equivalence
  oracle for a deterministic Emerson-Lei automaton, usable on its own.
- **An experiment driver** — batch a corpus of automata through learn +
  validate under per-case budgets, aggregate the run statistics into one CSV,
  and run the layered soundness harness.

## Orientation map (layering, acyclic, floor → top)

    objects/     the vocabulary: letters, lassos, the invariant I(L), the
                 mid-learning Cayley hypothesis, and their canonical text
                 serializations. Pure data; no automata, no spot.
       ↑
    contract.py  the Teacher interface (member / equiv). The learner's ONLY
                 source of truth about L.
       ↑
    reference/   build the reference I(L) from an HOA automaton (adapter over
                 aut2ltl's definability pipeline). Used by the teacher and the
                 validator; the learner NEVER imports it.
       ↑
    teacher/     Teacher implementations of `contract` over a known automaton
                 (white-box) or a spawned process (black-box).
       ↑
    learn/       the learner. Depends on `contract` + `objects` ONLY — never
                 reference, never spot, never aut2ltl. A pure query algorithm.
       ↑
    validate/    the invariant checkers (byte-equality + acceptor).
       ↑
    experiment/  the campaign: driver, statistics, harness, baselines.
       ↑
    __main__     the CLI front end (sos_learn / sos_validate dispatch).

**The one inviolable edge:** `learn/` sees only `contract` + `objects`. That is
what makes the learner a pure query algorithm — its only knowledge of `L` comes
through the teacher interface. Everything else may lean on `aut2ltl` and spot.

## Doc conventions in this tree

- **`README.md`** (this kind of file) is **client-facing**: what services a
  module offers and a small orientation map. Read it to *use* the module.
- **`algorithm.md`** is **dev-facing**: it gives the hard ideas a place to be
  described one level above the code. Read it to *change* the module. Most
  modules here are non-trivial and carry one.
- **Dunder files (`__init__.py`, `__main__.py`) are pointers only** — a
  docstring and re-exports / a one-line delegation. No logic lives in them; a
  named file always owns the logic.

## Status

The objects, teacher, validator, and the query learner (without saturation) are
in place: the learner reconstructs the invariant end to end and, on many census
cases, byte-matches the reference. The reference builder wraps the in-repo
definability pipeline behind the `sosl.sos` vocabulary. Current work is
milestone M2.5 — aligning both sides on the fresh-identity convention
(`objects/algorithm.md`, `reference/algorithm.md`) — ahead of M3 (saturation +
exact equivalence). The serialization is `.sos`; milestones and acceptance
gates are in `research_notes/sos_learner_spec.md` (the specification of record).
