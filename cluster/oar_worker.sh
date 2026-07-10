#!/bin/bash
# One OAR job's share of a run's command list, on a compute node.
#
# Takes every <split>-th command starting at <shard>, so the shards interleave
# rather than partition into contiguous blocks: a command list ordered by
# difficulty spreads evenly instead of piling the hard tail onto one job.
#
# Usage: oar_worker.sh <rundir> <shard> <split> <timeout_seconds>

set -uo pipefail

RUNDIR="$1"
SHARD="$2"
SPLIT="$3"
TIMEOUT="$4"

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=../deps/env.sh
source "$HERE/../deps/env.sh"

# The repo root, under the name the commands are promised. env.sh found it.
export OARRUN_ROOT="$AUT2LTL_ROOT"

# Width comes from OAR, not from the machine: $OAR_NODEFILE holds one line per
# core actually allocated, whereas nproc reports the whole node and would
# oversubscribe whatever else runs on it. One lane when not under OAR.
CORES=1
[ -s "${OAR_NODEFILE:-}" ] && CORES="$(grep -c '' "$OAR_NODEFILE")"

# Commands run with the repo root as working directory; every path they use, and
# every path in this tree, resolves from there.
cd "$OARRUN_ROOT" || exit 1

N="$(grep -c '' "$RUNDIR/cmds.txt")"
echo "shard $SHARD/$SPLIT of $N commands on $(hostname -s), $CORES wide, cap ${TIMEOUT}s"

seq 1 "$N" \
    | awk -v s="$SPLIT" -v k="$SHARD" '(NR - 1) % s == k' \
    | xargs -P "$CORES" -n 1 -I{} "$HERE/oar_one.sh" "$RUNDIR" {} "$TIMEOUT"

echo "shard $SHARD done"
