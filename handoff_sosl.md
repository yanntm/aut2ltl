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
5. ✅ **Drops are additive.** `--done <prior CSV>` on `census_campaign` /
   `census_e3` / `cluster_plan`: a slice already covered is not planned and not
   re-run. (Resume alone cannot do this — a campaign reads its done set from its
   *output*, and the cluster gives every command an empty private `$OARRUN_OUT.csv`.)
   `cluster/reap_until.sh RUN...` is the wait (ends on all-accounted or a stall).
6. ✅ **v2 drop reaped clean; the record is committed.** Catalogue grew 4248 →
   **6222** (purely additive — the earlier languages are byte-untouched), so only the
   new ones were run: sweep `20260711-064811-sweep_v2.cmds` (989 cmds) and E3
   `20260711-065537-e3_v2.cmds` (1491 cmds), both **fully accounted, 0 timeout,
   0 fail, 0 missing, 0 duplicate keys**; the late-adopted pair ran locally (4 runs,
   SOUND). Record: `reference/census/` (sweep 12444 rows, e3 24888 rows).
   - **default leg: 6222/6222 SOUND**, `N ∈ [2, 208]`, `splits ≤ N` with 0 violations.
   - ablation leg: SOUND 2357, ACCEPTOR_ONLY 3153, BUDGET 680, OVERSIZE 15,
     **CRASH 17** → item 7.
7. ✅ **RULED (2026-07-11, theory).** The ablation's fixpoint is the **certified
   Cayley acceptor** — an acceptor, never an algebra unless canonical. Paper
   Lemma 5.2 + Theorem 5.3: with the exact oracle, a certified fixpoint is
   canonical **or its partition is not a congruence** — box (b) is empty, the
   `ACCEPTOR_ONLY` population was pure (c), and E2's permanence counts stand
   (the 17 ex-`CRASH` rows join `permanent` → 3170). The proposed `O(n·|Σ|)`
   letter test is **REJECTED** (vacuous without merged letters — the stalled
   `a_implies_xa` export passes it); the normative test is the sweep's check
   phase, zero queries. Full ruling: report "Theory ruling (2026-07-11)"; spec
   rev 2026-07-11. Item-1 verdict vocab ratified.
7b. 🔴 **NEW — implement spec §8 item 13** (the amended fix): the Lemma 5.2
   check as classifier + `fixpoint_congruent` field; export **refusal** on a
   dirty check (keep the assert; add `--unchecked` for the P7/F8 fixture);
   fix `congruence_audit` (full check, not letters) and re-run the 14-case
   sample (predicted: all 14 flip to non-congruent); local gates; then the
   one-column **ablation-only** re-run drop (6222 cases; `--done` cannot
   apply) gated by P9/P10; then the E2 recount (`permanent = 3170`).
8. ⏳ **E1/E3 done; E2 was blocked on item 7 — now unblocked through 7b.**
   `census_e1` and `census_e3 --summary-only` are run
   and committed (`reference/census/e1_summary.md`, `e3_summary.md`), and the E3
   reading is **corrected** at full scale: on LTL the algebra is now more often the
   *larger* object (1524 v 1842) — the old "smaller on LTL" headline was an artifact
   of a small-shape corpus. What survives is the correlation, not the claim; the
   aggregate is still a wash.
   Still owed once 7b lands: `census_e2_exhibits` + the E2 recount, gates
   (`witness_lock`, dual-symmetry / (d′), `guard_fired_final = 0` on every SOUND row),
   and the theory deliverables that replace the paper's 9 `⟨TBD-M4⟩` (per-leg
   `n_guard_firings`, guard-green count, cap-escape count, wall-time line,
   LTL-agreement count).
- Parked until after the sweep: the "make the cap cheap to hit" measurement
  (lowered-cap re-run of the fired cases).

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
`fault_verdict_probe`, `campaign_e0` (Even `51 (32/4/7/8)` / EvenBlocks
`99 (67/4/14/14)` ledgers byte-stable — row P5). Diagnostics ≤ 15 s/example, one
input per argv; long output to `tests/sosl/logs/`, never `/tmp`.

---

# POST — ANSWERED (2026-07-11)

The theory ruling is in the report ("Theory ruling (2026-07-11) — canonical or
no algebra at all") and adopted in spec rev 2026-07-11 + paper Lemma 5.2 /
Theorem 5.3. One-paragraph summary: the ablation's fixpoint is the certified
Cayley acceptor; with the exact oracle a certified fixpoint is canonical or
its partition is not a congruence (box (b) empty — `ACCEPTOR_ONLY` means
"correct acceptor, no algebra"); E2's counts stand, sharpened; the letter
test is unsound (use the sweep's check phase, zero queries); GO on the
congruence-column ablation re-run. Engineering work: item 7b above =
spec §8 item 13.
