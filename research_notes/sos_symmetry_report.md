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

**How to use this file (implementer):** fill the pre-named finding
slots as the milestones close. Anything for the theory thread —
disagreements with the paper, E1 escalations of spec §8, the T2/T3
dossiers — goes in **To theory** at the bottom the moment it is found.
This file is current state, not a log: once a to-theory item is
resolved and its outcome lands in the paper or spec, it is removed
here, not archived.

## Status

**Corpus.** `flat_canon` holds **6 222** canonical cases, **2 484**
non-LTL by the `.cat` bit; by AP count 2 / 4 006 / 1 438 / 776 for
0–3 APs; stutter tags 896 invariant / 5 326 sensitive. Counts are
recomputed at run time from the corpus (`sy1_summary.md` /
`sy3_summary.md`), never hardcoded.

| milestone | state | findings |
|---|---|---|
| SY1 — signed perms, single check, kernel read-off | **DONE** (2026-07-11, gates green, campaign 6 222/6 222) | F1–F4 |
| SY2 — group, witness, symmetrization | *pending* | F5–F7 |
| SY3 — relational read-offs | **DONE** (2026-07-11, gates green, F8 oracle 6 222/6 222, campaign 6 222/6 222) | F8–F11 |
| SY4 — spectrum + hull/kernel | *pending* | F12–F14 |
| SY5 — Y-series campaigns (Y0a/Y0b/Y0c/Y1) | *pending* | F15–F16 |
| SY5/Y2 — orbit-folded extraction | *blocked on ToLTL hook* | — |

## SY1 — signed permutations, the single check, the kernel read-off

- **F1 — the worked examples behave as the paper computes.**
  *(CONFIRMED, every cell.)* Paper §9 P1–P3 on FIX_A/B/C: class
  counts **3 / 5 / 3** (and FIX_E 7); `|P|`/`|linked|` = **1/3,
  1/9, 2/4** (FIX_E 2/8) — exactly P3, `P` is half the linked pairs
  precisely on FIX_C. Full `B_n` truth tables asserted cell by cell:
  symmetric `{id, flip_b}` / `{id, swap_ab}` / `{id}`, anti `∅` /
  `∅` / `{flip_a}`, inert `{b}` / `∅` / `∅`. Two-level separation
  as predicted: `in_kernel(FIX_A, flip_b)` **True** while
  `in_kernel(FIX_B, swap_ab)` **False** with `is_symmetry` True.
  Pair-count verdicts: `anti_possible` True only on FIX_C. The
  recorded asymmetry witness for FIX_A/`flip_a` is the loop on the
  `¬a∧¬b` minterm (`(¬a¬b)^ω ∈ GF a` xor its flip image). Gate log:
  `reference/symmetry/sy1_gates.txt`; regen
  `python3 -m tests.symmetry.sigma_gate` (from `sosl/`). FIX_A
  (`GF a` over `{a, b}`) is calculus-built —
  `inverse_substitution` along `2^{a,b} → 2^{a}` then `reduce` — not
  through canonize, which sheds the free `b` (spec §3.4,
  `tests/symmetry/fixtures.py`).
- **F2 — the laws hold as runtime facts.** *(CONFIRMED, zero
  violations.)* Campaign: **69 742** candidate checks, each with the
  kernel law (`in_kernel ⟹ is_symmetry`), the obstruction law
  (`is_antisymmetry ⟹ anti_possible`) and the `|𝒞|`-preservation
  assertion of `apply_perm` — zero violations (any violation aborts
  the run; exit 0). Gates: group law + convention pin (100 seeded
  triples × n ∈ 1..5, all involutions, the `n = 2` pin equation);
  direction pin and metamorphic check exhaustive over all lassos
  `|u|,|v| ≤ 3` × all of `B_n` on each fixture (≈114 k member pairs
  per 2-AP fixture); anti/complement commutation both routes and the
  align cross-oracle on fixtures + 50 seeded corpus cases
  (seed 20260711) — all green, first run.
