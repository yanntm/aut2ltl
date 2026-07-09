# SoS Calculus — Implementation Specification

**Status (2026-07-09).**

| item | state |
|---|---|
| CAL1–CAL3: the package `sosl/sosl/sos/calculus/` (§2–§3) | **DONE** — implemented, harness 1–8 green, gates in `sosl/tests/calculus/` |
| soundness harness (§4) | **DONE** — green corpus-wide |
| `is_stutter_invariant` in `table.py` (§3.1, §8.6) | **TODO** — five lines + gate, prerequisite of V2 |
| CAL4: the experimental campaign (§8; sub-milestones §8.10) | **TODO** — nothing run yet; §8 is the work order |
| hull surgeries + ladder read-offs (safety closure / interior / liveness part / `is_obligation`) | **OPTIONAL TODO** — theory delivered (paper §3.6, Prop 3.5 + Thm 3.10); milestone CAL5 in §6 |
| exponential frontier (`W·L`, `W^ω`, `remove_ap`), NBA exits, CLI, learner integration | **NON-GOALS** here (see §6) |

An implementer starting cold reads, in order: this header, §1–§2, the
section for the component at hand, §7 before filing any bug, and — for
the experiments — §8.1 and §8.8 before writing a line. Revision history
of this document lives in git and `docs/HISTORY.md`, not here.

**Normative math.** `research_notes/sos_calculus.md` (the calculus paper:
align / operate / reduce, the surgery catalog, the ledger) with [SωS26] for
the invariant, its membership oracle, and canonicity (Thm 5.1). This
document fixes package shape, algorithms, harness, and milestones — in
enough detail that the implementer never has to re-derive a design decision.

**One-line goal.** `sosl.sos.calculus` — the package at
`sosl/sosl/sos/calculus/` — implements the calculus's three moves and its
surgery catalog as pure functions over existing invariant objects, every
decision procedure returning a replayable canonical witness. The open
work order is the CAL4 experimental campaign (§8) plus its one-function
prerequisite (§8.6).

**Layering law (hard).** `sosl.sos.calculus` imports `sosl.sos` (objects,
`.sos` io, existing primitives) and NOTHING else in the repo — in
particular never `sosl.learn`, `sosl.teacher`, `sosl.experiment`, `tests.*`.
The learner will later become a *client* of the calculus (the
exact-by-reference oracle of the learner spec); the dependency arrow
points only that way. Where an operation must accept a
learner-side object, it does so through the `FoldedLanguage` protocol of
section 1 — a structural interface, no import.

---

## 1. Objects

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

**`FoldedLanguage` (a `typing.Protocol`).** The minimal
interface a decision procedure needs from one side of a comparison:

```
class FoldedLanguage(Protocol):
    alphabet : Alphabet                   # align needs Σ, and cannot
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

All files below exist and are harness-green; the one missing function is
`is_stutter_invariant` in `table.py` (TODO, §8.6).

```
sosl/sosl/sos/calculus/
    table.py     Table: one (𝒞, λ, M) + memoized idem/linked/keys + Val
                 factory (a Table carries MANY pair sets; pair sets are
                 values, tables are shared); is_stutter_invariant [TODO]
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

  **The `linked_pair_of` renormalization is mandatory — do not "optimize"
  it away.** It is tempting to insert `(t, f)` directly for `f = M(y,x)`,
  expecting `f` idempotent and `(t, f)` linked to follow from `M(x,y) = e`
  idempotent. They do **not**: only `(y·x)²` is guaranteed idempotent
  (`(yx)³ = y·(xy)²·x = (yx)²`). Counterexample in the corpus,
  `flat_canon/sos/3state1ap0acc_074764.sos` (20 classes): the linked pair
  `(7,7)` factors as `e = M(1,8)`, and `f = M(8,1) = 13` has
  `M(13,13) ≠ 13`; 69 such firings occur in that one table. What *is*
  true is the word identity `u·(xy)^ω = (ux)·(yx)^ω`, a law about
  **cells**, not about linked pairs:
  `Val_P(s, e) = Val_P(M(s,x), M(y,x))` whenever `M(x,y) = e`. So the
  conjugate cell must be normalized back to a linked pair through `Val`'s
  own lookup — that is `linked_pair_of` above — before it is inserted.
  (This cell-level law is Proposition 3.1 of the calculus paper.)
  Conjugacy is symmetric (swap `x` and `y`), so the closure is a union of
  conjugacy classes.

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
   All behind a `check: bool = True` parameter — the interior of the
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
8. **Witness minimality**: on the named cases — the *triptych* (the
   three running examples of [SωS26]: `GF(aa)`, `Even`, `EvenBlocks`)
   plus the two stall specimens, all fixed as fixtures in the existing
   gates under `sosl/tests/calculus/` — the returned witnesses equal the
   brute-force minimal disagreeing/satisfying lassos from bounded
   enumeration.

