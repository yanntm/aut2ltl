# tests/pi2_hunt — the Π₂ recurrence hunt

Self-contained harness for the experiment posed in
[`research_notes/experiment_pi2_hunt.md`](../../research_notes/experiment_pi2_hunt.md):
find a **state-minimal** deterministic ω-automaton whose **language is star-free**
but which has a recurrence sub-question `Inf(C)` that is **not** star-free. The
outcome and analysis are written up in
[`research_notes/pi2_hunt_report.md`](../../research_notes/pi2_hunt_report.md) —
**start there**; the conjecture is refuted, and the witnesses are committed under
[`samples/fixtures/hoa/definability/`](../../samples/fixtures/hoa/definability/)
(`gf_abb_min_z2.hoa`, `gf_ab_anb_min_z2.hoa`).

The harness reuses `aut2ltl`'s oracle and holonomy decomposition as libraries and
changes nothing in the package. Everything runs one input per invocation, bounded
(`aut2ltl.bounded`, which reaps GAP), streaming, ≤15 s/example.

## Map

| script | purpose |
|---|---|
| `predicate.py <hoa>` | the `P1∧P2∧P3` judge on one automaton. P1 = star-free (oracle `decide`); P2 = the grounded form is SAT-minimal; P3 = some config's `Inf(C)` is oracle-NOT_LTL. Grounds configs on the minimal form **verbatim** (`build_cascade_unstripped`), not on `decompose_aut`'s padded normalisation. Exit 0 HIT / 1 near-miss / 2 error. |
| `monoid_check.py <hoa>` | **cascade-free, oracle-free** aperiodicity test of the transition monoid — the decisive, cheap root-cause check. A non-aperiodic monoid on a minimal star-free form is the counterexample core. Prints the period->1 group witness word. |
| `monoid_screen.py <folder>` | run `monoid_check` over a corpus in-process (~instant); tally aperiodic vs group-bearing and list the group forms. The cheap P3 pre-screen. |
| `witness_config.py <hoa>` | certificate extractor for a hit: the grounded-form size (rules out padding), the config count, and the serialized counting family (`p, u vⁿ x`) for every non-star-free `Inf(C)`. |
| `sweep.py <folder>` | run `predicate.py` over a folder, one bounded subprocess per file, `--jobs` parallel; stream a death histogram + `.lines.txt` (interrupt-safe). |
| `gen_dba_corpus.py` | generate the corpus: structured detection-memory templates (`GF/FG`, `GF(x&Xy)`, `GF(x&XFy)`, fairness) **+** a `randltl` stream, each reduced to a SAT-minimal recurrence form, deduped. |
| `canon_corpus.py` | map a folder of arbitrary (nondeterministic, TGBA) census automata to minimal deterministic forms — the 3B `genaut`-census entry point. |

## Generated (gitignored)

`corpus_*/` (reproducible via `gen_dba_corpus.py` / `canon_corpus.py`) and
`logs/*.lines.txt`. The markdown reports under `logs/` (death histograms, monoid
screen) are tracked.

## Quick start

```bash
# the root-cause check on the headline counterexample (instant)
python3 tests/pi2_hunt/monoid_check.py samples/fixtures/hoa/definability/gf_abb_min_z2.hoa
# its non-star-free Inf(C) certificates
python3 tests/pi2_hunt/witness_config.py samples/fixtures/hoa/definability/gf_abb_min_z2.hoa
# regenerate the corpus and the 24%-group statistic
python3 tests/pi2_hunt/gen_dba_corpus.py --out tests/pi2_hunt/corpus_3a
python3 tests/pi2_hunt/monoid_screen.py tests/pi2_hunt/corpus_3a
```
