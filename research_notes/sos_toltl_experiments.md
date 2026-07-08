# SoS → LTL — Experimentation Specification

**Status:** specification / declaration of intent. Everything below is to be
implemented; nothing below exists yet except where explicitly marked
*(exists in-repo)*. This document is the interface between the paper
(`sos_toltl.md`) and the implementation sessions: the paper's ⟨TBD⟩ tables
cite the experiment ids below, and every trace printed in the paper is a
*prediction* the tool must reproduce, per the family discipline
(`sosl_report.md` ledger style).

**Revision 2026-07-07** (theory review of the M1 report, appended to
`sos_toltl_report.md`): added §3b census reporting discipline; E1/E2 table
requirements; E4-interim (DG ledger, runnable at M1); E7 dual scan and
pull-forward to M1.5; E3 directed questions; E8 (C7's experiment) and C7's
milestone assignment; milestone M1.5.

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
  *(exists)* — internal baseline and cross-test comparator (E3, E4c). Note:
  the paper no longer speaks of any automaton-level transcription — these
  runs are diagnostics for us, not paper material.
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
- `k = 2, 3`: Definition 5.5 via Lemma 5.6(v)'s fixpoint — the sets `𝒜_j`
  of within-layer actions of readable length-`j` words, extended letter by
  letter to the closing cycle; smallest `k` with every tail action
  identity-or-constant, else `FAIL`. (Theory frozen 2026-07-07: the engine
  consumes a passing `k` at window width `k+1`, paper §5.7 / Thm 5.23.
  Build the layer action monoid `𝒜_R` as a by-product — the (A)-fail
  fallback runs on it, Prop 5.21/5.24.)
Output per language: list of layers with `|R|`, smallest passing `k` or
`FAIL`, letter classification table.

**C3 — condition (B) tester (bounded).** Per *final-candidate* layer `R`
(any layer some run can remain in forever — every layer with an internal
cycle), per width `k' = 1, 2, 3`: decide whether two lassos confined to
`R` with equal recurring `k'`-window sets can have different `P`-verdicts.
(The per-stem quantification of Definition 5.7 collapses per layer: `R` is
strongly connected, so every cycle is reachable from every class of `R`.)
Three stages, verdicts computed as `(d·e, e) ∈ P` with `d` the cycle's
anchor class and `e` the idempotent power of the loop class:
- *trivial pass (exact, polynomial)*: the cycle classes per anchor class
  are the closure `{ m : (d, m) reachable from (d, [ε]) }` in the
  `(position in R, accumulated word class)` product; one verdict across
  all of them ⟹ (B) holds trivially at every width.
- *bounded test*: enumerate cycle words up to length cap `2·|R|·|𝒞|`
  under a node budget; group by recurring `k'`-window set; a verdict
  conflict is an exact `FAIL(witness pair of lassos)`; conflict-free with
  the enumeration complete is a cap-bounded `PASS`; a tripped budget is
  `UNDECIDED(k')`. The cap must scale with `|𝒞|`, not with `|Σ_λ|`: the
  loop class folds through the whole algebra even where the walk is
  frozen (paper Prop 5.15(iii); the cap `2·|R|·|Σ_λ|` is refuted by
  `EvenBlocks`' layer `{6}` — conflicting loops `(a⁴·!a)^ω`/`(a⁵·!a)^ω`
  of length 5 against a cap of 4, yielding a false PASS at `k' = 3`).
- *exact procedure (normative once priced)*: per strongly connected
  subgraph `H` of the memory graph, the loop-class closure of covering
  tours via `(node, class, covered-edges)` states, grouped across
  subgraphs sharing a window projection (paper Prop 5.15(iii)). A
  cap-bounded `PASS` is not a theorem until either this replaces the
  enumeration or a sufficiency proof for the cap is frozen
  (`sos_toltl_report.md` F1).
Output: smallest passing `k'` with its PASS/UNDECIDED grade, or
`FAIL(witness pair of lassos)`.

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
- *AND-split* (per paper Thm 5.19 / Prop 5.20): enumerate *pairs* of
  congruences of `(𝒞, M)` (census-sized — brute force over principal
  congruences and joins is acceptable), coarsest first; for each `θ`
  compute the canonical saturation `Val^θ` (pointwise `∨` of `Val_P` over
  `θ`-blocks) and test `Val^{θ₁} ∧ Val^{θ₂} = Val_P` with both factors
  proper (`Val^{θᵢ} ≠ Val_P`) — this search is complete (Thm 5.19); the
  `θ₁ ∩ θ₂ = Δ` condition is a theorem (Prop 5.20), assert it, don't test
  for it. Report the factor invariants (re-canonicalized), or
  `IRREDUCIBLE`. **Test vectors:** `GFa` must *factor* — as
  `Fa ∧ (GFa ∨ G¬a)`, both congruences the neutral-unit merge (the
  paper's properness caveat in Thm 5.19; an earlier version of this spec
  wrongly predicted `IRREDUCIBLE`); `GFa ∧ FGb` must factor as
  `FGb ∧ GF(a ∨ !b)` — *not* as `GFa ∧ FGb`, `GFa` not being recognized
  on its table (paper §5.6(3), the corrected specimen). Whether a found
  split is *adopted* is the §5.6(1) guard's read-off decision — report
  factorizations and adoption separately.

## 3. The conformance gate (mandatory, every experiment)

For every emitted formula `φ` on every instance: build `𝓘(L(φ))` with the
reference construction and compare byte-for-byte against the input `𝓘`.
A mismatch is a stop-the-line bug in the engine, never a statistic.
Timeouts: per-instance cap 15s; a blown cap is recorded as `TIMEOUT` and
reported — it is a finding, not an error. Long outputs go to
`tests/**/logs/`, one file per experiment id.

## 3b. Census reporting discipline (mandatory, every census table)

A census experiment is a claim about *languages measured over an
exhaustive frame*; a table that does not declare its frame is not a census
result. Every census table (E1, E2, E4, E7, E8, the E6 sweeps) carries:

- **The frame declaration.** The enumeration axes and their values: state
  count, AP count, acceptance-set count, and — first-class, never implied —
  the **acceptance family** behind the set count (generalized-Büchi
  Inf-conjunction / parity / arbitrary Emerson–Lei), plus determinism and
  completeness of the inputs, and whether the enumeration is exhaustive
  over the declared axes or sampled (and how). The reference construction's
  contract is deterministic Emerson–Lei input; a census exercising only one
  family must say so in the table caption. The parity corpora
  (`genaut/corpus/`) join the bench at the next census run; arbitrary-EL
  shapes are a census-next axis.
- **Ventilation per shape.** Every statistic is reported per shape (one
  row per shape); pooled totals appear only alongside the per-shape rows,
  never instead of them.
- **The unit is the language, not the automaton.** The census enumerates
  automata, but the claims are about languages: the primary key of every
  census statistic is the distinct canonical `.sos` (byte-identical after
  canonical keying) — formula-string dedup is a proxy only, the invariant
  decides (distinct strings can be one language). Automaton counts
  survive as *presentation multiplicity*: itself a deliverable (the
  multiplicity distribution per language, expected top-heavy) and a free
  canonicity cross-check — every presentation of one `.sos` must yield
  identical read-offs, certificates and formulas, and a divergence is a
  stop-the-line bug, never a statistic. Measured skew motivating the
  upgrade (2state1ap1acc, Inf-only, portfolio path): 759 LTL answers
  collapse to at most 73 distinct structures, 43.6% of answers the
  universal language — automaton-weighted percentages on that shape are
  ~90% presentation noise.
- **The degenerate line.** Empty and universal specimens — the weakest
  stratum: one word class, `P` empty or full — pass (A) and (B) trivially
  and only inflate headline fractions. They get their own line per shape,
  with headline figures restated without them; report also the
  single-word-class count among the non-degenerate.

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
are common (every absorbing class is one). Tables per §3b: frame declared,
per-shape rows, keyed by distinct `.sos` with presentation multiplicity
alongside, degenerate line separated.

### E2 — window-determinacy statistics (census)

C3 over all final-candidate layers of census LTL specimens. **Paper
deliverable:** fraction (B)-determined at `k' ∈ {1,2,3}`; the witness pairs
for failures. **Prediction:** (B) holds at `k' ≤ 2` on all 1-AP census
specimens; failures require either ≥ 2 AP or larger monoids (order/
betweenness structure — see E6). Tables per §3b. Grades are three-valued
and never pooled: exact PASS (trivial-stage closure), cap-bounded PASS (no
sufficiency theorem until report-F1's open item is frozen), UNDECIDED.

### E3 — presentation cross-test *(internal diagnostics, not paper material)*

The paper defines its engine on the algebra alone and states no comparison
with automaton-level transcription; this experiment survives as *our*
diagnostics. For each census LTL specimen: (i) run the kanchor
preconditions on the repo's standard automaton forms (`sbacc(tgba(L))`,
per [KA26, §12] the form matters — record which form) and note the passing
width per SCC; (ii) run C2 on `Cay(L)`. Tabulate `(form width, algebra
width)` pairs, recording per language min width over forms vs. min width
over layers, with the bundling caveat — kanchor's state-based acceptance
folds (B) in, so compare (A)+(B) jointly against kanchor, and (B) alone
against daisy applicability. **Deliverable:** internal evidence table only.
An instance where the algebra needs a *larger* width than some form is a
research finding to bring back to the paper (it would revive the dropped
comparison as a theorem target); absent that, nothing here is cited.
**Prediction:** algebra ≤ form throughout the census, with `GF(aa)` (1 vs
2) the exemplar; no reverse instance found (low confidence — that is the
point of the diagnostic). Two directed questions ride along: (i) does
kanchor's SCC peel go through on the census reference forms at all —
per-SCC passing widths and failure modes, not only the min width; (ii)
daisy's applicability should coincide with the width-1 park stratum
(frozen layers, (B) at `k' = 1`) — check the correspondence, report
exceptions. E3 needs no new engine: an early pass on the 1-AP census runs
at M1.5.

### E4 — size ledgers

For every census LTL specimen and the worked examples, emit with: (a) this
engine (C4), (b) the DG-style baseline, (c) the automaton portfolio run on
`Cay(L)` exported as an ordinary deterministic automaton ⟨acceptance for
the export: TBD — the honest export is the pair-complete one; if none is
wired, run the portfolio on the census's own reference automata instead and
say so⟩. Record: DAG node count, flat tree size, modal depth, until-nesting
depth, `FLAT_OVERFLOW` events; Spot-simplified sizes where Spot terminates
within cap (bounded-or-skipped per repo discipline). **Paper deliverable:**
the §6/§8 ledgers over (a) vs (b) only; DAG-vs-`|𝒞|` scatter for the
scaling claim. Column (c) is internal diagnostics (the paper does not
mention automaton-level transcription), kept because a (c)-beats-(a) case
is a research finding for us. Column (c) is also the standing
*readability yardstick*: per distinct language the portfolio's simplified
formula (`GFa`, `!a & G(!a | X!a)`, …) sets the size/readability bar the
transcription should approach on the census — record the per-language
(a)-vs-(c) size ratio once (a) exists. **Prediction:** (a) ≤ (b) on flat size on
every instance, with the gap growing on multi-layer specimens; (a)
competitive with (c) and canonical where (c) is form-lucky.

**E4-interim (runnable at M1 — no C4 needed).** Column (b) alone over the
census: per instance the DAG node count and flat tree size (or
`FLAT_OVERFLOW`), ventilated by `|𝒞|` and per shape (§3b), with
size-bucket histograms (flat and DAG) and the DAG-vs-`|𝒞|` scatter. This
is §3/§6's explosion measured as a *distribution* instead of the single
`GF(aa)` exemplar, and it freezes the (b) column before (a) exists.

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
- **H5**: a non-LTL specimen whose ω-power patterns are *all constant*
  (certificate exists in linear shape only) — the dual of the paper's
  Proposition 4.2 blindness; a hit settles the open question of §4.1, an
  exhausted census is evidence toward "F₂ always available".
- **H6**: smallest specimen with a `k`-anchored layer (`k ≥ 2`) whose
  walk moves phase under a *neutral* `k`-window (an excursion completed
  at the window's last step) — the witness that the engine's operating
  width `k+1` is tight, not merely sufficient (paper §5.7, the remark
  after Lemma 5.22).
**Prediction:** H2/H3 do not exist at 2 states / 1 AP; first hits appear
⟨TBD: record where⟩. Each hit's `.sos`, layers, and witness go into
`tests/**/logs/` and the paper's §7 empirical map.

### E7 — certificate validation (non-LTL side)

For every non-LTL census specimen: extract the certificate (group orbit,
witness words, context shape, period `p′`); verify by the paper §4.4
toggle check — `2p′ + 1` lasso membership tests (`n = 0 … 2p′`) — against
the reference automaton *only* (no algebra on the verifier side); record word lengths against the paper's Theorem-4.4 bounds (each
component `< |𝒞|`, the absorbed index power quadratic). **Prediction:** all
verify; `Even` emits `F₁(u=a, v=a, x=(!a)^ω, p′=2)` (samples
`a^{n+1}·(!a)^ω`, accept iff `n` odd) and `EvenBlocks` emits
`F₂(u=ε, v=a, y=a·!a, p′=2)` (samples `(a^{n+1}·!a)^ω`, accept iff `n`
odd) — the paper's §4.3 canonical derivations, byte-exact.

**Dual scan (the H5 read-off).** The emitted certificate records which
shape fired *first* under the scan order, which is not the H5 datum. For
every non-LTL specimen run both scans to completion and record two
columns: first separating linear context (or `all-constant`), first
separating ω-power context (or `all-constant`). A specimen with ω-power
all-constant is an H5 hit (linear-only certificate); a census with none
is evidence toward "F₂ always available". Triptych vectors (run
2026-07-08, report F4): `Even` — linear ✓ *and* ω-power ✓, the ω-power
family being `F₂(u=ε, v=a, y=a·!a, p′=2)`, the same family that
certifies `EvenBlocks`; `EvenBlocks` — linear `all-constant`, ω-power ✓.
Neither is an H5 hit; H5 is genuinely a census hunt. **Sizes.** Tabulate component
lengths (`|u|`, `|v|`, `|x|`/`|y|`, `p′`) against the Theorem-4.4 bounds,
per shape and per `|𝒞|` (§3b). **Scheduling.** E7 consumes only M1
components (`witness/` + the reference automata): it runs at M1.5 on the
1-AP census and re-runs at M4 on census-next.

### E8 — decomposition census (C7)

For every census LTL specimen: (i) **OR-split by final layer** —
re-canonicalize each piece, record per-piece read-offs (`|𝒞'|`, ladder
rung, (A)/(B) widths); (ii) the **pair split** — restrict `P` to each
single accepting pair, re-canonicalize, same read-offs, plus the piece's
rung against `L`'s: the incidence of Wagner-ladder climb is the paper's
§5.6(1) guard turned into a measurement (rung read-off via the classifier
subproject — a dependency, note it in the run log); (iii) the **AND-split
search** of C7, reporting factored-vs-`IRREDUCIBLE` fractions and the
factor read-offs (the Thm 5.19 census query). Tables per §3b.
**Prediction:** final-layer pieces never climb the ladder and usually
shrink; pair pieces climb on a measurable fraction (the guard's raison
d'être) — if no pair piece climbs anywhere on the census, the guard is
over-cautious at these sizes and §5.6(1) earns a remark.

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

- **M1** — C1+C2+C3+C5, E0 gate green, E1+E2 tables produced. *(Done —
  `sos_toltl_report.md`.)*
- **M1.5** — census hygiene and the no-engine ledgers: E1/E2 re-issued
  per §3b (frame declared, per-shape rows, both weightings, degenerate
  line; parity corpora added to the bench); E4-interim; E7 on the 1-AP
  census (dual scan); early E3 pass.
- **M2** — C4 walk+window engine on the (A,k=1)/(B,k'≤2) strata, E0
  formula prediction green, E4(a) vs (b) ledger on the census subset the
  engine covers; conformance gate wired.
- **M3** — graded engine at window width `k+1` (paper §5.7, Thm 5.23:
  transient fold trees `TR`/`TL`, `step_κ`), scoped DG fallback on the
  layer action monoid `𝒜_R` (Prop 5.24) — full-coverage engine; full E4,
  E3; C7 + E8.
- **M4** — C6 + E5; E6 sweeps; E7 re-run on census-next.

Every milestone ends with a report appended to `sos_toltl_report.md`
(ledger style, one row per finding, predictions checked off or refuted —
a refuted prediction is a paper edit, not a footnote).
