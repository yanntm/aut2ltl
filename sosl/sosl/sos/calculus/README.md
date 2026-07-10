# sosl.sos.calculus — a calculus over the syntactic ω-semigroup

Once a language has its invariant `𝓘(L) = (𝒞, λ, M, P)`, most of what one wants
to *do* with an ω-regular language is free. Complementation is a set difference.
Intersection is a set intersection. Emptiness, universality, inclusion,
equivalence and "give me a word in both" are scans of a membership oracle over
`|𝒞|²` cells, each returning the **shortest lasso** that settles the question.
Nothing is re-determinized, nothing is re-complemented, no automaton is built.

The one operation that costs a product is `align`, which puts two languages
presented over *different* algebras onto a common node set. Everything else is
either free (a pair-set operation) or a partition refinement (`reduce`, the
return to canonical form).

## Services

- **A table and its languages.** `Table` is one algebra `(𝒞, λ, M)`; a
  `PairSet` (an immutable set of its linked pairs) is one language over it. One
  table hosts many languages; nothing is ever mutated.
- **The membership oracle `Val`.** `table.val(P, c, d)` decides
  `key(c)·key(d)^ω ∈ L(P)` and, by the factoring theorem, the membership of
  *every* lasso whose stem folds to `c` and loop folds to `d`. Every decision
  below is a scan of `Val` over cells, never over words.
- **The free fragment** (`surgery`): complement, union, intersection,
  difference, xor, the constants; `rooting` (the left quotient `key(c)⁻¹·L`) and
  its residual-count read-off; `inverse_substitution` (relabeling, letter
  merging, alphabet extension); `saturate` / `pair_language` (is this pair set a
  language at all?).
- **The hulls** (`surgery`, paper §3.6): `safety_closure` / `interior` /
  `liveness_part` — the safety hull, its dual, and the Alpern–Schneider
  liveness factor, all `O(n²)` on the same table — with the exact rung tests
  `is_safety` / `is_cosafety` and the obligation read-offs `is_obligation` /
  `obligation_degree` (the Wagner coordinates `(n⁺, n⁻)` as longest alternating
  paths in the condensed right-Cayley graph).
- **The decisions** (`decide`): `member`, `is_empty`, `is_universal`,
  `included`, `equivalent`, `intersecting_word` — each returning a `Witness`
  that is the globally minimal lasso settling the question, replayable against
  any independent membership oracle.
- **The generated product** (`align`): the reachable pairs of classes, keyed by
  shortlex BFS. No product multiplication table is materialized.
- **The normal form** (`reduce`): re-quotient a table by the syntactic
  congruence of one of its languages, returning the canonical `Invariant`. Only
  after `reduce` is byte-equality of `.sos` dumps a language test.

## Orientation map

    table       Table (one algebra), PairSet (one language), Val, the cell scan
                order, and the FoldedLanguage protocol
    surgery     the free fragment: Boolean ops, rooting, saturation, inverse
                substitution; the hulls (safety closure / interior / liveness
                part) and the obligation read-offs
    align       align(A, B) -> Aligned: the generated product, verdicts read
                componentwise
    decide      emptiness / universality / inclusion / equivalence /
                intersection-word / membership — all witness-carrying
    reduce      reduce(table, P) -> Invariant: the canonical re-quotient
    witness     Witness: lasso + expected bit + provenance + replay

## Layering

This package imports `sosl.sos` (the objects, the `.sos` io, `core.canonical`)
and **nothing else in the repo** — never `sosl.learn`, `sosl.teacher`,
`sosl.experiment`. The dependency arrow points only inward: a learner may become
a client of the calculus, not the reverse. Where an operation must accept a
learner-side object it does so through the `FoldedLanguage` protocol of
`table.py` — a structural interface, no import. No external tool (Spot) is
imported here; `Witness.replay` takes the oracle as an argument.

## Using it

```python
from sosl.sos import load_invariant
from sosl.sos.calculus import (
    Table, align, complement, equivalent, is_empty, reduce,
)

inv   = load_invariant(open("some.sos").read())
table = Table.of(inv)

other = complement(table, inv.accept)          # free
empty, witness = is_empty(table, other)        # a scan, with a shortest lasso
canonical = reduce(table, other)               # the .sos of the complement

eq, cex = equivalent(align(table.language(inv.accept),
                           Table.of(canonical).language(canonical.accept)))
```

## See also

`algorithm.md` — the normative statement of the calculus: the three moves, the
cell scan and its minimality proposition, the surgery catalog with its
correctness facts, the reduction, and the soundness harness the gates in
`sosl/tests/calculus/` implement. The specification of record is
`research_notes/sos_calculus_spec.md`, whose normative math is
`research_notes/sos_calculus.md`.
