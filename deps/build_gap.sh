#!/bin/bash
# Build GAP and install SgpDec under the repo's opt/. Always from source.
#
# Source only: no distro package, no system install, no sudo, no $HOME. GAP
# versions and bundled packages differ across machines, and the pipeline needs
# one it can name. Everything lands under opt/, and `rm -rf opt build` undoes it
# exactly.
#
# The packages are built for the machine that builds them: semigroups vendors
# libsemigroups, which compiles HPCombi's AVX2 intrinsics when the compiler
# offers them. The result is fast, and raises SIGILL on a machine without AVX2.
#
# One install, kept as it is: a prefix holding a GAP is left alone, whatever
# version it holds. To replace it, `rm -rf opt/gap` and run again.
#
# opt/gap/bin/gap is a wrapper: it carries the library path of GAP's own
# libgap.so and adds the prefix as an extra GAP root, so pkg/sgpdec loads. It is
# what a bare `gap` on PATH resolves to.
#
# Usage: deps/build_gap.sh

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
# shellcheck source=versions.sh
source "$HERE/versions.sh"

[ $# -eq 0 ] || { echo "usage: build_gap.sh (no arguments)" >&2; exit 2; }

PREFIX="$ROOT/opt/gap"
GAP_INST="$PREFIX/gap-inst"
DL="$ROOT/build/dl"
BUILD="$ROOT/build/gap-$GAP_VERSION"

log() { echo "[gap] $*"; }
die() { echo "[gap] ERROR: $*" >&2; exit 1; }

# True when the package compiled its kernel module. The source directory is
# unpacked before the compile and survives its failure, so it says nothing.
has_kernel_module() {
    test -n "$(find "$1/bin" -name '*.so' 2>/dev/null | head -1)"
}

mkdir -p "$DL" "$PREFIX/pkg" "$PREFIX/bin"

# --- GAP ---------------------------------------------------------------------

if [ ! -x "$GAP_INST/bin/gap" ]; then
    log "building GAP $GAP_VERSION into $GAP_INST"

    TARBALL="$DL/gap-$GAP_VERSION.tar.gz"
    if [ ! -s "$TARBALL" ]; then
        curl -fL --no-progress-meter -o "$TARBALL.part" "$GAP_URL" \
            || wget -q -O "$TARBALL.part" "$GAP_URL" \
            || die "could not download $GAP_URL"
        mv -f "$TARBALL.part" "$TARBALL"
    fi

    if [ ! -x "$BUILD/configure" ]; then
        rm -rf "$BUILD"
        mkdir -p "$ROOT/build"
        tar -xzf "$TARBALL" -C "$ROOT/build"
        [ -x "$BUILD/configure" ] || die "unexpected tarball layout: no $BUILD/configure"
    fi

    # GAP builds in its source tree (no VPATH support), hence build/ rather than
    # a separate object dir.
    #
    # -std=gnu17 is for GAP's vendored GMP, whose configure probe declares
    # `void g(){}` and then calls it with arguments. That is a valid unprototyped
    # declaration up to C17, but gcc 14+ defaults to C23, where it is an error;
    # GMP reads the error as "no working compiler" and the build stops. The
    # standard is pinned rather than the compiler chosen, so this stays correct
    # on nodes with an older gcc.
    (
        cd "$BUILD"
        ./configure --prefix="$GAP_INST" CC="${CC:-gcc} -std=gnu17"
        make -j"$BUILD_JOBS"
        make install
    )
    [ -x "$GAP_INST/bin/gap" ] || die "GAP build finished but no bin/gap"
    log "GAP built."
else
    log "GAP already built at $GAP_INST (--rebuild to force)"
fi

# --- GAP packages ------------------------------------------------------------

# GAP's `make install` warns that it installs no packages, so the ones SgpDec
# needs are compiled in the source tree (where sysinfo.gap and gac live) and
# copied into the prefix's GAP root afterwards. BuildPackages.sh must be run from
# a pkg directory, and --with-gaproot only accepts an absolute path: given a
# relative one, every package fails with "Unable to find GAP root directory".
NEED_PKGS=0
for p in $GAP_PKGS; do
    [ -d "$PREFIX/pkg/$p" ] || NEED_PKGS=1
done
for p in $GAP_KERNEL_PKGS; do
    has_kernel_module "$PREFIX/pkg/$p" || NEED_PKGS=1
done

if [ "$NEED_PKGS" -eq 1 ]; then
    log "building GAP packages: $GAP_PKGS"
    # semigroups vendors libsemigroups, which uses the AVX2 intrinsics of HPCombi.
    # Both are left at their defaults, so the packages are built for the machine
    # that builds them and raise SIGILL on a machine without those instructions.
    #
    # BuildPackages.sh defaults MAKEFLAGS to -j3, which throttles the one heavy
    # compile here (semigroups vendors libsemigroups) to three lanes whatever the
    # job holds. It honours the variable when set.
    ( cd "$BUILD/pkg" \
      && MAKEFLAGS="-j$BUILD_JOBS" \
         "$BUILD/bin/BuildPackages.sh" --with-gaproot="$BUILD" $GAP_PKGS ) \
        || die "BuildPackages failed; see $BUILD/pkg/log"

    # A package that failed to compile leaves its source directory behind, so
    # installing whatever is there would put a broken package in the prefix and
    # defer the failure to whoever loads it.
    for p in $GAP_KERNEL_PKGS; do
        has_kernel_module "$BUILD/pkg/$p" || die "package $p built no kernel module"
    done

    for p in $GAP_PKGS; do
        [ -d "$BUILD/pkg/$p" ] || die "package $p is not in the GAP distribution"
        rm -rf "${PREFIX:?}/pkg/$p"
        cp -r "$BUILD/pkg/$p" "$PREFIX/pkg/"
    done
    log "packages installed into $PREFIX/pkg"
else
    log "GAP packages already in $PREFIX/pkg"
fi

# --- SgpDec ------------------------------------------------------------------

SGPDEC_DIR="$PREFIX/pkg/sgpdec"
if [ ! -d "$SGPDEC_DIR" ]; then
    log "cloning SgpDec $SGPDEC_VERSION into $PREFIX/pkg"
    # By tag, not by release tarball: the tarball the release page advertises is
    # not served. SgpDec is pure GAP, so the checkout is the installation.
    git clone --quiet --depth 1 --branch "$SGPDEC_VERSION" \
        "$SGPDEC_REPO" "$SGPDEC_DIR" || die "could not obtain SgpDec sources"
else
    log "SgpDec already at $SGPDEC_DIR"
fi

# --- wrapper -----------------------------------------------------------------

# GAP's `make install` announces itself as experimental, and indeed leaves
# libgap.so where the loader will not find it. Rather than rely on rpath, the
# wrapper sets the library path itself, so `gap` works from a bare PATH lookup.
GAP_LIBS=""
for d in "$GAP_INST/lib" "$GAP_INST/lib64"; do
    [ -d "$d" ] && GAP_LIBS="$d${GAP_LIBS:+:$GAP_LIBS}"
done

cat >"$PREFIX/bin/gap" <<EOF
#!/usr/bin/env bash
# Generated by deps/build_gap.sh. Runs our GAP with its own libraries on the
# loader path and this prefix as an extra GAP root, so pkg/sgpdec loads.
# Callers spawn a bare 'gap' from PATH; this is it.
#
# -r drops \$HOME/.gap from GAPInfo.RootPaths. GAP adds that root unasked, and a
# package installed there would be loaded in preference to ours, making the
# result depend on the account rather than on the checkout.
export LD_LIBRARY_PATH="$GAP_LIBS\${LD_LIBRARY_PATH:+:\$LD_LIBRARY_PATH}"
exec "$GAP_INST/bin/gap" -r -l "$PREFIX;" "\$@"
EOF
chmod +x "$PREFIX/bin/gap"
log "wrote wrapper $PREFIX/bin/gap"

# --- verify ------------------------------------------------------------------

log "verifying SgpDec loads"

# Output is shown and kept, never captured in a variable: a gap killed by a
# signal leaves a command substitution nothing to print, and the failure then
# reports an exit status and no reason. grep reads the file afterwards rather
# than the pipe, whose early exit would SIGPIPE tee and fail a good verify.
VERIFY_LOG="$ROOT/build/gap-verify.log"
"$PREFIX/bin/gap" --bare -q -c \
    'if LoadPackage("SgpDec") = fail then Print("LOAD_FAIL\n"); else Print("LOAD_OK\n"); fi; QUIT;' \
    2>&1 | tee "$VERIFY_LOG" \
    || die "gap exited $? while loading SgpDec"
grep -q LOAD_OK "$VERIFY_LOG" || die "SgpDec did not load from $SGPDEC_DIR"

log "SgpDec OK"
