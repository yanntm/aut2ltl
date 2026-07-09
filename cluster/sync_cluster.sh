#!/bin/bash
# Bring the cluster copy of the repo to this working tree's HEAD.
#
# Only committed, pushed artefacts run on the cluster. The cluster is checked
# out at the exact local HEAD commit rather than at the remote's tip, so a run's
# recorded git_rev names the code that ran. Refuses to proceed otherwise: a
# dirty tree or an unpushed commit would silently run something else.
#
# Pushing is never done here. If HEAD is not on the remote, this says so and
# stops; running `git push` is the user's call.
#
# Usage: cluster/sync_cluster.sh [--allow-untracked]

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=config.sh
source "$HERE/config.sh"

ALLOW_UNTRACKED=0
[ "${1:-}" = "--allow-untracked" ] && ALLOW_UNTRACKED=1

ROOT="$(git -C "$HERE" rev-parse --show-toplevel)"
cd "$ROOT"

die() { echo "sync_cluster: $*" >&2; exit 1; }

git diff --quiet || die "working tree has unstaged changes; commit them first"
git diff --cached --quiet || die "index has staged changes; commit them first"

if [ "$ALLOW_UNTRACKED" -eq 0 ] && [ -n "$(git ls-files --others --exclude-standard)" ]; then
    echo "sync_cluster: untracked files present (they will NOT be sent):" >&2
    git ls-files --others --exclude-standard | sed 's/^/  /' >&2
    die "commit them, add them to .gitignore, or pass --allow-untracked"
fi

REV="$(git rev-parse HEAD)"
URL="$(git remote get-url origin)" || die "no 'origin' remote to clone from"

# The cluster fetches from origin, so HEAD must be reachable there. Checked
# against the remote-tracking refs; `git fetch` first if these are stale.
if ! git branch -r --contains "$REV" | grep -q .; then
    die "HEAD ($(git rev-parse --short HEAD)) is not on origin — run 'git push' first"
fi

ssh "$CLUSTER" bash -s <<EOF
set -eu
if [ ! -d "\$HOME/$REMOTE_REPO/.git" ]; then
    mkdir -p "\$(dirname "\$HOME/$REMOTE_REPO")"
    git clone "$URL" "\$HOME/$REMOTE_REPO"
fi
cd "\$HOME/$REMOTE_REPO"
git fetch --quiet origin
# Detached at the exact commit: the cluster tracks this tree, not a branch.
git checkout --quiet --detach "$REV"
git --no-pager log --oneline -1
EOF

echo "cluster at $(git rev-parse --short "$REV") ($CLUSTER:$REMOTE_REPO)"
