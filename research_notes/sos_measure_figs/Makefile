# Figures for `sos_measure.md` — TikZ sources to page-safe PNGs.
#
#   make            regenerate every .tex from its probe, then rasterize
#   make tex        regenerate the .tex sources only
#   make img        rasterize the existing .tex sources only
#   make sources    rebuild the .sos inputs (fd.sos, fe.sos) from the paper
#   make clean      drop the LaTeX by-products (keeps .tex and .png)
#
# Run from this directory. The probes are invoked from `sosl/` (the quant
# tests are a `sosl/tests` package), so figure paths are passed absolute.
HERE   := $(abspath .)
SOSL   := $(abspath ../../sosl)
SRC    := sources
IMG    := img
DPI    := 220
PY     := python3

FIGS   := fig1_readoff fig2_cut fig3_kernel
PNGS   := $(addprefix $(IMG)/,$(addsuffix .png,$(FIGS)))

.PHONY: all tex img sources clean
all: tex img

# ---- inputs: the two paper examples, canonicalized ----------------------
sources:
	cd $(SOSL) && $(PY) -m tests.quant.figs.sources $(HERE)/$(SRC)

# ---- sources: each .tex is the output of exactly one probe --------------
tex:
	cd $(SOSL) && $(PY) -m tests.quant.figs.fig1 \
	  $(HERE)/$(SRC)/fe.sos $(HERE)/$(SRC)/fig1_readoff.tex
	cd $(SOSL) && $(PY) -m tests.quant.figs.fig2 \
	  $(HERE)/$(SRC)/fd.sos $(HERE)/$(SRC)/fig2_cut.tex
	cd $(SOSL) && $(PY) -m tests.quant.figs.fig3 \
	  $(HERE)/$(SRC)/fd.sos $(HERE)/$(SRC)/fig3_kernel.tex

img: $(PNGS)

$(IMG)/%.png: $(SRC)/%.tex
	@mkdir -p $(IMG)
	pdflatex -interaction=nonstopmode -halt-on-error \
	  -output-directory=$(SRC) $< > $(SRC)/$*.log 2>&1 \
	  || { tail -20 $(SRC)/$*.log; exit 1; }
	pdftoppm -png -r $(DPI) -singlefile $(SRC)/$*.pdf $(IMG)/$*

clean:
	rm -f $(SRC)/*.aux $(SRC)/*.log $(SRC)/*.pdf
