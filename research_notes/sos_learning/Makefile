# Assemble the split paper parts into a single markdown, ../sos_learning2.md.
#
#   make            # (re)build ../sos_learning2.md from the parts below
#   make clean      # remove the assembled file
#
# Only the parts listed in PARTS are paper text; README.md and notation.md are
# editors' notes and stay out. The parts live in this folder and reference
# figures as ../sos_figs/... and ../sos_core_figs/...; the assembled file sits
# one level up (research_notes/), so ASM strips exactly one leading ../ from
# link and img-src targets.

OUT   := ../sos_learning2.md

PARTS := \
	s0_front.md \
	s2a_mat.md \
	s2b_algebra.md \
	s2c_examples.md \
	s3_table.md \
	s4a_harvest.md \
	s4b_gap.md \
	s4c_sweep.md \
	s5_correctness.md \
	s6_eval.md \
	s7_end.md \
	bib.md

# One-level-up path fix for links and image sources.
ASM := sed -e 's|](\.\./|](|g' -e 's|src="\.\./|src="|g'

.PHONY: all clean
all: $(OUT)

$(OUT): $(PARTS) Makefile
	@printf '%s\n\n' '<!-- ASSEMBLED by research_notes/sos_learning/Makefile — do not edit here; edit the parts in sos_learning/ and re-run make. -->' > $(OUT)
	@for f in $(PARTS); do $(ASM) $$f >> $(OUT); printf '\n\n' >> $(OUT); done
	@echo "wrote $(OUT) from $(words $(PARTS)) parts"

clean:
	rm -f $(OUT)
