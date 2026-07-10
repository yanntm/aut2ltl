#!/bin/bash
# Submit a single command as one cluster job.
#
# A one-liner front end to oarrun.sh: builds a one-line command list and hands
# it over, so the single job gets the same output slot, cap, status accounting
# and reap.sh handling as a sweep. Returns as soon as the job is queued.
#
# Usage: cluster/oarsub.sh [options] <command...>
#   --name SLUG        tag for the run id (default: the command's first word)
#   --timeout SECONDS  wall-clock cap on the command, 0 to disable
#   --cores N          cores requested for the job
#   --walltime H:MM:SS job limit
#   --resources STR    OAR resource string minus walltime
#   --oar-opts STR     extra oarsub options, e.g. --besteffort
#   --dry-run          print what would be submitted
#
# Everything after the options is the command. Quote it, or separate it with
# `--`, when it contains shell metacharacters:
#   cluster/oarsub.sh --timeout 0 'python3 -m survey --folder samples/validation'
#   cluster/oarsub.sh -- python3 -c 'import spot; print(spot.version())'
#
# Prints the run id on stdout; collect with `cluster/reap.sh <runid>`.

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

NAME=""
FORWARD=()
while [ $# -gt 0 ]; do
    case "$1" in
        --name)      NAME="$2"; shift 2 ;;
        --timeout|--walltime|--cores|--resources|--oar-opts)
                     FORWARD+=("$1" "$2"); shift 2 ;;
        --dry-run)   FORWARD+=("$1"); shift ;;
        -h|--help)   sed -n '2,21p' "$0"; exit 0 ;;
        --)          shift; break ;;
        -*)          echo "unknown option: $1" >&2; exit 2 ;;
        *)           break ;;
    esac
done

[ $# -gt 0 ] || { echo "usage: oarsub.sh [options] <command...>" >&2; exit 2; }

# Multiple words are joined verbatim: the job runs the line through `bash -c`,
# so an already-quoted single argument and a bare argv both behave as typed.
CMD="$*"
# The command's program name, without a directory or a script suffix: it becomes
# part of the run id and of the OAR job name.
[ -n "$NAME" ] || NAME="$(basename "${1%% *}" | sed 's/\.[a-zA-Z0-9]*$//')"

CMDS="$(mktemp)"
trap 'rm -f "$CMDS"' EXIT
printf '%s\n' "$CMD" >"$CMDS"

# Not exec'd: the trap must still fire, and oarrun.sh has already copied the
# list to the cluster by the time it returns.
"$HERE/oarrun.sh" --name "$NAME" --split 1 "${FORWARD[@]+"${FORWARD[@]}"}" "$CMDS"
