#!/bin/bash
# Build every native dependency into the repo's own opt/, from scratch.
#
# Self-contained by design: no root, no $HOME, nothing system-wide. A raw Linux
# box with a compiler, make and curl (or wget) ends up able to run the whole
# pipeline, and deleting opt/ and build/ undoes it exactly.
#
# Runnable anywhere. On the cluster it is submitted as an ordinary job, because
# the submit host cannot compile:
#   cluster/oarsub.sh --timeout 0 --walltime 3:00:00 -- cluster/provision.sh
# On a laptop or a container, just run it.
#
#   cluster/provision.sh              # spot + gap + its; keeps what is current
#   cluster/provision.sh --force      # rebuild and replace every prefix
#   cluster/provision.sh --spot-only
#   cluster/provision.sh --gap-only
#   cluster/provision.sh --its-only
#
# Each dependency keeps one install, stamped with its version. A run reuses a
# prefix whose stamp matches and replaces it otherwise, so --force is needed
# only to rebuild the same version.
#
# Ends by proving what the rest of the pipeline needs: `import spot`, and a
# `gap` on PATH that loads SgpDec -- each resolving from opt/, not from a system
# install that merely happens to answer.

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"

DO_SPOT=1
DO_GAP=1
DO_ITS=1
FORCE=()
while [ $# -gt 0 ]; do
    case "$1" in
        --force)     FORCE=(--rebuild); shift ;;
        --spot-only) DO_GAP=0; DO_ITS=0; shift ;;
        --gap-only)  DO_SPOT=0; DO_ITS=0; shift ;;
        --its-only)  DO_SPOT=0; DO_GAP=0; shift ;;
        -h|--help)   sed -n '2,24p' "$0"; exit 0 ;;
        *)           echo "unknown option: $1" >&2; exit 2 ;;
    esac
done

cd "$ROOT"

if [ "$DO_SPOT" -eq 1 ]; then
    echo "=== spot"
    "$HERE/build_spot.sh" "${FORCE[@]+"${FORCE[@]}"}"
fi

if [ "$DO_GAP" -eq 1 ]; then
    echo "=== gap"
    "$HERE/build_gap.sh" "${FORCE[@]+"${FORCE[@]}"}"
fi

if [ "$DO_ITS" -eq 1 ]; then
    echo "=== libDDD + libITS"
    "$HERE/build_its.sh" "${FORCE[@]+"${FORCE[@]}"}"
fi

echo "=== verify (as a job would see it)"
# shellcheck source=env.sh
source "$HERE/env.sh"

# Only what this invocation built: the three dependencies are independent, and
# each is submitted as its own job.
if [ "$DO_SPOT" -eq 1 ]; then
    python3 -c 'import spot; print("spot", spot.version(), "| accsets", spot.mark_t.max_accsets(), "|", spot.__file__)'
fi

if [ "$DO_GAP" -eq 1 ]; then
    gap --bare -q -c 'Print("gap ", GAPInfo.Version, "\n");
                      if LoadPackage("SgpDec") = fail then Print("SGPDEC FAIL\n"); else Print("SgpDec OK\n"); fi;
                      QUIT;'
fi

if [ "$DO_ITS" -eq 1 ]; then
    ls -l "$ROOT/opt/its/lib/libDDD.a" "$ROOT/opt/its/lib/libITS.a"
fi

echo "provisioned into $ROOT/opt"
