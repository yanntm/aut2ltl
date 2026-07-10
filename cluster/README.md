# cluster — submit, collect

Sends a list of shell commands to the OAR cluster and brings the results back.
The runner never knows what a command means, so a census sweep, a learning run
and the dependency build all go through it.

Building the dependencies is [`deps/`](../deps/README.md)'s job, not this
directory's. `deploy.sh` only submits that build as a job, because the submit host
cannot compile.

---

## Quick start

```bash
cluster/sync_cluster.sh                        # after each push
RUN=$(cluster/oarrun.sh --split 4 --cores 64 cmds.txt)
cluster/reap.sh "$RUN"                         # call again for progress
```

Build the dependencies on the cluster, when one of them moves. Three jobs, one per
dependency, in parallel — they are independent and write to disjoint prefixes:

```bash
cluster/sync_cluster.sh
cluster/reap.sh "$(cluster/deploy.sh)"
```

A dependency already in `opt/` is left alone. To replace one, remove its prefix on
the cluster (`rm -rf opt/gap`) and submit again.

---

## Commands and flags

### `deploy.sh [oarrun options...]` → prints a run id

Submits three jobs, one per dependency, each `deps/build_all.sh --<dep>-only`,
with `--cores $BUILD_JOBS --timeout 0 --walltime $DEPS_BUILD_WALLTIME`. They run
concurrently on three machines. `reap.sh` reports `3/3` when all are done, and
names the failing one otherwise.

### `sync_cluster.sh [rev]`

Fetches on the cluster and checks out `rev` (default `origin/master`). Consults
nothing local.

### `oarrun.sh [flags] cmds.txt` → prints a run id

| flag | default | |
|---|---|---|
| `--name SLUG` | basename of `cmds.txt` | tag in the run id |
| `--timeout SECONDS` | `15` | per-command wall-clock cap; `0` disables it |
| `--split K` | `1` | spread the list over K jobs |
| `--cores N` | `4` | cores **requested** per job, and commands in flight on them |
| `--walltime H:MM:SS` | `0:05:00` | per-job limit |
| `--resources STR` | `{host like 'tall%'}/nodes=1` | OAR resource string, minus the core term and walltime |
| `--oar-opts STR` | — | extra `oarsub` options, e.g. `--besteffort` |
| `--resume RUNID` | — | re-submit into an existing run; finished commands are skipped |
| `--dry-run` | — | print the `oarsub` calls, submit nothing |

Submits, per shard `k`:

```
oarsub -n <runid>.k -l {host like 'tall%'}/nodes=1/core=N,walltime=H:MM:SS \
  "$HOME/git/aut2ltl/cluster/oar_worker.sh $HOME/git/aut2ltl/oarrun/<runid> k K T"
```

### `oarsub.sh [flags] -- <command...>` → prints a run id

Single command through the same machinery. Takes `--name`, `--timeout`,
`--cores`, `--walltime`, `--resources`, `--oar-opts`, `--dry-run`. Use `--` when
the command has shell metacharacters.

### `reap.sh [--strict] [--quiet] RUNID`

Fetches the run into `results/cluster/<runid>/`, merges CSV shards, prints the
tally. `--strict` exits nonzero if any command is missing. Safe at any time;
calling it twice is how progress is observed.

`config.sh` holds every default (host, paths, OAR settings); all of it is
overridable from the environment.

---

## Contract for the commands

One shell command per line, run with the repo root as working directory, with
`deps/env.sh` already sourced.

**Output must be additive and flushed after each record.** Collection is then
decoupled from completion: a run still going, or killed at walltime, still yields
every result it produced. This is what makes `reap.sh` callable at any moment and
`--resume` cheap.

Each command gets:

| variable | |
|---|---|
| `$OARRUN_OUT` | a private output slot, `out/<idx>`; use as a file or create as a directory |
| `$OARRUN_RUN` | the run directory |
| `$OARRUN_IDX` | this command's 1-based index |
| `$OARRUN_ROOT` | the repo root |

**Do not append to one shared file**: `O_APPEND` is not atomic over NFS and
interleaves under fan-out. Write `$OARRUN_OUT.csv`; `reap.sh` concatenates the
shards in index order into `results.csv`, header once.

Stdout and stderr are line-buffered (`stdbuf`, `PYTHONUNBUFFERED=1`) into
`logs/<idx>.{out,err}`.

---

## Accounting

The status file is written last and atomically, so `reap.sh` distinguishes four
outcomes usually conflated:

| | meaning |
|---|---|
| `OK` | exit 0 |
| `TIMEOUT` | hit the per-command cap (exit 124/137) |
| `FAIL` | the tool's own nonzero exit |
| *missing* | **we** lost the work — walltime kill, eviction, dead node |

`reap.sh` prints `done/expected` with that breakdown. Missing entries are
reclaimed by `oarrun.sh --resume <runid>`, which re-submits into the same run
directory; commands that already have a status file are skipped.

---

## Shape of a run

`--split K` submits K jobs, each running commands `K`-strided through the list
(interleaved, so a difficulty-ordered list spreads evenly).

`--cores N` goes into the resource string as `/nodes=1/core=N`. Cores are asked
for, not taken: omitting the core term reserves the whole machine however narrow
the work. The worker reads the **granted** allocation back from `$OAR_NODEFILE`
— never `nproc`, which reports the whole machine — so reserved and used width
agree.

The host class is not a preference. `opt/` is compiled with the AVX2 instructions
of the machine that built it, so a job landing elsewhere dies of `SIGILL`; builds
and runs ask for the same class. It also makes timings comparable.

Job walltime defaults to **5 minutes**: shards are sized to fit it, not the
reverse. Raise `--split` or `--cores`, not the walltime. `oarrun.sh` warns when a
shard looks too big and names the split that would fit.

---

## Only committed code runs

The cluster runs what is on origin, so push before you sync. `reap.sh` is the
only transfer, always cluster → local; nothing is ever sent the other way.

## The submit host does nothing

It is provisioned for submission, not for work. `oarrun.sh` makes K immediate
`oarsub` calls and exits; `reap.sh` only reads files. No backgrounding there, no
`nohup`, no poll loop anywhere on the cluster — progress is observed by calling
`reap.sh` again from the client. Compute nodes have network, so the dependency
build downloads its own sources.

---

## Layout

Everything resolves from the repo root. The cluster checkout is `~/git/aut2ltl`
(`REMOTE_REPO` in `config.sh`); `opt/`, `build/`, `oarrun/` are subfolders of it,
root-anchored in `.gitignore`.

| | |
|---|---|
| `oarrun/<runid>/` | `cmds.txt`, `meta.json`, `out/`, `logs/`, `status/`, `oar/` |
| `results/cluster/<runid>/` | what `reap.sh` brings back, on the client |

## Files

| | |
|---|---|
| `config.sh` | every default; overridable from the environment |
| `deploy.sh` | submit the dependency build: one job per dependency, in parallel |
| `sync_cluster.sh` | check the cluster out at origin's master |
| `oarrun.sh` | submit a command list as K jobs |
| `oarsub.sh` | submit a single command |
| `oar_worker.sh` | one job: strided shard, `xargs -P <granted cores>` |
| `oar_one.sh` | one command: cap, capture, atomic status |
| `reap.sh` | fetch, merge CSV shards, report `done/expected` |
