### 3.3 Canonicity: the invariant of `L`

Definitions 3.5 and 3.6 leave two debts. A lasso bears many names — nothing
yet says `P` treats them alike. And the query evaluates whatever invariant it
is handed — nothing yet singles out, among the many invariants denoting one
language, a canonical one. Both debts are paid at once by building the
invariant from `L` itself, one class per behavior `L` can distinguish. The
classifying relation is Arnold's [Arn85]. A finite word sits in a lasso either
in the stem or inside the loop, and interchangeability must hold in both
positions:

> **Definition 3.7 (syntactic congruence of an ω-language [Arn85]).** Let
> `L ⊆ Σ^ω` be a regular ω-language. Two nonempty words `u, u' ∈ Σ⁺` are
> **syntactically congruent** for `L`, written `u ≈_L u'`, when they are
> interchangeable in both context shapes:
>
> ```
>     (linear)     ∀ u₀ ∈ Σ*,  ∀ lasso w ∈ Σ^ω :   u₀·u·w ∈ L     ⟺   u₀·u'·w ∈ L
>     (ω-power)    ∀ u₀, v₀ ∈ Σ*               :   u₀·(u·v₀)^ω ∈ L  ⟺   u₀·(u'·v₀)^ω ∈ L
> ```

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

> **Definition 3.8 (syntactic stamp; syntactic invariant of `L`).** Let
> `L ⊆ Σ^ω` be a regular ω-language, and let `𝒞_L := Σ⁺/≈_L` be its finite
> semigroup of congruence classes. The **syntactic stamp** of `L` is the
> quotient morphism
>
> ```
>     𝒮_L : Σ⁺ → 𝒞_L
> ```
>
> — surjective by construction, a semigroup morphism because `≈_L` is a
> two-sided congruence — with letter map `λ(x) = [x]` and the induced
> table `[u]·[v] := [u·v]`. The **syntactic invariant** of `L` is
> `𝓘(L) := ⟨𝒮_L, P(L)⟩`, where `P(L)` collects the names of the lassos of `L`:
>
> ```
>     P(L) := { (𝒮_L(u)·e, e)  :  u ∈ Σ*,  v ∈ Σ⁺,  e = 𝒮_L(v)^π,  u·v^ω ∈ L }.
> ```

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

> **Lemma 3.9 (substitution of congruent words).** Let `u, u', v, v' ∈ Σ⁺` with
> `u ≈_L u'` and `v ≈_L v'`. Then `u·v^ω ∈ L ⟺ u'·v'^ω ∈ L`.

*Proof.* Swap the loop: the ω-power shape of `v ≈_L v'`, at `u₀ = u` and
`v₀ = ε`, gives `u·v^ω ∈ L ⟺ u·v'^ω ∈ L`. Swap the stem: the linear shape of
`u ≈_L u'`, at `u₀ = ε` and `w = v'^ω`, gives `u·v'^ω ∈ L ⟺ u'·v'^ω ∈ L`. ∎

> **Theorem 3.10 (canonicity of the syntactic invariant).** Let `L ⊆ Σ^ω` be a
> regular ω-language.
>
> (i) All lassos sharing a name share `L`'s verdict; consequently, on `𝓘(L)`,
> lasso membership (Definition 3.5) is membership in `L` itself — every
> presentation of every lasso receives `L`'s verdict — and `L(𝓘(L)) = L`.

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
convention, and it is the form the serialized invariant of §5.2 puts to work.

*Example.* On Figure 1 (`aUGb`), present `aab·b^ω` as `(aab, b)` or as
`(aabb, bb)`: both land on the name `([a·b], [b])` — here even the name is
stable. That is a feature of `aUGb`, not of the theorem: `Even` (Ex. 3) names
one lasso through two distinct pairs, and canonicity (Theorem 3.10(i)) is what
forces those two names to one verdict.

> **Definition 3.11 (denoting invariant).** An invariant `𝓘 = ⟨𝒮, P⟩` over `Σ`
> **denotes** the regular ω-language `L ⊆ Σ^ω` when every presentation of every
> lasso receives `L`'s verdict from lasso membership (Definition 3.5): for all
> `(u, v) ∈ Σ* × Σ⁺`,
>
> ```
>     u·v^ω ∈ L    ⟺    (𝒮(u)·e, e) ∈ P,       e = 𝒮(v)^π.
> ```

Theorem 3.10(i) states that `𝓘(L)` denotes `L`. It is not the only invariant
that does — §4 builds another, finer, from an automaton — but it is the
coarsest, and §3.5 proves that every other is carried onto it by partition
refinement.
