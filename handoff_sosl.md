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

1. **Bank the §6.3 E2 drop** — `python3 -m tests.sosl.census_e2_exhibits
   ../reference/census/ablation_congruence.csv` (seconds, local; output
   `tests/sosl/logs/census_e2/flat_canon.md`): 3137 permanent stalls, gap
   distribution 1..53, prefix-independent **231**/3137, LTL 1741/3137,
   sharpest gap 53 (`3state1ap0acc_015752` + dual). **Blocked on theory
   item 1** (the PI count) before committing under `reference/census/`.
   The script cross-tabs by Wagner degree only — the spec's per-shape
   exhaustive negative still needs a shape column (prefix of `case_id`).

## Work items — theory

1. **Reconcile the PI count**: the 6222 ablation shows **231**
   prefix-independent permanent stalls, but the draft states two witnesses
   plus complements and the spec's per-shape claim is *zero* PI permanent
   stalls on every exhaustive shape. Restate the claim (or scope it) before
   engineering banks the E2 drop.
2. Integrate the E2 drop into §6.3's `⟨TBD⟩` markers once banked, and
   restate §6.4's LTL-cut paragraph from `e3_summary.md` — the direction
   inverts at 6222: keep the correlation, drop the direction claim.
3. Sweep the draft for 3938-era numbers and restate from the committed record
   (§6's preamble marks this; §6.2/§6.4 fills are in from `e1_summary.md`).

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
