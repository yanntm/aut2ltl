# cluster — provision, submit, collect

Two independent things live here.

**Provisioning** builds every native dependency into the repo's own `opt/`, from
source, on any Linux. No root, no `$HOME`, nothing system-wide.

**Running** sends a list of shell commands to the OAR cluster and brings the
results back. The runner never knows what a command means, so a census sweep, a
learning run and the provisioning build all go through it.

---

## Quick start

```bash
cluster/sync_cluster.sh                        # after each push
RUN=$(cluster/oarrun.sh --split 4 --cores 64 cmds.txt)
cluster/reap.sh "$RUN"                         # call again for progress
```

Provisioning is an ordinary job, run when a dependency moves:

```bash
cluster/sync_cluster.sh
cluster/reap.sh "$(cluster/oarsub.sh --timeout 0 --cores 10 --walltime 3:00:00 \
                     -- cluster/provision.sh)"
```

Locally, no cluster involved:

```bash
cluster/provision.sh          # build spot + gap + libDDD/libITS into opt/
source cluster/env.sh         # put them on PATH / PYTHONPATH / LIBDDD_HOME
```

---

## Commands and flags

### `provision.sh [--force] [--spot-only|--gap-only|--its-only]`

Builds Spot, GAP+SgpDec, libDDD+libITS into `opt/`. Ends by asserting each tool
resolves **under `opt/`** — a tool that merely answers is not a tool that came
from this tree.

| flag | |
|---|---|
| *(none)* | build what is missing or stale; leave a matching install alone |
| `--force` | rebuild and replace every prefix, even at the same version |
| `--spot-only` `--gap-only` `--its-only` | one dependency |

Each dependency keeps **one** install, stamped with its version in
`opt/<name>/.version`. The stamp is written **last**, after the verify step, so
an interrupted or unloadable install is never mistaken for a good one. A version
change replaces the prefix; `--force` is only needed to rebuild the same version.

### `build_spot.sh [--rebuild] [spot_version]`

`--rebuild` replaces the install. A positional version overrides what the tracked
repo says (e.g. `2.14.5.dev`).

### `build_gap.sh [--rebuild]`

Replaces GAP **and its packages** together: package kernel modules are compiled
against one GAP, and mixing them does not work.

### `build_its.sh [--rebuild]`

### `sync_cluster.sh`

Checks the cluster out detached at the local HEAD commit. No flags.

### `oarrun.sh [flags] cmds.txt` → prints a run id

| flag | default | |
|---|---|---|
| `--name SLUG` | basename of `cmds.txt` | tag in the run id |
| `--timeout SECONDS` | `15` | per-command wall-clock cap; `0` disables it |
| `--split K` | `1` | spread the list over K jobs |
| `--cores N` | `4` | cores **requested** per job, and commands in flight on them |
| `--walltime H:MM:SS` | `0:05:00` | per-job limit |
| `--resources STR` | `/nodes=1` | OAR resource string, minus the core term and walltime |
| `--oar-opts STR` | — | extra `oarsub` options, e.g. `--besteffort` |
| `--resume RUNID` | — | re-submit into an existing run; finished commands are skipped |
| `--dry-run` | — | print the `oarsub` calls, submit nothing |

Submits, per shard `k`:

```
oarsub -n <runid>.k -l /nodes=1/core=N,walltime=H:MM:SS \
  "$HOME/git/aut2ltl/cluster/oar_worker.sh $HOME/git/aut2ltl/oarrun/<runid> k K T auto"
```

### `oarsub.sh [flags] -- <command...>` → prints a run id

Single command through the same machinery. Takes `--name`, `--timeout`,
`--cores`, `--walltime`, `--resources`, `--oar-opts`, `--dry-run`. Use `--` when
the command has shell metacharacters.

### `reap.sh [--strict] [--quiet] RUNID`

Fetches the run into `results/cluster/<runid>/`, merges CSV shards, prints the
tally. `--strict` exits nonzero if any command is missing. Safe at any time;
calling it twice is how progress is observed.

### `env.sh`

Sourced, not run. Prepends `opt/spot/bin` and `opt/gap/bin` to `PATH`, Spot's
`lib{,64}` to `LD_LIBRARY_PATH`, its Python bindings to `PYTHONPATH`, and exports
`LIBDDD_HOME=opt/its`. Prefixes go in front **unconditionally**, so a missing
build fails loudly instead of resolving to a system tool.

`config.sh` holds every default (host, paths, versions, `BUILD_JOBS`); all of it
is overridable from the environment.

---

## Contract for the commands

One shell command per line, run with the repo root as working directory.

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

No host class is requested and no node is pinned. Prepend one with
`--resources '{(host like "tall%")}/nodes=1'` when timings must be comparable.

Job walltime defaults to **5 minutes**: shards are sized to fit it, not the
reverse. Raise `--split` or `--cores`, not the walltime. `oarrun.sh` warns when a
shard looks too big and names the split that would fit.

---

## Only committed code runs

