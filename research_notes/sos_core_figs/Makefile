# Figures for `sos_core.md` section 3 — .sos invariants to page-safe PNGs.
#
#   make            regenerate the machine forms, compile the hand-owned .tex,
#                   rasterize into img/
#   make clean      drop the LaTeX by-products (keeps .tex, .pdf, .png)
#
# Each figure is the FULL multiplication table of its algebra (every column of M,
# arrows fused under a comma-separated class list). `[eps]` is elided everywhere
# but in `core_F0_astar_bomega`, which passes `--keep-identity`: it and its elided
# twin `core_F0_astar_bomega_b` are the same algebra drawn both ways, the pair that
# shows the elision costs nothing (the identity's row and column are fixed by the
# axiom). Elided is the convention from there on.
#
# To propagate a change of drawn content into the hand-placed figures, add
# `--reseed` to a line: it redraws from the machine *at the tex's own coordinates*
# (`harvest()` in sos2cayley reads them back), so no hand placement is lost.
#
# Run from this directory. sos2cayley is invoked from `sosl/`, so the paths
# below are relative to it.
#
# NOTE: `<name>.tex` is HAND-OWNED — it is seeded once from `<name>_gen.tex` and
# never overwritten afterwards. A re-run refreshes only the machine forms
# (`_gen.tex`, `_gen.dot`) and rebuilds the pdf/png *from the hand-owned .tex*.
# To re-seed a figure from scratch, delete its `<name>.tex` first.

SOSL   := ../../sosl
HERE   := ../research_notes/sos_core_figs
PY     := python3
RENAME := a=a,!a=b

.PHONY: all clean
all:
	cd $(SOSL) && $(PY) -m tests.sos.sos2cayley $(HERE)/sources/astar_bomega.sos \
	  --name core_F0_astar_bomega --out-dir $(HERE)/sources --img-dir $(HERE)/img \
	  --rename '$(RENAME)' --keep-identity
	cd $(SOSL) && $(PY) -m tests.sos.sos2cayley $(HERE)/sources/astar_bomega.sos \
	  --name core_F0_astar_bomega_b --out-dir $(HERE)/sources --img-dir $(HERE)/img \
	  --rename '$(RENAME)'
	cd $(SOSL) && $(PY) -m tests.sos.sos2cayley $(HERE)/sources/gf_aa.sos \
	  --name core_F1_gf_aa --out-dir $(HERE)/sources --img-dir $(HERE)/img \
	  --rename '$(RENAME)'
	cd $(SOSL) && $(PY) -m tests.sos.sos2cayley $(HERE)/sources/even.sos \
	  --name core_F2_even --out-dir $(HERE)/sources --img-dir $(HERE)/img \
	  --rename '$(RENAME)'
	cd $(SOSL) && $(PY) -m tests.sos.sos2cayley $(HERE)/sources/evenblocks.sos \
	  --name core_F3_evenblocks --out-dir $(HERE)/sources --img-dir $(HERE)/img \
	  --rename '$(RENAME)'

clean:
	rm -f sources/*.aux sources/*.log sources/*.out
