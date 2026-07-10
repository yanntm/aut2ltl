#!/bin/bash
# Submit a single command as one cluster job.
#
# A front end to oarrun.sh: builds a one-line command list and hands it over, so
# the single job gets the same output slot, cap, status accounting and reap.sh
# handling as a sweep.
#
# Usage: cluster/oarsub.sh [oarrun options...] -- <command...>
#   Everything before `--` goes to oarrun.sh (see its --help); everything after
#   is the command, run through `bash -c` from the repo root. Several words are
#   an argv, reproduced on the node exactly as given; for shell syntax (pipes,
#   `&&`, redirects), pass the whole line as ONE quoted argument, taken verbatim.
#
#   cluster/oarsub.sh --timeout 0 -- python3 -m survey --folder samples/validation
#   cluster/oarsub.sh -- 'source deps/env.sh && java -jar "$ROLL_JAR" help'
#
# Prints the run id on stdout; collect with `cluster/reap.sh <runid>`.

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

OPTS=()
while [ $# -gt 0 ] && [ "$1" != "--" ]; do
    OPTS+=("$1"); shift
done
[ "${1:-}" = "--" ] && shift
[ $# -gt 0 ] || { echo "usage: oarsub.sh [oarrun options...] -- <command...>" >&2; exit 2; }

CMDS="$(mktemp)"
trap 'rm -f "$CMDS"' EXIT
# One argument is a shell line, taken verbatim -- cmds.txt semantics. Several
# arguments are an argv: re-quote each word, because quoting does not survive
# a bare "$*" join -- the node's `bash -c` would take only the first word as
# its script (e.g. `-- bash -c 'a && b'` used to run the one-word script
# `bash -c a` with the rest re-parsed by the outer shell).
if [ $# -eq 1 ]; then
    printf '%s\n' "$1" >"$CMDS"
else
    LINE="$(printf '%q ' "$@")"
    printf '%s\n' "${LINE% }" >"$CMDS"
fi

# Not exec'd: the trap must still fire, and oarrun.sh has copied the list to the
# cluster by the time it returns. --name defaults to the command's program.
"$HERE/oarrun.sh" --name "$(basename "${1%% *}" .sh)" --split 1 \
    "${OPTS[@]+"${OPTS[@]}"}" "$CMDS"
