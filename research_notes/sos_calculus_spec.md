# SoS Calculus — Implementation Specification

**Status:** rev. 2, 2026-07-09 — CAL1–CAL3 implemented as
`sosl/sosl/sos/calculus/`, harness 1–8 green; gates in `sosl/tests/calculus/`.
Rev-2 edits are marked inline and all correct rev-1 errors found in
implementation (the saturation rule of §3.3 chief among them). CAL4 (the V1/V2
ledger) remains open. **Theory-ratified 2026-07-09:** the §3.3 correction is
confirmed — `x·y` idempotent does not make `y·x` idempotent, only `(y·x)²`
is (`(yx)³ = y·(xy)²·x = (yx)²`) — and the cell-level law with
`linked_pair_of` renormalization is adopted into the calculus paper as
Proposition 3.1 (with witness minimality as Proposition 3.2; the stutter
scan renumbered to 3.3, V2 below updated). The `FoldedLanguage` alphabet
field and the scoped `check` flag on reduce are accepted as specced.

**Normative math.** `research_notes/sos_calculus.md` (the calculus paper:
align / operate / reduce, the surgery catalog, the ledger) with [SωS26] for
the invariant, its membership oracle, and canonicity (Thm 5.1). This
document fixes package shape, algorithms, harness, and milestones — in
enough detail that the implementer never has to re-derive a design decision.

**One-line goal.** Build `sosl.sos.calculus` — the package at
`sosl/sosl/sos/calculus/` — implementing the calculus's three moves and its
surgery catalog as pure functions over existing invariant objects, every
decision procedure returning a replayable canonical witness.

**Layering law (hard).** `sosl.sos.calculus` imports `sosl.sos` (objects,
`.sos` io, existing primitives) and NOTHING else in the repo — in
particular never `sosl.learn`, `sosl.teacher`, `sosl.experiment`, `tests.*`.
The learner will later become a *client* of the calculus (the
exact-by-reference oracle, `sos_learner_spec.md` §3.2 rev 2026-07-08h);
the dependency arrow points only that way. Where an operation must accept a
learner-side object, it does so through the `FoldedLanguage` protocol of
section 1 — a structural interface, no import.

---

## 1. Objects (all assumed existing except the protocol)

**Invariant.** `𝓘 = (𝒞, λ, M, P)` as read/written by
`sosl/sosl/sos/io/sos_format.md`: class set `𝒞` with the adjoined identity
`[ε]` and a shortlex key per class (`key(c)` = the shortlex-least word
folding to `c`; `key([ε]) = ε`); letter map `λ : Σ → 𝒞`; multiplication
table `M : 𝒞 × 𝒞 → 𝒞`; accepting pair set `P` over the linked pairs. All
identity conventions of the format are in force: `[ε]` is a fresh permanent
singleton, never merged, never a loop class; a non-empty class acting
neutrally is an ordinary class.

**Derived notions (compute once per table, memoize):**

- `fold(w)` for `w ∈ Σ*`: left-to-right fold of `λ(w_i)` through `M` from
  `[ε]`. `fold(ε) = [ε]`.
- `idem(d)` for `d ≠ [ε]`: the unique idempotent in the cyclic subsemigroup
  `{d, d², d³, …}` — walk powers via `M` until the first repeat, locate the
  cycle, take the idempotent on it (it exists and is unique; uniqueness is
  why component-wise and pair-wise evaluations in section 3.2 agree). Cost
  `O(|𝒞|)` per class, memoized.
- **linked pairs**: `{(s, e) : e ∈ E, e ≠ [ε], M(s, e) = s}` with
  `E = { e : M(e, e) = e }`. One `O(|𝒞|·|E|)` scan, cached.
- **`Val`, the membership oracle** — the central function of the whole
  package:

  ```
  Val_P(c, d) := (M(c, idem(d)), idem(d)) ∈ P        c ∈ 𝒞, d ∈ 𝒞 \ {[ε]}
  ```

  `(M(c, e), e)` is automatically linked, so `Val` is total on its domain.
  The factoring theorem it implements: `u·v^ω ∈ L ⟺ Val_P(fold(u), fold(v))`
  for every lasso — every decision below is a scan of `Val` over **cells**
  `(c, d) ∈ 𝒞 × (𝒞 \ {[ε]})` (`c = [ε]` encodes the empty stem), never over
  words.

