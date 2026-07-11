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
| GT2 — ladder tests | **DONE (2026-07-11)** — rung oracle 6222/6222, campaign 700/700, brute 264/264; two E1 escalations (paper §4.6 counts) in To theory | F5–F8 |
| GT3 — stutter two-tier | *pending* | F9–F11 |
| GT4 — band degree probe | *pending* | F12 |
| GT5/W0 — census campaigns (W0a/W0b/W0c) | *pending* | F13–F15 |
| GT5/W1 — MCC benchmark | *blocked on data* | — |

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
  Summary `reference/giventhat/gt2_rung_oracle.csv` +
  `tests/giventhat/logs/rung_oracle.md`; regen:
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

## GT3 — stutterization, two tiers

- **F9 — Thm 5.2 as a regression.** *(pending)* On the fixture: quotient
  table size 2, tier 1 UNKNOWN with `sc(p_min) = linked`, tier 2 YES.
  The paper's counterexample, machine-checked.
- **F10 — the tier gap, measured.** *(pending)* Over the campaign:
  tier-1 YES / tier-1 UNKNOWN + tier-2 YES / tier-2 NO counts — the
  frequency with which the stutter hull escapes the table (paper §7
  item 4's middle bucket).
- **F11 — tier-2 against the bounded semantic oracle.** *(pending)*
  Zero violations of spec §5.2 gates (a)–(d); certificate replays on
  every NO.

## GT4 — band-minimal Wagner degree (the Prop 4.5 probe)

- **F12 — greedy vs brute.** *(pending)* Equality on all probed cases,
  or the minimal disagreeing case verbatim (table, forced pattern,
  greedy pair, true minimum) — either outcome is a result; a
  disagreement additionally lands in To theory.

## GT5 — campaigns

- **F13 — W0a: the all-pairs endpoint sweep.** *(pending)* Endpoint
  kill matrix over all unordered same-stratum pairs; the inclusion
  digraph and disjointness graph committed as census artifacts (edge
  counts, density per stratum); sweep wall time and chunk count.
- **F14 — W0b: simple-on-complex.** *(pending)* On the asymmetric
  stratum (`¬φ` complex, `K` fact-shaped): bits distribution, per-rung
  hit and rung-drop rates, tier-gap frequency, band degrees — the
  realistic-direction numbers the paper's §7 items 2–4 cite.
- **F15 — W0c: incremental verification with ground truth.** *(pending)*
  Knowledge-decides rate vs the exact `S ⊨ φ` scan; median facts to
  decision; running-table growth vs the census ratio prediction; and
  the two per-step laws (monotonicity, losslessness) — zero violations
  expected, any violation goes to To theory verbatim (it is a
  paper-level event, §6.2).
- **W1** — blocked on the [DPT25] MCC problem set landing in the repo;
  no findings until then.

## To theory

**GT2 (2026-07-11): E1 escalation — the paper §4.6 class counts are
wrong; everything semantic in the worked example holds.** With
`¬φ = F(a∧c) ∨ (GFb ∧ GF¬b)` and `K = FGb ∧ Gc` over `AP = {a,b,c}`
(ltl2tgba → canonize; encoding vetted by lasso probes on the det HOA):
`|𝒞(¬φ)| = 5`, paper says 7; product table 10 classes, paper says 13.
`|𝒞(K)| = 4` as stated. Hand census supporting 5: `[ε]`; the absorbing
"has seen a∧c" class; and the no-a∧c classes split only by
`(has-b, has-¬b) ∈ {(1,0),(0,1),(1,1)}` — nothing else about a no-a∧c
word is future-relevant, as stem or as loop. Every *semantic*
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

**GT1 (2026-07-11): no spec/paper disagreement arose.** E1 held
(`|𝒞(D_ab)| = 6` on the first build), Prop 3.1 zero violations across
the fixture and 699 campaign pairs. Standing item 5's data is in:
fixture `iv.bits = 2`; campaign extremes min 0 / median 20 / p95 124 /
max 458 (F2, F3). One operational note for Q5 feasibility: at the
campaign maximum (`bits = 458`) the `2^F` lattice is far beyond
enumeration, while the median (20 bits ≈ 10^6 choices) sits at the
edge — the greedy/hull machinery of GT2/GT4 is not optional at census
sizes.

Standing items the theory thread expects data or answers on:

1. Any disagreement between the spec and the paper (spec §8 E1/E2
   escalations included) — smallest case, verbatim. **DELIVERED for
   GT2 (2026-07-11): the §4.6 class counts, above — awaiting a theory
   response.**
2. The rung-orientation verdict (F5): confirmed or flipped.
   **DELIVERED (2026-07-11): confirmed, 6 222/6 222 (F5).**
3. The GT4 dossier (F12) if greedy ≠ brute — it decides how Prop 4.5's
   proof gets written.
4. The tier-gap frequency (F10) — the paper argues the two-tier design
   from it; if the gap is empty in practice, §5.3's framing weakens
   and theory wants to know early.
5. `iv.bits` on the fixture and the campaign extremes (F2, F3) — feeds
   the paper's Q5 discussion of `2^F` enumeration feasibility.
   **DELIVERED with GT1 (see the GT1 note below); the §4.6 pair adds
   `bits = 25` as a mid-scale data point.**
6. Any W0c law violation (F15) — monotonicity or losslessness breaking
   falsifies paper §6.2 as stated; the minimal fact sequence, verbatim.
