# Choosing the Simplest Property Given Prior Knowledge — results

The answer to `research_notes/sos_giventhat_spec.md` (milestones
GT1–GT5): the `sosl.sos.giventhat` package measured against its gates,
the census-shaped W0 campaign, and — once the data lands — the [DPT25]
MCC benchmark. Each finding `Fn` below is a checked prediction (or a
flagged open point) of the paper `research_notes/sos_giventhat.md`; the
paper states results in pure form and cites no artifact — this report
ties every claim to a regenerable machine report under
`reference/giventhat/` or a gate log under `sosl/tests/giventhat/logs/`
(date / git-rev / seed / corpus header, regen command per finding).

**How to use this file (implementer):** fill the pre-named slots as the
milestones close; never renumber; a slot that dies gets a one-line
epitaph, not deletion. Anything that belongs to the theory thread —
disagreements with the paper, orientation flips, greedy/brute gaps,
escalations of spec §8 — goes in **To theory** at the bottom, the
moment it is found, even mid-milestone.

## Status

| milestone | state | findings |
|---|---|---|
| GT1 — interval + endpoints | **DONE (2026-07-11, git 4c7aa9fb5+)** | F1–F4 |
| GT2 — ladder tests | **DONE (2026-07-11)** — rung oracle 6222/6222, campaign 700/700, brute 264/264; §4.6 E1 escalations resolved (To theory) | F5–F8 |
| GT3 — the bounded quotient engine | *pending* | F9–F11 |
| GT4 — the simplifier and the tool | *pending* | F12–F13 |
| GT5 — the demonstration | *pending* | F14–F15 |

**Spec re-aimed (2026-07-12, theory).** The goal is now **one
operation** — `simplify(𝓘(¬φ), 𝓘(K)) → 𝓘(B)`, two `.sos` in, one
*smaller* `.sos` out — and the spec (GT3–GT5) plus the paper were
restructured around it. GT1 and GT2 stand exactly as delivered: GT1 is
steps 1–2 of the operation; GT2's rungs are re-scoped from deliverable
to **output metrics and optional constraints**. Slots F1–F8 are
unaffected. Slots F9–F15 are **re-cut below** (the old F9–F15 — stutter
tier 2, the Wagner brute probe, the W-series — are decommissioned, spec
§8; their epitaphs are inline). Nothing delivered was retracted.

## GT1 — the interval object + endpoint decisions

- **F1 — Prop 3.1 holds as a runtime law.** *(confirmed)* The
  `P_max \ P_min = P_K^c` identity and the freedom partition, asserted
  inside `given_that` on every construction: the fixture pair + 699
  scored campaign pairs (700 sampled, 1 F2-budget skip), **zero
  violations**. The conjugacy gate (partition of `linked`,
  `saturate({p})` recovering each class, every carried pair set a
  union of classes) also zero violations on all scored pairs.
  Regen: `cd sosl && python3 -m tests.giventhat.interval_gate
  --campaign`; rows `reference/giventhat/gt1_bits.csv`.
- **F2 — the fixture pair behaves as the paper computes.**
  *(confirmed)* `|𝒞(D_ab)| = 6` (as the paper's §5.2 hand count
  predicts), `|𝒞(D_K)| = 6` (datum), product table n = 6 with 7 linked
  pairs. `k_settles_phi = False` with the loop-2 witness
  `ε·(p·¬p)^ω = (ab)^ω` replaying IN both HOAs; `k_refutes_phi =
  False` with `ε·(¬p·p)^ω = (ba)^ω` replaying IN `D_K`, NOT in `D_ab`.
  **`iv.bits = 2`** (datum — the paper leaves it uncomputed; free band
  nonempty as predicted). 210 exhaustive metamorphic lassos, zero
  violations. Regen: `... interval_gate --fixture`.
- **F3 — the freedom distribution.** *(measured)* `|F|` over 699
  scored pairs: **min 0 / median 20 / p95 124 / max 458**; `bits = 0`
  share **1/699** (the point interval `1state1ap0acc_0 ×
  1state1ap0acc_3`, where K settles φ outright). Summary
  `reference/giventhat/gt1_interval.md`, raw
  `reference/giventhat/gt1_bits.csv` (seed 20260711).
- **F4 — endpoint kill rate, census-shaped.** *(measured)* fwd (300):
  settles 21 (7.0%), refutes 17 (5.7%); rev (299): settles 21, refutes
  12 (4.0%); comp (100): **settles 100/100**, refutes 0. The
  complement-partner stratum settles always, as predicted, and
  `k_settles_phi` agreed with `intersecting_word` finding nothing on
  every one. Settles is symmetric (fwd = rev = 21 — the built-in
  cross-check); refutes is directional and differs (17 vs 12).

