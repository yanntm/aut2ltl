# sos_sdd — symbolic SoS engine (libDDD core, Python API)

A C++/libDDD engine computing the syntactic ω-semigroup invariant `𝓘(L)` of
a Büchi automaton symbolically — multi-valued DDD now, hierarchical SDD as
the growth path — exposed to Python as a `SoS` class carrying the calculus
operators as its high-level API. It implements Phases 0–6 of the paper
(`research_notes/sos_symbolic.md`) and the §6 calculus moves; the experiment
contract is `research_notes/sos_symbolic_experiments.md` (C1–C10, E0–E9).

The engine changes *representation, never mathematics*: on every instance
where the explicit reference construction (`sosl.sos.build`) terminates, the
emitted `.sos` must be byte-identical to the reference's (the conformance
gate, spec §3). The serializer therefore mirrors
`sosl/sosl/sos/io/serialize.py` exactly.

This document is the IO contract — the Python API surface, the
instrumentation stream, the failure taxonomy. It is written before the code;
the code conforms to it.

## Architecture

- **C++ core** (`src/`): the five §2.2 primitives over libDDD, the phase
  homomorphisms, the calculus moves. All diagram traffic stays on this side;
  the binding is coarse-grained (one call per phase or move, never per node).
- **pybind11 module** `sos_sdd`: the `SoS` class and the engine
  configuration. No HOA parsing in C++ — Python digests inputs (the parser
  half of C2 exists in-repo) and passes plain data across the binding. No
  interchange file format: the automaton digest is an argument, not a file.
- **Python drivers** under `tests/`: sweep the C9 switches, compare emitted
  `.sos` against the reference (`cmp`), write the experiment ledgers.
  Conformance comparison is the driver's job, not the engine's.

## Input digest (Python → binding)

`sos_sdd.Automaton` — the §2.3 input contract, digested:

```python
Automaton(name="evenblocks",
          ap=["a"],                  # ordered; α ranges over 2^ap, never enumerated
          states=2, init=0,
          marks=2,                   # |C|; marks are 0..|C|-1
          acceptance="Inf(0)&Inf(1)",# HOA acceptance formula over the marks
          trans=[(0, "a", 1, {0}),   # (src, guard-cube, dst, mark set)
                 (0, "!a", 0, set()),
                 ...])
```

Guards are DNF cube strings over the declared APs (`a&!b`); a multi-cube
guard is several `trans` entries. Product families (C8) are structured, the
global automaton never expanded on the Python side:

```python
Product(components=[eb0, eb1, eb2],  # Automaton each
        mode="async")                # async: disjoint APs and marks,
                                     #   acceptance = conjunction
                                     # sync: APs shared by name
```

## Engine configuration (the C9 switches)

Every switch the E7/E8 sweeps need is a constructor argument, not a fork:

```python
eng = sos_sdd.Engine(
    coords="factored",        # or "flat" — slot space of a Product (C8/E2/E3)
    slot_perm="natural",      # "reverse" | explicit permutation list (E7)
    slot_encoding="packed",   # one variable per slot, domain Q×2^C (§4.2)
                              # | "split-sm" (state var above mark bits)
                              # | "split-il" (interleaved)          (E7)
    alpha="top",              # α-block position in relation diagrams (E7)
    fp1="layered", fp5="layered",
                              # | "chaining" | "saturation" (E8); a
                              # non-layered Phase 1 runs a costed
                              # length-reconstruction pass for shortlex,
                              # reported as its own op record
    square="check",           # squaring AND general pairing, compared —
                              # disagreement raises StopTheLine (C4)
                              # | "on" (shortcut trusted) | "off"
    quotient="explicit",      # small-side fallback, recorded (spec §5) | "symbolic"
    node_budget=0,            # live-node cap; 0 = unlimited (C3)
    time_budget=0.0,          # wall seconds; 0 = unlimited
    stats=None)               # path (JSONL) or callable(dict) (C1)
```

The first stats record echoes the resolved configuration
(`{"ev":"config", ...}`), so a ledger line is reproducible from its log.

## The `SoS` class

```python
S = eng.build(aut)                  # Phases 0–6
S = eng.build(aut, until_phase=1)   # M1 form: closure only; later-phase
                                    # accessors raise on a partial object
```

**Readings** (E0/E1/E5 are readings of these):

