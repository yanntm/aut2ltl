# sosl.quant — quantitative read-offs on a held invariant

From one invariant `I(L) = (C, key, λ, M, P)` this package computes:

- the **θ-profile**: one canonical Boolean per bottom SCC of the
  right-Cayley graph — the generic verdict of the words absorbed there
  (`theta_profile`);
- the **measure** `μ_p(L)` under any full-support rational Bernoulli `p`,
  as an exact `fractions.Fraction`, with its absorption certificate
  (`measure`) and its per-class extension (`value_vector`);
- the **distance** `d_p(L₁, L₂) = μ_p(L₁ Δ L₂)` on the aligned product,
  with the xor θ-profile's null-disagreement read-off (`distance`);
- the **shadow** — the `θ = 1` stem-region read-off on `L`'s own table,
  a language at distance 0 from `L` (`shadow`);
- the **essential form** — the canonical representative of `L` up to
  null sets, and its LTL-up-to-null verdict (`essential`,
  `ltl_up_to_null`).

Normative math: `research_notes/sos_measure.md` (Lemmas 3.1–3.3,
Theorem 3.4, §4.1–§4.2); working spec: `research_notes/sos_measure_spec.md`
(M1–M3). The *why it is correct* lives in `algorithm.md` next to this file.

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
- Layering: this package imports `sosl.sos`, `sosl.sos.calculus` and
  the classify aperiodicity scan (`sosl.sos.classify.aperiodic`), and
  nothing else in the repo.
- The shadow and the essential form return *reduced* invariants
  (byte-canonical `.sos` dumps: byte-equality is language equality);
  both raise on a violation of their paper laws (Thm 4.4(2) constancy)
  rather than emitting a downgraded result.
- `PARANOID` (module flag in `theta.py`, on by default) re-derives each
  θ bit from a second representative and a second kernel idempotent and
  asserts the invariances of paper Lemma 3.3.

## Source map

| file | contents |
|---|---|
| `chain.py` | right-Cayley edges; bottom SCCs, sorted by least shortlex class key |
| `kernel.py` | two-sided Cayley graph on `S`, its unique sink SCC = the kernel `K`, one idempotent `k ∈ K` |
| `theta.py` | `ThetaProfile`; `θ_C = Val(c, k)` per bottom SCC; paranoid cross-checks |
| `measure.py` | `p` validation, transient linear system, exact Gauss–Jordan, `MeasureResult`, `value_vector` |
| `routea.py` | independent oracle: `μ` of a deterministic complete EL automaton (`.hoa`) via BSCC analysis, same solver |
| `distance.py` | `d_p` = measure of the pair-set xor on the materialized aligned product; `DistanceResult` with the null-disagreement bit |
| `shadow.py` | Prop 4.1 stem-region surgery on the invariant's own table, then `reduce` |
| `essential.py` | Thm 4.4: value-vector congruence, held-out-identity quotient, shadow read-off, `reduce`; `ltl_up_to_null` aperiodicity verdict |

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
- `python3 -m tests.quant.fixtures2` — fixtures F-D through F-I
  (kernel negative control, the ℤ/2 example, shadow and essential
  ground truths including the F-G negative control).
- `python3 -m tests.quant.m3_gate PATH.sos` (per-case shadow/essential
  laws), `... A.sos B.sos` (distance symmetry + shadow⟹essential
  consistency), `... A.sos B.sos C.sos` (triangle inequality); same
  `--pairs` / `--triples` / `--list` / `--aggregate` shape (renders
  `reference/quant/m3_laws.{md,csv...}`).
