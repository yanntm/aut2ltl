# Figures for "The LTL Frontier from the Syntactic ω-Semigroup" — specification

*For a code/figure-focused session. The paper is
[`sos_toltl.md`](sos_toltl.md); the figure artifact is
[`sos_toltl_figs/`](sos_toltl_figs/) (index `figures.md`, regeneration
commands `reproduction.md`, build notes `notes.md`). Do not edit the paper
prose. If a spec below is unbuildable as stated, report back rather than
improvising.*

## Status

| figure | subject | state |
|---|---|---|
| FIG-1 | layered Cayley graph of `GF(aa)` | built, in the paper (Figure 3) — **one fix pending** (moving-layer tags, below) |
| FIG-2 | label-stack derivation panel | **todo** — blocked on the engine trace hook (below) |
| FIG-3 | DG explosion, tree vs DAG | built, in the paper (Figure 1) — **rebuild to the readable-formula spec** below |
| FIG-4 | `F a` micro-machine | built, in the paper (Figure 2) — done |

## Ground rules (every figure)

- Inputs are language-canonical `.sos` invariants (bundled under
  `sos_toltl_figs/sources/`), never an arbitrary automaton presentation.
- Every node, edge, tag and label is data produced by a probe
  (`tests/sos2ltl/figs/`), not drawn by hand; placement is the only thing a
  probe may hard-code. Sources are TikZ, rasterized by the artifact's
  `Makefile`; each figure carries a provenance footer in `figures.md`.
- Regenerate each figure's numbers from its provenance command before
  committing; probes single-input, ≤ 15 s, long output to `tests/**/logs/`.
- Drawing conventions (shared, already established in `figures.md`): solid
  blue = Cayley step under `a`; dashed amber = under `!a`; black = both
  letters agree; rounded grey box = layer; thick grey arrow = R-order; black
  stub = entry class; double circle = committed class. Transient layers
  display width `—`, never a vacuous `1` (if `anchoring.analyze` reports 1,
  adjust at the probe).

## FIG-1 — layered Cayley graph of `GF(aa)` (paper §5.2, Figure 3)

**Goal:** the six classes, their Cayley steps, the four layers, the R-order
diamond, each box tagged with its read-off.

**One fix pending.** The moving-layer side tags read `a: exit`, dropping
`a`'s in-layer role. Per the letter tables, on `{1,3}` the letter `a` is
`reset(3)` *and* exits from `3`; on `{2,4}` it is `reset(2)` and exits
from `2`. Tag accordingly — `a ↦ reset(3), exit@3` (resp.
`reset(2), exit@2`), or two lines. The `figures.md` caption already states
the correct roles; the drawing must agree with it.

## FIG-2 — the label stack as a derivation (paper §5.2, Example 2)

**Goal:** a two-column panel for `GF(aa)`: left, the R-order descent (the
layer being labelled, highlighted in a miniature of FIG-1); right, the label
produced at that step — `Final(5)`, then `sojourn`/`step`/`leave` of `{1,3}`,
`Final(1)`, `Final(2)`, `Final(0)` — each line tagged with the rule used
(`window Ω` / `sojourn` / `step` / `leave` / `exit fan`). Reading top to
bottom shows the representation assembled child-first. A table is acceptable
if it reads better than a drawing — decide and report.

**Blocking requirement:** the formulas must be the engine's own bricks,
simplification off. `aut2ltl.sos2ltl.engine.transcribe` returns only the
root label; the bricks are locals in `_layer_flat`/`_layer_graded`. Add a
`_TRACE`-guarded dump in `engine.py`, in the codebase's existing style
(`aut2ltl/daisy/daisy.py`): `_TRACE = "SOS2LTL_TRACE" in os.environ or
"TRANSLATOR_TRACE_ON" in os.environ`, one structured line per brick
(`[engine] layer=… brick=sojourn class=… formula=…`), everything inside
`if _TRACE:`. Do **not** re-implement the brick assembly probe-side — a copy
can drift from the engine, which defeats the figure being checkable. The
paper's §5.2 code block is the expected content; the engine must reproduce
it.