```python
S.em1_count()      # |EM¹| by model count
S.depth            # closure depth (longest shortlex key)
S.layers           # [(k, cardinality, nodes)] — kept layers (C3)
S.nodes            # (final, peak) live diagram nodes
S.to_sos()         # the .sos text — canonical, byte-identical to the
                   # reference; forces reduce() (below)
S.n_states()       # global automaton states (mixed-radix over the
                   # component blocks, block 0 most significant)
S.residual_classes()  # Phase 4's ≃-partition: state ids grouped by
                   # language equality, classes ordered by least member
S.profile_rows()   # every (x, A(q,x) bits per state) row — a test/debug
                   # reading exercising the Phase 3 columns
```

**Calculus operators (C10)** — each names its paper anchor; built-in
assertions are compiled in, not switchable:

```python
S.member(u, v)     # §6.1 lasso membership, closure-free — asserts Phase 1
                   #   never runs on a membership query
~S,  S & T,  S | T,  S - T
                   # §6.2 same-table Boolean algebra: free (Acc-predicate
                   #   plumbing) when S, T share a table; otherwise an
                   #   implicit align (§6.3) is performed and priced —
                   #   one closure, visible in stats
sos_sdd.align(S, T)          # §6.3 explicit alignment — asserts Comp is
                             #   never applied on the aligned space
S.included(T), S.equiv(T), S.empty()   # §6.4
S.witness(T)       # §6.4/Prop 6.2 — least separating lasso (stem, loop),
                   #   the C7 forward-walk mechanism reused verbatim
S.root(iota), S.subst(sigma) # §6.5 rootings / inverse substitutions
S.reduce()         # quotient to canonical form — explicit, so E9's
                   #   deferred-reduce column is a driver choice:
                   #   operators do NOT auto-reduce ("pay canonicity
                   #   only when consumed")
```

## Failure taxonomy (findings vs bugs)

Findings are exceptions carrying their data — a driver catches and ledgers
them, per spec §3 ("a blown cap or budget is a finding, not an error"):

- `sos_sdd.DiagramBudget` — node budget blown; carries the phase and the
  layer profile accumulated so far (spec C3: never a silent abort).
- `sos_sdd.TimeBudget` — wall budget blown; same payload.

Bugs are a distinct type, never caught-and-ledgered:

- `sos_sdd.StopTheLine` — an internal invariant violated: squaring vs
  pairing disagreement (C4); a `Comp`-shaped application inside the Phase 5
  refinement (C6, the rotation lemma); `Comp` on an aligned space (§6.3);
  Phase 1 entered from a membership query (§6.1); an orbit walk in Phases
  3–4 (C5). By definition a defect — file it.

## Instrumentation stream (C1 — built first)

One JSON object per record, to the `stats` sink, flushed as produced (a
budget-killed run keeps its prefix):

```
{"ev":"config", ...resolved switches...}
{"ev":"op",     "phase":1, "op":"closure-step", "round":3,
 "nodes_final":57, "nodes_peak":210, "ms":4.2}
{"ev":"layer",  "k":3, "card":9, "nodes":57}
{"ev":"phase",  "phase":1, "rounds":7, "nodes_final":123,
 "nodes_peak":210, "ms":31.5}
{"ev":"verdict","status":"OK", "em1":16, "depth":6,
 "nodes_final":123, "nodes_peak":210, "ms":118.0}
```

`nodes_*` are live diagram nodes of the engine's working sets, sampled after
each operation (`peak` = max over samples inside the op — an honest lower
bound on the true peak, stated as such in the ledgers). Calculus moves emit
`op` records too, so E9's per-operation pricing is a reading of the same
stream.

## Backend decisions (recorded, per spec §1)

- **libDDD, used directly** — not as an ITS type: the ITS contract
  standardizes what a reachability checker consumes, while this engine's
  substance (crossing, residual gfp, refinement, quotient, extraction,
  calculus) lives outside it. The slot-space and relation construction is
  isolated in one module with an ITS-shaped seam, so wrapping later is a
  bounded refactor. Parts general enough may be pushed back to the library.
- **Pure multi-valued DDD now; hierarchy (SDD) is an extension**, targeted
  at factored product coordinates when the scaling families land.
