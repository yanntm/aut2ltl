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

> **Definition 3.1 (stamp over an alphabet).** A **stamp** over `Σ` is a
> surjective semigroup morphism
>
> ```
>     𝒮 : Σ⁺ → 𝒞
> ```
>
> onto a finite semigroup `𝒞`, whose elements are the **classes**, written `[u]`
> for any nonempty word `u ∈ Σ⁺` with `𝒮(u) = [u]`. The stamp extends to all
> finite words by adjoining a **fresh** identity `[ε]`:
>
> ```
>     M := 𝒞 ∪ {[ε]},     𝒮(ε) := [ε],
> ```
>
> making `𝒮 : Σ* → M` a surjective monoid morphism.

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

---

| ![Figure 1a — the stamp core](../sos_core_figs/img/core_F0_astar_bomega_b_pairs.png) | ![Figure 1b — the monoid completion](../sos_core_figs/img/core_F0_astar_bomega.png) |
|:--:|:--:|

**Figure 1.** `𝓘(aUGb)`, drawn twice. Left — the stamp core: the complete data
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
further drawings use the left form.

---

*Example (the letter map is data).* Over `Σ = {a, b, c}`, the language
`(a|c)*·b^ω` has the same four classes and the same table: `a` and `c` are
interchangeable everywhere, `λ(a) = λ(c) = [a]`. Only `λ` tells the two stamps
apart — which is precisely why [PS05] compare stamps rather than semigroups.

In a finite semigroup the powers `c, c², c³, …` of any element cannot all be
distinct, so the sequence is eventually periodic and contains exactly one
idempotent [PP04].

> **Definition 3.2 (idempotent power; exponent of a stamp).** Let
> `𝒮 : Σ⁺ → 𝒞` be a stamp and `c ∈ 𝒞`. The **idempotent power** of `c` is the
> unique idempotent among its powers — the one `cⁿ` (`n ≥ 1`) with `cⁿ·cⁿ = cⁿ`.
> An **exponent** of `𝒮` is an integer `π ≥ 1` such that `c^π` is the idempotent
> power of *every* `c ∈ 𝒞`; one exists since `𝒞` is finite (e.g. `|𝒞|!`), and
> which multiple is chosen never matters. We fix one and write `c^π`.

`c^π` is an honest power, computed on the table alone, and the notation
deliberately avoids `^ω` — in this paper `^ω` always means infinite
repetition, and nothing here is infinite. This idempotent is exactly what
stands in for the ω-power of the two-sorted recognizers (§2): iterating a
loop's class until it stabilizes is how "forever" is read on a finite table.

*Example.* On Figure 1 (`aUGb`), `[a]`, `[b]`, `[b·a]` are idempotent, hence
their own idempotent powers. `[a·b]` is not: `[a·b]·[a·b] = [b·a]` — gluing two
words of `a⁺b⁺` puts an `a` after a `b` — so `[a·b]^π = [b·a]`: looping "`a`'s
then `b`'s" is exactly as dead as slipping once.

> **Definition 3.3 (linked pair of classes).** Let `𝒮 : Σ⁺ → 𝒞` be a stamp. A
> **linked pair** of `𝒮` is a pair of classes `(s, e) ∈ 𝒞 × 𝒞` with `e·e = e`
> and `s·e = s`: the loop class `e` is idempotent, and it absorbs the stem class
> `s`.

*Example.* On Figure 1 (`aUGb`), `([a·b], [b])` is linked: `[b]` is idempotent
and `[a·b]·[b] = [a·b]`. The pair `([a], [b])` is not: `[a]·[b] = [a·b] ≠ [a]`
— a stem that ends before `b`'s begin is not absorbed by them.

> **Definition 3.4 (pair set; invariant over an alphabet).** Let `𝒮` be a stamp
> over `Σ`. A **pair set** over `𝒮` is a finite set `P ⊆ 𝒞 × 𝒞` of linked pairs
> of `𝒮`. An **invariant** over `Σ` is a pair `𝓘 = ⟨𝒮, P⟩` of a stamp and a pair
> set over it.

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

> **Definition 3.5 (lasso membership; language of an invariant).** Let `𝓘 = ⟨𝒮, P⟩` be an
> invariant over `Σ`, and let `w ∈ Σ^ω` be a lasso with presentation
> `(u, v) ∈ Σ* × Σ⁺` (Definition 2.1), `w = u·v^ω`. Set
>
> ```
>     e := 𝒮(v)^π,     s := 𝒮(u)·e.
> ```
>
> Then `w ∈ L(𝓘)` iff `(s, e) ∈ P`.

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

> **Definition 3.6 (name of a lasso).** Let `𝒮` be a stamp over `Σ`. A linked
> pair `(s, e)` of `𝒮` **names** the lasso `w` when some presentation
> `(u, v) ∈ Σ* × Σ⁺` of `w` lands on it: `𝒮(v)^π = e` and `𝒮(u)·e = s`.

Definition 3.5 thus queries one name of `w` — the one its given presentation
lands on. A lasso bears several names: already `(u, v)` and `(u·v, v)` present
the same ω-word and may land on distinct pairs. Nothing yet says all names of
one lasso receive one verdict from `P`; that the semantics is nevertheless
well defined is the subject of the next section.
