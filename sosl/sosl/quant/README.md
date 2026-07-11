# sosl.quant — quantitative read-offs on a held invariant

From one invariant `I(L) = (C, key, λ, M, P)` this package computes:

- the **θ-profile**: one canonical Boolean per bottom SCC of the
  right-Cayley graph — the generic verdict of the words absorbed there
  (`theta_profile`);
- the **measure** `μ_p(L)` under any full-support rational Bernoulli `p`,
  as an exact `fractions.Fraction`, with its absorption certificate
  (`measure`).

Normative math: `research_notes/sos_measure.md` (Lemmas 3.1–3.3,
Theorem 3.4, §4.1); working spec: `research_notes/sos_measure_spec.md`
(M1). The *why it is correct* lives in `algorithm.md` next to this file.

## Contract

- Input is a validated, canonically numbered `Invariant` (what
  `load_invariant` returns, what `Table.of` accepts). No reduction is
  required or performed: everything here is insensitive to the table
  being syntactic-minimal, so a `P` flipped by the calculus complement
  works as-is.
- Numbers are `fractions.Fraction` end to end — no floats, no numpy, no
  subprocess. The measure path (`chain`/`kernel`/`theta`/`measure`) never
  touches Spot; `routea` (the independent oracle) uses Spot for HOA
  parsing and acceptance read-out only, bounded-or-skipped.
- Layering: this package imports `sosl.sos` and `sosl.sos.calculus` and
  nothing else in the repo.
- `PARANOID` (module flag in `theta.py`, on by default) re-derives each
  θ bit from a second representative and a second kernel idempotent and
  asserts the invariances of paper Lemma 3.3.

## Source map

| file | contents |
|---|---|
| `chain.py` | right-Cayley edges; bottom SCCs, sorted by least shortlex class key |
| `kernel.py` | two-sided Cayley graph on `S`, its unique sink SCC = the kernel `K`, one idempotent `k ∈ K` |
| `theta.py` | `ThetaProfile`; `θ_C = Val(c, k)` per bottom SCC; paranoid cross-checks |
| `measure.py` | `p` validation, transient linear system, exact Gauss–Jordan, `MeasureResult` |
| `routea.py` | independent oracle: `μ` of a deterministic complete EL automaton (`.hoa`) via BSCC analysis, same solver |

## Tests

Placed scripts under `sosl/tests/quant/`, run from `sosl/`:

- `python3 -m tests.quant.fixtures` — three hand-computed fixtures
  (exact expected profiles, measures, absorptions; both uniform and a
  skewed `p`).
- `python3 -m tests.quant.flip_gate PATH.sos` — one corpus case:
  `μ(L) + μ(¬L) == 1` exactly and pointwise-negated profiles; appends a
  CSV row under `tests/quant/logs/`. `--list` emits the corpus file
  list; `--aggregate` renders `reference/quant/m1_measure.{md,csv}`.
- `python3 -m tests.quant.oracle_gate PATH.sos` — law L1: `measure`
  against the Route A oracle on the paired `det/*.hoa`, exact equality
  under uniform and one skewed `p`; same `--list` / `--aggregate` shape
  (renders `reference/quant/m2_oracle.{md,csv}`).
- `python3 -m tests.quant.law_gate A.sos B.sos` (L2/L3 on one aligned
  pair) and `python3 -m tests.quant.law_gate PATH.sos` (L4 trichotomy,
  L5 obligation cross-check).
