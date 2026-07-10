#!/bin/bash
# Provision the cluster: one OAR job per dependency, in parallel.
#
# Spot, GAP and libDDD/libITS are independent and write to disjoint prefixes
# under opt/, so they build at the same time on three machines rather than one
# after another on one.
#
# A dependency already built into opt/ is left alone. To replace one, remove its
# prefix on the cluster -- `rm -rf opt/gap` -- and submit again.
#
# Usage: cluster/deploy.sh [oarrun options...]
#
# Prints the run id. Collect with `cluster/reap.sh <runid>`; it reports 3/3 when
# all three are done, and names the one that failed otherwise.

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=config.sh
source "$HERE/config.sh"
# For BUILD_JOBS: the jobs submitted here are builds, and ask for the width the
# build scripts use.
# shellcheck source=../deps/versions.sh
source "$HERE/../deps/versions.sh"

CMDS="$(mktemp)"
trap 'rm -f "$CMDS"' EXIT
cat >"$CMDS" <<EOF
deps/build_all.sh --spot-only
deps/build_all.sh --gap-only
deps/build_all.sh --its-only
EOF

# --timeout 0: a compile is bounded by the walltime, not by the per-command cap.
# --cores matches BUILD_JOBS, the width every build actually uses.
"$HERE/oarrun.sh" \
    --name deps \
    --split 3 \
    --cores "$BUILD_JOBS" \
    --timeout 0 \
    --walltime "$DEPS_BUILD_WALLTIME" \
    "$@" \
    "$CMDS"
