# Run-time environment for a tree whose dependencies were built into opt/.
#
# Sourced, never executed: it exports the paths that make `import spot`, a bare
# `gap`, and a CMake build against libDDD resolve to this tree's own builds.
#
# Everything resolves from the repo root, located from this file rather than from
# $PWD or $HOME, so a checkout anywhere works.

AUT2LTL_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export AUT2LTL_ROOT

# Spot and GAP, built into single prefixes under opt/. Prepended unconditionally,
# not only when present: our directories must win the PATH lookup whatever the
# machine carries, and a missing build should surface as `command not found`
# rather than as a silent fall-through to a system install.
export PATH="$AUT2LTL_ROOT/opt/spot/bin:$AUT2LTL_ROOT/opt/gap/bin:$PATH"

SPOT_PREFIX="$AUT2LTL_ROOT/opt/spot"
for libdir in "$SPOT_PREFIX/lib" "$SPOT_PREFIX/lib64"; do
    if [ -d "$libdir" ]; then
        export LD_LIBRARY_PATH="$libdir${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
    fi
done

# Where `make install` put the Python bindings: the lib/ vs lib64/ split is
# autotools' pyexecdir (Fedora says lib64, Debian lib) and the version segment
# follows the interpreter, so neither is assumed. This must succeed --
# LD_LIBRARY_PATH above already points libspot.so at our build, so were our
# bindings absent from PYTHONPATH a system `import spot` would load a foreign
# _impl.so against our library and die on an undefined symbol.
for sitedir in "$SPOT_PREFIX"/lib/python*/site-packages \
               "$SPOT_PREFIX"/lib64/python*/site-packages; do
    if [ -d "$sitedir" ]; then
        export PYTHONPATH="$sitedir${PYTHONPATH:+:$PYTHONPATH}"
    fi
done
unset SPOT_PREFIX libdir sitedir

# libDDD + libITS, installed into opt/its. Named rather than placed on a search
# path: the CMake build takes this prefix as a hint directly, which leaves its
# own default (a deps/ dir beside it) intact.
export LIBDDD_HOME="$AUT2LTL_ROOT/opt/its"

# So that `python3 -m aut2ltl ...` resolves the package from the root whatever
# the command's own working directory.
export PYTHONPATH="$AUT2LTL_ROOT${PYTHONPATH:+:$PYTHONPATH}"

# Line-buffer whatever the tools write, so a process killed part way through
# still leaves complete lines behind.
export PYTHONUNBUFFERED=1

# Keep numeric libraries from oversubscribing when many commands run at once.
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
