<!-- ASSEMBLED by research_notes/sos_core/Makefile — do not edit here; edit the parts in sos_core/ and re-run make. -->

# Materializing the Syntactic ω-Semigroup: a Canonical Representation of Regular ω-Languages

**Yann Thierry-Mieg**

With significant inputs from
**Claude (Anthropic)**

*Working draft — 2026-07-16*

## Abstract

The syntactic ω-semigroup of a regular ω-language is its canonical algebra:
presentation-independent and complete — it determines membership, equality,
and every definability property of the language. Defined by Arnold in 1985,
it has, to our knowledge, never been built from an automaton. We build it,
and we reify it: the invariant `𝓘(L) = ⟨𝒮, P⟩` — a stamp `𝒮 : Σ⁺ → 𝒞`
classifying the finite words by a finite table, and an acceptance layer `P`
of linked pairs over it — equipped with a standalone lasso-membership
semantics. This is a canonical normal form for regular ω-languages, which
the domain has never had: under shortlex naming, two languages are equal iff
their serialized invariants are byte-identical. The mathematical core is a
rotation lemma: Arnold's two-sided syntactic congruence is computable by
right multiplications alone — the structural fact missing from forty years
of literature between the definition and a construction. On it we build
`𝓘(D)` from any deterministic Emerson–Lei automaton `D` — an
acceptance-enriched stamp, then a right-computable quotient — and prove
`𝓘(D) = 𝓘(L(D))` against the semantics: one language, one table, whatever
the presentation. LTL-definability, the safety–progress rung, and the
weakest deterministic acceptance become read-offs of the invariant.

## 1. Introduction

On finite words, regular language theory has a normal form. The minimal
deterministic finite automaton (DFA) is *the* automaton of a language —
computed, hashed, compared for sixty years — and behind it stands the
syntactic monoid, the canonical algebra through which the deepest structural
facts are read, most famously Schützenberger's theorem: star-free equals
aperiodic [Sch65, PP04]. On infinite words — the setting of model checking
and reactive synthesis — there is no analogue: a regular ω-language has no
canonical minimal deterministic ω-automaton, and every pipeline in the field
manipulates *presentations*, never languages [PP04]. Two automata for one
language share nothing observable; each language-level question must first
be argued independent of the presentation it is asked on, and equality
itself is decided by products and complementation, never by comparison.

The canonical algebra exists — on paper. Arnold [Arn85] defined the
syntactic congruence of a regular ω-language: the coarsest congruence
saturating it (membership depends only on the classes), of finite index,
whose quotient — the **syntactic ω-semigroup** — is a function of the
language alone and recognizes it. In principle this is the exact ω-analogue
of the syntactic monoid, and it closes the classical chain: linear temporal
logic (LTL) `=` first-order logic `FO[<]` `=` star-free `=` aperiodic
syntactic ω-semigroup [Kam68, Tho79, DG08] — every earlier item of the chain
is a syntax, the last is the semantics, and it is the one this paper builds.
In practice the syntactic ω-semigroup is a phantom, defined everywhere and
built nowhere: no tool materializes it from an automaton, and the
algorithmic accounts of the flagship application — deciding
LTL-definability — are complexity arguments that emit no algebra and no
evidence [DG08].

The obstruction is structural, not just size, and its two halves were each
solved in isolation without ever being combined. First, a recognizer for
infinite behaviour must remember *acceptance along runs*: the transition
monoid forgets the acceptance events along a run, which are exactly what
ω-acceptance consumes — Carton, Perrin and Pin have a recognizer that keeps
them [CPP08],
but reach the syntactic quotient only by saturation over context triples, an
example rather than a procedure. Second, Arnold's congruence is inherently
*two-sided*, while the one operation a finite table offers for free is
multiplication on the right — Maler and Staiger display the congruence as a
finitary–infinitary split [MS97], but compute no quotient, and their loop
test still hides a two-sided context. This paper supplies the missing
mathematics and assembles the construction. Our contributions:

1. **The invariant** (§3). `𝓘(L) = ⟨𝒮, P⟩`: a stamp
   `𝒮 : Σ⁺ → 𝒞` presented by its classes, letter map and multiplication
   table, and a pair set `P` of linked pairs, with a self-contained
   membership semantics on lassos — the ultimately periodic words `u·v^ω`
   (Definition 3.5). Canonicity
   (Theorem 3.10) makes it a complete invariant — and, under shortlex
   naming, a normal form: language equality is byte equality of the
   serialized tables.

2. **The rotation lemma** (§3.3). A loop may be rotated — a factor carried
   from the loop's front onto the stem leaves the ω-word unchanged — and
   this single move is how two presentations of one ω-word come to
   disagree. Read on contexts,
   it collapses Arnold's two-sided congruence to a computation by right
   multiplications alone: the structural fact the literature lacked, and
   the engine of the construction.

3. **The construction** (§4). From any deterministic Emerson–Lei automaton
   `D`: an acceptance-enriched stamp — sound but too fine — then the
   quotient by two right-only relations, computed by partition refinement.
   Theorem 4.11 closes the loop against the semantics: `𝓘(D) = 𝓘(L(D))`,
   byte for byte, whatever presentation `D` was.

§5 splits the two costs — the construction pays an exponential that
PSPACE-hardness makes unavoidable, while everything on the finished table is
polynomial in `|𝒞|`, a size intrinsic to the language. §6 puts the invariant
to work: the identity questions — equality, complement, membership,
witnesses — nearly for free, then the LTL frontier as a one-look read-off,
exact in both directions because the invariant is canonical. §7 reviews
related work; §8 opens the directions the invariant makes available —
classification, rendering to formulas, a calculus, a census, learning;
§9 concludes.

Four running examples accompany the paper, met first as tables and only
later as automata: `aUGb`, the pedagogical thread of §2–§3, and `GF(aa)`,
`Even`, `EvenBlocks`, chosen to exercise both context shapes of the
congruence and both sides of the LTL frontier. Each has its own page
(Ex. 1–4) at the end of the paper — language, formula, classification,
automaton, invariant.


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
infinite words. We assume basic comfort with ω-automata and linear temporal
logic [PP04, MP92]; every algebraic notion, in contrast, is defined here, and
nothing algebraic is deep: each notion, once unwrapped, is algebra on a
finite set.

Consider the language of Carton and Perrin [CP97, Ex. 10] described by
`a*·b^ω` — some `a`'s, then `b`'s forever — which we name `aUGb`. It
accompanies every notion of this section, each computed on it by hand; §3
assembles the results into one drawing, its syntactic ω-semigroup
(Figure 1). Three more languages join it across the paper — `GF(aa)`,
`Even`, `EvenBlocks` — and the four together are the running examples,
numbered Ex. 1–4. Each has a one-page table at the end of the paper —
informal description, ω-regular expression, formula, deterministic
automaton, invariant, and a guided reading. The pages are transverse to the
text, meant to be leafed through at leisure, early and often; the prose
points into them where each earns its keep.

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

**On finite words, the classifier is a finite monoid.**

**Definition 2.2 (monoid).** A **monoid** is a triple `(M, ·, 1)`: a set
`M`; a total binary operation `· : M × M → M` that is **associative** —
`(x·y)·z = x·(y·z)` for all `x, y, z ∈ M`; and a distinguished element
`1 ∈ M`, the **identity**: `1·x = x = x·1` for all `x ∈ M`. The monoid is
**finite** when `M` is.

Each word of the definition carries weight. *A set*: the elements have no
internal structure — a five-element monoid is five tokens and a 5×5 table,
nothing more. *Total operation*: every pair composes, and the result stays
inside `M` — closure, never partiality. *Associative*: bracketing is
irrelevant, so the product of any finite sequence `x₁·x₂·⋯·xₙ` denotes one
element — the single axiom that makes "read a word left to right"
well-defined, and licenses computing the product by any grouping.
*Identity*: a do-nothing element, neutral on both sides; an identity is
unique when it exists (`1 = 1·1' = 1'`), so *the* identity is honest
grammar. Two consequences follow. Powers `x^n` are well-defined and, over a
finite carrier, must eventually repeat — the pigeonhole fact §3 sharpens
into the idempotent power. And the finite words themselves form a monoid,
`(Σ*, ·, ε)` under concatenation with the empty word — the **free** monoid,
and (with `Σ⁺` below) the one infinite carrier in this paper: every other
carrier is finite, and every argument on one is a table lookup.

**Definition 2.3 (morphism; recognition).** A **morphism** of monoids
`φ : (Σ*, ·, ε) → (M, ·, 1)` is a map carrying each operation of the
signature to its counterpart: `φ(u·v) = φ(u)·φ(v)` and `φ(ε) = 1`. The
finite monoid `M` **recognizes** a language of finite words through `φ` when
membership depends only on the value: the language is `φ⁻¹(F)` for an
accepting set `F ⊆ M`.

Because `Σ*` is freely generated by the letters, a morphism out of it is
fixed by its letter images — `φ(x₁⋯xₙ) = φ(x₁)·⋯·φ(xₙ)` — so evaluating `φ`
*is* reading the word letter by letter, one table lookup per letter. The
finitely many elements of `M` are the classes, and recognition says the
table is a complete classifier: two words with one value are
interchangeable for membership. Every regular language of finite words is
recognized by a finite monoid, and among its recognizers one is canonical,
the **syntactic monoid** — the cornerstone of algebraic language theory
[PP04].

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
so the infinite theory is built on the nonempty words `Σ⁺`.

**Definition 2.4 (semigroup).** A **semigroup** is a pair `(S, ·)`: a set
`S` and a total, associative binary operation on it — a monoid minus the
identity, element and axiom both.

The demotion is forced by the domain, not chosen: `Σ⁺` is a semigroup and
not a monoid — the empty word is not there to serve as identity — and it is
free in the same sense as `Σ*`, so a morphism out of it is again fixed by
its letter images. One distinction becomes available, and §3 leans on it: a
semigroup may happen to *contain* a **neutral element** — one whose row and
column in the table leave every element unchanged — without that element
being an identity in the signature's sense. Neutrality is a property the
table exhibits; identity is a role the tuple declares. Keeping the two apart
is exactly what the fresh basepoint of §3.1 does, and two of the four
running examples (Ex. 3, Ex. 4) carry such an accidental neutral class.

On `Σ⁺` and `Σ^ω` together, the words carry three total operations:

* **concatenation** `Σ⁺ × Σ⁺ → Σ⁺` of two finite words;
* the **mixed product** `Σ⁺ × Σ^ω → Σ^ω` — a finite word prefixed to an
  ω-word, concatenation continued;
* the **ω-power** `Σ⁺ → Σ^ω`, `v ↦ v^ω` — the new operation, repetition
  forever.

**Definition 2.5 (ω-semigroup [PP04, Ch. II]).** An **ω-semigroup** is a
pair of **sorts** `S = (S₊, S_ω)` equipped with the same signature: a
product `S₊ × S₊ → S₊` making `S₊` a semigroup, a mixed product
`S₊ × S_ω → S_ω`, and an **ω-power** `S₊ → S_ω`, subject to the
associativity laws that make every mixed expression unambiguous
[PP04, Ch. II]. It is **finite** when both sorts are.

One sort per kind of word: the semigroup `S₊` carries the classes of
nonempty finite words, the set `S_ω` the classes of ω-words.
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


## 3. The syntactic ω-semigroup as an invariant `𝓘(L)`

The definition of the invariant

```
    𝓘(L) = ⟨𝒮, P⟩
```

splits in two parts: a **stamp** `𝒮`, classifying the finite words, and an
**acceptance layer** `P`, a set of accepted linked pairs. We define the stamp
first.

### 3.1 Syntax: the invariant `𝓘 = ⟨𝒮, P⟩`

The stamp packages the classifier of finite words in the vocabulary of §2,
plus two adjectives. A morphism of *semigroups* is as in Definition 2.3
minus the identity clause: `𝒮(u·v) = 𝒮(u)·𝒮(v)` alone. A morphism is
**surjective** — *onto* — when its image is everything: `𝒮(Σ⁺) = 𝒞`, every
class the class of at least one word. And an element adjoined to a set is
**fresh** when it is a genuinely new point: the union is disjoint, no
existing element promoted into the new role.

**Definition 3.1 (stamp over an alphabet).** A **stamp** over `Σ` is a
surjective semigroup morphism

```
    𝒮 : Σ⁺ → 𝒞
```

onto a finite semigroup `𝒞`, whose elements are the **classes**, written `[u]`
for any nonempty word `u ∈ Σ⁺` with `𝒮(u) = [u]`. The stamp extends to all
finite words by adjoining a **fresh** identity `[ε]`:

```
    M := 𝒞 ∪ {[ε]},     𝒮(ε) := [ε],
```

making `𝒮 : Σ* → M` a surjective monoid morphism.

Each clause of the definition enforces something the rest of the paper
stands on. *Morphism*: the table determines the whole map — evaluating `𝒮`
is one lookup per letter, and no argument ever revisits the word itself.
*Onto a finite `𝒞`*: infinitely many nonempty words collapse onto `|𝒞|²`
products, and everything from here on is a scan of that table. *Surjective*:
no spectator classes — every class comes with word witnesses. *The bracket
`[u]`*: a name, not a set construction — `[u]` is the value `𝒮(u)`, and any
word with that value may serve as the name. *Fresh*: `[ε]` is **isolated** —
`𝒮(u) = [ε]` forces `u = ε` — and `𝒞` **absorbs** — `M` differs from `𝒞` by
exactly that basepoint, so a product touching a class of words stays in `𝒞`.

