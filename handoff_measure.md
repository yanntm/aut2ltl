# Handoff — SoS quantitative (measure / distance / entropy)

Bootstraps a fresh session on the quantitative thread. Read this, then
only the file and section named for the task at hand — nothing else.

## The files (all under `research_notes/`)

| role | file | rule |
|---|---|---|
| **paper** (normative math) | `sos_measure.md` | where spec and paper disagree, the paper wins; a disagreement is a finding, reported in the report — never silently "fixed" |
| **spec** (engineering direction) | `sos_measure_spec.md` | §0 ground rules are mandatory; an implementer reads §0 + the milestone section only |
| **report** (results interface) | `sos_measure_report.md` | every finding lands here with its regeneration command; the paper cites no artifact — the report carries reproducibility |
| **figures** | `sos_measure_figures.md` | FIG specs; artifact dir `sos_measure_figs/` |
| frozen | `sos_measure_experiments.md` | the closed work orders and the theory↔engineering exchanges that settled them; reference only, never worked from |
| memo (historical) | `sos_quantitative.md` | superseded by the paper for math; do not work from it |

## State

- **Theory: the paper is complete modulo data.** §3 (generic-verdict
  theorem, Bernoulli and Markov-product forms), §4 (shadow, measure-blind
  topology, residual series, essential form, measure-independence) and §5
  (entropy) are proved and ironed. §6 and the abstract headline are ⟨TBD⟩
  slots awaiting the M6 campaign.
- **Engineering: M1–M5 are done and green corpus-wide** (findings
  F-M1..F-M5 in the report, machine artifacts under `reference/quant/`).
  The engine is `sosl/sosl/quant/`: measure and θ-profile
  (`chain`/`kernel`/`theta`/`measure`), the independent oracles
  (`routea`), distance and the null-set quotient (`distance`/`shadow`/
  `essential`), entropy (`entropy`), and the Markov product
  (`mc`/`product`). Its README is the source map, its `algorithm.md` the
  soundness argument; gates live in `sosl/tests/quant/`.

## Work items — Theory

1. **Verdict on F-M5** (the Markov product). It carries one finding
   against the ratified `.mc` format: our letters render as Boolean cubes
   (`a&!b`) and a PRISM label name must be a plain identifier, so
   "the same file loads unmodified in PRISM and Storm" holds only up to
   label-name sanitization. No number moves — the word convention, the
   clause that decides the answer, is intact and pinned by fixture F-M.
   Remedy agreed with the user: a sanitizing printer at E4. Decide
   whether the `.mc` format description must say so.
2. **Fill the paper's ⟨TBD⟩ slots** from report findings as campaigns
   land. §6 and the abstract headline wait on M6; F-M3's census numbers
   (LTL-up-to-null, the measure-invisible groups) are candidate §6(iv)
   material, user-gated.
3. **References**: PRISM CAV'11 and Chatterjee–Doyen–Henzinger ToCL'10
   are still placeholders — get them into `papers/`, read, then cite.
4. **Drop the paper's last alternative-convention mention**: the §2.3
   parenthetical "(Transition-emitting chains embed: …)". The chain model
   is state-labelled everywhere else; decide whether the remark earns its
   keep.
5. Fenced, deliberately unclaimed: the Markov-source analogue of the
   essential form; the weighted/semiring direction is future work.

## Work items — Engineering (in order, each gated on the user's go)

1. **M6 (spec §12)** — the census campaign E1–E4. Fills the paper's §6
   and abstract ⟨TBD⟩ slots, through report findings only. The report
   carries two cross-gate laws the campaign must *assert* (they are free —
   E1–E3 compute both sides anyway, and a violation convicts M1/M3/M4).
   E4 is where PRISM actually runs the `.mc` files: it owns the label-name
   sanitizing printer and the stored-chain placement decision with the
   corpus keeper.
2. **Figures** — FIG-1/2/3 are built and placed in the paper; the
   artifact is `research_notes/sos_measure_figs/` (`make` rebuilds
   tex+png), its probes `sosl/tests/quant/figs/`. FIG-4 is unblocked (its
   own session); FIG-5 is blocked on M6.
3. Deferred until a user go-ahead: move `sosl/sosl/quant/` under
   `sosl/sosl/sos/`.

Implementation starts only on the user's go. One milestone per pass; stop
and hand back at each DONE (the spec's milestone section says exactly what
DONE means).

## Operational facts (save the rediscovery)

- Run from `sosl/` as modules: `cd sosl && python3 -m tests.quant.X`. cwd
  drifts mid-shell — always `cd` explicitly (commits from the repo root,
  tests from `sosl/`).
- Corpus: `genaut/corpus/flat_canon/` — `sos/*.sos` invariants
  (complement-closed), `det/*.hoa` the paired deterministic complete DELA
  (same basename — the oracle's input), `sos/*.cat` sidecars
  (`sosl.sos.classify.io.parse_cat`; `coords:` is `m⁺ m⁻ n⁺ n⁻`, the
  Wagner data for M6's per-degree splits). A concurrent stream regenerates
  the corpus, so counts move — rerun a gate rather than trust a stale
  number.
- Reuse the engine; never reimplement `fold`/`idem`/`Val`/complement or
  the SCC passes (they live under `sosl/sosl/sos/`, see spec §0 for the
  grep hints).
- Numbers are `fractions.Fraction` everywhere except the quarantined
  eigenvalue in `entropy`; no numpy, no floats in gates; probabilities
  render as fractions (`2/3`) in every human-facing artifact, figures
  included.
- Tests/probes: single-input argv, ≤ 15 s per case, long output to
  `sosl/tests/quant/logs/` (gitignored), validated `.md`/`.csv` to
  `reference/quant/` with the 4-line header (date, git rev, seed, corpus).
- Spot 2.14.5 imports (`import spot`); bounded-or-skipped, never waited
  on; a skip is a datum.
- PRISM 4.10.1 is dropped in `opt/prism-4.10.1-linux64-x86/bin/prism`
  (gitignored, unwired) — E4's model checker, and the arbiter of what
  `.mc` text will actually parse. Nothing in M1–M5 invokes it.

## Gotchas

- **Concurrent sessions** commit to this repo (calculus, corpus, learner,
  figs). Unfamiliar modified files are NOT yours: commit only your files
  by explicit path — `git add <paths> && git commit -F - -- <paths>` in
  one breath (a bare `commit` sweeps the other session's staged index; it
  has happened) — never `git add -A`, never touch history.
- The paper is not a log: no process language, no "we changed X",
  definitions before use (§2 carries the full kit — extend it there if a
  new notion is needed, never inline mid-proof).
- Fixture disagreements: the code is wrong until proven otherwise; if you
  believe a fixture is wrong, STOP and file a finding against the paper in
  the report.
- `docs/HISTORY.md` is append-only via shell and never read.
