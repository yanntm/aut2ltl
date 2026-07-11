# Measure, Distance, and Entropy on the Syntactic ω-Semigroup — results

The answer to `research_notes/sos_measure_spec.md` §8 (milestone QNT5):
the `sosl.sos.quant` package run against the E-series, measured on the
`flat_canon` census and on the QNT4 pipeline demo. Each finding `Fn` is a
checked prediction of the paper `research_notes/sos_measure.md`; the
paper states results in pure form and cites no artifact — this report is
where each claim is tied to a regenerable machine report.

Every campaign writes a machine-generated report under `reference/quant/`
(one `.md` + one `.csv`) carrying a date / git-rev / seed / corpus
header, so any row below is reproducible from that file alone. Commands
run from `sosl/`. Spot appears only inside the Route A oracle,
bounded-or-skipped; a blown per-case budget is a datum, never a wait.

*Status (2026-07-10): no findings yet — QNT1–QNT4 not started. This file
is the interface: findings land here as the milestones close, keyed to
the paper's ⟨TBD⟩ slots.*

## Slot map (paper ⟨TBD⟩ → expected finding)

| paper slot | experiment | finding |
|---|---|---|
| Abstract headline number | E1 | ⟨F1⟩ |
| §4.3 pipeline demo | E4 | ⟨F4⟩ |
| §5 entropy-per-degree | E2 | ⟨F2⟩ |
| §6 (i) measure/θ-profile distributions | E1 | ⟨F1⟩ |
| §6 (ii) measure-0/1 concentration in safety rungs | E1 | ⟨F1b⟩ |
| §6 (iii) entropy distribution | E2 | ⟨F2⟩ |
| §6 (iv) distance geometry, nearest-LTL-neighbor | E3 | ⟨F3⟩ |
| §6 (v) pipeline + baseline | E4 | ⟨F4⟩ |

## Harness state (QNT2)

*(to be filled: law-by-law green/red table, corpus coverage, oracle
agreement counts, Route A skip rate)*

## Findings

**F-M1 (2026-07-11, git b5cc0062e) — θ-profile + exact measure land; the
flip law holds corpus-wide.** Engine in `sosl/sosl/quant/` (placement
provisional, to move later); Theorem 3.4 implemented as specified
(bottom SCCs → kernel idempotent → one `Val` lookup per component →
transient system over `Fraction`). The three hand fixtures F-A/F-B/F-C
pass with exact equality under uniform and `p(a)=1/3`, including the
Lemma 3.3 idempotent-independence check on F-C and the byte-equal
complement route on F-B; `PARANOID` re-derivations stayed silent
throughout. Flip gate `μ(L) + μ(¬L) == 1` (exact) with pointwise-negated
profiles: **4248/4248 green**, 0 crashes, 0 missing, no reduce anywhere.
Distribution over the census: 1737 languages with `μ = 0`, 1737 with
`μ = 1`, 774 strictly interior — the exact 0/1 tie is the corpus's
complement-closure showing through the measure, an unplanned
cross-check. Median table 15 classes (max 121); median 1 bottom SCC
(max 7); worst case 173 ms. Machine report:
`reference/quant/m1_measure.{md,csv}`; regeneration (from `sosl/`):
`python3 -m tests.quant.flip_gate --list | while read f; do timeout 15
python3 -m tests.quant.flip_gate "$f" >/dev/null; done; python3 -m
tests.quant.flip_gate --aggregate` (fixtures:
`python3 -m tests.quant.fixtures`). No disagreement between spec and
paper surfaced.
