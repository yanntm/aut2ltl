# Reproduction — `sos_core` figures

The authority for these figures: what is built, from what, by which command, and
exactly where the human hand touches it. Every command runs from the repository
root, is single-input, and finishes in ~2 s.

## 0. Prerequisites

`pdflatex` with TikZ/PGF and the `standalone` class (TeX Live), `pdftoppm`
(poppler-utils), and GraphViz `dot`, all on `PATH`. Spot and the in-tree `sosl`
package. No network.

## 1. Inputs, with provenance

The four `.sos` invariants are bundled in [`sources/`](sources/) — the artifact
is self-contained. A `.sos` is a *complete language invariant*, so none of them
depends on an automaton presentation.

```sh
# GF(aa), Even, EvenBlocks — standing fixtures.
cp samples/fixtures/hoa/sos/{gf_aa,even,evenblocks}.sos research_notes/sos_core_figs/sources/

# a*.b^w (b := !a) — the warm-up, built from the formula it denotes.
cd sosl && python3 -c "
from sosl.sos.build import reference_of_ltl
from sosl.sos.io import dump_invariant
inv = reference_of_ltl('a U G!a'); inv.validate()
open('../samples/fixtures/hoa/sos/astar_bomega.sos','w').write(dump_invariant(inv))"
cp samples/fixtures/hoa/sos/astar_bomega.sos research_notes/sos_core_figs/sources/
```

`reference_of_ltl`, **not** `import_ltl` — the latter returns a Spot automaton,
not an `Invariant`.

## 2. Build

```sh
make -C research_notes/sos_core_figs          # all four
make -C research_notes/sos_core_figs clean    # drop LaTeX by-products
```

One figure at a time (from `sosl/`; this is the provenance line of each `.tex`):

```sh
cd sosl && python3 -m tests.sos.sos2cayley \
  ../research_notes/sos_core_figs/sources/even.sos \
  --name core_F2_even \
  --out-dir ../research_notes/sos_core_figs/sources \
  --img-dir ../research_notes/sos_core_figs/img \
  --rename 'a=a,!a=b' --rankdir TB
```

and likewise `astar_bomega.sos → core_F0_astar_bomega`, `gf_aa.sos →
core_F1_gf_aa`, `evenblocks.sos → core_F3_evenblocks`. Each run prints the
figure's `P` line.

`--rename 'a=a,!a=b'` fixes the display letters *and their order*. It matters:
the machine alphabet orders letters `!a < a` (absent before present), so a
`.sos`'s stored keys are shortlex-least under `b < a`. Keys, node order and
letter indices downstream all follow the rename order, never the machine one —
they are **recomputed, never read** from the file.

## 3. What is machine, what is hand

Per figure, `sources/` holds:

| file | owner | rewritten by a re-run? |
|---|---|---|
| `<name>_gen.dot` | machine | yes — a pure function of the `.sos` |
| `<name>_gen.tex` | machine | yes — likewise |
| `<name>.tex` | **hand** | **no** — seeded once from `_gen.tex`, then ours |
| `<name>.pdf` | machine | yes — compiled from `<name>.tex` |
| `img/<name>.png` | machine | yes — rasterized from `<name>.pdf` |

**The hand edits are decoration, and provably so.** A hand edit may touch
*placement directives only*: `\node` coordinates, `loop <dir>`, `bend`, the
caption anchor. It may never touch a `\draw`, a label, or a node's style — so
the graph in the paper is the graph the machine derived, moved around. The proof
is a diff away, and it is the reason both forms are committed:

```sh
diff research_notes/sos_core_figs/sources/core_F2_even{_gen,}.tex
#   -> only \node coordinates and loop/bend options; every \draw identical
```

The four figures are currently hand-placed on a shared grid (root above, classes
in a square, no crossing edges). Delete a `<name>.tex` and re-run to fall back to
the machine layout at any time.

**The verdicts are the machine's, and are inspectable.** Nothing a hand can do to
the `.tex` changes what the figure *asserts*, because every assertion is derived
from the `.sos` on each build:

- which node is the root, and that **no edge enters it** (freshness — a hard
  assert on every run, on every input);
- that every class is reachable from `[ε]`;
- which classes are **idempotent** (`c·c = c`) — the thick borders;
- which arrows are **key-tree** edges — the thicker strokes;
- the **monochrome cycles** (computed and asserted, deliberately not inked);
- the **accepting pairs `P`** — the caption, and echoed on stdout.

To see them without any drawing at all:

```sh
cd sosl && python3 -m sosl.sos.viz ../samples/fixtures/hoa/sos/even.sos --rename 'a=a,!a=b'
#   -> the generic dot text, plus the P line
```

## 4. The tool

- `sosl/sosl/sos/viz/` — the engine service: any `.sos` → a picture, generic over
  any invariant and any alphabet, with its own CLI
  (`python3 -m sosl.sos.viz <file.sos> -o out.{dot,tex,pdf,png}`). See its
  `README.md` / `algorithm.md`.
- `sosl/tests/sos/sos2cayley.py` — the paper wrapper: the two-file convention of
  §3, and the `P` line.
