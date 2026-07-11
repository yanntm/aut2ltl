# Figures for "Symmetries on the Syntactic ω-Semigroup" — specification

*For a code/figure-focused session. The paper is
[`sos_symmetry.md`](sos_symmetry.md); the figure artifact is
`sos_symmetry_figs/` (index `figures.md`, regeneration commands
`reproduction.md`, build notes `notes.md`) — create it on first build.
Do not edit the paper prose. If a spec below is unbuildable as stated,
report back rather than improvising.*

## Status

| figure | subject | state |
|---|---|---|
| FIG-1 | the two-level structure: kernel vs `Aut` (Examples A and B) | specified — ready to build (data needs only canonize + a table dump) |
| FIG-2 | `EvenHead`: spectrum, reflection, hull/kernel/gap (Prop 6.2) | specified — ready to build (same toolchain) |
| FIG-3 | the symmetric envelope (§7.4) | specified — conceptual schema, buildable now |

## Ground rules (every figure)

- Inputs are language-canonical `.sos` invariants, produced by
  `genaut/gen/canonize.py` from the fixture DELAs of
  `sos_symmetry_spec.md` §3.4/§6.3 (FIX_A/FIX_B/FIX_E); bundle the
  sources under `sos_symmetry_figs/sources/`.
- Every node, edge, tag and label of FIG-1/FIG-2 is data produced by a
  probe (place probes in `sosl/tests/symmetry/figs/`, single-input,
  ≤ 15 s, long output to logs), not drawn by hand; placement is the
  only thing a probe may hard-code. FIG-3 is the sanctioned exception:
  it is a schema of §7.4's objects and arrows, with no data content —
  say so in its caption.
- Sources are TikZ, rasterized by the artifact's `Makefile`; each
  figure carries a provenance footer in `figures.md`; regenerate each
  figure's numbers from its provenance command before committing.
- Drawing conventions shared with `sos_toltl_figs/figures.md`: solid
  blue = Cayley step under `a`; dashed amber = under `¬a`; black =
  both letters agree. New conventions for this paper (record them in
  `figures.md`): green double arrow = a signed permutation's action;
  red cross on a cell = the multiplicativity failure of a candidate;
  hatched region = a gap language.
- The paper's §9 P1–P5 values are the acceptance oracle: any number a
  probe produces that contradicts them is a finding to report (spec
  §8/E1 discipline), never something to draw around.

## FIG-1 — kernel vs `Aut`: the two-level structure (paper §3.1, beside Examples A/B)

**Goal:** one look separates the two levels of Theorem 3.1 — a
symmetry the letter map absorbs (kernel) vs a symmetry that lives in
the table (`Aut`).

Two panels over the 2-AP minterm square (vertices `ab, a¬b, ¬ab,
¬a¬b`):

1. **Left — Example A (`GFa`), the kernel.** The square colored by
   `λ`-fiber (two fat fibers: the `a`-face ↦ `F`, the `¬a`-face ↦
   `N`); the flip `σ_b` drawn as green double arrows moving *within*
   each fiber (tag: `λ∘σ_b = λ` — in `K`, read-off); the flip `σ_a`
   drawn crossing fibers (tag: candidate must go to the table — and
   there it fails, `ρ(P) ≠ P`).
2. **Right — Example B (`GFa ∧ GFb`), the automorphism.** The square
   with `λ` injective (four singleton fibers, each its own class);
   next to it the 5-class multiplication table (or its Cayley view —
   pick the more readable, report which); the swap's `ρ = (A B)`
   drawn as green double arrows on the table with `P = {(C,C)}`
   fixed; the flip `σ_a`'s forced images drawn up to the cell
   `ρ(A·B) ≠ ρ(A)·ρ(B)`, red-crossed (tag: dies on one cell, no
   keying pass).

Probe data: classes, `λ`, `M`, `P` dumped from the canonized `.sos`
of FIX_A and FIX_B; the candidate images computed by the probe from
the `SignedPerm` action (or, before SY1 lands, by ten lines of probe
arithmetic on minterm bitvectors — do not wait on the package).

## FIG-2 — `EvenHead`: the counting content confined to the gap (paper §6.2, Prop 6.2)

**Goal:** the whole of §6 in one figure — where the group sits, what
the reflection collapses, and what the hull/kernel sandwich decides.

Three aligned panels, left to right:

1. **The table.** Right-Cayley graph of the 7 classes of FIX_E
   (`1, A₁, A₀, B, C₀, C₁, D`; solid blue = step under `a`, dashed
   amber = under `b`); the maximal subgroup `{A₀, A₁}` boxed and
   tagged `Z/2` (this is `Spec(L)`); accepting pairs `P = {(B,B),
   (C₀,B)}` marked (double circle on the stems, or a pair list —
   report which reads better at this size).
2. **The reflection.** The 5-class quotient after collapsing
   `A₀ ∼ A₁` (which drags `C₀ ∼ C₁`); a wide arrow between panels
   tagged "collapse `Z/2`, one round"; the two saturations `P♯`,
   `P♭` listed under it.
3. **The languages.** Three nested regions: `L♯ = a^*·b^ω` (outer),
   `L = a^{2n}·b^ω`, `L♭ = {b^ω}` (inner); the gap `a^+·b^ω`
   hatched; the witness family `a·b^ω, a²·b^ω, a³·b^ω, …` drawn as
   dots alternating in/out of `L` inside the hatched region — the
   caption line is Prop 6.2's: on the gap, and only there, `L` is
   decided by counting.

Probe data: panels 1–2 from the canonized FIX_E `.sos` (classes,
`M`, `P`) and the collapse computed by the probe (union-find over
the one merge, then congruence closure — ~20 lines; assert 5 classes
and the two forced merges, per §9 P5); panel 3's dots from `member`
folds (or the same fold arithmetic inline).

## FIG-3 — the symmetric envelope (paper §7.4)

**Goal:** the schema of Proposition 7.4 — a reader sees in one look
that soundness never needs symmetry, and where the two gaps sit.

A 2×3 lattice of boxes: top row `M∩ ⊆ M ⊆ M∪`, bottom row
`L∩ ⊆ L ⊆ L∪`, the four envelope corners tagged `G`-invariant (the
middle column, the real problem, not); two highlighted check arrows:
`M∪/G ⊨ L∩` (tag: proof, both sides quotiented) and `M∩/G ⊭ L∪`
(tag: refutation, counterexample lifts); the two gaps `M∪ ∖ M∩` and
`L∪ ∖ L∩` hatched with a shared tag "completeness lost here — width
shrinks as `G` shrinks, `G = 1` exact"; a small subgroup-chain
ladder on the side (`B_AP ⊃ … ⊃ G ⊃ … ⊃ 1`) with the refinement
arrow tagged "witness names the generator to drop (§3.3)".

No data content — hand layout permitted (the ground-rule exception);
keep every tag verbatim from §7.4's vocabulary so the figure and the
prose cannot drift apart.
