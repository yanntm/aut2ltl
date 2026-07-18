### 5.3 Compression: the tests through states

What remains is to coarsen `𝒞_D`, and §4 already says how: group the classes
by their membership tests, then refine under right multiplication by the
letters (Theorem II). Taken literally, the tests read at every slot
`d ∈ M_D` — a set as large as the stamp itself. Determinism compresses the
slots to states: on the automaton invariant, a slot enters a test only
through the state it reaches.

> **Proposition 5.2 (slot compression).** On the automaton invariant, every
> membership test reads at a state: for all `d ∈ M_D`, `c ∈ 𝒞_D` and
> idempotent `f ∈ 𝒞_D`,
>
> ```
>     Λ(d, f)(c) = A(δ(q₀, d·c), f)        and        Ω(d)(c) = A(δ(q₀, d), c),
> ```
>
> so slots compress from `M_D` onto `Reach`. At a fixed `q ∈ Reach`,
> agreement of the `Λ`-tests over all extensions and loops is equality of
> residual languages, agreement of the `Ω`-tests over all extensions is
> equality of loop verdicts, and the test equivalence of Definition 4.3
> becomes, on `𝒞_D`:
>
> ```
>     c ∼lin c'  ⟺  ∀ q ∈ Reach :              L(δ(q, c)) = L(δ(q, c'))
>     c ∼ω  c'   ⟺  ∀ q ∈ Reach, ∀ g ∈ M_D :   A(q, c·g) = A(q, c'·g)
>     c ∼   c'   ⟺  c ∼lin c'  and  c ∼ω c'.
> ```

*Proof.* Each identity computes the verdict of one lasso through the
collapse, on two of its presentations. `Λ(d, f)(c)` is the `P_D`-bit of
`(d·c·f, f)` — by Corollary 5.1, the verdict of any lasso it names, say
`w_d·w_c·(w_f)^ω` on representative words — which the collapse (Lemma 5.1)
reads as `A(δ(q₀, d·c), f)`; likewise `Ω(d)(c)` is the verdict of
`w_d·(w_c)^ω`, read as `A(δ(q₀, d), c)`. The slot enters only through
`δ(q₀, d)`, and `δ(q₀, M_D) = Reach` exactly — every reachable state is
reached by a finite word.

For the `Λ`-family at a fixed `q`: `Λ(d, f)(c·g)`, over all `g ∈ M_D` and
idempotent `f`, is the membership of `w_g·(w_f)^ω` in the residual
`L(δ(q, c))`. These representative lassos test every lasso: `y·t^ω` shares
its name with `w_g·(w_f)^ω` at `g = 𝒮_D(y)`, `f = 𝒮_D(t)^π`, name-sharing
survives any common finite prefix, and the automaton invariant denotes
`L(D)` (Corollary 5.1) — one verdict. Agreement of the family for `c` and
`c'` is therefore agreement of `L(δ(q, c))` and `L(δ(q, c'))` on every
lasso, which is their equality [PP04, Ch. I, Cor. 9.8]. The `Ω`-family at
`q` is the displayed `∼ω` by the first identity: `Ω(d)(c·g) = A(q, c·g)`. ∎

`∼lin` compares the futures the words open — residual languages of reached
states — and never looks at marks; `∼ω` compares the loops the words can
close, under every right completion — the two positions a word occupies in a
lasso, each tested on the right. Neither mentions a left context.

*Example (the two relations divide the labor).* On `EvenBlocks`'s two-state
`D`, `⟨aa⟩` is the neutral class. `∼lin` is total: the language is
prefix-independent, both
states accept exactly `EvenBlocks`. The separation of `⟨a⟩` from `⟨aa⟩` is
carried entirely by `∼ω`, with the block-closing extension `g = ⟨b⟩`:
`A(q, ⟨a⟩·⟨b⟩) = A(q, ⟨ab⟩)` rejects at both slots — the loop `ab` closes
an odd block forever, violating `Fin(0)` — while `A(q, ⟨aa⟩·⟨b⟩)` accepts at
both: `(aab)^ω` closes even blocks forever.

*Remark (prefix-independence).* The example is the generic situation, not a
corner case: `L` is prefix-independent (`u₀·w ∈ L ⟺ w ∈ L` for all
`u₀ ∈ Σ*`, `w ∈ Σ^ω`) iff every residual equals `L` — determinism gives one
residual per reached state — iff `∼lin` is total, and then all
discrimination rides on `∼ω`. Tail properties live here, and it is why a
construction resting on residuals alone cannot even see them.

*Remark (rotation, on runs).* Left invariance (Lemma 4.3), read on the
machine: `A(q, c₀·c·g) = A(δ(q, c₀), c·g·c₀)` — read the loop `(c₀·c·g)^ω`
from `q` as `c₀·(c·g·c₀)^ω`: the prefix is read once, its marks recur
never. A left factor carries no information of its own; it only moves the
state where a right test is read — right extensions at state-indexed slots,
an observation-table discipline answering the obstruction Angluin and
Fisman record for ω-learning [AF21].

