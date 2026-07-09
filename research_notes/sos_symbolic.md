# A Symbolic Engine for the Syntactic ω-Semigroup: Why the Construction Is Decision-Diagram Shaped

**Yann Thierry-Mieg**

With significant inputs from
**Claude (Anthropic)**

*Working draft — 2026-07-09 — placeholders marked `⟨TBD: …⟩`*

## Abstract

The construction of the syntactic ω-semigroup from a deterministic
Emerson–Lei automaton [SωS26] is dominated by one object: the
acceptance-enriched monoid `EM(D)`, of worst-case size
`(|Q|·2^{|C|})^{|Q|}` — the `|Q|` in the exponent is where the explosion
lives, and the decision problem being PSPACE-complete, some wall is a
mathematical necessity. This paper locates the wall precisely and shows
everything else is *symbolic*: an enriched element is a `|Q|`-slot vector
over the small local domain `Q × 2^C`, the monoid is the **reachability
set** of the identity vector under right multiplication by letters, and —
the load-bearing observation — the rotation lemma of [SωS26], which
computes the two-sided syntactic congruence with right moves alone, is
exactly the statement that every relation the construction *iterates* is
**slot-local**: a conjunction of one identical small relation applied at
each slot. Closure is a least fixpoint; profiles collapse to a single
slot-read once idempotent powers are computed (repeated squaring, which
on the aperiodic side converges in logarithmically many steps); the
residual equivalence, delegated to an external language-equivalence
oracle in explicit implementations, *internalizes* as a small profile-
seeded refinement; the congruence is a greatest-fixpoint partition
refinement over letter relations; and the final quotient — the only
object anyone keeps — is small and explicit, shortlex keys and the
λ-quotient's guards falling out of the same fixpoint layers. On an
abstract engine offering set union/intersection, comparison,
`2k`-variable relations applied to `k`-variable sets, constrained
fixpoints, and quotient by an equivalence, the whole pipeline is native.
And construction is only the entry: the table built by the early
phases depends only on the marked semiautomaton, so one diagram serves
the entire Boolean algebra of acceptance conditions over it, and a
calculus of language operations rides the same diagrams — lasso
membership without ever closing the monoid, complement as a predicate
flip, intersection/union/difference of two languages over an alignment
that is variable-block concatenation, inclusion as a single relational
query with a canonical minimal witness, and the quotient deferred
until canonicity is actually consumed.
The exponential does not disappear; it is *represented*, and the encoding
must inherit the input's shape: for asynchronous products the enriched
monoid factors exactly (`EM(D₁ ⊗ D₂) ≅ EM(D₁) × EM(D₂)`), so factored
slot coordinates give additive diagrams where the flat state-space vector
is itself the explosion. The compactness bet is that of symbolic model
checking, made on the same grounds: engineered inputs are products.
⟨TBD: experimental headline — diagram size vs `|EM|` on the evaluation
corpus and on scaling product families.⟩

---

## 1. Introduction

[SωS26] ends its complexity section on a promissory note: the
construction's ingredients are all Boolean, its steps are all images,
fixpoints and quotients over sets, "native to decision diagrams". This
paper is the note called in — a design, not yet an implementation, but a
design in which every step is named, priced, and mapped onto a small
abstract engine.

The construction it symbolizes decides, among other things, whether an
ω-regular language is LTL-definable, and its cost profile is lopsided in
a way worth stating plainly. Everything *around* the enriched monoid is
polynomial: the two seed relations, the partition refinement, every §7
read-off of [SωS26], and the exported invariant `𝓘(L)` — often tiny —
at the end. The single exponential object is `EM(D)` itself, the monoid
of `|Q|`-slot vectors the construction closes under composition; and by
PSPACE-hardness [CH91] no representation removes that worst case. The
symbolic thesis is the model checker's: do not enumerate the set,
*represent* it; pay per diagram node, not per element; and let the
structure of engineered inputs — which are products, sparse in marks,
symmetric in letters — collapse what adversarial inputs cannot.

Four claims organize the paper:

1. **The construction factors through five primitives** (§2), all
   standard in symbolic model checking, with the whole pipeline written
   out phase by phase (§3): closure as reachability, idempotent powers
   as repeated squaring, profiles as one slot-read, residuals as a
   profile-seeded refinement on `Q`, the congruence as a
   greatest-fixpoint refinement, the quotient and all exports —
   shortlex keys, λ-quotient guards, the residuals block — extracted
   from objects the fixpoints already built.
2. **The reason it factors is the rotation lemma** (§4.1). Right
   multiplication by a generator updates every slot from itself; left
   multiplication permutes slots; general composition selects a slot by
   a runtime value. [SωS26, Lemma 4.4] — the two-sided congruence is
   computable by right moves alone — is, re-read on the encoding, the
   statement that the construction never iterates a slot-crossing
   relation: the one crossing it needs (idempotent powers) sits outside
   every fixpoint. The algebraic economy and the symbolic feasibility
   are one fact.
3. **Compactness is a structure bet with a precise best case** (§4.2):
   for asynchronous (interleaved) products the enriched monoid factors
   *exactly*, and in factored slot coordinates its diagram is additive
   in the components — while the flat state-space encoding of the same
   monoid can be exponential. The encoding must inherit the system's
   shape; hierarchically structured diagrams are not an optimization
   here but the difference between additive and exponential.
4. **The engine is not construction-only: it is a calculus** (§6).
   Because Phases 0–2 consume no acceptance condition, the expensive
   object is a *table* shared by every language over the same marked
   semiautomaton, and the everyday operations of an ω-automata toolbox
   become moves on that table: lasso membership is a closure-free fold,
   complement is a predicate flip, cross-language products align by
   concatenating variable blocks, inclusion and emptiness are single
   relational queries whose counterexamples are canonical minimal
   lassos extracted through the kept fixpoint layers — and the quotient
   itself becomes an *on-demand* normal form rather than a mandatory
   final phase.