---

## 5. The V-series at a glance (protocol: §8)

The experiments are specified in full in §8; this is the index.

| id | what | spec | status |
|---|---|---|---|
| V0 | gate: harness 1–8 green (triptych, named cases, corpus sample) — blocking for everything else | §4 | **DONE** |
| V1a | alignment-ratio distribution (uniform / large / related populations) | §8.3 | TODO |
| V1b | operation costs, calculus vs Spot, counts + warm timings | §8.4 | TODO |
| V1c | pipeline demo: normal-form economy + entry price | §8.5 | TODO |
| V2 | stutter read-off vs Spot over the census (needs `is_stutter_invariant`, §8.6) | §8.6 | TODO |
| V3 | Prop 3.4 blow-up check, `W·L_n` for n = 2..5 | §8.7 | TODO |

Reproducibility floor (house rule): validated V-outputs are copied into
the curated committed `reference/calculus/` tree and cited by path from
the paper.

---

## 6. Milestones

- **CAL1 — one table. [DONE]** `table.py` + `surgery.py` + single-table
  `decide.py` (member / empty / universal) + witnesses. Accept: harness
  1–4, 8 green; residual-count read-off matches the stored residuals block
  where the `.sos` has one.
- **CAL2 — two tables. [DONE]** `align.py` + cross-table `decide.py`.
  Accept: harness 5, 7 green corpus-wide (sampled).
- **CAL3 — normal form. [DONE]** `reduce.py`. Accept: harness 5–6 green
  on the full corpus; `reduce` idempotent everywhere; byte-equivalence
  and scan-equivalence agree everywhere.
- **CAL4 — the ledger. [TODO — the open milestone.]** V1 + V2 + V3
  delivered to `reference/calculus/` per the full protocol of §8;
  sub-milestones CAL4a–d in §8.10. Prerequisite:
  `is_stutter_invariant` (§8.6).
- **CAL5 — hulls. [OPTIONAL TODO — theory delivered, paper §3.6.]**
  `surgery.py` additions, all `O(n²)`, normative math Prop 3.5 and
  Cor 3.6–3.7 of the paper:
  - `live(table, P) -> FrozenSet[int]` — the classes `c` whose row
    `{M(c, x) : x ∈ 𝒞} ∪ {c}` meets `stems(P) = {s : (s, e) ∈ P}`
    (build the stems bitmask once, one pass over `M`);
  - `safety_closure(table, P) = {(s, e) ∈ linked : s ∈ live(P)}`;
  - `interior(table, P) = {(s, e) ∈ linked : s ∉ live(complement(P))}`;
  - `liveness_part(table, P) = union(P, complement(safety_closure(P)))`;
  - read-offs `is_safety(P) := P == safety_closure(P)` and
    `is_cosafety(P) := P == interior(P)` (exact tests — fixpoint
    equations, not approximations);
  - `is_obligation(table, P) -> bool` (paper Thm 3.10): bucket linked
    pairs by stem and check each bucket's verdict constant; then check
    the stem verdict constant on each `R`-class (`R`-classes = the
    strongly connected components of the right-Cayley graph
    `c → M(c, λ(a))`, one Tarjan/Kosaraju pass, `O(n·|Σ|)`); true iff
    both hold. Cost `O(|linked| + n·|Σ|)`.
  Gates: hull is extensive / monotone / idempotent on random pair sets;
  outputs satisfy the saturation law (harness 2); duality
  `interior(P) == complement(safety_closure(complement(P)))`;
  decomposition identity
  `P == intersection(safety_closure(P), liveness_part(P))`; every class
  is `live` for `liveness_part(P)` (its closure is `linked`);
  metamorphic replay against the paired det HOA — prefix-liveness of a
  lasso's prefixes checked by bounded per-state emptiness on the
  automaton, over all lassos `|u|, |v| ≤ 3`. For `is_obligation`, the
  corpus is its own oracle: the `.cat` sidecars carry the Wagner
  coordinates, and `is_obligation` must return true exactly when
  `m⁺ = m⁻ = 0` — a corpus-wide equality gate, no Spot involved.

