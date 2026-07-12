# Figures for `sos_core.md` section 3 — .sos invariants to page-safe PNGs.
#
#   make            regenerate the machine forms, compile the hand-owned .tex,
#                   rasterize into img/
#   make clean      drop the LaTeX by-products (keeps .tex, .pdf, .png)
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
