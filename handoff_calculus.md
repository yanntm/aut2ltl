# Handoff — SoS calculus

Bootstraps a fresh session on `research_notes/sos_calculus_spec.md`. Read this,
then only the spec section for the task at hand.

## State: E-CAL-EX + V4 DONE; engineering queue = spec §9.3 onward

- **V4 (spec §9.2) — DONE**, `sosl/tests/calculus/v4_ladder.py`
  (`--selftest` / `--one <case>` / `--campaign`; full sweep ~4 min),
  reference `reference/calculus/v4_ladder.{md,csv}`, report findings
  **F15–F19**, paper §8.5 filled. **6222/6222 agreement with Spot** on
  safety, co-safety and obligation; no blown budget. Carry three facts:
  - **Spot has no automaton-level Manna–Pnueli classifier.**
    `spot.is_obligation` / `is_persistence` / `mp_class` are
    formula-level (`tl/hierarchy.hh`: the formula is mandatory, the
    automaton only an accelerator); `autfilt` offers only *structural*
    `--is-weak` / `--is-terminal`. And translation is no escape — 2484
    of the 6222 corpus languages are not LTL-definable, so no formula
    exists to hand it. The formula-free oracle V4 uses instead:
    `is_safety_automaton` (language-level per `twaalgos/strength.hh` —
    "acceptance can be set to `true` without changing the language"),
    the same on `dualize` for co-safety (exact only on a deterministic
    *complete* automaton — the script guards the precondition), and
    `minimize_wdba` + equivalence for obligation (Spot's own
    `ocheck::via_WDBA`, minus the formula). `--selftest` pins all three
    against `spot.mp_class` on eight known-class formulas.
  - `spot.translate(f, "deterministic", ...)` is a *preference*, not a
    guarantee (`F G p` comes back nondeterministic under Büchi output);
    pass `"generic"` when you need an actual DELA.
  - Read Spot's headers under `opt/spot/include/spot/`, not the bindings'
    docstrings — the Python docstrings are empty, the headers carry the
    contracts.
- **Paper §8 is marked STALE.** Its preamble now says corpus = 6222, and
  every corpus-derived number in §8 *except* §8.5's V4 bullet is
  report-era 3938. The markers say what to do: re-source each figure from
  `sos_calculus_report.md`, one by one, matched to the finding that
  produced it — never re-typed, never left because it looks close. That
  is spec §9.4's sweep.

- **E-CAL-EX (spec §9.1) — DONE**, `sosl/tests/calculus/example_gate.py`
  (one shot, no argv, ~0.1 s), reference `reference/calculus/example_gate.md`,
  report section (F-EX / F-EX1 / F-EX2), paper §8.7 filled (only its
  *figures* line is still ⟨TBD⟩). Theory's hand computation of `a*·b^ω` is
  confirmed on every value, including the predicted minimal counterexample
  `ba·b^ω` for the reverse inclusion. Nothing for theory to adjudicate.
  Two findings worth carrying:
  - **F-EX1** — the hand reference in `tests/calculus/obligation_oracle.py`
    had **4** classes: it merged `A·B` into `B`, so it accepted `(ab)^ω ∉
    a*·b^ω` (`C² = D`, the loop class is not idempotent). Fixed in place to
    the 5-class table. The degree is `(1, 2)` on the wrong algebra too, so no
    CAL5 number moved — the error was invisible to the check it sat in.
  - **F-EX2** — `a*·b^ω` **is** a corpus row (`2state1ap1acc_16898`,
    `.cat` coords `0 0 1 2`). See the corpus-lookup rule under *Operational
    facts*: a raw `𝓘`-dump comparison reports it absent.