Freshness is the canonical choice, not a convenience: adjoining a *new* unit is
the universal way of making a semigroup a monoid, and it is deliberate that
this holds even when `𝒞` owns an internal neutral element — the
neutral-vs-identity distinction of §2, now enforced. Such an element is a
class of nonempty words invisible to the language — a genuine behavior,
loopable, with verdicts of its own — while `[ε]` is the basepoint "no word at
all", which can never be looped; `Even` (Ex. 3) exhibits both at once, kept
apart.

**Representation.** The notion is Pin and Straubing's [PS05], where a stamp is
a surjective morphism from a free monoid onto a finite monoid; we transpose it
to `Σ⁺` since the empty word plays no role in the ω-theory — no ω-word has an
empty trace. Because `Σ⁺` is the free semigroup over `Σ`, a stamp is determined
by its values on the letters:

```
    𝒮(x₁x₂⋯xₙ) = 𝒮(x₁)·𝒮(x₂)·⋯·𝒮(xₙ),
```

and conversely every map `Σ → 𝒞` whose image generates `𝒞` extends to a stamp.
We write `λ := 𝒮|_Σ` for this restriction, the **letter map**. A stamp is
therefore *finitely presented* by the data `(𝒞, λ, ·)` — the finite set of
classes, the letter map, the multiplication table — and this presentation is
the materialization this paper manipulates: classically the stamp *is* the
morphism; what the field has never had in hand is its table.

*Notation (representatives).* A class is denoted by one of its member words,
`[a·b]` for the class of `ab`; any member may serve, and nothing below depends
on the choice. For readability, figures and examples use the shortlex-least
member (shortest, then alphabetically first) — a naming convention, not data.

*Example.* The stamp of `aUGb = a*·b^ω` (Figure 1) has four classes,
`𝒞 = {[a], [b], [a·b], [b·a]}`, with `𝒮(a) = [a]`, `𝒮(b) = [b]`. The table is
the drawn graph: `[a]·[b] = [a·b]`, `[a·b]·[a] = [b·a]`, and `[b·a]` is a
two-sided zero — the dead words, once an `a` follows a `b`. These are §2's
four kinds, wearing their shortlex names.

| ![Figure 1a — the stamp core](sos_core_figs/img/core_F0_astar_bomega_b_pairs.png) | ![Figure 1b — the monoid completion](sos_core_figs/img/core_F0_astar_bomega.png) |
|:--:|:--:|

*Figure 1 — `𝓘(aUGb)`, drawn twice. Left — the stamp core: the complete data
of the invariant `⟨𝒮, P⟩` in one drawing. The four classes are the vertices.
The letter map `λ` is the two entry arrows — `a` enters at `[a]`, `b` at
`[b]`: where the reading of a word starts. The table is the edges: following
an edge multiplies on the right by its label; parallel edges are fused into
one arrow listing their labels; and the label `𝒞` on the zero's self-loop
abbreviates all four classes at once — the picture of absorption. The
acceptance layer is drawn on top: an accepting pair `(s, e) ∈ P` is the
doubled self-loop at the stem class `s`, labeled by its loop class `e` —
here `([b], [b])` and `([a·b], [b])` — and `P` is restated in full beneath.
Right — the monoid completion `M = 𝒞 ∪ {[ε]}` of the same stamp, `λ` and `P`
printed as text: the fresh identity drawn in, adding exactly its row — the
edges leaving `[ε]` — and its column, `[ε]` joining every self-loop. An
identity moves nothing: eliding it loses no edge worth reading, and all
further drawings use the left form.*

*Example (the letter map is data).* Over `Σ = {a, b, c}`, the language
`(a|c)*·b^ω` has the same four classes and the same table: `a` and `c` are
interchangeable everywhere, `λ(a) = λ(c) = [a]`. Only `λ` tells the two stamps
apart — which is precisely why [PS05] compare stamps rather than semigroups.

In a finite semigroup the powers `c, c², c³, …` of any element cannot all be
distinct, so the sequence is eventually periodic and contains exactly one
idempotent [PP04].

**Definition 3.2 (idempotent power; exponent of a stamp).** Let
`𝒮 : Σ⁺ → 𝒞` be a stamp and `c ∈ 𝒞`. The **idempotent power** of `c` is the
unique idempotent among its powers — the one `cⁿ` (`n ≥ 1`) with `cⁿ·cⁿ = cⁿ`.
An **exponent** of `𝒮` is an integer `π ≥ 1` such that `c^π` is the idempotent
power of *every* `c ∈ 𝒞`; one exists since `𝒞` is finite (e.g. `|𝒞|!`), and
which multiple is chosen never matters. We fix one and write `c^π`.

`c^π` is an honest power, computed on the table alone, and the notation
deliberately avoids `^ω` — in this paper `^ω` always means infinite
repetition, and nothing here is infinite. This idempotent is exactly what
stands in for the ω-power of the two-sorted recognizers (§2): iterating a
loop's class until it stabilizes is how "forever" is read on a finite table.

*Example.* On Figure 1 (`aUGb`), `[a]`, `[b]`, `[b·a]` are idempotent, hence
their own idempotent powers. `[a·b]` is not: `[a·b]·[a·b] = [b·a]` — gluing two
words of `a⁺b⁺` puts an `a` after a `b` — so `[a·b]^π = [b·a]`: looping "`a`'s
then `b`'s" is exactly as dead as slipping once.

**Definition 3.3 (linked pair of classes).** Let `𝒮 : Σ⁺ → 𝒞` be a stamp. A
**linked pair** of `𝒮` is a pair of classes `(s, e) ∈ 𝒞 × 𝒞` with `e·e = e`
and `s·e = s`: the loop class `e` is idempotent, and it absorbs the stem class
`s`.

*Example.* On Figure 1 (`aUGb`), `([a·b], [b])` is linked: `[b]` is idempotent
and `[a·b]·[b] = [a·b]`. The pair `([a], [b])` is not: `[a]·[b] = [a·b] ≠ [a]`
— a stem that ends before `b`'s begin is not absorbed by them.

**Definition 3.4 (pair set; invariant over an alphabet).** Let `𝒮` be a stamp
over `Σ`. A **pair set** over `𝒮` is a finite set `P ⊆ 𝒞 × 𝒞` of linked pairs
of `𝒮`. An **invariant** over `Σ` is a pair `𝓘 = ⟨𝒮, P⟩` of a stamp and a pair
set over it.

The typing is deliberate: `P` lives in `𝒞 × 𝒞`, entirely inside the semigroup.
The basepoint `[ε]` appears in no pair — the acceptance layer speaks only of
words.

*Example.* Figure 1 carries its pair set beneath the drawing:
`P = { ([b], [b]), ([a·b], [b]) }` — both pairs linked, both with loop class
`[b]`.

### 3.2 Semantics: the language of an invariant

An invariant decides lassos with the data it carries and nothing else: the
stamp assigns each finite word its class — stem and loop alike — and `P` lists
the pairs that accept.

**Definition 3.5 (language of an invariant).** Let `𝓘 = ⟨𝒮, P⟩` be an
invariant over `Σ`, and let `w ∈ Σ^ω` be a lasso with presentation
`(u, v) ∈ Σ* × Σ⁺` (Definition 2.1), `w = u·v^ω`. Set

```
    e := 𝒮(v)^π,     s := 𝒮(u)·e.
```

Then `w ∈ L(𝓘)` iff `(s, e) ∈ P`.

The queried pair is a linked pair of `𝒮`: `e` is idempotent as an idempotent
power, and `s·e = 𝒮(u)·e·e = s`. Both coordinates land in `𝒞` — `e` is the
idempotent power of a class of nonempty words, and `s = 𝒮(u)·e` is in `𝒞` by
absorption even when the stem is empty. The query never mentions `[ε]` —
nothing that happens forever has an empty trace, and here that is a typing
fact, not a lemma.

*Example.* On Figure 1 (`aUGb`), the two verdicts. For `aab·b^ω`: the loop's
class `𝒮(b) = [b]` is already idempotent, so `e = [b]`; the stem's class is
`𝒮(aab) = [a·b]` and `[a·b]·[b] = [a·b]`. The pair `([a·b], [b])` is in `P`:
accepted. For `ba·(ab)^ω`: the loop's class `𝒮(ab) = [a·b]` is not idempotent —
its square `[b·a]` is — so `e = [b·a]`; the stem's class is `[b·a]` and
`[b·a]·[b·a] = [b·a]`. The pair `([b·a], [b·a])` is not in `P`: rejected.

**Definition 3.6 (name of a lasso).** Let `𝒮` be a stamp over `Σ`. A linked
pair `(s, e)` of `𝒮` **names** the lasso `w` when some presentation
`(u, v) ∈ Σ* × Σ⁺` of `w` lands on it: `𝒮(v)^π = e` and `𝒮(u)·e = s`.

Definition 3.5 thus queries one name of `w` — the one its given presentation
lands on. A lasso bears several names: already `(u, v)` and `(u·v, v)` present
the same ω-word and may land on distinct pairs. Nothing yet says all names of
one lasso receive one verdict from `P`; that the semantics is nevertheless
well defined is the subject of the next section.

### 3.3 Canonicity: the invariant of `L`

Definitions 3.5 and 3.6 leave two debts. A lasso bears many names — nothing
yet says `P` treats them alike. And the query evaluates whatever invariant it
is handed — nothing yet singles out, among the many invariants denoting one
language, a canonical one. Both debts are paid at once by building the
invariant from `L` itself, one class per behavior `L` can distinguish. The
classifying relation is Arnold's [Arn85]. A finite word sits in a lasso either
in the stem or inside the loop, and interchangeability must hold in both
positions:

**Definition 3.7 (syntactic congruence of an ω-language [Arn85]).** Let
`L ⊆ Σ^ω` be a regular ω-language. Two nonempty words `u, u' ∈ Σ⁺` are
**syntactically congruent** for `L`, written `u ≈_L u'`, when they are
interchangeable in both context shapes:

```
    (linear)     ∀ u₀ ∈ Σ*,  ∀ lasso w ∈ Σ^ω :   u₀·u·w ∈ L     ⟺   u₀·u'·w ∈ L
    (ω-power)    ∀ u₀, v₀ ∈ Σ*               :   u₀·(u·v₀)^ω ∈ L  ⟺   u₀·(u'·v₀)^ω ∈ L
```

The linear shape mutates the stem — the tested word sits after a finite prefix
`u₀`, in front of a whole lasso `w`; the ω-power shape mutates inside the
loop, where the change recurs forever, `v₀` completing each turn. Congruence
is a property of the word, not of a position: the primes mark the replacement,
and the relation is instantiated at loop words (`v ≈_L v'`) in the
substitution lemma (3.9). The linear shape quantifies over lassos where
Arnold quantifies over a finite completion followed by a nonempty loop — the
same set of contexts, repackaged on the notion this paper is about. `≈_L` is a
two-sided congruence on `Σ⁺` of finite index for regular `L` [Arn85], and the
coarsest relation with these interchange properties — the first of two senses
in which the quotient below is minimal. Note the domain: the relation lives on
`Σ⁺`. The empty word is not comparable — the ω-power shape at `v₀ = ε` would
have to evaluate `ε^ω`, which is not an ω-word — and the quotient below is a
semigroup, as Definition 3.1 requires.

*Example.* On Figure 1 (`aUGb`), from `L = a*·b^ω` alone: `a ≉_L b` by the
ω-power shape at `u₀ = v₀ = ε` — `a^ω ∉ L`, `b^ω ∈ L`; `ab ≉_L ba` by the
linear shape at `u₀ = ε`, `w = b^ω` — `ab·b^ω ∈ L`, `ba·b^ω ∉ L`; and
`a ≈_L aa` — membership in `L` never counts `a`'s. The quotient `Σ⁺/≈_L` has
exactly four classes — `a⁺`, `b⁺`, `a⁺b⁺` and the dead words — the four
vertices of Figure 1.

**Definition 3.8 (syntactic stamp; syntactic invariant of `L`).** Let
`L ⊆ Σ^ω` be a regular ω-language, and let `𝒞_L := Σ⁺/≈_L` be its finite
semigroup of congruence classes. The **syntactic stamp** of `L` is the
quotient morphism

```
    𝒮_L : Σ⁺ → 𝒞_L
```

— surjective by construction, a semigroup morphism because `≈_L` is a
two-sided congruence — with letter map `λ(x) = [x]` and the induced
table `[u]·[v] := [u·v]`. The **syntactic invariant** of `L` is
`𝓘(L) := ⟨𝒮_L, P(L)⟩`, where `P(L)` collects the names of the lassos of `L`:

```
    P(L) := { (𝒮_L(u)·e, e)  :  u ∈ Σ*,  v ∈ Σ⁺,  e = 𝒮_L(v)^π,  u·v^ω ∈ L }.
```

The definition of `P(L)` makes no choice: it ranges over *all* presentations
of *all* accepted lassos and records the name each one lands on. In particular
no representative is consulted — testing a single lasso per pair, keyed by
chosen representatives, is how `P(L)` is *computed* (§4), and its correctness
is the content of canonicity (Theorem 3.10), not part of the definition.

*Example.* Figure 1 is `𝓘(aUGb)` — §2 called the drawing a syntactic
ω-semigroup, and Definition 3.8 is that claim made precise. The accepted lassos
are those eventually reading only `b`'s; their stems land in `{[b], [a·b]}`
after absorption, their loops settle on `[b]`, and
`P(L) = { ([b], [b]), ([a·b], [b]) }`, the pair set printed beneath the figure.

The two context shapes were tailored to lassos, and they pay immediately:

**Lemma 3.9 (substitution of congruent words).** Let `u, u', v, v' ∈ Σ⁺` with
`u ≈_L u'` and `v ≈_L v'`. Then `u·v^ω ∈ L ⟺ u'·v'^ω ∈ L`.

