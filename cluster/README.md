# cluster — run a list of commands on the OAR cluster

Generic. The runner never knows what a command means: a census sweep and a
multi-hour learning run go through the same three entry points.

```
cluster/sync_cluster.sh                        # push the working tree
RUN=$(cluster/oarrun.sh --split 4 cmds.txt)    # submit, prints a run id
cluster/reap.sh "$RUN"                         # fetch + report; call again for progress
```

## Contract for the commands

One shell command per line, run from the repo root on a compute node.

**Output must be additive and flushed after each record.** Collection is then
decoupled from completion: a run that is still going, or that was killed at
walltime, still yields every result it produced. This is what makes `reap.sh`
callable at any moment and `--resume` cheap.

Each command gets `$OARRUN_OUT`, a private output slot (`out/<idx>`) it may use
as a file or create as a directory. **Do not append to one shared file**:
`O_APPEND` is not atomic over NFS and interleaves under a whole-node fan-out.
Write `$OARRUN_OUT.csv` and `reap.sh` concatenates the shards in index order
into `results.csv`, header once. Also set: `$OARRUN_RUN`, `$OARRUN_IDX`.

Stdout and stderr are line-buffered (`stdbuf`, `PYTHONUNBUFFERED=1`) into
`logs/<idx>.{out,err}`.

## Accounting

Each command's status file is written last and atomically, so `reap.sh`
distinguishes three outcomes that are usually conflated:

| | meaning |
|---|---|
| `OK` | exit 0 |
| `TIMEOUT` | hit the per-command cap (exit 124/137) |
| `FAIL` | the tool's own nonzero exit |
| *missing* | **we** lost the work — walltime kill, eviction, dead node |

`reap.sh` prints `done/expected` with that breakdown. Missing entries are
reclaimed by `cluster/oarrun.sh --resume <runid>`, which re-submits into the
same run directory; commands with a status file are skipped.

## Shape of a run

`--split K` submits K jobs, each holding a whole node and running commands
`K`-strided through the list (interleaved, so a difficulty-ordered list spreads
evenly). Width per node is `nproc`, read on whichever machine the job lands on —
the fleet is heterogeneous and no host class is requested. Pin one via
`--resources '{(host like "tall%")}/nodes=1'` when timings must be comparable.

Per-command cap defaults to **15s** (the discipline; `--timeout 0` disables it
and lets walltime bound the job). Job walltime defaults to **5 minutes**: a job
holds a whole node, so shards are sized to fit rather than the reverse. Raise
`--split`, not the walltime. `oarrun.sh` warns when the shard looks too big and
suggests a split.

## Rules this respects

The submit host is provisioned for submission only. Nothing of ours runs there:
`oarrun.sh` makes K immediate `oarsub` calls and exits, `reap.sh` only reads
files. No backgrounding, no `nohup`, no poll loop on the cluster — progress is
observed by calling `reap.sh` again from the client.

Builds happen in an interactive job (`oarsub -I`), never on the submit host.
Python needs none; `cluster/env.sh` (sourced inside the job) is the one place
that says how `python3` and `spot` become importable.

## Files

| | |
|---|---|
| `config.sh` | client-side settings (host, paths, defaults); all overridable from the environment |
| `env.sh` | in-job environment on a compute node — **edit this to activate python3 + spot** |
| `sync_cluster.sh` | `rsync` the working tree up (uncommitted work included; no forced commits) |
| `oarrun.sh` | submit a command list as K jobs |
| `oar_worker.sh` | one job: strided shard, `xargs -P $(nproc)` |
| `oar_one.sh` | one command: cap, capture, atomic status |
| `reap.sh` | fetch, merge CSV shards, report `done/expected` |

Run directories live in `~/oarrun/<runid>/` on the cluster — outside the repo,
so `sync_cluster.sh --delete` cannot reach them. `reap.sh` copies them to
`results/cluster/<runid>/`.

## First run

`env.sh` ships as a no-op, so the first thing to do is find out what the nodes
actually have. The smoke test is an ordinary run:

```
printf 'python3 -c "import spot; print(spot.version())"\n' > /tmp/smoke.txt
cluster/sync_cluster.sh
cluster/reap.sh "$(cluster/oarrun.sh --name smoke --walltime 0:02:00 /tmp/smoke.txt)"
cat results/cluster/*-smoke/logs/1.out results/cluster/*-smoke/logs/1.err
```

If that fails, fix `env.sh` and resubmit. It is the only way to learn the node
environment: the submit host cannot import the stack.
