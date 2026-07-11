# Handoff — sosl learner thread

You are the **learner thread** (sosl). Bootstrap: this file, then `CLAUDE.md`
(discipline — binding), then the *last* entries of `research_notes/sos_learning_report.md`.
Do NOT read `docs/HISTORY.md`. This file carries **current work items + pointers
only**, no history — the report is the ledger.

## Critical files

- `research_notes/sos_learning.md` — the paper. Its 9 `⟨TBD-M4⟩` markers all wait
  on the completed guarded sweep (item 5 below → item 6 fills them).
- `research_notes/sos_learning_spec.md` — the normative spec (§7 verdict vocab).
- `research_notes/sos_learning_report.md` — the engineering↔theory ledger. Append dated
  entries; theory replies in place.
- Code: `sosl/sosl/` (learner/teacher/experiment); probes + drivers under
  `sosl/tests/sosl/` (run from `sosl/`: `python3 -m tests.sosl.<name>`).
- Cluster runner: `cluster/README.md` (interface), `results/README.md` (example).
  Committed reference data lives under `sosl/tests/sosl/reference/`, never `logs/`.

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

## Work items (in order)

1. ✅ **Fault-verdict misfile fixed.** `MISMATCH`→`FAIL` (soundness verdict), new
   `CRASH` (a run that never completed): leaked `_Budget`→`BUDGET`, other→`CRASH`,
   in `census_campaign` AND `driver.py`, `run_case`'s catch-all aligned, spec §7
   updated. Guard: `tests/sosl/fault_verdict_probe.py`. Theory to ratify the vocab.
2. ✅ **`census_campaign --cases i:j --out-csv FILE`** — private-shard sharding.
3. ✅ **`cluster_plan`** — cuts the sweep into a `cmds.txt`, packed to
   `OARRUN_TIMEOUT` sourced from `cluster/config.sh`. Default = learner sweep.
4. ✅ **`census_e3`** long-format + per-`(case,mode)` sharding; `cluster_plan --e3`
   plans the ROLL census. Paper-anchored `campaign_e3` untouched.
5. ✅/⏳ **Cluster run 1 reaped.** Run ids:
   - sweep `20260710-233331-sweep.cmds` — **DONE clean**: 8496 rows (4248×2),
     0 dup, 0 FAIL, 0 CRASH (SOUND 5897, ACCEPTOR_ONLY 2405, BUDGET 192,
     OVERSIZE 2). Merged: `logs/cluster/20260710-233331-sweep.cmds/results.csv`.
   - E3 `20260711-010141-e3.cmds` — ROLL side **complete** (3186/3186 modes OK);
     the 30 `--only ours` commands timed out (145 cases/cmd × the learner's slow
     tail). **Do NOT re-run ours on the cluster**: `ours` = the sweep's default-leg
     `ref_classes`/`n_member_total`/`n_equiv`; derive it into the E3 long CSV.
   Still owed: fix `cluster_plan --e3` to stop emitting `ours` commands; assemble
   the E3 `ours` rows from the sweep CSV; then the item-6 analyzers.
   The `--budget 60` sweep also discharges the `gates.txt` ask to redo the 72
   deferred dual-symmetry comparisons at higher budget.
6. ⏳ **Analyzers + gates off the merged CSVs, then hand theory.** Run
   `census_e1`, `census_e2_exhibits`, `census_e3 --summary-only`; gates
   `witness_lock`, dual-symmetry / (d′), `guard_fired_final = 0` on every SOUND
   row. Commit the drop under `sosl/tests/sosl/reference/` (immutable per drop).
   Deliver theory (item-6): per-leg `n_guard_firings`, guard-green run count,
   cap-escape count, the `guard_fired_final` check, the E2 recount, dual-symmetry
   with the 72 deferred resolved, a wall-time line, the LTL-agreement count —
   these replace the paper's 9 `⟨TBD-M4⟩`.
- Parked until after the sweep: the "make the cap cheap to hit" measurement
  (lowered-cap re-run of the fired cases; see the report's 2026-07-09 correction).

## Cluster essentials

Only committed+pushed code runs. Commands run at the repo root with `deps/env.sh`
sourced; a sosl line is `cd sosl && python3 -m tests.sosl...` writing to
`"$OARRUN_OUT.csv"` (absolute, survives the `cd`). Each shard writes its private
`$OARRUN_OUT.csv`; `reap.sh` merges to `logs/cluster/$RUN/results.csv`. Default
caps: `--timeout 130` per command, `--walltime 0:05:00` per job, `--split 8`,
`--cores 2`. **ROLL deployed**: `opt/roll/ROLL.jar` present cluster-side (built on
a JDK host by `deps/build_roll.sh`, copied into the JDK-less checkout —
`deps/README.md`); `$ROLL_JAR` resolves it, `baseline.py` defaults to `opt/roll`.

## Cluster ops — hard-won (full writeup: report 2026-07-11)

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
- **Use a stall-aware reaper** (parse missing/timeout/fail; exit on all-accounted
  OR a 4-round stall), not `until reap; do sleep; done` (idles forever on loss).
  `reap.sh` exits 0 when `DONE=OK+TIMEOUT+FAIL=N`; TIMEOUT/FAIL need a re-plan
  (resume skips them), only `missing` needs resume.
- **Don't pack a heavy-tailed kind by its average**; don't recompute derivable
  data (E3 `ours` = the sweep's default leg).

## Standing gates (green before any commit touching the learner)

From `sosl/`: `saturation_gate`, `even_conformance`, `evenblocks_conformance`,
`exact_fixtures`, `exact_ref_gate` (one case/invocation), `witness_lock`,
`fault_verdict_probe`, `campaign_e0` (Even `51 (32/4/7/8)` / EvenBlocks
`99 (67/4/14/14)` ledgers byte-stable — row P5). Diagnostics ≤ 15 s/example, one
input per argv; long output to `tests/sosl/logs/`, never `/tmp`.
