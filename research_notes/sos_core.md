# Materializing the Syntactic ω-Semigroup: a Canonical Representation of Regular ω-Languages

**Yann Thierry-Mieg**

With significant inputs from
**Claude (Anthropic)**

*Working draft — 2026-07-13*

## Abstract

- The syntactic ω-semigroup: canonical, complete, defined since Arnold 1985, never built.
- Contribution 1: the object itself, reified as `𝓘 = ⟨𝒜, P⟩` — an algebra
  `𝒜 = (𝒞, λ, M)` and an acceptance layer `P` over it — with a standalone
  lasso-membership semantics: a canonical normal form for ω-regular languages, which
  the domain has never had.
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

We fix a finite alphabet `Σ` and write `Σ*` for the finite words over it, `Σ⁺` for
the nonempty ones, `Σ^ω` for the infinite ones. The same exponents
serve on letters and words: for `x ∈ Σ`, `x*` — finitely many repetitions of `x`,
possibly none; `x⁺` — at least one; `x^ω` — repeated forever. A **language** here is a set of infinite words,
`L ⊆ Σ^ω`; we take `L` **regular** (ω-regular [PP04]) — the class with finite-memory
descriptions, and exactly the class the invariant of §3 captures. All examples in this
paper live over the two-letter alphabet `Σ = {a, b}`. This section fixes the few
classical notions the invariant rests on, adapting the presentation of Perrin and Pin
[PP04], each paired with the intuition tying the algebra back to languages of
infinite words.

Consider the language of Carton and Perrin [CP97, Ex. 10] described by `a*·b^ω` —
some `a`'s, then `b`'s forever — which we name `aUGb`. Its syntactic ω-semigroup
is drawn in Figure 1.

![Figure 1 — the invariant of aUGb](sos_core_figs/img/core_F0_astar_bomega.png)

*Figure 1 — the syntactic ω-semigroup of `aUGb = a*·b^ω`: five classes of finite
words, the letter steps between them, and the accepting pairs `P` beneath. It is the
multiplication table represented as a graph: both vertices and edges are labeled by
classes, modeling the product `M : 𝒞 × 𝒞 → 𝒞` of the algebra `𝒜` (§3) — following an
edge multiplies on the right by its label.*

**We only ever look at lassos.** A **lasso** (ultimately-periodic word) is `u·v^ω`: a
finite **stem** `u`, then a finite nonempty **loop** `v` repeated forever. The
organizing fact: *two regular ω-languages are equal iff they agree on all lassos*
[PP04, Ch. I, Cor. 9.8]. Classifying `L` is therefore assigning each lasso to one of finitely many
equivalence classes, and every notion below is machinery for naming the classes and
computing the assignment.

*Example.* `b^ω`, `ab·b^ω` and `aab·(bb)^ω` are lassos of `aUGb`; `ba·(ab)^ω` is a
lasso outside it.

**On finite words, the classifier is a finite monoid.** A **monoid** is a set with an
associative product and an identity element; the finite words `Σ*` form one, under
concatenation, with the empty word as identity. A finite monoid `M` **recognizes** a
language of finite words through a **morphism** `φ : Σ* → M` — a map carrying
concatenation to the product, `φ(u·v) = φ(u)·φ(v)`, and `ε` to the identity — such
that membership depends only on the value: the language is `φ⁻¹(P)` for an accepting
set `P ⊆ M`. The finitely many elements of `M` are the classes, and `φ` computes the
assignment, letter by letter. Every regular language of finite words is recognized by
a finite monoid, and among its recognizers one is canonical, the **syntactic monoid**
— the cornerstone of algebraic language theory [PP04].

*Example.* For `aUGb`, concatenation collapses onto five values — the five boxes
of Figure 1, the class `[ε]` of the empty word among them.

On *infinite* words, exactly one thing more is needed, because no product of finite
pieces expresses `v^ω`. One adjustment first: the empty word is the single finite
word that cannot be repeated forever — `ε^ω` is not an ω-word — so the infinite
theory is built on the nonempty words `Σ⁺`, a **semigroup**: the associative product
alone, no identity required. On `Σ⁺` and `Σ^ω` together, the words carry three total
operations:

* **concatenation** `Σ⁺ × Σ⁺ → Σ⁺` of two finite words;
* the **mixed product** `Σ⁺ × Σ^ω → Σ^ω` — a finite word prefixed to an ω-word,
  concatenation continued;
* the **ω-power** `Σ⁺ → Σ^ω`, `v ↦ v^ω` — the new operation, repetition forever.

An **ω-semigroup** `S = (S₊, S_ω)` is a finite structure with the same signature, one
**sort** per kind of word [PP04, Ch. II]: a finite semigroup `S₊` carries the classes
of nonempty finite words, a finite set `S_ω` carries the classes of ω-words; the
three operations become a product `S₊ × S₊ → S₊`, a mixed product `S₊ × S_ω → S_ω`,
and an ω-power `S₊ → S_ω`. The general definition equips the pair with an *infinite
product* `S₊^ω → S_ω` — one class for every infinite sequence of finite classes
[PP04, Ch. II]; on finite carriers the ω-power determines it entirely
[PP04, Ch. II, Thm 5.1], and the table-sized signature above is the form recalled
here. A **recognizer** for `L` is an ω-semigroup with a morphism
`φ = (φ₊, φ_ω)`, one component per sort — `φ₊ : Σ⁺ → S₊`, `φ_ω : Σ^ω → S_ω` —
carrying each operation to its counterpart,

`φ₊(u·v) = φ₊(u)·φ₊(v)`,   `φ_ω(u·w) = φ₊(u)·φ_ω(w)`,   `φ_ω(v^ω) = φ₊(v)^ω`,

such that membership depends only on the class: `L = φ_ω⁻¹(P)` for a set `P ⊆ S_ω`
of accepting ω-classes. Every regular `L` has a finite recognizer
[PP04, Ch. II, §7]. The organizing claim
is now explicit: two lassos with the same ω-class receive one verdict, and there are
at most `|S_ω|` classes of lassos.

**The second sort will not be carried.** Everything `S_ω` records about a lasso is
determined inside `S₊` by the classes of its stem and of its loop — the idempotent
power and the linked pair below are that determination made exact
[PP04, Ch. II, Thm 5.1]. §3 therefore
keeps one carrier — the classes of finite words, the class `[ε]` adjoined back to
make it a monoid again — and replaces `P` by a set of accepting *pairs* of word
classes.

*Example.* Figure 1 already has this one-sorted shape: five classes of finite words
and, beneath the drawing, the acceptance data as pairs of classes — no box for an
ω-word anywhere.

**The idempotent power.** In a finite semigroup the powers `s, s², s³, …` of any element
cannot all be distinct, so the sequence is eventually periodic and contains a unique
**idempotent**, the one power `s^n` (`n ≥ 1`) with `s^n·s^n = s^n`: the **idempotent
power** of `s`. Now read a loop `v` through the
morphism's finite-word component, simply `φ` from here on: the values of
`v, vv, vvv, …` are the powers of `φ(v)`, so they settle on the idempotent power of `φ(v)`.
That is how "loop forever" is read without any infinite object at hand: iterate the
loop's value until it stops changing, and keep that stable value.