*Proof.* Swap the loop: the ω-power shape of `v ≈_L v'`, at `u₀ = u` and
`v₀ = ε`, gives `u·v^ω ∈ L ⟺ u·v'^ω ∈ L`. Swap the stem: the linear shape of
`u ≈_L u'`, at `u₀ = ε` and `w = v'^ω`, gives `u·v'^ω ∈ L ⟺ u'·v'^ω ∈ L`. ∎

**Theorem 3.10 (canonicity of the syntactic invariant).** Let `L ⊆ Σ^ω` be a
regular ω-language.

(i) All lassos sharing a name share `L`'s verdict; consequently, on `𝓘(L)`,
the query of Definition 3.5 answers membership in `L` itself — every
presentation of every lasso receives `L`'s verdict — and `L(𝓘(L)) = L`.

(ii) `𝓘` is a **complete invariant**: for regular `L, L' ⊆ Σ^ω`, `L = L'` iff
there is a semigroup isomorphism `θ : 𝒞_L → 𝒞_{L'}` with `θ ∘ 𝒮_L = 𝒮_{L'}`
and `(θ×θ)(P(L)) = P(L')` — and such a `θ`, when it exists, is unique.

*Proof.* (i) Let `(u, v)` be a presentation of the lasso `w`, landing on the
name `(s, e)`: `e = 𝒮_L(v)^π`, `s = 𝒮_L(u)·e`. The idempotent power is an
honest power: rewrite `w` on the presentation `(u·v^π, v^π)` — the same
ω-word — whose coordinates are nonempty (the loop `v` is), so on them `𝒮_L` is
the quotient morphism: `s = [u·v^π]` and `e = [v^π]` as congruence classes.
Now take any two lassos named `(s, e)` and rewrite each this way: their
rewritten stems are congruent (both lie in the class `s`), their loops
congruent (both in `e`), and the substitution lemma (3.9) gives them one
verdict. So all lassos named `(s, e)` agree with each other — and `P(L)`
contains `(s, e)` iff that shared verdict is acceptance. The query on any
presentation of any lasso `w` therefore answers `w ∈ L`; and since lassos
determine a regular language [PP04, Ch. I, Cor. 9.8], `L(𝓘(L)) = L`.

(ii) If `L = L'` the two constructions are literally the same. Conversely, a
`θ` commuting with the stamps carries names to names and `P(L)` onto `P(L')`,
so the two queries agree on every lasso; by (i) each answers its own language,
hence `L = L'`. Uniqueness: `θ` is forced on every class by
`θ([u]) = θ(𝒮_L(u)) = 𝒮_{L'}(u)`, and `𝒮_L` is surjective. ∎

*Remark (byte equality).* Naming every class by its shortlex-least member
turns the unique isomorphism of Theorem 3.10(ii) into the identity on names:
two regular ω-languages are equal iff the serialized invariants — classes,
letter map, table, `P`, under shortlex naming — are byte-identical.
Canonicity is the mathematics; byte equality is that mathematics plus a naming
convention, and it is the form the serialized invariant of §6.1 puts to work.

*Example.* On Figure 1 (`aUGb`), present `aab·b^ω` as `(aab, b)` or as
`(aabb, bb)`: both land on the name `([a·b], [b])` — here even the name is
stable. That is a feature of `aUGb`, not of the theorem: `Even` (Ex. 3) names
one lasso through two distinct pairs, and canonicity (Theorem 3.10(i)) is what
forces those two names to one verdict.

§2 promised a reconciliation: one lasso, many names. The constraint that
canonicity puts on a pair set has a single generator. **A loop may be
rotated**: a factor carried from the loop's front onto the stem leaves the
ω-word unchanged, `u·v₁·(v₂·v₁)^ω = u·(v₁·v₂)^ω` — and rotation is the one
move that changes a lasso's name.

**Lemma 3.11 (rotation of a name).** Let `𝒮 : Σ⁺ → 𝒞` be a stamp and
`s, c, d ∈ 𝒞` with `s·(cd)^π = s`. Then `(s·c, (dc)^π)` is a linked pair, and
some lasso is named by both `(s, (cd)^π)` and `(s·c, (dc)^π)`.

*Proof.* First the identities in `𝒞`. Associativity gives `c·(dc)^m = (cd)^m·c`
for every `m ≥ 1`; at `m = π` — one exponent serving `cd` and `dc` alike —
this reads `c·(dc)^π = (cd)^π·c`. Hence
`(s·c)·(dc)^π = s·(cd)^π·c = s·c`: the rotated pair is linked.
By surjectivity of the stamp pick nonempty words `u, v₁, v₂ ∈ Σ⁺` with
`𝒮(u) = s`, `𝒮(v₁) = c`, `𝒮(v₂) = d`, and consider the single ω-word
`w := u·(v₁v₂)^ω`. The presentation `(u, (v₁v₂)^π)` lands on
`(s·(cd)^π, (cd)^π) = (s, (cd)^π)`; the presentation `(u·v₁, (v₂v₁)^π)` — the
same ω-word, `u·(v₁v₂)^ω = u·v₁·(v₂v₁)^ω` — lands on
`(s·c·(dc)^π, (dc)^π) = (s·c, (dc)^π)`. So `w` is named by both pairs. ∎

Every element named in the lemma lies in `𝒞`, and surjectivity hands each a
nonempty word: no corner case guards the identity, because `[ε]` is not there
to be rotated through.

**Definition 3.12 (conjugate pairs; saturated pair set).** Let `𝒮` be a stamp.
Two linked pairs of `𝒮` are **conjugate** when rotations connect them:
conjugacy is the equivalence generated by `(s, (cd)^π) ∼ (s·c, (dc)^π)` over
the triples `s, c, d ∈ 𝒞` with `s·(cd)^π = s` — the notion is classical
[PP04, Ch. II, Prop. 2.6]. A pair set `P` over `𝒮` is **saturated** when it is
closed under conjugacy:

```
    (s, (cd)^π) ∈ P   ⟺   (s·c, (dc)^π) ∈ P.
```

Stem extension is the degenerate rotation `c = d = 𝒮(v)`: the loop's value is
unchanged and the stem absorbs one turn — why `(u, v)` and `(uv, v)` may name
one lasso by two pairs.

**Corollary 3.13 (saturation of the syntactic invariant).** `P(L)` is
saturated.

*Proof.* By the rotation lemma (3.11) some lasso `w` is named by both pairs,
and `P(L)` is the set of names of accepted lassos, whose verdicts, by
canonicity (Theorem 3.10(i)), agree name-by-name: each of the two pairs is in
`P(L)` iff `w ∈ L` — both in or both out. ∎

Saturation is the one law an acceptance layer must obey, and it is
table-checkable: finitely many triples `(s, c, d)`, each one product and two
lookups. The rotation identity itself is classical: our
`c·(dc)^π = (cd)^π·c` is the finite shadow of Wilke's axiom
`s·(ts)^ω = (st)^ω` [PP04, Ch. II, Thm 5.1] — his `^ω` is the genuine
second-sort ω-power, ours a power in `𝒞` — and conjugacy of
linked pairs organizes the classical theory [PP04, Ch. II, Prop. 2.8, Cor. 2.9].
What this paper draws from it is a different service: rotation turns two-sided
demands about `L` into right-only computations — the engine of the construction
(§4), where it collapses Arnold's two-sided congruence to a right-invariant
refinement computable on a table.

*Example.* On Figure 1 (`aUGb`), every conjugacy class is a singleton —
whatever factor a rotation moves, the dead class absorbs it, and the two
accepting stems absorb their loops — so saturation of `P(aUGb)` is immediate.
`Even` (Ex. 3) works the check for real: present `a^ω` as `(ε, a)` — the
loop's class `[a]` has idempotent power `[a]^π = [a·a]`, and the queried pair
is `([a·a], [a·a])` — or as `(a, a)`, landing on
`([a]·[a·a], [a·a]) = ([a], [a·a])`: one lasso, two names, connected by the
conjugacy step at `s = c = d = [a]`. Both pairs are absent from `Even`'s `P`,
as saturation demands; a pair set containing one but not the other would be
illegal — its query self-contradictory on the single ω-word `a^ω`.


## 4. The construction: from an automaton to `𝓘(L)`

We now construct the invariant. The input is an automaton `D` for `L`, in the
most general deterministic form in use — throughout this section `L := L(D)`.
The output is `𝓘(D)`, and the destination is Theorem 4.11: `𝓘(D) = 𝓘(L)` —
not merely *an* invariant denoting `L`, but the syntactic invariant of §3.3
itself, byte for byte, whatever presentation `D` was. The construction is two
steps, and both are stamp-shaped: an enrichment of the automaton's transition
structure until acceptance is algebraic — the result is a stamp, rough but
sound (§4.2) — and a canonicalization: the quotient by Arnold's congruence
(Definition 3.7), which the rotation lemma (3.11) makes computable by right
multiplications alone (§4.3).

### 4.1 Emerson–Lei automata

Nothing in this subsection is ours: we fix the input format and its
vocabulary.

**Definition 4.1 (deterministic Emerson–Lei automaton).** A **deterministic,
complete Emerson–Lei automaton** over `Σ` is `D = (Q, ι, δ, Γ, Acc)`: a finite
set `Q` of **states** with an **initial** state `ι ∈ Q`; a total **transition
function** `δ : Q × Σ → Q`, each transition carrying a (possibly empty) subset
of a finite set `Γ` of **marks**; and an **acceptance condition** `Acc`, a
positive Boolean combination of atoms `Inf(γ)`, `Fin(γ)` for `γ ∈ Γ`. An
ω-word `w = x₁x₂⋯` traces the unique infinite **run** `q₀ = ι`,
`q_i = δ(q_{i-1}, x_i)` — one successor per letter, a successor for every
letter, so exactly one run, never stalling. `Acc` is evaluated on the set of
marks the run collects infinitely often — `Inf(γ)` true iff `γ` recurs,
`Fin(γ)` iff it does not — and `L(D)` is the set of ω-words whose run
satisfies `Acc`.

Emerson–Lei acceptance is the most general ω-regular acceptance — Büchi,
co-Büchi, Rabin, Muller are special shapes — and every regular `L` is `L(D)`
for some such `D`, determinization costing at worst an exponential [Saf88].
Figures draw `δ` one letter per edge, parallel edges fused with a comma
(`a, b`), marks printed on the edge they decorate. For readers coming from LTL
and the ω-automata tools: there the alphabet is the set of valuations of the
atomic propositions — one proposition gives two letters, two give four; this
paper's `a, b` is the one-proposition case.

For `q ∈ Q`, the **residual** `L(q) := { w ∈ Σ^ω : the run from q on w
satisfies Acc }` is what `D` would accept started at `q`; determinism ties
residuals to the language, `L(δ(ι, u)) = u⁻¹L` for every finite `u`. We write
`Reach := δ(ι, Σ*)` for the states some finite word reaches.

These automata are, in practice, the standard machine representation of
regular ω-languages — the form modern tools exchange and optimize. What the
format lacks is a canonical form: on finite words minimization yields *the*
minimal DFA, unique up to isomorphism, while a regular ω-language has no such
distinguished machine — `GF(aa)` is drawn twice in this paper as two
non-isomorphic automata on the same two states (Ex. 2 and Figure 2), with
nothing intrinsic to prefer either. §4.4 sends both to one invariant.

*Example.* The four languages appear as machines on their pages, Ex. 1–4 —
the reader is invited to revisit each page's formula and automaton rows now.
`aUGb` needs
three states, numbered as drawn on its page: the initial state `1` loops on
`a`; `b` leads to state `0`, which loops on `b`, that loop carrying the mark
`0`; an `a` at state `0` falls to the sink `2`, absorbing both letters
unmarked; `Acc = Inf(0)` — a run collects `0` forever iff it
eventually reads only `b`'s. `GF(aa)` tracks the parity of the running block
of `a`'s on two states: `a` *transposes* them — a `Z₂` in the maps
`q ↦ δ(q, u)` — and the transposition closing an `aa` carries the mark; `b`
resets, unmarked; `Acc = Inf(0)`. `Even` needs four states: the parity pair,
swapped by `a`, plus two sinks — `b` at even parity enters the accepting sink,
its self-loops marked, `b` at odd parity the rejecting one; `Acc = Inf(0)`.
`EvenBlocks` returns to two states: `a` toggles the parity of the running
block; `b` returns to even, marked `1` when the block it closes is even, `0`
when it is odd; `Acc = Fin(0) ∧ Inf(1)` — infinitely many even blocks,
finitely many odd ones.

### 4.2 Step 1: the enriched stamp

The classical algebra of `D` on finite words is its transition monoid, the
maps `q ↦ δ(q, u)`. It forgets the marks a run collects — exactly the data
`Acc` consumes. So we enrich it.

**Definition 4.2 (enriched element; enriched stamp).** For `u ∈ Σ*`, the
**enriched element** `⟨u⟩` records, at each state, where `u` leads and what it
collects:

```
    ⟨u⟩ : q ↦ ( δ(q, u), mk(q, u) ),
```

`mk(q, u) ⊆ Γ` the marks on the run from `q` over `u`. Under the composition
`⟨u₁⟩·⟨u₂⟩ = ⟨u₁·u₂⟩` — at `q`: reach `δ(q, u₁)`, continue by `u₂`, unite the
marks — the enriched elements form a finite monoid `EM(D)`, generated by the
letter elements `⟨x⟩`, with identity `⟨ε⟩ : q ↦ (q, ∅)`; every element is
`⟨u⟩` for some finite word `u`. We write `st_c(q)`, `mk_c(q)` for the two
components of `c ∈ EM(D)` at `q`. The images of the nonempty words form a
subsemigroup `EM₊(D)`, and

