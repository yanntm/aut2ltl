### 3.5 Canonicalization: from any well-formed invariant to the syntactic one

Canonicity (Theorem 3.10) made the syntactic invariant unique. This
subsection makes it reachable: from any well-formed invariant `𝓘 = ⟨𝒮, P⟩` —
writing `L := L(𝓘)` throughout (Proposition 3.15) — the syntactic invariant
`𝓘(L)` is computed by merging classes, nothing else. What stands in the way
is inherited from Arnold: two classes may merge exactly when their words are
interchangeable in every context, and interchangeability is a two-sided
demand — a word sits in a lasso between a left context and a right one —
while the one operation the table of `𝒞` offers for free is multiplication
on the right. The rotation lemma closes this gap in its second service: the
first (§3.4) forced saturation; the second converts every left demand into a
right computation.

> **Definition 3.16 (membership tests).** Let `𝓘 = ⟨𝒮, P⟩` be a well-formed
> invariant, `M = 𝒞 ∪ {[ε]}` its completion. For a **slot** `d ∈ M` and an
> idempotent `f ∈ 𝒞`, the **membership tests** on classes `c ∈ 𝒞` are
>
> ```
>     Λ(d, f)(c) := [ (d·c·f, f) ∈ P ]            (linear test)
>     Ω(d)(c)    := [ (d·c^π, c^π) ∈ P ]          (ω test)
> ```

Each test poses one lasso membership question to a class: by
Proposition 3.15, `Λ(d, f)(c)` is the membership in `L` of every lasso whose
stem reads `d` then `c` and whose loop settles on `f`, and `Ω(d)(c)` the
membership of looping `c` itself from `d`. The typing is §3.1's absorption
once more: both queried pairs are linked — `(d·c·f)·f = d·c·f` and
`(d·c^π)·c^π = d·c^π` — and lie in `𝒞 × 𝒞`; slots range over the completion,
`[ε]` serving as the empty context, while the tested class is a class of
nonempty words: no test loops the basepoint.

> **Lemma 3.17 (the tests characterize the congruence).** Let `u, u' ∈ Σ⁺`
> with `c = 𝒮(u)`, `c' = 𝒮(u')`. Then `u ≈_L u'` iff for every slot `d ∈ M`,
> every `g ∈ M`, and every idempotent `f ∈ 𝒞`:
>
> ```
>     Λ(d, f)(c·g) = Λ(d, f)(c'·g)      and      Ω(d)(c·g) = Ω(d)(c'·g).
> ```

*Proof.* A linear context `u₀·_·w` of Definition 3.7, its lasso `w` presented
`(y, t)`, evaluates on `u` to the membership of `u₀·u·y·t^ω` in `L`, which is
the bit of its queried name — the pair `(d·c·g·f, f)` at `d = 𝒮(u₀)`,
`g = 𝒮(y)`, `f = 𝒮(t)^π` — that is, to `Λ(d, f)(c·g)`; an ω-power context
`u₀·(_·v₀)^ω` evaluates to `Ω(d)(c·g)` at `g = 𝒮(v₀)`. Surjectivity runs the
translation both ways: every element of `M` is the value of a finite word,
`[ε]` of the empty one, and every idempotent `f` is `𝒮(t)^π` for any `t` with
`𝒮(t) = f`. ∎

> **Definition 3.18 (test equivalence).** The **test equivalence** `∼` on `𝒞`
> is the relation of Lemma 3.17: `c ∼ c'` iff all membership tests agree on
> `c·g` and `c'·g`, for every `g ∈ M`.

> **Lemma 3.19 (left invariance).** The test equivalence is a two-sided
> congruence on `𝒞`.

*Proof.* Right invariance is Definition 3.18's closure over `g`. Let
`c ∼ c'` and `b ∈ 𝒞`. *Linear tests:* `Λ(d, f)((b·c)·g) = Λ(d·b, f)(c·g)` —
associativity alone: the left factor shifts the slot, and slots are
universally quantified. *ω tests:* the pairs queried by `Ω(d)((b·c)·g)` and
by `Ω(d·b)(c·(g·b))` are conjugate in one step of Definition 3.13. Write
`x := b`, `y := c·g`: the pairs are `(d·(x·y)^π, (x·y)^π)` and
`(d·x·(y·x)^π, (y·x)^π)`, both linked, one exponent serving `x·y` and `y·x`
alike; the conjugacy step applies at `s := d·(x·y)^π` — indeed
`s·(x·y)^π = s` — and lands on `s·x = d·x·(y·x)^π` by the identity
`(cd)^π·c = c·(dc)^π` of the rotation lemma's proof. `P` is saturated, `𝓘`
being well-formed, so the two bits agree:

