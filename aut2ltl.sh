#!/bin/bash
# Run python3 against this checkout's own dependencies.
#
# A thin wrapper: it puts opt/ on PATH, LD_LIBRARY_PATH and PYTHONPATH, then
# hands every argument to python3 unchanged. So it is used exactly as python3 is:
#
#   ./aut2ltl.sh -m aut2ltl samples/foo.hoa
#   ./aut2ltl.sh -m survey --folder samples/validation
#
# The checkout is found from this script's own location, with symlinks resolved,
# so a link to it from anywhere on PATH works and no path is compiled in.

set -euo pipefail

HERE="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")" && pwd)"
# shellcheck source=deps/env.sh
source "$HERE/deps/env.sh"

exec python3 "$@"
