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

Everything in this subsection is [SωS26]'s, compressed to what the
encoding consumes.

**Input.** A **deterministic, complete** Emerson–Lei automaton
`D = (Q, ι, δ, C, Acc)` with `L(D) = L ⊆ Σ^ω`: transition function
`δ : Q × Σ → Q`, a finite set `C` of acceptance **marks** carried on
transitions (`mk(q, w) ⊆ C` the marks on the run from `q` over `w`),
and `Acc` a positive Boolean formula over atoms `Inf(c)`, `Fin(c)`
(`c ∈ C`), evaluated on the set of marks a run visits infinitely often
— the most general ω-regular acceptance, subsuming Büchi, Rabin and
Muller. Determinism makes runs unique and ties residuals to the
language: `L(q) = { α : the run from q satisfies Acc }` and
`L(δ*(ι, u)) = u⁻¹L`.

**The enriched monoid** [SωS26, Def. 3.1]. The enriched element of a
finite word is the map

```
⟦w⟧ : q ↦ ( δ(q, w),  mk(q, w) )
```

— a `|Q|`-slot vector over `V = Q × 2^C`; write `st_x(q)`, `mk_x(q)`
for the two components. Composition is
`(x·y)(q) = ( st_y(st_x(q)),  mk_x(q) ∪ mk_y(st_x(q)) )`, and `EM(D)`
is the transformation monoid generated by the letter elements `⟦a⟧`
over the identity `⟦ε⟧ : q ↦ (q, ∅)`; `⟦·⟧ : Σ* → EM(D)` is a monoid
morphism. The mark half is not decoration: the transition monoid alone
(states without marks) does not recognize `L` [SωS26, Prop. 3.4].

**Recognition and the oracle.** If two ω-words factor into blocks with
the same sequence of enriched images from `ι`, they agree on `L`
[SωS26, Lemma 3.2 (skeleton)]; consequently the syntactic morphism
factors through `⟦·⟧` and the syntactic ω-semigroup is a quotient of
`EM(D)` [SωS26, Cor. 3.3]. For a lasso, acceptance collapses to one
state and one loop [SωS26, Lemma 4.1]: writing `A(q, c)` for the
Emerson–Lei verdict of iterating the loop `c` from `q` (follow `st_c`
from `q` to its closed cycle, evaluate `Acc` on the marks `mk_c` around
that cycle),

```
Val(c, d)  =  A(st_c(ι), d)
```

decides `u·v^ω ∈ L` for *any* representatives `⟦u⟧ = c`, `⟦v⟧ = d` —
the prefix enters only through the state it reaches, and the verdict is
class-invariant [SωS26, Lemma 3.2]. In a finite monoid every element
`x` has a
unique idempotent among its powers, the **idempotent power** `x^π`; a
**linked pair** is `(s, e)` with `e·e = e`, `s·e = s` — the Ramsey
normal form of a lasso, `s` naming the stem, `e` the loop.

**The congruence, right-computable.** The syntactic congruence
(Arnold's) transports to `~` on `EM(D)`, and factors as
`~ = ~lin ∧ ~ω` [SωS26, Prop. 4.3]: `e ~lin f` iff
`L(st_e(q)) = L(st_f(q))` at every slot `q` (residual agreement —
mark parts irrelevant), and `e ~ω f` iff the **profiles**
`Aprof(e·b) = (q ↦ A(q, e·b))` agree under every right extension `b`.
The **rotation lemma** [SωS26, Lemma 4.4] — a left factor `a` turns
into a right extension read at the shifted slot,
`Aprof(a·e·b)(q) = Aprof(e·b·a)(st_a(q))` — makes `~` the coarsest
*right-invariant* refinement of the seed (`~lin`-class, `Aprof`), so
one Moore-style partition refinement computes it [SωS26, Thm. 4.5]:
seed, then split blocks disagreeing under some letter, at most
`|EM(D)|` splits.

**The invariant.** The output is `𝓘(L) = (𝒞, λ, M, P)`: the `~`-classes
`𝒞` keyed by shortlex-least representative words, the letter map
`λ(a) = [a]`, the multiplication table `M`, and the accepting linked
pairs `P` — a complete, canonical, presentation-independent invariant:
two regular ω-languages are equal iff their `𝓘` coincide [SωS26,
Thm. 5.1].

**Two classical facts** the decision procedures lean on [PP04]: an
ω-regular language is determined by its ultimately periodic words, so
language equality and inclusion are equalities/implications of `Val`
over all element pairs; and every nonempty Boolean combination of
ω-regular languages contains an ultimately periodic witness.

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

This is the standard kit of symbolic model checking — sets and
relations as BDDs [Bry86], reachability and fixpoints as relational
images [BCM+92], multi-valued variables as MDDs [KVBS98], quotients
and equivalences as in symbolic minimization [BdS92]. One
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
  the minimal BFS layer `i` intersecting the class gives the length;
  backward preimage chaining from the class through layers
  `i−1, …, 0` gives the layer-indexed sets that can still reach it,
  and a *forward* walk through those sets choosing the least letter
  at each step gives the lex-least word of that length — backward
  letter choice would minimize the wrong end. `|𝒞|` extractions, each
  linear in the closure depth); the multiplication table `M(κ, a)` by
  one `R_a` image per representative, lifted to `M(κ, κ′)` by folding
  the representative word of `κ′` letter by letter — `|𝒞|` folds of
  total length `Σ_κ |key(κ)|`, cheaper than `|𝒞|²` applications of
  Phase 2's crossing relation `Comp` and using only slot-local moves.
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
*defines*; the engine changes representation, never mathematics. One
proposition per phase:

