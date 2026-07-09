#!/bin/bash
# Submit a list of shell commands to the cluster as <split> OAR jobs.
#
# The command list is opaque: one shell command per line, run from the repo root
# on a compute node. Each gets a wall-clock cap and a private output slot
# ($OARRUN_OUT); results are collected later, and independently, by reap.sh.
#
# Nothing is left running on the submit host: this makes <split> immediate
# oarsub calls and exits. Progress is observed by running reap.sh, not by
# waiting here.
#
# Usage: cluster/oarrun.sh [options] <cmds.txt>
#   --name SLUG        tag for the run id (default: basename of cmds.txt)
#   --timeout SECONDS  per-command cap, 0 to disable (default: $OARRUN_TIMEOUT)
#   --split K          spread over K jobs / K nodes (default: $OARRUN_SPLIT)
#   --cores N|auto     commands in flight per node (default: $OARRUN_CORES)
#   --walltime H:MM:SS per-job limit (default: $OARRUN_WALLTIME)
#   --resources STR    OAR resource string minus walltime
#   --oar-opts STR     extra oarsub options, e.g. --besteffort
#   --resume RUNID     re-submit into an existing run, skipping finished commands
#   --dry-run          print the oarsub calls, submit nothing
#
# Prints the run id on stdout; pass it to reap.sh.

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=config.sh
source "$HERE/config.sh"

NAME=""
DRY=0
RESUME=""
while [ $# -gt 0 ]; do
    case "$1" in
        --name)      NAME="$2"; shift 2 ;;
        --timeout)   OARRUN_TIMEOUT="$2"; shift 2 ;;
        --split)     OARRUN_SPLIT="$2"; shift 2 ;;
        --cores)     OARRUN_CORES="$2"; shift 2 ;;
        --walltime)  OARRUN_WALLTIME="$2"; shift 2 ;;
        --resources) OARRUN_RESOURCES="$2"; shift 2 ;;
        --oar-opts)  OARRUN_OAR_OPTS="$2"; shift 2 ;;
        --resume)    RESUME="$2"; shift 2 ;;
        --dry-run)   DRY=1; shift ;;
        -h|--help)   sed -n '2,26p' "$0"; exit 0 ;;
        -*)          echo "unknown option: $1" >&2; exit 2 ;;
        *)           break ;;
    esac
done

if [ -n "$RESUME" ]; then
    # Re-submit into the existing run directory. Its cmds.txt is authoritative;
    # oar_one.sh skips any command that already has a status file, so the new
    # jobs only pick up what a walltime kill or an eviction left behind.
    [ $# -eq 0 ] || { echo "--resume takes no command list" >&2; exit 2; }
    RUNID="$RESUME"
    RUNDIR="$REMOTE_RUNS/$RUNID"
    ssh "$CLUSTER" "test -s '$RUNDIR/cmds.txt'" \
        || { echo "no such run on $CLUSTER: $RUNID" >&2; exit 2; }
    N="$(ssh "$CLUSTER" "grep -c '' '$RUNDIR/cmds.txt'")"
else
    [ $# -eq 1 ] || { echo "usage: oarrun.sh [options] <cmds.txt>" >&2; exit 2; }
    CMDS="$1"
    [ -s "$CMDS" ] || { echo "empty or missing command list: $CMDS" >&2; exit 2; }
    N="$(grep -c '' "$CMDS")"
    [ -z "$NAME" ] && NAME="$(basename "$CMDS" .txt)"
    RUNID="$(date +%Y%m%d-%H%M%S)-$NAME"
    RUNDIR="$REMOTE_RUNS/$RUNID"
fi

# A job holds a whole node, so the shard is sized to the walltime rather than
# the reverse. Advisory only: OAR schedules what we submit, a job killed at
# walltime keeps its finished results, and --resume makes finishing cheap.
if [ "$OARRUN_TIMEOUT" -gt 0 ]; then
    WT_SECONDS="$(awk -F: '{print $1 * 3600 + $2 * 60 + $3}' <<<"$OARRUN_WALLTIME")"
    WORST="$(( (N + OARRUN_SPLIT * OARRUN_ASSUMED_CORES - 1) \
               / (OARRUN_SPLIT * OARRUN_ASSUMED_CORES) * OARRUN_TIMEOUT ))"
    if [ "$WORST" -gt "$WT_SECONDS" ]; then
        SUGGEST="$(( (WORST + WT_SECONDS - 1) / WT_SECONDS * OARRUN_SPLIT ))"
        echo "warning: worst case ~${WORST}s per shard exceeds walltime ${OARRUN_WALLTIME}" >&2
        echo "         (assuming $OARRUN_ASSUMED_CORES cores/node); consider --split $SUGGEST" >&2
    fi
fi

GITREV="$(git -C "$HERE" rev-parse --short HEAD 2>/dev/null || echo unknown)"
GITDIRTY=false
git -C "$HERE" diff --quiet 2>/dev/null || GITDIRTY=true

META="$(mktemp)"
trap 'rm -f "$META"' EXIT
cat >"$META" <<EOF
{
  "runid": "$RUNID",
  "commands": $N,
  "timeout_seconds": $OARRUN_TIMEOUT,
  "split": $OARRUN_SPLIT,
  "cores": "$OARRUN_CORES",
  "walltime": "$OARRUN_WALLTIME",
  "resources": "$OARRUN_RESOURCES",
  "git_rev": "$GITREV",
  "git_dirty": $GITDIRTY,
  "submitted_at": "$(date -Is)",
  "submitted_from": "$(hostname -s)"
}
EOF

if [ "$DRY" -eq 1 ]; then
    echo "would submit $OARRUN_SPLIT job(s) for $N commands as $RUNID"
    echo "  oarsub $OARRUN_OAR_OPTS -n $RUNID.K -l $OARRUN_RESOURCES,walltime=$OARRUN_WALLTIME \\"
    echo "    \"\$HOME/$REMOTE_REPO/cluster/oar_worker.sh \$HOME/$RUNDIR K $OARRUN_SPLIT $OARRUN_TIMEOUT $OARRUN_CORES\""
    exit 0
fi

if [ -z "$RESUME" ]; then
    ssh "$CLUSTER" "mkdir -p '$RUNDIR'/{out,logs,status,oar}"
    scp -q "$CMDS" "$CLUSTER:$RUNDIR/cmds.txt"
    scp -q "$META" "$CLUSTER:$RUNDIR/meta.json"
else
    scp -q "$META" "$CLUSTER:$RUNDIR/meta.resume-$(date +%s).json"
fi

# oarsub deposits OAR.<jobid>.std{out,err} in its working directory; keep them
# with the run. Each call returns as soon as the job is queued, so nothing of
# ours is left running on the submit host.
ssh "$CLUSTER" bash -s <<EOF
set -eu
cd "\$HOME/$RUNDIR/oar"
for k in \$(seq 0 $((OARRUN_SPLIT - 1))); do
    oarsub $OARRUN_OAR_OPTS \
        -n "$RUNID.\$k" \
        -l "$OARRUN_RESOURCES,walltime=$OARRUN_WALLTIME" \
        "\$HOME/$REMOTE_REPO/cluster/oar_worker.sh \$HOME/$RUNDIR \$k $OARRUN_SPLIT $OARRUN_TIMEOUT $OARRUN_CORES" \
        | sed -n 's/^OAR_JOB_ID=//p'
done >>"\$HOME/$RUNDIR/oar/jobs.txt"
echo "submitted $OARRUN_SPLIT job(s) for $N command(s) as $RUNID" >&2
EOF

echo "$RUNID"
