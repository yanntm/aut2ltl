# The Syntactic ω-Semigroup as an Object — outline draft

**Working title:** *The Syntactic ω-Semigroup as an Object: a Canonical Normal Form
for ω-Regular Languages, and its Construction*

Restructure of `sos_constructed.md`: object first, construction second. All content
borrowed from there unless marked NEW. Bullets only at this stage — one sentence per
idea, no definitions, no filled text.

---

## Abstract

- The syntactic ω-semigroup: canonical, complete, defined since Arnold 1985, never built.
- Contribution 1: the object itself, reified as the tuple `𝓘 = (𝒞, λ, M, P)` with a
  standalone lasso-membership semantics — a canonical normal form for ω-regular
  languages, which the domain has never had.
- Contribution 2: the rotation lemma — the two-sided syntactic congruence is computable
  by right multiplications alone; the structural fact missing from 40 years of literature.
- Contribution 3: the construction from any deterministic Emerson–Lei automaton,
  assembling the two, with correctness `L(𝓘(D)) = L(D)` proved against the semantics.

## 1. Introduction

- Finite words have a normal form (the minimal DFA) and forty years of tooling on it;
  ω-words have none — no minimal deterministic automaton, every pipeline manipulates
  presentations, never languages.
- Arnold's syntactic ω-semigroup is the canonical algebra in principle and a phantom in
  practice: defined everywhere, built nowhere.
- The obstruction is structural (recognizers forget acceptance along runs; the
  congruence is two-sided) — kept from current §1, now as the bridge to Part B.
- Contributions restated: the object (§3), its uses as evidence of significance (§4),
  canonicity (§5), the construction with the rotation lemma at its core (§6–8).
- The three running examples announced — `GF(aa)`, `Even`, `EvenBlocks` — met first as
  tables, only later as automata.

## 2. Background

- We only ever look at lassos: ω-regular languages are equal iff they agree on
  ultimately-periodic words.
- A finite monoid plus one operation ("loop forever") classifies ω-words; morphisms and
  recognition.
- Linked pairs are the names of lassos: `(s, e)` with `se = s`, `e² = e`.
- What is recalled (PP04, Ramsey) vs what is new in this paper, stated once.
- (Arnold's congruence does NOT appear here — deferred to §5 where canonicity needs it.)

## 3. The object

- Definition: a well-formed tuple `𝓘 = (𝒞, λ, M, P)` — classes keyed shortlex, letter
  map, multiplication table, accepting linked pairs; axioms: associativity,
  letter-generated, fresh identity `[ε]`, `P` a conjugacy-saturated set of linked pairs.
- NEW: the saturation axiom made explicit — currently implicit in Lemma 3.2's "any
  representatives give the same verdict".
- Semantics: the lasso membership query — fold stem and loop through `λ, M`, iterate the
  loop to its idempotent, look up `P`.
- NEW: well-definedness lemma — the query is a function of the lasso, not of its
  presentation, iff `P` is saturated; this defines `L(𝓘)`.
- Residuals as derived data: every class denotes a residual language by the same query
  started at that class (current Prop 5.3, moved forward); the Cayley graph as the
  machine view (current Def 5.2).
- The serialization format (current Fig 2) presented here as the object's concrete form.
- The three example tables (current Table 3) read and queried before any automaton is
  drawn: the period-2 cycle in `Even` visible on the raw table.

## 4. What the object unlocks

- Identity band, near-free from the semantics: equality is byte equality of canonical
  serializations, complement is `P ↦ P^c`, emptiness is `P = ∅`, membership is one fold.
- Flagship read-off: LTL-definability is aperiodicity of the table — power-iterate each
  class, look for a cycle of period ≥ 2 (current §7.1, compressed).
- The taxonomy table (current §7.2) condensed: one sentence per row, each a structural
  test on the same object, several with no practical tool today.
- The suggestion, one paragraph: wherever a pipeline step is language-level, the
  automaton is a proxy and the canonical object can take its place — the calculus
  companion develops this.
- Nothing here is developed; this section motivates Part B and points at the family.

## 5. Canonicity

- Arnold's syntactic congruence recalled in full, with the two context shapes (current
  §2 block, moved here).
- The two shapes are genuinely independent — `Even` vs `EvenBlocks`, current Prop 4.6
  and examples.
- The syntactic tuple: the quotient by Arnold's congruence, keyed shortlex, is a
  well-formed tuple and a function of `L` alone.