**Proposition 3.1 (closure).** The lfp of Phase 1 equals
`{ ⟦w⟧ : w ∈ Σ* }`, and its layer `i` holds exactly the elements whose
shortest representative word has length `i`.
*Proof.* `R(α; x, x′)` holds iff `x′ = x·⟦α⟧` (compare slotwise with
[SωS26, Def. 3.1]'s composition law). By induction on `i`, the `i`-th
BFS frontier is `{ ⟦w⟧ : |w| = i } ∖ (earlier layers)` — exactly the
elements first reached at length `i`. The fixpoint is the union: every
`⟦w⟧` is reached in `|w|` steps, and nothing else is. ∎

**Proposition 3.2 (idempotent powers).** Phase 2's relation maps each
`x` to `x^π`, the unique idempotent among its powers.
*Proof.* The pairing lfp closes `{(x, x)}` under `(x, y) ↦ (x, y·x)`,
so it holds `{(x, x^j) : 1 ≤ j ≤ orbit length}`; the cyclic
subsemigroup `{x^j}` of a finite monoid contains exactly one idempotent
[PP04], so the `Idem`-filtered selection is functional and equals `π`.
For the squaring shortcut: if `x`'s orbit has period 1, then
`x^m = x^π` for every `m ≥` the orbit's index, and `2^j` passes the
index in `⌈log₂ index⌉` squarings. ∎

**Proposition 3.3 (profiles).** `A(q, x) = Acc(mk_{x^π}(st_{x^π}(q)))`
equals the loop verdict `A(q, x)` of [SωS26, Lemma 4.1].
*Proof.* Let `e = x^π = x^k` and `v` represent `x`; as ω-words
`v^ω = (v^k)^ω`, so the inf-set of iterating `x` from `q` is that of
iterating `e`. Idempotency gives `st_e ∘ st_e = st_e`: after one
`e`-block the run sits at `st_e(q)`, a fixed point of `st_e`, and every
further block collects exactly `mk_e(st_e(q))`. The inf-set is
therefore `mk_e(st_e(q))`, and `Acc` applied to it is Lemma 4.1's
verdict. ∎

**Proposition 3.4 (residuals).** Phase 4's gfp equals
`{ (q, q′) : L(q) = L(q′) }`.
*Proof.* A pair survives round `n` iff every pair reached from it by a
lockstep word of length `< n` agrees on all profile columns; the gfp
thus holds `(q, q′)` iff `A(δ*(q, u), x) = A(δ*(q′, u), x)` for all
`u, x` — by [SωS26, Lemma 4.1] agreement of `L(q)` and `L(q′)` on all
ultimately periodic words, which is language equality (§2.1).
Conversely language-equal states agree on every verdict and step to
language-equal states, so `≃` is a post-fixpoint. ∎

**Proposition 3.5 (congruence).** Phase 5's gfp equals the syntactic
congruence `~` of [SωS26, Thm. 4.5].
*Proof.* `Seed` is exactly Lemma 4.4's seed `R`: its first conjunct is
`~lin` (residual agreement at every slot, by Prop. 3.4), its second is
`Aprof(x) = Aprof(x′)` (by Prop. 3.3). The gfp with letter-preimage
refinement computes the coarsest right-invariant refinement of `Seed`,
which the rotation lemma [SωS26, Lemma 4.4] identifies with the
two-sided congruence `~`. ∎

**Proposition 3.6 (exports).** Phase 6 emits `𝓘(L) = (𝒞, λ, M, P)` of
[SωS26, Thm. 5.1].
*Proof.* `𝒞 = EM¹/~` by Prop. 3.5 and [SωS26, Thm. 4.5]; the extracted
keys are shortlex-least representatives by Prop. 3.1's layer
characterization (length) plus the forward lex-least walk (order);
`λ` and `M` are well-defined on classes because `~` is a two-sided
congruence; `P` is read through `Val` on representatives, and verdicts
are class-invariant [SωS26, Lemma 3.2]. ∎

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
same 16-point component diagram — Proposition 4.1 made visible⟩.

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
for — saturation [CLS01] and its hierarchical descendants [TMPHK09];
whether they beat the BFS order here is an §8 measurement, with one
caveat already visible: Phase 1's layers are load-bearing (shortlex,
witnesses), so a saturation-style closure must either re-derive lengths
afterwards or be reserved for runs that will not export keys.

