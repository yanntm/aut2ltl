# SoS Symbolic Engine — results

The answer to `research_notes/sos_symbolic_spec.md`: the `sos_sdd/`
engine (libDDD multi-valued DDD core behind a Python `SoS` API — backend
decisions recorded in `sos_sdd/README.md`) run against the experiment ids.
Each section answers one milestone; each finding `Fn` is a checked or
refuted prediction, or a mechanism the runs settled.

## M1 — C1–C3 + E0 (closure on the triptych)

Engine state: C1 (five primitives on libDDD + JSONL instrumentation),
C2 (Python guard-cube refinement into letter-behavior classes → numeric
payload; C++ slot space + per-class `Hom_Basic` step homs), C3 (layered
frontier BFS from the identity, layers kept, budgets as findings).
Phases ≥ 2 not started; unimplemented switches are refused, not ignored.

- **F1 — E0 cardinalities green, dual-verified.** `|EM¹|` = **10 / 7 / 16**
  on `gf_aa_parity` / `even` / `evenblocks` (identity included), matching
  the spec constants *and* an in-test explicit-BFS ground truth on every
  per-layer cardinality, not just totals. Depths 4 / 3 / 5; layer
  profiles `1,2,3,3,1` / `1,2,3,1` / `1,2,3,4,4,2`
  (`tests/sos_sdd/e0_triptych.py`, streams in `tests/sos_sdd/logs/`).
- **F2 — the §3.1 compression figure has its number.** The closed `EM¹`
  of `EvenBlocks` holds in **10 diagram nodes** against the 32 explicit
  slot cells (prediction: strictly below — confirmed with margin;
  `gf_aa_parity` needs 5 nodes for its 20 cells).
- **F3 — the letter coupling needs no α variables.** C2 refines the
  digest's guard cubes into **behavior classes** (two letters equal iff
  same (dst, marks) row at every state — the §4.2 "guard-equal letters"
  covariate, operationalized); the step is a union over classes of
  slot-local brick compositions, the alphabet never enumerated and the
  diagram never carrying letter bits. α-bits-as-variables is downgraded
  to a recorded fallback for inputs whose cube refinement explodes.
- **F4 — mechanism note (backend).** DDD-side `apply2k` is single-variable;
  relations-as-2k-diagrams was dropped for `Hom_Basic` brick sums (spec
  §2.2 primitive 3 realized as homomorphisms). The Phase 2 indexed read
  (`Comp`) is pinned on libITS-gal `ExprHom` (CAV 2012), a dependency that
  joins only at Phase 2 — deps are self-contained under `sos_sdd/deps/`
  (`install_deps.sh`).

M1 exit: instrumentation proven out (per-round `op`/`layer` records,
config echo, budget findings carrying the layer profile). Gate green.

## Comp-free advance (C7 mechanism + C8/E2 first points)

Engine state added: shortlex extraction over the kept layers (C7's
pinned mechanism — backward can-reach sets, forward least-class walk);
heterogeneous slot spaces (per-slot domains, packing entirely
Python-side in `slotmodel.py`); C8 async generators in both coordinate
systems. Phase 2 (`Comp`/ExprHom) still not started.

- **F5 — shortlex extraction exact.** Engine words equal a
  shortlex-ordered-BFS ground truth on **every** element of the triptych
  (33/33), longest word = closure depth on each instance
  (`tests/sos_sdd/shortlex_test.py`).
- **F6 — E2's factored line, measured early.** `EvenBlocks^{⊗n}`,
  factored coordinates: `|EM¹| = 16ⁿ` by model count at every `n ≤ 6`,
  Proposition 4.1's isomorphism **element-exact** through `n = 4`
  (65 536 elements), and the diagram is *literally additive*: **9n+1
  nodes** (10/19/28/37/46/55), all points under 60 ms. Prediction
  "`O(n · component)`" confirmed as equality, not just order.
