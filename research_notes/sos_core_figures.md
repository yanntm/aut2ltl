# Figures for `sos_core.md` §3 — delivered

The four Cayley-graph figures (`[Figure F0]` … `[Figure F3]`, §3.1–§3.5) are
built and committed. **This file is no longer the specification.** The artifact
is, and it is self-describing:

> **[`sos_core_figs/`](sos_core_figs/)** — the figures, their inputs, the tool,
> and how to rebuild them.
>
> - [`figures.md`](sos_core_figs/figures.md) — the four figures, what each shows,
>   and what the ink means.
> - [`reproduction.md`](sos_core_figs/reproduction.md) — **the authority**:
>   prerequisites, the inputs with their provenance, every command, and the
>   machine-vs-hand split.

| fig | language | input | file |
|---|---|---|---|
| F0 | `a*·b^ω` (= `a U G!a`) | `astar_bomega.sos` | `img/core_F0_astar_bomega.png` |
| F1 | `GF(aa)` | `gf_aa.sos` | `img/core_F1_gf_aa.png` |
| F2 | `Even` | `even.sos` | `img/core_F2_even.png` |
| F3 | `EvenBlocks` | `evenblocks.sos` | `img/core_F3_evenblocks.png` |

Displayed in `{a, b}` with `b := !a`. Each figure draws the algebra `𝒜` and
carries `P` as a caption beneath it — the object is `⟨𝒜, P⟩`, and only `𝒜` has a
shape.

## What the figures say

Recomputed from the `.sos` on every build, and agreeing with §3 throughout:

| fig | classes | idempotents | monochrome cycles | zero |
|---|---|---|---|---|
| F0 | 5 | `a, b, b·a` (`[a·b]² = [b·a]`) | none | `b·a` |
| F1 | 6 | `b, a·b, b·a, a·a` | none — its cycles are **mixed-letter** | `a·a` |
| F2 | 5 | `b, a·b, a·a` | `{[a],[a·a]}` under `a` — the `Z₂` | — |
| F3 | 8 | `b, a·a, a·b·a, b·a·b` | `{[a],[a·a]}`, `{[b],[b·a]}`, `{[a·b],[a·b·a]}` under `a` | `b·a·b` |

## Findings

1. **`import_ltl` is not the entry point** for building F0 — it returns a Spot
   `twa_graph`. The `Invariant` comes from `sosl.sos.build.reference_of_ltl`.
2. **Machine keys are not display keys.** The machine letter order is `!a < a`
   (absent before present), so a `.sos`'s keys are shortlex-least under `b < a`.
   The figures recompute keys by BFS in *display* order. On these four the words
   coincide and only the node ordering changes — but on a larger alphabet they
   will not.
3. **`P` does not fit in the drawing, and the Büchi convention is a trap.**
   Acceptance here is a *relation* on classes, not a predicate, so no node mark
   (double circle, colour, bold) can carry it. Worse: on all four figures `P`
   happens to factor as `stems × loops ∩ linked`, so a two-mark node scheme would
   be *accidentally* right on every figure we print while teaching a rule that is
   not a theorem. `P` is typeset, not drawn.

Monochrome cycles are computed and asserted on every build but are **not inked**:
a monochrome cycle is a property *of* the drawn arrows, not an arrow of another
kind. Likewise the letter is written on each arrow rather than coded in a dash.