### 4.2 The encoding must inherit the input's shape

**Proposition 4.1 (interleaving factorization).** Let `D₁ ⊗ D₂` be the
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
level.

**Lemma 4.2 (flat-order width).** Let `|Q₁| ≥ 2` and order the flat
slots row-major: every slot `(q₁⁰, ·)` of a fixed `q₁⁰` before any
other row, the order within and after the first row arbitrary. Then
the diagram of `EM(D₁) × EM(D₂)` in flat coordinates has width
`≥ |EM(D₂)|` at the boundary after the first row.
*Proof.* Fix any `e₁ ∈ EM(D₁)`. For each `e₂ ∈ EM(D₂)` the element
`(e₁, e₂)` yields a first-row assignment from which `e₂` is fully
recoverable: the slot `(q₁⁰, q₂)` carries state component
`(st_{e₁}(q₁⁰), st_{e₂}(q₂))` and mark component
`mk_{e₁}(q₁⁰) ∪ mk_{e₂}(q₂)`, and the mark sets are disjoint, so
`st_{e₂}` and `mk_{e₂}` are read off slot by slot. These `|EM(D₂)|`
prefixes are pairwise distinct, and their continuation sets are
pairwise disjoint: every continuation exposes `e₂` again in the next
row (same read-off, `|Q₁| ≥ 2` guarantees a next row). Distinct
nonempty continuation sets force distinct nodes at the boundary. ∎

The obstruction is order-symmetric — a `q₂`-major order hits
`|EM(D₁)|` — and the style is the classical one of hidden-weighted-bit
lower bounds [Bry91]; whether a crafted family resists *every* slot
order is the §4.3 conjecture. The moral is the
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
§8]; no representation makes the pipeline polynomial in general.

**Conjecture 4.3.** There is a family of automata `D_n` with
`|Q_n| = O(n)` whose enriched monoids admit no `poly(n)`-size diagram
under *any* slot order. Lemma 4.2 is the fixed-order half — every
row-major-style order is exponential on plain products — and the
conjectured families would entangle the slots so that no order finds a
product seam; we leave it open, noting only that its failure would be
the more surprising outcome (a canonical polynomial-width order for
all enriched monoids), not the safer one.

The claim is the symbolic model checker's claim, no
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
exploits [BdS92], and signature-based refinement [WHH+06] is the
engineered form of exactly Phase 5's shape: a per-element signature
(here: `Seed`-class plus letter-successor classes) recomputed to
fixpoint.

