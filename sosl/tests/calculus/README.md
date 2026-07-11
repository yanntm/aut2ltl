# tests/calculus/

The soundness harness of [`sosl.sos.calculus`](../../sosl/sos/calculus/) — the
eight checks of `algorithm.md` §7, one script each (plus a smoke run). Every
script is **single-input and self-bound**: it takes one `.sos` (or one directory
to sample), prints what it covered, and ends `SUCCESS`. A failing assertion
names the cell, the operation, and the lasso that broke.

A gate's answer key must not come from the code under test: `flat_canon`'s
filenames, the `.cat` sidecars, the paired det HOA and Spot are the keys used
here, and a hand-written reference is built from an independent model (the word
model, `sos.build.reference_of_ltl`) rather than transcribed. A reference that
shares the algebra it checks agrees with it for free — including where both are
wrong.

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

## The experiment scripts (`v*_*.py`)

Not gates: campaigns that measure the package against Spot over the census, for
`research_notes/sos_calculus_report.md`. Shape, uniform across them — `--one
<case>` for a single input, `--campaign` for the sweep, a per-case watchdog, and
a checkpoint in `logs/` (gitignored) so a stall loses one case and a restart
skips what finished. Validated `.md`/`.csv` are copied into
`reference/calculus/` with a 4-line header (date, git rev, seed, corpus).

| script | measures |
|---|---|
| `v1_align.py` | the alignment ratio against the rectangle `n_A·n_B`. |
| `v1_ops.py` | the operation ledger, calculus vs Spot, with abstract counts beside the wall clocks. |
| `v1_pipeline.py` | a four-stage pipeline: intermediate sizes and re-check costs. |
| `v2_stutter.py` | the stutter read-off vs `spot.is_stutter_invariant`. |
| `v3_blowup.py` | `\|𝒞(W·L_n)\| ≥ 2ⁿ−1` on hand-built acceptors, n = 2..5. |
| `v4_ladder.py` | `is_safety` / `is_cosafety` / `is_obligation` / `obligation_degree` vs Spot on the paired det HOA. `--selftest` pins Spot's semantics (below) against `spot.mp_class` on eight formulas of known Manna–Pnueli class. |

## Talking to Spot

- **Read the headers under `opt/spot/include/spot/`.** The Python docstrings are
  empty; the headers carry the contracts.
- **Spot has no automaton-level Manna–Pnueli classifier.** `spot.is_obligation`,
  `is_persistence`, `is_recurrence`, `mp_class` are *formula-level*
  (`tl/hierarchy.hh`: the formula is a mandatory argument, the automaton only an
  optional accelerator), and `autfilt` exposes only *structural* `--is-weak` /
  `--is-terminal`. Translating out is not available either — much of the census
  is not LTL-definable, so no formula exists to hand them. The formula-free
  automaton route (`v4_ladder.py`), language-level on a deterministic complete
  input: safety is `is_safety_automaton` (its contract — "the acceptance
  condition can be set to `true` without changing the language",
  `twaalgos/strength.hh` — is the closure fixpoint); co-safety is the same test
  on the complement; obligation is `minimize_wdba` plus an equivalence check
  (what Spot's own `ocheck::via_WDBA` runs inside `is_obligation`).
- **`spot.dualize` complements exactly only on a deterministic complete
  automaton**; on anything else it returns an alternating automaton that the
  predicates reject. Guard the precondition rather than trusting the input.
- **`spot.translate(f, "deterministic", …)` is a preference, not a guarantee** —
  `F G p` comes back nondeterministic under Büchi output. Pass `"generic"` when
  an actual DELA is wanted.
- Per-state emptiness on a det HOA: `aut.set_init_state(q)` + `aut.is_empty()`
  works on generic (EL) acceptance; restore the initial state after.
- Lasso replay against a det HOA goes through
  `sosl.teacher.whitebox.HoaTeacher.of_hoa(path).member(lasso)` — do not
  hand-parse letters.

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
