# SoS → LTL — Experimentation Specification

This document is the interface between the paper (`sos_toltl.md`) and the
implementation sessions: the paper's ⟨TBD⟩ tables cite the experiment ids
below, every trace printed in the paper is a *prediction* the tool must
reproduce, and results come back as findings in `sos_toltl_report.md`
(ledger style — a refuted prediction is a paper edit, not a footnote).

**Where things stand** (details per section; the report is the ledger):

- **Done, results in the report:** C1–C5 and C7; E0 (gate green); E1/E2
  (census tables by Wagner degree); E4-interim (DG ledger); E7 with the
  dual scan and mechanism tiers (H5 settled: ω-blind languages exist,
  linear-only certificates — the two-shape scan is load-bearing); E10
  (guard synthesis, grouping, residual indexing — measured); the F8
  soundness campaign (engine 0 FAIL, graded stratum declined to DG);
  E9 opened and its gallery sorted (`e9_scan`/`e9_profile`, the FIG-2
  trace hook; F13: H3 found — `G(a → F b)`, the (B) tester's blindness
  bugs fixed; F14: H2/H4 answered, the "≥ 2 AP" (A)-floor refuted —
  all 258 (A)-failing languages are 1 AP, floor `|𝒞| = 15`; E9
  candidates 1, 2, 4 have their smallest specimens).
- **Todo:** E9 candidates 3, 3a, 3b, 5 (the named 2-AP builds, the
  `GFa ∧ FGb` conformance, the width exemplar, the showpieces); H7
  (uncapped (A) fixpoint over the 258); E3 (presentation cross-test,
  early pass); full E4 and E8; E5 (blocked on C6, itself blocked on
  the paper's Thérien–Wilke freeze); H6 and smallest-H3 (census-next
  `2state2ap`); the graded engine (M3) once the paper's §4.3
  entry-rooted repair carries its completeness re-proof — 42.5% of the
  LTL catalogue is graded, so M3 is the coverage frontier.

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
from `M` (mutual right-divisibility) — this is a *test of Lemma 4.3*, run on
every input, not a one-off.

**C2 — condition (A) tester.** Per layer `R`, per width `k = 1, 2, 3`:
- `k = 1`: each letter's within-layer action is a partial identity or a
  partial constant (paper Def 4.4). Report per letter: `neutral | reset(t) |
  mixed`.
- `k = 2, 3`: Definition 4.5 via Lemma 4.6(v)'s fixpoint — the sets `𝒜_j`
  of within-layer actions of readable length-`j` words, extended letter by
  letter to the closing cycle; smallest `k` with every tail action
  identity-or-constant, else `FAIL`. (The engine
  consumes a passing `k` at window width `k+1`, paper §4.3 / Thm 4.13.
  Build the layer action monoid `𝒜_R` as a by-product — the (A)-fail
  fallback runs on it, paper Prop 4.11/4.14.)
Output per language: list of layers with `|R|`, smallest passing `k` or
`FAIL`, letter classification table.

**C3 — condition (B) tester (bounded).** Per *final-candidate* layer `R`
(any layer some run can remain in forever — every layer with an internal
cycle), per width `k' = 1, 2, 3`: decide whether two lassos confined to
`R` with equal recurring `k'`-window sets can have different `P`-verdicts.
(The per-stem quantification of Definition 4.8 collapses per layer: `R` is
strongly connected, so every cycle is reachable from every class of `R`.)
Three stages, verdicts computed as `(d·e, e) ∈ P` with `d` the cycle's
anchor class and `e` the idempotent power of the loop class:
- *trivial pass (exact, polynomial)*: the cycle classes per anchor class
  are the closure `{ m : (d, m) reachable from (d, [ε]) }` in the
  `(position in R, accumulated word class)` product; one verdict across
  all of them ⟹ (B) holds trivially at every width.
- *bounded test*: enumerate cycle words **breadth-first** (shortest
  cycles first — a conflict needs only short ones) up to length cap
  `2·|R|·|𝒞|`, under one node budget **per anchor class** (a shared
  budget lets one anchor starve the others, and a conflict routinely
  pairs cycles at two different anchors — report F13); group by
  recurring `k'`-window set; a verdict conflict is an exact
  `FAIL(witness pair of lassos)` regardless of the enumeration's
  completeness; conflict-free with
  the enumeration complete is a cap-bounded `PASS`; a tripped budget is
  `UNDECIDED(k')`. The cap must scale with `|𝒞|`, not with `|Σ_λ|`: the
  loop class folds through the whole algebra even where the walk is
  frozen (paper Prop 5.4(iii); the cap `2·|R|·|Σ_λ|` is refuted by
  `EvenBlocks`' layer `{6}` — conflicting loops `(a⁴·!a)^ω`/`(a⁵·!a)^ω`
  of length 5 against a cap of 4, yielding a false PASS at `k' = 3`).
