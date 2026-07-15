# Materializing the Syntactic ω-Semigroup — restructure sketch (§3 drafted, rest bulleted)

*Sketch — 2026-07-15. Section 3 written out around the stamp presentation
(semigroup stamp on `Σ⁺`, free monoid completion, comprehension-defined `P`);
all other sections as adjustment bullets against the current draft.*

## 1. Introduction

- Unchanged in substance; contribution 1 rephrased: the object is reified as an
  invariant `𝓘 = ⟨𝒮, P⟩` — a **stamp** `𝒮` classifying the nonempty finite words
  and an acceptance layer `P` of linked pairs over it.
- Fix the stale internal pointers (canonicity is §3.3, construction §4).

## 2. Background

- Unchanged through the ω-semigroup definitions: lassos, monoids/morphisms,
  the two-sorted recognizer, idempotent power, linked pairs, one-lasso-many-names.
- The paragraph "the second sort will not be carried" now lands one step further:
  §3 keeps a *semigroup* of word classes — the empty word is not a citizen of the
  ω-theory, and the identity the computations use is adjoined freely, not carved
  out of `Σ*`.
- Notation split, held paper-wide: `^ω` means infinite — `Σ^ω`, `v^ω`, `S_ω`, and
  the second-sort ω-power `φ₊(v)^ω` inside this section's recollection of the
  classical two-sorted recognizer. The idempotent power in a finite semigroup is
  written `s^π` (§3.1), following the ω-words tradition [PP04]; no algebra
  element ever wears `^ω`.
- `aUGb` and Figure 1/1′ unchanged; the figures already draw no `[ε]` vertex, which
  §3.1 now justifies once and for all (a freely adjoined identity has no incoming
  edges).

## 3. The syntactic ω-semigroup as an invariant `𝓘(L)`

The definition of the invariant

```
    𝓘(L) = ⟨𝒮, P⟩
```

splits in two parts: a **stamp** `𝒮`, classifying the nonempty finite words, and
an **acceptance layer** `P`, a set of accepted linked pairs. We define the stamp
first.

### 3.1 Syntax: the invariant `𝓘 = ⟨𝒮, P⟩`

**Definition 3.1 (stamp).** A **stamp** over `Σ` is a surjective semigroup
morphism

```
    φ : Σ⁺ → S
```

onto a finite semigroup `S`. The elements of `S` are the **classes**, written
`[w]` for any word `w` with `φ(w) = [w]`; surjectivity says every class is the
image of at least one nonempty word.

The notion is Pin and Straubing's [PS05], where a stamp is a surjective morphism
from a free monoid onto a finite monoid; we transpose it to the free semigroup
`Σ⁺`, since the empty word plays no role in the ω-theory — no ω-word has an
empty trace. Because `Σ⁺` is the free semigroup over `Σ`, a stamp is determined
by its restriction to the letters: writing `λ := φ|_Σ : Σ → S`, the morphism `φ`
is the unique extension of `λ`,

```
    φ(x₁x₂⋯xₙ) = λ(x₁)·λ(x₂)·⋯·λ(xₙ),
```

and conversely every map `λ : Σ → S` whose image generates `S` extends to a
stamp. A stamp is therefore *finitely presented* by the data

```
    𝒮 = (S, λ, ·)
```

— the finite semigroup, the letter map, the multiplication table — and this
presentation is the materialization this paper manipulates: the classical object
is the morphism, what the field has never had in hand is its table.

*Notation (representatives).* A class is denoted by one of its member words,
`[a·b]` for the class of `ab`; any member may serve, and nothing below depends on
the choice. For readability, figures and examples use the shortlex-least member
(shortest, then alphabetically first) — a naming convention, not data.

*Example.* The stamp of `aUGb = a*·b^ω` (Figure 1) has four classes,
`S = {[a], [b], [a·b], [b·a]}`, with `λ(a) = [a]`, `λ(b) = [b]`. The table is the
drawn graph: `[a]·[b] = [a·b]`, `[a·b]·[a] = [b·a]`, and `[b·a]` is a two-sided
zero — the dead words, once an `a` follows a `b`.

