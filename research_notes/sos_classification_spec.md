# SoS Classifier — Implementation and Experimentation Specification

**Status:** rev. 3, 2026-07-09. Rev. 1 was the declaration of intent; the
iteration-1 report (`sos_classification_report.md`) lands K1–K3 and X0/X1.
Rev. 2 binds the next iteration: K4 with its designed fixture (`Fork`,
C§9), the acceptance-family spectrum law (C§11), and the reporting
requirements on the census — bench manifest, per-shape ventilation, degree
ordering, dictionary naming. Rev. 3 adds section 9 — the equivalence
oracle, specified ahead of its commission: it is **blocked on
`sosl.sos.calculus`** (`sos_calculus_spec.md`, milestone CAL2) and must not
be started before that package stands; K4 is unaffected.

**Normative math.** `research_notes/sos_classification.md` (the companion
theory note, extending [SωS26] §7). Every procedure named below is defined
and justified there, with sources; this document only fixes tool shape,
harness, experiments, and milestones. Section references `C§n` point into
the companion.

**One-line goal.** Build `sos_classify`, a tool that reads one `.sos`
invariant and emits the complete classification record of the language —
identity data, LTL-definability, the safety–progress/topological rung, the
parity/Rabin index, the chain and superchain numbers, and the Wagner degree
— every verdict carrying a replayable witness.

---

## 1. Objects

**Input.** A `.sos` file (format of `sosl/sosl/sos/io/sos_format.md`): classes
with shortlex keys, letter map, multiplication table `M`, accepting pairs
`P`. The residuals block, if present, is ignored. Optionally, a
deterministic EL automaton (HOA) presenting the same language — needed only
by the Wagner-degree recursion (section 3.4); its absence degrades exactly
one field.

**Output record.** One flat JSON object (also human-readable text):

```
  aperiodic: bool            # C§4 — LTL-definability
  m_plus, m_minus: int       # C§5 — chain numbers (−1 = none)
  n_plus, n_minus: int       # C§6 — superchain numbers (−1 = none)
  rungs: { open, closed, weak, dba, dca: bool }      # C§7 table
  boolean_level: int         # least n with X in Σ_n / Π_n, when weak
  parity_length: int         # least m with m_plus <= m−1  (C§7)
  co_parity_length: int      # least m with m_minus <= m−1
  mu: ordinal                # C§8, Cantor form as a string, e.g. "w^2·1"
  sign: "sigma"|"pi"|"delta"
  gamma: ordinal | "PARTIAL(mu)"    # PARTIAL when derivation needed and no HOA given
  phi: (gamma, sign)         # the Wagner degree
  witnesses: {...}           # section 3.5
```

**Witnesses.** Every non-trivial verdict ships its certificate, expressed in
*lassos over the class keys* so it can be replayed against any presentation
of the language by plain membership queries (one per lasso — the `sosl`
teacher replays them as-is):

- non-aperiodicity: the class `c` and its power cycle (`key(c)`, period);
  the replay is the pair of lassos of [SωS26, §7.2]'s group read-off;
- a chain: `(key(s); key(e_0), …, key(e_m))` plus the `m+1` lassos
  `key(s)·key(e_i)^ω` with their expected alternating bits;
- a superchain: the chains plus the connecting words `u_i` (shortlex
  witnesses of `s_i ∈ s_{i−1}·S₊`, found by BFS in the right Cayley graph);
- a derivation (K4): the collapsed presentation `∂𝒜`, the derivative's own
  record, and the recursion trace `µ₀, µ₁, …` whose Cantor sum is `γ`.

---

## 2. Tool I/O

```
sos_classify <file.sos>
             [--hoa <file.hoa>]     # enables the full gamma recursion (3.4)
             [--json <out.json>] [--certificates]
             [--expect <fixture.json>]   # assert-equal against a fixture record
```

Exit codes: `0` record emitted; `2` record emitted with `gamma` PARTIAL
(derivation needed, no HOA given — not an error); `3` malformed input;
`4` internal invariant violation (an assertion of section 4 fired — always
a bug).

---

## 3. Components

