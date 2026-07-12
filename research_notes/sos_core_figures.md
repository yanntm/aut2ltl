# Task — `sos2cayley`: Cayley-graph figures for the sos_core paper

*For an engineering session. Build a generic `.sos → Cayley graph` renderer and
deliver four figures for [`sos_core.md`](sos_core.md) §3, whose ASCII placeholders
are marked `[Figure F0]` … `[Figure F3]`. You do **not** touch the paper prose —
the placeholders are swapped by a later theory session.*

Prerequisites: `dot` (GraphViz) and `rsvg-convert` on `PATH` — the same toolchain
as [`sos_figs/reproduction.md`](sos_figs/reproduction.md).

## Deliverable

1. **The tool** — `sosl/tests/sos/sos2cayley.py`: a CLI taking exactly ONE `.sos`
   file per invocation, emitting a GraphViz `.dot` and rendering it. Self-bound
   ≤ 15 s per run. Typed signatures on every function (params + return).
2. **Four figures** under `research_notes/sos_figs/img/`, basenames
   `core_F0_astar_bomega`, `core_F1_gf_aa`, `core_F2_even`,
   `core_F3_evenblocks`, each committed as `.dot` + `.png`
   (`dot -Tsvg | rsvg-convert`, like the existing images there).
3. **Inputs bundled**: copy the four input `.sos` into
   `research_notes/sos_figs/sources/` (existing self-containment convention).
4. **A `## Delivery` section appended to THIS file**: commands run, validation
   outcome per figure, findings if any. Commit tool + fixtures + outputs.

## Inputs

Load `.sos` with `sosl.sos.io.load_invariant` — never hand-parse.

| fig | language | input `.sos` |
|---|---|---|
| F0 | `a*·b^ω` (warm-up) | build it — see below |
| F1 | `GF(aa)` = `G F (a & X a)` | `samples/fixtures/hoa/sos/gf_aa.sos` |
| F2 | `Even` | `samples/fixtures/hoa/sos/even.sos` |
| F3 | `EvenBlocks` | `samples/fixtures/hoa/sos/evenblocks.sos` |

**F0 build (once).** The object of `a*·b^ω` with `b := !a` is the object of the
LTL formula `a U G!a`. Build it via `sosl.sos.build.import_ltl` (check its pydoc
for the exact signature), save with `sosl.sos.io.dump_invariant` to
`samples/fixtures/hoa/sos/astar_bomega.sos`, and commit that fixture. If
`import_ltl` is not the right entry point, stop and report — do not hand-write
the file.

**Letters.** The machine alphabet is `{a, !a}`; the paper displays `!a` as `b`.
The tool takes `--rename 'a=a,!a=b'` and everything rendered or checked below is
in DISPLAY letters. If a loaded object's alphabet is not exactly `{a, !a}`, that
is a finding — report it, don't guess.

## Rendering rules (exact)

Output must be deterministic: nodes sorted by shortlex display key, edges by
(source key, letter index). Rerunning must reproduce the `.dot` byte-for-byte.

1. **Keys recomputed, not trusted.** BFS from the identity class, trying letters
   in `--rename` order (`a` before `b`); `key(c)` = the shortlex-least word
   reaching `c`. Node label = the key with letters joined by `·`; the identity
   is labeled `ε`.
2. **Nodes**: `shape=ellipse`. Identity: `style=dashed, color=gray40,
   fontcolor=gray40`. Idempotent classes (`c·c = c`, computed from the product;
   identity excluded): `penwidth=2.4`. All other nodes `penwidth=1`.
3. **Edges** — one per (class `s`, letter `x`), target `s·λ(x)`:
   - letter 1 (`a`): `style=solid`; letter 2 (`b`): `style=dashed`. No edge
     labels and no in-image legend (the paper caption carries the legend).
   - **key-tree edges** (for each non-identity class whose key is `w·x`: the
     edge from the class of `w` on letter `x`): `penwidth=1.8`; every other
     edge `penwidth=0.9`.
   - **monochrome-cycle edges**: for each letter `x`, find the cycles of length
     ≥ 2 in the functional graph `s ↦ s·λ(x)`; those edges additionally get
     `color="black:invis:black"` (double-stroke). Self-loops are length-1
     cycles: never doubled.
