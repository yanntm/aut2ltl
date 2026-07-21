# hsc/core — the kernel

Read `../../algorithm.md` before editing anything here; the code is meant to
be its transcription.

| module | responsibility |
|---|---|
| `shape.py` | interned shape trees, frontier paths, name resolution |
| `leaf.py` | the leaf interface: the tier ledger as an ABC, plus `TierError` |
| `diagram.py` | `Node`, the unique table, uids, the adjoined zero |
| `algebra.py` | `normalize` (Theorem 5.1) and the support algebra; mutually recursive, hence one module |
| `hom.py` | homomorphism base class and the (term, data) application cache |
| `local.py` | position-addressed homs: `Filter`, parallel constant `Assign` |
| `combinators.py` | `Identity`, `Compose`, `Sum`, `Star` |
| `expr.py` | classifiers: an interned expression language over coordinates |
| `query.py` | `split_equiv`, `Partition`, the kernel merge, and `theta` |
| `branch.py` | classifier-driven homs: `Guard`, `Put`, `Case` |
| `stats.py` | the invoice: call counters, split by side of the leaf interface |

Invariants the kernel maintains and never re-derives:

- zero is `None` at every shape; it is never stored in a node, never
  traversed, never sorted;
- nodes are unique-tabled, so equal diagrams are the same object and
  emptiness at a composite shape is a pointer test;
- primes over a composite head are diagrams over that head — there is one
  diagram type, and internalization is the class hierarchy;
- no `top` and no `complement` is called anywhere; every carving is a meet
  or a relative difference against a prime already present;
- there is no inverse image, absolute or relative, and none is planned.

`split_equiv` is the one traversal; `Guard`, `Put`, `Case` and `theta` are
its callers, differing only in the codomain of the classifier and in what
they do with the pieces. Nothing re-implements the traversal.

A local hom at a cut is *the same hom one level down*, applied to primes or
to subs, and it recurses by re-invoking itself so the application cache is
hit. Recursing through a plain helper instead walks the diagram's tree
unfolding rather than its DAG, which throws away the sharing that is the
whole point of the representation.

`support()` on a hom is a static over-approximation of the coordinates it
touches -- the complement of libDDD's `skip`. It is groundwork for a
schedule, not used by one yet: the current `Star` is plain BFS, whose cost
is rounds x events x |X| in freshly built nodes. Saturation is the fix and
is deliberately not attempted here.

`algebra.DEBUG` toggles the degeneracy-ledger assertions on every
constructed node. A release-mode failure that debug mode would have caught
is by construction a coefficient-discipline violation.