- *exact procedure (normative once priced)*: per strongly connected
  subgraph `H` of the memory graph, the loop-class closure of covering
  tours via `(node, class, covered-edges)` states, grouped across
  subgraphs sharing a window projection (paper Prop 5.4(iii)). A
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

**C7 — combinator layer (paper §5.3).** Three pure-`.sos` operations:
- *re-canonicalizer*: given `(𝒞, λ, M, P')` with any pair set `P'`, re-run
  the reference construction's quotient to the piece's own syntactic
  invariant *(the refinement machinery exists in the construction tool;
  wrap, don't rewrite)*;
- *OR-split*: restrict `P` per final layer, re-canonicalize each piece,
  report per-piece read-offs (`|𝒞'|`, rung, (A)/(B) widths);
- *AND-split* (per paper Thm 5.8 / Prop 5.9): enumerate *pairs* of
  congruences of `(𝒞, M)` (census-sized — brute force over principal
  congruences and joins is acceptable), coarsest first; for each `θ`
  compute the canonical saturation `Val^θ` (pointwise `∨` of `Val_P` over
  `θ`-blocks) and test `Val^{θ₁} ∧ Val^{θ₂} = Val_P` with both factors
  proper (`Val^{θᵢ} ≠ Val_P`) — this search is complete (Thm 5.8); the
  `θ₁ ∩ θ₂ = Δ` condition is a theorem (Prop 5.9), assert it, don't test
  for it. Report the factor invariants (re-canonicalized), or
  `IRREDUCIBLE`. **Test vectors:** `GFa` must *factor* — as
  `Fa ∧ (GFa ∨ G¬a)`, both congruences the neutral-unit merge (the
  paper's properness caveat in Thm 5.8); `GFa ∧ FGb` must factor as
  `FGb ∧ GF(a ∨ !b)` — *not* as `GFa ∧ FGb`, `GFa` not being recognized
  on its table (paper §5.3(3)). Whether a found
  split is *adopted* is the §5.3(1) guard's read-off decision — report
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
for failures. Tables per §3b. Grades are three-valued
and never pooled: exact PASS (trivial-stage closure), cap-bounded PASS (no
sufficiency theorem until report-F1's open item is frozen), UNDECIDED.
**Status:** done catalogue-wide — 0 FAIL, 372 budget-UNDECIDED, all at
`(ω,·)`/`(ω²,·)` frozen final layers. The clean sweep is a *frame*
fact: a (B) failure needs ≥ 2 AP and ≥ 2 states at once (report F13,
`G(a → F b)`), and the catalogue holds no `2state2ap` shape. Re-runs
on census-next when that axis lands.

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
- **H2** *(found — report F14)*: smallest LTL specimen with an
  (A)-failing layer at `k ≤ 3` is `3state1ap0acc_004260` — `|𝒞| = 15`,
  **1 AP**, 3 states, `ϕ = (1,π)`; three 3-class layers, both letters
  mixed on each. 258 languages (A)-fail catalogue-wide, *all* 1 AP
  (F6's "≥ 2 AP floor" is refuted — the frontier is algebra size, not
  alphabet width).
- **H7** *(new)*: run the **uncapped** Lemma 4.6(v) fixpoint over the
  258 (A)-failing languages — per layer, the exact anchoring width or
  a *no-width* verdict. A no-width two-letter layer settles the
  paper's §4.2 open question and realizes Lemma 4.6(iii)'s scheme at
  half its alphabet budget; either way the `k`-distribution beyond the
  cap is the paper's §4.2 ⟨TBD⟩.
- **H3** *(found — report F13; remaining: the smallest witness)*: an
  LTL specimen with a (B)-failing final layer — the paper's "order
  beyond windows" example (§5.1). First witness `G(a → F b)`: 5
  classes, 2 AP, degree (ω,σ), 2 residuals; its final layer is moving,
  1-anchored, and fails (B) at *every* width on an exact witness pair
  (equal recurring window sets, opposite verdicts, the idle letter
  `!a&!b`). A (B) failure needs ≥ 2 AP *and* ≥ 2 states at once — a
  shape the catalogue omits; `2state2ap` is the census-next axis and
  minimality is decided there.
- **H4** *(answered — report F14)*: smallest specimen forced to the DG
  fallback. Read as "(A)-forced": `|𝒞| = 15` (= H2). Read as "forced
  at all": the graded stratum reaches it first, at `|𝒞| = 12`
  (`2state1ap0acc_086`, the F8 exhibit — confirmed the smallest graded
  language, 952 catalogue-wide).
- **H5** *(done — report F5/F7; remaining: re-run on census-next)*: a
  non-LTL specimen whose ω-power patterns are *all constant*
  (certificate exists in linear shape only) — the dual of the paper's
  Proposition 3.2 blindness. 100 exist (min `|𝒞| = 4`, exhibit `L₄`,
  paper §3.3): "F₂ always available" is refuted and the two-shape scan
  is necessary. The mechanism map is measured: right-ideal 8 /
  phase-collapse 10 / `P`-level 82 — the exact ω-blindness condition is
  acceptance-level, no condition on `(𝒞, ·)` alone is necessary
  (paper §3.3, Prop 3.5 sufficient only).
- **H6**: smallest specimen with a `k`-anchored layer (`k ≥ 2`) whose
  walk moves phase under a *neutral* `k`-window (an excursion completed
  at the window's last step) — the witness that the engine's operating
  width `k+1` is tight, not merely sufficient (paper §4.3, the remark
  after Lemma 4.12).
**Prediction:** H2/H3 do not exist at 2 states / 1 AP; first hits appear
⟨TBD: record where⟩. Each hit's `.sos`, layers, and witness go into
`tests/**/logs/` and the paper's §7 empirical map.

### E7 — certificate validation (non-LTL side)

For every non-LTL census specimen: extract the certificate (group orbit,
witness words, context shape, period `p′`); verify by the paper §3.4
toggle check — `2p′ + 1` lasso membership tests (`n = 0 … 2p′`) — against
the reference automaton *only* (no algebra on the verifier side); record word lengths against the paper's Theorem-3.4 bounds (each
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
all-constant is an H5 hit (linear-only certificate); 100 exist
(report F5), the map lives in E6/H5. Triptych
vectors (report F4): `Even` — linear ✓ *and* ω-power ✓,
the ω-power family being `F₂(u=ε, v=a, y=a·!a, p′=2)`, the same family
that certifies `EvenBlocks`; `EvenBlocks` — linear `all-constant`,
ω-power ✓. Neither is an H5 hit. **Sizes.** Tabulate component lengths
(`|u|`, `|v|`, `|x|`/`|y|`, `p′`) against the Theorem-3.4 bounds, per
shape and per `|𝒞|` (§3b). **Mechanism column (Prop 3.5).** Per non-LTL
language: does every period-`>1` cycle absorb right multiplication
(right ideal; checking `C·λ(Σ) ⊆ C` suffices)? The read-off *implies*
ω-blindness (paper Prop 3.5(ii)), so column-true must be a subset of the
H5 hits — a column-true non-H5 language is a stop-the-line bug in one of
the two computations, never a statistic; an H5 hit that is column-false
is the real finding (a second blindness mechanism, paper figure).
**Status.** Done catalogue-wide, dual scan and mechanism tiers included
(report F5/F7). Remaining: the full ledger re-runs at M4 on
census-next.

### E8 — decomposition census (C7)

For every census LTL specimen: (i) **OR-split by final layer** —
re-canonicalize each piece, record per-piece read-offs (`|𝒞'|`, ladder
rung, (A)/(B) widths); (ii) the **pair split** — restrict `P` to each
single accepting pair, re-canonicalize, same read-offs, plus the piece's
rung against `L`'s: the incidence of Wagner-ladder climb is the paper's
§5.3(1) guard turned into a measurement (rung read-off via the classifier
subproject — a dependency, note it in the run log); (iii) the **AND-split
search** of C7, reporting factored-vs-`IRREDUCIBLE` fractions and the
factor read-offs (the Thm 5.8 census query). Tables per §3b.
**Prediction:** final-layer pieces never climb the ladder and usually
shrink; pair pieces climb on a measurable fraction (the guard's raison
d'être) — if no pair piece climbs anywhere on the census, the guard is
over-cautious at these sizes and §5.3(1) earns a remark.

### E9 — worked-example curation for the paper

The paper (§5.2 and the figures task `sos_toltl_figures.md`) needs a
small gallery of specimens, each exercising one stratum of the engine
visibly, each small enough to print its label stack. This is a
*selection* task over material that already exists — the flat-canon
catalogue, the triptych fixtures, and the pre-SoS automaton test set
(the aut2ltl portfolio fixtures, incl. `samples/fixtures/hoa/anchor/`,
`…/kanchor/`, and the large-automaton/small-formula showpieces where
kanchor/daisy peeling solves naturally) — plus a handful of named
builds. Theory picks from the returned ledger; do not paste anything
into the paper.

Wanted, one to three candidates each, with per-candidate deliverable
`(.sos id or fixture path, |𝒞|, layer list with |R| and entry classes,
letter-kind tables, (A)/(B) widths per layer, ladder rung,
prefix-independence, emitted DAG size, emitted label stack raw +
Spot-simplified formula)`:

1. **Pure peel, longer chain.** Every layer a singleton, R-depth ≥ 3,
   not prefix-independent (so `leave` chains and reach shape survive);
   the `F a` of paper §5.2 is the depth-2 instance — find depth 3–4
   with the formula still one line.
2. **Anchored moving layer with a live `STAY∞`** *(answered — the
   gallery's `2state1ap0acc_024`, `|𝒞| = 6`: final layer `{1,4}`
   moving, accepting, (B)-determined, with exits — `STAY∞` and `LEAVE`
   live in one layer; 219 such languages, this the smallest)*.
   `G(a → F b)` cannot serve: its final layer fails (B) at every width
   (report F13 / E6-H3). Refinement (paper §5.2, Example 4): in the
   `|𝒞| = 6` specimen the `LEAVE` chain is semantically `⊥` — every
   exit lands on the empty-tail zero. For a specimen where *both*
   branches carry weight, re-query with the extra filter: accepting
   final layer *and* an exit child with `T ≠ ∅`. Side note kept for
   theory: the exact label of
   `G(a → F b)` is `GF b ∨ G(!a∧!b) ∨ F(b ∧ X G(!a∧!b))` — flat LTL —
   so F13's obstruction is the (B) *vocabulary* (recurring window
   sets), not LTL-expressibility; see the paper's §5.1 ⟨TBD⟩ on
   anchored parks.
3. **The named 2-AP builds:** `a U G b`, `a W G b`, `(GF a) U (G b)` —
   build `𝓘(L)` for each, report the read-offs; expected to exercise
   the anchored-transient-then-safety peel and the strength
   stratification; whichever is smallest and cleanest becomes a paper
   candidate.
3a. **`GFa ∧ FGb` — the paper's Example 3 and §5.3 specimen, one
   object, two treatments.** The paper hand-works its full stack
   (four classes `[ε], β₀, β₁, ⊥`; singleton peel; live `STAY∞` at
   `β₁` = `Gb ∧ GF(a∧b)`; frozen `⊥` with (B) at `k′ = 1`; the
   prefix-independent collapse to `FGb ∧ GF(a∧b)`). Provide the
   `.sos`, conformance-check every line of the paper's stack (classes,
   `λ`, `P`, layers, widths, emitted label), and produce the two
   AND-split quotient tables (`FGb`, `GF(a ∨ !b)`) the paper's §5.3
   ⟨TBD⟩ displays. A divergence from the paper's hand stack is
   stop-the-line for the paper text (theory to adjudicate which side
   erred).
3b. **The width-comparison exemplar, both paths.** `GF(a ∧ Xa)` on the
   kanchor side needs `k = 2` pairs on the minimal DBA (kanchor doc
   §9.2, fixture `samples/fixtures/hoa/kanchor/gf_a_xa.hoa`, label
   `GF(a ∧ Xa)` exact with no simplifier); the SoS side anchors its
   moving layers at width 1 and pays width 2 only in the frozen
   window (paper §5.2). Confirm the pair `(form width 2, algebra
   width 1)` lands in the E3 table as its exemplar row.
4. **Graded exhibit, smallest available.** A `k = 2`-anchored layer
   with the smallest `|𝒞|` in the catalogue (the F8 exhibit
   `2state1ap0acc_086_c` at 12 classes is the current holder — is
   there smaller?), for the §4.3 correction's discussion.
5. **Kanchor/daisy showpieces.** From the automaton portfolio's test
   set: two or three large-automaton inputs whose portfolio formula is
   tiny; run them through the SoS path (`𝓘(L)`, layers, engine) and
   report both formulas side by side — paper material for §8's
   readability yardstick if the SoS label matches or beats the
   portfolio's.

Constraint reminders: per-example probes single-input ≤ 15 s; ledger to
`tests/sos2ltl/logs/`; every candidate keyed by its canonical `.sos`
(presentation multiplicity noted where a fixture automaton is the
source).

### E10 — branch factoring: guard grouping and residual-indexed exits
(paper §6, rendering 1)

Two sharings on the engine's output, both exactness-preserving by the
paper's label contract (any exact label for the tail language serves),
to implement and measure:

0. **Guard synthesis (prerequisite, needed independently).** A
   renderer taking any letter set `S ⊆ Σ` to a *minimized Boolean
   formula over AP* whose satisfying valuations are exactly `S`
   (BDD-backed; deterministic output so canonicity survives). The
   current renderer ORs concrete letters only where the labeling is
   injective; on ≥ 2 AP that emits cube unions and can never produce
   `⊤` — so no brick's `S U ψ` ever collapses to `F ψ`, and guards
   like `b` or `!b` (paper §5.2, Example 3) print as two-cube
   disjunctions. Every guard position of every brick (St/Mo/Ex sets,
   anchors, window letters after λ-restore) goes through this
   component. Paper reference: §2.1's set-as-formula convention.
1. **Guard grouping (rendering-level).** Every exit fan
   `⋁_{a ∈ Ex(c)} (a ∧ X φ_{c·a})` renders grouped **by child key** —
   the target class, or its residual when item 2 is on — one disjunct
   per distinct child, the guard a letter set rendered by item 0 (`⊤`
   when all letters agree). (Keying on the target class instead blocks composition with
   item 2: two classes sharing one residual keep two arms.) Same
   grouping inside `leave`'s disjunction and the `TL` trees. Purely a
   printer/DAG-shape change; conformance identical.
2. **Residual-indexed exit children (memo-level).** Key exit children
   by the *residual* of the target class (fold the class key through
   the `.sos` residuals block), not by the class: branches that
   diverge in class but re-merge in future share one child label. The
   within-layer machinery (laws, anchors, windows) stays class-keyed;
   only the `X φ_target` slots coarsen. **Acyclicity care point:** the
   shared label must be one the R-order induction has *already built*
   (reuse-already-built, or equivalently an R-minimal representative);
   an arbitrary representative (e.g. shortlex-least) can close a
   cycle — prefix-independence is the extreme case, one residual
   shared by every class, whose "label" is the whole extraction (the
   paper's §5.1 no-recursion trap).

**Measurements, over the census (§3b discipline):** per language, the
class-vs-residual distinct-child counts; DAG and flat sizes before /
after each sharing (separately and combined); the count of `⊤`-guard
arcs (all-exits-one-target); no conformance regression (the survey
gate stays SUCCESS — any verified non-equivalence is stop-the-line, it
would mean the residual fold or the grouping is wrong, not a
statistic). **Prediction:** grouping is pure win on flat size, largest
at ≥ 2 AP (letter fans); residual indexing fires on a measurable
minority of languages (classes strictly finer than residuals is
common — every non-prefix-independent language with a group-free
algebra has candidates) with modest DAG wins. On prefix-independent
languages residual indexing degenerates (one residual) and the correct
mechanism is the paper's Lemma 5.2 emit-directly rule, not the memo —
report those languages under the emit-directly column, not as
residual-sharing wins.

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
- **`FLAT_OVERFLOW` on the DG baseline is a datum** (the paper's §2.3 point),
  expected already on mid-census instances.

## 6. Milestones

- **M1** — C1+C2+C3+C5, E0 gate green, E1+E2 tables produced. *(Done.)*
- **M1.5** — census hygiene and the no-engine ledgers: E1/E2 per §3b
  (frame declared, per-shape rows, both weightings, degenerate line);
  E4-interim; E7 dual scan. *(Done except the early E3 pass — still
  todo.)*
- **M2** — C4 walk+window engine on the (A,k=1)/(B,k'≤2) strata, E0
  formula prediction green, E4(a) vs (b) ledger on the census subset the
  engine covers; conformance via the survey oracle. *(Done, plus E10
  beyond plan; the graded stratum declines to DG per report F8.)*
- **M3** — graded engine at window width `k+1` (paper §4.3, Thm 4.13:
  transient fold trees `TR`/`TL`, `step_κ`), scoped DG fallback on the
  layer action monoid `𝒜_R` (paper Prop 4.14) — full-coverage engine;
  full E4, E3; E8. *(Todo; the graded engine is gated on the paper's
  §4.3 completeness re-proof; C7 is done.)*
- **M4** — C6 + E5; E6 sweeps; E7 re-run on census-next. *(Todo; C6
  blocked on the paper's Thérien–Wilke freeze.)*

Every milestone ends with a report appended to `sos_toltl_report.md`
(ledger style, one row per finding, predictions checked off or refuted —
a refuted prediction is a paper edit, not a footnote).
