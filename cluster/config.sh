# Local-side cluster configuration. Sourced by sync_cluster.sh / oarrun.sh / reap.sh.
# Nothing here runs on a compute node; see env.sh for the in-job environment.
# Every value may be overridden from the caller's environment.

# SSH destination. Passwordless via the default key (~/.ssh/id_ed25519).
: "${CLUSTER:=ythierry@cluster.lip6.fr}"

# Repo copy on the cluster, relative to the remote HOME. That HOME is NFS and
# visible from every compute node, so the path is valid inside jobs.
: "${REMOTE_REPO:=git/BuchiToLTL}"

# Run directories, under the repo root and root-anchored in .gitignore. Safe
# there because sync_cluster.sh checks out a commit and never removes untracked
# files.
: "${REMOTE_RUNS:=$REMOTE_REPO/oarrun}"

# Source of truth for which Spot release we track. cluster/build_spot.sh clones
# it to read the version and the tarball URL, then applies its own configure
# flags; that repo's own recipe targets ITS-Tools and builds no Python bindings.
: "${SPOT_SRC_REPO:=https://github.com/yanntm/Spot-BinaryBuilds}"

# Walltime for the one-off provisioning job. Long by design and by exception:
# a compile is not a sweep, and this runs when Spot moves, not per experiment.
: "${SPOT_BUILD_WALLTIME:=3:00:00}"

# make -j for the provisioning builds. A fixed width, never nproc: under a
# scheduler's cpuset nproc reports the whole machine rather than the allocation,
# and Spot's heavier translation units want memory more than they want lanes.
: "${BUILD_JOBS:=10}"

# Where reap.sh deposits a fetched run, relative to the local repo root.
: "${LOCAL_RESULTS:=results/cluster}"

# Default per-command wall-clock cap in seconds. 0 disables the cap and lets
# the OAR walltime bound the job instead.
: "${OARRUN_TIMEOUT:=15}"

# Default number of whole nodes to spread the command list across.
: "${OARRUN_SPLIT:=1}"

# Default commands in flight per node. "auto" means: ask OAR how many cores it
# actually gave us ($OAR_NODEFILE), inside the job.
: "${OARRUN_CORES:=auto}"

# Default OAR walltime per job. Deliberately small: a job holds a whole node,
# so shards are sized to fit this rather than the reverse. Raise --split, not
# the walltime. A job killed at walltime keeps every result it already wrote;
# reap.sh reports the gap and --resume finishes it.
: "${OARRUN_WALLTIME:=0:05:00}"

# Cores assumed per node when oarrun.sh checks a shard against the walltime
# before submitting. Only an estimate: the worker uses the real allocation.
: "${OARRUN_ASSUMED_CORES:=32}"

# OAR resource string, minus the walltime that oarrun.sh appends. A whole node
# with no machine-class property: the fleet is heterogeneous and the worker
# sizes itself from the allocation. Pin a class here when a run needs
# comparable timings, e.g. '{(host like "tall%")}/nodes=1'.
: "${OARRUN_RESOURCES:=/nodes=1}"

# Extra oarsub options (queue, project, --besteffort, ...).
: "${OARRUN_OAR_OPTS:=}"
