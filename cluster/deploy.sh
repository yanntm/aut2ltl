#!/bin/bash
# Provision the cluster: one OAR job per dependency, in parallel.
#
# Spot, GAP and libDDD/libITS are independent and write to disjoint prefixes
# under opt/, so they build at the same time on three machines rather than one
# after another on one.
#
# Usage: cluster/deploy.sh [--force] [oarrun options...]
#   --force  rebuild each prefix even when its version stamp matches
#
# Prints the run id. Collect with `cluster/reap.sh <runid>`; it reports 3/3 when
# all three are done, and names the one that failed otherwise.

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=config.sh
source "$HERE/config.sh"

FORCE=""
if [ "${1:-}" = "--force" ]; then FORCE=" --force"; shift; fi

CMDS="$(mktemp)"
trap 'rm -f "$CMDS"' EXIT
cat >"$CMDS" <<EOF
cluster/provision.sh --spot-only$FORCE
cluster/provision.sh --gap-only$FORCE
cluster/provision.sh --its-only$FORCE
EOF

# --timeout 0: a compile is bounded by the walltime, not by the per-command cap.
# --cores matches BUILD_JOBS, the width every build actually uses.
"$HERE/oarrun.sh" \
    --name provision \
    --split 3 \
    --cores "$BUILD_JOBS" \
    --timeout 0 \
    --walltime "$SPOT_BUILD_WALLTIME" \
    "$@" \
    "$CMDS"
