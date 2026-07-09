# Figures for `sos_toltl.md` — TikZ sources to page-safe PNGs.
#
#   make            regenerate every .tex from its probe, then rasterize
#   make tex        regenerate the .tex sources only
#   make img        rasterize the existing .tex sources only
#   make clean      drop the LaTeX by-products (keeps .tex and .png)
#
# Run from this directory. The probes are invoked from the repository root,
# so every path below is relative to it.

ROOT   := ../..
SRC    := sources
IMG    := img
DPI    := 220
PY     := python3

FIGS   := fig1_cayley fig3_dg fig4_fa
PNGS   := $(addprefix $(IMG)/,$(addsuffix .png,$(FIGS)))

.PHONY: all tex img clean
all: tex img

# ---- sources: each .tex is the output of exactly one probe --------------
tex:
	cd $(ROOT) && $(PY) -m tests.sos2ltl.figs.fig1 \
	  research_notes/sos_toltl_figs/$(SRC)/gf_aa.sos \
	  research_notes/sos_toltl_figs/$(SRC)/fig1_cayley.tex
	cd $(ROOT) && $(PY) -m tests.sos2ltl.figs.fig3 \
	  research_notes/sos_toltl_figs/$(SRC)/gf_aa.sos \
	  research_notes/sos_toltl_figs/$(SRC)/fig3_dg.tex
	cd $(ROOT) && $(PY) -m tests.sos2ltl.figs.fig4 \
	  research_notes/sos_toltl_figs/$(SRC)/fa.sos \
	  research_notes/sos_toltl_figs/$(SRC)/fig4_fa.tex

img: $(PNGS)

$(IMG)/%.png: $(SRC)/%.tex
	@mkdir -p $(IMG)
	pdflatex -interaction=nonstopmode -halt-on-error \
	  -output-directory=$(SRC) $< > $(SRC)/$*.log 2>&1 \
	  || { tail -20 $(SRC)/$*.log; exit 1; }
	pdftoppm -png -r $(DPI) -singlefile $(SRC)/$*.pdf $(IMG)/$*

clean:
	rm -f $(SRC)/*.aux $(SRC)/*.log $(SRC)/*.pdf
