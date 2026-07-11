# Handoff — sos_sdd symbolic engine thread

You are the **symbolic engine thread** (sos_sdd). Bootstrap: this file,
then `CLAUDE.md` (discipline — binding), then the files below in order.
Do NOT read `docs/HISTORY.md`. This file carries **current state + next
work items + pointers only**; the report is the ledger.

## Critical files (read in this order)

1. `sos_sdd/README.md` — the IO contract (Python API, stats stream,
   failure taxonomy) and **every recorded backend decision** — binding.
   Includes the C4 squaring design section (settled with the user over
   a full chat iteration — do NOT re-derive or second-guess it).
2. `research_notes/sos_symbolic_spec.md` — the experiment spec
   (C1–C10 components, E0–E9 experiments, M1–M5 milestones); its
   *State of play* block is current.
3. `research_notes/sos_symbolic_report.md` — the ledger, findings
   F1–F20: every measured/green claim, plus recorded gaps.
4. `research_notes/sos_symbolic.md` — the paper. Engine results are
   integrated (current-state voice, no history); 3 `⟨TBD⟩`s remain,
   all waiting on E-series data. Hard data claims belong in the
   report, never the paper.
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
  `smoke_api`, `smoke_core`, `letters_test`, `e0_triptych` (M1 gate:
  |EM¹|=10/7/16), `shortlex_test`, `e2_async` (16ⁿ, nodes 9n+1; flat
  n=3 = ledgered TIME_BUDGET finding), `phase2_test` (pairing π),
  `squaring_test` (C4 shortcut), `residuals_test` (C5; `stem` = the
  seed≠gfp witness), `congruence_test` (C6; ebeb 256→37),
  `conformance_test` (C7 byte gate, Spot-backed; `conformance_diff.py`
  = side-by-side probe), `hoa_bridge_test` (C2 parser half: round-trip
  + corpus byte-parity). Logs → `tests/sos_sdd/logs/`, never /tmp.
- **Sweeps are NEVER one process** (OOM'd once, near machine crash:
  libDDD's unique table is never GC'd, diagrams accumulate across
  instances). `e1_census.py --isolate` = per-instance subprocess under
  `aut2ltl.bounded` (unconditional SIGKILL backstop — the C++ core
  observes no signals), CSV-resume built in; `--shard k/N` = cluster
  fan-out (~300 jobs, per-shard CSV). The user wants corpus-scale
  sweeps on the cluster, not the local machine.

## Current state (all committed, all gates green)

**The full pipeline works end to end**: `Engine(...).build(aut,
until_phase=6)` runs Phases 0–6; `to_sos()` is **byte-identical to the
explicit reference** on every same-AP instance tried (spec §3
conformance gate — F14). Per component: C1–C3 (primitives, letter
classes, layered closure — layers kept, load-bearing), C4 complete
(pairing π + squaring shortcut, modes `off`/`check`/`on`), C5
(profiles + residuals, `src/residuals.hh`), C6 (congruence,
`src/congruence.hh`), C7 (quotient + `.sos`, `sos_sdd/quotient.py`,
`quotient="explicit"` only), C8 (async product generators, factored +
flat). Refused loudly, never ignored: `quotient="symbolic"`, products
at Phase 6, non-sorted APs, `fp1`/`fp5` ≠ "layered", non-natural
`slot_perm`, non-packed `slot_encoding`, unknown `square` values.

## Work items — engineering (in order)

1. ✅ **E1 fully done** (F17–F22): bridge `sos_sdd/hoa.py`
   (`digest_twa`, verbatim; import via standard APIs), driver
   `tests/sos_sdd/e1_census.py`, covariate pass
   `tests/sos_sdd/e1_covariates.py`, C5 cross-check
   `tests/sos_sdd/residual_crosscheck.py`. Data (tracked):
   `tests/sos_sdd/reference/e1_census.csv` + `e1_covariates.csv`.
   Conformance green on all 6102 completed corpus instances; |EM¹|
   corroborated three ways (model count / explicit BFS / byte gate);
   120 TIME_BUDGET at 10 s (1.9 %, mostly `3state2ap2acc_parity`).
2. ⏳ **C9/C10** — remaining engine switches (fp disciplines `chaining`
   / `saturation`, split slot encodings, slot permutations — E7/E8's
   axes) and the §6 calculus operators (member / Boolean algebra /
   align / included / witness / reduce; the `.sos` residuals trailer
   can ride the witness machinery). Paper §6 is the spec; C10 gates
   compare against Spot-side oracles, bounded.
3. ⏳ **E2's second component family** + per-point budget sweeps at
   scale; E3 order sweeps (needs C9's `slot_perm`).
4. Optional, cluster-sized: re-run the 120 TIME_BUDGET rows at bigger
   budgets (E6 will need the honest two-column data anyway);
   full-corpus C5 cross-check (sample of 25 done).
5. Housekeeping when touched: milestones append ledger rows to the
   report AND sync the spec's *State of play*; paper only when a
   `⟨TBD⟩` becomes measurable.

## To-theory (escalations awaiting a Theory session)

- **F22 — bless the monotone-marks metric.** Paper §4.2 says ⟨TBD:
  quantify on the corpus⟩; engineering operationalized it as
  per-(slot, dst) mark families, closure under adding one mark,
  fraction over non-empty families → **62 %** upward-closed. Adjust or
  bless before the paper cites it.
- **F19 vs E5's prediction.** Census budget kills land in phases
  1/3/5/2 = 52/32/21/15 — Phases 3 and 5 firing contradicts "Phases
  5–6 are cheap relative to closure". E5 profiling will decide; the §5
  cost-table narrative may need an edit.
- **F19 vs E6's prediction.** The explicit reference completed all 120
  instances the engine's 10 s budget killed — "loses nowhere on the
  census" looks refutable at small budgets. E6 must measure both
  columns honestly (budget parity).
- **Paper integration.** E1 data exists for the compression-scatter
  `⟨TBD⟩` (§3.1/§8): F17–F18 + the two reference CSVs; the correlate
  analysis (which covariate predicts compression) is a reading of
  those CSVs, not new runs.

## Binding engine facts (learned the hard way — do not relearn)

- **The user is the author of libDDD/libITS.** When the library API is
  tricky, STOP and bring him the problem with your analysis — do not
  blindly debug. He explicitly asked for this.
- **Variable 0 is adjacent to the terminal**; slot i = var i, higher
  vars on top. ExprHom dies in unbounded mutual recursion on inverted
  diagrams (F9); `Hom_Basic` bricks tolerate them silently — do not
  let that mask the bug. Pair spaces stack written block ABOVE read
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
  itself runs on all of EM¹ — only the quotient reading changes (F15).
- **AP-support exclusion:** Spot's import drops unused APs (e.g. empty
  language) — such instances sit outside the same-AP byte-parity set
  (`conformance_test` `dupe` case asserts it).
- Assertions of the spec are structural where possible: no orbit walks
  in Phases 3–4 (`residuals.hh`), no ExprHom include in `congruence.hh`
  (the rotation lemma as an include list), squaring divergence decided
  by the round cap.

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
`docs/HISTORY.md`. This handoff is untracked and disposable —
re-curate it after every landed milestone and regenerate at session
end (crash protection).
