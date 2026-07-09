# The LTL Frontier from the Syntactic ω-Semigroup — Figures

Companion artifact for [`sos_toltl.md`](../sos_toltl.md), built to the spec in
[`sos_toltl_figures.md`](../sos_toltl_figures.md). Every number shown is
produced by the probe named in each figure's provenance footer; nothing is
transcribed by hand. See [`reproduction.md`](reproduction.md) to regenerate,
and [`notes.md`](notes.md) for the measured facts and drawing decisions the
figures rest on.

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

## FIG-1 — the layered Cayley graph of `GF(aa)` (paper Figure 3)

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

![the label stack of GF(aa), as a derivation](img/fig2_stack.png)

**The label of `GF(aa)`, assembled child-first.** One block per layer, in the
order the R-order descent builds them: the frozen `{5}` first, then the two
moving layers, then the transient root. Left, the descent — a miniature of
FIG-1 with the layer being labelled lit and the layers already labelled
shaded. Right, the bricks that layer contributes, each tagged with the rule
that produced it; a brick that repeats a formula already introduced prints
that formula's *name*, so the panel is the label DAG rather than its
unfolding — `leave(3)` names `Final(5)`, `Final(3)` names `leave(3)` twice.
The formulas are the engine's own, dumped by `SOS2LTL_TRACE` with
simplification off; they are the paper's §5.2 stack, character for character,
with the ⊤/⊥ collapses the engine's constructors apply (`sojourn(1) = !a W a`
prints as `⊤`).

Read the degeneracies: both moving layers are all-rejecting as final layers,
so their `STAY∞` is `⊥` and `Final = LEAVE`; the root cannot sojourn at all,
so its label is its exit fan — `Final(0) = leave(0)` is the derivation saying
the root contributes only a fan. The mirror symmetry is literal: `Final(4)`
and `Final(1)` are the same formula, as are `Final(3)` and `Final(2)`.

Two rows are absent by design. `STAY∞` and `LEAVE` are the two disjuncts of
`Final`, and the only fact they carry that `Final` hides is whether the
confinement branch survived — which is each block's side note. And the panel
is drawn with the engine's *plain* rendering (`Rendering(residual=False)`):
under the default rendering exit children are keyed by residual, and since
`GF(aa)` is prefix-independent (one residual) the root's whole fan collapses
to `X Final(5)` — correct, cheaper, and it would leave the last step of the
derivation with nothing to show. The collapse is FIG-3's and §6's subject,
not this one's.

<!-- from: python3 -m tests.sos2ltl.figs.fig2 sources/gf_aa.sos sources/fig2_stack.tex -->

---

## FIG-3 — the DG formula: substitution tree vs memoized DAG (paper Figure 1)

![DG formula, tree vs DAG](img/fig3_dg.png)

**The same formula, drawn twice.** Both panels draw the DG induction's
*formula*, as operators over slots: a node says what it is (`⋁`, `⋀`, `φ U ψ`,
`X φ`, an atom verbatim), never an id. Right, the hash-consed arena: a subterm
used twice is one box with two in-arcs — the first arc builds it, every later
one is a *reference* (thin dotted). Left, the same slice as a substituting
recursion writes it: one copy per occurrence. In this slice alone, 22 copies
against 10 boxes.

The cut. `GF(aa)`'s arena is 1 287 nodes and its top is wide, not deep — a
seven-way `⋁` of `⋀`s of nine to nineteen conjuncts, 94 arcs onto 36 distinct
children — so the figure draws a *pattern* and states every elision in place.
`⋀`/`⋁` are associative-commutative: their arcs carry no slot label and the
node carries an arity badge (`⋀ ·12`) instead; only `X`/`U`/`XU` arcs name
their slots. The root's three cheapest disjuncts are drawn (`⋯ 4 more`); under
each, an arc goes to every child two drawn disjuncts share, plus one unshared
representative, and the rest are that node's `+k private` line. Each handle
`ψᵢ` carries its in-degree over *all seven* disjuncts (`ψ₁ ×7`: every disjunct
references it), its own head, and its `arena / flat` sizes — so the sharing the
cut could not draw is still counted. The `ψᵢ` are exactly the fresh
propositions of the paper's §6 definitional rendering.

Read the badges and the explosion is located. `ψ₁` is 9 arena nodes and 12
flat; `ψ₆`, a three-way `⋁`, is 114 arena nodes and **430 508** flat.
The violence is not in the recursion — which is a modest 49-node tree over 4
depths (`1, 10, 30, 8`) from 34 call sites, 26 distinct, 19 memoized — but in
what each node's `tilde` substitution does to the formula: the shared arena of
1 287 nodes has a flat unfolding of **1 991 717**. That is the size recurrence
of §2.3 — `f(M, Σ) ≈ f(M′, T) · maxₘ f(M, Σ∖{c})`, multiplicative because a
block formula is copied into every occurrence of every `T`-letter — and it is
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

## FIG-4 — the `F a` micro-machine (paper Figure 2)

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
