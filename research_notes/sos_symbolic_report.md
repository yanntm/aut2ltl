# SoS Symbolic Engine — results

The answer to `research_notes/sos_symbolic_experiments.md`: the `sos_sdd/`
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
