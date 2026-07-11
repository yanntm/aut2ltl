# Handoff — SoS calculus

Bootstraps a fresh session on `research_notes/sos_calculus_spec.md`. Read this,
then only the spec section for the task at hand.

## State (2026-07-11 pm): paper RESTRUCTURED; engineering queue = spec §9

- **Paper restructure (theory, 2026-07-11)** — `sos_calculus.md` is now
  ten sections under a new title (*Computing with ω-Regular Languages
  in Canonical Form: …*). Renumber map (sister docs already patched):
  Prop 3.3→5.1, 3.4→4.1, 3.5→6.1, Cor 3.6/3.7→6.2/6.3, Thm 3.10→6.6,
  Prop 3.11→6.7; Props 3.1/3.2 and §§3.1–3.3 unchanged. Citation DAG:
  the paper cites **core [SωS26] only**; SωSL/X/N refs removed. New
  content: §2.2 algebraic toolkit (ours to own), §2.3 running example
  `a*·b^ω` **hand-computed, 5 classes — pending machine check**
  (spec §9.1 E-CAL-EX, incl. the `ba·b^ω` counterexample prediction);
  §3.2 alphabet hygiene (free-AP drop, equality up to AP renaming);
  §4 polynomial middle band; §7.3 exits incl. the canonical det-EL
  exit (implemented in the corpus pipeline; **adequacy proposition is
  the open theory item**, see `sos_calculus_extensions.md` status);
  §8 evaluation (all numbers, report-era 3938 corpus, refresh pending —
  corpus now 6222). Figures task: `sos_calculus_figures.md`.
- **Engineering queue, in order** (spec §9): 9.1 E-CAL-EX example gate
  → 9.2 V4 classification battery vs Spot (fills paper §8.5 ⟨TBD⟩) →
  9.3 CAL6 alphabet hygiene (lift from corpus pipeline if it exists) →
  9.4 corpus-refresh sweep (BLOCKED on corpus stream) → figures.
- **Theory queue**: DELA adequacy proposition (paper §7.3 ⟨TBD⟩; sketch
  in extensions memo — check Le Saëc / saturating right congruences in
  `papers/` first); then the mixed product (extensions §1).

## Previous state (2026-07-11 am): CAL1–CAL5 DONE; measure M1 DONE, M2 next

- **CAL1–CAL3** — the package `sosl/sosl/sos/calculus/` (table / surgery /
  align / product / decide / reduce / witness), harness 1–8 green
  (`sosl/tests/calculus/`).
- **CAL4** — the experimental campaign: V1a/V1b/V1c/V2/V3 all delivered to
  `reference/calculus/`, paper `⟨TBD⟩` slots filled, report
  `research_notes/sos_calculus_report.md`.
- **CAL5** (this session) — the hull surgeries and obligation read-offs in
  `calculus.surgery`: `live` / `safety_closure` / `interior` / `liveness_part`,
  exact `is_safety` / `is_cosafety` fixpoint tests, `is_obligation` (stem-only
  verdict + R-class constancy via one Tarjan pass over the right-Cayley
  graph), `obligation_degree` (longest θ-alternating DAG paths → `(n⁺, n⁻)`).
  Gates: `tests/calculus/hulls.py` (closure laws, duality, Alpern–Schneider
  decomposition, prefix-liveness replay against the paired det HOA via
  per-state Spot emptiness) and `tests/calculus/obligation_oracle.py`
  (corpus-wide vs the `.cat` Wagner coordinates — green on all rows, degree =
  sidecar on every obligation row; worked reference `a*·b^ω → (1, 2)`).
  Spec correction found while gating: the sidecar condition for obligation is
  `max(m⁺, m⁻) ≤ 0`, NOT `m⁺ = m⁻ = 0` — a `-1` polarity (no chain at all,
  the empty/universal convention) is still an obligation.
