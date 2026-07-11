# Symmetries on the Syntactic ω-Semigroup — results

The answer to `research_notes/sos_symmetry_spec.md` (milestones
SY1–SY5): the `sosl.sos.symmetry` package measured against its gates,
the paper's hand-worked predictions (paper §9, P1–P5), and the
Y-series census campaigns. Each finding `Fn` below is a checked
prediction (or a flagged open point) of the paper
`research_notes/sos_symmetry.md`; the paper states results in pure
form and cites no artifact — this report ties every claim to a
regenerable machine report under `reference/symmetry/` or a gate log
under `sosl/tests/symmetry/logs/` (date / git-rev / seed / corpus
header, regen command per finding).

**How to use this file (implementer):** fill the pre-named slots as
the milestones close; never renumber; a slot that dies gets a one-line
epitaph, not deletion. Anything that belongs to the theory thread —
disagreements with the paper, E1 escalations of spec §8, the T2/T3
dossiers — goes in **To theory** at the bottom, the moment it is
found, even mid-milestone.

## Status

| milestone | state | findings |
|---|---|---|
| SY1 — signed perms, single check, kernel read-off | *pending* | F1–F4 |
| SY2 — group, witness, symmetrization | *pending* | F5–F7 |
| SY3 — relational read-offs | *pending* | F8–F11 |
| SY4 — spectrum + hull/kernel | *pending* | F12–F14 |
| SY5 — Y-series campaigns (Y0a/Y0b/Y0c/Y1) | *pending* | F15–F16 |
| SY5/Y2 — orbit-folded extraction | *blocked on ToLTL hook* | — |

## SY1 — signed permutations, the single check, the kernel read-off

- **F1 — the worked examples behave as the paper computes.**
  *(pending)* Paper §9 P1–P3 on FIX_A/B/C: class counts (3 / 5 / 3),
  the full `B_n` truth tables (every cell), the two-level separation
  (`in_kernel(FIX_A, flip_b)` True vs `in_kernel(FIX_B, swap_ab)`
  False with the symmetry still holding), the pair-count obstruction
  verdicts. Record `|P|` / `|linked|` per fixture as data.
- **F2 — the laws hold as runtime facts.** *(pending)* Kernel law
  (`in_kernel ⟹ is_symmetry`), `|𝒞|` preservation under
  `apply_perm`, the direction-pin and metamorphic gates, the
  anti/complement commutation: case counts, zero violations expected.
- **F3 — inert APs on the census.** *(pending)* Over 3 938 cases:
  share of cases with a nonempty `inert_aps`, distribution of
  `|inert|` by AP count — the paper §3.1 "fat kernel" expectation
  and the corpus-curation anecdote, quantified. Path:
  `logs/sy1_generators.csv`.
- **F4 — generator-level symmetry hits.** *(pending)* Frequency of
  symmetric transpositions / flips and of anti-symmetric generators
  over the census; the `anti_possible` fast-path hit rate (how often
  the count alone closes the anti question — a paper §3.2 talking
  point).

## SY2 — the group, the witness, symmetrization

- **F5 — `Sym±` group sizes.** *(pending)* Order distribution of
  `Sym_AP` and the anti coset over the sampled cases; the `n = 5`
  skip rate (decides whether the stabilizer-search stretch is
  commissioned); fixture groups as predicted.
- **F6 — asymmetry witnesses replay.** *(pending)* Every witness a
  member of exactly one side, minimality per the discipline scan;
  the FIX_A/`flip_a` witness recorded.
- **F7 — the orbit price of symmetrization.** *(pending)* Orbit-size
  distribution, cap-16 hit count — the paper §3.4 claims an orbit
  price, not a group-order price; this slot is its evidence.

## SY3 — relational read-offs

- **F8 — the corpus stutter oracle.** *(pending — run FIRST)*
  `stutter_rung(·, 1)` vs the `.cat` stutter tag over 3 938:
  agreement counts; any disagreement escalates to To theory with the
  smallest case.
