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
#   cluster/provision.sh              # spot + gap
#   cluster/provision.sh --spot-only
#   cluster/provision.sh --gap-only
#
# Ends by proving what the rest of the pipeline needs: `import spot`, and a
# `gap` on PATH that loads SgpDec.

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"

DO_SPOT=1
DO_GAP=1
case "${1:-}" in
    --spot-only) DO_GAP=0 ;;
    --gap-only)  DO_SPOT=0 ;;
    "")          ;;
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
    # Chooses the distro package when one is usable and root is available,
    # builds from source otherwise; either way SgpDec and the wrapper land in
    # opt/gap.
    "$ROOT/install_gap.sh"
fi

echo "=== verify (as a job would see it)"
# shellcheck source=env.sh
source "$HERE/env.sh"
python3 -c 'import spot; print("spot", spot.version())'
command -v gap && gap --no-window --bare -c 'if LoadPackage("SgpDec") = fail then Print("SGPDEC FAIL\n"); else Print("SgpDec OK\n"); fi; QUIT;'
echo "provisioned into $ROOT/opt"
