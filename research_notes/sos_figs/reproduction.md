# Reproduction guide — SoS figures & tables

Every command is run from the repository root. Diagnostics are single-input and
self-bound (≤ 15 s). The tools live in [`sosl/tests/sos/`](../../tests/sos) — see
that folder's `README.md` for a source map.

## 0. Prerequisites

Spot (`ltl2tgba`, `autfilt`, the `spot` Python module) and `rsvg-convert`
(librsvg) on `PATH`. The definability pipeline is the in-tree `aut2ltl` package.

## 1. The automata (bundled, with provenance)

The four deterministic HOAs are bundled next to this guide in
[`sources/`](sources/) — `gf_aa_parity.hoa`, `gf_aa_reset.hoa`, `even.hoa`,
`evenblocks.hoa` — so every step below is self-contained. They are the exact
fixtures under `samples/fixtures/hoa/sos/`, copied in. Their provenance:

```sh
# GF(aa) — two presentations of one language (canonicity check):
#   (a) run-parity form (Figure 1a, Table 2): a Z2 in the transition monoid
cp samples/fixtures/hoa/definability/gf_aa_parity.hoa samples/fixtures/hoa/sos/gf_aa_parity.hoa
#   (b) minimal reset form: aperiodic transition monoid, same S(L)
cp samples/fixtures/hoa/definability/gf_aa.hoa        samples/fixtures/hoa/sos/gf_aa_reset.hoa

# Even = (aa)*.b.Sigma^w, with b := !a  (strong SERE match of an initial prefix)
ltl2tgba -D -C --name='Even = (aa)*.b.Sigma^w  [b := !a]' \
  '{ {a[*2]}[*] ; !a }!' -H > samples/fixtures/hoa/sos/even.hoa

# EvenBlocks is a hand-built Fin(0) & Inf(1) automaton (see the fixture header).
# Each !a-transition carries exactly one mark for the parity of the block it
# completes — mark 1 on an even block (Inf(1)), mark 0 on an odd one (Fin(0)) —
# so no edge is double-labelled. PSL reference:
#   GF(!a) & FG( !a -> X{ {a[*2]}[*] ; !a }! ).

# Bundle the four into sources/ for a self-contained artifact:
cp samples/fixtures/hoa/sos/{gf_aa_parity,gf_aa_reset,even,evenblocks}.hoa \
   research_notes/sos_figs/sources/
```

Language identity against the references (each must print `EQUIV`):

```sh
autfilt -q --equivalent-to=<(ltl2tgba 'G F (a & X a)') research_notes/sos_figs/sources/gf_aa_parity.hoa && echo EQUIV
autfilt -q --equivalent-to=<(ltl2tgba 'G F (a & X a)') research_notes/sos_figs/sources/gf_aa_reset.hoa  && echo EQUIV
autfilt -q --equivalent-to=<(ltl2tgba '{ {a[*2]}[*] ; !a }!') research_notes/sos_figs/sources/even.hoa  && echo EQUIV
autfilt -q --equivalent-to=<(ltl2tgba 'GF(!a) & FG( !a -> X{ {a[*2]}[*] ; !a }! )') \
        research_notes/sos_figs/sources/evenblocks.hoa && echo EQUIV
```

## 2. Compute the algebra (all table parts, per input)

`build_sos.py` reads one input (HOA file **or** LTL/PSL formula) and prints the
Figure-1 line, the Table-1 fingerprint row, the full `EM(D)` dump with the
surjection onto `S(L)₊`, the canonical algebra, and the `.sos` invariant. The
algebra and the serialization come from `sosl` (the sole SoS exporter, fixed to
the fresh-identity convention); `--sos PATH` writes the serialization, and
`--residuals` appends the right-congruence trailer (used for these figures).

```sh
python3 -m tests.sos.build_sos research_notes/sos_figs/sources/gf_aa_parity.hoa \
        --sos samples/fixtures/hoa/sos/gf_aa.sos --residuals
python3 -m tests.sos.build_sos research_notes/sos_figs/sources/gf_aa_reset.hoa \
        --sos samples/fixtures/hoa/sos/gf_aa_reset.sos --residuals
python3 -m tests.sos.build_sos research_notes/sos_figs/sources/even.hoa \
        --sos samples/fixtures/hoa/sos/even.sos --residuals
python3 -m tests.sos.build_sos research_notes/sos_figs/sources/evenblocks.hoa \
        --sos samples/fixtures/hoa/sos/evenblocks.sos --residuals
```

## 3. Cross-checks (headline results)

