# Handoff — sos_sdd symbolic engine thread

You are the **symbolic engine thread** (sos_sdd). Bootstrap: this file,
then `CLAUDE.md` (discipline — binding), then the files below in order.
This file carries **current state + next work items + pointers only**.

## Critical files (read in this order)

1. `sos_sdd/README.md` — the IO contract (Python API, stats stream,
   failure taxonomy) and **every recorded backend decision** — binding.
   Includes the C4 squaring design section (settled with the user over
   a full chat iteration — do NOT re-derive or second-guess it).
2. `research_notes/sos_symbolic_spec.md` — the experiment spec
   (C1–C10 components, E0–E9 experiments, M1–M5 milestones); its
   *State of play* block is current and short.
3. `research_notes/sos_symbolic_report.md` — the **active ledger**:
   new findings land here, numbered from **F27**.
4. `research_notes/sos_symbolic_experiments.md` — the **frozen
   archive**: closed findings F1–F26 (M1 through C10 §6.2, E0–E1,
   Theory responses) + retired spec text. Reference it; never edit it.
5. `research_notes/sos_symbolic.md` — the paper, organized around
   **five research questions** (RQ1 correctness / RQ2 compression /
   RQ3 the exponential / RQ4 cost / RQ5 amortization; RQ↔E-id mapping
   in the spec's State of play). §8 answers RQ-by-RQ with tables;
   Appendix A is the parking lot for cut prose. Exactly **1 `⟨TBD⟩`
   remains** (§3 Phase 1, saturation — waits on E8). Every §8 number
   must be traceable to an archive/report finding or a tracked CSV.

- Code: Python façade `sos_sdd/*.py`; C++ core `sos_sdd/src/*.hh` +
  `module.cpp` (pybind11 `sos_sdd._core`). Tests + logs under
  `tests/sos_sdd/`.

## Build and test

- Build: `cd sos_sdd && cmake -B build && cmake --build build` (drops
  `_core*.so` in-package; links `deps/lib/libITS.a` BEFORE
  `libDDD.a`). `sos_sdd/deps/` is untracked; if missing, run
  `sos_sdd/install_deps.sh`.
- Every test: `timeout 15 python3 tests/sos_sdd/<file>.py <case>` from
  the repo root — one case per invocation (each file's `CASES` dict
  lists them; no argv = all cases). All green as of this handoff:
  `smoke_api`, `smoke_core`, `letters_test`, `e0_triptych`,
  `shortlex_test`, `e2_async`, `phase2_test`, `squaring_test`,
  `residuals_test`, `congruence_test`, `conformance_test`
  (+ `conformance_diff.py` probe), `hoa_bridge_test`, `slotperm_test`,
  `member_test`, `boolean_test`. Logs → `tests/sos_sdd/logs/`,
  never /tmp.
- **Sweeps are NEVER one process** (OOM'd once, near machine crash:
  libDDD's unique table is never GC'd, diagrams accumulate across
  instances). `e1_census.py --isolate` = per-instance subprocess under
  `aut2ltl.bounded` (unconditional SIGKILL backstop — the C++ core
  observes no signals), CSV-resume built in; `--shard k/N` = cluster
  fan-out (~300 jobs, per-shard CSV). The user wants corpus-scale
  sweeps on the cluster, not the local machine.

## Current state (all committed, all gates green)

The full pipeline works end to end and is **byte-identical to the
explicit reference at corpus scale** (6102/6102 completed census
instances). C1–C7 done; C9's `slot_perm` done; C10 §6.1 (membership)
and §6.2 (Boolean algebra) done with commutation gates green. E0 and
E1 closed; E2's factored line measured to `n = 6`. Details and every
closed finding: the archive (file 4 above). Refused loudly, never
ignored: `quotient="symbolic"`, products at Phase 6, non-sorted APs,
`fp1`/`fp5` ≠ "layered", non-natural `slot_perm`, non-packed
`slot_encoding`, unknown `square` values, ambiguous word cubes in
membership.

## Work items — engineering (in order)

1. ⏳ **C10 remainder** (paper §6 is the spec; E9's gates are the
   deliverable). Remaining, in dependency order:
   - **Alignment (§6.3), design settled and now normative in the
     spec's C10 bullet:** the ordinary build over the **sync-product
     slot model** (shared-AP letter-class refinement — E4's generator,
     `Product mode="sync"` in `slotmodel.py`); no per-block π assembly
     (README records why; measured optimization to revisit only if E9
     prices aligned re-pairing as dominant). Prop 6.1 validated end to
     end via readings + byte gates.
   - **§6.4 queries:** `S` projection, `Bad` intersection,
     included/equiv/empty; **witness** = C7's extraction retargeted
     at a set (backward preimages + forward least-letter walk).
   - **§6.5:** rooting = move ι (re-parameterization); inverse
     substitution = composed letter maps + re-closure (automatically
     inside EM¹ — generators are old elements).
   - **E9 remainder:** witness gate vs brute-force lasso enumeration;
     deferred-reduce priced; per-op stats for derived/forked runs
     (recorded gap — derived runs stream no stats yet).
2. ⏳ **C9 remainder** — fp disciplines (`fp1`/`fp5` `chaining` /
   `saturation` — E8's axis; a non-layered Phase 1 must run a costed
   length-reconstruction pass for shortlex), split slot encodings
   (`split-sm` / `split-il` — E7's axis).
3. ⏳ **E2's second component family** + per-point budget sweeps at
   scale; E3 order sweeps (unblocked — `slot_perm` is live).
4. **E5/E6 per the spec protocols (read them before running):**
   E5a = parse the retained census stats JSONLs
   (per-phase time/peak nodes on the 6102 completed; if not retained,
   stratified ~200 rerun); E5b = the 120 TIME_BUDGET rows at 60 s /
   300 s on the cluster (feeds E6). E6 = budget parity: rerun the
   *explicit reference* under the same caps — the corpus `sos/` tier
   is NOT the explicit column. Kill-phase histograms are
   right-censored; never present one as a cost profile.
5. Optional, cluster-sized: full-corpus C5 cross-check (sample of 25
   done).
6. Housekeeping when touched: new findings → report (from F27) AND
   sync the spec's *State of play*; paper only when a `⟨TBD⟩` becomes
   measurable or an §8 open cell gains data; retire the report to the
   archive when a campaign closes.

## Work items — theory

1. **Quotient-scaling decision** (the RQ4 named gap): no experiment
   grows the quotient (census max 148 classes; product quotients stay
   small). Decide whether the paper's claims stay bounded as stated
   or the spec gains a quotient-scaling family / census-extension
   axis — and if so, specify it (expected class growth, budgets,
   whether the explicit Phase 6 fallback needs pricing at ~10³
   classes).
2. **Integrate incoming results** into §8's open cells as they land
   (E5 profile → RQ4; E6 bottom line → RQ4; E3/E7 orders → RQ3; E9 →
   RQ5; E8 resolves the paper's last `⟨TBD⟩`). A refuted prediction
   is a paper edit, not a footnote.
3. **Conjecture 4.3** (any-order lower bound) remains open math —
   entangled-slot candidate families welcome; E3 can only probe it.

## To-theory (escalations awaiting a Theory session)

None. (The C10 alignment reword is folded into the spec; the archive
F26 block records the resolution.)

## Binding engine facts (learned the hard way — do not relearn)

- **The user is the author of libDDD/libITS.** When the library API is
  tricky, STOP and bring him the problem with your analysis — do not
  blindly debug. He explicitly asked for this.
- **Variable 0 is adjacent to the terminal**; slot i = var i, higher
  vars on top. ExprHom dies in unbounded mutual recursion on inverted
  diagrams (archive F9); `Hom_Basic` bricks tolerate them silently — do
  not let that mask the bug. Pair spaces stack written block ABOVE read
  block.
- **No GAL arrays, no `syncAssignExpr`** — plain scalars + the paper's
  case split; the simultaneous step (squaring) is the 2k relation
  encoding (README design section). The transparent `DoubleVars`
  doubling (`~/git/libITS/bin/ToTransRel.cpp`) suits GAL's sequential
  semantics only — REJECTED for Comp (reads need old values; colliding
  var numbers defeat any GalOrder). `assignExpr` handles rhs support
  above and below the lhs (author-confirmed).
- Anything crossing an engine step is held as **`DDD`/`Hom`**, never
  bare `GDDD`/`GHom` (GC sweeps unreferenced nodes); never trigger GC.
  A hom carrying a diagram overrides `mark()` (see `ApplyRel`).
- DDD edge values are `short`: domains ≤ 32767 (`slotspace.hh`; same
  guard on the explicit global-state space in `residuals.hh`).
- **All packing semantics live in `slotmodel.py`** and travel as
  numbers (`PackInfo`, accept-mask tables) — never as convention.
- Letters are never enumerated: letter-behavior classes
  (`letters.py`). Canonical keying per `sosl/sosl/sos/io/
  sos_format.md`; byte parity is against `sosl/sosl/sos/io/
  serialize.py`'s actual layout.
- **Identity convention (C7, normative):** word classes = ~-classes of
  non-empty-word images; `[eps]` adjoined fresh. Phase 5's congruence
  itself runs on all of EM¹ — only the quotient reading changes
  (archive F15).
- **AP-support exclusion:** Spot's import drops unused APs (e.g. empty
  language) — such instances sit outside the same-AP byte-parity set
  (`conformance_test` `dupe` case asserts it).
- Assertions of the spec are structural where possible: no orbit walks
  in Phases 3–4 (`residuals.hh`), no ExprHom include in `congruence.hh`
  (the rotation lemma as an include list), squaring divergence decided
  by the round cap, membership closure-free (`calculus.py` never
  imports `_core`).

## Concurrent editors — stay in your sphere

Other live sessions share this checkout (sosl learner / calculus /
toltl / cascade / genaut corpus). Therefore:
- **Stage explicit paths only** (`git add <your files>`); the index
  may hold others' changes at any moment. Never touch their files, no
  history/diff reading outside sos_sdd / sos_symbolic files.
- Commit messages via `git commit -F -` with a quoted heredoc, terse;
  several own files in one commit is fine. Never rebase/amend. Push
  only with the user's explicit OK, asked every time.

## Working rules (beyond CLAUDE.md)

Budgets/timeouts are findings, not errors — report them with the layer
profile (it survives in the stats stream). Spot is bounded-or-skipped
(per-case timeout), used only via the reference tool in gates. Present
intermediate results; do not start a new direction without user
validation. No touching root files (STATUS/TODO/CLAUDE.md) nor
`docs/HISTORY.md`. This handoff is tracked but disposable —
re-curate it after every landed milestone and regenerate at session
end (crash protection).