4. **Layout**: `dot`, default `rankdir=LR`, one `{rank=same; …}` group per key
   length (BFS layer). A `--rankdir` flag may override per figure if it reads
   better (say so in Delivery).
5. **`P` is not drawn.** The image shows the algebra `𝒜` alone. Print to
   stdout: `P = { ([s],[e]), … }` in display keys, sorted shortlex by stem then
   loop. The paper typesets that line beneath the figure — the `⟨𝒜, P⟩` split
   is a design point: the drawing is `𝒜`, the line is `P`.
6. **Provenance**: first line of each `.dot` is a comment
   `// sos2cayley <input> --rename a=a,!a=b`.

## Built-in checks (assert on every run)

- The identity node has **in-degree 0** — freshness: no edge may enter `[ε]`.
  Hard assert on every input.
- With `--expect <json>`: compare, **as sets**, the keys, the idempotents, the
  per-letter monochrome cycles, and the `P` pairs against the file. Ship the
  four expect files next to the tool and run each figure with its expect.

## Expected content (display letters)

A mismatch here is a FINDING to report back to theory — never something to
paper over or to "fix" by editing the expectation.

### F0 — `a*·b^ω` (5 classes)

```
 ·a :  ε↦a    a↦a     b↦b·a   a·b↦b·a   b·a↦b·a
 ·b :  ε↦b    a↦a·b   b↦b     a·b↦a·b   b·a↦b·a
```

keys `{ε, a, b, a·b, b·a}`; idempotents `{a, b, b·a}` (`[a·b]² = [b·a]`);
monochrome cycles: none; zero `b·a`;
`P = { ([b],[b]), ([a·b],[b]) }`.

### F1 — `GF(aa)` (6 classes)

```
 ·a :  ε↦a    a↦a·a   b↦b·a   a·b↦a     b·a↦a·a   a·a↦a·a
 ·b :  ε↦b    a↦a·b   b↦b     a·b↦a·b   b·a↦b     a·a↦a·a
```

keys `{ε, a, b, a·b, b·a, a·a}`; idempotents `{b, a·b, b·a, a·a}`;
monochrome cycles: none (the graph has mixed-letter cycles `[a]⇄[a·b]`,
`[b]⇄[b·a]` — those are NOT doubled); zero `a·a`;
`P = { ([a·a],[a·a]) }`.

### F2 — `Even` (5 classes)

```
 ·a :  ε↦a    a↦a·a   b↦b     a·b↦a·b   a·a↦a
 ·b :  ε↦b    a↦a·b   b↦b     a·b↦a·b   a·a↦b
```

keys `{ε, a, b, a·b, a·a}`; idempotents `{b, a·b, a·a}`;
monochrome cycles: `{[a], [a·a]}` under `a` (the `Z₂`); no zero;
`P = { ([b],[b]), ([b],[a·a]), ([b],[a·b]) }` (as a set — the paper lists them
in another order).

### F3 — `EvenBlocks` (8 classes)

```
 ·a :  ε↦a        a↦a·a     b↦b·a         a·b↦a·b·a
       b·a↦b      a·a↦a     a·b·a↦a·b     b·a·b↦b·a·b
 ·b :  ε↦b        a↦a·b     b↦b           a·b↦a·b
       b·a↦b·a·b  a·a↦b     a·b·a↦b·a·b   b·a·b↦b·a·b
```

keys `{ε, a, b, a·b, b·a, a·a, a·b·a, b·a·b}`;
idempotents `{b, a·a, a·b·a, b·a·b}` (note `[a·b]² = [b·a·b]` — not idempotent);
monochrome cycles under `a`: `{[a],[a·a]}`, `{[b],[b·a]}`, `{[a·b],[a·b·a]}`;
zero `b·a·b`;
`P = { ([b],[b]), ([a·b],[b]), ([b·a·b],[b]), ([b·a],[a·b·a]),
([b·a·b],[a·b·a]), ([a·b·a],[a·b·a]) }`.

## Layout intent

Match the spirit of the ASCII placeholders in `sos_core.md` §3.1–§3.5: root at
the left/top, the zero far right/bottom, swap-pairs adjacent. GraphViz need not
reproduce them literally.

## Rules

- Single-input invocations, ≤ 15 s each; long output to `tests/**/logs/`.
- Report findings; never adjust an expectation to make a check pass.
- Discipline per `CLAUDE.md`: commit per increment with `git commit -F -`;
  `git add` close to the commit.
