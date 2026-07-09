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

# The fleet is heterogeneous and a job holds a whole node, so the width is read
# from the machine we actually landed on rather than requested up front.
[ "$CORES" = auto ] && CORES="$(nproc)"

cd "$OARRUN_REPO" || exit 1

N="$(grep -c '' "$RUNDIR/cmds.txt")"
echo "shard $SHARD/$SPLIT of $N commands on $(hostname -s), $CORES wide, cap ${TIMEOUT}s"

seq 1 "$N" \
    | awk -v s="$SPLIT" -v k="$SHARD" '(NR - 1) % s == k' \
    | xargs -P "$CORES" -n 1 -I{} "$HERE/oar_one.sh" "$RUNDIR" {} "$TIMEOUT"

echo "shard $SHARD done"
