# SoS → LTL — Experimentation Specification

**Status:** specification / declaration of intent. Everything below is to be
implemented; nothing below exists yet except where explicitly marked
*(exists in-repo)*. This document is the interface between the paper
(`sos_toltl.md`) and the implementation sessions: the paper's ⟨TBD⟩ tables
cite the experiment ids below, and every trace printed in the paper is a
*prediction* the tool must reproduce, per the family discipline
(`sosl_report.md` ledger style).

**One-line goal.** Provide the data for `sos_toltl.md`: per-layer anchoring
and window-determinacy statistics over the census, the size ledgers against
Diekert–Gastin and the automaton portfolio, the frontier hunts (smallest
specimen per stratum), and the certificate validation — plus the conformance
gate that every emitted formula defines the input language exactly.

---

## 1. Objects consumed (all exist in-repo)

- **The invariant** `𝓘(L) = (𝒞, λ, M, P)` in `.sos` format, produced by the
  reference construction *(exists)*; byte-equality after canonical keying is
  the language-equality oracle.
- **The census** of small automata (2 states, 1 AP, small acceptance, …)
  with ground truth — `𝓘`, LTL status — precomputed *(exists)*.
- **The triptych** `GF(aa)`, `Even`, `EvenBlocks` and the kanchor/daisy
  fixtures (`samples/fixtures/hoa/anchor/`, `…/kanchor/`) *(exist)*.
- **The automaton portfolio** (aut2ltl recipes, incl. `kanchor`, `daisy`)
  *(exists)* — used as baseline and as the Conjecture-5.8 comparator.
- **The DG-style engine with DAG/memoization** *(exists per project notes)* —
  the naive baseline; if its output cannot be flattened on an instance, that
  *is* the measurement (record DAG size + `FLAT_OVERFLOW`), not a failure.

## 2. Components to implement (library level, no CLI polish needed)

**C1 — Cayley builder.** From `.sos`: the deterministic automaton `Cay(L)`
(states `𝒞`, edges `c →^a M(c, λ(a))`), its SCC decomposition, and the
SCC DAG. Assert: SCCs coincide with the R-classes computed independently
from `M` (mutual right-divisibility) — this is a *test of Lemma 5.3*, run on
every input, not a one-off.

**C2 — condition (A) tester.** Per layer `R`, per width `k = 1, 2, 3`:
- `k = 1`: each letter's within-layer action is a partial identity or a
  partial constant (paper Def 5.4). Report per letter: `neutral | reset(t) |
  mixed`.
- `k = 2, 3`: the graded test ⟨theory TBD in the paper, Def 5.5 — implement
  after the definition is frozen; until then report `k=1` results only and
  mark layers `k1-fail` as `UNGRADED`⟩.
Output per language: list of layers with `|R|`, smallest passing `k` or
`FAIL`, letter classification table.

**C3 — condition (B) tester (bounded).** Per *final-candidate* layer `R`
(any layer some run can remain in forever — every layer with an internal
cycle), per stem class `s ∈ R`, per width `k' = 1, 2, 3`: decide whether
two lassos confined to `R` from `s` with equal recurring `k'`-window sets
can have different `P`-verdicts. Procedure (exact, census-sized): enumerate
the simple-cycle decompositions of `R`'s within-layer graph up to length
cap `⟨2·|R|·|Σ_λ|⟩`; for each pair of cycle sets with equal `k'`-window
sets, compare the idempotent-power verdicts of their loop classes against
`s`. A cheaper sound over-approximation may be used to *pass* (all
idempotents reachable in `R` from `s` share one verdict ⟹ (B) holds
trivially at every width); the exact test is required only to *fail*.
Output: smallest passing `k'` or `FAIL(witness pair of lassos)`.

**C4 — engine bricks (walk + window).** The transcription per the paper's
§5 skeleton, emitting the class-indexed DAG; flattening and definitional
rendering as separate printers. Phased: M1 needs only C1–C3 (the statistics
stand alone); M2 adds the emitter.

**C5 — read-off preludes.** λ-quotient of the alphabet; ladder rung from
`P` (safety/co-safety/obligation detection); prefix-independence (residual
count from the `.sos` residuals block); complement flip. Each is a pure
`.sos` computation.

