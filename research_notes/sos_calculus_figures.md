# Task — figures for "Computing with ω-Regular Languages in Canonical Form"

*For a code-focused session, after `sos_calculus_spec.md` §9.1 (E-CAL-EX)
is green — every value drawn here must first pass that gate. Produce the
companion artifact the paper [`sos_calculus.md`](sos_calculus.md) will
point at. You edit only the figures artifact; do **not** touch the paper
prose (theory wires the links in afterwards).*

## Deliverable

One markdown file `research_notes/sos_calculus_figs/figures.md` (with an
`img/` subdir for rendered graphics), each item under a stable heading
(`## Figure 1`, `## Table 1`, …), paper-facing caption, one-line
provenance footer (`<!-- from: <probe/campaign> <input> <git-rev> -->`).
Commit any fixture built (HOA for the two example languages), path noted
in the footer.

## Figure 1 — the running example, as the tool holds it

`𝓘(a*·b^ω)` (paper §2.3; encoding per spec §9.1: one AP `p`, `a = ¬p`,
`b = p`). Two panels:

- (a) the multiplication table and `P`, rendered from the tool's dump —
  must match the paper's 5-class table byte-for-byte in content (keys,
  idempotents, linked pairs, `P = {(B,B), (C,B)}`);
- (b) the right-Cayley graph (nodes `𝒞`, one edge per letter), with
  `stems(P)` highlighted and the dead class `D` visually sunk; this
  panel is reused by §6, where the liveness scan reads
  `Live = 𝒞 \ {D}` off it.

Graphviz or the repo's existing HOA/graph rendering; keep it small
enough to read in a single column.

## Figure 2 — the generated product vs the rectangle

The alignment `𝓘(a*·b^ω) ⊗ 𝓘(GF a)` (paper §3.3): draw the `5 × 3`
rectangle of class pairs ghosted, with the 5 BFS-discovered nodes solid
and the discovery edges labeled by letter. Caption states the ratio
(5/15) and that the scan for `∩ = ∅` runs on the solid nodes only.
Values must match E-CAL-EX item 7.

## Figure 3 — the alignment-ratio distribution (paper §8.2)

Histogram of `|nodes|/(n₁·n₂)` from `reference/calculus/v1_align_ratio.csv`
(regenerate after the §9.4 corpus refresh; until then, mark the figure
DRAFT with the 3938-corpus data): uniform pairs and complement-partner
pairs as two overlaid distributions, medians marked (0.174 / 0.063 on
the old corpus). One panel, log-free axes, no 3D.

## Table 1 — the measured ledger (paper §8.3)

From `reference/calculus/v1_ops.csv`: one row per operation, columns
(operation | calculus warm median ms | Spot warm median ms | abstract
count). Include the honesty rows exactly as the report has them
(dualize vs flip+reduce; product+postprocess vs materialize+reduce kept
as separate, non-divided columns). Same refresh caveat as Figure 3.

## Placement (for theory, once delivered)

Figure 1 → §2.3 and §6; Figure 2 → §3.3; Figure 3 → §8.2; Table 1 →
§8.3. The paper carries no placeholders yet; theory adds the links when
the artifact lands.
