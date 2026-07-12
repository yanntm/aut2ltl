# Reproduction guide — `sos_core` figures

Every command runs from the repository root unless stated. Each is single-input
and self-bound (≤ 15 s; these finish in ~2 s).

## 0. Prerequisites

`pdflatex` with TikZ/PGF and the `standalone` class (TeX Live), `pdftoppm`
(poppler-utils), and GraphViz `dot` — all on `PATH`. Spot and the in-tree `sosl`
package. No network.

## 1. The inputs (bundled, with provenance)

The four `.sos` invariants are bundled in [`sources/`](sources/), so the artifact
is self-contained. They are language-canonical: a `.sos` is a complete language
invariant, so none of them depends on an automaton presentation.

```sh
# GF(aa), Even, EvenBlocks — standing fixtures.
cp samples/fixtures/hoa/sos/{gf_aa,even,evenblocks}.sos research_notes/sos_core_figs/sources/

# a*.b^w (b := !a) — the warm-up, built straight from the formula it denotes.
cd sosl && python3 -c "
from sosl.sos.build import reference_of_ltl
from sosl.sos.io import dump_invariant
inv = reference_of_ltl('a U G!a'); inv.validate()
open('../samples/fixtures/hoa/sos/astar_bomega.sos','w').write(dump_invariant(inv))"
cp samples/fixtures/hoa/sos/astar_bomega.sos research_notes/sos_core_figs/sources/
```

`reference_of_ltl` — *not* `import_ltl`, which returns a Spot automaton rather
than an `Invariant`.

## 2. The figures

`make` regenerates all four; the pdf/png always come from the **hand-owned**
`.tex` (§3), so a tuned coordinate survives a re-run.

```sh
make -C research_notes/sos_core_figs          # gen + compile + rasterize
make -C research_notes/sos_core_figs clean    # drop LaTeX by-products
```

Equivalently, one figure at a time (run from `sosl/`; this is the provenance
footer of each `.tex`):

```sh
cd sosl && python3 -m tests.sos.sos2cayley \
  ../research_notes/sos_core_figs/sources/even.sos \
  --name core_F2_even \
  --out-dir ../research_notes/sos_core_figs/sources \
  --img-dir ../research_notes/sos_core_figs/img \
  --rename 'a=a,!a=b'
```

and likewise `astar_bomega.sos → core_F0_astar_bomega`, `gf_aa.sos →
core_F1_gf_aa`, `evenblocks.sos → core_F3_evenblocks`. Each run prints the
figure's `P` line — the caption, cross-checkable against `sos_core.md` §3.

`--rename 'a=a,!a=b'` fixes the display letters *and their order*: the machine
alphabet is `{a, !a}` and orders letters `!a < a` (absent before present), while
the figures want `a` first. Everything downstream — the keys, the node order, the
letter styles — follows the rename order, not the machine one.

## 3. The two-file convention (what is machine, what is hand)

Per figure, `sources/` holds:

| file | owner | rewritten by a re-run? |
|---|---|---|
| `<name>_gen.dot` | machine | yes — a pure function of the `.sos` |
| `<name>_gen.tex` | machine | yes — likewise |
| `<name>.tex` | **hand** | **no** — seeded once from `_gen.tex`, then yours |
| `<name>.pdf` | machine | yes — compiled from `<name>.tex` |
| `img/<name>.png` | machine | yes — rasterized from `<name>.pdf` |

Traceability is the point, not full machine generation. `diff <name>_gen.tex
<name>.tex` is *exactly* the hand-tuning, and it is auditable at any time. The
`.tex` is written to be nudged: all styling lives in one `\tikzset` block
(`class`, `root`, `idem`, `letter a`, `letter b`, `tree`, `nontree`, `cyc`,
`pairs`), each class is one named `\node` at an explicit rounded coordinate, each
edge one `\draw`. Moving a node is editing one number; restyling is editing one
style. Delete a `<name>.tex` to re-seed it from the machine form.

As of now the four `.tex` are byte-identical to their `_gen.tex`: untuned,
pending review.

## 4. The tool

- `sosl/sosl/sos/viz/` — the engine service: `.sos → picture`, generic over any
  invariant and any alphabet. Its own CLI:
  `python3 -m sosl.sos.viz <file.sos> -o out.{dot,tex,pdf,png}`. See its
  `README.md` / `algorithm.md`.
- `sosl/tests/sos/sos2cayley.py` — the paper wrapper: the two-file convention
  above, and the `P` line on stdout.

Two structural laws are asserted on every run, on every input: **freshness** (no
edge enters `[ε]` — the identity is adjoined, so the root is a source) and
**reachability** (every class is reached from `[ε]`). A violation means the file
is not the invariant of an ω-language, and the run aborts rather than draw it.