**C6 — until-rank.** ⟨theory TBD — implement only after the paper freezes
the Wilke-condition statement; E5 is blocked on this and on nothing else.⟩

**C7 — combinator layer (paper §5.6).** Three pure-`.sos` operations:
- *re-canonicalizer*: given `(𝒞, λ, M, P')` with any pair set `P'`, re-run
  the reference construction's quotient to the piece's own syntactic
  invariant *(the refinement machinery exists in the construction tool;
  wrap, don't rewrite)*;
- *OR-split*: restrict `P` per final layer, re-canonicalize each piece,
  report per-piece read-offs (`|𝒞'|`, rung, (A)/(B) widths);
- *AND-split*: enumerate ω-congruences of `(𝒞, M)` (census-sized monoids —
  brute force over principal congruences and joins is acceptable), search
  for `P = P₁ ∩ P₂` with `Pᵢ` `θᵢ`-saturated and `θ₁ ∩ θ₂ = Δ`; report the
  factor invariants, or `IRREDUCIBLE`.

## 3. The conformance gate (mandatory, every experiment)

For every emitted formula `φ` on every instance: build `𝓘(L(φ))` with the
reference construction and compare byte-for-byte against the input `𝓘`.
A mismatch is a stop-the-line bug in the engine, never a statistic.
Timeouts: per-instance cap 15s; a blown cap is recorded as `TIMEOUT` and
reported — it is a finding, not an error. Long outputs go to
`tests/**/logs/`, one file per experiment id.

## 4. Experiments

### E0 — sanity on the worked examples (gates M1)

Run C1/C2/C3/C5 on the triptych. **Predictions to confirm** (from the
paper, computed by hand from [SωS26, Table 3]):

- `GF(aa)`: layers `{0}, {1,3}, {2,4}, {5}` with the R-order
  `0 → {1,3} | {2,4} → 5`; layers `{1,3}`, `{2,4}` pass (A) at `k = 1`
  (letter table: `!a ↦ reset(1)` resp. `reset(4)`, `a ↦ reset(3)` resp.
  `reset(2)`); layer `{5}` is frozen (both letters neutral) and passes (B)
  at `k' = 2` with witness window `aa`, failing at `k' = 1` (the
  Lemma-5.2 edge pair: `(a·!a)^ω` vs `(aa·!a)^ω`); layers `{1,3}`, `{2,4}`
  as final layers are all-rejecting (every pair off `5` is out of `P`).
  Prefix-independence: 1 residual. With C4: emitted DAG simplifies to
  `GF(a ∧ Xa)`.
- `Even`, `EvenBlocks`: extraction stops at step 0 (group found); layer
  statistics still computed and recorded for E1's denominators.

### E1 — anchoring statistics (census)

For every LTL specimen of the census: layers, sizes, smallest (A)-width per
layer, letter classification, frozen-layer count, ladder rung,
prefix-independence. **Paper deliverable:** the §7 inner-frontier table's
empirical column — fraction of layers per stratum, fraction of languages
fully stem-transcribable at `k ≤ 3`. **Prediction (falsifiable guess):** at
census sizes a large majority of layers pass (A) at `k = 1`; frozen layers
are common (every absorbing class is one).

### E2 — window-determinacy statistics (census)

C3 over all final-candidate layers of census LTL specimens. **Paper
deliverable:** fraction (B)-determined at `k' ∈ {1,2,3}`; the witness pairs
for failures. **Prediction:** (B) holds at `k' ≤ 2` on all 1-AP census
specimens; failures require either ≥ 2 AP or larger monoids (order/
betweenness structure — see E6).

### E3 — Conjecture 5.8 cross-test

For each census LTL specimen: (i) run the kanchor preconditions on the
repo's standard automaton forms (`sbacc(tgba(L))`, per [KA26, §12] the
form matters — record which form) and note the passing width per SCC;
(ii) run C2 on `Cay(L)`. Tabulate `(form width, algebra width)` pairs with
the SCC↔layer correspondence ⟨TBD: the correspondence is many-to-many;
record per language: min width over forms vs. min width over layers, plus
the bundling caveat — kanchor's state-based acceptance folds (B) in, so
compare (A)+(B) jointly against kanchor, and (B) alone against daisy
applicability⟩. **Paper deliverable:** the Conjecture 5.8 evidence table;
every instance where the algebra needs a *larger* width than some form is a
first-class finding to be quoted. **Prediction:** algebra ≤ form throughout
the census, with `GF(aa)` (1 vs 2) the exemplar; no reverse instance found
(low confidence — this is the point of the experiment).

