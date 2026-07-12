# Handoff — SoS quantitative (measure / distance / entropy)

Bootstraps a fresh session on the quantitative thread. Read this, then
only the file and section named for the task at hand — nothing else.

## The five files (all under `research_notes/`)

| role | file | rule |
|---|---|---|
| **paper** (normative math) | `sos_measure.md` | where spec and paper disagree, the paper wins; a disagreement is a finding, reported in the report — never silently "fixed" |
| **spec** (engineering direction) | `sos_measure_spec.md` | milestones M1–M6; §0 ground rules are mandatory; an implementer reads §0 + the milestone section only |
| **report** (results interface) | `sos_measure_report.md` | every finding lands here with its regeneration command; the paper cites no artifact — the report carries reproducibility |
| **figures** | `sos_measure_figures.md` | FIG specs; artifact dir `sos_measure_figs/` — **FIG-1/2/3 built (2026-07-11)**, FIG-4/5 open |
| memo (the map, historical) | `sos_quantitative.md` | superseded by the paper for math; do not work from it |

## State

- **Theory: paper complete modulo data.** §3 (generic-verdict theorem,
  Bernoulli + Markov-product forms) and §4.2 (shadow Prop 4.1,
  measure-blind topology Cor 4.2, residual-series Prop 4.3, essential
  form Thm 4.4, measure-independence Prop 4.5) at full rigor, ironed;
  §5 entropy proved; §6 and the abstract headline are ⟨TBD⟩ slots
  awaiting E-campaign data. References grounded in `papers/` (two
  placeholders pending: PRISM CAV'11, Chatterjee–Doyen–Henzinger
  ToCL'10 — do not cite them until in library and read).
- **Engineering: M1–M5 DONE.** F-M1..F-M4 accepted; **F-M5 awaits a
  theory verdict**. Engine in `sosl/sosl/quant/`
  (`chain`/`kernel`/`theta`/`measure` + `routea` + `distance`/`shadow`/
  `essential` + `entropy` + `mc`/`product`; placement provisional, to
  move under `sosl/sosl/sos/` on some later go-ahead). M1: flip law
  4248/4248 (F-M1). M2: Route A oracle exact 4248/4248, laws L2–L5
  green (F-M2; accepted, Thm 3.4 corpus-tested). M3: fixtures F-D..F-I
  green (F-G control held); cases 6222/6222 (Prop 4.5 byte-exact on
  all), pairs 993/1000, triples 497/500, 0 red anywhere
  (`reference/quant/m3_laws.md` + csvs, finding F-M3). Census data:
  5660/6222 LTL-up-to-null, 1922 of them carrying a measure-invisible
  group; essential trivial on 5164. M4: fixtures F-J..F-L green
  (golden mean by rational sign test); cases 6222/6222, 0 red, 0
  non-converged, 0 budget-blown; monotonicity pairs 1000/1000
  (`reference/quant/m4_entropy.md` + csvs). M3b: Thm 4.4(2)
  biconditional green 999/1000 on M3's seed-1 sample, 316
  null-disagreement = 316 essential-equal
  (`reference/quant/m3b_thm442.{md,csv}`; both in finding F-M4). M5:
  fixtures F-M..F-O green (F-M pins the word convention); Bernoulli
  embedding 6222/6222 byte-exact against M1 (both `p`'s, chain
  restarted at each letter state), complement flip 6222/6222, `.mc`
  round-trip, Route A product-side oracle 250/250 with 0 Spot skips
  (`reference/quant/m5_product.{md,csv}` + oracle csv, finding F-M5).

## Work items — Theory

1. **Verdict on F-M5** (the Markov product; report). It carries one
   finding against the ratified P-M5: PRISM 4.10.1 will not parse our
   label names — our letters render as Boolean cubes (`a&!b`) and a
   PRISM label name must be a plain identifier, so P-M5's "the same file
   loads unmodified in PRISM and Storm" holds only up to label-name
   sanitization. No number moves (M5 runs no PRISM; the word convention,
   the clause that decides the answer, is intact and now pinned by
   fixture F-M). Agreed remedy: a sanitizing printer at E4. Decide
   whether spec §11.1 should say so.
2. **Fill the paper's ⟨TBD⟩ slots** from report findings as campaigns
   land (§6 + abstract headline wait on M6; F-M3's census numbers —
   5660/6222 LTL-up-to-null, the 1922 measure-invisible groups — are
   candidate §6(iv) material, user-gated).
3. **References**: PRISM CAV'11 and Chatterjee–Doyen–Henzinger ToCL'10
   still placeholders — get them into `papers/`, read, then cite.
4. **Drop the paper's last alternative-convention mention**: the §2.3
   parenthetical "(Transition-emitting chains embed: …)". The chain
   model is state-labelled everywhere else in the corpus of documents;
   decide whether the embedding remark earns its keep or goes.
5. Fenced, deliberately unclaimed: Markov-source analogue of the
   essential form; weighted/semiring direction is future work.

## Work items — Engineering (in order, each gated on the user's go)

1. **M6 (spec §12)** — the census campaign E1–E4. NEXT, on the user's
   go; fills the paper's §6 and abstract ⟨TBD⟩ slots through report
   findings only. Theory's E1 and E2 predictions are registered in the
   report (the F-M3 and F-M4 replies). E4 (the pipeline demo) is where
   PRISM/Storm actually run the `.mc` files — it owns the label-name
   sanitizing printer (see theory item 1) and the stored-chain
   placement decision with the corpus keeper.
2. **Figures** — FIG-1/2/3 built and placed in the paper
   (§3.1/§3.4/§4.1): artifact `research_notes/sos_measure_figs/`
   (index `figures.md`, `Makefile`, `reproduction.md`, `notes.md`,
   PNGs in `img/`, canonical `.sos` sources F-D/F-E in `sources/`);
   probes in `sosl/tests/quant/figs/` (`fig1`, `fig2`+`fig2_draw`,
   `fig3`, shared `tikz`/`cayley`, `sources.py`).
   `make -C research_notes/sos_measure_figs` rebuilds tex+png; every
   value read off the tested `sosl.quant` engine, probes own
   placement only. FIG-4 unblocked by M3 (its own session); FIG-5
   blocked on M6.
3. Deferred until a user go-ahead: move `sosl/sosl/quant/` under
   `sosl/sosl/sos/`.

Implementation starts only on the user's go. One milestone per pass;
stop and hand back at each DONE (the spec's milestone sections say
exactly what DONE means).

## Operational facts (save the rediscovery)

- Run from `sosl/` as modules: `cd sosl && python3 -m tests.quant.X`.
  cwd drifts mid-shell — always `cd` explicitly (commits from repo
  root, tests from `sosl/`).
- Corpus: `genaut/corpus/flat_canon/` — `sos/*.sos` invariants
  (complement-closed), `det/*.hoa` paired deterministic complete DELA
  (same basename — M2's oracle input), `sos/*.cat` sidecars
  (`sosl.sos.classify.io.parse_cat`; `coords:` is `m⁺ m⁻ n⁺ n⁻` —
  Wagner data for M6's per-degree splits). A concurrent stream
  regenerates the corpus; counts may move — rerun gates rather than
  trusting stale numbers.
- M1 engine: `sosl/sosl/quant/` (`chain` / `kernel` / `theta` /
  `measure`; `PARANOID` flag on). Reuse it — never reimplement
  `fold`/`idem`/`Val`/complement (they live under `sosl/sosl/sos/`,
  see spec §0 for the grep hints).
- Numbers are `fractions.Fraction` everywhere except M4's quarantined
  eigenvalue; no numpy, no floats in gates; probabilities render as
  fractions (`2/3`) in every human-facing artifact, figures included.
- Tests/probes: single-input argv, ≤ 15 s per case, long output to
  `sosl/tests/quant/logs/` (gitignored), validated `.md`/`.csv` to
  `reference/quant/` with the 4-line header (date, git rev, seed,
  corpus).
- Spot 2.14.5 imports (`import spot`); bounded-or-skipped, never
  waited on; a skip is a datum. M2's per-state trick on a det HOA:
  `aut.set_init_state(q)` + `aut.is_empty()`; restore the init state.
- PRISM 4.10.1 is dropped in `opt/prism-4.10.1-linux64-x86/bin/prism`
  (gitignored, no wiring into `deps/`) — E4's model checker, and the
  arbiter of what `.mc` text it will actually parse. Nothing in M1–M5
  invokes it.

## Gotchas

- **Concurrent sessions** commit to this repo (calculus, corpus,
  learner, figs). Unfamiliar modified files are NOT yours: commit only
  your files by explicit path — `git add <paths> && git commit -F -
  -- <paths>` in one breath (a bare `commit` sweeps the other
  session's staged index; it has happened) — never `git add -A`,
  never touch history.
- The paper is not a log: no process language, no "we changed X",
  definitions before use (its §2 now carries the full kit — extend it
  there if a new notion is needed, never inline mid-proof).
- `docs/HISTORY.md` is append-only via shell and never read.
- Fixture disagreements: the code is wrong until proven otherwise; if
  you believe a fixture is wrong, STOP and file a finding against the
  paper in the report.
