# Task — `sos2cayley`: Cayley-graph figures for the sos_core paper

*Engineering task, now at **v2**. v1 is delivered in
`research_notes/sos_core_figs/` (tool, `img/`, `sources/` with `_gen`/tweaked
pairs, `figures.md`, `reproduction.md`, Makefile) — keep that structure and
regenerate in place. This revision changes the rendering only; inputs and
expected content are unchanged. You do not touch the paper prose.*

## v2 — what changes from v1

1. **Label every edge with its letter.** The figures must read without a
   legend: a small `a` or `b` on each edge, like the ASCII placeholders in the
   paper. Keeping solid-vs-dashed per letter as redundant coding is fine, but
   the label is what the reader uses. Self-loops too — one loop labeled `a,b`
   where both letters fix the node beats two stacked unlabeled loops.
2. **The ASCII placeholders in `sos_core.md` §3 are the approved figures —
   reproduce them.** Same relative node placement: root at left/top and visibly
   a source, swap pairs adjacent with their doubled `a`-edges between them,
   the zero at the far right/bottom. Same edges, routed similarly. The TikZ
   version is the approved ASCII drawn well, not a fresh layout; automatic
   layout is at most a starting point, and per-figure hand-set coordinates that
   match the ASCII are expected.
3. **Forget v1's mechanical constraints.** No byte-stable output requirement,
   no expect-file asserts, no prescribed pen widths. What matters is: the
   `.tex` stays pleasant to hand-edit (styles gathered in one `\tikzset`, named
   nodes, explicit coordinates, one `\draw` per edge), it compiles standalone,
   and the drawn content matches the tables below. Check that however is
   convenient; if something doesn't match, report it rather than absorbing it.

## Visual encoding (as in v1)

- Nodes labeled by their shortlex keys, letters joined by `·`; identity `ε`.
- Root: dashed border, grayed — and it should visibly have no incoming edge
  (freshness; if a render shows one, something is wrong upstream — report it).
- Idempotent classes (`c·c = c`, identity excluded): thick border.
- Monochrome cycles (length ≥ 2 under a single letter): doubled stroke. Mixed
  cycles and self-loops are never doubled.
- The `P` line is typeset beneath the drawing, for **all four figures** — the
  pairs are part of the object `⟨𝒜, P⟩`; a figure without them shows half the
  object.

## Inputs (as in v1 — all four `.sos` now exist)

Load with `sosl.sos.io.load_invariant`; display rename `!a → b`; everything
below is in display letters.

| fig | language | input `.sos` |
|---|---|---|
| F0 | `a*·b^ω` (warm-up) | `samples/fixtures/hoa/sos/astar_bomega.sos` |
| F1 | `GF(aa)` = `G F (a & X a)` | `samples/fixtures/hoa/sos/gf_aa.sos` |
| F2 | `Even` | `samples/fixtures/hoa/sos/even.sos` |
| F3 | `EvenBlocks` | `samples/fixtures/hoa/sos/evenblocks.sos` |

## Expected content (display letters)

A mismatch here is a finding to report back to theory, not something to paper
over.

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
monochrome cycles: none (the mixed-letter cycles `[a]⇄[a·b]`, `[b]⇄[b·a]` are
NOT doubled); zero `a·a`;
`P = { ([a·a],[a·a]) }`.

### F2 — `Even` (5 classes)

```
 ·a :  ε↦a    a↦a·a   b↦b     a·b↦a·b   a·a↦a
 ·b :  ε↦b    a↦a·b   b↦b     a·b↦a·b   a·a↦b
```

keys `{ε, a, b, a·b, a·a}`; idempotents `{b, a·b, a·a}`;
monochrome cycles: `{[a], [a·a]}` under `a` (the `Z₂`); no zero;
`P = { ([b],[b]), ([b],[a·b]), ([b],[a·a]) }`.

### F3 — `EvenBlocks` (8 classes)

```
 ·a :  ε↦a        a↦a·a     b↦b·a         a·b↦a·b·a
       b·a↦b      a·a↦a     a·b·a↦a·b     b·a·b↦b·a·b
 ·b :  ε↦b        a↦a·b     b↦b           a·b↦a·b
       b·a↦b·a·b  a·a↦b     a·b·a↦b·a·b   b·a·b↦b·a·b
```

keys `{ε, a, b, a·b, b·a, a·a, a·b·a, b·a·b}`;
idempotents `{b, a·a, a·b·a, b·a·b}` (`[a·b]² = [b·a·b]` — not idempotent);
monochrome cycles under `a`: `{[a],[a·a]}`, `{[b],[b·a]}`, `{[a·b],[a·b·a]}`;
zero `b·a·b`;
`P = { ([b],[b]), ([a·b],[b]), ([b·a·b],[b]), ([b·a],[a·b·a]),
([b·a·b],[a·b·a]), ([a·b·a],[a·b·a]) }`.

## Delivery

Regenerate the `_gen.tex` files and refresh the tweaked copies + `img/` (no
hand-tweaks exist yet — the tweaked files are still plain copies, pending
theory review). Note the v2 outcome per figure in `sos_core_figs/figures.md`,
findings included. Usual discipline per `CLAUDE.md`.
