# Choosing the Simplest Property Given Prior Knowledge, Canonically

**Yann Thierry-Mieg**

With significant inputs from
**Claude (Anthropic)**

*Working draft — 2026-07-11.*

## Abstract

To verify `S ⊨ φ` when the system is already known to satisfy `K`, the
model checker may replace the negated property by *any* language `B` in
the interval `ℒ(¬φ) ∩ ℒ(K) ⊆ ℒ(B) ⊆ ℒ(¬φ) ∪ ℒ(¬K)` [DPT25]. The
automata-theoretic original navigates that freedom heuristically, on
presentations: per-transition Boolean bands, closure constructions,
Minato covers. This paper moves the question onto the syntactic
ω-semigroup, where the interval is not a search space but an **exactly
represented finite lattice**: the powerset of the conjugacy classes of
`ℒ(¬K)` on one aligned table. The two decisive endpoint checks — `K`
settles `φ`, `K` refutes `φ` — become two scans, symmetric where the
automata side must dodge a universality test, each failure certified by
the minimal witness lasso. The central results are exact existence
tests, in polynomial time, for the questions the automata side can only
approach by construction-and-luck: *is there a safety (co-safety,
obligation, recurrence, persistence) property equivalent to `¬φ` given
`K`?* — one interval-test lemma, one hull per class, a canonical least
witness on success, a certificate of impossibility on failure, and,
inside the obligation band, the minimal achievable Wagner degree as a
greedy read-off. For stutter invariance the story sharpens into the
paper's technical heart: the natural quotient test is sound but provably
incomplete — the stutter hull can *escape the table*, a locality
phenomenon we exhibit over a two-letter alphabet — and the exact test is
recovered by a polynomial self-alignment of the table through the
stutter relation. Shedding atomic propositions is the same
quotient-and-pull-back move under a different congruence; integrating a
knowledge base is lossless where the automata side trades precision for
cost; and when `φ` and `K` are LTL, the whole lattice is LTL-definable,
closing the pipeline at the formula level: *formula in, simpler formula
out, equivalent given what we know* — an operation the automata toolbox
does not offer at all.

---

## 1. Introduction

**The problem.** LTL model checking decides `S ⊨ φ` — every infinite
execution of a system `S` satisfies a linear-time property `φ` — by an
emptiness check of a product `S ⊗ A_{¬φ}` [Var07]. Its cost is driven by
the property side: the size of `A_{¬φ}`, its acceptance strength (weak
and terminal automata admit cheaper emptiness checks [BRS99, ČP03]), its
stutter sensitivity (stutter-insensitive properties unlock partial-order
and structural reductions worth up to factorial factors [Pel94, Val93]),
and the atomic propositions it observes. **Prior knowledge** is a
property `K` the system is already known to satisfy: `ℒ(S) ⊆ ℒ(K)` — a
previously proven formula, an invariant from a reachability engine, a
structural fact. Duret-Lutz, Poitrenaud and Thierry-Mieg [DPT25] showed
that knowledge buys freedom: `S ⊨ φ` may be decided with any `B` in the
interval

    ℒ(¬φ) ∩ ℒ(K)  ⊆  ℒ(B)  ⊆  ℒ(¬φ) ∪ ℒ(¬K),          ([DPT25], Thm. 1)

because words outside `ℒ(K)` cannot occur in `S` and are therefore free
to add or remove. **The simplest property given `K`** is the `B` in that
interval that makes the model checker's life easiest: smaller, weaker in
acceptance strength, stutter-insensitive, observing fewer propositions.
On a benchmark derived from the MCC'22 model-checking contest, endpoint
checks on this interval alone answer half of 97 950 problems without
running an LTL model checker at all, and the rest get measurably simpler
automata [DPT25].

What the automata-theoretic approach cannot do is *reason about the
interval itself*. Its moves are presentation rewrites — per-transition
Boolean bands simplified by Minato's algorithm, closure constructions
bounded by emptiness checks — each sound, none complete, and the natural
language-level questions are not even posable: *does there exist a
safety property equivalent to `¬φ` given `K`? an obligation? a
stutter-insensitive one?* Each is decidable in principle — a bespoke
closure construction followed by a PSPACE containment — but no toolbox
poses them; a "no" from a heuristic means nothing, a "yes" comes
without a canonical witness, and the interval, with its infinitely
many ω-regular members, has no finite representation on that side.

**Canonically.** This paper transposes the framework onto the syntactic
ω-semigroup — the canonical finite algebra of an ω-regular language,
now constructible [SωS26] and equipped with an operational calculus of
alignments, pair-set surgeries and normal forms [SωSC26]. On the
invariant, the given-that interval acquires the finite representation
the automata side lacks, and the freedom becomes *arithmetic*:

1. **The interval is a finite lattice, exactly** (§3): after one
   alignment, the legal `B`s on the table are the saturated pair sets
   between two free surgeries `P_min` and `P_max`, and the lattice is
   isomorphic to the powerset of the conjugacy classes of `ℒ(¬K)` — the
   freedom [DPT25] probes heuristically, measured in bits. The two
   decisive endpoint checks are two scans, symmetric where the automata
   side must dodge an exponential universality test, and every verdict
   carries the minimal witness lasso.
2. **Exact simpler-class tests, one per rung** (§4): a single
   interval-test lemma turns each level of the safety–progress ladder
   into a polynomial decision — safety and co-safety via the topological
   hulls, obligation via a forcing argument on `R`-classes, recurrence
   and persistence via Horn-style least fixpoints — each with a
   canonical least (and greatest) witness and a minimal-lasso
   certificate of impossibility. Inside the obligation band, the
   minimal achievable Wagner degree is itself a greedy read-off. The
   same tests, applied to the interval `[P_{L₁}, P_{L₂}^c]` of two
   disjoint languages, decide *separator synthesis* by class — a
   two-automata operation absent from the toolbox, and a decidable
   ω-side instance of the separation program [PZ16]. The whole battery
   is worked end-to-end on [DPT25]'s own running example (§4.6), where
   it certifies no safety `B` exists, brackets their Minato-derived
   `Fa` between two canonical guarantee hulls, and reads the
   recurrence-to-guarantee drop off the table.
3. **Stutter invariance, exactly — and a locality theorem** (§5): the
   stutter-invariant languages on a table are exactly those recognized
   through its stutter quotient (a clean recognition proposition), but
   the least stutter-invariant *superset* can escape every table in
   sight: we exhibit a two-letter counterexample where a
   stutter-insensitive `B` exists in the interval and the quotient test
   must say no. The exact test is recovered by a **stutter
   self-alignment** — a polynomial reachability computation relating
   cells of the table that can host stutter-equivalent lassos — giving
   a two-tier algorithm: a cheap quotient test whose witness stays on
   the table, an exact alignment test whose witness may cost one
   re-entry, and a certified diagnostic in the gap.
4. **One move, several knobs; and formulas out** (§6): shedding
   `K`-only atomic propositions is the same quotient-and-pull-back
   move under a letter-fusion congruence; a knowledge base integrates
   *losslessly*, one alignment per fact, where the automata side
   explicitly trades precision; and when `φ` and `K` are LTL the whole
   lattice is aperiodic, so with the extraction of [SωSX26] the
   pipeline closes at the formula level — LTL simplification given
   prior knowledge, formula in, formula out.

The system `S` never enters the calculus: only the two spec-sized
objects `𝓘(¬φ)` and `𝓘(K)` pay the entry price, and the chosen `B`
meets `S` either as a polynomial exit acceptor or through the mixed
product of [SωSC26-ext]. §7 lays out the evaluation plan on the
third-party MCC'22 benchmark of [DPT25], §8 positions the work, §9
concludes.

## 2. Background

