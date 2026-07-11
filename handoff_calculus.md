# Handoff — SoS calculus

Bootstraps a fresh session on `research_notes/sos_calculus_spec.md`. Read this,
then only the spec section for the task at hand.

## TODO — engineering (spec §9, in order)

1. **§9.3 CAL6 — alphabet hygiene. NEXT.** `free_aps` / `drop_ap` /
   `rename_equal` in `calculus.surgery`. The corpus pipeline already carries the
   pieces (`sos.minimize.remove_free_aps`, `sos.relabel.canonical_relabeling`) —
   lift and share, do not duplicate, and report where they live.
2. **§9.4 corpus-refresh sweep. BLOCKED** on the corpus stream declaring the
   regeneration stable. Then: freeze the corpus, rerun V1a/V1b/V1c/V2/V3 (V4 is
   already on 6222), refresh every measured number in the report in one pass.
3. **Figures** — `sos_calculus_figures.md`; paper §8.7 wants the invariant and
   the aligned product rendered.

Non-goals stand (frontier ops, NBA exits, CLI, learner integration).

## TODO — theory

- **DELA adequacy proposition** (paper §7.3 ⟨TBD⟩) — sketch in the extensions
  memo; check Le Saëc / saturating right congruences in `papers/` first.
- **Integrate V4** — paper §8.5's ⟨TBD⟩ is answered by report findings F15–F19;
  and **every other number in paper §8 is on the wrong corpus** (report-era 3938
  against today's 6222). The report's *For theory* section states both. Until
  §9.4 runs, the report — not the paper — is the source of truth for every
  measured value.
- Then the **mixed product** `K × 𝒞` (`sos_calculus_extensions.md` §1) — model
  checking against a system without entry, the load-bearing one.

## What exists

- **The package** `sosl/sosl/sos/calculus/` — table / surgery / align / product /
  decide / reduce / witness. Soundness harness 1–8 green in `sosl/tests/calculus/`.
- **The hull and obligation read-offs** in `calculus.surgery` — `live` /
  `safety_closure` / `interior` / `liveness_part`, exact `is_safety` /
  `is_cosafety` fixpoints, `is_obligation` (stem verdict + R-class constancy, one
  Tarjan pass over the right-Cayley graph), `obligation_degree` (longest
  θ-alternating DAG paths → `(n⁺, n⁻)`). Gates: `hulls.py`, `obligation_oracle.py`
  (corpus-wide against the `.cat` Wagner coordinates, green on every row).
- **The experiments**, each `reference/calculus/*.{md,csv}` + a report section:
  V1a align ratio, V1b op ledger, V1c pipeline, V2 stutter, V3 blow-up (all on
  the report-era 3938 corpus), E-CAL-EX running-example gate, and **V4** the
  classification battery (`v4_ladder.py`, on 6222: **6222/6222 agreement with
  Spot** on safety / co-safety / obligation, no blown budget).
- Sibling threads with their own handoffs: measure (`sos_measure_spec.md`),
  given-that (`sos_giventhat.md`), extensions (`sos_calculus_extensions.md`).

## Facts worth carrying (each cost a session to learn)

- **Spot has no automaton-level Manna–Pnueli classifier.** `spot.is_obligation` /
  `is_persistence` / `mp_class` are formula-level (`tl/hierarchy.hh`: the formula
  is mandatory, the automaton only an accelerator); `autfilt` offers only
  *structural* `--is-weak` / `--is-terminal`. Translation is no escape — **2484 of
  the 6222 corpus languages are not LTL-definable**, so no formula exists to hand
  it. V4's formula-free oracle instead: `is_safety_automaton` (language-level per
  `twaalgos/strength.hh` — "acceptance can be set to `true` without changing the
  language"), the same on `dualize` for co-safety (exact only on a deterministic
  *complete* automaton — guard the precondition), and `minimize_wdba` +
  equivalence for obligation (Spot's own `ocheck::via_WDBA`, minus the formula).
  `v4_ladder.py --selftest` pins all three against `spot.mp_class`.
- `spot.translate(f, "deterministic", …)` is a *preference*, not a guarantee
  (`F G p` comes back nondeterministic under Büchi output); pass `"generic"` when
  you need an actual DELA.
- **Read Spot's headers** under `opt/spot/include/spot/` — the Python docstrings
  are empty; the headers carry the contracts.
- The `.cat` sidecar condition for obligation is `max(m⁺, m⁻) ≤ 0`, NOT
  `m⁺ = m⁻ = 0`: a `-1` polarity (no chain at all — the empty/universal
  convention) is still an obligation.
- **A gate that shares its answer key checks nothing.** The hand reference in
  `obligation_oracle.py` had a wrong 4-class table for `a*·b^ω` (it merged `A·B`
  into `B`, accepting `(ab)^ω`); the degree read off `(1, 2)` on the wrong algebra
  too, so the error was invisible to the check it sat in. `example_gate.py` catches
  it only because its answer key is built independently (Spot determinizes,
  `core.quotient` canonicalizes).

## Operational facts (save the rediscovery)

- Run everything from `sosl/` as modules: `cd sosl && python3 -m tests.calculus.X`.
  **cwd drifts** if you `cd` elsewhere mid-shell — always `cd` explicitly.
- Corpus: `genaut/corpus/flat_canon/` — `sos/*.sos` (complement-closed, 6222),
  `det/*.hoa` (same basename, deterministic complete DELA), `sos/*.cat` sidecars
  (`sosl.sos.classify.io.parse_cat`; `coords:` is `m⁺ m⁻ n⁺ n⁻`). A concurrent
  stream regenerates it (3938 → 4248 → 6222); all gate numbers are recomputable.
- **Looking a language UP in the corpus** — do not hand-roll this; the procedure is
  genaut's `canon_key` (`genaut/gen/sample.py`; `genaut/README.md` §flat_canon is
  the spec). `flat_canon` holds one file per language **up to renaming its
  symbols**, stored as the `B_k` orbit-min of `𝓘`, not the raw syntactic dump. The
  key is `dump_invariant(canonical_relabeling(remove_free_aps(inv))[1])`, and a
  stored file's bytes *are* that key — the lookup is a text match. Two traps, each
  of which alone turns a present language into an "absent" one: comparing raw `𝓘`
  dumps, and the **AP name** (part of the canonical bytes — the corpus spells its
  APs `a, b, …`; build the query language over those names).
  `example_gate.corpus_row` is the worked instance. Sanity rule: the key function
  must be a **fixpoint on the corpus's own files** before you trust it to say
  "absent".
