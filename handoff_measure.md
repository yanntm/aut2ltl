# Handoff — SoS quantitative (probability read off the invariant)

Bootstraps a fresh session on the quantitative thread. Read this, then only
the file and section named for the task at hand — nothing else.

## The files (all under `research_notes/`)

| role | file | rule |
|---|---|---|
| **paper** (the draft being written) | `sos_quant.md` | **the plan of record.** A skeleton: sections carry bullets and a provenance tag (`[have]` / `[new]` / `[open]`). Flesh it out; do not re-plan it |
| reservoir (normative math, superseded as a plan) | `sos_measure.md` | the proofs `sos_quant.md` reuses live here, and so does everything it parked. Mine it; do not work *from* it — its structure is the one we moved away from |
| report (results interface) | `sos_measure_report.md` | every finding lands here with its regeneration command. Carries the engine's correctness argument, not the new paper's experiments |
| figures | `sos_measure_figures.md` | FIG specs; artifact dir `sos_measure_figs/` |
| frozen | `sos_measure_experiments.md` | closed work orders (M1–M5) and the exchanges that settled them; reference only, never worked from |
| stale | `sos_measure_spec.md`, `sos_quantitative.md` | the old engineering spec (its M6 census campaign is **not** this paper's evaluation) and the original memo. Do not work from either |

## State

- **Theory: the paper was re-planned and the new draft is a skeleton.**
  `sos_quant.md` is the plan of record. Its thesis: two invariants in — a
  **model** `M` and a **spec** `S` — one exact fraction out; the i.i.d. random
  word is the *degenerate corner* `M = Σ^ω`. Three RQs (the object, the source,
  the identification), three numbers (satisfaction, agreement, the verdict
  distribution). The proofs it reuses are already written in `sos_measure.md`
  and already implemented; the new material is §4 (the verdict distribution),
  §5 (the source is the model's own invariant), and one open theorem (§6.5).
- **The experimental section is *not even started*.** No benchmark exists, no
  numbers exist, nothing has been run for this paper. The 6222-language census
  is **not** its evaluation — that is the classification framework's
  population, and it survives here only as the exhaustive *probe* suite that
  argues the engine is correct. It is pointed at, never reported as a result.
  `sos_quant.md` §7 says what the benchmark must be: **(model, spec) pairs**.
- **Engineering: the bricks are laid.** The engine is `sosl/sosl/quant/` and it
  documents itself — README is the source map, `algorithm.md` the soundness
  argument, gates in `sosl/tests/quant/`, results in `sos_measure_report.md`.
  **Leverage it; do not re-litigate the path that built it.**

## Work items — Theory

1. **Flesh out `sos_quant.md`, without deviating from its plan.** It is a
   skeleton on purpose: every section states what it will contain and where the
   material comes from. Turn the bullets into the paper. Reuse the proofs from
   `sos_measure.md` verbatim where the tag says `[have]` — §2 (the kit), §3 (the
   generic-verdict lemmas, now to be proved **once** for a general source, with
   Bernoulli as the `T = S` instance), §6.1–6.4 (shadow, residual series,
   essential form, measure-independence, the LTL frontier). Write the `[new]`
   sections: §4 (the verdict distribution — the Boolean-homomorphism lemma and
   the one-solve theorem), §5.2 (conditioning is degenerate — the hinge), §5.6
   (the sharpness dichotomy, two lines). **Do not re-plan, do not re-scope, do
   not add directions.** If the plan is wrong somewhere, say so and stop — do
   not quietly widen it.
2. **§6.5 — the open theorem, and it outranks everything else.** All of
   §6.1–6.4 is proved relative to the *degenerate* source. The equivalence a
   user wants is agreement **under the model**: `Pr_M(S₁ Δ S₂) = 0`. Conjecture:
   the whole of §6.3 relativizes, because the model-induced source lives on the
   **same monoid** (the aligned table) — the residual-`Pr` series still factors
   through classes, the congruence is still two-sided. Prove it or refute it. If
   it fails, §6 must be honestly labelled as the `Σ^ω` corner.
3. **Reading is gating** (§8). The novelty claim — "the first probabilistic
   exploitation of the syntactic algebra" — is unbacked: [VV06]
   (Varacca–Völzer, fairly correct systems) is the nearest neighbour and is
   engaged in one throwaway sentence, and two citations are still placeholders
   (PRISM CAV'11, Chatterjee–Doyen–Henzinger ToCL'10). Get them into `papers/`,
   read them, then claim. Also locate the prior art on *uniform resolution of
   nondeterminism* before claiming §5's construction. **If the verdict
   distribution or the null-quotient is already known, the plan is worthless and
   we need to learn that now, not at review.**
4. **Reversal to note:** the §2.3 transition-emitting embedding remark was
   slated for deletion. **It stays.** The model-induced walk puts letters on the
   Cayley edges, so the embedding is the bridge, not a vestige.
5. **F-M5 verdict** (the Markov product; report). Its one finding: PRISM will
   not parse our cube label names (`a&!b`), so `.mc`'s "same file, unmodified"
   holds only up to label-name sanitization. No number moves. `.mc` is now
   demoted to an *import path* (`sos_quant.md` §5.7), so this is a small call:
   accept, and note the sanitizing printer.

## Work items — Engineering

**None. Blocked on a new spec from Theory.** The old `sos_measure_spec.md` is
stale: its M6 census campaign is not this paper's evaluation, and its
milestones M1–M5 are done and frozen. Nothing should be built until
`sos_quant.md` is fleshed out and a spec is written against it. What that spec
will have to cover, when it comes (do **not** start on it):

- the **verdict distribution** `ν` (small: the aligned table, the absorption
  vector and the θ-profiles all exist — `ν` is grouping bottom SCCs by their
  bit vector and summing);
- the **model-induced walk** on the live classes of `I(M)`, and the fact that
  the chain × spec product *is* the calculus's `align`;
- the **(model, spec) benchmark** — the property specification patterns, paired
  with protocol-shaped safety models. It does not exist yet.

Deferred until a user go-ahead: move `sosl/sosl/quant/` under `sosl/sosl/sos/`.

## Operational facts (only what the code does not already say)

- Run from `sosl/` as modules: `cd sosl && python3 -m tests.quant.X`. cwd drifts
  mid-shell — always `cd` explicitly (commits from the repo root, tests from
  `sosl/`).
- The `genaut/corpus/flat_canon/` census is **probes, not results** — it is the
  classification framework's benchmark, and here it only argues the engine is
  correct. A concurrent stream regenerates it, so counts move: rerun a gate
  rather than trust a stale number.
- Artifacts: throwaway output to `sosl/tests/quant/logs/` (gitignored),
  validated `.md`/`.csv` to `reference/quant/` with the 4-line header (date,
  git rev, seed, corpus).
- PRISM 4.10.1 sits in `opt/prism-4.10.1-linux64-x86/bin/prism` — untracked,
  unwired, invoked by nothing. It is the arbiter of what `.mc` text will
  actually parse.

## Gotchas

- **Concurrent sessions** commit to this repo (calculus, corpus, learner, figs).
  Unfamiliar modified files are NOT yours: commit only your files by explicit
  path — `git add <paths> && git commit -F - -- <paths>` in one breath (a bare
  `commit` sweeps the other session's staged index; it has happened) — never
  `git add -A`, never touch history.
- The paper is not a log: no process language, no "we changed X", definitions
  before use (§2 carries the full kit — extend it there if a new notion is
  needed, never inline mid-proof).
- Fixture disagreements: the code is wrong until proven otherwise; if you
  believe a fixture is wrong, STOP and file a finding against the paper in the
  report.
- `docs/HISTORY.md` is append-only via shell and never read.
