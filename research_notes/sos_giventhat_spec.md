# SoS Given-That — Implementation Specification

**Status (2026-07-11).**

| item | state |
|---|---|
| GT1: the interval object + endpoint decisions (§3) | **OPEN — the commissioned milestone.** Everything needed is specified below to the function level; start here and stop here. |
| GT2: the ladder tests (§4) | SPECIFIED — do not start before GT1 acceptance |
| GT3: stutterization, two tiers (§5) | SPECIFIED — tier 2 is the hard one; tier 1 first |
| GT4: band-minimal Wagner degree (§6) | SPECIFIED — doubles as a theory probe; blocked on GT2 |
| GT5: the W-series campaigns (§7) | W0 (census-shaped) specified; W1 (MCC data) **blocked on data provisioning — do not go fetch it yourself** |

An implementer starting cold reads, in order: this header, §0–§1, the
section for the milestone at hand, §8 (expected failures) before filing
any bug, §9 (traps) before writing any code. Revision history lives in
git and `docs/HISTORY.md`, not here.

**Normative math.** `research_notes/sos_giventhat.md` (the given-that
paper). Section map: paper §3 → GT1; paper §4 → GT2 + GT4; paper §5 →
GT3; paper §7 → GT5. Behind it, `research_notes/sos_calculus.md`
[SωSC26] for the calculus (align / operate / reduce, the surgery
catalog, the hulls) and its spec `sos_calculus_spec.md` for the package
you are building on. Where this document and the paper disagree, STOP
and report — do not reconcile silently (the paper may be wrong; that is
a finding, see the report contract §10).

**One-line goal.** `sosl.sos.giventhat` — a new package at
`sosl/sosl/sos/giventhat/` — turns two invariants `𝓘(¬φ)` and `𝓘(K)`
into the given-that interval object of the paper, and answers, exactly
and with witnesses: does `K` settle `φ`; does `K` refute `φ`; does the
interval contain a safety / co-safety / obligation / recurrence /
persistence / stutter-invariant `B`; and at what minimal Wagner degree.

**Layering law (hard).** `sosl.sos.giventhat` imports `sosl.sos`
(objects, io), `sosl.sos.calculus` (Table, align, materialize, surgery,
decide, reduce, witness), `sosl.sos.classify` (the stutter read-off) —
and NOTHING else in the repo. Never `sosl.learn`, `sosl.teacher`,
`sosl.experiment`, `tests.*`. Test scripts under `sosl/tests/giventhat/`
may import anything they need (spot, replay hooks), like the calculus
gates do. One cross-package addition is commissioned in GT1
(`conjugacy_classes` in `calculus.surgery`, §3.2) — that one function,
nothing else moves in `calculus`.

**The one theorem you must keep in your head.** Paper Prop 3.1: on the
materialized product table, `P_max \ P_min = P_K^c`, and the legal `B`s
are exactly `P_min ⊔ (a union of conjugacy classes of linked pairs
outside P_K)`. Every data structure below is this sentence reified.
It is also a *runtime assertion* (§3.3): if it ever fails, the bug is
upstream (align / materialize / saturate), never here — report with the
failing case, do not work around.

---

## 0. Prerequisites (all DONE, all reused, none reimplemented)

From `sosl.sos.calculus` (see its spec for contracts):

- `Table` — `(𝒞, λ, M)` + memoized `fold` / `idem` / linked pairs /
  keys + `val(P)` closures. Pair sets are immutable sets of linked-pair
  ids over their table.