We import the objects and cite the results we build on; nothing in this
section is original here. `Σ` is a finite alphabet (for LTL,
`Σ = 2^{AP}`); a **lasso** is an ultimately periodic word `u·v^ω`,
`u ∈ Σ*`, `v ∈ Σ⁺`. Two ω-regular languages are equal iff they agree on
all lassos [PP04].

**The invariant.** The syntactic ω-semigroup of an ω-regular `L`
[Arn85], reified as `𝓘(L) = (𝒞, λ, M, P)` [SωS26]: a finite class set
`𝒞` (with adjoined identity `[ε]`, each class keyed by its
shortlex-least word), a letter map `λ : Σ → 𝒞`, a multiplication table
`M`, and the set `P` of **accepting linked pairs**. A pair `(s, e)` is
**linked** if `e·e = e`, `s·e = s`, `e ≠ [ε]`; `linked` denotes the set
of all linked pairs of a table; `(s, e)` is accepting when `u·z^ω ∈ L`
for representatives. `fold(w)` evaluates a finite word through `λ, M`;
`idem(d)` is the unique idempotent power of `d`, also written `d^π`. The **membership oracle** totalizes `P`:
`Val_P(c, d) := (M(c, idem(d)), idem(d)) ∈ P`, and for every lasso
`u·v^ω ∈ L ⟺ Val_P(fold(u), fold(v))`. The strong form (via Ramsey):
any ω-word factorized as `w₀·w₁·w₂⋯` with all `w_{j≥1}` folding to one
idempotent `e` has verdict `(fold(w₀)·e, e) ∈ P`; every ω-word admits
such a factorization, and this holds for *any* table recognizing `L`,
not only the syntactic one [PP04]. Scans run over **cells**
`(c, d) ∈ 𝒞 × (𝒞 \ {[ε]})` in the *discipline order* (shortest, then
lexicographic canonical lassos); the first satisfying cell yields the
globally minimal witness lasso [SωSC26, Prop 3.2]. Two ω-regular
languages are equal iff their reduced invariants are byte-equal
[SωS26, Thm 5.1].

**The calculus** [SωSC26]. Three moves: **align** — the generated
product of two invariants on one table `T` (the only product-priced
move, `≤ n₁·n₂` classes and in practice far fewer), carrying both
verdict maps; **operate** — surgery on pair sets over the fixed table
(Boolean algebra pointwise, complement one flip, decisions as
`Val`-scans); **reduce** — re-quotient to the canonical invariant of
any pair set's language. A pair set denotes a language iff it is
**saturated** under conjugacy: for every linked `(s, e)` and
factorization `e = x·y`, the cells `(s, e)` and
`((s·x)·(y·x)^π, (y·x)^π)` carry one verdict [SωSC26, Prop 3.1];
saturation is checkable and enforceable by a polynomial fixpoint
(`sat(·)`, the least saturated superset), and a saturated `Q` denotes
the language `L(Q)` its `Val` accepts. Green's preorders on a finite
monoid: `x ≤_R y` iff `x ∈ y·M¹` (right divisibility), `R` the induced
equivalence; `x ≤_H y` iff `x ∈ y·M¹ ∩ M¹·y`, `H` the induced
equivalence [PP04]. Conjugacy preserves the stem's `R`-class (the two
stems divide each other on the right; [SωSC26, after Prop 6.1]) — a
fact used repeatedly below.

**Hulls and the ladder** [SωSC26, §6]. `Live` is the set of classes
with nonempty residual (one `O(n²)` scan). The **safety closure** is
the surgery `P̄ := {(s,e) linked : s ∈ Live}` — the least closed
(safety) language above `L(P)`, by a proof that is word-semantic and
therefore valid on any recognizing table (Prop 6.1 there); the
**interior** `P̊` is the dual kernel; `L` is safety iff `P = P̄`,
co-safety (**guarantee**) iff `P = P̊` (Cor 6.2). The **obligation** (Staiger–Wagner)
class is characterized by Theorem 6.6 there: `L` is an obligation iff
`Val_P(s, e)` depends only on the `R`-class of the stem `s` —
equivalently `P` lies in the Boolean sublattice generated by the closed
pair sets; within the band, the Wagner coordinates `(n⁺, n⁻)` are the
longest alternating paths in the `θ`-labeled `R`-class DAG (Prop 6.7
there). **Recurrence** (`GF` shape, deterministic-Büchi-realizable,
`Π₂`) and **persistence** (`FG` shape, `Σ₂`) are the next rungs,
characterized on the algebra by the chain conditions `m⁺ ≤ 0` and
`m⁻ ≤ 0` — `m±` the maximal lengths of alternating-verdict chains
along `≤_H`, by starting polarity [Lan69, CP97, CP99, SW08].
Concretely: `L` is a recurrence property iff no linked stem `s`
carries loops `f ≤_H e` with `Val(s,e) = 1` and `Val(s,f) = 0` —
verdicts propagate down the `H`-order — and persistence is the mirror
condition. (Orientation anchor: for the recurrence specimen `GFa`,
the accepting loop `λ(a)` sits `H`-below the rejecting all-`b` loop,
as the condition demands; `FGa` mirrors it. The transcription is
confirmed against the census's chain coordinates (§7) by two distinct
decision paths over the calculus's shared `H`-order primitives — a
violation scan against an alternating-chain dynamic program — in
agreement on all 6 222 census languages.)

**Stutter notions.** `destutter(·)` collapses maximal finite blocks of
equal letters; two ω-words are stutter-equivalent iff they share their
destuttered normal form; `L` is stutter-invariant iff it is a union of
stutter classes. On the syntactic table: `L` is stutter-invariant iff
`λ(a)·λ(a) = λ(a)` for every letter [SωSC26, Prop 5.1] — and the ⇐
direction of that proof is again word-semantic, valid on any
recognizing table. The global **stutter closure** `SC(L₀)` — the union
of the stutter classes meeting `L₀` — is the least stutter-invariant
superset of `L₀` among all languages (stutter-invariant sets are closed
under arbitrary unions and intersections) and is ω-regular, by the
`cl`/`sl` closure constructions of [HK96, MD15].

**Given-that** [DPT25]. With `ℒ(S) ⊆ ℒ(K)` and `ℒ(S) ≠ ∅`:
`ℒ(S) ∩ ℒ(¬φ) = ∅ ⟺ ℒ(S) ∩ ℒ(B) = ∅` for any `B` in the interval
above (Theorem 1 there — the soundness theorem this paper inherits
unchanged, since it is a statement about languages). Their goals for
`B`: smaller or more deterministic, simpler strength class,
stutter-insensitive, fewer atomic propositions.

## 3. The interval is a lattice

Align `𝓘(¬φ)` and `𝓘(K)` once, on the generated product `T`; both
verdict maps ride along. Define the two **endpoint surgeries**

    P_min := P_{¬φ} ∩ P_K          P_max := P_{¬φ} ∪ P_K^c

— pointwise Boolean operations on pair sets, free. By construction
`L(P_min) = ℒ(¬φ) ∩ ℒ(K)` and `L(P_max) = ℒ(¬φ) ∪ ℒ(¬K)`: the
restriction and relaxation of [DPT25, §4], as pair sets on one table.
The interval is never empty (`P_min ⊆ P_{¬φ} ⊆ P_max`), and the legal
on-table `B`s are exactly the saturated `Q` with `P_min ⊆ Q ⊆ P_max`.

**Proposition 3.1 (the lattice is `2^F`).** `P_max \ P_min = P_K^c`,
and the saturated pair sets in `[P_min, P_max]` are exactly the sets
`P_min ⊔ ⋃S` for `S` a subset of

    F := { conjugacy classes of linked pairs of T outside P_K }.

The interval is thus isomorphic to the powerset lattice `2^F`.

