# Handoff — sosl learner thread

You are the **learner thread** (sosl). Bootstrap: this file, then `CLAUDE.md`
(discipline — binding), then the *last* entries of `research_notes/sos_learning_report.md`.
Do NOT read `docs/HISTORY.md`. This file carries **current work items + pointers
only**, no history — the report is the ledger.

## Critical files

- `research_notes/sos_learning.md` — the paper. Its `⟨TBD⟩` markers (the M4
  tallies, the §6.3 congruence recount, the §6.4 E3 restatement) wait on the
  E2 recount below.
- `research_notes/sos_learning_spec.md` — the normative spec (§7 verdict vocab).
- `research_notes/sos_learning_report.md` — the engineering↔theory ledger. Append dated
  entries; theory replies in place.
- Code: `sosl/sosl/` (learner/teacher/experiment); probes + drivers under
  `sosl/tests/sosl/` (run from `sosl/`: `python3 -m tests.sosl.<name>`).
- Cluster runner: `cluster/README.md` (interface), `results/README.md` (example).
- Committed reference data (never `logs/`): `reference/census/` — the catalogue
  sweep + E3 + the E1/E3 summaries; `reference/campaigns/` — the named-case gates
  (E0/M4B/E5). Both manifests are **generated** (`census_manifest`,
  `campaign_manifest`), never hand-edited. A figure that traces only to `logs/`
  does not enter the paper.

## Concurrent editors — stay in your sphere

Other live sessions share this checkout (calculus / symbolic / toltl / quant;
also a genaut session that owns `genaut/corpus/**` — the catalogue grows with
higher-Wagner-degree samples, and growth **renames** as well as adds; immaterial,
it all re-runs). Therefore:
- **Commit with explicit pathspecs only** (`git commit -F ... -- <file>`); the
  index may hold others' staged changes at any moment.
- No history/diff reading outside learner files; never touch their files.
- One commit per file (or a mechanical sweep together); `-F` heredoc for messages
  with backticks; never rebase/amend; push only with the user's explicit OK
  (asked every time).

## What holds (the banked record)

- **The catalogue** is 6222 complement-closed languages; the census record lives
  in `reference/census/` (sweep 12444 rows, E3 24888 rows), fully accounted.
- **Default leg: 6222/6222 SOUND**, `N ∈ [2, 208]`, `splits ≤ N`, 0 violations.
- **The congruence column is measured and banked**
  (`reference/census/ablation_congruence.csv`, 6222 ablation rows; grade with
  `python3 -m tests.sosl.congruence_column <csv>`):
  - **P9 clean** — all **3137** `ACCEPTOR_ONLY` rows are `fixpoint_congruent =
    false`. Theorem 5.3 has zero counterexamples over the catalogue.
  - **P10 clean** — all **2336** `SOUND` rows are `true`: no byte-equality ever
    arose from a non-congruent partition.
  - Dual-symmetric over the 2733 comparable pairs; zero off-diagonal mass, and
    no `CRASH` row anywhere in the leg.
  - A `BUDGET` row may carry either value or `n/a`: a run can check its fixpoint
    and only then exhaust its budget. Only `ACCEPTOR_ONLY` / `SOUND` are pinned.
- ⚠️ **The verdict partition is budget-censored — counts are a floor, not an
  invariant.** `ACCEPTOR_ONLY` / `SOUND` / `BUDGET` depends on what a machine
  finishes inside the 60 s budget: against the v2 sweep this drop moved **70
  cases into `BUDGET` and 14 out**. What is stable is the *classification* — **no
  case ever flipped `ACCEPTOR_ONLY` ↔ `SOUND`**. So `permanent = 3170` is not
  reproducible; a permanence count is a floor at a stated budget. This is the
  open POST.
- **A run's budget is a ceiling only under `run_case_bounded`** (its own process,
  OS-enforced kill at `budget + KILL_GRACE_S`) — the sweeps use it. `run_case`'s
  in-process `signal.alarm` is *cooperative*: Python defers it to a bytecode
  boundary, so it cannot preempt a native call. Gates and E0 may use either.
  `cluster_plan` packs commands against the enforced ceiling, never the bare
  budget.
- **The ablation's fixpoint is the certified Cayley acceptor** — an acceptor,
  never an algebra unless canonical (paper Lemma 5.2 / Theorem 5.3). With the
  exact oracle a certified fixpoint is canonical **or** its partition is not a
  congruence; `ACCEPTOR_ONLY` means "correct acceptor, no algebra". The
  normative congruence test is the sweep's check phase (`find_left_divergence`,
  zero queries); the `O(n·|Σ|)` letter test is unsound and is kept only as a
  contrast diagnostic in `congruence_audit`.
- **The export refuses** on a dirty check (`NotCongruent`). `--unchecked` is the
  diagnostic display the paper's §4.2 cell is defined on; its output is never a
  deliverable. `fixpoint_congruent` / `export_associative` are recorded (spec §7).
- **E1 / E3 are done and committed** (`reference/census/e1_summary.md`,
  `e3_summary.md`). E3 at full scale: on LTL the algebra is more often the
  *larger* object (1524 v 1842); the correlation survives, the aggregate is a
  wash.

## Open work (in order)

1. 🔴 **BLOCKED on the POST below — the E2 recount.** The permanence count cannot
   be banked until theory rules on how to report a budget-censored population
   (see POST). Once ruled: `census_e2_exhibits` + the recount over
   `reference/census/ablation_congruence.csv`, the gates (dual-symmetry / (d′),
   `guard_fired_final = 0` on every SOUND row), and the theory deliverables that
   replace the paper's `⟨TBD⟩` markers — per-leg `n_guard_firings`, guard-green
   count, cap-escape count, wall-time line, LTL-agreement count.
