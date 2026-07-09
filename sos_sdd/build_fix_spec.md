# Task: make the sos_sdd `_core` extension pass its smoke test

**Goal (the only success criterion).** From `sos_sdd/`:

```
rm -rf build && cmake -B build && cmake --build build
cd .. && timeout 15 python3 tests/sos_sdd/smoke_core.py   # must print SUCCESS
timeout 15 python3 tests/sos_sdd/smoke_api.py             # must stay SUCCESS
```

Do **not** weaken or delete any assertion in either test to get there.

## Current state (verified facts, in order)

1. libDDD is built from source at `/home/ythierry/git/libDDD`
   (`autoreconf -vfi && ./configure && make -j`). Artifacts in
   `ddd/.libs/`: `libDDD.a`, `libDDD.so.0.0.0`, plus `_d` debug variants.
   Build log: `tests/sos_sdd/logs/libddd_build.log`.
2. Linking `_core` against **libDDD.so** fails at import:
   `undefined symbol: _ZN4GDDD3oneE`. `nm -D libDDD.so.0` shows only ~2
   exported symbols — the shared build hides nearly everything. The
   owner confirms the `.so` path has never been used; **the static
   archive is the supported mode**. Abandoned; do not revisit unless
   everything else fails (see "last resort" below).
3. Linking against **libDDD.a** (current `CMakeLists.txt`, which prefers
   `libDDD.a` explicitly): compiles and links clean, module imports,
   then **SIGSEGV during `_core.selftest(...)`** — crash frames inside
   `_core.so` (no symbols; release + LTO), reached from the first
   selftest call. Backtrace and logs: `tests/sos_sdd/logs/`.
4. Toolchain: Fedora 43, g++, cmake 3.31, python 3.14, pybind11 from
   dnf (`pybind11-devel`, `python3-pybind11`). `pybind11_add_module`
   enables LTO by default (`lto-wrapper` warnings in the build log are
   that, and are harmless).

## Hypothesis 1 — near-certain, fix this first: GC use-after-free in our own code

libDDD garbage-collects any `GDDD`/`GHom` not held through the
reference-counted wrappers `DDD`/`Hom` when `MemoryManager::garbage()`
runs. Our instrumentation calls `garbage()` at **every** operation-bracket
close (`Stats::Op::close()` in `src/stats.hh`, `gc_per_op=true` set in
`make_stats()` in `src/module.cpp`). The selftest then violates the
holding rule (stated in `src/primitives.hh` and not followed):

- `GDDD rel` — bare; swept at the first `closure-step` close.
- `GHom step = apply2k(rel)` — `GHom` has no refcount; swept likewise.
  Its next application dereferences a deleted `_GHom`. This alone
  explains the crash.
- `GDDD next` inside the layered loop — bare when `round_op.close()`
  fires; the subsequent `next == layered` / `layered = next` reads a
  swept node.

**Fix, two parts:**