*Proof.* The identity is propositional:
`x ∈ P_max \ P_min ⟺ (x_φ ∨ ¬x_K) ∧ ¬(x_φ ∧ x_K) ⟺ ¬x_K` (where
`x_φ, x_K` abbreviate membership in `P_{¬φ}, P_K`). `P_min`, `P_max`
and `P_K` are saturated (Boolean surgeries preserve saturation), so a
saturated `Q` in the interval decomposes as `P_min ⊔ (Q \ P_min)` with
`Q \ P_min` a saturated subset of `P_K^c`, i.e. a union of conjugacy
classes of `F`; conversely every such union is saturated and lands in
the interval. ∎

The reading: **choosing `B` is choosing one verdict bit per conjugacy
class of `ℒ(¬K)`**; on the `K`-side classes the verdict is `¬φ`'s,
non-negotiable. `|F|` — the freedom in bits — is computed by one
saturation pass and is a per-problem statistic with no automata-side
counterpart (§7). `|F| = 0` means `K` already decides everything about
`¬φ`'s boundary: the interval is a point and the endpoint checks below
are the whole story.

**The two decisive checks are one scan each.**

- `L(P_min) = ∅ ⟺ ℒ(K) ⊆ ℒ(φ) ⟺ K ⊨ φ`: the property holds on any
  system satisfying `K` — no model checker runs. On failure, the first
  accepting cell yields the *minimal* lasso in `ℒ(¬φ) ∩ ℒ(K)`: "`K`
  does not settle `φ`, and here is the shortest behavior it leaves
  open."
- `L(P_max) = Σ^ω ⟺ P_max = linked ⟺ ℒ(K) ⊆ ℒ(¬φ) ⟺ K ⊨ ¬φ`: every
  run of the nonempty `S` is a counterexample. On the automata side
  this is a universality test, exponential on TGBA, which [DPT25] must
  dodge by re-translating a formula for `φ`; here it is emptiness of
  `P_max^c` — one flip away, exactly symmetric with the first check.
  On failure, the minimal lasso in `ℒ(φ) ∩ ℒ(K)`.

