# Machine artifacts for the SoS example pages — reports, .sos exports, EM tables.
#
#   make            refresh the algebra reports (sources/*.md) from the bundled
#                   HOAs, then render the paper-facing EM tables (sources/*.emtable.md)
#   make reports    the reports alone (tests.sos.assemble, one input per file)
#   make tables     the EM tables alone (em_table.py, --rename 'a=a,!a=b')
#   make sos        the .sos exports + the canonicity cross-check
#                   (gf_aa vs gf_aa_reset must be byte-identical)
#
# The automata drawings (img/) are hand-triggered; see reproduction.md §4.
# Run from this directory. The report tools run from `sosl/`.

SOSL   := ../../sosl
HERE   := ../research_notes/sos_figs
PY     := python3
RENAME := a=a,!a=b

ASSEMBLE = cd $(SOSL) && $(PY) -m tests.sos.assemble
BUILDSOS = cd $(SOSL) && $(PY) -m tests.sos.build_sos

# report:  $(call report,<file stem>,<title>,<hoa stem>)
report = $(ASSEMBLE) $(HERE)/sources/$(1).md '$(2)=$(HERE)/sources/$(3).hoa'
# emtable: $(call emtable,<file stem>)
emtable = $(PY) em_table.py sources/$(1).md --rename '$(RENAME)' --out sources/$(1).emtable.md

.PHONY: all reports tables sos
all: reports tables

reports:
	$(call report,aUGb,aUGb,aUGb)
	$(call report,gf_aa,GF(aa),gf_aa_parity)
	$(call report,gf_aa_reset,GF(aa) reset,gf_aa_reset)
	$(call report,even,Even,even)
	$(call report,evenblocks,EvenBlocks,evenblocks)
	$(call report,a_implies_xa,a_implies_xa,a_implies_xa)
	$(call report,a_once,a_once,a_once)

tables:
	$(call emtable,aUGb)
	$(call emtable,gf_aa)
	$(call emtable,even)
	$(call emtable,evenblocks)

sos:
	$(BUILDSOS) $(HERE)/sources/gf_aa_parity.hoa --sos ../samples/fixtures/hoa/sos/gf_aa.sos --residuals > /dev/null
	$(BUILDSOS) $(HERE)/sources/gf_aa_reset.hoa  --sos ../samples/fixtures/hoa/sos/gf_aa_reset.sos --residuals > /dev/null
	$(BUILDSOS) $(HERE)/sources/even.hoa         --sos ../samples/fixtures/hoa/sos/even.sos --residuals > /dev/null
	$(BUILDSOS) $(HERE)/sources/evenblocks.hoa   --sos ../samples/fixtures/hoa/sos/evenblocks.sos --residuals > /dev/null
	$(BUILDSOS) $(HERE)/sources/aUGb.hoa         --sos $(HERE)/sources/aUGb.sos --residuals > /dev/null
	$(BUILDSOS) $(HERE)/sources/a_implies_xa.hoa --sos $(HERE)/../sos_core_figs/sources/a_implies_xa.sos --residuals > /dev/null
	$(BUILDSOS) $(HERE)/sources/a_once.hoa       --sos $(HERE)/../sos_core_figs/sources/a_once.sos --residuals > /dev/null
	diff ../../samples/fixtures/hoa/sos/gf_aa.sos ../../samples/fixtures/hoa/sos/gf_aa_reset.sos && echo CANONICITY-OK
