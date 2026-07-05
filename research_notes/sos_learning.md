# Learning the Syntactic ω-Semigroup

**Yann Thierry-Mieg**

With significant inputs from
**Claude (Anthropic)**

*Shadow draft — 2026-07-05 — placeholders marked `⟨TBD: …⟩`*

## Abstract

The syntactic ω-semigroup of a regular ω-language `L` is its canonical algebra:
presentation-independent, complete, and the object from which membership,
equivalence, and every definability property of `L` — LTL-definability included —
are read. A companion paper [SωS26] shows it constructible from any deterministic
automaton for `L`. This paper shows it is *learnable*: we give an active-learning
algorithm in the MAT model whose queries are memberships of ultimately-periodic
words only, and whose hypotheses and target are the exportable invariant
`𝓘(L) = (𝒞, λ, M, P)`. The enabler is the rotation lemma of the companion paper,
transported from a computability statement to a query-completeness statement: every
two-sided context separating two finite words reduces to a right extension read at
a prefix-indexed slot, so an L\*-style observation table — rows finite words,
columns contexts in Arnold's two shapes — suffices, and no third dimension of
queries exists. Where the established FDFA approach learns one of several
presentation-dependent families of DFAs, and is blind on the many ω-languages whose
right congruence is trivial, this learner converges to the one canonical object;
its output answers definability questions directly, with equivalence between
hypotheses decided by byte-equality of invariants. ⟨TBD: query-complexity headline,
once Proposition 5.2 is settled⟩ ⟨TBD: one-sentence experimental headline on the
census benchmark⟩

---

## 1. Introduction

Active learning of ω-regular languages has a structural handicap that finite words
never had. For finite words, Angluin's L\* rests on the Myhill–Nerode theorem: the
right congruence of the language *is* the minimal acceptor, so an observation table
of prefixes against suffixes converges to a canonical object. For ω-words the right
congruence is not informative: it can be trivial while the language is complex, and
languages as plain as `FG(a ∨ Xa)` have a one-class right congruence [AF21]. The
response of the field — families of DFAs (FDFAs) covering the lasso structure
[AF16, ABF18] — works, but at a price: the learner must choose among family styles
(periodic, syntactic, recurrent), none canonical, and what is learned is an
*acceptor presentation*, not the language's own algebra.

The canonical object exists. Arnold's syntactic congruence [Arn85] quotients finite
words by interchangeability in every ultimately-periodic context, in two shapes —
in the stem, or inside the loop — and its quotient, the syntactic ω-semigroup
(SωS), is the exact ω-analogue of the syntactic monoid: presentation-independent,
finite, and complete for definability. The companion paper [SωS26] constructs it
from a deterministic automaton; its key computational step is a **rotation lemma**:
the two-sided congruence is the coarsest right-invariant refinement of a seed
relation, because a left factor prepended to a loop merely *rotates* it — a right
extension read at a shifted starting slot.

This paper's observation is that the rotation lemma is not about automata at all.
Read in the query model, it says: rows and columns are enough. Left contexts can be
confined to a prefix role (rows and query prefixes), right contexts in Arnold's two
shapes are the columns, and every distinction the two-sided congruence can make is
observable in that table — a completeness theorem for a query discipline
(Theorem 3.3). On top of it we build an L\*-style learner whose hypotheses are not
automata but the invariant `𝓘(L)` itself: classes keyed by shortlex representatives,
letter map, multiplication table, accepting linked pairs.

**Contributions.**
1. A two-sorted observation table for Arnold's congruence, with lasso membership
   queries only (§3).
2. Its completeness: the transported rotation lemma (Theorem 3.3) —
   counterexample-harvested columns suffice, in both shapes.
3. The learner: closedness, consistency, and counterexample processing per shape,
   assembling `𝓘(L)` with accepting pairs read only at equivalence time (§4);
   termination and canonicity of the limit (§5).
4. Equivalence of hypotheses by canonicity: invariant equality replaces product
   constructions (§5).
5. ⟨TBD: implementation + evaluation contribution line, after §6 exists⟩

⟨TBD: positioning paragraph relative to algebraic/categorical automata learning —
**gated on reading Urbat & Schröder, LICS 2020**; if generic algebra learning
already covers Wilke algebras, this paragraph claims the *syntactic* object, the
two-shape query discipline, and the implementation; if not, it claims the ground.⟩

Three running examples — `GF(aa)`, `Even`, `EvenBlocks`, the triptych of [SωS26] —
recur at every definition. The third is the important one here: it is
prefix-independent, its right congruence trivial, so every right-congruence-seeded
learner is structurally blind to it, while its whole content sits in the ω-sort of
our columns.

## 2. Background and query model