On the MCC'22 benchmark, the two endpoint strategies of [DPT25] solve
≈52% of problems outright, with a reported asymmetry ("empty seems
easier than universal") that their syntactic universality check
explains; on the invariant the two checks are the same scan on
complementary pair sets, and the kill rate should reproduce
symmetrically (§7).

**Certificate discipline.** Both checks, and every test in §§4–5,
factor through the membership oracle, so [SωSC26, Prop 3.2] applies:
every verdict is accompanied by the globally minimal witness lasso —
counterexamples a user can replay, ordered smallest-first.

## 4. Simpler classes, exactly: the interval test and the ladder

[DPT25] *hopes* for a weaker strength class as a side effect of label
rewrites. On the lattice, "is a weaker class available at all" is a
question with an exact answer, and one lemma dispatches all of its
instances.

**Lemma 4.1 (interval test).** Let `𝒦` be a family of saturated pair
sets on `T`, closed under intersection, with `linked ∈ 𝒦` (a Moore
family on the finite lattice of saturated sets). Then
`ρ_𝒦(Q) := ⋂{Q' ∈ 𝒦 : Q' ⊇ Q}` is a closure operator with image `𝒦`,
and

    𝒦 ∩ [P_min, P_max] ≠ ∅   ⟺   ρ_𝒦(P_min) ⊆ P_max ,

in which case `ρ_𝒦(P_min)` is the least member. Dually, if `𝒦` is
union-closed with `∅ ∈ 𝒦`, the kernel operator `κ_𝒦` gives the test
`P_min ⊆ κ_𝒦(P_max)` and the greatest member; if `𝒦` is closed under
both, its members form the sub-interval `[ρ_𝒦(P_min), κ_𝒦(P_max)]`.

*Proof.* If some `B ∈ 𝒦` satisfies `P_min ⊆ B ⊆ P_max`, then
`ρ_𝒦(P_min) ⊆ ρ_𝒦(B) = B ⊆ P_max` by monotonicity and idempotence.
Conversely `ρ_𝒦(P_min)` is itself a member of `𝒦` containing `P_min`.
The dual and the sub-interval statement are immediate. ∎

The lemma reduces each class to two questions: is the on-table family
`𝒦` the right proxy for the semantic class (the *locality* question,
taken up below), and is `ρ_𝒦` cheap. The ladder answers both, rung by
rung.

### 4.1 Safety and co-safety: the topological hulls

**Proposition 4.2.** A safety property `B` exists in the interval iff
`P̄_min ⊆ P_max`, and then `B = P̄_min` — the safety closure of the
lower endpoint — is the least one, *among all ω-regular languages, not
merely on-table ones*. Dually, a co-safety `B` exists iff
`P_min ⊆ P̊_max`, with greatest witness `P̊_max`. Both tests are one
`O(n²)` stem-liveness scan.

*Proof.* Lemma 4.1 with `𝒦` = closed pair sets — a Moore family: an
intersection of closed pair sets recognizes the intersection of their
languages, closed again, and `linked` recognizes `Σ^ω`; `ρ` is the
hull `P̄` of [SωSC26, Prop 6.1]. Locality — the reason "among all ω-regular
languages" is warranted — is Prop 6.1 itself: its proof identifies
`L(P̄)` with the *topological* closure `cl(L(P_min))`, a
presentation-independent object, and any safety `B ⊇ L(P_min)` in the
semantic interval satisfies `cl(L(P_min)) ⊆ B` by minimality of the
closure. ∎

Both families are also union-closed, so the sub-interval clause of
Lemma 4.1 hands each test its other endpoint; in particular, on a
co-safety "yes" the **least** member is the open hull `ρ̊(P_min)`,
and it is concrete: an open verdict is decided by a finite stem
prefix, so an open pair set is one whose stem set is a right ideal,
and `ρ̊(Q)` is the set of linked pairs whose stem is a right multiple
of a stem of `Q` (a set conjugacy already saturates, since conjugacy
preserves the stem's `R`-class, §2).

Reading: *given `K`, the model check reduces to a safety check* —
decided exactly, canonical checker handed over. On "no", the first
pair in `P̄_min \ P_max` yields a minimal lasso that every safety
property containing the mandatory behaviors must accept and that `K`
forbids adding: impossibility, certified.

### 4.2 Obligation: forcing on `R`-classes

By [SωSC26, Thm 6.6(3)], an on-table obligation is an `R`-class-
constant verdict: `θ : {R-classes of linked stems} → {0,1}` with
`B_θ := {(s,e) linked : θ(R(s)) = 1}`. Any such `B_θ` is automatically
saturated, because conjugacy preserves the stem's `R`-class (§2). The
interval constrains `θ` pointwise: call `r` **forced to 1** if some
pair of `P_min` has its stem in `r`, **forced to 0** if some linked
pair outside `P_max` does.

**Proposition 4.3.** An obligation `B` exists on `T` iff no `R`-class
is forced both ways — checkable in `O(|linked|)` after one SCC pass of
the right-Cayley graph. When consistent, the obligation members of the
interval form the sub-lattice `{θ : forced₁ ≤ θ ≤ ¬forced₀} ≅
2^{unforced}` — the D1 lattice reproduced one level up — with least
member `ρ_obl(P_min)` (θ = forced₁) and greatest `κ_obl(P_max)`
(θ = ¬forced₀).

*Proof.* Lemma 4.1 with `𝒦 = {B_θ}`: `𝒦` is closed under union and
intersection (pointwise on `θ`), and `ρ_obl(Q) = B_{θ}` with `θ(r) = 1`
iff `r` contains a stem of `Q` — the least `R`-class-constant superset.
`ρ_obl(P_min) ⊆ P_max` unfolds to exactly "no class forced both ways":
a pair `(s,e) ∈ B_{forced₁} \ P_max` is a linked pair outside `P_max`
whose stem class is forced to 1, i.e. a class forced both ways, and
conversely. Membership of `B_θ` in the obligation class (not merely in
a formal family) transfers to the unreduced table in both directions:
(⇐) an `R`-class-constant `B_θ` is a Boolean combination of closed
pair sets of `T` (the hull fixpoints of [SωSC26, §6]), each a safety
language on any recognizing table (Prop 6.1), hence an obligation; (⇒) an obligation `B` in the interval
has `R`-class-constant verdict on its own syntactic table (Thm 6.6),
and the reduce morphism `h : T → 𝓘(B)` preserves `R` (`s R s' ⟹
h(s) R h(s')`), so `Val_B` is `R`-class-constant on `T` as well. ∎

### 4.3 Recurrence and persistence: Horn hulls

The chain characterizations (§2) are **Horn conditions** on `P` — each
a closure rule of the shape "pairs in `P` force a pair into `P`":
recurrence is closure of `P` under

    (s, e) ∈ P,  f ≤_H e,  f a loop of s   ⟹   (s, f) ∈ P ,

persistence the mirror. The least superset of `Q` closed under a Horn
rule *and* conjugacy saturation is a monotone fixpoint — alternate the
rule with `sat(·)`, at most `|linked|` rounds, polynomial.

**Proposition 4.4 (sketch).** `∃` recurrence `B` in the interval `⟺`
`rec-hull(P_min) ⊆ P_max`; `∃` persistence `B` `⟺`
`rec-hull(P_max^c) ⊆ P_min^c` (complement exchanges the two classes
and reverses the interval: `B ∈ [P_min, P_max] ⟺ B^c ∈ [P_max^c,
P_min^c]`). The dual costs *one complement flip* — where the automata
side would pay a complementation before even posing the question.

*Two points to nail down in the full proof.* (i) The chain
characterization is stated on the syntactic algebra [CP99]; on the
unreduced `T` the (⇒) direction needs a violation in `𝓘(B)` to lift to
`T`, which follows from the standard finite-semigroup lemma that the
idempotent order lifts along surjective morphisms (idempotents lift,
and `≤_H`-related idempotent pairs lift to `≤_H`-related idempotent
pairs); the (⇐) direction is the easy one (`h` preserves `≤_H` and
verdicts). (ii) Locality: the test decides existence of an *on-table*
recurrence `B`; whether the semantic least recurrence superset can
escape the table (as the stutter hull does, §5) is open — see §4.5.

With Propositions 4.2–4.4 the **entire safety–progress ladder**
[MP92, ČP03] has exact polynomial interval tests — [DPT25]'s "simpler
strength class" goal answered exactly at every rung, each hit a
strength-class drop the emptiness check feels, each miss certified.

### 4.4 Inside the band: the minimal Wagner degree is a read-off

When obligations exist (Prop 4.3), which is the *simplest* one? By
[SωSC26, Prop 6.7] the Wagner coordinates of `B_θ` are the longest
`θ`-alternating strictly-`R`-descending sequences, per starting
polarity. Minimizing over the free classes looks like a search over
`2^{unforced}`; it is not:

**Proposition 4.5 (sketch — greedy band minimization).** Encode an
assignment of alternation depths as a *level function*
`ℓ : R-classes → {0, …, k}`, monotone along the `R`-descent order, with
the parity of `ℓ(r)` prescribed on forced classes (one fixed
parity–polarity convention per coordinate). A `θ` with maximal alternation
`≤ k` exists iff such an `ℓ` exists, and the pointwise-least monotone
parity-respecting `ℓ*` is computed bottom-up over the condensation in
one pass (take the max of the descendants' levels, bump by one if the
forced parity disagrees; free classes take the max unmodified). The
minimal achievable degree pair is read off `ℓ*`. Polynomial, no
search; the witness `θ*` is the parity of `ℓ*`.

*Status.* The encoding equivalence (alternation depth ≤ k ⟺ monotone
parity level function — the Hausdorff difference-hierarchy normal form
[Wag79] transported to the `R`-DAG) and the pointwise-least-solution
argument are routine; the two-coordinate simultaneity (`n⁺` and `n⁻`
minimized by one `ℓ*`, or by two one-sided passes) is the open half
of the proof.
Note the free classes are not innocent: a free class sitting above
forced classes of both polarities *must* create one alternation
whichever way it is set — the minimum is not "longest forced-only
alternation", which is why the level-function detour is needed.

### 4.5 Locality, separators, and the minimization landscape

**Locality (the on-table/semantic seam).** "`B` in the interval" means,
for the model checker, *any* ω-regular language between the bounds; the
calculus natively enumerates the on-table ones. The two coincide for a
class `𝒦` exactly when the semantic `𝒦`-hull of `L(P_min)` is
recognized by `T`. Status per rung: **safety/co-safety — local**
(Prop 4.2, the hull is topological); **stutter invariance — provably
non-local** (§5, the counterexample); **obligation, recurrence,
persistence — open**. For these classes the semantic question is a
class-separation problem (`does some obligation separate L(P_min) from
L(P_max)^c?`), adjacent to the separation program of Place–Zeitoun
[PZ16] on the ω-side, where the global least member need not even
exist; the on-table test remains exact for the question it answers,
and on-table witnesses are the useful ones (they stay in the
calculus). The locality map is itself a contribution-shaped question
the automata side cannot even phrase.

**Separator synthesis, free of charge.** For disjoint `L₁, L₂`, the
interval `[P_{L₁}, P_{L₂}^c]` on their aligned table turns every test
above into "is there a *safety* (co-safety, obligation, recurrence,
persistence) property separating `L₁` from `L₂`" — e.g. ∃ safety
separator ⟺ `P̄_{L₁} ∩ P_{L₂} = ∅`. Given-that is the special case
`L₁ = ℒ(¬φ) ∩ ℒ(K)`, `L₂ = ℒ(φ) ∩ ℒ(K)` — [DPT25, §9] itself notes
the connection to separation; here the connection is an algorithm.

**The minimization landscape.** Three tiers. (a) Class existence
per rung: polynomial, settled above. (b) Exact minimal Wagner degree:
polynomial within the obligation band (Prop 4.5); open in general —
the fine structure above the band mixes loop-sensitivity with the free
classes. (c) The [DPT25]-native objective, minimal `|𝒞|` after reduce:
the interval constrains lasso verdicts exactly as labeled samples
constrain an automaton in Gold-style identification, so NP-hardness à
la minimal-consistent-DFA [Gol78] is the natural conjecture and
reduction route; worth settling, in either direction. Note the
pleasant inversion of [DPT25]'s caveat that "the smallest language
need not have the smallest automaton": on the invariant,
smallest-`|𝒞|` is a *well-posed* objective, because the object is
canonical per language.

### 4.6 A worked example: [DPT25]'s own, on the invariant

The running example of [DPT25, Figs. 2–3]:
`¬φ = F(a∧c) ∨ (GFb ∧ GF¬b)` given `K = FGb ∧ Gc`, over
`Σ = 2^{a,b,c}` (we write a letter as the set of propositions it makes
true: `{abc}`, `{bc}`, …). There, transition-wise Boolean bands
simplified by Minato's algorithm turn `A_{¬φ}` into an automaton for
`Fa`, observed to be "now terminal". Here is the same instance as
pair-set arithmetic.

**The tables.** A finite word carries three monotone bits `(σ, p, q)`
— *contains an `a∧c` letter* / *a `b` letter* / *a `¬b` letter* —
multiplying by bitwise OR, with
`Val_{¬φ}((σ_s,·,·),(σ_e,p_e,q_e)) = σ_s ∨ σ_e ∨ (p_e ∧ q_e)`. The
bit table — `[ε]` plus the six consistent triples (a nonempty word
has `p ∨ q = 1`) — *recognizes* `¬φ` but is not syntactic: `σ` is
absorbing and `Val` reads nothing else once it is set (`σ_s` alone
from the stem, `σ_e` overriding `(p_e, q_e)` in the loop), so a
`σ = 1` word has verdict 1 in every context and the three `σ = 1`
triples are one class. `𝓘(¬φ)` has **5 classes** — `[ε]`, `(0,0,1)`,
`(0,1,0)`, `(0,1,1)`, and the accepting sink `⊤` — with 9 linked
pairs. `𝓘(K)` has 4: `[ε]`, `BC` (all letters `b∧c`), `C` (all `c`,
some `¬b`), and the absorbing dirty class `D` (some `¬c`), with
`Val_K(s, e) = [k_s ≠ D] ∧ [k_e = BC]`. The generated product has
**10 classes** — `[ε]` and the consistent quadruples: over `BC` the
letters force `(p,q) = (1,0)`, giving `(0,1,0)` and `⊤`; over `C`,
`q = 1`, giving `(0,0,1)`, `(0,1,1)` and `⊤`; over `D`, all four
nonempty `¬φ`-classes — and both verdicts ride along. Every letter
class is idempotent (both formulas are `X`-free), so `T = T/∼` and
the §5 quotient test is trivially exact on this instance; the
phenomenon of §5 needs a stutter-sensitive pair (§5.2).

**Endpoints (§3).** A `P_min` pair's stem absorbs its loop, so
`σ_s ∨ σ_e` collapses: `P_min = {stems (⊤ | BC/C), loops with
k = BC}` — the language `F(a∧c) ∧ FGb ∧ Gc`. Both decisive
checks fail, each with a one-letter-loop minimal witness:
`k_settles_phi` returns `({abc})^ω` (the shortest behavior `K` leaves
open to `¬φ`), `k_refutes_phi` returns `({bc})^ω` (the shortest
`K`-behavior satisfying `φ`).

**No safety `B`, certified (Prop 4.2).** The dead classes are exactly
those with `k = D`, so `P̄_min = {(s,e) : k_s ≠ D}` — the language
`Gc` — and the cell of `({bc})^ω` lies in `P̄_min \ P_max`: the scan
refuses with that minimal lasso. Reading: any safety property
containing the mandatory behaviors must accept `({bc})^ω` — every
prefix of it extends into `ℒ(¬φ) ∩ ℒ(K)` — yet `K` allows it and `φ`
holds on it: a refusal no presentation-side rewrite can emit.

**Co-safety `B` exists; the interval brackets Minato.** The interior:
`σ` is absorbing, so `Live_{P_max^c} = {σ = 0, k ≠ D}` and
`P̊_max = {stems with σ = 1 or k = D}` — the language
`F(a∧c) ∨ F¬c = F(a ∨ ¬c)`. Every `P_min` stem has `σ = 1`, so
`P_min ⊆ P̊_max`: **yes**, and by the sub-interval clause of
Lemma 4.1 the *on-table* guarantee members form exactly the bracket

    [ F(a∧c) ,  F(a ∨ ¬c) ]

— and every guarantee member, on-table or not, lies below the upper
hull, since the interior is a semantic object. (Least member: the
open hull of §4.1 — the right ideal of the `P_min` stems — and from
any `P_min` stem every `⊤`-row class is reachable, so the hull is all
of `F(a∧c)`. The route matters even on this toy: the instance's
freedom is `|F| = 25` bits, so the `2^F` enumeration behind any naive
search is already out of reach — the hull is the algorithm, not a
shortcut.)
[DPT25]'s `Fa` sits strictly inside the bracket —
`F(a∧c) ⊆ Fa ⊆ F(a∨¬c)` — and is itself **off-table**: no class of
`T` tracks `a` without `c`. Off-table members below the lower
endpoint exist too (e.g. "`a∧c` occurs before any `¬c`"): the bracket
delimits what the canonical algebra expresses, the upper endpoint
bounds everything. The heuristic landed a perfectly legal member; the
calculus names the canonical endpoints it landed between, and
certifies that the *class* is guarantee — which is exactly the "now
terminal" observation of their Figure 3, decided rather than noticed.

**The rung drop, read off.** On its own table, `Val_{¬φ}` is monotone
under adding loop bits, and `H`-descent in an OR-monoid *is* adding
bits: verdicts propagate down, so `¬φ` is a recurrence property
(§4.3). It is nothing lower: the stem `(0,1,1)` carries the loops
`(0,1,1) <_H (0,1,0)` with verdicts `1 > 0` — loop-sensitive, so not
an obligation, and accepting below while rejecting above, so not a
persistence property either. So the knowledge buys a
drop from recurrence to guarantee — from a full Büchi emptiness check
to reachability — and §4's tests deliver it with a canonical `B` and
a certificate at the rung below.

## 5. Stutter invariance, exactly

§6 of [DPT25] spends interval freedom to make `B` stutter-insensitive:
compute the closure `si(A)` (adds all partly-covered stutter classes),
adopt it if the added words avoid `K`; dually for the restriction. Both
are sound, neither is complete, and `sirestrict` is the only strategy
in their benchmark that times out. The algebraic account splits into a
recognition theorem, a negative surprise, and the exact test.

### 5.1 Recognition through the stutter quotient

**Proposition 5.1.** Let `π : T → T/∼` be the quotient of the table by
the smallest monoid congruence with `λ(a)·λ(a) ∼ λ(a)` for every
letter (computable by union-find with closure under left/right letter
multiplication, polynomial). The stutter-invariant languages
recognized by `T` are exactly the pullbacks `π⁻¹(P')` of saturated
pair sets `P'` on `T/∼`.

*Proof.* (⊇) `T/∼` has idempotent letter images by construction, and
the ⇐ direction of [SωSC26, Prop 5.1] is valid on any recognizing
table (§2): every `T/∼`-recognized language is stutter-invariant; its
pullback is recognized by `T` through `π`. (⊆) Let `L'` be
stutter-invariant and `T`-recognized. Its syntactic morphism factors
as `η = h ∘ fold` for a morphism `h : T → 𝓘(L')` — well-defined
because fold-equal words share every `L'`-context through the
recognizing pair set, surjective because `T` is generated. By
[SωSC26, Prop 5.1] (⇒), `η(a)² = η(a)`, so `h(λ(a)²) = h(λ(a))`: the kernel
of `h` is a congruence containing the generating pairs of `∼`, hence
`h` factors through `π`, and `L'` is a pullback. ∎

So the on-table stutter-invariant languages form a Boolean subalgebra,
and the least one above `L(Q)` is computable:

    sc(Q)  :=  π⁻¹( sat( forced_π(Q) ) ) ,

where `forced_π(Q)` collects the `T/∼`-associated pairs of `L(Q)`'s
lassos — one pass over `T`'s cells: for each cell `(c,d)` with
`Val_Q(c,d) = 1`, add the pair `(π(c)·e, e)`, `e = idem(π(d))` — and
`sat` is the conjugacy-saturation fixpoint. (The pullback of
`sat(forced)` contains `L(Q)` — every lasso of `L(Q)` maps to a
forced pair, and containment between ω-regular languages is decided
on lassos; conversely every saturated `P'` whose pullback contains
`L(Q)` must contain each forced pair, hence `sat(forced)`; pullback
is monotone, so `sc(Q)` is least.)

The natural conjecture is that `sc(P_min) ⊆ P_max` decides
stutterization. It does not.

### 5.2 The hull escapes the table

**Theorem 5.2 (non-locality of the stutter hull).** There are `¬φ`,
`K` such that a stutter-invariant ω-regular `B` exists in the interval
while `sc(P_min) ⊄ P_max`: the quotient test of §5.1 is sound but not
complete, because the global stutter closure `SC(L(P_min))` need not
be recognized by any table aligned from `𝓘(¬φ)` and `𝓘(K)`.

*Proof (the two-letter counterexample).* Take
`ℒ(¬φ) = {(ab)^ω}` and `ℒ(K) = {(ab)^ω, (ba)^ω}` — "the system
alternates, in one of the two phases". The interval is
`[{(ab)^ω}, Σ^ω \ {(ba)^ω}]`, and `B = SC({(ab)^ω})` — the words
destuttering to `(ab)^ω` — is a stutter-invariant ω-regular member
(it avoids `(ba)^ω`, whose normal form differs): the semantic answer
is **yes**. Now the table: `synt({(ab)^ω})` has six classes — `[ε]`,
the four classes `A_{xy}` of alternating words by first letter `x` and
last letter `y`, and the junk class `Z` (any word with a repeated
adjacent letter; all such words are interchangeable in every context
of the single word `(ab)^ω`) — and on the aligned `T` the two
components merge in lockstep (a word repeats an adjacent letter for
one language iff for the other), so the cascade below runs on `T`
exactly as written. Forcing
`λ(a)² ∼ λ(a)` merges `A_{aa} ∼ Z` (since `λ(a) = A_{aa}` and
`λ(a)² = Z`), then `A_{bb} ∼ Z`, then `A_{ab} = A_{aa}·A_{bb} ∼ Z` and
`A_{ba} ∼ Z`: `T/∼` collapses to `{[ε], Z}`, every lasso lands on the
single pair `(Z, Z)`, and `sc(P_min) = Σ^ω ⊄ Σ^ω \ {(ba)^ω}`. The
quotient test says **no**. The obstruction is not an artifact of a
poor alignment: both *syntactic* tables merge `aa` and `bb` — each is
junk in every context of either language — every table the calculus
derives from its canonical inputs (generated products, quotients)
inherits the merge, and `SC({(ab)^ω})` separates `aa(ab)^ω` (in) from
`bb(ab)^ω` (out). No derived table recognizes `SC`. ∎

Two honest remarks. First, this is a *locality* failure, not
unsoundness: when the quotient test passes, `sc(P_min)` is a valid,
canonical, on-table witness. Second, on this very instance [DPT25]'s
`sirelax` heuristic *succeeds* (the words `si(A)` adds avoid `K`): the
presentation-side closure reaches an off-table witness the naive
algebraic quotient cannot. The exact test must therefore do more than
quotient — and it can, in polynomial time.

### 5.3 The exact test: stutter self-alignment

**Theorem 5.3 (exact stutterization — sketch).** A
stutter-invariant ω-regular `B` exists in the interval iff
`SC(L(P_min)) ⊆ L(P_max)`, iff the **stutter alignment** of `T` with
itself detects no conflict:

    R_st := { (p, p') : some stutter-equivalent lassos α ≈ β
                        have associated T-cells p and p' } ,

and the test is `R_st ∩ ((Val_{P_min}{=}1) × (Val_{P_max}{=}0)) = ∅`.
`R_st` is computable in polynomial time. On "yes", the canonical least
witness is `SC(L(P_min))` — possibly off-table (Thm 5.2): re-enter it
(it is spec-sized) to continue in-calculus. On "no", the first
conflicting cell pair certifies: two stutter-equivalent behaviors, one
mandatory, one forbidden — no stutter-invariant property can separate
them, whatever the presentation.

*Construction sketch.* The first equivalence is the closure-operator
argument (`SC` is the global least stutter-invariant superset, §2).
For the second: containment of ω-regular languages is witnessed on
lassos, and a lasso's stutter class meets an ω-regular set iff it
meets it in a lasso (the intersection is ω-regular and nonempty), so
the lasso-level relation suffices. Two
stutter-equivalent lassos admit block-synchronized presentations over
a common destuttered base — the block-exponent sequence of an
ultimately periodic word is ultimately periodic — so `α = u·v^ω`,
`β = u'·v'^ω` where `u, u'` pump the same stutter-free stem `x` and
`v, v'` pump the same stutter-free, cyclically stutter-free loop `y`
(the eventually-constant normal forms `w·a^ω` handled as a separate,
simpler case). Pumping one base letter `b` multiplies the fold by an
arbitrary element of the cyclic set `⟨λ(b)⟩ = {λ(b), λ(b)², …}` —
*independently* on the two tracks. `R_st` is therefore reachability in
a walk over states `(last base letter, c, c') ∈ Σ × 𝒞 × 𝒞`: step by a
fresh letter `b ≠` last, multiply the tracks by chosen elements of
`⟨λ(b)⟩`; the stem relation is the reachable set from `([ε],[ε])`, the
loop relation is the same walk with matched first/last boundary
letters, closed cyclically, followed by the usual idempotent
renormalization of associated pairs. State space `O(|Σ|·n²)`, at most
`O(|Σ|·n²)` transitions per state (the cyclic-set sizes bound the
choices): polynomial, `O(|Σ|²·n⁴)` transitions in all, one
self-alignment. ∎(sketch)

**The two-tier algorithm.** Run the quotient test (§5.1) first —
cheap, witness on-table, stays in the calculus. On failure, run the
self-alignment (§5.3) — exact, witness may cost one re-entry. The gap
between the tiers is itself a certified diagnostic no automata
pipeline emits: *"the interval contains stutter-insensitive
properties, but none the aligned algebra can express."* Against
[DPT25, §6]: `sirelax`/`sirestrict` each test one candidate (`si(A)`,
`A ⊗ ss(A)^c`) and give up otherwise — the exact test subsumes both
candidates and all others, replaces the costly complement inside
`ss(·)` (their only source of timeouts) with scans, and returns the
least witness rather than an incidental one. Michaud–Duret-Lutz's
`sl(A) ⊗ sl(Ā)` product [MD15] finds its algebraic counterpart in the
self-alignment.

## 6. The same move elsewhere, and closing at the formula level

### 6.1 Shedding atomic propositions (the letter-fusion congruence)

[DPT25] drops `K`-only atomic propositions by existential
quantification, over-approximated per Boolean subformula (`QE(P,K)`),
with the honest argument that any over-approximation of knowledge is
still knowledge. On the invariant, the *exact* projection is the
powerset-priced frontier operation [SωSC26, §4] — and the free sound
approximation is §5.1's machinery under a different congruence: let
`π_p : T_K → T_K/∼_p` quotient by the smallest congruence merging
`λ(ℓ) ∼ λ(ℓ')` for all valuation pairs differing only on the shed
propositions `p`, and take

    K_p := π_p⁻¹( sat( forced_{π_p}(P_K) ) ) ,

the least `p`-blind on-table superset of `ℒ(K)`. **Stutterization and
AP-shedding are one move** — pull through a letter-identifying
congruence and back; only the generating relations differ
(`λ(a)² ∼ λ(a)` vs `λ(ℓ) ∼ λ(ℓ')`). The locality caveat returns with
a twist: here the semantic least `p`-blind superset *is* the exact
projection `∃p.K`, re-expanded over `Σ` — exponential — so the
on-table hull is the honest cheap tier, and exactness is priced where
the frontier says it must be. Open comparison
(small, self-contained): `K_p` versus
`QE(P,K)` — `QE` loses inter-subformula correlations (the paper's own
`X(a∧b) ∧ X(ā∧b)` example), `K_p` loses only what the algebra cannot
see `p`-blindly; conjecture: incomparable in general.

### 6.2 Integrating a knowledge base, losslessly

[DPT25, §7] integrates facts `K₁, …, K_n` one at a time, accepting a
loss of precision to avoid the conjunction automaton. On the invariant
the incremental story is *exact*: maintain the running aligned table
and interval; integrating `K_{i+1}` is one more align (the only
product-priced move) plus two pointwise updates,
`P_min ∩= P_{K_{i+1}}`, `P_max ∪= P_{K_{i+1}}^c`, and every
intermediate interval is exactly the interval of the conjunction so
far (the endpoint surgeries are pointwise Boolean and the running
product is generated by the same factors, so the updates commute with
conjunction). No delayed label choice, no precision ledger; the price
is table growth, and the census measurements give the reason for
optimism — correlated operands realize a small fraction of the
`n₁·n₂` rectangle (median 0.17, down to 0.06 for related tables
[SωSC26, §3.3]), and facts about one system are correlated by
construction. §7 measures the growth curve across real fact bases.
After choosing `B`, the product with
`S` is the mixed-product extension of the calculus
([SωSC26-ext, §1]): `S` never pays entry either.

### 6.3 LTL-given-that, end to end

When `φ` and `K` are both LTL, both tables are aperiodic, hence so is
the aligned `T` (a submonoid of a product of aperiodic monoids is
aperiodic), and by [SωSX26, Prop 5.11] **every on-table `B` in the
lattice is LTL-definable** — the lattice never leaves the variety,
however the free classes are cut. With the extraction of [SωSX26]
(`sos2ltl`), the pipeline closes at the formula level:

    φ, K  →  enter  →  choose B (§§3–5 criteria)  →  reduce
          →  sos2ltl  →  ψ : a formula, simpler than ¬φ,
                             equivalent to it given K

— **LTL simplification given prior knowledge**, formula in, formula
out, the operation [DPT25] explicitly cannot reach (its own ledger:
Spot has no automaton→LTL path). The §4 ladder makes the choice
*principled*: minimize the strength class first — each rung caps the
Manna–Pnueli shape of any defining formula (a safety `B` admits a
`□`-shaped `ψ`, an obligation a Boolean combination of `□`/`◇`
shapes) — then size within the rung. The natural simplification
metrics — extracted formula size, `|𝒞|`, Wagner degree — are compared
in §7.

A second, self-standing question falls out: when `¬φ` comes from
an automaton and is *not* LTL-definable, is some `B` in the interval
LTL-definable — **definability given that**? The LTL-definable
saturated sets form a Boolean subalgebra, so Lemma 4.1 applies
abstractly, but no cheap hull is known — definability is a property of
each `B`'s own reduce, not a pointwise condition on `T`. Enumeration
over `2^F` decides it when `|F|` is small (§7 reports the
distribution); a polynomial read-off is open. This connects the
given-that program directly to the definability program ([SωSX26];
the aut2ltl NOT_LTL certificates).

## 7. Evaluation plan

Reuse the [DPT25] benchmark (MCC'22-derived, third-party: 1601 model
instances, ~150 knowledge facts each, 97 950 problems), and its
protocol — measure the property-side integration, not the downstream
model checker. Planned measurements, in dependency order:

1. **Endpoint reproduction.** The two scans of §3 against Table 1
   of [DPT25] (their p.min∃/p.max∃ solve 25 508 + 25 508 of 97 950;
   symmetric by construction here — their reported empty/universal
   asymmetry should vanish). Entry-price accounting per case
   (spec-sized; measured as in the calculus pipeline demonstration
   [SωSC26, §4]).
2. **Freedom distribution.** `|F|` in bits per problem (Prop 3.1) — the
   size of the space every other strategy searches; no automata-side
   counterpart exists.
3. **Ladder hit rates (§4).** Per rung: how often a safety / co-safety
   / obligation / recurrence / persistence `B` exists where `A_{¬φ}`'s
   class was stronger; each hit is a strength-class drop the emptiness
   check feels. Plus the band-minimal Wagner degree (Prop 4.5) against
   the raw degree.
4. **Two-tier stutter rates (§5).** Quotient-test yes / alignment-only
   yes / no. The middle bucket measures simultaneously how often
   exactness beats the [MD15]-style closure heuristics and how often
   witnesses must leave the table. Compare wall-clock against
   `sirelax`/`sirestrict` (the latter's timeouts should disappear —
   no complement is ever taken).
5. **Incremental growth curve (§6.2).** Running table size across each
   fact base, against the census's alignment-ratio prediction.
6. **Formula-level table (§6.3, needs `sos2ltl`).** `¬φ ⇝ ψ` with
   sizes and Manna–Pnueli shapes.

Independently of the MCC data, the census emulates incremental
verification *with free ground truth*, in three tiers. (a) An
all-pairs endpoint sweep — one alignment per unordered pair, three
scan bits (disjointness, both inclusions) — yields the endpoint kill
matrix plus two reusable artifacts, the inclusion digraph and the
disjointness graph of the census (the implication matrices of [DR18]
are a sub-product). (b) The full battery runs on the *asymmetric*
stratum — complex `¬φ`, fact-shaped `K` (small tables, low rungs, the
shape of [DPT25]'s gleaned knowledge) — where the simpler-class claims
earn their keep. (c) Fixing a census language as the "system" `L_S`,
the inclusion digraph hands over its genuine knowledge candidates
(`K ⊇ L_S`), the exact verdict `S ⊨ φ` is one scan, and integrating
facts one at a time measures the knowledge-decides rate against that
ground truth — while asserting, per step, the two laws §6.2 stakes:
*monotonicity* (`P_min` only shrinks, `P_max` only grows, so every
verdict improves monotonically as knowledge accumulates) and
*losslessness* (the running interval byte-equals the one-shot
conjunction's after reduce). Both are falsifiable claims of this
paper, run as campaign assertions.

**First census-shaped data.** The interval core (§3) and the ladder
(§4) are implemented, gated, and campaign-run on 700 same-stratum
census pairs; the numbers are census-shaped — random pairs, none of
the MCC's realistic bias toward fact-shaped `K` — but already
load-bearing. *Freedom* (item 2): `|F|` min 0 / median 20 / p95 124 /
max 458 bits, and the point interval `|F| = 0` occurs (a pair where
`K` settles `φ` outright). The median already puts `2^F ≈ 10⁶` at the
edge of enumeration and the tail far beyond it: at census sizes the
hulls of §4 are the only route, not an optimization. *Endpoints*
(item 1's shape): settles ≈ 7% and refutes 4–6% per direction on
random pairs; settles is measured identical under operand swap, the
symmetry §3 predicts; and the complement-partner stratum settles
100%, as it must. *Ladder* (item 3), per rung — a member exists / raw
`¬φ` already on the rung / a strict drop is available, out of 700:
safety 318/169/149, co-safety 321/164/157, obligation 453/347/106,
recurrence 516/424/92, persistence 529/429/100. Read: on ~21% of
random census pairs, knowledge buys a strict drop to safety — a
Büchi-emptiness-to-reachability discount before any realistic
asymmetry is dialed in. *Validation riding along:* the
recurrence/persistence orientation of §2 agrees with the census chain
coordinates on all 6 222 languages (and decisively disagrees under
the swapped orientation — 4 914 of 6 222); the Horn hull of Prop 4.4
passes the closure-operator laws (extensive, monotone, idempotent,
saturated output, fixpoint iff recurrence) with zero violations; and
on all 264 campaign cases with `|F| ≤ 12`, exhaustive enumeration of
the `2^F` lattice reproduces every rung verdict, the returned
canonical member equal to the intersection (Moore rungs) resp. union
(kernel rungs) of the enumerated members. Every refusal certificate
replayed on both source automata.

The protocol follows the calculus campaigns: per-case budgets, seeded
and checkpointed runs, machine-readable outputs promoted to a
versioned reference tree. The first gate is the counterexample of
§5.2, run three ways — quotient test, self-alignment, and the
presentation-side `sirelax` — which must answer
insufficient / yes / yes.

## 8. Related work

**The automata-side original.** [DPT25] created the framework — the
interval theorem, the endpoint strategies, the Boolean bands with
Minato covers (§5 there), the stutter closures under knowledge
(§6), incremental integration (§7), and the MCC evaluation. This paper
is its algebraic double: same soundness theorem, same goals, but the
interval represented exactly, the class questions decided rather than
probed, and witnesses canonical. The two are complementary in a
precise sense (§5.2): presentation-side closures can reach off-table
witnesses cheaply; the calculus knows *whether* and *what*, the
automata side renders it — the exit acceptor of the chosen `B` still
deserves their §5 grooming against `A_K`, and the SG/TG bands apply to
it verbatim.

**Knowledge in verification.** Invariant-based property simplification
for CTL [BDJ+18] and quasi-invariants [LNO+14] are special cases of
knowledge; Dureja–Rozier's implication matrices across a formula set
[DR18] are subsumed by the §3 endpoint scans (their `f₁ ⇒ f₂` is
`L(P_min) = ∅` for the pair), which additionally simplify when no
implication holds. Blahoudek et al.'s refinement under mutual
exclusion of propositions [BDRS15] is the letter-level shadow of §6.1.
Assume–guarantee reasoning shares the "given that" phrase but not the
problem: there `K` is a contract to be discharged, here it is
established fact spent to simplify a different check.

**Separation.** The existence tests of §4 are decision procedures for
separator synthesis by class over ω-regular languages — the
effective-separation program pursued for first-order fragments over
finite words by Place–Zeitoun [PZ16], here in the topological/Wagner
dimension, made algorithmic by the hull surgeries. [DPT25, §9] already
observed that given-that *is* a separation problem; the lattice makes
the observation operational.

**Stutter invariance.** The closure constructions and checks are
classical [HK96, PWW98, MD15]; §5 relocates them: the check is a
letter-idempotency scan [SωSC26, Prop 5.1], the closure is exact but
possibly off-table (Thm 5.2 — a phenomenon, to our knowledge,
unremarked), and the knowledge-bounded stutterization of [DPT25, §6]
gets an exact polynomial decision (Thm 5.3).

**Algebraic foundations.** ω-semigroups, linked pairs, conjugacy
[PP04]; the Wagner hierarchy on the syntactic algebra [Wag79, CP97,
CP99, SW08]; the ladder [Lan69, MP92, ČP03]. The given-that lattice
is, to our knowledge, the first use of the syntactic ω-semigroup as
the *state space of a synthesis problem* — choosing a language under
interval constraints — rather than as a recognizer or classifier; the
program it extends is [SωS26] (construction), [SωSC26] (calculus),
[SωSX26] (extraction), [SωSN26] (census).

## 9. Conclusion

Prior knowledge turns "translate `¬φ`" into "choose the simplest
representative of an interval of languages". On automata the interval
is invisible — only presentations of a few members can be built and
compared; on the syntactic invariant it is a finite lattice with
measured freedom, two endpoint scans that decide half of a competition
benchmark's problems outright, exact polynomial answers to every
strength-class question the model checker cares about, a resolved —
and subtler than conjectured — stutterization story, lossless
knowledge accumulation, and, over LTL, a formula-to-formula
simplification no automata toolbox offers. The exponentials sit where
they always did: at entry, paid once per spec-sized object, never per
question.

The open edges are stated where they live: the locality map of §4.5
(which semantic hulls stay on-table), the lifting details of Prop 4.4,
the simultaneity write-up of Prop 4.5, the `|𝒞|`-minimization
hardness (Gold route, §4.5), the `K_p` vs `QE` comparison (§6.1), and
definability-given-that (§6.3). None blocks the evaluation of §7,
which sits directly on the existing calculus implementation, gated
first by the counterexample of §5.2.

---

## References

- **[Arn85]** A. Arnold. *A syntactic congruence for rational
  ω-languages.* TCS 39 (1985) 333–335.
- **[BDJ+18]** F. Bønneland, J. Dyhr, P. G. Jensen, M. Johannsen,
  J. Srba. *Simplification of CTL formulae for efficient model
  checking of Petri nets.* Petri Nets 2018, LNCS 10877.
- **[BDRS15]** F. Blahoudek, A. Duret-Lutz, V. Rujbr, J. Strejček. *On
  refinement of Büchi automata for explicit model checking.* SPIN
  2015, LNCS 9232.
- **[BRS99]** R. Bloem, K. Ravi, F. Somenzi. *Efficient decision
  procedures for model checking of linear time logic properties.* CAV
  1999, LNCS 1633.
- **[ČP03]** I. Černá, R. Pelánek. *Relating hierarchy of temporal
  properties to model checking.* MFCS 2003, LNCS 2747.
- **[CP97]** O. Carton, D. Perrin. *Chains and superchains for
  ω-rational sets, automata and semigroups.* IJAC 7(6) (1997).
- **[CP99]** O. Carton, D. Perrin. *The Wagner hierarchy.* IJAC 9(5)
  (1999).
- **[DPT25]** A. Duret-Lutz, D. Poitrenaud, Y. Thierry-Mieg.
  *Simplifying LTL Model Checking Given Prior Knowledge.* Petri Nets
  2025, LNCS, pp. 433–456.
- **[DR18]** R. Dureja, K. Y. Rozier. *More scalable LTL model
  checking via discovering design-space dependencies (D³).* TACAS
  2018.
- **[Gol78]** E. M. Gold. *Complexity of automaton identification from
  given data.* Inf. Control 37 (1978) 302–320.
- **[HK96]** G. J. Holzmann, O. Kupferman. *Not checking for closure
  under stuttering.* SPIN 1996.
- **[Lan69]** L. H. Landweber. *Decision problems for ω-automata.*
  Math. Systems Theory 3(4) (1969).
- **[LNO+14]** D. Larraz, K. Nimkar, A. Oliveras,
  E. Rodríguez-Carbonell, A. Rubio. *Proving non-termination using
  Max-SMT.* CAV 2014.
- **[MD15]** T. Michaud, A. Duret-Lutz. *Practical stutter-invariance
  checks for ω-regular languages.* SPIN 2015, LNCS 9232.
- **[MP92]** Z. Manna, A. Pnueli. *The Temporal Logic of Reactive and
  Concurrent Systems: Specification.* Springer, 1992.
- **[Pel94]** D. Peled. *Combining partial order reductions with
  on-the-fly model-checking.* CAV 1994, LNCS 818.
- **[PP04]** D. Perrin, J.-É. Pin. *Infinite Words: Automata,
  Semigroups, Logic and Games.* Elsevier, 2004.
- **[PWW98]** D. Peled, T. Wilke, P. Wolper. *An algorithmic approach
  for checking closure properties of temporal logic specifications
  and ω-regular languages.* TCS 195(2) (1998).
- **[PZ16]** T. Place, M. Zeitoun. *Separating regular languages with
  first-order logic.* LMCS 12(1), 2016.
- **[SW08]** V. Selivanov, K. W. Wagner. *Complexity of topological
  properties of regular ω-languages.* Fund. Inform. 83(1–2) (2008).
- **[SωS26]** Y. Thierry-Mieg, with Claude (Anthropic). *Constructing
  the syntactic ω-semigroup from a deterministic Emerson–Lei
  automaton.* Working draft, 2026.
- **[SωSC26]** Y. Thierry-Mieg, with Claude (Anthropic). *Computing
  with ω-regular languages in canonical form: a calculus on the
  syntactic ω-semigroup.* Working
  draft, 2026 (`sos_calculus.md`); the queued extensions
  (`sos_calculus_extensions.md`) are cited as [SωSC26-ext].
- **[SωSN26]** Y. Thierry-Mieg, with Claude (Anthropic). *A census of
  syntactic ω-semigroups.* Working draft, 2026.
- **[SωSX26]** Y. Thierry-Mieg, with Claude (Anthropic). *The LTL
  frontier from the syntactic ω-semigroup: certificates, formulas,
  and the shape of the cut.* Working draft, 2026.
- **[Val93]** A. Valmari. *On-the-fly verification with stubborn
  sets.* CAV 1993.
- **[Var07]** M. Y. Vardi. *Automata-theoretic model checking
  revisited.* VMCAI 2007, LNCS 4349.
- **[Wag79]** K. Wagner. *On ω-regular sets.* Inf. Control 43 (1979)
  123–177.
