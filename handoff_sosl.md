# Handoff — sosl learner thread

You are the **learner thread** (sosl). Bootstrap: this file, then `CLAUDE.md`
(discipline — binding), then the critical files below in order. This file
carries **current work items + pointers only**, no history.

## Critical files

1. `research_notes/sos_learning2/README.md` — folder guide: restructure
   status, part wiring, old→new theorem numbering map. Read first.
2. `research_notes/sos_learning2.md` — the paper (assembled; edit the parts
   in `research_notes/sos_learning2/`, then `make`). §4 is the current core:
   alignment as a fixpoint over evidence, four-constraint normal form,
   bootstrap with no seeded column.
3. `research_notes/sos_learning2/algorithm.md` — design brief + engineering
   deltas. Normative for engineering once theory lands item 1 below.
4. `research_notes/sos_learning_report.md` — v1 report: provenance of §7's
   current numbers until the regeneration lands.
5. Code: `sosl/sosl/` (learner/teacher/experiment); probes + campaigns under
   `sosl/tests/sosl/` (run from `sosl/`: `python3 -m tests.sosl.<name>`).
   Gates and unit tests are engineering-internal: keep them green before any
   learner commit, never report them.
6. Committed data: `reference/census/` and `reference/campaigns/` — their
   READMEs carry the regenerate recipes. Cluster interface: `cluster/README.md`.

## Work items — theory

1. **Spec the §4 deltas for engineering** (into `algorithm.md`): bootstrap
   (`R = {ε}`, zero columns; first query = promoted letter's ω-power via the
   `P`-fill, decides `∅` vs `Σ^ω`; remaining letters' ω-powers probed in
   shortlex order, discordance → align); evidence coherence as fourth
   normal-form check (cache replay, query-free; violations seed the chain
   with no query); every column minted, none seeded. Include the hand-derived
   named-case expectations (first mints, day-one beliefs, first
   counterexamples). Engineering is blocked on this.
2. **§3 sweep**: Definitions 3.1/3.2 still seed `R = {ε} ∪ Σ` — rows must
   start `{ε}` and grow by promotion only; day-one example material and
   §3.2's forward references follow the new bootstrap and vocabulary.
3. **§5 edits** (section stays): proofs argue from the normal form (they
   currently say "both checks clean"); add the two opened lemmas —
   confluence (fixpoint belief independent of pinned resolution order),
   evidence-coherence implication (implied by morphism+saturation, or
   strict — adopted either way).
4. **§6 decision** (user call pending): slated for removal or compression
   into §4/§7.3; §7.3, contribution 2, and the abstract's stall claims
   depend on what survives.
5. **Cross-ref + vocabulary sweep** over §1–§2, §5–§8: old §4 numbering
   (map in the folder README) and retired reap/sow–harvest wording; then
   delete the superseded `s4a_reap.md` / `s4b_sow.md`.

## Work items — engineering

1. **Catch up to the rebuilt §4** — blocked on theory item 1; implement
   against `algorithm.md` + paper §4: bootstrap reformulation, evidence
   coherence, probe sweep. Traces must match the spec'd expectations on the
   named cases.
2. **Full regeneration** (after 1): named-case ledgers, census
   byte-equality, relaxed leg, §7 per-phase counts — the §7 status note's
   queue, now including the bootstrap deltas.

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