- **Relations are homomorphism bricks, not 2k diagrams** (the ETF/`apply2k`
  route was considered and dropped — DDD-side `apply2k` is single-variable,
  and bricks get the library's canonization, caching and locality-driven
  saturation for free). Phase 1's letter step is per-slot total functions:
  `Hom_Basic` selectors/assignments summed over the **disjoint guard-cube
  classes of the digest** — the letter coupling never puts α variables in
  the diagram and never enumerates the alphabet; α-bits-as-variables is
  the recorded fallback if cube refinement ever explodes. Phase 2's
  `Comp` is the paper's `|Q|`-way case split rendered over **plain
  scalar variables** (`x_q`/`y_q` — the space is fixed-size, no array
  encoding) as guarded assignments: `assignExpr` / `predicate` of
  `its/gal/ExprHom.hpp` (the CAV 2012 symbolic expression evaluation),
  from **libITS' gal component**, which depends only on libITS root
  contracts + libDDD (parsers depend on it, never the reverse). That
  dependency joins at Phase 2; Phases 0–1 are pure libDDD.
- **Phases 3–4 rendering**: the digest's acceptance formula is grounded
  Python-side (`accept.py`) into per-slot accepting-mask tables that
  travel in the payload as numbers (like `PackInfo` — the core never
  parses formula text). A profile is one predicate application on π's
  pair space per global state (`S_q = predicate(A_q)(π)`: case-split
  slot read + mask membership — no orbit walk, no cycle detection);
  state agreement on all elements is O(1) canonical comparison of the
  columns, which seeds Phase 4's residual gfp — explicit Moore
  refinement over the global states (mixed-radix over the component
  blocks, guarded ≤ 32767 like the slot domains).
- **Variable order convention**: DDD variable 0 is adjacent to the
  terminal (slot `i` = variable `i`, higher variables on top) — the
  library convention, load-bearing for the expression homomorphisms and
  the SDD growth path. Pair spaces stack the written block (`y`) *above*
  the read block (`x`), so data-dependent reads resolve downward through
  the ExprHom query mechanism.
- **Guard**: DDD edge values are `val_t` (`short` in stock libDDD); the
  packed slot encoding caps at `|Q × 2^C| ≤ 32767`; the engine rejects a
  digest that exceeds it (reachable in flat coordinates on scaling
  families) instead of silently wrapping. Escape hatches, in order: a
  split encoding, or recompiling libDDD with a wider `val_t`.
- **Canonical keying**: normative constraints in
  `sosl/sosl/sos/io/sos_format.md` — AP order lexicographic by name,
  letter order = characteristic tuple over the APs with `0 < 1`
  (`!a < a`), shortlex keys, class ids in key order, linked pairs lex by
  `(s, e)`, `accept` **saturated**. The doc fixes constraints, not bytes:
  byte-level parity is against `sosl/sosl/sos/io/serialize.py`'s actual
  layout (the fixtures' `0 eps` / `N: row` shape). The least-letter
  choice in extraction walks is therefore lex on the α-bit vector in AP
  order — exactly the α-carrying diagram read top-down.

## Deviations from the experiments spec (recorded)

- Spec C8 says the generators "emit each in both slot coordinates"; here the
  `Product` carries *structure* and the coordinate choice is the engine's
  `coords` switch. Same measurements, one input object per family point, and
  E3's one-backend fairness clause holds by construction.
- No standalone CLI for now: the drivers are Python, the API is the tool. If
  profiling ever needs a pure-C++ entry point, a thin `main.cpp` replaying a
  digest dump can be added without touching this contract.
- The C4 squaring shortcut is **deferred**: `y ← y·y` rewrites every slot
  while reading the others, a genuinely simultaneous step — planned as a
  2k-variable relation encoding rather than `syncAssignExpr`. Until it
  lands only `square="off"` is implemented; `"check"`/`"on"` are refused
  loudly (never silently ignored), and Phase 2 runs the general pairing,
  which is the always-correct path.

## Build

C++17, pybind11 (system package), and the native deps installed from
source into the untracked local prefix `deps/` by:

```
./install_deps.sh   # libDDD + libITS from ~/git checkouts (see its header)
cmake -B build && cmake --build build
```

The extension lands inside the package directory, so `import sos_sdd`
works from the repo root without an install step. `LIBDDD_HOME`
overrides the deps/ prefix if ever needed.
