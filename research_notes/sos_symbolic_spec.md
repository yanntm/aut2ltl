# SoS Symbolic Engine — Experimentation Specification

**Status:** specification / declaration of intent. This document is the
interface between the paper (`sos_symbolic.md`) and the implementation
sessions: the paper's §8 evaluation plan and its ⟨TBD⟩ measurements are
fed by the experiment ids below, per the family discipline
(`sos_learning_report.md` ledger style).
Companion specs: `sos_census_spec.md` (the measurement corpus and
the derived-census driver, the engine's first consumer at scale),
`sos_toltl_spec.md` (downstream consumer of the emitted quotient).

**State of play** (details of closed work:
`sos_symbolic_experiments.md`, the frozen archive, findings F1–F26;
new findings land in `sos_symbolic_report.md` from F27).

- **Engine complete through Phase 6** (`sos_sdd/`, libDDD): C1–C7
  done, C9's `slot_perm` done, C10 §6.1–§6.2 done; the conformance
  byte-gate is green at corpus scale (6102/6102). **E0 and E1 are
  closed**; E2's factored line is measured to `n = 6` (second
  component family still owed).
- **Paper**: restructured around five research questions; §8 answers
  them with tables; one `⟨TBD⟩` left (§3 Phase 1 saturation — E8).
  Mapping: **RQ1 ← E0/E1**, **RQ2 ← E1**, **RQ3 ← E2/E3/E4/E7**,
  **RQ4 ← E5/E6 (+E8)**, **RQ5 ← E9**. Named gap the mapping
  exposes: no experiment grows the *quotient* (census max 148
  classes) — a quotient-scaling family or census-extension axis is
  an open question for a future revision of this spec.
- **Open**: C9 remainder (fp disciplines, split encodings), C10
  remainder (§6.3–§6.5 + E9), E2's second family and per-point
  budget sweeps, E3–E8, milestones M3–M5.

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
  once `sos_census_spec.md` M3 lands — the compression scatter's
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

**C1–C8 are DONE** — implementations and every rendering decision:
`sos_sdd/README.md` (binding); gates and findings: the archive; full
original definitions: archive, "Retired component definitions". One
line each:

- **C1 — engine bindings.** Five primitives + instrumentation hooks
  (per-op nodes, rounds, per-phase wall time — the JSONL stream every
  experiment reads).
- **C2 — symbolic input builder (Phase 0).** HOA → `Δ`/`Mk` → slot
  domain `V = Q × 2^C`, `Lett`/`R` slot-local, alphabet never
  enumerated (letter-behavior classes).
- **C3 — closure (Phase 1).** Layered lfp, layers *kept* (shortlex +
  extraction path); the explicit cap becomes a `DIAGRAM_BUDGET`
  finding with layer profile; `|EM¹|` by model count.
- **C4 — the crossing (Phase 2).** `Comp` case split, pairing lfp for
  π, squaring shortcut as the recorded 2k relation encoding (README
  design section); squaring is a shortcut never a verdict, converges
  iff orbit periods are powers of two.
- **C5 — profiles and residuals (Phases 3–4).** `ProfR` = π-composition
  + one slot-read (no cycle detection — structural); residual gfp on
  `Q × Q`, profile-seeded, oracle-free.
- **C6 — congruence (Phase 5).** `~lin`/`~ω` seed + letter-preimage
  gfp; the rotation lemma as a code invariant (no `Comp` inside the
  fixpoint — structural).
- **C7 — quotient and exports (Phase 6).** Explicit small-side
  quotient (recorded fallback), shortlex keys by BFS over the quotient
  algebra, λ-quotient guards, saturated accepting pairs, `.sos`. Its
  layer-driven extraction (backward preimage sets + *forward*
  least-letter walk) is the mechanism C10's §6.4 witness reuses.
