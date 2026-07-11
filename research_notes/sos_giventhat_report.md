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
| GT1 — interval + endpoints | *pending* | F1–F4 |
| GT2 — ladder tests | *pending* | F5–F8 |
| GT3 — stutter two-tier | *pending* | F9–F11 |
| GT4 — band degree probe | *pending* | F12 |
| GT5/W0 — census campaigns (W0a/W0b/W0c) | *pending* | F13–F15 |
| GT5/W1 — MCC benchmark | *blocked on data* | — |

## GT1 — the interval object + endpoint decisions

- **F1 — Prop 3.1 holds as a runtime law.** *(pending)* The
  `P_max \ P_min = P_K^c` identity and the freedom partition, asserted
  on every constructed interval: fixture + 700-pair campaign, zero
  violations expected. State the count.
- **F2 — the fixture pair behaves as the paper computes.** *(pending)*
  `|𝒞(D_ab)|` (paper predicts 6), `|𝒞(D_K)|` (datum), both endpoint
  checks inconclusive with witnesses replaying as `(ab)^ω` and
  `(ba)^ω`, `iv.bits` (datum — the paper leaves it uncomputed).
- **F3 — the freedom distribution.** *(pending)* `|F|` in bits over the
  campaign (min / median / p95 / max; share with `bits = 0`); a paper
  §7 item 2 number in census-shaped form. Path: `logs/gt1_bits.csv`.
- **F4 — endpoint kill rate, census-shaped.** *(pending)* How often
  `k_settles_phi` / `k_refutes_phi` decide outright, per sampling
  stratum (the complement-partner stratum should settle ~always —
  say whether it does).

## GT2 — the ladder tests

- **F5 — the corpus rung oracle.** *(pending — run FIRST)*
  `is_recurrence == (m⁺ ≤ 0)` and `is_persistence == (m⁻ ≤ 0)` over
  3 938 sidecars: agreement counts. If the orientation flipped, this
  slot carries the flip and the paper's §2 correction request.
- **F6 — hull laws.** *(pending)* `rec_hull` extensive / monotone /
  idempotent / saturated / fixpoint-iff-recurrence, case counts.
- **F7 — exactness vs the brute lattice oracle.** *(pending)* On every
  `bits ≤ 12` case: per-rung existence bits equal the `2^bits`
  enumeration; leastness of returned witnesses; number of probed
  cases and skips.
- **F8 — per-rung hit rates.** *(pending)* Over the campaign: how often
  each rung's `B` exists where the raw `¬φ` sat strictly higher —
  paper §7 item 3, census-shaped.

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

*(empty — populate the moment anything below occurs)*

Standing items the theory thread expects data or answers on:

1. Any disagreement between the spec and the paper (spec §8 E1/E2
   escalations included) — smallest case, verbatim.
2. The rung-orientation verdict (F5): confirmed or flipped.
3. The GT4 dossier (F12) if greedy ≠ brute — it decides how Prop 4.5's
   proof gets written.
4. The tier-gap frequency (F10) — the paper argues the two-tier design
   from it; if the gap is empty in practice, §5.3's framing weakens
   and theory wants to know early.
5. `iv.bits` on the fixture and the campaign extremes (F2, F3) — feeds
   the paper's Q5 discussion of `2^F` enumeration feasibility.
6. Any W0c law violation (F15) — monotonicity or losslessness breaking
   falsifies paper §6.2 as stated; the minimal fact sequence, verbatim.
