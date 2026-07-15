## 3. The syntactic ω-semigroup as an invariant `𝓘(L)`

The definition of the invariant

```
    𝓘(L) = ⟨𝒮, P⟩
```

splits in two parts: a **stamp** `𝒮`, classifying the finite words, and an
**acceptance layer** `P`, a set of accepted linked pairs. We define the stamp
first.

### 3.1 Syntax: the invariant `𝓘 = ⟨𝒮, P⟩`

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

Two consequences of the definition, used silently everywhere: **`[ε]` is
isolated** — the identity is fresh, so `𝒮(u) = [ε]` only for `u = ε` — and
**`𝒞` absorbs** — `M` differs from `𝒞` by exactly that basepoint, so a product
touching a class of words stays in `𝒞`. Surjectivity says every class is the
class of at least one nonempty word.

Freshness is the canonical choice, not a convenience: adjoining a *new* unit is
the universal way of making a semigroup a monoid, and it is deliberate that
this holds even when `𝒞` owns an internal neutral element. Such an element is a
class of nonempty words invisible to the language — a genuine behavior,
loopable, with verdicts of its own — while `[ε]` is the basepoint "no word at
all", which can never be looped; `Even` (§3.4) exhibits both at once, kept
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
the materialization this paper manipulates: the classical object is the
morphism, what the field has never had in hand is its table.

*Notation (representatives).* A class is denoted by one of its member words,
`[a·b]` for the class of `ab`; any member may serve, and nothing below depends
on the choice. For readability, figures and examples use the shortlex-least
member (shortest, then alphabetically first) — a naming convention, not data.

*Example.* The stamp of `aUGb = a*·b^ω` (Figure 1) has four classes,
`𝒞 = {[a], [b], [a·b], [b·a]}`, with `𝒮(a) = [a]`, `𝒮(b) = [b]`. The table is
the drawn graph: `[a]·[b] = [a·b]`, `[a·b]·[a] = [b·a]`, and `[b·a]` is a
two-sided zero — the dead words, once an `a` follows a `b`. These are §2's
four kinds, wearing their shortlex names.

| ![Figure 1a — the stamp core](../sos_core_figs/img/core_F0_astar_bomega_b.png) | ![Figure 1b — the monoid completion](../sos_core_figs/img/core_F0_astar_bomega.png) |
|:--:|:--:|

*Figure 1 — `𝓘(aUGb)`, drawn twice. Left — the stamp core, the presentation
`(𝒞, λ, ·)` of Definition 3.1: the four classes are the vertices, the table
the edges — following an edge multiplies on the right by its label, parallel
edges fused into one arrow listing their labels, and the label `𝒞` on the
zero's self-loop abbreviating all four classes at once: the picture of
absorption. Beneath the drawing, the letter map `λ` and the pair set `P`
(Definition 3.4): with the graph, the complete data of the invariant. Right —
the monoid completion `M = 𝒞 ∪ {[ε]}` of the same stamp: the fresh identity
drawn in, adding exactly its row — the edges leaving `[ε]`, where the reading
of a word starts — and its column, `[ε]` joining every self-loop. An identity
moves nothing: eliding it loses no edge worth reading, and all further figures
use the left form.*

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
convention, and it is the form the implementation consumes (Part B).

*Example.* On Figure 1 (`aUGb`), present `aab·b^ω` as `(aab, b)` or as
`(aabb, bb)`: both land on the name `([a·b], [b])` — here even the name is
stable. That is a feature of `aUGb`, not of the theorem: `Even` (§3.4) names
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
accepting stems absorb their loops — so saturation of `P(aUGb)` is immediate. A
conjugacy that genuinely pairs two names, and the saturation check it forces,
is worked on `Even` in §3.4.

### 3.4 The examples, as invariants

- The three languages and their figures carry over from the legacy draft —
  the figures already draw no `[ε]` vertex, and the letter actions, laws, and
  pair sets are all in `𝒞`. Class counts quoted as `|𝒞|`: `aUGb` 4, `GF(aa)`
  5, `Even` 4, `EvenBlocks` 7.
- `Even`: `[a·a]` is an *internal* neutral element of `𝒞` — nonempty,
  loopable, with its own verdicts (`(aa)^ω = a^ω` is rejected) — kept apart
  from the basepoint `[ε]`: the worked illustration of §3.1's freshness
  discussion.
- The saturation check on `a^ω` and the hand-reading block (membership by one
  query, monochrome-cycle test for LTL) carry over; aperiodicity is a property
  of `𝒞`.