Position: this engine is the entry gate to everything [SωS26] enables —
its §7 read-offs (aperiodicity, the safety–progress ladder, the Wagner
degree) all run on the small quotient the gate emits — and §6 shows the
gate is also a workshop: a pipeline that complements, conjoins,
quotients, checks and re-checks a specification can stay symbolic
throughout and reduce once at the end.

## 2. Background, the engine, and the symbolic input

### 2.1 The construction, recalled

⟨TBD: compress from [SωS26]. What §3 needs: `D = (Q, ι, δ, C, Acc)`
deterministic complete Emerson–Lei; the enriched element
`⟦w⟧ : q ↦ (δ(q, w), mk(q, w))` with composition
`(x·y)(q) = (st_y(st_x(q)), mk_x(q) ∪ mk_y(st_x(q)))`; `EM(D)` generated
by letter elements over the identity `⟦ε⟧ : q ↦ (q, ∅)`; the collapse
lemma `Acc(x, c) = A(st_x(ι), c)`; the seed = (pointwise residual
classes, profile `Aprof`); Moore refinement to the syntactic congruence
(Theorem 4.5 there); the exported invariant `𝓘(L) = (𝒞, λ, M, P)`.

What §6 needs, additionally: the idempotent power `x^π` (the unique
idempotent among the powers of `x`); *linked pairs* `(s, e)` — `e`
idempotent, `s·e = s`; the **membership oracle**
`Val(c, d) = A(st_c(ι), d)`, deciding `u·v^ω ∈ L` for any `u, v` with
`⟦u⟧ = c`, `⟦v⟧ = d` [SωS26, Lemma 4.1] — well-defined on classes
[SωS26, Lemma 3.2]; and the two classical facts the decision procedures
lean on: an ω-regular language is determined by its ultimately periodic
words, so language equality and inclusion are equalities/implications
of `Val` over all element pairs [PP04]; and every nonempty difference
of ω-regular languages contains an ultimately periodic witness.⟩

### 2.2 The abstract engine

A symbolic store over typed variables (Boolean-encoded or multi-valued),
offering natively:

1. **Set algebra** — union, intersection, difference of variable-sets;
2. **Comparison** — equality and inclusion tests (fixpoint detection);
3. **Relations** — a relation over `2k` variables, *applied* (image and
   preimage) to sets over `k` variables; relations composable and
   restrictable;
4. **Constrained fixpoints** — least and greatest fixpoints of monotone
   set/relation transformers, intersected with constraint sets;
5. **Quotient** — the quotient of a set or relation by an equivalence
   relation, with canonical-representative extraction (least element per
   class under the variable order, or witness extraction through kept
   fixpoint layers).

This is the standard kit of symbolic model checking ⟨TBD: cite the
lineage after the biblio sweep — the precise request list closes the
References⟩. One
operation below wants a remark in advance: we will once need a relation
whose construction is a `|Q|`-way case split (a slot selected by a
runtime value). It remains a finite relation over the same variables —
nothing beyond primitive 3 — but its diagram is not slot-local, and the
design confines it to a single preprocessing phase.

### 2.3 The symbolic input

`D` arrives as Boolean relations, the native form of HOA-style tools:
a transition relation `Δ(q, α, q′)` over state variables and the
atomic-proposition variables `α` (guards are BDDs over `AP`), and one
mark predicate `Mk_c(q, α)` per `c ∈ C`. The alphabet `Σ = 2^AP` is
never enumerated: every letter-indexed construction below carries `α`
as free variables and quantifies it natively — the alphabet-friendliness
[SωS26, §8] promises, realized. States and marks are small: the slot
domain is `V = Q × 2^C`, of `log|Q| + |C|` bits.

## 3. The encoding: seven phases, one crossing

**The element space.** An enriched element is a point in `V^Q` — `k = |Q|`
variables of type `V`, one per slot — and every set the construction
manipulates is a set of such points: one decision diagram. Variable
order: slots grouped by the input's structure (§4.2); within a slot,
state bits above mark bits ⟨TBD: order study⟩.

**Phase 0 — letter relations.** From `Δ` and `Mk`, the letter-element
relation and the right-multiplication relation:

```
Lett(α; x)      =  ⋀_q [ x_q = ( δ(q, α),  mk(q, α) ) ]
R(α; x, x′)     =  ⋀_q [ x′_q = ( δ(st_x(q), α),  mk_x(q) ∪ mk(st_x(q), α) ) ]
```

Both are conjunctions of one identical local relation per slot — each
slot's new value reads that slot's old value and the shared `α` — the
cheapest relational shape the engine knows: a synchronous product of
identical local steps. `R` has `2k` slot variables plus the shared
`α`-block.

**Phase 1 — closure is reachability.**

```
EM¹(D)  =  lfp  X ↦ { ⟦ε⟧ } ∪ ∃α. R(α; X)
```

— the monoid *is* the reachability set of the identity vector
`⋀_q x_q = (q, ∅)` in the right Cayley graph. The layered (BFS) fixpoint
is preferred over chaining ⟨TBD: vs saturation-style orders — measure⟩
because the layers are load-bearing: layer `i` holds exactly the
elements whose shortest representative word has length `i`, so keeping
the layers *is* the length half of shortlex keying, and Phase 6's
representative extraction walks them backward. The closure cap of the
explicit implementation (an `INCONCLUSIVE` exit) becomes a diagram-size
budget — a different resource, and the paper's central empirical
question (§8). The slogan: **closing a monoid under generators is not
like model checking; it is model checking** — states are the elements,
transitions are right multiplications, the initial state is the
identity.

