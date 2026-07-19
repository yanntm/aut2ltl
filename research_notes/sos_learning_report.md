# SoS Learner — Paper Data Report

**Rev 2026-07-19.** The produced tables for the paper, one section per paper
section, each citing its committed machine-generated source (regeneration
commands: the spec). Anything not yet produced is marked OWED there. The
development ledger lives in git history.

**State of play.** Pipeline complete. Default leg: **6222/6222 SOUND**,
`N ∈ [2, 208]`, `splits ≤ N` on every language, zero violations
(`reference/census/sweep_results.csv`). All §6 data is banked except the
spec's owed fills.

## §3–§5 — worked traces, and the §4.2 display

- Even / EvenBlocks ledgers + signature matrices:
  `reference/campaigns/e0/e4_transcripts.md`.
- The stalled displays — coarse vs canonical `.sos` with separating left
  contexts (`a_implies_xa` 4 vs 5 classes, `a_once` 3 vs 4):
  `reference/campaigns/m4b/e2_report.md`.

## §6.2 — cost

Named cases (source `reference/campaigns/e0/results.csv`, default rows):

| case | `N` | initial | splits | member (fill/harvest/sat/`P`) | equiv | cex |
|---|--:|--:|--:|---|--:|--:|
| `a_once` | 4 | 2 | 2 | 35 (26/3/2/4) | 2 | 1 |
| `a_implies_xa` | 5 | 4 | 1 | 43 (32/0/2/9) | 1 | 0 |
| `even` | 5 | 3 | 2 | 51 (32/4/7/8) | 2 | 1 |
| `gf_aa_parity` / `gf_aa_reset` | 6 | 3 | 3 | 74 (51/4/9/10) | 2 | 1 |
| `evenblocks` | 8 | 3 | 5 | 99 (67/4/14/14) | 2 | 1 |

Census: per-N medians (splits, fill, member, equiv) and the Wagner ventilation
are `reference/census/e1_summary.md` — the paper excerpts buckets. The LTL-cut
cost split (same source):

| definability | languages | median `N` | median splits | median member |
|---|--:|--:|--:|--:|
| LTL (aperiodic) | 3738 | 12 | 9 | 291 |
| non-LTL | 2484 | 20 | 16 | 557 |

Wall time (default leg, source `reference/census/e1_summary.md`): **10733 s
total** over 6222 languages — median 0.12 s, p99 20.5 s, worst 49.6 s
(`2state3ap1acc_parity_02738846096277145868_c`, N=68) — all under the 60 s
budget.

Size-controlled ventilation (same source) is a **negative**: with cost
normalized by the designed bounds (splits/N, member/(N²·|Σ|)) the LTL cut
nearly vanishes (0.71 vs 0.81 splits/N) and the Wagner ladder shows no
monotone hardness trend (0.43–0.88 across degrees, DBA/DCA-proper lowest,
safety/guarantee highest). Classification affects cost only through N; the
paper reports no per-class claim.

Oracle guard and certification, per leg (§6.1; same source): the
functionality guard fires on 2694 of 6222 default-leg runs (3398 firings;
ablation leg 4451 runs, 25288 firings), and the fallback finished within its
work cap on every run — `eq_certification` is `exact` on all 6222 default
rows; the ablation leg's 697 uncertified rows are exactly its 665 BUDGET +
17 CRASH + 15 OVERSIZE runs. Zero cap-escapes on either leg.

## §6.3 — the saturation ablation

Congruence column, 6222 ablation rows at the 60 s budget
(source `reference/census/ablation_congruence.csv`, graded in
`reference/census/ablation_congruence_summary.md`):

| verdict | `fixpoint_congruent` | rows |
|---|---|--:|
| `ACCEPTOR_ONLY` (permanent stall) | false | 3137 |
| `SOUND` (recovered canonical) | true | 2336 |
| `BUDGET` (undecided) | n/a / false / true | 719 / 12 / 5 |
| `OVERSIZE` (beyond oracle cap) | n/a | 13 |

Zero off-diagonal mass: every certified stall fails the congruence check and
every byte-equal run passes it — **Theorem 5.3 with zero counterexamples over
the catalogue** — dual-symmetric over the 2733 comparable pairs. Counts are
floors at the stated budget (≥ 3137 permanent; no decided case ever flips).

Prefix-independent permanent stalls: two witnesses plus their complements,
certified on the canonical invariants (prefix-independence algebraic, every
minted column ω-sort — `witness_lock` green; complements stated by duality).

Stall frequency / gap distribution / per-shape exhaustive negative /
individual exhibits at 6222: OWED (spec).

## §6.4 — ROLL FDFA baseline

Source `reference/census/e3_summary.md` (from `e3_assembled.csv`, 24888 rows):

| metric | ours | ROLL periodic | ROLL syntactic | ROLL recurrent |
|---|--:|--:|--:|--:|
| median size | 16 | 16 | 21 | 12 |

Size over the 5960 jointly-decided languages (algebra `N` vs ROLL's smallest
FDFA): smaller **2032**, larger **3574**, tied **354** — a wash inside the
`N + N²` envelope. Ventilated by the LTL cut:

| definability | smaller | larger | tied |
|---|--:|--:|--:|
| LTL (aperiodic) | 1524 | 1842 | 207 |
| non-LTL | 508 | 1732 | 147 |

At 6222 the LTL-cut direction *inverts* vs the draft's small-shape numbers —
the paper keeps the correlation and drops the direction claim (spec). The
capability column (LTL-definability read-off, ours only) is the result.
LTL agreement: the read-off agrees with ground truth on **all 6222**
languages — every default-leg run certifies `exact` (invariant byte-equal to
the reference, `e1_summary.md` certification tally), so the aperiodicity
test is evaluated on the reference object itself.

## §6.5 — counterexample sensitivity

Source `reference/campaigns/e5/`. Pumping the loop from length 3 to 96 grows
the harvest term from 4 to 9 queries — one per doubling, `harvest ≈ log₂ ℓ` —
with the learned invariant unchanged on every padded run.