- `align(A, B) -> Aligned` and `materialize(aligned, A, B) -> Product`
  — the product table with **both** input pair sets carried onto it
  (`pairs_a`, `pairs_b`). Given-that operates on the *materialized*
  product: the endpoints are cross-table Boolean combinations, and
  `Aligned` alone cannot host surgeries (trap #2).
- `surgery`: `complement / union / intersection / difference`,
  `saturate` (with the mandatory `linked_pair_of` renormalization —
  calculus spec §3.3; you will lean on it in §3.2), `safety_closure`,
  `interior`, `is_safety`, `is_cosafety`, `is_obligation`,
  `obligation_degree`, `live`.
- `decide`: `member / is_empty / is_universal / included / equivalent /
  intersecting_word` — all witness-carrying, all scanning cells in the
  discipline order (shortest stem, shortest loop, stem lex, loop lex),
  so every witness is the globally minimal lasso (calculus spec Prop W).
- `reduce(table, P) -> Invariant` — the canonical re-quotient.
- `witness.Witness` with `replay(oracle)`.

From `sosl.sos.classify`: `is_stutter_invariant(inv)` — the
`λ(a)² = λ(a)` read-off.

Corpus: `genaut/corpus/flat_canon/` — 3 938 canonical `.sos` invariants
+ paired det HOA, `.cat` sidecars carrying the Wagner coordinates
`(m⁺, m⁻, n⁺, n⁻)`, the LTL bit, and the `stutter:` tag. Alphabet
strata as in calculus spec §8.2: sample pairs WITHIN one stratum only.

---

## 1. Package shape

```
sosl/sosl/sos/giventhat/
    __init__.py    re-exports given_that, Interval, the GT2/GT3 entry points
    interval.py    GT1: Interval, given_that, endpoint decisions, choose
    ladder.py      GT2: forced classes, per-rung existence tests, hulls
    stutter.py     GT3: stutter congruence + tier-1 quotient test;
                   tier-2 self-alignment
    degree.py      GT4: band-minimal Wagner degree (greedy + brute probe)

sosl/tests/giventhat/
    fixtures.py        builds + caches the two fixture DELAs (§3.5)
    interval_gate.py   GT1 acceptance
    ladder_gate.py     GT2 acceptance (incl. the corpus rung oracle)
    stutter_gate.py    GT3 acceptance
    degree_gate.py     GT4 acceptance
    w0_census.py       GT5/W0 campaign
    logs/              working logs (never /tmp)
```

Library only, no CLI. Type-annotate every public signature (params and
return; `typing.Optional/Tuple/FrozenSet`, `Protocol` where a contract
is behavioral) — house rule.

---

## 2. Objects

**PairSet, RClass, ConjClass.** A pair set is what `calculus` says it
is. An `RClass` is a strongly connected component of the right-Cayley
graph `c → M(c, λ(a))` restricted to linked-pair stems (the SCC pass
`is_obligation` already runs — expose/reuse that routine rather than
writing a second Tarjan; if it is private, promote it to a shared
helper `r_classes(table) -> Sequence[FrozenSet[ClassId]]` inside
`calculus.surgery` as part of the GT2 landing, with its own one-line
gate: `R`-classes partition the linked stems). A `ConjClass` is a
conjugacy class of linked pairs (§3.2).

**Interval (the GT1 object, frozen dataclass).**

```
@dataclass(frozen=True)
class Interval:
    table: Table                     # the materialized product table
    p_neg_phi: PairSet               # P_¬φ carried onto table
    p_k: PairSet                     # P_K carried onto table
    p_min: PairSet                   # P_¬φ ∩ P_K
    p_max: PairSet                   # P_¬φ ∪ P_K^c
    freedom: Tuple[ConjClass, ...]   # conjugacy classes of linked \ p_k,
                                     # in first-representative discipline
                                     # order (deterministic)
    @property
    def bits(self) -> int: ...       # len(freedom) — |F| of paper Prop 3.1
```

---

## 3. GT1 — the interval object + endpoint decisions (THE MILESTONE)

Normative math: paper §3 (Prop 3.1 and the two decisive checks).
Everything in this section is prescribed; if an ambiguity remains,
choose the reading that matches the paper and say so in the report.

### 3.1 `given_that`

```
given_that(neg_phi: Invariant, k: Invariant) -> Interval
```

Steps, in order:

1. **Assert same alphabet** (same AP set and order). Do not adapt —
   `inverse_substitution` is the adapter and it is out of scope. A
   mismatch is a caller error: raise.
2. `aligned = align(neg_phi, k)`; `prod = materialize(aligned,
   neg_phi, k)` — one product table, both pair sets carried
   (`p_neg_phi = prod.pairs_a`, `p_k = prod.pairs_b`).
3. `p_min = intersection(p_neg_phi, p_k)`;
   `p_max = union(p_neg_phi, complement(p_k))` — two free surgeries on
   the product table.
4. `freedom = tuple(C for C in conjugacy_classes(prod.table)
   if C.isdisjoint(p_k))` (§3.2; a class is entirely in or entirely
   out of the saturated `p_k` — assert that dichotomy per class while
   filtering).
5. **Runtime law (assert, always on, cheap):**
   `difference(p_max, p_min) == complement(p_k)` and the union of
   `freedom` equals that same set, disjointly. This is paper Prop 3.1;
   a violation is an upstream bug — raise with the offending pair id,
   never continue.
6. Return the frozen `Interval`.

Cost: one align + one materialize (the only product-priced moves), one
`conjugacy_classes` pass, `O(|linked|)` surgeries.

### 3.2 `conjugacy_classes` — the one commissioned addition to `calculus.surgery`

```
conjugacy_classes(table) -> Tuple[FrozenSet[Pair], ...]
```

Partition of `linked(table)` into conjugacy classes: process linked
pairs in the deterministic order (sort by
`(len(key(s)), key(s), len(key(e)), key(e))`); for each not-yet-visited
pair, its class is `saturate({pair})` (the existing fixpoint — with its
`linked_pair_of` renormalization; do NOT re-derive the closure, call
`saturate`); mark all members visited; class order = discovery order.
Cost `O(|linked|·n²)` worst case — fine at census sizes; memoize on the
table like `linked` is.

Gate (goes into `interval_gate.py`, runs on every case): the classes
partition `linked`; `saturate({p}) == class_of(p)` for a sample of `p`
per class; for every *saturated* `P` encountered (both carried sides,
`p_min`, `p_max`), `P` is exactly the union of the classes it meets.

### 3.3 Endpoint decisions

```
k_settles_phi(iv: Interval) -> Tuple[bool, Optional[Witness]]
k_refutes_phi(iv: Interval) -> Tuple[bool, Optional[Witness]]
```

- `k_settles_phi`: `is_empty(iv.p_min)` on the product table. True ⟹
  `K ⊨ φ`, done, no model checker. False ⟹ witness = the minimal lasso
  of `ℒ(¬φ) ∩ ℒ(K)` (the scan's first cell — `decide` already returns
  it), provenance string `"k_settles_phi"`.
- `k_refutes_phi`: `is_empty(complement(iv.p_max))`. True ⟹ `K ⊨ ¬φ`
  (every run of a nonempty system is a counterexample). False ⟹
  witness = minimal lasso of `ℒ(φ) ∩ ℒ(K)`.
- **Do not implement a universality scan** — the second check IS
  emptiness of a complement, one flip; that symmetry is a claim of the
  paper (§3) and the code should exhibit it (trap #4).

### 3.4 The choice API

```
choose(iv, chosen: Iterable[int]) -> PairSet     # indices into freedom
decompose(iv, q: PairSet) -> Optional[FrozenSet[int]]
```

- `choose`: `p_min ∪ ⋃ freedom[i]`. By Prop 3.1 the result is saturated
  and in the interval by construction — assert both anyway under a
  `check=True` default (harness runs checked; campaigns may pass
  `check=False`).
- `decompose`: inverse — if `q` is saturated and `p_min ⊆ q ⊆ p_max`,
  return the index set (`q \ p_min` is a union of freedom classes;
  match by intersection — each class all-in or all-out, assert the
  dichotomy); else `None`.
- Laws (gate): `choose(∅) == p_min`; `choose(range(bits)) == p_max`;
  `decompose(choose(S)) == S` for random `S`; monotone:
  `S ⊆ S' ⟹ choose(S) ⊆ choose(S')`.

### 3.5 The fixture pair (build FIRST — everything gates on it)

The paper's §5.2 counterexample, used from GT1 on. `fixtures.py`
builds two DELAs over one AP `p` (exactly two letters:
`a := p`, `b := ¬p` — no fourth-valuation trap here), writes them
under `sosl/tests/giventhat/logs/fixtures/`, canonizes each with
`genaut/gen/canonize.py` (trust its defaults; head its pydoc for the
output flag only), and caches the resulting `.sos` paths.

- `D_ab` — `ℒ = {(ab)^ω}`: states `q0` (initial), `q1`, sink `R`.
  Transitions: `q0 --a--> q1`; `q0 --b--> R`; `q1 --b--> q0` carrying
  acceptance mark `{0}`; `q1 --a--> R`; `R --⊤--> R`. Acceptance
  `Inf(0)`. Deterministic, complete.
- `D_K` — `ℒ = {(ab)^ω, (ba)^ω}`: states `s0` (initial), `x1, x0`
  (the ab-phase), `y1, y0` (the ba-phase), sink `R`. Transitions:
  `s0 --a--> x1`, `s0 --b--> y1`; `x1 --b--> x0` mark `{0}`,
  `x0 --a--> x1`; `y1 --a--> y0` mark `{0}`, `y0 --b--> y1`; every
  other letter from every state → `R`; `R --⊤--> R`. Acceptance
  `Inf(0)`.

Expected facts to assert (each failure = STOP and report, §8/E1):

- `|𝒞(D_ab)| == 6` — the paper's hand computation (`[ε]`, four
  alternating classes by first/last letter, junk). A different value
  convicts either canonize or the paper's §5.2 walkthrough; that is a
  to-theory finding, not something to patch.
- `|𝒞(D_K)|` — record as a datum (no hard assert; the paper does not
  compute it).
- On `iv = given_that(𝓘(D_ab), 𝓘(D_K))`:
  `k_settles_phi(iv) == (False, w1)` with `w1` a lasso of loop length 2
  whose replay is IN both HOAs (it must be `(ab)^ω` up to presentation);
  `k_refutes_phi(iv) == (False, w2)` with `w2` replaying IN `D_K` and
  NOT IN `D_ab` (it must be `(ba)^ω` up to presentation);
  `iv.bits ≥ 1` — record the exact value as a datum (the paper predicts
  the free band is nonempty; its exact class count on the product table
  is not hand-computed — report it).

Witness replay uses the existing teacher replay hook against the det
HOA (calculus spec trap #11: reuse the `.sos`-letter → BDD mapping,
never re-parse letters by hand). Spot bounded-or-skipped as always.

### 3.6 GT1 semantic gates (in `interval_gate.py`)

1. **Metamorphic endpoints** (the deep check): for every lasso
   `(u, v)` with `|u|, |v| ≤ 3` (exhaustive over the fixture alphabet;
   sampled ≥ 500 lassos per corpus case):
   `member(p_min, u, v) == member_¬φ(u, v) AND member_K(u, v)` and
   `member(p_max, u, v) == member_¬φ(u, v) OR NOT member_K(u, v)`,
   where the right-hand memberships run on the ORIGINAL two invariants
   (not the carried sides) — this crosses the align/materialize
   boundary and is the gate that would catch a carry bug.
2. **Endpoint cross-oracle**: `k_settles_phi` agrees with the
   independent route `intersecting_word(aligned)` (no word ⟺ settles);
   `k_refutes_phi` agrees with `included(K ≤ ¬φ)` on the aligned pair.
   Witnesses from both routes replay against both HOAs (bounded).
3. **Prop 3.1 law + conjugacy gate** (§3.1.5, §3.2) on every case.
4. **Choice laws** (§3.4) with 20 random seeded subsets per case.
5. **Corpus campaign**: 300 seeded same-stratum pairs
   `(¬φ := L₁, K := L₂)` from `flat_canon` (seed `20260711`, sampled
   within strata proportionally), plus the 300 reversed pairs
   (`K := L₁`), plus 100 pairs `(L, its complement partner)` — the
   last stratum makes `p_min = ∅` (K settles) a frequent, predictable
   outcome: assert `k_settles_phi` is True exactly when
   `intersecting_word` finds nothing. Per-case budget 15 s; checkpoint
   file; `--one <case>` mode (house rules, calculus spec §8.1 applies
   verbatim).

**GT1 acceptance:** `interval_gate.py` green on the fixture pair and
the full 700-pair campaign, zero unexplained rows; the `|F|`
distribution over the campaign written to
`sosl/tests/giventhat/logs/gt1_bits.csv` (this is a paper §7 datum —
carry it into the report, finding slot F3); `conjugacy_classes` landed
in `calculus.surgery` with its gate and the calculus harness still
green (run it — you touched the package).

---

## 4. GT2 — the ladder tests

Normative math: paper §4 (Lemma 4.1, Props 4.2–4.4). Entry points in
`ladder.py`, all taking an `Interval`, all returning
`(bool, Optional[PairSet] least_witness, Optional[Witness] refusal)` —
on yes, the least (and where cheap, greatest) member; on no, the
minimal lasso certificate (the first hull pair pushed past `p_max`,
rendered as its canonical lasso).

- `exists_safety(iv)`: `safety_closure(p_min) ⊆ p_max` — reuse CAL5's
  `safety_closure`, subset test is one pass; least witness the closure
  itself. `exists_cosafety(iv)`: `p_min ⊆ interior(p_max)`; greatest
  witness the interior.
- `forced(iv) -> Tuple[FrozenSet[RClass], FrozenSet[RClass]]`:
  forced-1 = `R`-classes containing a stem of `p_min`; forced-0 =
  `R`-classes containing a stem of some linked pair outside `p_max`.
  One pass each after `r_classes(table)`.
- `exists_obligation(iv)`: forced-1 ∩ forced-0 == ∅ (paper Prop 4.3).
  Least witness `{(s,e) linked : R(s) ∈ forced-1-closure}` — careful:
  the least member is θ = forced₁ exactly (no closure beyond it);
  greatest is θ = ¬forced₀. Assert both are saturated and in the
  interval, and `is_obligation` (CAL5) holds on both.
- **H-order helper** (in `ladder.py`, memoized per table):
  `h_below(table) -> relation on idempotents`: `f ≤_H e` iff
  `∃x: M(e,x) = f` and `∃y: M(y,e) = f` — two boolean row/column
  sweeps per idempotent pair, `O(|E|²·n)`; fine at census sizes.
- `rec_hull(table, Q) -> PairSet`: least fixpoint alternating
  (a) the Horn rule — for `(s,e) ∈ Q` and `f ≤_H e` with `(s,f)`
  linked, add `(s,f)` — with (b) `saturate`, until stable (≤ `|linked|`
  rounds). Forgetting (b) yields non-language sets; the saturation law
  will convict you (trap #10).
- `is_recurrence(table, P) -> bool`: no linked stem `s` with loops
  `f ≤_H e`, `Val(s,e)=1`, `Val(s,f)=0`. `is_persistence`: mirror.
- `exists_recurrence(iv)`: `rec_hull(p_min) ⊆ p_max`.
  `exists_persistence(iv)`: `rec_hull(complement(p_max)) ⊆
  complement(p_min)` — ONE complement flip, no new machinery; the code
  should be four lines and the paper says why (Prop 4.4).

Gates (`ladder_gate.py`):

1. **The corpus rung oracle** (the decisive one — run it FIRST, before
   any interval work): over all 3 938 corpus invariants,
   `is_recurrence(P) == (m⁺ ≤ 0)` and `is_persistence(P) == (m⁻ ≤ 0)`
   against the `.cat` sidecar coordinates. **The paper hand-checked the
   orientation on four examples; the corpus decides it.** If the gate
   fails *consistently flipped* (agreement rate ≈ 0 under one
   orientation, ≈ 1 under the swap), implement the swap and file the
   flip as a prominent to-theory finding (report slot F5) — the paper's
   §2 paragraph must then be corrected. If it fails *mixed*, that is a
   real bug or a real theory problem: STOP, report the smallest
   disagreeing case.
2. **Hull laws**: `rec_hull` extensive / monotone / idempotent on
   random saturated pair sets; output saturated; `is_recurrence(rec_hull(Q))`
   true; `rec_hull(Q) == Q` iff `is_recurrence(Q)`.
3. **The brute-force lattice oracle** (exactness, the gate that makes
   these tests trustworthy): on every campaign case with
   `iv.bits ≤ 12`, enumerate ALL `2^bits` choices; for each rung,
   `exists_rung(iv) == any(is_rung(reduce-free check on choose(S)))`
   over the enumeration, using the independent CAL5/GT2 predicates
   (`is_safety`, `is_cosafety`, `is_obligation`, `is_recurrence`,
   `is_persistence`) on the raw chosen pair set (no reduce needed —
   the predicates read the table). Also: when yes, the returned least
   witness is ⊆ every enumerated member (leastness, checked
   literally). Cases with `bits > 12`: skip the oracle, record.
4. **Witness discipline**: on no, the refusal lasso replays as ∈
   hull-language and ∉ `L(p_max)` against the exit HOAs (bounded) or
   via `member` on the table (always).

**GT2 acceptance:** rung oracle 3 938/3 938 explained (green or a
filed orientation flip); ladder gates green on the GT1 campaign pairs;
brute oracle zero disagreements on every `bits ≤ 12` case.

---

## 5. GT3 — stutterization, two tiers

Normative math: paper §5 (Prop 5.1, Thm 5.2, Thm 5.3). Tier 1 lands
first and gates alone; tier 2 is a separate landing.

### 5.1 Tier 1 — the quotient test

- `stutter_quotient(table) -> (QuotientTable, pi)`: smallest monoid
  congruence with `λ(a)² ∼ λ(a)` per letter. Union-find over classes;
  worklist of merged pairs; on merging `x ∼ y`, enqueue
  `M(c,x) ∼ M(c,y)` and `M(x,c) ∼ M(y,c)` for every class `c`; drain
  to fixpoint. `[ε]` can never merge (products of non-identity classes
  are non-identity — assert it rather than special-casing, trap #8).
  Quotient table re-keyed by the shared shortlex BFS (same routine as
  align/reduce — one implementation, four call sites now).
- `sc(table, Q, quotient, pi) -> PairSet` (the on-table stutter hull):
  `forced` = one pass over the cells of `table`: for each cell `(c,d)`
  with `Val_Q(c,d)` true, insert `linked_pair_of(pi(c)·e, e)`,
  `e = idem(pi(d))`, into the quotient pair set; then `saturate` in
  the quotient; then pull back:
  `{(s,e) ∈ linked(table) : (pi(s)·idem(pi(e)), idem(pi(e))) ∈ P'}`.
- `exists_stutter_invariant_tier1(iv)`: `sc(p_min) ⊆ p_max`; witness
  on yes: `sc(p_min)` (on-table, canonical); on no: NOTHING is
  concluded (tier 1 is only sufficient — the paper's Thm 5.2; the
  return type must make this unmistakable: return a three-valued
  verdict `YES / UNKNOWN`, never `NO`).

Gates: `sc` extensive / idempotent; `is_stutter_invariant(reduce(sc(Q)))`
true always; `sc(Q) == Q` iff `is_stutter_invariant(reduce(Q))` on
sampled saturated `Q`; metamorphic soundness — for lassos
`|u|,|v| ≤ 3`, if `member(Q, u, v)` then `member(sc(Q), u', v')` for
every stutter-variant presentation `(u', v')` in the same bound.
**Fixture**: on the §3.5 pair, the quotient table must collapse to
`{[ε], Z}` (assert size 2) and tier 1 must return UNKNOWN with
`sc(p_min) = linked` (assert universal) — this is Thm 5.2 running as a
regression test.

### 5.2 Tier 2 — the stutter self-alignment (the hard part)

`exists_stutter_invariant(iv) -> (bool, certificate)` — exact, paper
Thm 5.3. Compute the stutter cell relation `R_st` and scan for a
conflict `(Val_{p_min} true) × (Val_{p_max} false)`.

Prescribed construction (deviations allowed only with a written
justification in the report):

- **Stem relation.** Walk states `(last_letter, c, c') ∈ Σ × 𝒞 × 𝒞`,
  start `(⊥, [ε], [ε])`; step: pick `b ≠ last_letter`, pick
  `g ∈ ⟨λ(b)⟩` and `g' ∈ ⟨λ(b)⟩` *independently* (`⟨d⟩` = the cyclic
  set `{d, d², …}`, memoized per class), move to
  `(b, M(c,g), M(c',g'))`. Reachable set = pairs of folds of
  stutter-variants of a common stutter-free stem.
- **Loop relation.** Same walk, but seeded per first letter `b₀` and
  closed cyclically: accept `(c, c')` reached from `(b₀, start)` where
  the last letter `≠ b₀` OR the loop is a single letter block
  (`y = b₀^k` — the single-letter loop case: `⟨λ(b₀)⟩ × ⟨λ(b₀)⟩`
  directly). Then associated-pair renormalization on both tracks
  (`linked_pair_of`), remembering that the two tracks renormalize
  *independently*.
- **Eventually-constant case.** Normal forms `w·a^ω`: stems from the
  stem relation with last letter `≠ a` (or empty), loops
  `(λ(a)^i, λ(a)^j)` — enumerate directly; do not force it through the
  cyclic walk.
- **Conflict scan.** For every related cell pair
  `((c,d), (c',d'))`: conflict iff `Val_{p_min}(c,d)` and
  `¬Val_{p_max}(c',d')`. Answer yes iff no conflict. Certificate on
  no: the two canonical lassos of the conflicting cells and their
  common destuttered base (reconstruct from the walk path — store
  parent pointers) — "two stutter-equivalent behaviors, one mandatory,
  one forbidden".
- **Do NOT build `SC`'s automaton for the decision** (trap #12). The
  yes-side witness object (an actual `B` for the model checker) is a
  stretch goal: `sc(p_min)` when tier 1 already said yes; otherwise
  mark `witness=None, off_table=True` and stop — constructing
  `SC(L(p_min))` via closure automata + re-entry is future work, not
  GT3.

Gates: (a) fixture: tier 2 must answer **YES** where tier 1 said
UNKNOWN — the paper's headline counterexample, now a three-way
regression (`tier1 UNKNOWN / tier2 YES / spot sirelax-style check YES`
— the last via bounded Spot on the exit acceptors if convenient, else
skip and note); (b) consistency: tier-1 YES ⟹ tier-2 YES on every
campaign case; (c) the bounded semantic oracle: enumerate all lasso
pairs `|u|,|v| ≤ 3` with equal destuttered normal forms; any such pair
with `member(p_min, u, v)` and `¬member(p_max, u', v')` must make
tier 2 answer NO, and tier-2's NO certificate must itself replay
(`member` both sides); (d) on corpus campaign cases where the language
is already stutter-invariant (`.cat` tag) and `¬φ = K = L`, tier 1
must answer YES immediately.

**GT3 acceptance:** tier-1 gates green (fixture regression included);
tier-2 green on fixture + campaign, zero (a)–(d) violations; the
tier-1-UNKNOWN-but-tier-2-YES frequency over the campaign recorded
(report slot F10 — this measures how often the hull escapes the table,
a paper §7 number).

---

## 6. GT4 — band-minimal Wagner degree (a theory probe)

Normative math: paper Prop 4.5 — **flagged there as a sketch**; this
milestone is deliberately built as its experimental verification.

- `min_band_degree(iv) -> Optional[Tuple[int, int]]`: None unless
  `exists_obligation(iv)`. Greedy: condense to `R`-classes; bottom-up
  over the condensation compute the pointwise-least monotone level
  function `ℓ*` — `ℓ*(r) = max over R-successors' ℓ*`, bumped by one
  if `r` is forced and the parity of the current value disagrees with
  the forced polarity; free classes take the max unmodified. Read the
  degree pair off `ℓ*` (per-polarity: run once with parity convention
  1-at-even, once 0-at-even — two passes; return the pair).
- **The brute probe (mandatory, the point of the milestone):** on
  every case with `bits ≤ 12` AND `exists_obligation`, enumerate all
  consistent `θ` (free classes both ways), compute
  `obligation_degree(choose-equivalent pair set)` (CAL5) for each, and
  take the true minimum. `min_band_degree` must equal it. **A
  disagreement is a publishable theory finding about Prop 4.5's
  simultaneity gap — record the minimal case verbatim in the report
  (slot F12) and do NOT tweak the greedy to match; the theory thread
  owns the resolution.**

**GT4 acceptance:** greedy == brute on every probed case, or the
disagreement dossier filed; degree distribution over the campaign
recorded.

---

## 7. GT5 — the W-series campaigns

House rules of calculus spec §8.1 apply verbatim (budgets, seeds,
checkpoints, output headers, CSV+md shape, `reference/` promotion).

- **W0 — census-shaped given-that** (`w0_census.py`): over the GT1
  campaign pairs (700, seeded), one row per pair: `n_¬φ`, `n_K`,
  `|nodes|`, ratio, `bits`, `k_settles`, `k_refutes`, per-rung
  existence bits, tier-1/tier-2 stutter verdicts, band-minimal degree,
  wall times per stage. Deliverable `reference/giventhat/w0_census.md`
  + `.csv`: the endpoint kill rate, the `bits` distribution, per-rung
  hit rates, the tier-gap frequency — paper §7 items 2–4 in
  census-shaped form. Every number the paper later cites in pure form
  comes from here; the report carries the reproducibility.
- **W1 — the MCC benchmark of [DPT25].** BLOCKED: needs the DPT25
  problem set (formulas + knowledge facts per model instance) landed
  in the repo by the user. Do not fetch external artifacts on your
  own initiative; when the data lands, a W1 protocol revision of this
  spec will accompany it. Until then W1 does not exist for you.

**GT5 acceptance (W0):** reference files committed with headers,
zero unexplained failure rows, the four summary tables present.

---

## 8. Expected failures — read before filing a bug

| # | check | expectation | on failure |
|---|---|---|---|
| A1 | Prop 3.1 runtime law (§3.1.5) | always green | upstream bug (align/materialize/saturate) — report the pair id, never work around |
| A2 | choice laws (§3.4) | always green | interval-core bug |
| E1 | fixture `\|𝒞(D_ab)\| == 6` | must hold | first suspect the HOA encoding; then canonize; only then the paper's §5.2 hand count — that escalation is a to-theory finding |
| E2 | fixture GT3 regression (tier1 UNKNOWN, tier2 YES) | must hold | if tier 2 says NO here, tier 2 is wrong (the paper proves YES semantically) — do not conclude the paper is wrong before the bounded oracle (§5.2.c) also fails |
| T1 | corpus rung oracle | green OR consistently flipped | flipped ⟹ implement swap + file finding F5; mixed ⟹ STOP, smallest case to the report |
| T2 | GT4 greedy vs brute | may disagree | that is the experiment working — dossier to slot F12, do not patch |
| F1 | Spot cross-checks | MAY disagree | dictionary/naming first; only a failed witness replay makes it a bug |
| F2 | Spot timeout | allowed | skip, record, never wait |

## 9. The trap list (each traces to a section)

1. **Alphabet strata** — `align` asserts equal alphabets; sample
   within strata (§3.6.5); never adapt inline.
2. **Endpoints live on the MATERIALIZED product** — `Aligned` is
   decision-only; `intersection/union/complement` need `materialize`
   (§3.1.2).
3. **Conjugacy closure must renormalize** — always through
   `saturate`/`linked_pair_of`; never insert raw `(sx, yx)` (calculus
   spec §3.3; §3.2 here).
4. **No universality scan** — `k_refutes_phi` is emptiness of a
   complement; implementing universality separately breaks the
   paper's symmetry claim (§3.3).
5. **Rung orientation** — the corpus decides, not the four hand
   examples; a flip is a reported theory correction (§4.1, T1).
6. **Brute oracles cap at `bits ≤ 12`** — skip and record above;
   never raise the cap to "get more coverage" (§4.3, §6).
7. **Per-case budget 15 s, checkpoint campaigns, `--one` mode** —
   calculus spec §8.1 verbatim (§3.6.5, §7).
8. **`[ε]` never merges in the stutter congruence** — assert, don't
   special-case (§5.1).
9. **Tier 2 has two normal-form cases** — infinitely-alternating and
   eventually-constant; forgetting the second is the bug the bounded
   oracle (§5.2.c) is designed to catch.
10. **Horn hull without saturate is not a language** — alternate to
    joint fixpoint; the saturation law convicts (§4).
11. **Tier-1 "no" does not exist** — the verdict type is YES/UNKNOWN
    (Thm 5.2); only tier 2 says NO (§5.1).
12. **Do not build `SC`'s automaton** for the tier-2 decision; the
    off-table witness is future work (§5.2).
13. **Reuse the shortlex BFS and the SCC pass** — one implementation
    each, shared with calculus; a second Tarjan is a review reject
    (§2, §5.1).
14. **`reduce(check=True)` is quadratic** — checked once per case
    outside timers, `check=False` inside (calculus spec trap #7).

## 10. Report contract

`research_notes/sos_giventhat_report.md` is the channel back to the
theory thread; its skeleton (with pre-named finding slots F1–F13) is
committed next to this spec. Rules: every milestone acceptance writes
its findings into the named slots; every to-theory item (E1
escalations, T1 flips, T2 dossiers, tier-gap statistics, anything
where this spec and the paper disagree) goes into the report's
**To theory** section the moment it is found — that section is read by
the thread that owns the paper; it is how you talk to us. Findings
state numbers with their `reference/`/logs path and regen command;
the paper cites numbers in pure form only after they appear in the
report (the calculus split, `sos_calculus_spec.md` §8.9, applies
verbatim).
