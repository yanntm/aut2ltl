# SoS Quantitative (Measure / Distance / Entropy) — Implementation Specification

**Status.**

| item | state |
|---|---|
| M1 measure + θ-profile, M2 oracle + laws, M3 distance / shadow / essential (+ M3b), M4 entropy, M5 the Markov product | **DONE**, green corpus-wide — findings F-M1..F-M5 in `sos_measure_report.md`; the work orders that produced them are frozen in `sos_measure_experiments.md` |
| **M6 = QNT5: the census campaign E1–E4 (§12)** | **OPEN — the current work order** |
| MDPs, semiring-valued `Val`, Hausdorff dimension, performance work | **NON-GOALS** (§13) |

An implementer starting cold reads §0 and §12 of this file, and the open
findings + registered predictions of `sos_measure_report.md`. The engine
they extend is `sosl/sosl/quant/` — its README is the source map, its
`algorithm.md` the soundness argument. Do not read `docs/HISTORY.md`.

**Normative math.** `research_notes/sos_measure.md` (the paper). Where this
spec and the paper disagree, the paper wins and the disagreement is a bug to
report in `sos_measure_report.md`.

## 0. Ground rules (read first, they are all mandatory)

- **Package**: the engine is `sosl/sosl/quant/` (placement provisional —
  a move under `sosl/sosl/sos/` needs a user go-ahead). Test scripts go in
  `sosl/tests/quant/`, logs in `sosl/tests/quant/logs/` (never `/tmp`),
  validated `.md`/`.csv` in `reference/quant/`.
- **Layering (hard)**: `sosl.quant` imports `sosl.sos`,
  `sosl.sos.calculus` and the classify scans, and NOTHING else in the
  repo — never `sosl.learn`, `sosl.teacher`, `sosl.experiment`, `tests.*`.
  Do not modify any existing file outside `sosl/sosl/quant/` and
  `sosl/tests/quant/`.
- **Reuse, don't re-derive.** The invariant, its `.sos` reader, `fold`,
  `idem`, `Val`, the linked pairs, the complement surgery, `align` /
  `materialize`, `reduce`, the hulls and the SCC passes all exist under
  `sosl/sosl/sos/` (`invariant.py`, `io/`, `calculus/`) — read
  `calculus/README.md` before writing a line. The measure engine on top of
  them is `sosl/sosl/quant/` (its README is the source map, its
  `algorithm.md` the soundness argument): reuse it, never reimplement it.
- **Numbers are `fractions.Fraction`, end to end.** No `float` in any
  gate. No numpy. No subprocess. The one quarantined float is `entropy`'s
  final `log₂`, widened one ulp outward. Spot appears only inside the
  independent oracles (`routea`), bounded-or-skipped, never waited on — a
  skip is a datum.
- **Type every signature** (params + return), `from __future__ import
  annotations` allowed; follow the typing style of the calculus package.
- **Tests are placed scripts** run as `python3 -m tests.quant.<name>`
  from `sosl/`, one input per invocation where a corpus is walked
  (argv = one `.sos` path), ≤15s per case; a blown budget is a finding
  to report, not something to code around.
- **Files stay under ~500 LOC**, one responsibility each.
- Every public function gets a context-free docstring: what the
  function computes on its own inputs — not who calls it, not the
  campaign it serves.
- **A disagreement with the paper is a finding**, reported in
  `sos_measure_report.md` — never silently "fixed". A fixture
  disagreement means the code is wrong until proven otherwise.

## 12. M6 (QNT5) — the census campaign

Machine reports under `reference/quant/` (one `.md` + one `.csv` per
experiment, date / git-rev / seed / corpus header; `.cat`/CSV sidecar
columns, no JSON). E1 measure+θ-profile columns (distribution per
Wagner degree / safety band); E2 entropy column; E3 the *exact* metric
geometry per alphabet slice — NOT sampled: (a) all μ=0 languages are
one `d_p = 0` class and all μ=1 languages another (skip their pairs
entirely); (b) among the strictly-interior languages, the exact
`d_p = 0` classes are the byte-classes of the reduced essential forms
(paper Thm 4.4) — no pairwise work; re-check a sample of merged and
separated pairs with the aligned xor-profile; (b') the frontier
column: `ltl_up_to_null` per language — report how many non-LTL
census languages are null-equivalent to LTL ones; (c) exhaustive
all-pairs `d_p`
between class representatives (the M1 census counts make this a few
`10^5` alignments at worst) — report diameter, distance distribution,
clustering by Wagner degree, nearest-LTL-neighbor per non-LTL
language; E4 pipeline demo (one spec, a family of chains,
baseline = Route A route; wall-clock + spec-side artifact stability).
Per-case budget 15s; blown budget is a datum. Every number destined
for the paper lands first as a finding row in `sos_measure_report.md`
with its regeneration command.

## 13. Non-goals

- **MDPs / schedulers**: refused (branching wall, paper §4.3).
- **Semiring-valued `Val`**: future work, paper §7 last paragraph.
- **Hausdorff dimension**: not until entropy has landed.
- **Performance work of any kind**: census sizes are small; exactness
  and replayability outrank speed everywhere.
