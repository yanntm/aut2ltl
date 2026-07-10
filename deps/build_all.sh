#!/bin/bash
# Build every native dependency into the repo's own opt/.
#
# Self-contained by design: no root, no $HOME, nothing system-wide. A Linux box
# with a compiler, make and curl (or wget) ends up able to run the whole
# pipeline, and deleting opt/ and build/ undoes it exactly.
#
#   deps/build_all.sh              # spot + gap + its
#   deps/build_all.sh --spot-only
#   deps/build_all.sh --gap-only
#   deps/build_all.sh --its-only
#
# A dependency already built into opt/ is left alone. To replace one, remove its
# prefix -- `rm -rf opt/gap` -- and run this again.
#
# Ends by proving what the rest of the pipeline needs: `import spot`, and a `gap`
# on PATH that loads SgpDec -- each resolving from opt/, not from a system
# install that merely happens to answer.

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"

DO_SPOT=1
DO_GAP=1
DO_ITS=1

case "${1:-}" in
    "")          ;;
    --spot-only) DO_GAP=0; DO_ITS=0 ;;
    --gap-only)  DO_SPOT=0; DO_ITS=0 ;;
    --its-only)  DO_SPOT=0; DO_GAP=0 ;;
    -h|--help)   sed -n '2,17p' "$0"; exit 0 ;;
    *)           echo "unknown option: $1" >&2; exit 2 ;;
esac

cd "$ROOT"

if [ "$DO_SPOT" -eq 1 ]; then
    echo "=== spot"
    "$HERE/build_spot.sh"
fi

if [ "$DO_GAP" -eq 1 ]; then
    echo "=== gap"
    "$HERE/build_gap.sh"
fi

if [ "$DO_ITS" -eq 1 ]; then
    echo "=== libDDD + libITS"
    "$HERE/build_its.sh"
fi

echo "=== verify"
# shellcheck source=env.sh
source "$HERE/env.sh"

# Only what this invocation built: the three dependencies are independent.
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

echo "built into $ROOT/opt"