- **F7 — the flat wall is where Lemma 4.2 says it is.** Flat coordinates:
  `n = 2` needs 258 nodes against factored's 19; `n = 3` exhausts an 8 s
  per-point budget at layer 9 (card 646, 2954 nodes — profile in
  `tests/sos_sdd/logs/e2_flat_3.jsonl`). Recorded as the `TIME_BUDGET`
  finding it is; the proper divergence plot is E3's, with C9's order
  sweep still to come.

## C4 — the crossing (Phase 2: pairing lfp; squaring deferred)

Engine state added: the pair space (y-block stacked above the x-block),
`Comp` as the paper's `|Q|`-way case split over plain scalar GAL
expressions (`assignExpr`/`predicate` of libITS-gal — no arrays, no
`syncAssignExpr`), the pairing lfp from the diagonal and the idempotence
predicate; `until_phase=2` live. The squaring shortcut is deferred
(simultaneous step — pending a 2k-variable relation encoding);
`square="check"/"on"` are refused, never ignored.

- **F8 — π element-exact everywhere tried.** Engine `{(x, x^π)}` equals
  an explicit power-orbit ground truth on **every** element of every
  case: triptych 10/7/16, a period-3 cycle (6 elements, 5 pairing
  rounds — the orbit shape squaring could never carry), and
  `EvenBlocks^{⊗2}` factored (256 elements, the case split crossing
  component block offsets). π functional (|π| = |EM¹|) on all — the
  built-in Prop 3.2 check (`tests/sos_sdd/phase2_test.py`, streams in
  `tests/sos_sdd/logs/phase2_*.jsonl`).
- **F9 — mechanism note: the variable orientation was load-bearing.**
  Phase 1's `Hom_Basic` bricks key on variable numbers only and silently
  tolerated diagrams built upside-down (variable 0 topmost); ExprHom
  navigates the order and the first crossing attempt died in unbounded
  mutual recursion. Convention now fixed engine-wide: variable 0
  adjacent to the terminal, written block above read block so
  data-dependent reads resolve downward through the query mechanism.
  Arrays (`x[i]` cells + `createArrayAccess`) were dropped with the
  author's direction — the space is fixed-size, scalars + the case
  split are the spec'd rendering (the paper's `Comp` formula verbatim).

## C5 — profiles and residuals (Phases 3–4)

Engine state added: the digest's acceptance formula grounded Python-side
into per-slot accepting-mask tables (`sos_sdd/accept.py`; numbers in the
payload, never formula text — the `PackInfo` pattern); Phase 3 profile
columns `S_q = predicate(A_q)(π)` — one case-split slot read + mask
membership per global state, **no orbit walk and no cycle detection
anywhere in the path** (the C5 invariant); the seed by O(1) canonical
comparison of the columns (two states agree on every element iff their
columns are the same node — no per-pair quantification); Phase 4 as
Moore refinement over the explicit global states (mixed-radix over the
component blocks). `until_phase=4` is the new ceiling
(`src/residuals.hh`; gate `tests/sos_sdd/residuals_test.py`, streams in
`tests/sos_sdd/logs/residuals_*.jsonl`).

- **F10 — profiles element-exact everywhere tried.** Every verdict bit
  `A(q, x)` read off the symbolic columns equals a cycle-walk ground
  truth (the explicit algorithm the engine must avoid) on every
  element × state of every case: triptych, mod3, dupe, stem,
  `EvenBlocks^{⊗2}` factored (multi-block global states crossing
  `block_base`).
- **F11 — the residual partition is the gfp, and the seed alone is
  not.** Engine `≃` equals an explicitly-unwound lockstep gfp on all
  seven cases; the `stem` case pins why Phase 4 exists: `L(0) =
  a(!a)^ω` is nonempty yet every pure-loop verdict `A(0, x)` is 0, so
  the profile columns merge `{0,1,3}` (`distinct_columns=2`) and only
  the letter-step refinement splits state 0 off (`rounds=2`, classes
  `{0} | {1,3} | {2}`). On the other six cases the seed already is the
  gfp (`rounds=1`).
