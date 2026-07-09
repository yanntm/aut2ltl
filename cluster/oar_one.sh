#!/bin/bash
# Run one command of a run's command list, on a compute node.
#
# Invoked by oar_worker.sh, once per command, up to <cores> at a time. Writes
# exactly one status file, last, and atomically: its presence means the command
# is finished and must not be re-run, which is what makes --resume correct after
# a walltime kill.
#
# Usage: oar_one.sh <rundir> <idx> <timeout_seconds>
#   idx is 1-based into <rundir>/cmds.txt; timeout 0 disables the cap.

set -uo pipefail

RUNDIR="$1"
IDX="$2"
TIMEOUT="$3"

STATUS="$RUNDIR/status/$IDX"
[ -s "$STATUS" ] && exit 0

CMD="$(sed -n "${IDX}p" "$RUNDIR/cmds.txt")"
[ -z "$CMD" ] && exit 0

# Handed to the command: a private output slot it may use as a file or create
# as a directory. Per-command rather than shared, because appending to one file
# from many nodes over NFS is not atomic and interleaves under load. reap.sh
# concatenates the shards in index order.
export OARRUN_RUN="$RUNDIR"
export OARRUN_IDX="$IDX"
export OARRUN_OUT="$RUNDIR/out/$IDX"

START="$(date +%s)"
if [ "$TIMEOUT" -gt 0 ]; then
    stdbuf -oL -eL timeout -k 5 "$TIMEOUT" bash -c "$CMD" \
        >"$RUNDIR/logs/$IDX.out" 2>"$RUNDIR/logs/$IDX.err"
else
    stdbuf -oL -eL bash -c "$CMD" \
        >"$RUNDIR/logs/$IDX.out" 2>"$RUNDIR/logs/$IDX.err"
fi
RC=$?
END="$(date +%s)"

# 124 is timeout(1)'s own verdict; 137 is the SIGKILL that follows -k.
case "$RC" in
    0)        STATE=OK ;;
    124|137)  STATE=TIMEOUT ;;
    *)        STATE=FAIL ;;
esac

# Write elsewhere and rename: a reader never sees a half-written status file,
# and a node dying mid-write leaves no status at all (counted as missing).
TMP="$STATUS.tmp.$$"
printf '%s %d %d %s\n' "$STATE" "$RC" "$((END - START))" "$(hostname -s)" >"$TMP"
mv -f "$TMP" "$STATUS"
