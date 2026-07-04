# The SOSG, Constructed

**Claude (Anthropic)** and **Yann Thierry-Mieg**

*Working draft — 2026-07-04*

## Abstract

The syntactic ω-semigroup (SOSG) of a regular ω-language `L` is its canonical
algebra: the ω-analogue of the syntactic monoid that underpins the entire
finite-word theory of regular languages. Introduced by Arnold in 1985 as the
coarsest congruence saturating `L`, it is presentation-independent and complete —
it determines membership, equivalence, and every definability property of `L`,
including whether `L` is expressible in linear temporal logic. Yet, unlike the
finite-word syntactic monoid, which has been computed routinely for three decades,
the SOSG has never been constructed from an automaton. The obstruction is not
merely its size: computing it requires two ingredients the literature holds only
separately — a recognizer that remembers *acceptance along runs* rather than only
transitions, and a way to compute the inherently *two-sided* syntactic congruence
without ever quantifying over two-sided contexts. We supply both. The first is the
acceptance-enriched monoid `EM(D)`, read off any deterministic form `D` of `L`; we
prove it recognizes `L` and that the SOSG is a quotient of it. The second is a
collapse of Arnold's two context shapes into two independently checkable
relations — pointwise residual equality and right-invariant acceptance-profile
equality — together with a rotation lemma proving that the two-sided congruence is
computable by right multiplications alone. This yields the SOSG explicitly, for the
first time, as a canonical and *exportable* semantic representation of an ω-regular
language, LTL-definable or not. From that one object several familiar artifacts
fall out as exports: the exact LTL-definability decision; a portable,
representation-independent certificate refuting definability when it fails; a
defining LTL formula when it holds (the language reified *as a formula*); a
canonical counter-free automaton (the language reified *as an automaton*); and a
complete invariant that turns language equality into table equality. The
construction is uniform over finite and infinite words; its finite-word
specialization is the classical syntactic monoid, of independent interest to the
learning community.

---

## 1. Introduction

Finite-word regular language theory has a keystone: the **syntactic monoid**. It is
canonical (a function of the language, not of any accepting automaton), it is
computable (from a minimal DFA, in standard tools since AMoRE in the 1990s), and it
is the object through which the deepest structural facts are read — most famously
Schützenberger's theorem, that a language is star-free (equivalently first-order
definable) exactly when its syntactic monoid is aperiodic [Sch65]. Learning,
classification, and decision procedures for finite-word languages all pass through
this one algebra.

Infinite words have the exact analogue in principle. Arnold [Arn85] defined the
**syntactic congruence** of a regular ω-language `L` — the coarsest congruence that
saturates `L` — whose quotient is the **syntactic ω-semigroup**, which we abbreviate
**SOSG**. It is presentation-independent and it is *complete*: it fixes membership,
equivalence, and definability, and — by the classical chain
`LTL = FO[<] = star-free = aperiodic SOSG` [Kam68, Tho79, Per84, DG08] — reading
aperiodicity off it decides LTL-definability exactly, in both directions.

And yet the SOSG is, in practice, a phantom. It is defined everywhere and built
nowhere: no tool, to our knowledge, materializes it from an ω-automaton, and the
existing algorithmic accounts of aperiodicity for ω-languages are nondeterministic
on-the-fly complexity arguments [DG08, Prop. 12.3] that emit no algebra and no
evidence. This paper asks why, and removes the obstruction.

**The obstruction is structural, not just size.** Two difficulties, each solved in
the literature *in isolation*, were never combined into a construction:

1. **Recognition must see acceptance along runs.** A recognizing algebra for an
   ω-language cannot forget the marks a run passes through — only its endpoints —
   because acceptance is a property of the infinitely-visited marks. Carton, Perrin
   and Pin [CPP08] give such a recognizer (Boolean matrices over `Q × Q` recording
   whether a path exists and whether it passes an accepting state) but they read the
   *syntactic quotient* only by brute-force saturation over all context triples — an
   example, not a procedure.

2. **The syntactic congruence is two-sided.** Arnold's congruence quantifies over
   both a left context and a right one, inside two shapes (a linear tail and an
   ω-power loop). Maler and Staiger [MS97] display the congruence as a conjunction
   of a finitary and an infinitary part — but compute no quotient, and their
   infinitary part still quantifies a two-sided context inside the loop.

