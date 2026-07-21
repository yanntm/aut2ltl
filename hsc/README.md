# hsc — Hierarchical Shape Calculus, prototype

Implementation of the calculus described in `research_notes/hsc_core.md`,
along the line of `research_notes/hsc_spec.md`. Performance is not a goal;
the products are the API, the measured cost model, and pressure on the
theory's open obligations.

## Layout

- `hsc/core/` — the kernel. Shapes, diagrams, the canonical decomposition,
  the support algebra, homomorphisms. See `hsc/core/README.md`.
- `hsc/leaves/` — leaf modules (imported support algebras). See
  `hsc/leaves/README.md`.
- `hsc/model.py` — modelling sugar: name leaves, build a shape, resolve
  names to frontier paths.
- `examples/` — runnable systems. `counter.py` (4-bit increment),
  `philosophers.py` (Ex1 of the calculus document).
- `tests/` — property checks against the brute-force shadow.
- `algorithm.md` — the algorithms, written before the code. Read it before
  editing `core/`.

## Quick start

```
python -m examples.philosophers      # from hsc/
python -m examples.counter
python -m tests.test_algebra
```

## Scope of this iteration

Deliberate simplifying assumptions, each one a named place to grow:

| assumption | where it bites | lifted by |
|---|---|---|
| Boolean coefficients only | subs are diagrams, never weighted maps | a `Semiring` instance on the sub position |
| no `Unit` shape | shapes are `Leaf \| Pair`; no data at the point | adding `Unit` to `shape.py` |
| guards are single-variable | `filter(a<b)` cannot be written | `split_equiv` (see `algorithm.md` §6) |
| assigns write constants | `assign(a := b+1)` cannot be written | `split_equiv` |
| no `split_equiv` yet | no `Θ`, no `case`, no discovered alphabets | the next milestone |
| no term/classifier language | homs are Python objects | the s-expression surface, later |

What *does* run end to end: shapes with composite heads (so Theorem 6.4's
internalization is exercised from the first line), the canonical
decomposition, the full support algebra (meet/join/relative difference,
no top anywhere), filters, parallel constant assigns, sum, and star —
enough to compute reachable sets and inspect their congruence towers.
