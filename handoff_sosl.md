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
3. `research_notes/sos_learning_report.md` — the report. Current; its protocol
   notes govern how the numbers may be quoted.
4. Working gate: `cd sosl && python3 -m tests.sosl.gate_invariant_contract`.
5. Committed data: `reference/census/` and `reference/campaigns/` — their
   READMEs carry the regenerate recipes.

## Do not trust

- `research_notes/sos_learning_spec.md` — **stale**. The paper and
  `learn/algorithm.md` are the only normative documents.
- `reference/campaigns/m4b/` — **stale**, ablation-driven, not re-run;
  `campaign_m4b.py` no longer imports.
- Scripts under `sosl/tests/sosl/` may import names that no longer exist.
  Verify before running; a script that gates nothing current is a candidate
  for removal, not repair.

## The census runs locally — do not plan a cluster for it

    cd sosl && python3 -m tests.sosl.census_campaign --budget 60
    python3 -m tests.sosl.census_e1 tests/sosl/logs/census/results.csv

The E3 ROLL leg is the only part that costs real time (a JVM per language per
mode); its rows are committed and reused, `ours` re-derived via
`census_e3 --from-sweep`.

## Work items — theory

1. **§7 rewrite from the recomputed report.** Drop the §7.1 status note about
   queued regeneration.
2. **Decide `a → Xa`**: it no longer runs zero-counterexample (cex = 1,
   equiv = 2), so §7.2's claim and §7.3's echo are false against the code.
   Recover the behaviour, or drop the claim.
3. **Confirm the ablation leaves the paper.** No runner exists and the record
   is deleted; if it stays, the leg must be rebuilt.
4. Standing queue: §3 day-one material to the zero-seed bootstrap; §5 proofs
   from the normal form + the two opened lemmas; cross-ref sweep, then
   delete `s4a_reap.md` / `s4b_sow.md`.

## Work items — engineering

1. **Expand the frontier by letter classes, not letters.** `Table.domain`
   builds `rows · Σ` in full and `fill` queries every cell, so a row costs
   `|Σ|` extensions however λ acts. At the two-sided fixpoint letters sharing
   a λ-class are interchangeable in every context, so `rows · λ(Σ)` carries
   the same information: `|Σ|` queries to classify the letters once, then
   `|rows| · |λ(Σ)|` instead of `|rows| · |Σ|`. Measured ceiling
   (`tests/sosl/probe_letter_collapse.py`): **2.67× at 3 AP** — 8 letters land
   in 3 classes on the median language, only 102 of 776 keep all eight — and
   nothing at 1 AP, rare at 2. Fill dominates membership (18852 of 19731 at
   `N = 208`), so the saving lands where cost is highest.
   The learner knows the collapse only from evidence, so use the *current*
   classes speculatively: a premature merge is a discordance, which the
   coherence replay and legality already handle by minting a column and
   restarting. Core change (`learn/table.py`, `learn/partition.py`) — get the
   user's go before editing.
2. **The EQ-by-EQ animation** — step through what the learner believes at each
   equivalence query. Not started.
3. ROLL's 262 total + 177 partial failures are **unattributed**:
   `baseline.py` records a `detail` that `census_e3` drops. Needs a re-run to
   say timeout vs crash.
4. Scripts under `tests/sosl/` still carry the dead `Config(saturation=…)` /
   `NOSAT_EXACT` names; four were fixed by use, the unrun ones are unchecked.

## The corpus

`genaut/corpus/flat_canon` only — 6222 languages, complement-closed. Reach
cases via `manifest.flat_canon_cases()`; resolve duals via
`manifest.dual_index` — **never construct a `<id>_c` name**.

## Concurrent editors — stay in your sphere

Other live sessions share this checkout (calculus / symbolic / toltl / quant;
a genaut session owns `genaut/corpus/**`). Commit with explicit pathspecs
only (`git commit -F … -- <file>`); no history/diff reading outside learner
files; never rebase/amend; push only on the user's explicit OK.

This handoff is current-state only: re-curate after every landed increment —
a completed item is flushed (result → report, method → spec, history → git).
