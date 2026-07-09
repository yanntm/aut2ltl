# Build notes — facts and conventions behind the figures

Companion to [`figures.md`](figures.md). Records the measured facts the
figures rest on and the drawing decisions in force, so any figure can be
rebuilt or extended without re-deriving them. Open work items live in the
specification, [`../sos_toltl_figures.md`](../sos_toltl_figures.md), not
here.

## 1. FIG-3's two objects: the call tree and the formula arena

The substituting recursion tree of `GF(aa)` on its six-class algebra is
**49 nodes over 4 depths** (`1, 10, 30, 8`), from 34 call sites, 26 distinct;
memoized, 19 nodes. The famous `1 991 717` is a different object: the flat
unfolding of the **formula** — the blow-up happens inside each recursion
node, at the `tilde` substitution that copies a block formula into every
occurrence of every `T`-letter. The recursion visits few nodes; each node
multiplies. Any FIG-3 rendering must keep the two objects distinct: call
tree/DAG on one axis, formula arena (1 287) and its unfolding on the other.

The figure now draws the **formula**; the recursion tallies are quoted in the
caption and printed by the probe, but no longer drawn. The old call-shaped
panels are in the history of `tests/sos2ltl/figs/fig3.py`.

## 1b. The measured shape of the `GF(aa)` arena top

Read off `formulaview` (`python3 -m tests.sos2ltl.figs.fig3`):

- arena 1 287 nodes; **230** of them reachable from the root *in the operator
  view* (the `∨`/`¬` nodes that merely spell a `U` or an `∧` are consumed by
  the head that names them);
- root: `⋁` of arity **7**; its disjuncts are `⋀`s of arity 15, 9, 12, 8, 16,
  19, 15;
- level 1 → 2: **94 arcs onto 36 distinct children**, 25 of them shared, 79 of
  the 90 distinct arcs landing on a shared child.

That width is why the cut is rule-driven, not depth-driven: three operator
levels of this arena are ~44 boxes and 94 arcs, and its tree unfolding at the
same cut is 109 boxes — unreadable at any page size.

## 1c. FIG-3's width discipline, as built

Per the spec's amendment. Drawn: the root, its **3 cheapest disjuncts**
(arities 9, 12, 8 — the rest are one `⋯ 4 more` node), and 10 handles
`ψ₁ … ψ₁₀`. Budget spent: DAG panel **14 nodes / 22 arcs**, tree panel
**26 / 22** — inside the spec's ≈ 40 / ≈ 60.

- **AC relaxation.** `∧`/`∨` carry an arity badge and *no* slot labels
  (`Head.ac` in `formulaview`); only `X`/`U`/`XU` arcs name `φ`/`ψ`.
- **Arcs for sharing.** An arc is drawn to every child two *drawn* disjuncts
  share, plus one unshared representative per node; the rest are the node's
  `+k private` line. A handle's `×n` badge counts its references among *all
  seven* disjuncts, so the sharing the cut did not draw is still counted.
- **Three open branches, not one.** The spec offered "draw one disjunct in
  full". Drawing three stays inside the budget and keeps the left panel
  meaningful: with a single drawn parent there are almost no repeated
  occurrences, so the copies-vs-references contrast — the whole point of the
  pair — would collapse to a badge. Three parents give 22 copies of 10
  subterms. The fallback (swap the specimen) was not needed.

## 2. Which size pair the artifact quotes

- `e0_dg`: **19 recursion nodes / arena 1 287 / flat 1 991 717** — the DG
  induction's own hash-consed AST, before Spot sees anything. **This is the
  pair the paper and the figures quote.**
- `survey --use sos2ltl_dg`: **dag 258 / tree 315 412** — the same formula
  after `to_spot`, where Spot's hash-consing and constructor normalizations
  collapse structure the DG arena keeps.

Both are real; a factor of ~6 separates the flat counts. Never mix them in
one table.

## 3. FIG-2: which rendering, and why a panel rather than a table

The bricks come from the engine's `SOS2LTL_TRACE` dump, re-read by Spot's
parser; the probe never rebuilds one. Two decisions the drawing rests on.

- **Plain rendering, not the default.** `Rendering(residual=False)` draws the
  root's exit fan as `(!a ∧ X Final(1)) ∨ (a ∧ X Final(2))`. The default keys
  exit children by residual; `GF(aa)` is prefix-independent (one residual),
  so the fan collapses to `X Final(5)` and the last derivation step shows
  nothing. Both are exact — the collapse is one of §6's three renderings, and
  E10's ledger prices it.
- **Panel, not table.** The spec allowed either. The panel wins because the
  left column carries something a table cannot: *where in the R-order* the
  step is. Each block's miniature lights the layer being labelled and shades
  the layers already labelled, so "assembled child-first" is visible rather
  than asserted. The right column is a table, in effect, so nothing is lost.
- **Names, not copies.** Subterm names (`Final(5)`, `step`, `leave(3)`) are
  substituted structurally on the hash-consed formula, so a name appears
  exactly where the engine shares a node. Boolean subterms are never named —
  `¬a` reads better than `sojourn(2)`. A layer may only name the labels of
  the classes its exit fans actually reach: `Final(1)` and `Final(4)` are
  *the same formula* (the mirror), so a global name table would print
  whichever was interned last.
- **`STAY∞` / `LEAVE` get no row.** They are the disjuncts of `Final`. The
  one fact they carry that `Final` hides — whether the confinement branch
  survived — is the block's side note.

## 4. Drawing decisions in force

- **TikZ + `pdflatex` + `pdftoppm`**, not `dot`: sources are text, styles
  live in one file, output is paper-grade. The probe emits the `.tex`; the
  `Makefile` rasterizes. Placement (coordinates, bends, loop directions) is
  the *only* thing a probe hard-codes — every node, edge and tag string is
  read off the algebra.
- **Entry glyph**: a short black stub into the node from below-outside (the
  natural side, above, already carries the Cayley step from `[ε]` and the
  grey R-order arrow — three arrowheads in one place read as noise).
- **Parallel letters merged**: where both letters agree on a class (a frozen
  class's loop) one black arrow labelled `!a, a`, in neutral ink.
- **Transient layers** are tagged `transient` only — width displays as `—`,
  never a vacuous `1`.
- **`GF(aa)` layout**: layer boxes left/right mirrored (`{1,3}` left,
  `{2,4}` right), frozen layer centred below — the mirror symmetry of the
  moving layers is visible as an actual reflection.

## 5. Probe capabilities

[`tests/sos2ltl/figs/dgtrace.py`](../../tests/sos2ltl/figs/dgtrace.py):
`TracingSynth` subclasses `dg.synth.Synth`, overriding `node()` (the sole
recursion entry) to record the call graph `(parent, child)` as a multiset;
sizes come from `Ast.tree_size` / `len(Ast)`, and hash-consed `Ast` node
identity *is* subtree identity (what FIG-3's readable-formula rebuild keys
on). Pointed at the census, `dgtrace` would also measure the paper §2.3
sub-call conjecture empirically.
