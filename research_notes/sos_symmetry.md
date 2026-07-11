# Symmetries on the Syntactic ω-Semigroup: Read-offs, Reductions, and the Group Spectrum

**Yann Thierry-Mieg**

With significant inputs from
**Claude (Anthropic)**

*Working draft — 2026-07-11. Every unproven leap is flagged ⟨TBD⟩.*

## Abstract

Is a specification invariant under exchanging two processes? Under
swapping a request with its grant? Under commuting two independent
actions? Model checkers *consume* the answers — symmetry reduction and
partial-order reduction are sound only when they hold — yet no tool
*computes* them: each is a language-equivalence question,
PSPACE-complete per candidate at the formula level, so tools
substitute syntactic checks on the formula that are sound,
incomplete, and silent on failure. We show
that on the canonical syntactic invariant `𝓘(L)` of an ω-regular
language, the whole family collapses to inspections of one small
table: alphabet symmetries are automorphisms of the invariant (a
stabilizer search, with exact verdicts and, on failure, a minimal
witness lasso locating the asymmetry); closure under factor
rewritings — stutter invariance, letter invisibility, and the maximal
independence relation the specification tolerates — is a system of
table equations; and the groups hidden *inside* the invariant form a
canonical *group spectrum* that refines the LTL-definability frontier
and yields canonical LTL upper and lower approximations
`L♭ ⊆ L ⊆ L♯` confining the counting content of `L` to the gap
between them. Everything except two explicitly priced closure
operations is a read-off.

---

## 1. Introduction

### 1.1 The problem: three kinds of symmetry

Let `L ⊆ Σ^ω` be an ω-regular language — a linear-time
specification. Three families of questions about the *symmetries* of
`L` arise in verification practice, and they are related but
distinct:

1. **Outer symmetries.** Which bijections `σ : Σ → Σ`, extended
   letterwise to infinite words, fix the language: `σ(L) = L`? Over
   an alphabet of valuations `Σ = 2^AP` the natural candidates are
   *signed permutations* — permute atomic propositions, flip
   polarities. These are the symmetries **symmetry reduction**
   consumes [ES96, CEFJ96, ID96]: quotienting the *system* by a group
   `G` is sound only if the *specification* is `G`-invariant.
2. **Relation invariances.** Under which factor rewritings `u ↔ v`
   is membership preserved? Stutter invariance (`a ↔ aa`) is the
   known instance; commutations (`ab ↔ ba`) are the spec-side
   condition **partial-order reduction** consumes [Pel93, God96].
3. **Inner symmetries.** What groups live *inside* the recognizing
   algebra of `L`? These are not symmetries of `L` as a set of words;
   they are symmetries of its *behavior* — the hidden counters — and
   they measure exactly how far `L` is from LTL-definability
   [Tho79, DG08].

Every instance of kinds 1 and 2 is a language-equivalence question —
PSPACE-complete per candidate from a formula, and still a
per-candidate product-and-equivalence construction on deterministic
automata — and it is absent from the standard toolbox: symmetry is
not an invariant of a presentation, so no automaton you hold
exhibits it. Kind 3 is invisible on automata
altogether. The state of the art in tools is syntactic checking on
the *formula* (when there is one), which is sound, incomplete, tied
to how the property happened to be written, and produces nothing
usable when it fails.

### 1.2 The title terms, and why the syntactic ω-semigroup

The **syntactic ω-semigroup** of `L` (Arnold [Arn85], Perrin–Pin
[PP04]) is the canonical minimal algebra recognizing `L` — the
ω-analogue of the syntactic monoid. Following [SωS26] we work with
its finite presentation, the *invariant* `𝓘(L) = (𝒞, λ, M, P)`:
canonically keyed classes `𝒞`, letter map `λ`, multiplication table
`M`, accepting linked pairs `P`. Its completeness theorem — two
languages are equal iff their canonically keyed invariants are
byte-equal — is read by the calculus [CAL26] as an API: `𝓘(L)` *is*
the language, operations are surgeries on the table, equivalence is
byte comparison.

A **read-off** is a question answered by inspecting `𝓘(L)` — a table
lookup, a per-generator pass, a byte comparison — with no
construction, no product, no language-theoretic query. A
**reduction** (in the title) is the model-checking consumer: symmetry
reduction and partial-order reduction, whose soundness premises are
exactly the questions of §1.1. The **group spectrum** is the set of
simple groups dividing `𝒞` — the canonical measure of the counting
content of `L`, defined in §6.

The economics that make this work: canonicity turns "is
`σ(L) = L`?" into one free surgery (an inverse substitution, [CAL26]
§3.2) plus one canonical keying pass, then byte equality. On the
census corpus [SωSN26] the invariants have at most a few hundred
classes; a stabilizer search over such a table is trivial. The
PSPACE question was never asked of the right object.

### 1.3 Contributions

- **Theorem 3.1** (symmetry = automorphism): `σ(L) = L` iff `σ`
  lifts to an automorphism of `(𝒞, M, P)` over the letter map, iff a
  one-pass byte check succeeds; with the two-level fiber structure
  (a kernel of "free" symmetries the invariant has already quotiented
  away), the signed extension to polarity flips, and anti-symmetries
  (`σ(L) = L^c`) at the same price (§3.2).
- **The asymmetry witness** (§3.3): on failure, a minimal lasso in
  `L Δ σ(L)` — the actionable artifact syntactic checks cannot
  produce — and **symmetrization** (§3.4), the largest `G`-invariant
  strengthening / smallest weakening, honestly priced by the orbit
  of `L`, not the order of `G`.
- **Theorem 4.2** (block-substitution principle): `L` is closed
  under the factor rewriting `u ↔ v` iff `[u] = [v]` in `𝒞` — any
  finite rewriting system becomes a conjunction of table equations.
  Instances: invisible letters, stutter invariance (recovering the
  read-off of [CAL26] §3.5), a `k`-block ladder, and **Theorem 4.4**:
  the *maximal independence relation the specification tolerates*,
  `Î_L = {(a,b) : [ab] = [ba]}` — the exact spec-side input of
  partial-order reduction, computed in `O(|Σ_λ|²)` lookups.
- **Theorem 5.1** (equivariant extraction): symmetric languages
  receive symmetric canonical formulas from the ToLTL extraction
  [ToLTL26], and extraction can run per orbit of layers — free DAG
  compression.
- **The group spectrum** (§6): read off the maximal subgroups the
  definability machinery [SωSX26] already walks; empty iff `L` is
  LTL; conjecturally solvable iff LTL+modular-counting. **Proposition
  6.2**: the aperiodic reflection of the invariant yields canonical
  LTL approximations `L♭ ⊆ L ⊆ L♯` (the *LTL kernel and hull*), with
  the counting content of `L` confined to the gap `L♯ ∖ L♭`.
