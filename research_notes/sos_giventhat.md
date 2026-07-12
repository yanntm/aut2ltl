# Smaller, Given That: Canonical Property Simplification with Prior Knowledge

**Yann Thierry-Mieg**

With significant inputs from
**Claude (Anthropic)**

*Working draft — 2026-07-12. Restructured around the operation
`𝓘(¬φ) ⊗ 𝓘(K) ↦ 𝓘(B)`; material not serving it is developed less and
parked in Appendix A.*

## Abstract

To verify `S ⊨ φ` when the system is already known to satisfy `K`, the
model checker may replace the negated property by *any* language `B` in
the interval `ℒ(¬φ) ∩ ℒ(K) ⊆ ℒ(B) ⊆ ℒ(¬φ) ∪ ℒ(¬K)` [DPT25]. The
automata-theoretic original navigates that freedom heuristically, on
presentations: per-transition Boolean bands simplified by Minato covers,
stutter closures, existential quantification of propositions. We give
instead a single **operation on canonical objects** — two syntactic
ω-semigroups in, one smaller syntactic ω-semigroup out:

    simplify : 𝓘(¬φ), 𝓘(K)  ↦  𝓘(B),   ℒ(B) ∩ ℒ(K) = ℒ(¬φ) ∩ ℒ(K),
                                        |𝒞(B)| ≤ |𝒞(¬φ)| .

Three things make it possible. (1) *The interval is an exactly
represented finite lattice*: after one alignment it is the powerset of
the conjugacy classes of `ℒ(¬K)` on one table, and its two endpoints are
two scans — symmetric where the automata side must dodge a universality
test. (2) *The objective is well-posed*: on the invariant, "smallest"
means fewest classes after reduction, and the object is canonical per
language — the pleasant inversion of [DPT25]'s own caveat that the
smallest language need not have the smallest automaton. (3) *The search
space is exactly the congruences of the aligned table*: a language `B`
in the interval has `|𝒞(B)|` classes iff `B` is recognized through a
congruence `π` with that many classes, and whether the interval contains
a `π`-recognizable member is decided **exactly, in polynomial time**, by
a *bounded quotient test* — the least `π`-recognizable superset of the
lower endpoint, computed by one cell pass and one saturation, must stay
under the upper endpoint. Admissibility is inherited by refinements, so
the targets are the maximal admissible congruences and greedy coarsening
is the licensed search — the same shape Minato's algorithm has, with an
exact test where they have a heuristic. Deciding the true minimum is in
**NP** (guess the congruence, verify in polynomial time); we conjecture
it NP-complete by the Gold route. The quotient engine is *one machine*:
seeded with `λ(a)² ∼ λ(a)` it is stutter-invariance (whose hull provably
*escapes the table* — a locality theorem we exhibit over two letters);
seeded with `λ(ℓ) ∼ λ(ℓ')` it sheds atomic propositions; unseeded it
minimizes. Constraints compose exactly, by a joint closure fixpoint,
where the automata side chains heuristics and hopes. Finally, a
three-class floor lemma makes optima *certifiable for free*: whenever the
two endpoint checks are inconclusive, no member of the interval has fewer
than three classes. We run the operation on both of [DPT25]'s own worked
figures. It returns a `B` with **3 classes** on each — against inputs of
5 and 4, and against their `min|K` (6 and 4) and `max|K` (4 and 3) — so
by the floor its answer is not merely smaller but **provably minimal over
the whole interval**, on one of which the lattice has 2^25 members. On the
way it drops a recurrence property to a guarantee, and repairs a
stutter-sensitive property into a stutter-invariant one — the two goals
[DPT25] pursue by heuristics that, on those same figures, land on a
strictly larger member or (their Minato pass, on the second) do nothing
at all.

---

## 1. Introduction

**The problem.** LTL model checking decides `S ⊨ φ` — every infinite
execution of a system `S` satisfies a linear-time property `φ` — by an
emptiness check of a product `S ⊗ A_{¬φ}` [Var07]. Its cost is driven by
the property side: the size of `A_{¬φ}`, its acceptance strength (weak
and terminal automata admit cheaper emptiness checks [BRS99, ČP03]), its
stutter sensitivity (stutter-insensitive properties unlock partial-order
reductions worth up to factorial factors [Pel94, Val93]), and the atomic
propositions it observes. **Prior knowledge** is a property `K` the
system is already known to satisfy: `ℒ(S) ⊆ ℒ(K)` — a previously proven
formula, an invariant from a reachability engine, a structural fact.
Duret-Lutz, Poitrenaud and Thierry-Mieg [DPT25] showed that knowledge
buys freedom: `S ⊨ φ` may be decided with any `B` in the interval

    ℒ(¬φ) ∩ ℒ(K)  ⊆  ℒ(B)  ⊆  ℒ(¬φ) ∪ ℒ(¬K),          ([DPT25], Thm. 1)

because words outside `ℒ(K)` cannot occur in `S` and are therefore free
to add or remove. On a benchmark derived from the MCC'22 model-checking
contest, endpoint checks on this interval alone answer half of 97 950
problems without running an LTL model checker at all, and the rest get
measurably simpler automata [DPT25].