```
    𝒮_D : Σ⁺ → EM₊(D),    u ↦ ⟨u⟩,
```

is a surjective semigroup morphism onto a finite semigroup — a stamp
(Definition 3.1), the **enriched stamp** of `D`.

The stamp is rough: sound (below) but generally finer than the syntactic one.
Note that `⟨ε⟩` may lie in `EM₊(D)`: on `EvenBlocks`'s two-state automaton
`⟨aa⟩ = ⟨ε⟩` — two `a`'s toggle back, collecting nothing — an internal neutral
element among the images of nonempty words. This is exactly the situation
Definition 3.1's freshness is designed for: the basepoint `[ε]` of the final
invariant is adjoined fresh by the quotient stamp of §4.4, whatever identities
`EM₊(D)` happens to own.

*Example.* On the two-state `GF(aa)`, the elements `⟨a⟩` and `⟨aaa⟩` have the
*same* state part — the transposition — and differ only in marks:
`mk_{⟨aaa⟩}(0) = {0}` (the longer word closes an `aa`), `mk_{⟨a⟩}(0) = ∅`.
The transition monoid identifies them; the enrichment keeps them apart.
Closing the letters under composition gives `|EM₊| = 9` for this presentation
of `GF(aa)`, `6` for `Even` — and the full `16` for `EvenBlocks`, where `⟨ε⟩`,
being `⟨aa⟩`, is itself an image of nonempty words and nothing is spared;
`aUGb` closes at `9`. The example pages carry the four tables in full, one
row per element with its fold onto `𝒞`: `9 → 4`, `9 → 5`, `6 → 4`, `16 → 7`
(Ex. 1–4).

**Lemma 4.3 (skeleton).** Let `w = u₁u₂⋯` and `w' = u'₁u'₂⋯` be ω-words
factored into nonempty blocks with the same sequence of enriched images —
`⟨u_k⟩ = ⟨u'_k⟩` for every `k`. Then `w ∈ L ⟺ w' ∈ L`.

*Proof.* Determinism gives each word one run. The composition law turns block
equality into prefix equality, `⟨u₁⋯u_k⟩ = ⟨u'₁⋯u'_k⟩`, so both runs sit at
the same state `p_k = st_{⟨u₁⋯u_k⟩}(ι)` at every block boundary; and the marks
collected inside block `k` are read off the block's own image at that state:
`mk(p_{k-1}, u_k) = mk_{⟨u_k⟩}(p_{k-1}) = mk_{⟨u'_k⟩}(p_{k-1})
= mk(p_{k-1}, u'_k)`. The two runs collect the same marks per block, hence the
same set of marks infinitely often — and `Acc` is a function of that set
alone. ∎

Block equality is the needed hypothesis: equal *prefix* images do not
suffice. On the one-state automaton of Proposition 4.5 below, `a·a·a⋯` and
`a·b·b⋯` have equal enriched images on every prefix — all collect the mark —
yet the first is in `L(D)` and the second is not: a union of marks along a
prefix hides which block collected them.

**Corollary 4.4 (the enriched stamp refines the syntactic stamp).** Let
`u, u' ∈ Σ⁺`. If `⟨u⟩ = ⟨u'⟩` then `u ≈_L u'`. Consequently the syntactic
stamp factors through the enriched one: there is a unique — and surjective —
semigroup morphism `ρ : EM₊(D) → 𝒞_L` with `𝒮_L = ρ ∘ 𝒮_D`.

*Proof.* Both shapes of Definition 3.7 compare ω-words that factor into
nonempty blocks with equal enriched images. Linear shape: for `u₀ ∈ Σ*` and a
lasso `w = v₀·v^ω`, the words `u₀·u·w` and `u₀·u'·w` factor as
`u₀ | u | v₀ | v | v | ⋯` against `u₀ | u' | v₀ | v | v | ⋯` (empty context
blocks dropped on both sides at once) — equal blockwise, `⟨u⟩ = ⟨u'⟩` at the
one block that differs; Lemma 4.3 gives one verdict. The ω-power shape factors
as `u₀ | u·v₀ | u·v₀ | ⋯` against `u₀ | u'·v₀ | ⋯`, with
`⟨u·v₀⟩ = ⟨u⟩·⟨v₀⟩ = ⟨u'⟩·⟨v₀⟩`. For the factorization: set
`ρ(⟨u⟩) := 𝒮_L(u)` — well defined by the implication just proved, a morphism
because `𝒮_D` and `𝒮_L` are, surjective because `𝒮_L` is, and forced on every
element by the equation. ∎

So `≈_L` lives on the finite semigroup: computing `𝒞_L = Σ⁺/≈_L` is computing
the kernel of `ρ`, a quotient of `EM₊(D)`. Two boundary facts calibrate how
far `EM₊(D)` is from that quotient.

**Proposition 4.5 (enrichment is necessary).** No quotient of the transition
monoid can serve, in general, as the carrier of a stamp denoting `L(D)`.

*Proof (a one-state witness).* Let `D` have one state `p`, both letters of
`Σ = {a, b}` self-looping, the mark on the `a`-loop only, `Acc = Inf(0)`:
`L(D)` is "infinitely many `a`'s". The transition monoid is trivial — every
word is the identity map on `{p}` — so any stamp built on a quotient of it
gives `a` and `b` one class, the queries of `a^ω` and `b^ω` coincide
(Definition 3.5), and the two receive one verdict. But `a^ω ∈ L(D)` and
`b^ω ∉ L(D)`. The enriched elements do separate them:
`mk_{⟨a⟩}(p) = {0} ≠ ∅ = mk_{⟨b⟩}(p)`. ∎

The starkness is the message: a trivial transition monoid under a nontrivial
language. No state bookkeeping recovers acceptance — the marks along the run
are irreducible data, and the enrichment is the smallest way to keep them. It
is also why a group in a transition monoid proves nothing about `L`: it can be
pure encoding, invisible to the marks. `GF(aa)`'s transposition is exactly
that situation, resolved in §4.4.

*Example (the converse defect: the enriched stamp is too fine).* On the
`aUGb` automaton, `⟨ba⟩` and `⟨aba⟩` are distinct elements —
`mk_{⟨ba⟩}(0) = {0}` while `mk_{⟨aba⟩}(0) = ∅` — though `ba ≈_L aba`: both
are dead, and no context separates them. Ex. 1's table holds four such dead
variants, kept apart only by which slots saw the mark on the way to the
sink, one zero class under all of them. The next step quotients exactly this
excess away.

### 4.3 Step 2: the quotient, computed on the right

What remains is to merge elements of `EM₊(D)` exactly when the words they
image are congruent — interchangeable in every stem, in every loop.
Interchangeability is a two-sided demand: a word sits in a lasso between a
left context and a right one. A semigroup's table, meanwhile, offers one
operation for free: multiply on the right. The gap is closed by the rotation
lemma (3.11) read on runs: a left factor carries no information of its own; it
only shifts the slot where a right test is read.

**Lemma 4.6 (loop verdict; collapse).** Let `s ∈ EM(D)` and `c ∈ EM₊(D)`. All
lassos `u·v^ω` with `⟨u⟩ = s` and `⟨v⟩ = c` share one verdict (Lemma 4.3),
written `Acc(s, c)`; and it depends on `s` only through the single state the
stem reaches:

```
    Acc(s, c) = A(st_s(ι), c),
```

where the **loop verdict** `A(q, c)` iterates `c` from `q`: follow `st_c`
from `q` into its closed cycle, unite the marks `mk_c` around that cycle,
evaluate `Acc`.

*Proof.* The stem is read once; its marks are collected finitely often and
none recurs. The set of marks recurring in `u·v^ω` is therefore that of the
tail `v^ω` read from `st_s(ι)`: the iteration of `st_c` from there eventually
closes a cycle, the marks `mk_c` around that cycle recur, and no other mark
does. ∎

**Definition 4.7 (the two right relations).** For `c, c' ∈ EM₊(D)`, with
`Aprof(c) := (q ∈ Reach ↦ A(q, c))` the **profile** of `c`:

```
    c ∼lin c'   ⟺   ∀ q ∈ Reach :   L(st_c(q)) = L(st_{c'}(q)) ;
    c ∼ω  c'    ⟺   ∀ d ∈ EM(D) :   Aprof(c·d) = Aprof(c'·d) ;
```

and `∼ := ∼lin ∧ ∼ω`. The slots are `Reach`, not `Q`: an unreachable state
names no context. The extension `d` ranges over all of `EM(D)`, identity
included — `d = ⟨ε⟩` tests the bare loop `c` itself, and `c·d` is always the
image of a nonempty word.

`∼lin` compares the futures the words open — residual languages of reached
states — and never looks at marks; `∼ω` compares the loops the words can
close, under every right completion. Neither mentions a left context.

*Example (the two relations divide the labor).* On `EvenBlocks`'s two-state
`D`, `⟨aa⟩ = ⟨ε⟩`. `∼lin` is total: the language is prefix-independent, both
states accept exactly `EvenBlocks`. The separation of `⟨a⟩` from `⟨aa⟩` is
carried entirely by `∼ω`, with the block-closing extension `d = ⟨b⟩`:
`Aprof(⟨a⟩·⟨b⟩) = Aprof(⟨ab⟩)` rejects at both slots — the loop `ab` closes
an odd block forever, violating `Fin(0)` — while `Aprof(⟨aa⟩·⟨b⟩)` accepts at
both: `(aab)^ω` closes even blocks forever.

**Lemma 4.8 (rotation, on runs).** Let `c₀, c, d ∈ EM(D)` and `q ∈ Reach`. A
left factor acts on both relations only by re-indexing the slot:

```
    st_{c₀·c}(q) = st_c(st_{c₀}(q))        and
    Aprof(c₀·c·d)(q) = Aprof(c·d·c₀)(st_{c₀}(q)).
```

Consequently, with `R` the equivalence "same `∼lin`-class and same profile
`Aprof`", the relation `∼` is the coarsest right-invariant equivalence
refining `R`, and it is a two-sided congruence on `EM₊(D)`.

*Proof.* The state identity is composition of maps. For the profile identity,
read the loop `(c₀·c·d)^ω` from `q` as `c₀·(c·d·c₀)^ω` — one rotation, the
move of Lemma 3.11 applied to a context: the factor `c₀` is carried from the
loop's front onto the stem. That prefix is read once, its marks recur never,
so the verdict is the loop verdict of `c·d·c₀` from the state the prefix
reaches (Lemma 4.6): `Aprof(c₀·c·d)(q) = A(st_{c₀}(q), c·d·c₀)
= Aprof(c·d·c₀)(st_{c₀}(q))`.

*Right-invariance.* Both halves of the seed survive a right factor: residual
equality steps through letters (`L(p) = L(p')` gives
`L(δ(p, x)) = x⁻¹L(p) = x⁻¹L(p') = L(δ(p', x))`), so `c ∼lin c'` gives
`c·d ∼lin c'·d`; and `Aprof(c·d·d') = Aprof(c'·d·d')` is an instance of
`c ∼ω c'`. Hence `∼` is right-invariant.

*Coarsest.* Suppose `c·d R c'·d` for every `d ∈ EM(D)`: the profile half over
all `d` is `c ∼ω c'`, and the `∼lin` half at `d = ⟨ε⟩` is `c ∼lin c'` — so
`c ∼ c'`. Conversely `c ∼ c'` gives `c·d ∼ c'·d` (right-invariance), hence
`c·d R c'·d` for every `d`. So `∼` is exactly "`R`-equal under every right
extension": the coarsest right-invariant equivalence refining `R`.

*Two-sided.* For a left factor `c₀`: `c₀·c ∼lin c₀·c'` since
`st_{c₀·c}(q) = st_c(st_{c₀}(q))` and `st_{c₀}(q) ∈ Reach`; and
`Aprof(c₀·c·d)(q) = Aprof(c·(d·c₀))(st_{c₀}(q))
= Aprof(c'·(d·c₀))(st_{c₀}(q)) = Aprof(c₀·c'·d)(q)` — the left factor became
a right extension. With right-invariance, `∼` is a two-sided congruence. ∎

The lemma is the load-bearing step. Maler and Staiger [MS97] display the
finitary × infinitary split — at the single slot `ι`, `∼lin` is their
classical right congruence — but their two-sided quantification stays inside
the loop test; Carton, Perrin and Pin [CPP08] saturate over context triples.
The conjugation `c₀·c·d ↦ c·d·c₀` — the rotation lemma (3.11) applied to
contexts instead of names — is the step neither takes, and it is what makes a
two-sided congruence computable with the one operation a table offers for
free. It is also an observation-table discipline — right extensions at
prefix-indexed slots — answering the obstruction Angluin and Fisman record
for ω-learning [AF21]; and a coarsest right-invariant refinement is precisely
what partition refinement computes (§4.4).

**Proposition 4.9 (prefix-independence, as a theorem not a case).** `L` is
prefix-independent (`u₀·w ∈ L ⟺ w ∈ L` for all `u₀ ∈ Σ*`, `w ∈ Σ^ω`) iff `L`
has a single residual iff `∼lin` is total. In that case all discrimination is
carried by `∼ω`.

*Proof.* Prefix-independence says every residual `u⁻¹L` equals `L`;
determinism gives one residual per reached state, all equal, so `∼lin`, which
compares residuals of reached states, is total. Conversely a single residual
class forces every prefix to preserve membership. ∎

