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
