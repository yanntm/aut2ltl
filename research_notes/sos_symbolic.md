# A Symbolic Engine for the Syntactic ω-Semigroup: Why the Construction Is Decision-Diagram Shaped

**Yann Thierry-Mieg**

With significant inputs from
**Claude (Anthropic)**

*Working draft — 2026-07-12 — placeholders marked `⟨TBD: …⟩`*

## Abstract

The construction of the syntactic ω-semigroup from a deterministic
Emerson–Lei automaton [SωS26] is dominated by one exponential object:
the acceptance-enriched monoid `EM(D)`, worst-case
`(|Q|·2^{|C|})^{|Q|}`, and PSPACE-hardness makes some wall a
mathematical necessity. We present the first symbolic
(decision-diagram) computation of a syntactic algebra: an enriched
element is a `|Q|`-slot vector over the small domain `Q × 2^C`, the
monoid is the reachability set of the identity vector, residuals and
congruence are partition-refinement fixpoints, and the rotation lemma
of [SωS26] — the two-sided congruence yields to right moves alone —
guarantees that every relation the construction *iterates* is
slot-local: the algebraic economy and the symbolic feasibility are
one fact. Decision diagrams are empirical tools, so the paper's
claims are measured ones, organized around five research questions.
**Correctness** (RQ1): the engine's exported invariant is
byte-identical to the explicit reference construction's on all 6102
census instances both tools complete — wholesale, not sampled.
**Compression** (RQ2): on that unstructured census the diagram holds
the monoid at 0.29× its explicit cell count at the median — a
constant factor, never exponential, with per-slot value sharing the
dominant predictor of the margin. **The exponential** (RQ3): on
`n`-fold asynchronous products the factored diagram is `9n + 1` nodes
carrying `16ⁿ` elements, measured to `n = 6`, while flat encodings of
the same monoid are provably exponential in row-major orders and
observably hit that wall at `n = 3` — the win exists and is
conditional on slot coordinates that inherit the product shape.
**Cost** (RQ4): the engine carries algebras to 12 225 elements under
a 10-second budget and loses exactly the structureless census tail
to explicit enumeration, as the theory predicts it must.
**Amortization** (RQ5): the table built by the acceptance-free phases
serves every language over the same marked semiautomaton — lasso
membership that never closes the monoid and a same-table Boolean
algebra are measured, commutation-exact against from-scratch builds;
the wider calculus (alignment by variable-block concatenation,
inclusion with canonically minimal witnesses, rootings) is designed
and specified. The exponential does not disappear; it is represented
— when, and only when, the input has the structure engineered
systems have.

---

## 1. Introduction

[SωS26] constructs, from a deterministic Emerson–Lei automaton `D`,
the syntactic ω-semigroup of its language: a finite, canonical,
presentation-independent invariant `𝓘(L)` from which LTL-definability
and the rest of the classification landscape (the safety–progress
ladder, the Wagner degree) are polynomial read-offs. Its complexity
section ends on a promissory note: the construction's ingredients are
all Boolean, its steps all images, fixpoints and quotients over sets,
"native to decision diagrams". This paper is the note called in.

The cost profile is lopsided in a way worth stating plainly.
Everything *around* the enriched monoid is polynomial: the seed
relations, the partition refinement, every §7 read-off of [SωS26],
and the exported invariant — often tiny — at the end. The single
exponential object is `EM(D)` itself, the monoid of `|Q|`-slot
vectors the construction closes under composition, worst-case
`(|Q|·2^{|C|})^{|Q|}`; and by PSPACE-hardness [CH91] no
representation removes that worst case. The thesis is the symbolic
model checker's: do not enumerate the set, *represent* it; pay per
diagram node, not per element; and let the structure of engineered
inputs — which are products, sparse in marks, symmetric in letters —
collapse what adversarial inputs cannot.

A thesis of that kind is settled empirically or not at all. Decision
diagrams carry no useful size theorem: the same set is linear or
exponential depending on the variable order, intermediate ("peak")
diagrams can dwarf final ones, and the field's forty years are a
literature of structure bets checked on benchmarks. The paper is
therefore built around five research questions, and its evaluation
(§8) is organized as their answers:

- **RQ1 (correctness).** Does the symbolic pipeline compute the same
  canonical object as the explicit reference construction — not on
  samples, but wholesale?
- **RQ2 (compression).** On ordinary, unstructured inputs, how far
  below explicit storage does the diagram sit, and what structure
  predicts the margin?
- **RQ3 (the exponential).** Is there an input family on which the
  symbolic representation is exponentially smaller than explicit
  storage — and what does reaching it require of the encoding?
- **RQ4 (cost).** What does construction cost, where does it die,
  and when does plain explicit enumeration win?
- **RQ5 (amortization).** Does the expensive object amortize — one
  table serving many languages and operations — or is it rebuilt per
  use?

**Contributions.**

1. **A symbolic syntactic-algebra engine, correct wholesale**
   (§2–§3). The construction factors through five primitives standard
   in symbolic model checking: closure as reachability, idempotent
   powers as a pairing fixpoint with a logarithmic squaring shortcut,
   profiles as one slot-read, residuals as an internalized refinement
   (no external language-equivalence oracle), the congruence as
   greatest-fixpoint partition refinement, the quotient explicit on
   the small side. To our knowledge this is the first decision-diagram
   computation of a syntactic algebra, on finite or infinite words
   (§9). The exported invariant is byte-identical to the explicit
   reference's on every census instance both tools complete (RQ1):
   the engine changes representation, never mathematics.