- **F3 — inert APs on the census.** *(MEASURED: identically zero —
  by curation, not by nature.)* Nonempty `inert_aps`: **0 / 6 222**.
  This is structural: `genaut/gen/flatten.py` minimizes the alphabet
  of every adopted case (`remove_free_aps`), so a free AP cannot
  survive into `flat_canon`. The paper §3.1 "fat kernel" expectation
  is thus *unmeasurable on this corpus* — the curation already
  harvested exactly what `inert_aps` detects (the read-off and
  `sosl.sos.minimize.free_aps` coincide). Data:
  `reference/symmetry/sy1_generators.csv` (+ `sy1_summary.md`);
  regen `sigma_gate --campaign` then `sy1_summary`.
- **F4 — generator-level symmetry hits.** *(MEASURED.)* Over 6 222
  cases: **206 (3.31 %)** have at least one symmetric generator —
  per generator (CSV naming, `t<i><j>` transposition / `f<i>` flip):
  `t01` 82, `t02` 86, `t12` 4, `f0` 36, `f1` 10. Anti-symmetric generators hit on only **8 cases (0.13 %)**,
  all polarity flips, never a transposition. `anti_possible` is True
  on **164 cases (2.64 %)**: the pair-count alone closes the anti
  question negatively on the remaining **97.36 %** of the census — a
  very sharp fast path (paper §3.2 Lemma 3.2).
  Full `B_n` sweep (all 6 222 rows have `n ≤ 3`): 5 600 rows have
  the trivial group `{id}`; the tail: 498 rows with 2 symmetric
  elements, 52 × 4, 58 × 6, 2 × 8, 8 × 12, 4 × 24 (order-24
  subgroup of `B_3`, |B_3| = 48 — SY2 material). Wall: median
  5.8 ms/case, max 4.3 s, zero budget blows.
  **Stratified by AP count** (the load-bearing view — see
  `sy1_summary.md` "Stratified"): nontrivial signed groups on
  **0.80 %** of 1-AP rows, **14.05 %** of 2-AP, **50.00 %** of 3-AP
  (622 = 10.0 % overall). Two structural reads: (i) symmetry
  prevalence grows steeply with the AP count, and 64 % of the census
  is 1-AP where `B_1 = {id, flip}` leaves almost nothing to find;
  (ii) generator screening under-detects — at `n = 2` only 38 of
  the 202 nontrivial-group rows show a generator hit, at `n = 3`
  only 136 of 388: most symmetric elements are composite (signed
  swaps, 3-cycles), which is empirical justification for SY2's full
  group computation.

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

- **F8 — the corpus stutter oracle.** *(CONFIRMED — 6 222/6 222.)*
  `stutter_rung(inv, 1)` vs the `.cat` stutter tag over all 6 222
  rows: **full agreement, zero disagreements**. The read-off's
  `invariant` count is **896**, byte-for-byte the corpus `.cat`
  stutter-tag total (896 invariant / 5 326 sensitive) — the algebraic
  equation (`∀a: [a] = [aa]`) reproduces the semantic ground truth
  exactly on the syntactic corpus (paper §4.2 / Thm 4.2 special case).
  Internal cross-check `stutter_rung(1) == classify.is_stutter_invariant`
  also green on every row. Gate log:
  `reference/symmetry/sy3_gates.txt` (gate 1); regen
  `python3 -m tests.symmetry.relations_gate --oracle` (from `sosl/`).
