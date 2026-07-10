#!/bin/bash
# Build ROLL (Regular Omega Language Learning) into the repo's opt/roll prefix.
#
# Not one of the pipeline's native dependencies: ROLL is the external FDFA
# learner the sosl E3 experiments run as their baseline, deployed through deps/
# so a cluster node has it. It has no released distribution, so it is cloned
# from its GitHub at HEAD, packed by the project's own build.sh (mvn package,
# then a repack of the target jars into one self-contained ROLL.jar -- RABIT
# included), installed as opt/roll/ROLL.jar. Pure bytecode: unlike the native
# dependencies the artifact is portable across machine classes.
#
# Needs java, jar and mvn on the machine; nothing is fetched beyond the clone
# and maven's own dependency resolution.
#
# One install, kept as it is. To replace it, `rm -rf opt/roll` and run again.
#
# Usage: deps/build_roll.sh

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
# shellcheck source=versions.sh
source "$HERE/versions.sh"

[ $# -eq 0 ] || { echo "usage: build_roll.sh (no arguments)" >&2; exit 2; }

PREFIX="$ROOT/opt/roll"
SRC="$ROOT/build/roll-library"

log() { echo "[roll] $*"; }
die() { echo "[roll] ERROR: $*" >&2; exit 1; }

if [ -f "$PREFIX/ROLL.jar" ]; then
    log "already built at $PREFIX (rm -rf $PREFIX to rebuild)"
    exit 0
fi

command -v java >/dev/null || die "java not found (a JDK is needed)"
command -v mvn >/dev/null || die "mvn not found (maven is needed)"

# `jar` (and javac, which maven's compile needs) may be off PATH even where
# java is on it -- a distro often symlinks only java into /usr/bin. Resolve
# the JDK from the running java's own java.home and put its bin/ first.
if ! command -v jar >/dev/null; then
    JAVA_HOME="$(java -XshowSettings:properties -version 2>&1 \
                 | sed -n 's/^ *java\.home = //p')"
    { [ -n "$JAVA_HOME" ] && [ -x "$JAVA_HOME/bin/jar" ]; } \
        || die "jar not found and java.home ('$JAVA_HOME') has no bin/jar (a full JDK is needed)"
    export JAVA_HOME
    export PATH="$JAVA_HOME/bin:$PATH"
    log "jar resolved from java.home: $JAVA_HOME/bin"
fi

if [ ! -d "$SRC/.git" ]; then
    log "cloning $ROLL_REPO -> ${SRC#"$ROOT"/}"
    mkdir -p "$(dirname "$SRC")"
    git clone --depth 1 "$ROLL_REPO" "$SRC"
else
    git -C "$SRC" fetch --quiet --depth 1 origin HEAD
    git -C "$SRC" reset --quiet --hard FETCH_HEAD
fi

# The project's build.sh repacks only after a successful mvn package, so a
# leftover jar from an earlier run must not pass as this one's output.
rm -f "$SRC/ROLL.jar"
log "mvn package + repack (the project's own build.sh)"
(cd "$SRC" && /bin/bash ./build.sh)
[ -f "$SRC/ROLL.jar" ] || die "build produced no ROLL.jar (mvn failed?)"

mkdir -p "$PREFIX"
cp "$SRC/ROLL.jar" "$PREFIX/ROLL.jar"

java -jar "$PREFIX/ROLL.jar" help >/dev/null || die "installed jar does not run"
log "ROLL OK in $PREFIX"
