# SoS Learner — Paper Data Report

**Rev 2026-07-19.** The produced tables for the paper, one section per paper
section, each citing its committed machine-generated source. The development
ledger lives in git history.

**State of play.** Every number below is recomputed under the invariant-typed
learner (pair legality, the zero-seed bootstrap, evidence coherence). Nothing is
carried over from the earlier drop. Default leg: **6222/6222 SOUND**,
`N ∈ [2, 208]`, zero violations (`reference/census/sweep_results.csv`).

**Two protocol notes that govern the counts.**

1. *Wall time is not comparable across drops.* The earlier record's timings came
   from a cluster; these are one workstation, single-threaded. The learner did
   get faster, but the ratio between the two records is not a measurement of
   that — the old learner no longer exists to re-time. Wall times are reported
   as measured here; no speedup factor is claimed.
2. *The ablation leg is gone.* The learner enforces legality unconditionally, so
   there is no relaxed-learner runner and no §6.3/§7.3 stall census in this
   revision. The record was removed (`reference/census/ablation_*`, recoverable
   from git).

## §3–§5 — worked traces, and the §4.2 display

- Even / EvenBlocks ledgers + signature matrices:
  `reference/campaigns/e0/e4_transcripts.md`.
- Figures 4–5 (the day-one invariants): probe-dumped `.sos` in
  `research_notes/sos_core_figs/sources/sosl_*.sos` ←
  `python3 -m tests.sosl.fig_learner_exports`; rendered there by `make sosl`.
- The `reference/campaigns/m4b/` displays are **stale** — that campaign is
  ablation-driven and was not re-run.

## §6.2 — cost

Named cases (source `reference/campaigns/e0/results.csv`):

| case | `N` | initial | splits | member (fill/harvest/legality/`P`) | equiv | cex |
|---|--:|--:|--:|---|--:|--:|
| `a_once` | 4 | 2 | 2 | 10 (7/1/1/1) | 2 | 1 |
| `a_implies_xa` | 5 | 2 | 3 | 20 (13/3/0/4) | 2 | 1 |
| `even` | 5 | 2 | 3 | 25 (17/4/1/3) | 2 | 1 |
| `gf_aa_parity` / `gf_aa_reset` | 6 | 2 | 4 | 31 (22/3/1/5) | 2 | 1 |
| `evenblocks` | 8 | 2 | 6 | 44 (34/3/2/5) | 2 | 1 |

Both `GF(aa)` presentations still give byte-identical ledgers and signature
matrices (presentation-independence). Membership is roughly half the earlier
drop on every case.

**`initial` is now 2 on every named case, and this is structural.** The bootstrap
probe sweep queries one ω-power per alphabet letter, so its whole day-one
information is `|Σ|` bits; all five named cases are 1-AP, where `|Σ| = 2`. Two
classes is the seed's information ceiling there, not a weakness in it.

**`splits = N − 2` holds exactly on all 6222 languages** (checked; source
`e1_summary.md`, where median splits = max splits = `N − 2` in every `N` bucket).
The designed bound `splits ≤ N` is therefore no longer an inequality the data
tests — it is an identity the learner satisfies by construction. Theory may want
to restate the proposition accordingly.

Equivalence queries over the whole census: **never more than 4** (1 on 2266
languages, 2 on 3306, 3 on 568, 4 on 82).

Median membership by class count (source `e1_summary.md`):

| `N` | 2 | 4 | 8 | 13 | 21 | 32 | 50 | 72 | 97 | 121 | 208 |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| median member | 1 | 61 | 46 | 103 | 240 | 442 | 826 | 1331 | 1682 | 2780 | 19731 |
| median equiv | 1 | 1 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 |

The LTL-cut cost split (same source):

| definability | languages | median `N` | median splits | median member |
|---|--:|--:|--:|--:|
| LTL (aperiodic) | 3738 | 12 | 10 | 131 |
| non-LTL | 2484 | 20 | 18 | 234 |

Wall time (this workstation, single-threaded): **94 s total** over 6222
languages — median 0.00 s, p99 0.2 s, worst 1.2 s (`N = 208`).