- Parked: the "make the cap cheap to hit" measurement (lowered-cap re-run of the
  fired cases).

## Cluster essentials

Only committed+pushed code runs. Commands run at the repo root with `deps/env.sh`
sourced; a sosl line is `cd sosl && python3 -m tests.sosl...` writing to
`"$OARRUN_OUT.csv"` (absolute, survives the `cd`). Each shard writes its private
`$OARRUN_OUT.csv`; `reap.sh` merges to `logs/cluster/$RUN/results.csv`. Default
caps: `--timeout 130` per command, `--walltime 0:05:00` per job, `--split 8`,
`--cores 2`. **ROLL deployed**: `opt/roll/ROLL.jar` present cluster-side (built on
a JDK host by `deps/build_roll.sh`, copied into the JDK-less checkout —
`deps/README.md`); `$ROLL_JAR` resolves it, `baseline.py` defaults to `opt/roll`.

## Cluster ops — the rules

- **Walltime (5 min), not `--timeout`, is the binding constraint.** Small
  `--split` packs many slow commands/job → walltime kill → mass `missing`. Size
  `--split` so each job's missing load ≈ `--cores` (one worst-case cmd < walltime).
- **`missing` right after submit = queued/running, NOT lost.** Only resume once
  the count is FROZEN ≥4 reap rounds (~6 min > walltime = drained).
- **Never resume before drain** — the original + resumed jobs write different
  `$OARRUN_OUT` shards → `reap.sh` concatenates both → **duplicate rows**. Always
  verify 0 dup keys in the merged CSV.
- **Resume with a BIGGER `--split`, and re-pass `--timeout`** (else it reverts to
  the config default 130 and cuts multi-case commands).
- **Wait with `cluster/reap_until.sh RUN...`** (background it): exits 0
  all-accounted / 3 stalled (naming the resume) / 4 rounds-exhausted, and takes
  several runs at once. Lost work never gets a status, so it must be watched for,
  not waited on. `reap.sh` exits 0 when `DONE=OK+TIMEOUT+FAIL=N`; TIMEOUT/FAIL need
  a re-plan (resume skips them), only `missing` needs resume.
- **Don't pack a heavy-tailed kind by its average**; don't recompute derivable
  data (E3 `ours` = the sweep's default leg).

## Standing gates (green before any commit touching the learner)

From `sosl/`: `saturation_gate`, `even_conformance`, `evenblocks_conformance`,
`exact_fixtures`, `exact_ref_gate` (one case/invocation), `witness_lock`,
`fault_verdict_probe`, `congruence_gate`, `campaign_e0` (Even `51 (32/4/7/8)` /
EvenBlocks `99 (67/4/14/14)` ledgers byte-stable — row P5). Diagnostics
≤ 15 s/example, one input per argv; long output to `tests/sosl/logs/`, never
`/tmp`.

## The corpus (genaut)

The learner's test set is **`genaut/corpus/flat_canon/` only** — 6222 languages,
one per language up to AP relabeling, closed under complement. The other tiers
(`tgba/`, `spot_det/`, `det/`, `sos/`, `flat/`, `sampled/`) are presentation
censuses and are not ours. Reach cases through `manifest.flat_canon_cases()`.

**Never address a case by a name you construct.** In particular a complement:
genaut mints the `<primal>_c` alias only where the enumeration was one-sided, so
a dual that some campaign drew under its own combo id has no `_c` file at all.
The catalogue grows, and growth renames — a hardcoded `<id>_c` is a latent
crash. Resolve duals out of the catalogue, or rely on duality and don't name
them.

---

# POST — how should a budget-censored population be reported?

**The claims are safe; a count is not.** P9 and P10 are clean over the whole
catalogue (3137 `ACCEPTOR_ONLY`, all non-congruent; 2336 `SOUND`, all congruent;
zero off-diagonal). Theorem 5.3 stands with no counterexample. But the *size* of
the permanent population is not an invariant of the corpus: it is whatever a
machine can finish inside the 60 s budget. Re-running the same leg moved **70
cases into `BUDGET` and 14 out of it** versus the banked sweep, so the spec's
predicted `permanent = 3170` measures as **3137** here — and would measure
differently again on other nodes.

Crucially, **no case ever flipped `ACCEPTOR_ONLY` ↔ `SOUND`**: what a run
*decides*, it decides stably. Only *whether it decides in time* moves. The
`BUDGET` rows are undecided, not counter-evidence.

Three ways out, engineering has no preference and will do as ruled:

1. **Report the floor.** "≥ 3137 permanent at a 60 s budget, 736 undecided" —
   honest, reproducible as an inequality, and the E2 permanence claim is
   existential anyway (it needs the population to be non-empty and its members
   certified, both of which hold).
2. **Shrink the censored region.** Re-run only the 736 `BUDGET` cases at a much
   larger budget (they are 12% of the corpus, so even 10× is cheap) and report
   the count at that budget with the residue stated. Does not eliminate
   censoring, just pushes it down.
3. **Drop the count from the paper** and report the partition as
   decided/undecided, if §6.3 does not actually need a number.

Engineering leans (2)-then-(1): it costs one small drop and lets the paper state
a much tighter floor. But whether §6.3's argument needs an exact count is a
theory question, so it is yours.
