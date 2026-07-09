#!/usr/bin/env bash
# Builds and installs the sos_sdd native dependencies — libDDD, and
# libITS (only its gal expression component is consumed) — from source
# checkouts into an untracked local prefix, so the tool depends on no
# system install.
#
#   ./install_deps.sh [LIBDDD_SRC] [LIBITS_SRC] [PREFIX]
#
# Defaults: sibling checkouts ~/git/libDDD and ~/git/libITS, prefix
# sos_sdd/deps (gitignored). Both projects are stock autotools:
#
#   autoreconf -vfi && ./configure --prefix=$PREFIX && make && make install
#
# libITS must be configured against the *installed* libDDD prefix
# (--with-libddd=$PREFIX): its build expects the install layout
# ($PREFIX/include/ddd/*.h, $PREFIX/lib/libDDD.a), not a source tree.
# The sos_sdd CMake build looks in deps/ first (see CMakeLists.txt).

set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
LIBDDD_SRC="${1:-$HOME/git/libDDD}"
LIBITS_SRC="${2:-$HOME/git/libITS}"
PREFIX="${3:-$HERE/deps}"
JOBS="$(nproc)"

echo "== libDDD: $LIBDDD_SRC -> $PREFIX"
cd "$LIBDDD_SRC"
autoreconf -vfi
./configure --prefix="$PREFIX"
make -j"$JOBS"
make install

echo "== libITS: $LIBITS_SRC -> $PREFIX (against installed libDDD)"
# The CI recipe (.github/workflows/linux.yml): antlr.sh fetches antlr 3.4
# (jar + C runtime) into usr/local *inside the libITS tree*, then configure
# points at it. gmp and expat come from the system (dnf gmp-devel
# expat-devel) rather than the CI's hermetic source builds.
cd "$LIBITS_SRC"
if [ ! -f usr/local/lib/antlr-3.4-complete.jar ]; then
  /bin/bash ./antlr.sh
fi
autoreconf -vfi
./configure --prefix="$PREFIX" --with-libddd="$PREFIX" \
  --with-antlrc="$LIBITS_SRC/usr/local" \
  --with-antlrjar="$LIBITS_SRC/usr/local/lib/antlr-3.4-complete.jar"
# The bin/ executables need gmpxx.h (dnf gmp-devel) but are not consumed
# here; the library archives land in the tree's lib/ regardless, so a
# partial make is tolerated and the real gate is the artifact check below.
make -j"$JOBS" || echo "WARN: full make failed (bin/ tools?); checking library artifacts"

# Export what this project consumes: the static archives and the its/
# header tree (make install is tied to the full build, so do it by hand).
mkdir -p "$PREFIX"/lib "$PREFIX"/include
cp lib/libITS.a "$PREFIX"/lib/
cp lib/libITSmain.a "$PREFIX"/lib/ 2>/dev/null || true
(find its \( -name '*.hh' -o -name '*.hpp' -o -name '*.h' \) | tar cf - -T -) \
  | (cd "$PREFIX"/include && tar xf -)

echo "== done:"
ls "$PREFIX"/lib/libDDD.a "$PREFIX"/lib/libITS.a
ls "$PREFIX"/include/its/gal/ExprHom.hpp