- **Workflows and measurements** (§7, §9): the exact
  symmetry-reduction premise check with witness/repair; the
  independence certificate for POR; aperiodic screening for non-LTL
  properties; and **Proposition 7.4**, the *symmetric envelope* —
  enveloping both the specification (§3.4) and the system by any
  group `G`, sound fully-quotiented proof and refutation checks that
  assume no symmetry of either, turning the subgroup lattice into an
  abstraction lattice with exact, witness-carrying refinement. Three
  cheap census columns and a deduplication axis.

Everything above except symmetrization (§3.4) — whose price the
envelope of §7.4 inherits — and the quotient frontier (§7.2) is a
read-off or a per-generator keying pass.

### 1.4 Outline

§2 collects the background objects — nothing there is original. §3–§6
develop the three kinds of symmetry (outer, relational, inner), each
notion defined before use; three hand-worked examples (Examples A–C,
§3) and one worked non-LTL specimen (`EvenHead`, §6.2) thread the
sections and are restated as machine-checkable predictions in §9. §7
assembles the model-checking workflows. §8 discusses related work; §9
concludes with the measurement plan for the census [SωSN26].

## 2. Preliminaries

Nothing in this section is original; we fix notation and recall the
facts we lean on, with pointers.

### 2.1 ω-languages and ultimately periodic words

`Σ` is a finite alphabet, `Σ^ω` the infinite words, `L ⊆ Σ^ω`
ω-regular throughout. An *ultimately periodic* word is `u·v^ω` with
`u, v` finite, `v` nonempty; ω-regular languages are determined by
their ultimately periodic members. A *lasso* is a presentation of
such a word.

### 2.2 ω-semigroups, linked pairs, factorization-independence

An ω-semigroup [PP04] recognizes `L` through a morphism from
`(Σ⁺, Σ^ω)`. A *linked pair* is `(s, e)` with `s·e = s`,
`e·e = e`. Ramsey's theorem gives every `α ∈ Σ^ω` a factorization
`α = u·v₁·v₂⋯` whose blocks map to a single idempotent `e` with
prefix class `s`; the pair `(s, e)` is the *induced* pair. The fact
we lean on throughout §4: **recognition is
factorization-independent** — the verdict of `α` depends only on the
sequence of classes of *any* factorization of `α` into finite blocks
[PP04].

### 2.3 The syntactic invariant and canonicity

