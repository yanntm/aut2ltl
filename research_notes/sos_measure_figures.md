# Figures for "Measure, Distance, and Entropy on the Syntactic ω-Semigroup" — specification

*For a code/figure-focused session. The paper is
[`sos_measure.md`](sos_measure.md); the figure artifact is
`sos_measure_figs/` (index `figures.md`, regeneration commands
`reproduction.md`, build notes `notes.md` — create the directory on the
toltl model, `sos_toltl_figs/`). Do not edit the paper prose. If a spec
below is unbuildable as stated, report back rather than improvising.*

## Status

| figure | subject | state |
|---|---|---|
| FIG-1 | the worked read-off: chain, θ, absorption for "first `b` at even position" | **buildable now** (M1 engine) |
| FIG-2 | the doubled-word cut, run on a sampled word | **buildable now** (M1 componentry + small probe) |
| FIG-3 | the kernel group and the phase contrast | **buildable now** (M1 componentry) |
| FIG-4 | the null-class tower: `L → sh(L) → ess(L)` on the warning pair | blocked on M3 (`shadow`/`essential`) |
| FIG-5 | census data: measure per Wagner degree, entropy per degree, quotient distance heatmap | blocked on M4/M6 (E1–E3) |

## Ground rules (every figure)

- Inputs are language-canonical `.sos` invariants, bundled under
  `sos_measure_figs/sources/` — the M1/M3 fixture languages (spec
  `sos_measure_spec.md` §4, §9), never an arbitrary presentation.
- Every node, edge, tag, number and probability is data produced by a
  probe under `tests/quant/figs/` (single-input argv, ≤ 15 s, long
  output to `tests/quant/logs/`), not drawn by hand; placement is the
  only thing a probe may hard-code. Sources are TikZ, rasterized by the
  artifact's `Makefile`; each figure carries a provenance footer in
  `figures.md`.
- Exact values stay exact: probabilities and `x`-values render as
  fractions (`2/3`), never decimals.
- Drawing conventions (fix once in `figures.md`, reuse): solid blue =
  Cayley step under `a`; dashed amber = under `b`; rounded grey box =
  SCC; double circle = class in a bottom SCC; thick border = kernel
  element; green/red corner tag = `θ = 1` / `θ = 0`; node annotation
  below = its `x`-value.

## FIG-1 — the worked read-off, end to end (paper §4.1, Example)

**Goal:** the entire §4.1 algorithm visible in one picture, on the
paper's own example (fixture F-E, "`b` occurs and the first `b` is at
an even position").

Draw the right-Cayley graph of the 5-class invariant: `[ε]`, the
transient SCC `{A₀, A₁}` (one grey box; the `a`-edges exchanging them,
the `b`-exits), the two bottom SCCs `{F₀}`, `{F₁}` (double circles,
self-loops on both letters). Tags: `θ = 1` on `F₀`, `θ = 0` on `F₁`;
thick borders on `F₀, F₁` (the kernel spans both bottom SCCs — the
caption's point). Under each node its `x`-value at uniform: `2/3`
(`[ε]`), `2/3` (`A₀`), `1/3` (`A₁`), `1` (`F₀`), `0` (`F₁`); result
line `μ = x_[ε] = 2/3` beneath. All values from a probe invoking the
M1 engine on the fixture (`theta_profile`, `measure`, and the kernel
routine for the thick borders); the probe prints exactly the tuple the
drawing consumes.

## FIG-2 — the doubled-word cut (paper §3.1, Lemma 3.1)

**Goal:** the proof's mechanism on one concrete random word — a reader
who follows the picture has re-run the proof.

Setting: the §3.4 example language ("some `a` at infinitely many even
positions"), whose kernel idempotent is `k = fold(aa)` and
`H(k) ≅ ℤ/2`, so every fold in `H(k)` renders as a parity — the one
case where the group is drawable. The probe: seed-fixed, sample one
word prefix (uniform letters, length ~60, seed in the provenance
footer); locate the disjoint aligned occurrences of `w·w = aaaa`; emit
the midpoint cut positions, each inter-cut block, its fold's parity
(the `H(k)` value), the cumulative parities, and the recurring value
`g` with the selected `J`-cuts.

Draw the word as a ruler: letters in a monospace strip; `aaaa`
occurrences highlighted; midpoint cuts as vertical bars; under each
inter-cut block its `H(k)`-parity; a second row of cumulative
parities with the recurring value's occurrences circled — those are
the `J`-cuts — and a final row bracketing the inter-`J` blocks, each
tagged `fold = k`. Left of the first cut, the stem bracket tagged
`fold(y) ∈ Stems(c, k)`. If length 60 under the seed yields fewer
than three `J`-cuts, increase the length at the probe (report the
value used), not the drawing.

## FIG-3 — the kernel group and the phase contrast (paper §3.4, Example)

**Goal:** why only the kernel forgets phases — the paper example's two
halves side by side.

Left panel: the right-Cayley graph of the 9-class invariant (classes
`(r, E)` plus `[ε]`), SCC boxes, the unique bottom SCC
`K = {(0,{0,1}), (1,{0,1})}` double-circled and thick-bordered, tagged
`≅ ℤ/2` and `θ = 1`. Right panel: two verdict rows, all entries
probe-computed via `Val`: the non-kernel idempotent `e' = fold(ba)`
against stems `fold(b)` and `fold(bb)` — verdicts `1` and `0`,
annotated "`R`-equivalent stems, split verdict"; the kernel loop `k =
fold(aa)` against the same stems — verdicts `1` and `1`, annotated
with the re-bracketing `u·(aa)^ω = (u·a)·(aa)^ω`. Lasso names
(`b·(ba)^ω ∈ L`, `bb·(ba)^ω ∉ L`) under the `e'` row.

## FIG-4 — the null-class tower (paper §4.2) — BLOCKED on M3

**Goal:** the three objects and what each decides, instantiated on the
warning pair.

A two-column tower: left column `L₁ = Σ*·b·Σ^ω`, right column
`L₂ = Σ^ω`; three rows: the reduced invariants (byte-different), their
shadows (byte-different — annotated "sufficient only"), their
essential forms (byte-EQUAL — annotated "complete: `d_p = 0`"). Each
cell shows the invariant's class count and key fingerprint as emitted
by the M3 probe (`shadow`, `essential`, `reduce`); arrows down the
columns labeled `sh` and `ess`; a bracket joining the bottom row
labeled with the byte-equality verdict. Build only once M3's F-G/F-H
fixtures are green; the probe must consume the same fixture files.

## FIG-5 — census data figures — BLOCKED on M4/M6

Three data figures, one per E-campaign, each generated from the
`reference/quant/` CSVs (never recomputed at draw time; the CSV is the
provenance):

- **5a (E1):** distribution of `μ` at uniform per Wagner degree —
  strip/violin per degree with the `{0, 1}` masses shown apart from
  the interior values; the F-M1 counts (μ-0 / μ-1 / interior) as a
  headline annotation.
- **5b (E2):** entropy `h` against class count `n`, colored by Wagner
  degree; the `h = log₂|Σ|` ceiling drawn per alphabet slice.
- **5c (E3):** the exact quotient distance matrix for the largest
  alphabet slice, heatmap over `ess`-class representatives ordered by
  a single-linkage clustering; LTL-definable representatives marked on
  the axes (the nearest-LTL-neighbor question read directly off the
  picture).

Numbers, bins and orderings all from the CSVs; captions cite the
generating experiment id and git-rev, matching the report's
regeneration commands.