Size-controlled ventilation is now a **stronger negative than before**: with
`splits = N − 2` exactly, `splits/N = 1 − 2/N` is a deterministic function of `N`
alone, so the normalized split cost carries no information about classification
whatsoever — the LTL cut (0.83 vs 0.90) and the whole Wagner ladder (0.00–0.94)
are reporting median `N` and nothing else. Classification affects cost only
through `N`; the paper reports no per-class claim.

Certification: `eq_certification` is `exact` on all 6222 default rows. The
functionality-guard column is **retired** — the current teacher records no
firings (`n_guard_firings = -1` on every row), and `census_e1` now reports the
guard only for a leg that populates it.

## §6.4 — ROLL FDFA baseline

Source `reference/census/e3_summary.md` (from `e3_assembled.csv`, 24888 rows).
The ROLL rows are the earlier cluster campaign, unchanged; the `ours` rows are
derived fresh from the recomputed sweep.

**Coverage, and why the comparison set is 5783.** Ours decides 6222/6222. ROLL
decides all three FDFA modes on **5783**, some but not all on **177**, and none
on **262** — at the per-run timeout the baseline applies. Paired counts run only
over the 5783 ROLL decides completely: its best mode is a `min` over three, so
scoring a partially-failed language on its survivors would compare a `min` over
three against a `min` over one. ROLL's ~7% attrition is ROLL's, and the earlier
phrasing "the languages both learners decide" wrongly read it as symmetric.

| metric | ours | ROLL periodic | ROLL syntactic | ROLL recurrent |
|---|--:|--:|--:|--:|
| median size | 16 | 16 | 21 | 12 |
| median MQ | 180 | 132 | 212 | 167 |
| median EQ | **2** | 6 | 6 | 7 |

Size over the 5783: algebra smaller **2026**, larger **3406**, tied **351** — a
wash inside the `N + N²` envelope. Ventilated:

| definability | smaller | larger | tied |
|---|--:|--:|--:|
| LTL (aperiodic) | 1520 | 1777 | 206 |
| non-LTL | 506 | 1629 | 145 |

**The query axis is the new result, and it did not exist in the previous
revision** — MQ/EQ were recorded in the CSV and never analyzed. Against ROLL's
cheapest mode:

- **Membership is parity.** Ours fewer on **2616**, tied 27, more on **3140**;
  median ratio ours/ROLL **1.11**. On LTL-definable languages it is a dead heat
  (1788 fewer / 1702 more). Under the earlier learner this ratio was 2.48 — the
  recompute is what moved it.
- **Equivalence is decisive.** Ours fewer on **5663**, tied 109, more on **11**.

So the honest Q3 claim is no longer "a wash": at equal membership cost and
comparable size, the algebra is learned with a third the equivalence queries,
and carries the LTL read-off. That argument depends on MQ and EQ not being
fungible — one membership is a simulation, one equivalence is a verification
against the whole hypothesis — which the paper should state rather than assume.

LTL agreement: every default-leg run certifies `exact` (invariant byte-equal to
the reference), so the aperiodicity read-off is evaluated on the reference object
itself and agrees with ground truth on all 6222.

## §6.5 — counterexample sensitivity

Source `reference/campaigns/e5/results.csv`, 28 runs, all SOUND — padding never
changes the learned invariant.

| case | loop 3 → 96 | harvest |
|---|---|---|
| `even` | 3 → 96 | **4, flat** |
| `a_once` | 1 → 32 | **1, flat** |
| `gf_aa_parity` | 3 → 96 | 3 → 8 |
| `evenblocks` | 3 → 96 | 3 → 9 |

This is **stronger than the claimed result**. The paper states one query per
doubling universally; in fact two of the four cases absorb padding at *zero*
cost, and only `gf_aa_parity` / `evenblocks` show the `log₂ ℓ` growth.

## Owed / open

- **`a → Xa` no longer runs zero-counterexample.** It now takes cex = 1, equiv =
  2. §7.2's "one legality escalation, zero counterexamples, a single assenting
  equivalence query" and §7.3's echo of it are both false against current code.
  Reported to theory rather than adapted to: the claim may be worth recovering,
  or worth dropping.
- ROLL's 262 total and 177 partial failures are **unattributed** — `baseline.py`
  records a `detail` (timeout / nonzero exit / unparsed stats) that `census_e3`
  does not persist. Distinguishing "timed out" from "crashed" needs a re-run.
- ROLL runtime is not recorded at all; deferred by decision (JVM startup would
  dominate).
