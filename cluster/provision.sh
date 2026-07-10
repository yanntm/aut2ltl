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
#   cluster/provision.sh              # spot + gap + its
#   cluster/provision.sh --spot-only
#   cluster/provision.sh --gap-only
#   cluster/provision.sh --its-only
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
case "${1:-}" in
    --spot-only) DO_GAP=0; DO_ITS=0 ;;
    --gap-only)  DO_SPOT=0; DO_ITS=0 ;;
    --its-only)  DO_SPOT=0; DO_GAP=0 ;;
    "")          ;;
    -h|--help)   sed -n '2,19p' "$0"; exit 0 ;;
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

echo "=== verify (as a job would see it)"
# shellcheck source=env.sh
source "$HERE/env.sh"

# Resolved through PATH, then checked to be the one under opt/: a bare name that
# silently found a system install would verify the wrong thing entirely.
for tool in python3 gap ltl2tgba; do
    case "$tool" in python3) continue ;; esac
    resolved="$(command -v "$tool" || true)"
    case "$resolved" in
        "$ROOT/opt/"*) ;;
        *) echo "verify: $tool resolves to '${resolved:-nothing}', not under $ROOT/opt" >&2; exit 1 ;;
    esac
done

python3 -c 'import spot, pathlib, sys
root = pathlib.Path(sys.argv[1]).resolve()
mod = pathlib.Path(spot.__file__).resolve()
if root / "opt" not in mod.parents and not str(mod).startswith(str(root / "opt")):
    sys.exit(f"verify: spot imported from {mod}, not from {root}/opt")
print("spot", spot.version(), "| accsets", spot.mark_t.max_accsets())' "$ROOT"

gap --bare -q -c 'Print("gap ", GAPInfo.Version, "\n");
                  if LoadPackage("SgpDec") = fail then Print("SGPDEC FAIL\n"); else Print("SgpDec OK\n"); fi;
                  QUIT;'
echo "provisioned into $ROOT/opt"