- **C8 — product family generators.** `D^{⊗n}` async + sync variants,
  factored and flat coordinates (the engine's `coords` switch —
  recorded deviation, README); `EvenBlocks^{⊗n}` canonical
  (`|EM| = 16ⁿ`, Prop 4.1).

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
  Phase 1 lfp on the aligned space — i.e. the **ordinary build over
  the sync-product slot model** (E4's generator, `Product
  mode="sync"`). The engine never builds a monolithic `Comp` (Phase 2
  is per-slot case-split bricks), so the requirement "*`Comp` is
  never applied on the aligned space*" holds structurally, with no
  dedicated assembly; Prop 6.1's per-block π assembly is an optional,
  measured optimization — revisit only if E9 prices aligned
  re-pairing as dominant. Prop 6.1 is validated end to end via
  readings and byte gates. ⟨User-settled; supersedes the earlier
  mandated per-block assembly — archive, F26 block.⟩
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

### E0 — sanity on the worked examples (gated M1) — CLOSED

Closed green: `|EM¹|` = 10 / 7 / 16 on the triptych, depths and
byte-parity confirmed, the §3.1 figure measured (10 nodes < 32
cells). Full protocol and findings F1–F2/F14: the archive.

### E1 — the compression scatter (census corpus) — CLOSED

Closed: conformance at corpus scale (6102/6102 byte-identical),
compression prediction confirmed 6100/6102, covariates measured and
blessed, correlates and depth read off. Full protocol, Theory
addendum and findings F17–F23: the archive. Data:
`tests/sos_sdd/reference/e1_census.csv` + `e1_covariates.csv`
(tracked); regen read-offs via `tests/sos_sdd/e1_readoff.py`.

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
columns. **Prediction:** Phase 3's verdict read
is crossing-shaped (a value-indexed slot select against the π pair
space — §5 row 3 of the paper), so the expected peaks are Phase 2
(building π) and Phase 3 (consuming it) on crossing-bound instances,
and Phase 1 where closure itself is the wall; Phases 4 and 6
negligible (the Phase 4 seed is absorbed by canonicity into `|Q|`
predicate applications); Phase 5 intermediate (rounds × letter
classes, slot-local). A different profile is a paper edit (the §5
table's narrative).

**Protocol.** The census kill histogram is
right-censored — "died in phase p" charges unknown upstream spend to
p — and cannot populate the cost table. E5a: parse the retained
per-instance census stats JSONLs (if kept; else a stratified
~200-instance rerun) into per-phase wall time + peak nodes over the
completed 6102, aggregated by shape. E5b: rerun the 120 `TIME_BUDGET`
instances at 60 s and 300 s (cluster, `--isolate`/`--shard`) for
uncensored tail profiles — the same runs feed E6's engine column.

### E6 — the bottom line vs the explicit implementation

Two-column showdown on the corpus + scaling families: instances the
explicit closure cap kills that the engine carries (to `UNVERIFIED` or
verified completion), and the converse (diagram budget blown where
explicit enumeration walks through — expected on unstructured inputs
with incompressible monoids). **Paper deliverable:** the headline —
whether the `|Q|` exponent *moved* from cardinality to diagram width on
structured inputs. **Prediction:** the engine wins on the scaling
families — include the E2/E3 points and record where the explicit
tool caps on `16ⁿ` enumeration (find the crossover `n`). The census
(`|Q| ≤ 3`, enumerated, `|EM¹| ≤ 12 225`) is the unstructured world
where §4.3 predicts no engine win: expect the engine to lose ≲120
census rows at 10 s against ~0 for the explicit tool, the loss column
mostly closing at 60 s — that is the honest census column, not a bug.

**Protocol: budget parity or nothing.** The corpus `sos/` tier is NOT
the explicit column — it was generated under its own budget on its
own runs; rerun the explicit reference under the same caps. Same
machine, same per-instance wall budget for both tools; two budget
points, 10 s and 60 s (tail optionally 300 s); report all cells (per
tool: completions, kills by kind — engine
`TIME_BUDGET`/`DIAGRAM_BUDGET` vs explicit `INCONCLUSIVE`/timeout).
Census extension shapes are the corpus thread's call, not E6's.

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

## 6. Milestones

- **M1 — DONE** (C1–C3 + E0; archive). **M2 — DONE except E5's first
  profile** (C4–C7 pipeline, conformance green, E1 scatter; archive).
- **M3** — C8 + E2/E3/E4 (the scaling story — the paper's headline
  measurements); Proposition 4.1 verified at every affordable `n`.
- **M4** — C9 + E7/E8 studies; E6 bottom line; hand the derived-census
  driver to `sos_census_spec.md` C6 as its at-scale backend.
- **M5** — C10 + E9 (the calculus): commutation and witness gates
  green, the deferred-reduce column measured. Depends on M2 (the
  pipeline) and C8 (aligned pairs at scale); independent of M4's
  sweeps. §6.1–§6.2 gates already green (archive, F25–F26).

Every milestone ends with a report appended to `sos_symbolic_report.md`
(ledger style, one row per finding, predictions checked off or refuted —
a refuted prediction is a paper edit, not a footnote).
