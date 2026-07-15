## 2. Background

We fix a finite alphabet `Σ` and write `Σ*` for the finite words over it, `Σ⁺`
for the nonempty ones, `Σ^ω` for the infinite ones. The same exponents serve
on letters and words: for `x ∈ Σ`, `x*` — finitely many repetitions of `x`,
possibly none; `x⁺` — at least one; `x^ω` — repeated forever. A **language**
here is a set of infinite words, `L ⊆ Σ^ω`; we take `L` **regular**
(ω-regular [PP04]) — the class with finite-memory descriptions, and exactly
the class the invariant of §3 captures. All examples in this paper live over
the two-letter alphabet `Σ = {a, b}`. This section fixes the few classical
notions the invariant rests on, adapting the presentation of Perrin and Pin
[PP04], each paired with the intuition tying the algebra back to languages of
infinite words. Nothing here is assumed and nothing is deep: each notion, once
unwrapped, is algebra on a finite set.

Consider the language of Carton and Perrin [CP97, Ex. 10] described by
`a*·b^ω` — some `a`'s, then `b`'s forever — which we name `aUGb`. It
accompanies every notion of this section, each computed on it by hand; §3
assembles the results into one drawn object, its syntactic ω-semigroup
(Figure 1).

**We only ever look at lassos.** The infinite words this paper computes with
are the ultimately periodic ones, and they have a finite syntax:

**Definition 2.1 (presentation; lasso).** A **presentation** is a pair
`(u, v) ∈ Σ* × Σ⁺`: a finite **stem** `u`, possibly empty, and a finite
nonempty **loop** `v`. It presents the infinite word `u·v^ω` — the stem, then
the loop repeated forever. A **lasso** (ultimately-periodic word) is an
infinite word `w ∈ Σ^ω` admitting a presentation, `w = u·v^ω`.

The organizing fact: *two regular ω-languages are equal iff they agree on all
lassos* [PP04, Ch. I, Cor. 9.8]. Classifying `L` is therefore assigning each
lasso to one of finitely many equivalence classes, and every notion below is
machinery for naming the classes and computing the assignment.

*Example.* `b^ω`, `ab·b^ω` and `aab·(bb)^ω` are lassos of `aUGb`; `ba·(ab)^ω`
is a lasso outside it.

**On finite words, the classifier is a finite monoid.** A **monoid** is a set
with an associative product and an identity element — nothing more. The finite
words `Σ*` form one, under concatenation, with the empty word as identity; the
monoids of interest below are *finite*, and everything done with them is done
on their multiplication table. A finite monoid `M` **recognizes** a language
of finite words through a **morphism** `φ : Σ* → M` — a map carrying
concatenation to the product, `φ(u·v) = φ(u)·φ(v)`, and `ε` to the identity —
such that membership depends only on the value: the language is `φ⁻¹(P)` for
an accepting set `P ⊆ M`. The finitely many elements of `M` are the classes,
and `φ` computes the assignment, letter by letter. Every regular language of
finite words is recognized by a finite monoid, and among its recognizers one
is canonical, the **syntactic monoid** — the cornerstone of algebraic language
theory [PP04].

*Example.* For `aUGb`, watch what a finite word can still become, and what it
becomes when repeated forever. Every nonempty word falls into one of four
kinds:

* the words of `a⁺` — nothing committed: still the prefix of accepted
  ω-words, and more `a`'s change nothing;
* the words of `a⁺b⁺` — committed: still the prefix of accepted ω-words, but
  only of those continuing with `b`'s forever — one more `a` is fatal;
* the words of `b⁺` — these lead nowhere new: an accepted future never
  leaves the kind, and it is the only kind whose infinite repetition is
  accepted, `b^ω ∈ aUGb`;
* the dead words `a*b⁺a(a|b)*` — an `a` after a `b`: the prefix of no
  accepted ω-word, and no ω-power rescues them.

Concatenation never leaves the kinds — `a⁺·a⁺ ⊆ a⁺`, `a⁺·b⁺ ⊆ a⁺b⁺`,
`b⁺·a⁺` is dead, and dead absorbs everything — so, with the empty word as a
fifth value, gluing words reduces to a five-entry multiplication table: the
classifier announced, computed by hand, no automaton consulted.

On *infinite* words, exactly one thing more is needed, because no product of
finite pieces expresses `v^ω`. One adjustment first: the empty word is the
single finite word that cannot be repeated forever — `ε^ω` is not an ω-word —
so the infinite theory is built on the nonempty words `Σ⁺`, a **semigroup**:
the associative product alone, no identity required — a monoid with one axiom
dropped. On `Σ⁺` and `Σ^ω` together, the words carry three total operations:

* **concatenation** `Σ⁺ × Σ⁺ → Σ⁺` of two finite words;
* the **mixed product** `Σ⁺ × Σ^ω → Σ^ω` — a finite word prefixed to an
  ω-word, concatenation continued;
* the **ω-power** `Σ⁺ → Σ^ω`, `v ↦ v^ω` — the new operation, repetition
  forever.