1. In `src/module.cpp` (selftest): hold every diagram/hom that survives
   an Op close through the counted types — `DDD rel_holder(rel)` is not
   enough on its own; the clean pattern is `DDD rel = ...;`
   `Hom step = apply2k(rel);` and `DDD next` inside the loop (note
   `Apply2k::mark()` marks its relation, so a `Hom` also protects the
   diagram it wraps, but keep `rel` as `DDD` anyway for the rule's
   sake). Every local that crosses an Op-bracket boundary must be
   `DDD`/`Hom`, including temporaries like `B - A` if an Op closes
   between creation and use (currently none does in that section —
   check, don't assume, after your edits).
2. In `src/module.cpp` `make_stats()`: change both `gc_per_op` arguments
   to **false** (default off). Per-op GC makes *every* engine
   intermediate a GC hazard forever; peaks are then refreshed only at
   explicit `collect()` points (there is one before the verdict record).
   Update the comment in `src/stats.hh` above `gc_per_op` accordingly:
   it trades exact per-op peaks for the obligation that *all* live
   intermediates be refcount-held; default off.

Then rebuild and rerun the gate. Expect SUCCESS. If the numbers change
(they should not — GC never changes set contents, only whether the
`table_*` figures shrink), do not adjust test assertions; investigate.

## Hypothesis 2 — only if the crash survives Hypothesis 1's fix

A compile-flag/ABI mismatch between the archive and our translation
unit: libDDD was built by autotools with its own `DEFS`/`CXXFLAGS`
(possibly `-DHAVE_CONFIG_H` and hash-container selection macros that
change header-defined types), while `src/module.cpp` includes the same
headers with none of those defines — a layout mismatch in header-inlined
code would crash exactly at first unicity-table use.

Recipe:
1. Get the true flags: `cd /home/ythierry/git/libDDD/demo && make V=1`
   (or read `DEFS`/`AM_CPPFLAGS`/`CXXFLAGS` in `ddd/Makefile`). Note
   every `-D` and `-std=` in a real compile line.
2. Write a **standalone C++ probe** (no Python): `sos_sdd/src/probe.cpp`
   with a `main()` doing what selftest does; add a temporary CMake
   executable target linking the same `libDDD.a`. If the probe crashes
   with our flags and passes with the demo's flags, mirror the missing
   defines via `target_compile_definitions(_core PRIVATE ...)` and
   delete nothing until the smoke gate is green. Keep the probe target
   (it is a useful valgrind/gdb entry point) — mention it in the commit.
3. Independently cheap to try: `pybind11_add_module(_core NO_EXTRAS
   src/module.cpp)` disables LTO/strip — gives symbolized backtraces
   with `-DCMAKE_BUILD_TYPE=Debug`, and rules LTO in or out.

## Hypothesis 3 — last resort, requires owner sign-off before doing it

If (and only if) static linking is genuinely unusable, the fallback is a
libDDD-side change: make its shared library export symbols properly
(visibility), **added alongside** the existing artifacts. Hard
constraints from the owner: the `.a` and its build flags must not
change in any way (all downstream projects consume the `.a` exclusively,
with `-fwhole-program` and static glibc); the change must build on
GitHub Actions (that is the real distro test); nothing is committed in
`/home/ythierry/git/libDDD` — produce a patch file under
`tests/sos_sdd/logs/` plus a short writeup, and stop there.

## Working rules (repo discipline, non-negotiable)

- Diagnostic runs: ≤15s each, one input per invocation; long output
  redirected to `tests/sos_sdd/logs/`, never `/tmp`, never piped to
  `tail` mid-run. A blown timeout is a finding to report, not something
  to work around.
- No process management (`kill`, `&`, `nohup`); background via the
  harness only.
- Tests live under `tests/` as placed scripts — no `python -c`
  one-liners.
- Commits: `git commit -F -` with a quoted heredoc, terse message, no
  backticks in the message. Related files may share one commit. Never
  amend/rebase; fix forward. Do not touch files outside `sos_sdd/`,
  `tests/sos_sdd/`, and (read-only) `/home/ythierry/git/libDDD`.
- When done: both smoke tests SUCCESS, work committed, and a short
  summary of root cause + what changed appended to this file under a
  "## Resolution" heading (part of the final commit).

## Resolution (fixed in-session; no delegation needed)

Hypothesis 1, confirmed by the library author: bare `GDDD`/`GHom` locals
(`rel`, `step`, `next`) were swept by `MemoryManager::garbage()` fired
from the per-op stats bracket; the next application dereferenced a
deleted `_GHom`. Fix: counted `DDD`/`Hom` handles for everything that
outlives a step, and the instrumentation no longer triggers collection
at all — memory management is libDDD's alone (author guidance; it
collects when useful). `table_peak` now reads the library's own
high-water mark, possibly stale between its GCs; stats are advisory.
Static `libDDD.a` is the linking mode (the `.so` exports nothing and is
unused upstream). Both smoke tests SUCCESS.