## GT2 — the ladder tests

- **F5 — the corpus rung oracle.** *(confirmed — the paper's
  orientation holds)* `is_recurrence == (m⁺ ≤ 0)` and
  `is_persistence == (m⁻ ≤ 0)` over the full corpus (6 222 sidecars at
  run time — the corpus has grown past the spec's 3 938 under
  regeneration): **6 222/6 222 agreement as stated**, 4 914/6 222
  under the swapped orientation — decisively the stated one, no flip,
  no mixed cases, zero F2 skips. The two sides share
  `classify.primitives`' H-order but decide by different paths (the
  ladder's violation scan vs `classify.chains`' alternating-path DP).
  Summary (incl. the per-aps table)
  `reference/giventhat/gt2_rung_oracle.md`; regen:
  `cd sosl && python3 -m tests.giventhat.ladder_gate --rung-oracle`.
- **F6 — hull laws.** *(confirmed)* Over the 700-pair GT1 campaign
  populations (seed 20260711, 700/700 scored, zero F2): `rec_hull`
  extensive / monotone / idempotent / output-saturated /
  `is_recurrence`-on-output / fixpoint-iff-recurrence, 6 seeded random
  saturated pair sets per product table — **zero violations**; the
  `r_classes` one-liner (partition of the linked stems) zero
  violations. Witness discipline (spec §4 gate 4): every refusal lasso
  replayed via table `member` AND against both det HOAs — zero
  violations. Regen: `cd sosl && python3 -m tests.giventhat.ladder_gate
  --campaign`; summary `reference/giventhat/gt2_ladder.md`.
- **F7 — exactness vs the brute lattice oracle.** *(confirmed)* On the
  **264** campaign cases with `bits ≤ 12` (436 skipped, recorded): all
  `2^bits` choices enumerated; per-rung existence equals the
  enumeration verdict, the returned member is literally the
  intersection (Moore rungs) resp. union (kernel rungs) of the
  enumerated members and is itself enumerated — **zero disagreements**
  across all five rungs. Rows `reference/giventhat/gt2_ladder.csv`.
- **F8 — per-rung hit rates.** *(measured)* Over 700 scored pairs —
  interval has a member / raw `¬φ` already on the rung / strict drop
  available: safety **318 / 169 / 149**, co-safety **321 / 164 /
  157**, obligation **453 / 347 / 106**, recurrence **516 / 424 /
  92**, persistence **529 / 429 / 100**. Read: on a fifth of census
  pairs, knowledge buys a strict drop to safety — the paper §7 item 3
  number, census-shaped. Table `reference/giventhat/gt2_ladder.md`.

## GT3 — the bounded quotient engine (spec §5, paper §4.2–§4.4, §5.3)

- **F9 — Prop 4.2 against the bounded oracle.** *(pending)* On every
  case with `bits ≤ 12`: enumerate the `2^F` members, keep the
  `π`-recognizable ones, and confirm that the set is nonempty **iff**
  `admits(π, iv)`, with `least_member` = their intersection and
  `greatest_member` = their union. Exact agreement, or the smallest
  disagreeing case verbatim — which convicts Prop 4.2 and goes to
  To theory, never a patch of the hull.
- **F10 — Prop 4.1 at runtime.** *(pending)* On sampled saturated `q`:
  `syntactic_congruence(T, q).n == |𝒞(reduce(T, q))|`, and `q` is
  recognized by that congruence — the claim that congruences *are* the
  search space, checked rather than assumed.
- **F11 — Thm 5.7 as a regression (was F9).** *(pending)* On the
  fixture: stutter quotient size 2, `sc(p_min) = linked` (universal),
  stutter verdict **UNKNOWN**. The paper's counterexample,
  machine-checked. *(The old F9's tier-2 YES leg is decommissioned —
  spec §8.)*

*Epitaph — old F10/F11 (the two-tier stutter gap and the tier-2
semantic oracle):* decommissioned with stutter tier 2 (spec §8). The
tier-2 test decides existence but yields no witness the operation can
emit; the UNKNOWN *frequency* survives as a column of F15.

## GT4 — the simplifier and the tool (spec §6, paper §4.6)

