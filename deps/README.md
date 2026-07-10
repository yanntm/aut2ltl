# deps — the native dependencies, built from source

Three things the pipeline needs and pip cannot provide. Each is built into the
repo's own `opt/`, from source, on any Linux. No root, no `$HOME`, nothing
system-wide. `rm -rf opt build` undoes it exactly.

Run [`../install.sh`](../install.sh) once; it calls `build_all.sh` and then checks
that the wrapper resolves each dependency. Nothing here knows about a cluster.

| | |
|---|---|
| `versions.sh` | which revision of each dependency; every value overridable from the environment |
| `env.sh` | the run-time environment; sourced, never run |
| `build_all.sh` | build all three, then verify |
| `build_spot.sh` | read the tracked version, fetch, out-of-tree build with Python bindings |
| `build_gap.sh` | GAP from source, its package chain, the `gap` wrapper |
| `build_its.sh` | libDDD + libITS from clean clones |
| `build_roll.sh` | ROLL (the sosl E3 FDFA baseline), packed to one portable jar |

`build_all.sh` takes `--spot-only` / `--gap-only` / `--its-only` /
`--roll-only`; the build scripts take nothing at all.

ROLL is not part of the default build: it is an experiment baseline, not a
pipeline dependency, and needs a system JDK and maven. It has no released
distribution, so `--roll-only` clones its GitHub at HEAD, runs the project's
own `build.sh` (maven, then a repack into one self-contained jar, RABIT
included), and installs `opt/roll/ROLL.jar`; `env.sh` exports `ROLL_JAR` when
that file exists. Being bytecode, it is the one artifact that ignores the
machine-class caveat below.

## Updating a dependency

There is no `--force`, because there is nothing a flag would say that removing
the prefix does not say better. A dependency present in `opt/` is used as it is;
a dependency absent from `opt/` is built.

```bash
git pull                     # take whatever versions.sh now names
rm -rf opt/gap               # or opt/spot, or opt/its
./install.sh                 # rebuilds only what is missing
```

Spot is the case that catches people. `versions.sh` names
[Spot-BinaryBuilds](https://github.com/yanntm/Spot-BinaryBuilds), not a Spot
version: `build_spot.sh` clones that repo *at build time* and reads the release it
tracks, which is often a tagged dev revision. So the Spot you get is whatever that
repo said on the day `opt/spot` was built, and picking up an upstream change to it
means `rm -rf opt/spot && ./install.sh` — nothing in this checkout will notice on
its own.

## The builds are machine-specific

`semigroups` vendors `libsemigroups`, which compiles HPCombi's **AVX2** intrinsics
whenever the compiler offers them. We let it: HPCombi is a large constant-factor
win on exactly the transformation-semigroup work SgpDec does. The price is that
`opt/` runs on machines with AVX2 and raises `SIGILL` on the others.

Nothing detects this for you. A checkout shared between machines — an NFS home,
say — must be built on, and used from, machines of the same class. That is why
`cluster/config.sh` asks OAR for one.

## The dependencies

**Spot.** [Spot-BinaryBuilds](https://github.com/yanntm/Spot-BinaryBuilds) is the
source of *version truth*, not of source: `build_spot.sh` clones it to read which
Spot release we track (often a tagged dev revision) and where its tarball lives,
then fetches that tarball and applies **our own** configure flags. Theirs targets
ITS-Tools — `--disable-shared`, static archives, no Python bindings — and we do
`import spot`, so we build shared with `--enable-python`, out-of-tree.

The bindings compile against whichever `python3` is present. That is why we build
rather than download: a prebuilt `_spot.so` is bound to one CPython ABI and one
glibc.

`--enable-max-accsets=64` (kept from their recipe) lifts Spot's default
32-acceptance-set ceiling, which our automata cross; a skipped oracle is not a
verified one.

**GAP + SgpDec.** Built from source; there is no distro-package path, since a
result must be a function of the commit rather than of the GAP a machine carries.
GAP's own `make install` warns that it installs **no packages**, so SgpDec's
closure — `GAPDoc, orb, semigroups, datastructures, digraphs, genss, images, IO` —
is compiled with GAP's `BuildPackages.sh` and copied into the prefix. Only the
packages that actually produced a kernel module are installed: a failed compile
leaves its source directory behind, and installing that would defer the failure
to whoever loads it.

`opt/gap/bin/gap` is a generated wrapper: it carries `libgap.so` on the loader
path, adds the prefix as an extra GAP root, and passes `-r` so `$HOME/.gap` is
dropped from `GAPInfo.RootPaths` — a package in the account would otherwise
outrank ours.

GAP vendors GMP, whose `configure` probe declares `void g(){}` and calls it with
arguments: valid up to C17, an error under gcc 14+'s default C23, which GMP reads
as "no working compiler". Hence `CC="gcc -std=gnu17"` — the dialect is pinned,
not the compiler, so older machines behave alike.

One GAP is kept, whatever version it is; it moves rarely and an older one serves.
Upgrading is `rm -rf opt/gap`, done deliberately: the packages carry kernel
modules compiled against one GAP, and mixing them does not work, so the prefix is
replaced whole or not at all.

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
