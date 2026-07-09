# Task — figures for "The LTL Frontier from the Syntactic ω-Semigroup"

*For a code/figure-focused session. Produce the figures the paper
[`sos_toltl.md`](sos_toltl.md) marks as `⟨TBD: FIG-n …⟩`, replacing its ASCII
placeholders. Deliverable: `research_notes/sos_toltl_figs/` (images) plus a
`sos_toltl_figs/figures.md` index, one stable heading per figure
(`## FIG-1`, …), each with a paper-facing caption and a one-line provenance
footer (`<!-- from: <probe> <input> -->`) so it can be regenerated. Do **not**
edit the paper prose; if a figure spec below is unbuildable as stated, report
back rather than improvising.*

All inputs are language-canonical: build from the named `.sos` invariants
(`genaut/corpus/flat_canon/sos/`, or the triptych fixtures under
`samples/fixtures/hoa/sos/`), never from an arbitrary automaton presentation.
Every number shown in a figure must be produced by a probe, not transcribed
by hand.

## FIG-1 — the layered Cayley graph of `GF(aa)` (paper §5.2, replaces the
R-order ASCII)

One drawing, three visual strata:

- **Nodes** = the six classes of `S(GF(aa))₊¹`, labelled by shortlex key
  (`[ε]`, `[!a]`, `[a]`, `[!a·a]`, `[a·!a]`, `[a·a]`) *and* class id 0–5.
- **Edges** = the Cayley steps `c →^x c·λ(x)`, one arrow per (class, letter),
  letters `a` / `!a` distinguished (solid / dashed, or two colors from the
  repo's standard palette).
- **Layer boxes**: the four SCCs `{0}`, `{1,3}`, `{2,4}`, `{5}` drawn as
  rounded boxes; the R-order as thick grey arrows between boxes (the diamond
  `{0} → {1,3} | {2,4} → {5}`).
- **Per-layer annotation** (small side-tag on each box): the letter kinds —
  e.g. `{1,3}`: `!a ↦ reset(1), a ↦ reset(3)`, "(A) at k=1"; `{5}`: "frozen;
  (B) at k′=2"; `{0}`: "transient". Entry classes (1 and 2) marked with an
  incoming-arrow glyph.

Layout suggestion: vertical, top `{0}`, bottom `{5}`, mirroring the paper's
ASCII. Verify the edge list against `Cay(L)` computed by the C1 probe
(`aut2ltl/sos2ltl/cayley.py` consumers under `tests/sos2ltl/`), not by hand.

## FIG-2 — the label stack as a derivation (paper §5.2, optional upgrade of
the code-block stack)

A two-column "rules stack" panel for `GF(aa)`: left column the R-order
descent (layer being labelled, highlighted in a miniature of FIG-1), right
column the label produced at that step, in the order of the paper's stack
(`Final(5)`, then `sojourn/step/leave` of `{1,3}`, `Final(1)`, `Final(2)`,
`Final(0)`). Each right-column line carries the rule name used
(`window Ω` / `sojourn` / `step` / `leave` / `exit fan`). The point of the
figure is *evolution*: reading top to bottom shows the representation being
assembled child-first. If this reads better as a table than a drawing, a
table is acceptable — decide and report. The formulas must be the engine's
own output (E0 probe), simplification off, so the figure is checkable.

## FIG-3 — DG recursion: tree vs DAG (paper §2.3)

Side-by-side, same recursion, two renderings:

- **Left**: the DG recursion *tree* for `GF(aa)` on its six-class algebra —
  nodes = calls `DG(monoid, alphabet, target)`, children as in the paper's
  operational listing (one sequence call + one call per T-letter
  occurrence). Do not draw all ~2M flat nodes: draw to depth 3–4 and
  elide with "⋮ (n more)" counts per level, the counts produced by the DG
  probe (`aut2ltl/sos2ltl/dg/`), run with a per-level tally
  ⟨engineering: if the probe does not currently emit per-level tallies, add
  a counter — this is the one new capability the figure needs⟩.
- **Right**: the same recursion memoized — the 19 recursion nodes of the
  shared arena, drawn once each, with reference edges (thin, curved) where
  the tree duplicates. Annotate the three totals under the panels:
  19 recursion nodes / arena 1 287 / flat 1 991 717.

Caption states the mechanism (substitution copies vs references) and points
at the paper's size recurrence.

## FIG-4 — the `F a` micro-machine (paper §5.2, example 1)

Low priority: the paper's ASCII is probably sufficient. If drawn, same
conventions as FIG-1 (three singleton layers in a chain, committed sink
double-circled, the all-rejecting middle layer tagged `STAY∞ = ⊥`).

## Verification gate (every figure)

Regenerate each figure's numbers from its provenance command before
committing; a figure whose numbers cannot be reproduced by a single probe
invocation is not done. Per repo discipline: probes single-input, ≤ 15 s,
long output to `tests/**/logs/`.
