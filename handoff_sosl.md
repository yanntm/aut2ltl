# Handoff — sosl learner thread

You are the **learner thread** (sosl). Bootstrap: this file, then `CLAUDE.md`
(discipline — binding), then the critical files below in order. This file
carries **current work items + pointers only**, no history.

## Critical files

1. `research_notes/sos_learning_spec.md` — the paper-data spec: every figure's
   committed source + regenerate command, and the owed list. Normative.
2. `research_notes/sos_learning_report.md` — the produced tables, paper-ready,
   each citing its committed source.
3. `research_notes/sos_learning.md` — the paper. Edited via the split parts in
   `research_notes/sos_learning/` (read its README; `make` assembles).
4. Code: `sosl/sosl/` (learner/teacher/experiment); probes + campaigns under
   `sosl/tests/sosl/` (run from `sosl/`: `python3 -m tests.sosl.<name>`).
   Gates and unit tests are engineering-internal: keep them green before any
   learner commit, never report them.
5. Committed data: `reference/census/` and `reference/campaigns/` — their
   READMEs carry the regenerate recipes. Cluster interface: `cluster/README.md`.

## Work items — engineering

None — all §6 data is banked under `reference/census/` (e1/e2/e3 summaries +
their CSVs).

## Work items — theory

1. **Review the rebooted §6** (`sos_learning/s6_experiments.md`, assembled;
   every number from the committed record via the report). On approval,
   delete the superseded `s6_eval.md` (kept in the folder, out of the
   assembly).

## The corpus

`genaut/corpus/flat_canon` only — 6222 languages, complement-closed. Reach
cases via `manifest.flat_canon_cases()`; resolve duals via
`manifest.dual_index` — **never construct a `<id>_c` name** (the catalogue
grows, and growth renames; a hardcoded name is a latent crash).

## Cluster essentials

Only committed+pushed code runs; a sosl line is `cd sosl && python3 -m
tests.sosl…` writing `"$OARRUN_OUT.csv"`. Walltime (5 min), not `--timeout`,
is the binding constraint — size `--split` so one worst-case command fits a
job. `missing` right after submit = queued, not lost: resume only once the
count is frozen ≥ 4 reap rounds, with a **bigger** `--split` and `--timeout`
re-passed; wait with `cluster/reap_until.sh` (backgrounded); verify 0
duplicate keys after `merge_drops`. Sweeps run under `run_case_bounded`
(OS-enforced ceiling; in-process alarms cannot preempt native calls). ROLL:
`opt/roll/ROLL.jar`, resolved by `$ROLL_JAR`.

## Concurrent editors — stay in your sphere

Other live sessions share this checkout (calculus / symbolic / toltl / quant;
a genaut session owns `genaut/corpus/**`). Commit with explicit pathspecs
only (`git commit -F … -- <file>`); no history/diff reading outside learner
files; never touch their files; `-F` heredoc for messages; never
rebase/amend; push only on the user's explicit OK, asked every time.

This handoff is current-state only: re-curate after every landed increment —
a completed item is flushed (result → report, method → spec, history → git).
