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

**Corpus note (2026-07-11).** The corpus was regenerated and extended
between the spec's writing and SY1's run: `flat_canon` now holds
**6 222** cases (spec text says 3 938), of which **2 484** are
non-LTL by the `.cat` bit (spec says 1 698); by AP count: 2 zero-AP,
4 006 one-AP, 1 438 two-AP, 776 three-AP; stutter tags 896 invariant
/ 5 326 sensitive. All counts from
`reference/symmetry/sy1_summary.md` — SY1 data is produced on the
current corpus, counts recomputed, never hardcoded.

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
  `python3 -m tests.symmetry.sigma_gate` (from `sosl/`).
  **Deviation from spec §3.4, FIX_A build:** the entire canonize
  pipeline sheds free APs (spot label simplification +
  `remove_free_aps`; `flat_canon` is alphabet-minimal by
  construction), so *no* hand HOA can carry the unused `b` through
  `genaut/gen/canonize.py`. FIX_A over `{a, b}` is instead produced
  in the calculus: `inverse_substitution` along the projection
  `2^{a,b} → 2^{a}` of the canonized 1-AP `GF a`, then `reduce` —
  same language, same 3 classes, `b` free by construction
  (`tests/symmetry/fixtures.py`). Escalated below.
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
  `sosl.sos.minimize.free_aps` coincide). Escalated below. Data:
  `reference/symmetry/sy1_generators.csv` (+ `sy1_summary.md`);
  regen `sigma_gate --campaign` then `sy1_summary`.
- **F4 — generator-level symmetry hits.** *(MEASURED.)* Over 6 222
  cases: **206 (3.31 %)** have at least one symmetric generator —
  per generator (CSV naming, `t<i><j>` transposition / `f<i>` flip):
  `t01` 82, `t02` 86, `t12` 4, `f0` 36, `f1` 10. Anti-symmetric generators hit on only **8 cases (0.13 %)**,
  all polarity flips, never a transposition. `anti_possible` is True
  on **164 cases (2.64 %)**: the pair-count alone closes the anti
  question negatively on the remaining **97.36 %** of the census — a
  very sharp fast path (paper §3.2 talking point; see To theory).
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
  group computation. Escalated below (measurement-design question).

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
  non-trivially populated, not vacuous. The `= k` (not `≤ k`) reading
  of the rung is what makes this a genuine parameter; see To-theory
  item 5 (a spec/paper prose fix, not a semantic surprise). By AP the
  deep rungs concentrate in 1-AP counting languages (594 at k=2, 326
  at k=3). Data: `sy3_summary.md` (F11).

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

1. **[2026-07-11, SY1] Corpus renumbering.** `flat_canon` is now
   6 222 cases (2 484 non-LTL) after regeneration + adoption of the
   parity sampling campaign; every "3 938" / "1 698" in the spec and
   the paper's §9 measurement plan is stale. No semantic impact on
   SY1 (counts were recomputed), but the paper's census-shaped
   claims should quote the new totals once they cite this report.

   **Theory response (2026-07-11).** Swept. Spec: §0 corpus block
   now states 6 222 / 2 484 with the AP breakdown and a
   recount-at-run-time rule, plus the two structural facts every
   milestone must respect (alphabet-minimality, 1-AP skew); all
   SY1/SY3/SY4/SY5 occurrences updated. Paper: §9 `Spec` bullet
   now 2 484. One further stale number found in the sweep: the
   paper §3.1 cost remark quoted `|𝒞| ≤ 121` (old corpus); the max
   `n_classes` over `reference/symmetry/sy1_generators.csv` is
   **208**, paper updated — engineering: countersign by adding
   max `|𝒞|` to `sy1_summary.md` at the next regen.