```sh
# Canonicity: the two GF(aa) presentations yield byte-identical invariants.
diff samples/fixtures/hoa/sos/gf_aa.sos samples/fixtures/hoa/sos/gf_aa_reset.sos && echo IDENTICAL

# Presentation-independence: building from the FORMULA reproduces the same .sos.
python3 -m tests.sos.build_sos 'G F (a & X a)' --sos sosl/tests/sos/logs/gf_from_formula.sos --residuals >/dev/null
diff samples/fixtures/hoa/sos/gf_aa.sos sosl/tests/sos/logs/gf_from_formula.sos && echo IDENTICAL

# GF(aa) is LTL: the synthesized formula is verified Spot-equivalent.
python3 -m tests.probes.dg_probe research_notes/sos_figs/sources/gf_aa_parity.hoa   # VERIFY: equivalent
```

Expected verdicts: `GF(aa)` → LTL; `Even` → not LTL, `F₁` (linear);
`EvenBlocks` → not LTL, `F₂` (ω-power). Sanity `|S(L)₊¹| ≤ |EM¹|` holds in every
row, and `EvenBlocks` shows a single residual class (prefix-independence).

## 4. Render the automata (Figure 1)

Spot draws the SVG; `rsvg-convert` rasterizes to a page-safe PNG (fixed width,
aspect preserved).

```sh
python3 -m tests.sos.render_svg research_notes/sos_figs/sources/gf_aa_parity.hoa research_notes/sos_figs/img/gf_aa.png
python3 -m tests.sos.render_svg research_notes/sos_figs/sources/gf_aa_reset.hoa  research_notes/sos_figs/img/gf_aa_reset.png
python3 -m tests.sos.render_svg research_notes/sos_figs/sources/even.hoa        research_notes/sos_figs/img/even.png
python3 -m tests.sos.render_svg research_notes/sos_figs/sources/evenblocks.hoa  research_notes/sos_figs/img/evenblocks.png
```

## 5. Regenerate the per-example source reports

`assemble.py` renders the full algebra summary behind each file in
[`sources/`](sources/) — the raw material the curated [`figures.md`](figures.md)
is picked from — one input per file, each self-bound (≤ 15 s):

```sh
python3 -m tests.sos.assemble research_notes/sos_figs/sources/gf_aa.md \
  'GF(aa)=research_notes/sos_figs/sources/gf_aa_parity.hoa'
python3 -m tests.sos.assemble research_notes/sos_figs/sources/gf_aa_reset.md \
  'GF(aa) reset=research_notes/sos_figs/sources/gf_aa_reset.hoa'
python3 -m tests.sos.assemble research_notes/sos_figs/sources/even.md \
  'Even=research_notes/sos_figs/sources/even.hoa'
python3 -m tests.sos.assemble research_notes/sos_figs/sources/evenblocks.md \
  'EvenBlocks=research_notes/sos_figs/sources/evenblocks.hoa'
```

The run-parity `gf_aa.md` is the presentation the paper uses (Figure 1a,
Tables 1–2); `gf_aa_reset.md` is the second, aperiodic presentation whose
`.sos` is byte-identical — the canonicity check made visible.

## 6. `aUGb` — the warm-up `a·U·G·b`

`a U G b` with `b := !a`, i.e. the language `a*·bω`. Same four steps as above,
on one input:

```sh
ltl2tgba -D -C --name='aUGb = a*.b^w  [b := !a]' 'a U G!a' -H \
  > research_notes/sos_figs/sources/aUGb.hoa
autfilt -q --equivalent-to=<(ltl2tgba 'a U G!a') research_notes/sos_figs/sources/aUGb.hoa && echo EQUIV

python3 -m tests.sos.build_sos research_notes/sos_figs/sources/aUGb.hoa \
        --sos research_notes/sos_figs/sources/aUGb.sos --residuals
python3 -m tests.sos.render_svg research_notes/sos_figs/sources/aUGb.hoa research_notes/sos_figs/img/aUGb.png
python3 -m tests.sos.assemble research_notes/sos_figs/sources/aUGb.md \
  'aUGb=research_notes/sos_figs/sources/aUGb.hoa'
```

`D` has 3 states (initial `1` looping on `a`, accepting `0` looping on `!a`,
rejecting sink `2`), `|EM¹| = 7`, `|S(L)₊¹| = 5`, no group in the transition
monoid — LTL by construction. Same language as
[`sos_core_figs/sources/astar_bomega.sos`](../sos_core_figs/sources/astar_bomega.sos),
which the other figure set builds from the formula instead.
