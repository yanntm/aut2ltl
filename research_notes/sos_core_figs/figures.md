# The Syntactic ω-Semigroup — Core Figures

Companion artifact for [`sos_core.md`](../sos_core.md) §3, whose ASCII
placeholders `[Figure F0]` … `[Figure F3]` these four replace. Built to the task
in [`sos_core_figures.md`](../sos_core_figures.md).

Every figure is drawn from a language-canonical `.sos` invariant by one tool,
`sos2cayley` (over the engine service `sosl.sos.viz`); nothing in a picture is
transcribed by hand. The inputs are bundled in [`sources/`](sources/), so the
artifact is self-contained. See [`reproduction.md`](reproduction.md) to rebuild.

## What is drawn

The object of a language is `⟨𝒜, P⟩`. Only `𝒜` has a shape, so the **drawing is
the algebra** — the congruence classes and the right action of the letters — and
the **accepting pairs `P` are typeset as the caption**, never drawn as arrows: an
accepting pair is a pair of classes, not a transition.

A node is a class, named by its **key**: the shortlex-least word reaching it, so
the key of a node can be read off the picture as the path from the root.

| ink | meaning |
|---|---|
| dashed grey ellipse | the root `[ε]` — the *adjoined* identity, the class of no word, hence a **source**: no edge enters it |
| thin ellipse | an ordinary class |
| **thick** ellipse | an **idempotent** class, `[c]·[c] = [c]` — the classes that can be the loop of a linked pair |
| solid arrow | a step on the letter `a` |
| dashed arrow | a step on the letter `b` (`b := !a`) |
| thicker arrow | a **key-tree** edge: the edge that first reaches its target in the BFS, i.e. the last letter of the target's key. These `n-1` edges span the graph from the root |
| **doubled** arrow | an edge on a **monochrome cycle** of length ≥ 2: a cycle of the single-letter map `s ↦ s·λ(x)`. A self-loop is a cycle of length 1 and is *never* doubled — what the doubling marks is a class genuinely *rotating* under one letter, i.e. a non-trivial group inside the algebra |

Out-degree is `|Σ| = 2` at every node, always: the picture is a deterministic
transition system on classes.

## F0 — `a*·b^ω`, the warm-up

![F0](img/core_F0_astar_bomega.png)

Source: [`sources/astar_bomega.sos`](sources/astar_bomega.sos) — the object of
`a U G!a`. Five classes. `[b·a]` is the **zero** (every letter loops back to it):
once a `b` has been followed by an `a`, no future can repair the word. The three
thick nodes `{[a], [b], [b·a]}` are the idempotents; `[a·b]` is *not* one —
`[a·b]² = [b·a]` — which is the first thing this figure is for. No monochrome
cycle: nothing is doubled.

`P = { ([b],[b]), ([a·b],[b]) }` — accept iff the word ends up looping in `[b]`,
reached either from `[b]` itself or from a stem in `[a·b]`.

## F1 — `GF(aa)` = `G F (a & X a)`

![F1](img/core_F1_gf_aa.png)

Source: [`sources/gf_aa.sos`](sources/gf_aa.sos). Six classes; `[a·a]` is the
zero and the only accepting loop. The two visible 2-cycles, `[a] ⇄ [a·b]` and
`[b] ⇄ [b·a]`, are **mixed-letter** — one leg on `a`, one on `b` — so they are
*not* monochrome and are correctly left undoubled. This is the figure that makes
the monochrome criterion honest: a cycle in the drawing is not the same thing as
a cycle under one letter.

`P = { ([a·a],[a·a]) }`.

## F2 — `Even`

![F2](img/core_F2_even.png)

Source: [`sources/even.sos`](sources/even.sos). Five classes. The doubled pair
`[a] ⇄ [a·a]` under the letter `a` is the **`Z₂`**: the parity counter, a
non-trivial group living inside the algebra, and the whole point of the example.
It is exactly what the monochrome-cycle criterion is meant to expose, and exactly
what an aperiodic (LTL-definable) language cannot contain.

`P = { ([b],[b]), ([b],[a·a]), ([b],[a·b]) }`.

## F3 — `EvenBlocks`

![F3](img/core_F3_evenblocks.png)

Source: [`sources/evenblocks.sos`](sources/evenblocks.sos). Eight classes, the
largest of the four, and three monochrome `a`-cycles at once — `[a] ⇄ [a·a]`,
`[b] ⇄ [b·a]`, `[a·b] ⇄ [a·b·a]` — each a copy of the same parity group acting on
a different residual. `[b·a·b]` is the zero. Note again that `[a·b]` is not
idempotent (`[a·b]² = [b·a·b]`), while `[a·b·a]` is.

`P = { ([b],[b]), ([a·b],[b]), ([b·a·b],[b]), ([b·a],[a·b·a]), ([b·a·b],[a·b·a]), ([a·b·a],[a·b·a]) }`.

## Status

The four `.tex` in `sources/` are byte-identical to their `_gen.tex` — nothing has
been hand-tuned yet; they are pending review. The `dot` layout is loose (F0 and
F2 in particular are stretched vertically). Tuning means editing coordinates in
the hand-owned `.tex`; see [`reproduction.md`](reproduction.md) §3.