`sync_cluster.sh` checks the cluster out detached at the local HEAD commit — not
at the remote's tip — so a run's recorded `git_rev` names the code that ran. An
unpushed HEAD is refused: the cluster fetches from origin and could not reach it.
Uncommitted changes are ignored; they do not travel. Nothing is pushed for you,
and `reap.sh` is the only transfer, always cluster → local.

## The submit host does nothing

It is provisioned for submission, not for work. `oarrun.sh` makes K immediate
`oarsub` calls and exits; `reap.sh` only reads files. No backgrounding there, no
`nohup`, no poll loop anywhere on the cluster — progress is observed by calling
`reap.sh` again from the client. Compute nodes have network, so the provisioning
job downloads its own sources.

---

## The dependencies

**Spot.** [Spot-BinaryBuilds](https://github.com/yanntm/Spot-BinaryBuilds) is the
source of *version truth*, not of source: `build_spot.sh` clones it to read which
Spot release we track (often a tagged dev revision) and where its tarball lives,
then fetches that tarball and applies **our own** configure flags. Theirs targets
ITS-Tools — `--disable-shared`, static archives, no Python bindings — and we do
`import spot`, so we build shared with `--enable-python`, out-of-tree.

The bindings compile against whichever `python3` the node has. That is why we
build rather than download: a prebuilt `_spot.so` is bound to one CPython ABI and
one glibc, and the fleet is heterogeneous.

`--enable-max-accsets=64` (kept from their recipe) lifts Spot's default
32-acceptance-set ceiling, which our automata cross; a skipped oracle is not a
verified one.

**GAP + SgpDec.** Built from source; there is no distro-package path, since a
result must be a function of the commit rather than of the GAP a node carries.
GAP's own `make install` warns that it installs **no packages**, so SgpDec's
closure — `GAPDoc, orb, semigroups, datastructures, digraphs, genss, images, IO`
— is compiled with GAP's `BuildPackages.sh` and copied into the prefix.
`opt/gap/bin/gap` is a generated wrapper: it carries `libgap.so` on the loader
path, adds the prefix as an extra GAP root, and passes `-r` so `$HOME/.gap` is
dropped from `GAPInfo.RootPaths` — a package in the account would otherwise
outrank ours.

GAP vendors GMP, whose `configure` probe declares `void g(){}` and calls it with
arguments: valid up to C17, an error under gcc 14+'s default C23, which GMP reads
as "no working compiler". Hence `CC="gcc -std=gnu17"` — the dialect is pinned,
not the compiler, so older nodes behave alike.

**libDDD + libITS.** Cloned into `build/`, installed into `opt/its`, reached by
CMake through `LIBDDD_HOME`, the override `sos_sdd/CMakeLists.txt` already
honours — no build-file changes. Only libITS's gal expression component is
consumed; its `bin/` tools want headers nothing here needs, so a partial `make`
is tolerated and the artifact check is the gate. Both projects clear `CXXFLAGS`
before `AC_PROG_CXX`, suppressing autoconf's default `-g -O2`, so an unconfigured
build is `-O0` with `-flto`: the IR bloat of link-time optimization without the
optimization. `-O2` and `-DNDEBUG` are therefore stated, not inherited; DDD's
asserts sit in the hot path.

No source file changed for any of this: `bls/gap/runner.py` spawns a bare `gap`
and gets the wrapper, `import spot` resolves from the prefix, and CMake reads an
environment variable it already supported.

---

## Layout

Everything resolves from the repo root. The cluster checkout is `~/git/aut2ltl`
(`REMOTE_REPO` in `config.sh`); `opt/`, `build/`, `oarrun/` are subfolders of it,
root-anchored in `.gitignore`.

| | |
|---|---|
| `opt/spot` `opt/gap` `opt/its` | the installs, one each, version-stamped |
| `build/` | clones, tarballs, object trees; disposable |
| `oarrun/<runid>/` | `cmds.txt`, `meta.json`, `out/`, `logs/`, `status/`, `oar/` |
| `results/cluster/<runid>/` | what `reap.sh` brings back, on the client |

`rm -rf opt build` undoes provisioning exactly.

## Files

| | |
|---|---|
| `config.sh` | every default; overridable from the environment |
| `env.sh` | in-job environment; sourced, never run |
| `provision.sh` | build all dependencies into `opt/` |
| `build_spot.sh` | read the tracked version, fetch, out-of-tree build with Python bindings |
| `build_gap.sh` | GAP from source, its package chain, the `gap` wrapper |
| `build_its.sh` | libDDD + libITS from clean clones |
| `sync_cluster.sh` | check the cluster out at this tree's HEAD |
| `oarrun.sh` | submit a command list as K jobs |
| `oarsub.sh` | submit a single command |
| `oar_worker.sh` | one job: strided shard, `xargs -P <granted cores>` |
| `oar_one.sh` | one command: cap, capture, atomic status |
| `reap.sh` | fetch, merge CSV shards, report `done/expected` |