- **F9 — invisible letters on the census.** *(MEASURED: identically
  zero — structural, like F3.)* Nonempty `invisible_letters`:
  **0 / 6 222**. An invisible letter is a **class** equality
  `[c] = 1`; an inert AP (F3) is a **fiber** equality `λ∘flip = λ` —
  distinct read-offs (trap #8), and both empty on this corpus. The
  alphabet-minimal, canonized corpus carries no padding letter, so
  the census cannot exercise the ≠-side on fixtures; the fixture gate
  asserts `invisible_letters` empty on FIX_A/B/C and the census
  frequency (0) is the F9 datum. Data:
  `reference/symmetry/sy3_summary.md` (F9); regen
  `relations_gate --campaign` then `sy3_summary`.
- **F10 — `Î_L` density.** *(MEASURED — steeply AP-stratified.)*
  Density = fraction of ordered distinct class pairs with
  `[cd] = [dc]`. Overall mean **0.192**; **4 318 (69.4 %)** cases are
  fully rigid (`Î_L = ∅`, tolerate no commuting), **744 (11.96 %)**
  fully commutative (density 1), 1 160 partial. Stratified mean
  density: **0.014** (1-AP), **0.377** (2-AP), **0.771** (3-AP) — a
  specification tolerates more adjacent swaps as its alphabet widens
  (the paper §4.3 POR datum: "how much commuting do real specs
  tolerate"). Data + strata table: `sy3_summary.md` (F10).
- **F11 — the `k`-ladder entry.** *(MEASURED — the `{1,2,3,None}`
  spread is populated.)* `ladder_entry` = least rung `k ≤ 3` with
  `stutter_rung(k)` (`[v] = [vv]` for all length-`k` class-words):
  **1 → 896, 2 → 736, 3 → 326, None → 4 264**. The `k=1` bucket (896)
  is exactly the stutter-invariant set (rung 1 is stutter); rungs 2–3
  add **1 062 cases that are block-stutter at a deeper window but not
  letter-stutter** — the "new canonical parameter" of paper §4.2 is
  non-trivially populated, not vacuous. The rung tests length-`= k`
  blocks (not `≤ k`) — the reading that makes the entry a genuine
  parameter; the one pending theory ask (below) is that prose fix. By
  AP the deep rungs concentrate in 1-AP counting languages (594 at
  k=2, 326 at k=3). Data: `sy3_summary.md` (F11).

## SY4 — the spectrum and the LTL hull/kernel

- **F12 — the corpus LTL-bit oracle.** *(pending — run FIRST)*
  `spec == ∅` iff the `.cat` LTL bit, over all 6 222: agreement
  counts; any disagreement is a to-theory event, smallest case verbatim.
- **F13 — the spectrum census.** *(pending)* Spectrum values over the
  2 484 non-LTL rows (expected overwhelmingly `{Z/2}`),
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

**Open ask (one).**

1. **The `k`-block ladder rung is length `= k`, not `≤ k` — a
   one-word prose fix in paper §4.2 and spec §5.** Both currently
   write the rung as "`[v] = [vv]` for all `|v| ≤ k`", which is
   internally inconsistent with the same passage and the fixture gate:
   the `≤ k` reading is nested, so `ladder_entry` (least satisfying
   rung) can only be 1 or `None` — never the 2/3 the F11 distribution
   names; it contradicts the paper's own per-rung count "`|Σ_λ|^k`
   equations" (that is the length-**exactly**-`k` count); and under
   `≤ k` the gate's `ladder_entry(FIX_A) == 1` is trivially true for
   every stutter language. The length-`= k` reading — rungs do not
   nest, `ladder_entry ∈ {1,2,3,None}` — is what every concrete
   artifact agrees on; it is implemented (`relations.py`) and yields
   the F11 spread 896 / 736 / 326 / 4 264. **Requested:** change
   "`|v| ≤ k`" to "`|v| = k`" in paper §4.2 and spec §5; no math
   moves (`k=1` is still stutter, Thm 4.2 unaffected).

**Standing items — open data/answers the theory thread expects.**

- **Spec/paper disagreements** (spec §8 E1 escalations): smallest case
  verbatim. The paper's P1–P5 hand computations are predictions under
  test; a stable mismatch after the E1 ladder is a paper-arithmetic
  correction theory owns.
- **F12 — the LTL-bit oracle** (needs SY4): `spec == ∅` iff the `.cat`
  LTL bit over all 6 222, confirmed or the smallest disagreeing case
  (the §6 twin of the F8 oracle, now confirmed).
- **F13 — a nonabelian/non-solvable spectrum specimen** (needs SY4): a
  headline find — the paper's §6.1 gains a concrete witness outside
  `FO+MOD`. File the moment it appears.
- **F14 — the leastness probe** (needs SY4): it gates the
  `aperiodic_reflection` implementation of the proved Lemma 6.2a; a
  strictly-between aperiodic congruence is a bug dossier (convicts the
  implementation, not the math), filed verbatim.
- **F5 / F7 — group-size and orbit-price numbers** (need SY2): feed
  the paper §9 stratified expectations and decide whether spec §4's
  stabilizer-search stretch is commissioned (the `n = 5` skip tier).
