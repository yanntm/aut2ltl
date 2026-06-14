# aut2ltl — Project TODO

Project-level work items. Engine-level items live in `aut2ltl/kr/TODO.md`.

## RESUME HERE — kr/ CascadeTranslator refactor (2026-06-14)

We are turning `kr/` into a clean OO architecture: a contract floor, self-gating
translator *members*, and a composition combinator. Most of it is done and
pushed (master @ `b7349f5`); the **pipeline sweep is the last piece**.

### Done (pushed)
- `aut2ltl/contract.py`: `ReconResult`, `Translator`, and `CascadeTranslator`
  (Protocol with a fixed `name` — members are named, self-gating callables).
- `aut2ltl/combinators.py`: `first_success([...])` — the chain composite
  (try in order, first OK wins, else decline), generic over the input type.
- kr leaves are now **CascadeTranslator members, one per file**, each self-gating
  (returns a faithful `ReconResult` or declines) and stamping `technique={name}`:
  `kr/acc.py` (Acc/acc, bounded fragment), `kr/buchi.py`, `kr/cobuchi.py`,
  `kr/weak.py`, `kr/bls.py` (general Muller-DNF fallback). Predicates
  `is_{buchi,cobuchi,weak}_cascade` live with their member.
- support: `kr/muller.py::assemble_muller_dnf` (the bls builder);
  `kr/reachability_operators.py` + `kr/fin.py` (the 5 reach formulas + `fin_c`,
  the mutually-recursive core); `reset_build_state` lives there now.
- `kr/cascade/` is a **package**: `model.py` (Cascade), `config_graph.py`
  (analysis + relocated `good_muller_sets`), `__init__.py` re-exports.
- tests: `tests/test_contract_combinators.py`, `tests/kr/test_acc_translator.py`.

### Next steps (the pipeline sweep — `reachability.py` is the last hand-rolled bit)
1. **Collapse the ladder.** Replace `reachability.py::reconstruct_ltl_paper_style`
   (the hand-rolled acc→weak→buchi→cobuchi→bls `if`-ladder) with
   `first_success([acc, weak, buchi, cobuchi, bls])` over the member instances.
   ⚠️ **CAVEAT — do not lose this:** each stage needs a *specific* automaton form,
   and determinization does not reverse, so the per-stage form recovery (the
   `postprocess(.,"generic")` inside the cobuchi/weak predicates, and
   `decompose_aut`'s normalized parity `D` kept as authoritative `original_aut`)
   must be preserved. It currently lives *inside* each member, so it should travel
   with them — but VERIFY the orchestrator/ladder does nothing form-specific
   before collapsing it. (Per-member gates `KR_DISPATCH_{ACC,WEAK,BUCHI,COBUCHI}`
   must survive: build the list conditionally.)
2. **Kill the naming misnomers.** Rename `reconstruct_ltl_paper_style` →
   `reconstruct_cascade` (the cascade-level peer of portfolio's
   `reconstruct_decomposed`). Delete `reconstruct_bls` (it is the *pipeline*
   wrapper + depth guard, NOT the `bls` leaf — confusing) and `build_phi` (dead;
   only `"muller"` worked). Repoint the ~7 callers of `reconstruct_bls(casc)` →
   `reconstruct_cascade(casc).formula`: survey_mp_cascade.py, survey_sizes.py,
   test_kr_reconstruct.py, test_kr_zoom.py, test_kr_basic.py, probe_acc_dispatch.py,
   probe_buchi_dispatch.py.
3. **GAP adapter.** Build `as_translator(cascade_translator) -> Translator`
   (twa → `decompose_aut` → cascade → member) so the twa-level entry composes;
   it is the bridge from `CascadeTranslator` up to `Translator`.

### Known debt (flagged by user, deferred)
- **Module-global mutable state** in `reachability_operators.py` (counters +
  memos; `reset_build_state` is a band-aid) — bad design; move to instance/context.
- `kr/README.old` to delete once the new `kr/README.md` is settled.

### Gates & discipline (do not skip)
- Run BOTH gates **in full** before committing engine changes:
  `python3 tests/kr/test_kr_r4_audit.py` → CLEAN; and
  `python3 tests/kr/survey_mp_cascade.py` with **NO args** (all ~35 formulas) →
  every case `equiv=True`. Passing a subset of formulas SKIPS the gate — don't.
- Commit **locally only** (push only when the user says so this turn). Tests are
  **placed scripts** under `tests/` (no `python -c`). Comments **describe** what
  code does, never refactor history. One file per commit unless it is a logical
  move; the user sometimes asks for file-by-file with per-file messages.

## Other

- **Real CLI** over `reconstruct_decomposed` (current `cli.py` is an sl-only
  stub). See `STATUS.md` "CLI".
- Engine work items: see `aut2ltl/kr/TODO.md`.
- The per-file LOC inventory that used to live here is **stale** after this
  session (cascade→package, gap_bridge→gap/, acceptance_dispatch split into
  acc/buchi/cobuchi/weak/bls, etc.); regenerate on demand.
