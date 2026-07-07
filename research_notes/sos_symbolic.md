# A Symbolic Engine for the Syntactic ω-Semigroup: Why the Construction Is Decision-Diagram Shaped

**Yann Thierry-Mieg**

With significant inputs from
**Claude (Anthropic)**

*Working draft — 2026-07-07 — placeholders marked `⟨TBD: …⟩`*

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
The exponential does not disappear; it is *represented*, and the encoding
must inherit the input's shape: for asynchronous products the enriched
monoid factors exactly (`EM(D₁ ⊗ D₂) ≅ EM(D₁) × EM(D₂)`), so factored
slot coordinates give additive diagrams where the flat state-space vector
is itself the explosion. The compactness bet is that of symbolic model
checking, made on the same grounds: engineered inputs are products.
⟨TBD: experimental headline — diagram size vs `|EM|` on the census corpus
and on scaling product families.⟩

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

Three claims organize the paper:

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

Position in the family: this engine is the *entry gate*. The calculus
[SωSC26] amortizes what is paid here once; the extraction [SωSX26] and
every read-off run on the small quotient the gate emits; the census
[SωSN26] supplies the measurement corpus and the structured scaling
families.

## 2. Background, the engine, and the symbolic input

### 2.1 The construction, recalled

⟨TBD: compress from [SωS26]. What §3 needs: `D = (Q, ι, δ, C, Acc)`
deterministic complete Emerson–Lei; the enriched element
`⟦w⟧ : q ↦ (δ(q, w), mk(q, w))` with composition
`(x·y)(q) = (st_y(st_x(q)), mk_x(q) ∪ mk_y(st_x(q)))`; `EM(D)` generated
by letter elements over the identity `⟦ε⟧ : q ↦ (q, ∅)`; the collapse
lemma `Acc(x, c) = A(st_x(ι), c)`; the seed = (pointwise residual
classes, profile `Aprof`); Moore refinement to the syntactic congruence
(Theorem 4.5 there); the exported invariant `𝓘(L) = (𝒞, λ, M, P)`.⟩

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

This is the standard kit of symbolic model checking ⟨TBD: library
requests for the lineage — BDDs, symbolic reachability and its fixpoint
disciplines, symbolic bisimulation minimization, multi-valued and
hierarchical diagram variants; cite after the biblio sweep⟩. One
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
question (§7). The slogan: **closing a monoid under generators is not
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
  entire LTL side of the frontier, i.e. every input the extraction
  [SωSX26] will consume — repeated **squaring** converges:
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
everything the family consumes falls out of objects already present:

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
  is one relational image: the λ-quotient alphabet of [SωSX26], with its
  rendering guards, is a Phase-6 byproduct rather than a post-processing
  step.
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
`V = Q × 2^C` of 8 values; `EM¹` has 17 elements — 17 points in `V²`.
Small enough to see the sharing that the diagram exploits: the slot-0
and slot-1 values of the 16 non-identity elements are highly correlated
(state components complementary or equal, mark components differing in
one bit along the four `{0,1}`-subsets), and the two-level diagram has
one node per distinct slot-0 value with shared slot-1 suffixes ⟨TBD:
draw it; count nodes vs the 34 explicit cells; then the same picture for
a 3-fold asynchronous product of `EvenBlocks`, where the explicit table
is `17³ ≈ 5000` rows and the factored diagram is three copies of the
same 17-point component diagram — the §4.2 proposition made visible⟩.

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
diagonal letter pairs, precisely the *generated alignment product* `⊗`
of the calculus [SωSC26, §3.1], met here at the entry gate. The
relations still factor; how close the reachable set stays to
product-form is an empirical column (§7). Two further compression
sources are unconditional:

- **Constant and shared slots.** The completion sink is the same slot
  value in every element — one diagram node, ever; transient states
  reached alike shared across elements likewise.
- **Monotone marks.** Per slot, the mark set only grows along right
  extensions, so mark components populate upward-closed families —
  a classically diagram-friendly shape ⟨TBD: quantify on the census⟩.
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
inputs that occur are engineered, hence structured. The census corpus
[SωSN26] and the scaling product families of §3.1 measure which world
the practical inputs inhabit, and §7's headline question is whether the
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
symbolic contract; the open quantity is the diagrams themselves (§7).
Two structural notes. The closure depth of Phase 1 equals the length of
the longest shortlex-minimal representative, `< |𝒞|` *after* quotient
collapse but up to `|EM|` before it ⟨TBD: is the pre-quotient depth
small in practice? measure⟩. And Phase 5's split count is bounded by
`|EM|` but its *effective* rounds end at the syntactic partition — the
same early-stabilization phenomenon symbolic bisimulation minimization
exploits ⟨TBD: cite after sweep⟩.

A remark on the learner: the observation table of [SωSL26] is also a
vector set (rows = words, columns = experiments), and its two column
sorts are the seed of Phase 5 in disguise; a symbolic learner sharing
this engine is left as a prospect ⟨TBD: one paragraph once the learner's
data structures freeze⟩.

## 6. Consumers and scope

The engine is the family's entry gate, and its scope ends at the
quotient:

- **Construction & classification** [SωS26]: the invariant and every §7
  read-off — aperiodicity, ladder, index, Wagner — are scans of the
  small explicit quotient; nothing downstream of Phase 6 is symbolic.
- **Certificates** [SωSX26, §4]: the group scan, context scans, and
  family assembly run on the quotient table; the engine's only
  contribution is having built it.
- **Extraction** [SωSX26, §5]: `Cay(L)`, the layers, (A)/(B), the brick
  emission — all on the quotient. One exception cuts back in: the
  *re-canonicalization* of combinator pieces (Thm 5.19 there) is a
  Phase-5 refinement on an already-small table — the symbolic machinery
  applies but is not needed.
- **Calculus** [SωSC26]: the align–operate–reduce economy prices its
  entry gate as "what determinization always cost"; this paper is the
  bill itemized — and the alignment product `⊗` is §4.2's synchronous
  embedding, so a symbolic *aligner* for large same-alphabet pairs is a
  natural extension ⟨TBD: is cross-table alignment ever large enough to
  want the engine? census will say⟩.
- **Census** [SωSN26]: the intrinsic census enumerates small tables and
  never needs the engine; the *derived* census (pushing machine corpora
  through the construction) is exactly repeated entry-gating and is the
  engine's first consumer at scale.

## 7. Evaluation

⟨TBD: after implementation. The planned columns: (i) diagram size vs
`|EM|` across the census corpus — the compression scatter; (ii) scaling
on asynchronous product families (`n` copies of a fixed component:
cardinality `|EM|ⁿ`, factored diagram size expected `O(n·|EM-diagram|)` —
the §4.2 proposition as a measured line); (iii) synchronous products —
distance of the reachable set from product form; (iv) phase profiling —
where the time goes, with Phase 2's crossing and Phase 4's seed
quantification the predicted peaks; (v) variable-order sensitivity, flat
vs factored on the same inputs — the §4.2 lower-bound picture
empirically; (vi) the bottom line against the explicit implementation's
closure cap: instances the cap kills that the diagram carries, and the
converse.⟩

## 8. Related work

⟨TBD: full pass, after the biblio sweep. The slots: symbolic model
checking and reachability — the engine lineage and the origin of the
"represent, don't enumerate" claim; saturation and event locality — the
fixpoint discipline matching §4.1's slot-local shape; symbolic
bisimulation minimization and signature refinement — the nearest
relatives of Phases 4–5; multi-valued, list, and hierarchical decision
diagram variants — the data structures §4.2's factored coordinates
want; explicit transition-monoid computation (AMoRE lineage) — the
baseline that motivated [SωS26, §8]'s note; and the finite-word
syntactic-monoid tools, none of which, to our knowledge, is symbolic.
Position claim: symbolic techniques have computed transition *systems*
for forty years and transition *monoids* apparently never — yet the
monoid is the better-shaped object, its generators acting slot-locally
by the very lemma that makes the syntactic quotient computable.⟩

## 9. Conclusion

⟨TBD: the arc — the syntactic ω-semigroup's construction was born
symbolic and nobody noticed: its one deep algebraic lemma is a locality
theorem, its dominant object is a reachability set, its congruence a
partition refinement, its residual oracle an internal fixpoint, and its
output small. The engine relocates the PSPACE wall from "the object
cannot be built" to "the object is built whenever the input has the
structure engineered systems have" — the relocation symbolic model
checking performed on state spaces, applied to the canonical algebra of
ω-regular languages; and the encoding lesson is the hierarchical one:
the diagram must inherit the shape of the system, factored coordinates
turning product cardinality into additive representation.⟩

---

## References

- **[CH91]** S. Cho, D. T. Huynh. *Finite-automaton aperiodicity is
  PSPACE-complete.* TCS 88 (1991) 99–116.
- **[PP04]** D. Perrin, J.-É. Pin. *Infinite Words: Automata, Semigroups,
  Logic and Games.* Elsevier, 2004.
- **[SωS26]** Y. Thierry-Mieg, with Claude (Anthropic). *Constructing the
  syntactic ω-semigroup from a deterministic Emerson–Lei automaton.*
  Working draft, 2026.
- **[SωSL26]** Y. Thierry-Mieg, with Claude (Anthropic). *Learning the
  syntactic ω-semigroup.* Working draft, 2026.
- **[SωSX26]** Y. Thierry-Mieg, with Claude (Anthropic). *The LTL
  frontier from the syntactic ω-semigroup.* Working draft, 2026.
- **[SωSC26]** Y. Thierry-Mieg, with Claude (Anthropic). *A calculus on
  the syntactic ω-semigroup.* Working draft, 2026.
- **[SωSN26]** Y. Thierry-Mieg, with Claude (Anthropic). *A census of
  syntactic ω-semigroups.* Working draft, 2026.
- ⟨TBD: the symbolic lineage — BDDs; symbolic model checking;
  saturation/event locality; symbolic bisimulation minimization;
  MDD/SDD/hierarchical variants; AMoRE for the explicit
  transition-monoid baseline — library requests for the biblio sweep.⟩