**What is missing.** [DPT25] navigates the freedom with three
presentation-level heuristics: `min|K` / `max|K` (the endpoints
themselves), *Bounded-by-Minato* (per-transition Boolean bands, each
label replaced by a simpler one between a lower and an upper bound,
Minato's prime-irredundant-cover algorithm [Min93] doing the choosing),
and `sirelax` / `sirestrict` (add, resp. remove, the partly-covered
stutter classes). Each is sound; none is complete; each answers "here is
*a* member", never "here is *the* member, and nothing smaller exists on
this algebra". The interval itself — with its infinitely many ω-regular
members — has no finite representation on that side, so the natural
questions cannot even be posed: *how much freedom is there? is there a
smaller `B` at all? a safety one? a stutter-insensitive one? and is the
one I found anywhere near the best?*

**This paper: one operation.** We transpose the framework onto the
syntactic ω-semigroup — the canonical finite algebra of an ω-regular
language, now constructible [SωS26] and equipped with an operational
calculus of alignments, pair-set surgeries and normal forms [SωSC26] —
and obtain a single closed operation on canonical objects:

    simplify( 𝓘(¬φ), 𝓘(K) )  =  𝓘(B)

with `ℒ(B) ∩ ℒ(K) = ℒ(¬φ) ∩ ℒ(K)` (so `B` is a legal substitute, by
[DPT25, Thm 1]) and `|𝒞(B)| ≤ |𝒞(¬φ)|` (so it never regresses). Two
`.sos` files in, one smaller `.sos` file out. The contributions are the
four things that make that line true:

1. **The interval is a finite lattice, exactly** (§3). After one
   alignment, the legal `B`s on the table are the saturated pair sets
   between two free surgeries `P_min` and `P_max`, and the lattice is
   isomorphic to the powerset `2^F` of the conjugacy classes of
   `ℒ(¬K)` — the freedom [DPT25] probes, now *measured in bits*. The two
   decisive endpoint checks are two scans, symmetric where the automata
   side must dodge an exponential universality test, and every verdict
   carries the minimal witness lasso.

2. **The objective is well-posed, and its search space is the
   congruences of the aligned table** (§4). "Smallest" = fewest classes
   after `reduce`; because the invariant is canonical per language, this
   is a property of the *language*, not of a presentation. We show
   (Prop 4.1) that minimizing `|𝒞|` over the interval is *exactly*
   minimizing `|T/π|` over the congruences `π` of the aligned table `T`
   that *admit* a member — nothing is lost by searching congruences
   instead of languages.

3. **The bounded quotient test decides admissibility exactly, in
   polynomial time** (Prop 4.2). For any congruence `π`, the least
   `π`-recognizable superset of `P_min` is computed by one cell pass and
   one saturation on the quotient; the interval contains a
   `π`-recognizable member iff that hull stays under `P_max`, and the
   hull *is* then the least such member (its complement-dual, the
   greatest). Admissibility is inherited by refinements (Prop 4.3), so
   the targets are the *maximal admissible congruences* and greedy
   merge-until-stuck is the licensed search. The exact minimum is in
   **NP** (Thm 4.4) and conjectured NP-complete — so a greedy with an
   exact test inside is the honest shape, and it is precisely the shape
   Minato's algorithm has on their side. The difference: their inner
   test is a heuristic cover, ours is a decision procedure.

4. **One machine, several knobs, composing exactly** (§5). A single
   interval-test lemma (any intersection-closed family of languages is
   decided by its closure operator on `P_min`) organizes everything:
   `π`-recognizability is one such family, and so is every rung of the
   safety–progress ladder. Seeding the quotient with `λ(a)² ∼ λ(a)`
   gives **stutter invariance** — where we prove a locality theorem: the
   stutter hull can *escape every table in sight*, so the quotient test
   is sound but incomplete, a phenomenon we exhibit over a two-letter
   alphabet (Thm 5.7). Seeding it with `λ(ℓ) ∼ λ(ℓ')` **sheds atomic
   propositions**. And constraints *compose*: the least `B` that is
   simultaneously (say) stutter-invariant and safety is one joint
   closure fixpoint (Lemma 5.2) — where [DPT25]'s evaluation must chain
   `SIrelax+BM` and take what luck gives.

5. **It works on their own examples, provably** (§6). [DPT25] draw
   exactly two instances as figures; we run the operation on both. A
   three-class floor lemma (Lemma 4.6) says that whenever the endpoint
   checks are inconclusive, *every* member of the interval has at least
   three classes — so a member with three is optimal, certified without
   enumeration. The operation returns exactly that on both figures: 3
   classes against inputs of 5 and 4, beating their `min|K` (6, 4) and
   `max|K` (4, 3), dropping a recurrence to a guarantee on the first, and
   turning a stutter-sensitive property into a stutter-invariant one on
   the second — where their `sirestrict` lands on a strictly larger legal
   member and their Minato pass, by their own admission, changes nothing.
   The paper therefore stands on derivation, not on a campaign.

The system `S` never enters the calculus: only the two spec-sized
objects `𝓘(¬φ)` and `𝓘(K)` pay the entry price. §7 is the evaluation
plan — corroboration, not support — §8 positions the work, §9 concludes.
Appendix A parks the material of earlier drafts that the operation does
not need: decommissioned, not retracted.

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
of all linked pairs of a table. `fold(w)` evaluates a finite word
through `λ, M`; `idem(d)` is the unique idempotent power of `d`. The
**membership oracle** totalizes `P`:
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
[SωS26, Thm 5.1] — **canonicity per language**, the fact everything in
§4 rests on.

**A table, and what it recognizes.** A **table** `T = (𝒞, λ, M)` is an
invariant with the accepting set held apart. `T` is *generated*: every
class is `fold(w)` for some word. A saturated pair set `Q` over `T` (see
below) denotes a language `L(Q)`, and `T` **recognizes** exactly the
languages so denoted. The syntactic invariant of `L(Q)` is obtained by
`reduce(T, Q)`: the re-quotient of `T` by the coarsest congruence under
which `Q` is still well defined [SωSC26, §5]. We write `|𝒞(L)|` for the
class count of the syntactic invariant of `L` — a *language* statistic.

**The calculus** [SωSC26]. Three moves: **align** — the generated
product of two invariants on one table `T` (the only product-priced
move, `≤ n₁·n₂` classes and in practice far fewer, median realized
fraction 0.17), carrying both verdict maps; **operate** — surgery on
pair sets over the fixed table (Boolean algebra pointwise, complement
one flip, decisions as `Val`-scans); **reduce** — re-quotient to the
canonical invariant of any pair set's language. A pair set denotes a
language iff it is **saturated** under conjugacy: for every linked
`(s, e)` and factorization `e = x·y`, the cells `(s, e)` and
`((s·x)·(y·x)^π, (y·x)^π)` carry one verdict [SωSC26, Prop 3.1];
saturation is checkable and enforceable by a polynomial fixpoint
(`sat(·)`, the least saturated superset). Green's preorders: `x ≤_R y`
iff `x ∈ y·M¹`, `x ≤_H y` iff `x ∈ y·M¹ ∩ M¹·y` [PP04]. Conjugacy
preserves the stem's `R`-class [SωSC26, after Prop 6.1] — used
repeatedly.

**Hulls and the ladder** [SωSC26, §6]. `Live` is the set of classes with
nonempty residual (one `O(n²)` scan). The **safety closure** is the
surgery `P̄ := {(s,e) linked : s ∈ Live}` — the least closed (safety)
language above `L(P)`, by a proof that is word-semantic and therefore
valid on any recognizing table (Prop 6.1 there); the **interior** `P̊`
is the dual kernel; `L` is safety iff `P = P̄`, co-safety
(**guarantee**) iff `P = P̊` (Cor 6.2). The **obligation**
(Staiger–Wagner) class: `L` is an obligation iff `Val_P(s, e)` depends
only on the `R`-class of the stem `s` (Thm 6.6 there); within the band,
the Wagner coordinates `(n⁺, n⁻)` are the longest alternating paths in
the `θ`-labeled `R`-class DAG (Prop 6.7). **Recurrence** (`GF` shape,
`Π₂`) and **persistence** (`FG` shape, `Σ₂`) are characterized by the
chain conditions `m⁺ ≤ 0`, `m⁻ ≤ 0` [Lan69, CP97, CP99, SW08]:
concretely, `L` is a recurrence property iff no linked stem `s` carries
loops `f ≤_H e` with `Val(s,e) = 1` and `Val(s,f) = 0`, and persistence
is the mirror. (The transcription is confirmed against the census's
chain coordinates by two distinct decision paths, in agreement on all
6 222 census languages, and decisively refuted under the swapped
orientation — §7.)

**Stutter notions.** `destutter(·)` collapses maximal finite blocks of
equal letters; two ω-words are stutter-equivalent iff they share their
destuttered normal form; `L` is stutter-invariant iff it is a union of
stutter classes. On the syntactic table: `L` is stutter-invariant iff
`λ(a)·λ(a) = λ(a)` for every letter [SωSC26, Prop 5.1] — and the ⇐
direction of that proof is word-semantic, valid on any recognizing
table. The global **stutter closure** `SC(L₀)` — the union of the
stutter classes meeting `L₀` — is the least stutter-invariant superset
of `L₀` among *all* languages, and is ω-regular [HK96, MD15].

**Given-that** [DPT25]. With `ℒ(S) ⊆ ℒ(K)` and `ℒ(S) ≠ ∅`:
`ℒ(S) ∩ ℒ(¬φ) = ∅ ⟺ ℒ(S) ∩ ℒ(B) = ∅` for any `B` in the interval
(Theorem 1 there — the soundness theorem this paper inherits unchanged,
since it is a statement about languages). Their goals for `B`: smaller
or more deterministic, simpler strength class, stutter-insensitive,
fewer atomic propositions. Their tools: the endpoints; Bounded-by-Minato
(`BM`), which replaces each transition label `f` by a simpler `f'` with
`f ∧ T_G(t) ⇒ f' ⇒ f ∨ ¬S_G(q)`, choosing `f'` with Minato's
prime-irredundant-cover algorithm [Min93]; and `sirelax` / `sirestrict`.
Their own caveat, which §4.1 inverts: *the smallest language need not
have the smallest automaton*.

## 3. The interval is a finite lattice

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
counterpart. `|F| = 0` means the interval is a point. On census pairs
`|F|` has median 20 and p95 124 (§7): the lattice is astronomically
large, and *enumeration is never the algorithm* — §4 is.

**The two decisive checks are one scan each.**

- `L(P_min) = ∅ ⟺ ℒ(K) ⊆ ℒ(φ) ⟺ K ⊨ φ`: the property holds on any
  system satisfying `K` — no model checker runs. On failure, the first
  accepting cell yields the *minimal* lasso in `ℒ(¬φ) ∩ ℒ(K)`: "`K` does
  not settle `φ`, and here is the shortest behavior it leaves open."
- `L(P_max) = Σ^ω ⟺ P_max = linked ⟺ ℒ(K) ⊆ ℒ(¬φ) ⟺ K ⊨ ¬φ`: every run
  of the nonempty `S` is a counterexample. On the automata side this is
  a universality test, exponential on TGBA, which [DPT25] must dodge by
  re-translating a formula for `φ`; here it is emptiness of `P_max^c` —
  one flip away, exactly symmetric with the first check. On failure, the
  minimal lasso in `ℒ(φ) ∩ ℒ(K)`.

These are the operation's first two lines (§4.6): when either fires, the
model-checking problem is *answered*, and no `B` need be emitted at all.
On the MCC'22 benchmark the two endpoint strategies of [DPT25] solve
≈52% of problems outright, with a reported asymmetry ("empty seems
easier than universal") that their syntactic universality check
explains; on the invariant the two checks are the same scan on
complementary pair sets, and the asymmetry should vanish.

**Certificate discipline.** Every test in this paper factors through the
membership oracle, so [SωSC26, Prop 3.2] applies: every verdict is
accompanied by the globally minimal witness lasso — counterexamples a
user can replay, ordered smallest-first.

## 4. The objective, and the search space that realizes it

This section is the paper. §3 gave the freedom a representation; here we
*spend* it, on the objective the model checker actually feels.

### 4.1 Smallest, and why the question is well-posed here

[DPT25] wants `B` "smaller". On automata that goal is slippery, and they
say so: the smallest *language* in the interval need not have the
smallest *automaton*, so the objective is a property of a presentation,
one heuristic rewrite is as defensible as another, and "is there
anything smaller?" has no answer. On the invariant the situation
inverts. The syntactic ω-semigroup is **canonical per language** [SωS26,
Thm 5.1]: two languages are equal iff their reduced invariants are
byte-equal. So

    |𝒞(B)| := the number of classes of reduce(B)

is a function of the *language* `B`, and

    minimize |𝒞(B)|  subject to  P_min ⊆ B ⊆ P_max

is a well-posed optimization problem over a finite lattice. That is the
objective of this paper.

It is also the right one. `|𝒞|` bounds the exit acceptor handed to the
model checker (the invariant of `B` is turned into an automaton by a
polynomial construction [SωSC26, §7], whose size is driven by `|𝒞|` and
the linked-pair count); it bounds the size of an extracted LTL formula
when one is wanted; and it is monotone in every other structural
statistic we care about. We note the corollary and do not pursue it
here: when `φ` and `K` are LTL, the aligned table is aperiodic, hence so
is every quotient of it, so **every `B` this operation emits is
LTL-definable** [SωSX26, Prop 5.11] — a smaller algebra yields a smaller
formula through `sos2ltl` with no extra work, so "LTL in, simpler LTL
out" follows from the operation rather than motivating a separate
construction (Appendix A.4).

Two reference points bound any honest claim of "smaller", and both are
free:

- `|𝒞(¬φ)|` — **the input**. `P_{¬φ}` is itself in the interval, so the
  identity is always a legal answer and the operation must never
  regress.
- `|𝒞(L(P_min))|` and `|𝒞(L(P_max))|` — **[DPT25]'s `min|K` / `max|K`**.
  These are legal members too, and, as [DPT25] observes, they are
  usually *larger* than the input: taking the conjunction with `K` asks
  the model checker to prove `K` as well.

The operation's contract is therefore `|𝒞(B)| ≤ min` of the three, and
its claim is that the inequality is usually strict.

And there is a floor, which costs nothing and certifies optima for free:

**Lemma 4.6 (the three-class floor).** If neither endpoint check fires —
`K ⊭ φ` and `K ⊭ ¬φ` — then **every** `B` in the interval satisfies
`|𝒞(B)| ≥ 3`. Consequently any member attaining 3 classes is a
*minimum*, certified without enumerating anything.

*Proof.* A table has at least two classes (`[ε]` is adjoined fresh, so
no letter maps to it). Suppose `𝓘(L)` has exactly two, `[ε]` and `C`;
every nonempty word folds to `C`, so `C·C = C` and the only linked pair
is `(C, C)` (`[ε]·C = C ≠ [ε]`). Its accepting set is `∅` or `{(C,C)}`,
i.e. `L ∈ {∅, Σ^ω}`. Now `K ⊭ φ` means `L(P_min) ≠ ∅` and `K ⊭ ¬φ` means
`L(P_max) ≠ Σ^ω`; every member `B` has `L(P_min) ⊆ L(B) ⊆ L(P_max)`, so
`B ∉ {∅, Σ^ω}` and `|𝒞(B)| ≥ 3`. ∎

The two examples of §6 both hit the floor: the operation returns a
3-class `B` on each, so on [DPT25]'s own figures its answer is not merely
smaller — it is **optimal, and provably so**. The floor also explains why
the endpoint checks come first: they are exactly the case distinction
that makes the objective non-degenerate.

### 4.2 The search space is the congruences of the aligned table

A language in the interval is a saturated pair set on `T`; there are
`2^{|F|}` of them, and `|F|` has median 20. We do not search them. We
search *congruences* instead, and lose nothing.

Fix the aligned table `T`. A **congruence** `π` on `T` is an equivalence
on `𝒞` compatible with `M` on both sides, keeping `[ε]` a singleton (it
is automatically one: `[ε]` is adjoined, so no product of non-identity
classes returns to it). The quotient table `T/π = (𝒞/π, π∘λ, M/π)` is
again a generated table. Say a saturated pair set `B` on `T` is
**`π`-recognizable** iff

    B = π⁻¹(P') := { (s,e) ∈ linked(T) : Val_{P'}(π(s), π(e)) = 1 }

for some saturated `P'` on `T/π`. Two facts make this the right notion.
First, `π(idem_T(d)) = idem_{T/π}(π(d))` (the image of an idempotent
power of `d` is an idempotent power of `π(d)`, and that idempotent is
unique), whence

    Val_{π⁻¹(P')}(c, d) = Val_{P'}(π(c), π(d))   for every cell (c,d),

so `π⁻¹(P')` denotes exactly the language `P'` denotes through the
morphism `π ∘ fold`: **`B` is `π`-recognizable iff `T/π` recognizes
`L(B)`**. Second, `π⁻¹` commutes with the Boolean operations, so the
`π`-recognizable sets form a *Boolean subalgebra* of the saturated pair
sets — closed under intersection, union and complement.

**Proposition 4.1 (the search space is exactly right).** For every
saturated `B` on `T`, let `π_B` be the syntactic congruence of `L(B)` —
the coarsest congruence of `T` under which `B` is well defined, i.e. the
one `reduce(T, B)` computes. Then `B` is `π_B`-recognizable and
`|T/π_B| = |𝒞(B)|`. Consequently, calling `π` **admissible** when the
interval contains a `π`-recognizable member,

    min { |𝒞(B)| : P_min ⊆ B ⊆ P_max }  =  min { |T/π| : π admissible } .

*Proof.* `T` is generated and recognizes `L(B)`, so its quotient by the
syntactic congruence of `L(B)` *is* the syntactic ω-semigroup of `L(B)`
[SωSC26, §5], giving both claims of the first sentence. (`≥`) Take a `B`
attaining the left minimum; `π_B` is admissible (`B` witnesses it) and
`|T/π_B| = |𝒞(B)|`. (`≤`) Take an admissible `π` attaining the right
minimum, with member `B`; then `T/π` recognizes `L(B)`, so the syntactic
invariant of `L(B)` is a quotient of `T/π` and `|𝒞(B)| ≤ |T/π|`. ∎

The optimization has moved from `2^{|F|}` languages to the congruence
lattice of `T`, with no loss. What remains is to decide admissibility.

### 4.3 The bounded quotient test

This is the engine. Fix a congruence `π` and a saturated `Q` on `T`.
Write `e_q := idem_{T/π}(π(d))` and define, by one pass over the cells of
`T` and one saturation on the quotient,

    forced_π(Q) := { ( M/π( π(c), e_q ), e_q )  :  cell (c,d) of T
                                                   with Val_Q(c, d) = 1 }
    hull_π(Q)   := π⁻¹( sat_{T/π}( forced_π(Q) ) ) .

**Proposition 4.2 (the bounded quotient test).** `hull_π(Q)` is the
**least `π`-recognizable superset of `Q`**. Consequently

    the interval contains a π-recognizable member
        ⟺   hull_π(P_min) ⊆ P_max ,

and in that case the `π`-recognizable members of the interval form the
sub-interval

    [ hull_π(P_min) ,  ( hull_π(P_max^c) )^c ]

— least and greatest member, both computable by the same pass.

*Proof.* (Extensive.) Let `(s,e) ∈ Q`. It is linked, so `idem(e) = e`
and `M(s,e) = s`, whence `Val_Q(s,e) = 1`: the cell `(s,e)` contributes
to `forced_π(Q)` exactly the quotient pair that `Val` reads at
`(π(s), π(e))`, so `(s,e) ∈ π⁻¹(forced_π(Q)) ⊆ hull_π(Q)`.
(`π`-recognizable.) By definition, `hull_π(Q)` is the pullback of a
saturated set.
(Least.) Let `B = π⁻¹(P')` be `π`-recognizable with `Q ⊆ B`. For any
cell `(c,d)` with `Val_Q(c,d) = 1` we get `Val_B(c,d) = 1` (the oracle
reads a pair of `Q ⊆ B`), i.e. `Val_{P'}(π(c), π(d)) = 1`, which says
precisely that the quotient pair contributed by `(c,d)` lies in `P'`.
Hence `forced_π(Q) ⊆ P'`; `P'` is saturated, so
`sat(forced_π(Q)) ⊆ P'`; and `π⁻¹` is monotone, so
`hull_π(Q) ⊆ B`.
The interval statement is Lemma 5.1 applied to the Moore family of
`π`-recognizable sets (intersection-closed, contains `linked`), whose
closure operator is `hull_π` by what precedes; the greatest member
follows because the family is closed under complement, so the largest
`π`-recognizable subset of `P_max` is the complement of the least
`π`-recognizable superset of `P_max^c`. ∎

The cost is one `O(n²)` cell pass plus one saturation on a *smaller*
table — polynomial, and cheaper than the alignment that produced `T`.
Note the two traps the proof pins down: the saturation happens **on the
quotient, before the pullback** (saturating the pulled-back set on `T`
gives a different, wrong answer), and the forced pair is the one the
*oracle reads*, i.e. renormalized through the idempotent — inserting the
raw image pair is unsound.

**Remark (this generalizes §5's `sc`).** With the stutter seeds
`λ(a)² ∼ λ(a)`, `hull_π` is exactly the stutter hull `sc` of Prop 5.6,
and Prop 4.2 specializes to its correctness. The proof above never uses
*which* congruence `π` is — which is why the stutter machinery
generalizes into an optimizer.

### 4.4 Refinement monotonicity: greedy is the licensed search

Call `π'` **coarser** than `π` when every `π`-class is contained in a
`π'`-class (so `T/π'` is a quotient of `T/π`).

**Proposition 4.3 (monotonicity).** If `π'` is coarser than `π`, then
`hull_π(Q) ⊆ hull_{π'}(Q)` for every `Q`. Hence **admissibility is
inherited by refinements**: if `π'` is admissible, so is every `π`
refining it.

*Proof.* `hull_{π'}(Q)` is `π'`-recognizable, hence `π`-recognizable
(factor the pullback through the intermediate morphism `T/π → T/π'`),
and it contains `Q`; since `hull_π(Q)` is the *least* `π`-recognizable
superset of `Q`, it is below it. If `hull_{π'}(P_min) ⊆ P_max` then
`hull_π(P_min) ⊆ hull_{π'}(P_min) ⊆ P_max`. ∎

So coarsening can only *lose* admissibility, never gain it: the
admissible congruences form a downward-closed set in the coarsening
order, and the interesting ones are the **maximal admissible
congruences**, an antichain. By Prop 4.1 the optimum is attained at one
of them. This licenses exactly one search shape — *merge classes while
you still can* — and it is worth naming the parallel: on the automata
side, Minato's algorithm computes a **prime irredundant cover**, i.e. it
greedily grows implicants until they are maximal and drops the redundant
ones. We greedily coarsen a congruence until it is maximal. Same shape;
the difference is what happens inside the loop. Their inner step picks a
label from a Boolean band by a heuristic; ours *decides*, exactly, by
Prop 4.2, whether the merge keeps a legal member alive.

### 4.5 How hard is the true minimum?

**Theorem 4.4 (membership in NP).** The decision problem — given
`𝓘(¬φ)`, `𝓘(K)` and `k`, is there a `B` in the interval with
`|𝒞(B)| ≤ k`? — is in **NP**.

*Proof.* Align and materialize (polynomial). Guess a partition `π` of
the classes of `T` with at most `k` blocks. Verify in polynomial time
that `π` is a congruence (`O(n²|Σ|)`), that `[ε]` is a singleton block,
and that `hull_π(P_min) ⊆ P_max` (Prop 4.2 — one cell pass and one
saturation). By Prop 4.1 such a `π` exists iff such a `B` does. ∎

**Conjecture 4.5.** The problem is NP-complete. The reduction route is
Gold's [Gol78]: the interval constrains lasso verdicts exactly as a
labeled sample constrains a DFA — the `P_min` pairs are the positive
examples, the pairs outside `P_max` the negative ones, and the freedom
`F` is precisely a set of *don't-cares*. Minimal consistent DFA
identification from a sample with don't-cares is NP-hard; transporting
it to linked pairs on an ω-semigroup is the work.

We therefore do **not** promise the minimum. We ship a polynomial greedy
whose every inner decision is exact, we report what it achieves against
the three reference points of §4.1, and — on instances small enough to
enumerate `2^F` — we report the gap to the true optimum as a measured
quality of the heuristic, never as evidence about Conjecture 4.5.

### 4.6 The operation

    simplify( 𝓘(¬φ), 𝓘(K) ) :

    1.  T, P_{¬φ}, P_K  ←  materialize( align( 𝓘(¬φ), 𝓘(K) ) )
        P_min ← P_{¬φ} ∩ P_K ;  P_max ← P_{¬φ} ∪ P_K^c        (§3)

    2.  if L(P_min) = ∅ :  return SETTLED  (K ⊨ φ)              — one scan
        if L(P_max^c) = ∅ : return REFUTED (K ⊨ ¬φ)             — one scan
        (both with the minimal witness lasso on the negative side)

    3.  for each seed congruence π₀ ∈ { π_{¬φ}, id, (stutter seeds) } :
            π ← π₀                                  -- admissible: see below
            repeat
                among all merges of two distinct non-identity blocks of π,
                keep those whose congruence closure π' is admissible
                    (Prop 4.2:  hull_{π'}(P_min) ⊆ P_max)
                if none: break
                π ← the admissible π' with fewest blocks   (ties: key order)
            record  hull_π(P_min)  and  ( hull_π(P_max^c) )^c

    4.  B ← the recorded member — over all seeds, both polarities, and the
            three reference members P_{¬φ}, P_min, P_max — with the fewest
            classes after reduce.

    5.  assert  B ∩ P_K = P_min          (legality: [DPT25] Thm 1)
        return  reduce(T, B)

**The seeds matter, and one of them makes the contract free.** `π_{¬φ}`
— the syntactic congruence of `¬φ` itself, which `reduce(T, P_{¬φ})`
already computes — is *always admissible*: `P_{¬φ}` is `π_{¬φ}`-
recognizable and lies in the interval, so `hull_{π_{¬φ}}(P_min) ⊆
P_{¬φ} ⊆ P_max`. Seeding there starts the greedy on a table of exactly
`|𝒞(¬φ)|` classes and only coarsens further, which is why step 4 can
guarantee

    |𝒞(B)| ≤ min( |𝒞(¬φ)|, |𝒞(L(P_min))|, |𝒞(L(P_max))| )     — never a regression,

with strictness the empirical claim (§7). The identity seed explores a
region `π_{¬φ}` may not dominate (maximal admissible congruences form an
antichain, and greedy from different seeds lands on different ones); the
stutter seed, when admissible, buys stutter-insensitivity on top
(§5.3) — and when it is not admissible, the operation says so and falls
back, rather than pretending.

**Step 5 is the whole soundness argument.** On the table, [DPT25]'s
Theorem 1 is a *set identity*: `B ∩ P_K = P_min` — equivalent, by
Prop 3.1, to `P_min ⊆ B ⊆ P_max`. It is asserted on every emission.

## 5. One lemma, a catalogue of constraints

Everything the operation can be *asked for* — beyond smallness — is a
family of languages, and one lemma decides them all.

**Lemma 5.1 (interval test).** Let `𝒦` be a family of saturated pair
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

**Lemma 5.2 (constraints compose, exactly).** If `𝒦₁, …, 𝒦ₘ` are Moore
families with closures `ρ₁, …, ρₘ`, then `⋂ᵢ 𝒦ᵢ` is a Moore family whose
closure is the least fixpoint of the alternation
`Q ↦ ρₘ(⋯ρ₁(Q)⋯)` above `Q`, reached in at most `|linked|` rounds.
Hence *the least `B` satisfying all the constraints simultaneously* is
computed by one joint fixpoint, and it lies in the interval iff that
fixpoint stays under `P_max`.

*Proof.* An intersection of Moore families is a Moore family. The
alternation is monotone, extensive and bounded by the finite lattice, so
it converges; its limit lies in every `𝒦ᵢ` (each `ρᵢ` is idempotent at
the limit) and is below any common member above `Q` (induction on the
rounds, using monotonicity of each `ρᵢ`). Apply Lemma 5.1. ∎

This is where the algebraic account pulls decisively ahead. [DPT25]'s
evaluation chains strategies — its table literally reports
"`SIrelax+BM`", one heuristic run after another, with no claim about the
result. Here, *"the smallest `B` that is also stutter-invariant and also
a safety property"* is a single closure fixpoint, and it is the least
such `B` — or a certificate that none exists. The catalogue of `ρ`s
follows; each is one entry in the composition.

### 5.1 The quotient family (the optimizer, §4)

For a fixed `π`, the `π`-recognizable sets are a Moore family (indeed a
Boolean subalgebra) with closure `hull_π` (Prop 4.2). This is the entry
the operation *searches over*; the entries below are the ones a user
*imposes*.

### 5.2 The safety–progress ladder: constraints, and metrics on the output

Each rung of the Manna–Pnueli ladder [MP92, ČP03] is a Moore (or kernel)
family with a cheap closure. They serve the operation twice: as
constraints ("give me the smallest *safety* `B`"), and as **metrics on
the emitted `B`** — the strength class is what the emptiness check
actually feels, so the operation reports the rung of `¬φ` and the rung
of `B`, and a strict drop is a headline of §7.

**Proposition 5.3 (safety / co-safety).** A safety `B` exists in the
interval iff `P̄_min ⊆ P_max`, and then `P̄_min` is the least one *among
all ω-regular languages, not merely on-table ones*. Dually a co-safety
`B` exists iff `P_min ⊆ P̊_max`, with greatest witness `P̊_max`. Both
tests are one `O(n²)` stem-liveness scan.

*Proof.* Lemma 5.1 with `𝒦` = closed pair sets — a Moore family: an
intersection of closed pair sets recognizes the intersection of their
languages, closed again, and `linked` recognizes `Σ^ω`; `ρ` is the hull
`P̄` of [SωSC26, Prop 6.1]. *Locality* — the reason "among all ω-regular
languages" is warranted — is Prop 6.1 itself: its proof identifies
`L(P̄)` with the *topological* closure `cl(L(P_min))`, a
presentation-independent object, and any safety `B ⊇ L(P_min)` in the
semantic interval satisfies `cl(L(P_min)) ⊆ B` by minimality. ∎

Both families are also union-closed, so Lemma 5.1's sub-interval clause
hands each test its other endpoint; on a co-safety "yes" the least
member is the open hull — the set of linked pairs whose stem is a right
multiple of a stem of `P_min` (conjugacy already saturates it, since it
preserves the stem's `R`-class).

**Proposition 5.4 (obligation).** An on-table obligation is an
`R`-class-constant verdict `B_θ` [SωSC26, Thm 6.6(3)], automatically
saturated. Call an `R`-class *forced to 1* if some pair of `P_min` has
its stem in it, *forced to 0* if some linked pair outside `P_max` does.
An obligation `B` exists iff no `R`-class is forced both ways —
`O(|linked|)` after one SCC pass of the right-Cayley graph — and the
obligation members then form the sub-lattice
`{θ : forced₁ ≤ θ ≤ ¬forced₀} ≅ 2^{unforced}`, least member `θ = forced₁`,
greatest `θ = ¬forced₀`.

*Proof.* Lemma 5.1 with `𝒦 = {B_θ}`, closed under union and intersection
pointwise on `θ`; `ρ_obl(Q) = B_θ` with `θ(r) = 1` iff `r` contains a
stem of `Q`. `ρ_obl(P_min) ⊆ P_max` unfolds to "no class forced both
ways". Membership in the obligation *class* (not merely the formal
family) transfers to the unreduced table both ways: (⇐) an
`R`-class-constant `B_θ` is a Boolean combination of closed pair sets of
`T`, each a safety language on any recognizing table (Prop 6.1), hence
an obligation; (⇒) an obligation `B` has `R`-class-constant verdict on
its own syntactic table (Thm 6.6), and the reduce morphism `h : T →
𝓘(B)` preserves `R`, so `Val_B` is `R`-class-constant on `T`. ∎

**Proposition 5.5 (recurrence / persistence, sketch).** The chain
conditions of §2 are **Horn conditions** on `P`: recurrence is closure
under `(s,e) ∈ P, f ≤_H e, f a loop of s ⟹ (s,f) ∈ P`, persistence the
mirror. The least superset of `Q` closed under the Horn rule *and*
conjugacy saturation is a monotone fixpoint (alternate the rule with
`sat(·)`, at most `|linked|` rounds — an instance of Lemma 5.2). Then
`∃` recurrence `B` iff `rec-hull(P_min) ⊆ P_max`; `∃` persistence `B`
iff `rec-hull(P_max^c) ⊆ P_min^c` — the dual costs *one complement
flip*, where the automata side would pay a complementation before even
posing the question.

*To nail down in the full proof.* (i) The chain characterization is
stated on the syntactic algebra [CP99]; on the unreduced `T` the (⇒)
direction needs a violation in `𝓘(B)` to lift to `T`, which follows from
the standard finite-semigroup lemma that `≤_H`-related idempotents lift
along surjective morphisms; (⇐) is easy (`h` preserves `≤_H` and
verdicts). (ii) Locality: the test decides existence of an *on-table*
recurrence `B`; whether the semantic least recurrence superset can
escape the table (as the stutter hull does, §5.3) is **open**.

*Free corollary — separator synthesis.* For disjoint `L₁, L₂`, the
interval `[P_{L₁}, P_{L₂}^c]` on their aligned table turns every test
above into "is there a safety (obligation, recurrence, …) property
*separating* `L₁` from `L₂`". Given-that is the case
`L₁ = ℒ(¬φ) ∩ ℒ(K)`, `L₂ = ℒ(φ) ∩ ℒ(K)`. [DPT25, §9] noted the
connection to separation [PZ16]; here it is an algorithm. We do not
pursue it.

### 5.3 Stutter invariance: the seeded quotient, and a locality theorem

[DPT25, §6] spends interval freedom to make `B` stutter-insensitive:
compute `si(A)` (adds all partly-covered stutter classes), adopt it if
the added words avoid `K` (`sirelax`); dually `sirestrict`, which is the
only strategy in their benchmark that times out — it needs a
complement. On the algebra, stutter invariance is *the quotient engine
of §4 under one seed set*, and the story has a twist worth the section.

**Proposition 5.6 (recognition through the stutter quotient).** Let
`π_st` be the smallest congruence with `λ(a)·λ(a) ∼ λ(a)` for every
letter (union-find, closed under left/right letter multiplication;
polynomial). The stutter-invariant languages recognized by `T` are
exactly the `π_st`-recognizable pair sets, and the least
stutter-invariant on-table superset of `L(Q)` is `hull_{π_st}(Q)` —
written `sc(Q)`.

*Proof.* (⊇) `T/π_st` has idempotent letter images by construction, and
the ⇐ direction of [SωSC26, Prop 5.1] is valid on any recognizing table
(§2): every `T/π_st`-recognized language is stutter-invariant. (⊆) Let
`L'` be stutter-invariant and `T`-recognized. Its syntactic morphism
factors as `η = h ∘ fold` for a morphism `h : T → 𝓘(L')`; by [SωSC26,
Prop 5.1] (⇒), `η(a)² = η(a)`, so `h(λ(a)²) = h(λ(a))`: the kernel of
`h` is a congruence containing the generating pairs of `π_st`, hence `h`
factors through `π_st`, and `L'` is `π_st`-recognizable. The hull
statement is Prop 4.2 at `π = π_st`. ∎

So `sc(P_min) ⊆ P_max` is a *sufficient* test for a stutter-invariant
member, with an on-table canonical witness. The natural conjecture is
that it is also necessary. **It is not.**

**Theorem 5.7 (the stutter hull escapes the table).** There are `¬φ`,
`K` such that a stutter-invariant ω-regular `B` exists in the interval
while `sc(P_min) ⊄ P_max`: the quotient test is sound but *incomplete*,
because the global stutter closure `SC(L(P_min))` need not be recognized
by any table aligned from `𝓘(¬φ)` and `𝓘(K)`.

*Proof (the two-letter counterexample).* Take `ℒ(¬φ) = {(ab)^ω}` and
`ℒ(K) = {(ab)^ω, (ba)^ω}` — "the system alternates, in one of the two
phases". The interval is `[{(ab)^ω}, Σ^ω \ {(ba)^ω}]`, and
`B = SC({(ab)^ω})` — the words destuttering to `(ab)^ω` — is a
stutter-invariant ω-regular member (it avoids `(ba)^ω`, whose normal
form differs): the semantic answer is **yes**. Now the table:
`synt({(ab)^ω})` has six classes — `[ε]`, the four classes `A_{xy}` of
alternating words by first letter `x` and last letter `y`, and the junk
class `Z` (any word with a repeated adjacent letter; all such words are
interchangeable in every context of the single word `(ab)^ω`) — and on
the aligned `T` the two components merge in lockstep (a word repeats an
adjacent letter for one language iff for the other). Forcing
`λ(a)² ∼ λ(a)` merges `A_{aa} ∼ Z` (since `λ(a) = A_{aa}` and
`λ(a)² = Z`), then `A_{bb} ∼ Z`, then `A_{ab} = A_{aa}·A_{bb} ∼ Z` and
`A_{ba} ∼ Z`: `T/π_st` collapses to `{[ε], Z}`, every lasso lands on the
single pair `(Z, Z)`, and `sc(P_min) = Σ^ω ⊄ Σ^ω \ {(ba)^ω}`. The
quotient test says **no**. The obstruction is not an artifact of a poor
alignment: both *syntactic* tables merge `aa` and `bb` — each is junk in
every context of either language — so every table the calculus derives
from its canonical inputs inherits the merge, while `SC({(ab)^ω})`
separates `aa(ab)^ω` (in) from `bb(ab)^ω` (out). No derived table
recognizes `SC`. ∎

Two honest remarks. First, this is a **locality** failure, not
unsoundness: when the test passes, `sc(P_min)` is a valid, canonical,
on-table witness, and the operation emits it. Second, on this very
instance [DPT25]'s `sirelax` *succeeds* — the presentation-side closure
reaches an off-table witness the algebra cannot express. The two
approaches are genuinely complementary here, and we say so.

The consequence for the operation is a three-valued answer, not a
two-valued one: with the stutter seed, `simplify` returns **YES** with a
witness, or **UNKNOWN** — never "no". (An exact test *does* exist — a
polynomial self-alignment of the table through the stutter relation —
but it decides existence without constructing a witness the calculus can
use, so it is a diagnostic rather than a simplification. It is stated,
with its construction, in Appendix A.1.)

### 5.4 Shedding atomic propositions: another seed

[DPT25] drops `K`-only atomic propositions by existential
quantification, over-approximated per Boolean subformula (`QE(P,K)`). On
the invariant this is the same engine again: let `π_p` be the smallest
congruence merging `λ(ℓ) ∼ λ(ℓ')` for all valuations `ℓ, ℓ'` differing
only on the shed propositions `p`, and take `hull_{π_p}(P_K)` — the
least `p`-blind on-table superset of `ℒ(K)`, re-lettered over the
smaller alphabet by inverse substitution [SωSC26, §4]. **Stutterization,
AP-shedding and minimization are one move** — pull through a congruence
and back; only the generating relations differ (`λ(a)² ∼ λ(a)`,
`λ(ℓ) ∼ λ(ℓ')`, none). The locality caveat returns with a twist: the
semantic least `p`-blind superset *is* the exact projection `∃p.K`
re-expanded over `Σ` — exponential — so the on-table hull is the honest
cheap tier. Whether it beats `QE(P,K)` is open (they lose different
things; conjecture: incomparable).

### 5.5 The catalogue

| family `𝒦` | closure `ρ_𝒦` | cost | local? |
|---|---|---|---|
| `π`-recognizable (fixed `π`) | `hull_π` (Prop 4.2) | cell pass + quotient saturation | by construction (on-table is the point) |
| safety / co-safety | `P̄` / `P̊` | `O(n²)` liveness scan | **yes** (topological, Prop 5.3) |
| obligation | `R`-class forcing | `O(n·\|Σ\|)` SCC pass | open |
| recurrence / persistence | Horn hull + `sat` | polynomial fixpoint | open |
| stutter-invariant | `sc = hull_{π_st}` (Prop 5.6) | as `hull_π` | **no** (Thm 5.7) |
| `p`-blind | `hull_{π_p}` | as `hull_π` | no (exact projection is exponential) |

Any intersection of these is decided by one joint fixpoint (Lemma 5.2).

## 6. The operation on [DPT25]'s own examples

[DPT25] draws exactly two instances as figures. We run the operation on
both. In each case it returns a `B` that is **strictly smaller than the
input**, and — by the three-class floor (Lemma 4.6) — **provably minimal
over the whole interval**. No experiment is involved: the numbers below
are the algebra, and each is reproducible in one command
(`sosl/tests/giventhat/dpt_examples.py`).

| | `\|𝒞(¬φ)\|` | `\|𝒞(K)\|` | `\|𝒞(T)\|` | `\|F\|` | `min\|K` | `max\|K` | **`\|𝒞(B)\|`** | rung `¬φ → B` | stutter `¬φ → B` |
|---|---|---|---|---|---|---|---|---|---|
| Figs. 2–3 | 5 | 4 | 10 | 25 | 6 | 4 | **3** | recurrence → **guarantee** | inv → inv |
| Fig. 4 | 4 | 3 | 5 | 3 | 4 | 3 | **3** | guarantee → guarantee | **sensitive → invariant** |

The two are complementary. On Figs. 2–3 the optimum lies *strictly
inside* the lattice — below the input *and* below both of [DPT25]'s
endpoint strategies — and `2^F` has 33 554 432 members, so only the hulls
can reach it. On Fig. 4 the lattice has eight members and we enumerate it
by hand: the minimum is unique.

### 6.1 Figs. 2–3: the running example

The running example of [DPT25, Figs. 2–3]:
`¬φ = F(a∧c) ∨ (GFb ∧ GF¬b)` given `K = FGb ∧ Gc`, over `Σ = 2^{a,b,c}`
(a letter is written as the set of propositions it makes true: `{abc}`,
`{bc}`, …). There, transition-wise Boolean bands simplified by Minato's
algorithm turn `A_{¬φ}` into an automaton for `Fa`, observed to be "now
terminal". Here is the same instance as one operation.

**The tables.** A finite word carries three monotone bits `(σ, p, q)` —
*contains an `a∧c` letter* / *a `b` letter* / *a `¬b` letter* —
multiplying by bitwise OR, with
`Val_{¬φ}((σ_s,·,·),(σ_e,p_e,q_e)) = σ_s ∨ σ_e ∨ (p_e ∧ q_e)`. The bit
table recognizes `¬φ` but is not syntactic: `σ` is absorbing and `Val`
reads nothing else once it is set, so the three `σ = 1` triples are one
class. **`𝓘(¬φ)` has 5 classes** — `[ε]`, `(0,0,1)`, `(0,1,0)`,
`(0,1,1)`, and the accepting sink `⊤` — with 9 linked pairs. `𝓘(K)` has
**4**: `[ε]`, `BC` (all letters `b∧c`), `C` (all `c`, some `¬b`), and
the absorbing dirty class `D` (some `¬c`). The generated product `T` has
**10 classes**, and both verdicts ride along. Every letter class is
idempotent (both formulas are `X`-free), so `T = T/π_st`: the stutter
seed is free here, and the phenomenon of Thm 5.7 needs a
stutter-sensitive pair.

**Step 2 — the endpoints.** `P_min = {stems (⊤ | BC/C), loops with
k = BC}` — the language `F(a∧c) ∧ FGb ∧ Gc`. Both decisive checks fail,
each with a one-letter-loop minimal witness: `K` does not settle `φ`
(`({abc})^ω` is the shortest behavior left open), and `K` does not
refute it (`({bc})^ω` is the shortest `K`-behavior satisfying `φ`). The
freedom is `|F| = 25` bits — `2^25` legal members, so enumeration is
already out of reach on a toy.

**Step 3–4 — the search.** The three reference points: the input
`|𝒞(¬φ)| = 5`; [DPT25]'s `min|K` = `ℒ(¬φ) ∩ ℒ(K)`, which has **6**
classes — *larger than the input*, exactly as [DPT25] predict ("using
these automata is similar to asking the model checker to prove `K` in
addition to `¬φ`"); and their `max|K` = `ℒ(¬φ) ∪ ℒ(¬K)`, which has **4**.
So knowledge already buys one class through their own relaxation. The
operation buys two, and proves nothing more is available.

**What the constraints say about the answer** (each decided, none
guessed):

- **No safety `B`** (Prop 5.3). The dead classes are exactly those with
  `k = D`, so `P̄_min` is the language `Gc`, and the cell of `({bc})^ω`
  lies in `P̄_min \ P_max`: refused, with that minimal lasso. Any safety
  property containing the mandatory behaviors must accept `({bc})^ω` —
  every prefix of it extends into `ℒ(¬φ) ∩ ℒ(K)` — yet `K` allows it and
  `φ` holds on it. Impossibility, certified: a verdict no
  presentation-side rewrite can emit.
- **A co-safety `B` exists, and the interval brackets Minato's answer.**
  `σ` is absorbing, so `P̊_max` is the language `F(a∧c) ∨ F¬c =
  F(a ∨ ¬c)`; every `P_min` stem has `σ = 1`, so `P_min ⊆ P̊_max`:
  **yes**. By Lemma 5.1's sub-interval clause the on-table guarantee
  members form exactly the bracket

      [ F(a∧c) ,  F(a ∨ ¬c) ]

  and [DPT25]'s `Fa` sits strictly inside it — `F(a∧c) ⊆ Fa ⊆
  F(a∨¬c)` — and is itself **off-table**: no class of `T` tracks `a`
  without `c`. The heuristic landed a perfectly legal member; the
  calculus names the canonical endpoints it landed between, and
  *certifies that the class is guarantee* — which is exactly the "now
  terminal" observation of their Figure 3, decided rather than noticed.
- **The rung drop, read off.** On its own table `Val_{¬φ}` is monotone
  under adding loop bits, and `H`-descent in an OR-monoid *is* adding
  bits, so `¬φ` is a **recurrence** property. It is nothing lower: the
  stem `(0,1,1)` carries loops `(0,1,1) <_H (0,1,0)` with verdicts
  `1 > 0` — loop-sensitive, so not an obligation, and accepting below
  while rejecting above, so not a persistence. Knowledge therefore buys
  a drop from **recurrence to guarantee** — from a full Büchi emptiness
  check to reachability.

**The answer, and its optimality.** Both ends of the guarantee bracket
have **3 classes** (`F(a∧c)`: `[ε]`, "not yet", the accepting sink;
`F(a∨¬c)` likewise), so the operation returns a 3-class guarantee `B` —
against `|𝒞(¬φ)| = 5`, `min|K` = 6, `max|K` = 4. And by Lemma 4.6 no
member of the interval can have fewer than 3, since neither endpoint
check fired. **The answer is minimal over all 2^25 members of the
lattice, certified without enumerating one of them.**

Read the whole instance in one line: *given `K`, the recurrence property
`¬φ` may be replaced by a guarantee property with 3 classes instead of 5
— a full Büchi emptiness check becomes reachability, on a smaller
object, and nothing smaller exists.* [DPT25] obtain `Fa`, a legal member
their Minato pass happened to land on; they cannot say it is a
guarantee (they *observe* their automaton is "now terminal"), cannot say
whether anything smaller exists, and cannot name the bracket it sits in.

### 6.2 Fig. 4: the stutter example, small enough to enumerate

[DPT25, Fig. 4] is `¬φ = XFa` given `K = ā` (i.e. `¬a` holds initially),
over `Σ = 2^{a}`. They use it to motivate `sirelax` / `sirestrict`:
`A_{XFa}` is stutter-sensitive — it rejects `w = a·ā^ω` but accepts
`aa·ā^ω`, two stutter-equivalent words — and since `w ∉ ℒ(K)`, the
freedom can be spent to repair that.

**The algebra.** `𝓘(XFa)` has **4 classes**: `[ε]`, `N` (no `a`), `A` (an
`a`, only at index 0), `T` (an `a` at index ≥ 1; absorbing), with the
product `(α,β)·(α',β') = (α∨α', β∨α')` where `α` = "contains an `a`",
`β` = "contains an `a` at index ≥ 1". Note `λ(a)² = A·A = T ≠ A`: the
letter class is not idempotent, so `XFa` is stutter-sensitive by the
read-off of §2 — [DPT25]'s observation, as a one-line equational check.
`𝓘(ā)` has **3 classes** (`[ε]`, `F_a`, `F_ā` — the first letter,
left-absorbing) and is stutter-invariant. The aligned product `T` has
**5 classes** and 8 linked pairs; both endpoint checks are inconclusive,
so Lemma 4.6 applies.

**The freedom is 3 bits.** The linked pairs outside `P_K` fall into three
conjugacy classes — `{(a1,n1)}` = the single word `a·ā^ω`;
`{(t_a,n1)}` = `a`-initial words with an `a` later but finitely many;
`{(t_a,t_a), (t_a,t_n)}` = `a`-initial words with infinitely many `a`s.
So the interval has exactly **8** members, and we can list what each
costs:

| `|𝒞|` | members |
|---|---|
| **3** | **1** — and it is `ℒ(¬φ) ∪ ℒ(¬K)` = `XFa ∨ a₀` = **`Fa`** |
| 4 | 4 — among them the input `XFa`, the lower endpoint `min|K`, and `G(a) ∨ F(ā ∧ Fa)` |
| 5 | 3 |

**Everything [DPT25] does to this example is a point of that lattice.**
Their `sirelax` adds the partly-covered stutter class and lands on `Fa` —
the minimum, reached by luck and unrecognized as such. Their `sirestrict`
removes it instead and lands on `G(a) ∨ F(ā ∧ Fa)`, which is precisely
the member `P_min ⊔ C₃`: legal, stutter-invariant, and **strictly worse**
(4 classes). And their Minato pass `BM` does **nothing at all** here —
they say so themselves: *"it would only give us bounds `ā…⊤` on the first
transition, but since this transition is already labeled by `⊤` it would
not be changed."* The heuristic that our operation doubles is, on this
instance, empty; the operation is not.

**What the operation does.** `max|K` is already `Fa` (3 classes), so the
reference points alone win here — and the floor certifies that no member
of the eight is smaller. But the greedy finds it too, and how it finds it
is the point: seeded at `π_{¬φ}` (the 4-class table of `XFa`, blocks
`[ε] | {a1} | {n1} | {t_a, t_n}`), **one merge** collapses `{a1}` into
`{t_a, t_n}` — and that merge *is* `λ(a)² ∼ λ(a)`, the stutter seed of
§5.3. The unconstrained minimizer **discovers stutter-invariance on its
own**, because on this instance the smallest member happens to be the
stutter-invariant one. The output is stutter-invariant where the input
was not — the partial-order reductions [DPT25] were after — and it is
smaller, and it is optimal. Three goals, one merge, no heuristic.

## 7. Evaluation plan

**What is already established, and by what.** The claims of this paper
are theorems, and §6 discharges the empirical-looking one — *the freedom
is leverageable* — on [DPT25]'s own two figures, by derivation rather
than by campaign: a `B` strictly smaller than the input on both, drops to
3 classes from 5 and from 4, **certified optimal by Lemma 4.6**, with a
rung drop on one and a stutter repair on the other. Nothing below is
needed to support that. What a campaign adds is *frequency* — how often
this happens on languages nobody chose to illustrate a paper with — and a
score for the greedy where the optimum is computable.

**Scope.** Wall-clock, the MCC benchmark and the downstream model checker
are out of scope for this draft; the tests are polynomial and the objects
are spec-sized.

**The instrument.** `simplify` (§4.6) as a tool: two `.sos` in, one
`.sos` out. **The sample:** same-stratum pairs from the census corpus of
[SωSN26] (3 938 canonical invariants, complement-closed, with
`.cat` sidecars carrying Wagner coordinates, the LTL bit and the stutter
tag), both sides small enough that `|F| ≤ 12` on a large share — so the
exhaustive `2^F` optimum is computable on most of the sample and the
greedy can be *scored*, not merely run.

**The table** (one row per pair): the three reference points
`|𝒞(¬φ)|, |𝒞(L(P_min))|, |𝒞(L(P_max))|`; the emitted `|𝒞(B)|`; `|F|`;
the rung of `¬φ` and of `B`; the stutter bit of each; and, where
`|F| ≤ 12`, the true optimum by enumeration.

**Headlines.** (1) The fraction of pairs where `|𝒞(B)|` is *strictly*
below all three reference points — the claim of this paper. (2) The
median reduction ratio `|𝒞(B)| / |𝒞(¬φ)|`. (3) The rung-drop rate.
(4) The stutter-invariance-gained rate, and the frequency of the
UNKNOWN verdict of §5.3 (how often the hull escapes the table — a
number no automata pipeline can produce). (5) The greedy-vs-exhaustive
gap distribution — *a measured quality of our heuristic*, and explicitly
**not** evidence about Conjecture 4.5.

**The first gate, before any table:** the counterexample of Thm 5.7,
which must return tier-1 UNKNOWN while the free greedy still emits a
member, and [DPT25]'s example of §6, whose predicted 3-class guarantee
answer is the first regression test.

**Already in hand** (from the interval core and the ladder, run on 700
same-stratum census pairs — census-shaped, with none of the MCC's
realistic bias toward fact-shaped `K`, but load-bearing): the freedom
`|F|` has min 0 / median 20 / p95 124 / max 458 bits, and the point
interval `|F| = 0` occurs. Endpoints: settles ≈ 7%, refutes 4–6% per
direction on random pairs; settles is identical under operand swap (the
symmetry §3 predicts) and the complement-partner stratum settles 100%,
as it must. Per rung — member exists / `¬φ` already there / **strict drop
available**, out of 700: safety 318/169/**149**, co-safety
321/164/**157**, obligation 453/347/**106**, recurrence 516/424/**92**,
persistence 529/429/**100**. Read: on ~21% of random census pairs,
knowledge buys a strict drop to safety — a Büchi-emptiness-to-
reachability discount before any realistic asymmetry is dialed in.
*Validation riding along:* the recurrence/persistence orientation of §2
agrees with the census chain coordinates on all 6 222 languages (and
decisively disagrees under the swapped orientation — 4 914 of 6 222);
the Horn hull passes the closure-operator laws with zero violations; and
on all 264 campaign cases with `|F| ≤ 12`, exhaustive enumeration of the
`2^F` lattice reproduces every rung verdict, the returned canonical
member equal to the intersection (Moore rungs) resp. union (kernel
rungs) of the enumerated members. Every refusal certificate replayed on
both source automata.

Protocol: per-case budgets, seeded and checkpointed runs, machine-
readable outputs promoted to a versioned reference tree; every number
the paper states in pure form is traceable to it.

## 8. Related work

**The automata-side original.** [DPT25] created the framework — the
interval theorem, the endpoint strategies, the Boolean bands with
Minato covers, the stutter closures under knowledge, incremental
integration, and the MCC evaluation. This paper is its algebraic double:
same soundness theorem, same goals, but the interval represented
exactly, the objective well-posed, the class questions decided rather
than probed, and witnesses canonical. The two remain complementary in a
precise sense (Thm 5.7): presentation-side closures can reach off-table
witnesses cheaply; the calculus knows *whether* and *what*, the automata
side renders it — the exit acceptor of the chosen `B` still deserves
their grooming against `A_K`.

**Minimization from constraints.** Our objective — fewest classes
consistent with a lower and an upper bound — is the ω-side of minimal
consistent automaton identification [Gol78]: the interval's mandatory
and forbidden lassos are the sample, the freedom `F` the don't-cares.
The NP membership of Thm 4.4 is the ω-semigroup counterpart of the
classical guess-and-check; the hardness (Conj 4.5) is open. Minato's
algorithm [Min93] plays the same role on the automata side — a greedy
search for a maximal simplification within bounds — which is why the two
programs have the same shape and different inner steps.

**Knowledge in verification.** Invariant-based property simplification
for CTL [BDJ+18] and quasi-invariants [LNO+14] are special cases of
knowledge; Dureja–Rozier's implication matrices across a formula set
[DR18] are subsumed by the §3 endpoint scans (their `f₁ ⇒ f₂` is
`L(P_min) = ∅` for the pair), which additionally simplify when no
implication holds. Blahoudek et al.'s refinement under mutual exclusion
of propositions [BDRS15] is the letter-level shadow of §5.4.
Assume–guarantee reasoning shares the "given that" phrase but not the
problem: there `K` is a contract to be discharged, here it is
established fact spent to simplify a different check.

**Stutter invariance.** The closure constructions and checks are
classical [HK96, PWW98, MD15]; §5.3 relocates them: the check is a
letter-idempotency scan [SωSC26, Prop 5.1], the least on-table
stutter-invariant superset is one instance of the quotient engine, and
the closure is exact but possibly **off-table** (Thm 5.7 — a phenomenon,
to our knowledge, unremarked).

**Separation.** The rung tests of §5.2 are decision procedures for
separator synthesis by class over ω-regular languages — the
effective-separation program pursued for first-order fragments over
finite words by Place–Zeitoun [PZ16], here in the topological/Wagner
dimension.

**Algebraic foundations.** ω-semigroups, linked pairs, conjugacy [PP04];
the Wagner hierarchy on the syntactic algebra [Wag79, CP97, CP99, SW08];
the ladder [Lan69, MP92, ČP03]. The given-that lattice is, to our
knowledge, the first use of the syntactic ω-semigroup as the *state
space of a synthesis problem* — choosing a language under interval
constraints — rather than as a recognizer or classifier; the program it
extends is [SωS26] (construction), [SωSC26] (calculus), [SωSX26]
(extraction), [SωSN26] (census).

## 9. Conclusion

Prior knowledge turns "translate `¬φ`" into "choose the smallest
representative of an interval of languages". On automata the interval is
invisible, the objective is ill-posed, and only a few members can be
built and compared. On the syntactic invariant the interval is a finite
lattice with measured freedom; the objective — fewest classes — is a
property of the language, not of a drawing; the search space is exactly
the congruences of one aligned table; admissibility of a congruence is
decided exactly by a bounded quotient test in polynomial time; the true
optimum sits in NP; and a greedy whose every inner step is a decision
procedure delivers a `B` that never regresses on the input. On both of
the examples [DPT25] chose to draw, it does better than that: a 3-class
answer against inputs of 5 and 4, **provably minimal** by the three-class
floor, dropping a recurrence property to a guarantee on one and repairing
a stutter-sensitive property on the other — where their own heuristics
land on a strictly larger member, or on nothing. The same quotient
engine, differently seeded, is stutterization and proposition-shedding;
constraints compose by a joint fixpoint rather than by chaining
heuristics. The exponentials sit where they always did: at entry, paid
once per spec-sized object, never per question.

The open edges are stated where they live: the hardness of `|𝒞|`
minimization (Conj 4.5), the locality map of §5.5 (which semantic hulls
stay on-table — settled negatively for stutter, open for obligation and
above), the lifting details of Prop 5.5, and the `p`-blind hull versus
`QE` comparison (§5.4).

---

## Appendix A. Decommissioned material (reuse candidates)

Results and plans from the 2026-07-11 draft that the operation of §4
does not need. They are correct as far as they go and are parked here
deliberately — each is a candidate for a follow-on paper or for
re-promotion if the operation's evaluation calls for it.

### A.1 The exact stutter test (stutter self-alignment)

**Theorem (exact stutterization — sketch).** A stutter-invariant
ω-regular `B` exists in the interval iff `SC(L(P_min)) ⊆ L(P_max)`, iff
the **stutter alignment** of `T` with itself detects no conflict:
`R_st := {(p, p') : some stutter-equivalent lassos α ≈ β have associated
T-cells p and p'}`, and the test is
`R_st ∩ ((Val_{P_min}{=}1) × (Val_{P_max}{=}0)) = ∅`. `R_st` is
computable in polynomial time: two stutter-equivalent lassos admit
block-synchronized presentations over a common destuttered base, so
pumping one base letter `b` multiplies the fold by an arbitrary element
of the cyclic set `⟨λ(b)⟩` — *independently* on the two tracks — and
`R_st` is reachability in a walk over states
`(last base letter, c, c') ∈ Σ × 𝒞 × 𝒞`, with the eventually-constant
normal forms `w·a^ω` handled as a separate, simpler case. `O(|Σ|²·n⁴)`
transitions.

**Why it is parked.** It decides existence exactly, but on "yes" the
witness is `SC(L(P_min))`, which Thm 5.7 shows need not be on the table
— so the operation has *nothing to emit*. It is a certified diagnostic
("the interval contains stutter-insensitive properties, but none this
algebra can express"), not a simplification. Promote it when off-table
re-entry (re-constructing `SC(L(P_min))` as a fresh spec-sized input) is
built; then it also subsumes both of [DPT25]'s stutter candidates and
removes their only source of timeouts (no complement is taken).

### A.2 Band-minimal Wagner degree

**Proposition (sketch — greedy band minimization).** When obligations
exist (Prop 5.4), encode alternation depths as a *level function*
`ℓ : R-classes → {0,…,k}`, monotone along the `R`-descent order, with
parity prescribed on forced classes. A `θ` with maximal alternation
`≤ k` exists iff such an `ℓ` exists, and the pointwise-least monotone
parity-respecting `ℓ*` is computed bottom-up over the condensation in
one pass. The minimal achievable Wagner degree pair is read off `ℓ*`.
*Status:* the encoding equivalence and the least-solution argument are
routine; the two-coordinate simultaneity is the open half. Free classes
are not innocent — one sitting above forced classes of both polarities
must create an alternation whichever way it is set.

**Why it is parked.** The Wagner degree is a refinement *inside* the
obligation band; the operation's objective is `|𝒞|`, and degree is at
best a tie-break. Promote it as a knob if the evaluation shows ties.

### A.3 Lossless incremental knowledge

[DPT25, §7] integrates facts `K₁, …, K_n` one at a time, accepting a
loss of precision to avoid the conjunction automaton. On the invariant
the incremental story is *exact*: maintain the running aligned table and
interval; integrating `K_{i+1}` is one more align plus two pointwise
updates, `P_min ∩= P_{K_{i+1}}`, `P_max ∪= P_{K_{i+1}}^c`, and every
intermediate interval is exactly the interval of the conjunction so far
(the endpoint surgeries are pointwise Boolean and the running product is
generated by the same factors). No delayed label choice, no precision
ledger; the price is table growth, and correlated operands realize a
small fraction of the `n₁·n₂` rectangle [SωSC26, §3.3]. Two falsifiable
laws to assert if this is ever run: *monotonicity* (`P_min` only shrinks,
`P_max` only grows, so every verdict improves monotonically) and
*losslessness* (the running interval reduces byte-equal to the one-shot
conjunction's).

**Why it is parked.** It is a claim about a *sequence* of operations; we
have not yet demonstrated one.

### A.4 LTL-given-that, end to end

When `φ` and `K` are both LTL, both tables are aperiodic, hence so is
the aligned `T` and every quotient of it, so by [SωSX26, Prop 5.11]
**every `B` the operation emits is LTL-definable**. With the extraction
of [SωSX26] (`sos2ltl`) the pipeline closes at the formula level: `ψ`
out, simpler than `¬φ`, equivalent to it given `K` — an operation
[DPT25] cannot reach (Spot has no automaton→LTL path). We record this as
a **corollary of a smaller algebra**, not as a separate construction to
build: a smaller invariant yields a smaller formula for free.

A second question falls out and stays open: when `¬φ` is *not*
LTL-definable, is some `B` in the interval LTL-definable —
**definability given that**? The LTL-definable saturated sets form a
Boolean subalgebra, so Lemma 5.1 applies abstractly, but no cheap hull
is known; enumeration decides it when `|F|` is small.

### A.5 The MCC-scale evaluation

The [DPT25] benchmark (1 601 model instances, ~150 facts each, 97 950
problems) and its protocol — endpoint reproduction against their
Table 1, freedom distribution, ladder hit rates, two-tier stutter rates,
incremental growth curves, and a formula-level table. Blocked on data
provisioning, and downstream of a working operation. Performance
comparisons (notably against `sirestrict`'s timeouts) belong here.

---

## Renumbering from the 2026-07-11 draft

| old | new |
|---|---|
| Prop 3.1 (lattice) | Prop 3.1 — unchanged |
| Lemma 4.1 (interval test) | **Lemma 5.1** |
| Prop 4.2 (safety/co-safety) | **Prop 5.3** |
| Prop 4.3 (obligation) | **Prop 5.4** |
| Prop 4.4 (recurrence/persistence) | **Prop 5.5** |
| Prop 4.5 (band-minimal degree) | **Appendix A.2** |
| §4.5 (locality / minimization landscape) | absorbed into §4.1, §4.5, §5.5 |
| §4.6 (worked example) | **§6.1** (+ **§6.2**, new: [DPT25] Fig. 4) |
| Prop 5.1 (stutter recognition) | **Prop 5.6** |
| Thm 5.2 (non-locality) | **Thm 5.7** |
| Thm 5.3 (self-alignment) | **Appendix A.1** |
| §6.1 (AP shedding) | **§5.4** |
| §6.2 (incremental) | **Appendix A.3** |
| §6.3 (LTL end to end) | **Appendix A.4** + corollary in §4.1 |
| — | **new: Prop 4.1, Prop 4.2, Prop 4.3, Thm 4.4, Conj 4.5, Lemma 4.6, Lemma 5.2** |

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
- **[Min93]** S. Minato. *Fast generation of irredundant sum-of-products
  forms from binary decision diagrams.* SASIMI 1993.
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
  syntactic ω-semigroup.* Working draft, 2026 (`sos_calculus.md`); the
  queued extensions (`sos_calculus_extensions.md`) are cited as
  [SωSC26-ext].
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