**Phase 2 — the one crossing: idempotent powers.** Composition
`z = x·y` reads, at slot `q`, the `y`-slot indexed by a value of `x`:

```
Comp(x, y, z)  =  ⋀_q  ⋁_{p ∈ Q}  [ st_x(q) = p  ∧  z_q = ( st_y(p),  mk_x(q) ∪ mk_y(p) ) ]
```

— the `|Q|`-way case split announced in §2.2, the only slot-crossing
relation in the pipeline, used to compute the **idempotent-power map**
`π : x ↦ x^π` (the unique idempotent among the powers of `x`) as a
functional relation on the element space:

- *General case*: close the pairing `{(x, x^j)}_{j≥1}` under one more
  right factor of `x` — a pairing lfp of at most `ℓ` rounds, `ℓ` the
  longest power-orbit — then select per `x` the unique idempotent in its
  orbit (`Idem(y) = [Comp(y, y, y)]`, a diagram test).
- *Aperiodic shortcut*: when every element's orbit has period 1 — the
  entire LTL-definable side of the frontier [SωS26, §7] — repeated
  **squaring** converges:
  `x^{2^j} = x^π` as soon as `2^j` passes the index, so `O(log ℓ)`
  applications of `Sq(x, z) = Comp(x, x, z)` compute `π` outright.
  (Squaring also converges on period-2 groups — it detects powers of
  two, not aperiodicity — so it is a shortcut, never a verdict; the
  aperiodicity verdict itself is read on the small quotient, where it
  belongs.)

Phase 2 sits outside every fixpoint of the pipeline: `π` is computed
once and consumed as a static functional relation.

**Phase 3 — profiles are one slot-read.** For an idempotent `e`, the
functional graph of `st_e` stabilizes in one step — `e·e = e` gives
`st_e ∘ st_e = st_e`, so every image state is a fixed point — hence
iterating a loop of class `c` from `q` has inf-set
`mk_{c^π}(st_{c^π}(q))` and

```
A(q, x)  =  Acc( mk_{x^π}( st_{x^π}(q) ) )
```

with `Acc`, a positive Boolean formula over `C`, applied as a small
predicate on the mark bits of one slot. No orbit computation, no cycle
detection, per element or otherwise: the profile relation
`ProfR(x, q) ∈ {0,1}` is the composition of the `π`-map with a single
slot selection and the `Acc` predicate. (This is [SωS26, Lemma 4.1]'s
`A(q, c)` — the walk-the-cycle prose there is the explicit rendering;
idempotency makes the symbolic rendering a lookup.)

**Phase 4 — residuals, internalized.** Explicit implementations obtain
`q ≃ q′` (`L(q) = L(q′)`) from an external language-equivalence oracle.
Symbolically it is a *small* fixpoint over `Q × Q`, seeded by the
profile columns and refined by the deterministic steps:

```
≃  =  gfp  E ↦ { (q, q′) : ∀x ∈ EM. A(q, x) = A(q′, x) }
             ∩ { (q, q′) : ∀α. (δ(q, α), δ(q′, α)) ∈ E }
```

*Correctness*: unwinding the gfp, `(q, q′)` survives iff every
lockstep-reachable pair agrees on every loop verdict, i.e.
`∀b, c ∈ EM: A(st_b(q), c) = A(st_b(q′), c)`, which is agreement on all
ultimately-periodic words, which is language equality. The seed costs
one universal quantification of the element diagram per state pair —
the heaviest single query in the pipeline after Phase 2 — and the
refinement is over the tiny space `Q × Q`. The engine is oracle-free
end to end.

**Phase 5 — seed and congruence.** The seed equivalence on elements is
slot-local given `≃` and `ProfR`:

```
Seed(x, x′)  =  ⋀_q ≃( st_x(q), st_{x′}(q) )   ∧   ⋀_q [ A(q, x) = A(q, x′) ]
```

(the first conjunct is `~lin` — mark components irrelevant, exactly as
[SωS26, §4] notes; the second is the `~ω` seed), and the syntactic
congruence is a greatest fixpoint of partition refinement using only
the slot-local letter relations:

```
~  =  gfp  R ↦ Seed ∩ { (x, x′) : ∀α. ( R_α(x), R_α(x′) ) ∈ R }
```

— preimages under `R(α; ·, ·)` with `α` quantified symbolically; the
rotation lemma [SωS26, Lemma 4.4] is what licenses stopping here, with
no left translations and no two-sided contexts (§4.1). Termination in at
most `|EM|` rounds; each round is two relation applications and an
intersection.

**Phase 6 — quotient and exports.** Primitive 5 quotients `EM¹/~`;
everything a consumer needs falls out of objects already present:

- **Class table**: representatives `x_κ` per class (least element per
  class under the variable order, or shortlex-faithful extraction:
  minimal BFS layer intersecting the class, then backward preimage
  chaining through the layers choosing the least letter — `|𝒞|`
  extractions, each linear in the closure depth); the multiplication
  table `M(κ, a)` by one `R_a` image per representative, lifted to
  `M(κ, κ′)` via representative words ⟨TBD: or one `Comp` application
  per class pair — `|𝒞|²` small queries on a small set⟩.
- **Letter map and λ-quotient**: `λ` classifies letters by the class of
  `Lett(α; ·)` — and since `α` is symbolic, the *guard* of each letter
  class (the BDD over `AP` collecting the letters mapping to class `κ`)
  is one relational image: the quotient alphabet (letters the language
  never distinguishes, merged, each class carrying its guard) is a
  Phase-6 byproduct rather than a post-processing step.
- **Accepting pairs**: on the small quotient, enumerate linked pairs
  `(s, e)` by table arithmetic and evaluate each verdict as
  `Val(s, e) = A( st_{x_s}(ι), x_e )` — Phase 3's predicate applied to
  representatives; well-defined because verdicts are class-invariant
  [SωS26, Lemma 3.2].
