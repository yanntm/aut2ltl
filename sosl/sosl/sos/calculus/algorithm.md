# calculus — align, operate, reduce

Dev-facing notes: the hard ideas one level above the code. The specification of
record is `research_notes/sos_calculus_spec.md`; its normative math is the
calculus paper `research_notes/sos_calculus.md`, with [SωS26] for the invariant,
its membership oracle, and canonicity (Thm 5.1). Read this to *change* the
module; read `README.md` to *use* it.

The whole package rests on one sentence: **every question is a scan of `Val`
over cells, never over words.**

---

## 1. Objects

**Invariant.** `𝓘 = (𝒞, λ, M, P)` as read/written by `sosl/sos/io/sos_format.md`:
class set `𝒞` with the adjoined identity `[ε]` and a shortlex key per class
(`key(c)` = the shortlex-least word folding to `c`; `key([ε]) = ε`); letter map
`λ : Σ → 𝒞`; multiplication table `M : 𝒞 × 𝒞 → 𝒞`; accepting pair set `P` over
the linked pairs. All identity conventions of the format are in force: `[ε]` is
a fresh permanent singleton, never merged, never a loop class; a non-empty class
acting neutrally is an ordinary class.

**Derived notions** (computed once per table, memoized on `Table`):

- `fold(w)` for `w ∈ Σ*`: left-to-right fold of `λ(w_i)` through `M` from `[ε]`.
  `fold(ε) = [ε]`.
- `idem(d)` for `d ≠ [ε]`: the unique idempotent in the cyclic subsemigroup
  `{d, d², d³, …}`. It exists and is unique; uniqueness is why component-wise
  and pair-wise evaluations in the aligned product agree.
- **linked pairs**: `{(s, e) : M(e,e) = e, e ≠ [ε], M(s, e) = s}`.
- **`Val`, the membership oracle** — the central function of the whole package:

      Val_P(c, d) := (M(c, idem(d)), idem(d)) ∈ P        c ∈ 𝒞, d ∈ 𝒞 \ {[ε]}

  `(M(c, e), e)` is automatically linked, so `Val` is total on its domain. The
  factoring theorem it implements: `u·v^ω ∈ L ⟺ Val_P(fold(u), fold(v))` for
  every lasso — so every decision is a scan over **cells** `(c, d) ∈ 𝒞 × (𝒞 \
  {[ε]})` (`c = [ε]` encodes the empty stem).

**Cell order and canonical lassos (normative, shared by every witness).** The
canonical lasso of cell `(c, d)` is `key(c)·key(d)^ω`. Cells are ordered by
their canonical lassos under the **teacher's minimization discipline**: shortest
stem, then shortest loop, then stem lex, then loop lex — the same order
`sosl/teacher/equiv.py` enumerates counterexamples in. Every "first / least
cell" below means least in this order. It is realized by `cells_in_order`, which
is lazy: a scan that stops at the first hit pays only for the prefix it consumed.

