# Reproduction guide — SOSG figures & tables

Every command is run from the repository root. Diagnostics are single-input and
self-bound (≤ 15 s). The tools live in [`tests/sosg/`](../../tests/sosg) — see
that folder's `README.md` for a source map.

## 0. Prerequisites

Spot (`ltl2tgba`, `autfilt`, the `spot` Python module) and `rsvg-convert`
(librsvg) on `PATH`. The definability pipeline is the in-tree `aut2ltl` package.

## 1. Build and verify the fixtures

The four HOA fixtures under `samples/fixtures/hoa/sosg/`.

```sh
# GF(aa) — two presentations of the same language (canonicity check):
#   (a) run-parity form, carries a Z2 in the transition monoid
cp samples/fixtures/hoa/definability/gf_aa_parity.hoa samples/fixtures/hoa/sosg/gf_aa_parity.hoa
#   (b) minimal reset form, aperiodic transition monoid
cp samples/fixtures/hoa/definability/gf_aa.hoa        samples/fixtures/hoa/sosg/gf_aa_reset.hoa

# Even = (aa)*.b.Sigma^w, with b := !a  (strong SERE match of an initial prefix)
ltl2tgba -D -C --name='Even = (aa)*.b.Sigma^w  [b := !a]' \
  '{ {a[*2]}[*] ; !a }!' -H > samples/fixtures/hoa/sosg/even.hoa

# EvenBlocks is a hand-built Fin&Inf automaton (see the fixture header);
# its PSL reference formula is  GF(!a) & FG( !a -> X{ {a[*2]}[*] ; !a }! ).
```

Language identity against the sources (each must print `EQUIV`):

```sh
autfilt -q --equivalent-to=<(ltl2tgba 'G F (a & X a)') samples/fixtures/hoa/sosg/gf_aa_parity.hoa && echo EQUIV
autfilt -q --equivalent-to=<(ltl2tgba 'G F (a & X a)') samples/fixtures/hoa/sosg/gf_aa_reset.hoa  && echo EQUIV
autfilt -q --equivalent-to=<(ltl2tgba '{ {a[*2]}[*] ; !a }!') samples/fixtures/hoa/sosg/even.hoa  && echo EQUIV
autfilt -q --equivalent-to=<(ltl2tgba 'GF(!a) & FG( !a -> X{ {a[*2]}[*] ; !a }! )') \
        samples/fixtures/hoa/sosg/evenblocks.hoa && echo EQUIV
```

## 2. Compute the algebra (all table parts, per input)

`build_sosg.py` reads one input (HOA file **or** LTL/PSL formula) and prints the
Figure-1 line, the Table-1 fingerprint row, the full `EM(D)` dump with the
surjection onto `S(L)₊`, the canonical algebra, and the `.sosg` invariant; with
`--sosg PATH` it also writes the serialization.

```sh
python3 -m tests.sosg.build_sosg samples/fixtures/hoa/sosg/gf_aa_parity.hoa \
        --sosg samples/fixtures/hoa/sosg/gf_aa.sosg
python3 -m tests.sosg.build_sosg samples/fixtures/hoa/sosg/gf_aa_reset.hoa \
        --sosg samples/fixtures/hoa/sosg/gf_aa_reset.sosg
python3 -m tests.sosg.build_sosg samples/fixtures/hoa/sosg/even.hoa \
        --sosg samples/fixtures/hoa/sosg/even.sosg
python3 -m tests.sosg.build_sosg samples/fixtures/hoa/sosg/evenblocks.hoa \
        --sosg samples/fixtures/hoa/sosg/evenblocks.sosg
```

## 3. Cross-checks (headline results)

```sh
# Canonicity: the two GF(aa) presentations yield byte-identical invariants.
diff samples/fixtures/hoa/sosg/gf_aa.sosg samples/fixtures/hoa/sosg/gf_aa_reset.sosg && echo IDENTICAL

# Presentation-independence: building from the FORMULA reproduces the same .sosg.
python3 -m tests.sosg.build_sosg 'G F (a & X a)' --sosg tests/sosg/logs/gf_from_formula.sosg >/dev/null
diff samples/fixtures/hoa/sosg/gf_aa.sosg tests/sosg/logs/gf_from_formula.sosg && echo IDENTICAL

# GF(aa) is LTL: the synthesized formula is verified Spot-equivalent.
python3 -m tests.probes.dg_probe samples/fixtures/hoa/sosg/gf_aa_parity.hoa   # VERIFY: equivalent
```

Expected verdicts: `GF(aa)` → LTL; `Even` → not LTL, `F₁` (linear);
`EvenBlocks` → not LTL, `F₂` (ω-power). Sanity `|S(L)₊¹| ≤ |EM¹|` holds in every
row, and `EvenBlocks` shows a single residual class (prefix-independence).

## 4. Render the automata (Figure 1)

Spot draws the SVG; `rsvg-convert` rasterizes to a page-safe PNG (fixed width,
aspect preserved).

```sh
python3 -m tests.sosg.render_svg samples/fixtures/hoa/sosg/gf_aa_parity.hoa research_notes/sosg_figs/img/gf_aa.png
python3 -m tests.sosg.render_svg samples/fixtures/hoa/sosg/even.hoa        research_notes/sosg_figs/img/even.png
python3 -m tests.sosg.render_svg samples/fixtures/hoa/sosg/evenblocks.hoa  research_notes/sosg_figs/img/evenblocks.png
```

## 5. Assemble the generic Markdown report (optional)

`assemble.py` renders a full Markdown algebra summary for any set of inputs —
the raw material the curated [`figures.md`](figures.md) is picked from. It is a
general diagnosis tool: point it at any HOA to see the algebra it holds.

```sh
python3 -m tests.sosg.assemble tests/sosg/logs/sosg_report.md \
  'GF(aa)=samples/fixtures/hoa/sosg/gf_aa_parity.hoa' \
  'Even=samples/fixtures/hoa/sosg/even.hoa' \
  'EvenBlocks=samples/fixtures/hoa/sosg/evenblocks.hoa'
```