- **Residuals block**: the `≃`-classes of Phase 4, keyed by their least
  reaching words through the same layers.

The output is the explicit, canonical `𝓘(L)` — the exponential
intermediate never exists outside its diagram, and is discarded with it.

**Correctness, wholesale.** Each phase computes an object [SωS26]
*defines*; the engine changes representation, never mathematics. ⟨TBD:
one proposition per phase — closure = `EM¹(D)` by induction on word
length; Phase 3 = Lemma 4.1's `A` via the one-step-stabilization fact;
Phase 4 = residual equality via the ultimately-periodic characterization;
Phase 5 = Theorem 4.5's congruence by right-invariance of the seed;
Phase 6 = the invariant of Theorem 5.1. Each proof two to five lines,
citing its [SωS26] anchor.⟩

### 3.1 A specimen, symbolically

`EvenBlocks` [SωS26, Table 2(c)]: `|Q| = 2`, `C = {0, 1}`, slot domain
`V = Q × 2^C` of 8 values; `EM¹` has 16 elements (identity included —
`⟦aa⟧ = ⟦ε⟧` merges into it) — 16 points in `V²`. Small enough to see
the sharing that the diagram exploits: the slot-0 and slot-1 values of
the 15 non-identity elements are highly correlated
(state components complementary or equal, mark components differing in
one bit along the four `{0,1}`-subsets), and the two-level diagram has
one node per distinct slot-0 value with shared slot-1 suffixes ⟨TBD:
draw it; count nodes vs the 32 explicit cells; then the same picture for
a 3-fold asynchronous product of `EvenBlocks`, where the explicit table
is `16³ = 4096` rows and the factored diagram is three copies of the
same 16-point component diagram — the §4.2 proposition made visible⟩.

## 4. Why this works: locality, shape, and the honest wall

### 4.1 The rotation lemma is the locality theorem

The construction's algebraic keystone — [SωS26, Lemma 4.4]: the
two-sided syntactic congruence is the coarsest right-invariant
refinement of its seed, so right multiplications suffice — is, re-read
on the encoding, a statement about *variable locality*, and the three
multiplications stratify exactly:

| operation | slot `q` of the result reads | relational shape |
|---|---|---|
| right mult. by letter, `x·⟦a⟧` | slot `q` of `x` | **slot-local**: one identical small relation per slot |
| left mult. by letter, `⟦a⟧·x` | slot `δ(q, a)` of `x` | slot *permutation*: crossing, but static |
| general composition `x·y` | slot `st_x(q)` of `y` | value-indexed selection: the `\|Q\|`-way case split |

A construction that quantified over two-sided contexts — Arnold's
congruence taken literally — would iterate the third row inside its
fixpoints. The rotation lemma confines every *iterated* relation to the
first row; the single third-row use (Phase 2) is preprocessing. That is
the precise sense in which "everything is a right move" is not an
algebraic elegance but the existence condition for this engine. A
secondary dividend: because the first row is one identical local
relation conjoined per slot, the fixpoints of Phases 1 and 5 have
exactly the shape event-locality-based fixpoint accelerations were built
for ⟨TBD: saturation-style evaluation — the implementers' home turf;
cite after the sweep⟩.

### 4.2 The encoding must inherit the input's shape

**Proposition (interleaving factorization).** Let `D₁ ⊗ D₂` be the
asynchronous product: `Σ = Σ₁ ⊎ Σ₂`, states `Q₁ × Q₂`, a `Σᵢ`-letter
driving component `i` and fixing the other, mark sets disjoint. Then
`w ↦ (⟦w↾Σ₁⟧, ⟦w↾Σ₂⟧)` induces an isomorphism

```
EM(D₁ ⊗ D₂)  ≅  EM(D₁) × EM(D₂).
```

*Proof sketch.* A run of `w` from `(q₁, q₂)` projects to runs of the
subwords from the components, marks collected separately (disjointness),
so the enriched element of `w` at slot `(q₁, q₂)` is the pair of the
component elements' slots — the map is a well-defined injective
morphism. Surjectivity: for `(⟦u⟧₁, ⟦v⟧₂)` take `w = u·v`; each
component sees only its own subword. ∎