*Example.* `EvenBlocks` is prefix-independent — deleting a finite prefix
changes neither "infinitely many `b`" nor "eventually every completed block
is even" — so its `∼lin` is total: the finitary half is blind, and the whole
of its non-LTL-ness (the `Z₂` of Ex. 4) is invisible until `∼ω` is
computed. This is the generic situation for tail properties, not a corner
case, and it is why a construction resting on residuals alone cannot even see
it.

### 4.4 The theorem: `𝓘(D) = 𝓘(L)`

The two steps assemble into the constructed invariant, and the constructed
invariant turns out to be §3.3's.

**Definition 4.10 (the constructed invariant).** `𝓘(D) := ⟨𝒮_D/∼, P(D)⟩`,
where:

- `𝒮_D/∼ : Σ⁺ → 𝒞_D := EM₊(D)/∼`, `u ↦ [⟨u⟩]`, is the **quotient stamp**:
  the composition of `𝒮_D` with the projection — surjective onto a finite
  semigroup because `∼` is a two-sided congruence (Lemma 4.8) — with letter
  map `λ(x) = [⟨x⟩]` and the fresh `[ε]` adjoined by Definition 3.1's
  completion;
- each class is keyed by the shortlex-smallest *nonempty* word whose enriched
  image lies in it — total by surjectivity of `𝒮_D`;
- `P(D)`: for each linked pair `(s, e)` of the quotient stamp
  (Definition 3.3), test the single lasso `u_s·(u_e)^ω` on `D`, `u_s` and
  `u_e` the keys; put `(s, e)` in `P(D)` iff it is accepted.

`P(D)` is the computation promised in §3.3: one keyed lasso per pair, where
Definition 3.8 ranges over all presentations of all accepted lassos. That the
single test suffices is canonicity — all lassos sharing a name share `L`'s
verdict (Theorem 3.10(i)) — once the theorem below identifies the quotient
stamp with the syntactic one.

**Theorem 4.11 (the construction is the syntactic invariant).** Let
`u, u' ∈ Σ⁺`. Then

```
    ⟨u⟩ ∼ ⟨u'⟩   ⟺   u ≈_L u'.
```

Consequently the quotient stamp *is* the syntactic stamp — the two are the
same quotient of `Σ⁺`, same classes holding the same words, same keys, same
letter map and table — and `𝓘(D) = 𝓘(L)`: byte equality with Definition 3.8,
whatever `D` presented `L`.

*Proof.* (⟸) Let `u ≈_L u'`. For `∼lin`: fix `q ∈ Reach`, say `q = δ(ι, u₀)`.
For every lasso `w`: `w ∈ L(st_{⟨u⟩}(q)) = (u₀·u)⁻¹L ⟺ u₀·u·w ∈ L ⟺` (linear
shape) `u₀·u'·w ∈ L ⟺ w ∈ L(st_{⟨u'⟩}(q))`; two regular ω-languages agreeing
on all lassos are equal [PP04, Ch. I, Cor. 9.8], so the residuals are equal
at every slot. For `∼ω`: fix `q = δ(ι, u₀) ∈ Reach` and `d ∈ EM(D)`; `EM(D)`
is letter-generated, so `d = ⟨v₀⟩` for some `v₀ ∈ Σ*`, and `u·v₀` is
nonempty. By the collapse (Lemma 4.6), `Aprof(⟨u⟩·d)(q) = A(q, ⟨u·v₀⟩)` is
the verdict of `u₀·(u·v₀)^ω`, which by the ω-power shape equals the verdict
of `u₀·(u'·v₀)^ω`, which is `Aprof(⟨u'⟩·d)(q)`.

(⟹) Let `⟨u⟩ ∼ ⟨u'⟩`; both shapes of Definition 3.7 must be checked. Linear:
for `u₀ ∈ Σ*` and a lasso `w`, with `q := δ(ι, u₀) ∈ Reach`:
`u₀·u·w ∈ L ⟺ w ∈ L(st_{⟨u⟩}(q))`, and `∼lin` equates that residual with
`L(st_{⟨u'⟩}(q))` — one verdict with `u'` in place of `u`. ω-power: for
`u₀, v₀ ∈ Σ*`, with `q := δ(ι, u₀)`: the verdict of `u₀·(u·v₀)^ω` is
`Aprof(⟨u⟩·⟨v₀⟩)(q)` (Lemma 4.6), and `∼ω` at `d = ⟨v₀⟩` equates it with
`Aprof(⟨u'⟩·⟨v₀⟩)(q)`, the verdict of `u₀·(u'·v₀)^ω`.

The components now match one by one. The equivalence says the two stamps
`𝒮_D/∼` and `𝒮_L` have the same kernel, so they are the same quotient of
`Σ⁺`: each class holds exactly the same nonempty words, the shortlex keys
coincide, the letter maps agree on the letters, and both tables are induced
by the same concatenation. For the pair sets: linked pairs correspond, and
`P(D)`'s single keyed test answers membership in `L(D) = L` — by canonicity
(Theorem 3.10(i)) exactly `P(L)`'s content at that pair. Identical components,
identical keys: with the shortlex naming of §3.3's byte-equality remark,
`𝓘(D) = 𝓘(L)` byte for byte — the unique isomorphism `θ` of
Theorem 3.10(ii) is the identity. ∎

**Corollary 4.12 (one language, one table).** (i) `L(𝓘(D)) = L(D)`, and
`P(D)` is saturated — Theorem 3.10 and Corollary 3.13 applied to `𝓘(L)`.
(ii) Any two deterministic complete Emerson–Lei automata recognizing one
language yield the byte-identical invariant.

*Example (canonicity, exhibited).* Compute `𝓘(D)` from the run-parity
`GF(aa)` of Ex. 2 — two states, a `Z₂` of transpositions — and again from
the **reset** presentation of Figure 2: the same two states, but each letter
sends *every* state to one place, an aperiodic transition monoid. The two
automata are not isomorphic, and their transition monoids disagree even on
whether a group is present. Both runs return the invariant of Ex. 2, byte
for byte: five classes, `9 → 5` against `6 → 5`. The transposition was pure presentation, and
Theorem 4.11's quotient is where it dies — while `Even` and `EvenBlocks`
keep their `Z₂` (Ex. 3, Ex. 4): those groups are `L`'s own.

| ![Figure 2 — the reset presentation of GF(aa)](sos_figs/img/gf_aa_reset.png) |
|:--:|

| presentation | `\|Q\|` | `a` acts by | group in transition monoid? | `\|EM₊\|` | `𝓘(GF(aa))` |
|---|:--:|---|:--:|:--:|---|
| run-parity (Ex. 2) | 2 | transposition | yes — `Z₂` | 9 | Ex. 2's drawing |
| reset (above) | 2 | reset | no — aperiodic | 6 | *byte-identical* |

*Figure 2 — canonicity, exhibited. The reset presentation of `GF(aa)`: the
same two states as Ex. 2's machine, but each letter sends every state to one
place — `a` to the "just saw `a`" state, whose `a`-self-loop carries the
mark, `b` to the other. Not isomorphic to Ex. 2's automaton, transition
monoids disagreeing even on whether a group is present, enriched semigroups
of different sizes — one byte-identical invariant out of both.*

**The algorithm.** The theorem is also the procedure. The seed `R` groups
elements of `EM₊(D)` by `∼lin`-class and profile — both read directly off
`D`: residual equality of reached states, one loop verdict per slot. Moore
refinement then splits a block whenever two members separate under a right
letter, `c·⟨x⟩ ≁ c'·⟨x⟩`, to fixpoint — at most `|EM₊(D)|` splits — and by
Lemma 4.8 the result is exactly `∼`. `P(D)` is one lasso test per candidate
linked pair. Everything downstream of `EM₊(D)` is polynomial in its size; the
size itself is the subject of §5.


## 5. Complexity

Two costs must be kept apart: building the invariant from an automaton, and
using it once built.

**Building.** The construction is dominated by the size of the enriched
semigroup: an enriched element is a vector of `|Q|` slots over the local
domain `Q × 2^Γ` (Definition 4.2), so

```
    |EM₊(D)| ≤ (|Q|·2^{|Γ|})^{|Q|},
```

and the `|Q|` in the exponent is the source of the explosion. That a wall
sits somewhere is a mathematical necessity, not an engineering apology:
deciding aperiodicity of a regular ω-language — the LTL read-off of §6 — is
PSPACE-complete, with hardness transferred from finite-word minimal-DFA
aperiodicity [CH91] and the ω upper bound from [DG08, Prop. 12.3]; the
surrounding classifications are no cheaper. Everything around the enriched
semigroup is benign by contrast: each generator acts slot-wise; the seed `R`
— residual equality of reached states, one loop verdict per slot — and the
Moore refinement of §4.4 run in time polynomial in `|EM₊(D)|` and `|Q|`; and
`P(D)` is one lasso test per linked pair. The cost is entirely the size of
`EM₊(D)`, and that size is intrinsic to the problem, not to the construction.

**Using.** Once built, the sizes change meaning: `|𝒞|` is a function of `L`
alone (Theorem 4.11) — the intrinsic complexity of the language, the
ω-analogue of the syntactic monoid's size — where `|Q|` and `|EM₊(D)|` were
functions of a presentation. The serialized invariant is `O(|𝒞|²)` table
entries plus a pair set `P ⊆ 𝒞 × 𝒞`, and every operation of §6 is a scan of
that table. The presentation debt — determinization [Saf88], then `EM₊(D)` —
is paid once, at entry; nothing downstream ever revisits the automaton.

**Symbolic prospects.** On a more optimistic note, every object and operation
here is BDD-friendly and the redundancy is high, so a symbolic approach is
likely to alleviate much of this inherent complexity. The ingredients are all
Boolean — the alphabet `2^AP`, the mark sets over `Γ`, the positive-Boolean
`Acc` — and every step is a set operation, not an arithmetic one: closing
`EM₊(D)` under composition, the two right relations of §4.3, and the
partition refinement of §4.4 are all images, fixpoints, and quotients over
sets, native to decision diagrams.


## 6. What the invariant unlocks

The invariant was built to be used. This section reads decisions off the
finished table: first the band of identity questions the semantics answers
nearly for free, then the definability frontier. Throughout, an invariant is
handled through its finite presentation `(𝒞, λ, ·, P)` under shortlex keys —
the serialized form the byte-equality remark of §3.3 announced.

### 6.1 The exportable invariant and the identity band

What the field exchanges today is a presentation — an automaton in the
Hanoi Omega-Automata (HOA) exchange format, one machine among many for its
language. The invariant serializes to
a file that *is* the language. `𝓘(GF(aa))`, in full:

```
SOS v1
ap: a
classes: 6
0 eps
1 !a
2 a
3 !a;a
4 a;!a
5 a;a
letters: !a->1 a->2
mult:
0: 0 1 2 3 4 5
1: 1 1 3 3 1 5
2: 2 4 5 2 5 5
3: 3 1 5 3 5 5
4: 4 4 2 2 4 5
5: 5 5 5 5 5 5
accept:
5 5
residuals: 1
0 eps
res-step:
0: 0 0
```

The file is the tool's export, verbatim — the one place the paper keeps the
raw letters: the alphabet is the single atom and its negation, `ap: a` with
`!a` for the paper's `b`, and keys read `x;y` for `x·y`. Classes are listed
by shortlex key, monoid convention: class `0 eps` is the adjoined `[ε]`, so
`classes: 6` counts `|𝒞| = 5` plus the basepoint. The row `c: …` of `mult`
gives `c·d` for `d` in id order; `accept` lists `P` — here the single pair
`([a·a], [a·a])`, ids `5 5`. The trailing `residuals:` block is derived
data — the right congruence, recomputable from the core, so byte equality is
unaffected; its single class exhibits `GF(aa)`'s prefix-independence.

The file decides lassos by Definition 3.5 with no further apparatus. For
`(a·b)^ω`: the stamp sends the loop to `𝒮(ab) = 4 = [a·b]`, already idempotent
(`4·4 = 4`); the empty stem gives `s = e = 4`; and `4 4` is not listed under
`accept`: rejected — no `aa` recurs.

*Example (canonicity, in bytes).* The two non-isomorphic presentations of
`GF(aa)` in §4.4 — run-parity and reset — both construct exactly this file.
Language equality of the two inputs is not tested; it is exhibited: one
language, one file.

**Proposition 6.1 (the identity band).** Let `𝓘(L) = ⟨𝒮, P⟩` and `𝓘(L')` be
syntactic invariants over `Σ`, serialized under shortlex keys. Then:

(i) *(equality)* `L = L'` iff the two serializations are byte-identical;

(ii) *(membership)* `u·v^ω ∈ L` is decided by one evaluation of `𝒮` — the
letter map `λ`, then table products — and one lookup in `P`
(Definition 3.5);

(iii) *(emptiness, universality)* `L = ∅` iff `P = ∅`, and `L = Σ^ω` iff `P`
is the set of all linked pairs of `𝒮`;

(iv) *(witness)* every `(s, e) ∈ P` yields, from its keys, the canonical
lasso `u_s·(u_e)^ω ∈ L`.

*Proof.* (i) is Theorem 3.10(ii) with the byte-equality remark: the unique
isomorphism is the identity on shortlex names. (ii) is Definition 3.5, whose
verdict is presentation-independent by Theorem 3.10(i). (iii): every linked
pair names a lasso — pick `u ∈ s`, `v ∈ e` by surjectivity: `𝒮(v)^π = e` and
`𝒮(u)·e = s` — so `P = ∅` accepts no lasso and `P` full accepts them all;
two regular ω-languages agreeing on all lassos are equal
[PP04, Ch. I, Cor. 9.8], here to `∅` and to `Σ^ω` respectively. (iv): the
presentation `(u_s, u_e)` lands on `(s, e)` — the keys are nonempty,
`𝒮(u_e) = e` is idempotent so `e^π = e`, and `𝒮(u_s)·e = s·e = s` — and
`(s, e) ∈ P` accepts it. ∎