- **F9 — invisible letters on the census.** *(pending)* Frequency of
  `[c] = 1` letters; contrast with F3 (invisible ≠ inert — state
  both numbers side by side).
- **F10 — `Î_L` density.** *(pending)* Distribution of the tolerated
  independence relation's density over the census; the paper §4.3
  POR pitch cites this ("how much commuting do real specs
  tolerate").
- **F11 — the `k`-ladder entry.** *(pending)* `ladder_entry`
  distribution (`1 / 2 / 3 / None`) — the paper §4.2 new-parameter
  claim, census-shaped.

## SY4 — the spectrum and the LTL hull/kernel

- **F12 — the corpus LTL-bit oracle.** *(pending — run FIRST)*
  `spec == ∅` iff the `.cat` LTL bit, over 3 938: agreement counts;
  any disagreement is a to-theory event, smallest case verbatim.
- **F13 — the spectrum census.** *(pending)* Spectrum values over the
  1 698 non-LTL rows (expected overwhelmingly `{Z/2}`),
  cross-tabulated with Wagner coordinates; FIX_E and `EvenBlocks`
  sanity; **any nonabelian or non-solvable specimen is a headline
  find — file immediately**; composition-factor cap (order > 512)
  skips, if any.
- **F14 — the reflection, hull and kernel.** *(pending)* Paper §9 P5
  on FIX_E: 5-class reflection in one round, hull/kernel byte-equal
  to the canonized `FG¬a ∧ G(¬a → G¬a)` / `G¬a`, gap membership
  alternating with parity for `n ≤ 6`. Corpus: LTL rows collapse to
  identity (must be 100%), `|𝒞/θ|` vs `|𝒞|` columns, reflection
  iteration counts, and the leastness probe (spec §6 gate 5) — a
  strictly-between aperiodic congruence, if ever found, goes to To
  theory verbatim.

## SY5 — the Y-series campaigns

- **F15 — the Y0 census columns.** *(pending)* Y0a (`Sym±`, kernel
  share), Y0b (spectrum column), Y0c (gap column) as
  `reference/symmetry/y0_*.md` + `.csv`; the three columns the paper
  §9 measurement plan promises, with wall times and skip rates.
- **F16 — orbit deduplication (Y1).** *(pending)* The `B_AP`-orbit
  dedup map and shrink factor on `n ≤ 4` rows — the paper §9
  deduplication axis; sharpens the census "exhaustive below the
  wall" claim by the reported factor.
- **Y2** — blocked on the ToLTL engine hook and the paper §5
  renderer-equivariance ⟨TBD⟩; no findings until the theory thread
  unblocks it.

## To theory

*(empty — populate the moment anything below occurs)*

Standing items the theory thread expects data or answers on:

1. Any disagreement between the spec and the paper (spec §8 E1
   escalations included) — smallest case, verbatim. The paper's
   hand computations (P1–P5) are predictions under test: a stable
   mismatch after the E1 escalation ladder means the paper's
   arithmetic gets corrected, and theory owns that edit.
2. The stutter-oracle verdict (F8) and the LTL-bit-oracle verdict
   (F12): confirmed or the smallest disagreeing case.
3. The leastness probe (F14): any strictly-between aperiodic
   congruence falsifies the reflection-as-`θ_ap` reading of paper
   §6.2 — the dossier decides how Prop 6.4's proof gets written.
4. Kernel fatness and group-size numbers (F3, F5) — feed the paper
   §9 expectations ("large kernels, small semantic groups"); if the
   corpus says otherwise, §3.1's third remark gets rewritten.
5. The `anti_possible` hit rate (F4) — decides whether the
   pair-count obstruction is a remark or a highlighted lemma.
6. Any nonabelian/non-solvable spectrum specimen (F13) — a find; the
   paper's §6.1 discussion would gain a concrete witness outside
   `FO+MOD`.
7. The orbit-price evidence (F7) and the tier of `n = 5` skips (F5)
   — decide whether the stabilizer-search stretch of spec §4 is
   commissioned.
