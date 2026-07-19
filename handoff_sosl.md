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
3. `research_notes/sos_learning_report.md` — the report. **Fully recomputed;
   every number in it is current.**
4. Working gate: `cd sosl && python3 -m tests.sosl.gate_invariant_contract`.
5. Committed data: `reference/census/` and `reference/campaigns/` — their
   READMEs carry the regenerate recipes.

## Do not trust

- `research_notes/sos_learning_spec.md` is **stale — do not trust it**. The
  paper and `learn/algorithm.md` are the only normative documents.
- `reference/campaigns/m4b/` is **stale**: ablation-driven, not re-run.
  `campaign_m4b.py` no longer imports (`E2_EXPECT` / `e2_runs` are gone).
- Scripts under `sosl/tests/sosl/` may import names that no longer exist —
  `Config(saturation=…)` and `NOSAT_EXACT` are the two dead ones already
  found and fixed in e0/e5/census. Verify before running.

## The census runs locally now — no cluster

The whole 6222-language sweep is **94 s single-threaded** (~12 runs/s;
worst language `N = 208` at 1.2 s). Do not plan a cluster campaign for it:

    cd sosl && python3 -m tests.sosl.census_campaign --budget 60
    python3 -m tests.sosl.census_e1 tests/sosl/logs/census/results.csv

The E3 ROLL leg is the one thing that still costs real time (a JVM per
language per mode); its rows are committed and are reused, with `ours`
re-derived from the sweep via `census_e3 --from-sweep`.

## Work items — theory

1. **§7 rewrite from the recomputed report** — the report is ready and the
   §7 status note about queued regeneration should go. State the counting
   convention.
2. **`a → Xa` no longer runs zero-counterexample** (now cex = 1, equiv = 2).
   §7.2's "zero counterexamples, a single assenting equivalence query" and
   §7.3's echo of it are false against current code. Decide: recover the
   behaviour, or drop the claim.
3. **`splits = N − 2` is now an identity**, exactly, on all 6222 languages —
   not an inequality the data tests. Prop. 5.3's `splits ≤ N` may want
   restating; and `splits/N = 1 − 2/N` makes the size-controlled ventilation
   a stronger negative (it carries no information beyond `N`).
4. **§7.4 is no longer a wash.** The query axis (new: MQ/EQ were recorded and
   never analyzed) gives membership parity at 1.11× and equivalence 5663
   fewer of 5783. The claim needs MQ and EQ to be non-fungible — state that
   argument rather than assume it.
5. **§7.5 is stronger than claimed**: padding is *free* on `even` and
   `a_once` (harvest flat), `log₂ ℓ` only on `gf_aa_parity`/`evenblocks`.
6. §6/§7.3 ablation: no runner exists and the record is deleted. Confirm it
   leaves the paper, or the leg must be rebuilt.
7. Standing queue: §3 day-one material to the zero-seed bootstrap; §5 proofs
   from the normal form + the two opened lemmas; cross-ref sweep, then
   delete `s4a_reap.md` / `s4b_sow.md`.

## Work items — engineering

1. **Next up: the EQ-by-EQ animation** — step through what the learner
   believes at each equivalence query. Not started.
2. ROLL's **262 total + 177 partial failures are unattributed**:
   `baseline.py` records a `detail` (timeout / exit / unparsed) that
   `census_e3` does not persist. Needs a re-run to say timeout vs crash.
3. ROLL runtime deliberately not recorded (JVM startup would dominate).

## Counting and comparison conventions (hold these)

- `member` counts distinct ω-words; phases fill / harvest / legality / `P`.
- Wall times are **not comparable across drops** — the old record is a
  cluster drop, the current one this workstation, and the old learner is
  gone. Report as measured; claim no speedup factor.
- The ROLL comparison set is the **5783** languages ROLL decides in *all
  three* modes. Its best mode is a `min` over three; a partially-failed
  language is excluded, not scored on its survivors.

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