A remark on learning: an active-learning observation table for
ω-regular languages [AF16] — rows keyed by words, columns by
experiments, cells holding verdicts — is also a vector set over a
small local domain, its row set grown by one-letter extensions
(Phase 1's move) and its row equivalence a refinement under
column agreement (Phase 5's move); the structural match suggests a
*symbolic learner* whose table lives in one diagram and whose
consistency checks are the engine's comparisons. We leave it as a
prospect: the queries a teacher answers are per-word, so the win would
be in the table's representation and closure processing, not in query
count.

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
`Val(c, d) = A(st_c(ι), d)` of §2.1. [SωS26, §7.2] sketches this
calculus at the *invariant* level — operations on the reduced,
canonical `𝓘(L)`. This section carries it to the **un-reduced table**:
the everyday operations of an ω-automata toolbox — membership,
complement, Boolean combinations, product, inclusion, emptiness — are
*moves on the table*, performed on diagrams the construction already
keeps; and the quotient (Phases 4–6) is demoted from mandatory final
phase to **on-demand normal form**, licensed by one observation:

**Proposition 6.0 (reduce commutes with the moves).** Let `op` be any
move of this section and `Op` the language operation it implements.
Reducing the moved table yields `𝓘(Op(L))` — the same object as
reducing first and applying [SωS26, §7.2]'s invariant-level operation.
*Proof.* Each move produces the table of an automaton recognizing
`Op(L)` exactly (complement: `(D, ¬Acc)`; alignment: the synchronous
product with the combined predicate; rooting: `D` re-based at `q_u`;
inverse homomorphism: `D` re-lettered through `h` — the per-move
correctness arguments below), and Phases 4–6 compute the syntactic
quotient of whatever table they are given, which is a function of the
recognized language alone [SωS26, Thms. 4.5, 5.1]. Both paths land on
the canonical invariant of the same language. ∎

The economic slogan this earns: not *pay canonicity once*, but
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
`EM¹(Dᵢ)`, so the component maps cover it — computed per block if the
languages did not enter separately). Phase 2 — the pipeline's
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
reduce. Two languages over the *same* `D` skip alignment altogether:
`S` degenerates to the reachable slot set `{ st_c(ι) : c ∈ EM¹ }` and
the same query runs on the single table. Emptiness and universality
are the degenerate predicates (`Val ≡` false / true on one side),
`∃ c, d : Val(c, d)` being one quantification of the closure diagram.

**Witnesses, canonical and minimal.** A nonempty `Bad` carries its own
counterexample, and the layers make it *the* counterexample. Order
lasso presentations `(u, v)`, `v ≠ ε`, by stem length, then loop
length, then stem lex, then loop lex; the selection must follow the
layers, not the variable order:

- `i* :=` the least closure layer holding a `c` with
  `(st_c(ι₁), st_c(ι₂))` in `Bad`'s state-pair projection — one
  intersection per layer, on the small space;
- `j* :=` the least layer holding a `d` with `Bad(st_c(ι₁),
  st_c(ι₂), d)` for some `c ∈ layer i*`;
- `C* := { c ∈ layer i* : ∃d ∈ layer j*. Bad }`; the stem `u` is the
  lex-least length-`i*` word folding into `C*` (Phase 6's extraction:
  backward preimage sets, then a forward least-letter walk), pinning
  `c = ⟦u⟧`;
- the loop `v` is the lex-least length-`j*` word folding into
  `{ d ∈ layer j* : Bad(st_c(ι₁), st_c(ι₂), d) }`.

**Proposition 6.2 (minimal witness).** If `L₁ ⊄ L₂`, the extracted
`u·v^ω` lies in `L₁ ∖ L₂`, and `(u, v)` is the least separating lasso
presentation in the order above.
*Proof.* Separation: `Bad(st_c(ι₁), st_c(ι₂), d)` for `c = ⟦u⟧`,
`d = ⟦v⟧` says `Val₁(c, d) ∧ ¬Val₂(c, d)`, which is
`u·v^ω ∈ L₁ ∖ L₂` (§2.1). Minimality: let `(u′, v′)` be any separating
presentation and `c′ = ⟦u′⟧`, `d′ = ⟦v′⟧` its folds — elements of the
closure satisfying `Bad`. Layers bound lengths from below:
`layer(c′) ≤ |u′|` (Prop. 3.1) and `layer(c′) ≥ i*` (definition of
`i*`), so `|u′| ≥ i*`. If `|u′| = i*` then `c′ ∈ layer i*`, so
`layer(d′) ≥ j*` and `|v′| ≥ layer(d′) ≥ j*`. If moreover
`|v′| = j*` then `d′ ∈ layer j*`, hence `c′ ∈ C*` and `u′` is a
length-`i*` word folding into `C*`, so `u ≤_lex u′`; and if `u′ = u`
then `c′ = c` (folds are deterministic), so `v′` folds into `v`'s
selection set and `v ≤_lex v′`. ∎

Emptiness and universality witnesses come from the same mechanism with
`Val` (or its negation) in place of `Bad`, on the single table. Every
decision procedure of this section therefore emits the *minimal*
certificate, deterministically — a discipline automata-side
counterexample extraction does not have.

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
| inclusion / equivalence | product + EL emptiness | `Bad = ∅?` (§6.4) | one projection + one intersection, on the aligned closure |
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
  [PP04]: each class language `{ w : ⟦w⟧ ∈ κ }` is recognized by the
  Cayley DFA of the reduced table (`|𝒞|` states, transitions read off
  `M` and `λ`), `|P| ≤ |𝒞|²` pairs, so a nondeterministic Büchi
  automaton of size `O(|𝒞|·|P|) = O(|𝒞|³)` falls out of the invariant;
  a *deterministic* exit on top costs what determinization always
  costs. Extraction of a defining LTL formula on the aperiodic side is
  beyond this paper's scope.
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
Proposition 4.1 as a measured line); (iii) synchronous products —
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