## FIG-3 — the DG explosion, readable as a formula (paper §2.3, Figure 1)

**Goal:** a human can *interpret the formula over the DAG* — read a node,
follow its arcs — with no expansion anywhere, and see the explosion as
copies-vs-references. The current panels (call-site nodes labelled by bare
ids) show only structure; rebuild them so the nodes say what they are:

1. **Nodes are operators over slots.** Label each node with its head
   connective and metavariable slots — `φ U ψ`, `X φ`, `φ ∧ ψ`, `¬φ`,
   `⋁ᵢ φᵢ` for wide disjunctions, atoms verbatim — never an id.
2. **Arcs are slots.** Label each out-arc with the slot it fills (`φ` /
   `ψ`; position for the wide ones). A shared subformula is one node with
   several in-arcs; the sharing itself becomes readable — *the same `φ`,
   used twice*.
3. **Collapse by naming, not ellipsis.** The `GF(aa)` arena (1 287 nodes)
   cannot be drawn whole: draw the top three or four operator levels and
   collapse each cut subtree into a named handle `ψᵢ` — one box per
   *distinct* subtree, reused wherever referenced. These names are exactly
   the fresh propositions of the paper's §6 definitional rendering; the
   caption should say so. A small arena/flat size badge on each `ψᵢ` box is
   welcome where it does not hurt readability.
4. **Panels.** Right: the formula DAG's top, as above. Left: the same top
   expanded as a tree — copies where the DAG references, at the same
   depth — the explosion made visible. If the current call-shaped panels
   still earn a place, they may stay as a second row; the formula-shaped
   pair is the one the paper's reader needs.

**How:** the recursion/call data comes from
[`tests/sos2ltl/figs/dgtrace.py`](../tests/sos2ltl/figs/dgtrace.py)
(`TracingSynth`); formula heads, slots and subtree identity come from the
DG `Ast` (hash-consed — node identity *is* subtree identity; sizes via
`Ast.tree_size` / `len(Ast)`).

**Width discipline** (the arena's top is wide — measured on `GF(aa)`,
a 7-way `∨` of `∧`s with 9–19 conjuncts, 101 arcs into 36 distinct
children — so the cut is rule-driven, not depth-driven):

- **Budget:** ≈ 40 drawn nodes / ≈ 60 drawn arcs per panel; everything
  beyond collapses to named handles.
- **AC relaxation:** `∧`/`∨` are associative-commutative — their in-arcs
  need no slot labels, and an n-ary node carries a width badge
  (`∧ ·14`). Only `X`/`U`/`W` arcs carry `φ`/`ψ`.
- **Arcs are for sharing.** Draw an arc only to (i) a child referenced
  by ≥ 2 drawn parents and (ii) one representative unshared child per
  node; every other child appears as a compact handle list inside its
  parent (`∧ ·14 : ψ₃ ψ₇ … (11 more)`). Every handle everywhere shows
  its in-degree badge (`ψ₃ ×5` — "referenced by 5 of the 7 disjuncts"),
  so sharing stays visible where arcs are not drawn.
- **One open branch.** Of the top disjuncts, draw one in full — the one
  referencing the most shared children — and collapse the siblings to
  handles with size badges. The width itself is part of the message
  (the case split is blindness (4) as syntax); the `∨ ·7` badge carries
  it without 101 arcs.
- **Fallback if the measurements defeat even this:** keep the built
  call-shaped panels for `GF(aa)` (numbers quoted underneath, as now)
  and produce the readable-formula pair on the *smallest catalogue
  language whose DG arena top fits the budget* — a ledger query, report
  which. Do not force `GF(aa)` through a rendering that stops being
  readable; readability is the requirement, the specimen is a
  parameter.

## FIG-4 — the `F a` micro-machine (paper §5.2, Figure 2)

Done. No open items.