*Example (the letter map is data).* Over `Σ = {a, b, c}`, the language
`(a|c)*·b^ω` has the same four classes and the same table: `a` and `c` are
interchangeable everywhere, `λ(a) = λ(c) = [a]`. Only `λ` tells the two stamps
apart — which is precisely why [PS05] compare stamps rather than semigroups.

**The adjoined identity.** Stems may be empty, so the computations need a value
for the empty word. We work in the **free monoid completion**

```
    C := S ∪ {[ε]},
```

the monoid obtained by adjoining a *fresh* identity `[ε]` to `S` — fresh even
when `S` already contains a neutral element. This is the canonical completion:
freely adjoining a unit is the universal way of making a semigroup a monoid (the
left adjoint of the forgetful functor), and its unit is always a new element.
The **fold** of the stamp is the extension of `φ` to all finite words,

```
    ⟦·⟧ : Σ* → C,     ⟦ε⟧ := [ε],     ⟦w⟧ := φ(w)  for w ∈ Σ⁺,
```

a monoid morphism. Two facts, both by construction rather than by axiom:

- **`[ε]` is isolated**: `⟦u⟧ = [ε]` iff `u = ε` — the adjoined identity is
  fresh, so no nonempty word folds to it;
- **`S` absorbs**: for `c ∈ C` and `s ∈ S`, `c·s ∈ S` and `s·c ∈ S` — a product
  touching a class of words stays one.

The distinction the freshness preserves is semantic, not clerical: a stamp may
own an *internal* neutral element — a class of nonempty words that are invisible
to `L`, a genuine behavior, loopable, with its own verdict — and `[ε]`, the
basepoint "no word at all", which can never be looped. `Even` (§3.4) exhibits
both at once, kept apart.

**The idempotent power.** In the finite semigroup `S` the powers `s, s², s³, …`
of any class cannot all be distinct, so the sequence is eventually periodic and
contains a unique **idempotent**, the one power `sⁿ` (`n ≥ 1`) with
`sⁿ·sⁿ = sⁿ`: the **idempotent power** of `s`. Fix an **exponent** `π` of `S`:
an integer `n ≥ 1` such that `sⁿ` is idempotent for *every* `s ∈ S` — one
exists since `S` is finite (e.g. `|S|!`), and which multiple is chosen never
matters. We write `s^π` for the idempotent power, following the ω-words
tradition [PP04]: it is an honest power, computed on the table alone, and the
notation deliberately avoids `^ω` — in this paper `^ω` always means infinite
repetition, and nothing here is infinite. This idempotent is exactly what
stands in for the ω-power of the two-sorted recognizers (§2): iterating a
loop's class until it stabilizes is how "forever" is read on a finite table.

*Example.* On Figure 1 (`aUGb`), `[a]`, `[b]`, `[b·a]` are idempotent, hence
their own idempotent powers. `[a·b]` is not: `[a·b]·[a·b] = [b·a]` — gluing two
words of `a⁺b⁺` puts an `a` after a `b` — so `[a·b]^π = [b·a]`: looping "`a`'s
then `b`'s" is exactly as dead as slipping once.

**Definition 3.2 (pair set; invariant).** A **pair set** over a stamp `𝒮` is a
finite set `P ⊆ S × S` of pairs of classes. An **invariant** is a pair
`𝓘 = ⟨𝒮, P⟩`.

The typing is deliberate: `P` lives in `S × S`, entirely inside the semigroup.
The adjoined `[ε]` appears in no pair — the acceptance layer speaks only of
words.

*Example.* Figure 1 carries its pair set beneath the drawing:
`P = { ([b], [b]), ([a·b], [b]) }`.

### 3.2 Semantics: the language of an invariant

An invariant decides lassos with the data it carries and nothing else: the fold
assigns each finite word its class — stem and loop alike — and `P` lists the
pairs that accept.

**Definition 3.3 (language of an invariant).** Let `𝓘 = ⟨𝒮, P⟩` be an invariant
over `Σ`, and `w = u·v^ω ∈ Σ^ω` a lasso, its loop `v` nonempty. Let
`e := ⟦v⟧^π ∈ S` be the idempotent power of the fold of the loop, and
`s := ⟦u⟧·e ∈ S` — the stem's fold, absorbed by the loop. Then

