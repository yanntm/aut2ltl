# Handoff — SoS given-that

Bootstraps a fresh engineering session on
`research_notes/sos_giventhat_spec.md`. Read this, then the spec header
and its §0–§3, then only the spec section for the milestone at hand.
Do NOT start from the paper — the spec is the work order; the paper is
the normative math you consult when the spec points at it.

## The three documents and their roles

- **Spec (your work order):** `research_notes/sos_giventhat_spec.md` —
  milestones GT1–GT5, algorithms to the function level, gates,
  acceptance, traps. Where the spec and the paper disagree: STOP and
  report (spec §8/§10), never reconcile silently.
- **Paper (normative math):** `research_notes/sos_giventhat.md` —
  pre-paper draft, 2026-07-11. Section map: paper §3 → GT1, §4 → GT2 +
  GT4, §5 → GT3, §7 → GT5. Its own dependencies:
  `research_notes/sos_calculus.md` [SωSC26] (the calculus you build
  on) and `papers/DuretLutz_Poitrenaud_ThierryMieg_2025_ICATPN.pdf`
  [DPT25] (the automata-side original; the user is a co-author).
- **Report (your channel back to theory):**
  `research_notes/sos_giventhat_report.md` — pre-named finding slots
  F1–F15 + a **To theory** section. Fill slots as milestones close;
  anything surprising goes to To theory the moment it is found. This
  file is how you talk to the theory thread; they are waiting on
  specific items listed at its bottom. The report is the traceable
  reproducibility artifact — the paper cites numbers in pure form and
  never an artifact path.
- **Figures (separate commission):**
  `research_notes/sos_giventhat_figures.md` — for a figure-focused
  session; FIG-2 is buildable on the calculus package alone, the rest
  gate on GT1 / GT3 / W0. Probes call the package, never re-implement
  it (the drift rule there).

## State (2026-07-11): GT1 and GT2 DONE — GT3 is the next engineering milestone

- **GT1 (DONE, accepted):** `sosl/sosl/sos/giventhat/interval.py`
  (`Interval`, `given_that`, `k_settles_phi`/`k_refutes_phi`,
  `choose`/`decompose`), `conjugacy_classes` in `calculus.surgery`.
  Gates `tests/giventhat/interval_gate.py` green on the fixture and
  the 700-pair campaign (699 scored, 1 explained F2). Data:
  `reference/giventhat/gt1_interval.md` + `gt1_bits.csv`; report
  F1–F4 filled. Fixture facts: `|𝒞(D_ab)| = 6` (E1 held),
  `|𝒞(D_K)| = 6`, `iv.bits = 2`.
- **GT2 (DONE, accepted):** `sosl/sosl/sos/giventhat/ladder.py` (the
  five `exists_*` rung tests, `forced`, `h_below`, `is_recurrence` /
  `is_persistence`, `rec_hull`), `r_classes` promoted into
  `calculus.surgery`. Gates: `tests/giventhat/ladder_gate.py`
  (`--rung-oracle` / `--one` / `--fixture` / `--pair` / `--campaign`)
  + `tests/giventhat/gt2_summary.py`. Rung oracle **6 222/6 222**
  (paper orientation confirmed, F5); campaign 700/700 with zero gate
  violations; brute lattice oracle exact on all 264 `bits ≤ 12`
  cases; §4.6 fixture green on every prediction, class counts
  included (`|𝒞(¬φ)| = 5`, product 10 — paper §4.6 and the spec
  fixture item state these; `reference/giventhat/gt2_fixture.md` is
  the census). Data: `reference/giventhat/gt2_ladder.md` + two
  csvs; report F5–F8 filled.
- **Policy (2026-07-11):** code duplication in the name of oracle
  "independence" is rejected — `h_below` reuses `classify.primitives`
  (`idempotents` / `leq_h_idem`); the accepted cross-check standard is
  a *different decision path* over shared primitives. Spec §4 and the
  layering law carry the edit.
- Prerequisites all DONE and harness-green: the calculus package
  (CAL1–CAL5, see `research_notes/sos_calculus_spec.md` status table)
  including the hull surgeries, `is_obligation`, `obligation_degree`;
  `sosl.sos.classify` (stutter read-off + primitives). Reuse, never
  reimplement (spec §0 lists exactly what you get).

## TODO — engineering (next session starts here)

