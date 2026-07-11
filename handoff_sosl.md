# Handoff — sosl learner thread

You are the **learner thread** (sosl). Bootstrap: this file, then `CLAUDE.md`
(discipline — binding), then the *last* entries of `research_notes/sos_learning_report.md`.
Do NOT read `docs/HISTORY.md`. This file carries **current work items + pointers
only**, no history — the report is the ledger.

## Critical files

- `research_notes/sos_learning.md` — the paper. Its `⟨TBD⟩` markers (the M4
  tallies, the §6.3 congruence recount, the §6.4 E3 restatement) wait on
  items 7b → 8 below.
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

Other live sessions share this checkout (calculus / symbolic / toltl; also a
genaut session actively rewriting `genaut/corpus/**` — the catalogue grew
3938→4248 and will keep growing with higher-Wagner-degree samples; immaterial, it
all re-runs). Therefore:
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
- **Ablation leg**: SOUND 2357, ACCEPTOR_ONLY 3153, BUDGET 680, OVERSIZE 15.
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

1. 🟡 **The ablation-only re-run drop — IN FLIGHT.**
   `RUN=20260711-220435-sweep.cmds` (3111 commands, `--split 256`; planned by
   `cluster_plan --legs ablate`, 2 cases/command, 60 s/run under the 130 s cap).
   The ablation leg only: the default leg's column is `true` by construction and
   E3 is untouched. `--done` **cannot** apply — the column needs the final table,
   which only a re-run reconstructs. `--split 256` (not the default 8) because
   the leg's cost is the 680 BUDGET cases burning their full budget; a small
   split walltime-kills the jobs and mass-`missing`s.
   - Wait: `cluster/reap_until.sh 20260711-220435-sweep.cmds` (never resume
     before drain; verify 0 duplicate keys in the merged CSV).
   - Merged output: `logs/cluster/$RUN/results.csv`. Promote to
     `reference/census/` once graded.
   - Grade: `python3 -m tests.sosl.congruence_column <merged CSV>` — asserts
     **P9** (`ACCEPTOR_ONLY ⇒ false`; build-stopping, Theorem 5.3), **P10**
     (`SOUND ⇒ true`; exit 2, NOT build-stopping — a byte-equality out of a
     non-congruent partition is a theory finding: report the case ids, do not
     bank the rows), and dual symmetry over `manifest.dual_index`.
   - Expected: `false` on all 3153 + 17, `true` on all 2357, zero off-diagonal,
     dual-symmetric (congruence is complement-invariant).
2. 🔴 **The E2 recount** (`permanent = 3170`) + `census_e2_exhibits`, gates
   (dual-symmetry / (d′), `guard_fired_final = 0` on every SOUND row), and the
   theory deliverables that replace the paper's `⟨TBD⟩` markers: per-leg
   `n_guard_firings`, guard-green count, cap-escape count, wall-time line,
   LTL-agreement count.
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

No open POST to theory.