### 3.1 Primitives layer (C§2)

From `M` alone: power orbits (idempotent power and eventual period per
class), the idempotent set `E`; right/left Cayley reachability and the
Green preorders `<=_R`, `<=_L`, `<=_H`; the `H`-order Hasse DAG on `E`
(test: `ef = fe = e`); linked-pair enumeration; the complement flip of `P`.
The identity class `[eps]` is excluded from stems and idempotents
throughout (as in the `.sos` conventions). This layer is shared by every
band and is the natural first deliverable.

### 3.2 Chain engine (C§5)

Longest-alternating-path DP over the `H`-Hasse DAG of `E`, per admissible
stem (`s·e = s`), scoring alternation of `(s, e_i) ∈ P`; emits
`(m_plus, m_minus)` with one maximal witness each. The soundness and
completeness of searching only the Theorem-6 normal forms is C§5's
transport argument — the engine implements the search, not the proof.

### 3.3 Superchain engine (C§6)

Mark stems carrying maximal-length chains with their signs (from 3.2);
longest sign-alternating strictly-`R`-descending path over the marked
stems' `R`-classes; emits `(n_plus, n_minus)` with a witness. Then the
read-off table of C§7 (rungs, boolean level, parity lengths) and
`mu`/`sign` of C§8 are pure arithmetic on the four integers.

### 3.4 Degree assembly (C§8)

If `m = 0` or `n_plus != n_minus`: `gamma = mu`, done — this covers every
case where no derivative is needed (all of the triptych, C§9). Otherwise
the recursion needs the derivative language: with `--hoa`, build the
derived automaton (collapse of the maximal-superchain basins, [CP99 §3] as
restated in C§8), rebuild its `.sos` through the in-repo construction, and
recurse (termination: `m` strictly decreases). Without `--hoa`, emit
`gamma = PARTIAL(mu)` and exit 2. The designed specimen for this path is
`Fork` (C§9): `ϕ = (ω+1, δ)`, exactly one derivation, `∂Fork` clopen; its
3-state EL presentation is given in C§9 and its ground-truth `.sos` comes
from the in-repo construction. No census case reaches this regime — C§11
proves none can under generalized-Büchi acceptance — so `Fork` is the
acceptance test. Reading the derivative's chain numbers
directly off `𝓘(X)` is flagged in C§8 as open — do NOT attempt it in this
iteration.

### 3.5 Certificate emitter

