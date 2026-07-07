# aut2ltl.sos2ltl — LTL extraction from the syntactic ω-semigroup

A `Translator` whose engine runs on the invariant `𝓘(L) = (𝒞, λ, M, P)` — the
syntactic ω-semigroup in its canonical `.sos` form (`sosl.sos.Invariant`) —
rather than on any automaton the user supplied. The construction it implements
is `research_notes/sos_toltl.md`; the experiment contract is
`research_notes/sos_toltl_experiments.md` (components C1–C7 below).

The LTL/non-LTL verdict is a power-orbit scan of the multiplication table
`M` (`sosl.sos.classify.aperiodic`), exact by canonicity of the invariant —
both sides of the verdict are theorems, never suspicions.

## Pipeline

```
Language ──bridge──► Invariant 𝓘(L) ──classify.aperiodic──► aperiodic?
                                          │no: group orbit
                                          ▼
                                     witness/  — §4 counting family F₁/F₂,
                                          │      toggle-replayed → NOT_LTL
                                          │yes
                                          ▼
                        cayley → anchoring/windows — (A)/(B) read-offs
                                          │
                                          ▼
                                        dg/    — Diekert–Gastin synthesis
```

## Modules

- **`bridge.py`** — `Language → sosl.sos.Invariant` via the reference
  construction (`sosl.sos.build`). The only Spot-adjacent module; a blown
  resource cap is a decline, never a verdict.
- **`readoffs.py`** (C5) — pure table scans: the λ-quotient of the alphabet,
  prefix-independence (`P` loop-determined), absorbing classes. The
  aperiodicity verdict comes from `sosl.sos.classify.aperiodic`.
- **`cayley.py`** (C1) — `Cay(L)`: states `𝒞`, edges `c →^a M(c, λ(a))`; SCC
  decomposition and DAG; asserts SCCs = R-classes of `M` on every input
  (the Lemma 5.3 test).
- **`anchoring.py`** (C2) — condition (A) per layer, widths `k = 1, 2, 3`:
  letter classification `neutral | reset(t) | mixed` at `k = 1`, the
  Lemma 5.6(v) fixpoint above; builds the layer action monoid `𝒜_R`.
- **`windows.py`** (C3) — condition (B) per final-candidate layer and stem
  class, widths `k' = 1, 2, 3`, bounded: cheap sound pass, exact fail with a
  witness lasso pair, `UNDECIDED` on cap.
- **`witness/`** (§4) — the non-LTL certificate: three scans of the table →
  counting family `F₁(u, v, x, p′)` or `F₂(u, v, y, p′)`, plus the
  `2p′ + 1`-query toggle replay. See `witness/algorithm.md`.
- **`dg/`** — the Diekert–Gastin local-divisor synthesis, consuming the
  invariant natively. See `dg/algorithm.md`.
- **`translator.py`** — the `Translator`: bridge, step-0 witness scan on
  `𝓘(L)` itself, then synthesis. Faithful-or-NOK, like every translator.

## Layering

Depends on `sosl.sos` (the invariant floor — alphabet, lasso, invariant,
serialization, reference builder, the `classify` scans) and the `aut2ltl`
contract floor (`Language`, `LTLResult`, `Translator`, `Witness`). Imports
nothing from `aut2ltl.bls`. Tests live under `tests/sos2ltl/`.
