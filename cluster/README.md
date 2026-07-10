# cluster — run a list of commands on the OAR cluster

Generic. The runner never knows what a command means: a census sweep, a
multi-hour learning run and the Spot build itself all go through it.

```
cluster/sync_cluster.sh                        # after each commit
RUN=$(cluster/oarrun.sh --split 38 cmds.txt)   # submit, prints a run id
cluster/reap.sh "$RUN"                         # fetch + report; call again for progress
cluster/oarsub.sh -- python3 -m survey ...     # single command, same machinery
```

Provisioning is a job like any other, run once in a blue moon (when Spot moves):

```
cluster/sync_cluster.sh
cluster/reap.sh "$(cluster/oarsub.sh --timeout 0 --walltime 3:00:00 -- cluster/provision.sh)"
```

Everything resolves from the repo root. The cluster checkout is at
`~/git/BuchiToLTL`, and `opt/`, `build/`, `oarrun/` are subfolders of it
(root-anchored in `.gitignore`).

## Only committed code runs

`sync_cluster.sh` checks the cluster out **detached at the local HEAD commit** —
not at the remote's tip — so a run's recorded `git_rev` names the code that ran.
An unpushed HEAD is refused, since the cluster fetches from origin and could not
reach it. Uncommitted changes are ignored: they do not travel. Nothing is ever
pushed for you, and `reap.sh` is the only transfer, always cluster to local.

## Contract for the commands

One shell command per line, run with the repo root as working directory.

**Output must be additive and flushed after each record.** Collection is then
decoupled from completion: a run still going, or killed at walltime, still
yields every result it produced. This is what makes `reap.sh` callable at any
moment and `--resume` cheap.

Each command gets `$OARRUN_OUT`, a private output slot (`out/<idx>`) to use as a
file or create as a directory. **Do not append to one shared file**: `O_APPEND`
is not atomic over NFS and interleaves under a whole-node fan-out. Write
`$OARRUN_OUT.csv` and `reap.sh` concatenates the shards in index order into
`results.csv`, header once. Also set: `$OARRUN_RUN`, `$OARRUN_IDX`,
`$OARRUN_ROOT`.

Stdout and stderr are line-buffered (`stdbuf`, `PYTHONUNBUFFERED=1`) into
`logs/<idx>.{out,err}`.

## Accounting

Each command's status file is written last and atomically, so `reap.sh`
distinguishes four outcomes that are usually conflated:

| | meaning |
|---|---|
| `OK` | exit 0 |
| `TIMEOUT` | hit the per-command cap (exit 124/137) |
| `FAIL` | the tool's own nonzero exit |
| *missing* | **we** lost the work — walltime kill, eviction, dead node |

`reap.sh` prints `done/expected` with that breakdown. Missing entries are
reclaimed by `cluster/oarrun.sh --resume <runid>`, which re-submits into the
same run directory; commands that already have a status file are skipped.

## Shape of a run

`--split K` submits K jobs, each holding a whole node and running commands
`K`-strided through the list (interleaved, so a difficulty-ordered list spreads
evenly). Width per node is the core count OAR actually allocated, read from
`$OAR_NODEFILE` — never `nproc`, which reports the whole machine and would
oversubscribe it. The fleet is heterogeneous and no host class is requested; pin
one with `--resources '{(host like "tall%")}/nodes=1'` when timings must be
comparable.

Per-command cap defaults to **15s** (the discipline; `--timeout 0` disables it
and lets walltime bound the job). Job walltime defaults to **5 minutes**: shards
are sized to fit it rather than the reverse. Raise `--split` or `--cores`, not
the walltime. `oarrun.sh` warns when a shard looks too big and names the split
that would fit.

## The submit host does nothing

It is provisioned for submission, not for work. `oarrun.sh` makes K immediate
`oarsub` calls and exits; `reap.sh` only reads files. No backgrounding there, no
`nohup`, no poll loop anywhere on the cluster — progress is observed by calling
`reap.sh` again from the client.

Compute nodes have network, so the provisioning job downloads its own sources.

## Provisioning: from scratch, inside the folder

`provision.sh` builds every native dependency into the repo's own `opt/`. No
root, no `$HOME`, nothing system-wide; `rm -rf opt build` undoes it exactly. It
runs anywhere a compiler, `make` and `curl` exist — a raw Linux box, a
container, a compute node. On the cluster it is submitted as a job, because the
submit host cannot compile. Compute nodes have network, so the job fetches its
own sources.

**Spot.** [Spot-BinaryBuilds](https://github.com/yanntm/Spot-BinaryBuilds) is the
source of *version truth*, not of source: `build_spot.sh` clones it to read which
Spot release we track (often a tagged dev revision) and where its tarball lives,
then fetches that tarball and applies **our own** configure flags. Theirs targets
ITS-Tools — `--disable-shared`, static archives, no bindings — and we do
`import spot`, so we build shared with `--enable-python`. Out-of-tree: sources
and objects under `build/`, install to `opt/spot-<ver>/`.

The bindings compile against whichever `python3` the node has. That is the point
of building rather than downloading: a prebuilt `_spot.so` is bound to one
CPython ABI and one glibc, and the fleet is heterogeneous.

`--enable-max-accsets=64` (kept from their recipe) lifts Spot's default
32-acceptance-set ceiling, which our automata cross; a skipped oracle is not a
verified one.

**GAP + SgpDec.** `build_gap.sh` builds GAP from source into `opt/gap/` and
installs SgpDec into `opt/gap/pkg/`. There is no distro-package path: a result
must be a function of the commit, not of the GAP a given node happens to carry.
`opt/gap/bin/gap` is a generated wrapper that adds the prefix as an extra GAP
root and carries `libgap.so` on the loader path, which GAP's own (self-described
experimental) `make install` does not.

`env.sh` prepends both prefixes to `PATH` unconditionally, so ours win the lookup
and a missing build fails loudly instead of silently resolving to a system tool.
No source file changed for any of this: `bls/gap/runner.py` spawns a bare `gap`
and gets the wrapper; `import spot` resolves from the prefix. `provision.sh` ends
by proving each tool resolves under `opt/`, not merely that it runs.

## Files

| | |
|---|---|
| `config.sh` | client-side settings (host, paths, defaults); all overridable from the environment |
| `env.sh` | in-job environment on a compute node; finds `opt/spot-*` and `opt/gap` from the root |
| `provision.sh` | build spot + gap into `opt/`; runs on any Linux, no root |
| `build_spot.sh` | read the tracked version, fetch, out-of-tree build with Python bindings |
| `build_gap.sh` | build GAP from source, install SgpDec, write the `gap` wrapper |
| `sync_cluster.sh` | check out the cluster at this tree's HEAD (committed + pushed only) |
| `oarrun.sh` | submit a command list as K jobs |
| `oarsub.sh` | submit a single command |
| `oar_worker.sh` | one job: strided shard, `xargs -P <allocated cores>` |
| `oar_one.sh` | one command: cap, capture, atomic status |
| `reap.sh` | fetch, merge CSV shards, report `done/expected` |

`reap.sh` copies `~/git/BuchiToLTL/oarrun/<runid>/` to
`results/cluster/<runid>/` here.
