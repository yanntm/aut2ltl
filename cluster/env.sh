# In-job environment. Sourced by oar_worker.sh on a compute node, never on the
# submit host: that host is provisioned for submission only and cannot build or
# import the scientific stack.
#
# Everything resolves from the repo root, located from this file rather than
# from $PWD or $HOME, so a checkout anywhere works. Spot is our own build under
# opt/, produced by cluster/build_spot.sh; no system-wide install is assumed.

OARRUN_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export OARRUN_ROOT

# Highest-versioned prefix under opt/, if one has been built. Version sort, so
# spot-2.14.5 wins over spot-2.9.6 where a lexical sort would not.
_spot_prefix="$(find "$OARRUN_ROOT/opt" -maxdepth 1 -type d -name 'spot-*' 2>/dev/null \
                | sort -V | tail -1)"
if [ -n "$_spot_prefix" ]; then
    export PATH="$_spot_prefix/bin:$PATH"
    for _lib in "$_spot_prefix/lib" "$_spot_prefix/lib64"; do
        [ -d "$_lib" ] && export LD_LIBRARY_PATH="$_lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
    done

    # Where `make install` put the python bindings. Both the lib/ vs lib64/ split
    # (autotools' pyexecdir: Fedora says lib64, Debian says lib) and the version
    # segment depend on the machine, so neither is assumed. This must succeed:
    # LD_LIBRARY_PATH above already points libspot.so at our build, so if our
    # bindings are missing from PYTHONPATH a system `import spot` would load a
    # foreign _impl.so against our library and die on an undefined symbol.
    for _sp in "$_spot_prefix"/lib/python*/site-packages \
               "$_spot_prefix"/lib64/python*/site-packages; do
        [ -d "$_sp" ] && export PYTHONPATH="$_sp${PYTHONPATH:+:$PYTHONPATH}"
    done
fi
unset _lib _sp _spot_prefix

# GAP, built by build_gap.sh into opt/gap. Prepended unconditionally, not only
# when present: our directory must win the PATH lookup whatever the machine
# carries, and a missing build should surface as `gap: command not found` rather
# than as a silent fall-through to a system install of another version.
export PATH="$OARRUN_ROOT/opt/gap/bin:$PATH"

# libDDD + libITS, built by build_its.sh into opt/its. Named rather than placed
# on a search path: the CMake build takes this prefix as a hint directly, which
# leaves its own default (a deps/ dir beside it) intact.
export LIBDDD_HOME="$OARRUN_ROOT/opt/its"

# So that `python3 -m aut2ltl ...` resolves the package from the root whatever
# the command's own working directory.
export PYTHONPATH="$OARRUN_ROOT${PYTHONPATH:+:$PYTHONPATH}"

# Line-buffer whatever the commands write, so a job killed at walltime still
# leaves complete lines behind. Tools that manage their own output files must
# flush after each record themselves; this only covers stdout/stderr.
export PYTHONUNBUFFERED=1

# Keep numeric libraries from oversubscribing: the worker already runs one
# command per core.
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