- **F12 — the operation, end to end.** *(pending)* `simplify` on the
  fixture and on small corpus pairs: the §6.3 soundness law
  (`B ∩ P_K == P_min`, plus the independent language-level cross-check)
  green on every case; the emitted `.sos` re-read and byte-stable under
  `reduce`; `SETTLED` / `REFUTED` verdicts carrying their minimal
  witness lasso.
- **F13 — the [DPT25] example (paper §6), predicted vs actual.**
  *(pending)* The paper **predicts** a guarantee `B` inside the bracket
  `[F(a∧c), F(a∨¬c)]` with fewer than 5 classes (against
  `|𝒞(¬φ)| = 5`, `bits = 25`, both endpoints larger). Report the actual
  `|𝒞(B)|`, the rung, and which seed/side won. **A miss is a
  To-theory finding, not a bug to hide** — it would mean the greedy
  does not reach what the hulls prove exists.

*Epitaph — old F12 (greedy vs brute Wagner degree):* decommissioned
(spec §8). Prop 4.5 is a sketch and `2^F` enumeration is not a proof
technique; the degree is at best a tie-break under the `|𝒞|` objective.

## GT5 — the demonstration (spec §7, paper §7)

- **F14 — the size table.** *(pending)* One row per pair over the
  N ≈ 200 small same-stratum sample: `|𝒞(¬φ)|`, `|𝒞(P_min)|`,
  `|𝒞(P_max)|`, **`|𝒞(B)|`**, `bits`, rung in → out, stutter in → out.
  Headline: the fraction where `|𝒞(B)|` is *strictly* below all three
  reference points, and the median ratio `|𝒞(B)| / |𝒞(¬φ)|`. This is
  the paper's central claim; a 0% rate is a finding, reported as such.
- **F15 — the heuristic, scored.** *(pending)* Where `bits ≤ 12`: the
  greedy's `|𝒞(B)|` against the exhaustive `2^F` optimum — the gap
  distribution. Plus the rung-drop rate and the stutter UNKNOWN
  frequency (how often the hull escapes the table — a number no automata
  pipeline can produce). **State in the summary, in these words, that
  the gap measures our heuristic and is not evidence about Conj 4.5.**

*Epitaph — old F13/F14/F15 (the W-series: all-pairs endpoint sweep,
asymmetric stratum, incremental verification with ground truth):*
decommissioned (spec §8). W0 is a frequency census downstream of a
working operation; W1 stays blocked on the [DPT25] MCC data. The
census-shaped numbers already delivered under F1–F8 carry the paper's
§7 "already in hand" paragraph.

## To theory

