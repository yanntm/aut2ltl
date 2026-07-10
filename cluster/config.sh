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

# GAP, built from source like Spot: never a distro package, or a run would depend
# on which node it landed on rather than on the commit. Keep this recent: GAP
# vendors GMP, and older bundles fail configure's long-long check under a modern
# gcc ("could not find a working compiler").
: "${GAP_VERSION:=4.15.1}"
: "${GAP_URL:=https://github.com/gap-system/gap/releases/download/v${GAP_VERSION}/gap-${GAP_VERSION}.tar.gz}"

# SgpDec, the GAP package the Krohn-Rhodes path consumes.
: "${SGPDEC_VERSION:=v1.2.0}"
: "${SGPDEC_URL:=https://github.com/gap-packages/sgpdec/releases/download/${SGPDEC_VERSION}/sgpdec-1.2.0.tar.gz}"

# libDDD and libITS, for the symbolic path. Cloned into build/, installed into
# opt/its; only libITS's gal expression component is consumed.
: "${LIBDDD_REPO:=https://github.com/lip6/libDDD}"
: "${LIBITS_REPO:=https://github.com/lip6/libITS}"

# SgpDec's transitive dependencies, in the GAP distribution but not installed by
# GAP's `make install`. Four of them carry kernel modules that must be compiled
# (io, orb, datastructures, digraphs, semigroups); semigroups vendors libsemigroups
# and dominates the build time. Order is irrelevant, BuildPackages.sh sorts it out.
: "${GAP_PKGS:=gapdoc io orb datastructures digraphs genss images semigroups}"

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
