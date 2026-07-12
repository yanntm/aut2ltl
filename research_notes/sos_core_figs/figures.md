# The Syntactic ω-Semigroup — Core Figures

Companion artifact for [`sos_core.md`](../sos_core.md) §3, replacing the ASCII
placeholders `[Figure F0]` … `[Figure F3]`. Inputs bundled in
[`sources/`](sources/); see [`reproduction.md`](reproduction.md) to rebuild, and
for what the machine derives versus what the hand only moves.

## What is drawn

The object of a language is `⟨𝒜, P⟩`. Only `𝒜` has a shape, so the **drawing is
the algebra** — the classes and the right action of the letters — and the
**accepting pairs `P` are the caption**. An accepting pair is a pair of classes,
not a transition; drawing it as an arrow would be a lie about its type, and no
node mark can carry it either (acceptance is a *relation*, not a predicate — the
Büchi double circle has no analogue here).

A node is a class, named by its **key**: the shortlex-least word reaching it. So
a key can be read off the picture as a path from the root.

| ink | meaning |
|---|---|
| rounded box | a class |
| incoming stub from nowhere | the root `[ε]`, marked like an initial state. It is the *adjoined* identity — the class of no word — hence a **source**, and that stub stays the only arrow entering it (freshness, asserted on every build) |
| arrow, labeled `a` / `b` | one letter step `s → s·λ(x)`. **The label is the only letter coding** — no dashes, no colours |
| arrow labeled `a,b` | both letters agree on this target; one arrow, not two |
| thicker arrow | a **key-tree** edge: the last letter of its target's key. These `n−1` arrows span the graph from the root, and are what makes a key readable as a path |

Out-degree is `|Σ| = 2` at every node, always: the picture is a deterministic
transition system on classes.

**What is deliberately *not* inked.** Derived facts get no ink of their own —
they are *properties of* what is drawn, not extra things to draw. Two of them
matter to the prose, and both are computed and asserted on every build:

- **idempotency** (`[c]·[c] = [c]`) — a property of the product, not a kind of
  class;
- **monochrome cycles** (a cycle of one letter's map `s ↦ s·λ(x)`) — a property
  of the drawn arrows, not an arrow of another kind.

Read them off the build (`python3 -m sosl.sos.viz …`), not off the picture.

## F0 — `a*·b^ω`, the warm-up

![F0](img/core_F0_astar_bomega.png)

From [`sources/astar_bomega.sos`](sources/astar_bomega.sos), the object of
`a U G!a`. Five classes. `[b·a]` is the **zero** — every letter loops back to it:
once a `b` is followed by an `a`, no future repairs the word. The idempotents are
`{[a], [b], [b·a]}`; `[a·b]` is *not* one, since `[a·b]² = [b·a]`, and that is the
first thing this figure is for. No monochrome cycle.

## F1 — `GF(aa)` = `G F (a & X a)`

![F1](img/core_F1_gf_aa.png)

From [`sources/gf_aa.sos`](sources/gf_aa.sos). Six classes; `[a·a]` is the zero
and the only accepting loop. Two waiting rooms — `[a] ⇄ [a·b]` and `[b] ⇄ [b·a]`
— each escaping on `a` toward the zero. Both cycles **mix letters** (one leg on
`a`, one on `b`), so neither is a monochrome cycle: a cycle *in the drawing* is
not the same thing as a cycle *under one letter*, and this is the figure that
keeps that distinction honest.

## F2 — `Even`

![F2](img/core_F2_even.png)

From [`sources/even.sos`](sources/even.sos). Five classes, placed so the pair
`[a] ⇄ [a·a]` under the letter `a` is the square's **diagonal**: this is the
**`Z₂`**, a parity counter, a non-trivial group living inside the algebra — and
exactly what an aperiodic (LTL-definable) language cannot contain.

## F3 — `EvenBlocks`

![F3](img/core_F3_evenblocks.png)

From [`sources/evenblocks.sos`](sources/evenblocks.sos). Eight classes, and the
same parity group three times over — `[a] ⇄ [a·a]`, `[b] ⇄ [b·a]`,
`[a·b] ⇄ [a·b·a]` — one per phase of the language. `[b·a·b]` is the zero, and
unlike F0's it is no death sentence: two of the six accepting pairs sit at it.
Again `[a·b]` is not idempotent (`[a·b]² = [b·a·b]`), while `[a·b·a]` is.