Renders the witnesses of section 1 and, under `--certificates`, replays
each lasso against the `--hoa` presentation when given (one simulation per
lasso, the `sosl` teacher's `member`), asserting the expected bits. A
witness that fails replay is exit code 4.

---

## 4. Soundness harness

Layered, all automated, all green before any experiment is reported.

1. **Internal laws (free, always on).** On every run assert
   [CP97, Props. 6, 10] as restated in C§5–6: `0 <= m < ∞`,
   `|m_plus − m_minus| <= 1`, `|n_plus − n_minus| <= 1`,
   `n >= 1 ⟹ m_plus = m_minus`; every emitted witness internally
   consistent (linkage, strict `H`/`R`-descents, alternation).
2. **Duality gate.** Classify `L` and its complement (flip `P`) in one run;
   assert `m_plus ↔ m_minus`, `n_plus ↔ n_minus`, `sigma ↔ pi`,
   `delta ↔ delta`, `gamma` equal, and rung dualities (open ↔ closed,
   dba ↔ dca). Costs one extra classification; run it on every case.
3. **Fixtures.** The triptych records of C§9 (`Even (0,0,0,1)/(1,σ)`,
   `GF(aa) (0,1,−1,0)/(ω,σ)`, `EvenBlocks (1,2,−1,0)/(ω²,σ)`) are
   hand-verified in the companion; assert byte-equality of the emitted
   records against them via `--expect`. Rev. 2 adds the fourth fixture
   `Fork (1,1,0,0)/(ω+1,δ)` (C§9) — byte-equality including
   `n_derivations = 1` and the derivative's clopen record `(1, δ)`.
4. **Cross-checks against Spot (bounded-or-skipped, per repo discipline).**
   Where Spot exposes a matching test — safety / co-safety, weak
   (obligation), DBA-realizability, parity-index style information —
   compare verdicts over the census. Expect naming mismatches before bugs:
   the Wagner-vs-Borel dictionary of C§7 is normative; document every
   mapping used. A Spot timeout is a skip, never a wait.
5. **Witness replay (5 = 3.5 under the harness).** For every census case
   with a source HOA: replay all witnesses. This is the deepest check — a
   chain witness ties the algebraic verdict back to concrete lassos of the
   language.
6. **Spectrum law (corpus-level, C§11).** Every input whose acceptance is
   generalized-Büchi must classify inside Proposition 11.1's list —
   `m_plus <= 0` and `ϕ ∈ {(0,σ), (0,π)} ∪ {(n,s) : 1 ≤ n < ω} ∪ {(ω,σ)}` —
   and never into the derivative regime. A violation is exit 4: either the
   classifier or the corpus's acceptance labeling is wrong.

---

## 5. Experiments

Corpus: the census + triptych + the two stall specimens, as in
`sos_learning_spec.md` §6 (same manifest; ground-truth `.sos` from the
construction). Rev. 2 adds the `Fork` specimen with its HOA (C§9).

**The bench is itself a deliverable (rev. 2).** The report must state
precisely what was tested: deterministic complete transition-based EL
automata, enumerated exhaustively over *which* shape parameters (states,
atomic propositions, colours, guard alphabet) — "exhaustive census" with no
manifest is not a result. Concretely, a **manifest table**, one row per
shape family × acceptance family (generalized-Büchi `⋀ Inf` / parity
`Fin`/`Inf` alternation / general EL if emitted), with columns:

- raw enumerated automata, and what "survivor" means (which filters);
- **distinct languages**, deduplicated by `𝓘`-hash ([SωS26, Thm 5.1]'s hash
  join) — the shape's automaton-to-language compression ratio is a datum no
  other tool computes;
- the distribution of `N = |𝒞|` over the shape's distinct languages (min /
  median / max suffices), feeding the size-vs-degree cross-tabulation of
  C§12 — deep degrees force `N` up, large `N` does not force depth, and
  where the census sits in that triangle is the measurement.

The parity corpora are census members, not a sidebar: same manifest, same
tables, same gates.

**X0 — Validation.** Harness green over the corpus. Gate for the rest.

**X1 — The classification profile of the census.** For every census
language: the full record. Deliverables: distribution tables — rungs,
parity lengths, `(m, n)` pairs, degrees — over the census; the first
measured Wagner-degree profile of a systematically enumerated language
class (no existing tool computes this — report it as data, not just
validation). Rev. 2 reporting requirements: (i) every distribution
**ventilated per shape family and per acceptance family**, aggregate last,
so the acceptance-family effect (C§11) is visible in the data; (ii) the
degree table ordered by Wagner degree, weakest first, with the trivial pair
`(0,σ)`/`(0,π)` (empty / universal) in a separated block — it is the weakest
class, not two rows among the proper ones; (iii) readings named by the
C§7–8 dictionary — in particular `(1, δ)` is the nontrivial **clopen**
class, properly `Δ₁` (rev. 1's report misnames it "properly Δ₂"; properly
`Δ₂` is `(2, δ)`, coordinates `(0,0,1,1)`); (iv) **every distribution over
distinct languages, not enumerated automata**: dedup by `𝓘`-hash first,
count each language once, and carry its **abundance** — the number of
enumerated automata realizing it — as a column. The abundance-weighted
(per-automaton) view may appear alongside, but the headline profile is
per-language: a probe of `2state1ap1acc_buchi` shows 759 LTL-answering
automata collapsing to at most 73 languages (by formula hash — an upper
bound, the translator being presentation-dependent), with `true` alone
absorbing 43.6% of the answers. Free cross-path gate while dedupling: within
one `𝓘`-bucket, every formula produced by the aut2ltl translation path
names the same language; a bucket holding non-equivalent formulas convicts
one of the two paths.

