#!/bin/bash
# Update the cluster's checkout from origin.
#
# The cluster runs what is on origin. Nothing else is consulted: no local
# working tree, no local HEAD.
#
# Usage: cluster/sync_cluster.sh [rev]
#   rev   commit, tag or branch to check out (default: origin/master)

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=config.sh
source "$HERE/config.sh"

REV="${1:-origin/master}"

ssh "$CLUSTER" bash -s <<EOF
set -eu
cd "\$HOME/$REMOTE_REPO"
git fetch --quiet origin
git checkout --quiet --detach "$REV"
git --no-pager log --oneline -1
EOF
