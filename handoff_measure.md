# Handoff — SoS quantitative (measure / distance / entropy)

Bootstraps a fresh session on the quantitative thread. Read this, then
only the file and section named for the task at hand — nothing else.

## The five files (all under `research_notes/`)

| role | file | rule |
|---|---|---|
| **paper** (normative math) | `sos_measure.md` | where spec and paper disagree, the paper wins; a disagreement is a finding, reported in the report — never silently "fixed" |
| **spec** (engineering direction) | `sos_measure_spec.md` | milestones M1–M6; §0 ground rules are mandatory; an implementer reads §0 + the milestone section only |
| **report** (results interface) | `sos_measure_report.md` | every finding lands here with its regeneration command; the paper cites no artifact — the report carries reproducibility |
| **figures** | `sos_measure_figures.md` | FIG specs on the toltl model; artifact dir `sos_measure_figs/` (to create) |
| memo (the map, historical) | `sos_quantitative.md` | superseded by the paper for math; do not work from it |

## State (2026-07-11)

- **Theory: paper complete modulo data.** §3 (generic-verdict theorem,
  Bernoulli + Markov-product forms) and §4.2 (shadow Prop 4.1,
  measure-blind topology Cor 4.2, residual-series Prop 4.3, essential
  form Thm 4.4, measure-independence Prop 4.5) at full rigor, ironed;
  §5 entropy proved; §6 and the abstract headline are ⟨TBD⟩ slots
  awaiting E-campaign data. References grounded in `papers/` (two
  placeholders pending: PRISM CAV'11, Chatterjee–Doyen–Henzinger
  ToCL'10 — do not cite them until in library and read).
- **Engineering: M1, M2 DONE and accepted; M3 DONE, F-M3 filed,
  awaiting theory reply.** Engine in `sosl/sosl/quant/`
  (`chain`/`kernel`/`theta`/`measure` + `routea` + `distance`/`shadow`/
  `essential`; placement provisional, to move under `sosl/sosl/sos/` on
  some later go-ahead). M1: flip law 4248/4248 (F-M1). M2: Route A
  oracle exact 4248/4248, laws L2–L5 green (F-M2; accepted, Thm 3.4
  corpus-tested). M3: fixtures F-D..F-I green (F-D/F-E were owed by M2,
  built at M3 start; F-G control held); cases 6222/6222 (Prop 4.5
  byte-exact on all), pairs 993/1000, triples 497/500, 0 red anywhere
  (`reference/quant/m3_laws.md` + csvs, finding F-M3). Census data:
  5660/6222 LTL-up-to-null, 1922 of them carrying a measure-invisible
  group; essential trivial on 5164.

## TODO — the open items, in order

1. **Theory reply to F-M3** — then M4 becomes the work order.
2. **M4 (spec §10)** — entropy; the only float-bearing module
   (certified Collatz–Wielandt enclosure); `h(cl(L)) = h(L)` asserted
   structurally, not on floats.
3. **M5 (spec §11)** — the Markov product `Pr_M(L)`; needs a `.mc`
   chain format fixed with the corpus keeper first.
4. **M6 (spec §12)** — the census campaign E1–E4; fills the paper's §6
   and abstract ⟨TBD⟩ slots through report findings only.
5. **Figures** — FIG-1/2/3 buildable NOW on M1 (specs in the figures
   file; probes under `tests/quant/figs/`); FIG-4 blocked on M3, FIG-5
   on M4/M6.
6. **Theory follow-ups (user-gated, not self-serve):** fill the paper's
   ⟨TBD⟩ slots from report findings when campaigns land; Markov-source
   analogue of the essential form is deliberately unclaimed (paper
   fences it); the weighted/semiring direction is future work.

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

## Gotchas

- **Concurrent sessions** commit to this repo (calculus, corpus,
  learner, figs). Unfamiliar modified files are NOT yours: commit only
  your files by explicit path — `git add <paths> && git commit -F -
  -- <paths>` in one breath (a bare `commit` sweeps the other
  session's staged index; it has happened) — never `git add -A`,
  never touch history.
- Committing needs the user's go-ahead; pushing is always asked
  separately, every time.
- The paper is not a log: no process language, no "we changed X",
  definitions before use (its §2 now carries the full kit — extend it
  there if a new notion is needed, never inline mid-proof).
- `docs/HISTORY.md` is append-only via shell and never read.
- Fixture disagreements: the code is wrong until proven otherwise; if
  you believe a fixture is wrong, STOP and file a finding against the
  paper in the report.