**X2 — The paper table, exercised.** One row per band of [SωS26, §7]'s
summary table: demonstrate each classification answered on the same one
object, with its witness, on a named example. Deliverable: the worked
section feeding the core paper's §7 (and the companion's C§9 extended
beyond the triptych by machine).

**X3 — Cost.** Wall time and component counts (`|E|`, DAG sizes, DP sizes)
vs `N` over the census and the stretch set: confirm the polynomial claims
of C§10, and locate the practical ceiling (expected: the ceiling is the
construction of `.sos`, not the classifier — measure both to substantiate
it).

---

## 6. Metrics file (`stats.json`)

```
case_id, shape_family, acceptance_family, classes, n_idempotents, n_linked_pairs,
aperiodic, m_plus, m_minus, n_plus, n_minus,
mu, sign, gamma, gamma_partial (bool), parity_length, co_parity_length,
rung_open, rung_closed, rung_weak, rung_dba, rung_dca,
n_derivations, witness_replayed (bool),
wall_seconds, verdict (SOUND|MISMATCH|PARTIAL|BUDGET)
```

---

## 7. Milestones and acceptance criteria

- **K1 — Primitives + identity + LTL cut.** Layer 3.1, band read-offs C§3–4
  with the group witness. Accept: fixtures' `aperiodic` column green;
  duality gate green on the census; witness replay green where HOA exists.
- **K2 — Chains.** Engine 3.2, the `m`-dependent rungs and parity lengths of
  C§7. Accept: triptych `(m_plus, m_minus)` fixtures green; internal law 1
  and duality green corpus-wide; Spot safety/weak/DBA cross-checks
  reconciled (mismatches documented as mapping notes, not code changes,
  unless a witness replay refutes us).
- **K3 — Superchains + degree, non-derived.** Engine 3.3, `mu`/`sign`, and
  `gamma` on the `m = 0 ∨ n_plus != n_minus` cases (all of the triptych).
  Accept: full triptych records byte-equal to C§9; census X1 tables
  generated.
- **K4 — Derivation + campaign.** Component 3.4, X1–X3 executed, results
  CSV and figures by script. Accept: every census case SOUND or PARTIAL
  with PARTIAL only where derivation is genuinely required and no HOA was
  supplied; `n_derivations` and termination logged; X-deliverables
  produced. Rev. 2 sharpens the gate: `Fork` classified end-to-end — exit 2
  with `PARTIAL(ω)` from the `.sos` alone, `ϕ = (ω+1, δ)` with `--hoa`,
  `n_derivations = 1` — the spectrum law (harness 6) green corpus-wide, and
  the X1 deliverables regenerated to rev.-2 reporting (bench manifest,
  per-shape ventilation, degree ordering, dictionary naming).

Non-goals for this iteration: reading the derivative off the invariant
without a presentation (open, C§8); the sub-LTL fragments (FO², Σ₂,
until-rank — [SωS26, §7.2] notes they need variety + topology machinery
beyond this tool); any classification of non-ω-regular inputs.

---

## 8. Expected failures — read before filing a bug

| # | check | config | expectation | on failure |
|---|---|---|---|---|
| A1 | internal laws (4.1) | all | always green | classifier-core bug |
| A2 | duality gate (4.2) | all | always green | asymmetric bug in chain/superchain search |
| A3 | witness replay (4.5) | HOA available | always green | the verdict is wrong or the witness extraction is; the replay transcript localizes it |
| A4 | spectrum law (4.6) | gen-Büchi inputs | always green | classifier bug, or the corpus's acceptance labeling is wrong |
| P1 | triptych fixtures (4.3) | K2+ | green | bug — the values are hand-verified in C§9; recheck against the companion before touching them |
| F1 | Spot cross-check disagrees | X0/X1 | MAY be red | naming/dictionary mismatch first (C§7 box); only a failed witness replay downgrades it to a bug |
| F2 | `gamma` PARTIAL without `--hoa` | any | expected | by design (exit 2); supply the HOA to resolve |
| F3 | stretch-set case exceeds budget | X3 | allowed | record BUDGET; the ceiling being the construction, not the classifier, is itself the X3 result |

---