2. **A characterization of when representation beats enumeration**
   (§4). The existence condition is the rotation lemma of [SωS26]
   re-read as a *locality* theorem: every relation the construction
   iterates is slot-local, and the two slot-crossing reads sit
   outside every fixpoint (§4.1). The best case is exact: for
   asynchronous products the enriched monoid factors (Proposition
   4.1), so factored slot coordinates give additive diagrams for
   multiplicative cardinality — measured as an equality (RQ3) —
   while flat coordinates are provably exponential under row-major
   orders (Lemma 4.2), observed exactly there, the any-order question
   posed as Conjecture 4.3. Off the best case the win is a constant
   factor with an identified predictor, per-slot sharing (RQ2); and
   the census tail the engine loses to explicit enumeration is
   exactly the structureless world where §4.3 predicts it must lose
   (RQ4).

3. **The table as substrate** (§6). Phases 0–2 never read the
   acceptance condition, so their product — the closure and the
   `π`-map — serves *every* language over the same marked
   semiautomaton, with a commutation theorem (Proposition 6.0)
   licensing on-demand canonicity. Two moves are measured (RQ5):
   lasso membership that never builds the monoid, and a same-table
   Boolean algebra whose derived invariants are byte-identical to
   from-scratch builds. The cross-table calculus — alignment by
   variable-block concatenation, inclusion as one query with a
   canonically minimal witness (Propositions 6.1–6.2), rootings and
   inverse substitutions — is designed and specified; its measurement
   is named open.

Position: this engine is the entry gate to everything [SωS26] enables —
its §7 read-offs all run on the small quotient the gate emits — and §6
makes the gate a workshop: a pipeline that complements, conjoins,
quotients, checks and re-checks a specification can stay symbolic
throughout and reduce once at the end.

§2 recalls the construction and fixes the abstract engine and the
symbolic input; §3 gives the encoding phase by phase, each with its
correctness proposition; §4 the locality and shape analysis behind
RQ2/RQ3; §5 the cost model behind RQ4; §6 the calculus behind RQ5;
§7 the scope boundary; §8 the evaluation, by research question; §9
related work. Material parked during restructuring is in Appendix A.

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

**The enriched monoid** [SωS26, Def 3.1]. The enriched element of a
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
(states without marks) does not recognize `L` [SωS26, Prop 3.4].

