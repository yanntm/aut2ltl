# In-job environment. Sourced by oar_worker.sh on a compute node, never on the
# submit host: that host is provisioned for submission only and cannot build or
# import the scientific stack.
#
# Everything resolves from the repo root, located from this file rather than
# from $PWD or $HOME, so a checkout anywhere works. Spot is our own build under
# opt/, produced by cluster/build_spot.sh; no system-wide install is assumed.

OARRUN_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export OARRUN_ROOT

# Spot and GAP, built by build_spot.sh / build_gap.sh into single prefixes.
# Prepended unconditionally, not only when present: our directories must win the
# PATH lookup whatever the machine carries, and a missing build should surface as
# `command not found` rather than as a silent fall-through to a system install.
export PATH="$OARRUN_ROOT/opt/spot/bin:$OARRUN_ROOT/opt/gap/bin:$PATH"

_spot="$OARRUN_ROOT/opt/spot"
for _lib in "$_spot/lib" "$_spot/lib64"; do
    [ -d "$_lib" ] && export LD_LIBRARY_PATH="$_lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
done

# Where `make install` put the python bindings: the lib/ vs lib64/ split is
# autotools' pyexecdir (Fedora says lib64, Debian lib) and the version segment
# follows the interpreter, so neither is assumed. This must succeed --
# LD_LIBRARY_PATH above already points libspot.so at our build, so were our
# bindings absent from PYTHONPATH a system `import spot` would load a foreign
# _impl.so against our library and die on an undefined symbol.
for _sp in "$_spot"/lib/python*/site-packages "$_spot"/lib64/python*/site-packages; do
    [ -d "$_sp" ] && export PYTHONPATH="$_sp${PYTHONPATH:+:$PYTHONPATH}"
done
unset _lib _sp _spot

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
