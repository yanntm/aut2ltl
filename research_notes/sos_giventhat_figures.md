# Figures for "Choosing the Simplest Property Given Prior Knowledge" — specification

*For a code/figure-focused session. The paper is
[`sos_giventhat.md`](sos_giventhat.md); the figure artifact is
[`sos_giventhat_figs/`](sos_giventhat_figs/) (index `figures.md`,
regeneration commands `reproduction.md`, build notes `notes.md`,
`Makefile`), modeled on [`sos_toltl_figs/`](sos_toltl_figs/). Do not edit
the paper prose. If a spec below is unbuildable as stated, report back
rather than improvising.*

## Status

| figure | subject | state |
|---|---|---|
| FIG-1 | the freedom lattice, on the worked example (paper §3 / §4.6) | specified — needs GT1 (`given_that` + `conjugacy_classes`) |
| FIG-2 | hull geometry of the worked example (paper §4.6) | specified — buildable on the calculus package alone; **build first** |
| FIG-3 | the stutter hull escapes the table (paper §5.2) | specified — needs GT3 tier 1 (`stutter_quotient`) |
| FIG-4 | campaign panels (paper §7) | pre-registered — blocked on W0 data |

Dependencies name milestones of
[`sos_giventhat_spec.md`](sos_giventhat_spec.md); coordinate with that
thread rather than duplicating its components probe-side (the drift rule
below).

## Ground rules (every figure)

- Inputs are language-canonical `.sos` invariants, bundled under
  `sos_giventhat_figs/sources/` with their regeneration commands — the
  two fixture pairs of the spec (§3.5 the stutter pair, §4 gate 5 the
  worked example), produced by `genaut/gen/canonize.py` from the DELAs
  the spec prescribes. Never an arbitrary automaton presentation.
- Every node, edge, tag and label is data produced by a probe
  (`sosl/tests/giventhat/figs/`), not drawn by hand; placement is the
  only thing a probe may hard-code. Probes are single-input, ≤ 15 s,
  long output to `sosl/tests/giventhat/logs/`.
- **The drift rule.** A probe never re-implements an engine component
  (interval construction, conjugacy partition, hulls, stutter
  congruence) — it calls the package, or the figure waits for the
  milestone that provides it. A probe-side copy can drift from the
  engine, which defeats the figure being checkable.
- Sources are TikZ, rasterized by the artifact's `Makefile`; each figure
  carries a provenance footer in `figures.md` (probe command, git rev,
  source basenames). FIG-4's campaign panels may instead use a plotting
  script (matplotlib acceptable); same provenance discipline.
- Regenerate each figure's numbers from its provenance command before
  committing.

**Drawing conventions (shared; fix them in `figures.md` and keep them
across all figures):**

- In *pair-class panels*, a node is a **conjugacy class of linked
  pairs**, labelled by its canonical lasso (shortest representative,
  `key(s)·key(e)^ω` of its least cell) with a pair-count badge (`·n`).
  Fill: **solid dark** = mandatory (class ⊆ `P_min`); **hatched** =
  forbidden (class outside `P_max`); **white** = free (the `F` classes
  of paper Prop 3.1).
- In *monoid-class panels*, a node is a table class labelled by its
  shortlex key; solid blue arrow = right-Cayley step under the first
  letter, dashed amber = under the second, black = both agree; rounded
  grey box = `R`-class (SCC of the right-Cayley graph).
- Hull contours: blue closed curve = safety closure `P̄`; green closed
  curve = interior `P̊`. Red double-shaft arrow = congruence merge.
- In *language insets*, languages are nested rounded regions; a dashed
  boundary marks an **off-table** language (one no derived table
  recognizes); single words are dots labelled by their lasso.

## FIG-1 — the freedom lattice, on the worked example (paper §3, placed near Prop 3.1; specimen from §4.6)

**Goal:** one look shows "the interval *is* `|F|` bits": every conjugacy
class of the aligned table sorted into mandatory / forbidden / free
bands, the free band being exactly the `ℒ(¬K)` classes.

- Probe: load the two §4.6 sources (`¬φ = F(a∧c) ∨ (GFb ∧ GF¬b)`,
  `K = FGb ∧ Gc`), run `given_that`, emit every conjugacy class with its
  canonical lasso, pair count, and band (mandatory / forbidden / free —
  free split is the `freedom` field, do not recompute).
- Layout: three horizontal bands (mandatory top, free middle, forbidden
  bottom), classes as convention nodes. Call out two classes with side
  tags: the endpoint witnesses `({abc})^ω` (mandatory band — the
  `k_settles` refusal) and `({bc})^ω` (forbidden band — the `k_refutes`
  refusal and the safety certificate of FIG-2).
- Caption states: `|F|` (from the probe — the paper deliberately leaves
  it uncomputed; report the value in `notes.md` too, the theory thread
  wants it), the lattice `2^F`, and that a `B` is exactly a subset of
  the middle band.