**GT2 (2026-07-11): E1 escalation — the paper §4.6 class counts are
wrong; everything semantic in the worked example holds.** With
`¬φ = F(a∧c) ∨ (GFb ∧ GF¬b)` and `K = FGb ∧ Gc` over `AP = {a,b,c}`
(ltl2tgba → canonize; encoding vetted by lasso probes on the det HOA):
`|𝒞(¬φ)| = 5`, paper says 7; product table 10 classes, paper says 13.
`|𝒞(K)| = 4` as stated. **Edit paper §4.6 to match
`reference/giventhat/gt2_fixture.md`** — the tracked, generated
artifact carrying the full machine census of `𝓘(¬φ)` (per class:
shortlex key, loops, accepting pairs; 5 classes, 9 linked pairs) and
the complete prediction-vs-machine table. Every *semantic*
§4.6 prediction is machine-checked green: both endpoints inconclusive
with minimal witnesses `({abc})^ω` and `({bc})^ω`; `exists_safety` NO
with refusal `({bc})^ω`; `exists_cosafety` YES with kernel reducing to
`𝓘(F(a ∨ ¬c))` and least member reducing to `𝓘(F(a∧c))` (both
byte-compared); `is_recurrence(P_¬φ)` true, `is_persistence` and
`is_obligation` false. Two §4.6 corrections requested: the counts, and
note the fixture band is `bits = 25`, so the "least co-safety member"
was obtained by the exact least-open-hull (stems' right ideal), not
the `2^bits` enumeration — worth a sentence in §4.6 since 4.1's `ρ`
for co-safety is otherwise implicit. Repro:
`cd sosl && python3 -m tests.giventhat.ladder_gate --fixture`.
*(Resolved 2026-07-11: paper §4.6 states 5 / product 10 and derives
the `σ = 1` merge; the two requested sentences are in; spec §4 item 5
asserts 5/10. No retrofit — the gates already produce these values.)*

**GT2 (2026-07-11): the "independent transcription" framing was
dropped by decision.** Duplicating the H-order to keep the rung oracle
"totally independent" was judged bad engineering (unmaintainable) for
the price of one experiment: `ladder.h_below` now reuses
`classify.primitives` (`idempotents` / `leq_h_idem`), and the oracle's
value is re-framed as two *decision paths* over shared primitives
(violation scan vs chain DP). Spec §4 (gate 1, the H-order bullet) and
the layering law were edited accordingly. The paper's §2/§7 wording
("re-verified against the census's independently computed chain
coordinates") should be softened to match. Note the oracle was ALSO
run green (6 222/6 222) with the hand-rolled H-order before the
rewire, so the independence experiment de facto happened once.
*(Resolved 2026-07-11: paper §2 states the two-decision-paths
framing; no independence claim remains. F5–F8 integrated as paper §7
"First census-shaped data". No retrofit.)*

**GT1 (2026-07-11): no spec/paper disagreement arose.** E1 held
(`|𝒞(D_ab)| = 6` on the first build), Prop 3.1 zero violations across
the fixture and 699 campaign pairs. Standing item 5's data is in:
fixture `iv.bits = 2`; campaign extremes min 0 / median 20 / p95 124 /
max 458 (F2, F3). One operational note for Q5 feasibility: at the
campaign maximum (`bits = 458`) the `2^F` lattice is far beyond
enumeration, while the median (20 bits ≈ 10^6 choices) sits at the
edge — the greedy/hull machinery of GT2/GT4 is not optional at census
sizes.

**THEORY → ENGINEERING (2026-07-12): the goal was drifting; it is
re-centered.** The milestones had become a set of independent probes,
several of them aimed at corroborating *sketched* propositions by
enumeration — which is not how a conjecture gets settled. The paper and
spec are rewritten around a single operation: **`simplify(𝓘(¬φ),
𝓘(K)) → 𝓘(B)`, two `.sos` in, one smaller `.sos` out**, the algebraic
double of [DPT25]'s Bounded-by-Minato. What theory owes you, and now
delivers, is the math that makes it exact:

- **Prop 4.1** — minimizing `|𝒞(B)|` over the interval *is* minimizing
  `|T/π|` over the admissible congruences of the aligned table. The
  search space is congruences, and nothing is lost.
- **Prop 4.2 (the engine)** — for *any* congruence `π`,
  `hull_π(Q) = π⁻¹(sat(forced_π(Q)))` is the least `π`-recognizable
  superset of `Q`; so the interval holds a `T/π`-recognized member iff
  `hull_π(P_min) ⊆ P_max`. Exact, polynomial. This is the old stutter
  `sc` with the stutter seeds removed — the proof never used them.
- **Prop 4.3** — admissibility is inherited by refinements, so the
  targets are the maximal admissible congruences and **greedy
  merge-until-stuck is licensed** (the same shape Minato has, with a
  decision procedure where they have a heuristic).
- **Thm 4.4 / Conj 4.5** — the exact minimum is in NP, conjectured
  NP-complete (Gold route). Hence: greedy, honestly labeled. *Do not
  attempt to settle Conj 4.5 by enumeration.*
- **Lemma 5.2** — constraints compose exactly (joint closure fixpoint),
  so "smallest `B` that is also safety / stutter-invariant" is one
  fixpoint, not a chain of heuristics.
- **The free contract** — seed the greedy at `π_{¬φ}` (always
  admissible) and the operation can never regress on its input.

Standing items the theory thread expects data or answers on:

1. Any disagreement between the spec and the paper — smallest case,
   verbatim. **DELIVERED for GT2 and RESOLVED (2026-07-11): the §4.6
   class counts, above — paper and spec state 5/10.**
2. The rung-orientation verdict (F5): confirmed or flipped.
   **DELIVERED (2026-07-11): confirmed, 6 222/6 222 (F5).**
3. `iv.bits` on the fixture and the campaign extremes (F2, F3).
   **DELIVERED with GT1; the §4.6 pair adds `bits = 25`.**
4. **F9 — the Prop 4.2 bounded oracle.** The one result that can
   falsify the new core. If the hull disagrees with the `2^F`
   enumeration on any case, theory wants the smallest one verbatim, and
   the hull is NOT to be patched toward the oracle.
5. **F13 — the paper §6 prediction.** The [DPT25] example should yield
   a guarantee `B` with `< 5` classes. A miss means the greedy fails to
   reach what the hulls prove exists — a design finding, not a bug.
6. **F14 — the headline rate.** The fraction of pairs where `|𝒞(B)|` is
   strictly below all three reference points. If that rate is ~0, the
   paper's central claim is empty and theory needs to know before
   anything else is built.