**Proposition W (witness minimality).** *Implement the scan in this order and
global minimality comes for free.* If some lasso `(u, v)` satisfies a
`Val`-definable predicate (a disagreement, a nonemptiness…), then the least
satisfying *cell*'s canonical lasso is ≤ `(u, v)` in the discipline order.
*Why:* `(u, v)` satisfies iff its cell `(fold(u), fold(v))` satisfies (the
factoring theorem); `key(fold(u))` is shortlex-≤ `u` and `key(fold(v))`
shortlex-≤ `v`, so the cell's canonical lasso dominates componentwise; the least
satisfying cell is ≤ that. Hence the returned witness is minimal over *all*
lassos, not just key-built ones. This is a requirement, not a remark: it is what
the learner's E5 minimal-order guarantee will inherit, and `tests/calculus/
witness_min.py` checks it against brute-force enumeration.

**`FoldedLanguage` (protocol).** The minimal interface a decision procedure needs
from one side of a comparison: `alphabet`, `classes`, `identity`, `step(c, a)`,
`verdict(stem, loop)`. An `Invariant` implements it through `Language`
(`step(c,a) = M(c, λ(a))`, `verdict = Val_P`). A learner Cayley hypothesis
implements it with its `step` table and its P-cache read-off — *its own*
discipline, no linked-pair law assumed (a mid-run form need not be associative).
Alignment and the decision scans use only this protocol; the surgery catalog and
`reduce` require a genuine `Invariant`.

*Deviation from the spec:* the protocol carries `alphabet`, which the spec's
sketch omits. `align` needs Σ and cannot recover it from the class set; both
`Invariant` and `Hypothesis` already expose it.

---

## 2. `table.py` — the algebra

`Table` wraps an accept-free `Invariant` (the carrier) and memoizes `fold`,
`idempotent_power`, `linked_pairs` and the factorization index. The algebra is
*not* reimplemented here; only `Val` and the cell order are new.

Two hard requirements:

- **Pair sets are plain immutable sets of linked-pair ids** over their table;
  every surgery returns a new set; nothing mutates a table.
- **Key discipline**: keys are the shortlex-BFS names — process the queue by
  length then lex, extend by letters in the fixed `Σ` order, first discovery of
  a class fixes its key. One routine, `sos.core.canonical.shortlex_bfs`, serves
  three call sites: `canonicalize` (for producers of invariants), `Table.of_raw`
  (which additionally *restricts* to the reachable part instead of rejecting an
  unreachable class), and `align` (over class *pairs*). Class id order, key
  shortlex order, and scan position therefore agree.

---

## 3. `align.py` — the generated product (the only product-priced move)

    align(A: FoldedLanguage, B: FoldedLanguage) -> Aligned

Precondition: same alphabet — assert, do not adapt; `inverse_substitution` is
the adapter.

BFS over pair nodes `(c_A, c_B)`, seeded with the identity pair `(id_A, id_B)`
(key `ε`), extending by `step` on both sides simultaneously, in shortlex order:
the reachable node set is exactly `{(fold_A(w), fold_B(w)) : w ∈ Σ*}` — the
letter-generated subsemigroup plus identity — of size `≤ n_A·n_B`, usually far
less. Each node stores its shortlex key (first discovery); each edge is two
`step` calls.

- **No product multiplication table is ever materialized.** `Aligned` exposes
  `step` (componentwise), the node set with keys, and the two verdict maps
  `Val_A(node_c, node_d) := A.verdict(c_A, d_A)`, `Val_B(…) := B.verdict(c_B,
  d_B)` — component evaluation, each side under its own discipline. When a side
  is an `Invariant`, evaluating on the component with `idem(d_A)` is equivalent
  to projecting a pair idempotent power — the cyclic idempotent is unique — so
  componentwise is safe. The hypothesis side has no such notion and must only
  ever be asked through its `verdict`.
- Cost: `O(n_A·n_B·|Σ|)` `step` calls, `O(n_A·n_B)` memory. `Aligned.ratio`
  records the realized `|nodes| / (n_A·n_B)`; V1 measures it. Observed on
  corpus pairs: median ≈ 0.18, min ≈ 0.008.
- When both sides are languages over one table (`A.table is B.table`), `align`
  returns the trivial diagonal without BFS.

---

## 4. `surgery.py` — the free fragment

All functions take (table, pair set(s)) and return pair sets on the same table,
`O(|linked|)` unless stated. Each carries its one-line correctness fact as its
docstring; the harness replays them.

- `complement(P) = linked \ P`. Correct because `Val_{Pᶜ} = ¬Val_P` pointwise
  (the flip commutes with the `(M(c,e), e)` lookup).
- `union / intersection / difference / xor`: set operations; `Val` commutes with
  all of them pointwise. Constants: `empty = ∅`, `universal = linked`.
- `rooting(P, c) = {(s, e) ∈ linked : (M(c, s), e) ∈ P}` for `c ∈ 𝒞`.
  Well-defined (`(M(c,s), e)` is linked when `(s, e)` is) and
  `Val_{P_c}(x, d) = Val_P(M(c, x), d)`, so `L(P_c) = key(c)⁻¹·L`. The action
  law `P_{M(c,d)} = (P_c)_d` is asserted in the harness. The **residual count
  read-off**: the number of distinct sets among `{P_c : c ∈ 𝒞}` — expose it, it
  is a datum.
- `pair_language(pairs)` — any *saturated* subset of linked pairs as a language.
- `inverse_substitution(table, P, Σ', π: Σ' → Σ)`: same classes and product,
  letter map `λ ∘ π`. The reachable part may shrink, so the result is restricted
  to it and `P` filtered to the survivors; hand it to `reduce` before any
  byte-level use. Covers relabeling, letter merging, alphabet extension by
  duplication.

### 4.1 Saturation — where the spec is wrong

Two linked pairs denote the same ω-word class iff they are **conjugate**. The
spec (§3.3) states the closure as

    (s, e) ∈ Q, x, y ∈ 𝒞, M(x,y) = e, M(y,x) = f, t = M(s,x)  ⟹  (t, f) ∈ Q

with the parenthetical "*(f idempotent and (t,f) linked follow)*". **That
parenthetical is false.** `M(x,y) = e` idempotent does not make `M(y,x)`
idempotent. Counterexample, `3state1ap0acc_074764.sos` (20 classes): the linked
pair `(7, 7)` factors as `e = M(1, 8)`, and `f = M(8, 1) = 13` has `M(13,13) ≠
13`. Sixty-nine such firings occur in that one table.

What is true is the *word* identity `u·(xy)^ω = (ux)·(yx)^ω`, which is a law
about **cells**, not about linked pairs:

    Val_P(s, e) = Val_P(M(s,x), M(y,x))      whenever M(x, y) = e

So the conjugate cell must be normalized back to a linked pair through `Val`'s
own lookup before it is inserted. The implemented rule is

    (s, e) ∈ Q, M(x,y) = e  ⟹  linked_pair_of(M(s,x), M(y,x)) ∈ Q
    where linked_pair_of(t, f) = (M(t, idem(f)), idem(f))

Conjugacy is symmetric (swap `x` and `y` to travel back), so the closure is a
union of conjugacy classes. `O(|linked|·n²)` worst case; run rarely.

Two uses: (i) legality check — `pair_language` asserts `saturate(pairs) =
pairs`; (ii) **internal law** — every pair set produced by this catalog
satisfies `saturate(P') = P'`; the harness asserts it on every operation output,
and a violation convicts the operation. Never `saturate` an output silently to
hide it.

### 4.2 Hulls and the obligation rung (paper §3.6)

The topological classifications as surgeries and read-offs on the same table.
Normative math: paper Prop 3.5, Cor 3.6–3.7, Thm 3.10, Prop 3.11.

- `live(P) = {c : row of c in M meets stems(P)}` — the classes with a nonempty
  residual (the identity is a class, so the row contains `c` itself). One
  `O(n²)` pass against a stem bitmask.
- `safety_closure(P) = {(s, e) ∈ linked : s ∈ live(P)}` — the pair set of
  `cl(L)`, the smallest closed superset. A closure operator on the saturated
  pair sets (extensive, monotone, idempotent).
- `interior(P) = {(s, e) ∈ linked : s ∉ live(complement(P))}` — the largest
  open subset, `¬cl(¬L)`.
- `liveness_part(P) = P ∪ complement(safety_closure(P))` — the canonical
  liveness factor: every class is live for it, and
  `P = safety_closure(P) ∩ liveness_part(P)` (Alpern–Schneider on one table).
- `is_safety(P) := P == safety_closure(P)`, `is_cosafety(P) := P ==
  interior(P)` — exact fixpoint tests, not approximations.
- `is_obligation(P)`: the verdict depends only on the R-class of the stem —
  bucket linked pairs by stem (constant verdict per bucket), then demand
  constancy on each SCC of the right-Cayley letter graph `c → M(c, λ(a))`
  (R-classes, since the table is letter-generated). One Tarjan pass,
  `O(|linked| + n·|Σ|)`.
- `obligation_degree(P) -> (n⁺, n⁻)` (precondition `is_obligation`, asserted):
  condense the right-Cayley graph, label each SCC holding a linked stem with
  its verdict `θ`, and take the longest `θ`-alternating path starting at a
  `θ = 1` (resp. `0`) node — one reverse-topological DP per polarity. A lone
  node is a path of length 0; a polarity with no starting node yields `-1`
  (the empty/universal convention of the `.cat` sidecars).

Gates: `tests/calculus/hulls.py` (closure laws, duality, decomposition,
prefix-liveness replay against the paired det HOA) and
`tests/calculus/obligation_oracle.py` (the `.cat` Wagner coordinates as the
oracle: `is_obligation ⟺ max(m⁺, m⁻) ≤ 0`, degree = sidecar `(n⁺, n⁻)`;
worked reference `a*·b^ω` → `(1, 2)`).

---

## 5. `decide.py` — decisions as scans, witnesses always

All procedures scan cells in the normative order and return `(bool,
Optional[Witness])`; by Proposition W the witness is the globally minimal one.
Single-table forms take `(table, P)`; cross-table forms take an `Aligned`.

- `member(P, u, v)`: `Val_P(fold(u), fold(v))` — `O(|u| + |v|)` lookups.
- `is_empty(P)`: `P = ∅`; else the least cell with `Val_P` true furnishes the
  witness. (Scan cells, not `P`: the least *pair* in `P` is not in general the
  least *cell* — a short non-idempotent loop key can map into a long-keyed
  linked pair.)
- `is_universal(P)`: `is_empty(complement(P))`.
- `included(A ≤ B)` on an `Aligned`: first cell with `Val_A ∧ ¬Val_B` yields the
  separating lasso. Cost `O(|nodes|²)` verdict evaluations.
- `equivalent(A, B)` on an `Aligned`: one scan of `Val_A ≠ Val_B` — both
  inclusion defects in one pass, least disagreeing cell as counterexample. On
  two *reduced* invariants, byte equality of the `.sos` dumps is the `O(1)`-scan
  alternative ([SωS26 Thm 5.1]) — `byte_equivalent` exposes it, and the two must
  agree wherever both apply (harness 5, 7).
- `intersecting_word(A, B)` on an `Aligned`: least cell with `Val_A ∧ Val_B` —
  the model-checking-shaped query. The one procedure whose certificate attends
  the `True` answer.

---

## 6. `reduce.py` — the normal form

    reduce(table, P) -> Invariant     # the syntactic invariant of L(P)

The re-quotient of the calculus paper §3.1 move 3. The congruence: `c ≈ c'` iff
`c` and `c'` are interchangeable in both context shapes over the table.
Partition refinement, letters only:

1. **Base partition** by the `O(n)`-bit signature
   `sig(c) = ( Val_P(c, d) : d ∈ 𝒞 \ [ε] ) ++ ( Val_P(x, c) : x ∈ 𝒞 )`
   (the class as a stem against every loop; as a loop against every stem).
2. **Refine to a two-sided congruence**: split blocks until for every letter `a`,
   `c ≈ c'` implies `M(c, λ(a)) ≈ M(c', λ(a))` and `M(λ(a), c) ≈ M(λ(a), c')`.
   Moore-style iteration to fixpoint, `≤ n` rounds of `O(n·|Σ|)`. Letters
   suffice: contexts are letter products, so single-letter two-sided stability
   plus the base signature yields full-context interchangeability — the standard
   induction; do not enumerate context triples.
3. **Quotient**: classes = blocks; `M`, `λ` induced (well-defined by step 2, and
   asserted); `P` = image pairs. Re-key by the shortlex BFS.
4. **Identity convention**: `[ε]` is excluded from the refinement and re-adjoined
   as the fresh singleton — never merged, even if some block acts neutrally (the
   `.sos` canonicity requirement).
5. **Assertions before returning** (each a violation ⇒ raise, never emit): the
   quotient's `Val` pulls back to the input's `Val` on every cell (`O(n²)`);
   `reduce` of the result is byte-identical to the result (idempotence); the
   result parses back through the `.sos` io round-trip. `check=False` skips
   them, for the interior of those very checks and for large aligned products
   where the quadratic pullback would dominate.

Cost target: `O(n²·|Σ| + n²)` after the base signatures (`O(n²)` `Val` calls) —
negligible at census sizes (`n ≤ 121`).

---

## 7. Soundness harness

Implemented by the gates in `sosl/tests/calculus/`; see that folder's
`README.md` for the source map and how to run them.

1. **Boolean laws** (per table, random languages): double complement, De Morgan,
   `xor = (∪) \ (∩)`, `∅`/`linked` identities — pure set algebra, plus pointwise
   `Val` agreement on all cells.
2. **Saturation law**: `saturate(P') = P'` for the output of every catalog
   operation, on every harness case.
3. **Metamorphic replay** (the deep check): for each operation and each lasso
   with `|u|, |v| ≤ 3` (exhaustive): `member(result, u, v)` equals the Boolean
   combination of `member(input_i, u, v)` — complement flips, union ors, rooting
   prepends `key(c)`, inverse substitution maps letters.
4. **Rooting laws**: `P_{M(c,d)} = (P_c)_d`; `P_{[ε]} = P`.
5. **Alignment laws**: `align(I, I)` is the diagonal and `equivalent` accepts it;
   `reduce` is byte-identity on an already-reduced invariant; `equivalent` on an
   aligned pair agrees with byte equality of the two reduced sides.
6. **Duality gate**: `reduce(complement(P))` byte-equals the stored complement —
   the corpus (`genaut/corpus/flat_canon/`) is complement-closed, so this runs
   on *every* corpus case for free.
7. **The corpus as equality oracle**: `flat_canon` holds one file per language,
   so language equality *is* filename equality. Sampled pairs (same-file and
   cross-file): `equivalent` returns true exactly on same-file pairs, and every
   counterexample on a cross-file pair replays correctly against both `.sos`
   sides.
8. **Witness minimality**: the returned witnesses equal the brute-force minimal
   disagreeing/satisfying lassos from bounded enumeration.

Checks quadratic in the class count are sampled once a table is large, so that
one gate on one input stays inside the per-example diagnostic budget; each gate
prints the scope it actually covered.

## 8. Expected failures — read before filing a bug

| # | check | expectation | on failure |
|---|---|---|---|
| A1 | harness 1–5, 8 | always green | calculus-core bug |
| A2 | saturation law (harness 2) | always green | the operation emits a non-language pair set — fix the operation, never `saturate` the output silently |
| A3 | reduce idempotence / pullback (§6.5) | always green | quotient bug; the failing cell localizes it |
| P1 | corpus equality oracle (harness 7) | green | if `equivalent` disagrees with filename identity, suspect the calculus first, the corpus dedup second — report, do not "fix" the corpus |
| F1 | Spot cross-checks (V1/V2) | MAY disagree | dictionary/naming first; only a failed witness replay makes it a bug |
| F2 | Spot timeout in V1/V2 | allowed | skip and record, never wait (repo discipline) |

## 9. Not here, on purpose

The exponential frontier (`W·L`, `W^ω`, `remove_ap` — paper §3.4) is **not**
implemented and not stubbed. Nor are exit constructions to NBA, hulls (paper
§3.5, "conjecturally" — theory owes the pair sets first), any CLI, or any
learner integration (a separate commission against `sos_learning_spec.md` §3.2,
once this package stands).
