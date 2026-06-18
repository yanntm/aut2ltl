# aut2ltl — Project TODO

Open project-level items only. Completed campaigns are recorded in `docs/HISTORY.md`
and git history. (The big docs + contract/combinator refactors + the `decomp/` regroup
and the `kr → bls` engine reorg all landed — see HISTORY 2026-06-17.)

## Portfolio rework (NEXT PRIORITY)

`aut2ltl/portfolio/builder.py` now holds named assembly **recipes** over the
translators. `best` = `Simplify(strength(acceptance(daisy(core))), "hi")` with
`core = first(partscc, bls)` — the modern re-expression of the historical
`Decompose / SlDriven / Decompose` default, `daisy` in place of the sl envelope and
`partscc` in place of `t2`. It **reproduces and slightly beats** that default and is
reachable via `--use best` (see HISTORY 2026-06-18; survey log pointer below). The
new framing (from this session): **`sl/` and the current `portfolio/` contents should
disappear** — all of sl is covered by `daisy` (a stronger self-loop labeler), and the
one piece with no daisy equivalent (`fuse2`) is already extracted to `heur/`.

Remaining, roughly in order:

- **Promote `best` to the actual default.** Replace the old `Decompose / SlDriven /
  Decompose` graph (`portfolio/__init__.py` `reconstruct_decomposed`,
  `build.py::_default_portfolio`) with `builder.best`, so the no-`--use` path IS the
  recipe. The benchmark gives the strongest case yet: `best` is not just smaller but
  **correct** where the legacy default is WRONG — a verified `FALSE` (non-equivalent)
  on a strong-until chain that `best` reconstructs soundly (see HISTORY 2026-06-18).
- **Retire the old portfolio contents** once `best` is the default and nothing imports
  them: `portfolio/decompose.py` (`Decompose`), `portfolio/sl.py` (`Sl`),
  `portfolio/sl_driven.py` (`SlDriven`), `portfolio/options.py` (`SL_*`), and the old
  cited-technique ladder in `build.py`. Then **retire `aut2ltl/sl/` entirely.**
- **Settle the `--use` vocabulary**: recipes (`best`, …) + the leaf names; `str`/`bls`
  → `bls`/`muller`. Drop the inline `_simp_f` boundary calls `portfolio/sl*.py` carry
  (the `Simplify` decorator subsumes them).
- **`best_of` combinator + a `cost`/size field on `LTLResult`.** Recipes pick the
  FIRST success; size is the research objective, so add `best_of([...], key=cost)`
  beside `first_success` (`LTLResult` is pre-shaped for a cost field).
- **A `recurse`/`fix` combinator (idea — revisit with `best_of`).** `daisy`, the
  `strength`/`acceptance` decomposers all share ONE shape: structural recursion over a
  well-founded decomposition — `leaf = combine([leaf(sub) for sub in decompose(lang)])`
  with a floor base case. NOT Kleene (not iteration of one op on the same input; it
  hands strictly-smaller subproblems back, terminating by well-founded descent). A
  shared `recurse(decompose, combine, floor)` would unify the three and give ONE place
  to swap `first`→`best_of`, memoize subproblems on the `Language`, and tag uniformly.
  Today each combinator owns its own recursion (honest, explicit) — extract only when
  the `best_of` + memo payoff is real.
- **Retire the transitional shims** once importers repoint: `aut2ltl/contract.py` and
  `aut2ltl/bls/bls.py`.
- **`fuse2` is unwired** (`heur/fuse2`). Decision: leave it out; let fuzzing measure
  whether its absence costs `best` vs the default before deciding to wire it.

Latest `--use best` survey vs the default reference: **`tests/logs/best.csv`**
(+10.7% DAG, 40/40 sound, several cases smaller than default). **NOT committed** —
throwaway scratch, still WIP; promote to `tests/logs/reference/<date>/` only once
`best` becomes the default.

## Open

- **Output size at scale (the live research front).** The construction is cheap; the
  flat form explodes and Spot hits its 32-acceptance-set wall. Representation/
  verification, not fidelity. Analysis: `docs/dag_folding.md`.
- **Benchmark sub-project (`tests/benchmark/`).** A size bench, `default` vs `best`,
  reusing the survey engine over file-based `inputs/` (the survey corpus + W/U/R chains
  + 105 Kinská HOA; survey already routes HOA, oracle vs the source automaton — the old
  "HOA input to the survey" item, now done). Collection done for those three categories.
  Next: more categories, a *very* progressive `randltl` ladder (the construction is
  multiply-exponential — lean on the per-input timeout), and curation (dedup via
  `normalize.py`, a representative classified set). Reference: `tests/benchmark/logs/reference/`.
- **Flags manual.** The `--use` / `-O` reference doc the root README points to (add
  the `--use best` recipe and the recipe-vs-leaf distinction).

## Housekeeping

- Two stale bls probes (`tests/kr/test_kr_zoom.py`, `tests/kr/measure_formula_dag.py`)
  import the removed `reachability` shell — repoint to `aut2ltl.bls.operators` or drop.

## Deferred (intentional — revisit only if needed)

- **Options wiring, Buckets 2 & 3.** The remaining `KR_*` knobs (fuse_letters,
  fold_fin_reach, simp.*, tracing, resource/safety limits) are declared in the package
  `options.py` contracts but still read from `os.environ`. Process-scoped by nature,
  so they stay env unless per-instance A/B is ever required.
- **Infra compartment.** Share `bdd_dict`/buddy and the DAG unifier as refs on the
  threaded context (the Options and Caches compartments already landed).