2. **[2026-07-11, SY1] F3 is structurally zero — spec §3.4/F3 and
   the paper §3.1 "fat kernel" expectation need a decision.** The
   corpus pipeline alphabet-minimizes every case (`remove_free_aps`
   in `flatten.py`), and the minimizer's free-AP test *is* the
   `inert_aps` read-off, so nonempty `inert_aps` is impossible on
   `flat_canon` by construction: 0/6 222 measured. The
   corpus-curation anecdote is thereby *confirmed at the pipeline
   level* (the curation harvests exactly the kernel flips) but the
   census cannot quantify kernel fatness. Options we see: (a) state
   the coincidence-of-read-offs as the finding itself (the paper's
   Example A is what the curation automates), (b) commission a
   measurement on the *pre-minimization* corpus tiers, or (c) drop
   the census-shaped version of the claim. Related deviation: FIX_A
   over `{a, b}` cannot be built through canonize.py (it sheds `b`);
   we build it by calculus alphabet-extension + reduce (F1) —
   suggest spec §3.4 be edited to that construction.

   **Theory response (2026-07-11).** Decision: **(a)** — the
   coincidence of the read-offs is the finding, and the paper now
   says so: §3.1 Example A states that the curation *is* Example A
   run at scale (inert propositions structurally absent, 0/6 222),
   and that kernel fatness lives upstream of any curated corpus, in
   raw specifications as users write them; the §9 `Sym±` bullet no
   longer expects kernel measurements from the census. Option (b)
   (pre-minimization tiers) is NOT commissioned — it measures the
   corpus generator's habits, not verification practice, so the
   number would not support the paper's claim anyway; it stays
   available if a referee asks. Spec edited as you suggest: §3.4
   FIX_A is now the calculus construction verbatim (your F1 build),
   trap #7 rewritten to match, SY1 acceptance and Y0a now say
   assert-zero, not measure.
3. **[2026-07-11, SY1] The pair-count obstruction is sharper than a
   remark.** `anti_possible` is False on 97.36 % of the census, so
   the count alone refutes *all* anti-candidates nearly everywhere
   (and the 8 realized anti hits are all polarity flips). Item 5 of
   the standing list: on this evidence the obstruction deserves the
   highlighted-lemma treatment in §3.2.

   **Theory response (2026-07-11).** Promoted: it is now **Lemma
   3.2 (the pair-count obstruction)** in paper §3.2, with a
   three-line proof (the witnessing automorphism permutes the
   linked pairs and carries `P` onto its complement) and the census
   sharpness stated in prose (97.36 % closed by the count; every
   realized anti-symmetry a polarity flip). The §1.3 contribution
   bullet and §9 P3 now cite it by number. Standing item 5 is
   resolved.
4. **[2026-07-11, SY1] The census is too 1-AP-heavy for the paper's
   symmetry claims — larger AP sets needed (measurement design,
   theory owns).** 64 % of `flat_canon` is 1-AP, where
   `B_1 = {id, flip}` makes the symmetry question nearly vacuous
   (0.80 % nontrivial); prevalence climbs to 14.05 % at 2 APs and
   **50 %** at 3 APs (stratified table in `sy1_summary.md`). The
   group-spectrum, `Sym±`-distribution and orbit-dedup measurements
   (SY2/SY4/SY5, paper §9) will be shaped by this skew. Options:
   (a) commission the corpus thread to *sample* 4-AP (and heavier
   3-AP) shapes on the cluster — exhaustive enumeration at 4 APs is
   out of reach, and note random sampling may find symmetry rare;
   (b) manufacture ground-truth cases by symmetrization (§3.4 /
   SY2): `⋂_{σ∈G} σ(L)` over corpus seeds is `G`-invariant *by
   construction* at any `n`, giving a stress set with known groups;
   (c) keep the census as-is but state all census-shaped claims
   stratified by AP count, never pooled. We recommend (b) + (c)
   now (no new corpus dependency, SY2 builds symmetrization anyway)
   with (a) as the follow-up campaign. Related F4 datum: most
   symmetric elements are composite (generator screening finds 35 %
   of nontrivial groups at `n = 3`), so any larger-`n` campaign
   should budget for group search, not generator scans.

   **Theory response (2026-07-11).** Adopted: **(b) + (c)** now,
   **(a)** as the follow-up, exactly as recommended. Concretely:
   (c) — the stratified-by-AP mandate is now spec §0 structural
   fact (ii), binding on Y0a and every census-shaped table; paper
   §9's `Sym±` bullet states the stratified baseline (0.80 / 14.05
   / 50 %) and why pooled rates are mix artifacts. (b) — a new
   campaign **Y0s (symmetrized ground truth)** is spec'd in §7:
   150 seeded rows per arity `n ∈ {2, 3}`, planted groups chosen so
   composite elements are represented (`⟨t01∘f0⟩` order-4 signed
   swap at `n = 2`; S₃ and the 3-cycle `⟨(012)⟩` at `n = 3` — your
   F4 under-detection point), degenerate collapses counted and
   dropped, `G ≤ Sym±(L')` asserted elementwise with strict
   containment recorded as data, orbit prices fed to F7. The paper
   §9 gains a matching "symmetrized ground truth" bullet with the
   lower-bound caveat stated. (a) — the sampled 4-AP corpus
   campaign is named in the spec as the follow-up, explicitly NOT
   part of SY5; we will commission it to the corpus thread once
   Y0s bounds expectations.

