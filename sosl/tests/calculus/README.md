# tests/calculus/

The soundness harness of [`sosl.sos.calculus`](../../sosl/sos/calculus/) — the
eight checks of `algorithm.md` §7, one script each (plus a smoke run). Every
script is **single-input and self-bound**: it takes one `.sos` (or one directory
to sample), prints what it covered, and ends `SUCCESS`. A failing assertion
names the cell, the operation, and the lasso that broke.

Run as modules from the `sosl/` subtree root (see [`../README.md`](../README.md)
for the import discipline):

```
cd sosl
CORPUS=../genaut/corpus/flat_canon/sos
python3 -m tests.calculus.smoke         $CORPUS/3state1ap0acc_074764.sos
python3 -m tests.calculus.laws          $CORPUS/3state1ap0acc_074764.sos
python3 -m tests.calculus.align_gate    $CORPUS/3state1ap0acc_074764.sos $CORPUS/3state1ap0acc_074764_c.sos
python3 -m tests.calculus.product_gate  $CORPUS/3state1ap0acc_074381.sos $CORPUS/3state1ap0acc_013844.sos
python3 -m tests.calculus.duality       $CORPUS/3state1ap0acc_074764.sos
python3 -m tests.calculus.witness_min   $CORPUS/3state1ap0acc_005684.sos $CORPUS/3state1ap0acc_074764.sos
python3 -m tests.calculus.corpus_oracle $CORPUS 40 0
python3 -m tests.calculus.hulls         $CORPUS/3state1ap0acc_074764.sos
python3 -m tests.calculus.obligation_oracle $CORPUS 60 0
python3 -m tests.calculus.example_gate
```

## Source map

| script | harness | checks |
|---|---|---|
| `smoke.py` | — | every entry point once on one file: table shape, residual count, saturation of `P` and `Pᶜ`, the emptiness / universality / equivalence / intersection witnesses, the self-alignment ratio, and `reduce`. The first thing to run on a new input. |
| `laws.py` | 1–4 | Boolean laws with pointwise `Val` agreement on every cell; the saturation law on every catalog output; metamorphic replay (`member` of a result is the operation on the `member`s of its inputs) exhaustively over lassos with `|u|,|v| ≤ 3`, including the three `inverse_substitution` maps; the rooting action laws. |
| `align_gate.py` | 5 | `align(I, I')` on two separately loaded copies is the diagonal and `equivalent` accepts it; `reduce` is byte-identity on an already-reduced invariant. With a second file: `equivalent` over the aligned product agrees with `byte_equivalent` of the two reduced sides, and a disagreement witness replays positive on the left and negative on the right. |
| `product_gate.py` | 5b | `materialize(align(a, b), a, b)` builds the product omega-semigroup that `align` defers: over every canonical cell lasso of the aligned product, `member` of `reduce(a ∩ b)` / `reduce(a ∪ b)` equals the Boolean combination of the two sides' `member`s; both carried sides are saturated; and the intersection is empty exactly when `intersecting_word` finds no shared word. `--sample N` sweeps same-alphabet corpus pairs. |
| `duality.py` | 6 | `complement` is an involution, and `reduce(complement(P))` is **byte-identical** to the corpus's stored complement (`X.sos` ↔ `X_c.sos`) — the free operation landing exactly on the canonical form an independent automaton-side construction produced. Without a companion file, the involution law alone. |
| `corpus_oracle.py` | 7 | language equality *is* filename equality in `flat_canon/`, an answer key the calculus never sees. Over a sample: same-file pairs are `equivalent` (and byte-equal reduced), cross-file pairs are separated by a witness that replays against both sides. Accumulates the alignment-ratio distribution — the V1 ledger's raw material. |
| `witness_min.py` | 8 | Proposition W: the cell scan returns the *globally* minimal witness. Brute-force every lasso up to a bound in the same discipline order and demand the same lasso. A second file adds the cross-language scans, where the minimal separator is long enough for the claim to bite. |
| `stutter.py` | V2 prereq | `Table.is_stutter_invariant` (paper Prop 3.3, the algebraic read-off) against the exact §8.6 divergence search over class triples/pairs: on a canonical invariant they must agree, and every "sensitive" verdict comes with two stutter-equivalent lassos that `member` confirms disagree. |
| `hulls.py` | CAL5 | the hull surgeries (paper §3.6): `safety_closure` is a closure operator and `interior` its dual (extensive/monotone/idempotent, outputs saturated), the duality and Alpern–Schneider decomposition identities, the exact `is_safety`/`is_cosafety` fixpoint tests, hull Boolean combinations are obligations — and `member` of the closure equals prefix-liveness on the paired det HOA (per-state emptiness, Spot) over all lassos up to the exhaustive bound. |
| `example_gate.py` | E-CAL-EX | the paper's running example, mechanically: the five-class table of `a*·b^ω` (regenerated from the word model `{ε, a⁺, b⁺, a⁺b⁺, dead}`, not transcribed), its linked pairs and `P`, the stutter read-off, the two rootings, the hulls and the degree `(1, 2)` — cross-checked against `classify`'s Wagner coordinates *and* against the `.cat` sidecar of the corpus row holding the language (`2state1ap1acc_16898`, located by genaut's own `canon_key`: the `B_k` orbit-min bytes, in the corpus's AP naming) — then `𝓘(GF a)` and the alignment of the two: 5 nodes of `5 × 3`, empty intersection, `a*·b^ω ⊆ FG ¬a` holding and its converse refuted by `ba·b^ω`. Both invariants are built by `sos.build.reference_of_ltl` (Spot + quotient), so the calculus reads off an algebra it did not build. No argv. |
| `obligation_oracle.py` | CAL5 | `is_obligation` / `obligation_degree` against the `.cat` Wagner coordinates, the answer key the calculus never sees: obligation ⟺ `max(m⁺, m⁻) ≤ 0` (a `-1` polarity still counts — the empty/universal convention), and on every obligation row the degree equals the sidecar `(n⁺, n⁻)`. Opens with the paper's worked reference `a*·b^ω → (1, 2)`. `LIMIT 0` (default) sweeps the whole directory. |

## Scope and budget

Checks quadratic in the class count (`rooting` action laws, saturation of every
rooting, the metamorphic rooting sweep) run over a **sampled** class set once a
table exceeds 16 classes; `laws.py` prints `classes N sampled` when it does. This
keeps one gate on one input inside the per-example diagnostic budget: the largest
census table (121 classes) takes ~4.5 s.

`corpus_oracle.py` takes `COUNT` and `SEED`; it runs all `COUNT²` ordered pairs
and restricts the draw to one alphabet (`align` compares languages over one Σ).
40 files ≈ 1 s.

## What these do not cover

The package itself imports no external tool, and `Witness.replay` takes its
oracle as an argument. The only Spot use in the harness proper is `hulls.py`'s
per-state emptiness on the paired det HOA (skipped with a note when no HOA is
paired); the V1 (ledger) and V2 (read-off validation) experiments of
`research_notes/sos_calculus_spec.md` §5, which compare against Spot
bounded-or-skipped at scale, live in the `v*_*.py` scripts.
