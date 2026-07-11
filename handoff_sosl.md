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
7. 🔴 **OPEN — blocked on theory.** The no-saturation fixpoint is **not a congruence**
   for the product, so the object export reads off is not an algebra. The 17 crashes
   are the loud tip; the dangerous kind is **silent** (non-congruent, yet every class
   still reachable → no assertion, a meaningless invariant counted as
   `ACCEPTOR_ONLY`). **See the POST section at the end of this file** — the question,
   the four-box taxonomy, and the fix held pending the ruling. Full data: the report's
   "Open defect" section.
8. ⏳ **E1/E3 done; E2 blocked.** `census_e1` and `census_e3 --summary-only` are run
   and committed (`reference/census/e1_summary.md`, `e3_summary.md`), and the E3
   reading is **corrected** at full scale: on LTL the algebra is now more often the
   *larger* object (1524 v 1842) — the old "smaller on LTL" headline was an artifact
   of a small-shape corpus. What survives is the correlation, not the claim; the
   aggregate is still a wash.
   Still owed once item 7 rules: `census_e2_exhibits` + the E2 recount, gates
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

# POST — question for the theory thread: what is the ablation's object?

*Self-contained: no code needed to answer. The engineering fix is blocked on the
ruling, and so is E2's recount. Full data in the report's "Open defect" section.*

## The setup, in the paper's terms

The learner maintains a partition of words into classes and stops at a **fixpoint**:
the table is closed and consistent, and the equivalence query returns no
counterexample. From that fixpoint we **export an algebra**: the classes, with the
product

    [c] · [d]  :=  class of ( c · rep(d) )

— multiply by a *representative* of `d`. This is well defined on classes only if the
partition is a **congruence** for concatenation. Our `𝓘(L)` is, by definition,
ε-generated: every class is a product of letters starting from ε.

**Saturation is what forces the fixpoint to be a congruence.** The E2 ablation turns
it off (`--no-saturation`, with the exact equivalence oracle). And then the fixpoint
need not be one: we measure, on real languages, classes `c` and letters `a` with

    [c] · [a]  ≠  class of ( c·a )

i.e. the product **depends on which representative was chosen**. It is not an
operation on classes at all.

Crucially, the hypothesis is still **language-correct**: export is only reached
because the *exact* oracle certified equivalence to `L`. The learner produced a
correct acceptor and no algebra.

Worked case (`2state2ap2acc_parity_1618…`), same language, both legs:

| | classes | reachable from ε by the product | `[c]·[a]` vs `class(c·a)` disagreements |
|---|---|---|---|
| saturation **on** | 17 (= `\|𝓘(L)\|`) | 17 | **0** |
| saturation **off** | 13 | 10 | **4** |

The 3 missed classes are reachable in the *automaton* — the learner can name them.
Only the algebraic product cannot.

## The taxonomy this induces on the ablation leg

Every ablation run falls in one of four boxes. Two are fine, two are not:

| | fixpoint a congruence? | ε-product reaches every class? | what export yields | today |
|---|---|---|---|---|
| (a) | yes | yes | the canonical object | `SOUND` (2357) |
| (b) | yes | yes | a genuine recognizer of `L`, not the canonical one | `ACCEPTOR_ONLY` ✅ honest |
| (c) | **no** | yes | **an algebra read off an ill-defined product — meaningless** | `ACCEPTOR_ONLY` ❌ **silently wrong** |
| (d) | **no** | no | nothing — an assertion fires | `CRASH` (17) ❌ |

(d) is loud and harmless. **(c) is the problem**: nothing notices, and the row is
counted as though export had merely landed on a coarser object. In a 14-case sample
of parity `ACCEPTOR_ONLY` runs, **3 were in box (c)**. So E2's `ACCEPTOR_ONLY`
population is a mixture of (b) and (c), and we do not currently know the ratio.

Data floor, for calibration: on the full 6222-language catalogue the **default leg is
6222/6222 SOUND**. Everything here is confined to the ablation leg. The 9 crashing
languages are all parity, and complement-symmetric.

## What we need ruled

1. **What *is* the no-saturation fixpoint?** It is a language-correct acceptor whose
   class set is not closed under the product. It is not `𝓘(L)`, and in boxes (c)/(d)
   it is not an algebra. Does the paper name this object — or does §5's ablation story
   simply become *"saturation is what makes the fixpoint an algebra at all"*, which is
   what the data now says outright?

2. **What is E2 measuring?** E2 claims *with exact equivalence, every surviving stall
   is provably permanent*. That quantifies over exactly this leg. If some rows export
   a meaningless invariant, the counts are drawn from a contaminated population. The
   recount is blocked until (1) is answered.

3. **Is `ACCEPTOR_ONLY` one verdict or two?** Its spec §7 gloss — "export byte-differs,
   hypothesis sound" — presupposes that export *succeeds*. Boxes (b) and (c) are
   different facts and are currently conflated. Should "correct acceptor, **no algebra
   exists**" be its own verdict?

4. **Are the 9 crashing languages witnesses rather than bugs?** They exhibit a fixpoint
   that is language-correct and algebraically inconsistent — E2's thesis in its
   sharpest form. Worth an exhibit in the paper?

5. *(Optional, if theory wants the number.)* Sizing box (c) exactly is cheap: the test
   is `[c]·[a] == class(c·a)` for all classes and letters, `O(n·|Σ|)`. It needs the
   partition, so it means re-running the ablation leg once with a `congruent` column
   added. Say the word and it is one cluster drop.

## The engineering fix, held pending the ruling

Ready to land, but each piece encodes an answer to the above, so it waits:

- export **refuses** on a non-congruent fixpoint instead of assuming (the existing
  assertion stays — it is a correct guard on its own contract, just the wrong place
  to discover this);
- the "correct acceptor, no algebra" outcome gets an honest verdict/detail, so (b) and
  (c) stop being counted together;
- the congruence test becomes a standing gate on the ablation leg, so box (c) can
  never be counted silently again.

Probes already in the tree: `tests/sosl/crash_unreachable.py` (per-case diagnosis,
`--sat` for the contrast), `tests/sosl/congruence_audit.py` (one line per case:
`congruent` / `reachable` / `bad_cells`).
