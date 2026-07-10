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

# Where reap.sh deposits a fetched run, relative to the local repo root. Under
# the ignored logs/ tree: a cluster run is an ordinary throwaway run that happened
# to execute elsewhere. What lands in results/ is what someone chose to adopt,
# after diffing a run against the reference.
: "${LOCAL_RESULTS:=logs/cluster}"

# Default per-command wall-clock cap in seconds. 0 disables the cap and lets the
# OAR walltime bound the job instead. Eight examples at a 15s budget, plus the
# interpreter's start: a planner that packs commands reads this back and cuts its
# chunks to fit, rather than naming a cap of its own. The job walltime above it
# leaves margin for a cold cache and a slow node.
: "${OARRUN_TIMEOUT:=130}"

# Default number of jobs to spread the command list across. Throughput comes
# from jobs, not from wide ones: a command is sequential.
: "${OARRUN_SPLIT:=8}"

# Cores requested per job, and commands in flight on them: oarrun.sh puts this
# in the resource string and the worker reads the granted allocation back from
# $OAR_NODEFILE, so the width used equals the width reserved. Small on purpose.
# A command is a sequential run and wants one core; asking for a node's worth
# would idle 60 of its cores and crowd out other jobs. Raise --split instead.
: "${OARRUN_CORES:=2}"

# Default OAR walltime per job. Deliberately small: shards are sized to fit it
# rather than the reverse. Raise --split, not the walltime. Comfortably above the
# per-command cap, so a run of consecutive timeouts does not cost the job. A job
# killed at walltime keeps every result it already wrote; reap.sh reports the gap
# and --resume finishes it.
: "${OARRUN_WALLTIME:=0:05:00}"

# OAR resource string, minus the core term and the walltime that oarrun.sh
# appends. The host class is not a preference: the dependencies under opt/ are
# compiled with the AVX2 instructions of the machine that built them, and a job
# landing anywhere else dies of SIGILL. Builds and runs must therefore ask for
# the same class. It also makes timings comparable, which a heterogeneous
# allocation would not.
#
# Assigned the long way: ${VAR:=default} ends the default at its first `}`, and
# the OAR filter contains one, so that form would silently store a truncated
# string. Single quotes inside the filter, because oarrun.sh interpolates this
# into a double-quoted -l argument.
if [ -z "${OARRUN_RESOURCES:-}" ]; then
    OARRUN_RESOURCES="{host like 'tall%'}/nodes=1"
fi

# Extra oarsub options (queue, project, --besteffort, ...).
: "${OARRUN_OAR_OPTS:=}"