```
    w ∈ L(𝓘)   iff   (s, e) ∈ P.
```

Both coordinates land in `S`: `e` is the idempotent power of a class of nonempty
words, and `s = ⟦u⟧·e` is in `S` by absorption even when the stem is empty. The
query never mentions `[ε]` — nothing that happens forever has an empty trace,
and here that is a typing fact, not a lemma.

*Example.* On Figure 1 (`aUGb`), the two verdicts. For `aab·b^ω`: the loop folds
to `[b]`, already idempotent, so `e = [b]`; the stem folds to `[a·b]` and
`[a·b]·[b] = [a·b]`. The pair `([a·b], [b])` is in `P`: accepted. For
`ba·(ab)^ω`: the loop folds to `[a·b]`, not idempotent — its square `[b·a]` is —
so `e = [b·a]`; the stem folds to `[b·a]` and `[b·a]·[b·a] = [b·a]`. The pair
`([b·a], [b·a])` is not in `P`: rejected.

The definition reads `w` through one presentation `(u, v)`, and a lasso has
many. That the verdict does not depend on the presentation chosen is not
automatic; it is the subject of the next section.

### 3.3 Canonicity: the invariant of `L`

Definition 3.3 leaves two debts. It reads a lasso through one presentation, and
a lasso has many — nothing yet says all presentations receive one verdict. And
it evaluates whatever invariant it is handed — nothing yet singles out, among
the many invariants denoting one language, a canonical one. Both debts are paid
at once by building the invariant from `L` itself, one class per behavior `L`
can distinguish. The classifying relation is Arnold's [Arn85]. A finite word
sits in a lasso either in the stem or inside the loop, and interchangeability
must hold in both positions:

**Definition 3.4 (syntactic congruence [Arn85]).** Two words `u, v ∈ Σ⁺` are
**syntactically congruent** for `L`, written `u ≈_L v`, when they are
interchangeable in both context shapes:

```
    (linear)     ∀ x, y ∈ Σ*, t ∈ Σ⁺ :   x·u·y·t^ω ∈ L  ⟺  x·v·y·t^ω ∈ L
    (ω-power)    ∀ x, y ∈ Σ*          :   x·(u·y)^ω ∈ L  ⟺  x·(v·y)^ω ∈ L
```

The linear shape mutates the stem — a finite change, a loop `t` appended to
complete the lasso; the ω-power shape mutates inside the loop, where the change
recurs forever. `≈_L` is a two-sided congruence on `Σ⁺` of finite index for
regular `L` [Arn85], and the coarsest relation with these interchange
properties — the first of two senses in which the quotient below is minimal.
Note the domain: the relation lives on `Σ⁺`. The empty word is not comparable —
the ω-power shape at `y = ε` would have to evaluate `ε^ω`, which is not an
ω-word — and the quotient below is a semigroup, as Definition 3.1 requires.

*Example.* On Figure 1 (`aUGb`), from `L = a*·b^ω` alone: `a ≉_L b` by the
ω-power shape at `x = y = ε` — `a^ω ∉ L`, `b^ω ∈ L`; `ab ≉_L ba` by the linear
shape at `x = y = ε`, `t = b`; and `a ≈_L aa` — membership in `L` never counts
`a`'s. The quotient `Σ⁺/≈_L` has exactly four classes — `a⁺`, `b⁺`, `a⁺b⁺` and
the dead words — the four vertices of Figure 1.

**Definition 3.5 (the invariant of `L`).** `𝓘(L) := ⟨𝒮(L), P(L)⟩`, where:

- `𝒮(L)` is the quotient morphism `φ_L : Σ⁺ → Σ⁺/≈_L` — surjective by
  construction, a semigroup morphism because `≈_L` is a two-sided congruence: a
  stamp, the **syntactic stamp** of `L`, presented by `λ(x) := [x]` and the
  induced table `[u]·[v] := [u·v]`;