We import the companion paper's objects wholesale and recall only what the learner
touches; see [SωS26, §2] for the unhurried version. `Σ` is a finite alphabet. A
**lasso** is `u·v^ω`; ω-regular languages are determined by their lassos. Two
finite words are **syntactically congruent**, `u ≈_L v`, when interchangeable in
Arnold's two context shapes [Arn85]:

```
    (linear)    ∀ x, y ∈ Σ*, t ∈ Σ⁺ :   x·u·y·t^ω ∈ L  ⟺  x·v·y·t^ω ∈ L
    (ω-power)   ∀ x, y ∈ Σ*         :   x·(u·y)^ω  ∈ L  ⟺  x·(v·y)^ω  ∈ L
```

The quotient `S(L)₊ = Σ⁺/≈_L`, completed with its accepting linked pairs, is the
syntactic ω-semigroup, reified as the invariant `𝓘(L) = (𝒞, λ, M, P)` — classes
keyed by shortlex-least representatives, letter map, multiplication table,
accepting linked-pair set — a complete, canonical, exportable representation of
`L` [SωS26, Thm 5.1].

**The query model.** A teacher for `L` answers **membership queries** on lassos
(`u·v^ω ∈ L`?) and **equivalence queries** on hypotheses `𝓗` (an invariant-shaped
tuple), returning a lasso counterexample on failure. This is the standard MAT
model restricted to ultimately-periodic words, which is no restriction at all:
lassos determine `L`, and every query the algorithm ever poses is one.

In our experiments the teacher is the companion construction itself: membership is
one deterministic run, and an equivalence query builds `𝓘` of the hypothesis's
language and compares invariants byte-for-byte — canonicity making the teacher
cheap is itself a small advertisement for the object. Nothing in the learner
depends on this realization.

## 3. The observation table

**Definition 3.1 (table).** A table is `T = (R, E_lin, E_ω)` where `R ⊆ Σ⁺` is a
finite, shortlex-reduced set of **rows**, observed together with its frontier
`R·Σ`, and the columns are of two sorts:

- `E_lin ⊆ Σ* × Σ* × Σ⁺` — **linear columns**; the entry of row `u` at
  `(x, y, t)` is the bit `[ x·u·y·t^ω ∈ L ]`;
- `E_ω ⊆ Σ* × Σ*` — **ω-columns**; the entry of row `u` at `(x, y)` is the bit
  `[ x·(u·y)^ω ∈ L ]`.

Rows `u, v` are **table-equivalent**, `u ≡_T v`, when all entries agree.

Every entry is one membership query. By construction `≈_L` refines `≡_T` for any
column set — columns are particular Arnold contexts — so learning is the business
of growing `E_lin ∪ E_ω` until `≡_T` *is* `≈_L` on the rows, and growing `R` until
the rows exhaust `𝒞`.

The two sorts divide the labor exactly as the two relations `~lin` and `~ω` of the
companion construction do. On `Even`, linear columns already separate everything —
the stem decides membership. On `EvenBlocks`, *every* linear column is a constant
row-function (prefix-independence: a stem mutation is swallowed), and the entire
language lives in the ω-sort: the column `(ε, !a)` separates rows `a` and `aa`,
since `(a·!a)^ω ∉ L` and `(aa·!a)^ω ∈ L`. A learner without the ω-sort cannot even
represent what distinguishes them — this is [AF21]'s obstruction, met head-on.

**Theorem 3.3 (completeness of the discipline).** Let the column set be closed
under the harvest rules of §4 (consistency minting and counterexample extraction).
Then at fixpoint, `≡_T` coincides with `≈_L` restricted to `R`, and the rows meet
every class of `𝒞` reachable by the closedness rule.

> ⟨TBD: proof. Plan: transport of [SωS26, Lem. 4.4]. (i) Any separating two-sided
> context for `u ≉_L v` is one of the two shapes. (ii) Linear shape: the left part
> `x` enters the query as a literal prefix — rows never need left extension, the
> column carries `x` itself; closure under suffix-shift of `y` mirrors the
> right-invariance argument. (iii) ω-power shape: a left extension of the loop
> content is a rotation of the loop, i.e. a right extension `(x', y·a)`-style
> column read under a shifted prefix — write the rotation identity
> `x·(a·u·y)^ω = x·a·(u·y·a)^ω` and check it is exactly the harvested column form.
> (iv) Conclude: the harvest rules generate, from any witness of `u ≉_L v`, a
> column separating `u, v` in finitely many steps. The delicate half is (iii)+(iv)
> = Lemma 4.4 below, the declared crux of the paper.⟩

## 4. The learner