- **Measure M1** (2026-07-11) — the quantitative thread now has its own spec
  (`research_notes/sos_measure_spec.md`, normative paper
  `research_notes/sos_measure.md`); M1 is DONE: θ-profile + exact `μ_p(L)` in
  `sosl/sosl/quant/` (chain / kernel / theta / measure; `Fraction` end to end,
  no reduce, `PARANOID` Lemma-3.3 cross-checks on). Package placement is
  provisional (user: move under `sosl/sosl/sos/` later). Gates:
  `tests/quant/fixtures.py` (three hand fixtures, exact, two `p`'s) and
  `tests/quant/flip_gate.py` (`μ(L)+μ(¬L)==1` + negated profiles, one file
  per invocation) — 4248/4248 green. Machine report
  `reference/quant/m1_measure.{md,csv}`; finding F-M1 in
  `research_notes/sos_measure_report.md`. Corpus datum: 1737 / 774 / 1737
  languages at `μ = 0` / interior / `μ = 1` (the 0–1 tie is the corpus's
  complement-closure).

## What remains

No open *implementation* items; spec non-goals stand (frontier ops, NBA exits,
CLI, learner integration). The post-CAL5 audit produced three research-notes
memos — the open directions, in priority order:

- `research_notes/sos_calculus_extensions.md` — paper sections to draft:
  the **mixed product** `K × 𝒞` (model checking against a system without
  entry — the load-bearing one), §3.4 frontier completion + the polynomial
  `X`/prefix-code middle band, LTL-operators-over-SoS, monitor one-liner.
- `research_notes/sos_giventhat.md` — port of [DPT25] (`papers/DuretLutz_…
  2025_ICATPN.pdf`, user is a co-author): the knowledge interval as a lattice
  of pair sets, one-scan safety/co-safety/obligation existence tests (CAL5),
  stutter-quotient conjecture, LTL-given-that end-to-end once `sos2ltl` lands.
- Quantitative thread: M1 closed and theory-ratified (F-M1 + reply in
  `sos_measure_report.md`; the flip law is θ-blind — θ ground truth is
  M2's burden). **M2 is the open work order**: `sos_measure_spec.md` §8,
  self-contained — Route A oracle on the paired `det/*.hoa`
  (deterministic complete EL; no NBA exit exists in the calculus, none
  is needed), laws L1–L5. Then M3 (distance) / M4 (entropy) per the
  status table. Implementation starts only on the user's go.

The corpus is being regenerated by a concurrent work stream (counts moved
3938 → 4248 during CAL5); all gate numbers are recomputable — rerun
`obligation_oracle` after a corpus refresh if a stale count matters.

## Operational facts (save the rediscovery)

- Run everything from `sosl/` as modules: `cd sosl && python3 -m tests.calculus.X`.
  **cwd drifts** if you `cd` elsewhere mid-shell — always `cd` explicitly.
- Corpus: `genaut/corpus/flat_canon/` — `sos/*.sos` (complement-closed),
  `det/*.hoa` (same basename, deterministic complete DELA), `sos/*.cat`
  sidecars (`sosl.sos.classify.io.parse_cat`; `coords:` is `m⁺ m⁻ n⁺ n⁻`).
- Spot 2.14.5 is importable (`import spot`). Bounded-or-skipped, never waited
  on. Per-state emptiness on a det HOA: `aut.set_init_state(q)` +
  `aut.is_empty()` works on generic (EL) acceptance; restore the init state.
- Lasso replay against a det HOA: `sosl.teacher.whitebox.HoaTeacher.of_hoa(path)
  .member(lasso)` (do not hand-parse letters); its compiled `_dst[mask][state]`
  table is the precedent-sanctioned way to walk run states in a test.
- Experiment pattern (see `v2_stutter.py`): `--one <case>` + `--campaign` with
  per-case watchdog and a checkpoint file in `tests/calculus/logs/`
  (gitignored); validated `.md`/`.csv` copied to `reference/calculus/` with a
  4-line header (date, git rev, seed, corpus).

## Gotchas

- **Concurrent sessions** commit to this same repo (learner campaign / corpus
  regeneration / figs). Git history and unfamiliar modified files are NOT
  yours — commit ONLY your files by explicit path, never `git add -A`, never
  touch history.
- Commit style: `git commit -F -` heredoc, terse, several files ok; committing
  needs the user's go-ahead, pushing is always asked separately.