Arnold's congruence [Arn85, §2]: `w ∼_L w'` iff for all finite
`u, v₁, v₂`, `u·(v₁ w v₂)^ω ∈ L ⟺ u·(v₁ w' v₂)^ω ∈ L` and
`v₁ w v₂ · u^ω ∈ L ⟺ v₁ w' v₂ · u^ω ∈ L`; it is the largest
congruence recognizing `L` [Arn85, Thm 2.3]. In proofs we use the
equivalent *context form*: for all finite `x, y` and all
`β ∈ Σ^ω`, `x·w·y·β ∈ L ⟺ x·w'·y·β ∈ L` and
`x·(w·y)^ω ∈ L ⟺ x·(w'·y)^ω ∈ L`. (Equivalence for ω-regular `L`:
the context form refines Arnold's — his two clauses are the
instances `β := u^ω` and `x := u·v₁, y := v₂·v₁`; conversely, given
`x·w·y·β ∈ L`, Ramsey-factorize the word over `∼_L` and use that
`x·w·y·β₀ ∼_L x·w'·y·β₀` with saturation — the syntactic congruence
recognizes, hence saturates, `L` [Arn85, Lem. 2.2] — to move the
arbitrary tail.) The quotient is the syntactic ω-semigroup, the
minimal recognizer. [SωS26] computes and canonically
keys its finite presentation `𝓘(L) = (𝒞, λ, M, P)`: `𝒞` a keyed
class set generated by `λ(Σ)`, `M` the multiplication table, `P` the
accepting linked pairs. Membership of an ultimately periodic word is
a fold and a lookup; **two ω-regular languages are equal iff their
canonically keyed invariants are byte-equal** [SωS26, Thm 5.1]. We
write `Σ_λ` for the quotient alphabet `λ(Σ)` and call `λ⁻¹(c)` a
*`λ`-fiber*.

### 2.4 The calculus: surgeries and prices

From [CAL26] we use five operations, with their price tags:

- **inverse substitution** (free): rewire `λ` along a letter map;
- **reduce** (cheap): re-quotient to syntactic + canonical keying;
- **complement** (free): flip `P` within the linked pairs;
- **align** (the only product-priced move): a generated product of
  two invariants, enabling Boolean combinations;
- **scan** (cheap on an aligned product): produce a minimal witness
  lasso in a difference language.

"Read-off" ([CAL26] §3.5) means: answered on `𝓘(L)` by lookups and
byte comparisons alone, none of the above needed beyond at most one
reduce.

### 2.5 Alphabets of valuations; signed permutations

In verification `Σ = 2^AP` for a set `AP` of atomic propositions;
letters are *minterms* (total valuations). The *hyperoctahedral
group* `B_AP` of **signed permutations** — permute `AP`, flip
polarities of individual propositions — acts on `Σ` through the cube
structure; it is the meaningful candidate group for specification
symmetries (process permutations, request/grant dualities), not the
full `Sym(Σ)`.

### 2.6 Aperiodicity, LTL, and group divisors

A finite semigroup is *aperiodic* iff it contains no nontrivial
group. For ω-regular `L`: `𝒞` aperiodic ⟺ `L` is first-order
definable ⟺ `L` is LTL-definable (FO ⟺ star-free on ω-words is
[Tho79, Thm 2.1]; the full chain through aperiodicity and LTL is
surveyed in [DG08]); [SωSX26] implements this frontier on the
invariant, with counting-family certificates on refusal. A group
*divides* a semigroup if it is a quotient of a subsemigroup; the
maximal subgroups of `𝒞` are its group `H`-classes at idempotents.
Krohn–Rhodes theory supplies: the simple groups dividing a finite
semigroup are exactly the Jordan–Hölder factors of its maximal
subgroups — stated (as "elementary group theory") inside the proof
of [KR65, Cor. 3.2(b)], where `PRIMES(S)` is computed from the
maximal subgroups. On finite words, solvable monoids correspond to
`FO+MOD` definability ([Str94, Thm VII.2.1]; the
Straubing–Thérien–Thomas line).

## 3. Outer symmetries

### 3.1 Symmetry = automorphism

Fix a bijection `σ : Σ → Σ`, extended letterwise to `Σ^ω`.

**Theorem 3.1.** The following are equivalent:

(i) `σ(L) = L`;

(ii) there is an automorphism `ρ` of `(𝒞, M)` with `ρ ∘ λ = λ ∘ σ`
and `ρ(P) = P` (componentwise on pairs);

(iii) the canonical keying of `(𝒞, λ∘σ, M, P)` is byte-equal to
`𝓘(L)`.

When it exists, `ρ` is unique, and `σ ↦ ρ_σ` is a group homomorphism
`Sym(L) → Aut(𝒞, M, P)` whose kernel is
`K = { σ : λ∘σ = λ }` — the permutations moving letters only within
`λ`-fibers.

*Proof.* (ii ⟹ i): `ρ` preserves products, idempotents, hence linked
pairs. For any `α` with Ramsey factorization inducing `(s, e)`, the
same cut positions factorize `σ(α)` with letter classes
`λ(σ(a)) = ρ(λ(a))`, inducing `(ρs, ρe)`; by
factorization-independence (§2.2) and `ρ(P) = P`,
`σ(α) ∈ L ⟺ α ∈ L`, and bijectivity gives `σ(L) = L`.

(i ⟹ ii): define `ρ[u] := [σ(u)]`. Well-defined: if `u ∼_L v`, then
for every context, `x·σ(u)·y·β ∈ L ⟺ σ(σ⁻¹x · u · σ⁻¹y · σ⁻¹β) ∈ L
⟺ σ⁻¹x · u · σ⁻¹y · σ⁻¹β ∈ L` (using `σL = L`), likewise for `v` and
for the ω-power contexts of Arnold's congruence (§2.3) — so
`σ(u) ∼_L σ(v)`. Multiplicativity and bijectivity (inverse from
`σ⁻¹`) are immediate; `ρ∘λ = λ∘σ` by construction on generators;
`ρ(P) ⊆ P` because `(s, e) ∈ P` is witnessed by `u·v^ω ∈ L` with
`[u] = s, [v] = e`, and `σ(u·v^ω) = σ(u)·σ(v)^ω ∈ σ(L) = L`; the
same argument for `σ⁻¹` gives `ρ⁻¹(P) ⊆ P`, hence `ρ(P) = P`.

(i ⟺ iii): `(𝒞, λ∘σ, M, P)` is the *syntactic* invariant of
`σ⁻¹(L)` — contexts transport through the bijection, so
`u ∼_{σ⁻¹L} v ⟺ σ(u) ∼_L σ(v)`, no re-quotient occurs, and reduce
is keying only. Byte equality is language equality [SωS26, Thm 5.1],
and `σ⁻¹(L) = L ⟺ σ(L) = L`; the cycle closes through (i).

Uniqueness: `λ(Σ)` generates `𝒞`, and `ρ` is determined on
generators. The kernel computation is immediate. ∎

**The two-level fiber structure.** `K` is a product of symmetric
groups on the `λ`-fibers and is *always* contained in `Sym(L)` — a
`σ` with `λ∘σ = λ` satisfies (iii) with the tuple literally
unchanged; the invariant has already quotiented these symmetries
away. The semantic
content of `Sym(L)` is its image in `Aut(𝒞, M, P)`, a permutation
action on the quotient alphabet `Σ_λ`. Precisely: `σ ∈ Sym(L)` iff
`ρ_σ` restricted to `λ(Σ)` permutes the fibers *respecting fiber
cardinalities*, so

```
Sym(L)  =  preimage of  { ρ ∈ Aut(𝒞, M, P) : ρ permutes λ(Σ), |λ⁻¹(c)| = |λ⁻¹(ρc)| }.
```

**Example A (an inert atomic proposition — the kernel).**
`L_A = GF a` over `AP = {a, b}`. By hand:
`𝒞 = {1, F, N}` with `F` = [contains an `a`-letter] (absorbing:
`xF = Fx = F`), `N` = [contains none] (idempotent); `λ` sends the two
`a`-minterms to `F` and the two `¬a`-minterms to `N`; three linked
pairs, `P = {(F, F)}`. This configuration arises routinely whenever
a property constrains only some of the propositions in its
interface. The fibers are fat, and the polarity flip `σ_b`
satisfies `λ∘σ_b = λ`: it lies in the kernel `K`, and its symmetry is
visible *without any search* — a pure read-off on `λ`. Semantically,
`b` is redundant in `L_A` (existentially quantifying it does not
change the language) even though it may appear syntactically in every
guard of an automaton presentation. Automaton-level detection
requires a product-with-complement test per proposition; on the
invariant it is one pass over the fibers. This is the degenerate but
practically common bottom of the theory: symmetries the invariant has
already paid for. (Predicted verdicts over `B_2`: symmetric
`{id, σ_b}`, no anti-symmetry, `inert = {b}` — §9, P2.)

**Example B (a semantic symmetry — beyond the kernel).**
`L_B = GF a ∧ GF b` over `AP = {a, b}`. By hand: `𝒞 = {1, A, B, C, N}`
— `[ε]` plus the four (seen an `a`-letter?, seen a `b`-letter?) flag
classes `A = (1,0)`, `B = (0,1)`, `C = (1,1)`, `N = (0,0)`;
multiplication is componentwise OR; `λ` is *injective* on the four
minterms (`ab ↦ C`, `a¬b ↦ A`, `¬ab ↦ B`, `¬a¬b ↦ N`), so the kernel
`K` is trivial; `P = {(C, C)}`. The swap `a ↔ b` induces
`ρ = (A B)` fixing `1, C, N`, an automorphism with `ρ(P) = P`: a
symmetry living genuinely in `Aut(𝒞, M, P)`. The flip `σ_a` forces
`ρ(A) = N, ρ(N) = A, ρ(B) = C, ρ(C) = B` (read off `λ∘σ_a`), which
already fails multiplicativity — `ρ(A·B) = ρ(C) = B` but
`ρ(A)·ρ(B) = N·C = C` — so most non-symmetries die on a table cell,
before any keying pass. (Predicted over `B_2`: symmetric
`{id, swap}`, no anti-symmetry, `inert = ∅` — §9, P2.)

**Cost.** A single check (iii) is one keying pass. The full group is
the stabilizer above: a backtracking search over candidate generator
images constrained by `M` — graph-isomorphism-flavored, and trivial
at invariant sizes (`|𝒞| ≤ 121` on the census). No language-theoretic
query occurs anywhere. Contrast automata: `Sym` is not an invariant
of a presentation, and each candidate `σ` costs an equivalence
check.

### 3.2 The signed group, and anti-symmetries

Over `Σ = 2^AP` (§2.5) the meaningful group is `B_AP`. Define
`Sym_AP(L) := Sym(L) ∩ B_AP`, computed by the same stabilizer search
restricted to cube-respecting candidates; per generator (a
transposition `a ↔ b` or a flip `a ↔ ¬a`) the check is one keying
pass, so a candidate group `G` given by generators is checked in
`|generators|` passes.

**Anti-symmetries** cost the same: `σ(L) = L^c` iff there is `ρ` as
in Theorem 3.1(ii) with `ρ(P) = P^c` (complement within the linked
pairs — one flip, §2.4), iff the keying of `(𝒞, λ∘σ, M, P)`
byte-equals `𝓘(L^c)`. Define the *signed symmetry group*
`Sym±(L) ≤ B_AP × Z/2` recording both; self-dual specifications
(`L^c = σ(L)`) are common in practice (request/grant dualities) and
currently invisible to tools.

**The pair-count obstruction.** Any `ρ` witnessing an anti-symmetry
is a bijection of the linked pairs carrying `P` onto its complement,
so `L` admits an anti-symmetry only if `|P| = |linked| − |P|` —
exactly half the linked pairs accept. One integer comparison refutes
*all* anti-candidates at once, before any keying pass. On Example B,
`|P| = 1` against nine linked pairs: no anti-symmetry, decided by
counting alone.

**Example C (an anti-symmetry).** `L_C = a·Σ^ω` ("a at the first
instant") over `AP = {a}`. By hand: `𝒞 = {1, T, R}` with `T` = [first
letter `a`], `R` = [first letter `¬a`]; multiplication is left
projection (`x·y = x` on nonempty classes), every nonempty class
idempotent; linked pairs `{(T,T), (T,R), (R,T), (R,R)}`;
`P = {(T,T), (T,R)}` — note `|P| = 2 = |linked|/2`, the obstruction
is satisfied. The flip `σ_a` induces `ρ = (T R)`, and
`ρ(P) = {(R,R), (R,T)} = P^c`: an anti-symmetry (`σ_a(L_C) = L_C^c`,
as it should — flipping the first letter exchanges the language with
its complement). Predicted over `B_1`: symmetric `{id}`, anti
`{σ_a}` (§9, P2).

### 3.3 The asymmetry witness

When a check fails the calculus does not stop at "no": align `𝓘(L)`
with `𝓘(σL)` (one generated product, §2.4) and scan the symmetric
difference for its minimal lasso — a concrete ultimately periodic
behavior `u·v^ω ∈ L Δ σ(L)`, i.e. a run the specification treats
differently from its `σ`-image. For the model-checking use (§7.1)
this is the actionable artifact: it points at the exact
process-index asymmetry in the spec, the way a counterexample points
at a bug. Syntactic symmetry checks on formulas — the state of the
art in symmetry-reduction tools — are sound, incomplete, and produce
nothing on failure.

### 3.4 Symmetrization

For a target group `G` (given by generators) and an asymmetric `L`,
the largest `G`-invariant strengthening is `⋂_{g∈G} g(L)` and the
smallest `G`-invariant weakening is `⋃_{g∈G} g(L)`. Both are computed
by a fixpoint of align+operate+reduce over the generators; the
fixpoint is reached in at most `|orbit_G(L)|` alignments, since every
intermediate is an intersection (union) of orbit elements. The orbit
is `1` when `L` is symmetric (the check), small when `L` is nearly
symmetric (the repair use case: "here is the symmetric core you may
have meant"), and can reach `|G|` in the worst case — this is the
honest price tag, and it is an orbit price, not a group-order price.

## 4. Relation invariances

### 4.1 The block-substitution principle

**Definition 4.1.** For finite nonempty words `u, v`, say `L` is
`(u ↔ v)`-closed if membership is preserved under replacing any
family of pairwise disjoint factor occurrences of `u` by `v` (and
conversely) — finitely or infinitely many at once.

**Theorem 4.2.** `L` is `(u ↔ v)`-closed iff `[u] = [v]` in `𝒞`.

*Proof.* (⟸) Let `α` be rewritten to `α′` by replacing a (possibly
infinite) disjoint family of `u`-occurrences by `v`. Factorize `α`
into blocks so that each replaced occurrence is one block: the block
class sequences of `α` and `α′` agree (`[u] = [v]`, other blocks
unchanged). Membership depends only on the block class sequence
(§2.2), so `α ∈ L ⟺ α′ ∈ L`.

(⟹) Single replacements in word contexts give
`x·u·y·β ∈ L ⟺ x·v·y·β ∈ L` for all `x, y, β`; the periodic infinite
replacement gives `x·(u·y)^ω ∈ L ⟺ x·(v·y)^ω ∈ L` for all `x, y`.
These are exactly the two clauses of the context form of Arnold's
congruence (§2.3), so `u ∼_L v`, i.e. `[u] = [v]`. ∎

The theorem turns *any* finite rewriting system into a conjunction of
table equations — a read-off in the sense of §2.4. The instances form
a ladder:

### 4.2 Instances

**Invisible letters** (`[c] = 1`, the unit): `L` is closed under
arbitrary insertion and deletion of `c` — padding letters, detected
by one table lookup per letter. (Deletion is the `(c ↔ cc)`-closure
argument run backwards plus `(xc ↔ x)`; directly: `[c] = 1` makes the
block sequence with and without the `c`-blocks identical.
⟨TBD: state the deletion case as a one-line corollary — deletion
changes the block *count*, so use the sequence-with-units
normalization.⟩)

**Stutter invariance** (`∀a: [a] = [aa]`): the known read-off,
implemented and census-validated in [CAL26] §3.5; Theorem 4.2 gives
it as the special case `u = a, v = aa` with the infinite-family
clause covering the `(ab)^ω ∼ (aabb)^ω`-style equivalences that
finite rewriting alone does not reach. ⟨TBD: confirm the equivalence
of Definition 4.1's closure with Peled–Wilke stutter equivalence
[PW97] in full — the destuttering direction with unboundedly growing
block repetitions; expected to follow from the same block-sequence
argument applied to the destuttered normal form.⟩

**The `k`-block ladder** (`[v] = [vv]` for all `|v| ≤ k`): stutter
invariance at the level of length-`≤k` blocks; `k = 1` is stutter.
Each rung is `|Σ_λ|^k` table equations (`[v]` depends only on the
letter classes of `v`, so the quotient alphabet suffices). Where a language enters the
ladder is a new canonical parameter, plausibly interacting with the
window width of the (B)-ladder in [ToLTL26] ⟨TBD: any formal
relation; both are "bounded-block" parameters but of different
type⟩.

**Commutations** — the payoff instance, next.

### 4.3 The independence relation a specification tolerates

**Definition 4.3.** `Î_L := { (a, b) ∈ Σ² : [ab] = [ba] }` — the
*tolerated independence relation* of `L`.

**Theorem 4.4.** `Î_L` is the largest irreflexive-symmetric relation
`I` such that `L` is closed under swapping any disjoint family of
adjacent `ab → ba` occurrences with `(a,b) ∈ I`. It is computed by
`O(|Σ_λ|²)` table lookups.

*Proof.* Closure under a mixed disjoint family of swaps over `I` is
the block argument of Theorem 4.2 verbatim: each swapped block
`ab ↦ ba` keeps its class when `[ab] = [ba]`, so the block class
sequence is unchanged. Maximality: for `(a, b) ∉ Î_L`, already the
single-pair closure fails by Theorem 4.2 (⟹) with `u = ab`,
`v = ba`. Since `[ab]` depends only on `(λ(a), λ(b))`, `Î_L` is a
union of `λ`-fiber rectangles: compute it on `Σ_λ` and lift through
the fibers. ∎

On the running examples: Example B's table is componentwise OR —
commutative — so `Î` is *total*: the specification tolerates every
adjacent swap (GF-properties are trace-closed, and the table knows
it). Example C's table is left projection, so `[xy] = [x] ≠ [y] =
[yx]` for distinct letter classes: `Î = ∅` — a first-instant property
tolerates no commuting at all. Both are two-lookup verdicts (§9, P4).

This is the specification-side condition of partial-order reduction,
computed exactly. Today a POR engine either requires the property to
be stutter-invariant and action-invisible, or checks syntactic
"visibility" of actions in the formula — both are approximations of
`Î_L`. Handing the engine the true maximal relation enlarges the
ample/stubborn sets it may legally use; conversely, if the system's
independence relation `I_M` is *not* contained in `Î_L`, the pair
`(a, b) ∈ I_M ∖ Î_L` plus a minimal distinguishing lasso (the §3.3
scan on `L` vs its swap image ⟨TBD: the swap image of `L` under a
single-pair rewriting is not an inverse substitution — construct it
as an aligned product with the 2-state swap transducer; check this
stays within the aligned fragment of [CAL26] §3.3⟩) certifies
exactly why the reduction is unsound.

Two honest caveats. First, full ω-trace equivalence (infinite traces,
Diekert–Muscholl ⟨TBD: precise citation and statement⟩) is coarser
than the disjoint-swap closure of Theorem 4.4: an infinite trace
rearrangement may displace a letter unboundedly. Whether
`Î_L`-closure under disjoint swaps implies closure under full
ω-trace equivalence for recognizable `L` is a known-territory
question to settle before claiming the POR theorem at citation
weight ⟨TBD: check Diekert–Gastin–Petit on recognizable ω-trace
languages; the expected answer is yes for `I`-diamond-closed
languages⟩. Second, integration with a concrete POR
(ample-set conditions C0–C3) is tool work, out of scope here; what
the invariant contributes is the exact spec-side relation and its
certificates.

**From heuristic to read-off.** The translator suite behind
[ToLTL26] includes a leaf strategy that searches, heuristically, for
a *determining alphabet* on an SCC of an automaton presentation (the
project note `stutterquotient.md`). On the invariant the analogous
split is canonical: the don't-care letters of a layer are its
neutral letters (the `St`-structure of [ToLTL26] §4.2), and the
global padding letters are the `[c] = 1` read-off — the search
becomes a read-off, per layer, with no presentation in sight.

## 5. Equivariant extraction

This section presupposes the extraction pipeline of [ToLTL26];
terms not defined here — layers, the R-order, `An/St`, windows,
configuration machines, conditions (A)/(B)/(C) — are its.

**Theorem 5.1 (⟨TBD: verify the renderer clause⟩).** Let `σ(L) = L`.
Then every canonical construction from `𝓘(L)` commutes with `σ`; in
particular the ToLTL extraction of [ToLTL26] satisfies
`extract(σL) = σ(extract(L))` up to the atom renaming induced by
`σ`, *provided* the `λ`-preimage Boolean synthesis renders
letter sets equivariantly.

*Proof sketch.* Presentation-insensitivity [SωS26, Thm 5.1] makes
every stage of the extraction a function of `(𝒞, M, P)` plus the
letter map; `ρ_σ` (Theorem 3.1) is an isomorphism of that data over
the relabeling `σ`, so each stage's output transports. The one
non-algebraic step is rendering a set of letters as a Boolean
formula over `AP`: if the renderer's tie-breaking uses a fixed `AP`
order, equivariance holds only up to `σ`'s action on that order —
normalize by choosing the order canonically per `Sym_AP(L)`-orbit.
⟨TBD: make this precise and check the in-repo renderer; this is the
only obstruction.⟩ ∎

Consequences. (i) A symmetric specification automatically receives a
symmetric formula — a feature no DG-style extractor offers (their
separator choices break symmetry silently). (ii) `Aut(𝒞, M, P)` acts
on layers, the R-order, `An/St`, windows and configuration machines;
conditions (A)/(B)/(C) of [ToLTL26] are `Aut`-invariant, so decision
and transcription can run *per layer-orbit*, emitting one `Ω` per
orbit and substituting renamed atoms for the rest — free DAG
compression, measurable on the census (§9). (iii) For the calculus,
`Sym±(L)` is itself canonical metadata: it survives every free
surgery that commutes with the group and can be maintained
incrementally along a pipeline ⟨TBD: which surgeries preserve which
subgroups — complement preserves `Sym`, swaps `Sym±`-components;
quotients may enlarge⟩.

## 6. Inner symmetries: the group spectrum

### 6.1 The spectrum

The maximal subgroups of `𝒞` (§2.6) are exhibited by the
definability machinery [SωSX26] — they are what the counting
certificates are built from. Define the **group spectrum** `Spec(L)`
as the set of simple groups dividing `𝒞`; equivalently (§2.6,
[KR65, Cor. 3.2(b)]) the union of the composition factors of the
maximal subgroups. `Spec` is canonical, computed by
standard group algorithms on groups of table size, and:

- `Spec(L) = ∅` ⟺ `𝒞` aperiodic ⟺ `L` is LTL-definable — the
  frontier of [SωSX26], recovered as the bottom of the spectrum.
- `Spec(L)` solvable (indeed within `{Z/p}`) should correspond to
  definability in LTL extended with modular counting, transposing
  the finite-word correspondence between solvable monoids and
  `FO+MOD` (§2.6, [Str94, Thm VII.2.1] — which is moreover stated
  per prime set `𝒱`, matching the spectrum refinement below) to the
  ω-setting ⟨TBD: the ω-transposition —
  expected to follow the same route as the aperiodic case through
  [PP04]'s wreath machinery; find or prove the exact statement⟩.

The certificate upgrade is the point: a NOT_LTL verdict currently
says "not LTL, here is a counting family". With the spectrum it says
*which counting repairs it*: a language with `Spec = {Z/2}` is
LTL+`MOD₂` (the worked example of §6.2); one with `Spec = {Z/3}`
needs ternary counting; a nonabelian simple divisor would place the
language outside every `FO+MOD` extension. The definability oracle
already walks these groups — the spectrum comes at no extra cost
(§9).

### 6.2 The LTL hull and kernel

The pseudovariety of aperiodic monoids is closed under finite
subdirect products, so among the congruences of `𝒞` with aperiodic
quotient there is a least one, `θ_ap` (the *aperiodic reflection* of
the table) ⟨TBD: spell out the ω-sort — `θ_ap` must be a congruence
of the ω-semigroup, i.e. compatible with the pair structure; take
the least monoid congruence with aperiodic quotient and check it
lifts, or generate the lift explicitly⟩. Let `q : 𝒞 → 𝒞/θ_ap` and
define two saturations of `P`:

```
P♯ = q⁻¹(q(P))        (pairs whose θ-class meets P)
P♭ = { p : q⁻¹(q(p)) ⊆ P }   (pairs whose whole θ-class is in P)
```

**Proposition 6.2 (LTL hull and kernel).** The invariants
`(𝒞/θ_ap, q∘λ, M/θ_ap, q(P♯))` and `(…, q(P♭))` recognize languages
`L♯ ⊇ L ⊇ L♭` that are LTL-definable, canonical, and optimal among
the `θ_ap`-saturated approximations: `L♯` is the least superset and
`L♭` the greatest subset of `L` recognized through the aperiodic
reflection of `L`'s own algebra.

*Proof sketch.* Recognition through an aperiodic ω-semigroup gives
FO- hence LTL-definability ([Tho79]-line, [DG08]); optimality is the
definition of saturation; canonicity is inherited from `𝓘` and the
uniqueness of `θ_ap`. ⟨TBD: full proof, and the reduce implementation
— `θ_ap` is computable as the reflexive-transitive closure of
collapsing each maximal subgroup to its idempotent, iterated to a
congruence; verify this generates `θ_ap` exactly, not merely an
aperiodic congruence.⟩ ∎

The *gap* `L♯ ∖ L♭` is where the group content is essential: on the
gap, and only there, `L` is decided by counting.

**Worked example (`EvenHead`).** `L = { a^{2n}·b^ω : n ≥ 0 }` over
`AP = {a}`, writing `b := ¬a`. By hand, seven syntactic classes:

```
1 = [ε]           A₁ = [a^odd]        A₀ = [a^even, ≥2]
B  = [b^m]        C₀ = [a^even b^m]   C₁ = [a^odd b^m]   (m ≥ 1)
D  = [dead: an a after a b]
```

(`B ≠ C₀`: the context `x = b` separates them — `b·b·b^ω ∈ L` but
`b·a²b·b^ω ∉ L`.) The unique nontrivial maximal subgroup is
`{A₀, A₁} ≅ Z/2` at the idempotent `A₀`, so `Spec(L) = {Z/2}`: not
LTL, repairable by `MOD₂`. The accepting pairs are
`P = {(B, B), (C₀, B)}`. Collapsing `A₀ ∼ A₁` and closing to a
congruence forces `C₀ ∼ C₁` and nothing else: the reflection has
**five** classes `{1, A, B, C, D}` and is aperiodic in one round.
Saturating `P`:

```
P♯ = {(B,B), (C₀,B), (C₁,B)}   →   L♯ = a^*·b^ω     (hull: drop the parity)
P♭ = {(B,B)}                   →   L♭ = {b^ω}       (kernel: only the parity-free member)
```

Both are LTL, concretely: `L♯ ≡ FG¬a ∧ G(¬a → G¬a)` and
`L♭ ≡ G¬a`. The gap `L♯ ∖ L♭ = a^+·b^ω` is exactly the region where
membership in `L` *is* the parity of the head — Proposition 6.2's
"counting content confined to the gap", exhibited. The counting
witness family `a^n·b^ω` of [SωSX26] lives inside the gap for every
`n ≥ 1`, by construction. All of the above is a machine-checkable
prediction (§9, P5) ⟨TBD: verify the witness family lands in the gap
on the census's non-LTL specimens generally, beyond this specimen⟩.

### 6.3 A remark on the two enemies

The determinacy analysis of [BLS-C26] (§C.4) found exactly two
mechanisms by which equal recurrence data can split a verdict:
*group cancellation* (parity-style specimens such as `EvenHead`) and
*zero absorption* (collapse into an absorbing class). The spectrum
maps the first census-wide; the sandwich scan of [BLS-C26]
classifies both. A language with empty spectrum can still be hard
for bounded-recurrence conditions — absorption is aperiodic — but it
is at least LTL; a language with nonempty spectrum is not LTL at
all, and §6.2 confines the damage. Cancellation (a group) and
absorption (a zero) sit at the two ends of Green's `J`-order — the
divisibility order of the table — and both are read off the same
table.

## 7. Model checking as calculus, with symmetries

### 7.1 The symmetry-reduction workflow

Classical symmetry reduction quotients the *system* by a group
`G ≤ B_AP` (process permutations, typically); soundness requires the
*specification* to be `G`-invariant [ES96, CEFJ96, ID96]. The
invariant-side workflow:

1. Per generator `g` of `G`: check `g(L) = L` (one keying pass,
   §3.1–3.2). Exact, unlike the syntactic formula checks in tools.
2. On failure: emit the asymmetry witness (§3.3) — a lasso in
   `L Δ g(L)` — and offer the symmetrized core (§3.4) as the repair.
3. On success: model-check the quotient structure `M/G` against `L`
   as usual; the spec side is discharged *semantically*.

Everything in steps 1–2 is new capability at negligible cost; step 3
is the classical method, now resting on an exact premise. And failure
of step 1 no longer ends the story: the symmetric envelope (§7.4)
keeps the quotient usable, soundly, for asymmetric specifications.

### 7.2 Quotient specifications: the priced frontier

The dual move — expressing a `G`-invariant `L` over the orbit
alphabet `Σ/G` (counter abstraction's specification side) — is an
existential projection, which the calculus prices at the
exponential frontier ([CAL26] §3.4). Conjecture: for `G`-invariant
`L` the projection's blow-up collapses — the `ρ_G`-fixed subtable of
`𝒞` should control the orbit language's invariant ⟨TBD: false in
general or true on a band? Start with the obligation band, where
verdicts are stem-R-class functions and the fixed-point analysis is
finite-word; even a band-restricted theorem is useful, since counter
abstraction targets are usually safety/obligation⟩.

### 7.3 Aperiodic screening

Proposition 6.2 gives a sound two-sided LTL screen for verifying
`M ⊨ L` when `L` is not LTL: if every run of `M` satisfies `L♭`,
then `M ⊨ L`; if some run violates `L♯`, that run is a genuine
counterexample. Both checks are LTL model checking (any off-the-shelf
engine); only runs landing in the gap `L♯ ∖ L♭` — the counting core —
need the counting machinery (an automaton with the group product, or
the certificate replay of [SωSX26]). The screen is canonical: it
depends on `L` alone, not on how the property was written.

### 7.4 The symmetric envelope: sound quotient checking without symmetry

Classical symmetry reduction treats the group as a *hypothesis*: `G`
must be a symmetry of the system, and the specification must be
`G`-invariant, or the method is off. The two symmetrizations of §3.4
remove the hypothesis on the specification side; symmetrizing the
system removes it on the other. Fix **any** `G ≤ B_AP` — chosen for
engine convenience, with no symmetry assumption on `M` or `L` — and
form the four `G`-invariant envelopes (the spec pair by §3.4; the
system pair trace-wise, `g(M)` denoting the `g`-relabeled system):

```
L∩ = ⋂_{g∈G} g(L)  ⊆  L  ⊆  ⋃_{g∈G} g(L) = L∪
M∩ = ⋂_{g∈G} g(M)  ⊆  M  ⊆  ⋃_{g∈G} g(M) = M∪
```

**Proposition 7.4 (the symmetric envelope).** For every `G ≤ B_AP`:

(i) *(proof)* if `M∪/G ⊨ L∩` then `M ⊨ L`;

(ii) *(refutation)* if some run of `M∩/G` violates `L∪`, its lift is
a genuine counterexample to `M ⊨ L`;

and both checks are fully quotiented: all four envelope objects are
`G`-invariant by construction, so the classical quotient theorems
[ES96, CEFJ96] apply to them unconditionally. Soundness never uses
symmetry of `M` or `L`; symmetry only controls the width of the two
gaps `L∪ ∖ L∩` and `M∪ ∖ M∩` — i.e. the *completeness*, not the
soundness, of the method.

*Proof sketch.* (i) `M ⊆ M∪` (traces) and `L∩ ⊆ L`, so
`M∪ ⊨ L∩ ⟹ M ⊨ L`. The quotient step needs both premises of the
classical theorem, and the construction supplies both: `M∪` is
closed under `G`, so `G` acts on it by automorphisms, and `L∩` is
`G`-invariant. (ii) mirror: `M∩ ⊆ M` and `L ⊆ L∪`, so a run of
`M∩/G` violating `L∪`, lifted through the quotient (legal for the
same two reasons), is a run of `M` outside `L`. ∎

The engine economics split unevenly: `M∪` is *cheap* — the union of
the `g`-relabeled transition relations over the generators' closure,
on the same state space; `M∩` is *priced* — trace intersection needs
a product over the orbit, and in practice the refutation side runs
on `M` directly against `L∪` instead (still sound: the run is a
genuine run of `M`, and `L ⊆ L∪` makes its violation genuine too;
only the system side then forgoes the quotient). On the invariant side, `L∩`/`L∪`
carry the §3.4 orbit price and come out as canonical invariants with
all read-offs available — including their own `Sym`, which now
contains `G` by construction.

**The subgroup lattice as an abstraction lattice.** Shrinking `G`
tightens all four envelopes monotonically; `G = 1` is the exact
problem. This is abstraction refinement with an *exact* refinement
signal: an inconclusive gap run, replayed through the §3.3 witness
machinery, names the generator `g` whose asymmetry (`g(L) ≠ L`,
witnessed by a lasso) caused the loss — drop `g` from `G` (refine),
or repair the specification toward its symmetric core (§3.4). The
engine can walk down a subgroup chain adaptively, spending orbit
price on the spec side only where the state-space payoff on the
system side warrants it — the spec side quotes the price
(`|orbit_G(L)|`) *before* any state-space work. The system-side
realization (orbit canonization over a hierarchical symbolic
representation, adaptive `G` selection against the hierarchy) is
engine work, out of scope here; what the invariant contributes is
that every object the engine needs on the specification side is
exact, canonical, priced in advance, and witness-carrying.

⟨TBD: relate to the partial-symmetry line — Emerson–Trefler's
virtual/near symmetry — once fetched and read; the system-side
over-approximation by symmetrizing the transition relation is
folklore-adjacent there, but the two-sided envelope with an exact,
priced spec side appears new.⟩

## 8. Related work

Symmetry reduction in model checking: Emerson–Sistla [ES96],
Clarke–Enders–Filkorn–Jha [CEFJ96], Ip–Dill [ID96]. The spec-side
check is syntactic on the formula in [ES96] (automorphisms of the
formula, their §2.6) and [CEFJ96] (invariance of the atomic
propositions, hence of the formula); [ID96] instead *guarantees*
symmetry by a type discipline on the system description (scalarsets)
— none of the three computes the semantic symmetry group of the
specification. Partial order reduction: Peled [Pel93], Godefroid
[God96]; the spec-side conditions are stutter-invariance (next-free
LTL) plus visible/invisible-operation approximations. Partial and
near symmetry on the system side: Emerson–Trefler ⟨TBD: fetch and
read — the §7.4 envelope's system half should be positioned against
virtual symmetry⟩.
Stutter invariance on ω-words: Peled–Wilke [PW97], Etessami [Ete00];
the algebraic read-off is [CAL26] §3.5. Trace theory for the
independence semantics: Mazurkiewicz traces, infinite traces
Diekert–Muscholl ⟨TBD: fetch precise refs⟩. Modular counting and
solvable monoids: Straubing [Str94], Straubing–Thérien–Thomas ⟨TBD:
fetch; and the ω-analogues⟩. Krohn–Rhodes [KR65] for the
group-divisor facts. The syntactic ω-semigroup line: [Arn85],
[PP04], and the project's [SωS26, SωSL26, SωSX26, SωSN26, CAL26,
ToLTL26].

⟨TBD: a genuine literature pass on "automorphisms of syntactic
monoids/semigroups" — the finite-word statement of Theorem 3.1 is
surely folklore; find who states it, and whether anyone computes
`Sym(L)` as a language operation. The ω-version and the calculus
framing appear new.⟩

## 9. Conclusion and measurement plan

On the canonical invariant, the symmetry questions verification
consumes stop being PSPACE queries and become inspections: outer
symmetry is a stabilizer search with exact verdicts and witness
lassos (§3), relational invariance is a system of table equations
culminating in the exact independence relation POR needs (§4), and
the inner groups yield a canonical spectrum refining the LTL frontier
together with LTL approximations that confine the counting content to
a gap (§6). The two operations that are *not* read-offs —
symmetrization and quotienting — carry explicit, orbit-shaped price
tags (§3.4, §7.2). The message of the paper is the economics:
symmetry was never expensive; it was asked of the wrong object.

**Measurement plan.** Three columns and one axis, all cheap, for the
census [SωSN26]:

- **`Sym±(L)`** per language (stabilizer search §3.1–3.2): expect
  large kernels `K` (fat `λ`-fibers) and small semantic groups;
  interesting outliers are the self-dual and fully symmetric
  specimens. Deduplicating the corpus by `B_AP`-orbit (it is closed
  under complement only today) shrinks it and sharpens the
  "exhaustive below the wall" claim.
- **`Spec(L)`** over the 1 698 non-LTL languages: expected
  overwhelmingly `{Z/2}`; any nonabelian or non-solvable specimen is
  a find. Cross-tabulate with the Wagner degree (the
  topological-complexity coordinate the census records per
  language).
- **Hull/kernel gap**: `|𝒞/θ_ap|` vs `|𝒞|`, and the gap languages'
  invariant sizes; verify the counting witnesses land in the gap.
- **Orbit-folded extraction** (Theorem 5.1(ii)): DAG size with and
  without orbit folding on the symmetric specimens.
- **Envelope width** (§7.4): on the nearly-symmetric specimens
  (those where a single generator fails), the size of
  `𝓘(L∪ ∖ L∩)` relative to `𝓘(L)` and the orbit count actually
  paid — the datum that decides whether the symmetric envelope is a
  practical screen or a theoretical remark.

**Machine-checkable predictions (the worked examples, restated).**
Each is a hand computation above; a mismatch convicts either the
construction pipeline or this paper's arithmetic — both outcomes are
findings.

- **P1 — invariant sizes.** `|𝒞(L_A)| = 3` (Example A, `GFa` over 2
  APs), `|𝒞(L_B)| = 5` (Example B, `GFa ∧ GFb`), `|𝒞(L_C)| = 3`
  (Example C, `a·Σ^ω`), `|𝒞(EvenHead)| = 7`.
- **P2 — symmetry truth tables.** Over the full signed group:
  Example A `{id, σ_b}` / no anti / `inert = {b}`; Example B
  `{id, swap}` / no anti / `inert = ∅`; Example C `{id}` / anti
  `{σ_a}`; `EvenHead` `{id}` / no anti.
- **P3 — the pair-count obstruction.** Example C satisfies
  `2|P| = |linked|` (2 of 4); Examples A (1 of 3) and B (1 of 9) are
  refuted for anti-symmetry by the count alone.
- **P4 — independence relations.** `Î` total on Example B, empty on
  Example C.
- **P5 — `EvenHead` inner data.** `Spec = {Z/2}`; the aperiodic
  reflection has 5 classes, reached in one collapse round; the hull
  and kernel invariants are byte-equal to the canonized invariants of
  `FG¬a ∧ G(¬a → G¬a)` and `G¬a` respectively; `a^n·b^ω` is in the
  gap for `1 ≤ n ≤ 6` (bounded check), and membership in `L` on the
  gap alternates with the parity of `n`.

Engineering is commissioned in the companion spec
`sos_symmetry_spec.md` (milestones SY1–SY5, campaign ids Y0–Y2); the
predictions above are its fixture gates, and results return through
`sos_symmetry_report.md`. The census tooling covers all five
measurements without new infrastructure beyond the stabilizer search
and the symmetrization fixpoint.

## References (tags used; full list on landing)

Verified-in-library entries carry their `papers/` filename; we do
not cite what we have not read.

- **[Arn85]** A. Arnold. *A syntactic congruence for rational
  ω-languages.* Theoretical Computer Science 39, pp. 333–335 (1985).
  (`Arnold_1985_TCS`)
- **[CAL26]** Y. Thierry-Mieg, with Claude (Anthropic). *A Calculus
  on the Syntactic ω-Semigroup: Align, Operate, Reduce.* Working
  draft, 2026 (`sos_calculus.md`).
- **[CEFJ96]** E. M. Clarke, R. Enders, T. Filkorn, S. Jha.
  *Exploiting symmetry in temporal logic model checking.* Formal
  Methods in System Design 9(1/2), pp. 77–104 (1996).
  (`Clarke_Enders_Filkorn_Jha_1996_FMSD`)
- **[DG08]** V. Diekert, P. Gastin. *First-order definable
  languages.* In *Logic and Automata*, 2008.
  (`Diekert_Gastin_2008`)
- **[ES96]** E. A. Emerson, A. P. Sistla. *Symmetry and model
  checking.* Formal Methods in System Design 9(1/2), pp. 105–131
  (1996). (`Emerson_Sistla_1996_FMSD`, the Nov. 1994 TR version)
- **[Ete00]** K. Etessami. *A note on a question of Peled and Wilke
  regarding stutter-invariant LTL.* IPL 75 (2000). ⟨to fetch⟩
- **[God96]** P. Godefroid. *Partial-Order Methods for the
  Verification of Concurrent Systems — An Approach to the
  State-Explosion Problem.* PhD thesis, Université de Liège, 1994;
  published as LNCS 1032, Springer, 1996.
  (`Godefroid_1994_Thesis` — the library copy is the thesis)
- **[ID96]** C. N. Ip, D. L. Dill. *Better verification through
  symmetry.* Formal Methods in System Design 9(1/2), pp. 41–75
  (1996). (`Ip_Dill_1996_FMSD`)
- **[KR65]** K. Krohn, J. Rhodes. *Algebraic theory of machines I.
  Prime decomposition theorem for finite semigroups and machines.*
  Transactions of the AMS 116, pp. 450–464 (1965).
  (`Krohn_Rhodes_1965_TAMS`)
- **[Pel93]** D. Peled. *All from one, one for all: on model checking
  using representatives.* CAV 1993, LNCS 697. (`Peled_1993_CAV`)
- **[PP04]** D. Perrin, J.-É. Pin. *Infinite Words: Automata,
  Semigroups, Logic and Games.* Elsevier, 2004.
  (`Perrin_Pin_2004_Book`)
- **[PW97]** D. Peled, T. Wilke. *Stutter-invariant temporal
  properties are expressible without the next-time operator.*
  Information Processing Letters 63(5), pp. 243–246 (1997).
  (`Peled_Wilke_1997_IPL`)
- **[Str94]** H. Straubing. *Finite Automata, Formal Logic, and
  Circuit Complexity.* Birkhäuser, Progress in Theoretical Computer
  Science, 1994. (`Straubing_1994_Book`)
- **[SωS26]** *Constructing the syntactic ω-semigroup from a
  deterministic Emerson–Lei automaton.* Working draft, 2026.
- **[SωSL26]** the learner note; **[SωSX26]** the definability /
  certificates note; **[SωSN26]** the census note; **[ToLTL26]**
  `sos_toltl.md`; **[BLS-C26]** `bls_cascade.md`.
- **[Tho79]** W. Thomas. *Star-free regular sets of ω-sequences.*
  Information and Control 42(2), pp. 148–156 (1979).
  (`Thomas_1979_IC`)
- ⟨TBD, to fetch: Etessami (above); Diekert–Muscholl (infinite
  traces, Acta Informatica 31, 1994); Gastin–Petit (*Infinite
  traces*, in The Book of Traces, 1995); Straubing–Thérien–Thomas
  (generalized quantifiers, Inf. & Comput. 118, 1995) — cited only
  through [Str94] until read; the ω-MOD analogue; folklore source
  for finite-word Theorem 3.1.⟩
