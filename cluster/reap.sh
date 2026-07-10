#!/bin/bash
# Fetch a run's results and report how much of it exists.
#
# Additive and idempotent: it copies down whatever has been written so far and
# tallies it against the command count, so it is safe to call while jobs are
# still running, and calling it twice is how progress is observed. The only
# thing it does on the cluster is read files.
#
# A command's status file is written last and atomically, so the split below is
# meaningful: FAIL is the tool's verdict, TIMEOUT is the cap, and a missing
# status is work *we* lost and can reclaim with `oarrun.sh --resume`.
#
# Usage: cluster/reap.sh [--quiet] <runid>

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
# shellcheck source=config.sh
source "$HERE/config.sh"

QUIET=0
[ "${1:-}" = "--quiet" ] && { QUIET=1; shift; }
[ $# -eq 1 ] || { echo "usage: reap.sh [--quiet] <runid>" >&2; exit 2; }
RUNID="$1"

DEST="$ROOT/$LOCAL_RESULTS/$RUNID"
mkdir -p "$DEST"
rsync -az "$CLUSTER:$REMOTE_RUNS/$RUNID/" "$DEST/"

[ -s "$DEST/cmds.txt" ] || { echo "no command list in $DEST — unknown run id?" >&2; exit 2; }
N="$(grep -c '' "$DEST/cmds.txt")"

read -r OK TIMEOUT FAIL < <(
    cat "$DEST"/status/* 2>/dev/null \
        | awk '{ c[$1]++ } END { printf "%d %d %d\n", c["OK"], c["TIMEOUT"], c["FAIL"] }'
)
DONE=$((OK + TIMEOUT + FAIL))

# Per-command CSV shards, concatenated in index order with one header. Written
# per command rather than appended to a shared file because O_APPEND is not
# atomic over NFS and interleaves under fan-out.
SHARDS=("$DEST"/out/*.csv)
if [ -e "${SHARDS[0]}" ]; then
    printf '%s\n' "${SHARDS[@]}" | sort -t/ -k2 -n \
        | xargs awk 'FNR == 1 && NR != 1 { next } { print }' >"$DEST/results.csv"
fi

echo "$RUNID: $DONE/$N done — $OK ok, $TIMEOUT timeout, $FAIL fail, $((N - DONE)) missing"
[ "$QUIET" -eq 1 ] && exit 0

echo "  fetched to $DEST"
for f in "$DEST"/status/*; do
    case "$(head -c 4 "$f" 2>/dev/null)" in
        FAIL) i="${f##*/}"
              printf '    FAIL [%s] %s\n' "$i" "$(sed -n "${i}p" "$DEST/cmds.txt")" ;;
    esac
done
exit 0
