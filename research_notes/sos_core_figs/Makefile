# Figures for `sos_core.md` section 3 — .sos invariants to page-safe PNGs.
#
#   make            compile the hand-owned .tex, rasterize into img/, refresh the
#                   machine forms (_gen.tex, _gen.dot)
#   make reseed     the same, but REDRAW each hand-owned .tex from the machine at
#                   its own coordinates — the way to propagate a change of style or
#                   of drawn content (a new label rule, a new arc rule) into figures
#                   that have been placed by hand. `harvest()` in sos2cayley reads
#                   back ONLY the node coordinates and the self-loop directions.
#
#   WARNING: reseed keeps coordinates and loop directions, nothing else. Any OTHER
#   hand geometry — a manual `to[bend ...]` on an arrow, a hand-set pair loop — is
#   NOT harvested and IS lost on reseed. Re-apply it by hand afterwards (grep the
#   commit / diff the _gen.tex), then compile that figure directly (do not `make`,
#   which would reseed it again). That is all; see task_cleanup_export.md at root
#   for the owed fix that would make this unnecessary.
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

# One pairs variant: $(call pairfig,<invariant>,<variant name>,<base name>). The
# variant inherits the base figure's hand placement — seeded once by copying the
# base .tex, then always reseeded WITH --draw-pairs, since the pair loops are machine
# (auto bottom-corner, not harvested) while the node coordinates it keeps are the
# base's. Nothing hand-owned is lost by the forced reseed.
pairfig = test -f sources/$(2).tex || cp sources/$(3).tex sources/$(2).tex; \
          $(CAYLEY) $(HERE)/sources/$(1).sos --name $(2) $(COMMON) --reseed --draw-pairs

.PHONY: all reseed figures pairs clean
all:    pairs
reseed: RESEED := --reseed
reseed: pairs

figures:
	$(call fig,astar_bomega,core_F0_astar_bomega,--keep-identity)
	$(call fig,astar_bomega,core_F0_astar_bomega_b)
	$(call fig,gf_aa,core_F1_gf_aa)
	$(call fig,even,core_F2_even)
	$(call fig,evenblocks,core_F3_evenblocks)
	$(call fig,a_implies_xa,a_implies_xa)
	$(call fig,a_once,a_once)

# The accepting pairs drawn on top of the four elided invariants (Figure 2), each a
# second copy of its base figure with P rendered as bold doubled self-loops.
pairs: figures
	$(call pairfig,astar_bomega,core_F0_astar_bomega_b_pairs,core_F0_astar_bomega_b)
	$(call pairfig,gf_aa,core_F1_gf_aa_pairs,core_F1_gf_aa)
	$(call pairfig,even,core_F2_even_pairs,core_F2_even)
	$(call pairfig,evenblocks,core_F3_evenblocks_pairs,core_F3_evenblocks)
	$(call pairfig,a_implies_xa,a_implies_xa_pairs,a_implies_xa)
	$(call pairfig,a_once,a_once_pairs,a_once)

# One figure by name (base + its pairs variant where one exists), every other
# figure untouched:  make one-a_implies_xa,  make one-core_F2_even, ...
.PHONY: one-core_F0_astar_bomega one-core_F0_astar_bomega_b one-core_F1_gf_aa \
        one-core_F2_even one-core_F3_evenblocks one-a_implies_xa one-a_once
one-core_F0_astar_bomega:
	$(call fig,astar_bomega,core_F0_astar_bomega,--keep-identity)
one-core_F0_astar_bomega_b:
	$(call fig,astar_bomega,core_F0_astar_bomega_b)
	$(call pairfig,astar_bomega,core_F0_astar_bomega_b_pairs,core_F0_astar_bomega_b)
one-core_F1_gf_aa:
	$(call fig,gf_aa,core_F1_gf_aa)
	$(call pairfig,gf_aa,core_F1_gf_aa_pairs,core_F1_gf_aa)
one-core_F2_even:
	$(call fig,even,core_F2_even)
	$(call pairfig,even,core_F2_even_pairs,core_F2_even)
one-core_F3_evenblocks:
	$(call fig,evenblocks,core_F3_evenblocks)
	$(call pairfig,evenblocks,core_F3_evenblocks_pairs,core_F3_evenblocks)
one-a_implies_xa:
	$(call fig,a_implies_xa,a_implies_xa)
	$(call pairfig,a_implies_xa,a_implies_xa_pairs,a_implies_xa)
one-a_once:
	$(call fig,a_once,a_once)
	$(call pairfig,a_once,a_once_pairs,a_once)

clean:
	rm -f sources/*.aux sources/*.log sources/*.out