```
    Ω(d)(b·c·g) = Ω(d·b)(c·(g·b)).
```

The right-hand side is a membership test at slot `d·b` on the right extension
`g·b` of `c`, where `c ∼ c'` applies; the same identity, read back, gives
`Ω(d)(b·c·g) = Ω(d)(b·c'·g)`. ∎

A left factor acts on a linear test by shifting its slot, and on an ω test by
rotating the loop — a right extension read at a shifted slot. No new identity
was proved: the rotation lemma, deployed a second time.

> **Theorem 3.20 (canonicalization).** Let `𝓘 = ⟨𝒮, P⟩` be a well-formed
> invariant and `L = L(𝓘)`. Then the test equivalence is the pushforward of
> Arnold's congruence — `𝒮(u) ∼ 𝒮(u') ⟺ u ≈_L u'` for all `u, u' ∈ Σ⁺` — and
> the quotient invariant `𝓘/∼`, the quotient stamp with the image pair set,
> is `𝓘(L)`: the same quotient of `Σ⁺`, byte-identical under shortlex keys.
> Moreover `∼` is computed on the table by partition refinement: group the
> classes by their membership tests, then split under right multiplication by
> the letters until stable — at most `|𝒞|` splits.

*Proof.* The displayed equivalence is Lemma 3.17. Two congruences on `Σ⁺`
with one kernel are one quotient — the same classes as sets of words, the
same letter map, the same induced table — so the quotient stamp is `𝒮_L`.
For the pair sets: a quotient of stamps preserves idempotent powers, so a
lasso named `(s, e)` by `𝒮` is named by the image pair in the quotient; hence
`(s, e) ∈ P` iff that lasso lies in `L` (Proposition 3.15) iff the image pair
lies in `P(L)` (Theorem 3.10(i)) — the bit of a pair is constant on
`∼`-classes, and the image of `P` is exactly `P(L)`. For the refinement: a
partition stable under every right letter is stable under every right
extension — the letters generate `𝒞`, `𝒮` being surjective — so the fixpoint
is exactly the closure Definition 3.18 demands; and every split separates
classes that Lemma 3.17 proves `≈_L`-inequivalent, so at most `|𝒞|` occur. ∎

*Example (a parity ghost).* Tensor `aUGb`'s stamp with length parity:
`𝒮×(u) := (𝒮(u), |u| mod 2)`, eight classes, with pair set
`P× := { ((s, p), (e, 0)) : (s, e) ∈ P }` — a loop's parity must be
idempotent, hence even. With an even exponent every query projects onto
Figure 1's, so `𝓘×` is well-formed and `L(𝓘×) = aUGb`. The tests dissolve
the ghost at the first grouping: every bit factors through the first
coordinate, so `(c, 0)` and `(c, 1)` share all tests, and right
multiplication keeps them paired — the refinement is stable at once, and the
quotient is Figure 1: four classes, the parity gone. §4 replays the scene at
scale: its automaton stamp for `aUGb` carries nine classes of mark
bookkeeping (Ex. 1), refined onto the same four.

> **Corollary 3.21 (the invariants denoting `L`).** Let `L` be regular and
> `𝒮 : Σ⁺ → 𝒞` a stamp whose kernel refines `≈_L` — `𝒮(u) = 𝒮(u')` implies
> `u ≈_L u'`. There is exactly one pair set over `𝒮` making the invariant
> denote `L`: the names of the accepted lassos,
>
> ```
>     P := { (𝒮(u)·e, e)  :  u ∈ Σ*,  v ∈ Σ⁺,  e = 𝒮(v)^π,  u·v^ω ∈ L },
> ```
>
> and every invariant denoting `L` arises this way.

*Proof.* Existence: two presentations landing on one name have, rewritten on
`(u·v^π, v^π)`, `𝒮`-congruent stems and loops, hence `≈_L`-congruent ones,
and the substitution lemma (3.9) gives their lassos one verdict — the
displayed `P` answers every query with `L`'s verdict. Uniqueness: every
linked pair is the queried name of some lasso — surjectivity picks a
presentation — whose verdict forces the pair's bit. Conversely, an invariant
denoting `L` has a kernel refining `≈_L` — classes with one value agree on
all membership tests, hence on all Arnold contexts (Lemma 3.17) — and
carries the forced pair set. ∎

An invariant denoting `L` exists at every refinement of the syntactic stamp
and nowhere else; it is well-formed; and canonicalization carries it onto
`𝓘(L)`, by right multiplications on its own table. Obtaining one is a
question about presentations, not about the algebra: §4 answers it for the
deterministic automata of the field, and the directions of §7 answer it
elsewhere.
