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
read-offs. Classification checks that automata libraries implement as
constructions (stutter-invariance, the safety–progress ladder, the
acceptance strength a language actually needs) are equations on the
table; the safety closure, the interior, and the Alpern–Schneider
decomposition are `O(n²)` surgeries whose fixpoints generate exactly the
obligation (Staiger–Wagner) class, with the Wagner degree inside that
band a longest-path read-off. The exponentials do not disappear — they
concentrate, exactly at the ω-rational constructors (concatenation by a
prefix set, ω-power) and existential projection, where a powerset is
intrinsic. The economy is *pay canonicity once*: entering the calculus
costs what determinization always cost; everything downstream is cheap,
normal-formed, and certificate-producing. The calculus is implemented as
a small pure library, its every decision replayable against independent
oracles; measured on a complement-closed corpus of small languages, the
generated product realizes a median 0.17 of its `n₁·n₂` bound, and every
classification read-off agrees with the automata-side construction on
every language of the corpus.

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
query — is this property a safety property, is it stutter-invariant, what
acceptance strength does it really need — is its own bespoke construction
followed by an equivalence check. And every one of these steps returns a
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
3. **Read-offs replacing constructions** (§5–§6): classification
   queries answered by equations on the table, including a one-scan
   stutter-invariance test (Proposition 5.1, with full proof) where the
   automata-side check builds closure automata and tests product
   emptiness; the hulls — safety closure, interior, and the
   Alpern–Schneider decomposition — as `O(n²)` surgeries on the same
   table (Proposition 6.1), turning the ladder's first rungs into
   fixpoint equations; and the theorem that the obligation rung is
   *exactly* the Boolean sublattice the hull fixpoints generate
   (Theorem 6.6), with obligation membership a one-scan read-off and
   the band's Wagner degrees longest-path read-offs
   (Proposition 6.7).
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
frontier; §5 turns the classification battery into read-offs; §6
develops the hulls and the obligation band they generate; §7 draws the
ledger and the cost summary and states what the calculus refuses to
simulate; §8 reports the measurements; §9 positions the work; §10
concludes.

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
ideal. `L` is the left dual, `H = R ∩ L`. The `R`-classes are the
strongly connected components of the **right-Cayley graph** of the table
(nodes `𝒞`, an edge `c → c·λ(a)` per letter [SωS26, Def 5.2]), and
`≥_R` is reachability in it — the geometric reading every scan of §6
exploits. On idempotents we use the natural order:
`f ≤_H e` iff `e·f = f·e = f`.

**The kernel.** Every finite semigroup has a least two-sided ideal `K`,
its *kernel*, and `K` is completely simple: by Rees–Suschkewitsch it is
isomorphic to a matrix semigroup over a group `G` — elements are
triples `(i, g, λ)` (row, group element, column), multiplication is
`(i, g, λ)·(j, h, μ) = (i, g·q_{λj}·h, μ)` with sandwich entries
`q_{λj} ∈ G`, and every subsemigroup of a completely simple semigroup
is completely simple. Lemma 6.4 computes inside one such presentation;
only the multiplication rule is needed.

