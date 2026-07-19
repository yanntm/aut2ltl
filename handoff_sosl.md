# Handoff — sosl learner thread

You are the **learner thread** (sosl). Bootstrap: this file, then `CLAUDE.md`
(discipline — binding), then the critical files below in order. This file
carries **current work items + pointers only**, no history.

## Critical files

1. `sosl/sosl/learn/algorithm.md` — the learner, normative for engineering:
   state, the four-constraint normal form, bootstrap, pinned orders,
   counting conventions. Read first, with `sosl/sosl/README.md` for the map.
2. `research_notes/sos_learning2.md` — the paper (edit the parts in
   `research_notes/sos_learning2/`, then `make`); §3–§5 is the theory the
   code transcribes.
3. `research_notes/sos_learning_report.md` — the report to update (below).
4. Working gate: `cd sosl && python3 -m tests.sosl.gate_invariant_contract`.
5. Committed data: `reference/census/` and `reference/campaigns/` — their
   READMEs carry the regenerate recipes. Cluster interface: `cluster/README.md`.

## Do not trust

- `research_notes/sos_learning_spec.md` is **stale — do not trust it**. The
  paper and `learn/algorithm.md` are the only normative documents.
- Scripts under `sosl/tests/sosl/` are suspect: many import names that no
  longer exist. Verify before running; a script that gates nothing current
  is a candidate for **plain removal**, not repair. The gate in critical
  file 4 is the one known-good entry point.
- `sosl/sosl/experiment/` (stats fields, report renderers, manifest configs)
  may lag the learner; align it as needed by the goal, trim what serves
  nothing.

## Work items — engineering

1. **Recompute the report.** Every number in
   `research_notes/sos_learning_report.md` needs recomputing — reuse none.
   Deliver: named-case runs (the paper's five, plus `EvenBlocks`) with
   per-phase ledgers under the counting conventions of `learn/algorithm.md`
   (member = distinct ω-words; phases fill/harvest/legality/P); census
   byte-equality at scale; equivalence/counterexample counts per case. All
   data traceable to git-tracked machine-generated artefacts.
2. Report any misprediction against the paper's worked examples (§3–§4
   tables) to theory instead of adapting to it — the paper may need the
   edit, not the code.

## Work items — theory

1. §7 rewrite from the recomputed report; state the counting convention.
2. Standing queue: §3 day-one material to the zero-seed bootstrap; §5 proofs
   from the normal form + the two opened lemmas (confluence,
   evidence-coherence implication); §6 decision (user call pending);
   cross-ref sweep, then delete `s4a_reap.md` / `s4b_sow.md`.

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