An **ω-semigroup** `S = (S₊, S_ω)` is a finite structure with the same
signature, one **sort** per kind of word [PP04, Ch. II]: a finite semigroup
`S₊` carries the classes of nonempty finite words, a finite set `S_ω` carries
the classes of ω-words; the three operations become a product
`S₊ × S₊ → S₊`, a mixed product `S₊ × S_ω → S_ω`, and an ω-power `S₊ → S_ω`.
The general definition equips the pair with an *infinite product*
`S₊^ω → S_ω` — one class for every infinite sequence of finite classes
[PP04, Ch. II]; on finite carriers the ω-power determines it entirely
[PP04, Ch. II, Thm 5.1], and the table-sized signature above is the form
recalled here. A **recognizer** for `L` is an ω-semigroup with a morphism
`φ = (φ₊, φ_ω)`, one component per sort — `φ₊ : Σ⁺ → S₊`,
`φ_ω : Σ^ω → S_ω` — carrying each operation to its counterpart,

`φ₊(u·v) = φ₊(u)·φ₊(v)`,   `φ_ω(u·w) = φ₊(u)·φ_ω(w)`,   `φ_ω(v^ω) = φ₊(v)^ω`,

such that membership depends only on the class: `L = φ_ω⁻¹(P)` for a set
`P ⊆ S_ω` of accepting ω-classes. Every regular `L` has a finite recognizer
[PP04, Ch. II, §7]. The organizing claim is now explicit: two lassos with the
same ω-class receive one verdict, and there are at most `|S_ω|` classes of
lassos.

**The second sort will not be carried.** Everything `S_ω` records about a
lasso is determined inside `S₊` by the classes of its stem and of its loop —
the idempotent power and the linked pair below are that determination made
exact [PP04, Ch. II, Thm 5.1]. §3 therefore keeps one carrier — a finite
semigroup of classes of nonempty words, with a fresh identity adjoined for the
computations (§3.1) — and replaces `P` by a set of accepting *pairs* of word
classes.

*Example.* The four kinds of `aUGb` already have this one-sorted shape: they
classify nonempty finite words only, and the acceptance data will be pairs of
kinds — stem, loop — with no class of ω-words anywhere.

**The idempotent power.** In a finite semigroup the powers `c, c², c³, …` of
any element cannot all be distinct, so the sequence is eventually periodic and
contains a unique **idempotent**, the one power `cⁿ` (`n ≥ 1`) with
`cⁿ·cⁿ = cⁿ`: the **idempotent power** of `c`. Now read a loop `v` through the
morphism's finite-word component, simply `φ` from here on: the values of
`v, vv, vvv, …` are the powers of `φ(v)`, so they settle on the idempotent
power of `φ(v)`. That is how "loop forever" is read without any infinite
object at hand: iterate the loop's value until it stops changing, and keep
that stable value.

*Example.* For `aUGb`, the value `φ(b)` — the kind `b⁺` — is its own
idempotent power: more `b`'s change nothing, `b⁺·b⁺ ⊆ b⁺`. The value `φ(ab)`
— the kind `a⁺b⁺` — is not: its square is the dead kind (`abab` puts an `a`
after a `b`, and no continuation rescues that), itself idempotent — so the
idempotent power of `φ(ab)` is the dead kind: looping `ab` forever is exactly
as dead as slipping once.

**A linked pair names a lasso.** Reading `u·v^ω` through the morphism `φ`
(Ramsey's theorem [PP04, Ch. II, Thm 2.1]): the loop settles on an idempotent
`e` — the idempotent power of `φ(v)` — and the stem on `s = φ(u)·e`, with
`s·e = s` (the stem precedes the loop and is absorbed by it). A **linked
pair** is any `(s, e)` with `e² = e` and `s·e = s`; `s` names the stem, `e`
the loop, `(s, e)` the lasso. A recognizer is fixed by which lassos it
accepts, hence by its set of **accepting linked pairs** — which is why (§3)
the acceptance datum of the invariant is a *set of pairs*, not a subset of the
carrier.

*Example.* Read `aab·b^ω` by hand: the loop's value `φ(b)` — the kind `b⁺` —
is already idempotent, so `e = φ(b)`; the stem's value `φ(aab)` is the kind
`a⁺b⁺`, which the loop absorbs — `a⁺b⁺·b⁺ ⊆ a⁺b⁺` — so `s = φ(aab)`. The
pair `(a⁺b⁺, b⁺)` names the lasso — as it does every lasso with stem in
`a⁺b*` and loop in `b⁺`. And the accepting pairs of `aUGb` read off the four
roles — accepted means eventually only `b`'s: `(b⁺, b⁺)` and `(a⁺b⁺, b⁺)`,
nothing else.

**One lasso, many names.** A single ω-word has many presentations —
`u·v^ω = (uv)·v^ω = u·(v²)^ω = (u·v₁)·(v₂·v₁)^ω` for any split `v = v₁·v₂` —
and, as §3 shows, these need not name it by the same linked pair. Reconciling
them is not bookkeeping: it is the **rotation lemma** (§3), the paper's
structural pivot, and the one nontrivial constraint the invariant must
satisfy.

*Example.* `a·(ba)^ω = ab·(ab)^ω = ab·(abab)^ω`: one ω-word, three
presentations — and infinitely many more. §3 shows how to canonically choose
a single one, and gives it: shortest stem, then shortest loop — here `(ab)^ω`
with the empty stem, the shortlex representative of the whole family.

We now present a canonical representation of an arbitrary regular ω-language
`L`, using its syntactic ω-semigroup reified as an invariant `𝓘(L)`.