5. **[2026-07-11, SY3] The `k`-block ladder rung reads `= k`, not
   `≤ k` — a prose fix in spec §5 and paper §4.2.** Both write the
   rung as "`[v] = [vv]` for all `|v| ≤ k`", but that phrasing is
   internally inconsistent with the rest of the same passage and with
   the fixture gate:
   - It is **nested** (a larger `k` is a strictly stronger
     requirement), so `ladder_entry` = "least `k` with `stutter_rung`"
     can only ever be **1 or `None`** — never the 2/3 the F11
     distribution table names, making the "new canonical parameter"
     vacuous.
   - It contradicts the paper's own per-rung count "**each rung is
     `|Σ_λ|^k` table equations**" (that count is the number of
     length-**exactly**-`k` class-words; `≤ k` would be
     `Σ_{j≤k}|Σ_λ|^j`).
   - It contradicts spec §5 gate 3's expectation
     `ladder_entry(FIX_A) == 1` only being informative under a
     non-nested reading (under `≤ k`, *every* stutter language is 1
     trivially).

   The reading every concrete artifact agrees on is **length
   `= k`**: rung `k` tests `[v] = [vv]` for class-words of length
   exactly `k`, the rungs do **not** nest, and `ladder_entry` (least
   satisfying rung) ranges over `{1, 2, 3, None}`. Implemented that
   way (`relations.py`, `algorithm.md`), and it yields the F11 spread
   896 / 736 / 326 / 4 264 with the `k=1` bucket coinciding with the
   stutter set as required. **Requested:** theory change "`|v| ≤ k`"
   to "`|v| = k`" in paper §4.2 and spec §5 (one word each); no
   downstream math moves — `k=1` is still stutter, Thm 4.2 is
   unaffected. Flagged rather than silently reconciled per the report
   contract, though the evidence is one-sided.

Standing items the theory thread expects data or answers on:

1. Any disagreement between the spec and the paper (spec §8 E1
   escalations included) — smallest case, verbatim. The paper's
   hand computations (P1–P5) are predictions under test: a stable
   mismatch after the E1 escalation ladder means the paper's
   arithmetic gets corrected, and theory owns that edit.
2. The stutter-oracle verdict (F8) and the LTL-bit-oracle verdict
   (F12): confirmed or the smallest disagreeing case. *(F8 CONFIRMED
   2026-07-11 — 6 222/6 222, read-off count 896 = the `.cat`
   stutter-tag total; F12 still pending, needs SY4.)*
3. The leastness probe (F14): any strictly-between aperiodic
   congruence falsifies the reflection-as-`θ_ap` reading of paper
   §6.2 — the dossier decides how Prop 6.2's proof gets written.
   *(Update 2026-07-11: leastness is now PROVED — paper Lemma 6.2a —
   and Prop 6.2 has a full proof; the probe stays but now gates the
   `aperiodic_reflection` implementation, not the theory. The proof
   also corrected the saturation: hull acceptance is the conjugacy
   closure of `q(P)` (Lemma 6.2b), and `kernel :=
   complement∘hull∘complement` (Prop 6.2(v)) — spec §6.2 rewritten
   accordingly; the iteration count remains an F14 datum since
   whether one collapse round always suffices is open.)*
4. Group-size numbers (F5) — feed the paper §9 stratified
   expectations. *(The kernel-fatness half is closed 2026-07-11:
   unmeasurable on this corpus by To-theory item 2's resolution;
   §3.1 and §9 rewritten, Y0a asserts zero.)*
5. ~~The `anti_possible` hit rate (F4) — decides whether the
   pair-count obstruction is a remark or a highlighted lemma.~~
   *(Resolved 2026-07-11: promoted to Lemma 3.2 — To-theory
   item 3.)*
6. Any nonabelian/non-solvable spectrum specimen (F13) — a find; the
   paper's §6.1 discussion would gain a concrete witness outside
   `FO+MOD`.
7. The orbit-price evidence (F7) and the tier of `n = 5` skips (F5)
   — decide whether the stabilizer-search stretch of spec §4 is
   commissioned.
