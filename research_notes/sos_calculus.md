# Computing with ω-Regular Languages in Canonical Form: A Calculus on the Syntactic ω-Semigroup

**Yann Thierry-Mieg**

With significant inputs from
**Claude (Anthropic)**

*Working draft — 2026-07-11.*

## Abstract

The syntactic ω-semigroup of an ω-regular language — Arnold's canonical
algebra — is now constructible from any deterministic Emerson–Lei
automaton, reified as a finite, byte-comparable invariant
`𝓘(L) = (𝒞, λ, M, P)`: a keyed class set, a letter map, a multiplication
table, and a set of accepting linked pairs [SωS26]. This paper proposes
to *compute with it*: to perform the everyday operations of an
ω-automata toolbox (Spot's, say) on the invariant instead of on
automata. The calculus has three primitive moves: **align** two
invariants on a common table (a generated product, the only
product-priced move), **operate** by surgery on the pair set `P` (where
almost every operation lives, almost always for free), and **reduce** to
the canonical object (re-quotient, polynomial). Complement —
`2^{Θ(n log n)}` on nondeterministic Büchi automata — is one bit-flip.
Equivalence — PSPACE on automata — is byte equality. Membership of a
lasso is one fold and one lookup; emptiness, universality, and inclusion
are scans, each returning the *minimal* witness lasso; left quotients,
inverse substitutions, and alphabet hygiene — dropping an unconstrained
atomic proposition, equality up to renaming — are free surgeries and
read-offs. One classification the calculus itself consumes is an
equation on the table: LTL-definability is aperiodicity of `M`, one
scan, and every surgery preserves it. The safety closure, the interior,
and the Alpern–Schneider decomposition are `O(n²)` surgeries on the
same table. The exponentials do not disappear — they
concentrate, exactly at the ω-rational constructors (concatenation by a
prefix set, ω-power) and existential projection, where a powerset is
intrinsic. The economy is *pay canonicity once*: entering the calculus
costs what determinization always cost; everything downstream is cheap,
normal-formed, and certificate-producing. The calculus is implemented as
a small pure library, its every decision replayable against independent
oracles; measured on a complement-closed corpus of small languages, the
generated product realizes a median 0.17 of its `n₁·n₂` bound, and the
read-offs it keeps agree with the automata-side construction on every
language of the corpus.

---

## 1. Introduction

An ω-automata toolbox — Spot [DL+16, DL+22] is the exemplar throughout —
pays for language operations with automaton constructions. Intersection
and union are products, decorated with acceptance bookkeeping —
degeneralization counters, condition rewrites.
Complementation of a nondeterministic Büchi automaton is the hard currency
of the trade: `2^{Θ(n log n)}` states, through Safra trees, rank
functions, slices, or one of their descendants [Saf88, TFVT10]. Language
inclusion and equivalence are PSPACE-complete, discharged in practice by
complement-and-product or by simulation heuristics. Each classification
query is its own bespoke construction followed by an equivalence
check. And every one of these steps returns a
*machine*: a presentation of the result, not the result itself. The output
must be re-simplified after every operation, the simplification is
heuristic and model-bound, and no normal form exists to simplify *to* —
minimal deterministic ω-automata are not unique, and even minimizing a
deterministic Büchi automaton is NP-complete [Sch10]. The costs are
per-operation and the results are never canonical.

There is a second way to hold an ω-regular language. Arnold's syntactic
congruence [Arn85] assigns to `L` a canonical finite algebra — the
syntactic ω-semigroup — which is presentation-independent and complete.
That object was for four decades a definition without a construction; it
is now built from any deterministic Emerson–Lei automaton [EL87] and
reified as
the exportable invariant `𝓘(L) = (𝒞, λ, M, P)`: a keyed class set, a
letter map, a multiplication table, and a set of accepting linked pairs
[SωS26]. The reification comes with a completeness theorem
[SωS26, Thm 5.1]: two ω-regular languages are equal iff their invariants
are byte-equal after canonical keying.

This paper reads the completeness theorem as an API. If `𝓘(L)` *is* the
language, then operations on languages ought to be operations on
invariants — and it turns out that almost all of them are trivial ones.
The calculus we propose has three primitive moves:

1. **Align.** Put two invariants on one table, by a *generated product* —
   the reachable part of the pairing, at most `n₁·n₂` classes and often
   far fewer. This is the only move priced like an automaton product, and
   one alignment serves every subsequent operation on the pair.
2. **Operate.** Perform the operation as a surgery on pair sets over the
   fixed table. This is where the toolbox lives: complement is one flip,
   Boolean combinations are set operations, left quotients are index
   shifts, membership of a lasso is a fold and a lookup, and every
   decision procedure is a scan that emits the minimal witness lasso.
3. **Reduce.** Re-quotient the table by the congruence its own verdicts
   induce, returning *the* syntactic invariant of the result — a normal
   form, available after every step, that automata do not have.

An operation is expensive exactly when it
cannot be phrased as surgery on an aligned table, and the calculus is
honest about which those are: the ω-rational constructors — concatenation
by a prefix set, ω-power — and existential projection of an atomic
proposition quantify over a split position or a guessed run, and there a
powerset is intrinsic. Entering the calculus from a nondeterministic
acceptor embeds a determinization; no lower bound is evaded. The economic
claim is *amortization*: a pipeline that complements, conjoins, quotients,
checks and re-checks a specification pays the exponential once, at the
gate, instead of at every complement — and every intermediate result it
holds is canonical, byte-comparable, and certificate-bearing.

Contributions:

1. **The three-move decomposition** and the free-surgery catalog (§3):
   the classical toolbox — complement, union, intersection, difference,
   membership, emptiness, universality, inclusion, equivalence,
   intersection-nonemptiness, left quotient, relabeling, alphabet
   hygiene — realized as
   pair-set surgeries and `Val`-scans over a fixed table, with the
   conjugacy-saturation law (Proposition 3.1) delimiting which pair sets
   are languages at all.
2. **The certificate discipline** (Proposition 3.2): every decision the
   calculus renders is accompanied by the *globally minimal* witness
   lasso, obtained from the scan order alone — no separate
   counterexample-extraction machinery.
3. **Read-offs replacing constructions** (§5–§6): the LTL-definability
   gate — aperiodicity of the table, one scan, preserved by every
   surgery (Lemma 3.3) — and the hulls: safety closure, interior, and
   the Alpern–Schneider decomposition as `O(n²)` surgeries on the same
   table (Proposition 6.1, Corollaries 6.2–6.3).
4. **The ledger, and the evidence** (§7–§8): a side-by-side of the
   calculus against a production toolbox, one row per operation, with
   the exponential frontier located exactly (§4); and the measurements.
   The calculus is implemented as a small pure library under a
   soundness harness whose deepest gates are metamorphic replay and a
   complement-closed corpus used as an equality oracle. Measured
   against Spot over that corpus (§8), the rows come out as the
   frontier predicts: the free surgeries and read-offs run in
   microseconds on the held object, and where the automata side pays a
   determinization or an equivalence test the calculus pays a set
   operation or a byte comparison.

§2 recalls the object, the algebraic toolkit the proofs use, and the
running example. §3 develops the calculus; §4 locates the exponential
frontier; §5 keeps the one classification read-off the calculus
consumes — the LTL cut; §6 develops the hulls; §7 draws the ledger and
the cost summary and states what the calculus refuses to simulate; §8
reports the measurements; §9 positions the work; §10 concludes.

## 2. Background: the object, the toolkit, the example

### 2.1 The invariant and its oracle

We recall from [SωS26] exactly what the calculus consumes, and fix the
conventions every later scan relies on. Throughout, `Σ` is a finite
alphabet (for LTL applications `Σ = 2^AP`), `L ⊆ Σ^ω` is ω-regular, and a
**lasso** is an ultimately-periodic word `u·v^ω` with stem `u ∈ Σ*` and
loop `v ∈ Σ⁺`. Two ω-regular languages are equal iff they agree on all
lassos [PP04], so every object below is machinery for sorting lassos into
finitely many types.

**The invariant.** `𝓘(L) = (𝒞, λ, M, P)`:

- `𝒞` — the finite set of classes of Arnold's syntactic congruence, each
  keyed by its shortlex-least representative word (`key(c)`); a fresh
  identity `[ε]` is adjoined unconditionally, keyed by the empty word,
  never merged even when a non-empty class acts neutrally;
- `λ : Σ → 𝒞` — the letter map;
- `M : 𝒞 × 𝒞 → 𝒞` — the multiplication table (the Cayley table of
  `S(L)₊¹`);
- `P` — the set of **accepting linked pairs**: pairs `(s, e)` with
  `e·e = e`, `s·e = s`, `e ≠ [ε]`, such that `u·z^ω ∈ L` for
  representatives `u` of `s` and `z` of `e`.

We write `n = |𝒞|`, `fold(w)` for the left-to-right evaluation of a
finite word through `λ` and `M` (`fold(ε) = [ε]`), and `linked(𝓘)` for
the set of all linked pairs of the table. For `d ≠ [ε]`, `idem(d)`
denotes the unique idempotent in the cyclic subsemigroup
`{d, d², d³, …}`; it exists and is unique because the table is finite,
and is computed by one `O(n)` power walk, memoized.

**The membership oracle.** The central function of the calculus is the
totalization of `P` to arbitrary stem/loop classes:

```
Val_P(c, d)  :=  ( M(c, idem(d)), idem(d) ) ∈ P        c ∈ 𝒞, d ∈ 𝒞 \ {[ε]}
```

The pair `(M(c, e), e)` with `e = idem(d)` is automatically linked, so
`Val_P` is total on its domain, and the factoring theorem of the
construction gives, for every lasso,

```
u·v^ω ∈ L   ⟺   Val_P(fold(u), fold(v)).
```

The theorem has a stronger form the proofs below use: for *any* ω-word
`α` and any factorization `α = w₀·w₁·w₂·⋯` whose blocks `w_{j≥1}` all
fold to one idempotent `e`, membership is decided by the associated
pair — `α ∈ L ⟺ (fold(w₀)·e, e) ∈ P` — and Ramsey's theorem guarantees
every ω-word admits such a factorization [PP04]. Two ω-words that admit
factorizations with the same stem image and the same idempotent block
image therefore share their verdict.

Every decision procedure below is a scan of `Val` over **cells**
`(c, d) ∈ 𝒞 × (𝒞 \ {[ε]})` — the stem class `c = [ε]` encoding the empty
stem — never a scan over words.

**Cell order and canonical lassos.** The canonical lasso of a cell
`(c, d)` is `key(c)·key(d)^ω`. Cells are ordered by their canonical
lassos under the *discipline order*: shortest stem, then shortest loop,
then stem lexicographic, then loop lexicographic. Every "first cell" or
"least witness" below means least in this order; Proposition 3.2 will
show that scanning in it yields witnesses that are minimal among *all*
lassos, not merely among key-built ones.

**Completeness and canonicity.** Theorem 5.1 of [SωS26]: for a fixed
`Σ`, `𝓘(L)` determines `L` exactly — two ω-regular languages over `Σ`
are equal iff their invariants coincide, and the canonical serialization
makes "coincide" byte equality. This is the theorem the calculus
operationalizes: it licenses treating pair sets over a fixed table as
languages, and byte comparison of reduced objects as the equivalence
test.

**Notation for the calculus.** `𝓘₁ = (𝒞₁, λ₁, M₁, P₁)` and
`𝓘₂ = (𝒞₂, λ₂, M₂, P₂)` are two invariants over a common `Σ`, with
`n_i = |𝒞_i|`. A **table** is a triple `(𝒞, λ, M)` — the algebra without
its acceptance datum; one table hosts many pair sets, and the calculus's
central discipline is that pair sets are *values* over a shared,
immutable table. Not every subset of `linked(𝓘)` denotes a language; the
exact condition — saturation under conjugacy — is Proposition 3.1.

### 2.2 The algebraic toolkit

The proofs of §6 use a small kit of classical finite-semigroup facts,
collected here so the paper is self-contained; [PP04] covers all of it.
Products are taken in `M`; recall that `𝒞` contains the fresh identity
`[ε]`, so `c·𝒞` below already includes `c` itself.

**Idempotent powers.** In a finite semigroup every element `x` has
exactly one idempotent among its powers `{x, x², x³, …}`; we write it
`x^π` (so `idem(d) = d^π`, computed by the memoized power walk of §2.1).
The exponent can be taken uniform over the table (any sufficiently
divisible one); the proofs use only idempotence, `x·x^π·x = x^{π+2}`-style
arithmetic, and uniqueness.

**Green's relations.** For `x, y ∈ 𝒞`: `x ≤_R y` iff `x ∈ y·𝒞`, and
`x R y` iff each is `≤_R` the other — they generate the same right
ideal. The `R`-classes are the strongly connected components of the
**right-Cayley graph** of the table (nodes `𝒞`, an edge `c → c·λ(a)`
per letter [SωS26, Def 5.2]), and `≥_R` is reachability in it — the
geometric reading the liveness scan of §6 exploits.

### 2.3 The running example

The specimen threaded through the paper is Carton–Perrin's own
[CP97, Ex. 10]: `L = a*·b^ω` over `Σ = {a, b}` — some `a`'s, then `b`'s
forever. Its invariant has five classes,

```
𝒞 = { [ε], A, B, C, D },    keyed    ε, a, b, ab, ba,
```

with `A = [a]` the words in `a⁺`, `B = [b]` those in `b⁺`, `C = [ab]`
those in `a⁺b⁺`, and `D = [ba]` the *dead* words — once an `a` follows
a `b`, no continuation can rescue the word. The letter map is
`λ(a) = A`, `λ(b) = B`; the multiplication table (identity row and
column omitted) is

| `·` | `A` | `B` | `C` | `D` |
|---|---|---|---|---|
| **`A`** | `A` | `C` | `C` | `D` |
| **`B`** | `D` | `B` | `D` | `D` |
| **`C`** | `D` | `C` | `D` | `D` |
| **`D`** | `D` | `D` | `D` | `D` |

The idempotents are `A`, `B`, `D` (`C² = D`, so `C^π = D`). The linked
pairs are `(A,A), (D,A), (B,B), (C,B), (D,B), (D,D)`, and the
accepting set is

```
P = { (B, B), (C, B) }
```

— the two behaviors of the language: "reading `b`'s after nothing but
`a`'s (if any), keep reading `b`'s".

**Reading the algebra: lasso queries.** Membership of a lasso is one
fold and one lookup (§3.2), and the example shows each part of the
oracle at work:

- `b^ω`: `fold(ε) = [ε]`, `fold(b) = B` idempotent;
  `Val_P([ε], B) = ((B, B) ∈ P)` — accept.
- `aab·b^ω`: `fold(aab) = A·A·B = C`, loop class `B`;
  `(C·B, B) = (C, B) ∈ P` — accept.
- `a·(ab)^ω`: `fold(ab) = C` is *not* idempotent; the oracle totalizes
  through `C^π = D`: `Val_P(A, C) = ((A·D, D) ∈ P) = ((D, D) ∈ P)` —
  reject. The idempotent-power step is visibly doing the work: the
  loop `ab` keeps producing an `a` after a `b`.

Every later section revisits this table: complement and quotients in
§3.2, alignment in §3.3, and the hulls in §6.

## 3. The calculus

### 3.1 Three primitive moves

Every operation below factors through three moves:

1. **Align.** Put two invariants on one table: the *generated product*
   `𝓘₁ ⊗ 𝓘₂`, with class set the submonoid of `𝒞₁ × 𝒞₂` generated by
   `{ (λ₁(a), λ₂(a)) : a ∈ Σ }` (fresh identity adjoined), letter map
   `a ↦ (λ₁(a), λ₂(a))`, componentwise multiplication, and *both* pair
   sets carried along as verdict maps
   `Val_i((c₁,c₂), (d₁,d₂)) = Val_i(c_i, d_i)`. The generated part is
   computed by a shortlex BFS from the identity pair, extending by
   letters — exactly the reachable set
   `{ (fold₁(w), fold₂(w)) : w ∈ Σ* }` — so nodes are keyed on first
   discovery and no product multiplication table is ever materialized.
   Size at most `n₁·n₂`, often far less — only the generated part
   exists. One alignment serves all subsequent operations on the pair.
   (Componentwise verdicts are sound because the cyclic idempotent is
   unique: evaluating `idem` on a component agrees with projecting an
   idempotent power of the pair.)
2. **Operate.** Surgery on pair sets over the fixed table. This is where
   the operations live, and the catalog of §3.2 is the point: almost all
   of them are `O(|P|)` or one scan.
3. **Reduce.** Re-canonicalize: quotient the table by the congruence its
   own `Val` induces. Concretely, a partition refinement: seed with the
   `O(n)`-bit signature of each class (its `Val` row as a stem against
   every loop, and its `Val` column as a loop against every stem), then
   refine to two-sided stability under every *letter* — single-letter
   stability plus the base signature suffices for full-context
   interchangeability, by the standard induction, so context triples are
   never enumerated. At most `n` Moore rounds of `O(n·|Σ|)`; the
   quotient inherits `M`, `λ`, and the image pair set, is re-keyed by
   the shortlex BFS, and *is* the syntactic invariant of the pair set's
   language. Reduction is the calculus's normal form — the move automata
   do not have (minimal deterministic ω-automata are not unique
   [Sch10]; simplification is heuristic and model-bound).

The slogan: **align is the only product-priced move; operate is free;
reduce is the normal form.** An operation is expensive exactly when it
cannot be phrased as surgery on an aligned table — §4 locates those.

### 3.2 The free fragment: the surgery catalog

All of the following act on a fixed table `(𝒞, λ, M)`; each is either a
query answered by lookups, or a surgery returning a pair set on the same
table, to be reduced at will. One safety net covers the whole fragment:

**Lemma 3.3 (surgery never leaves the variety).** For every saturated
pair set `P'` over the table of `𝓘(L)` (letter map possibly recomposed),
the syntactic algebra of `L(P')` divides `M`. In particular an aperiodic
table yields only aperiodic — that is, LTL-definable [DG08] — results,
however the pair sets are cut.

*Proof.* `reduce` (§3.1) quotients the carrier by a congruence of `M`
after restricting, when the letter map changed, to the generated
subsemigroup; the result — by [SωS26, Thm 5.1] applied to the reduced
object, *the* syntactic algebra of `L(P')` — is a quotient of a
subsemigroup of `M`, i.e. a divisor. Aperiodicity (`x^{k+1} = x^k` for
`k` large) passes to subsemigroups and quotients. ∎

- **Lasso membership.** `member(P, u, v) := Val_P(fold(u), fold(v))`:
  `O(|u| + |v|)` table lookups (plus one memoized idempotent walk). This
  is not an operation *built from* the oracle — it *is* the oracle, the
  function every other entry scans. On automata the same query runs the
  word against the machine and inspects the loop's acceptance; here the
  automaton-shaped work (the fold) is the whole cost, and the verdict is
  a set lookup.
- **Boolean algebra.** `P₁ ∪ P₂`, `P₁ ∩ P₂`, `P^c` (relative to the
  linked pairs), differences, xor: the same-table languages form a
  *finite Boolean algebra*, isomorphic to the algebra of saturated pair
  sets, because `Val` commutes pointwise with every set operation (the
  flip and the joins act after the same `(M(c,e), e)` lookup). Complement
  is one flip — against `2^{Θ(n log n)}` for nondeterministic Büchi
  complementation [TFVT10], this is the calculus's headline entry — and
  the constants are `∅` (empty language) and `linked(𝓘)` (universal).
  On the running example the flip is
  `P^c = {(A,A), (D,A), (D,B), (D,D)}` — the complement `¬(a*·b^ω)` on
  the same five classes, no Safra in sight.
- **Rooting (left quotients).** For `c ∈ 𝒞` define
  `P_c := { (s, e) linked : (c·s, e) ∈ P }`. Well-defined — `(c·s, e)` is
  linked when `(s, e)` is — and `Val_{P_c}(x, d) = Val_P(c·x, d)`, so
  `L(P_c) = u⁻¹L` for any representative `u` of `c` (in particular
  `P_{[ε]} = P`): prefix subtraction is pair surgery. The rootings form a right `M`-action,
  `P_{c·d} = (P_c)_d`, so quotients compose as they must
  (`(uv)⁻¹L = v⁻¹(u⁻¹L)`), and the number of distinct rootings *is* the
  residual count read-off [SωS26, Prop 4.6]: the residual automaton of
  `L`, internalized. In particular `L` is prefix-independent iff all
  rootings equal `P`. On the running example, `P_A = P` (`a⁻¹L = L`:
  the `a*` absorbs) while `P_B = {(B, B)}` — the language `{b^ω}`:
  after one `b`, only `b`'s remain.
- **Pair languages and prolongations.** The pair classes are the
  conjugacy classes, and conjugacy is a law about *cells*, not pairs:

  **Proposition 3.1 (conjugacy and saturation).** For every linked pair
  `(s, e)` and every factorization `e = x·y`:
  `s·e^ω = (s·x)·(y·x)^ω`, so the cells `(s, e)` and `(s·x, y·x)` carry
  one verdict. The conjugate cell renormalizes to the linked pair
  `((s·x)·f, f)` with `f = (y·x)^π` — and the renormalization is not
  optional: `x·y` idempotent does not make `y·x` idempotent; only
  `(y·x)²` is guaranteed to be (`(yx)³ = y·(xy)²·x = (yx)²`), so the
  naive pair-level transport `(s, e) ↦ (s·x, y·x)` leaves the linked
  pairs. Two linked pairs denote the same ω-word class iff the closure
  under these renormalized moves connects them [PP04]; a set of linked
  pairs is a language over the table iff it is a union of such classes —
  *saturated*. (Conjugacy is symmetric — swap `x` and `y` — so the
  closure is a union of conjugacy classes; the fixpoint costs
  `O(|linked|·n²)` and doubles as the legality check for arbitrary pair
  sets. Every surgery in this catalog preserves saturation, and the
  implementation's harness asserts it on every output.)

  Any saturated `P'` is then a language: a single conjugacy class gives
  "the words realizing exactly this accepting behavior" — *prolonging
  the language from one of its behaviors*, the finest OR-decomposition
  the algebra supports.
- **Inverse substitutions.** For `π : Σ' → Σ` (relabeling, letter
  merging, alphabet extension by duplication): compose `λ ∘ π`, same
  table, reduce — the reachable part may shrink, so the result meets the
  normal form before any byte-level use. Inverse morphic images are
  free; Spot's `relabel` is a special case.
- **Alphabet hygiene.** For LTL applications `Σ = 2^AP`, and two
  toolbox staples become read-offs on `λ`:
  - *Unconstrained propositions.* `p ∈ AP` is **free** in `L` iff
    `λ(a[p↦1]) = λ(a[p↦0])` for every valuation `a` — `|Σ|/2` lookups.
    (⇒: toggling `p` at one position is an Arnold-context move, so
    freeness merges the letter classes; ⇐: equal letter classes give
    any two words agreeing outside `p` equal block folds in a shared
    Ramsey factorization, hence one verdict.) When the test passes,
    existential and universal projection of `p` coincide and are an
    *alphabet quotient*: merge the letter pairs — `λ` factors through
    the merged alphabet — and reduce. No powerset; contrast §4, where
    projecting a *constrained* proposition is exponential. The read-off
    prices the operation before it is paid.
  - *Equality up to renaming.* Whether `L₂ = π(L₁)` for some permutation
    `π` of `AP`: each candidate `π` is a relabel (an inverse
    substitution), one `reduce`, one byte comparison — and canonicity
    prunes hard, since class count, `|P|`, and the multiset of
    letter-class profiles are renaming-invariant and must match before
    any `π` is tried. On a corpus this is deduplication up to symmetry,
    an operation with no automata-side analogue short of an isomorphism
    search over machines that are not canonical to begin with.
- **Canonical witnesses.** Every nonempty pair set carries its own
  certificate: `(s, e) ∈ P` yields the lasso `key(s)·key(e)^ω`, shortlex
  keys giving *the* canonical witness word. A witness or counterexample
  is read off in the same scan as the decision it certifies — the
  calculus's certificate discipline, available to every operation.
  And the witness is not merely canonical:

  **Proposition 3.2 (the canonical witness is minimal).** Order lassos
  by stem length, then loop length, then lexicographically, and scan
  cells `(c, d)` in the order of their lassos `key(c)·key(d)^ω`. For any
  property that factors through the membership oracle, the first
  satisfying cell's lasso is the least satisfying lasso *among all
  lassos*: a satisfying `(u, v)` lives in the cell
  `(fold(u), fold(v))`, whose keys are shortlex-least in their classes,
  so the cell's lasso dominates it componentwise. Every certificate the
  calculus emits — an emptiness witness, an inclusion or equivalence
  counterexample — is therefore the minimal one, and a client consuming
  counterexamples (a learner's teacher, say) inherits a minimal-order
  guarantee from the scan order alone.
- **Decision procedures as scans.** All of the following scan cells in
  the discipline order and return the verdict together with the least
  witnessing cell's lasso; by Proposition 3.2 that witness is globally
  minimal.
  - *Emptiness*: `P = ∅`; otherwise the least cell with `Val_P` true
    furnishes the witness. (Scan cells, not `P` itself: the least *pair*
    in `P` is not in general the least *cell* — a short non-idempotent
    loop key maps into a long-keyed linked pair.)
  - *Universality*: emptiness of `P^c` — one flip away, where automata
    pay a full complementation before their emptiness check.
  - *Inclusion* `L₁ ⊆ L₂` (same or aligned table): the pointwise test
    `Val₁ ≤ Val₂`; the first cell with `Val₁ ∧ ¬Val₂` yields the
    canonical separating lasso. Compare: PSPACE-complete on automata,
    with counterexamples needing product-emptiness runs.
  - *Equivalence*: on two *reduced* invariants, byte equality of the
    canonical serializations [SωS26, Thm 5.1] — no scan at all, one
    comparison linear in the artifact size. On an
    aligned pair, one scan of `Val₁ ≠ Val₂` decides both inclusion
    defects in a single pass and returns the least disagreeing cell as
    counterexample; the two routes agree wherever both apply.
  - *Intersection-nonemptiness with witness* (the model-checking-shaped
    query, Spot's `intersecting_word`): least cell with `Val₁ ∧ Val₂`.

### 3.3 The aligned fragment

Cross-table operations pay the alignment price `O(n₁·n₂·|Σ|)` once:

- **Union / intersection / difference / xor across tables**: align, then
  §3.2 pointwise. Note what is *absent*: no acceptance-condition
  surgery. Büchi intersection needs degeneralization counters, union of
  deterministic models may not exist in the same acceptance class,
  generalized conditions need bookkeeping; here acceptance is a pair set
  and conjunction is pointwise `∧` of verdicts.
- **Model-checking-shaped queries**: `L₁ ∩ L₂ = ∅?` is align + scan of
  `Val₁ ∧ Val₂` + canonical witness. Same product asymptotics as
  automata, plus the normal form and the certificate.
- **When alignment stays small.** The generated product materializes
  only `{ (fold₁(w), fold₂(w)) : w ∈ Σ* }` — the correlation the two
  languages actually exhibit, not the rectangle `𝒞₁ × 𝒞₂`. This is the
  calculus's own notion of "on-the-fly": exactly as a model checker
  builds only reachable product states, `align` builds only realizable
  class pairs. The two regimes are instructive. When the operands are
  related — one refines the other, both were produced by surgery from a
  common ancestor table, both constrain the same letters — folds
  correlate and the generated part collapses toward the larger factor
  (in the limit, aligning a table with itself is the diagonal, and the
  implementation short-circuits it). When the operands are genuinely
  independent — constraints over disjoint atomic propositions — the
  generated part *is* essentially the full rectangle, and that is not an
  artifact: the intersection of independent constraints genuinely
  multiplies behaviors. The realized ratio `|nodes| / (n₁·n₂)` is a
  datum the implementation records per alignment; §8 measures its
  distribution over corpus pairs — both regimes are visible, and the
  rectangle is never approached. One further economy is structural: an
  aligned product is a table like any other, so a *session* of
  operations on the same pair — inclusion both ways, intersection,
  difference, their emptiness checks — pays its BFS once.

*On the running example.* Align `𝓘(a*·b^ω)` with `𝓘(GF a)`
("infinitely many `a`'s": three classes — `[ε]`, `α` = contains an
`a`, `β` = nonempty and `a`-free — with `P₂ = {(α, α)}`). The BFS
discovers five nodes — `([ε],[ε]), (A,α), (B,β), (C,α), (D,α)` — of
the fifteen-cell rectangle: exactly the correlation the two languages
exhibit. On the shared table, `a*·b^ω ∩ GF a = ∅` is one scan: a true
cell needs a loop whose idempotent has first component `B` and second
component `α`, and no discovered node offers both (`B` pairs only with
`β`). The same aligned table answers the inclusion
`a*·b^ω ⊆ FG ¬a` — the pointwise `Val₁ ≤ ¬Val₂` — with no further
construction.

## 4. The exponential frontier

The calculus is honest about where powersets are intrinsic:

- **Concatenation by a prefix set (`W·L`) and ω-power (`W^ω`).** The
  ω-rational constructors quantify existentially over a split position:
  `α ∈ W·L` asks for *some* factorization `α = w·β` with `w ∈ W`,
  `β ∈ L`. A `Val`-scan over a fixed table evaluates one factorization
  type per cell; no surgery on an aligned table expresses an existential
  over factorizations — and none could, because the result's algebra can
  be exponentially larger than both operands':

  **Proposition 4.1 (concatenation blows up).** Over `Σ = {a, b, #}`,
  let `W = Σ*·#` (a three-element syntactic monoid: the last letter is
  `#` or it is not) and
  `L_n = { α : α contains a b, and the number of a's before the first b
  is ≡ 0 mod n }`, whose invariant has at most `2n + 1` classes (a phase
  counter mod `n` that freezes at the first `b`: `n` `b`-free classes,
  `n` frozen ones, `[ε]`). Then `𝓘(W·L_n)` has at least `2^n − 1`
  classes.

  *Proof.* `α ∈ W·L_n` iff some `#` of `α` is followed by a `b`, with
  the a-count strictly between that `#` and the first subsequent `b`
  divisible by `n` — each `#` opens a *thread* carrying the phase "a's
  seen since this `#`", and all live threads resolve together at the
  next `b`. For a nonempty `S = {s₁ < ⋯ < s_m} ⊆ {0, …, n−1}` let

  ```
  u_S  =  #·a^{s_m − s_{m−1}}·#·a^{s_{m−1} − s_{m−2}}·#·⋯·#·a^{s₁}
  ```

  a `b`-free word whose `j`-th `#` is followed by exactly `s_{m−j+1}`
  letters `a`: the live phases of `u_S` are exactly `S`. For any phase
  `φ`, the suffix `v_φ = a^{(n−φ) mod n}·b^ω` opens no thread
  (`#`-free) and resolves every live phase `ψ` at its `b` with total
  count `ψ + (n−φ) ≡ ψ − φ (mod n)`; hence
  `u_S·v_φ ∈ W·L_n ⟺ φ ∈ S`. The residuals `u_S⁻¹(W·L_n)` are
  therefore pairwise distinct, and distinct residuals are distinct
  rootings, which are indexed by classes (§3.2):
  `|𝒞(W·L_n)| ≥ 2^n − 1`. ∎

  The residuals in the proof are the subset-tracking of `L_n`'s phase
  counter — the subset construction, resurfacing in the algebra: this
  is where the nondeterminism that automata carry natively re-enters
  (an NBA for `W·L_n` guesses the split and stays linear in `n`).
  ω-power hides the same existential — a factorization into infinitely
  many `W`-blocks — and is expected to behave alike, though we exhibit
  only the concatenation half. Constructions exist on the algebraic
  side [PP04] but cost what determinization costs: the honest route is
  exit to an acceptor, apply the constructor, re-enter through the
  gate. Built by hand and re-entered through the gate, `W·L_n` realizes
  `|𝒞| = 17, 48, 127, 318` for `n = 2, …, 5` — each above `2^n − 1`, off
  acceptors of only `2^n + 1` states — the subset construction
  resurfacing in the algebra exactly as the proof predicts (§8); a
  corpus bounded to a handful of acceptor states never reaches the
  constructors that force it.
- **Existential projection (`remove_ap`).** Quantifying an atomic
  proposition away is the QPTL wall: a deterministic
  definitional extension is free (it is an inverse substitution, §3.2 —
  *adding* letters costs nothing), a genuine guess is a powerset. Spot
  pays the same, differently distributed.
- **The polynomial middle band.** Between the free fragment and the
  powerset wall sits a band where a split is present but
  *deterministic*: `X L = Σ·L` (the split is at position 1, and
  `a⁻¹(X L) = L` for every `a` — a new small table, constructible
  directly); `W·L` when `W` is a prefix code, so the factorization is
  functional — the thread mechanism of Proposition 4.1 cannot open,
  since at most one thread is ever live; and the free-proposition drop
  of §3.2, where the projection quantifier is vacuous. The frontier is
  three-tiered: surgery (free), deterministic split (a new polynomial
  object), existential split (powerset, intrinsic).
- **Entry price.** Constructing `𝓘(L)` from a nondeterministic acceptor
  embeds a determinization, and the construction itself is dominated by
  the enriched-monoid closure [SωS26, §8]; the calculus does not evade
  lower bounds, it *relocates* them to the entry gate. The economic
  claim is amortization: **pay canonicity once, then operate in the free
  fragment.** A specification pipeline that complements `k` times pays
  Safra `k` times on automata and zero times here; a pipeline that
  interleaves Boolean structure with equivalence checks pays PSPACE per
  check there and byte comparisons here; and every intermediate object
  it holds is already in normal form, so nothing is ever re-simplified.
  (§8 measures a four-stage pipeline: the entry is a small one-time
  share of the whole, and every stage's "did my rewrite change the
  language" re-check is a byte comparison.)

## 5. The LTL cut — the one classification the calculus keeps

Classification of the held language — the safety–progress ladder, the
acceptance index, the Wagner degree — is *diagnosis* on the same
object, sketched in [SωS26, §7.2]; it is not this paper's subject, and
the calculus neither needs nor restates it. One cut is different,
because the calculus itself consumes it: **LTL-definability**. `L` is
LTL-definable iff `M` is aperiodic (`x^{k+1} = x^k` for `k` large
enough) — the classical correspondence [DG08] landed on the canonical
table, where no presentation artifact can blur it — and aperiodicity is
one `O(n²)` power-orbit scan of the table, with a witness (a genuine
group cycle in the algebra) when it fails. The calculus uses the bit as
a *gate*: Lemma 3.3 keeps every surgery inside the variety, so a
pipeline that enters LTL-definable stays LTL-definable through any
sequence of free operations; the §7.3 exit reads the same bit (the
Cayley acceptor is counter-free exactly then); and formula extraction —
beyond this paper — is priced before it is attempted. Spot has no
automaton→LTL query at all; on the invariant it is a scan.

One more classification survives, in §6, because it arrives as the
fixpoint equation of an *operator*: the safety closure of `L`, its
interior, and the Alpern–Schneider decomposition
`L = safety ∩ liveness` are pair-set surgeries on the same table,
computable in `O(n²)`, and the safety and co-safety verdicts fall out
of them.

## 6. Hulls

Equip `Σ^ω` with the Cantor topology; a *safety* property is a closed
set, a *co-safety* (guarantee) property an open one, and the safety
closure `cl(L)` — the smallest closed superset — is the "safety part"
of `L` in the sense of Alpern–Schneider [AS85, MP92]. On automata,
computing `cl` is a construction (prune dead states, weaken
acceptance); the earlier draft of this paper conjectured it was a
surgery. It is, and the key is a one-scan notion of class liveness.

Say a class `c ∈ 𝒞` is **live** if its residual is nonempty — a class
property, because the syntactic congruence refines residual equality
(take `x = ε` in the linear context shape). Liveness is read off the
table:

```
Live  :=  { c ∈ 𝒞 : (c·𝒞) ∩ stems(P) ≠ ∅ },     stems(P) = { s : (s,e) ∈ P }
```

— if `c·x = s` is an accepting stem, `key(x)·key(e)^ω` continues `c`
into `L`; conversely a nonempty residual contains a lasso, and folding
it lands `c·fold(u')` on the stem of an accepting pair. One pass over
the rows of `M` against a `stems(P)` bitmask: `O(n²)`.

Two monotonicity facts drive everything: deadness propagates to
*extensions* (`c` dead ⟹ `c·x` dead), and liveness propagates to
*prefixes* (a prefix of a live word is live, by composing
continuations).

**Proposition 6.1 (the safety hull is a surgery).**
`cl(L) = L(P̄)` where `P̄ := { (s, e) ∈ linked : s ∈ Live }`.

*Proof.* Let `C := { α : every finite prefix of α is live }`.

*`C` is pair-determined, with pair set `P̄`.* Take any ω-word `α` and
any Ramsey factorization `α = w₀·w₁·w₂⋯` with idempotent block image
`e`; its associated linked pair is `(s, e)` with `s = fold(w₀)·e`, and
every block-boundary prefix `w₀⋯w_k` (`k ≥ 1`) folds exactly to `s`.
If `α ∈ C`, the boundary prefixes are live, so `s ∈ Live`. If
`s ∈ Live`, the boundary prefixes are live, and an arbitrary prefix is
a prefix of some boundary prefix, hence live — so `α ∈ C`. Membership
in `C` thus depends only on the associated pair and holds exactly on
`P̄`: `C = L(P̄)` (and `P̄` is saturated for free, membership being
word-semantic).

*`C = cl(L)`.* `C` is closed: if `α ∉ C` it has a dead prefix `p`, and
the whole cylinder `p·Σ^ω` misses `C`. `L ⊆ C`: a member's prefixes
are live by its own suffixes. Minimality: let `L' ⊇ L` be closed and
`α ∈ C`; if `α ∉ L'`, openness of the complement gives a prefix `p` of
`α` with `p·Σ^ω ∩ L' = ∅`, yet `p` is live, so some `p·γ ∈ L ⊆ L'` —
contradiction. Hence `C ⊆ L'`, and `C` is the least closed superset. ∎

An algebraic sanity check, tying into Proposition 3.1: a conjugate
presentation of the same lasso renormalizes its stem from `s` to
`(s·x)·(y·x)^π` (`e = x·y`), and stem-liveness must not notice. It
does not: `x·(yx)^π·y = (xy)^{π+1} = e`, so `s` and `(s·x)·(y·x)^π`
divide each other on the right — they share a right ideal, and `Live`
is a union of R-classes.

*On the running example.* `stems(P) = {B, C}`, and every class except
`D` reaches one (`[ε]·B = B`, `A·B = C`), so `Live = {[ε], A, B, C}`
and `P̄ = {(A, A), (B, B), (C, B)}`: the safety closure
`cl(L) = a^ω ∪ a*·b^ω` — the added pair `(A, A)` is exactly the limit
word `a^ω` the closure must adjoin. For the interior, *every* class is
live for `P^c` (`stems(P^c) = {A, D}`, and even `B` reaches `D`), so
`P̊ = ∅`: `int(L) = ∅` — no cylinder stays inside `L`, one stray `a`
kills any prefix.

**Corollary 6.2 (interior, safety and co-safety as fixpoints).** The interior (largest open subset) is the dual surgery
`int(L) = ¬cl(¬L)`, with pair set
`P̊ := { (s, e) ∈ linked : s ∉ Live_{P^c} }` — the stems all of whose
continuations stay in `L`. Consequently, on the reduced invariant: `L`
is a safety property iff `P = P̄`; a co-safety property iff `P = P̊`;
clopen iff both. (Saturated pair sets on one table are in bijection
with their languages, so the fixpoint equations are exact tests.)

**Corollary 6.3 (Alpern–Schneider on one table).** With
`Q := P ∪ P̄^c`: `L(P̄)` is a safety property, `L(Q)` is a liveness
property, and `L = L(P̄) ∩ L(Q)`. The intersection is the Boolean
identity `P = P̄ ∩ (P ∪ P̄^c)`, valid because `P ⊆ P̄` (an accepting
pair's stem is its own continuation). Liveness of `L(Q)`: *every*
class is live for `Q` — a `P`-live class reaches an accepting stem of
`P ⊆ Q`; a `P`-dead class `c` has every continuation stem
`(c·x)·e'` dead, so every one of its cells lands in `P̄^c ⊆ Q` — and a
pair set whose classes are all live has hull `linked`, i.e.
`cl(L(Q)) = Σ^ω`. ∎

(On the running example `Q = P ∪ {(D,A), (D,B), (D,D)}` — "either
still on script, or already doomed" — a liveness property whose
intersection with `cl(L)` returns exactly `L`.)

Both factors live on `L`'s own table; one `reduce` each yields their
canonical invariants. Two consequences are worth a line. Since the
factors' algebras divide `M`, the safety closure and the canonical
liveness part of an LTL-definable language are LTL-definable —
aperiodicity survives the split, consistent with the known closure
properties of the safety fragment. And the hull is a closure operator
in the lattice sense on the saturated pair sets of a fixed table
(extensive, monotone, idempotent — idempotence because
`Live_{P̄} = Live_P`), so the closed pair sets form a finite lattice of
fixpoints on the table. (What that lattice generates inside the
classification hierarchy is a diagnosis question — not this paper's.)

The running example closes the section: `a*·b^ω` is not closed — `a^ω`
lies in its closure — and not open — its interior is empty — but it is
`cl(L)` minus the closed set `{a^ω}`: a Boolean combination of the
table's own closed sets, obtained entirely by surgery.

## 7. The ledger against a production toolbox

### 7.1 One row per operation

The table below sets the calculus against an automata toolbox, one row
per everyday entry point, with Spot [DL+16, DL+22] as the reference
implementation of the automata column. The pattern of the columns is the
paper's thesis in miniature: the automata side pays per operation and
returns machines; the calculus side pays at `align` (at worst) and
returns pair sets one `reduce` away from canonical.

| operation | automata (Spot) | on `𝓘(L)` |
|---|---|---|
| complement | `2^{Θ(n log n)}` (Safra/rank/slice [TFVT10]) | `P ↦ P^c`, free |
| union / intersection / difference | product (+ acceptance surgery) | align `O(n₁n₂)` + pointwise `∨/∧/∖` |
| emptiness + witness | SCC scan | `P = ∅?`, key-built minimal lasso |
| universality | complement + emptiness | `P = linked?`, scan |
| inclusion / equivalence | PSPACE / simulations | `Val₁ ≤ Val₂` scan / byte equality |
| lasso membership | run the lasso against the machine | one fold through `λ, M`, one `P` lookup |
| left quotient | derivative construction | rooting `P_c`, free |
| relabel / inverse subst. | rebuild | compose `λ`, free |
| drop unconstrained APs | powerset-flavored `remove_ap` | free-AP read-off + alphabet quotient (§3.2) |
| equality up to AP renaming | isomorphism-flavored search | relabel + reduce + byte compare, canonicity-pruned (§3.2) |
| determinize | Safra/Zielonka | *meaningless* — object already canonical-deterministic; the cost sits at entry |
| degeneralize / to-parity / acc transforms | bespoke constructions | *dissolved* — acceptance is `P`, data not architecture |
| minimize / simulation reductions | heuristic, model-bound (NP-c for DBA [Sch10]) | reduce: the normal form, always, uniquely |
| safety closure / liveness split | closure construction (`cl`) | stem-liveness surgery `P̄`, `O(n²)` (Prop 6.1, Cor 6.3) |
| concatenation `W·L`, `W^ω` | native (nondeterminism) | exponential — intrinsic (§4) |
| projection `remove_ap` | subset-flavored | exponential when constrained (§4); free when the AP is unconstrained (§3.2) |
| automaton → LTL | absent | aperiodicity read-off (§5); extraction beyond this paper |

### 7.2 Cost summary

One line per move; `n` is the class count of the relevant table,
`linked ⊆ 𝒞²` its linked pairs, and costs count table lookups /
`Val` evaluations (each `O(1)` after memoization).

| move / query | cost | output |
|---|---|---|
| entry: construct `𝓘(L)` from `D` | dominated by `\|EM(D)\| ≤ (\|Q\|·2^{\|C\|})^{\|Q\|}` [SωS26, §8] | the invariant |
| align | `O(n₁·n₂·\|Σ\|)` steps, `≤ n₁·n₂` nodes | shared table + two verdict maps |
| Boolean surgeries, rooting | `O(\|linked\|)` | pair set, same table |
| saturation / legality check | `O(\|linked\|·n²)` | pair set (run rarely) |
| inverse substitution | `O(\|Σ'\|)` + reduce | same table, new letter map; reduce before byte-level use |
| lasso membership | `O(\|u\| + \|v\|)` | bit |
| emptiness / universality | `O(n²)` `Val` | bit + minimal lasso |
| inclusion / equivalence / intersection-word | `O(\|nodes\|²)` verdicts on the aligned table | bit + minimal lasso |
| equivalence of reduced objects | byte comparison | bit |
| reduce | `O(n²)` `Val` + `≤ n` rounds × `O(n·\|Σ\|)` | *the* canonical invariant |
| LTL cut (aperiodicity) | `O(n²)` power orbits | bit + witness cycle (§5) |
| free-AP test / drop | `O(\|Σ\|)` / + reduce | bit / smaller-alphabet invariant (§3.2) |
| safety hull / interior / liveness part | `O(n²)` | pair sets, same table (Prop 6.1, Cor 6.2–6.3) |
| `W·L`, `W^ω`, `remove_ap` (constrained) | exponential (exit + re-entry) | §4 |

The entry row is a floor, not an apology: deciding aperiodicity of an
ω-regular language — one read-off among the ones the object supports —
is already PSPACE-complete (hardness from the finite-word case [CH91],
the ω transfer as in [SωS26, §8] via [DG08]), so *some*
exponential must sit somewhere in any substrate this complete; the
calculus sits it at the gate.

### 7.3 Exit constructions

The calculus should end where the consumer needs.

- *To an NBA*: the classical decomposition
  `L = ⋃_{(s,e) ∈ P} X_s·(Y_e)^ω` over accepting pairs [PP04], where
  `X_c = { w : fold(w) = c }` is recognized by the right-Cayley DFA of
  the table (`|𝒞|` states, final state `c`), gives an acceptor
  polynomial in `|𝒞|` — `O(|P|·|𝒞|)` states by the standard stem–loop
  gadget.
- *To a canonical deterministic EL automaton*: the right-Cayley graph
  of the table [SωS26, Def 5.2], completed by an acceptance condition
  derived from `P` — a canonical (not minimal) deterministic acceptor,
  and *counter-free exactly when `L` is LTL-definable*, since the graph
  is the algebra acting on itself. The transformation is implemented —
  the corpus of §8 pairs every invariant with the deterministic EL
  acceptor this exit produces; its adequacy proposition is left as a
  prospect, as in [SωS26].
- *To LTL*: gated by the §5 aperiodicity read-off; formula extraction
  is beyond this paper.
- *To certificates*: the witness and replay formats of §3, always.

### 7.4 What the calculus refuses to simulate

Anything needing branching semantics
(games, synthesis) — the invariant is a linear-time object. And
succinctness: `𝓘(L)` can be exponentially larger than a good
nondeterministic presentation. The honest positioning: the calculus is
not a back-end for one-shot translations; it is the substrate for
pipelines that *keep* a language and work on it.

## 8. Evaluation

The calculus is implemented as a small pure library; every decision
returns a replayable witness object. The corpus behind all measurements
is complement-closed — one canonical invariant per language, each
paired with the deterministic EL acceptor of the §7.3 exit. It grew
during the study: §§8.2–8.4 and §8.6 were measured on its
3938-language edition; the hull comparison of §8.5 on the current
6222-language edition. The two editions are never
mixed inside a comparison, and the 3938-era figures will be regenerated
on the frozen corpus in one sweep before submission. Spot
[DL+16, DL+22] is the automata-side reference throughout; external
calls are budgeted, and a blown budget is reported as a datum, never
waited out.

### 8.1 The soundness harness

Four gates, from unit-level to corpus-wide: (i) *metamorphic replay* —
for every operation, membership in the result equals the corresponding
Boolean combination of memberships in the inputs, checked exhaustively
over all lassos with `|u|, |v| ≤ 3`; (ii) the *saturation law* — every
catalog output is saturated in the sense of Proposition 3.1, asserted
on every harness case; (iii) a *duality gate* — the corpus is
complement-closed, so `reduce(P^c)` must byte-equal the stored
complement on every corpus language; (iv) the *corpus as equality
oracle* — one file per language, so `equivalent` must agree with
filename identity, and every counterexample on a cross-file pair must
replay against both sides. All four are green corpus-wide.

### 8.2 The generated product is affordable (§3.3)

Over 5000 uniformly sampled corpus pairs the realized ratio
`|nodes|/(n₁·n₂)` has median **0.174**, p95 **0.356**, max **0.593** —
81% of products below a quarter of the rectangle, none above 0.6. The
two regimes of §3.3 are both visible: on 1000 language/complement
pairs — related tables — the median falls to **0.063**; on 200 pairs
drawn from the top-decile class counts, where a rectangle could hurt,
the median is **0.119**. Cold BFS median below half a millisecond.

### 8.3 The ledger, measured (§7.1)

Warm medians on held objects: a containment decision **0.0083 ms**,
lasso membership **0.0002 ms**, complement-and-reduce **0.175 ms**.
Honesty note: the automata side is *faster in raw wall-clock* on these
tiny deterministic automata (Spot's `dualize` at 0.0008 ms) — the
inputs are deterministic, so no Safra is ever paid there; the theory
row stands on the nondeterministic bound [TFVT10], and the ledger's
argument is the operation *counts* and the normal-form structure, not
the clock. Normal form and heuristic are never divided: the canonical
intersection (materialize + pointwise `∧` + reduce, 2.4 ms) is a
different product from Spot's raw `product` (0.0018 ms) followed by
heuristic `postprocess` (0.033 ms) — one is byte-comparable and
canonical, the other a presentation. `align` amortizes as §3.3
predicts: at `k = 1 / 5 / 10` decisions on a held product the
per-decision cost is 0.094 / 0.026 / 0.018 ms.

### 8.4 The pipeline (§4)

A four-stage pipeline (`E1 = ¬A`, `E2 = E1 ∩ B`, `E3 = ¬E2`,
`E4 = E3 ∪ A`) over 20 corpus pairs: entering the calculus — building
`𝓘(L)` from the deterministic acceptor — is a one-time **0.43 ms**,
about 15% of the pipeline total; after it, every stage's "did my
rewrite change the language" re-check is a byte comparison at
**0.0001 ms** against Spot's `equivalent_to` at 0.0039 ms — and the
byte compare stays linear in the artifact while the equivalence test
grows with the machines. Inputs being deterministic, the demonstration
isolates the normal-form economy, not the exponential entry the
frontier reserves.

### 8.5 Read-offs against the automata side (§6)

- *Hulls* (Prop 6.1, Cor 6.2–6.3): closure laws (extensive, monotone,
  idempotent), duality `int = ¬cl¬`, and the Alpern–Schneider identity
  replayed corpus-wide; stem-liveness of the hull replays against
  per-state emptiness of the paired deterministic acceptor.
- *The hull fixpoints against Spot*, on the full 6222-language edition:
  safety by Spot's acceptance-trivialization fixpoint
  (`is_safety_automaton`), co-safety by the same test on the dual (the
  inputs are deterministic and complete, so dualizing complements). The
  `P = P̄` / `P = P̊` equations agree with that oracle on
  **6222 / 6222** languages, on both verdicts (1514 positives each,
  equal by complement-closure), with an empty disagreement dossier.
  Timings are reported and not sold: both sides are sub-10-µs on tables
  of median 15 classes; the asymptotics, not the clock, are the claim.

### 8.6 The blow-up, empirically (§4)

The `W·L_n` family of Proposition 4.1, built as acceptors and
re-entered through the gate: `|𝒞(W·L_n)| = 17, 48, 127, 318` for
`n = 2, …, 5`, each above the proved `2^n − 1`, off acceptors of only
`2^n + 1` states — the subset construction resurfacing in the algebra
exactly as the proof predicts. The entry price shows as growth (about
×8–9 per step), not a wall: the largest case completes in 0.36 s.

### 8.7 The running example, mechanically

Every value hand-computed for `a*·b^ω` carries a machine counter-signature:
`reference/calculus/example_gate.md` (gate:
`sosl/tests/calculus/example_gate.py`). The invariant is *not* the one the
calculus builds — it is Spot's determinization of `(¬p) U (G p)`, quotiented to
canonical form; the multiplication table is regenerated from the word model
`{ε, a⁺, b⁺, a⁺b⁺, dead}` rather than transcribed; and the committed `.cat`
sidecar of the corpus row that holds this language (`2state1ap1acc_16898` — the
census catalogues it at the smallest shape that emits it) supplies an
independent cross-check.

The five-class table of §2.3 (keys `ε, a, b, ab, ba`), its six linked pairs and
its `P = {(B,B), (C,B)}` are confirmed cell by cell, as are the two rootings
and the hulls of §6 (`Live = 𝒞 \ {D}`, closure adds exactly `(A,A)`, empty
interior, the Alpern–Schneider factor). The alignment of §3.3 generates 5 nodes of
the possible `5 × 3`, the intersection with `GF a` is empty, `a*·b^ω ⊆ FG ¬a`
holds, and the reverse inclusion is refuted by exactly the predicted minimal
counterexample `ba·b^ω`.

⟨TBD: render the invariant and the aligned product of §3.3 as figures.⟩

## 9. Related work

**Automata toolboxes.** Spot [DL+16, DL+22] is the reference point
throughout §7–§8: a mature, carefully-engineered library in which every
language operation is an automaton construction and every classification
query a construction-plus-test. Notably, Spot already
committed to the most general acceptance (arbitrary Emerson–Lei
conditions over the HOA format [DL+16]), which is the automata-side echo
of this calculus's stance that acceptance is data, not architecture;
the calculus takes the last step and makes it a *set*, closed under the
Boolean algebra. The complementation problem it must solve per
negation has a five-decade literature of its own, surveyed and measured
in [TFVT10]; the absence of a normal form on the automata side is not an
engineering gap but a theorem-shaped obstacle — minimal deterministic
Büchi automata are not unique and are NP-hard to find [Sch10]. The
calculus does not compete with these tools at their own game (one-shot
translation, model checking against a system); it changes the object so
that the game is different.

**Recognition by ω-semigroups.** The algebraic theory the calculus
operates in is classical: ω-semigroups and their linked pairs, the
ω-rational operations, and the conjugacy analysis of pair classes are
the material of Perrin and Pin [PP04]; Wilke's algebras [Wil93] give the
equivalent finite signature, and Maler–Staiger [MS97] the congruence
landscape around Arnold's. What that literature does not do is *operate*:
the algebra recognizes, characterizes, classifies — it is not treated as
a data structure with a surgery catalog and a normal-form move. The
missing precondition was the object itself, constructed [SωS26].

**Canonical automata.** Carton–Michel's unambiguous (prophetic) Büchi
automata [CM03] give a canonical *acceptor* — existence and uniqueness,
of automaton-theoretic rather than operational vocation, and the natural
exit format for §7.3's exit constructions on the non-deterministic side.
The residual structure the rooting surgery internalizes (§3.2) is on the
automata side the subject of the FDFA/family-of-DFAs line
[AF16, ABF18, AF21]: families of right congruences as acceptors,
canonical in their own terms and learnable. The syntactic invariant is
coarser-grained machinery — a two-sided congruence with its
multiplication — and it is exactly the two-sided table that turns
properties into equations (aperiodicity, conjugacy of pairs) that right
congruences cannot phrase.

**Finite-word proxies.** Closest in spirit to "operate on a canonical
object" is the `L_$` construction of Calbrix–Nivat–Podelski [CNP93]: the
regular finite-word language `{u$v : u·v^ω ∈ L}` determines `L`, its
minimal DFA is canonical, and Boolean operations transfer. The calculus
can be read as the algebraic completion of that program: the invariant
also determines `L` and also carries Boolean structure, but additionally
exposes the multiplication — and with it the read-offs (aperiodicity,
the hulls) and the surgeries (rooting, conjugacy-saturated
prolongations) that a DFA over a `$`-alphabet keeps implicit.

Position: none of these lines treats the syntactic object as an
*operational* substrate — a thing one aligns, cuts, and re-normalizes —
with the decision procedures, the certificate discipline, and the
normal-form move packaged as a calculus. That is this paper's claim.

## 10. Conclusion

Recognition is usually consumed as a verdict: the algebra accepts, the
characterization holds, the hierarchy level is such. This paper consumes
it as a calculus. Three moves — align, the only product-priced one;
operate, the free surgery catalog on pair sets; reduce, the normal form
automata never had — carry the everyday toolbox: a Boolean algebra of
languages with complements for free, residuals as an internal action,
decisions as scans that emit minimal certificates, the LTL gate and
the hulls as equations read off the table. The exponentials concentrate where they
are intrinsic — the entry gate, the ω-rational constructors, existential
projection — and the economy is pay-canonicity-once: a pipeline that
keeps a language and works on it pays determinization at the door and
nothing per operation after.

The calculus sits one step above the construction that provides its
object [SωS26]; everything else here is self-contained, and the
object's other prospects — learning it from queries, classifying it,
extracting defining formulas, counting the small universe — are
downstream of the operations this paper fixes. The hulls stay an
operator story: closure, interior, and the Alpern–Schneider split, a
lattice of fixpoint surgeries on one table. The measurements (§8) bear
the economy out: the
alignment ratios, the operation ledger, the pipeline, and the
concatenation blow-up sit where §§3–4 place them.

---

## References

- **[ABF18]** D. Angluin, U. Boker, D. Fisman. *Families of DFAs as
  acceptors of ω-regular languages.* LMCS 14(1), 2018.
- **[AF16]** D. Angluin, D. Fisman. *Learning regular omega languages.*
  TCS 650 (2016) 57–72.
- **[AF21]** D. Angluin, D. Fisman. *Regular ω-languages with an
  informative right congruence.* Inf. Comput. 278 (2021).
- **[Arn85]** A. Arnold. *A syntactic congruence for rational
  ω-languages.* TCS 39 (1985) 333–335.
- **[AS85]** B. Alpern, F. B. Schneider. *Defining liveness.* Inf.
  Process. Lett. 21(4) (1985) 181–185.
- **[CH91]** S. Cho, D. T. Huynh. *Finite-automaton aperiodicity is
  PSPACE-complete.* TCS 88 (1991) 99–116.
- **[CM03]** O. Carton, M. Michel. *Unambiguous Büchi automata.* TCS 297
  (2003) 37–81.
- **[CNP93]** H. Calbrix, M. Nivat, A. Podelski. *Ultimately periodic
  words of rational ω-languages.* MFPS 1993, LNCS 802.
- **[CP97]** O. Carton, D. Perrin. *Chains and superchains for
  ω-rational sets, automata and semigroups.* Int. J. Algebra Comput.
  7(6) (1997) 673–695.
- **[DG08]** V. Diekert, P. Gastin. *First-order definable languages.*
  In *Logic and Automata*, 2008.
- **[DL+16]** A. Duret-Lutz, A. Lewkowicz, A. Fauchille, T. Michaud,
  É. Renault, L. Xu. *Spot 2.0 — a framework for LTL and ω-automata
  manipulation.* ATVA 2016.
- **[DL+22]** A. Duret-Lutz, E. Renault, M. Colange, F. Renkin,
  A. Gbaguidi Aisse, P. Schlehuber-Caissier, T. Medioni, A. Martin,
  J. Dubois, C. Gillard, H. Lauko. *From Spot 2.0 to Spot 2.10: what's
  new?* CAV 2022.
- **[EL87]** E. A. Emerson, C.-L. Lei. *Modalities for model checking:
  branching time logic strikes back.* Sci. Comput. Program. 8 (1987)
  275–306.
- **[MP92]** Z. Manna, A. Pnueli. *The Temporal Logic of Reactive and
  Concurrent Systems: Specification.* Springer, 1992.
- **[MS97]** O. Maler, L. Staiger. *On syntactic congruences for
  ω-languages.* TCS 183 (1997) 93–112.
- **[PP04]** D. Perrin, J.-É. Pin. *Infinite Words: Automata,
  Semigroups, Logic and Games.* Elsevier, 2004.
- **[Saf88]** S. Safra. *On the complexity of ω-automata.* FOCS 1988,
  319–327.
- **[Sch10]** S. Schewe. *Minimisation of deterministic parity and Büchi
  automata and relative minimisation of deterministic finite automata.*
  FSTTCS 2010 / arXiv:1007.1333.
- **[SωS26]** Y. Thierry-Mieg, with Claude (Anthropic). *Constructing
  the syntactic ω-semigroup from a deterministic Emerson–Lei automaton.*
  Working draft, 2026.
- **[TFVT10]** M.-H. Tsai, S. Fogarty, M. Y. Vardi, Y.-K. Tsay. *State
  of Büchi complementation.* CIAA 2010 (full version).
- **[Wil93]** T. Wilke. *An algebraic theory for regular languages of
  finite and infinite words.* Int. J. Algebra Comput. 3(4) (1993)
  447–489.
