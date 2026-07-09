# Build notes — what the spec asked, what the algebra gave

Issues encountered building the figures of
[`sos_toltl_figures.md`](../sos_toltl_figures.md), recorded for steering. The
figures themselves are in [`figures.md`](figures.md). Three items are
substantive (one is a correction to the paper's §2.3 prose); the rest are
drawing decisions taken and worth confirming.

## 1. The DG recursion tree is 49 nodes, not ~2M — §2.3 conflates two objects

The spec for FIG-3 says: *"Do not draw all ~2M flat nodes: draw to depth 3–4
and elide with '⋮ (n more)' counts per level"*, and asks for a per-level
tally to size the elision. Measured, the substituting recursion tree of
`GF(aa)` on its six-class algebra is **49 nodes over 4 depths** — `1, 10, 30,
8` — from 34 call sites, 26 of them distinct. No elision is needed; the whole
tree fits in a panel.

The 1 991 717 is a different object: the **flat unfolding of the formula**,
not of the recursion. The blow-up happens *inside* each recursion node, at the
`tilde` substitution that transports the compressed-alphabet formula back to
the node's own alphabet by copying a block formula into every occurrence of
every `T`-letter. The recursion visits few nodes; each node multiplies.

This matters for the paper, not just the figure. §2.3 currently reads:

> the memoized recursion is 19 recursion nodes and a shared arena of 1 287
> nodes, while the flat tree unfolds to 1 991 717 nodes

which is true, but the surrounding prose ("*substitution copies vs
references*", "*the multiplicative blow-up is confined entirely to the
unfolding step*") invites reading `1 991 717` as the size of the recursion
unfolded — i.e. as evidence that memoizing the *recursion* is what saves us.
It isn't: memoizing the recursion saves a factor of 49/19 ≈ 2.6. What saves
us is that the *arena* is shared (1 287 nodes) and never flattened. The
recurrence `f(M, Σ) ≈ f(M′, T) · maxₘ f(M, Σ∖{c})` is a recurrence on formula
size, and every one of its levels is a `tilde`, not a recursive call.

**Suggested prose fix** (§2.3, not applied — the task forbids editing the
paper): distinguish the *call* DAG (19 nodes; 49 if copied) from the *formula*
DAG (1 287 nodes; 1 991 717 if flattened), and attribute the multiplicative
recurrence to the latter. The figure as built draws the call DAG in both
panels and quotes the formula sizes underneath, which is the honest pairing,
but the caption has to do work the paper should be doing.

Consequence for the open question. §2.3's `⟨TBD⟩` asks for *"a proven
polynomial bound on the number of distinct sub-calls from `𝓘(L)`"*. The
measurements say the sub-call count is small and the arena is what one should
want a bound on. A polynomial bound on distinct sub-calls would **not** bound
the arena, since one node's `tilde` can multiply. Worth splitting into two
conjectures before anyone tries to prove either.

## 2. Two size pairs, both real, easy to quote wrongly

- `e0_dg`: **19 recursion nodes / arena 1 287 / flat 1 991 717** — the DG
  induction's own hash-consed AST, before Spot sees anything. This is what
  §2.3 quotes and what FIG-3 quotes.
- `survey --use sos2ltl_dg`: **dag 258 / tree 315 412 / sharing 1 222.5×** —
  the same formula after `to_spot`, where Spot's hash-consing and its
  constructors' trivial normalizations (double negation, flattening,
  dedup) collapse structure the DG arena keeps.

Neither is wrong; a factor of ~6 separates the flat counts. Any table mixing
them will be read as an inconsistency. Recommend the paper state which one it
reports, once, and stick to it.

## 3. FIG-2 deferred

The derivation panel wants each `sojourn` / `step` / `leave` / `Final` brick,
with simplification off, as *the engine's own output*.
`aut2ltl.sos2ltl.engine.transcribe` returns only the root label; the bricks
are locals in `_layer_flat` and `_layer_graded`. Two ways to get them:

1. reimplement the 6-line assembly in the probe from the engine's own brick
   helpers (`_sojourn`, `_leave`) — rejected: a probe-side copy of the
   assembly can silently drift from the engine, which defeats the point of
   the figure being checkable;
2. a `_TRACE`-guarded dump in the engine, in the codebase's existing style
   (`aut2ltl/daisy/daisy.py`): `_TRACE = "SOS2LTL_TRACE" in os.environ or
   "TRANSLATOR_TRACE_ON" in os.environ`, one structured line per brick
   (`[engine] layer=1 brick=sojourn class=1 formula=…`) built inside
   `if _TRACE:` so nothing is computed when off. The probe sets the variable,
   captures stderr, and renders. This costs the engine ~8 lines and buys a
   debugging facility beyond the figure.

Option 2 is the intended route. It was not taken because `engine.py` was
under concurrent edit (the `guards.py` AP-formula refactor) throughout this
session, and because that refactor changes the brick *shapes* the panel would
display — guards now render as minimized AP-formulas rather than unions of
cubes, so a panel drawn against the old engine would be stale on arrival.
Build FIG-2 once the refactor has landed.

Note the refactor is already visible in the root label: `GF(aa)` now
transcribes to `DAG 20 / tree 57`, against a 169-character string before.

## 4. Drawing decisions taken (confirm or overrule)

- **`tikz` + `pdflatex` + `pdftoppm`**, not `dot`. Sources are text, the
  palette and styles live in one file, and the output is paper-grade. The
  probe emits the `.tex`; a `Makefile` rasterizes. Placement (coordinates,
  bends, loop directions) is the *only* thing the probes hard-code — every
  node, edge and tag string is read off the algebra.
- **Entry glyph.** The spec asks for entry classes "marked with an
  incoming-arrow glyph". Drawn as a short black stub into the node from
  below-outside, because the natural side (above) is where both the Cayley
  step from `[ε]` and the grey R-order arrow already arrive — three arrowheads
  in one place read as noise.
- **Parallel letters merged.** Where both letters agree on a class (the frozen
  layer's self-loop) one black arrow is drawn labelled `!a, a`, rather than
  two overlapping loops. Letter hue is then meaningless, so the merged arrow
  takes the neutral ink.
- **The transient root shows no `(A)` width.** `anchoring.analyze` reports
  width 1 for layer `{0}`, which is true and vacuous (no class stays). The tag
  says `transient` only, matching the paper. If the intent is that a transient
  layer's width be reported as `—` rather than `1`, that is an `anchoring`
  question, not a drawing one.
- **`GF(aa)` layer boxes are drawn left/right mirrored** (`{1,3}` left,
  `{2,4}` right) with the frozen layer centred below, mirroring the paper's
  ASCII diamond. The mirror symmetry of the two moving layers is then visible
  as an actual reflection.

## 5. New capability added

[`tests/sos2ltl/figs/dgtrace.py`](../../tests/sos2ltl/figs/dgtrace.py) — the
one new capability the spec pre-authorized. `TracingSynth` subclasses
`dg.synth.Synth` and overrides `node()`, the sole recursion entry, to record
the call graph `(parent, child)` as a multiset. It changes nothing in
`dg/synth.py`, computes no sizes of its own (those come from `Ast.tree_size`
and `len(Ast)`), and yields the per-level tallies and the memoized DAG that
FIG-3 draws. It would also answer §2.3's open question empirically across the
census, if pointed at it.