Our contribution is to supply both missing pieces and thereby construct the SOSG.
For (1) we define the **acceptance-enriched monoid** `EM(D)` and prove it recognizes
`L`, with the SOSG a quotient of it (§3). For (2) we **collapse** Arnold's two
shapes: the linear shape becomes pointwise residual equality, the ω-power shape
becomes right-invariant profile equality, and a two-line **rotation lemma** proves
the two-sided congruence is computable with right multiplications alone (§4). The
main theorem is that this right-computable quotient *is* the SOSG (Theorem 4.5).

**The object first, its uses second.** Having built the SOSG, we reify it as a
canonical, complete, *exportable* representation of the language — what a minimal
deterministic ω-automaton would be if one existed, which for ω-words it does not
(§5). The definability questions then become exports (§6): the decision (is `L`
LTL?), a portable witness when the answer is no, and — the two ways to render the
algebra back into a familiar object — a defining formula (`L` *as an LTL formula*,
via Diekert–Gastin) and a counter-free automaton (`L` *as an automaton*, via the
Cayley construction). We keep the tool out of the argument entirely: every claim
below is about the object.

Two examples run throughout. **`GF(aa) := GF(a ∧ Xa)`** ("infinitely many
`aa`-factors"), which *is* LTL but has a natural presentation whose transition
monoid carries a spurious group; and **`Even := (aa)*·b·Σ^ω`** ("an even number of
`a`'s, then a `b`, then anything"), the canonical mod-2 language, which is *not* LTL
and whose group is genuine. The first shows the SOSG destroying a fake group; the
second, exhibiting a real one and handing out its refutation.

---

## 2. The object

We fix a finite alphabet `Σ` (for LTL applications `Σ = 2^AP`), write `Σ*`, `Σ^ω`,
`Σ^∞ = Σ* ∪ Σ^ω`, and take `L ⊆ Σ^ω` regular. The input is any **deterministic,
complete** automaton `D = (Q, ι, δ, C, Acc)` with `L(D) = L`: `δ : Q × Σ → Q`, a
finite set `C` of acceptance **marks** carried on transitions, and an **Emerson–Lei**
acceptance condition `Acc` — a positive Boolean combination of `Inf(c)` and `Fin(c)`
over `c ∈ C`, the most general ω-regular acceptance, subsuming Büchi, co-Büchi,
Rabin, and Muller. For a state `q`, its **residual** is the ω-language
`L(q) = { α ∈ Σ^ω : the run of D from q on α satisfies Acc }`; determinism makes
`L(ι·u) = u⁻¹L` for every finite prefix `u`.

**ω-semigroups and linked pairs.** An ω-semigroup `S = (S₊, S_ω)` carries an
associative product on `S₊` and a mixed product `S₊ × S_ω → S_ω` and infinite power
`S₊ → S_ω`, subject to the usual associativity axioms [PP04, Ch. II]. A morphism
`φ : Σ^∞ → S` recognizes `L` if `L = φ⁻¹(P)` for `P ⊆ S_ω`. By Ramsey's theorem
every `α ∈ Σ^ω` admits a factorization into finite blocks whose images are
eventually a single idempotent `e`, so `α ∈ φ⁻¹(s)·φ⁻¹(e)^ω` for a **linked pair**
`(s, e)` — `se = s`, `e² = e` — of `S₊`; linked pairs are the algebraic addresses of
ultimately-periodic words [CPP08, PP04]. Two regular ω-languages coincide iff they
agree on ultimately-periodic words, so a recognizer's verdict on linked pairs
determines it entirely.

**The syntactic congruence (Arnold).** Two finite words `u, v ∈ Σ*` are
**syntactically congruent** for `L`, written `u ≈_L v`, when they are
interchangeable in both of Arnold's context shapes [Arn85]:

```
    (linear)    ∀ x, y ∈ Σ*, t ∈ Σ⁺ :   x·u·y·t^ω ∈ L  ⟺  x·v·y·t^ω ∈ L
    (ω-power)   ∀ x, y ∈ Σ*         :   x·(u·y)^ω  ∈ L  ⟺  x·(v·y)^ω  ∈ L
```

`≈_L` is a congruence of finite index; its quotient `S(L)₊ = Σ⁺/≈_L`, completed with
the linked-pair data into an ω-semigroup `S(L)`, is the **SOSG**. It is
presentation-independent (defined from `L` alone) and it is the coarsest congruence
saturating `L` [Arn85]. The two shapes are not redundant: they are the linear tail
after a mutation and the loop through it, and §4.4 shows each is needed.

**The characterization.** We *decide against*, and never re-prove, the classical
equivalences

```
    L is LTL-definable  ⟺  L is FO[<]-definable  ⟺  L is star-free  ⟺  S(L)₊ is aperiodic,
```

where **aperiodic** = group-free: no `s ∈ S(L)₊` has a nontrivial orbit
`s^a, …, s^{a+p} = s^a` with period `p > 1` [Kam68, Tho79, Per84, PP04, DG08]. A
nontrivial group is precisely a modulo-`p` counter, which star-free logic cannot
express.

*On the threads.* For `Even`, the letter `a` toggles the a-count parity before the
first `b`, and no finite context can undo that parity: `a` has order 2 in `S(Even)₊`
— a real group, so `Even` is not LTL. For `GF(aa)`, a run-parity presentation makes
`a` a transposition of two states, but at infinity the parity is invisible to
membership (an `aa` factor either recurs or not, a threshold not a count); the group
is an artifact of the presentation and, as §4 shows, is absent from `S(GF(aa))₊`,
which is aperiodic.

The task is to build `S(L)` from `D`. The two keys follow.

---

## 3. Key I — the acceptance-enriched monoid

The recognizer must remember what acceptance reads. The transition monoid of `D` —
the maps `q ↦ δ(q, w)` — does not: it forgets the marks a run collects, which is
exactly the data an Emerson–Lei condition consumes. We therefore enrich it.

**Definition 3.1 (enriched monoid).** For a finite word `w`, its **enriched
element** is the map

```
    ⟦w⟧ : q ↦ ( δ(q, w),  mk(q, w) ),
```

where `mk(q, w) ⊆ C` is the set of marks on the transitions of the run from `q` on
`w`. `EM(D)` is the set of enriched elements under composition

```
    ⟦w⟧·⟦w'⟧ : q ↦ ( δ(δ(q,w), w'),  mk(q,w) ∪ mk(δ(q,w), w') ),
```

a transformation monoid on the finite set `Q × 2^C`, generated by the letter
elements `⟦a⟧` (`a ∈ Σ`), with identity `⟦ε⟧ : q ↦ (q, ∅)`.

Write `st_e(q)`, `mk_e(q)` for the two components of `e ∈ EM(D)` at `q`. The map
`⟦·⟧ : Σ* → EM(D)` is a monoid morphism by construction.

**Lemma 3.2 (skeleton).** If two ω-words `α, β` factor into blocks with the same
sequence of enriched elements read from `ι` — i.e. `α = w₁w₂⋯`, `β = w'₁w'₂⋯` with
`⟦w₁⋯w_k⟧ = ⟦w'₁⋯w'_k⟧` for all `k` — then `α ∈ L ⟺ β ∈ L`.

*Proof.* Determinism gives a unique run for each. At every block boundary `k` the two
runs are at the same state `p_k = st_{⟦w₁⋯w_k⟧}(ι) = st_{⟦w'₁⋯w'_k⟧}(ι)`, and the
marks collected within block `k` are equal, `mk(p_{k-1}, w_k) = mk(p_{k-1}, w'_k)`, by
equality of the enriched elements and the composition law. Hence the two runs visit
the same states at boundaries and the same multiset of marks within each block, so
they have the same set of marks visited infinitely often — and `Acc`, an Emerson–Lei
condition, is a function of that inf-set alone. Thus the runs agree on acceptance. ∎

**Corollary 3.3 (`EM` recognizes `L`; the SOSG is a quotient).** The syntactic
morphism `Σ* → S(L)₊` factors through `⟦·⟧ : Σ* → EM(D)`. Consequently there is a
surjective ω-semigroup morphism `EM(D) ↠ S(L)`, and `S(L)` is a computable quotient
of `EM(D)`.

*Proof.* By Lemma 3.2, acceptance in any context depends on the constituent finite
words only through their enriched elements: if `⟦u⟧ = ⟦v⟧` then substituting `v` for
`u` in any block factorization preserves the enriched-element sequence, hence
membership. So `⟦u⟧ = ⟦v⟧ ⟹ u ≈_L v`, i.e. the enriched congruence refines `≈_L`;
`≈_L` therefore factors through `EM(D)`, and its quotient `S(L)` is a quotient of
`EM(D)`. ∎

**Proposition 3.4 (enrichment is necessary).** The transition monoid alone does not
recognize `L`: there are words `u, v` with `st_{⟦u⟧} = st_{⟦v⟧}` (equal state maps)
but `u ≉_L v`.

*Proof.* Take a state `p` with a self-loop on some letter `a` carrying a mark that
`Acc` reads (say `Inf`-required), and let `u = a`, `v` a word looping `p` to itself
on marks that `Acc` does not require. Then `st_{⟦u⟧}(p) = st_{⟦v⟧}(p) = p` but the
ω-power context `_^ω` at `p` separates them: `u^ω` collects the required mark
infinitely often and `v^ω` does not, so exactly one is accepted from `p`, and a
prefix reaching `p` transports the separation to a linear/ω-power context on the full
language. ∎

Proposition 3.4 is why a group in the transition monoid proves nothing about `L`: it
can be pure encoding, invisible to `EM` and hence to the SOSG. (Symmetrically,
aperiodicity of the transition monoid is *sufficient* for aperiodicity of `S(L)₊`,
inherited upward through the enrichment — a one-directional convenience, not part of
the object.) The `GF(aa)` thread is exactly this situation, resolved in §4.

*On the threads.* The enriched monoid of `GF(aa)`'s 2-state run-parity presentation
has 10 elements; that of `Even` has the four sink-and-parity behaviors closed under
the two letters. Both carry a group in `EM` — the question §4 answers is which one
survives the quotient.

---

## 4. Key II — the two-sided congruence, computed with right moves

Corollary 3.3 leaves us the syntactic congruence `≈_L` transported to a relation `~`
on the finite monoid `EM(D)` — congruent elements are those interchangeable in both
context shapes. Naively `~` quantifies over left context, right context, and loop.
We now collapse it into two relations that quantify over none of these on the left,
and prove the two-sided congruence is a right-refinement.

Throughout, `Acc(x, c)` for `x, c ∈ EM(D)` denotes the acceptance of an
ultimately-periodic word `w·z^ω` with `⟦w⟧ = x`, `⟦z⟧ = c` — well-defined by
Lemma 3.2 — read from `ι`.

**Lemma 4.1 (collapse).** `Acc(x, c)` depends on the prefix `x` only through the
single state `st_x(ι)`. Writing `A(q, c)` for the Emerson–Lei verdict of iterating
`c` from `q` (follow `st_c` from `q` to its closed cycle; take the marks `mk_c`
around that cycle; evaluate `Acc`), we have `Acc(x, c) = A(st_x(ι), c)`.

*Proof.* The prefix `w` (with `⟦w⟧ = x`) is read once; its marks are collected on a
finite run and are visited finitely often, so none lies in the inf-set of `w·z^ω`.
The inf-set is entirely determined by the ultimately-periodic tail `z^ω` read from the
state `st_x(ι)` the prefix reaches — which cycles through the functional graph of
`st_c` and repeats the marks `mk_c` around the closed cycle. Hence `Acc(x, c)` is a
function of `st_x(ι)` and `c` only, namely `A(st_x(ι), c)`. ∎

**Definition 4.2.** For `e, f ∈ EM(D)` let

```
    e ~lin f   ⟺   ∀ q ∈ Q :   L(st_e(q)) = L(st_f(q)),
    e ~ω  f    ⟺   ∀ b ∈ EM(D)¹ :   Aprof(e·b) = Aprof(f·b),        where  Aprof(c) = (q ↦ A(q, c)).
```

**Proposition 4.3 (factorization).** `e ~ f  ⟺  e ~lin f  ∧  e ~ω f`.

*Proof.* *Linear shape.* By Lemma 4.1, `x·e·y·t^ω ∈ L ⟺ A(st_{x·e·y}(ι), t)`, and
`st_{x·e·y}(ι) = st_y(st_e(st_x(ι)))`. As `x` ranges over `EM¹`, `st_x(ι)` ranges over
exactly the reachable states; fix such a `q`. The linear condition then reads
`∀ y, t : A(st_y(st_e(q)), t) = A(st_y(st_f(q)), t)`, i.e. the states `st_e(q)` and
`st_f(q)` accept the same ultimately-periodic words, i.e. (agreement on
ultimately-periodic words being language equality) `L(st_e(q)) = L(st_f(q))`. Over all
`q` this is `~lin`. The mark parts of `e, f` are irrelevant to it.

*ω-power shape.* By Lemma 4.1, `x·(e·y)^ω ∈ L ⟺ A(st_x(ι), e·y)`, and `∀x` collapses
to `∀q` as above, giving `∀ y : A(q, e·y) = A(q, f·y)` for all `q`, i.e.
`∀ y : Aprof(e·y) = Aprof(f·y)`, which is `~ω`. ∎

The linear half is computed **once, on `D`** — it is language-equivalence of reached
states, no monoid involved — and at the slot `q = ι` alone it is the classical
syntactic right congruence of Maler–Staiger [MS97]; `~lin` demands it at every start
state simultaneously. The ω half is a right-congruence condition seeded by profiles.
Neither has a left translation. What remains is to show the *two-sided* congruence
needs none.

**Lemma 4.4 (rotation).** `~` is the coarsest right-invariant equivalence contained
in the seed `(~lin, Aprof)`; equivalently, seeds equal under all right extensions are
equal under every two-sided context.

*Proof.* A left factor `a` acts on the seed only by re-indexing the slot. For `~lin`:
`st_{a·e}(q) = st_e(st_a(q))`, so a left `a` merely evaluates `~lin` at the shifted
slot `st_a(q)` — determinism. For `~ω`: reading `(a·e·b)^ω` from `q` equals reading
`a·(e·b·a)^ω`, and by Lemma 4.1 the finite `a`-prefix is invisible to the loop's
verdict, so `Aprof(a·e·b)(q) = Aprof(e·b·a)(st_a(q))` — a **right** extension `e·b·a`
of `e`, read at the shifted slot `st_a(q)`. Hence any two-sided context reduces to a
right extension at a re-indexed slot; if `e, f` agree under all right extensions at
all slots they agree under all two-sided contexts. Finally `~lin` is itself
right-invariant (derivatives of equal languages are equal:
`L(s) = L(s') ⟹ L(δ(s,a)) = L(δ(s',a))`), so `~` is the coarsest right-invariant
refinement of a single seed. ∎

Lemma 4.4 is the load-bearing step against Maler–Staiger: they *display* the
finitary × infinitary split; the rotation lemma is what makes the two-sided
syntactic congruence computable with the one operation a monoid's closure table
offers for free — right multiplication.

**Theorem 4.5 (the SOSG, constructed).** `EM(D)/~ = S(L)`, where `~ = ~lin ∧ ~ω` is
the right-computable congruence of Definition 4.2. Concretely, `S(L)₊` is the
partition of `EM(D)` obtained by seeding with `(~lin`-class, `Aprof)` and refining by
right multiplication to fixpoint.

*Proof.* By Corollary 3.3, `≈_L` factors through `EM(D)`, and by construction its
transported relation is exactly interchangeability in the two shapes, i.e. `~`; by
Proposition 4.3 this is `~lin ∧ ~ω`. So `EM(D)/~ = Σ⁺/≈_L = S(L)₊`, and the
linked-pair data (the accepting pairs, §5) completes it to `S(L)`. The stated
computation realizes `~` by Lemma 4.4: right-invariance of both seed components makes
one Moore-style refinement to fixpoint compute `~lin ∧ ~ω` exactly. ∎

**Proposition 4.6 (prefix-independence, as a theorem not a case).** `L` is
prefix-independent (`σα ∈ L ⟺ α ∈ L` for all `σ ∈ Σ*`) iff `L` has a single residual
iff `~lin` is total. In that case all discrimination is carried by `~ω`.

*Proof.* Prefix-independence says every residual `u⁻¹L` equals `L`; determinism then
gives one residual class, so `~lin`, which compares residuals of reached states, is
total. Conversely one residual class forces every prefix to preserve membership. ∎

Angluin and Fisman note the same blindness from the learning side: LTL languages with
a *trivial right congruence* exist, e.g. `FG(a ∨ Xa)` [AF21] — the profile half is the
repair. This is precisely why the negative certificate must come in two shapes (§6.2).

*On the threads, resolved.* For `GF(aa)`, the ten enriched elements refine to **six**
`~`-classes, every class power-cycle of period 1: the run-parity words the transition
monoid kept apart are `~`-equivalent (at infinity the parity collapses to the
threshold "contains `aa`"), so `S(GF(aa))₊` is aperiodic — `GF(aa)` is LTL, its
group destroyed by the quotient. For `Even`, the letter `a`'s order-2 action survives
into `S(Even)₊`: a genuine `Z₂`, so `Even` is not LTL, and §6.2 extracts its witness.

---

## 5. The reified object

Theorem 4.5 produces `S(L)` as concrete data: a set of classes, a multiplication
table, the images of the letters, and — to recover `L` and not merely its algebra —
the set of **accepting linked pairs** `P = { (s, e) : e² = e, se = s, u·z^ω ∈ L for
⟦u⟧ ∈ s, ⟦z⟧ ∈ e }`. We key each class by its **shortlex-least representative word**
over `Σ` (a language invariant, independent of `D`), so the data is a function of `L`
alone.

**Theorem 5.1 (complete invariant).** For a fixed `Σ`, the tuple `𝓘(L) = ` (keyed
classes, multiplication table, letter map, accepting-pair set `P`) determines `L`
exactly: two regular ω-languages over `Σ` are equal iff their `𝓘` coincide.

*Proof.* `𝓘(L)` encodes the syntactic morphism `⟦·⟧` up to the canonical keying and
the accepting set. Membership of any ultimately-periodic word `u·z^ω` is decided by
computing `(⟦u⟧, ⟦z⟧)`, reducing to its linked pair, and testing `P`. Since regular
ω-languages are equal iff they agree on ultimately-periodic words, `𝓘(L)` determines
`L`. Conversely `𝓘` is a function of `L` (Theorem 4.5, canonical keying), so equal
languages have equal `𝓘`. ∎

Theorem 5.1 is what makes the SOSG worth building as an object rather than as a means
to a verdict. It is a **canonical, complete, presentation-independent semantic
representation** of `L` — what a minimal deterministic ω-automaton would be, except
that for ω-words no canonical minimal deterministic automaton exists. It is
*exportable*: a serialization of `𝓘(L)` is a portable artifact — a semantic HOA — that
any downstream consumer can read, and two such artifacts are language-equal iff
byte-equal after canonical keying. Notably `𝓘` needs no aperiodicity: it is defined
for *all* regular ω-languages, LTL or not. What one does with the object is the
subject of §6; that one *has* it is the point of this section.

A first, aperiodicity-free use: **language equality is table equality.** Where
pairwise equivalence of `N` languages costs `O(N²)` automaton products, hashing `𝓘`
buckets a corpus by true language in a hash join — the natural operation for
deduplicating large language sets.

---

## 6. Exports

From the one object, the definability questions and two reifications follow. We keep
these deliberately short: each is a corollary of §§4–5, not a construction of its own.

### 6.1 Deciding — is `L` LTL?

Read aperiodicity off `S(L)₊`: power-iterate each class (the class of `v^{k+1}` is a
function of those of `v^k` and `v`, since `~` is a two-sided congruence by
Lemma 4.4), and detect a group by a repeated class in a power sequence. Aperiodic ⟺
LTL, exactly and in both directions, because `S(L)₊` *is* the presentation-independent
invariant (Theorem 4.5) — a group in it is never an artifact. This is the whole
decision; there is no separate screen.

### 6.2 Refuting — a portable witness of non-LTL

When `S(L)₊` has a group, non-LTL-ness can be handed out as an object checkable
against `L` by membership alone, trusting nothing about the SOSG computation. Two
shapes mirror Arnold's two contexts:

```
    F₁(u,v,x,p) :  n ↦ [ u·vⁿ·x   ∈ L ]      F₂(u,v,y,p) :  n ↦ [ u·(vⁿ·y)^ω ∈ L ],
```

`p > 1`, each sample ultimately periodic, membership determined by `n mod p` and
non-constant.

**Proposition 6.1 (soundness, representation-free).** Either family with `p > 1`
proves `L` is not star-free.

*Proof.* If `L` were star-free, `S(L)₊` would be aperiodic, so `[vⁿ]` would be
eventually constant in `n`; by Lemma 3.2 membership of the samples would be eventually
constant, contradicting a genuine period `p > 1` holding for all `n`. The argument
mentions no automaton and no algebra — only `L` and the samples. ∎

**Proposition 6.2 (completeness — two shapes suffice).** If `L` is not LTL, a family
of shape `F₁` or `F₂` exists; no third shape is needed.

*Proof.* Arnold's congruence separates finite words by exactly the linear and
ω-power contexts [Arn85]. A group of period `p > 1` in `S(L)₊` has two powers `v^a,
v^{a+1}` that are non-congruent, hence separated by a context of one shape; unrolling
that separation along the power cycle yields a toggling family of the matching shape.
Both shapes are load-bearing: on a prefix-independent `L` (Proposition 4.6) every
linear sample is constant, so `F₂` is required. ∎

The witness is *extracted* by locating a group cycle in `S(L)₊` and running the DFA
distinguishing-word construction forward over the right-multiplication table to a
separating extension, whose location (a residual difference or a profile difference)
names the shape; it is then replayed by membership against `L` itself, so not even our
representation is trusted. Following the certifying-algorithms discipline [MMNS11],
this is *negative-side* certification with a **language-level** witness — where the
classical evidence for non-aperiodicity (a forbidden cycle in a minimal DFA, a
finite-order element of a group `H`-class) is representation-bound and meaningless
without trusting the construction under audit. We know of no prior packaging of
non-star-freeness as a replayable, representation-independent certificate.

*Thread.* `Even`: `v = a`, `p = 2`, `x = b·a^ω`; the sample `aⁿ·b·a^ω ∈ Even ⟺ n
even` — a linear `F₁`. (The prefix-independent mod-2 "every `a`-block eventually
even" is the `F₂` cameo: `~lin` blind, the witness necessarily an ω-power.)

### 6.3 Reifying `L` as a formula — the Diekert–Gastin synthesis

When `S(L)₊` is aperiodic, the algebra can be turned back into an LTL formula by
Diekert and Gastin's local-divisor induction [DG08, §8], whose input is precisely a
recognizing morphism onto a *canonical* aperiodic monoid — supplied, for the first
time, by Theorem 4.5. The induction pivots on a visible letter `c`, replaces the
monoid by its strictly smaller local divisor `mT ∩ Tm` (strict decrease is where
aperiodicity is spent), compresses words at their `c`'s, and recurses on the smaller
monoid and the smaller alphabet, translating back by two substitution lemmas; the
infinite-word letters are handled as conjugacy classes of linked pairs [PP04]. (We
note in passing that the paper's substitution clause prints a non-strict `U` where a
strict next-until is required, and that the synthesized formula, being a function of
the canonical algebra, is a normal form — same language, same formula.) The formula,
verified equivalent, is the checkable certificate the positive verdict of §6.1
otherwise lacks. *Thread:* `GF(aa)` pivots on the idle letter `¬a`, discovers that an
`aa` never straddles a `¬a`, and reassembles to `GF(a ∧ Xa)`.

### 6.4 Reifying `L` as an automaton — the Cayley construction

The parallel reification turns the algebra into an automaton. The **right-Cayley
automaton** of `S(L)₊¹` has the classes as states and `s ↦ s·⟦a⟧` as its transition
on letter `a`.

**Proposition 6.3.** The transition monoid of the right-Cayley automaton is the
right-regular representation of `S(L)₊`, hence isomorphic to `S(L)₊`; it is
therefore aperiodic — i.e. the automaton is **counter-free** — exactly when `L` is
LTL.

*Proof.* The maps `s ↦ s·t` for `t ∈ S(L)₊` generate a monoid isomorphic to `S(L)₊`
(the right-regular representation of a monoid is faithful); aperiodicity transfers.
Diekert–Gastin's counter-free theorem [DG08] equates counter-free with aperiodic
transition monoid for deterministic automata. ∎

This is a **forward, deterministic, constructible counter-free automaton** for any
LTL language — the object no minimal deterministic ω-automaton provides, and the
forward mirror of the co-deterministic prophetic form. Any construction assuming
counter-freeness — the Krohn–Rhodes cascade of [BLS22] among them — can be re-run on
it. One point remains open: the **acceptance condition** on the Cayley transitions,
an Emerson–Lei table filled from the profiles via the linked pairs, and whether it is
well-defined from the infinity set of states alone; Maler–Staiger [MS97] is the entry
point, and the residual quotient alone is provably too coarse (that of a 2-state
parity form of `GF(aa)` is a single state). We record this as the natural sequel, not
a claim.

---

## 7. Finite words

*(Placeholder — deferred to a later iteration.)* The construction is uniform over
`Σ^∞`: restricted to finite words `Σ*`, the enriched monoid degenerates to the
transition monoid with a "reached final" flag, the profiles and linked-pair calculus
vanish, `~ω` collapses, and `EM/~` is the classical **syntactic monoid**. The
finite-word specialization — its relation to the learning community's families of
right congruences and syntactic FDFAs [Kla94, AF16, ABF18, AF21], and to the
finite-word Schützenberger decision [Sch65, CH91] — is the subject of a companion
treatment.

---

## 8. Feasibility

The construction is dominated by `|EM(D)| ≤ (|Q|·2^{|C|})^{|Q|}`; the `|Q|` in the
exponent is the explosion. It is intrinsic, not an engineering apology: deciding
aperiodicity of a regular ω-language is PSPACE-complete (hardness transferred from
minimal-DFA finite-word aperiodicity [CH91]; the ω upper bound is [DG08, Prop. 12.3]),
so a size bound somewhere is a mathematical necessity. Around materialization the work
is polynomial in `|EM|` and `|Q|`. Every enriched element is a vector of `|Q|` slots
over the small local domain `Q × 2^C`, and every operation the construction uses is a
slot-wise right multiplication — the shape symbolic (decision-diagram) fixpoint
methods are built for, an opening on the `|Q|` exponent that nothing in §§3–4 forbids.
We claim no economy beyond effectiveness.

---

## 9. Conclusion

The syntactic ω-semigroup is the canonical algebra of an ω-regular language and, for
four decades, a phantom — defined, central, and never built from an automaton. It was
never built because construction needs a recognizer that sees acceptance along runs
and a way to compute a two-sided congruence with one-sided moves; the acceptance-
enriched monoid and the rotation-collapsed Arnold decomposition are exactly those two
keys, and Theorem 4.5 assembles them into the object. Reified, it is a canonical,
complete, exportable semantic representation of the language, LTL or not, from which
the decision, a portable non-LTL witness, and the two reifications — as a formula and
as a counter-free automaton — all follow as exports. The syntactic ω-semigroup is not
only definable; it is buildable, and worth building.

---

## References

- **[Arn85]** A. Arnold. *A syntactic congruence for rational ω-languages.* TCS 39
  (1985) 333–335.
- **[ABF18]** D. Angluin, U. Boker, D. Fisman. *Families of DFAs as acceptors of
  ω-regular languages.* LMCS 14(1) 2018.
- **[AF16]** D. Angluin, D. Fisman. *Learning regular omega languages.* TCS 650
  (2016) 57–72.
- **[AF21]** D. Angluin, D. Fisman. *Regular ω-languages with an informative right
  congruence.* Inf. Comput. 278 (2021).
- **[BLS22]** U. Boker, K. Lehtinen, S. Sickert. *On the Translation of Automata to
  Linear Temporal Logic.* FoSSaCS 2022.
- **[CPP08]** O. Carton, D. Perrin, J.-É. Pin. *Automata and semigroups recognizing
  infinite words.* 2008.
- **[CH91]** S. Cho, D. T. Huynh. *Finite-automaton aperiodicity is PSPACE-complete.*
  TCS 88 (1991) 99–116.
- **[DG08]** V. Diekert, P. Gastin. *First-order definable languages.* In *Logic and
  Automata*, 2008.
- **[Kam68]** H. Kamp. *Tense Logic and the Theory of Linear Order.* PhD thesis, UCLA,
  1968.
- **[Kla94]** N. Klarlund. *A homomorphism concept for ω-regularity.* CSL 1994.
- **[MS97]** O. Maler, L. Staiger. *On syntactic congruences for ω-languages.* TCS 183
  (1997) 93–112 (rev. 2008).
- **[MMNS11]** R. McConnell, K. Mehlhorn, S. Näher, P. Schweitzer. *Certifying
  algorithms.* Computer Science Review 5(2) 2011.
- **[Per84]** D. Perrin. *Recent results on automata and infinite words.* MFCS 1984.
- **[PP04]** D. Perrin, J.-É. Pin. *Infinite Words: Automata, Semigroups, Logic and
  Games.* Elsevier, 2004.
- **[Sch65]** M. P. Schützenberger. *On finite monoids having only trivial subgroups.*
  Information and Control 8 (1965) 190–194.
- **[Tho79]** W. Thomas. *Star-free regular sets of ω-sequences.* Information and
  Control 42 (1979) 148–156.
