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
S.congruence_count()    # |EM¹/~| — the syntactic class count (Phase 5)
S.congruence_classes()  # every ~-class as explicit element tuples — a
                   # test/debug reading; Phase 6 consumes the blocks
                   # symbolically
S.n_classes()      # invariant classes incl. the fresh [eps] (Phase 6)
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
- **Phase 5 rendering**: the congruence is symbolic partition refinement
  on the pair space with the y-block erased to zero (a `setVarConst`
  sweep), so the Phase 3 columns project onto the closure's space; the
  seed splits by the erased profile columns (~ω) and by residual-class
  slot selections (~lin), and the gfp splits by letter-class *preimages*
  (the closure's per-class reverse homs). Everything in that path is
  slot-local `Hom_Basic` — `congruence.hh` never includes the ExprHom
  machinery, which is the rotation-lemma code invariant (no `Comp`
  inside the fixpoint).
- **Phase 6 rendering** (`quotient.py`, the `quotient="explicit"` route —
  the recorded small-side fallback; `"symbolic"` is refused): word
  classes are the ~-classes of non-empty-word images with `[eps]`
  adjoined fresh (the reference's normative identity convention —
  `sosl.sos.core.quotient`: a quotient over elements alone would merge
  `!a` into `[eps]` for GF a and break byte parity); mult folds packed
  representative values (never `Comp`); ids/keys by shortlex BFS over
  the small quotient algebra itself (mirroring
  `sosl.sos.core.canonical.shortlex_bfs`); verdicts off the Phase 3
  profile rows at the initial state. `to_sos()` emits the core sections
  only (the optional residuals trailer does not participate in language
  identity). Recorded limits: single `Automaton` digests with sorted
  APs (products refused); languages whose reference import drops unused
  APs (Spot postprocess, e.g. the empty language) sit outside the
  same-AP byte-parity instance set.
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
## The squaring shortcut (C4) — recorded design (implemented,
`src/squaring.hh`)

`y ← y·y` rewrites every slot while reading the others, a genuinely
simultaneous step; `syncAssignExpr` is ruled out. The recorded rendering
is a **2k-variable relation encoding**: materialize the squaring map as
an interleaved relation diagram once, then iterate it with a relational
product — simultaneity becomes vacuous because the relation's input and
output live on distinct variables.

- **The relation space.** A dedicated 2n-variable space holding only the
  relation: slot `q` becomes the adjacent pair `r_q = var 2q+1` (pre,
  read-only) above `w_q = var 2q` (post, write-only). Variable 0 stays
  adjacent to the terminal; the numbering is collision-free, so a
  `GalOrder` over it is well-defined. Pre-above-post is chosen so the
  product matches before it emits. (The transparent `DoubleVars`
  doubling of `libITS bin/ToTransRel.cpp` — colliding numbers, homs
  hitting the curried first occurrence — was considered and rejected
  *for this step*: it is correct for GAL's sequential read-after-write
  semantics, but `Comp`'s cross-slot reads need the OLD values, and the
  colliding numbers make the frozen copies unaddressable by any
  `GalOrder`.)
- **The dupe gadget.** A ten-line renumbering variant of `DoubleVars`:
  `phi(q, v) = GDDD(2q+1, v) ^ GDDD(2q, v) ^ GHom(this)`, taking EM¹ to
  the diagonal `D = {(z ⧉ z)}` on the relation space.
- **The step.** The paper's case split verbatim on the interleaved
  order: `H_q = Σ_p [w_q := r_{base_q+p} | (r_q & mask_q)] ∘
  [r_q >> C_q == p]`. Every guard and rhs mentions only r-variables,
  every write targets a w-variable — written set ∩ read set = ∅, so the
  composition `∘_q H_q` equals the simultaneous `Comp` **by
  construction** (order-independence is syntactic, not a semantic
  argument). Cross-slot reads sit either side of the written variable;
  `assignExpr` handles rhs support above and below the lhs (author's
  confirmation). `R = (∘_q H_q)(D) = {(z ⧉ z·z)}` is built **once** —
  every power `x^{2^j}` stays in EM¹ — at the cost of about one pairing
  round.
- **The product.** `applyRel(R)`: a GHom carrying the R sub-diagram (the
  `Apply2k` pattern, cached by hash on the carried DDD), applied to the
  pair set on the *crossing's* block-stacked space. It travels **two
  R-levels per set variable** while descending the z-block: match the
  set value against R's pre arcs (no match ⇒ null), emit each post
  value as `GDDD(var, w′) ^ applyRel(grandson)`, summed; the factory
  maps `GDDD::one ↦ GHom::id`, so R exhausts exactly where the x-block
  begins and the x-block passes through untouched. Matching is by
  depth — R's own variable numbers are irrelevant to the product — and
  the set never leaves the crossing pair space.
- **The loop.** `P_0 = diag`, `P_{j+1} = applyRel(R)(P_j)`. R is total
  and functional on EM¹, so `|P_j| = |EM¹|` every round (asserted; a
  violation is StopTheLine, a defect). P holds one pair per x, so the
  O(1) set fixpoint `P_{j+1} == P_j` is equivalent to pointwise
  `z = z·z`, i.e. every z idempotent — the fixpoint IS the idempotence
  test, and the result is `{(x, x^π)}` by the unique-idempotent
  argument. Cap: `⌈log₂|EM¹|⌉ + 1` rounds — an orbit of index `i`,
  period `d` has `x^{2^j}` stable iff `2^j ≥ i` and `d | 2^j`, both
  settled by the cap if ever, so squaring converges **iff every orbit
  period is a power of two** (the "detects powers of two, not
  aperiodicity" note, now the loop's termination theorem).
- **Modes.** `"check"`: pairing and squaring both run; convergence ⇒
  one O(1) comparison against the pairing's π, disagreement raises
  StopTheLine; divergence is a recorded finding (expected on
  non-power-of-two periods; mod3 is the canonical case) with the
  pairing's π standing. `"on"`: squaring only (the `O(log ℓ)` payoff);
  divergence raises StopTheLine ("shortcut trusted but did not
  converge") so a sweep can never mislabel a periodic instance.
  `"off"`: pairing only.
- **Placement and gate.** `src/squaring.hh` (dupe, interleaved order,
  step, R, product, loop); `Crossing` stays frozen, `SoSCore`
  orchestrates the check-mode comparison. Gate cases: the triptych
  under `"check"` (converges, agrees with the `"off"` build), mod3
  (must diverge under `"check"`, must StopTheLine under `"on"`), a
  period-2 counter (converges despite periodicity), `EvenBlocks^{⊗2}`
  factored (`block_base` offsets in the interleaved space). Ground
  truth: the pairing π, itself F8-validated against explicit power
  orbits, plus every R row checked against the explicit packed
  composition (`square_rel_pairs`, a test/debug reading). Gate:
  `tests/sos_sdd/squaring_test.py`.

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