*Example.* On Figure 1 (`aUGb`), the value `φ(b) = [b]` is its own idempotent power —
more `b`'s change nothing, `[b]·[b] = [b]`. The value `φ(ab) = [a·b]` is not: its
square `[a·b]·[a·b] = [b·a]` is the value of the *dead* words (`abab` puts an `a`
after a `b`, and no continuation rescues that), itself idempotent — so the idempotent
power of `φ(ab)` is `[b·a]`: looping `ab` forever is exactly as dead as slipping once.

**A linked pair names a lasso.** Reading `u·v^ω` through the morphism `φ`
(Ramsey's theorem [PP04, Ch. II, Thm 2.1]): the loop
settles on an idempotent `e` — the idempotent power of `φ(v)` — and the stem on
`s = φ(u)·e`, with `s·e = s` (the
stem precedes the loop and is absorbed by it). A **linked pair** is any `(s, e)` with
`e² = e` and `s·e = s`; `s` names the stem, `e` the loop, `(s, e)` the lasso. A
recognizer is fixed by which lassos it accepts, hence by its set of **accepting linked
pairs** — which is why (§3) the acceptance datum of the invariant is a *set of pairs*, not a
subset of the monoid.

*Example.* Read `aab·b^ω` on Figure 1: the loop's value `[b]` is already idempotent,
so `e = [b]`; the stem walks `a·a·b` from the root to `[a·b]`, which the loop absorbs
(`s = [a·b]·[b] = [a·b]`). The pair `([a·b], [b])` names the lasso — as it does every
lasso with stem in `a⁺b*` and loop in `b⁺`.

**One lasso, many names.** A single ω-word has many presentations —
`u·v^ω = (uv)·v^ω = u·(v²)^ω = (u v₁)·(v₂ v₁)^ω` — and, as §3 shows, these need not name
it by the same linked pair. Reconciling them is not bookkeeping: it is the **rotation
lemma** (§3), the paper's structural pivot, and the one nontrivial constraint the invariant
must satisfy.

*Example.* `a·(ba)^ω = ab·(ab)^ω = ab·(abab)^ω`: one ω-word, three presentations —
and infinitely many more. §3 shows how to canonically choose a single one, and gives
it: shortest stem, then shortest loop — here `(ab)^ω` with the empty stem, the
shortlex representative of the whole family.

We now present a canonical representation of an arbitrary regular ω-language `L`,
using its syntactic ω-semigroup reified as an invariant `𝓘(L)`.

## 3. The syntactic ω-semigroup as an invariant `𝓘(L)`

The definition of the invariant

```
    𝓘(L) = ⟨𝒜, P⟩
```

splits in two parts: the **algebra** `𝒜`, a finite monoid classifying the finite
words, and the **acceptance layer** `P`, a set of accepted linked pairs carrying
acceptance. We define the algebra first.

### 3.1 Syntax: the invariant `𝓘 = ⟨𝒜, P⟩`

Let us define the algebra component `𝒜` of the invariant `𝓘 = ⟨𝒜, P⟩`.

**Definition 3.1 (algebra).** An **algebra** `𝒜` over `Σ` is a triple `(𝒞, λ, M)`:

- `𝒞` is a finite set of **classes**, denoted `[c]`, where `c ∈ Σ*` is the
  **representative** of that class; the empty word is always in its own class `[ε]`;
- `λ : Σ ∪ {ε} → 𝒞` is the **letter map**, associating to each letter of the alphabet
  its class; by definition `λ(ε) = [ε]` and, for all `x ∈ Σ`, `λ(x) ≠ [ε]` — `[ε]` is
  **isolated**;
- `M : 𝒞 × 𝒞 → 𝒞` is the **multiplication table**: **associative**, with `[ε]` a
  two-sided **identity** — for all `c ∈ 𝒞`, `M(c, [ε]) = M([ε], c) = c` — so `(𝒞, M)`
  is a finite monoid, and we write `s·t := M(s, t)`.

By convention, the shortlex-smallest word in each class (shortest, then alphabetical)
is chosen as its representative.

*Example.* The algebra of `aUGb` (`a*·b^ω`) is represented in Figure 1. It
contains five classes `𝒞 = {[ε], [a], [b], [a·b], [b·a]}`, which are also the
vertices of the diagram, with `λ(a) = [a]` and `λ(b) = [b]`. The edges are also
labeled by `𝒞`, representing the multiplication table `M : 𝒞 × 𝒞 → 𝒞` of the algebra
as a graph. The letter actions

```
 ·a :  [ε]↦[a]    [a]↦[a]     [b]↦[b·a]   [a·b]↦[b·a]   [b·a]↦[b·a]
 ·b :  [ε]↦[b]    [a]↦[a·b]   [b]↦[b]     [a·b]↦[a·b]   [b·a]↦[b·a]
```

are read off its edges, and these two rows are the whole of `M`: any product `s·t` is
the representative of `t` walked from `s`, edge by edge.

*Example.* On Figure 1 (`aUGb`), consider the lasso `aab·b^ω`. Its reading starts in
`[ε]`, and we do not progress by
letters but by classes: reading a letter `x` follows the edge labeled `λ(x)`. The
first `a` follows `[a]`, from `[ε]` to `[ε]·[a] = [a]`, the class vertex of the
letter itself. In this
situation reading `a` stays in place, `[a]·[a] = [a]`, while `b` moves on,
`[a]·[b] = [a·b]`: after the stem `aab` we sit in `[a·b]`. The loop `b^ω` then turns
on the self-loop `[b]` of `[a·b]` forever — the reading of a lasso is a finite path
that ends circling a cycle. Reading §2's outside lasso `ba·(ab)^ω` instead:
`[ε]·[b] = [b]`, then `[b]·[a] = [b·a]`, and the loop `(ab)^ω` circles at `[b·a]`,
since `[b·a]·[a] = [b·a]·[b] = [b·a]`.

*Example.* On Figure 1 (`aUGb`), `[a]` holds the words in `a⁺`, `[b]` those in
`b⁺`, `[a·b]` those in `a⁺b⁺`, and `[b·a]` the *dead* words, a two-sided **zero**
(`x·[b·a] = [b·a]·x = [b·a]`): once an `a` follows a `b`, no continuation can rescue
the word — which is why the second reading never left `[b·a]`.

**The letter map.** `λ` is data in its own right: two algebras may share their
classes and their table and differ only in `λ`.

*Example.* Over `Σ = {a, b, c}`, the language `(a|c)*·b^ω` has exactly the five
classes and products of Figure 1: `a` and `c` are interchangeable everywhere, so
`λ(a) = λ(c) = [a]`, and the drawing is unchanged; only `λ` tells the two algebras
apart.

**The idempotent power.** Each class `s` has a unique idempotent power (§2): among
the powers `s, s², s³, …` — finitely many, since `𝒞` is finite — exactly one is
idempotent. We write it `s^ω`: the superscript is free — the invariant carries no
second sort and no ω-power — and this idempotent is exactly what stands in for them.
It is a computation on the multiplication table alone.

*Example.* On Figure 1 (`aUGb`), all classes but `[a·b]` are
idempotent, hence their own idempotent powers:
`[ε]` is the identity; `[a]·[a] = [a]` and `[b]·[b] = [b]` read on their self-loops —
more `a`'s, more `b`'s change nothing; and `[b·a]·[b·a] = [b·a]`, the zero absorbing
even itself. `[a·b]` is not: gluing two words of `a⁺b⁺` puts an `a` after a `b`, so
`[a·b]·[a·b] = [b·a]` — already idempotent. Hence `[a·b]^ω = [b·a]`: iterating "`a`'s
then `b`'s" forces an `a` after a `b`.

The second component of the invariant `𝓘` is a set of pairs of classes.

**Definition 3.2 (pair set; invariant).** A **pair set** over an algebra `𝒜` is a
finite set `P ⊆ 𝒞 × 𝒞` of pairs of classes. An **invariant** is a pair `𝓘 = ⟨𝒜, P⟩`.

*Example.* Figure 1 carries its pair set beneath the drawing:
`P = { ([b], [b]), ([a·b], [b]) }`. Of the two lassos we have been reading since §2,
only `aab·b^ω` belongs to `aUGb`; `ba·(ab)^ω` does not — and `P` is the data that
separates them. The first reading ended circling `[a·b]` on the loop class `[b]`, and
`([a·b], [b])` is listed in `P`; the second ended at `[b·a]`, which appears in no
pair.

### 3.2 Semantics: the language of an invariant

An invariant decides lassos with the data it carries and nothing else: `λ` assigns
each letter its class, the table `M` extends that assignment to every finite word —
stem and loop alike — and `P` lists the pairs that accept. The assignment of words
to classes comes first.

**Definition 3.3 (fold).** Let `𝒜 = (𝒞, λ, M)` be an algebra over `Σ`. The
**fold** of `𝒜` is the map `⟦·⟧ : Σ* → 𝒞` extending the letter map to all finite
words through the table: for `u = x₁x₂⋯xₙ ∈ Σ*`,
`⟦u⟧ := λ(x₁)·λ(x₂)·⋯·λ(xₙ)`, the empty product being `⟦ε⟧ := λ(ε) = [ε]`; we call
`⟦u⟧` the fold of `u`.

The fold is well defined: `M` is a total function and associative (Definition 3.1),
so the product of the letter classes always exists and its value does not depend on
how it is parenthesized — one class per word. It is moreover a monoid morphism —
`⟦u·v⟧ = ⟦u⟧·⟦v⟧`, `⟦ε⟧ = [ε]` — the only one agreeing with `λ` on the letters: on
nonempty words it is §2's morphism `φ`, realized on the table, and the adjoined
`[ε]` extends it to the empty word.

*Example.* On Figure 1 (`aUGb`), the fold of a word is where its reading ends — one
letter, one edge, from the root: `⟦aab⟧ = [a]·[a]·[b] = [a·b]`, and
`⟦ba⟧ = [b]·[a] = [b·a]`, the dead class.

**Definition 3.4 (language of an invariant).** Let `𝓘 = ⟨𝒜, P⟩` denote an invariant
over `Σ`, and `w = u·v^ω ∈ Σ^ω` a lasso, its loop `v` nonempty. Let `e := ⟦v⟧^ω` be
the idempotent power in `𝒜` of the fold of `v`. Then

```
    w ∈ L(𝓘)   iff   (⟦u⟧·e, e) ∈ P.
```

*Example.* On Figure 1 (`aUGb`), the two verdicts. For `aab·b^ω`: the loop folds to
`⟦b⟧ = [b]`, already idempotent, so `e = [b]`; the stem folds to `⟦aab⟧ = [a·b]` and
`[a·b]·[b] = [a·b]`. The pair `([a·b], [b])` is in `P`: accepted. For `ba·(ab)^ω`:
the loop folds to `⟦ab⟧ = [a·b]`, not idempotent — its square `[b·a]` is — so
`e = [b·a]`; the stem folds to `[b·a]` and `[b·a]·[b·a] = [b·a]`. The pair
`([b·a], [b·a])` is not in `P`: rejected, as §2 announced.

The definition reads `w` through one presentation `(u, v)`, and a lasso has many.
That the verdict does not depend on the presentation chosen is not automatic; it is
the subject of the next section.

### 3.3 Naming lassos, and the rotation lemma

A **linked pair** of the algebra is `(s, e) ∈ 𝒞 × 𝒞` with `e² = e` and `s·e = s`. It
**names** every lasso `u·v^ω` with `⟦u⟧·⟦v⟧^ω = s` and `⟦v⟧^ω = e`. Loops are nonempty,
so both components of a naming pair are folds of nonempty words; since `[ε]` is
adjoined (Definition 3.1) neither is `[ε]`, so a naming pair lies in `(𝒞∖{[ε]})²`. Read as
intuition: no name may accept by staying at the start — a loop is the value of
something that happens forever, and the empty past cannot recur.

*Example.* Six linked pairs: `([a],[a])`, `([b],[b])`, `([a·b],[b])`, `([b·a],[a])`,
`([b·a],[b])`, `([b·a],[b·a])`. The pair `([a],[a])` names `a^ω` and nothing else;
`([b·a],[a])` names the lassos with a `b` somewhere, then `a`'s forever; `([a·b],[b])`
names exactly the lassos with stem in `a⁺b*` and loop in `b⁺`.

One lasso has many presentations, and — this is the subtlety the object must confront —
they need not name it by one pair. Three elementary **moves** relate the presentations of
a common ω-word:

```
    stem-extend   (u, v)      ↦ (uv, v)          [ uv·v^ω = u·v^ω ]
    loop-power    (u, v)      ↦ (u, v^k)  (k≥1)  [ (v^k)^ω = v^ω ]
    loop-rotate   (u, v₁v₂)   ↦ (uv₁, v₂v₁)      [ u(v₁v₂)^ω = uv₁(v₂v₁)^ω ]
```

On the named pair, `loop-power` changes nothing (`(⟦v⟧^k)^ω = ⟦v⟧^ω`, the idempotent
power of a power). The other two move it — and both are instances of one rotation, the
paper's pivot.

*Example.* `a·(ba)^ω ↦ ab·(ab)^ω` is a `loop-rotate`; `ab·(ab)^ω ↦ ab·(abab)^ω` a
`loop-power`. All three presentations fold to the one name `([b·a], [b·a])` — this
example's stems absorb, so its moves happen to fix the name; the lemma below is what
makes verdicts survive the moves that do not.

**Lemma 3.3 (rotation lemma).** For all `s, g, h ∈ 𝒞` with `s·(gh)^ω = s`, the linked
pairs

```
    (s, (gh)^ω)   and   (s·g, (hg)^ω)
```

name the same lassos: every ω-word named by one is named by the other.

*Proof.* By letter-generation pick words `w, p, q` with `⟦w⟧ = s`, `⟦p⟧ = g`, `⟦q⟧ = h`.
The single ω-word `w·(pq)^ω` has the presentation `(w, pq)`, named by
`(⟦w⟧·⟦pq⟧^ω, ⟦pq⟧^ω) = (s·(gh)^ω, (gh)^ω) = (s, (gh)^ω)`; and the presentation
`(wp, qp)` — the same word, since `w(pq)^ω = wp(qp)^ω` — named by
`(⟦wp⟧·⟦qp⟧^ω, ⟦qp⟧^ω) = (s·g·(hg)^ω, (hg)^ω)`. Here `g·(hg)^ω = (gh)^ω·g`, so the stem
is `s·(gh)^ω·g = s·g` (using `s·(gh)^ω = s`), and `(s·g, (hg)^ω)` is a linked pair
(`(hg)^ω` idempotent; `s·g·(hg)^ω = s·(gh)^ω·g = s·g`). Any lasso named by either pair
thus presents, by loop rotation, as one named by the other. ∎

The lemma says a loop may be **rotated** — a factor `g` carried from the loop's front
onto the stem — the loop's idempotent conjugating `(gh)^ω ↦ (hg)^ω` while the stem
absorbs `g`. `stem-extend` is the degenerate case `g = h = ⟦v⟧`: then `(gh)^ω = ⟦v⟧^ω` is
unchanged and the stem merely gains `⟦v⟧`, which is why a longer stem can name the same
lasso by a different pair. `loop-rotate` is the general case. So of the three moves, only
`loop-power` fixes the pair; every other pair-change is one rotation step.

*Example.* The degenerate case on `(a, b) ↦ (ab, b)`: the stem gains `[b]`, which
`[a·b]` absorbs — both presentations carry the name `([a·b], [b])`.

Call two linked pairs **conjugate**, `(s, e) ≈ (s', e')`, when connected by rotations —
the equivalence generated by `(s, (gh)^ω) ≈ (s·g, (hg)^ω)`. Lemma 3.3 says conjugate
pairs name the same lassos, so a recognizer must accept them together.

*Example.* All six conjugacy classes are singletons — every rotation fixes the pair,
the dead class absorbing whatever factor moves. A conjugacy that genuinely pairs two
names is worked in §3.5.

**The rotation lemma is the structural pivot of the paper.** Here it constrains the
acceptance layer (§3.3). In §7, applied not to the loop of a single lasso but to the
two-sided contexts of Arnold's syntactic congruence, the same rotation carries a *left*
context around the loop into a *right* extension at a shifted starting point — collapsing
the two-sided congruence to a right-invariant refinement, computable by the one operation
a monoid's table offers for free. That collapse is the construction's core; it is
Lemma 3.3 read at the level of contexts, and §7 only instantiates it.

### 3.4 The acceptance layer, and well-definedness

**Definition 3.4 (acceptance layer; object).** An **acceptance layer** over an algebra
`𝒜` is a set `P` of linked pairs that is **saturated** — closed under conjugacy:

```
    (s, (gh)^ω) ∈ P  ⟺  (s·g, (hg)^ω) ∈ P     for all s, g, h ∈ 𝒞 with s·(gh)^ω = s.
```

An **object** is a pair `𝓘 = ⟨𝒜, P⟩`: an algebra and an acceptance layer over it. Saturation is a finite, mechanical closure — checkable directly on the
multiplication table, with no automaton and no external theory (§3.5 verifies it by hand
on the examples).

*Example.* `P = { ([b],[b]), ([a·b],[b]) }` — the two behaviors of `a*·b^ω`: "reading
`b`'s after nothing but `a`'s (if any), keep reading `b`'s". Saturation is immediate,
each pair being its own conjugacy class (§3.2). The flip `P^c` — the other four linked
pairs — is an equally legal layer, and denotes the complement (§4).

**The membership query.** Given a lasso `u·v^ω`, the object answers membership by folding
and one lookup:

```
    e := ⟦v⟧^ω,   s := ⟦u⟧·e,   accept  u·v^ω  ⟺  (s, e) ∈ P.
```

`(s, e)` is a linked pair (`e² = e`; `s·e = ⟦u⟧·e·e = s`) — the pair naming `u·v^ω`.

*Example.* Three runs. `b^ω`: the loop `[b]` is already idempotent, the empty stem
gives `s = [ε]·[b] = [b]`; `([b],[b]) ∈ P` — accepted. `aab·b^ω`: `⟦aab⟧ = [a·b]`,
loop `[b]`; `([a·b],[b]) ∈ P` — accepted. `a·(ab)^ω`: `⟦ab⟧ = [a·b]` is *not*
idempotent — the table refuses `ab` as a stable block; iterate to `[a·b]^ω = [b·a]`,
then `s = [a]·[b·a] = [b·a]` and `([b·a],[b·a]) ∉ P` — rejected, the idempotent-power
step visibly doing the work: the loop `ab` keeps producing an `a` after a `b`.

**Lemma 3.5 (well-definedness).** The query's verdict on `u·v^ω` depends only on the
ω-word, not on the presentation `(u, v)`, **iff** `P` is saturated.

*Proof.* (⇐) Two presentations of one ω-word are connected by the three moves
(Lemma 3.6). `loop-power` leaves the named pair, hence the verdict, unchanged;
`stem-extend` and `loop-rotate` change it by one conjugacy step, which preserves
`P`-membership by saturation. The verdict is thus constant along any chain connecting two
presentations. (⇒) Fix `s, g, h` with `s·(gh)^ω = s`; the cases `g = [ε]` or `h = [ε]`
are trivial (both pairs coincide), so take `g, h ≠ [ε]`. Then `s ≠ [ε]` (else
`s = s·(gh)^ω = (gh)^ω`, but `(gh)^ω` is a fold of nonempty words and `[ε]` is
adjoined). Letter-generation realizes `s, g, h` by words, and Lemma 3.3's two
presentations of the one word `w(pq)^ω` carry the pairs `(s, (gh)^ω)` and
`(s·g, (hg)^ω)`. Presentation-independence forces one verdict, i.e. both pairs lie in `P`
or neither. ∎

*Example.* Presentation-independence is immediate here — singleton conjugacy classes;
§3.5's saturation check shows the ⇒ direction biting on a `P` that would answer `a^ω`
two ways.

**Lemma 3.6 (presentations connect).** Two presentations name the same ω-word iff
connected by `stem-extend`, `loop-power`, `loop-rotate` and their inverses.

*Proof.* (⇐) Each move preserves the ω-word (the identities beside the moves). (⇒) Reduce
any `(u, v)` to a canonical presentation of `α := u·v^ω` fixed by `α` alone. Let `π` be
the least eventual period of `α` and `t` its least pre-period (`α` is `π`-periodic from
position `t`, both minimal). As `v^ω` is the tail of `α` from position `|u|`, `v` is a
power of the length-`π` rotation `ρ` of the primitive period beginning at position `|u|`;
`loop-power`⁻¹ takes `v = ρ`. If `|u| > t`, the last letter of `u` lies in the periodic
part and is the letter `ρ` continues with, so `loop-rotate`⁻¹ pulls it into the loop,
lowering `|u|` by one and rotating `ρ`; iterate to `|u| = t`. The result — the length-`t`
prefix of `α` and the period rotated to begin at `t` — depends only on `α`, so any two
presentations reduce to it. ∎

*Example.* `(aab, bb)` reduces: `loop-power`⁻¹ to `(aab, b)`; the stem's last letter
`b` lies in the periodic part, so `loop-rotate`⁻¹ pulls it in, giving `(aa, b)` — the
canonical presentation (`t = 2`, `π = 1`), reached from any presentation of `aab·b^ω`.

By Lemma 3.5 a saturated `P` makes the query a function of the ω-word. Read as a
recognizer, the object accepts exactly the lassos of a unique regular ω-language
`L(𝓘)` — agreement on lassos determining a regular ω-language (§2) — and this is the
language the object denotes.

*Example.* The two accepting names admit exactly the lassos with stem in `a*b*` and
loop in `b⁺` — the lassos of `a*·b^ω`, and no others: `L(𝓘) = L`.

### 3.5 Residuals are derived data

Started at any class, the object answers membership of a residual.

**Proposition 3.7 (residuals).** For `s ∈ 𝒞` set
`L_s := { y·t^ω : (s·⟦y⟧·⟦t⟧^ω, ⟦t⟧^ω) ∈ P }` — the query run from `s` — with
`L_{[ε]} = L(𝓘)`. Then each `L_{s·λ(a)} = a⁻¹L_s`, residual equality is right-invariant
(`L_s = L_{s'} ⟹ L_{s·λ(a)} = L_{s'·λ(a)}`), and the residual automaton is a quotient of
the Cayley graph — all recomputable from `⟨𝒜, P⟩`.

*Proof.* `L_{s·λ(a)} = a⁻¹L_s` is immediate from the fold:
`y·t^ω ∈ L_{s·λ(a)} ⟺ (s·λ(a)·⟦y⟧·⟦t⟧^ω, ⟦t⟧^ω) ∈ P ⟺ (s·⟦a·y⟧·⟦t⟧^ω, ⟦t⟧^ω) ∈ P
⟺ a·y·t^ω ∈ L_s`. Right-invariance follows, so quotienting the Cayley graph (Def 3.2) by
residual equality yields a deterministic, complete letter-graph — the residual
automaton. ∎

*Example.* `L_{[a]} = a⁻¹L = L` (the `a*` absorbs); `L_{[b]} = L_{[a·b]} = {b^ω}`;
`L_{[b·a]} = ∅`. The five-node Cayley graph quotients to a three-state residual
automaton — `{[ε],[a]}`, `{[b],[a·b]}`, `{[b·a]}` — strictly coarser than the algebra:
the residuals cannot tell `[b]` from `[a·b]`, the two-sided congruence can.

No congruence and no automaton is invoked. The residuals are derived data and rightly
enter no equality test between objects (§5).

### 3.6 Concrete form, read on the examples

Recall the three running examples (introduced fully in §1): **`GF(aa)`** — infinitely
many `aa`-factors, LTL-definable; **`Even`** — an even number of `a`'s before the first
`b`, then anything, *not* LTL; **`EvenBlocks`** — infinitely many `b` and eventually
every completed `a`-block even, *not* LTL and prefix-independent. Each is met here as
its algebra — the letter actions, the few laws that organize them, and the Cayley
graph drawn; automata wait until §6, the machine formats (serialization, integer
tables) until Part B. In all
three, `λ(a) = [a]` and `λ(b) = [b]`, and letter-generation makes the two action rows
the whole of `M`.

**(a) `GF(aa)`** — six classes:

```
 ·a :  [ε]↦[a]    [a]↦[a·a]   [b]↦[b·a]   [a·b]↦[a]     [b·a]↦[a·a]   [a·a]↦[a·a]
 ·b :  [ε]↦[b]    [a]↦[a·b]   [b]↦[b]     [a·b]↦[a·b]   [b·a]↦[b]     [a·a]↦[a·a]
```

Laws: `[a·a]` — "has seen `aa`" — is a two-sided **zero**
(`x·[a·a] = [a·a]·x = [a·a]`); every power cycle has period 1 — aperiodic, the LTL
side of the cut; the idempotents are `[b]`, `[a·b]`, `[b·a]`, `[a·a]`, with
`[a]^ω = [a·a]`. One accepting pair, `P = { ([a·a],[a·a]) }`: hit the zero and loop
there — `aa` recurs.

![Figure 2 — the object of GF(aa)](sos_core_figs/img/core_F1_gf_aa.png)

*Figure 2 — `GF(aa)`. Two waiting rooms — `[a] ⇄ [a·b]` and `[b] ⇄ [b·a]`, cycles
that mix letters, hence no group — each escaping on `a` toward the zero; the one
accepting name loops at the zero itself.*

**(b) `Even`** — five classes:

```
 ·a :  [ε]↦[a]    [a]↦[a·a]   [b]↦[b]     [a·b]↦[a·b]   [a·a]↦[a]
 ·b :  [ε]↦[b]    [a]↦[a·b]   [b]↦[b]     [a·b]↦[a·b]   [a·a]↦[b]
```

Laws: `{[a], [a·a]}` is a **period-2 cycle** (`[a]·[a] = [a·a]`, `[a·a]·[a] = [a]`) — a
`Z₂` in the algebra, visible in the `·a` row as the swap `[a] ↔ [a·a]`. `[a·a]` acts as
the **identity** on the four word classes: the algebra owns a second neutral element,
and the adjoined identity of §3.1 keeps `[ε]` apart. `[b]` and `[a·b]` are
**left zeros**, fixed by both letters: the first `b` has been read, after an even
(`[b]`) or odd (`[a·b]`) count of `a`'s. Accepting pairs `([b],[b])`, `([b],[a·a])`,
`([b],[a·b])`: once `[b]` is reached, every loop accepts.

![Figure 3 — the object of Even](sos_core_figs/img/core_F2_even.png)

*Figure 3 — `Even`. The diagonal `[a] ⇄ [a·a]`, both legs on the single letter
`a`, is a monochrome two-cycle — the `Z₂` drawn; every accepting name stems at
`[b]`.*

**(c) `EvenBlocks`** — eight classes:

```
 ·a :  [ε]↦[a]       [a]↦[a·a]    [b]↦[b·a]        [a·b]↦[a·b·a]
       [b·a]↦[b]     [a·a]↦[a]    [a·b·a]↦[a·b]    [b·a·b]↦[b·a·b]
 ·b :  [ε]↦[b]       [a]↦[a·b]    [b]↦[b]          [a·b]↦[a·b]
       [b·a]↦[b·a·b] [a·a]↦[b]    [a·b·a]↦[b·a·b]  [b·a·b]↦[b·a·b]
```

Laws: the *same* `Z₂` `{[a], [a·a]}` returns, and `[a·a]` is again neutral on the word
classes; `[b·a·b]` — a completed odd block — is the two-sided **zero**. Unlike
`aUGb`'s dead class, this zero is no death sentence: the language forgives finitely
many odd blocks, and the acceptance layer says so — of the six accepting pairs

```
P = { ([b],[b]),  ([a·b],[b]),  ([b·a],[a·b·a]),
      ([a·b·a],[a·b·a]),  ([b·a·b],[b]),  ([b·a·b],[a·b·a]) }
```

two sit at the zero itself: what has happened is absorbed; what loops forever decides.

![Figure 4 — the object of EvenBlocks](sos_core_figs/img/core_F3_evenblocks.png)

*Figure 4 — `EvenBlocks`. The same `Z₂` acting as three `·a` swaps — one per
phase of the language — and two accepting names sitting at the zero.*

---

**Reading the object by hand.** Three checks, all on the letter actions above and none
touching an automaton.

*Membership by one fold.* Is `(a·a)^ω ∈ Even`? Fold the loop: `[ε] ↦ [a] ↦ [a·a]`,
already idempotent; the empty stem gives `s = [ε]·[a·a] = [a·a]`. The pair
`([a·a], [a·a])` is not among `Even`'s accepting pairs, so it is rejected — correctly,
`(aa)^ω` never sees a `b`.

*The group is on the table.* In `Even`, `[a]·[a] = [a·a]` and `[a·a]·[a] = [a]`: the
pair `{[a], [a·a]}` is a cycle of period 2, a `Z₂` sitting in the algebra. Since (as §5
makes exact) aperiodicity of the algebra is LTL-definability, this cycle *is* the
reason `Even` is not LTL — read straight off the letter actions, before any acceptance
is consulted. `GF(aa)`'s algebra, by contrast, has every power-cycle of period 1:
aperiodic, hence LTL. In the drawing the criterion is a *monochrome* cycle — one
letter (more generally one word) repeated, as `Even`'s `·a` swap between `[a]` and
`[a·a]` (Figure 3). A cycle that mixes letters proves nothing: `GF(aa)`'s graph
closes `[a] →^b [a·b] →^a [a]` (Figure 2's waiting rooms), and its algebra is
aperiodic all the same.

*Saturation, checked.* The query on `a^ω` presented two ways must agree, and does:
`(ε, a)` folds to the pair `([ε]·[a]^ω, [a]^ω) = ([a·a], [a·a])`, while `(a, a)` folds
to `([a]·[a·a], [a·a]) = ([a], [a·a])` — a conjugacy step
`(s, (gh)^ω) ≈ (s·g, (hg)^ω)` with `s = g = h = [a]`. Both pairs are absent from
`Even`'s accepting set, as saturation (Definition 3.4) demands; a `P` containing one
but not the other would be an *illegal* acceptance layer, its query self-contradictory
on the single word `a^ω`.

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
- The syntactic object: the quotient by Arnold's congruence, keyed shortlex, is a
  well-formed `⟨𝒜, P⟩` and a function of `L` alone.
- Complete invariant theorem (current Thm 5.1): two languages are equal iff their
  objects are byte-equal.
- Two minimality senses, both exact: coarsest congruence saturating `L` (Arnold);
  unique canonical complete invariant. (Minimal-recognizer claim dropped.)
- The two shapes double as the specification the construction must meet — hand-off
  to Part B.

## 6. The construction, I: seeing acceptance

We now construct the invariant. The input is an automaton for `L`; the output is an
invariant `𝓘(D) = ⟨𝒜(D), P(D)⟩`; the destination of this section and the next is the
correctness theorem — `L(𝓘(D)) = L(D)` (Theorem 7.5) — proved with §3's semantics
and two automaton lemmas, nothing else. That the result is moreover canonical — one
invariant per language, whatever `D` presented it — is deferred to §8.

**The input.** A **deterministic, complete Emerson–Lei automaton** over `Σ` is
`D = (Q, ι, δ, C, Acc)`: a finite set `Q` of **states** with an **initial** `ι ∈ Q`;
a total **transition function** `δ : Q × Σ → Q`, each transition carrying a (possibly
empty) subset of a finite set `C` of **marks**; and an **acceptance condition**
`Acc`, a positive Boolean combination of atoms `Inf(c)`, `Fin(c)` for `c ∈ C`. An
ω-word `α = x₀x₁⋯` traces the unique infinite **run** `q₀ = ι`,
`q_{i+1} = δ(q_i, x_i)` — one successor per letter, a successor for every letter, so
exactly one run, never stalling. `Acc` is evaluated on the set of marks the run
collects infinitely often — `Inf(c)` true iff `c` recurs, `Fin(c)` iff it does not —
and `L(D)` is the set of ω-words whose run satisfies `Acc`. Emerson–Lei acceptance is
the most general ω-regular acceptance (Büchi, co-Büchi, Rabin, Muller are special
shapes), and every regular `L` is `L(D)` for some such `D` [Saf88]. For `q ∈ Q`, the
**residual** `L(q) := { α : the run from q on α satisfies Acc }` is what `D` would
accept started at `q`; determinism gives `L(δ(ι, u)) = u⁻¹L(D)` for every finite
`u`. We write `Reach := δ(ι, Σ*)` for the states some finite word reaches.

*Example.* `aUGb` is `L(D)` for a three-state `D`: state `A` (initial) loops on
`a`; `b` leads to `B`, which loops on `b`, that loop carrying the single mark `c`; an
`a` at `B` falls to the sink `Z`, which absorbs both letters unmarked.
`Acc = Inf(c)`: a run collects `c` forever iff it eventually reads only `b`'s.

**The obstruction.** The classical algebra of `D` on finite words is its transition
monoid, the maps `q ↦ δ(q, w)`. It forgets the marks a run collects — exactly the
data `Acc` consumes. So we enrich it.

**Definition 6.1 (enriched monoid).** For `w ∈ Σ*`, the **enriched element** `⟨w⟩`
records, at each state, where `w` leads and what it collects:

```
    ⟨w⟩ : q ↦ ( δ(q, w), mk(q, w) ),
```

`mk(q, w) ⊆ C` the marks on the run from `q` over `w`. `EM(D)` is the set of
enriched elements under the composition `⟨w⟩·⟨w'⟩ = ⟨w·w'⟩` — at `q`: reach
`δ(q, w)`, continue by `w'`, unite the marks — a finite monoid generated by the
letter elements `⟨x⟩`, with identity `⟨ε⟩ : q ↦ (q, ∅)`. We write `st_e(q)`,
`mk_e(q)` for the two components of `e ∈ EM(D)` at `q`. (The brackets `⟨·⟩` leave
`⟦·⟧` to §3's fold.)

*Example.* On the two-state presentation of `GF(aa)` — state `1` after an odd run of
`a`'s, the `a` leaving `1` closes an `aa` and carries the mark `c`, `b` resets to `0`
unmarked, `Acc = Inf(c)` — the elements `⟨a⟩` and `⟨aaa⟩` have the *same* state
part, the transposition of `{0, 1}`, and differ only in marks: `mk_{⟨aaa⟩}(0) = {c}`
(the longer word closes an `aa`), `mk_{⟨a⟩}(0) = ∅`. The transition monoid
identifies them; the enrichment is what keeps them apart.

**Lemma 6.2 (skeleton).** If two ω-words factor into blocks with the same sequence
of enriched images — `α = w₁w₂⋯`, `β = w'₁w'₂⋯` with `⟨w₁⋯w_k⟩ = ⟨w'₁⋯w'_k⟩` for
every `k` — then `α ∈ L(D) ⟺ β ∈ L(D)`.

*Proof.* Determinism gives each word one run. Equality of the prefix images puts
both runs at the same state `p_k = st_{⟨w₁⋯w_k⟩}(ι)` at every block boundary, and
equality of the images with the composition law makes the marks collected inside
block `k` equal on both sides: `mk(p_{k-1}, w_k) = mk(p_{k-1}, w'_k)`. The two runs
thus collect the same marks per block, hence the same set of marks infinitely often
— and `Acc` is a function of that set alone. ∎

**Proposition 6.3 (enrichment is necessary).** No quotient of the transition monoid
can serve, in general, as the algebra of an invariant denoting `L(D)`.

*Proof (a one-state witness).* Let `D` have one state `p`, both letters of
`Σ = {a, b}` self-looping, the mark `c` on the `a`-loop only, `Acc = Inf(c)`:
`L(D)` is "infinitely many `a`'s". The transition monoid is trivial — every word is
the identity map on `{p}` — so in any algebra built on it the folds of `a` and `b`
coincide, the queries of `a^ω` and `b^ω` coincide (Definition 3.4), and the two
receive one verdict. But `a^ω ∈ L(D)` and `b^ω ∉ L(D)`. The enriched elements do
separate them: `mk_{⟨a⟩}(p) = {c} ≠ ∅ = mk_{⟨b⟩}(p)`. ∎

The starkness is the message: a trivial transition monoid under a nontrivial
language. No state bookkeeping recovers acceptance — the marks along the run are
irreducible data, and the enrichment is the smallest way to keep them. It is also
why a group in a transition monoid proves nothing about `L`: it can be pure
encoding, invisible to the marks. `GF(aa)`'s transposition above is exactly that
situation, resolved in §7.

Conversely, `EM(D)` classifies too finely. On the `aUGb` automaton above,
`⟨ba⟩` and `⟨aba⟩` are distinct elements (`mk_{⟨ba⟩}(B) = {c}` while
`mk_{⟨aba⟩}(B) = ∅`) though no context whatsoever separates the words `ba` and
`aba`: both are dead. The next section quotients exactly this excess away.

## 7. The construction, II: the rotation lemma

What remains is a quotient: merge elements of `EM(D)` exactly when the words they
image are interchangeable — in every stem, in every loop — and read `P` off the
result. Interchangeability is a two-sided demand: a word sits in a lasso between a
left context and a right one. A monoid's table, meanwhile, offers one operation for
free: multiply on the right. The gap is closed by the rotation lemma — §3's rotation
read on runs: a left factor carries no information of its own; it only shifts the
slot where a right test is read.

**Lemma 7.1 (collapse).** For `x, c ∈ EM(D)`, `c` the image of a nonempty word, all
lassos `w·z^ω` with `⟨w⟩ = x` and `⟨z⟩ = c` share one verdict (Lemma 6.2), written
`Acc(x, c)`; and it depends on `x` only through the single state the stem reaches:

```
    Acc(x, c) = A(st_x(ι), c),
```

where the **loop verdict** `A(q, c)` iterates `c` from `q`: follow `st_c` from `q`
into its closed cycle, unite the marks `mk_c` around that cycle, evaluate `Acc`.

*Proof.* The stem is read once; its marks are collected finitely often and none
recurs. The set of marks recurring in `w·z^ω` is therefore that of the tail `z^ω`
read from `st_x(ι)`: the iteration of `st_c` from there eventually closes a cycle,
the marks `mk_c` around that cycle recur, and no other mark does. ∎

**Definition 7.2 (the two right relations).** For `e, f ∈ EM(D)` images of nonempty
words, with `Aprof(c) := (q ∈ Reach ↦ A(q, c))` the **profile** of `c`:

```
    e ~lin f   ⟺   ∀ q ∈ Reach :   L(st_e(q)) = L(st_f(q)) ;
    e ~ω  f    ⟺   ∀ b ∈ EM(D) :   Aprof(e·b) = Aprof(f·b) ;
```

and `~ := ~lin ∧ ~ω`. The slots are `Reach`, not `Q`: an unreachable state names no
context. The extension `b` ranges over all of `EM(D)`, identity included — `b = ⟨ε⟩`
tests the bare loop `e` itself, and `e·b` is always the image of a nonempty word.

`~lin` compares the futures the words open — residual languages of reached states —
and never looks at marks; `~ω` compares the loops the words can close, under every
right completion. Neither mentions a left context.

*Example (the two relations divide the labor).* `EvenBlocks` is `L(D)` for a
two-state `D` tracking the parity of the running block of `a`'s: `a` toggles the
state; `b` returns to the even state, marked `1` when the block it closes is even,
`0` when it is odd; `Acc = Fin(0) ∧ Inf(1)`. Here `⟨aa⟩ = ⟨ε⟩` — two `a`'s toggle
back, collecting nothing. `~lin` is total: the language is prefix-independent, both
states accept exactly `EvenBlocks`. The separation of `⟨a⟩` from `⟨aa⟩` is carried
entirely by `~ω`, with the block-closing extension `b = ⟨b⟩`:
`Aprof(⟨a⟩·⟨b⟩) = Aprof(⟨ab⟩)` rejects at both slots — the loop `ab` closes an odd
block forever, violating `Fin(0)` — while `Aprof(⟨aa⟩·⟨b⟩)` accepts at both —
`(aab)^ω` closes even blocks forever.

**Lemma 7.3 (rotation).** A left factor acts on both relations only by re-indexing
the slot: for all `a, e, b ∈ EM(D)` and `q ∈ Reach`,

```
    st_{a·e}(q) = st_e(st_a(q))        and        Aprof(a·e·b)(q) = Aprof(e·b·a)(st_a(q)).
```

Consequently, with `R` the equivalence "same `~lin`-class and same profile `Aprof`",
the relation `~` is the coarsest right-invariant equivalence refining `R`, and it is
a two-sided congruence on `EM(D)`.

*Proof.* The state identity is composition of maps. For the profile identity, read
the loop `(a·e·b)^ω` from `q` as `a·(e·b·a)^ω` — one rotation, §3's move: the factor
`a` is carried from the loop's front onto the stem. That prefix is read once, its
marks recur never, so the verdict is the loop verdict of `e·b·a` from the state the
prefix reaches (Lemma 7.1): `Aprof(a·e·b)(q) = A(st_a(q), e·b·a) =
Aprof(e·b·a)(st_a(q))`.

*Right-invariance.* Both halves of the seed survive a right factor: residual
equality steps through letters (`L(p) = L(p')` gives
`L(δ(p, x)) = x⁻¹L(p) = x⁻¹L(p') = L(δ(p', x))`), so `e ~lin f` gives
`e·c ~lin f·c`; and `Aprof(e·c·b) = Aprof(f·c·b)` is an instance of `e ~ω f`. Hence
`~` is right-invariant.

*Coarsest.* Suppose `e·b R f·b` for every `b`: the profile half over all `b` is
`e ~ω f`, and the `~lin` half at `b = ⟨ε⟩` is `e ~lin f` — so `e ~ f`. Conversely
`e ~ f` gives `e·b ~ f·b` (right-invariance), hence `e·b R f·b` for every `b`. So
`~` is exactly "R-equal under every right extension": the coarsest right-invariant
equivalence refining `R`.

*Two-sided.* For a left factor `a`: `a·e ~lin a·f` since
`st_{a·e}(q) = st_e(st_a(q))` and `st_a(q) ∈ Reach`; and
`Aprof(a·e·b)(q) = Aprof(e·(b·a))(st_a(q)) = Aprof(f·(b·a))(st_a(q)) =
Aprof(a·f·b)(q)` — the left factor became a right extension. With right-invariance,
`~` is a two-sided congruence. ∎

The lemma is the load-bearing step. Maler and Staiger [MS97] display the finitary ×
infinitary split — at the single slot `ι`, `~lin` is their classical right
congruence — but their two-sided quantification stays inside the loop test; Carton,
Perrin and Pin [CPP08] saturate over context triples. The conjugation
`a·e·b ↦ e·b·a` — the same rotation §3 applies to the pairs naming a lasso, applied
here to contexts — is the step neither takes, and it is what makes a two-sided
congruence computable with the one operation a monoid's table offers for free. Two
remarks we can back: the right-extension-at-slots discipline is an
observation-table discipline, answering the obstruction Angluin and Fisman record
for ω-learning [AF21]; and a coarsest right-invariant refinement is precisely what
partition refinement — or its symbolic implementation — computes (§8).

**Definition 7.4 (the constructed invariant).** `𝓘(D) := ⟨𝒜(D), P(D)⟩`:

- `𝒞`: the `~`-classes of images of nonempty words, plus the adjoined `[ε]`; each
  word class is represented by the shortlex-smallest word whose enriched image lies
  in it (the convention of §3.1);
- `λ`: `λ(x) :=` the class of `⟨x⟩` for `x ∈ Σ`, and `λ(ε) = [ε]`;
- `M`: the induced product on word classes — well-defined since `~` is a two-sided
  congruence (Lemma 7.3), closed since nonempty words concatenate to nonempty words
  — with `[ε]` the identity by definition;
- `P(D)`: for each pair `(s, e)` of word classes with `e·e = e` and `s·e = s`, test
  the single lasso `w_s·(w_e)^ω` on `D`, `w_s` and `w_e` the representatives; put
  `(s, e)` in `P(D)` iff it is accepted.

`𝒜(D)` is an algebra in the sense of Definition 3.1 — `[ε]` is isolated: no letter
maps to it, and a product of word classes is a word class. The fold of a nonempty
word unwinds to its `~`-class, `⟦w⟧ = [⟨w⟩]` (Definition 3.3 composes the letter
classes, and `~` is a congruence); in particular every representative folds to its
own class.

**Theorem 7.5 (correctness).** `𝓘(D)` is a well-formed invariant — `P(D)` is
saturated, so the semantics of Definition 3.4 is presentation-independent — and

```
    L(𝓘(D)) = L(D).
```

*Proof.* **Step 1: every query returns `D`'s verdict.** Let `u·v^ω` be a lasso, `v`
nonempty. Definition 3.4 queries `e := ⟦v⟧^ω` and `s := ⟦u⟧·e`. Choose `k ≥ 1` with
`⟦v⟧^k = e` (the idempotent power is a power); folding is compatible with
concatenation (§3.2), so `e = ⟦v^k⟧ = [⟨v^k⟩]` and `s = ⟦u·v^k⟧ = [⟨u·v^k⟩]`.
Rewrite the ω-word on this presentation: `u·v^ω = (u·v^k)·(v^k)^ω`.

*Stem swap.* `⟨u·v^k⟩ ~ ⟨w_s⟩` — both lie in `s` — so in particular `~lin` at the
slot `ι`: the states `st_{⟨u·v^k⟩}(ι)` and `st_{⟨w_s⟩}(ι)` have equal residuals, so
the two stems open the same futures and
`u·v^ω = (u·v^k)·(v^k)^ω ∈ L(D) ⟺ w_s·(v^k)^ω ∈ L(D)`.

*Loop swap.* `⟨v^k⟩ ~ ⟨w_e⟩` — both lie in `e` — so in particular `~ω` at the empty
extension: `Aprof(⟨v^k⟩) = Aprof(⟨w_e⟩)`. With `q := st_{⟨w_s⟩}(ι) ∈ Reach`, the
collapse (Lemma 7.1) turns both memberships into loop verdicts at `q`:
`w_s·(v^k)^ω ∈ L(D) ⟺ A(q, ⟨v^k⟩) = A(q, ⟨w_e⟩) ⟺ w_s·(w_e)^ω ∈ L(D)`.

Chaining: `u·v^ω ∈ L(D) ⟺ w_s·(w_e)^ω ∈ L(D) ⟺ (s, e) ∈ P(D)`, the last step by
definition of `P(D)`. The right-hand side is exactly Definition 3.4's verdict on
`u·v^ω`: every presentation of every lasso receives from `𝓘(D)` the verdict of
`L(D)`.

**Step 2: well-formedness.** By Step 1 the verdict on a presentation `(u, v)`
equals membership of the ω-word `u·v^ω` in `L(D)` — a function of the ω-word alone.
The semantics is presentation-independent, so by the well-definedness lemma of §3.4
(Lemma 3.5, forward direction), `P(D)` is saturated.

**Step 3: the language.** `𝓘(D)` and `D` accept the same lassos (Step 1); two
regular ω-languages agreeing on all lassos are equal (§2), and `L(𝓘(D))` is the
regular language its lasso verdicts pin (§3.2). Hence `L(𝓘(D)) = L(D)`. ∎

The theorem is deliberately self-contained: no syntactic congruence, no Arnold —
the two automaton lemmas (skeleton and collapse) and §3's semantics carry it. What
it does *not* say is that `𝓘(D)` is independent of the presentation `D`; that is
canonicity, Theorem B of §8, and it is where Arnold's congruence enters. §8 also
turns Lemma 7.3 into the algorithm: the coarsest right-invariant refinement of the
seed is computed by partition refinement, and `P(D)` by one lasso test per
candidate pair.

## 8. The algorithm and the two theorems

- Moore partition refinement from the seed `R = (~lin-class, Aprof)`, split by right
  letters to fixpoint (current Thm 4.5's procedure).
- Reading `P` off `D`: test one shortlex lasso per candidate linked pair.
- NEW — Theorem A (correctness, self-contained): `𝓘(D)` is well-formed (saturation
  proved, not assumed) and `L(𝓘(D)) = L(D)`; proof from the skeleton lemma and the
  collapse only, no Arnold.
- Theorem B (canonicity): `𝓘(D)` is the syntactic object of §5 — the constructed
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
  supplied, and `⟨𝒜, P⟩` is the deliverable.
- The rotation lemma stands on its own as the mathematical core.
- The family builds on `⟨𝒜, P⟩`: companions consume the object this paper defines
  and constructs.

---

## Not transferred (parked, decide later)

- Current §6 (finite-word specialization, LTLf) — at most a one-line degeneration
  remark somewhere in Part B if we want the sanity check.
- Current §7 use-case development beyond the §4 teaser — lives in the companion papers.
- No prospects beyond material we have (no prophetic extraction, no learning-paper
  promises beyond the two factual template remarks in §7).