**The engine lineage.** Every primitive of §2.2 is symbolic model
checking's: Boolean sets and relations as BDDs [Bry86], reachability
and fixpoints as relational images over them [BCM+92] — the origin of
the "represent, don't enumerate" claim this paper transplants — and
multi-valued slot domains as MDDs [KVBS98]. The fixpoint discipline
matching §4.1's slot-local shape is saturation and event locality
[CLS01]; the data structure §4.2's factored coordinates want is the
hierarchical family — SDDs [CT05] and their operation homomorphisms
[TMPHK09] — where a component's diagram is a *value* of the enclosing
one, so block concatenation is native rather than emulated by variable
grouping.

**Phases 4–5's nearest relatives.** Symbolic bisimulation minimization
[BdS92] computes a greatest-fixpoint partition refinement over a BDD
transition relation, and signature-based refinement [WHH+06] is the
engineered per-element-signature form; Phase 5 is the same algorithmic
species with a different seed (residual classes and profiles rather
than labels) and a different carrier (a monoid's right Cayley graph
rather than a transition system). Phase 4 internalizes what those
tools take as given — the state equivalence itself.

**Transition monoids, explicitly.** Computing the syntactic monoid of
a *finite*-word language is classical and implemented — the AMoRE
system is the reference lineage [MMPTV95] — but explicit: elements
enumerated, tables materialized. We are not aware of any symbolic
(decision-diagram) computation of transition monoids or syntactic
algebras, on finite or infinite words; the observation that the
enriched monoid's generators act slot-locally — the same lemma that
makes the syntactic quotient computable at all [SωS26, Lemma 4.4] —
suggests the omission is historical, not structural: symbolic
techniques have computed transition *systems* for forty years, and the
transition *monoid* is, if anything, the better-shaped object.

**The per-operation baseline.** The ω-automata toolbox tradition that
§6.7's ledger is drawn against is Spot's [DLLF+16, DL22]: automata as
the carrier, each operation a construction (product, complement,
simplification [DL14]), specialized decision procedures on the side
(e.g. stutter-invariance checks [MD15]). The calculus of §6 is the
algebraic counterpart: one carrier per language *family* (the table),
operations as predicate moves, canonicity on demand — at the entry
price of determinism (§6.6) that the automata tradition does not pay.

## 10. Conclusion

The syntactic ω-semigroup's construction was born symbolic, and nobody
noticed. Its one deep algebraic lemma — rotation, the fact that a
two-sided congruence yields to right moves alone — is, read on the
encoding, a *locality* theorem: every relation the construction
iterates is one small relation conjoined per slot. Its dominant object
is a reachability set; its congruence, a partition refinement; its
residual oracle, an internal fixpoint on `Q × Q`; its output, small
and explicit. Nothing had to be reformulated to fit the engine — the
engine is what the definitions already say, and the propositions of §3
are each a few lines for that reason.

What the design buys is the relocation symbolic model checking
performed on state spaces, applied to the canonical algebra of
ω-regular languages: the PSPACE wall moves from "the object cannot be
built" to "the object is built whenever the input has the structure
engineered systems have". The encoding lesson is the hierarchical one
— the diagram must inherit the shape of the system, factored
coordinates turning product cardinality (Proposition 4.1) into
additive representation, the flat encoding provably exponential where
the factored one is linear (Lemma 4.2).

And the object built is a substrate, not an endpoint. The table
outlives any one language: every acceptance condition over the same
marked semiautomaton rides it for free, the calculus of §6 runs an
ω-toolbox's everyday operations on it without leaving the diagram —
membership without closure, complement for free, products by block
concatenation, inclusion as one query with a provably minimal
certificate (Proposition 6.2) — and canonicity, the construction's
original deliverable, is paid only when canonicity is consumed. The
open question is the one the paper was honest about throughout,
and §8 is designed to answer it: whether the `|Q|` exponent, evicted
from cardinality, can be kept out of diagram width on the inputs that
occur.