- **Recorded gap:** the spec's cross-check against the explicit tool's
  residual classes (`sosl` rides Spot's `language_map` on HOA inputs)
  waits on E1's HOA→digest bridge; the gate's ground truth is the same
  gfp computed by a deliberately different explicit algorithm
  (cycle-walk verdicts + lockstep refinement).

## C6 — the congruence (Phase 5)

Engine state added: symbolic partition refinement on the pair space
with the y-block erased to zero (`setVarConst` sweep — the Phase 3
columns project onto the closure's space); seed by the erased profile
columns (~ω) and residual-class slot selections (~lin, over the global
states); gfp by letter-class *preimage* splits using the closure's
per-class reverse homs. The rotation-lemma invariant is structural:
`src/congruence.hh` is pure `Hom_Basic` and never includes the ExprHom
machinery — no `Comp`-shaped relation can appear inside the fixpoint.
`until_phase=5` is the new ceiling; `fp5≠"layered"` is now checked and
refused (gate `tests/sos_sdd/congruence_test.py`, streams in
`tests/sos_sdd/logs/congruence_*.jsonl`).

- **F12 — the syntactic partition is exact everywhere tried.** Engine
  `EM¹/~` equals an explicit right-translation-refinement ground truth
  (sosl-style, seeded by cycle-walk verdict + residual signatures) on
  all seven cases — element-for-element, not just counts:
  `gf_aa_parity` 10→6, `even` 7→5, `evenblocks` 16→7 (the identity
  class absorbs `⟦aa⟧`, [SωS26, Table 2(c)]), `mod3` 6→2, `dupe` 4→2,
  `stem` 7→4, `EvenBlocks^{⊗2}` factored 256→37. The `gf_aa_parity`
  count of 6 also matches the explicit tool's `gfaa` fixture
  (`sosl/tests/sos/logs/_core_gfaa.sos`, `classes: 6`) — a cross-tool
  corroboration ahead of C7's byte gate.
- **F13 — compression note.** The 256-element factored product
  quotients to 37 classes with the whole refinement running on DDD
  blocks (the partition never exists as an explicit element list on
  the engine side); the largest class (156 elements) is one diagram
  block throughout.

## C7 — quotient and `.sos` emission (Phase 6, the conformance gate)

Engine state added: `sos_sdd/quotient.py` — the `quotient="explicit"`
route (the recorded small-side fallback; `"symbolic"` refused): word
classes over non-empty-word images with `[eps]` adjoined fresh, mult by
folding packed representative values (never `Comp`), saturated accept
pairs with verdicts off the Phase 3 profile rows at the initial state,
ids/keys by shortlex BFS over the small quotient algebra (mirroring the
reference's `canonical.shortlex_bfs`). `Engine.build(..., until_phase=6)`
returns the Phase 6 object; `to_sos()` emits the core sections in the
reference serializer's exact layout (gate
`tests/sos_sdd/conformance_test.py`; probe
`tests/sos_sdd/conformance_diff.py`).

- **F14 — the conformance gate is green.** The emitted `.sos` is
  **byte-identical** to the reference construction's
  (`sosl.sos.build.reference_of_hoa` → `dump_invariant`, Spot-backed)
  on every same-AP instance tried: `gf_aa_parity` (6 classes), `even`
  (5), `evenblocks` (8), `mod3` (3), `stem` (4).
- **F15 — the identity convention was the one real divergence.** The
  first cut quotiented EM¹ wholesale and came out one class short
  wherever a non-empty word folds onto the identity element (`mod3`:
  `⟦!a⟧ = 1` merged `[!a]` into `[eps]`, 2 classes vs the reference's
  3; `evenblocks`: 7 vs 8). The reference's convention is normative
  and now mirrored: the congruence runs on all of EM¹ (Phase 5
  unchanged), but word classes are read off the non-empty-word images
  and `[eps]` is a fresh class no word can collide with.
- **Recorded exclusion (AP support).** For languages where Spot's
  import postprocess drops unused APs (e.g. the empty language of
  `dupe`), the reference answers a different-AP presentation and byte
  parity is out of scope by the format's own same-AP equality clause —
  asserted as such in the gate. Products are refused at Phase 6
  (`.sos` for product digests is not defined yet).

## C4 completion — the squaring shortcut (2k relation encoding)

Engine state added: `src/squaring.hh` implementing the recorded design
(`sos_sdd/README.md`, settled with the libDDD author): the squaring map
materialized once as an interleaved relation `R = {(z ⧉ z·z)}` (dupe
gadget with collision-free numbering; the Comp case split reading only
pre variables — hazard-free by construction), iterated by an
`Apply2k`-pattern relational-product homomorphism over the crossing's
pair space, capped at `⌈log₂|EM¹|⌉ + 1` rounds. All three `square`
modes live; unknown modes refused.

- **F16 — the C4 check gate is green, and the termination theorem
  behaves.** Under `square="check"`, every R row equals the explicit
  packed composition and the converged shortcut equals the pairing π
  (the engine's own O(1) comparison — a disagreement would be
  StopTheLine) on: the triptych, `MOD2`, `EvenBlocks^{⊗2}` factored —
  each converging in **2 squaring rounds** against pairing's 2–5.
  `mod3` (orbit period 3) diverges at the cap exactly as the theorem
  predicts — recorded finding, pairing π stands — and `square="on"`
  raises StopTheLine on it; `MOD2` (period 2) converges despite
  periodicity, pinning "detects powers of two, not aperiodicity" as
  observed behavior. `square="on"` skips the pairing lfp entirely on
  the converging cases and its π is element-identical.

## E1 — the census sweep (conformance at scale + the compression scatter)

Engine state added: `sos_sdd/hoa.py` — `digest_twa`, the C2 parser
half: a Spot `twa_graph` becomes the digest verbatim (isop guard cubes,
acceptance text as-is; non-D-form refused loudly); obtaining and
normalizing the graph stays with the standard APIs (`spot.automaton`,
`sosl.sos.build.canonical`). Placed driver `tests/sos_sdd/e1_census.py`:
full pipeline (`square="off"`) per instance under a 10 s engine budget,
one CSV row + one stats JSONL per instance, `--shard k/N` for cluster
fan-out, `--isolate` for in-machine sweeps. Bridge gate
`tests/sos_sdd/hoa_bridge_test.py` (round-trip byte-parity on
triptych/mod3/stem; corpus byte-parity incl. marks=0, parity acceptance,
complement entries). Data: `tests/sos_sdd/reference/e1_census.csv`
(tracked — the paper's scatter source), regenerated by
`e1_census.py --all --isolate`.

- **F17 — the conformance gate is green at corpus scale.** All 6222
  `genaut/corpus/flat_canon` instances swept; **6102 completed, every
  single one byte-identical** to the precomputed corpus reference
  (`flat_canon/sos/<name>.sos` — the det/sos tiers are a self-consistent
  pair, so the gate needs no reference runs). Zero MISMATCH. The C7
  gate's instance set widens from 5 instances to 6102 — that recorded
  gap is closed.
- **F18 — the compression prediction holds on essentially all rows.**
  `nodes_final ≤ |EM¹|·|Q|` explicit cells on **6100/6102** completed
  instances; the two exceptions are the 1-element algebras
  (`1state1ap0acc_0/_3`: 1 cell against the 2-node DDD root+terminal
  floor) — a floor effect, not a compression failure. Largest completed
  algebra: `|EM¹| = 12 225` (`2state2ap2acc_parity_…_c`). Total engine
  time over the 6102: 1 647 s. Scatter and §4.2 covariate correlates:
  the CSV carries states/APs/marks/letter-classes; constant/shared
  slots and mark upward-closure are **not yet wired** (recorded gap).
- **F19 — the honest wall, profiled.** 120 instances (1.9 %) blow the
  10 s budget, concentrated exactly where the spec predicts: 101/120 in
  `3state2ap2acc_parity` (the largest sampled shape), the rest in its
  neighbors. Phase profile of the kills: Phase 1 ×52, Phase 3 ×32,
  Phase 5 ×21, Phase 2 ×15 — Phases 3 and 5 firing at all is a datum
  against E5's "Phases 5–6 are cheap" prediction, to revisit when E5
  profiles properly. Note for E6's bottom line: the explicit reference
  *completed* all 120 (their corpus `.sos` exists), so at this budget
  the census's second half ("loses nowhere on the census") is not
  looking good — E6 must measure both columns honestly.
- **F20 — operational constraint, learned the hard way.** A one-process
  corpus sweep OOMs (near machine crash): libDDD's unique table is
  never GC'd, so diagrams accumulate across instances. Recorded rule:
  corpus-scale sweeps run **process-isolated** — locally via
  `--isolate` (per-instance subprocess under `aut2ltl.bounded`'s
  `timeout --signal=INT --kill-after=1`; the SIGKILL is unconditional,
  the C++ core observes no signals) or as a cluster fan-out
  (`--shard k/N`, ~300 jobs). This run: the engine's own `TimeBudget`
  landed every finding, zero hard-KILLED rows.

- **F21 — the C5 cross-check gap is closed.** The engine's Phase 4
  partition equals `spot.language_map`'s (the explicit tool's
  `residual_classes`, run on the RAW parsed graph so state numbering is
  the digest's) on the classic six (triptych, mod3, dupe, stem) and a
  deterministic 25-instance corpus spread — 30 matched, 1
  budget-skipped, 0 diverged (`tests/sos_sdd/residual_crosscheck.py`;
  the full-corpus version can ride a cluster fan-out if wanted).
- **F22 — the §4.2 covariates, measured (and |EM¹| corroborated a
  third way).** `tests/sos_sdd/e1_covariates.py` closes EM¹ explicitly
  in Python (no engine) per completed instance and records: constant
  slots (singleton value set), `distinct_cells` (per-slot value-set
  sizes summed — the sharing source), and mark upward-closure per
  (slot, dst) family. Its element count equals the census `em1` on
  **all 6102 instances** — an independent corroboration of the model
  count. Aggregates (`tests/sos_sdd/reference/e1_covariates.csv`):
  constant slots present on 3092/6102 instances; mean
  `distinct_cells / (|EM¹|·|Q|)` ≈ **0.039** (per-slot sharing alone
  collapses the explicit table to ~4 %); **62 %** of mark families
  upward-closed. ⟨To Theory: the paper's §4.2 leaves the
  monotone-marks metric as "quantify on the corpus" — the
  operationalization here (per-(slot,dst) family, closure under adding
  one mark, fraction over non-empty families) needs blessing or
  adjustment before the paper cites the 62 %.⟩

E1's scope is now fully closed. Scatter correlate analysis (which
covariate predicts compression) is a reading of the two reference CSVs,
left for the paper integration.

## Theory responses — the E1 escalations (2026-07-11)

- **F23 — the E1 read-offs** (Theory-run; regen
  `python3 tests/sos_sdd/e1_readoff.py` — joins the two tracked
  reference CSVs, no engine runs; engineering to adopt the script).
  - *Upward-closure, stratified* by the name's acc token:
    0acc 41150/70983 = **58.0 %**, 1acc **71.6 %**, 2acc **62.8 %**,
    3acc 15/21; pooled **62.2 %**, pooled over acc>0 **64.9 %**.
    Note to engineering: the census `marks` column disagrees with the
    name token (all 2733 0acc instances carry `marks=1`; 1acc spreads
    over `marks ∈ {1,2,3}`) — explain the discrepancy (Spot import
    normalization?) and re-stratify by the digest's `|C|` (one-line
    groupby change in the script).
  - *Compression correlates* (`ratio = nodes_final / cells`; quantiles
    p5/median/p95 = **0.12 / 0.29 / 0.50**, max 2.0 = the two floor
    rows). Spearman vs ratio: sharing (`distinct_cells/cells`)
    **+0.73** (dominant), `|EM¹|` −0.66, depth −0.59, marks −0.51,
    letter classes −0.41, states −0.30, upward-closed fraction
    **+0.19** (weak, unfavorable sign — floor-confounded),
    const. slots +0.16. Reading: per-slot sharing predicts
    compression; bigger, more-marked algebras compress relatively
    better; upward-closure is a structure datum, not a predictor.
  - *Pre-quotient closure depth* (the §5 ⟨TBD⟩): median **6**, p90 11,
    p99 16, max **27** (at `|EM¹| = 3291`); `depth/|EM¹|` ≤ 0.6
    always, 0.22 at the median; depth ≤ the *post*-quotient class
    count on **98.6 %** of rows.

- **F22 response — blessed, with the lemma that grounds it and two
  adjustments.** The operationalization is right: closure under adding
  one mark is *equivalent* to upward closure in `2^C`, and fibering
  per `(slot, dst)` is the correct family (marks co-vary with the
  destination). What monotonicity actually proves is weaker than the
  paper's old sentence and now stands in §4.2 as the stabilizer-closure
  fact: `F(q,d)` is closed under union with the mark sets of `d`'s
  stabilizers `M(d) = {mk_y(d) : st_y(d) = d}` (immediate from the
  composition law), hence a union of up-sets in the lattice `M(d)`
  generates; *full* upward closure holds exactly when stabilizer marks
  realize every single-mark increment — the 62 % measures that
  frontier. Adjustments: (1) cite stratified — the paper carries 62 %
  pooled / 65 % on marked instances, strata in F23; (2) the metric is
  a structure datum, not a compression predictor (ρ = +0.19 vs
  sharing's +0.73) — the paper says so explicitly.

- **F19 response, E5 half — the kill histogram is right-censored; the
  Phase 3 signal is real and now priced.** "Died in phase p" charges
  an unknown upstream spend to p's bucket: the histogram is a survival
  statistic, not a cost profile, and cannot edit §5's table by itself.
  It *does* prove Phases 3 and 5 are macroscopic on tail instances (a
  phase catches deaths in proportion to the time it occupies near the
  budget). The structural cause was in the design all along: Phase 3's
  verdict read is value-indexed (read `st` at slot `q`, then the marks
  at the slot so named) — the §4.1 third-row shape, a `|Q|`-way case
  split applied to the π pair space, the largest diagram in the
  pipeline; one round, never iterated, but crossing-priced per
  application. §5 row 3 and the E5 prediction are revised accordingly
  (spec): peaks expected at Phase 2 (building π) and Phase 3
  (consuming it), Phase 1 where closure itself is the wall, Phases
  4/6 cheap, Phase 5 intermediate. Protocol in the spec: parse the
  retained census JSONLs if kept; rerun the 120 kills at bigger
  budgets for uncensored tail profiles.

- **F19 response, E6 half — the 120 completions are not budget
  parity.** The corpus `sos/` tier was generated under the corpus
  generator's own budget on its own runs — it witnesses completion,
  not completion-within-10 s. E6's protocol is now pinned in the spec:
  same machine, same per-instance wall budget, both tools, two budget
  points, all failure kinds reported on both sides. Pre-registered
  expectations: at 10 s the engine's census loss column is non-empty
  (the 120 are the candidates) and shrinks sharply at 60 s; the census
  (`|Q| ≤ 3`, enumerated, `|EM¹| ≤ 12 225`) is the unstructured world
  where §4.3 predicts no engine win — the bottom line's win column
  lives on the scaling families and shapes the census does not sample.
  "Loses nowhere on the census" was flagged low-confidence and is
  expected to be *refuted* at small budgets; the refutation is a paper
  edit (the honest two-column table), not a bug.
