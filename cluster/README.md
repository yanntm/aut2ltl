# cluster — run a benchmark on the OAR cluster

The cluster is deployed and working. Push your code to `master`, then:

```bash
git push                                       # only committed code runs
cluster/sync_cluster.sh                        # bring master onto the cluster
RUN=$(cluster/oarrun.sh cmds.txt)              # defaults: 8 jobs, 2 cores each
cluster/reap_until.sh "$RUN"                   # run this in the background
```

Results arrive in `logs/cluster/$RUN/results.csv`, with `logs/` beside it. That
is the whole interface. You do not build anything, you do not log into the cluster,
and you do not need to understand what follows.

`reap_until.sh` is how you wait: it reaps in a loop and turns on the `missing`
count, so it ends whether the run completes or the cluster loses work — exit 0 when
every command is accounted for, exit 3 when the counts freeze (a stall), naming the
resume command. Put it in the background and be notified on completion rather than
waiting on it: no polling by hand, no progress-watching. It takes several runs at
once.

A bare `cluster/reap.sh "$RUN"` still works and is still safe at any moment — it
collects whatever exists so far and prints the tally.

Accounted for is not the same as succeeded: a command that fails or times out has a
verdict, so it never blocks completion — but it needs a **re-plan**, not a resume
(`--resume` skips anything with a status file). Only *lost* work is reclaimed, with
`cluster/oarrun.sh --resume "$RUN"`, which re-submits just the gaps. Resume only
once a stall is confirmed: re-submitting while the originals still run makes both
copies write, into different shards, and `reap.sh` concatenates **both** —
duplicate rows that corrupt every tally.

`cmds.txt` is one shell command per line. Each runs at the repo root with the
dependencies (Spot, GAP + SgpDec, libDDD/libITS, and `$ROLL_JAR` when deployed)
already on `PATH`, and writes its
CSV to `$OARRUN_OUT.csv` — never to a shared file. See
[Contract for the commands](#contract-for-the-commands).

Two defaults will bite a long benchmark:

- `--timeout 130` caps **each command**. Raise it past your slowest single command,
  or pass `0` to disable. A command that exceeds it is reported `TIMEOUT`, not lost.
- `--walltime 0:05:00` caps **each job**. Rather than raise it, raise `--split` so
  the shards fit; `oarrun.sh` warns and names the split that would.

`--cores 2` is deliberate and rarely wants raising: a command is a sequential run,
so extra cores idle. Throughput comes from `--split`.

`reap.sh` is safe to call while the run is still going: it collects whatever has
been produced so far. Commands report `OK` / `TIMEOUT` / `FAIL`, and anything the
cluster lost is *missing* and reclaimed with `oarrun.sh --resume "$RUN"`.

Since `sync_cluster.sh` fast-forwards the cluster's checkout of `master`, it fails
rather than discard work if that tree has commits of its own. That failure is
information; do not force past it.

---

## Other scenarios

**Check the infra is alive.** Four commands, each asking one dependency to identify
itself on the granted node; expect `4/4 done — 4 ok` and a four-row `results.csv`:

```bash
cluster/reap.sh "$(cluster/oarrun.sh --split 2 --cores 4 cluster/smoke.txt)"
```

**One command, not a list.** `cluster/oarsub.sh [flags] -- <command...>`, same
machinery, same run id.

**Rebuild a dependency**, when one of them moves. Four jobs, one per dependency, in
parallel — they are independent and write to disjoint prefixes:

```bash
cluster/sync_cluster.sh
cluster/reap.sh "$(cluster/deploy.sh)"
```

A dependency already in `opt/` is left alone. To replace one, remove its prefix on
the cluster (`rm -rf opt/gap`) and submit again. Building is
[`deps/`](../deps/README.md)'s job, not this directory's; `deploy.sh` only submits
that build as a job, because the submit host cannot compile.

---

## What this is

Sends a list of shell commands to the OAR cluster and brings the results back.
The runner never knows what a command means, so a census sweep, a learning run
and the dependency build all go through it.

---

## Commands and flags

### `deploy.sh [oarrun options...]` → prints a run id

Submits four jobs, one per dependency, each `deps/build_all.sh --<dep>-only`,
with `--cores $BUILD_JOBS --timeout 0 --walltime $DEPS_BUILD_WALLTIME`. They run
concurrently on four machines. `reap.sh` reports `4/4` when all are done, and
names the failing one otherwise.

### `sync_cluster.sh [rev]`

Fetches on the cluster and checks out `rev` (default `origin/master`). Consults
nothing local.

### `oarrun.sh [flags] cmds.txt` → prints a run id

| flag | default | |
|---|---|---|
| `--name SLUG` | basename of `cmds.txt` | tag in the run id |
| `--timeout SECONDS` | `130` | per-command wall-clock cap; `0` disables it |
| `--split K` | `8` | spread the list over K jobs |
| `--cores N` | `2` | cores **requested** per job, and commands in flight on them |
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
`--cores`, `--walltime`, `--resources`, `--oar-opts`, `--dry-run`. After `--`,
several words are an argv reproduced on the node exactly as given; for shell
syntax (pipes, `&&`, redirects) pass the whole line as one quoted argument,
taken verbatim.

### `reap.sh RUNID`

Fetches the run into `logs/cluster/<runid>/` (ignored scratch), merges the CSV shards, prints the
tally. Exits 0 once every command has a status file, nonzero while any has none.
Takes no flags: the exit code is what a wait loop needs, and reading files on the
cluster is safe at any time, so calling it again is how progress is observed.

### `reap_until.sh [--rounds N] [--every S] [--stall K] RUNID...`

The way to **wait** for one or more runs — background it. Reaps in a loop and turns
on the `missing` count, so lost work ends the wait instead of hanging it:

| exit | |
|---|---|
| `0` | `ALL_ACCOUNTED` — every command of every run has a verdict |
| `3` | `STALLED` — `missing` unchanged for `--stall` rounds (default 4, i.e. past a walltime); prints the resume command |
| `4` | `--rounds` exhausted |

It never auto-resumes: that is the duplicate-row trap, and reclaiming lost work is
a decision, not a reflex.

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
shards into `results.csv`, header once. Row order across shards is not meaningful —
the commands ran in parallel — so a consumer keys on a column, never on position.

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
reverse. Raise `--split`, not the walltime, and not `--cores` — a command is
sequential, so a wider job idles the cores it reserved. `oarrun.sh` warns when a
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
| `logs/cluster/<runid>/` | what `reap.sh` brings back, on the client; ignored scratch |

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
| `reap_until.sh` | wait for runs: reap in a loop, end on all-accounted or a stall |
