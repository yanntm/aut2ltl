#!/bin/bash
# Build libDDD and libITS from source into the repo's opt/its prefix.
#
# Source only, like the other dependencies: the checkouts are cloned into build/,
# never beside the repo and never into $HOME, so a result is a function of the
# commit rather than of what a machine happens to carry.
#
# Only libITS's gal expression component is consumed. Its bin/ tools want headers
# (gmpxx) that nothing here needs, so a partial `make` is tolerated: the gate is
# the presence of the archives and the its/ header tree, checked at the end.
#
# The prefix is exported to CMake as LIBDDD_HOME by env.sh, which is the override
# sos_sdd/CMakeLists.txt already honours -- no build file changes.
#
# One install, kept as it is. To replace it, `rm -rf opt/its` and run again.
#
# Usage: deps/build_its.sh

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
# shellcheck source=versions.sh
source "$HERE/versions.sh"

[ $# -eq 0 ] || { echo "usage: build_its.sh (no arguments)" >&2; exit 2; }

PREFIX="$ROOT/opt/its"
DDD_SRC="$ROOT/build/libDDD"
ITS_SRC="$ROOT/build/libITS"

log() { echo "[its] $*"; }
die() { echo "[its] ERROR: $*" >&2; exit 1; }

if [ -f "$PREFIX/lib/libDDD.a" ] && [ -f "$PREFIX/lib/libITS.a" ] \
   && [ -f "$PREFIX/include/its/gal/ExprHom.hpp" ]; then
    log "already built at $PREFIX (rm -rf $PREFIX to rebuild)"
    exit 0
fi

command -v autoreconf >/dev/null || die "autoreconf not found (autotools needed)"

clone_or_update() {  # <url> <dir>
    if [ ! -d "$2/.git" ]; then
        log "cloning $1 -> ${2#"$ROOT"/}"
        mkdir -p "$(dirname "$2")"
        git clone --depth 1 "$1" "$2"
    else
        git -C "$2" fetch --quiet --depth 1 origin HEAD
        git -C "$2" reset --quiet --hard FETCH_HEAD
    fi
}

clone_or_update "$LIBDDD_REPO" "$DDD_SRC"
clone_or_update "$LIBITS_REPO" "$ITS_SRC"

mkdir -p "$PREFIX/lib" "$PREFIX/include"

# --- libDDD ------------------------------------------------------------------

# Both libraries suppress autoconf's default -g -O2 for C++ (configure.ac does
# `test -z "$CXXFLAGS" && CXXFLAGS=` before AC_PROG_CXX), so an unconfigured
# build is -O0 with -flto: the IR bloat of link-time optimization without the
# optimization. The optimization level and NDEBUG are therefore stated, not
# inherited. NDEBUG matters most for libDDD, whose asserts sit in the hot path.
ITS_CXXFLAGS="-O2"
ITS_CPPFLAGS="-DNDEBUG"

log "libDDD -> $PREFIX"
(
    cd "$DDD_SRC"
    autoreconf -vfi
    ./configure --prefix="$PREFIX" CXXFLAGS="$ITS_CXXFLAGS" CPPFLAGS="$ITS_CPPFLAGS"
    make -j"$BUILD_JOBS"
    make install
)

# --- libITS ------------------------------------------------------------------

# antlr 3.4 (jar + C runtime) is fetched by the project's own script into
# usr/local inside its tree; configure is then pointed at it. libITS must be
# configured against the *installed* libDDD prefix, not a source tree.
log "libITS -> $PREFIX (against installed libDDD)"
(
    cd "$ITS_SRC"
    if [ ! -f usr/local/lib/antlr-3.4-complete.jar ]; then
        /bin/bash ./antlr.sh
    fi
    autoreconf -vfi
    ./configure --prefix="$PREFIX" --with-libddd="$PREFIX" \
        --with-antlrc="$ITS_SRC/usr/local" \
        --with-antlrjar="$ITS_SRC/usr/local/lib/antlr-3.4-complete.jar" \
        CXXFLAGS="$ITS_CXXFLAGS" CPPFLAGS="$ITS_CPPFLAGS"

    make -j"$BUILD_JOBS" || log "WARN: full make failed (bin/ tools?); checking artifacts"

    # `make install` is tied to the full build, so export by hand what is
    # consumed: the archives and the its/ header tree.
    cp lib/libITS.a "$PREFIX/lib/"
    cp lib/libITSmain.a "$PREFIX/lib/" 2>/dev/null || true
    (find its \( -name '*.hh' -o -name '*.hpp' -o -name '*.h' \) | tar cf - -T -) \
        | (cd "$PREFIX/include" && tar xf -)
)

# --- verify ------------------------------------------------------------------

for artifact in lib/libDDD.a lib/libITS.a include/its/gal/ExprHom.hpp; do
    [ -e "$PREFIX/$artifact" ] || die "missing $artifact under $PREFIX"
done
log "libDDD + libITS OK in $PREFIX"