The corollary is the design point. Represent the element in **factored
coordinates** — `|Q₁|` slots of type `V₁` followed by `|Q₂|` slots of
type `V₂`, i.e. the pair `(e₁, e₂)` — and the diagram of the product
monoid is the *concatenation* of the component diagrams: **additive**
size for multiplicative cardinality, and every `R_a` still slot-local
(a `Σ₁`-letter's relation is component-1's relation conjoined with the
identity on component-2's block). Represent the same monoid in **flat
coordinates** — one slot per global state `(q₁, q₂)` — and slot
`(q₁, q₂)` holds a value determined by the hidden pair
`(e₁(q₁), e₂(q₂))`: the same component value recurs across a whole row
of slots, a long-range correlation the diagram must carry through every
level, width `Ω(|EM₂|)` under the natural orders ⟨TBD: make this a
stated lower-bound lemma for the flat order, hidden-weighted-bit style;
possibly order-independent for a crafted family⟩. The moral is the
hierarchical one: the slot space must follow the system decomposition,
and hierarchically structured diagrams are not a refinement here but
the difference between linear and exponential.

For **synchronous** products (shared alphabet) the map
`x ↦ (x↾₁, x↾₂)` is still an injective morphism, so
`EM(D) ↪ EM(D₁) × EM(D₂)` — the image is the submonoid generated by the
diagonal letter pairs: the *generated alignment product* on which the
calculus of §6 puts two languages side by side. The
relations still factor; how close the reachable set stays to
product-form is an empirical column (§8). Two further compression
sources are unconditional:

- **Constant and shared slots.** The completion sink is the same slot
  value in every element — one diagram node, ever; transient states
  reached alike shared across elements likewise.
- **Monotone marks.** Per slot, the mark set only grows along right
  extensions, so mark components populate upward-closed families —
  a classically diagram-friendly shape ⟨TBD: quantify on the corpus⟩.
- **Letter symmetry.** Letters the language never distinguishes are
  guard-equal in `Lett` before anything is built: the λ-quotient
  operates at the entry, symbolically.

### 4.3 The honest wall

Aperiodicity of a regular ω-language is PSPACE-complete [CH91; SωS26,
§8]; no representation makes the pipeline polynomial in general, and
there should exist families whose enriched monoids admit no small
diagram under any variable order ⟨TBD: prove for a crafted family, or
leave as a stated conjecture with the flat-order lemma of §4.2 as
partial evidence⟩. The claim is the symbolic model checker's claim, no
more and no less: worst cases stand; structured cases — products,
sparse marks, few residuals, small λ-quotients — collapse; and the
inputs that occur are engineered, hence structured. The evaluation
corpus and the scaling product families of §3.1 measure which world
the practical inputs inhabit, and §8's headline question is whether the
`|Q|` exponent *moved* — from cardinality, where it provably lives, to
diagram width, where structure fights it.

## 5. The pipeline, costed

| phase | computes | primitive | relational shape | rounds |
|---|---|---|---|---|
| 0 | `Lett`, `R` | build from `Δ, Mk` | slot-local, `2k + AP` | — |
| 1 | `EM¹` + layers | lfp, image | slot-local | closure depth `≤ \|EM\|` |
| 2 | `π`-map | pairing lfp / squaring | **crossing** (`\|Q\|`-way split) | `O(ℓ)`; `O(log ℓ)` aperiodic |
| 3 | `ProfR` | compose + predicate | one slot-read + `Acc` | 1 |
| 4 | `≃` | gfp on `Q × Q` | small; seed: one `∀x ∈ EM` | `≤ \|Q\|` |
| 5 | `~` | gfp refinement | slot-local preimages, `∀α` | `≤ \|EM\|` splits |
| 6 | `𝓘(L)` | quotient + extraction | small, explicit | `\|𝒞\|` extractions |

Every round is polynomial in the *diagram sizes* of its operands — the
symbolic contract; the open quantity is the diagrams themselves (§8).
Two structural notes. The closure depth of Phase 1 equals the length of
the longest shortlex-minimal representative, `< |𝒞|` *after* quotient
collapse but up to `|EM|` before it ⟨TBD: is the pre-quotient depth
small in practice? measure⟩. And Phase 5's split count is bounded by
`|EM|` but its *effective* rounds end at the syntactic partition — the
same early-stabilization phenomenon symbolic bisimulation minimization
exploits ⟨TBD: cite after sweep⟩.

A remark on learning: an active-learning observation table for
ω-regular languages (rows = words, columns = experiments) is also a
vector set over a small local domain, and its column sorts are the seed
of Phase 5 in disguise; a symbolic learner sharing this engine is left
as a prospect ⟨TBD: one paragraph, or cut⟩.

## 6. The calculus: operating without leaving the diagram

Everything so far builds one language's invariant. The pipeline's own
bookkeeping proves something stronger: **Phases 0–2 never read `Acc`**.
The letter relations, the closure `EM¹` with its layers, and the
`π`-map depend only on the *marked semiautomaton* `(Q, ι, δ, C, Mk)`;
the acceptance formula enters at Phase 3, as a small predicate on one
slot's mark bits. Call the acceptance-free part the **symbolic table**

```
T(D)  =  ( Lett, R,  EM¹ + layers,  π-map )
```

so that a *language over the table* is nothing but a Boolean predicate
`Acc` on mark-sets, carried through Phase 3 into the verdict oracle
`Val(c, d) = A(st_c(ι), d)` of §2.1. This section develops the
consequence: the everyday operations of an ω-automata toolbox —
membership, complement, Boolean combinations, product, inclusion,
emptiness — are *moves on the table*, performed on diagrams the
construction already keeps; and the quotient (Phases 4–6) is demoted
from mandatory final phase to **on-demand normal form**: none of the
moves below needs it, and each commutes with it ⟨TBD: one proposition —
operating then reducing yields the same invariant as reducing then
performing the quotient-side operation; a short diagram-chase per
move⟩. The economic slogan this earns: not *pay canonicity once*, but
*pay canonicity only when canonicity is consumed*.

### 6.1 Lasso membership, closure-free

`u·v^ω ∈ L(D)?` Fold both words: `|u| + |v|` applications of the
right-multiplication relation, `α` fixed to the letter read, to
singleton sets starting at `{⟦ε⟧}` — on a singleton every relation is
a concrete function, each image a
singleton — giving `c = ⟦u⟧`, `d = ⟦v⟧` as explicit slot vectors; then
`d^π` by concrete power iteration (at most `ℓ` compositions, `O(log ℓ)`
by squaring in the aperiodic case), one slot read, one `Acc`
evaluation. The verdict is `Val(c, d)` — and **Phase 1 never ran**: a
membership query builds no monoid, touches no fixpoint.

Honesty requires the comparison: on a *deterministic* input a single
membership is answered by just running the automaton around the lasso,
at the same cost. What the fold buys is not the bit but the *elements*
`c, d` — the same `|u|+|v|`-step computation is the oracle every
operation below composes with, its output lands in the algebra (ready
to be rooted, compared, canonicalized), where the automaton-side run
composes with nothing.

### 6.2 Complement and the same-table Boolean algebra

`L(D, Acc)^c = L(D, ¬Acc)`: complement is one predicate negation;
no diagram moves. (No positivity is lost: the Emerson–Lei format's
positive formulas over `Inf(c)`/`Fin(c)` atoms, with `Fin = ¬Inf`,
denote exactly the arbitrary Boolean predicates on inf-sets — a class
closed under `¬, ∧, ∨` — and Phase 3 evaluates the predicate on a
concrete mark set, never using positivity.) More generally the
Emerson–Lei languages over one
marked semiautomaton form a Boolean algebra mirrored by their
acceptance formulas — `L(D, Acc₁) ∪ L(D, Acc₂) = L(D, Acc₁ ∨ Acc₂)`
and likewise for `∧` and `∧¬` — so union, intersection and difference
of same-table languages are Boolean operations on small predicates
under one shared (and untouched) exponential table. Again the honest
baseline: negating a deterministic automaton's acceptance formula is
free on the automaton side too. The difference is what comes *after*:
the automaton-side result is a new automaton to be re-simplified and
re-classified per operation, while here every result is one Phase-3
predicate away from its verdicts and one on-demand reduce away from
its canonical form — with all the classification read-offs of
[SωS26, §7] waiting on the other side.

### 6.3 Alignment is variable-block concatenation

Cross-table operations — `L₁ = L(D₁, Acc₁)`, `L₂ = L(D₂, Acc₂)` —
need the two languages on one table, and §4.2 has
already drawn it: concatenate the slot blocks (`|Q₁|` slots of type
`V₁`, then `|Q₂|` of type `V₂`), conjoin the letter relations on the
shared `α`-block, and run Phase 1's lfp. (Distinct `AP` sets merge by
union first, and the merge is literally free: each `Δᵢ` simply does
not mention the other's variables — where explicit-alphabet tools pay
`2^{AP₁ ∪ AP₂}` up front.) The reachable set is exactly
the submonoid of `EM(D₁) × EM(D₂)` generated by the diagonal letter
pairs — the *generated alignment product*, computed on-the-fly:
elements outside the generated part never exist, and the factored
coordinates keep the aligned diagram near-additive when the components
interact weakly (§4.2, §8). Verdicts lift blockwise:

**Proposition 6.1 (idempotent powers factor through blocks).** For an
aligned element `x = (x₁, x₂)`, `x^π = (x₁^π, x₂^π)`. *Proof sketch*:
powers act blockwise, so `x^π = (x₁^k, x₂^k)` for its exponent `k`;
each block is then an idempotent power of `xᵢ`, and the cyclic
subsemigroup generated by `xᵢ` has a unique idempotent. ∎

The consequence is stronger than verdict lifting: the aligned `π`-map
*is* `π₁` on block 1 conjoined with `π₂` on block 2, restricted to the
aligned closure (block `i` of the closure projects onto exactly
`EM¹(Dᵢ)`, so the component maps cover it). Phase 2 — the pipeline's
one crossing — is never run on the aligned space: the case split stays
per-component, its cost additive while the aligned space is
multiplicative. Hence `Valᵢ` on the aligned table reads block `i`
alone — Phase 3 per
component, no cross-block work — and cross-table union, intersection
and difference are pointwise `∨ / ∧ / ∧¬` of per-block verdict
predicates. Note what is *absent*: no acceptance-condition surgery.
Automata products under heterogeneous Emerson–Lei conditions need
degeneralization counters or Zielonka-style bookkeeping; here
acceptance never left predicate form, and the Boolean combination of
two conditions is the Boolean combination of two predicates.

### 6.4 Inclusion, equivalence, emptiness: one query, minimal witness

Since ω-regular languages are determined by their ultimately periodic
words (§2.1), on the aligned table

```
L₁ ⊆ L₂   ⟺   ∀ c, d ∈ EM_⊗ :  Val₁(c, d) → Val₂(c, d)
```

and the check factors into two reads the engine already knows. First
project the closure onto two slots: the set
`S = { (st_c(ι₁), st_c(ι₂)) : c ∈ EM_⊗ }` over the small space
`Q₁ × Q₂` — one image of the closure diagram, and recognizably the
classical reachable product state space, recovered as a *projection of
the monoid*. Then one intersection:

```
Bad  =  S(q₁, q₂)  ∧  ProfR₁(q₁, d)  ∧  ¬ProfR₂(q₂, d)
```

with both `ProfR`s Phase-3 objects of the aligned table; `L₁ ⊆ L₂` iff
`Bad = ∅`. The query composes relations already built, introduces no
new relational shape, and is never iterated. Equivalence is two
inclusions (one `Bad` with the verdict xor), or byte equality after
reduce; emptiness and universality are the single-table degenerate
cases (`Val ≡` false / true on one side), `∃ c, d : Val(c, d)` being
one quantification of the closure diagram.