- `P(L)` collects the **names of the accepted lassos**:

```
    P(L) := { (⟦u⟧·e, e)  :  u ∈ Σ*,  v ∈ Σ⁺,  e = ⟦v⟧^π,  u·v^ω ∈ L }.
```

The definition of `P(L)` makes no choice: it ranges over *all* presentations of
*all* accepted lassos and records the pair each one folds to. In particular no
representative is consulted — testing a single lasso per pair, keyed by chosen
representatives, is how `P(L)` is *computed* (§4), and its correctness is
Theorem 3.7's content, not part of the definition.

*Example.* Figure 1 is `𝓘(aUGb)` — §2 called the drawing a syntactic
ω-semigroup, and Definition 3.5 is that claim made precise. The accepted lassos
are those eventually reading only `b`'s; their stems fold into `{[b], [a·b]}`
after absorption, their loops settle on `[b]`, and
`P(L) = { ([b], [b]), ([a·b], [b]) }`, the pair set printed beneath the figure.

Say a pair `(s, e) ∈ S × S` **names** the lasso `u·v^ω` when some presentation
folds to it — `⟦v⟧^π = e` and `⟦u⟧·e = s`. `P(L)` is, verbatim, the set of names
of accepted lassos; the debt is that a pair may name several lassos, and a lasso
bears several names. The two context shapes were tailored to exactly this:

**Lemma 3.6 (substitution).** If `u ≈_L u'` and `v ≈_L v'` (all four words
nonempty), then `u·v^ω ∈ L ⟺ u'·v'^ω ∈ L`.

*Proof.* Swap the loop: the ω-power shape of `v ≈_L v'`, at `x = u` and `y = ε`,
gives `u·v^ω ∈ L ⟺ u·v'^ω ∈ L`. Swap the stem: the linear shape of `u ≈_L u'`,
at `x = y = ε` and `t = v'`, gives `u·v'^ω ∈ L ⟺ u'·v'^ω ∈ L`. ∎

**Theorem 3.7 (canonicity).** For every regular ω-language `L`:

(i) all lassos sharing a name share `L`'s verdict; consequently, on `𝓘(L)`, the
query of Definition 3.3 answers membership in `L` itself — every presentation of
every lasso receives `L`'s verdict — and `L(𝓘(L)) = L`;

(ii) `𝓘` is a **complete invariant**: `L = L'` iff there is a semigroup
isomorphism `θ : S(L) → S(L')` with `θ ∘ φ_L = φ_{L'}` and
`(θ×θ)(P(L)) = P(L')` — and such a `θ`, when it exists, is unique.

*Proof.* (i) Let `(u, v)` present the lasso `w`, `v` nonempty, and let `(s, e)`
be the name it folds to: `e = ⟦v⟧^π`, `s = ⟦u⟧·e`. The idempotent power is an
honest power: rewrite `w` on the presentation `(u·v^π, v^π)` — the same
ω-word — whose coordinates are nonempty (the loop `v` is), so the fold is the
quotient morphism on them: `s = [u·v^π]` and
`e = [v^π]` as congruence classes. Now take any two lassos named `(s, e)` and
rewrite each this way: their rewritten stems are congruent (both lie in the
class `s`), their loops congruent (both in `e`), and Lemma 3.6 gives them one
verdict. So all lassos named `(s, e)` agree with each other — and `P(L)`
contains `(s, e)` iff that shared verdict is acceptance. The query on any
presentation of any lasso `w` therefore answers `w ∈ L`; and since lassos
determine a regular language [PP04, Ch. I, Cor. 9.8], `L(𝓘(L)) = L`.

(ii) If `L = L'` the two constructions are literally the same. Conversely, a
`θ` commuting with the stamps carries names to names and `P(L)` onto `P(L')`,
so the two queries agree on every lasso; by (i) each answers its own language,
hence `L = L'`. Uniqueness: `θ` is forced on every class by
`θ([u]) = θ(φ_L(u)) = φ_{L'}(u)`, and `φ_L` is surjective. ∎