**Recognition and the oracle.** If two ω-words factor into blocks with
the same sequence of enriched images from `ι`, they agree on `L`
[SωS26, Lemma 3.2 (skeleton)]; consequently the syntactic morphism
factors through `⟦·⟧` and the syntactic ω-semigroup is a quotient of
`EM(D)` [SωS26, Cor 3.3]. For a lasso, acceptance collapses to one
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
`~ = ~lin ∧ ~ω` [SωS26, Prop 4.3]: `e ~lin f` iff
`L(st_e(q)) = L(st_f(q))` at every slot `q` (residual agreement —
mark parts irrelevant), and `e ~ω f` iff the **profiles**
`Aprof(e·b) = (q ↦ A(q, e·b))` agree under every right extension `b`.
The **rotation lemma** [SωS26, Lemma 4.4] — a left factor `a` turns
into a right extension read at the shifted slot,
`Aprof(a·e·b)(q) = Aprof(e·b·a)(st_a(q))` — makes `~` the coarsest
*right-invariant* refinement of the seed (`~lin`-class, `Aprof`), so
one Moore-style partition refinement computes it [SωS26, Thm 4.5]:
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
design confines it to one-shot, never-iterated uses: built in Phase 2,
consumed once more by Phase 3's verdict read.

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
the packed value `(q, S)` is one multi-valued variable (split
encodings — state above marks, interleaved — are §8's order study).

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
budget — a different resource, and the subject of RQ2–RQ4 (§8). The slogan: **closing a monoid under generators is not
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
- *Squaring shortcut*: repeated **squaring** `z ← z·z` reaches `x^π`
  in `O(log ℓ)` rounds whenever it converges, and its convergence is
  exactly characterized: `x^{2^j}` stabilizes iff `2^j` passes the
  orbit's index *and* the orbit's period divides `2^j`, so the
  iteration converges **iff every orbit period is a power of two** —
  the entire aperiodic (LTL-definable) side of the frontier
  [SωS26, §7] included, but not only it, so squaring is a shortcut,
  never a verdict; the aperiodicity verdict itself is read on the
  small quotient, where it belongs. The squaring step is genuinely
  simultaneous — every slot written while every slot is read — which
  no assignment-shaped operation renders; instead the squaring map is
  materialized **once** as a `2k`-variable relation
  `Sq = {(z, z·z) : z ∈ EM¹}`: double each element variable into an
  adjacent (pre, post) pair and apply one `Comp` case split whose
  guards and right-hand sides read only pre variables — written and
  read variable sets disjoint, so simultaneity is vacuous. Every power
  `x^{2^j}` stays inside `EM¹`, so the one relation serves all rounds,
  each round a relational image (primitive 3), and a
  `⌈log₂|EM¹|⌉ + 1` round cap decides divergence: past it, an orbit
  that has not stabilized never will.

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
`ProfR(x, q) ∈ {0,1}` is the composition of the `π`-map with a
*value-indexed* slot read — slot `q` names the state
`p = st_{x^π}(q)`, and it is slot `p`'s mark component that `Acc`
consumes: a `|Q|`-way case split of Phase 2's shape, applied to the π
pair space. One round, `|Q|` applications, outside every fixpoint —
but crossing-priced per application, and since the π pair space is
the largest diagram in the pipeline, this read is the expected second
cost peak after Phase 2 itself (§5, §8). (This is [SωS26, Lemma
4.1]'s `A(q, c)` — the walk-the-cycle prose there is the explicit
rendering; idempotency makes the symbolic rendering a lookup.)

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
ultimately-periodic words, which is language equality. The seed is
cheaper than the formula reads: materialize per state the **profile
column** `S_q = { x ∈ EM : A(q, x) }` — one predicate application of
`ProfR` to the element diagram — and two states agree on *every*
element iff `S_q` and `S_{q′}` are the **same node** of the unique
table. Canonicity turns the per-pair universal quantification into
`|Q|` predicate applications plus `O(1)` comparisons; the refinement
is over the tiny space `Q × Q`. The engine is oracle-free end to end.

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

- **Class table**: the quotient hands each class a representative
  element; the multiplication table and the letter map are evaluated
  on representatives on the small side — slot-local composition of
  explicit points, never Phase 2's crossing relation. Canonical ids
  and keys then cost nothing extra: a shortlex BFS **over the quotient
  algebra itself** — `step(κ, α) = M(κ, λ(α))` from `[ε]`, letters in
  canonical order — names every class by the first word that reaches
  it, which is its shortlex-least key, and its discovery order is the
  id order. The layer-indexed extraction walk (the minimal layer gives
  the length; backward preimage sets; a *forward* least-letter walk —
  a backward letter choice would minimize the wrong end) is not needed
  for the table; it is the witness reader of §6.4.
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

**The identity convention.** `[ε]` is adjoined **fresh**: word classes
are the `~`-classes of the images of *non-empty* words — the identity
element counts among them exactly when some non-empty word folds onto
it — and the class of the empty word is a separate class that no word
can collide with, a two-sided unit in `M`. Quotienting `EM¹` wholesale
would instead merge `[ε]` with `[w]` whenever `⟦w⟧` happens to equal
the identity element (`!a` in a one-state automaton of `GF a` already
does), making the class count presentation-dependent; the fresh class
is what makes the export canonical.

The output is the explicit, canonical `𝓘(L)` — the exponential
intermediate never exists outside its diagram, and is discarded with it.

**Correctness, wholesale.** Each phase computes an object [SωS26]
*defines*; the engine changes representation, never mathematics. One
proposition per phase:

**Proposition 3.1 (closure).** The lfp of Phase 1 equals
`{ ⟦w⟧ : w ∈ Σ* }`, and its layer `i` holds exactly the elements whose
shortest representative word has length `i`.
*Proof.* `R(α; x, x′)` holds iff `x′ = x·⟦α⟧` (compare slotwise with
[SωS26, Def 3.1]'s composition law). By induction on `i`, the `i`-th
BFS frontier is `{ ⟦w⟧ : |w| = i } ∖ (earlier layers)` — exactly the
elements first reached at length `i`. The fixpoint is the union: every
`⟦w⟧` is reached in `|w|` steps, and nothing else is. ∎

**Proposition 3.2 (idempotent powers).** Phase 2's relation maps each
`x` to `x^π`, the unique idempotent among its powers.
*Proof.* The pairing lfp closes `{(x, x)}` under `(x, y) ↦ (x, y·x)`,
so it holds `{(x, x^j) : 1 ≤ j ≤ orbit length}`; the cyclic
subsemigroup `{x^j}` of a finite monoid contains exactly one idempotent
[PP04], so the `Idem`-filtered selection is functional and equals `π`.
For the squaring shortcut: `x^{2^j} = x^π` iff `2^j ≥` the orbit's
index and the orbit's period divides `2^j`; both conditions are
settled — if they ever hold — once `2^j ≥ |EM¹|`, so the capped
iteration converges exactly when every orbit period is a power of two,
in `O(log ℓ)` rounds. ∎

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
congruence `~` of [SωS26, Thm 4.5].
*Proof.* `Seed` is exactly Lemma 4.4's seed `R`: its first conjunct is
`~lin` (residual agreement at every slot, by Prop. 3.4), its second is
`Aprof(x) = Aprof(x′)` (by Prop. 3.3). The gfp with letter-preimage
refinement computes the coarsest right-invariant refinement of `Seed`,
which the rotation lemma [SωS26, Lemma 4.4] identifies with the
two-sided congruence `~`. ∎

**Proposition 3.6 (exports).** Phase 6 emits `𝓘(L) = (𝒞, λ, M, P)` of
[SωS26, Thm 5.1].
*Proof.* `𝒞` is the word-class quotient of Prop. 3.5's `~` (with the
fresh `[ε]`) by [SωS26, Thm 4.5]; the BFS keys are shortlex-least
because breadth-first discovery with letters taken in canonical order
reaches each class first by its length-least, then lex-least word;
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
one node per distinct slot-0 value with shared slot-1 suffixes. The
closed `EM¹` holds in **10 diagram nodes** against the 32 explicit slot
cells (the run-parity form of `GF(aa)`: 5 nodes for 20 cells). The
`n`-fold asynchronous product of `EvenBlocks` in factored coordinates
makes Proposition 4.1 visible: the diagram is literally additive —
**`9n + 1` nodes** carrying `16ⁿ` elements, so at `n = 3` a 28-node
diagram stands where the explicit table has `16³ = 4096` rows (the
measured line is §8's, RQ3).

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
first row; the third-row uses — Phase 2's pairing/squaring and Phase
3's one-round verdict read — are preprocessing, outside every
fixpoint. That is
the precise sense in which "everything is a right move" is not an
algebraic elegance but the existence condition for this engine. A
secondary dividend: because the first row is one identical local
relation conjoined per slot, the fixpoints of Phases 1 and 5 have
exactly the shape event-locality-based fixpoint accelerations were built
for — saturation [CLS01] and its hierarchical descendants [TMPHK09];
whether they beat the BFS order here is an open §8 measurement (RQ4),
with one caveat already visible: Phase 1's layers are load-bearing (shortlex,
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
product-form is an open empirical column (§8, RQ3). Two further
compression sources are unconditional:

- **Constant and shared slots.** The completion sink is the same slot
  value in every element — one diagram node, ever; transient states
  reached alike shared across elements likewise.
- **Monotone marks.** Per slot, the mark set only grows along right
  extensions, and the growth pins a closure fact: write
  `F(q, d) = { mk_x(q) : x ∈ EM¹, st_x(q) = d }` for
  the mark family at slot `q` with destination `d`, and
  `M(d) = { mk_y(d) : y ∈ EM¹, st_y(d) = d }` for the mark sets of
  `d`'s stabilizers. The composition law gives, for `st_x(q) = d` and
  `st_y(d) = d`, `(x·y)(q) = (d, mk_x(q) ∪ mk_y(d))` — so `F(q, d)`
  is closed under union with every member of `M(d)`: a union of
  up-sets in the lattice the stabilizer marks generate. Full upward
  closure in `2^C` — the classically diagram-friendly case — holds
  exactly when the stabilizer marks realize every single-mark
  increment; measured on the census corpus, 62 % of non-empty
  `(slot, dst)` families are fully upward-closed. A real tendency —
  though as a *predictor* of compression it ranks well below slot
  sharing (§8, RQ2).
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
the practical inputs inhabit; RQ3 and RQ4 (§8) ask whether the `|Q|`
exponent *moved* — from cardinality, where it provably lives, to
diagram width, where structure fights it.

## 5. The pipeline, costed

| phase | computes | primitive | relational shape | rounds |
|---|---|---|---|---|
| 0 | `Lett`, `R` | build from `Δ, Mk` | slot-local, `2k + AP` | — |
| 1 | `EM¹` + layers | lfp, image | slot-local | closure depth `≤ \|EM\|` |
| 2 | `π`-map | pairing lfp / squaring | **crossing** (`\|Q\|`-way split) | `O(ℓ)`; `O(log ℓ)` when periods are powers of two |
| 3 | `ProfR` | compose + predicate | **crossing-shaped** read (value-indexed slot select) + `Acc` | 1 (× `\|Q\|` applications) |
| 4 | `≃` | gfp on `Q × Q` | small; seed: `\|Q\|` profile columns + `O(1)` compares | `≤ \|Q\|` |
| 5 | `~` | gfp refinement | slot-local preimages, `∀α` | `≤ \|EM\|` splits |
| 6 | `𝓘(L)` | quotient + algebra BFS | small, explicit | `\|𝒞\|·\|Σ\|` table steps |

Every round is polynomial in the *diagram sizes* of its operands — the
symbolic contract; the open quantity is the diagrams themselves
(§8, RQ2–RQ4).
Two structural notes. The closure depth of Phase 1 equals the length of
the longest shortlex-minimal representative, `< |𝒞|` *after* quotient
collapse but up to `|EM|` before it — and in practice it is small: on
the census corpus the pre-quotient depth has median 6, p99 16, max 27
(reached at `|EM¹| = 3291`), never exceeds `0.6·|EM¹|` (0.22 at the
median), and sits below the *post*-quotient class count on 98.6 % of
instances. And Phase 5's split count is bounded by
`|EM|` but its *effective* rounds end at the syntactic partition — the
same early-stabilization phenomenon symbolic bisimulation minimization
exploits [BdS92], and signature-based refinement [WHH+06] is the
engineered form of exactly Phase 5's shape: a per-element signature
(here: `Seed`-class plus letter-successor classes) recomputed to
fixpoint.

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
*pay canonicity only when canonicity is consumed*. Of the moves
below, membership (§6.1) and the same-table algebra (§6.2) are
measured (§8, RQ5); the cross-table moves (§6.3–§6.5) are designed
and specified, their measurement open.

### 6.1 Lasso membership, closure-free

`u·v^ω ∈ L(D)?` Fold both words: `|u| + |v|` applications of the
right-multiplication relation, `α` fixed to the letter read, to
singleton sets starting at `{⟦ε⟧}` — on a singleton every relation is
a concrete function, each image a
singleton — giving `c = ⟦u⟧`, `d = ⟦v⟧` as explicit slot vectors; then
`d^π` by concrete power iteration (at most `ℓ` compositions, `O(log ℓ)`
by squaring in the aperiodic case), one slot read, one `Acc`
evaluation. The verdict is `Val(c, d)` — and **Phase 1 never ran**: a
membership query builds no monoid, touches no fixpoint. (On a
deterministic input, running the automaton around the lasso answers
the same bit at the same cost — what the fold buys is the *elements*
`c, d`, which land in the algebra ready to be rooted, compared, and
canonicalized; the longer comparison is parked in Appendix A.)

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
need the two languages on one table, and §4.2 has already drawn it:
concatenate the slot blocks, conjoin the letter relations on the
shared `α`-block (distinct `AP` sets merge by union, and the merge is
free — each `Δᵢ` simply does not mention the other's variables), and
run Phase 1's lfp. The reachable set is exactly the submonoid of
`EM(D₁) × EM(D₂)` generated by the diagonal letter pairs — the
*generated alignment product*, computed on-the-fly in the factored
coordinates §4.2 prescribes. Verdicts lift blockwise:

**Proposition 6.1 (idempotent powers factor through blocks).** For an
aligned element `x = (x₁, x₂)`, `x^π = (x₁^π, x₂^π)`.

So the aligned `π`-map is per-block, Phase 2 — the pipeline's one
crossing — is never run on the multiplicative aligned space, `Valᵢ`
reads block `i` alone, and cross-table union, intersection and
difference are pointwise `∨ / ∧ / ∧¬` of per-block verdict
predicates — no degeneralization counters, no acceptance-condition
surgery: acceptance never left predicate form. (Proof and the full
construction: Appendix A.)

### 6.4 Inclusion, equivalence, emptiness: one query, minimal witness

Since ω-regular languages are determined by their ultimately periodic
words (§2.1), on the aligned table

```
L₁ ⊆ L₂   ⟺   ∀ c, d ∈ EM_⊗ :  Val₁(c, d) → Val₂(c, d)
```

and the check factors into two reads the engine already knows: the
projection `S = { (st_c(ι₁), st_c(ι₂)) : c ∈ EM_⊗ }` onto the small
space `Q₁ × Q₂` — recognizably the classical reachable product state
space, recovered as a *projection of the monoid* — then one
intersection:

```
Bad  =  S(q₁, q₂)  ∧  ProfR₁(q₁, d)  ∧  ¬ProfR₂(q₂, d)
```

with both `ProfR`s Phase-3 objects of the aligned table; `L₁ ⊆ L₂`
iff `Bad = ∅`. The query composes relations already built and is
never iterated. Equivalence is two inclusions or byte equality after
reduce; same-`D` pairs skip alignment; emptiness and universality
are the degenerate predicates. A nonempty `Bad` carries its own
counterexample, and the kept layers make it canonical:

**Proposition 6.2 (minimal witness).** If `L₁ ⊄ L₂`, the layer-driven
selection — least stem layer, then least loop layer, then the coupled
lex-least forward walks of Phase 6's extraction mechanism — yields
`u·v^ω ∈ L₁ ∖ L₂` with `(u, v)` the least separating lasso
presentation in (stem length, loop length, stem lex, loop lex) order.

(Selection algorithm and proof: Appendix A.) Every decision procedure
of this section thus emits the minimal certificate, deterministically
— a discipline automata-side counterexample extraction does not have.
One pricing note survives the compression: automata-side emptiness
under an arbitrary Emerson–Lei condition is NP-complete in the
condition [EL87, Thm 4.7]; here idempotency dissolved the accepting
cycle into a slot read and the Boolean structure into a predicate on
one slot's mark bits, absorbed into the same diagram-size bet as
everything else, not paid as a separate search.

### 6.5 Rootings and relabelings

`u⁻¹L` is a re-parameterization, not surgery: fold `u` (§6.1) and
move the initial slot to `q_u = st_{⟦u⟧}(ι)`; quotients compose as
`st` composition, and the distinct rootings are Phase 4's
`≃`-classes — the residual automaton, internalized. Inverse
substitutions, and more generally inverse non-erasing homomorphisms
`h⁻¹(L)`, substitute the `α`-block: the new generators are folds
`⟦h(a)⟧` — elements of the *old* monoid — so the re-closure lfp runs
constrained inside the existing diagram, and inverse homomorphic
images never leave it. (Full construction: Appendix A.)

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
- **The AP set is part of the object.** `𝓘(L)` is keyed over a
  declared `AP`, and byte equality is same-AP equality: a language
  indifferent to a declared proposition still carries it. Reducing an
  input to its support APs is an input normalization a front end may
  apply — not the engine's business, and not part of the invariant.
- **Not simulated.** Branching semantics — games, synthesis — are out:
  the invariant is a linear-time object. And canonicity has a price
  ceiling: `𝓘(L)` can be exponentially larger than a good
  nondeterministic presentation, so the calculus is not a back-end for
  one-shot translations; it is the substrate for pipelines that *keep*
  a language and work on it.

## 8. Evaluation

Decision diagrams are empirical tools: no theorem makes a diagram
small, and a symbolic algorithm is judged by what its inputs'
structure does to its variables. This section therefore answers the
five research questions of §1 in turn. Protocols, per-instance data
and the finding ledger live in the companion experiment report — the
reproducibility artefact — and every number below is traceable to a
tracked, machine-generated artefact there.

**Setup.** The engine: multi-valued decision diagrams (libDDD),
letter steps as per-slot homomorphism sums, the crossing as the
`|Q|`-way case split over expression homomorphisms, the squaring
relation as §3 describes, Phase 6 explicit on the small side. The
reference: the explicit implementation of [SωS26], whose emitted
invariant is the conformance oracle. The corpus: a census of 6222
canonical deterministic Emerson–Lei automata (`|Q| ≤ 3`, ≤ 2 APs) —
deliberately the *unstructured* world: enumerated shapes, no product
seam to exploit. The scaling family: `EvenBlocks^{⊗n}`, the `n`-fold
asynchronous product of §3.1's specimen, in factored and flat slot
coordinates. Budget: 10 s per instance unless stated; a blown budget
is a datum, and a run beyond the reference's own cap is `UNVERIFIED`
and never promoted to a correctness claim.

### RQ1 — Is the symbolic construction correct in practice?

**Yes: byte-identical to the reference, wholesale.**

| census instances | completed (10 s) | byte-identical | mismatches |
|---|---|---|---|
| 6222 | 6102 | **6102** | **0** |

On every instance where both tools complete and share the declared
AP set (§7), the exported `.sos` is byte-identical after canonical
keying: the same canonical object, so every downstream
classification read-off of [SωS26, §7] transfers unchanged. The gate
is not a sample — it is the census. The 120 non-completions are
budget kills, taken up under RQ4.

### RQ2 — How small is the representation on unstructured inputs?

**A constant factor below explicit storage — 3.4× at the median —
and never exponential in either direction.** Explicit storage of
`EM¹` is `|EM¹| · |Q|` slot cells; the final diagram sits at or
below that on 6100 of 6102 completed instances (the two exceptions
are 1-element algebras against the diagram's 2-node root+terminal
floor).

| node-to-cell ratio | p5 | median | p95 |
|---|---|---|---|
| census, 6102 completions | 0.12 | 0.29 | 0.50 |

On the worked specimens: `EvenBlocks` holds its 16-element `EM¹` in
10 nodes against 32 cells; the run-parity form of `GF(aa)`, 5
against 20. One direction of the question is structural rather than
empirical: a *final* diagram exponentially larger than the explicit
table cannot occur — a set of `k` vectors of length `m` fits in a
trie of `O(k·m)` nodes, and reduction only shrinks it — so the
empirical content is the margin and its predictor. Rank-correlating
structure against the ratio (Spearman, over the census):

| covariate | ρ vs node-to-cell ratio |
|---|---|
| per-slot sharing (distinct-cells / cells) | **+0.73** |
| `\|EM¹\|` | −0.66 |
| closure depth | −0.59 |
| marks | −0.51 |
| letter classes | −0.41 |
| states | −0.30 |
| upward-closed mark fraction | +0.19 |
| constant slots | +0.16 |

Per-slot sharing dominates, and there is much to share: the mean
distinct-cells-to-cells ratio is 0.039 — per-slot value reuse alone
collapses the explicit table to ~4 %. Larger and more-marked
algebras compress relatively better. The §4.2 monotone-marks
tendency is real (62 % of non-empty `(slot, dst)` families fully
upward-closed) but is a structure datum, not a compression
predictor.

### RQ3 — Where is the exponential, and what does reaching it require?

**Observed: an exponential separation on product inputs — conditional
on slot coordinates that inherit the product shape.** On
`EvenBlocks^{⊗n}`, Proposition 4.1 is measured as an equality:

| `n` | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| `\|EM¹\| = 16ⁿ` | 16 | 256 | 4 096 | 65 536 | 1 048 576 | 16 777 216 |
| factored nodes `= 9n+1` | 10 | 19 | 28 | 37 | 46 | 55 |
| flat nodes | 10 | 258 | > 2 954 † | — | — | — |

† the flat build at `n = 3` exhausts its per-point budget mid-closure
(layer 9 of the fixpoint, diagram still growing) — Lemma 4.2's wall,
observed where it is proved. All factored points complete in under
60 ms; the interleaving isomorphism is verified element-exactly
through `n = 4`.

The conditionality is the standard decision-diagram caveat, and we
state it as a result rather than a disclaimer: the same monoid is
linear or exponential *depending only on the variable order*.
Factored coordinates were given to the engine here, not discovered by
it; row-major flat orders are provably exponential (Lemma 4.2); and
whether any flat order escapes is open (Conjecture 4.3). A first
sensitivity datum points the same way: block-preserving permutations
of the factored order are node-neutral (19 nodes at `n = 2` under
identity and reversal alike), while a block-interleaving rotation
inflates the same set to 82 — slot *grouping* is what matters,
within-block order is second-order. Open: the systematic order study
(grouping strategies × within-slot encodings) and the synchronous
half — how far engineered synchronizations drift from product form.

### RQ4 — What does construction cost, and when does explicit enumeration win?

**The engine carries the census at 0.27 s per instance on average,
tops out — under 10 s — at a 12 225-element algebra, and loses
exactly the 1.9 % of instances with the least structure to exploit.**
Totals: 1 647 s over the 6 102 completions. The largest completed
algebra has `|EM¹| = 12 225`; census-wide, syntactic class counts
are small (median 15, maximum 148), so quotient-size scaling beyond
a few hundred classes is untested — a named boundary of everything
this section reports. Squaring, where its convergence condition
holds, reaches `π` in 2 rounds against the pairing's 2–5; where an
orbit period is not a power of two, the round cap detects divergence
and the pairing carries — the shortcut is measured as a shortcut,
never trusted as a verdict.

The 120 budget kills concentrate on the largest sampled shape
(101/120 on the 3-state 2-AP parity class); their kill-phase counts
are 52/32/21/15 in Phases 1/3/5/2. Two caveats bound what this
shows. First, a kill histogram is right-censored — an instance dying
in phase `p` charges its unknown upstream spend to `p` — so it
proves Phases 3 and 5 are macroscopic at the tail (as Phase 3's
crossing shape predicts, §5) but cannot populate §5's cost table;
the uncensored per-phase profile is open. Second, the explicit
reference completed all 120 of these instances under its own,
unequal conditions: on this census (`|Q| ≤ 3`, enumerable, no
product seam — §4.3's world) the engine has no structural advantage
and should be expected to lose small-budget rows. The controlled
bottom line is open and pre-registered: both tools on the same
machine under the same wall budgets, all failure kinds reported on
both sides, plus the crossover point on the scaling families where
explicit `16ⁿ` enumeration must cap — with the stated expectation
that the engine's win column lives on structured inputs, not the
census.

### RQ5 — Does the table amortize: is the calculus real?

**The acceptance-indifferent substrate and its same-table moves are
measured; the cross-table calculus is designed, its measurement
open.** Both measured moves pass the Prop 6.0 commutation gate —
op-then-reduce byte-identical to reduce-then-op:

- *Membership without closure* (§6.1): across seven instance/rooting
  cases × 210 lassos each, the fold's verdict agrees with an
  independent explicit lasso simulation and with the engine's own
  Phase 3 read; the closure-free claim holds structurally — the
  membership path cannot invoke the fixpoint machinery at all.
- *The same-table Boolean algebra* (§6.2): complement, union,
  intersection and difference as predicate moves, no diagram work;
  every derived invariant tried is byte-identical to the
  from-scratch build of the operated language — and, on two cases,
  to the explicit reference of the operated input itself; double
  complement returns the original bytes; the reduce is observed lazy
  (the acceptance-dependent phases run on the first
  verdict-consuming read, not before).

Open: alignment (§6.3) at scale; the inclusion query with its
minimal-witness gate (§6.4 — Prop 6.2's extraction checked against
brute-force lasso enumeration); rootings and substitutions (§6.5);
and the deferred-reduce pricing — the measured column for "pay
canonicity only when consumed".

### The answers, in one place

| RQ | answer | open remainder |
|---|---|---|
| RQ1 correctness | byte-identical at census scale, 6102/6102, zero mismatches | — |
| RQ2 compression | constant factor (median 3.4×); per-slot sharing predicts the margin | — |
| RQ3 the exponential | observed (`9n+1` nodes vs `16ⁿ` elements); conditional on factored coordinates; flat provably and observably exponential | order study; Conjecture 4.3; synchronous distance |
| RQ4 cost | 12 225-element ceiling at 10 s; loses only the structureless tail | uncensored profile; budget-parity bottom line; quotient-size scaling |
| RQ5 amortization | substrate + same-table moves measured, commutation-exact | alignment, witness gate, deferred-reduce pricing |

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
original deliverable, is paid only when canonicity is consumed.

The answers so far stand where the bets were placed. The exponent
stays out of diagram width exactly when the coordinates inherit the
input's structure (RQ3); it degrades to a constant-factor margin
where there is no structure to inherit (RQ2); and it returns as a
time wall on the structureless tail, as it must (RQ4). What remains
open is named in §8's closing table — the order study, the
budget-parity bottom line, the calculus at scale — and each open
cell has its protocol fixed before its data exists.

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

---

## Appendix A — Parked material

Paragraphs moved out of the main text during restructuring, kept
verbatim for possible reuse and otherwise to be discarded. Nothing
here is part of the paper's argument; internal section references are
those of the revision that contained them.

### A.1 The former abstract

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
slot-read once idempotent powers are computed (a pairing fixpoint, with
repeated squaring a logarithmic shortcut exactly when the orbit periods
are powers of two — the aperiodic side included); the
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
The engine exists: its exported invariant is byte-identical to the
explicit reference construction's on every instance both complete —
measured at census scale, 6102 instances byte-identical — and
the factored bet is measured where it starts: `9n + 1` diagram nodes
carrying `16ⁿ` elements on the `n`-fold product family, against a flat
encoding that hits its proven exponential wall at `n = 3`; across the
census the diagram sits under the explicit cell count on all but two
floor cases (median 3.4×), with per-slot sharing the covariate that
predicts the margin (§8).

### A.2 The former introduction's claim block

[SωS26] ends its complexity section on a promissory note: the
construction's ingredients are all Boolean, its steps are all images,
fixpoints and quotients over sets, "native to decision diagrams". This
paper is the note called in — a design in which every step is named,
priced, and mapped onto a small abstract engine, and an implementation
whose exported invariant is byte-identical to the explicit reference
construction's (§8).

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
   relation: the crossings it needs — idempotent powers, and the
   verdict read that consumes them — sit outside every fixpoint. The
   algebraic economy and the symbolic feasibility are one fact.
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

### A.3 The symbolic-learner prospect (from §5)

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

### A.4 The per-move honesty digressions (from §6.1 and §6.4)

From §6.1: Honesty requires the comparison: on a *deterministic*
input a single membership is answered by just running the automaton
around the lasso, at the same cost. What the fold buys is not the bit
but the *elements* `c, d` — the same `|u|+|v|`-step computation is
the oracle every operation below composes with, its output lands in
the algebra (ready to be rooted, compared, canonicalized), where the
automaton-side run composes with nothing.

From §6.4: Honesty once more: with deterministic inputs,
automata-side inclusion is also polynomial (negate one acceptance
formula, product, emptiness). The claims here are different ones:
(i) the query runs on the factored diagram in cases where the flat
product state space is itself the explosion (§4.2); (ii) acceptance
stays a predicate — automata-side emptiness under an arbitrary
Emerson–Lei condition is NP-complete in the condition [EL87,
Thm 4.7], the accepting-cycle search growing with the Boolean
structure, while here idempotency dissolved the cycle into a slot
read and the Boolean structure into a predicate evaluated on one
slot's mark bits (Phase 3): that hardness is absorbed into the same
diagram-size bet as everything else, not paid as a separate search;
(iii) the witness is canonical-minimal by construction; (iv) the
same aligned table then serves every further operation on the pair.

### A.5 The former §6.3 body (alignment, in full)

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

### A.6 The former §6.4 witness selection and proof (in full)

First project the closure onto two slots: the set
`S = { (st_c(ι₁), st_c(ι₂)) : c ∈ EM_⊗ }` over the small space
`Q₁ × Q₂` — one image of the closure diagram, and recognizably the
classical reachable product state space, recovered as a *projection of
the monoid*. Then one intersection: `Bad`; `L₁ ⊆ L₂` iff `Bad = ∅`.
The query composes relations already built, introduces no new
relational shape, and is never iterated. Equivalence is two
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

*Proof of Proposition 6.2.* Separation: `Bad(st_c(ι₁), st_c(ι₂), d)`
for `c = ⟦u⟧`, `d = ⟦v⟧` says `Val₁(c, d) ∧ ¬Val₂(c, d)`, which is
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
`Val` (or its negation) in place of `Bad`, on the single table.

### A.7 The former §6.5 body (in full)

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

### A.8 The former §8 (Evaluation, in full)

The engine is built on multi-valued decision diagrams (libDDD): letter
steps as per-slot homomorphism sums, the crossing as the `|Q|`-way case
split over symbolic expression homomorphisms, the squaring relation and
its relational product as §3 describes, Phase 6 explicit on the small
side. Protocols, instance-level figures and the finding ledger live in
the companion experiment report (`sos_symbolic_spec.md` /
`sos_symbolic_report.md`); this section states what is measured and
what remains.

**Measured.**

- **Conformance, at census scale.** On every instance where the
  explicit reference construction terminates (and shares the input's
  declared AP set — §7), the engine's exported `.sos` is
  **byte-identical** to the reference's: the output is the same
  canonical object, so every downstream classification read-off
  transfers unchanged. Measured across the 6222-instance census
  corpus: all 6102 instances completing a 10 s budget byte-identical,
  zero mismatches; the 120 budget kills concentrate on the largest
  sampled shape and are the bottom line's tail (open column iii).
- **Compression, at census scale.** `EvenBlocks`: 10 diagram nodes
  against 32 explicit slot cells; the `GF(aa)` run-parity form: 5
  against 20. Across the census, the diagram sits at or under the
  explicit cell count on 6100 of 6102 completed instances (the two
  exceptions are 1-element algebras against the diagram's 2-node
  floor); the node-to-cell ratio has quantiles 0.12 / 0.29 / 0.50
  (p5 / median / p95). The scatter's correlates, by rank correlation:
  **per-slot sharing dominates** (mean distinct-cells-to-cells ratio
  0.039 — the sharing source is there to exploit), larger and
  more-marked algebras compress relatively better, and the
  monotone-marks fraction is a weak covariate — a structure datum,
  not a predictor (§4.2).
- **Factored scaling — Proposition 4.1 as an equality.**
  `EvenBlocks^{⊗n}` in factored coordinates: `|EM¹| = 16ⁿ` exactly at
  every `n ≤ 6`, on a diagram of exactly `9n + 1` nodes — additivity
  measured as an equality, not an order — with the interleaving
  isomorphism element-exact through `n = 4`. The same inputs in flat
  coordinates hit Lemma 4.2's wall already at `n = 3` (a time budget
  mid-closure with the diagram still growing); the divergence pair at
  scale is the variable-order study's.
- **Phase profile, small instances.** The crossing dominates as
  predicted; the Phase 4 seed does not — canonicity absorbs it into
  `|Q|` predicate applications (§3, Phase 4). Where squaring
  converges it reaches `π` in 2 rounds on every instance tried,
  against the pairing's 2–5; where it cannot (an orbit period that is
  not a power of two), the cap detects it and the pairing carries.
  At census scale the only profile signal so far is right-censored —
  the 10 s budget kills land in Phases 1/3/5/2 at 52/32/21/15 —
  enough to show the Phase 3 read is macroscopic at the tail (as its
  crossing shape predicts, §5), not enough to populate the cost
  table: open column (v).

**Open columns.** (i) synchronous products — distance of the reachable
set from product form; (ii) variable-order sensitivity, flat vs
factored and the split-encoding orders, on the same inputs — the §4.2
lower-bound picture empirically; (iii) the bottom line against the
explicit implementation under *budget parity*: instances the cap kills
that the diagram carries, and the converse — the census tail already
warns that the small-budget census column will not flatter the engine
(the census is the unstructured world of §4.3: `|Q| ≤ 3`, enumerated,
`|EM¹| ≤ 12 225`, where explicit enumeration is fast and there is no
product seam to exploit); (iv) the calculus in motion — a worked
multi-operation pipeline (complement, conjoin, check, re-check)
measured against per-operation automata constructions, and
deferred-reduce vs reduce-then-operate on the same sequence; (v) the
uncensored phase profile — per-phase time and peak nodes at census
scale and on the scaling families.