---

## References

- **[AF16]** D. Angluin, D. Fisman. *Learning regular omega languages.*
  TCS 650 (2016) 57–72.
- **[BCM+92]** J. R. Burch, E. M. Clarke, K. L. McMillan, D. L. Dill,
  L. J. Hwang. *Symbolic Model Checking: 10²⁰ States and Beyond.*
  Inf. & Comput. 98(2) (1992) 142–170.
- **[BdS92]** A. Bouali, R. de Simone. *Symbolic Bisimulation
  Minimisation.* CAV 1992.
- **[Bry86]** R. E. Bryant. *Graph-Based Algorithms for Boolean
  Function Manipulation.* IEEE Trans. Computers C-35(8) (1986) 677–691.
- **[Bry91]** R. E. Bryant. *On the Complexity of VLSI Implementations
  and Graph Representations of Boolean Functions with Application to
  Integer Multiplication.* IEEE Trans. Computers 40(2) (1991) 205–213.
  ⟨not yet in the library⟩
- **[CH91]** S. Cho, D. T. Huynh. *Finite-automaton aperiodicity is
  PSPACE-complete.* TCS 88 (1991) 99–116.
- **[CLS01]** G. Ciardo, G. Lüttgen, R. Siminiceanu. *Saturation: An
  Efficient Iteration Strategy for Symbolic State-Space Generation.*
  TACAS 2001.
- **[CT05]** J.-M. Couvreur, Y. Thierry-Mieg. *Hierarchical Decision
  Diagrams to Exploit Model Structure.* FORTE 2005.
- **[DL14]** A. Duret-Lutz. *LTL Translation Improvements in Spot 1.0.*
  Int. J. Critical Computer-Based Systems 5(1/2) (2014) 31–54.
- **[DL22]** A. Duret-Lutz, E. Renault, M. Colange, F. Renkin,
  A. Gbaguidi Aisse, P. Schlehuber-Caissier, T. Medioni, A. Martin,
  J. Dubois, C. Gillard, H. Lauko. *From Spot 2.0 to Spot 2.10:
  What's New?* CAV 2022.
- **[DLLF+16]** A. Duret-Lutz, A. Lewkowicz, A. Fauchille, T. Michaud,
  E. Renault, L. Xu. *Spot 2.0 — A Framework for LTL and ω-Automata
  Manipulation.* ATVA 2016.
- **[EL87]** E. A. Emerson, C.-L. Lei. *Modalities for model checking:
  branching time logic strikes back.* Sci. Comput. Program. 8 (1987)
  275–306. (Thm 4.7: the fair-state problem under a general
  canonical-form fairness constraint is NP-complete.)
- **[KVBS98]** T. Kam, T. Villa, R. K. Brayton,
  A. Sangiovanni-Vincentelli. *Multi-valued Decision Diagrams: Theory
  and Applications.* Int. J. Multiple-Valued Logic 4(1–2) (1998) 9–62.
- **[MD15]** T. Michaud, A. Duret-Lutz. *Practical Stutter-Invariance
  Checks for ω-Regular Languages.* SPIN 2015.
- **[MMPTV95]** O. Matz, A. Miller, A. Potthoff, W. Thomas,
  E. Valkema. *Report on the Program AMoRE.* Tech. Rep. 9507, CAU
  Kiel, 1995. ⟨not yet in the library⟩
- **[PP04]** D. Perrin, J.-É. Pin. *Infinite Words: Automata, Semigroups,
  Logic and Games.* Elsevier, 2004.
- **[SωS26]** Y. Thierry-Mieg, with Claude (Anthropic). *Constructing
  the syntactic ω-semigroup from a deterministic Emerson–Lei automaton.*
  To appear, 2026.
- **[TMPHK09]** Y. Thierry-Mieg, D. Poitrenaud, A. Hamez, F. Kordon.
  *Hierarchical Set Decision Diagrams and Regular Models.* TACAS 2009.
- **[WHH+06]** R. Wimmer, M. Herbstritt, H. Hermanns, K. Strampp,
  B. Becker. *Sigref — A Symbolic Bisimulation Tool Box.* ATVA 2006.
  ⟨not yet in the library⟩
