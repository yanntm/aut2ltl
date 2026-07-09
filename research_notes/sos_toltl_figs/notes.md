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

## 2. Which size pair the artifact quotes

- `e0_dg`: **19 recursion nodes / arena 1 287 / flat 1 991 717** — the DG
  induction's own hash-consed AST, before Spot sees anything. **This is the
  pair the paper and the figures quote.**
- `survey --use sos2ltl_dg`: **dag 258 / tree 315 412** — the same formula
  after `to_spot`, where Spot's hash-consing and constructor normalizations
  collapse structure the DG arena keeps.

Both are real; a factor of ~6 separates the flat counts. Never mix them in
one table.

## 3. Drawing decisions in force

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

## 4. Probe capabilities

[`tests/sos2ltl/figs/dgtrace.py`](../../tests/sos2ltl/figs/dgtrace.py):
`TracingSynth` subclasses `dg.synth.Synth`, overriding `node()` (the sole
recursion entry) to record the call graph `(parent, child)` as a multiset;
sizes come from `Ast.tree_size` / `len(Ast)`, and hash-consed `Ast` node
identity *is* subtree identity (what FIG-3's readable-formula rebuild keys
on). Pointed at the census, `dgtrace` would also measure the paper §2.3
sub-call conjecture empirically.
