# SoS Symbolic Engine — Experimentation Specification

**Status:** specification / declaration of intent. This document is the
interface between the paper (`sos_symbolic.md`) and the implementation
sessions: the paper's §8 evaluation plan and its ⟨TBD⟩ measurements are
fed by the experiment ids below, per the family discipline
(`sosl_report.md` ledger style).
Companion specs: `sos_census_experiments.md` (the measurement corpus and
the derived-census driver, the engine's first consumer at scale),
`sos_toltl_experiments.md` (downstream consumer of the emitted quotient).

**State of play.**
- **DONE (exists in-repo, consumed as-is):** the explicit reference
  construction emitting `.sos` (the conformance oracle); the HOA parser
  side of C2; the triptych automata.
- **DONE (paper-side, settles questions this spec used to leave open):**
  the flat-order lower bound is *stated and proved* for row-major-style
  orders (paper Lemma 4.2), with the any-order question posed as
  Conjecture 4.3 — E3 now probes the conjecture, it no longer decides a
  lemma; the shortlex/witness extraction mechanism is pinned (backward
  preimage sets + *forward* least-letter walk — see C7, C10); the
  calculus is specified with its correctness propositions (paper §6,
  Props 6.0–6.2) — covered by C10 + E9.
- **TODO: everything else.** C1–C10, E0–E9, M1–M5: none started.

**One-line goal.** Provide the data for `sos_symbolic.md`: the
compression scatter (diagram size vs `|EM|`), the factored-vs-flat
scaling lines on product families (Proposition 4.1 measured), the
phase cost profile, the fixpoint-discipline and variable-order studies,
the calculus in motion, and the bottom line against the explicit
construction's closure cap — under a conformance gate that the engine's
output invariant is byte-identical to the reference's.

---

## 1. Objects consumed

- **The explicit reference construction** emitting `𝓘(L)` in `.sos`
  format, with its closure cap / `INCONCLUSIVE` exit *(exists)* — the
  conformance oracle and the E6 baseline.
- **The census corpus** — machine census + triptych + intrinsic rows
  once `sos_census_experiments.md` M3 lands — the compression scatter's
  x-axis population.
- **The triptych**, `EvenBlocks` in particular: `|Q| = 2`, `C = {0,1}`,
  slot domain of 8 values, `|EM¹| = 16` identity included
  (`⟦aa⟧ = ⟦ε⟧` merges into it, [SωS26, Table 2(c)]) — the paper's
  §3.1 worked specimen *(exists)*.
- **HOA inputs as Boolean relations**: transition relation
  `Δ(q, α, q′)` with AP-guards, mark predicates `Mk_c(q, α)` — the
  paper's §2.3 input contract; the parser side exists in-repo, the
  relational build is C2.
- **A decision-diagram backend** offering the five primitives (§2.2 of
  the paper): set algebra, comparison, `2k`-variable relations applied
  to `k`-variable sets, constrained fixpoints, quotient by an
  equivalence. ⟨Backend choice is an implementation decision to record,
  not to mandate here; multi-valued and hierarchical variants are what
  §4.2 wants — the flat-vs-factored study E3 needs *both* encodings on
  one backend to be fair.⟩

## 2. Components to implement (library level, no CLI polish needed)

**C1 — engine bindings.** The five primitives over the chosen backend,
plus instrumentation hooks: node counts (peak and final) per operation,
fixpoint round counts, wall time per phase. Every experiment below is a
reading of these hooks; build them first, not last.

**C2 — symbolic input builder (Phase 0).** From HOA: `Δ`, `Mk_c`,
the slot domain `V = Q × 2^C`, the letter-element relation
`Lett(α; x)` and the right-multiplication relation `R(α; x, x′)` —
slot-local by construction, `α` carried symbolically, the alphabet
never enumerated.

**C3 — closure (Phase 1).** Layered lfp from the identity vector;
layers *kept* (they are the length half of shortlex keying and Phase
6's extraction path). The explicit tool's closure cap becomes a
**diagram-node budget**: blowing it is a `DIAGRAM_BUDGET` finding with
the layer profile attached, never a silent abort. Cardinality
(`|EM¹|`) available by model count for cross-checks.

**C4 — the crossing (Phase 2).** The composition relation
`Comp(x, y, z)` (the `|Q|`-way case split), the pairing lfp for the
idempotent-power map `π`, and the aperiodic squaring shortcut
(`O(log ℓ)` applications of `Sq`), with the guard the paper specifies:
squaring is a shortcut, never a verdict — on inputs where the shortcut
and the general pairing disagree, that is a stop-the-line bug.

**C5 — profiles and residuals (Phases 3–4).** `ProfR` as π-composition
+ one slot-read + the `Acc` predicate (no cycle detection anywhere —
assert it: no orbit walk in the code path); the residual gfp on
`Q × Q`, profile-seeded, oracle-free. Cross-check `≃` against the
explicit tool's residual classes on every conformance instance.

**C6 — congruence (Phase 5).** Seed (`~lin` slot-conjunction over `≃`,
`~ω` profile columns) and the gfp partition refinement over the
slot-local letter relations only — assert statically that no
`Comp`-shaped relation is applied inside this fixpoint (the rotation
lemma as a code invariant, §4.1 of the paper).

**C7 — quotient and exports (Phase 6).** Quotient, shortlex
representative extraction through the kept layers — the mechanism the
paper pins in Phase 6: the minimal layer gives the length, a backward
preimage pass builds the layer-indexed can-still-reach sets, and a
*forward* walk through them choosing the least letter gives the
lex-least word (a backward letter choice minimizes the wrong end,
yielding reverse-lex — do not implement that) — the multiplication
table (`M(κ, a)` by `R_a` images, `M(κ, κ′)` by folding representative
words, never `Comp`), λ-quotient with symbolic guards, accepting pairs
via `Val` on representatives, residuals block; serialize to `.sos`.

**C8 — product family generators.** From a fixed component `D`: the
`n`-fold asynchronous product `D^{⊗n}` (disjoint alphabets and marks)
and synchronous (shared-alphabet) variants; emit each in **both slot
coordinates** — factored (component-grouped variables) and flat (one
slot per global state) — as inputs to E2/E3. `EvenBlocks^{⊗n}` is the
canonical family (`|EM| = 16ⁿ`, by Proposition 4.1 of the paper).

**C9 — order and discipline switches.** Variable-order control
(slot grouping; state-above-marks vs interleaved within slot) and
fixpoint-discipline control (layered BFS vs chaining vs
saturation-style where the backend offers it) — E7/E8 are sweeps over
these switches, so they must be switches, not forks.

**C10 — the calculus (paper §6).** Moves on tables built by C2–C4;
each item names its paper anchor and its built-in assertion:

- **Lasso membership, closure-free (§6.1):** fold `u`, `v` through `R`
  with `α` fixed on singleton sets; `d^π` by concrete power iteration
  (squaring on the aperiodic side); verdict `Val(c, d)`. *Assert Phase
  1 never runs on a membership query.*
- **Same-table Boolean algebra (§6.2):** complement / `∪ / ∩ / \` as
  predicate combinations over one table — no diagram moves to build,
  only the plumbing that keeps several `Acc` predicates per table.
- **Alignment (§6.3):** block-concatenated slot spaces, letter
  relations conjoined on the shared `α`-block (AP-set union free),
  Phase 1 lfp on the aligned space; the aligned π-map assembled
  per block (Prop 6.1). *Assert `Comp` is never applied on the aligned
  space.*
- **Inclusion / equivalence / emptiness (§6.4):** the `S` projection
  onto `Q₁ × Q₂`, the `Bad` intersection, the degenerate same-`D` and
  emptiness forms.
- **Witness extraction (§6.4, Prop 6.2):** the layer-driven selection
  — least stem layer `i*`, least loop layer `j*`, then the coupled
  lex-least forward walks (C7's mechanism, reused verbatim).
- **Rootings and inverse substitutions (§6.5):** `ι`
  re-parameterization; generator substitution + constrained re-closure
  inside the existing `EM¹`.

## 3. The conformance gate (mandatory, every experiment)

For every instance where the explicit reference terminates within its
cap: the engine's emitted `𝓘(L)` must be **byte-identical** to the
reference's after canonical keying. A mismatch is a stop-the-line bug —
the engine changes representation, never mathematics (§3 of the paper,
"correctness wholesale"). Where the reference does *not* terminate, the
instance is `UNVERIFIED`: sanity-checked by model-count consistency
(`|EM¹|` vs layer sums; idempotence of the emitted table; E0-style
spot lassos through `Val`), and reported as such — an `UNVERIFIED`
success is a claim about scale, and is labeled as one.
Timeouts: per-instance cap 15s for census-sized runs; scaling families
run under explicit per-point budgets recorded in the log. A blown cap
or budget is a finding (`TIMEOUT` / `DIAGRAM_BUDGET`), not an error.
Long outputs to `tests/**/logs/`, one file per experiment id.

## 4. Experiments

### E0 — sanity on the worked examples (gates M1)

C2+C3 on the triptych, full pipeline once M2 lands. **Predictions to
confirm:** `|EM¹|` = 10 / 7 / 16 for `GF(aa)` / `Even` / `EvenBlocks`,
identity included, per [SωS26, Tables 1–2] (for `EvenBlocks`,
`⟦aa⟧ = ⟦ε⟧` merges into the identity — 15 non-identity elements);
closure depths match the longest shortlex key per [SωS26]; emitted `𝓘`
byte-equal to the reference on all three; for `EvenBlocks`, the diagram
node count of the closed `EM¹` is strictly below the 32 explicit slot
cells — the §3.1 figure's numbers, to be drawn from this run.

### E1 — the compression scatter (census corpus)

Full pipeline over the census corpus; record per instance `|EM¹|`
(model count) against final and peak diagram nodes, plus the §4.2
unconditional-compression covariates (constant/shared slots, mark
upward-closure, guard-equal letters). **Paper deliverable:** the
scatter and its correlates — which structure predicts compression.
**Prediction:** diagram ≤ explicit cells on essentially all census
rows, with compression strongest on sparse-mark, letter-symmetric
inputs.

### E2 — asynchronous scaling (Proposition 4.1, measured)

`EvenBlocks^{⊗n}` (and one second component family for robustness),
factored coordinates, `n` ascending. Record cardinality `|EM¹| = 16ⁿ`
(model count — also a *test* of the interleaving-factorization
Proposition 4.1: assert the count and the per-component projections)
vs diagram nodes. **Paper deliverable:** the measured line — additive
diagram size against multiplicative cardinality. **Prediction:**
factored diagram grows `O(n · component)`; the proposition's
isomorphism verified exactly at every `n` the budget allows.

### E3 — flat vs factored (Lemma 4.2 illustrated, Conjecture 4.3 probed)

The same `D^{⊗n}` inputs in flat slot coordinates, best flat order the
sweep finds (C9). The paper has *decided* this question's shape: the
row-major flat orders are provably exponential (Lemma 4.2), and
whether some order escapes is Conjecture 4.3. E3 therefore does not
arbitrate a lemma; it illustrates the proved half and probes the
conjecture. **Paper deliverable:** the divergence plot — flat width
against `n` per order tried, against the factored line. **Prediction:**
every order the sweep tries blows exponentially while factored stays
linear. A flat order that stays small would contradict nothing proved
— Lemma 4.2 only covers row-major-style boundaries — but it is a
research finding against Conjecture 4.3 and a paper edit; report it
prominently, not as a failure.

### E4 — synchronous products

Shared-alphabet products of census components; measure the distance of
the reachable `EM¹` from full product form (model count vs `∏|EMᵢ|`,
per-component projections). **Paper deliverable:** the distance column
— how close engineered synchronizations stay to product form, the
compactness bet's empirical content on its harder half. **Prediction:**
distance grows with synchronization density; no closed-form guess ⟨that
is the point of measuring⟩.

### E5 — phase profiling

Per instance (census + scaling families): time and peak nodes per
phase. **Paper deliverable:** the cost table of §5 with measured
columns. **Prediction:** Phase 2 (the crossing) and Phase 4's seed
quantification (`∀x ∈ EM` per state pair) are the peaks; Phases 5–6
are cheap relative to closure. A different profile is a paper edit
(the §5 table's narrative).

### E6 — the bottom line vs the explicit implementation

Two-column showdown on the corpus + scaling families: instances the
explicit closure cap kills that the engine carries (to `UNVERIFIED` or
verified completion), and the converse (diagram budget blown where
explicit enumeration walks through — expected on unstructured inputs
with incompressible monoids). **Paper deliverable:** the headline —
whether the `|Q|` exponent *moved* from cardinality to diagram width on
structured inputs. **Prediction:** the engine wins on products and
loses nowhere on the census ⟨low confidence on the second half⟩.

### E7 — variable-order sensitivity

C9 sweep: slot grouping strategies × within-slot orders, on a fixed
census subset + one scaling point. **Paper deliverable:** the ⟨TBD:
order study⟩ of §3 — how sensitive the pipeline is, and the
recommended default. **Prediction:** within-slot order is second-order;
slot grouping (factored vs flat, §4.2) dominates everything.

### E8 — fixpoint discipline

Layered BFS vs chaining vs saturation-style (where the backend offers
it) on Phases 1 and 5; record rounds, peak nodes, time; separately,
Phase 5's effective-round count vs its `|EM|` bound (the
early-stabilization phenomenon). **Paper deliverable:** the ⟨TBD: vs
saturation⟩ decision of §3 Phase 1, with the caveat the paper already
fixes — the layers are load-bearing for shortlex extraction, so any
non-layered discipline must reconstruct lengths (cost it honestly).
**Prediction:** saturation-style wins on peak nodes for Phase 1;
Phase 5 stabilizes far below its bound.

### E9 — the calculus in motion (paper §8(vii))

C10 on census pairs plus one scaling pair: a worked multi-operation
pipeline — complement, conjoin, inclusion check with witness, edit,
re-check — measured against per-operation automata constructions
(Spot as the baseline where formats allow; honest attribution per the
working rules — a baseline failing on >32 acceptance sets is its
limit, not ours). Three deliverables, two of them gates:

- **Commutation gate (Prop 6.0), mandatory:** for every conformance
  instance and every move, op-then-reduce must be byte-identical to
  reduce-then-op (the invariant-level operation of [SωS26, §7.2]).
  A mismatch is a stop-the-line bug in the move's implementation.
- **Witness gate (Prop 6.2):** on small instances, cross-check the
  extracted lasso against brute-force enumeration of lassos in
  (stem length, loop length, lex) order — the extracted one must be
  the least separating presentation, exactly.
- **Deferred reduce, priced:** the same operation sequence run
  reduce-at-the-end vs reduce-after-every-op — the "pay canonicity
  only when consumed" slogan as a measured column.

**Prediction:** same-table operations are free; aligned operations
cost one closure each and dominate; witness extraction is cheap
against the closure that enabled it (its backward sets are `O(depth)`
small-space passes).

## 5. Expected failures (read before filing bugs)

- **`DIAGRAM_BUDGET` on unstructured inputs is a datum** — the honest
  wall (§4.3 of the paper); record the layer profile and move on. The
  PSPACE lower bound predicts these exist; finding none would itself be
  suspicious.
- **Flat-coordinate blowups in E3 are the predicted result**, not a
  regression; only *factored* blowups on asynchronous products
  contradict the paper (stop-the-line: they refute Proposition 4.1's
  corollary, which is proved — so they mean a bug).
- **`UNVERIFIED` is not verified**: beyond the explicit cap the
  conformance gate is one-sided; never promote an `UNVERIFIED` run to a
  correctness claim in the paper's tables.
- **Squaring vs pairing disagreement** (C4) is stop-the-line; squaring
  silently *agreeing* on a period-2 group is expected (it detects
  powers of two, not aperiodicity) and is why the verdict is read on
  the quotient only.
- **Backend quotient (primitive 5) may be weak or missing** in the
  chosen library; an explicit small-side fallback for Phase 6 is
  acceptable (the quotient is small by then) — record it, it does not
  taint the symbolic claims about Phases 1–5.

## 6. Milestones (all TODO — none started)

- **M1** — C1–C3 + E0 closure (cardinalities and depths green on the
  triptych); instrumentation proven out.
- **M2** — C4–C7 full pipeline; conformance gate green on triptych +
  census subset; E1 scatter; E5 first profile.
- **M3** — C8 + E2/E3/E4 (the scaling story — the paper's headline
  measurements); Proposition 4.1 verified at every affordable `n`.
- **M4** — C9 + E7/E8 studies; E6 bottom line; hand the derived-census
  driver to `sos_census_experiments.md` C6 as its at-scale backend.
- **M5** — C10 + E9 (the calculus): commutation and witness gates
  green, the deferred-reduce column measured. Depends on M2 (the
  pipeline) and C8 (aligned pairs at scale); independent of M4's
  sweeps.

Every milestone ends with a report appended to `sos_symbolic_report.md`
(ledger style, one row per finding, predictions checked off or refuted —
a refuted prediction is a paper edit, not a footnote).
