# A Symbolic Engine for the Syntactic ω-Semigroup: Why the Construction Is Decision-Diagram Shaped

**Yann Thierry-Mieg**

With significant inputs from
**Claude (Anthropic)**

*Skeleton draft — 2026-07-07 — placeholders marked `⟨TBD: …⟩`*

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
exactly the statement that every relation the construction iterates is
**slot-local**: a conjunction of one identical small relation applied at
each slot. Closure is a least fixpoint; profiles collapse to a single
slot-read once idempotent powers are computed (one relational squaring);
the residual equivalence, delegated to an external language-equivalence
oracle in explicit implementations, *internalizes* as two quantifications
over the element set; the congruence is a greatest-fixpoint partition
refinement; and the final quotient — the only object anyone keeps — is
small and explicit. On an abstract engine offering set union/intersection,
comparison, `2k`-variable relations applied to `k`-variable sets,
constrained fixpoints, and quotient by an equivalence, the whole pipeline
is native. The exponential does not disappear; it is *represented*: the
compactness bet is that of symbolic model checking itself — vector sets
with shared structure, monotone mark components, constant sink slots, and
product-form systems whose enriched monoids factor slot-group-wise.
⟨TBD: experimental headline — DD size vs `|EM|` on the census corpus and
on structured families.⟩

---

## 1. Introduction

⟨TBD: full pass. The arc: [SωS26, §8] closes with a promissory note —
"every object and operation here is BDD-friendly" — and this paper is
the note called in. The three claims: (1) a precise factorization of the
construction into the five primitives of an abstract symbolic engine
(§2), with every iterated relation slot-local (§3); (2) the *reason* it
factors: the rotation lemma, proved in [SωS26] as an algebraic
convenience, is re-read here as the symbolic-locality theorem — left
multiplication and general composition cross slots, right multiplication
by a generator does not, and the construction needs the crossing
operation exactly once (idempotent powers), never inside a fixpoint (§4);
(3) the compactness sources and their limits — PSPACE-hardness [CH91]
says the worst case stands, structure says the practical case need not
look like it (§4.3). Position in the family: this paper is the entry
gate — the calculus [SωSC26] amortizes what this engine pays once; the
census [SωSN26] supplies the measurement corpus.⟩

## 2. Background, and the abstract engine

⟨TBD: compressed recall of [SωS26]: `D = (Q, ι, δ, C, Acc)` deterministic
complete Emerson–Lei; the enriched element
`⟦w⟧ : q ↦ (δ(q, w), mk(q, w))`; `EM(D)`; the two-relation seed and the
Moore refinement; the invariant `𝓘(L)` as output. Notation: `st_x(q)`,
`mk_x(q)` for the two components of slot `q` of an element `x`.⟩

**The engine.** We assume a symbolic store over typed variables
(Boolean-encoded or multi-valued) offering, natively:

1. **Set algebra** — union, intersection, difference of variable-sets;
2. **Comparison** — equality and inclusion tests (fixpoint detection);
3. **Relations** — a relation over `2k` variables, *applied* (image and
   preimage) to sets over `k` variables;
4. **Constrained fixpoints** — least and greatest fixpoints of monotone
   relation/set transformers, intersected with constraint sets;
5. **Quotient** — the quotient of a set or relation by an equivalence
   relation, with canonical-representative extraction.

This is the standard kit of symbolic model checking ⟨TBD: library
requests for the lineage — BDDs, symbolic reachability, symbolic
bisimulation minimization; cite after the biblio sweep⟩; nothing below
asks for more.

## 3. The encoding: five phases, one crossing