**The algorithm.** The construction runs entirely on tables. The table is
materialized first: a class is stored as its two maps (§5.2), the letter
classes are read off `δ` and `mk`, and closure under right extension by the
letters — the maps of a product computed from the maps of its factors, no
word consulted — yields `𝒞_D`. The seed then groups
the classes of `𝒞_D` by their compressed tests — residuals and loop
verdicts at every reachable slot (Proposition 5.2); the `|𝒞_D|·|Q|`
verdicts each cost one walk of a
functional graph (the loop verdict, Lemma 5.1). Residual equality of states
is a fixpoint on the same data, one
level down: seed two states equal when their loop-verdict *columns* agree —
`A(p, c) = A(q, c)` for every `c ∈ 𝒞_D` — and refine under the letters,
splitting whenever `δ(p, x)` and `δ(q, x)` fall in distinct blocks, at most
`|Q|` splits. The seed settles the empty stems — the pure loops read from
`p` — and refinement closes under letter stems, hence under all stems, so
the fixpoint is exactly residual equality: two states agreeing on every
lasso accept one language [PP04, Ch. I, Cor. 9.8]. Moore refinement then
splits a block of classes
whenever a right letter separates two members — `c·⟨x⟩` and `c'·⟨x⟩` in
distinct blocks of the current partition — to fixpoint, at most `|𝒞_D|`
splits; the result is stable under every right letter, hence under every
right element — `𝒞_D` is letter-generated, `𝒮_D` being surjective — and it
is exactly the test equivalence: Theorem II's refinement, run on the
compressed slots of Proposition 5.2. Everything
downstream of `𝒞_D` is polynomial in its size; the size itself is the
subject of §6.1.

### 5.4 Theorem III: `𝓘(D) = 𝓘(L)`

The two steps assemble, and the assembled object is §3's.

> **Definition 5.4 (the constructed invariant).** `𝓘(D)` is the
> canonicalization of the automaton invariant: the quotient
> `⟨𝒮_D, P_D⟩/∼` of Theorem II, each class keyed by its shortlex-least
> word.

In practice the quotient's pair set is read off by one lasso test per linked
pair `(s, e)`: run `u_s·(u_e)^ω` on `D`, the keys naming the classes —
legitimate because the quotient is well-formed (Theorem II), so all lassos
sharing a name share the verdict (Proposition 4.1(i)).

> **Theorem III (the construction).** For every deterministic complete
> Emerson–Lei automaton `D`: `𝓘(D) = 𝓘(L(D))` — the constructed invariant
> is the syntactic invariant of the language, byte for byte, whatever
> presentation `D` was.

*Proof.* The automaton invariant is well-formed and denotes `L(D)`
(Corollary 5.1), and canonicalization carries any such invariant onto the
syntactic invariant of its language (Theorem II). ∎

> **Corollary 5.2 (one language, one file).** (i) `L(𝓘(D)) = L(D)`.
> (ii) Any two deterministic complete Emerson–Lei automata recognizing one
> language construct the identical invariant — an instance of the general
> fact that any two well-formed invariants denoting one language
> canonicalize to one file (Theorem II).

*Proof.* (i) Theorem III with Theorem I(i): `𝓘(L(D))` denotes `L(D)`.
(ii) Theorem III, applied to each automaton. ∎

*Example (canonicity, exhibited).* Compute `𝓘(D)` from the run-parity
`GFaa` of Ex. 2 — two states, a `Z₂` of transpositions — and again from
the **reset** presentation of Figure 2: the same two states, but each letter
sends *every* state to one place, an aperiodic transition monoid. The two
automata are not isomorphic, and their transition monoids disagree even on
whether a group is present. Both runs return the invariant of Ex. 2,
identically: five classes, `9 → 5` against `6 → 5`. The transposition was pure presentation, and
Theorem III's quotient is where it dies — while `Even` and `EvenBlocks`
keep their `Z₂` (Ex. 3, Ex. 4): those groups are `L`'s own.

---

<table>
<tr>
<td align="center"><img src="../sos_figs/img/gf_aa_reset.png" alt="GFaa reset automaton" width="280"></td>
<td valign="middle">

| presentation | `\|Q\|` | `a` acts by | group in transition monoid? | `\|𝒞_D\|` | `𝓘(GFaa)` |
|---|:--:|---|:--:|:--:|---|
| run-parity (Ex. 2) | 2 | transposition | yes — `Z₂` | 9 | Ex. 2's drawing |
| reset (left) | 2 | reset | no — aperiodic | 6 | *identical* |

</td>
</tr>
</table>

**Figure 2.** Canonicity, exhibited. The reset presentation of `GFaa`: the
same two states as Ex. 2's machine, but each letter sends every state to one
place — `a` to the "just saw `a`" state, whose `a`-self-loop carries the
mark, `b` to the other. Not isomorphic to Ex. 2's automaton, transition
monoids disagreeing even on whether a group is present, automaton stamps
of different sizes — the identical invariant out of both.

---
