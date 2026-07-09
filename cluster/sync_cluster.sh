#!/bin/bash
# Push the working tree to the cluster copy of the repo.
#
# One-way, laptop -> cluster. Uses rsync rather than a cluster-side `git pull`
# so that uncommitted work runs without first being committed. Excludes are in
# cluster/rsync-exclude; run directories live outside the repo, so --delete
# cannot reach them.
#
# Usage: cluster/sync_cluster.sh [-n|--dry-run] [rsync options...]

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=config.sh
source "$HERE/config.sh"

ROOT="$(git -C "$HERE" rev-parse --show-toplevel)"

ssh "$CLUSTER" "mkdir -p '$REMOTE_REPO' '$REMOTE_RUNS'"

rsync -az --delete \
      --exclude-from="$HERE/rsync-exclude" \
      "$@" \
      "$ROOT/" "$CLUSTER:$REMOTE_REPO/"

echo "synced $ROOT -> $CLUSTER:$REMOTE_REPO"