**Chains and the Wagner coordinates.** Fix a saturated pair set `P` on
the table. A *chain of length `n`* is a linked stem `s` carrying
idempotent loops `e₀ >_H e₁ >_H ⋯ >_H e_n` whose verdicts
`Val_P(s, e_i)` alternate; its *sign* is the first verdict. `m⁺(L)`
(resp. `m⁻(L)`) is the maximal length of a chain of sign 1 (resp. 0),
with the convention `m^b = −1` when no linked pair of verdict `b`
exists at all, and `m(L) = max(m⁺, m⁻)`. A *superchain of length `n`*
is a sequence of chains `C₀, …, C_n` of alternating signs whose stems
are strictly `R`-decreasing and successively accessible
(`s_{i+1} ∈ s_i·𝒞`); `n⁺(L)` / `n⁻(L)` are the maximal lengths of
superchains of first sign 1 / 0. These coordinates, evaluated in the
syntactic ω-semigroup, determine the Wagner degree of `L`
[Wag79, CP97, CP99, SW08]. §6 imports exactly two facts from that
theory: `m(L) = 0` iff `L` is a Boolean combination of open sets
(Wagner's theorem in the Carton–Perrin form [CP99, Thm 6, Cor 7]), and
the superchain normal form [CP97, Thm 7].

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
§3.2, alignment in §3.3, the hulls, the obligation verdict, and the
Wagner degree `(n⁺, n⁻) = (1, 2)` in §6.

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

## 5. Read-offs replace constructions

Spot answers classification queries by building automata and testing
them; on the invariant the same queries are equations on the table. The
first is worked in full, as the pattern for the rest.

**Stutter invariance, one scan.** Two ω-words are *stutter-equivalent*
iff they have the same destuttered normal form, where destuttering
collapses every maximal finite block of equal consecutive letters to one
letter (an eventually-constant word `u·a^ω` has normal form
`destutter(u·a)·a^ω`). `L` is stutter-invariant iff it is a union of
stutter classes.

**Proposition 5.1.** `L` is stutter-invariant iff `λ(a)·λ(a) = λ(a)`
for every letter `a ∈ Σ`.

*Proof.* (⇒) Fix `a ∈ Σ`; we show `a ≈_L a·a` in Arnold's congruence,
whence `λ(a) = λ(a·a) = λ(a)²` since the syntactic morphism is
multiplicative. In the linear shape, for any `x, y ∈ Σ*`, `t ∈ Σ⁺`, the
words `x·a·y·t^ω` and `x·a·a·y·t^ω` differ by duplicating one letter
occurrence, so they destutter identically and stutter invariance gives
them one verdict. In the ω-power shape, for any `x, y ∈ Σ*`,
`x·(a·y)^ω` and `x·(a·a·y)^ω` differ by duplicating one `a` inside each
loop iteration — infinitely many duplications, but destuttering
collapses each `a·a` block the same way in both, so the normal forms
again coincide and stutter invariance again gives one verdict. Both
shapes agree on `a` versus `a·a`, so `a ≈_L a·a`.

(⇐) Suppose every letter class is idempotent. First, on finite words,
`fold(w) = fold(destutter(w))`: collapsing one adjacent equal pair
`…a·a… ↦ …a…` preserves the fold by `λ(a)² = λ(a)` and
multiplicativity; induct on the number of collapses. It suffices to show
that every ω-word `α` has the same verdict as its normal form `β`, since
stutter-equivalent words share their normal form.

*Case 1: `α` eventually constant*, `α = u·a^ω`. Its factorization
`u, a, a, a, …` has all loop blocks folding to the idempotent
`λ(a)`, so by the factoring theorem (§2) the verdict of `α` is
`Val_P(fold(u), λ(a))`, i.e. membership of the linked pair
`(fold(u)·λ(a), λ(a))` in `P`. Now `fold(u)·λ(a) = fold(u·a) =
fold(destutter(u·a))` by the finite-word fact, and the normal form
`β = destutter(u·a)·a^ω` evaluates on the same pair (its stem folds to
`fold(destutter(u·a))`, which already ends in `λ(a)` and is absorbed).
Same cell, same verdict.

*Case 2: letters change infinitely often.* Write the normal form as
`β = b₀b₁b₂⋯` with `b_i ≠ b_{i+1}`; then `α = b₀^{k₀}·b₁^{k₁}·⋯` for
some exponents `k_i ≥ 1`. By Ramsey (§2), `β` admits a factorization
`β = w₀·w₁·w₂·⋯` with `fold(w_j) = e` idempotent for all `j ≥ 1`. Every
cut point of this factorization sits between two *distinct* letters —
`β` is stutter-free — so it marks a block boundary of `α`, and cutting
`α` at those boundaries blows each factor `w_j = b_i⋯b_m` up to
`w_j' = b_i^{k_i}⋯b_m^{k_m}`, whose destuttered form is `w_j` itself
(adjacent letters inside `w_j` differ). By the finite-word fact
`fold(w_j') = fold(w_j)`, so `α = w₀'·w₁'·w₂'·⋯` is a factorization
with the same stem image `fold(w₀)` and the same idempotent block image
`e` as `β`'s, and the strong factoring theorem of §2 gives both words
one verdict. ∎

(On the running example: `A² = A` and `B² = B` — `a*·b^ω` is
stutter-invariant, in two lookups.)

Spot's check [MD15] translates the property *and its negation* to Büchi
automata, applies closure constructions — `cl` (destuttering) and `sl`
("self-loopization", instuttering) — and tests emptiness of products
such as `sl(A) ⊗ sl(Ā)`: two translations, two closures, one product
emptiness. Here it is `|Σ|` table lookups. (The comparison is fair in
one direction only — [MD15] starts from a formula, we start from the
invariant — but in a pipeline that already holds `𝓘(L)`, the marginal
cost of the query is the point.)

The rest of the classification battery follows the same pattern —
a construction on automata, an equation on the table:

- **The safety–progress ladder** (safety, co-safety/guarantee,
  obligation, recurrence, persistence, reactivity): each rung is a
  closure condition on the accepting set `P` over the linked-pair
  structure [SωS26, §7.2; Lan69, MP92, PW13] — Spot's `is_safety`,
  `is_obligation`, … as scans, uniform over one object where the
  automata-side answers are model-specific checks. The first rungs
  become *exact fixpoint tests* once the hulls are in hand — that is
  §6's subject.
- **Acceptance strength needed** (Spot's parity/Rabin-index style
  queries): the acceptance index — the minimal deterministic condition
  the *language* needs — is the maximal alternating chain in the
  algebra, computable in the syntactic ω-semigroup by Carton–Perrin
  [CP97, Cor. 1]; a property of the language, not of a chosen condition.
- **Wagner degree**: the complete classification up to Wadge
  reducibility is fixed by the chain and superchain structure of the
  algebra [CP97, CP99, SW08]; every hierarchy query above specializes
  it.
- **LTL-definability**: the aperiodicity scan on `M` — `L` is
  LTL-definable iff `M` is aperiodic, the classical correspondence
  [DG08] landed on the canonical table, and stable under every surgery
  by Lemma 3.3. Formula extraction is beyond this paper; the read-off
  is its gate. (Spot has no automaton→LTL path.)
- **Hulls.** The safety closure of `L`, its interior, and the
  Alpern–Schneider decomposition `L = safety ∩ liveness` are pair-set
  surgeries on the same table, computable in `O(n²)` — §6 proves it.

## 6. Hulls, and the obligation rung they generate

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

**Corollary 6.2 (interior, and the ladder's first rungs as
fixpoints).** The interior (largest open subset) is the dual surgery
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
fixpoints on the table. The natural next question is whether the
*obligation* rung of the ladder — the Staiger–Wagner class, Boolean
combinations of safety properties — is exactly the Boolean sublattice
those fixpoints generate. It is, and the rest of this section proves
it.

First, the generated sublattice has a concrete description. The closed
pair sets of the table are exactly the sets

```
Q_S := { (s, e) ∈ linked : Reach(s) ∩ S ≠ ∅ },     S ⊆ linked stems,
```

where `Reach(s) := s·𝒞 ∩ (linked stems)` — Proposition 6.1 makes any
hull a `Q_S` (take `S = stems(P)`), and each `Q_S` is its own hull (by
transitivity of reachability). The Boolean subalgebra generated by the
`Q_S` is generated by the singletons `Q_{{t}}`, whose indicator on a
pair `(s, e)` is `[t ∈ Reach(s)]`; its atoms are therefore the fibers
of `(s, e) ↦ Reach(s)`. And `Reach(s) = Reach(s')` iff `s` and `s'`
divide each other on the right — Green's relation `R` (§2.2). So:

> `P` is **hull-generated** iff `Val_P(s, e)` depends only on the
> `R`-class of the stem `s` — in particular, not on the loop at all.

The Wagner-side characterization of obligation is classical: `L` is a
Boolean combination of open (equivalently closed) sets iff its Wagner
degree is finite, iff `m(L) = 0` — no chain of length 1 (§2.2), the
chains living in the syntactic ω-semigroup by the Carton–Perrin
normal form [CP97, Thm 6; Wag79; CP99, Thm 6 and Cor 7; SW08]. Two
lemmas take us from `m = 0` to stem-only verdicts. Throughout, note that if
`(s, e)` and `(s, f)` are linked then `s` absorbs the whole
subsemigroup `⟨e, f⟩` on the right: `s·(any product of e's and f's) = s`,
letter by letter — so every element of `⟨e, f⟩` below is again a loop
of `s`, and every conjugacy move fixes the stem.

**Lemma 6.4 (loops over one stem are connected).** Let `P` be
saturated with `m = 0`. Then `Val_P(s, e) = Val_P(s, f)` for every two
loops `e, f` of a common linked stem `s`.

*Proof.* Fix an idempotent `k` in the kernel (minimal ideal) `K` of
`⟨e, f⟩`, and set `g := (e·k·e)^π`, `g' := (f·k·f)^π`.

*Descent.* From `(eke)·e = ek(ee) = eke = e·(eke)` we get
`(eke)^m·e = (eke)^m = e·(eke)^m` for all `m ≥ 1`, so `g·e = e·g = g`:
`g ≤_H e`. Also `g ∈ K` (`K` is an ideal, closed under powers), and
`(s, g)` is linked by the absorption remark. If `g ≠ e`, the pair
`e >_H g` with differing verdicts would be a chain of length 1, so
`m = 0` forces `Val(s, g) = Val(s, e)`; likewise
`Val(s, g') = Val(s, f)`.

*Conjugacy in the kernel.* `T := ⟨g, g'⟩ ⊆ K` is completely simple: a
subsemigroup of a completely simple semigroup is completely simple
(for `t, u ∈ T`, `tut` lies in the group H-class of `t` in `K`, so
`(tut)^π` is that group's identity and `t = (tut)^π·t ∈ T·u·T`; thus
`T` is simple, and finite simple with idempotents is completely
simple). We exhibit `x, y ∈ T` with `x·y = g` and `y·x = g'`. If
`g R g'` or `g L g'` this is the classical pair of identities
(`g·g' = g'`, `g'·g = g` when `g R g'`; take `x = g'`, `y = g`, giving
`xy = g'g = g` and `yx = gg' = g'`; dually for `L`). Otherwise
normalize `T`'s Rees presentation (§2.2) over its rows `{1, 2}` and columns
`{1, 2}` so that the sandwich entries are
`p₁₁ = p₁₂ = p₂₁ = 1, p₂₂ = γ`, with `g = (1, 1, 1)` and
`g' = (2, γ⁻¹, 2)`. Then `x := g·g' = (1, γ⁻¹, 2)` and
`y := (g'·g)^{ord(γ)} = (2, 1, 1)` are in `T`, and

```
x·y = (1, γ⁻¹·p₂₂·1, 1) = (1, γ⁻¹γ, 1) = g,
y·x = (2, 1·p₁₁·γ⁻¹, 2) = (2, γ⁻¹, 2) = g'.
```

So the loop `g` factors as `x·y` with `y·x = g'`; by Proposition 3.1
the cells `(s, g)` and `(s·x, (y·x)^π) = (s, g')` carry one verdict
(the stem is fixed since `x ∈ ⟨e, f⟩`). Chaining:
`Val(s,e) = Val(s,g) = Val(s,g') = Val(s,f)`. ∎

(The kernel step is where chains alone are powerless: inside a
completely simple semigroup distinct idempotents are `H`-incomparable,
so `m = 0` says nothing there — and indeed `(e·k·e)^π = e` whenever
`e` itself lies in the kernel. It is *saturation* — the conjugacy law
of Proposition 3.1 — that connects the kernel loops. The conjugacy of
`D`-equivalent idempotents is classical; the point of the computation
is that `x, y` can be taken inside `⟨e, f⟩`, which is what keeps the
stem absorbed.)

**Lemma 6.5 (blind verdicts are `R`-invariant).** Let `P` be saturated
and loop-blind (`Val_P(s, e) =: θ(s)` for every loop `e` of `s`). Then
`θ(s) = θ(s')` whenever `s R s'`.

*Proof.* Write `s' = s·x`, `s = s'·y`. Then `E := (xy)^π` is a loop of
`s` and `(yx)^π` a loop of `s'`. Factor `E = X·Y` with
`X = (xy)^π·x`, `Y = y·(xy)^{π−1}`: then `X·Y = (xy)^{2π} = E` and
`Y·X = (yx)^{2π} = (yx)^π`. Proposition 3.1 sends the cell `(s, E)` to
`((s·X)·(yx)^π, (yx)^π) = (s', (yx)^π)`, so
`θ(s) = Val(s, E) = Val(s', (yx)^π) = θ(s')`. ∎

**Theorem 6.6 (the obligation rung is hull-generated).** For an
ω-regular `L` with syntactic invariant `(𝒞, λ, M, P)`, the following
are equivalent:

1. `L` is an obligation (Staiger–Wagner) property — a Boolean
   combination of safety properties;
2. `m(L) = 0`: no linked stem carries two `H`-comparable loops with
   different verdicts;
3. `Val_P(s, e)` depends only on the stem `s` — equivalently, only on
   the `R`-class of `s`;
4. `P` belongs to the Boolean sublattice of saturated pair sets
   generated by the closed pair sets of the table.

*Proof.* (1)⟺(2) is Wagner's theorem in the Carton–Perrin form: the
Boolean closure of the open ω-rational sets is exactly the finite
Wagner degrees, i.e. `m(X) = 0` [Wag79; CP99, Thm 6, Cor 7; SW08],
with chains transported to the syntactic ω-semigroup by [CP97, Thm 6].
(2)⟹(3): Lemma 6.4 gives stem-only; Lemma 6.5 upgrades stem-only to
`R`-class-only (saturation alone). (3)⟹(4): a loop-blind, `R`-constant
`P` is a union of the atoms of the generated subalgebra, by the
description above. (4)⟹(1): each `Q_S` is a safety language
(Proposition 6.1), and Boolean combinations of safety properties are
obligations by definition. ∎

Three consequences. **A read-off**: obligation membership — Spot's
`is_obligation`, answered there through weak-automaton realizability
constructions — is one scan: bucket the linked pairs by stem, check
each bucket is constant, check constancy across each `R`-class (the
strongly connected components of the right-Cayley graph):
`O(|linked| + n·|Σ|)`. **A normal form**: an obligation language is a
Boolean combination of the *canonical* closed sets `Q_{{t}}` of its
own table — no foreign safety constituents are ever needed. **A
boundary**: the lattice of hulls captures the safety-shaped hierarchy
*exactly up to* obligation; from the next rungs on (recurrence,
persistence and above), verdicts are provably loop-sensitive
(`m ≥ 1`), so no Boolean combination of fixpoints can express them —
the hull story is complete, not truncated. And the fine structure
*inside* the band comes for free — Wagner's superchain coordinates
`n±`, which stratify the obligation class by its difference level
`D_n(Σ₁)` and side `σ/π/δ` [Wag79, CP99], transcribe exactly to the
`θ`-labeled DAG:

**Proposition 6.7 (the Wagner degree of an obligation language, on
the DAG).** Let `m(L) = 0` and let `θ` be the stem verdict of
Theorem 6.6. For a polarity `b ∈ {0, 1}`, let `alt_b` be the maximal
`n` for which there exist linked stems
`s₀ ≥_R s₁ ≥_R ⋯ ≥_R s_n` (each `s_{i+1} ∈ s_i·𝒞`) with
`θ(s₀) = b` and `θ(s_i) ≠ θ(s_{i+1})` for all `i`. Then
`n⁺(L) = alt₁` and `n⁻(L) = alt₀`: the superchain coordinates are the
longest alternating paths in the `θ`-labeled `R`-class DAG, computable
in `O(n·|Σ|)` after the SCC pass of Theorem 6.6 (condense, then one
dynamic-programming sweep in reverse topological order per polarity).

*Proof.* (≤) By the superchain normal form [CP97, Thm 7], any
`X`-superchain of length `n` can be brought to chains
`C'_i = (s_i, E_i)` with every pair linked and the stems *strictly*
`R`-decreasing; with `m(L) = 0` each chain is a single linked pair,
the alternation of the chains' signs is alternation of
`Val(s_i, e_i) = θ(s_i)` (Theorem 3.10(3)), and a strictly
`R`-decreasing stem sequence is a path in the DAG of the required
shape. (≥) Conversely, an alternating path yields a superchain
directly: take `C_i = ({s_i}, (e_i))` for any loop `e_i` of `s_i` — a
chain of the required maximal length `0`, of sign `θ(s_i)`;
accessibility needs a nonempty word class `u_i` with
`s_i·u_i = s_{i+1}`, which exists
because `s_{i+1} ∈ s_i·𝒞` while `s_i R s_{i+1}` is impossible —
`R`-equivalent stems share `θ` (Lemma 6.5) and `θ` alternates. ∎

The running example closes its arc here. Every linked stem carries
loops of one verdict — `θ(A) = 0`, `θ(B) = θ(C) = 1`, `θ(D) = 0`,
buckets constant, `R`-classes singletons — so `a*·b^ω` *is* an
obligation (it is not closed: `a^ω` lies in its closure; not open:
its interior is empty; but it is `cl(L)` minus the closed set
`{a^ω}`). The `θ`-labeled DAG carries the alternating paths
`A → C → D` (`0, 1, 0`) and `C → D` (`1, 0`), so
`(n⁺, n⁻) = (1, 2)` — exactly the values computed by chain-juggling
in [CP97, Ex. 10], here a two-edge longest-path read-off.

## 4. The ledger against a production toolbox

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
| determinize | Safra/Zielonka | *meaningless* — object already canonical-deterministic; the cost sits at entry |
| degeneralize / to-parity / acc transforms | bespoke constructions | *dissolved* — acceptance is `P`; the needed strength is a read-off |
| minimize / simulation reductions | heuristic, model-bound (NP-c for DBA [Sch10]) | reduce: the normal form, always, uniquely |
| stutter-invariance | `cl`/`sl` closures + product emptiness [MD15] | `λ(a)² = λ(a)` scan (Prop 3.3) |
| safety/obligation/… tests | model-specific checks | safety/co-safety: `P = P̄` / `P = P̊` (Cor 3.6); obligation: stem-only verdict scan (Thm 3.10) |
| safety closure / liveness split | closure construction (`cl`) | stem-liveness surgery `P̄`, `O(n²)` (Prop 3.5, Cor 3.7) |
| acceptance index / Rabin index | condition transforms + tests | alternating-chain read-off [CP97] |
| concatenation `W·L`, `W^ω` | native (nondeterminism) | exponential — intrinsic (§3.4) |
| projection `remove_ap` | subset-flavored | exponential — the QPTL wall (§3.4) |
| automaton → LTL | absent | [SωSX26] on the aperiodic side |

**Exit constructions.** The calculus should end where the consumer
needs. To an NBA: the classical decomposition
`L = ⋃_{(s,e) ∈ P} X_s·(Y_e)^ω` over accepting pairs [PP04], where
`X_c = { w : fold(w) = c }` is recognized by the right-Cayley DFA of the
table (`|𝒞|` states, final state `c`), gives an acceptor polynomial in
`|𝒞|` — `O(|P|·|𝒞|)` states by the standard stem–loop gadget. To LTL:
via [SωSX26] when the table is aperiodic. To certificates: the
witness/replay formats of [SωSX26, §4], always.

**What cannot be simulated.** Anything needing branching semantics
(games, synthesis) — the invariant is a linear-time object. And
succinctness: `𝓘(L)` can be exponentially larger than a good
nondeterministic presentation; the census [SωSN26] measures how often
canonicity actually costs. The honest positioning: the calculus is not a
back-end for one-shot translations; it is the substrate for pipelines
that *keep* a language and work on it.

**Implementation.** The calculus is implemented as a small pure library
(the companion specification `sos_calculus_spec.md` fixes the package,
the algorithms, and the milestones; align/operate/reduce and the full
catalog above are in place). Every decision returns a replayable witness
object; the soundness harness's deepest gates are (i) *metamorphic
replay* — for every operation, membership in the result equals the
corresponding Boolean combination of memberships in the inputs, checked
exhaustively over all lassos with `|u|, |v| ≤ 3`; (ii) the *saturation
law* — every catalog output is saturated in the sense of Proposition
3.1, asserted on every harness case; (iii) a *duality gate* — the census
corpus is complement-closed, so `reduce(P^c)` must byte-equal the stored
complement on every corpus language; and (iv) the *corpus as equality
oracle* — the canonical corpus holds one file per language, so
`equivalent` must agree with filename identity, and every counterexample
on a cross-file pair must replay against both sides. Run against Spot
over the census, the ledger's rows come out as the table predicts, and
the stutter-invariance read-off agrees with the automata-side check on
every one of the census languages, with no disagreement — 648 of them
stutter-invariant, better than a quarter of the LTL-definable class.
The hull fragment of §3.6 is under the same discipline: the safety
closure replays as prefix-liveness against each language's
deterministic acceptor, and the obligation read-off and the band's
degree (Theorem 3.10, Proposition 3.11) agree, on every census
language, with the Wagner coordinates computed independently by the
census's chain and superchain engines — the calculus reading off in
one SCC pass what the classification side establishes by chain
juggling.

## 5. Complexity summary

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
| stutter-invariance | `O(\|Σ\|)` | bit (Prop 3.3) |
| safety hull / interior / liveness part | `O(n²)` | pair sets, same table (Prop 3.5, Cor 3.6–3.7) |
| obligation test | `O(\|linked\| + n·\|Σ\|)` | bit (Thm 3.10: stem-only verdict) |
| Wagner degree within the obligation band | `O(n·\|Σ\|)` after SCCs | `(n⁺, n⁻)` = longest alternating DAG paths (Prop 3.11) |
| ladder / index / Wagner read-offs | polynomial scans of the table | verdicts [SωS26, §7.2] |
| `W·L`, `W^ω`, `remove_ap` | exponential (exit + re-entry) | §3.4 |

The entry row is not an apology but a floor: deciding aperiodicity of an
ω-regular language — one read-off among the ones the object supports —
is already PSPACE-complete (hardness from the finite-word case [CH91],
the ω transfer as in [SωS26, §8] via [DG08]), so *some*
exponential must sit somewhere in any substrate this complete. The
calculus's design choice is to sit it at the gate, once, rather than
inside every operation.

## 6. Related work

**Automata toolboxes.** Spot [DL+16, DL+22] is the reference point
throughout §4: a mature, carefully-engineered library in which every
language operation is an automaton construction and every classification
query a construction-plus-test — the stutter-invariance battery of
[MD15] being the type specimen of the latter. Notably, Spot already
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
exit format for §4's exit constructions on the non-deterministic side.
The residual structure the rooting surgery internalizes (§3.2) is on the
automata side the subject of the FDFA/family-of-DFAs line
[AF16, ABF18, AF21]: families of right congruences as acceptors,
canonical in their own terms and learnable. The syntactic invariant is
coarser-grained machinery — a two-sided congruence with its
multiplication — and it is exactly the two-sided table that turns
classifications into equations (idempotency of letter classes, conjugacy
of pairs) that right congruences cannot phrase.

**Finite-word proxies.** Closest in spirit to "operate on a canonical
object" is the `L_$` construction of Calbrix–Nivat–Podelski [CNP93]: the
regular finite-word language `{u$v : u·v^ω ∈ L}` determines `L`, its
minimal DFA is canonical, and Boolean operations transfer. The calculus
can be read as the algebraic completion of that program: the invariant
also determines `L` and also carries Boolean structure, but additionally
exposes the multiplication — and with it the read-offs (aperiodicity,
the ladder, the index, the Wagner degree) and the surgeries (rooting,
conjugacy-saturated prolongations) that a DFA over a `$`-alphabet keeps
implicit.

**Hierarchy computations on the algebra.** That the Wagner hierarchy is
computable in the syntactic ω-semigroup is Carton–Perrin [CP97, CP99],
completed by Selivanov–Wagner's complexity analysis [SW08]; Landweber's
ladder [Lan69] and its effective characterizations on canonical automata
[PW13] are the automata-side counterparts. §3.5 claims none of these
results — it claims their *placement*: on one shared table, as scans
among other scans, downstream of one entry price.

Position: none of these lines treats the syntactic object as an
*operational* substrate — a thing one aligns, cuts, and re-normalizes —
with the decision procedures, the certificate discipline, and the
normal-form move packaged as a calculus. That is this paper's claim.

## 7. Conclusion

Recognition is usually consumed as a verdict: the algebra accepts, the
characterization holds, the hierarchy level is such. This paper consumes
it as a calculus. Three moves — align, the only product-priced one;
operate, the free surgery catalog on pair sets; reduce, the normal form
automata never had — carry the everyday toolbox: a Boolean algebra of
languages with complements for free, residuals as an internal action,
decisions as scans that emit minimal certificates, classifications as
equations read off the table. The exponentials concentrate where they
are intrinsic — the entry gate, the ω-rational constructors, existential
projection — and the economy is pay-canonicity-once: a pipeline that
keeps a language and works on it pays determinization at the door and
nothing per operation after.

The calculus is the operational face of a program whose other faces are
already drafted: [SωS26] builds the object, [SωSL26] learns it (and its
teacher consumes this paper's minimal counterexamples), [SωSX26] is its
most elaborate derived operation, and the census [SωSN26] counts the
universe it operates on. The hull section closed its own follow-ups:
the safety-shaped hierarchy lives on one table as a lattice of
fixpoints, it generates *exactly* the obligation class (Theorem 3.10),
and the Wagner degrees inside that band are longest alternating paths
on the `θ`-labeled `R`-class DAG (Proposition 3.11) — beyond the band,
loop-sensitivity is intrinsic and the general Wagner read-off takes
over. The measurements bear the economy out: the alignment ratios, the
operation ledger, the pipeline, and the concatenation blow-up sit where
§3 places them.

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
- **[CP99]** O. Carton, D. Perrin. *The Wagner hierarchy.* Int. J.
  Algebra Comput. 9(5) (1999) 597–620.
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
- **[Lan69]** L. H. Landweber. *Decision problems for ω-automata.* Math.
  Systems Theory 3(4) (1969) 376–384.
- **[MD15]** T. Michaud, A. Duret-Lutz. *Practical stutter-invariance
  checks for ω-regular languages.* SPIN 2015.
- **[MP92]** Z. Manna, A. Pnueli. *The Temporal Logic of Reactive and
  Concurrent Systems: Specification.* Springer, 1992.
- **[MS97]** O. Maler, L. Staiger. *On syntactic congruences for
  ω-languages.* TCS 183 (1997) 93–112.
- **[PP04]** D. Perrin, J.-É. Pin. *Infinite Words: Automata,
  Semigroups, Logic and Games.* Elsevier, 2004.
- **[PW13]** S. Preugschat, T. Wilke. *Effective characterizations of
  simple fragments of temporal logic using Carton–Michel automata.* LMCS
  9(2:08) (2013).
- **[Saf88]** S. Safra. *On the complexity of ω-automata.* FOCS 1988,
  319–327.
- **[Sch10]** S. Schewe. *Minimisation of deterministic parity and Büchi
  automata and relative minimisation of deterministic finite automata.*
  FSTTCS 2010 / arXiv:1007.1333.
- **[SW08]** V. Selivanov, K. W. Wagner. *Complexity of topological
  properties of regular ω-languages.* Fund. Inform. 83(1–2) (2008).
- **[SωS26]** Y. Thierry-Mieg, with Claude (Anthropic). *Constructing
  the syntactic ω-semigroup from a deterministic Emerson–Lei automaton.*
  Working draft, 2026.
- **[SωSL26]** Y. Thierry-Mieg, with Claude (Anthropic). *Learning the
  syntactic ω-semigroup.* Working draft, 2026.
- **[SωSN26]** Y. Thierry-Mieg, with Claude (Anthropic). *A census of
  syntactic ω-semigroups.* Working draft, 2026.
- **[SωSX26]** Y. Thierry-Mieg, with Claude (Anthropic). *The LTL
  frontier from the syntactic ω-semigroup: certificates, formulas, and
  the shape of the cut.* Working draft, 2026.
- **[TFVT10]** M.-H. Tsai, S. Fogarty, M. Y. Vardi, Y.-K. Tsay. *State
  of Büchi complementation.* CIAA 2010 (full version).
- **[Wag79]** K. Wagner. *On ω-regular sets.* Information and Control
  43 (1979) 123–177.
- **[Wil93]** T. Wilke. *An algebraic theory for regular languages of
  finite and infinite words.* Int. J. Algebra Comput. 3(4) (1993)
  447–489.