**Cell order and canonical lassos (normative, shared by every witness).**
The canonical lasso of cell `(c, d)` is `key(c)·key(d)^ω`. Cells are ordered
by their canonical lassos under the **teacher's minimization discipline**:
shortest stem, then shortest loop, then stem lex, then loop lex. Every
"first/least cell" below means least in this order.

**Proposition W (witness minimality — implement the scan in this order and
you get global minimality for free).** If some lasso `(u, v)` satisfies a
`Val`-definable predicate (a disagreement, a nonemptiness…), then the least
satisfying *cell*'s canonical lasso is ≤ `(u, v)` in the discipline order.
*Why:* `(u, v)` satisfies iff its cell `(fold(u), fold(v))` satisfies (the
factoring theorem); `key(fold(u))` is shortlex-≤ `u` and `key(fold(v))`
shortlex-≤ `v`, so the cell's canonical lasso dominates componentwise; the
least satisfying cell is ≤ that. Hence the returned witness is minimal over
*all* lassos, not just key-built ones. This is the property the learner's
E5 minimal-order guarantee will inherit; it is a requirement, not a remark.

**`FoldedLanguage` (protocol, new — `typing.Protocol`).** The minimal
interface a decision procedure needs from one side of a comparison:

```
class FoldedLanguage(Protocol):
    alphabet : Alphabet                   # rev 2: align needs Σ, and cannot
                                          # recover it from the class set
    classes  : Sequence[ClassId]          # identity first
    identity : ClassId
    def step(self, c: ClassId, a: Letter) -> ClassId: ...
    def verdict(self, stem: ClassId, loop: ClassId) -> bool: ...
```

An `Invariant` implements it with `step(c, a) = M(c, λ(a))` and
`verdict = Val_P`. A learner Cayley hypothesis implements it with its
`step` table and its P-cache read-off — *its own* discipline, no linked-pair
law assumed (a mid-run form need not be associative). Alignment and the
decision scans use only this protocol; the surgery catalog and `reduce`
require a genuine `Invariant`.

---

## 2. Package shape

```
sosl/sosl/sos/calculus/
    table.py     Table: one (𝒞, λ, M) + memoized idem/linked/keys + Val
                 factory (a Table carries MANY pair sets; pair sets are
                 values, tables are shared)
    align.py     align(A, B) -> Aligned: the generated product, lazy mult
    surgery.py   the free fragment: Boolean ops, complement, rooting,
                 pair languages + saturate(), inverse substitution
    decide.py    emptiness / universality / inclusion / equivalence /
                 intersection-word / membership — all witness-carrying
    reduce.py    reduce(Table, P) -> Invariant: the canonical re-quotient
    witness.py   Witness: lasso + expected bit + provenance + replay
```

No CLI in this iteration; the package is a library. (A `sos_calc` front-end
can come with a later revision if the experiments want one.)

---

## 3. Components — the algorithms

### 3.1 `table.py`

Wraps one `(𝒞, λ, M)`; owns `fold`, `idem`, linked pairs, keys, and
`val(P)(c, d)` closures. Two hard requirements:

- **Pair sets are plain immutable sets of linked-pair ids** over their
  table; every surgery returns a new set; nothing mutates a table.
- **Key discipline**: if keys are not already stored, they are rebuilt by a
  BFS over letter-extension in shortlex order (process the queue by length
  then lex; extend by letters in the fixed `Σ` order; the first discovery
  of a class fixes its key). The same BFS routine is reused verbatim by
  `align` and `reduce` — one implementation, three call sites.

### 3.2 `align.py` — the generated product (the only product-priced move)

```
align(A: FoldedLanguage, B: FoldedLanguage) -> Aligned
```

Precondition: same alphabet (same AP set and order) — assert, do not adapt;
`inverse_substitution` (3.3) is the adapter.

