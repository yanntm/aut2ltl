# results — committed reference survey runs

Per-corpus reference runs of the **default** portfolio, one folder under
`reference/`. Each holds the per-formula CSV (GitHub renders it as a table) and a
one-glance `SUMMARY.txt`:

| corpus | folder | CSV | inputs |
|---|---|---|---|
| validation (the correctness gate) | `reference/validation/` | `default.csv` | 80 |
| benchmark (survey + W/U/R chains + Kinská) | `reference/benchmark/` | `default.csv` | 333 |
| Kinská on their own | `reference/kinska/` | `kinska.csv` | 165 |

Each CSV is keyed by its **`source`** column — the unique provenance of every row
(relative path / `file:line` / `--ltl:k`). The `input` column is the readable
label and may repeat.

## Refreshing a reference run (the evaluation gate)

Never overwrite a committed CSV blind. Rerun into the gitignored scratch `logs/`,
diff against the committed reference, and only overwrite when the diff is clean.

```bash
# 1. rerun into scratch (logs/ is gitignored; --logs writes survey_<ts>.csv there)
mkdir -p logs/rerun/{validation,kinska,benchmark}
python3 -m survey --folder samples/validation --logs logs/rerun/validation > logs/rerun/validation/SUMMARY.txt
python3 -m survey --folder samples/kinska     --logs logs/rerun/kinska     > logs/rerun/kinska/SUMMARY.txt
python3 -m survey --folder samples/benchmark  --logs logs/rerun/benchmark  > logs/rerun/benchmark/SUMMARY.txt

# 2. diff each new run against its committed reference (keyed on source; exits 1 on a regression)
python3 -m survey.diff.results reference/validation/default.csv logs/rerun/validation/survey_*.csv
python3 -m survey.diff.results reference/kinska/kinska.csv      logs/rerun/kinska/survey_*.csv
python3 -m survey.diff.results reference/benchmark/default.csv  logs/rerun/benchmark/survey_*.csv
```

**Clean** = each diff reports `0 regression(s)` and each `SUMMARY.txt` ends
`SUCCESS` (no verified non-equivalent / `FAIL`). A validation regression
(`TRUE -> ` anything else) makes the diff exit 1 — investigate, do not overwrite.
Size / technique movements are informational, a human judgement call.

```bash
# 3. only when clean: overwrite the committed CSV + summary, then commit
cp logs/rerun/validation/survey_*.csv reference/validation/default.csv
cp logs/rerun/validation/SUMMARY.txt  reference/validation/SUMMARY.txt
# …same for kinska/ and benchmark/…
```

Run these from the repo root (the diff paths above are relative to `results/`).