- Budget: if the aligned table yields more than ≈ 25 conjugacy classes,
  group same-band classes with identical `k`-status into a stacked
  badge (`× m`) rather than dropping any — the *count* is the message.

## FIG-2 — hull geometry of the worked example (paper §4.6) — BUILD FIRST

**Goal:** the two §4.6 decisions — safety refused, guarantee granted —
visible as containments on one drawing.

- **Left panel (pair-class plane):** the linked-pair conjugacy classes
  of the §4.6 aligned table (same probe data as FIG-1, or the calculus
  package directly: `materialize` + Boolean surgeries; the `F`
  partition is not needed here, so this panel does not wait for GT1).
  Overlay two contours: blue = `P̄_min` (safety closure of the lower
  endpoint), green = `P̊_max` (interior of the upper). The picture must
  show: `P_min` (dark) inside green — co-safety yes; blue sticking out
  past `P_max` (i.e. covering a hatched class) exactly at the class of
  `({bc})^ω` — safety no, with that node tagged as the certificate.
  Hull pair sets come from `calculus.surgery.safety_closure` /
  `interior` on the materialized product — never recomputed probe-side.
- **Right panel (language inset):** nested regions
  `L(P_min) ⊂ F(a∧c) ⊂ Fa ⊂ F(a∨¬c) ⊂ L(P_max)`, with `Fa` dashed
  (off-table) and the two solid bracket endpoints labelled as the
  canonical hulls; one dot for `({bc})^ω` outside `F(a∨¬c)` but inside
  `L(P_max)`. Every containment in the chain must be verified by the
  probe (byte-compare or `included` scans against canonized DELAs for
  `F(a∧c)`, `Fa`, `F(a∨¬c)` — the same DELAs GT2 gate 5 uses; bundle
  them in `sources/`). The `Fa`-is-off-table tag is checked by
  reducing `Fa`'s invariant and testing that no saturated pair set on
  the aligned table has its language (equivalently: `included` both
  ways against every union of freedom classes is out of budget — use
  the paper's argument instead and tag it `caption-checked`, or wait
  for GT1's `decompose` and check `decompose(Fa) = None`; say which in
  `notes.md`).

## FIG-3 — the stutter hull escapes the table (paper §5.2)

**Goal:** Theorem 5.2 at a glance — the congruence cascade flattening
the table on the left, the semantic separation it destroys on the
right.

- **Left panel (monoid-class panel):** the six classes of
  `synt({(ab)^ω})` (`[ε]`, `A_aa`, `A_ab`, `A_ba`, `A_bb`, `Z`) with
  their Cayley steps; red merge arrows numbered in cascade order
  (`A_aa → Z` first, from `λ(a)² = Z`, then `A_bb`, then the products),
  ending in a small rendering of the two-class quotient `{[ε], Z}`.
  Table and cascade from GT3's `stutter_quotient` (drift rule — this
  panel waits for GT3 tier 1); the source is the §3.5 fixture pair.
- **Right panel (language inset):** the stutter class `SC({(ab)^ω})` as
  a dashed region (off-table) containing the dots `(ab)^ω` and
  `aa(ab)^ω`, excluding `(ba)^ω` and `bb(ab)^ω`; from the two
  separated dots `aa(ab)^ω` (in) and `bb(ab)^ω` (out), arrows to a
  single shared node `(Z, Z)` — the one quotient pair both fold to,
  the separation the table cannot make. Folds and the four
  memberships probe-checked (`member` on the fixture invariants;
  stutter-class memberships by destuttered-form comparison).
- Caption carries the theorem's one-liner: the quotient test answers
  "insufficient", yet `B = SC` exists — and the two-tier resolution
  (§5.3) in one sentence.

## FIG-4 — campaign panels (paper §7; pre-registered, blocked on W0)

Specs to freeze now, build when `reference/giventhat/` lands:

- **(a) Freedom histogram:** `|F|` distribution over W0b (log-y; the
  `bits = 0` bar called out — those are the endpoint-only problems).
- **(b) Rung drops:** per source rung of `¬φ`, stacked bars of the best
  available rung given `K` (W0b) — the "simpler strength class,
  exactly" picture.
- **(c) Tier gap:** three bars — quotient-test yes / alignment-only
  yes / no (W0b) — the middle bar is Theorem 5.2 measured in the wild.
- **(d) Incremental staircases:** for a handful of W0c `(L_S, φ)`
  cases, `bits` and the per-rung existence bits vs number of facts
  integrated — monotone staircases by the §6.2 laws; any
  non-monotonicity would be a theory event, so the plotting script
  must *assert* monotonicity, not smooth it.

Read the `dataviz` conventions before building these; keep one palette
across the four panels and the TikZ figures.