- Spot 2.14.5 is importable (`import spot`). Bounded-or-skipped, never waited on.
  Per-state emptiness on a det HOA: `aut.set_init_state(q)` + `aut.is_empty()`
  works on generic (EL) acceptance; restore the init state.
- Lasso replay against a det HOA: `sosl.teacher.whitebox.HoaTeacher.of_hoa(path)
  .member(lasso)` (do not hand-parse letters); its compiled `_dst[mask][state]`
  table is the precedent-sanctioned way to walk run states in a test.
- Experiment pattern (see `v2_stutter.py`, `v4_ladder.py`): `--one <case>` +
  `--campaign` with per-case watchdog and a checkpoint file in
  `tests/calculus/logs/` (gitignored); validated `.md`/`.csv` copied to
  `reference/calculus/` with a 4-line header (date, git rev, seed, corpus).

## Gotchas

- **Engineering does not edit the paper.** `sos_calculus.md` is theory's; results
  land in `sos_calculus_report.md` and theory integrates them — including the
  ⟨TBD⟩ slots a work order says it "fills" (that means *answers*, in the report).
  When a paper number looks wrong or stale, say so in the report; do not fix it in
  place.
- **Concurrent sessions** commit to this same repo (learner campaign / corpus
  regeneration / figs). Git history and unfamiliar modified files are NOT yours —
  commit ONLY your files by explicit path. Repo discipline is `CLAUDE.md`'s; this
  file does not restate it.
