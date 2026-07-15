# Assemble the split paper parts into a single markdown, ../sos_core.md.
#
#   make            # (re)build ../sos_core.md from the parts below
#   make clean      # remove the assembled file
#
# Only the parts listed in PARTS are paper text; README.md and notation.md are
# editors' notes and stay out. The parts live in this folder and reference
# figures as ../sos_core_figs/... and ../sos_figs/...; the assembled file sits
# one level up (research_notes/), so ASM strips exactly one leading ../ from
# link and img-src targets, and deletes the examples.md TOC bullets (the Ex_*
# pages are inlined immediately after, so the intra-folder links are redundant).

OUT   := ../sos_core.md

PARTS := \
	s0_front.md \
	s2_background.md \
	s3_invariant.md \
	s4_construction.md \
	s5_end.md \
	examples.md \
	Ex_aUGb.md \
	Ex_GFaa.md \
	Ex_Even.md \
	Ex_EvenBlocks.md \
	bib.md

# One-level-up path fix + drop TOC lines that link to an Ex_*.md page.
ASM := sed -e 's|](\.\./|](|g' -e 's|src="\.\./|src="|g' -e '/](Ex_[A-Za-z]*\.md)/d'

.PHONY: all clean
all: $(OUT)

$(OUT): $(PARTS) Makefile
	@printf '%s\n\n' '<!-- ASSEMBLED by research_notes/sos_core/Makefile — do not edit here; edit the parts in sos_core/ and re-run make. -->' > $(OUT)
	@for f in $(PARTS); do $(ASM) $$f >> $(OUT); printf '\n\n' >> $(OUT); done
	@echo "wrote $(OUT) from $(words $(PARTS)) parts"

clean:
	rm -f $(OUT)
