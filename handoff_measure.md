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

## State (2026-07-11)

- **Theory: paper complete modulo data.** §3 (generic-verdict theorem,
  Bernoulli + Markov-product forms) and §4.2 (shadow Prop 4.1,
  measure-blind topology Cor 4.2, residual-series Prop 4.3, essential
  form Thm 4.4, measure-independence Prop 4.5) at full rigor, ironed;
  §5 entropy proved; §6 and the abstract headline are ⟨TBD⟩ slots
  awaiting E-campaign data. References grounded in `papers/` (two
  placeholders pending: PRISM CAV'11, Chatterjee–Doyen–Henzinger
  ToCL'10 — do not cite them until in library and read).
- **Engineering: M1, M2, M3, M4+M3b DONE (F-M1..F-M4, all accepted).** Engine in `sosl/sosl/quant/`
  (`chain`/`kernel`/`theta`/`measure` + `routea` + `distance`/`shadow`/
  `essential` + `entropy`; placement provisional, to move under
  `sosl/sosl/sos/` on some later go-ahead). M1: flip law 4248/4248
  (F-M1). M2: Route A oracle exact 4248/4248, laws L2–L5 green (F-M2;
  accepted, Thm 3.4 corpus-tested). M3: fixtures F-D..F-I green (F-G
  control held); cases 6222/6222 (Prop 4.5 byte-exact on all), pairs
  993/1000, triples 497/500, 0 red anywhere
  (`reference/quant/m3_laws.md` + csvs, finding F-M3). Census data:
  5660/6222 LTL-up-to-null, 1922 of them carrying a measure-invisible
  group; essential trivial on 5164. M4: fixtures F-J..F-L green
  (golden mean by rational sign test); cases 6222/6222, 0 red, 0
  non-converged, 0 budget-blown; monotonicity pairs 1000/1000
  (`reference/quant/m4_entropy.md` + csvs). M3b: Thm 4.4(2)
  biconditional green 999/1000 on M3's seed-1 sample, 316
  null-disagreement = 316 essential-equal
  (`reference/quant/m3b_thm442.{md,csv}`; both in finding F-M4).

## Work items — Theory

1. ~~Reply to F-M3~~ DONE (2026-07-11): accepted in the report with
   the M3b addendum (spec §9.1) and a rewritten §10; E1 prediction
   registered (5164 with μ∈{0,1}, split 2582/2582).
1b. ~~Reply to F-M4 + ratify P-M5~~ DONE (2026-07-11): F-M4 accepted
   (CW common-denominator deviation ratified, spec §10 amended; E2
   prediction registered: zero census rows with `μ > 0` and
   `ρ < |Σ|`); P-M5 RATIFIED on all three points — Moore convention,
   PRISM subset (well-formedness normative), **initial letter
   INCLUDED in the word** — spec §11 rewritten as the full M5 work
   order (fixtures F-M/F-N/F-O, four gates, Bernoulli-embedding law
   replacing the one-state Mealy cross-check). Then promoted on user
   go: the paper's §2.3/§3.5 now state the chain model
   state-labelled NATIVELY (`(Q, P, ι, ℓ)`, path word, Bernoulli
   chain `B_p`; Thm 3.4 = the `B_p` case; Mealy is the embedded
   convention) — proof unchanged, spec already Moore-native.
2. **Fill the paper's ⟨TBD⟩ slots** from report findings as campaigns
   land (§6 + abstract headline wait on M6; F-M3's census numbers —
   5660/6222 LTL-up-to-null, the 1922 measure-invisible groups — are
   candidate §6(iv) material, user-gated).
3. **References**: PRISM CAV'11 and Chatterjee–Doyen–Henzinger ToCL'10
   still placeholders — get them into `papers/`, read, then cite.
4. Fenced, deliberately unclaimed: Markov-source analogue of the
   essential form; weighted/semiring direction is future work.

## Work items — Engineering (in order, each gated on the user's go)

1. ~~M4 (spec §10) + M3b~~ DONE (2026-07-11, finding F-M4): engine
   `sosl/sosl/quant/entropy.py`, fixtures3, `m4_gate`, `m3b_gate`;
   all gates green (0 red / 0 non-converged / 0 case budget-kills; 1
   m3b pair kill, a datum). One spec deviation, soundness-neutral and
   recorded in F-M4 + `algorithm.md` §10: the CW iterate is fixed
   point over the COMMON denominator 10⁴⁰ (per-entry
   `limit_denominator` blows up through the lcm). Awaiting theory
   reply.
2. **Convention-flip doc sweep (cheap, do before or with M5).** The
   paper's chain model changed AFTER your M1–M4 docs were written:
   state-labelled is now PRIMARY (`M = (Q, P, ι, ℓ)`, word =
   `ℓ(s₀)ℓ(s₁)…` including the initial letter; Mealy is the embedded
   convention; Thm 3.4 = the Bernoulli-chain `B_p` case — see the
   P-M5 reply + addendum in the report). Expected code impact on
   M1–M4: NONE — chains only enter at M5, and μ_p/Bernoulli is
   untouched. But go make sure: sweep your docs (`quant/algorithm.md`,
   `quant/README.md`, any forward-looking M5 text) for paraphrases of
   the old transition-emitting model, "one-state chain emitting all
   letters", or Thm 3.5's old `[ε]` product start, and align them; if
   any *code or gate* turns out to depend on the old convention,
   that's a finding — report it, don't silently adapt.
3. **M5 (spec §11)** — the Markov product `Pr_M(L)`. NEXT, on the
   user's go; P-M5 is RATIFIED (2026-07-11) and spec §11 is the
   complete work order, written against the NEW convention: `.mc` =
   restricted PRISM-language subset, state-labelled (Moore), exact
   rationals in source, word INCLUDES the initial state's letter
   (`word = ℓ(s₀)ℓ(s₁)…`; product starts at `(q₀, λ(ℓ(q₀)))`, reads
   `ℓ(q')` per step). Fixture F-M pins the convention. Stored-chain
   placement stays with the corpus keeper (only needed at M6/E4).
4. **M6 (spec §12)** — the census campaign E1–E4; fills the paper's §6
   and abstract ⟨TBD⟩ slots through report findings only.
5. **Figures** — FIG-1/2/3 **DONE (2026-07-11)**: artifact
   `research_notes/sos_measure_figs/` (index `figures.md`, `Makefile`,
   `reproduction.md`, `notes.md`, PNGs in `img/`, canonical `.sos`
   sources F-D/F-E in `sources/`); probes in `sosl/tests/quant/figs/`
   (`fig1`, `fig2`+`fig2_draw`, `fig3`, shared `tikz`/`cayley`,
   `sources.py`). `make -C research_notes/sos_measure_figs` rebuilds
   tex+png; every value read off the tested `sosl.quant` engine, probes
   own placement only. FIG-1/2/3 **placed in the paper**
   (§3.1/§3.4/§4.1, 2026-07-11). FIG-4 now unblocked by M3 (its own
   session); FIG-5 blocked on M4/M6.
6. Deferred until a user go-ahead: move `sosl/sosl/quant/` under
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
