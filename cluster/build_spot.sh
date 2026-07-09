#!/bin/bash
# Build Spot with Python bindings and install it under the repo's opt/.
#
# Spot-BinaryBuilds is the source of version truth, not of the source itself: it
# is cloned only to read which Spot release we track (often a tagged dev
# revision) and where its tarball lives. Its own build recipe targets ITS-Tools,
# producing static archives with `--disable-shared` and no Python bindings, so
# the recipe here is ours: shared libraries, bindings enabled, and the higher
# acceptance-set ceiling.
#
# Everything stays inside the repo: the clone and the build tree under build/,
# the install under opt/. Nothing is written to $HOME, nothing needs root, and
# `rm -rf opt build` undoes it exactly.
#
# Usage: cluster/build_spot.sh [spot_version]
#   spot_version overrides what the clone says, e.g. 2.14.5.dev

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
# shellcheck source=config.sh
source "$HERE/config.sh"

TRUTH="$ROOT/build/Spot-BinaryBuilds"
DL="$ROOT/build/dl"
mkdir -p "$DL"

# --- version truth -----------------------------------------------------------

if [ ! -d "$TRUTH/.git" ]; then
    echo "cloning $SPOT_SRC_REPO (version truth)"
    mkdir -p "$(dirname "$TRUTH")"
    git clone --depth 1 "$SPOT_SRC_REPO" "$TRUTH"
else
    git -C "$TRUTH" fetch --quiet --depth 1 origin HEAD
    git -C "$TRUTH" reset --quiet --hard FETCH_HEAD
fi

RECIPE="$TRUTH/build_spot.sh"
[ -f "$RECIPE" ] || { echo "no build_spot.sh in $TRUTH" >&2; exit 1; }

# The live assignment, not the commented-out alternatives above it.
SPOTVER="${1:-$(sed -n 's/^export SPOTVER=\([^ #]*\).*/\1/p' "$RECIPE" | tail -1)}"
[ -n "$SPOTVER" ] || { echo "could not read SPOTVER from $RECIPE" >&2; exit 1; }

# Likewise the live wget line: the tarball moves between hosts across versions,
# so the URL is read rather than hardcoded.
URL="$(grep -E '^[[:space:]]*wget' "$RECIPE" | tail -1 \
       | grep -oE 'https?://[^[:space:]]+' \
       | sed "s/\$SPOTVER/$SPOTVER/g; s/\${SPOTVER}/$SPOTVER/g")"
[ -n "$URL" ] || { echo "could not read the tarball URL from $RECIPE" >&2; exit 1; }

echo "spot $SPOTVER"
echo "  from $URL"

# --- fetch -------------------------------------------------------------------

TARBALL="$DL/spot-$SPOTVER.tar.gz"
if [ ! -s "$TARBALL" ]; then
    curl -fL --no-progress-meter -o "$TARBALL.part" "$URL" \
        || wget -q --no-check-certificate -O "$TARBALL.part" "$URL" \
        || { echo "could not download $URL" >&2; exit 1; }
    mv -f "$TARBALL.part" "$TARBALL"
fi

SRC="$ROOT/build/spot-$SPOTVER"
if [ ! -x "$SRC/configure" ]; then
    rm -rf "$SRC"
    tar -xzf "$TARBALL" -C "$ROOT/build"
    [ -x "$SRC/configure" ] || { echo "unexpected tarball layout: no $SRC/configure" >&2; exit 1; }
fi

# --- build -------------------------------------------------------------------

PREFIX="$ROOT/opt/spot-$SPOTVER"
BUILD="$ROOT/build/spot-$SPOTVER-build"

echo "building on $(hostname -s), make -j$BUILD_JOBS"
echo "  prefix $PREFIX"

mkdir -p "$BUILD"
cd "$BUILD"

# Out-of-tree, so the unpacked source stays reusable and a stale config.cache
# never survives a version bump.
#
# Ours, and deliberately not theirs: shared libraries and Python bindings,
# because the pipeline does `import spot`. --enable-max-accsets=64 lifts Spot's
# default 32-acceptance-set ceiling, which our automata cross; a skipped oracle
# is not a verified one. The bindings compile against whichever python3 the node
# has, which is the point of building here rather than shipping a binary: a
# prebuilt _spot.so is bound to one CPython ABI and one glibc.
"$SRC/configure" -C \
    VALGRIND=false \
    PYTHON="$(command -v python3)" \
    --prefix="$PREFIX" \
    --enable-shared \
    --enable-python \
    --disable-devel \
    --without-included-lbtt \
    --enable-max-accsets=64

make -j"$BUILD_JOBS"
make install

# --- verify ------------------------------------------------------------------

# Prove the thing the rest of the pipeline depends on, from the root, exactly as
# a job would. Sourced after install so it sees the prefix that just appeared.
cd "$ROOT"
# shellcheck source=env.sh
source "$HERE/env.sh"
python3 -c 'import spot; print("import spot OK:", spot.version())'
ltl2tgba --version | head -1 || true