BFS over pair nodes `(c_A, c_B)`, seeded with the identity pair
`(id_A, id_B)` (key `ε`), extending by `step` on both sides simultaneously,
in shortlex order (3.1's routine): the reachable node set is exactly
`{(fold_A(w), fold_B(w)) : w ∈ Σ*}` — the letter-generated subsemigroup
plus identity — of size `≤ n_A·n_B`, usually far less. Each node stores its
shortlex key (first discovery); each edge is two `step` calls.

- **No product multiplication table is ever materialized.** `Aligned`
  exposes `step` (componentwise), the node set with keys, and the two
  verdict maps `Val_A(node_c, node_d) := A.verdict(c_A, d_A)`,
  `Val_B(…) := B.verdict(c_B, d_B)` — component evaluation, each side under
  its own discipline. (When a side is an `Invariant`, evaluating on the
  component with `idem(d_A)` is equivalent to projecting a pair idempotent
  power — the cyclic idempotent is unique — so componentwise is safe. The
  hypothesis side has no such notion and must only ever be asked through
  its `verdict`.)
- Cost: `O(n_A·n_B·|Σ|)` `step` calls, `O(n_A·n_B)` memory. Record the
  realized `|nodes| / (n_A·n_B)` ratio — V1 measures it.
- When both sides are `Invariant`s over one table (`A.table is B.table`),
  `align` returns the trivial diagonal without BFS.

### 3.3 `surgery.py` — the free fragment

All functions take (table, pair set(s)) and return pair sets on the same
table, `O(|linked|)` unless stated. Each carries its one-line correctness
fact as its docstring; the harness (section 4) replays them.

- `complement(P) = linked \ P`. Correct because
  `Val_{Pᶜ} = ¬Val_P` pointwise (the flip commutes with the
  `(M(c,e), e)` lookup).
- `union / intersection / difference / xor`: set operations;
  `Val` commutes with all of them pointwise (same lookup, Boolean on
  membership). Constants: `empty = ∅`, `universal = linked`.
- `rooting(P, c) = {(s, e) ∈ linked : (M(c, s), e) ∈ P}` for `c ∈ 𝒞`.
  Well-defined (`(M(c,s), e)` is linked when `(s, e)` is) and
  `Val_{P_c}(x, d) = Val_P(M(c, x), d)`, so `L(P_c) = key(c)⁻¹·L`.
  Assert the action law `P_{M(c,d)} = (P_c)_d` in the harness. The
  **residual count read-off**: number of distinct sets among
  `{P_c : c ∈ 𝒞¹}` (dedup by frozenset) — expose it, it is a datum.
- `pair_language(pairs)` — any *saturated* subset of linked pairs as a
  language. Saturation (two linked pairs denote the same ω-word class iff
  conjugate) is closed operationally by

  ```
  saturate(Q): least fixpoint of
      (s, e) ∈ Q, x, y ∈ 𝒞, M(x,y) = e
      ⟹ linked_pair_of(M(s,x), M(y,x)) ∈ Q
  where linked_pair_of(t, f) = (M(t, idem(f)), idem(f))
  ```

  **Rev 2 correction.** The rule was first stated as `(t, f) ∈ Q` for
  `f = M(y,x)`, with the parenthetical "*f idempotent and (t,f) linked
  follow*". That parenthetical is **false**: `M(x,y) = e` idempotent does not
  make `M(y,x)` idempotent. Counterexample, `flat_canon/sos/
  3state1ap0acc_074764.sos` (20 classes): the linked pair `(7,7)` factors as
  `e = M(1,8)`, and `f = M(8,1) = 13` has `M(13,13) ≠ 13`; 69 such firings
  occur in that one table. What *is* true is the word identity
  `u·(xy)^ω = (ux)·(yx)^ω`, a law about **cells**, not about linked pairs:
  `Val_P(s, e) = Val_P(M(s,x), M(y,x))` whenever `M(x,y) = e`. So the
  conjugate cell must be normalized back to a linked pair through `Val`'s own
  lookup — that is `linked_pair_of` above — before it is inserted. Conjugacy
  is symmetric (swap `x` and `y`), so the closure is a union of conjugacy
  classes.

  `O(|linked|·n²)` worst case, run rarely. Two uses: (i) legality check —
  `pair_language` asserts `saturate(pairs) = pairs`; (ii) **internal law**
  — every pair set produced by this catalog satisfies
  `saturate(P') = P'`; the harness asserts it on every operation output
  (cheap at census sizes, and a violation convicts the operation).
- `inverse_substitution(inv, π: Σ' → Σ)`: same table, letter map `λ ∘ π`;
  reachable part may shrink — the result is handed to `reduce` before any
  byte-level use. Covers relabeling, letter merging, alphabet extension by
  duplication.

### 3.4 `decide.py` — decisions as scans, witnesses always

All procedures scan cells in the normative order of section 1 and return
`(bool, Optional[Witness])`; by Proposition W the witness is the globally
minimal one. Single-table forms take `(table, P)`; cross-table forms take
an `Aligned`.

- `member(P, u, v)`: `Val_P(fold(u), fold(v))` — `O(|u| + |v|)` lookups.
- `is_empty(P)`: `P = ∅`; else the least cell with `Val_P` true furnishes
  the witness. (Scan cells, not `P`: the least *pair* in `P` is not in
  general the least *cell* — e.g. a short non-idempotent loop key maps
  into a long-keyed linked pair.)
- `is_universal(P)`: `is_empty(complement(P))`.
- `included(A ≤ B)` on an `Aligned`: scan cells `(c, d)` of the aligned
  node set (`c` any node, `d` any non-identity node); first cell with
  `Val_A ∧ ¬Val_B` yields the separating lasso. Cost: `O(|nodes|²)`
  verdict evaluations, each `O(1)` amortized.
- `equivalent(A, B)` on an `Aligned`: one scan of `Val_A ≠ Val_B` — both
  inclusion defects in one pass, least disagreeing cell as counterexample.
  On two *reduced* invariants, byte equality of the `.sos` dumps is the
  `O(1)`-scan alternative ([SωS26 Thm 5.1]) — expose both;
  `equivalent` must agree with byte equality wherever both apply (harness).
- `intersecting_word(A, B)` on an `Aligned`: least cell with
  `Val_A ∧ Val_B` — the model-checking-shaped query, witness included.

### 3.5 `reduce.py` — the normal form

```
reduce(table, P) -> Invariant     # the syntactic invariant of L(P)
```

The re-quotient of the calculus paper §3.1 move 3. The congruence to
compute: `c ≈ c'` iff `c` and `c'` are interchangeable in both context
shapes over the table. Algorithm — partition refinement, letters only:

1. **Base partition** by the `O(n)`-bit signature
   `sig(c) = ( Val_P(c, d) : d ∈ 𝒞 \ [ε] ) ++ ( Val_P(x, c) : x ∈ 𝒞 )`
   (the class as a stem against every loop; the class as a loop against
   every stem; `c = [ε]` has no loop part — see step 4).
2. **Refine to a two-sided congruence**: split blocks until for every
   letter `a`, `c ≈ c'` implies `M(c, λ(a)) ≈ M(c', λ(a))` and
   `M(λ(a), c) ≈ M(λ(a), c')`. Moore-style iteration: recompute per-class
   letter-successor block vectors, re-partition, repeat to fixpoint —
   `≤ n` rounds of `O(n·|Σ|)`. (Letters suffice: contexts are letter
   products, so single-letter two-sided stability plus the base signature
   yields full-context interchangeability — the standard induction; do
   not enumerate context triples.)
3. **Quotient**: classes = blocks; `M`, `λ` induced (well-defined by
   step 2); `P` = image pairs. Re-key by the shortlex BFS of 3.1.
4. **Identity convention**: `[ε]` is excluded from the refinement and
   re-adjoined as the fresh singleton — never merged, even if some block
   acts neutrally (the `.sos` canonicity requirement).
5. **Assertions before returning** (each a violation ⇒ raise, never
   emit): the quotient's `Val` pulls back to the input's `Val` on every
   cell (`O(n²)`); `reduce` of the result is byte-identical to the result
   (idempotence); the result parses back through the `.sos` io round-trip.
   Rev 2: behind a `check: bool = True` parameter — the interior of the
   idempotence check, and scans over large aligned products where the
   quadratic pullback would dominate, pass `check=False`.

Cost target: `O(n²·|Σ| + n²)` after the base signatures (`O(n²)` `Val`
calls) — negligible at census sizes (`n ≤ 121`, aligned products a few
thousand).

### 3.6 `witness.py`

`Witness = (stem: str, loop: str, expected: bool, provenance)` —
provenance names the operation and the cell (class keys) that produced it.
Deterministic rendering (the byte-stable fixture format). `replay(oracle)`
takes any membership callable `(u, v) -> bool` — another invariant's
`member`, the sosl teacher, a bounded Spot check — and asserts the bit.
No Spot dependency inside the package; replay hooks are injected.

---

## 4. Soundness harness (all automated, green before any experiment)

1. **Boolean laws** (per table, random pair sets): double complement,
   De Morgan, `xor = (∪) \ (∩)`, `∅`/`linked` identities — pure set
   algebra, plus pointwise `Val` agreement on all cells.
2. **Saturation law**: `saturate(P') = P'` for the output of every catalog
   operation, on every harness case.
3. **Metamorphic replay** (the deep check): for each operation and each
   lasso with `|u|, |v| ≤ 3` (exhaustive, the acceptor-check budget):
   `member(result, u, v)` equals the Boolean combination of
   `member(input_i, u, v)` — complement flips, union ors, rooting
   prepends `key(c)`, inverse substitution maps letters.
4. **Rooting laws**: `P_{M(c,d)} = (P_c)_d` on all `(c, d)`; `P_{[ε]} = P`.
5. **Alignment laws**: `align(I, I)` reduces byte-equal to `I`;
   `equivalent` on an aligned pair agrees with byte equality of the two
   reduced sides.
6. **Duality gate**: `reduce(complement(P))` byte-equals the stored
   complement — the corpus (`genaut/corpus/flat_canon/`) is
   complement-closed, so this runs on *every* corpus case for free.
7. **The corpus as equality oracle**: `flat_canon` holds one file per
   language — language equality *is* filename equality. Sample pairs
   (both same-file and cross-file): `equivalent` must return true exactly
   on same-file pairs, and every counterexample on a cross-file pair must
   replay correctly against both `.sos` sides (and against the det HOA,
   bounded, where present).
8. **Witness minimality**: on the named cases (triptych + the two stall
   specimens), the returned witnesses equal the brute-force minimal
   disagreeing/satisfying lassos from bounded enumeration.

---

## 5. Experiments (lean — this package is infrastructure)

- **V0 — gate.** Harness 1–8 green over the triptych, the named cases, and
  a fixed 100-language corpus sample. Blocking for everything else.
- **V1 — the ledger, measured.** Over corpus pairs: distribution of the
  alignment ratio `|nodes| / (n_A·n_B)`; wall time of complement /
  equivalence / inclusion / intersection-word on invariants vs Spot doing
  the same on the paired det automata (bounded-or-skipped, per repo
  discipline). Deliverable: the measured rows of the calculus paper's §4
  ledger and the "pay canonicity once" pipeline demo (k complements +
  conjunctions, Spot's cumulative cost vs one entry + free surgery).
- **V2 — read-off validation.** Stutter-invariance by the paper's
  Prop 3.3 (`λ(a)·λ(a) = λ(a)` scan; renumbered from 3.1 — §3.2's
  conjugacy and witness-minimality propositions now precede it) vs
  Spot's check over the census; disagreements are dictionary items
  first, bugs only on a failed replay.

Per the reproducibility floor (`sos_learner_spec.md` §8 item 9): validated
V-outputs are copied into the curated committed `reference/` tree and cited
by path in the report.

---

## 6. Milestones

- **CAL1 — one table.** `table.py` + `surgery.py` + single-table
  `decide.py` (member / empty / universal) + witnesses. Accept: harness
  1–4, 8 green; residual-count read-off matches the stored residuals block
  where the `.sos` has one.
- **CAL2 — two tables.** `align.py` + cross-table `decide.py`. Accept:
  harness 5, 7 green corpus-wide (sampled); V1 alignment-ratio data
  collected.
- **CAL3 — normal form.** `reduce.py`. Accept: harness 5–6 green on the
  full corpus; `reduce` idempotent everywhere; byte-equivalence and
  scan-equivalence agree everywhere.
- **CAL4 — the ledger.** V1 + V2 delivered to `reference/`.

Non-goals for this iteration: the exponential frontier (`W·L`, `W^ω`,
`remove_ap` — §3.4 of the paper; do not implement, do not stub); exit
constructions to NBA; hulls (§3.5 "conjecturally" — theory owes the pair
sets first); any CLI; any learner integration (that is a *separate*
commission against `sos_learner_spec.md` §3.2 once this package stands).

## 7. Expected failures — read before filing a bug

| # | check | expectation | on failure |
|---|---|---|---|
| A1 | harness 1–5, 8 | always green | calculus-core bug |
| A2 | saturation law (harness 2) | always green | the operation emits a non-language pair set — fix the operation, never `saturate` the output silently |
| A3 | reduce idempotence / pullback (3.5.5) | always green | quotient bug; the failing cell localizes it |
| P1 | corpus equality oracle (harness 7) | green | if `equivalent` disagrees with filename identity, suspect the calculus first, the corpus dedup second — report, do not "fix" the corpus |
| F1 | Spot cross-checks (V1/V2) | MAY disagree | dictionary/naming first; only a failed witness replay makes it a bug |
| F2 | Spot timeout in V1/V2 | allowed | skip and record, never wait (repo discipline) |