- **Paper restructure (theory, 2026-07-11)** — `sos_calculus.md` is now
  ten sections under a new title (*Computing with ω-Regular Languages
  in Canonical Form: …*). Renumber map (sister docs already patched):
  Prop 3.3→5.1, 3.4→4.1, 3.5→6.1, Cor 3.6/3.7→6.2/6.3, Thm 3.10→6.6,
  Prop 3.11→6.7; Props 3.1/3.2 and §§3.1–3.3 unchanged. Citation DAG:
  the paper cites **core [SωS26] only**; SωSL/X/N refs removed. New
  content: §2.2 algebraic toolkit (ours to own), §2.3 running example
  `a*·b^ω` (hand-computed, 5 classes — **machine-checked, green**, §8.7);
  §3.2 alphabet hygiene (free-AP drop, equality up to AP renaming);
  §4 polynomial middle band; §7.3 exits incl. the canonical det-EL
  exit (implemented in the corpus pipeline; **adequacy proposition is
  the open theory item**, see `sos_calculus_extensions.md` status);
  §8 evaluation (all numbers, report-era 3938 corpus, refresh pending —
  corpus now 6222). Figures task: `sos_calculus_figures.md`.
- **Engineering queue, in order** (spec §9): ~~9.1 E-CAL-EX~~ (done)
  → ~~9.2 V4 classification battery vs Spot~~ (done) →
  **9.3 CAL6 alphabet hygiene — NEXT** (`free_aps` / `drop_ap` / `rename_equal`;
  the corpus pipeline already has the pieces — `sos.minimize.
  remove_free_aps` and `sos.relabel.canonical_relabeling` — so lift and
  share, do not duplicate) → 9.4 corpus-refresh sweep (BLOCKED on the
  corpus stream) → figures (`sos_calculus_figures.md`; paper §8.7 still
  wants the invariant + aligned product rendered).
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

The open *implementation* items are the spec §9 queue above (9.2 V4 → 9.3 CAL6
→ 9.4 refresh → figures); the spec's non-goals stand (frontier ops, NBA exits,
CLI, learner integration). Beyond the queue, the post-CAL5 audit produced three
research-notes memos — the open *directions*, in priority order:

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
3938 → 4248 → **6222**; the paper §8 numbers are still report-era 3938, which
is what §9.4 exists to fix). All gate numbers are recomputable — rerun
`obligation_oracle` after a corpus refresh if a stale count matters.

## Operational facts (save the rediscovery)

- Run everything from `sosl/` as modules: `cd sosl && python3 -m tests.calculus.X`.
  **cwd drifts** if you `cd` elsewhere mid-shell — always `cd` explicitly.
- Corpus: `genaut/corpus/flat_canon/` — `sos/*.sos` (complement-closed),
  `det/*.hoa` (same basename, deterministic complete DELA), `sos/*.cat`
  sidecars (`sosl.sos.classify.io.parse_cat`; `coords:` is `m⁺ m⁻ n⁺ n⁻`).
- **Looking a language UP in the corpus** (F-EX2 — do not hand-roll this; the
  procedure is genaut's `canon_key`, `genaut/gen/sample.py`, and `genaut/README.md`
  §flat_canon is the spec). `flat_canon` holds one file per language **up to
  renaming its symbols**, stored as the `B_k` orbit-min of `𝓘`, not the raw
  syntactic dump. So the key is
  `dump_invariant(canonical_relabeling(remove_free_aps(inv))[1])`
  (`sosl.sos.relabel` / `sosl.sos.minimize` / `sosl.sos.io`), and a stored file's
  bytes *are* that key — the lookup is a text match, no per-file refolding. Two
  traps, each of which alone turns a present language into an "absent" one:
  comparing raw `𝓘` dumps, and the **AP name** (part of the canonical bytes —
  the corpus spells its APs `a, b, …`; build the query language over those
  names). `example_gate.corpus_row` is the worked instance. Sanity rule: the key
  function must be a **fixpoint on the corpus's own files** before you trust it
  to say "absent" (it is, on all 6222).
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
  yours — commit ONLY your files by explicit path. Repo discipline is
  `CLAUDE.md`'s; this file does not restate it.
