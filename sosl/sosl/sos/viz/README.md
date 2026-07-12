# sosl.sos.viz — drawing an invariant

The Cayley graph of an `Invariant`, as a picture. Turn the algebra `(C, key, λ,
M)` into a *figure model* — a layout-agnostic graph whose nodes and edges already
carry every fact a drawing wants to show — then render it, to GraphViz `dot` or
to hand-editable TikZ, with the accepting pairs `P` as the caption underneath.

    python3 -m sosl.sos.viz <file.sos> -o <out.dot|.tex|.pdf|.png>
                            [--rename 'a=a,!a=b'] [--layout dot|layered] [--no-pairs]

`model`, `dot` and `tikz` are pure text; the two impure modules are named as
such (`layout` runs `dot -Tplain` to harvest coordinates, `render` runs
`pdflatex` / `pdftoppm` / `dot`), and every external call is bounded and reported
on failure, never worked around.

## Services

- **The figure model** (`model.py`). `figure_of(inv, rename=…)` walks the
  algebra once and returns a `Figure`: one `Node` per class and one `Edge` per
  (class, letter), with the classification a drawing needs already decided —
  which node is the root, which are idempotent, which edges form the key tree,
  which edges lie on a monochrome cycle. Keys are **recomputed** by a BFS in the
  caller's letter order, not read from `inv.keys` (see `algorithm.md`: the
  serialized keys are shortlex-least in the *machine* letter order, where
  `!a < a`; a figure usually wants `a` first).
- **Display letters** (`model.Naming`). The machine alphabet names letters by
  Boolean cube (`a`, `!a`, `a&!b`). A figure renames them (`!a ↦ b`) and fixes
  the order in which letters are tried and drawn. Everything downstream of
  `figure_of` speaks display letters only.
- **The dot backend** (`dot.py`). `dot_of(fig)` — a generic `digraph` for any
  invariant over any alphabet: the model's classification carried in node/edge
  attributes, `P` as the graph title. Good enough to look at an arbitrary `.sos`
  on its own; also the layout oracle for the TikZ backend.
- **The TikZ backend** (`tikz.py`). `tikz_of(fig, placement)` — a standalone
  `.tex` written to be *nudged*: all styling centralized in one `\tikzset`, one
  named `\node` per class at an explicit coordinate, one `\draw` per edge.
  Restyling is one style; moving a node is one number.
- **Placement** (`layout.py`). `place(fig, engine)`: `layered` (pure — column by
  key length) or `dot` (the coordinates GraphViz computes, which untangles what a
  naive layering crosses).

## Orientation map

    model     Figure / Node / Edge / Naming; figure_of(inv) — the classification
    dot       dot_of(fig) — generic digraph text (display + layout oracle)
    tikz      tikz_of(fig, pos) — standalone, hand-editable .tex
    layout    place(fig) — class -> (x, y) in cm; `dot -Tplain` or pure layering
    render    pdflatex / pdftoppm / dot -Tpng — the external steps

## See also

`algorithm.md` — key recomputation, the key tree, and the monochrome-cycle
criterion (the three things that are not obvious). The consumer of record is
`sosl/tests/sos/sos2cayley.py` (paper figures for `research_notes/sos_core.md`),
which adds the two-file hand-editing convention and checks each figure against a
theory-written expectation.
