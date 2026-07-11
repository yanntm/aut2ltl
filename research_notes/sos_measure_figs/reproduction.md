# Reproduction guide — `sos_measure` figures

Every command runs from the repository root unless stated. The figure probes
live in [`sosl/tests/quant/figs/`](../../sosl/tests/quant/figs) and are invoked
as a `sosl/tests` module, so they run **from `sosl/`**; the `Makefile` does the
`cd` and passes absolute paths. Each probe is single-input and self-bound
(≤ 15 s; all finish in well under 1 s).

## 0. Prerequisites

`pdflatex` with TikZ/PGF and `standalone` (TeX Live), and `pdftoppm`
(poppler-utils) on `PATH`. The in-tree `sosl` package for the probes. No
network, no Spot (the measure engine never calls it), no external drawing tool.

## 1. The inputs (bundled, with provenance)

Both `.sos` invariants are bundled in [`sources/`](sources/), so the artifact is
self-contained. They are the paper's two worked examples, coded from the algebra
and canonicalized; `sources.py` also replays every measure the paper states
(F-E: `μ = 2/3` at uniform, `3/4` at `p_a = 1/3`; F-D: `μ = 1` for every `p`,
the non-kernel split `1`/`0`, the kernel merge `1`/`1`).

```sh
make -C research_notes/sos_measure_figs sources     # rebuild fe.sos, fd.sos
# equivalently, from sosl/:
cd sosl && python3 -m tests.quant.figs.sources \
  ../research_notes/sos_measure_figs/sources
```

## 2. The figures

`make` regenerates every `.tex` from its probe, then rasterizes. The probes are
the source of truth: each writes its own TikZ, so no number in a figure is
hand-copied.

```sh
make -C research_notes/sos_measure_figs          # tex + png
make -C research_notes/sos_measure_figs tex      # sources only
make -C research_notes/sos_measure_figs img      # rasterize only
make -C research_notes/sos_measure_figs clean    # drop .aux/.log/.pdf
```

Equivalently, one figure at a time (this is the provenance footer of each), run
from `sosl/`:

```sh
python3 -m tests.quant.figs.fig1 \
  ../research_notes/sos_measure_figs/sources/fe.sos \
  ../research_notes/sos_measure_figs/sources/fig1_readoff.tex
python3 -m tests.quant.figs.fig2 \
  ../research_notes/sos_measure_figs/sources/fd.sos \
  ../research_notes/sos_measure_figs/sources/fig2_cut.tex
python3 -m tests.quant.figs.fig3 \
  ../research_notes/sos_measure_figs/sources/fd.sos \
  ../research_notes/sos_measure_figs/sources/fig3_kernel.tex
```

Called without an output path, each probe only prints what it would draw — the
cheapest way to check a figure's numbers (`fig1` the x-vector, `fig2` the cut /
parity structure, `fig3` the four `Val` verdicts). `fig2 … --scan` searches
seeds and reports the word length and cut structure of each.

## 3. The numbers, and where they come from

The figure probes read every value off the tested measure engine
(`sosl.quant`: `bottom_sccs`, `kernel`, `kernel_idempotent`, `theta_profile`,
`measure`, `value_vector`) and the calculus `Table` (`fold`, `idem`, `val`),
and the SCC boxes off the calculus `_right_cayley_sccs` pass. They own only the
placement. Cross-check against the source builder and the M1/M2 gates:

```sh
cd sosl
python3 -m tests.quant.figs.sources        # F-E / F-D values vs the paper
python3 -m tests.quant.fixtures            # the M1 hand fixtures F-A/F-B/F-C
```

Expected read-offs — **F-E** (`fe.sos`, 5 classes): bottom SCCs `{[¬a]}`,
`{[a·¬a]}`; kernel `{[¬a], [a·¬a]}`; `θ = (1, 0)`; x-vector by class id
`[2/3, 1, 1/3, 0, 2/3]`; `μ = 2/3`. **F-D** (`fd.sos`, 9 classes): unique bottom
SCC `{[a·a], [¬a·a·¬a]} = {fold(aa), fold(baa)}`, `k = fold(aa)`, `θ = (1,)`,
`μ = 1`; `Val(fold(b), e') / Val(fold(bb), e') = 1 / 0` with `e' = fold(ba)`,
`Val(·, k) = 1 / 1`.

The FIG-2 word is sampled with `random.Random(20260887)` at length 56 (the seed
and length are constants in `fig2.py`, printed in the figure's provenance);
`--scan` documents how the seed was chosen (shortest uniform word exhibiting a
genuine `H(k)` excursion with ≥ 3 `J`-cuts).

## 4. Style

The palette, node/edge styles and the `standalone` preamble live once in
[`sosl/tests/quant/figs/tikz.py`](../../sosl/tests/quant/figs/tikz.py); the
decorated right-Cayley drawing shared by FIG-1 and FIG-3 in
[`cayley.py`](../../sosl/tests/quant/figs/cayley.py); the word ruler of FIG-2 in
[`fig2_draw.py`](../../sosl/tests/quant/figs/fig2_draw.py). Letters are told
apart by hue *and* dash pattern, so the figures survive greyscale printing.