## 9. The equivalence oracle (rev. 3 — spec'd ahead, blocked on the calculus)

**Commission gate.** Do not start before `sosl.sos.calculus` reaches CAL2
(`sos_calculus_spec.md`). This section assumes that spec realized: `Table`,
`FoldedLanguage`, `align`, `equivalent`, Proposition W's cell order, and
witness replay all exist and their harness is green. Everything here is
composition plus requirements — if an algorithm seems to be missing, it
lives in the calculus spec, not here.

**One-line goal.** `sos_equiv(A, B) -> EQUAL | Counterexample(lasso)`:
decide language equality between a `FoldedLanguage` client `A` and a
reference invariant `B = 𝓘(L)`, returning the *minimal* disagreeing lasso
under the teacher discipline (shortest stem, then shortest loop, then
shortlex) — the exact-by-reference oracle of `sos_learning_spec.md` §3.2
(rev 2026-07-08h), packaged as a standalone component.

**The two sides.**

- `B` is always a genuine (reduced) `Invariant` — for census work, the
  precomputed corpus `.sos`. Its verdicts are algebraic (`Val_P`).
- `A` is anything satisfying `FoldedLanguage`: another invariant (then this
  tool is the calculus's `equivalent`, nothing more), or a learner Cayley
  hypothesis adapted to the protocol — `step` from its table, `verdict`
  from its P-cache read-off. **Normative:** the adapter must route every
  `A`-verdict through the hypothesis's own prediction discipline; no
  linked-pair law, no idempotent-power shortcut on the `A` side — a
  mid-run form need not be associative (`sos_learning_spec.md` §4.2), and
  the oracle must certify the object *as it answers*, not an algebraic
  idealization of it.

**Procedure** (= calculus `align` + `equivalent`, with the requirements
pinned):

1. `aligned = align(A, B)` — shortlex BFS, lazy mult, `≤ n_A·n_B` nodes.
2. Scan aligned cells in the normative order; first cell with
   `Val_A ≠ Val_B` returns its canonical lasso as the counterexample
   (globally minimal by Proposition W); an exhausted scan returns `EQUAL`
   with the scan itself as the certificate (`|nodes|`, cell count — record
   both in the run's stats).
3. No work cap, no `ExactTooLarge`: the whole computation is
   `O(n_A·n_B·|Σ|)` steps plus `O(|nodes|²)` constant-time verdicts. If a
   census case ever feels slow here, that is a bug or a pathological
   alignment ratio — report it, never cap it.

**Acceptance gates (all three before the learner commission is requested):**

1. **Closure-oracle conformance.** On the E0 named cases (triptych + the
   two permanent-stall specimens, both legs): every counterexample, every
   ledger, every learned invariant byte-identical to the existing
   transformation-closure oracle's. Both decide the same question and both
   minimize under the same discipline, so any drift convicts one of them —
   bisect with the witness replay before touching either.
2. **Witness replay.** Every returned counterexample replays correctly
   against both sides and, where a det HOA exists, against it (bounded).
3. **The OVERSIZE stragglers.** Re-run the deferred `OVERSIZE`
   classifications of the flat_canon ablation leg (`ref 57 / 93`,
   `3state1ap0acc`) to completion; their permanent-vs-transient verdicts
   are the payoff and go to the learner thread's E2 counts
   (`sos_learning_report.md`). Outputs land under the curated `reference/` tree
   per the reproducibility floor.

**Certification note (record with every run).** The trust anchor is the
reference `B` — the construction's output, independently cross-checked by
the census byte-equality gate — not a product with the presenting
automaton. Same certification level as the closure oracle, different
mechanism (the F6/RABIT precedent in `sos_learning_spec.md`).

**Consumers, in order.** (1) The learner teacher's `--eq-mode exact`
(`sos_learning_spec.md` §3.2) — a separate commission, requested only after
the gates above are green. (2) This tool's own harness: the duality gate
(section 4.2) and the corpus cross-checks may replace bounded acceptor
comparisons with `sos_equiv` once it stands. (3) Referenceless targets
(learner E6) are out of scope here — they keep the closure fallback.
