#!/bin/bash
# Fetch a run's results and report how much of it exists.
#
# Additive and idempotent: it copies down whatever has been written so far and
# tallies it against the command count, so it is safe to call while jobs are
# still running, and calling it twice is how progress is observed. The only
# thing it does on the cluster is read files.
#
# A command's status file is written last and atomically, so the three-way
# split below is meaningful: FAIL is the tool's verdict, TIMEOUT is the cap, and
# a missing status is work *we* lost (walltime kill, eviction, node death) and
# can reclaim with `oarrun.sh --resume`.
#
# Usage: cluster/reap.sh [--strict] [--quiet] <runid>
#   --strict  exit 1 unless every command has a status
#   --quiet   print the one-line tally only

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=config.sh
source "$HERE/config.sh"

ROOT="$(git -C "$HERE" rev-parse --show-toplevel)"

STRICT=0
QUIET=0
while [ $# -gt 0 ]; do
    case "$1" in
        --strict) STRICT=1; shift ;;
        --quiet)  QUIET=1; shift ;;
        -h|--help) sed -n '2,18p' "$0"; exit 0 ;;
        -*) echo "unknown option: $1" >&2; exit 2 ;;
        *) break ;;
    esac
done
[ $# -eq 1 ] || { echo "usage: reap.sh [--strict] [--quiet] <runid>" >&2; exit 2; }
RUNID="$1"

DEST="$ROOT/$LOCAL_RESULTS/$RUNID"
mkdir -p "$DEST"
rsync -az "$CLUSTER:$REMOTE_RUNS/$RUNID/" "$DEST/"

[ -s "$DEST/cmds.txt" ] || { echo "no command list in $DEST — unknown run id?" >&2; exit 2; }
N="$(grep -c '' "$DEST/cmds.txt")"

OK=0; TIMEOUT=0; FAIL=0
if [ -d "$DEST/status" ]; then
    read -r OK TIMEOUT FAIL < <(
        find "$DEST/status" -type f -print0 \
            | xargs -0 --no-run-if-empty cat \
            | awk '{ c[$1]++ } END { printf "%d %d %d\n", c["OK"], c["TIMEOUT"], c["FAIL"] }'
    )
fi
DONE=$((OK + TIMEOUT + FAIL))
MISSING=$((N - DONE))

# Per-command CSV shards, concatenated in index order with one header. Written
# per command rather than appended to a shared file because O_APPEND is not
# atomic over NFS and interleaves under a whole-node fan-out.
SHARDS=$(find "$DEST/out" -maxdepth 1 -name '*.csv' 2>/dev/null | wc -l)
if [ "$SHARDS" -gt 0 ]; then
    find "$DEST/out" -maxdepth 1 -name '*.csv' -printf '%f\n' \
        | sort -n \
        | sed "s|^|$DEST/out/|" \
        | xargs --no-run-if-empty awk 'FNR == 1 && NR != 1 { next } { print }' \
        >"$DEST/results.csv"
fi

echo "$RUNID: $DONE/$N done — $OK ok, $TIMEOUT timeout, $FAIL fail, $MISSING missing"

if [ "$QUIET" -eq 0 ]; then
    echo "  fetched to $DEST"
    if [ "$SHARDS" -gt 0 ]; then
        echo "  merged $SHARDS csv shard(s) into $DEST/results.csv"
    fi
    if [ "$MISSING" -gt 0 ]; then
        echo "  $MISSING command(s) have no status: still queued/running, or lost to a"
        echo "  walltime kill. Fill the gaps with: oarrun.sh --resume $RUNID"
    fi
    if [ "$FAIL" -gt 0 ]; then
        echo "  failing commands:"
        grep -lE '^FAIL ' "$DEST"/status/* 2>/dev/null | head -5 \
            | sed 's|.*/||' | while read -r i; do
                printf '    [%s] %s\n' "$i" "$(sed -n "${i}p" "$DEST/cmds.txt")"
            done
        if [ "$FAIL" -gt 5 ]; then
            echo "    ... and $((FAIL - 5)) more (see $DEST/logs/)"
        fi
    fi
fi

if [ "$STRICT" -eq 1 ] && [ "$MISSING" -gt 0 ]; then
    exit 1
fi
exit 0