1. **GT3 (spec §5, paper §5) — the commissioned milestone.** Tier 1
   first (the stutter-quotient test; verdict type is YES/UNKNOWN,
   trap #11), then tier 2 (the stutter self-alignment — two
   normal-form cases, trap #9; do NOT build `SC`'s automaton,
   trap #12). Fixture regression E2: tier 1 UNKNOWN, tier 2 YES —
   if tier 2 says NO there, tier 2 is wrong. Report slots F9–F11.
2. **GT4 (spec §6) — after GT3; now unblocked by GT2.** Greedy vs
   brute band-degree probe; a disagreement is the experiment working
   (T2) — dossier to F12, do not patch.
3. **GT5/W0 (spec §7)** — after GT3/GT4. W1 stays **blocked on
   external data — do not fetch it**.

## TODO — theory (reads the report's To theory, owes back)

Nothing pending. Next items land here when engineering files a To
theory entry (expected: the GT4 dossier if greedy ≠ brute, the GT3
tier-gap frequency).

## The one theorem to keep in your head

Paper Prop 3.1: on the product table, `P_max \ P_min = P_K^c`, and
the legal `B`s are exactly `P_min ⊔ (union of conjugacy classes
outside P_K)`. Every GT1 structure reifies this sentence, and it runs
as an always-on assertion — if it fires, the bug is upstream
(align / materialize / saturate); report, don't work around.

## Operational facts (save the rediscovery)

- Run everything from `sosl/` as modules:
  `cd sosl && python3 -m tests.giventhat.X`. cwd drifts — always `cd`
  explicitly. Tests live in `sosl/tests/giventhat/` (create it), logs
  in `sosl/tests/giventhat/logs/` (gitignored), never `/tmp`.
- Corpus: `genaut/corpus/flat_canon/` — `sos/*.sos` (canonical,
  complement-closed), `det/*.hoa` (same basename, det complete DELA),
  `sos/*.cat` sidecars (`sosl.sos.classify.io.parse_cat`; `coords:`
  is `m⁺ m⁻ n⁺ n⁻` — GT2's oracle reads these). Counts keep moving
  under a concurrent regeneration (6 222 `.sos` at the GT2 run) —
  recompute, do not hardcode.
- Reuse pointers: `_Corpus` in `sosl/tests/calculus/v1_align.py`
  (invariant/table cache, alphabet strata, content-hash complement
  partner map — never guess partners from filenames); `check_pair` in
  `tests/giventhat/interval_gate.py` is the per-pair gate pattern.
  The GT1 fixture pair builds via `tests.giventhat.fixtures.build()`
  (cached under `logs/fixtures/`, gitignored — a fresh clone rebuilds
  it on first `--fixture` run; canonize keeps input basenames, so one
  tag folder per fixture set works).
- Alphabet strata: `align` asserts equal alphabets; sample pairs
  WITHIN one stratum (calculus spec §8.2 has the recipe).
- Spot 2.14.5 importable (`import spot`), bounded-or-skipped, never
  waited on. Lasso replay against a det HOA:
  `sosl.teacher.whitebox.HoaTeacher.of_hoa(path).member(lasso)` — do
  not hand-parse letters.
- Fixture DELAs are canonized with `genaut/gen/canonize.py` — trust
  its defaults, head its pydoc for the output flag only.
- Experiment pattern (copy `sosl/tests/calculus/v2_stutter.py`):
  `--one <case>` + `--campaign` with per-case 15 s watchdog and a
  checkpoint file; validated `.md`/`.csv` promoted to
  `reference/giventhat/` with the 4-line header (date, git rev, seed,
  corpus).
- Type-annotate every public signature (params + return) — house rule.

## Gotchas

- **Concurrent sessions** commit to this repo (corpus regeneration,
  learner, figs). Unfamiliar modified files are NOT yours — commit
  ONLY your files by explicit path, never `git add -A`, never touch
  history (no reset/rebase/amend, ever).
- Git usage: the repo-wide CLAUDE.md rules apply verbatim (commit your
  work as it progresses, one file per commit preferred, `-F` heredoc,
  never push, never rewrite history). No track-specific git rules.
- Layering law (spec header) is hard: `sosl.sos.giventhat` imports
  `sosl.sos`, `sosl.sos.calculus`, `sosl.sos.classify` — nothing else.
  Test scripts may import anything.
- Read the spec's trap list (§9) BEFORE coding — several traps are
  bugs that type-check and pass casual testing (raw conjugacy inserts,
  a separate universality scan, tier-1 returning NO, a second Tarjan).
- House conventions enforced in review: `__init__.py` carries symbol
  re-exports ONLY — docs live in the package `README.md` (services,
  source map) and `algorithm.md` (the ideas, one level above code).
  No `functools.lru_cache` — an operation cache is an explicit memo
  slot on the owning object (`Table._linked` / `_conjugacy` are the
  idiom). Prefer new files; edit existing files only when really
  necessary (the commissioned `surgery.py` addition was; a
  convenience re-export is not).
