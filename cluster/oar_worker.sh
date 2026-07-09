#!/bin/bash
# One OAR job's share of a run's command list, on a compute node.
#
# Takes every <split>-th command starting at <shard>, so the shards interleave
# rather than partition into contiguous blocks: a command list ordered by
# difficulty spreads evenly instead of piling the hard tail onto one job.
#
# Usage: oar_worker.sh <rundir> <shard> <split> <timeout_seconds> <cores|auto>

set -uo pipefail

RUNDIR="$1"
SHARD="$2"
SPLIT="$3"
TIMEOUT="$4"
CORES="$5"

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=env.sh
source "$HERE/env.sh"

# The fleet is heterogeneous, so the width is discovered rather than requested up
# front. Asked of OAR, not of the machine: $OAR_NODEFILE holds one line per core
# actually allocated to this job, whereas nproc reports the whole node and would
# oversubscribe whatever else is running on it.
if [ "$CORES" = auto ]; then
    if [ -n "${OAR_NODEFILE:-}" ] && [ -s "$OAR_NODEFILE" ]; then
        CORES="$(grep -c '' "$OAR_NODEFILE")"
    else
        CORES=1   # not under OAR: no allocation to read, so take one lane
    fi
fi

# Commands run with the repo root as working directory; every path they use, and
# every path in this tree, resolves from there.
cd "$OARRUN_ROOT" || exit 1

N="$(grep -c '' "$RUNDIR/cmds.txt")"
echo "shard $SHARD/$SPLIT of $N commands on $(hostname -s), $CORES wide, cap ${TIMEOUT}s"

seq 1 "$N" \
    | awk -v s="$SPLIT" -v k="$SHARD" '(NR - 1) % s == k' \
    | xargs -P "$CORES" -n 1 -I{} "$HERE/oar_one.sh" "$RUNDIR" {} "$TIMEOUT"

echo "shard $SHARD done"
