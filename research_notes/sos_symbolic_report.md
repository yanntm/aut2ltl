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