- Complete invariant theorem (current Thm 5.1): two languages are equal iff their
  tuples are byte-equal.
- Two minimality senses, both exact: coarsest congruence saturating `L` (Arnold);
  unique canonical complete invariant. (Minimal-recognizer claim dropped.)
- The two shapes double as the specification the construction must meet — hand-off
  to Part B.

## 6. The construction, I: seeing acceptance

- The input: any deterministic complete Emerson–Lei automaton `D` (current §2 automaton
  block, moved here).
- The first obstruction: the transition monoid forgets the marks acceptance reads.
- The acceptance-enriched monoid `EM(D)` (current Def 3.1) and the skeleton lemma
  (current Lemma 3.2).
- Necessity (current Prop 3.4): the one-state witness with trivial transition monoid
  under a nontrivial language.
- The enriched monoids of the three examples (current Table 2).

## 7. The construction, II: the rotation lemma

- The second obstruction: Arnold's congruence is two-sided, but a monoid's closure
  table offers only right multiplication.
- The collapse (current Lemma 4.1): a prefix acts only through the single state it
  reaches — evaluation factors through a finite left action on slots.
- The rotation lemma, stated at its natural generality: a left factor acts on a
  two-sided context only by re-indexing the slot — `a·e·b` at slot `q` equals `e·b·a`
  at slot `st_a(q)` — so the two-sided congruence is the coarsest right-invariant
  refinement of a slot-indexed seed; three-line proof.
- Discussion, factual: MS97 displayed the finitary × infinitary split with two-sided
  quantification still inside the loop; CPP08 saturated over context triples; the
  conjugation `a·e·b ↦ e·b·a` is the step neither took.
- Template remarks, only what we have: the right-extension-at-slots discipline is
  exactly an observation-table discipline (AF21's obstruction answered), and the
  one-sided fixpoint is what a symbolic implementation computes.
- Instantiation on `EM(D)`: `~lin` (residual equality at reached slots) and `~ω`
  (right-invariant profile equality), current Def 4.2 and Prop 4.3; the worked
  `EvenBlocks` split.

## 8. The algorithm and the two theorems

- Moore partition refinement from the seed `R = (~lin-class, Aprof)`, split by right
  letters to fixpoint (current Thm 4.5's procedure).
- Reading `P` off `D`: test one shortlex lasso per candidate linked pair.
- NEW — Theorem A (correctness, self-contained): `𝓘(D)` is well-formed (saturation
  proved, not assumed) and `L(𝓘(D)) = L(D)`; proof from the skeleton lemma and the
  collapse only, no Arnold.
- Theorem B (canonicity): `𝓘(D)` is the syntactic tuple of §5 — the constructed
  quotient is Arnold's.
- Examples resolved: `GF(aa)`'s presentation group dies in the quotient (10 → 6, LTL);
  `Even` and `EvenBlocks` keep a genuine `Z₂`.
- Canonicity exhibited (current Fig 3): two non-isomorphic presentations of `GF(aa)`,
  byte-identical output.

## 9. Complexity

- Two costs, currently blurred, now split: the object is quadratic in `|𝒞|`; the
  construction path through `EM(D)` is exponential in `|Q|` in the worst case.
- `|𝒞|` is a language invariant — the intrinsic complexity of `L`; PSPACE-hardness of
  the aperiodicity question says some exponential is unavoidable.
- Everything after construction is polynomial in the table (current §8 read-off claims).
- BDD-friendliness note kept: all ingredients Boolean, all steps set operations.

## 10. Related work

- Arnold (the congruence), MS97 (the display), CPP08 (the recognizer, saturation over
  triples), PP04 (the algebraic frame), Wilke, DG08 (decidability without an algebra),
  AF16/AF21/ABF18 (the learning obstruction the rotation lemma addresses).
- Positioning sentence per item: what each had, what each lacked toward the object.

## 11. Conclusion

- The object was never built because two structural pieces were missing; both are
  supplied, and the tuple is the deliverable.
- The rotation lemma stands on its own as the mathematical core.
- The family builds on `(𝒞, λ, M, P)`: companions consume the object this paper defines
  and constructs.

---

## Not transferred (parked, decide later)

- Current §6 (finite-word specialization, LTLf) — at most a one-line degeneration
  remark somewhere in Part B if we want the sanity check.
- Current §7 use-case development beyond the §4 teaser — lives in the companion papers.
- No prospects beyond material we have (no prophetic extraction, no learning-paper
  promises beyond the two factual template remarks in §7).
