#!/usr/bin/env bash
# Reap one or more runs until every command is accounted for, or the runs stall.
#
# Usage: cluster/reap_until.sh [--rounds N] [--every S] [--stall K] RUNID...
#
# `reap.sh` exits 0 once every command has a status file, so the obvious wait is
# `until reap.sh "$RUN"; do sleep 30; done`. That loop never ends when the cluster
# *loses* work: a walltime-killed or evicted command never gets a status, so it
# stays `missing` and the loop spins forever, doing nothing and reporting nothing.
#
# This one turns on the `missing` count instead. It exits 0 when every run reaches
# zero `missing` (all accounted), and exits 3 when the counts stop moving for
# `--stall` consecutive rounds — a stall is a finding, and the operator resumes
# (`oarrun.sh --resume RUNID`). It deliberately does NOT auto-resume: re-submitting
# while the originals still run writes duplicate rows into a second shard, which
# corrupts every tally. `TIMEOUT`/`FAIL` are *accounted*, not missing — they need a
# re-plan, not a resume, so they never block completion; they are reported.
set -u

ROUNDS=120
EVERY=60
STALL=4
while [ $# -gt 0 ]; do
    case "$1" in
        --rounds) ROUNDS="$2"; shift 2 ;;
        --every)  EVERY="$2";  shift 2 ;;
        --stall)  STALL="$2";  shift 2 ;;
        *) break ;;
    esac
done
[ $# -ge 1 ] || { echo "usage: reap_until.sh [--rounds N] [--every S] [--stall K] RUNID..." >&2; exit 2; }

HERE="$(cd "$(dirname "$0")" && pwd)"
RUNS=("$@")
prev=""
same=0

for round in $(seq 1 "$ROUNDS"); do
    total_missing=0
    state=""
    echo "--- round $round  ($(date +%H:%M:%S))"
    for run in "${RUNS[@]}"; do
        line="$("$HERE/reap.sh" "$run" 2>/dev/null | grep -- "done —" | head -1)"
        [ -n "$line" ] || { echo "  $run: no tally yet"; total_missing=$((total_missing + 1)); continue; }
        echo "  $line"
        miss="$(echo "$line" | grep -o '[0-9]\+ missing' | grep -o '[0-9]\+')"
        [ -n "$miss" ] || miss=0
        total_missing=$((total_missing + miss))
        state="$state|$run:$miss"
    done

    if [ "$total_missing" -eq 0 ]; then
        echo "ALL_ACCOUNTED after $round round(s)"
        exit 0
    fi

    # A frozen `missing` count across rounds means the jobs have drained and the
    # remainder is lost work, not work in flight (a job outlives at most one
    # walltime, so several rounds of no movement settle it).
    if [ "$state" = "$prev" ]; then
        same=$((same + 1))
        if [ "$same" -ge "$STALL" ]; then
            echo "STALLED: $total_missing missing, unchanged for $same rounds — resume with:"
            for run in "${RUNS[@]}"; do echo "  cluster/oarrun.sh --resume $run --split <bigger> --cores 4 --timeout 300"; done
            exit 3
        fi
    else
        same=0
    fi
    prev="$state"
    sleep "$EVERY"
done

echo "ROUNDS_EXHAUSTED: $total_missing still missing"
exit 4
