#!/bin/bash
# Fetch a run's results and report how much of it exists.
#
# A wrapper around one rsync. It only reads files on the cluster, so it is safe
# to call at any time; calling it again is how progress is observed.
#
# Exits 0 once every command has a status file, nonzero while any has none, so
# waiting for a run needs no flag:
#
#     until cluster/reap.sh "$RUN"; do sleep 30; done
#
# Usage: cluster/reap.sh <runid>

set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=config.sh
source "$HERE/config.sh"

[ $# -eq 1 ] || { echo "usage: reap.sh <runid>" >&2; exit 2; }
DEST="$(cd "$HERE/.." && pwd)/$LOCAL_RESULTS/$1"
mkdir -p "$DEST"
rsync -az "$CLUSTER:$REMOTE_RUNS/$1/" "$DEST/"

shopt -s nullglob
N="$(grep -c '' "$DEST/cmds.txt")"

# A status file is written last and atomically: FAIL is the tool's verdict,
# TIMEOUT is the cap, and an absent status is work lost to a walltime kill or a
# dead node, reclaimable with `oarrun.sh --resume`.
read -r OK TO FAIL DONE < <(cat "$DEST"/status/* 2>/dev/null |
    awk '{ c[$1]++ } END { printf "%d %d %d %d\n", c["OK"], c["TIMEOUT"], c["FAIL"], NR }')

# One CSV per command, header kept once. Written per command rather than appended
# to a shared file because O_APPEND is not atomic over NFS and interleaves under
# fan-out. Row order is not meaningful; the commands run in parallel.
shards=("$DEST"/out/*.csv)
[ "${#shards[@]}" -gt 0 ] && awk 'FNR == 1 && NR != 1 { next } { print }' "${shards[@]}" >"$DEST/results.csv"

echo "$1: $DONE/$N done — $OK ok, $TO timeout, $FAIL fail, $((N - DONE)) missing"
echo "  $DEST"
[ "$DONE" -eq "$N" ]
