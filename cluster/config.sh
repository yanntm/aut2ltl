# Local-side cluster configuration. Sourced by sync_cluster.sh / oarrun.sh / reap.sh.
# Nothing here runs on a compute node; see deps/env.sh for the in-job environment,
# and deps/versions.sh for what the dependencies are built from.
# Every value may be overridden from the caller's environment.

# SSH destination. Passwordless via the default key (~/.ssh/id_ed25519).
: "${CLUSTER:=ythierry@cluster.lip6.fr}"

# Repo copy on the cluster, relative to the remote HOME. That HOME is NFS and
# visible from every compute node, so the path is valid inside jobs. Named after
# the project, not after any one working copy's directory.
: "${REMOTE_REPO:=git/aut2ltl}"

# Run directories, under the repo root and root-anchored in .gitignore. Safe
# there because sync_cluster.sh checks out a commit and never removes untracked
# files.
: "${REMOTE_RUNS:=$REMOTE_REPO/oarrun}"

# Walltime for a provisioning job submitted through deploy.sh. Long by design and
# by exception: a compile is not a sweep, and it runs when a dependency moves,
# not per experiment.
: "${DEPS_BUILD_WALLTIME:=3:00:00}"

# Where reap.sh deposits a fetched run, relative to the local repo root.
: "${LOCAL_RESULTS:=results/cluster}"

# Default per-command wall-clock cap in seconds. 0 disables the cap and lets
# the OAR walltime bound the job instead.
: "${OARRUN_TIMEOUT:=15}"

# Default number of whole nodes to spread the command list across.
: "${OARRUN_SPLIT:=1}"

# Cores requested per job, and commands in flight on them: oarrun.sh puts this
# in the resource string and the worker reads the granted allocation back from
# $OAR_NODEFILE, so the width used equals the width reserved. Raise it for a
# sweep that wants throughput; a request without a core term reserves the whole
# machine, however few cores the work has.
: "${OARRUN_CORES:=4}"

# Default OAR walltime per job. Deliberately small: shards are sized to fit it
# rather than the reverse. Raise --split or --cores, not the walltime. A job
# killed at walltime keeps every result it already wrote; reap.sh reports the
# gap and --resume finishes it.
: "${OARRUN_WALLTIME:=0:05:00}"

# OAR resource string, minus the core term and the walltime that oarrun.sh
# appends. The host class is not a preference: the dependencies under opt/ are
# compiled with the AVX2 instructions of the machine that built them, and a job
# landing anywhere else dies of SIGILL. Builds and runs must therefore ask for
# the same class. It also makes timings comparable, which a heterogeneous
# allocation would not.
#
# Single-quoted inside the filter: oarrun.sh interpolates this into a
# double-quoted -l argument, which a double quote here would close early.
: "${OARRUN_RESOURCES:={host like 'tall%'}/nodes=1}"

# Extra oarsub options (queue, project, --besteffort, ...).
: "${OARRUN_OAR_OPTS:=}"
