# Reproduction guide — `sos_toltl` figures

Every command runs from the repository root unless stated. Probes are
single-input and self-bound (≤ 15 s each; these finish in well under 1 s).
The figure probes live in [`tests/sos2ltl/figs/`](../../tests/sos2ltl/figs).

## 0. Prerequisites

`pdflatex` with TikZ/PGF and `standalone` (TeX Live), and `pdftoppm`
(poppler-utils) on `PATH`. Spot and the in-tree `aut2ltl` / `sosl` packages
for the probes. No network, no external drawing tool.

## 1. The inputs (bundled, with provenance)

Both `.sos` invariants are bundled in [`sources/`](sources/), so the artifact
is self-contained. They are language-canonical: an invariant is a complete
language invariant, so neither depends on an automaton presentation.

```sh
# GF(aa) — the six-class syntactic algebra. Byte-identical from either the
# run-parity or the reset presentation (canonicity check, see sos_figs/).
cp samples/fixtures/hoa/sos/gf_aa.sos research_notes/sos_toltl_figs/sources/gf_aa.sos

# F a — the pure-peel micro-example, built straight from the formula.
cd sosl && python3 -m tests.sos.build_sos 'F a' \
  --sos ../research_notes/sos_toltl_figs/sources/fa.sos
```

## 2. The figures

`make` regenerates every `.tex` from its probe, then rasterizes. The probes
are the source of truth: each writes its own TikZ, so no number in a figure is
hand-copied.

```sh
make -C research_notes/sos_toltl_figs          # tex + png
make -C research_notes/sos_toltl_figs tex      # sources only
make -C research_notes/sos_toltl_figs img      # rasterize only
make -C research_notes/sos_toltl_figs clean    # drop .aux/.log/.pdf
```

Equivalently, one figure at a time (this is the provenance footer of each):

```sh
python3 -m tests.sos2ltl.figs.fig1 \
  research_notes/sos_toltl_figs/sources/gf_aa.sos \
  research_notes/sos_toltl_figs/sources/fig1_cayley.tex
python3 -m tests.sos2ltl.figs.fig2 \
  research_notes/sos_toltl_figs/sources/gf_aa.sos \
  research_notes/sos_toltl_figs/sources/fig2_stack.tex
python3 -m tests.sos2ltl.figs.fig3 \
  research_notes/sos_toltl_figs/sources/gf_aa.sos \
  research_notes/sos_toltl_figs/sources/fig3_dg.tex
python3 -m tests.sos2ltl.figs.fig4 \
  research_notes/sos_toltl_figs/sources/fa.sos \
  research_notes/sos_toltl_figs/sources/fig4_fa.tex
```

Called without an output path, a probe only prints what it would draw — the
cheapest way to check a figure's numbers. Set `FIGS_TRACE` (or the global
`TRANSLATOR_TRACE_ON`) for the per-node / per-edge dump on stderr.

## 3. The numbers, and where they come from

The figure probes read structure off the tested modules (`cayley`,
`anchoring`, `windows`, `engine._committed`) and sizes off the tested
primitives (`Ast.tree_size`, `len(Ast)`). They own only the placement.
Cross-check any figure against the standing E0 probes:

```sh
# FIG-2: the bricks themselves, straight from the engine
SOS2LTL_TRACE=1 python3 -m tests.sos2ltl.e0_engine samples/fixtures/hoa/sos/gf_aa.sos
#   -> one `[engine] layer=… brick=… formula=…` line per brick, on stderr

# FIG-1: layers and the R-order; the (A) widths; the (B) widths + witnesses
python3 -m tests.sos2ltl.e0_layers    samples/fixtures/hoa/sos/gf_aa.sos --expect gfaa
python3 -m tests.sos2ltl.e0_anchoring samples/fixtures/hoa/sos/gf_aa.sos --expect gfaa
python3 -m tests.sos2ltl.e0_windows   samples/fixtures/hoa/sos/gf_aa.sos --expect gfaa

# FIG-3: the three totals the caption quotes
python3 -m tests.sos2ltl.e0_dg samples/fixtures/hoa/sos/gf_aa.sos
#   -> 19 nodes, arena 1287, tree 1991717

# FIG-3, the second size pair (post-Spot, quoted only in the figure's note)
python3 -m survey --hoa samples/fixtures/hoa/sos/gf_aa_parity.hoa --use sos2ltl_dg
#   -> dag=258 tree=315412 sharing=1222.5
```

Expected read-offs for `GF(aa)`: 6 classes, 4 layers `{0} → {1,3} | {2,4} →
{5}`, entry classes `1` and `2`, prefix-independent, absorbing `[5]`; layers
`{1,3}` and `{2,4}` 1-anchored, layer `{5}` frozen; `{5}` passes (B) at
`k′ = 2` with a replayable `k′ = 1` conflict witness
`(a;a, a;!a)^ω` [reject] vs `(a;a, a;a;!a)^ω` [accept].
For `F a`: 3 classes, 3 singleton layers, `P = {([a],[!a]), ([a],[a])}`,
committed class `[a]`.

## 4. Style

The palette, the node/edge styles and the `standalone` preamble live once in
[`tests/sos2ltl/figs/tikz.py`](../../tests/sos2ltl/figs/tikz.py); the layered
machine drawing (FIG-1, FIG-4) in
[`machine.py`](../../tests/sos2ltl/figs/machine.py); the operator view of the
DG arena that FIG-3 draws (heads, slots, arity, AC) in
[`formulaview.py`](../../tests/sos2ltl/figs/formulaview.py). Letters are told
apart by hue *and* dash pattern, so the figures survive greyscale printing.
