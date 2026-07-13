# Figures for `sos_core.md` section 3 — .sos invariants to page-safe PNGs.
#
#   make            compile the hand-owned .tex, rasterize into img/, refresh the
#                   machine forms (_gen.tex, _gen.dot)
#   make reseed     the same, but REDRAW each hand-owned .tex from the machine at
#                   its own coordinates — the way to propagate a change of style or
#                   of drawn content (a new label rule, a new arc rule) into figures
#                   that have been placed by hand. `harvest()` in sos2cayley reads
#                   the coordinates and the self-loop directions back out of the
#                   .tex, so nothing hand-placed is lost.
#   make clean      drop the LaTeX by-products (keeps .tex, .pdf, .png)
#
# Each figure is the FULL multiplication table of its algebra (every column of M,
# arrows fused under a comma-separated class list, an arrow carrying every column
# written `C`). `[eps]` is elided everywhere but in `core_F0_astar_bomega`, which
# passes `--keep-identity`: it and its elided twin `core_F0_astar_bomega_b` are the
# same algebra drawn both ways, the pair that shows the elision costs nothing (the
# identity's row and column are fixed by the axiom). Elided is the convention from
# there on, and `C` is written only there — with `[eps]` drawn it would name two
# different sets, one on a self-loop and another on an arrow that leaves its source.
#
# Run from this directory. sos2cayley is invoked from `sosl/`, so the paths below
# are relative to it.
#
# NOTE: `<name>.tex` is HAND-OWNED. `make` never overwrites it; `make reseed`
# rewrites it from the machine but keeps its placement. To re-seed one from scratch
# (fresh layout, hand placement discarded), delete its `<name>.tex` first.

SOSL   := ../../sosl
HERE   := ../research_notes/sos_core_figs
PY     := python3
RENAME := a=a,!a=b

# One figure: $(call fig,<invariant>,<name>,<extra flags>)
CAYLEY  = cd $(SOSL) && $(PY) -m tests.sos.sos2cayley
COMMON  = --out-dir $(HERE)/sources --img-dir $(HERE)/img \
          --rename '$(RENAME)' --rankdir TB
fig     = $(CAYLEY) $(HERE)/sources/$(1).sos --name $(2) $(COMMON) $(RESEED) $(3)

.PHONY: all reseed figures clean
all:    figures
reseed: RESEED := --reseed
reseed: figures

figures:
	$(call fig,astar_bomega,core_F0_astar_bomega,--keep-identity)
	$(call fig,astar_bomega,core_F0_astar_bomega_b)
	$(call fig,gf_aa,core_F1_gf_aa)
	$(call fig,even,core_F2_even)
	$(call fig,evenblocks,core_F3_evenblocks)

clean:
	rm -f sources/*.aux sources/*.log sources/*.out