**The element space.** Fix the slot domain `V = Q × 2^C` (a state plus a
mark set — `log|Q| + |C|` bits). An enriched element is a point in
`V^Q` — `k = |Q|` variables, each of the small type `V` — and `EM(D)` is
a *set* of such points: one decision diagram, variable order by slot
⟨TBD: order heuristics; slot grouping for product systems, §4.2⟩. The
alphabet never appears in the element space: letters enter only through
relations, and `Σ = 2^AP` stays symbolic throughout — the guards of `D`
are already Boolean functions over `AP`, and every letter-indexed
operation below quantifies `AP` natively rather than enumerating `2^AP`
(the core paper's alphabet-friendliness claim, realized).

**Phase 1 — closure is reachability.** Right multiplication by a letter
`a` acts on an element slot-wise:

```
R_a(x, x′)  =  ⋀_{q ∈ Q}  [ x′_q = ( δ(st_x(q), a),  mk_x(q) ∪ mk(st_x(q), a) ) ]
```

— a `2k`-variable relation that is a **conjunction of one identical
local relation per slot**, each slot's update reading only that slot:
the cheapest shape a symbolic engine knows (a synchronous product of
identical local steps). Bundling the letter symbolically,
`R(α; x, x′)` over `AP ∪ slots ∪ slots′`, one relation serves the whole
alphabet. Then

```
EM(D)  =  lfp  X ↦ {⟦ε⟧} ∪ ∃α. R(α; X)
```

— the monoid *is* the reachability set of the identity vector in the
right Cayley graph, and the closure cap of explicit implementations
becomes the familiar art of symbolic reachability (layered BFS — whose
layers, kept, also hand out shortest representatives; saturation-style
orders; ⟨TBD: which discipline wins here⟩). This is the paper's first
slogan: **closing a monoid under generators is not like model checking;
it is model checking.**

**Phase 2 — the one crossing: idempotent powers.** General composition
`z = x·y` reads, at slot `q`, the `y`-slot *indexed by a value of `x`*
(`z_q = (st_y(st_x(q)), mk_x(q) ∪ mk_y(st_x(q)))`): a value-indexed slot
selection, the one operation that crosses slots — expressible as a
`|Q|`-way case split, but priced accordingly. The construction needs it
exactly once, outside every fixpoint: the **squaring relation**
`Sq(x, z) = Comp(x, x, z)`, iterated `O(log)` times per orbit to the
unique idempotent power, yields the map `x ↦ x^π` as a symbolic function
⟨TBD: the clean iteration scheme — repeated squaring lands on the
cycle; one more multiplication pass aligns to the idempotent; bound the
number of `Sq` applications by `O(log ℓ)` for maximal orbit length
`ℓ ≤ |EM|`⟩.

**Phase 3 — profiles are one slot-read.** For idempotent `e`, the
functional graph of `st_e` stabilizes in one step (`st_e ∘ st_e = st_e`:
images are fixed points), so iterating a loop of class `c` from `q` has
inf-set `mk_{c^π}(st_{c^π}(q))` — no orbit computation, no cycle
detection:

```
A(q, c)  =  Acc( mk_{c^π}( st_{c^π}(q) ) )
```

with `Acc`, a positive Boolean over `C`, applied as a small predicate on
the mark bits. The profile relation `ProfR(x, q)` (the verdict bit of
iterating `x` from `q`) is thus a composition of the `π`-map with one
slot selection and the `Acc` predicate.

**Phase 4 — the residual equivalence, internalized.** Explicit
implementations compute `q ≃ q′` (`L(q) = L(q′)`) by an external
language-equivalence oracle. Symbolically it falls out of the objects
already built: two states agree on every ultimately-periodic word iff
they agree on every (stem element, loop element) pair,

```
q ≃ q′   ⟺   ∀ b, c ∈ EM(D) :  A(st_b(q), c) = A(st_b(q′), c),
```

two universal quantifications over the element set — heavy, native, and
oracle-free. The engine needs no external language machinery anywhere.

**Phase 5 — seed, refinement, quotient.** The seed equivalence on
elements is slot-local given `≃` and `ProfR`:

```
Seed(x, x′)  =  ⋀_q  ≃( st_x(q), st_{x′}(q) )   ∧   ⋀_q  [ A(q, x) = A(q, x′) ]
```

and the syntactic congruence is a greatest fixpoint of partition
refinement using only the letter relations:

```
~  =  gfp  R ↦ Seed ∩ { (x, x′) : ∀α. (R_α(x), R_α(x′)) ∈ R }
```

— preimages under the slot-local `R_α`, the alphabet again quantified
symbolically. Finally primitive 5 quotients: canonical representatives
per `~`-class (BFS-least through the kept layers = shortlex keys), the
explicit table `M` by applying letters to representatives, `P` by the
linked-pair scan on the *small* quotient — the output `𝓘(L)` is explicit
and canonical, exactly [SωS26]'s object; the exponential intermediate
never exists outside its diagram.

**Correctness** is inherited, not re-proved: each phase computes the
object [SωS26] defines (closure, `A(q,c)` via the collapse lemma,
`~lin`/`~ω` seed, Theorem 4.5's refinement); the engine changes the
representation, never the mathematics. ⟨TBD: one proposition per phase
stating the computed set equals the defined object, each a two-line
appeal to the corresponding [SωS26] statement plus the idempotent
one-step-stabilization fact of Phase 3.⟩

## 4. Why this works: locality, compression, and the honest wall

### 4.1 The rotation lemma is the locality theorem

The construction's algebraic keystone — [SωS26, Lemma 4.4]: the
two-sided syntactic congruence is the coarsest right-invariant refinement
of the seed, so right multiplications suffice — is, re-read on the
encoding, a statement about *variable locality*:

- **right** multiplication by a generator updates each slot from itself
  (`R_a`: slot-local, the cheap relation);
- **left** multiplication by `a` reads slot `δ(q, a)` into slot `q` — a
  static slot permutation (structured, but crossing);
- **general** composition reads a slot selected by a runtime value — the
  expensive crossing.

A construction quantifying over two-sided contexts would iterate the
crossing operation inside its fixpoints; the rotation lemma confines the
construction to the slot-local relation, and the single crossing that
remains (idempotent powers, Phase 2) sits outside all fixpoints. That is
the precise sense in which [SωS26]'s "everything is a right move" is not
just an algebraic economy but the reason a symbolic engine exists at
all. ⟨TBD: sharpen into a statement — e.g. per-iteration DD-operation
bounds: slot-local image is linear in diagram size per slot type,
crossing is worst-case multiplicative; cite the engine literature after
the sweep.⟩

### 4.2 Where compression comes from

The bet is structural redundancy in `EM(D) ⊆ V^Q`, and its sources are
concrete:

- **Shared sub-vectors.** Elements agree on many slots (transient states
  reached alike; the completion sink is a constant slot in *every*
  element — one node in the diagram, ever).
- **Monotone marks.** Per slot, `mk` only grows along right extensions;
  mark components populate upward-closed families, a classically
  DD-friendly shape.
- **Product systems factor.** If `D` is a synchronous product of
  components with disjoint mark sets, an enriched element of `D`
  projects to a pair of enriched elements of the components and
  `EM(D)` embeds in `EM(D₁) × EM(D₂)`: with slot variables grouped by
  component, the diagram of the embedding is *linear* in the diagrams of
  the factors even where the cardinality multiplies. Compositional
  specifications — the practical case — are exactly product-shaped.
  ⟨TBD: state and prove the embedding; relate to the AND-split of
  [SωSX26, §5.6(3)], which is the same factorization read on the
  quotient.⟩
- **Letter symmetry.** The λ-quotient (letters the language never
  distinguishes) appears symbolically as guard equality — collapsing
  `2^AP` before anything is built.

### 4.3 The honest wall

Aperiodicity of a regular ω-language is PSPACE-complete [CH91; SωS26,
§8], so no representation makes the construction polynomial in general:
there are automata whose enriched monoids admit no small diagram under
any order ⟨TBD: does a family with provably exponential DDs exist for
*every* variable order? plausible via the usual hidden-weighted-bit
style arguments — library request, or leave as a stated conjecture⟩. The
claim is the symbolic model checker's claim, no more: worst cases stand,
structured cases — products, sparse marks, few residuals, small
λ-quotients — collapse, and the census corpus [SωSN26] plus a family of
scaling product specimens measure which world the practical inputs
inhabit. ⟨TBD: the measurement plan; the kinship with why symbolic
reachability succeeded on hardware — the inputs are engineered objects,
and engineered objects are products.⟩

## 5. The pipeline, costed

⟨TBD: one table — phase / primitive used / relation arity / #fixpoint
iterations / output object; the only `3k`-flavored arity at Phase 2;
everything else `2k` slot-local or quantification. A remark on
incrementality: the BFS layers double as the shortlex keying, so
canonicity costs nothing extra. A remark on the learner [SωSL26]: its
observation table is also a vector set, and the same engine applies —
left as a prospect.⟩

## 6. Evaluation

⟨TBD: after implementation — DD sizes vs `|EM|` across the census;
scaling on product families (k components × m states); the Phase-2
crossing cost in practice; comparison against the explicit
implementation's cap; the answer to "did the `|Q|` exponent move".⟩

## 7. Related work

⟨TBD: skeleton — symbolic model checking and reachability (the engine
lineage; library requests); symbolic bisimulation minimization and
partition refinement (nearest relatives of Phase 5); decision-diagram
variants for vector sets (MDD/SDD/hierarchical — the slot-group story of
§4.2 wants hierarchical diagrams); transition-monoid computations in
explicit tools (AMoRE-lineage) as the explicit baseline; [SωS26, §8] as
the promissory note this paper redeems.⟩

## 8. Conclusion

⟨TBD: the arc — the syntactic ω-semigroup's construction was born
symbolic and nobody noticed: its one deep algebraic lemma is a locality
theorem, its dominant object is a reachability set, its congruence a
partition refinement, and its output small. The engine relocates the
PSPACE wall from "the object cannot be built" to "the object is built
whenever the input has the structure engineered systems have" — the same
relocation symbolic model checking performed on state spaces, applied to
the canonical algebra of ω-regular languages.⟩

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
- ⟨TBD: the symbolic lineage — BDDs (Bryant), symbolic model checking
  (Burch–Clarke–McMillan et al.), saturation, symbolic bisimulation
  minimization, MDD/SDD/hierarchical diagram variants; AMoRE for the
  explicit transition-monoid baseline — library requests for the biblio
  sweep.⟩