**Closedness and the hypothesis.** `T` is **closed** when every frontier word
`u·a` (`u ∈ R`, `a ∈ Σ`) is `≡_T` to some row; otherwise `u·a` (shortlex-reduced)
is promoted to `R`. From a closed and consistent table the hypothesis `𝓗` is read
off exactly as `𝓘` is: classes = `≡_T`-classes of rows keyed shortlex, `λ(a)` =
class of the row equivalent to `a`, `M([u],[v])` = class of the row equivalent to
`u·v` ⟨TBD: `u·v` may not be in `R ∪ R·Σ`; either close `R` under representative
concatenation on demand (extra queries, bounded — argue it) or build `M` on
one-letter extensions only and prove the monoid generated is the same — decide
after Lemma 4.2 is proved⟩, and `P` per below.

**Consistency.** `T` is **consistent** when `u ≡_T v` implies `u·a ≡_T v·a` for
all `a ∈ Σ`. A violation at column `c` mints a new column: for `c = (x, y, t)`
linear, the column `(x, a·y, t)`; for `c = (x, y)` ω, the column `(x, a·y)` — the
letter migrates from the row into the column, shifting `y` in the linear sort and
*rotating* the loop in the ω-sort.

**Lemma 4.2 (minting is sound and sufficient).** The minted column separates
`u, v`, and consistency at fixpoint makes `≡_T` a right congruence on rows.

> ⟨TBD: proof — the linear case is L\* verbatim; the ω case must check that
> `x·(u·a·y)^ω` is a legal ω-column entry for row `u`, which it is by definition
> with column `(x, a·y)` — the content of the check is only bookkeeping, but write
> it, it is where a reader verifies the rotation is real.⟩

**Counterexample processing.** An equivalence query returns a lasso `w·z^ω` on
which `𝓗` and the teacher disagree. Fold `w·z^ω` through `𝓗` (reduce `z` to an
idempotent power, as in the membership read-off of [SωS26, Fig. 2]); then locate a
divergence:

**Lemma 4.3 (linear harvest).** If the disagreement is attributable to the stem —
⟨TBD: precise criterion, in terms of the folded prefix classes⟩ — then a
Rivest–Schapire-style binary search over the stem's prefix decompositions yields a
linear column `(x, y, t)` separating two currently-merged rows, in
`O(log |w|)` membership queries.

**Lemma 4.4 (ω harvest).** Otherwise the disagreement lives in the loop, and there
exist a rotation `z' ` of `z` and a split `z' = z₁·z₂` such that the ω-column
`(x, z₂)` with ⟨TBD: exact prefix `x` — the folded stem representative, or the
raw stem `w`? decide: raw `w` is always sound, representative is shorter; start
with raw⟩ separates two currently-merged rows.

> ⟨TBD: Lemma 4.4 is the paper's crux and the declared open risk: prove that a
> disagreeing lasso always surrenders a separating column under rotation+split
> search, and bound the search (naively `O(|z|²)` splits × rotations; aim for
> `O(|z| log |z|)` or accept quadratic and say so). If a counterexample resists
> both harvests, the completeness proof of Theorem 3.3 has a hole exactly there —
> solve this lemma FIRST, everything else is scaffolding around it.⟩

**Accepting pairs.** `P` is computed only when the monoid part has stabilized
(table closed and consistent, about to pose an equivalence query): enumerate the
linked pairs `(s, e)` of the hypothesis (`e·e = e`, `s·e = s` in `M`), and for each
pose one membership query `w_s·(w_e)^ω` on the shortlex keys. Mid-learning linked
pairs are not read: idempotents of an unstable `M` can merge later, and a `P`
computed early answers for classes that will not survive. ⟨TBD: one-line lemma that
at equivalence time the queried verdicts are class-invariant — this is [SωS26,
Lem. 3.2] transported to the hypothesis, *conditioned* on the hypothesis being
correct; when it is not, the equivalence query's counterexample repairs it, so
soundness of the loop does not depend on it. State this carefully.⟩

**The loop.** Close; make consistent; read `𝓗` with `P`; pose equivalence; on
counterexample, harvest (Lemma 4.3 or 4.4) and repeat. ⟨TBD: 15-line pseudocode
block once the `M`-construction choice above is made.⟩

## 5. Correctness and complexity

**Theorem 5.1 (termination and canonicity).** The loop terminates, and its final
hypothesis is `𝓘(L)` — not an acceptor for `L` among others, but the canonical
invariant itself, byte-equal to the teacher-side construction after shortlex
keying.

> ⟨TBD: proof — progress: each counterexample adds a row class or a separating
> column; both are bounded by `|𝒞|` (columns per sort — check the bound, likely
> `|𝒞|` per sort suffices by the refinement argument); limit is `≈_L` by
> Theorem 3.3; canonicity by [SωS26, Thm 4.5 + 5.1].⟩