*Remark (byte equality).* Naming every class by its shortlex-least member turns
the unique isomorphism of (ii) into the identity on names: two regular
ω-languages are equal iff the serialized invariants — classes, `λ`, table, `P`,
under shortlex naming — are byte-identical. Canonicity is the mathematics; byte
equality is that mathematics plus a naming convention, and it is the form the
implementation consumes (Part B).

*Example.* On Figure 1 (`aUGb`), present `aab·b^ω` as `(aab, b)` or as
`(aabb, bb)`: both fold to the name `([a·b], [b])` — here even the name is
stable. That is a feature of `aUGb`, not of the theorem: `Even` (§3.4) names one
lasso through two distinct pairs, and Theorem 3.7(i) is what forces those two
names to one verdict.

§2 promised a reconciliation: one lasso, many names. The constraint that
Theorem 3.7 puts on a pair set has a single generator. **A loop may be
rotated**: a factor carried from the loop's front onto the stem leaves the
ω-word unchanged, `u·g·(h·g)^ω = u·(g·h)^ω` — and rotation is the one move that
changes a lasso's name.

**Lemma 3.8 (rotation).** Let `𝒮` be a stamp and `s, g, h ∈ S` with
`s·(gh)^π = s`. Then `(s·g, (hg)^π)` is a linked pair, and some lasso is named
by both `(s, (gh)^π)` and `(s·g, (hg)^π)`.

*Proof.* First the identities in `S`. Associativity gives `g·(hg)^m = (gh)^m·g`
for every `m ≥ 1`; at `m = π` — one exponent serving `gh` and `hg` alike —
this reads `g·(hg)^π = (gh)^π·g`. Hence
`(s·g)·(hg)^π = s·(gh)^π·g = s·g`: the rotated pair is linked.
By surjectivity of the stamp pick nonempty words `w, p, q` with `φ(w) = s`,
`φ(p) = g`, `φ(q) = h`, and consider the single ω-word `α := w·(pq)^ω`. The
presentation `(w, (pq)^π)` folds to `(s·(gh)^π, (gh)^π) = (s, (gh)^π)`; the
presentation `(w·p, (qp)^π)` — the same ω-word, `w·(pq)^ω = w·p·(qp)^ω` — folds
to `(s·g·(hg)^π, (hg)^π) = (s·g, (hg)^π)`. So `α` is named by both pairs. ∎

Every element named in the lemma lies in `S`, and surjectivity hands each a
nonempty word: no corner case guards the identity, because `[ε]` is not there
to be rotated through.

Call two linked pairs **conjugate** when rotations connect them — the
equivalence generated by `(s, (gh)^π) ∼ (s·g, (hg)^π)`; the notion is classical
[PP04, Ch. II, Prop. 2.6]. Stem extension is the degenerate rotation
`g = h = ⟦v⟧`: the loop's value is unchanged and the stem absorbs one turn —
why `(u, v)` and `(uv, v)` may name one lasso by two pairs.

**Definition 3.9 (saturation).** A pair set `P` over a stamp is **saturated**
when it is closed under conjugacy: for all `s, g, h ∈ S` with `s·(gh)^π = s`,

```
    (s, (gh)^π) ∈ P   ⟺   (s·g, (hg)^π) ∈ P.
```

**Corollary 3.10.** `P(L)` is saturated.

*Proof.* By Lemma 3.8 some lasso `α` is named by both pairs, and `P(L)` is the
set of names of accepted lassos whose verdicts, by Theorem 3.7(i), agree
name-by-name: each of the two pairs is in `P(L)` iff `α ∈ L` — both in or both
out. ∎

Saturation is the one law an acceptance layer must obey, and it is
table-checkable: finitely many triples `(s, g, h)`, each one product and two
lookups. The rotation identity itself is classical: our
`g·(hg)^π = (gh)^π·g` is the finite shadow of Wilke's axiom
`s·(ts)^ω = (st)^ω` [PP04, Ch. II, Thm 5.1] — his `^ω` is the genuine
second-sort ω-power, ours a power in `S` — and conjugacy of
linked pairs organizes the classical theory [PP04, Ch. II, Prop. 2.8, Cor. 2.9].
What this paper draws from it is a different service: rotation turns two-sided
demands about `L` into right-only computations — the engine of the construction
(§4), where it collapses Arnold's two-sided congruence to a right-invariant
refinement computable on a table.

