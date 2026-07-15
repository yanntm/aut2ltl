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
make -C research_notes/sos_core_figs          # the figures AND the pairs variants
make -C research_notes/sos_core_figs clean    # drop LaTeX by-products
```

Two families come out: the four elided invariants plus the `--keep-identity`
twin, and — from the `pairs` target `make` runs — a `_pairs` variant of each
elided invariant, the same figure with the accepting pairs *drawn* (see §5). A
pairs variant inherits its base figure's hand placement: the `Makefile` seeds it
once by copying the base `.tex`, then always reseeds it with `--draw-pairs`, since
the pair loops are machine (auto bottom-corner) while the coordinates it keeps are
the base's — nothing hand-owned is lost by the forced reseed.

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
*placement* only — `\node` coordinates and `loop <dir>` — never a `\draw`, a
label, or a style. The graph in the paper is the graph the machine derived, moved
around. The proof is a diff away, and it is why both forms are committed:

```sh
diff research_notes/sos_core_figs/sources/core_F2_even{_gen,}.tex
#   -> only \node coordinates and loop directions; every \draw identical
```

The four figures are hand-placed on a shared grid: root above, the classes on a
square (F3 on a 2x3 rectangle), no crossing edges, self-loops outside the square.

**`--reseed` is what makes that survive a redesign, and is the reproduction of the
placement itself.** When the *drawing* changes — a style dropped, a caption added,
labels rewritten — the hand-placed figures would otherwise have to be re-tuned by
hand, or worse, hand-patched (which is how a figure quietly stops matching its
`.sos`). Instead:

```sh
# redraw <name>.tex entirely from the machine, AT ITS OWN COORDINATES
cd sosl && python3 -m tests.sos.sos2cayley … --reseed
```

`harvest()` (in `tests/sos/sos2cayley.py`) reads the existing `<name>.tex` for two
things and two only — the `\node` coordinates and the `to[loop <dir>]` directions —
and hands them back to the generator as the placement. Everything else in the file
is re-derived. So a restyle propagates into a hand-placed figure with **no hand
edit at all**, and the placement is reproducible rather than a pile of nudges: the
content is 100% machine, the arrangement is 100% ours, and the two never mix.

Two decorations are 100% machine — not in the harvest set, so a reseed regenerates
them and there is nothing to hand-tune: the **λ stubs** (elided figures, letters
entering the class they name from a top corner) and the **pair loops** of a
`_pairs` variant (§5, bottom-corner `to[out=…,in=…]` loops — deliberately *not* the
`loop <dir>` form, so `harvest` passes them by).

It refuses rather than half-transplant: if the invariant changed such that a class
is gone or renamed, `harvest` raises and you re-seed from scratch (delete
`<name>.tex` and re-run) instead of silently keeping a stale layout.

**The verdicts are the machine's, and are inspectable.** Nothing a hand can do to
the `.tex` changes what the figure *asserts*, because every assertion is derived
from the `.sos` on each build:

- which node is the root, and that **no edge enters it** (freshness — a hard
  assert on every run, on every input);
- that every class is reachable from `[ε]`;
- which arrows are **key-tree** edges — the thicker strokes;
- which classes are **idempotent** (`c·c = c`), and the **monochrome cycles** —
  both computed and asserted, both deliberately *not* inked: they are properties
  of what is drawn, not further things to draw;
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

## 5. Drawing the accepting pairs (`--draw-pairs`)

The default figure typesets `P` as a caption — an accepting pair is a pair of
classes, not a transition, and forcing it in as an arrow lies about its type. But a
linked pair `(s, e)` satisfies `s·e = s`, so it is a **self-loop at `s`**, always,
by construction (verified on every build: `s·e = s` and `e·e = e`). The `_pairs`
variants exploit exactly that: with `--draw-pairs`, `P` is *drawn* as bold doubled
self-loops at each stem `s`, labelled with the loop classes `[e]` (pairs sharing a
stem fuse into one loop), aimed at a bottom corner outward from the centre. They
ride on top of the plain algebra — a second reading of the same picture — and do not
remove `[e]` from the plain self-loop it already sits on.

```sh
# a pairs variant, seeded from its base figure's placement (the Makefile does this):
cp research_notes/sos_core_figs/sources/core_F1_gf_aa.tex \
   research_notes/sos_core_figs/sources/core_F1_gf_aa_pairs.tex
cd sosl && python3 -m tests.sos.sos2cayley \
  ../research_notes/sos_core_figs/sources/gf_aa.sos --name core_F1_gf_aa_pairs \
  --out-dir ../research_notes/sos_core_figs/sources \
  --img-dir ../research_notes/sos_core_figs/img \
  --rename 'a=a,!a=b' --rankdir TB --reseed --draw-pairs
```
