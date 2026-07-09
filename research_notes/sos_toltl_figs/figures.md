# The LTL Frontier from the Syntactic ω-Semigroup — Figures

Companion artifact for [`sos_toltl.md`](../sos_toltl.md), built to the spec in
[`sos_toltl_figures.md`](../sos_toltl_figures.md). Every number shown is
produced by the probe named in each figure's provenance footer; nothing is
transcribed by hand. See [`reproduction.md`](reproduction.md) to regenerate,
and [`notes.md`](notes.md) for what the specification asked for and what the
algebra actually turned out to support.

Inputs are language-canonical `.sos` invariants, bundled in
[`sources/`](sources/): `gf_aa.sos` (the six-class syntactic algebra of
`GF(aa)`, byte-identical from either presentation) and `fa.sos` (`F a`).

Drawing conventions, shared by FIG-1 and FIG-4:

| ink | meaning |
|---|---|
| solid blue arrow | a Cayley step under the letter `a` |
| dashed amber arrow | a Cayley step under `!a` |
| solid black arrow | a step both letters agree on (a frozen class's loop) |
| rounded grey box | one layer = one SCC of `Cay(L)` = one R-class |
| thick grey arrow | the R-order between layers |
| thin black stub | an entry class of its layer |
| double circle | a committed class (`T_c = Σ^ω`, the co-safety base case) |

---

## FIG-1 — the layered Cayley graph of `GF(aa)`

![layered Cayley graph of GF(aa)](img/fig1_cayley.png)

**The six classes of `S(GF(aa))₊¹`, their Cayley steps, and the four layers
the R-order stratifies them into.** The drawing is the paper's §5.2 diamond:
the transient root `{0}`; two mirrored moving layers `{1,3}` and `{2,4}`,
each 1-anchored — under `!a` layer `{1,3}` resets onto class `1`, under `a`
onto class `3`, and layer `{2,4}` is the mirror — and the absorbing frozen
layer `{5}` = "contains `aa`", where both letters are neutral and the walk
stops moving. The side tag of each box is the layer's read-off: which letter
kind (`reset` / `exit` / `neutral`) each letter has, the condition-(A) width,
and the condition-(B) width. Both moving layers are *all-rejecting as final
layers* — no linked pair off class `5` is accepting — so their `STAY∞`
branches are `⊥` and only their `LEAVE` chains survive; the language's whole
two-letter content is confined to the frozen layer, where (B) holds at width
`k′ = 2` and yields the brick `GF(a ∧ Xa)`. Anchoring is layer-local: the
letter `a` is globally ambiguous (it opens, closes, or extends an `aa`), but
within each layer one letter suffices, which is what makes width 1 enough.

<!-- from: python3 -m tests.sos2ltl.figs.fig1 sources/gf_aa.sos sources/fig1_cayley.tex -->

---

## FIG-2 — the label stack as a derivation

**Deferred, not built.** The panel must display the engine's own
`sojourn` / `step` / `leave` / `Final` bricks with simplification off, but
`aut2ltl.sos2ltl.engine.transcribe` returns only the root label — the
per-layer bricks are locals inside `_layer_flat`. Emitting them needs a
`_TRACE`-guarded dump in the engine, and the engine was under concurrent edit
(the `guards.py` / AP-formula refactor) while these figures were built.
Rationale and the proposed shape of the hook are in
[`notes.md`](notes.md#fig-2-deferred); the paper's §5.2 code block stands in
the meantime, and it is correct — the engine reproduces it.

---

## FIG-3 — the DG recursion: substitution tree vs memoized DAG

![DG recursion, tree vs DAG](img/fig3_dg.png)

**The same recursion, drawn twice.** Left, the induction unfolded as a
substituting recursion would build it: one node per *call site*, so the call
`DG(M′, T, ·)` that four different parents make is copied four times (see how
often `2`, `11` and `4` recur across the row). Right, the same recursion
memoized on the key `(frame, target)`: 19 distinct nodes, each built once,
with a *reference* — thin dotted arrow, annotated `n×` where one parent
references the same child `n` times — wherever the left panel copied. Shaded
nodes are base cases (every letter invisible); the recursion is acyclic
because the local-divisor induction strictly decreases.

For `GF(aa)`'s six-class algebra the recursion *tree* is a modest 49 nodes over
4 depths (`1, 10, 30, 8`) across 34 call sites, 26 of them distinct. The
violence is not in the recursion but in what each node's `tilde` substitution
does to the *formula*: the shared arena of 1 287 formula nodes has a flat
unfolding of **1 991 717** nodes. That is the size recurrence of §2.3 —
`f(M, Σ) ≈ f(M′, T) · maxₘ f(M, Σ∖{c})`, multiplicative because a block
formula is copied into every occurrence of every `T`-letter — and it is
confined entirely to the unfolding step. The number of distinct sub-calls is
governed by the algebra, not by the tree.

> **On the two size pairs.** `1 287 / 1 991 717` is the DG arena and its flat
> unfolding, in the induction's own hash-consed AST, before the formula is
> handed to Spot. Running the same synthesis through the portfolio
> (`survey --use sos2ltl_dg`) reports `dag = 258, tree = 315 412,
> sharing = 1 222.5×`: Spot's own hash-consing and its constructors' trivial
> normalizations shrink both numbers. The two pairs measure different objects;
> the figure quotes the first, which is what the paper's §2.3 commits to.

<!-- from: python3 -m tests.sos2ltl.figs.fig3 sources/gf_aa.sos sources/fig3_dg.tex -->

---

## FIG-4 — the `F a` micro-machine

![the F a micro-machine](img/fig4_fa.png)

**A pure peel: every layer a singleton, so condition (A) is vacuous.** Three
classes — `[ε]`, `[!a]` ("no `a` yet"), `[a]` ("an `a` has occurred",
two-sided absorbing) — in a chain with a skip. The accepting linked pairs are
`([a],[!a])` and `([a],[a])`: once class `[a]` is reached every loop accepts,
so `[a]` is **committed**, `T_{[a]} = Σ^ω`, and its label collapses to `⊤` —
the co-safety base case, drawn double-circled, surfacing per class rather than
by a global read-off. The middle layer `{[!a]}` is all-rejecting as a final
layer (`([!a],[!a]) ∉ P`), which kills its `STAY∞`; only its `leave` brick
survives, giving `Final([!a]) = !a U (a ∧ X ⊤)`. The root is a pure exit fan.
Reading the labels bottom-up reassembles `F a`.

<!-- from: python3 -m tests.sos2ltl.figs.fig4 sources/fa.sos sources/fig4_fa.tex -->