*Example.* On Figure 1 (`aUGb`), every conjugacy class is a singleton —
whatever factor a rotation moves, the dead class absorbs it, and the two
accepting stems absorb their loops — so saturation of `P(aUGb)` is immediate. A
conjugacy that genuinely pairs two names, and the saturation check it forces,
is worked on `Even` in §3.4.

### 3.4 The examples, as invariants

- The three languages and their figures are **unchanged** — the figures already
  draw no `[ε]` vertex, and the letter actions, laws, and pair sets are all in
  `S`. Class counts are now quoted as `|S|`: `aUGb` 4, `GF(aa)` 5, `Even` 4,
  `EvenBlocks` 7 (each `+1` for the completion `C` if one insists on counting
  the basepoint).
- `Even`'s paragraph gains its point rather than losing it: `[a·a]` is an
  *internal* neutral element of `S` — a class of nonempty, loopable words with
  its own verdicts (`(aa)^ω = a^ω` is rejected) — kept apart from the basepoint
  `[ε]` by the free completion. The old "the adjoined identity keeps `[ε]`
  apart" remark becomes the worked illustration of §3.1's freshness discussion.
- The saturation check on `a^ω` (`(ε, a)` vs `(a, a)` naming `([a·a],[a·a])`
  and `([a],[a·a])`) carries over verbatim.
- The hand-reading block (membership by one fold, monochrome-cycle test for
  LTL, saturation) carries over verbatim; aperiodicity is a property of `S`
  (the adjoined `[ε]` sits in no nontrivial power cycle).

## 4. The construction: from an automaton to `𝓘(L)`

- §4.1 (Emerson–Lei input) unchanged.
- §4.2: the enriched object becomes the **enriched stamp**: `w ↦ ⟨w⟩` restricted
  to `Σ⁺` is a surjective semigroup morphism onto `EM₊(D)`, the enriched images
  of nonempty words; `⟨ε⟩` is the same free completion on the automaton side.
  Lemma 4.3 (skeleton), Corollary 4.4 (refines Arnold), Proposition 4.5
  (enrichment necessary) unchanged in substance.
- §4.3: the two right relations, the rotation-on-runs lemma, and
  prefix-independence unchanged; all quantifications already range over images
  of nonempty words, which is now the native carrier.
- §4.4: Definition 4.10's key-testing (one lasso `w_s·(w_e)^ω` per candidate
  linked pair, keys = shortlex-least *nonempty* members — total, since every
  class of `S` has one by surjectivity) is now explicitly the *computation* of
  `P`, its correctness delegated to Theorem 3.7. Theorem 4.11 restated at the
  same altitude as canonicity: `⟨u⟩ ∼ ⟨v⟩ ⟺ u ≈_L v`, hence `𝓘(D)` and `𝓘(L)`
  agree up to the unique isomorphism commuting with the stamps — the identity
  under shortlex naming, byte equality as the serialization remark.
- The `GF(aa)` two-presentations exhibit and the algorithm paragraph unchanged
  (`|EM₊|` counts drop by one: the identity is no longer counted).

## 5. Complexity

- As current bullets: split invariant cost (quadratic in `|S|`) from
  construction cost (exponential in `|Q|` worst case); `|S|` the intrinsic
  complexity of `L`; BDD-friendliness note. Quantitative reporting standardizes
  on `|S|` — no conditional `±1` across the corpus.

## 6. What the invariant unlocks

- As current bullets: identity band (byte equality, complement `P ↦ P^c` within
  the linked pairs of `S`, emptiness, membership by one fold); LTL-definability
  as aperiodicity of `S`; taxonomy table condensed; the proxy suggestion, one
  paragraph.

## 7. Related work

- As current bullets; add [PS05] (stamps — the presentation vehicle, and the
  reason `λ` is part of the object).

## 8. Conclusion

- As current bullets; the rotation lemma stands alone as the mathematical core.