**Proposition 6.2 (complement).** `𝓘(L̄) = ⟨𝒮_L, LP(𝒮_L) ∖ P(L)⟩`, writing
`LP(𝒮)` for the set of all linked pairs of a stamp: the complement shares
the stamp — classes, keys, letter map, table — and flips the pair set within
the linked pairs.

*Proof.* Both context shapes of Definition 3.7 are membership equivalences,
symmetric in `L` and `L̄`, so `≈_L = ≈_{L̄}` and the syntactic stamps
coincide, keys included. Every linked pair names at least one lasso (proof
of 6.1(iii)), and all lassos sharing a name share one verdict
(Theorem 3.10(i)): the names split, `P(L)` holding those whose lassos lie in
`L`, and the remaining linked pairs are exactly the names of the lassos of
`L̄` — that is, `P(L̄)`. ∎

*Remark (what the flip is, and is not).* On our deterministic Emerson–Lei
input, complementation is already cheap — dualize `Acc` on the same `D` — so
the flip claims no speedup over the input format; the expensive contrast
(`2^{Θ(n log n)}` for nondeterministic Büchi [Saf88]) belongs to
nondeterminism. The gain is the target: the flipped invariant is *already
canonical* — it is `𝓘(L̄)` itself, no re-canonicalization — and it makes a
structural fact plain: `L` and `L̄` share their entire algebra, and `P`
alone tells them apart. Equality is where the band has no automaton-level
rival: a corpus of `N` presentations deduplicates by `O(N²)` pairwise
product constructions, a corpus of serialized invariants by hashing — equal
languages, identical bytes.

### 6.2 The LTL frontier

**Theorem 6.3 (the aperiodicity cut — classical).** A regular `L ⊆ Σ^ω` is
LTL-definable iff `𝒞_L` is **aperiodic**: no class has a power cycle of
period `≥ 2` — equivalently, `c^π·c = c^π` for every `c ∈ 𝒞_L`.

The chain is LTL `=` FO[<] `=` star-free `=` aperiodic syntactic algebra
[Kam68, Tho79, DG08], the ω-transport of Schützenberger's theorem [Sch65];
see [DG08] for the consolidated account. What this paper adds is not the
theorem but the table it is read off:

**Corollary 6.4 (the decision).** On the constructed invariant `𝓘(D)`,
LTL-definability of `L(D)` is decided by finitely many table products —
compute `c^π` for each class, test `c^π·c = c^π` — and the verdict is exact
in both directions, whatever `D` presented the language, because
`𝓘(D) = 𝓘(L)` (Theorem 4.11). ∎

Canonicity is what the exactness rests on. On a non-canonical recognizer
only one direction survives: aperiodicity of `EM₊(D)` — or of the transition
monoid — is inherited by the quotient and thus *sufficient* for LTL, but a
group there proves nothing, since it can be pure presentation
(Proposition 4.5's one-state witness; `GF(aa)`'s transposition, which §4.4
kills). On the four examples: `aUGb` — `[a·b]` falls to the idempotent
`[b·a]` in one step, every power cycle has period 1: LTL. `GF(aa)` — the
`Z₂` of its presentation died in the quotient, all five classes settle with
period 1: LTL. `Even` and `EvenBlocks` — `[a]·[a] = [a·a]` and
`[a·a]·[a] = [a]`, a power cycle of period 2: a genuine group, not LTL, and
the invariant's verdict certifies it.

**A practical instance.** The Property Specification Language PSL
(IEEE 1850), with its sequential extended regular expressions (SEREs),
properly extends LTL and is the specification idiom of hardware
verification; the mod-2 counting that
takes a written property out of LTL lives *syntactically* in an even
repetition `{·}[*2]`. "Is this PSL property actually LTL?" — simpler, far
better tool-supported — is asked with no tool to answer it; it is exactly
the table check above, and `Even` and `EvenBlocks` are its minimal
witnesses.


## 7. Related work

**Arnold [Arn85].** The syntactic congruence is his: the coarsest congruence
saturating a rational ω-language, of finite index, with a recognizing
quotient — three pages from 1985, and the canonicity §3.3 inherits. What the
note does not contain is a construction: no acceptor input, no algorithm —
and forty years without either.

**Perrin–Pin [PP04]; Wilke.** The algebraic frame — ω-semigroups, linked
pairs, the lasso-density fact this paper leans on throughout — is theirs.
Wilke's axiomatization carries the identity `s·(ts)^ω = (st)^ω`; our
rotation identity `c·(dc)^π = (cd)^π·c` is its finite shadow (§3.3),
redeployed as a computation scheme rather than an axiom.

**Maler–Staiger [MS97].** They display the syntactic congruence as a
finitary × infinitary conjunction; at the single slot `ι` the finitary half
is the classical right congruence. No quotient is computed, and the
infinitary half still quantifies a two-sided context inside the loop.
§4.3's two relations are that split made right-only, and the rotation lemma
is the step the display lacks.

**Carton–Perrin–Pin [CPP08].** A recognizer that sees acceptance — Boolean
transition matrices recording path existence and accepting visits — with the
syntactic quotient reached by saturation over context triples: an example,
not a procedure. The enriched stamp plays their matrices' role on
deterministic Emerson–Lei input; the rotation lemma replaces the saturation.

**Pin–Straubing [PS05].** Stamps: comparing surjective morphisms rather than
abstract semigroups, the reason the letter map is data (§3.1). We transpose
the notion from `Σ*` to `Σ⁺`, where the ω-theory lives.

**Diekert–Gastin [DG08].** The consolidated star-free/aperiodic account, and
the PSPACE aperiodicity argument [DG08, Prop. 12.3] — a nondeterministic
on-the-fly bound that emits no algebra and no evidence. The construction
here is its evidence-producing counterpart, at the same worst-case price
(§5); their formula-extraction induction is the path §8 names for rendering.

**Learning [AF16, ABF18, AF21].** The recorded obstruction: the right
congruence alone does not characterize an ω-regular language — LTL languages
with a trivial right congruence exist [AF21] — so the field learns families
of DFAs [AF16, ABF18], presentation-dependent acceptors. The rotation lemma
reads the two-sided congruence from right extensions at prefix-indexed
slots — observation-table shaped (§8).

## 8. Perspectives

The point of an archetype is what it makes routine. Each direction below
opens on the invariant — the language itself in hand — where the
automaton-level literature left it closed or presentation-bound; each is one
claim, not a development.

**Classification beyond the LTL cut.** The acceptance index — Büchi,
co-Büchi, parity `[i, j]`, Rabin — and, subsuming it, the exact Wagner
degree are chain and superchain structure of the syntactic algebra
[CP97, CP99]: data the table carries, computable on it. The finer
first-order fragments (FO², Σ₂, until rank) likewise pair a variety
condition on `𝒞` with a topological side condition [DK09, Wilke99].

**Rendering the algebra as a formula.** On the aperiodic side, a defining
LTL formula is reachable in principle from the algebra by the
Diekert–Gastin induction [DG08]. Starting from automata, the state of the
art translates counter-free automata only [BLS22], with no route from an
arbitrary presentation — nor, without the algebra, a practical way to decide
eligibility in the first place (§6.2).

**Operating on invariants.** Equality and complement (§6.1) are the
degenerate cases of a calculus: align two stamps over one common table — the
one product-priced move — and Boolean combinations of languages become
pointwise operations on pair sets, re-canonicalized by the quotient of §4.3.
The costs concentrate where they must: the ω-rational constructors
(prefixing by a word set, ω-power) and alphabet surgery such as projection
embed powersets — determinization's price resurfacing exactly there, and
only there.

**A census of small languages.** Byte-canonicity makes the small ω-regular
*languages* enumerable: catalogued by `|𝒞|`, one item each, two items
distinct iff their files differ — where existing censuses enumerate
machines and meet each language once per presentation. A reference atlas of
the small languages, deduplicated by the invariant, becomes a well-defined
object of study.

**Learning the algebra.** The rotation lemma is an observation-table
discipline: every two-sided demand of the congruence is met by right
extensions read at prefix-indexed slots (Lemma 4.8) — rows and columns, the
shape a minimally-adequate-teacher (MAT) learner consumes. Learning the
syntactic ω-semigroup itself from
membership queries on lassos therefore looks feasible — where [AF21] records
the obstruction for right congruences and the field learns
presentation-dependent families of acceptors instead [AF16, ABF18].

**One level down: finite words.** Run on a complete DFA — final states in
place of marks — the construction degenerates to the classical syntactic
monoid: the enrichment is vacuous, the ω-power shape disappears with the
ω-words it quantified over, and the seed is already the congruence — no
rotation, no refinement. The degenerate case landing on the known answer
audits the machinery; and the same aperiodicity check of §6.2 then decides
LTLf-definability [DV13], one level down, where the same tooling gap stands.

## 9. Conclusion

For finite words, the syntactic monoid has carried the algebraic theory of
regular languages for sixty years: one finite algebra per language,
canonical, and everything readable from it. For infinite words the analogous
algebra — the syntactic ω-semigroup of Arnold — has existed since 1985 on
paper only.

The obstruction was never size alone; it was structure. A recognizer for
infinite behaviour must remember acceptance along runs, not endpoints — that
is the enrichment. And the syntactic congruence is two-sided, while
everything a finite table offers for free is right-handed — that is the
rotation lemma: a left context carries no information of its own, it only
moves the point where a right test is read. The lemma is the mathematical
core of the paper, and it stands on its own.

What a canonical form changes is the unit of discourse. Automata are
presentations: every pipeline that manipulates them manipulates a choice,
and anything read off them must first be argued independent of that choice.
The invariant is the language: equality is identity of two files, complement
flips a set of pairs, membership is a table walk, LTL-definability is the
absence of a group — and the classical taxonomy of ω-regular languages turns
into structural facts about one finite invariant. Beyond verdicts, the
invariant in hand invites operation — computing with languages, cataloguing
them,
learning them — directions that were closed at the level of presentations.
The construction of this paper reifies Arnold's phantom: the syntactic
ω-semigroup is no longer only defined — it is built.


# Worked examples

The paper's four running languages, numbered Ex. 1–4 and cited that way from
the prose, each presented on its own page along the same axes: an
**informal** description, its **ω-regular** word over the two
letters `{a, b}`, its **formula** (LTL, or PSL/SERE where mod-2 counting takes it
out of LTL), a **classification** block, its deterministic **Emerson–Lei
automaton** `D` (the input of §4), and its syntactic **invariant** `𝓘` (§3).

**The classification block.** Three verdicts head each page — facts about a
language that are usually hard to come by, here tool-computed from the page's
invariant; the procedures are out of scope of this paper. *LTL*:
definability in linear temporal logic, with its stutter sensitivity.
*Geometry*: the
rung on the safety–progress ladder of Manna and Pnueli [MP92] — safety,
guarantee, obligation, recurrence, persistence, reactivity — the coarse view
of Wagner's hierarchy [Wag79]; `properly` marks an exact position.
*Recognizer*: the weakest deterministic acceptance recognizing the language,
tied to the geometry by Landweber's theorem [Lan69] — DBA / DCA abbreviate
deterministic Büchi / co-Büchi automata, accepting when marked transitions
recur / eventually cease. Each page is self-contained. The formulas live over the single atom
`a`, so the second letter is the literal `!a`; **throughout this paper the
LTL/PSL forms are read with `b` in place of `!a`.**

**Reading key.** `D` is drawn deterministic, complete, transition-based: each
edge carries a letter — `a`, `b`, or `a,b` for the both-letters (true) edge —
and the coloured bullets on an edge are its acceptance marks, the condition
`Acc` named in the header. `𝓘` is the stamp core of §3.1: vertices are the
congruence classes, edges are the letter-action table, and the letter map `λ`
and the saturated set of accepting linked pairs `P` are listed beneath; the
label `𝒞` abbreviates a self-loop carrying every class.

**The construction table.** Each page closes on the table §4 builds from its
`D`: one row per element `⟨w⟩` of the enriched semigroup `EM₊(D)`
(Definition 4.2), named by its shortlex-least word. The `at q` columns hold
the pair `(δ(q, w), mk(q, w))` — where reading `w` from state `q` lands, and
the marks collected on the way: the row *is* the element. The `·⟨b⟩`,
`·⟨a⟩` columns name the element reached by extending on the right by one
letter — the step the construction iterates, and the table is closed: every
entry names a row. The last column is the class the row folds onto in the
quotient of §4.3.



# Example 1 — `aUGb`

| aspect | `aUGb` |
|---|---|
| Language (informal) | "a finitely until always b" |
| ω-regular | `a*·b^ω` |
| LTL | `a U G !a` |
| LTL | **yes** — stutter insensitive |
| Geometry | obligation, properly level 2: a Boolean combination of safety and guarantee, no single one suffices |
| Recognizer | weak deterministic — one automaton serves as both DBA and DCA |
| Det. Emerson–Lei `D` | ![aUGb automaton](sos_figs/img/aUGb.png) |
| Invariant `𝓘` | ![aUGb invariant](sos_core_figs/img/core_F0_astar_bomega_b_pairs.png) |

`[a]` is the class of finite words `a⁺` only containing `a`. `[a·b]` is words of
the form `a⁺b⁺` that start with a sequence of `a`'s then a sequence of `b`'s.
`[b]` is the class `b⁺` of words only containing `b`. `[b·a]` the class of words
that have met an `a` after `b` (somewhere in the word).

