# results — committed reference survey runs

Per-corpus reference runs of the **default** portfolio, one folder under
`reference/`. Each holds the per-formula CSV (GitHub renders it as a table) and a
one-glance `SUMMARY.txt`:

| corpus | folder | CSV | inputs |
|---|---|---|---|
| validation (the correctness gate) | `reference/validation/` | `default.csv` | 83 |
| benchmark (survey + W/U/R chains + Kinská) | `reference/benchmark/` | `default.csv` | 336 |
| Kinská on their own | `reference/kinska/` | `kinska.csv` | 165 |

Each CSV is keyed by its **`source`** column — the unique provenance of every row
(relative path / `file:line` / `--ltl:k`). The `input` column is the readable
label and may repeat.

## Refreshing a reference run (the evaluation gate)

Never overwrite a committed CSV blind. Rerun into the gitignored scratch `logs/`,
diff against the committed reference, and only overwrite when the diff is clean.

**Run every command below from the repo root, using the relative paths as written**
(`cd` to the root once, then never `cd` again — in particular do not `cd results/`,
or the relative `logs/...` paths drift and later steps fail).

```bash
# 1. rerun into a FRESH scratch (logs/ is gitignored; --logs writes a NEW
#    survey_<ts>.csv each run — wipe first so the survey_*.csv glob in steps 2-3
#    matches exactly one file and never an older stale run)
rm -rf logs/rerun
mkdir -p logs/rerun/{validation,kinska,benchmark}
python3 -m survey --folder samples/validation --logs logs/rerun/validation > logs/rerun/validation/SUMMARY.txt
python3 -m survey --folder samples/kinska     --logs logs/rerun/kinska     > logs/rerun/kinska/SUMMARY.txt
python3 -m survey --folder samples/benchmark  --logs logs/rerun/benchmark  > logs/rerun/benchmark/SUMMARY.txt

# 2. diff each new run against its committed reference (keyed on source; exits 1 on a regression)
python3 -m survey.diff.results results/reference/validation/default.csv logs/rerun/validation/survey_*.csv
python3 -m survey.diff.results results/reference/kinska/kinska.csv      logs/rerun/kinska/survey_*.csv
python3 -m survey.diff.results results/reference/benchmark/default.csv  logs/rerun/benchmark/survey_*.csv
```

**Clean** = each diff reports `0 regression(s)` and each `SUMMARY.txt` ends
`SUCCESS` (no verified non-equivalent / `FAIL`). A validation regression
(`TRUE -> ` anything else) makes the diff exit 1 — investigate, do not overwrite.
Size / technique movements are informational, a human judgement call.

### Step 1 on the cluster, if and only if you have one

Only on a machine inside the LIP6 network, where the OAR cluster answers. Anywhere
else the local step 1 above is the procedure — this section is not a fallback and
has no offline mode. It replaces step 1 only; steps 2–4 are unchanged, reading the
CSV from wherever it was produced.

The corpus is one example per row and the rows are independent, so it shards. The
planner discovers the examples once and cuts them into index ranges, each sized to
fit the runner's per-command cap, which it reads out of `cluster/config.sh`. No
sizing to choose, and no flags:

```bash
git push                                       # only committed code runs
cluster/sync_cluster.sh
python3 -m survey.cluster.plan --folder samples/validation -o logs/cluster/validation.txt
RUN=$(cluster/oarrun.sh logs/cluster/validation.txt)
until cluster/reap.sh "$RUN"; do sleep 30; done   # run this in the background
```

A cluster run is an ordinary throwaway run that happened to execute elsewhere: it
lands in the ignored `logs/cluster/$RUN/`, exactly as a local rerun lands in
`logs/rerun/<corpus>/`. Nothing enters `results/` by running. Feed
`logs/cluster/$RUN/results.csv` to step 2 in place of
`logs/rerun/<corpus>/survey_*.csv` — the shards carry each example's original
`source`, so the merged CSV is row-for-row comparable with the reference — and then
step 3 adopts it, or does not. Swap the `--folder` for `samples/benchmark` or
`samples/kinska`; nothing else changes.

No shard writes a `SUMMARY.txt` — each summarized only its own slice, into its own
`logs/cluster/$RUN/logs/<idx>.err`. Rebuild the run's summary from the merged CSV
once the run is **fully reaped**, and the local criterion applies unchanged:

```bash
python3 -m survey.summary logs/cluster/$RUN/results.csv > logs/cluster/$RUN/SUMMARY.txt
```

The summary is a fold over the rows, so this is the same text a live run would have
printed, `SUCCESS` and all, save the wall-clock `build=` (the cluster's nodes are
not your laptop). It exits 1 on a verified non-equivalence, so it gates. Pass
`--label` to name the recipe: the CSV records the technique that answered, not the
one `--use` asked for.

**Clean**, here, is `reap.sh` reporting `N/N done` with `0 timeout, 0 fail, 0
missing`, the regenerated `SUMMARY.txt` ending `SUCCESS`, *and* the step-2 diff
reporting `0 regression(s)`. Regenerate only when the run is complete: a summary
folded over a partial CSV counts only the commands that finished, and will happily
say `SUCCESS`. A `missing` command is work the cluster lost, not a regression:
reclaim it with `cluster/oarrun.sh --resume "$RUN"` and reap again before you
believe any diff.

See [`cluster/README.md`](../cluster/README.md) for the runner itself.

```bash
# 3. only when clean: overwrite the committed CSV + summary, then commit
cp logs/rerun/validation/survey_*.csv results/reference/validation/default.csv
cp logs/rerun/validation/SUMMARY.txt  results/reference/validation/SUMMARY.txt
# …same for kinska/ and benchmark/…

# 4. clean up behind yourself so the next refresh starts from an empty scratch
rm -rf logs/rerun
```

Every step runs from the repo root with the relative paths exactly as written above —
do not `cd` into `results/` between steps (that drifts the `logs/...` paths and breaks
the diff/copy commands).
