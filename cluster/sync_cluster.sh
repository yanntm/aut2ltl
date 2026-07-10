#!/bin/bash
# Update the cluster's checkout from origin.
#
# The cluster runs what is on origin. Nothing local is consulted: not the working
# tree, not HEAD.
#
# It lands on master and fast-forwards. Never a detached HEAD: the checkout stays
# a repository someone can `git pull` in, and a fast-forward that cannot happen
# is a report rather than a silent reset -- the cluster's tree is not a scratch
# copy, and a commit made there by hand is worth noticing before it is lost.
#
# Usage: cluster/sync_cluster.sh

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=config.sh
source "$HERE/config.sh"

[ $# -eq 0 ] || { echo "usage: sync_cluster.sh (no arguments)" >&2; exit 2; }

ssh "$CLUSTER" bash -s <<EOF
set -eu
cd "\$HOME/$REMOTE_REPO"
git fetch --quiet origin
git checkout --quiet master
git merge --ff-only origin/master
git --no-pager log --oneline -1
EOF