Acceptance is in two pairs: `([b], [b])` representing the word `b^ω`, and
`([a·b], [b])` the words of the form `a⁺·b^ω`. Note that these are classes:
`([a·b], [b])` represents `a·b^ω`, `ab·b^ω`, `aabbb·b^ω`, `ab·bbb^ω`, …

The LTL row is a read-off of the drawing: every power sequence
settles with period 1 — `[a]`, `[b]`, `[b·a]` are idempotent, and `[a·b]`
falls onto the idempotent `[b·a]` in one step — so the invariant is
aperiodic: LTL.

Reading a lasso (Definition 3.5). Take `ababba·b^ω`. The loop first:
`𝒮(b) = [b]` is already idempotent, so `e = [b]`. The stem:
`𝒮(ababba) = ([a]·[b])·([a]·[b])·([b]·[a]) = [a·b]·[a·b]·[b·a]` (an arbitrary
parenthesizing, since `𝒮` is associative); `[a·b]·[a·b] = [b·a]`, and `[b·a]`
right-extended by anything is still `[b·a]`, so `𝒮(ababba) = [b·a]`. The
queried stem is `s = 𝒮(u)·e = [b·a]·[b]`, and absorption simplifies it away:
`s = [b·a]`. The name `([b·a], [b])` is not in `P`, so the lasso `ababba·b^ω`
is not in the language.

**Construction (§4).** `|EM₊| = 9` elements folding onto the `|𝒞| = 4`
classes above. The excess the quotient removes is all mark bookkeeping the
language ignores:
`⟨b⟩ ≠ ⟨b·b⟩` and `⟨a·b⟩ ≠ ⟨a·b·b⟩` differ solely in a mark already
collected — membership never counts `b`'s — and the four dead behaviors
`⟨b·a⟩, ⟨b·b·a⟩, ⟨a·b·a⟩, ⟨a·b·b·a⟩`, kept apart in `EM₊` by which slots
happened to see the mark on the way to the sink, fold onto the single zero
`[b·a]`.

| ⟨w⟩ | at 0 | at 1 | at 2 | ·⟨b⟩ | ·⟨a⟩ | → class |
|---|---|---|---|---|---|---|
| `⟨b⟩` | `(0, {0})` | `(0, ∅)` | `(2, ∅)` | `⟨b·b⟩` | `⟨b·a⟩` | `[b]` |
| `⟨a⟩` | `(2, ∅)` | `(1, ∅)` | `(2, ∅)` | `⟨a·b⟩` | `⟨a⟩` | `[a]` |
| `⟨b·b⟩` | `(0, {0})` | `(0, {0})` | `(2, ∅)` | `⟨b·b⟩` | `⟨b·b·a⟩` | `[b]` |
| `⟨b·a⟩` | `(2, {0})` | `(2, ∅)` | `(2, ∅)` | `⟨b·a⟩` | `⟨b·a⟩` | `[b·a]` |
| `⟨a·b⟩` | `(2, ∅)` | `(0, ∅)` | `(2, ∅)` | `⟨a·b·b⟩` | `⟨a·b·a⟩` | `[a·b]` |
| `⟨b·b·a⟩` | `(2, {0})` | `(2, {0})` | `(2, ∅)` | `⟨b·b·a⟩` | `⟨b·b·a⟩` | `[b·a]` |
| `⟨a·b·b⟩` | `(2, ∅)` | `(0, {0})` | `(2, ∅)` | `⟨a·b·b⟩` | `⟨a·b·b·a⟩` | `[a·b]` |
| `⟨a·b·a⟩` | `(2, ∅)` | `(2, ∅)` | `(2, ∅)` | `⟨a·b·a⟩` | `⟨a·b·a⟩` | `[b·a]` |
| `⟨a·b·b·a⟩` | `(2, ∅)` | `(2, {0})` | `(2, ∅)` | `⟨a·b·b·a⟩` | `⟨a·b·b·a⟩` | `[b·a]` |


# Example 2 — `GF(aa)`

| aspect | `GF(aa)` |
|---|---|
| Language (informal) | "infinitely many aa : an a followed by an a." |
| ω-regular | `((a\|b)*·a·a)^ω` |
| LTL | `G F(a ∧ X a)` |
| LTL | **yes** — stutter sensitive |
| Geometry | recurrence, properly `Gδ`: strictly above every obligation |
| Recognizer | DBA-proper — deterministic Büchi suffices, no deterministic co-Büchi can |
| Det. Emerson–Lei `D` | ![GF(aa) run-parity automaton](sos_figs/img/gf_aa.png) |
| Invariant `𝓘` | ![GF(aa) invariant](sos_core_figs/img/core_F1_gf_aa_pairs.png) |

`[a]` is the class of words that start with an `a`, have never seen two `a`'s
in a row, and most recently read an `a`. `[a·b]` is the class of words that
start with an `a`, most recently read a `b`, and so far contain only isolated
`a`'s — no block of two. The last letter is what separates them: an `a` may
pair with the next letter, a `b` cannot. These two classes cycle: extending
`[a·b]` by `[a]` returns to `[a]` (`[a·b]·[a] = [a]`, forgetting that `b`'s
were ever seen), and `[a]·[b] = [a·b]` goes back. The cycle is *not* a
counter: the trip around it multiplies by `[b]` then by `[a]`, two different
classes, and no single class powers around it — `[a·b]·[a·b] = [a·b]`, while
`[a]·[a] = [a·a]` leaves. Every power sequence settles with period 1 (though
only at exponent 2: `[a]` needs one step to stabilize), so the invariant is
aperiodic — the LTL row's verdict, read off the drawing.

`[a·a]` is the class of all words that contain at least one block of two
consecutive `a`'s. It is a sink: once two `a`'s in a row have been seen the
stamp classifier is content, and any further extension is absorbed and stays
in `[a·a]`. In the drawing it is entered by reading one more `a` from the two
classes that end on an unpaired `a`: `[a]`, and `[b·a]` on the `b`-side.

Since acceptance asks for infinitely many such blocks, the only accepted pair
is `([a·a], [a·a])`, and it is only logical that `[a·a]` be the loop
component. Less obvious is that the stem component must also be `[a·a]`: this
is always arrangeable by the rotation lemma, which pushes letters of the
looped part back into the prefix until the prefix, too, is seen to carry two
consecutive `a`'s. That is the canonical presentation of all accepted lassos
of the language here.

The classes `[b]` and `[b·a]` play the same waiting-room game for words that
start with a `b` — `[b]` on a last-read `b`, `[b·a]` on an unpaired `a` —
until the first block of two `a`'s is met.

Reading a lasso (Definition 3.5). Take `(aab)^ω`, the empty-stem presentation
`(ε, aab)`. The loop first: `𝒮(aab) = [a]·[a]·[b] = [a·a]·[b] = [a·a]` — the
sink absorbs — already idempotent, so `e = [a·a]`. The stem is empty, and
absorption lands the query in `𝒞` anyway: `s = 𝒮(ε)·e = [ε]·[a·a] = [a·a]`.
The name `([a·a], [a·a])` is in `P`: accepted — an `aa` closes in every turn
of the loop. Against it, `(ab)^ω`: the loop `𝒮(ab) = [a·b]` is idempotent,
`s = [ε]·[a·b] = [a·b]`, and `([a·b], [a·b])` is not in `P`: rejected — the
`a`'s stay isolated forever.

**Construction (§4).** `|EM₊| = 9` elements folding onto the `|𝒞| = 5`
classes above. The enrichment at work: `⟨a⟩` and `⟨a·a·a⟩` have the *same*
state part — the transposition — and differ only in marks, the longer word
having closed an `aa`; the transition monoid identifies them, the enrichment
keeps them apart. The fold then does the reverse service: four "contains
`aa`" behaviors — `⟨a·a⟩, ⟨b·a·a⟩, ⟨a·a·a⟩, ⟨b·a·a·a⟩`, distinct as
vectors — collapse onto the sink `[a·a]`, and `⟨a·b·a⟩` rejoins `[a]` — the
`Z₂` visible in the `at` columns is pure presentation, and §4.4 is where it
dies.

| ⟨w⟩ | at 0 | at 1 | ·⟨b⟩ | ·⟨a⟩ | → class |
|---|---|---|---|---|---|
| `⟨b⟩` | `(0, ∅)` | `(0, ∅)` | `⟨b⟩` | `⟨b·a⟩` | `[b]` |
| `⟨a⟩` | `(1, ∅)` | `(0, {0})` | `⟨a·b⟩` | `⟨a·a⟩` | `[a]` |
| `⟨b·a⟩` | `(1, ∅)` | `(1, ∅)` | `⟨b⟩` | `⟨b·a·a⟩` | `[b·a]` |
| `⟨a·b⟩` | `(0, ∅)` | `(0, {0})` | `⟨a·b⟩` | `⟨a·b·a⟩` | `[a·b]` |
| `⟨a·a⟩` | `(0, {0})` | `(1, {0})` | `⟨b·a·a⟩` | `⟨a·a·a⟩` | `[a·a]` |
| `⟨b·a·a⟩` | `(0, {0})` | `(0, {0})` | `⟨b·a·a⟩` | `⟨b·a·a·a⟩` | `[a·a]` |
| `⟨a·b·a⟩` | `(1, ∅)` | `(1, {0})` | `⟨a·b⟩` | `⟨b·a·a⟩` | `[a]` |
| `⟨a·a·a⟩` | `(1, {0})` | `(0, {0})` | `⟨b·a·a⟩` | `⟨a·a⟩` | `[a·a]` |
| `⟨b·a·a·a⟩` | `(1, {0})` | `(1, {0})` | `⟨b·a·a⟩` | `⟨b·a·a⟩` | `[a·a]` |


# Example 3 — `Even`

| aspect | `Even` |
|---|---|
| Language (informal) | "even number of a's met when first b encountered" |
| ω-regular | `(aa)*·b·(a\|b)^ω` |
| PSL/SERE | `{ {a[*2]}[*] ; !a }!` |
| LTL | **no** |
| Geometry | guarantee, properly open: a good finite prefix decides |
| Recognizer | reachability — an accepting sink to reach, the weakest acceptance there is |
| Det. Emerson–Lei `D` | ![Even automaton](sos_figs/img/even.png) |
| Invariant `𝓘` | ![Even invariant](sos_core_figs/img/core_F2_even_pairs.png) |

`[a]` is the class of words that have seen only an odd number of `a`'s (and no
`b` yet); `[a·a]` the class of words that have seen only an even — and
nonzero — number of `a`'s, again with no `b` yet. Reading one more `a` flips
the parity, so `[a]` and `[a·a]` form a small strongly connected component
(SCC) —
the parity counter. We leave it only by reading a `b`. The counter is a
genuine period-2 power cycle — `[a]·[a] = [a·a]`, `[a·a]·[a] = [a]` — a
group: the LTL row's *no*, read off the drawing.

Where the `b` lands us records the parity at that moment. From `[a]`, an odd
count, we go to `[a·b]`: the class of all words with an odd number of `a`'s
before the first `b` — a sequence of `a`'s was left unpaired. It is a sink: any
extension stays in the same class. From `[a·a]`, an even count, we go to `[b]`.

`[b]` is the most subtle class to interpret. It coalesces not only `b⁺`, as in
the earlier figures, but also any even number of `a`'s followed by at least one
`b`. Once `[b]` is reached the stamp classifier is content, and `[b]` absorbs any
suffix.

Acceptance therefore fixes the stem to `[b]`: an even number of `a`'s until a
`b` is met. The loop, on the other hand, can be essentially anything — `[a·b]`
and `[a·a]` canonically cover the cases where it extends by `a`'s — giving the
three accepted pairs `([b], [b])`, `([b], [a·a])`, `([b], [a·b])`.

Reading a lasso (Definition 3.5). Take `aaaba·(ba)^ω`. The loop first:
`𝒮(ba) = [b]·[a] = [b]`, already idempotent, so `e = [b]`. The stem:
`𝒮(aaaba) = ([a]·[a]·[a])·([b]·[a]) = [a]·[b] = [a·b]`, and the queried stem
is `s = 𝒮(u)·e = [a·b]·[b] = [a·b]` — the sink absorbs. The name
`([a·b], [b])` is not in `P`: rejected, an odd run of `a`'s was left
unpaired. A *different* lasso, one `a` shorter — stem `aaba`, an even
prefix — lands elsewhere: `𝒮(aaba) = ([a]·[a])·([b]·[a]) = [a·a]·[b] = [b]`,
`s = [b]·[b] = [b]`, and `([b], [b])` is accepted.

One lasso, two names. A word's verdict never depends on its presentation, but
its name can. Present `b·(ab)^ω` as written: the loop's class
`𝒮(ab) = [a]·[b] = [a·b]` is the sink, already idempotent, and the stem is
absorbed, `s = [b]·[a·b] = [b]`:
the name `([b], [a·b])`, accepted. Rotate one letter onto the stem —
`b·(ab)^ω = ba·(ba)^ω`, the same ω-word — and the loop's class is now
`𝒮(ba) = [b]·[a] = [b]`, also idempotent, with `s = [b]·[b] = [b]`: the name
`([b], [b])`, accepted again. Two distinct pairs naming the one ω-word,
connected by a single rotation — and both in `P`, as saturation (§3.3)
demands.

**Construction (§4).** `|EM₊| = 6` elements folding onto the `|𝒞| = 4`
classes above. The delicate row is `⟨a·a⟩`: its state part is the *identity
map* — two `a`'s return every state to itself — and only the mark collected
at the accepting sink (state `0`) keeps it apart from `⟨ε⟩`. The quotient
keeps them apart too, as §3.1 demands: `[a·a]` is a neutral class of
nonempty words — its row and column in `𝒞`'s table move nothing — while
`[ε]` is the fresh basepoint: the neutral-vs-identity distinction of §3.1,
exhibited by the machine. The fold itself merges the mark-only splits
`⟨b⟩, ⟨b·b⟩` and `⟨a·b⟩, ⟨a·b·b⟩`.

