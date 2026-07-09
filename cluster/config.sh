# Local-side cluster configuration. Sourced by sync_cluster.sh / oarrun.sh / reap.sh.
# Nothing here runs on a compute node; see env.sh for the in-job environment.
# Every value may be overridden from the caller's environment.

# SSH destination. Passwordless via the default key (~/.ssh/id_ed25519).
: "${CLUSTER:=ythierry@cluster.lip6.fr}"

# Repo copy on the cluster, relative to the remote HOME. That HOME is NFS and
# visible from every compute node, so the path is valid inside jobs.
: "${REMOTE_REPO:=git/BuchiToLTL}"

# Run directories, kept outside REMOTE_REPO so sync_cluster.sh --delete can
# never reach them.
: "${REMOTE_RUNS:=oarrun}"

# Where reap.sh deposits a fetched run, relative to the local repo root.
: "${LOCAL_RESULTS:=results/cluster}"

# Default per-command wall-clock cap in seconds. 0 disables the cap and lets
# the OAR walltime bound the job instead.
: "${OARRUN_TIMEOUT:=15}"

# Default number of whole nodes to spread the command list across.
: "${OARRUN_SPLIT:=1}"

# Default commands in flight per node. "auto" means nproc, measured inside the
# job on whichever machine it lands.
: "${OARRUN_CORES:=auto}"

# Default OAR walltime per job. Deliberately small: a job holds a whole node,
# so shards are sized to fit this rather than the reverse. Raise --split, not
# the walltime. A job killed at walltime keeps every result it already wrote;
# reap.sh reports the gap and --resume finishes it.
: "${OARRUN_WALLTIME:=0:05:00}"

# Cores assumed per node when oarrun.sh checks a shard against the walltime
# before submitting. Only an estimate: the worker uses the real nproc.
: "${OARRUN_ASSUMED_CORES:=32}"

# OAR resource string, minus the walltime that oarrun.sh appends. A whole node
# with no machine-class property: the fleet is heterogeneous and the worker
# sizes itself with nproc. Pin a class here when a run needs comparable
# timings, e.g. '{(host like "tall%")}/nodes=1'.
: "${OARRUN_RESOURCES:=/nodes=1}"

# Extra oarsub options (queue, project, --besteffort, ...).
: "${OARRUN_OAR_OPTS:=}"