### E4 — size ledgers

For every census LTL specimen and the worked examples, emit with: (a) this
engine (C4), (b) the DG-style baseline, (c) the automaton portfolio run on
`Cay(L)` exported as an ordinary deterministic automaton ⟨acceptance for
the export: TBD — the honest export is the pair-complete one; if none is
wired, run the portfolio on the census's own reference automata instead and
say so⟩. Record: DAG node count, flat tree size, modal depth, until-nesting
depth, `FLAT_OVERFLOW` events; Spot-simplified sizes where Spot terminates
within cap (bounded-or-skipped per repo discipline). **Paper deliverable:**
the §6/§8 ledgers; DAG-vs-`|𝒞|` scatter for the scaling claim.
**Prediction:** (a) ≤ (b) on flat size on every instance, with the gap
growing on multi-layer specimens; (a) competitive with (c) and canonical
where (c) is form-lucky.

### E5 — until-rank vs emitted depth *(blocked on C6)*

Per census LTL specimen: until-rank from the algebra, until-depth of the
emitted (simplified) formula. **Paper deliverable:** the optimality-gap
ledger — instances where emitted depth exceeds the certified lower bound,
listed. **Prediction:** gap 0 on ladder-low and (A,k=1)+(B,k'≤2) strata.

### E6 — frontier hunts

Exhaustive sweeps, census then census-next (grow states/AP/acceptance one
notch at a time, smallest-first):
- **H1**: smallest non-LTL specimen *(known — reconfirm against the
  certificate extractor, E7)*.
- **H2**: smallest LTL specimen with an (A)-failing layer at `k ≤ 3`.
- **H3**: smallest LTL specimen with a (B)-failing final layer at
  `k' ≤ 3` — the paper's candidate for the "order beyond windows" example
  (§5.5); the witness lasso pair is a paper figure.
- **H4**: smallest LTL specimen whose extraction must invoke the DG
  fallback at all (= H2 ∪ H3 minimum).
**Prediction:** H2/H3 do not exist at 2 states / 1 AP; first hits appear
⟨TBD: record where⟩. Each hit's `.sos`, layers, and witness go into
`tests/**/logs/` and the paper's §7 empirical map.

### E7 — certificate validation (non-LTL side)

For every non-LTL census specimen: extract the certificate (group orbit,
witness words, context shape, period `p`); verify by `2p` lasso membership
tests against the reference automaton *only* (no algebra on the verifier
side); record word lengths against the `O(|𝒞|)` bound. **Prediction:** all
verify; `Even` and `EvenBlocks` yield the paper's Table-1 witnesses with
`p = 2`, linear resp. ω-power shape.

## 5. Expected failures (read before filing bugs)

- **C3 blow-up on large layers.** The exact (B) test is combinatorial;
  census sizes are tiny, but H-series sweeps may hit the cap — record
  `UNDECIDED(k')` and move on; an UNDECIDED is a stratum-statistics gap,
  not a bug.
- **Portfolio baseline on `Cay(L)` may be ill-posed** until the acceptance
  export question (E4c) is settled; running (c) on reference automata is
  the sanctioned fallback.
- **Spot simplification stalls** are bounded-or-skipped; raw sizes are the
  primary metric, simplified sizes a bonus column.
- **`FLAT_OVERFLOW` on the DG baseline is a datum** (the paper's §3 point),
  expected already on mid-census instances.

## 6. Milestones

- **M1** — C1+C2+C3+C5, E0 gate green, E1+E2 tables produced.
- **M2** — C4 walk+window engine on the (A,k=1)/(B,k'≤2) strata, E0
  formula prediction green, E4(a) vs (b) ledger on the census subset the
  engine covers; conformance gate wired.
- **M3** — graded (A) per frozen Def 5.5, DG-fallback integration
  (full-coverage engine), full E4, E3.
- **M4** — C6 + E5; E6 sweeps; E7.

Every milestone ends with a report appended to `sos_toltl_report.md`
(ledger style, one row per finding, predictions checked off or refuted —
a refuted prediction is a paper edit, not a footnote).