**Witnesses, canonical and minimal.** A nonempty `Bad` carries its own
counterexample: take its least element `(q₁, q₂, d)` under the variable
order, extract the shortlex key of `d` backward through the kept
layers (Phase 6's mechanism) for the loop word, and the key of the
least `c` reaching `(q₁, q₂)` for the stem. Ordering lassos by stem
length, then loop length, then lexicographically, the extracted lasso
is least among *all* ultimately periodic separating words — a
satisfying `(u, v)` lives at the element pair `(fold(u), fold(v))`,
whose keys dominate it componentwise ⟨TBD: state as a proposition with
the two-line proof; requires the layer-faithful extraction of Phase 6,
not the plain least-element read⟩. Every decision procedure of this
section therefore emits the *minimal* certificate, deterministically —
a discipline automata-side counterexample extraction does not have.

Honesty once more: with deterministic inputs, automata-side inclusion
is also polynomial (negate one acceptance formula, product, emptiness).
The claims here are different ones: (i) the query runs on the factored
diagram in cases where the flat product state space is itself the
explosion (§4.2); (ii) acceptance stays a predicate — automata-side
emptiness under an arbitrary Emerson–Lei condition is NP-complete in
the condition [EL87, Thm 4.7], the accepting-cycle search growing with
the Boolean structure, while here idempotency dissolved the cycle into
a slot read and the Boolean structure into a predicate evaluated on
one slot's mark bits (Phase 3): that hardness is absorbed into the
same diagram-size bet as everything else, not paid as a separate
search; (iii) the witness is canonical-minimal by
construction; (iv) the same aligned table then serves every further
operation on the pair.

### 6.5 Rootings and relabelings

**Left quotients.** For `u⁻¹L`: fold `u` (§6.1) and read
`q_u = st_{⟦u⟧}(ι)`; the rooted language is the same table, the same
predicate, with the initial slot moved to `q_u` — not even surgery, a
re-parameterization. Quotients compose as they must
(`(uv)⁻¹L = v⁻¹(u⁻¹L)` is `st` composition), the distinct rootings are
Phase 4's `≃`-classes — the residual automaton, internalized — and a
rooting followed by any §6 operation costs nothing extra.

**Inverse substitutions.** For a relabeling `σ : Σ' → Σ` (letter
renaming or merging), substitute the `α`-block: compose `Lett` and `R`
with the relation `⟦α = σ(α′)⟧` over the `AP` variables. The new
generators are elements of the old monoid, so the re-closure lfp runs
*constrained inside the existing diagram* — Phase 1 with the new
letter relation, intersected with `EM¹` at every step. And nothing
restricts the images to letters: for any non-erasing homomorphism
`h : Σ' → Σ⁺` the generator of `a ∈ Σ'` is the fold `⟦h(a)⟧` — an
element of the old monoid, reached in `|h(a)|` applications of `R` —
and the same constrained re-closure yields the table of `h⁻¹(L)`:
inverse homomorphic images never leave the diagram.

### 6.6 The frontier, unchanged

The ω-rational constructors — concatenation `W·L` by a prefix set,
ω-power `W^ω` — and existential projection (`remove_ap`) quantify over
a split position or a hidden run, and no move on a fixed table
expresses that; the syntactic object of the result can be exponentially
larger (already so for syntactic monoids of concatenations on finite
words). Symbolically the projection case is sharp: quantifying an `AP`
variable out of `Δ` is one line — `∃α_p. Δ` — and yields a relation
that is no longer functional per slot; every phase above assumed
deterministic slot values. The wall re-enters exactly where the input
leaves determinism, and the symbolic subset construction that would
restore it is the entry price again — relocated, not evaded.

### 6.7 The ledger

| operation | on automata (det. EL input) | on the table | diagram work |
|---|---|---|---|
| lasso membership | run the lasso | fold + power + slot read (§6.1) | none — no closure |
| complement | negate `Acc` | negate `Acc` | none |
| same-`D` `∪ / ∩ / \` | combine `Acc`s | combine `Acc`s | none |
| cross-`D` `∪ / ∩ / \` | build the product | block-concat + re-close (§6.3) | the aligned closure |
| inclusion / equivalence | product + EL emptiness | `Bad = ∅?` (§6.4) | one projection + one intersection |
| emptiness + witness | accepting-cycle search (NP-c. in the EL condition) | `∃c,d. Val` + layer extraction | one query |
| left quotient | move the initial state | move `ι` | none |
| relabel / inverse subst. | rebuild | substitute `α`-block (§6.5) | constrained re-close |
| canonical form, byte equality | *none in general* | reduce = Phases 4–6, on demand | the §5 costs |
| `W·L`, `W^ω`, `∃`-projection | native nondeterminism | exponential (§6.6) | entry gate again |

Rows one through eight cost parity or better against deterministic
automata (better exactly where the acceptance condition's Boolean
structure bites) — the table's real dividends are the last two
columns' qualitative entries: canonicity exists and is optional, witnesses are
minimal, acceptance surgery is dissolved, and everything runs factored
where the flat product is unbuildable.

## 7. Scope

The engine's boundaries, stated once:

- **Downstream of Phase 6** the quotient is small and explicit, and
  every classification read-off of [SωS26, §7] — aperiodicity, the
  safety–progress ladder, the acceptance index, the Wagner degree — is
  a scan of that explicit table; nothing there is symbolic, and this
  paper adds nothing to it.
- **Exits.** A pipeline that must hand an automaton back exits through
  the classical `⋃ L_s·(L_e)^ω` decomposition over accepting pairs
  [PP04], polynomial in `|𝒞|` from the reduced table ⟨TBD: exact size;
  determinized exits⟩; extraction of a defining LTL formula on the
  aperiodic side is beyond this paper's scope.
- **Not simulated.** Branching semantics — games, synthesis — are out:
  the invariant is a linear-time object. And canonicity has a price
  ceiling: `𝓘(L)` can be exponentially larger than a good
  nondeterministic presentation, so the calculus is not a back-end for
  one-shot translations; it is the substrate for pipelines that *keep*
  a language and work on it.

## 8. Evaluation

⟨TBD: after implementation. The planned columns: (i) diagram size vs
`|EM|` across the evaluation corpus — the compression scatter; (ii) scaling
on asynchronous product families (`n` copies of a fixed component:
cardinality `|EM|ⁿ`, factored diagram size expected `O(n·|EM-diagram|)` —
the §4.2 proposition as a measured line); (iii) synchronous products —
distance of the reachable set from product form; (iv) phase profiling —
where the time goes, with Phase 2's crossing and Phase 4's seed
quantification the predicted peaks; (v) variable-order sensitivity, flat
vs factored on the same inputs — the §4.2 lower-bound picture
empirically; (vi) the bottom line against the explicit implementation's
closure cap: instances the cap kills that the diagram carries, and the
converse; (vii) the calculus in motion — a worked multi-operation
pipeline (complement, conjoin, check, re-check) measured against
per-operation automata constructions, and deferred-reduce vs
reduce-then-operate on the same sequence.⟩

## 9. Related work

⟨TBD: full pass, after the biblio sweep. The slots: symbolic model
checking and reachability — the engine lineage and the origin of the
"represent, don't enumerate" claim; saturation and event locality — the
fixpoint discipline matching §4.1's slot-local shape; symbolic
bisimulation minimization and signature refinement — the nearest
relatives of Phases 4–5; multi-valued, list, and hierarchical decision
diagram variants — the data structures §4.2's factored coordinates
want; explicit transition-monoid computation (AMoRE lineage) — the
baseline that motivated [SωS26, §8]'s note; and the finite-word
syntactic-monoid tools, none of which, to our knowledge, is symbolic;
the ω-automata toolbox tradition (Spot — request in the References) as
the per-operation baseline §6's ledger is drawn against.
Position claim: symbolic techniques have computed transition *systems*
for forty years and transition *monoids* apparently never — yet the
monoid is the better-shaped object, its generators acting slot-locally
by the very lemma that makes the syntactic quotient computable.⟩

## 10. Conclusion

⟨TBD: the arc — the syntactic ω-semigroup's construction was born
symbolic and nobody noticed: its one deep algebraic lemma is a locality
theorem, its dominant object is a reachability set, its congruence a
partition refinement, its residual oracle an internal fixpoint, and its
output small. The engine relocates the PSPACE wall from "the object
cannot be built" to "the object is built whenever the input has the
structure engineered systems have" — the relocation symbolic model
checking performed on state spaces, applied to the canonical algebra of
ω-regular languages; the encoding lesson is the hierarchical one:
the diagram must inherit the shape of the system, factored coordinates
turning product cardinality into additive representation; and the
object built is a substrate, not an endpoint — the table outlives any
one language, the calculus of §6 running an ω-toolbox's everyday
operations on it without leaving the diagram, canonicity paid only
when consumed.⟩

---

## References

- **[CH91]** S. Cho, D. T. Huynh. *Finite-automaton aperiodicity is
  PSPACE-complete.* TCS 88 (1991) 99–116.
- **[EL87]** E. A. Emerson, C.-L. Lei. *Modalities for model checking:
  branching time logic strikes back.* Sci. Comput. Program. 8 (1987)
  275–306. (Thm 4.7: the fair-state problem under a general
  canonical-form fairness constraint is NP-complete.)
- **[PP04]** D. Perrin, J.-É. Pin. *Infinite Words: Automata, Semigroups,
  Logic and Games.* Elsevier, 2004.
- **[SωS26]** Y. Thierry-Mieg, with Claude (Anthropic). *Constructing
  the syntactic ω-semigroup from a deterministic Emerson–Lei automaton.*
  To appear, 2026.
⟨TBD: the symbolic lineage — in the library, to be cited at the §9
sweep:

- R. E. Bryant. *Graph-Based Algorithms for Boolean Function
  Manipulation.* IEEE Trans. Computers, 1986. (BDDs)
- J. R. Burch, E. M. Clarke, K. L. McMillan, D. L. Dill, L. J. Hwang.
  *Symbolic Model Checking: 10²⁰ States and Beyond.* Inf. & Comput.,
  1992. (symbolic reachability)
- T. Kam, T. Villa, R. K. Brayton, A. Sangiovanni-Vincentelli.
  *Multi-valued Decision Diagrams: Theory and Applications.* UCB/ERL
  memo, 1996 (journal version: Int. J. Multiple-Valued Logic, 1998).
  (MDDs)
- G. Ciardo, G. Lüttgen, R. Siminiceanu. *Saturation: An Efficient
  Iteration Strategy for Symbolic State-Space Generation.* TACAS 2001.
  (saturation / event locality — §4.1's fixpoint discipline)
- J.-M. Couvreur, Y. Thierry-Mieg. *Hierarchical Decision Diagrams to
  Exploit Model Structure.* FORTE 2005. (SDDs — §4.2's factored
  coordinates)
- Y. Thierry-Mieg, D. Poitrenaud, A. Hamez, F. Kordon. *Hierarchical
  Set Decision Diagrams and Regular Models.* TACAS 2009.
  (hierarchical variants + operation homomorphisms)
- A. Bouali, R. de Simone. *Symbolic Bisimulation Minimisation.*
  CAV 1992. (nearest relative of Phases 4–5)
- A. Duret-Lutz, A. Lewkowicz, A. Fauchille, T. Michaud, E. Renault,
  L. Xu. *Spot 2.0 — A Framework for LTL and ω-Automata Manipulation.*
  ATVA 2016; with A. Duret-Lutz. *LTL Translation Improvements in
  Spot 1.0.* IJCCBS, 2014; A. Duret-Lutz et al. *From Spot 2.0 to
  Spot 2.10: What's New?* CAV 2022; T. Michaud, A. Duret-Lutz.
  *Practical Stutter-Invariance Checks for ω-Regular Languages.*
  SPIN 2015. (the toolbox baseline of §6.7)

Still missing from the library:

- R. E. Bryant. *On the Complexity of VLSI Implementations and Graph
  Representations of Boolean Functions with Application to Integer
  Multiplication.* IEEE Trans. Computers, 1991. (the
  hidden-weighted-bit lower bound — §4.2's flat-order lemma style)
- R. Wimmer, M. Herbstritt, H. Hermanns, K. Strampp, B. Becker.
  *Sigref — A Symbolic Bisimulation Tool Box.* ATVA 2006. (signature
  refinement)
- O. Matz, A. Miller, A. Potthoff, W. Thomas, E. Valkema. *Report on
  the Program AMoRE.* Tech. Rep. 9507, CAU Kiel, 1995. (explicit
  transition-monoid baseline)⟩
