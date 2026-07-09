# In-job environment. Sourced by oar_worker.sh on a compute node, never on the
# submit host: that host is provisioned for submission only and cannot import
# the scientific stack. Anything needing a build belongs in an interactive job
# (`oarsub -I`), not here.
#
# Edit the activation line below to match whatever provides python3 + spot.

: "${OARRUN_REPO:=$HOME/git/BuchiToLTL}"
export OARRUN_REPO

# Make python3 and spot importable. Replace with the site's incantation, e.g.
#   module load python/3.11
#   source "$OARRUN_REPO/.venv/bin/activate"
#   source "$HOME/opt/spot/setup.sh"
# Left as a no-op so a bare `import spot` failure is reported by the smoke run
# rather than masked by a broken activation.
:

# Line-buffer whatever the commands write, so a job killed at walltime still
# leaves complete lines behind. Tools that manage their own output files must
# flush after each record themselves; this only covers stdout/stderr.
export PYTHONUNBUFFERED=1

# Keep numeric libraries from oversubscribing: the worker already runs one
# command per core.
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
