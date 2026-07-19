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

The design discipline: **the learner never poses a hypothesis that is not a
language.** Every equivalence query ships a well-formed `Invariant` — the
canonical form of the learner's current belief language — and the certified
limit is `I(L)`, byte-equal to the reference construction. The theory is
`research_notes/sos_learning2.md`.

This is a distinct tool from `aut2ltl`. It reuses some of `aut2ltl`'s
primitives (HOA loading, the definability pipeline) but its intent is
orthogonal: `aut2ltl` *translates* a known automaton to a formula; `sosl`
*learns* an unknown language's algebra through a query interface.

## Services this package offers

- **`learn`** — given a teacher for an unknown `L`, reconstruct `I(L)` as a
  canonical serialized invariant, plus run statistics; see `learn/README.md`.
- **A teacher over any HOA automaton** — a correct membership + equivalence
  oracle for a deterministic Emerson-Lei automaton, usable on its own; see
  `teacher/README.md`.
- **An experiment driver** — batch a corpus through learn + validate under
  per-case budgets, aggregate run statistics into CSV; see
  `experiment/README.md`.
- **The SoS vocabulary and calculus** — the `Invariant`, its `.sos`
  serialization, the reference construction from an automaton, and the
  algebraic calculus (complement, product, align, decide, reduce) the exact
  oracle runs on; see `sos/README.md`.

## Orientation map (layering, acyclic, floor → top)

    sos/         the vocabulary and its services: letters, lassos, the
                 invariant I(L) and its .sos serialization (sos/io), the
                 reference construction from an automaton (sos/core,
                 sos/build — spot-backed), and the calculus (sos/calculus).
       ↑
    contract.py  the Teacher interface (member / equiv over Invariant
                 hypotheses). The learner's ONLY source of truth about L.
       ↑
    teacher/     Teacher implementations of `contract` over a known automaton.
       ↑
    learn/       the learner. Depends on `contract` + `sos` ONLY — never
                 teacher internals, never spot, never aut2ltl. A pure query
                 algorithm.
       ↑
    experiment/  the campaign: driver, statistics, harness, baselines.
       ↑
    quant/       quantitative studies over learned/reference invariants.

**The one inviolable edge:** `learn/` sees only `contract` + `sos`. That is
what makes the learner a pure query algorithm — its only knowledge of `L`
comes through the teacher interface. Everything else may lean on `aut2ltl`
and spot.

## Doc conventions in this tree

- **`README.md`** (this kind of file) is **client-facing**: what services a
  module offers and a small orientation map. Read it to *use* the module.
- **`algorithm.md`** is **dev-facing**: it gives the hard ideas a place to be
  described one level above the code. Read it to *change* the module. Most
  modules here are non-trivial and carry one.
- **Dunder files (`__init__.py`, `__main__.py`) are pointers only** — a
  docstring and re-exports / a one-line delegation. No logic lives in them; a
  named file always owns the logic.