Non-goals for this iteration: the exponential frontier (`W·L`, `W^ω`,
`remove_ap` — §3.4 of the paper; do not implement, do not stub); exit
constructions to NBA; any CLI; any learner integration (that is a
*separate* commission, specified on the learner's side, once this
package stands).

## 7. Expected failures — read before filing a bug

| # | check | expectation | on failure |
|---|---|---|---|
| A1 | harness 1–5, 8 | always green | calculus-core bug |
| A2 | saturation law (harness 2) | always green | the operation emits a non-language pair set — fix the operation, never `saturate` the output silently |
| A3 | reduce idempotence / pullback (3.5.5) | always green | quotient bug; the failing cell localizes it |
| P1 | corpus equality oracle (harness 7) | green | if `equivalent` disagrees with filename identity, suspect the calculus first, the corpus dedup second — report, do not "fix" the corpus |
| F1 | Spot cross-checks (V1/V2) | MAY disagree | dictionary/naming first; only a failed witness replay makes it a bug |
| F2 | Spot timeout in V1/V2 | allowed | skip and record, never wait (repo discipline) |
| E1 | V3 bound `\|𝒞(W·L_n)\| ≥ 2^n − 1` | must hold | suspect the HOA encoding (§8.8 trap 9) first; only then escalate to theory (Prop 3.4) — never patch the numbers |
| E2 | V3 construction timeout at n ≥ 4 | allowed, publishable | it IS the entry price — record as a datum and stop (§8.8 trap 10) |

---

## 8. CAL4 — the experimental protocol, in full

This section is a self-contained design spec for the V-series: an
implementer should be able to build and run the whole campaign from this
text plus the package's public API, without re-deriving any decision.
Read §8.1 (ground rules) and §8.8 (the trap list) *before* writing any
code. The deliverable is not "numbers exist" but "the exact values of
§8.7 sit in `reference/calculus/`, each traceable to a seed, a git rev,
and a corpus rev".

### 8.1 Ground rules (repo discipline, distilled)

- **Per-case budget ≤ 15 s, hard.** A blown budget is a *finding* (record
  it, move on), never a retry loop. The cap is per example: every
  experiment script has a `--one <case>` mode taking a single input on
  argv, and a `--campaign` mode that iterates cases internally with a
  per-case watchdog and a checkpoint file (append one line per finished
  case; on restart, skip finished cases). Campaigns run as background
  tasks; nobody sits in front of them.
- **Spot is bounded-or-skipped.** Every Spot call sits under a hard
  budget (default 10 s). On timeout: skip, record an F2 row, continue.
  Never wait, never retry.
- **No `/tmp`.** Working logs under `sosl/tests/calculus/logs/`
  (gitignored ok); *validated* outputs are copied into the committed
  `reference/calculus/` tree and cited by path from the paper (the
  house reproducibility floor).
- **Placement and layering.** Scripts live in `sosl/tests/calculus/`
  (`v1_align.py`, `v1_ops.py`, `v1_pipeline.py`, `v2_stutter.py`,
  `v3_blowup.py`). The layering law of this spec binds the *package*
  `sosl.sos.calculus`, not the tests: experiment scripts MAY import
  `spot`, the sosl teacher's replay hooks, and anything else they need.
- **Determinism.** Every sampling uses a fixed, named seed written into
  the output header. Sort every glob and every dict iteration. Fixed
  float formats (`{:.4f}` for ratios, `{:.1f}` ms for times). Outputs
  must be byte-stable across reruns modulo the timing columns.
