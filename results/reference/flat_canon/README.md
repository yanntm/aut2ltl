# flat_canon — committed machine outputs for `sos_toltl_report.md`

Every table in `research_notes/sos_toltl_report.md` is audited against a file
here: the report is machine-built and traceable, not hand-transcribed. The bench
is `genaut/corpus/flat_canon/` (one deterministic Emerson–Lei automaton `D` and
one invariant `𝓘(L)` per distinct language, complement-closed; produced per
`genaut/README.md`). Each output below carries the exact command that produced
it; re-running it must reproduce the file.

| file | report section | command (from repo root) |
|---|---|---|
| `sos2ltl.csv` / `sos2ltl.SUMMARY.txt` | E4-interim, F8 | `python3 -m survey --folder genaut/corpus/flat_canon/det --use sos2ltl --logs logs/flat_canon/sos2ltl` |
| `sos2ltl_dg.csv` / `sos2ltl_dg.SUMMARY.txt` | E4-interim | `python3 -m survey --folder genaut/corpus/flat_canon/det --use sos2ltl_dg --logs logs/flat_canon/sos2ltl_dg` |
| `diff_dg_vs_engine.txt` | F8 (soundness gate) | `python3 -m survey.diff.results sos2ltl_dg.csv sos2ltl.csv` |
| `E1E2.txt` | E1, E2 (by Wagner degree) | `python3 -m tests.sos2ltl.census_build genaut/corpus/flat_canon/sos` then `python3 -m tests.sos2ltl.census_report tests/sos2ltl/logs/e12_flat_canon.jsonl` |
| `E7_ledger.txt` | E7 (dual scan, replay, cross-tabs) | `python3 -m tests.sos2ltl.e7_ledger genaut/corpus/flat_canon/sos` |
| `E7_tiers.txt` | E7, F7 (ω-blindness tiers) | `python3 -m tests.sos2ltl.e7_tiers tests/sos2ltl/logs/e7_flat_canon.jsonl` |
| `F8_engine_fails.txt` | F8 (engine-unsoundness ranking) | `python3 -m tests.sos2ltl.engine_fails sos2ltl.csv` |

The CSVs are keyed on `source` (the unique per-language provenance path); `input`
is the readable label and may repeat. The survey run is verified by the Spot
oracle and now ends `SUCCESS` — **0 FAIL** after both F8 defects were fixed; the
`not-checked` rows are SIZE-unverified (DG fallbacks and large engine formulas,
not errors). `F8_engine_fails.txt` is empty (no verified-non-equivalent answer).

Refresh discipline (per `results/README.md`): re-run into gitignored `logs/`,
diff against these committed files, overwrite only when the diff is understood.
