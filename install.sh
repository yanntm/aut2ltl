#!/bin/bash
# Build this checkout's dependencies and make the aut2ltl wrapper reachable.
#
# Run once, from a fresh clone. It builds Spot, GAP + SgpDec and libDDD + libITS
# into opt/ (see deps/), then checks that the wrapper resolves each of them.
# Nothing is installed system-wide and nothing needs root.
#
#   ./install.sh
#
# The build takes a while: semigroups vendors libsemigroups and Spot is large.
# A dependency already built into opt/ is left alone; to replace one, remove its
# prefix -- `rm -rf opt/spot` -- and run this again.
#
# The dependencies are compiled for the machine that builds them, AVX2 included.
# A checkout shared between machines must be built on, and used from, machines
# with the same instruction set.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

[ $# -eq 0 ] || { echo "usage: install.sh (no arguments)" >&2; exit 2; }

"$ROOT/deps/build_all.sh"

echo "=== verify"
# Through the wrapper, which is how the tool is run: this proves the wrapper's
# own environment, not merely that the builds exist.
"$ROOT/aut2ltl.sh" -c 'import spot; print("spot", spot.version())'
"$ROOT/aut2ltl.sh" -c 'import aut2ltl; print("aut2ltl imported")'

echo
echo "done. run the tool with:"
echo "  ./aut2ltl.sh -m aut2ltl --help"