- **Output shape.** One CSV per experiment (raw rows) + one `.md`
  summary (the tables the paper will cite). Every file starts with a
  4-line header: date, git rev (`git rev-parse --short HEAD`), seed,
  corpus path.

### 8.2 Inputs: the corpus, exactly

- `genaut/corpus/flat_canon/sos/*.sos` — 3 938 canonical invariants,
  one file per language, complement-closed. `.cat` sidecars carry the
  classification read-offs (LTL-definability among them). Load through
  the existing `sosl.sos` io; wrap in `Table.of`.
- `genaut/corpus/flat_canon/det/*.hoa` — the paired deterministic
  Emerson–Lei automata, **same basename** as the `.sos`. This is the
  Spot-side input; never rebuild it.
- Size facts to rely on: `|𝒞|` min/median/max = 2/15/121; primal
  automaton states ≤ 9. Everything is small; if something is slow, the
  cause is the code, not the data.
- **Complement partners.** The corpus is complement-closed but the
  partner is *another file* with an unrelated name. Build the partner
  map once: dict from content-hash of the canonical serialization of
  `reduce(complement(P))` to filename — O(corpus) — and reuse it in
  V1a's "related pairs" stratum. Do not guess from filenames.
- **Alphabet strata.** Corpus languages live over different AP sets
  (1-AP and 2-AP shapes). `align` *asserts* equal alphabets. Partition
  the corpus by alphabet first; every pair sampled below is sampled
  **within one stratum**. (Trap #1 of §8.8.)

### 8.3 V1a — alignment ratio (fills the §3.3 TBD of the paper)

**Question.** How much smaller than the rectangle `n_A·n_B` is the
generated product in practice, and does relatedness of the operands
show up as predicted?

**Design.** Three pair populations, all seeded (`seed = 20260709`):

1. `uniform`: 5 000 unordered pairs `{A, B}`, `A ≠ B`, drawn uniformly
   within alphabet strata (proportionally to the stratum's pair count).
2. `large`: 200 pairs drawn among the top-decile `|𝒞|` languages —
   uniform sampling is dominated by small tables (median 15) and the
   paper's claim must be tested where products can actually grow.
3. `related`: for 1 000 sampled languages, the pair (L, complement
   partner of L). Same algebra on both sides, so the generated product
   should collapse to (near) the diagonal — this instantiates §3.3's
   "related operands" contrast with zero modeling effort.

**Per pair, record:** basenames, `n_A`, `n_B`, `|Σ|`, `|nodes|`,
`ratio = aligned.ratio` (use the field the implementation already
exposes; do not re-derive the convention for the adjoined identity),
BFS wall time (cold — alignment is the one move where cold time *is*
the datum).

**Summary tables (the paper cites these):** per population:
min / p25 / median / p75 / p95 / max of ratio; fraction of pairs with
ratio < 0.25, < 0.5, < 0.9, ≈ 1.0; median BFS time. One sentence
comparing `related` vs `uniform` medians.

### 8.4 V1b — operation costs, calculus vs Spot (fills the §4 ledger TBD)

**Framing decision (write it into the summary, verbatim if need be).**
The corpus automata are *deterministic*, so Spot's complement is
`spot.dualize` — cheap and correct on deterministic complete automata —
and nothing here exhibits the `2^{Θ(n log n)}` NBA complementation of
the ledger's theory row. V1b therefore measures the *held-object*
economy (what an operation costs when you already have the canonical
object vs when you have a deterministic automaton), NOT the
nondeterministic entry story. Do not oversell; the theory row stands on
[TFVT10], not on these timings. Similarly, do not compare `reduce`
against Spot's simplifications head-to-head — one is a normal form, the
other a heuristic — report them as separate columns, never as a ratio.

**Operations measured** (per case; sample: the first 1 000 `uniform`
pairs of V1a, plus each pair's two languages for the unary rows):

| row | calculus call | Spot counterpart (bindings) |
|---|---|---|
| complement | `complement` + `reduce(check=False)` | `spot.dualize(aut)` |
| intersection | align + pointwise ∧ + reduce(check=False) | `spot.product(a, b)` (+ its simplification, timed separately) |
| equivalence | byte compare of the two `.sos` files; also `equivalent(aligned)` | `a.equivalent_to(b)` (or `spot.contains` both ways) |
| inclusion | `included(aligned)` | `spot.contains(b, a)` |
| intersection-word | `intersecting_word(aligned)` | `a.intersecting_word(b)` |
| lasso membership | `member` on the canonical witness lassos harvested above | lasso → `spot.parse_word(...).as_automaton()` → `intersects` |

**Timing method.** `time.perf_counter`; 1 warmup call then median of 7.
Warm-vs-cold policy: the calculus's memoized `idem`/`linked`/keys are
*part of the held object* — warm timings are the honest ledger entry;
say so in the summary. Alignment time is excluded from the per-op rows
(it is V1a's row and the ledger prices it separately); report
"align-amortized" figures: (align + k ops) / k for k = 1, 5, 10.

**Implementation-independent counts.** Wall clocks compare a Python
package against C++; alongside every timing, record the abstract cost:
cells scanned, `|linked|`, `|nodes|`. The paper leans on counts; the
times are corroboration.

**Spot bindings vs CLI.** Use `import spot` (bindings). If bindings are
unavailable, fall back to `autfilt` CLI but report those timings in a
*separate* column marked "includes ~10 ms process startup" — never mix
the two in one column (trap #3). Bindings cannot be interrupted
in-process: rely on the checkpoint file so a stall loses one case
(restart skips it, mark F2), and keep the campaign in a background
task.

### 8.5 V1c — the pipeline demo (fills the §3.4 entry-price TBD)

**Honest scope (trap #14).** On this corpus everything is deterministic
and small, so the demo CANNOT exhibit "Spot pays Safra k times" — that
claim stays theoretical in the paper. What the demo *can* measure is
the normal-form economy: intermediate sizes, simplification churn, and
the cost of re-checks along a pipeline.

**Pipeline.** For 20 seeded pairs (A, B) (same alphabet, both `|𝒞|` in
the middle decile):

```
E1 = ¬A;  E2 = E1 ∩ B;  E3 = ¬E2;  E4 = E3 ∪ A;
after each stage: an emptiness check and an equivalence re-check of the
stage output against its freshly recomputed form (the "did my rewrite
change the language" query every pipeline actually runs).
```

Calculus side: surgeries + `reduce(check=False)` per stage; re-checks
are byte comparisons; witnesses come free. Spot side: `dualize` /
`product` / `product_or` per stage, then the library's standard
simplification (timed); re-checks are `equivalent_to`; witnesses need
`intersecting_word` runs. Also report the **entry price** honestly: the
one-time cost of constructing the two `.sos` inputs, re-measured by
running `genaut/gen/canonize.py` on the paired det HOA (head its pydoc
for flags; trust its defaults).

**Deliverable.** One table: stage | `|𝒞|` after reduce / calculus time |
Spot states after simplification / Spot time; a cumulative row; the
entry-price row on top. Plus three sentences of interpretation, written
against trap #14.

### 8.6 V2 — the stutter read-off vs Spot (fills the §4 V2 TBD)

**Package addition first (TODO — not yet in the package):**
`is_stutter_invariant(table) -> bool` in `table.py` —
`all(M(λ(a), λ(a)) == λ(a) for a in Σ)`, docstring citing Prop 3.3 of
the paper. Five lines; add a gate replaying it against brute-force
stutter checks on the triptych.

**Sweep.** All 3 938 corpus languages: our verdict (the scan) vs Spot's
verdict on the paired det HOA. Spot route: the [MD15] entry points —
`spot.is_stutter_invariant` accepts formula- and automaton-shaped
inputs; for a deterministic automaton pass its `spot.dualize` as the
negation if the signature asks for one; if the direct call resists, the
closure primitives (`spot.closure`, `spot.sl`) implement Theorem 1 of
[MD15] by hand. Consult the bindings' help before improvising.

**Agreement table:** agree-invariant / agree-sensitive / disagree, plus
the census datum the paper and [SωSN26] both want: the count and share
of stutter-invariant languages in `flat_canon`, split by the `.cat`
LTL bit (stutter-invariance × aperiodicity is a free bonus
correlation).

**Disagreements (F1 discipline — dictionary first, bug only on failed
replay).** When WE say *sensitive* and Spot says invariant: produce a
witness pair and replay. The witness is guaranteed by the syntactic
congruence: pick a letter `a` with `λ(a)² ≠ λ(a)`; then some Arnold
context separates `a` from `aa` — search, in the discipline order:

- linear shape: for cells `(x, y, t)` over `𝒞 × 𝒞 × (𝒞 \ [ε])`,
  compare `Val(x·λ(a)·y, t)` against `Val(x·λ(aa)·y, t)`; on the first
  difference emit `key(x)·a·key(y)·key(t)^ω` vs
  `key(x)·a·a·key(y)·key(t)^ω`;
- ω shape: for `(x, y)`, compare `Val(x, λ(a)·y)` against
  `Val(x, λ(aa)·y)`; emit `key(x)·(a·key(y))^ω` vs
  `key(x)·(a·a·key(y))^ω`.

One of the two shapes must fire (that is what `λ(a) ≠ λ(aa)` *means*).
The two words are stutter-equivalent by construction; replay both
against the det HOA (the teacher's replay hook, or the V1b lasso
route). Two different verdicts on replay ⟹ Spot's verdict (or the
dictionary mapping) is wrong — report, do not fix. When WE say
*invariant* and Spot says sensitive: suspect us first; enumerate all
lassos `|u|, |v| ≤ 3`, compare `member` on each against `member` on its
destuttered form; the first divergence convicts the scan (a calculus
bug), no divergence + Spot still disagreeing ⟹ F1 report with the
enumeration attached.

### 8.7 V3 — Prop 3.4, empirically (fills the blow-up check deferred by the paper)

**Goal.** Confirm `|𝒞(W·L_n)| ≥ 2^n − 1` on real constructions for
`n = 2, 3, 4, 5`, and exhibit the operand sizes next to it.

**Build the DELA for `W·L_n` directly** (do not implement concatenation
— write the known result of it):

- State: a set `S ⊆ {0, …, n−1}` of live phases ("a-count since each
  open `#`, mod n"), plus one accepting sink `ACC`. Initial state: `∅`.
- Transitions from `S`: on `a`: `S ↦ {(s+1) mod n : s ∈ S}`; on `#`:
  `S ↦ S ∪ {0}`; on `b`: if `0 ∈ S` then `ACC` else `∅`.
  `ACC` loops to itself on every letter, its self-loops carrying the
  single acceptance mark; condition `Inf(0)` (Büchi). Deterministic,
  complete, ≤ `2^n + 1` states.
- Correctness argument to keep in the script's docstring: a run reaches
  `ACC` iff some `#`-thread has a-count ≡ 0 (mod n) at the first `b`
  after it — which is membership in `W·L_n`.
- **The alphabet encoding trap (#9).** The proposition's `Σ = {a,b,#}`
  is abstract; HOA needs `2^AP`, and 2 APs give **four** valuations.
  Do NOT silently alias the fourth valuation to `b` or `#` — that
  changes the language. Convention: `a := (!p&!q) | (p&q)` (the
  increment *class* has two letters), `b := p&!q`, `# := !p&q`. The
  blow-up proof survives verbatim with a two-letter increment class;
  say so in the summary.
- Also build the operand `L_n` DELA (phase counter `c ∈ Z_n`; on `a`:
  `c+1`; on `#`: `c`; on `b`: `ACC` if `c = 0` else `REJ`; two sinks;
  `Inf(0)` on `ACC` loops) to measure `|𝒞(L_n)|` — expected ≈ `2n + 1`;
  `W`'s three-element monoid needs no run.

**Run** `genaut/gen/canonize.py` on each HOA (per-case budget applies).
**Anticipate (trap #10): the construction itself may blow the 15 s cap
at n = 4 or 5 — the enriched monoid IS the entry price this very
section of the paper talks about.** A timeout there is a *publishable
datum* (the entry price exhibited on 17–33 states), not a failure:
record it as such and stop at the last n that finishes.

**Deliverable table:** n | `|𝒞(L_n)|` | `|𝒞(W·L_n)|` | bound `2^n − 1` |
construction time (or TIMEOUT). Values must satisfy the bound; a
violation convicts either the automaton (first suspect: the encoding
trap) or Prop 3.4 (escalate to theory, do not patch).

### 8.8 The trap list (read before coding; each traces to a section)

1. **Alphabet mismatch** crashes `align` by design — stratify pairs by
   alphabet (§8.2). Never "adapt" alphabets inline;
   `inverse_substitution` is the adapter and it is out of scope here.
2. **Spot bindings cannot be timed out in-process** — checkpoint per
   case; a stall loses one case, the restart skips it (F2).
3. **CLI vs bindings timings differ by process startup** — separate
   columns, never one.
4. **Python vs C++** — always record abstract counts (cells, linked,
   nodes) next to wall clocks; the paper argues with counts.
5. **Warm vs cold** — memoized tables are part of the held object; warm
   is the ledger figure; align is reported cold. State the policy in
   every summary header.
6. **Complement partners are content-mapped**, not name-mapped (§8.2).
7. **`reduce(check=True)` is quadratic** in its assertions — inside any
   timed region call `reduce(..., check=False)`; run one checked pass
   per case *outside* the timers (soundness stays covered).
8. **Negation on the Spot side is `dualize`** (inputs are deterministic
   and complete) — never invoke NBA complementation and then quote its
   cost as if it were forced.
9. **The fourth valuation** in V3's 2-AP encoding must be assigned a
   *role in the language* (a second increment letter), not aliased away
   (§8.7).
10. **V3's construction may time out at n ≥ 4** — that is the entry
    price, a datum; record and stop, do not raise budgets to force it.
11. **Lasso replay against HOA** needs the `.sos`-letter → BDD mapping
    — reuse the teacher's existing replay hook; do not re-parse letter
    strings by hand.
12. **Do not race `reduce` against Spot's simplifications** — different
    contracts (normal form vs heuristic); separate columns (§8.4).
13. **Byte-stability**: sort globs, sort iteration, fix float formats;
    reruns must diff only in timing columns.
14. **The pipeline demo cannot show Safra costs on this corpus** —
    frame it as the normal-form / free-recheck economy; the exponential
    story stays theoretical (§8.5).

### 8.9 Deliverables — the exact values the paper is waiting for

Each item names the paper TBD it fills and the reference file that
carries it (all under `reference/calculus/`, each with the §8.1
header):

1. **`v1_align_ratio.md`** → paper §3.3 TBD: ratio percentiles per
   population, the `related` vs `uniform` contrast, median BFS time.
2. **`v1_ops.md`** → paper §4 implementation TBD (ledger rows): per
   operation, median calculus time + abstract counts vs median Spot
   time; the align-amortized figures; F2 skip counts.
3. **`v1_pipeline.md`** → paper §3.4 entry-price TBD: the stage table
   with the entry-price row, cumulative totals, three framed sentences.
4. **`v2_stutter.md`** → paper §4 V2 TBD + a census datum for
   [SωSN26]: agreement table, stutter-invariant count and share, split
   by the LTL bit, disagreement dossier (target: zero unexplained).
5. **`v3_blowup.md`** → paper §3.4 Prop 3.4 deferred check: the n-table
   with the bound column; if a TIMEOUT row exists, one sentence
   presenting it as the entry price made visible.
6. **Headline sentence inputs** → paper abstract + contribution 4: the
   summary numbers of items 1–4 in one paragraph at the top of
   `v1_ops.md` (corpus size 3 938, median ratio, the one
   representative op-time pair, stutter agreement rate).

After the reference files land, patch the paper's five TBD slots citing
the files by path; the abstract's TBD sentence becomes the headline
paragraph. The hull conjecture (§3.5 of the paper) is NOT part of CAL4;
it stays a theory item.

### 8.10 Milestone restated

- **CAL4a** — V1a + V1b delivered (items 1–2, 6 of §8.9).
- **CAL4b** — V1c delivered (item 3).
- **CAL4c** — V2 delivered, zero unexplained disagreements (item 4).
- **CAL4d** — V3 delivered (item 5); paper TBDs patched.

Acceptance for the whole of CAL4: the five reference files committed,
the paper carrying their numbers, and every F1/F2 row in the files
explained by a dossier line.
