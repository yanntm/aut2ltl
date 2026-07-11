# aut2ltl.sos2ltl — LTL extraction from the syntactic ω-semigroup

A `Translator` whose engine runs on the invariant `𝓘(L) = (𝒞, λ, M, P)` — the
syntactic ω-semigroup in its canonical `.sos` form (`sosl.sos.Invariant`) —
rather than on any automaton the user supplied. The construction it implements
is `research_notes/sos_toltl.md`; the experiment contract is
`research_notes/sos_toltl_spec.md` (components C1–C7 below).

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
                              engine.py — walk+window transcription
                                          │ outside the flat-brick stratum
                                          ▼
                                        dg/    — Diekert–Gastin synthesis
```

## Modules

- **`bridge.py`** — `Language → sosl.sos.Invariant` via the reference
  construction (`sosl.sos.build`). The only Spot-adjacent module; a blown
  resource cap is a decline, never a verdict.
- **`readoffs.py`** (C5) — pure table scans: the λ-quotient of the alphabet,
  the residual (right-congruence) partition of the classes, prefix-independence
  (`P` loop-determined), absorbing classes. The aperiodicity verdict comes from
  `sosl.sos.classify.aperiodic`.
- **`guards.py`** — a letter set `S ⊆ Σ` as a minimized Boolean formula over
  `AP` (BDD + Minato ISOP, via `aut2ltl.ltl.builders.fuse_or`), memoized per
  set. The set-as-formula convention of the paper's §2.1: every guard position
  of every brick goes through it, so `{a&b, a&!b}` prints `a` and a set that
  is all of `Σ` prints `⊤`.
- **`cayley.py`** (C1) — `Cay(L)`: states `𝒞`, edges `c →^a M(c, λ(a))`; SCC
  decomposition and DAG; asserts SCCs = R-classes of `M` on every input
  (the Lemma 4.3 test).
- **`anchoring.py`** (C2) — condition (A) per layer, widths `k = 1, 2, 3`:
  letter classification `neutral | reset(t) | mixed` at `k = 1`, the
  Lemma 4.6(v) fixpoint above; builds the layer action monoid `𝒜_R` and the
  anchor windows `An_κ(c)` with their domains (the graded engine's triggers
  and seam certificates).
- **`windows.py`** (C3) — condition (B) per final-candidate layer and stem
  class, widths `k' = 1, 2, 3`, bounded: cheap sound pass, exact fail with a
  witness lasso pair, `UNDECIDED` on cap.
- **`witness/`** (§4) — the non-LTL certificate: three scans of the table →
  counting family `F₁(u, v, x, p′)` or `F₂(u, v, y, p′)`, plus the
  `2p′ + 1`-query toggle replay. See `witness/algorithm.md`.
- **`engine.py`** (C4) — the walk+window transcription: the §4.2 bricks
  (`sojourn`/`step`/`leave`/`STAY∞`) on 1-anchored layers, the §4.3 graded
  bricks (`step_κ`, the `TR`/`TL` transient fold trees, the `seam(c)`
  certificates — Theorem 4.13) on layers anchored at `k ≥ 2`, class-memoized
  `Final(c)`, window terms from the Prop 5.4 normal form (minimal-set `GF`
  collapse on upward-closed families). Operates on the anchored,
  window-determined stratum — every layer anchored at some finite width,
  every final-candidate layer window-determined — and returns None outside
  it (a no-width layer is the Prop 4.14 scoped fallback, not built here).
  Emits a hash-consed `spot.formula` DAG, never
  a string. `Rendering` switches the three §6 branch-factoring renderings
  (minimized guards, exit fans grouped by child, exit children keyed by
  residual); all on is normal operation, the flags exist to price each.
- **`dg/`** — the Diekert–Gastin local-divisor synthesis, consuming the
  invariant natively; the baseline and the fallback below the engine.
  See `dg/algorithm.md`.
- **`cascade/`** — the decomposition fallback (paper §6, spec E11): the
  per-layer KR-cascade delegate the engine consumes through its
  `LayerFallback` hook — the stem half on no-width layers (Prop 4.14,
  cascade extractor), the loop half on window-undetermined
  final-candidate layers (tail-restricted acceptor, `Fin(C)`). See
  `cascade/algorithm.md`.
- **`translator.py`** — the `Translator`: bridge, step-0 witness scan on
  `𝓘(L)` itself, then the engine behind its conformance gate (the
  emitted formula's reference invariant must be byte-equal to the
  input), dg where the stratum's preconditions fail. Faithful-or-NOK,
  like every translator. Registered as the portfolio recipe `sos2ltl`;
  `sos2ltl_casc` is the same assembly with the `cascade/` delegate
  below the engine.

## Layering

Depends on `sosl.sos` (the invariant floor — alphabet, lasso, invariant,
serialization, reference builder, the `classify` scans) and the `aut2ltl`
contract floor (`Language`, `LTLResult`, `Translator`, `Witness`). Imports
nothing from `aut2ltl.bls` — except `cascade/`, the single sanctioned
import point (the delegate consumes the bls gap bridge, operators and
member ladder). Tests live under `tests/sos2ltl/`.