| ⟨w⟩ | at 0 | at 1 | at 2 | at 3 | ·⟨b⟩ | ·⟨a⟩ | → class |
|---|---|---|---|---|---|---|---|
| `⟨b⟩` | `(0, {0})` | `(3, ∅)` | `(0, ∅)` | `(3, ∅)` | `⟨b·b⟩` | `⟨b·b⟩` | `[b]` |
| `⟨a⟩` | `(0, {0})` | `(2, ∅)` | `(1, ∅)` | `(3, ∅)` | `⟨a·b⟩` | `⟨a·a⟩` | `[a]` |
| `⟨b·b⟩` | `(0, {0})` | `(3, ∅)` | `(0, {0})` | `(3, ∅)` | `⟨b·b⟩` | `⟨b·b⟩` | `[b]` |
| `⟨a·b⟩` | `(0, {0})` | `(0, ∅)` | `(3, ∅)` | `(3, ∅)` | `⟨a·b·b⟩` | `⟨a·b·b⟩` | `[a·b]` |
| `⟨a·a⟩` | `(0, {0})` | `(1, ∅)` | `(2, ∅)` | `(3, ∅)` | `⟨b⟩` | `⟨a⟩` | `[a·a]` |
| `⟨a·b·b⟩` | `(0, {0})` | `(0, {0})` | `(3, ∅)` | `(3, ∅)` | `⟨a·b·b⟩` | `⟨a·b·b⟩` | `[a·b]` |


# Example 4 — `EvenBlocks`

| aspect | `EvenBlocks` |
|---|---|
| Language (informal) | "Infinitely often b, and all sequences of a are eventually even in length" |
| ω-regular | `(a\|b)*·((aa)*·b)^ω` |
| PSL/SERE | `GF!a ∧ FG(!a → X{ {a[*2]}[*] ; !a }!)` |
| LTL | **no** |
| Geometry | reactivity: strictly above recurrence and persistence |
| Recognizer | parity `{0,1,2}`, proper — a genuine Rabin pair; neither DBA nor DCA |
| Det. Emerson–Lei `D` | ![EvenBlocks automaton](sos_figs/img/evenblocks.png) |
| Invariant `𝓘` | ![EvenBlocks invariant](sos_core_figs/img/core_F3_evenblocks_pairs.png) |

As in `Even`, `[a]` and `[a·a]` are the classes of words that have seen only
`a`'s, in odd and even count — the same parity SCC, the same period-2
power cycle (`[a]·[a] = [a·a]`, `[a·a]·[a] = [a]`): a genuine group, and the
LTL row's *no*, read off the drawing. A `b` exits the SCC:
from an even count to `[b]`, from an odd count to `[a·b]` — but unlike
`Even`, where the first `b` settled everything, no exit is final here.

`[b]` agglomerates the words made of even `a`-blocks and `b`'s — the leading
block even as read, every block closed inside the word even, a trailing run
of `a`'s allowed if even — containing at least one `b`. The cycle
`[b]`/`[b·a]` grows a trailing block: an unpaired trailing `a` sits in
`[b·a]`, its partner returns to `[b]`. `[a·b]` and `[a·b·a]` are their twins
for a leading block left odd — `[a·b·a]` reads the even-block cycle entered
mid-block, an open run of `a`'s at both ends. The last class, `[b·a·b]` (key
word `bab`), holds the words that have *completed* an odd block, closed by
`b`'s on both sides: it is the two-sided zero, absorbing every extension.
Absorbing is not dead: the language is prefix-independent — no finite prefix
ever decides membership — and the zero reappears below as an accepting stem.

Acceptance is six pairs:

```
P = { ([b], [b]),      ([a·b], [b]),      ([b·a·b], [b]),
      ([b·a], [a·b·a]), ([b·a·b], [a·b·a]), ([a·b·a], [a·b·a]) }
```

— exactly the linked pairs whose loop is `[b]` or `[a·b·a]`, the two readings
of "only even blocks, and `b`'s, forever": block-aligned, or entered
mid-block. The stems are everything such a loop absorbs — every class
carrying at least one `b`, the zero included: finitely many completed odd
blocks are forgiven, prefix independence again. The two all-`a` classes
appear in no pair: the loop holds infinitely many `b`'s, rotation pushes one
of them back into the stem, so a canonical stem must carry a `b` — and `[a]`,
`[a·a]` cannot.

Reading a lasso (Definition 3.5). Take `aabaab·(baa)^ω`. The loop first:
`𝒮(baa) = ([b]·[a])·[a] = [b·a]·[a] = [b]`, already idempotent, so `e = [b]`.
The stem, grouped `(aa)·(baab)` and reduced on each side before conjoining:
`(aa) = [a]·[a] = [a·a]` is the parity cycle;
`(baab) = ([b]·[a])·([a]·[b]) = [b·a]·[a]·[b] = [b]·[b] = [b]` runs the
`[b]`/`[b·a]` cycle, closing on an even count. Conjoining,
`[a·a]·[b] = [b]`, so `𝒮(aabaab) = [b]`. The queried stem is
`s = 𝒮(u)·e = [b]·[b] = [b]`, and the name `([b], [b])` is in `P`:
accepted — every block the word completes is even, and `b`'s recur.

**Construction (§4).** `|EM₊| = 16` elements folding onto the `|𝒞| = 7`
classes above. The first row is the collision §3.1's fresh basepoint is
built for: `⟨a·a⟩ = ⟨ε⟩` — two `a`'s toggle back and collect nothing — so
the identity is itself an image of nonempty words, `EM₊` is the whole
monoid, and the neutral class `[a·a]` is genuine language data. The language
lives entirely in the marks: six elements — `⟨b·a·b⟩` and its five mark
variants below it — are one behavior for `L` and fold onto the zero
`[b·a·b]`. And unlike `GF(aa)`'s page, the parity `Z₂` *survives* the
fold — `[a]·[a] = [a·a]`, `[a·a]·[a] = [a]` — this group is `L`'s own.

| ⟨w⟩ | at 0 | at 1 | ·⟨b⟩ | ·⟨a⟩ | → class |
|---|---|---|---|---|---|
| `⟨a·a⟩` | `(0, ∅)` | `(1, ∅)` | `⟨b⟩` | `⟨a⟩` | `[a·a]` |
| `⟨b⟩` | `(0, {1})` | `(0, {0})` | `⟨b·b⟩` | `⟨b·a⟩` | `[b]` |
| `⟨a⟩` | `(1, ∅)` | `(0, ∅)` | `⟨a·b⟩` | `⟨a·a⟩` | `[a]` |
| `⟨b·b⟩` | `(0, {1})` | `(0, {0,1})` | `⟨b·b⟩` | `⟨b·b·a⟩` | `[b]` |
| `⟨b·a⟩` | `(1, {1})` | `(1, {0})` | `⟨b·a·b⟩` | `⟨b⟩` | `[b·a]` |
| `⟨a·b⟩` | `(0, {0})` | `(0, {1})` | `⟨a·b·b⟩` | `⟨a·b·a⟩` | `[a·b]` |
| `⟨b·b·a⟩` | `(1, {1})` | `(1, {0,1})` | `⟨b·b·a·b⟩` | `⟨b·b⟩` | `[b·a]` |
| `⟨b·a·b⟩` | `(0, {0,1})` | `(0, {0})` | `⟨b·b·a·b⟩` | `⟨b·a·b·a⟩` | `[b·a·b]` |
| `⟨a·b·b⟩` | `(0, {0,1})` | `(0, {1})` | `⟨a·b·b⟩` | `⟨a·b·b·a⟩` | `[a·b]` |
| `⟨a·b·a⟩` | `(1, {0})` | `(1, {1})` | `⟨a·b·a·b⟩` | `⟨a·b⟩` | `[a·b·a]` |
| `⟨b·b·a·b⟩` | `(0, {0,1})` | `(0, {0,1})` | `⟨b·b·a·b⟩` | `⟨b·b·a·b·a⟩` | `[b·a·b]` |
| `⟨b·a·b·a⟩` | `(1, {0,1})` | `(1, {0})` | `⟨b·a·b⟩` | `⟨b·a·b⟩` | `[b·a·b]` |
| `⟨a·b·b·a⟩` | `(1, {0,1})` | `(1, {1})` | `⟨b·b·a·b⟩` | `⟨a·b·b⟩` | `[a·b·a]` |
| `⟨a·b·a·b⟩` | `(0, {0})` | `(0, {0,1})` | `⟨b·b·a·b⟩` | `⟨a·b·a·b·a⟩` | `[b·a·b]` |
| `⟨b·b·a·b·a⟩` | `(1, {0,1})` | `(1, {0,1})` | `⟨b·b·a·b⟩` | `⟨b·b·a·b⟩` | `[b·a·b]` |
| `⟨a·b·a·b·a⟩` | `(1, {0})` | `(1, {0,1})` | `⟨a·b·a·b⟩` | `⟨a·b·a·b⟩` | `[b·a·b]` |


## References

*Imported from the legacy `../sos_constructed.md` bibliography (which carries
page data from the read library), plus [PS05] and [BLS22] added by this
restructure. Entries marked (†) are not cited by any drafted section
(s0–s7) — prune at freeze.*

- **[ABF18]** D. Angluin, U. Boker, D. Fisman. *Families of DFAs as acceptors
  of ω-regular languages.* LMCS 14(1) 2018.
- **[AF16]** D. Angluin, D. Fisman. *Learning regular omega languages.* TCS
  650 (2016) 57–72.
- **[AF21]** D. Angluin, D. Fisman. *Regular ω-languages with an informative
  right congruence.* Inf. Comput. 278 (2021).
- **[Arn85]** A. Arnold. *A syntactic congruence for rational ω-languages.*
  TCS 39 (1985) 333–335.
- **[BLS22]** U. Boker, K. Lehtinen, S. Sickert. *On the translation of
  automata to linear temporal logic.* FoSSaCS 2022, LNCS 13242, 140–160.
- **[CH91]** S. Cho, D. T. Huynh. *Finite-automaton aperiodicity is
  PSPACE-complete.* TCS 88 (1991) 99–116.
- **[CP97]** O. Carton, D. Perrin. *Chains and superchains for ω-rational
  sets, automata and semigroups.* Int. J. Algebra Comput. 7(6) (1997) 673–695.
- **[CP99]** O. Carton, D. Perrin. *The Wagner hierarchy.* Int. J. Algebra
  Comput. 9(5) (1999) 597–620.
- **[CPP08]** O. Carton, D. Perrin, J.-É. Pin. *Automata and semigroups
  recognizing infinite words.* In *Logic and Automata: History and
  Perspectives*, Amsterdam University Press, 2008.
- **[DG08]** V. Diekert, P. Gastin. *First-order definable languages.* In
  *Logic and Automata*, 2008.
- **[DK09]** V. Diekert, M. Kufleitner. *Fragments of first-order logic
  over infinite words.* STACS 2009; Theory Comput. Syst. 48(3) (2011) 486–516.
- **[DV13]** G. De Giacomo, M. Y. Vardi. *Linear temporal logic
  and linear dynamic logic on finite traces.* IJCAI 2013.
- **[Kam68]** H. Kamp. *Tense Logic and the Theory of Linear Order.* PhD
  thesis, UCLA, 1968.
- **[Kla94]** (†) N. Klarlund. *A homomorphism concept for ω-regularity.*
  CSL 1994.
- **[Lan69]** L. H. Landweber. *Decision problems for ω-automata.* Math.
  Systems Theory 3(4) (1969) 376–384.
- **[MP71]** (†) R. McNaughton, S. Papert. *Counter-Free Automata.* MIT
  Press, 1971.
- **[MP92]** Z. Manna, A. Pnueli. *The Temporal Logic of Reactive and
  Concurrent Systems: Specification.* Springer, 1992.
- **[MS97]** O. Maler, L. Staiger. *On syntactic congruences for
  ω-languages.* TCS 183 (1997) 93–112 (rev. 2008).
- **[Per84]** (†) D. Perrin. *Recent results on automata and infinite words.*
  MFCS 1984.
- **[PP04]** D. Perrin, J.-É. Pin. *Infinite Words: Automata, Semigroups,
  Logic and Games.* Elsevier, 2004.
- **[PS05]** J.-É. Pin, H. Straubing. *Some results on C-varieties.*
  RAIRO — Theoretical Informatics and Applications 39(1) (2005) 239–262.
- **[PW13]** (†) S. Preugschat, T. Wilke. *Effective characterizations of
  simple fragments of temporal logic using Carton–Michel automata.* LMCS
  9(2:08) (2013).
- **[Saf88]** S. Safra. *On the complexity of ω-automata.* FOCS 1988, 319–327.
- **[Sch65]** M. P. Schützenberger. *On finite monoids having only trivial
  subgroups.* Information and Control 8 (1965) 190–194.
- **[SW08]** (†) V. Selivanov, K. W. Wagner. *Complexity of topological
  properties of regular ω-languages.* Fund. Inform. 83(1–2) (2008).
- **[Tho79]** W. Thomas. *Star-free regular sets of ω-sequences.*
  Information and Control 42 (1979) 148–156.
- **[Wag79]** K. Wagner. *On ω-regular sets.* Information and Control 43
  (1979) 123–177.
- **[Wilke99]** T. Wilke. *Classifying discrete temporal properties.*
  STACS 1999, LNCS 1563, 32–46.