**Proposition 5.2 (query complexity).** ⟨TBD: statement. Target shape: membership
queries `O(|𝒞|²·|Σ| + |𝒞|·(cex harvest costs))`, equivalence queries `≤ |𝒞|` —
fill the constants after Lemmas 4.3/4.4 fix the harvest costs. Output-polynomial
in `|𝒞| = |S(L)₊|` is the honest and correct yardstick.⟩

The yardstick deserves a paragraph of candor, mirroring [SωS26, §8]. `|S(L)₊|` can
be exponentially larger than a smallest automaton or FDFA for `L`; that is the
price of the canonical target, and we measure it rather than hide it (§6). The
converse is the sale: on languages with trivial or near-trivial right congruence —
`EvenBlocks`, `FG(a ∨ Xa)` [AF21], and generically tail properties — the
right-congruence-seeded part of any FDFA degenerates while nothing here does,
because nothing here is seeded by the right congruence: the ω-columns query the
loop structure directly. ⟨TBD: can we exhibit a family where some FDFA flavor is
exponentially larger than `𝓘`? If yes, the comparison cuts both ways and the
section gets a theorem; if not, keep it empirical.⟩

## 6. Evaluation

⟨TBD: entire section — after implementation. Fixed decisions, so the section can
be written into: teacher = the companion engine (membership = one run;
equivalence = invariant comparison); benchmark = the census of small automata
(2 states, 1 AP, 1 acceptance set, …), for which ground truth — `𝓘`, LTL status —
is already computed; metrics = membership/equivalence query counts, table
dimensions, wall time, against `|𝒞|`; baseline = an FDFA learner (ROLL family) on
identical teachers, with the equalized metric being cost-to-answer a definability
question (an FDFA cannot answer it without further construction — that asymmetry
is reported as a result, not a footnote); worked in-text examples = the triptych.⟩

## 7. Related work

⟨TBD: after the due-diligence acquisitions, in priority order: Urbat–Schröder
LICS 2020 (the gate — read before finalizing the intro's positioning), Angluin
1987, Rivest–Schapire 1993, the ROLL line (experimental baseline), Bohn–Löding
passive learning, Michaliszyn–Otop, CALF (van Heerdt–Sammartino–Silva); also
check the exact claim of Maler & Pnueli 1995 on learning star-free/aperiodic
languages before listing it. Anchors already in hand and vetted: [AF16, ABF18, AF21]
(FDFA line and the right-congruence obstruction), [Arn85] (the congruence),
[MS97] (finitary/infinitary display), [SωS26] (construction, rotation lemma,
invariant). The section's argument, independent of what the acquisitions reveal:
prior learners target acceptors; this one targets the language's own algebra, and
the definability read-offs come with it.⟩

## 8. Conclusion

The syntactic ω-semigroup was constructible [SωS26]; it is also learnable, and by
the same mechanism: the rotation lemma, which there collapsed a two-sided
congruence into right computations on a monoid, here collapses it into rows and
columns of lasso queries. The learner's limit is not an acceptor chosen from a
family but the canonical invariant of the language — the object definability
questions are read from — so learning and classification cease to be separate
activities. ⟨TBD: closing sentence tied to the experimental headline.⟩

---

## References

*(entries marked ⟨acquire⟩ are placeholders — not citable until the paper is in
`papers/` and checked; the prioritized acquisition list is in §7)*

- **[AF16]** D. Angluin, D. Fisman. *Learning regular omega languages.* TCS 650
  (2016) 57–72.
- **[ABF18]** D. Angluin, U. Boker, D. Fisman. *Families of DFAs as acceptors of
  ω-regular languages.* LMCS 14(1) 2018.
- **[AF21]** D. Angluin, D. Fisman. *Regular ω-languages with an informative right
  congruence.* Inf. Comput. 278 (2021).
- **[Arn85]** A. Arnold. *A syntactic congruence for rational ω-languages.* TCS 39
  (1985) 333–335.
- **[MS97]** O. Maler, L. Staiger. *On syntactic congruences for ω-languages.* TCS
  183 (1997) 93–112 (rev. 2008).
- **[SωS26]** Y. Thierry-Mieg, with Claude (Anthropic). *The syntactic
  ω-semigroup, constructed.* Working draft, 2026.
- ⟨acquire⟩ **[Ang87]** D. Angluin. *Learning regular sets from queries and
  counterexamples.* Inf. Comput. 75 (1987).
- ⟨acquire⟩ **[RS93]** R. Rivest, R. Schapire. *Inference of finite automata using
  homing sequences.* Inf. Comput. 103 (1993).
- ⟨acquire⟩ **[US20]** H. Urbat, L. Schröder. *Automata learning: an algebraic
  approach.* LICS 2020.
- ⟨acquire⟩ **[ROLL]** — the FDFA learning tool line; exact cite after
  acquisition.
