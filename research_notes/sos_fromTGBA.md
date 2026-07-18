# From Nondeterministic TGBA to the Syntactic ω-Semigroup, Without Determinization

*Working draft — 2026-07-18. Standalone companion to the core construction paper
`sos_core.md`, cited [SωS26] throughout; written as deltas against it. Placement
undecided: (a) replace [SωS26] §4, with a degeneration paragraph recovering the
deterministic EL entry; (b) a second paper on routes from LTL to the SoS — this entry
(tableau route) plus the direct compositional route — in which case this content migrates
to `sos_fromltl.md`; (c) both papers, non-redundant. The write-up below is
placement-neutral: [SωS26] §3 — the invariant, its semantics, canonicity, rotation — is
untouched and is the shared target.*

## 0. Aim and shape

[SωS26] enters through a deterministic, complete Emerson–Lei automaton: the automaton
stamp `≈_D`, whose classes are (transition map, mark map) vectors over the slot set `Q`,
followed by a right-only refinement — seeded on residuals and loop verdicts, closed by the
rotation lemma — landing on the keyed normal form `𝓘(L)`.

This note replaces the *entry* and keeps the *quotient*. The new entry consumes a
nondeterministic transition-based generalized-Büchi automaton (TGBA) — the native output of
tableau constructions à la Couvreur — and produces a stamp that **strongly recognizes**
`L(A)`: every lasso's membership is a function of its linked-pair name. The quotient module
of [SωS26] is then generalized in exactly one place: *slots are left values of the stamp's
monoid, not states of an automaton*. The deterministic construction reappears as the
special case in which the slot set compresses onto reachable states (Proposition 5.1). Determinization was an
optimization of the slot set, never a hypothesis of the theory.

Cost of the trade: one genuinely new lemma (necessity for the profile-matrix stamp,
by pigeonhole + Ramsey — Lemma 3.2, packaged as strong recognition in Theorem 3.3), and
wider seed tables (`|S¹|` slots instead of `|Q|`, before slot compression). Gain: Safra is
deleted from every pipeline whose source is a formula.

## 1. Automata and conventions

`Σ` a finite alphabet. `A = (Q, Σ, δ, Q₀, F, mk)`:

- `δ ⊆ Q × Σ × Q` a transition **relation** — nondeterminism allowed, completeness **not**
  required, multiple initial states allowed;
- `F` a finite set of **marks**; `mk : δ → 2^F` assigns marks to transitions;
- acceptance: a run is accepting iff **every** mark in `F` is carried by infinitely many of
  its transitions (`⋀_{f∈F} Inf(f)`).

`L(A) ⊆ Σ^ω` is the set of words with an accepting run from some initial state. The
**profile** of a finite path is the union of the mark sets of its transitions — the set of
marks the path exhibits at least once.

Everything below is stated for lassos `u·v^ω` (`u ∈ Σ*`, `v ∈ Σ⁺`); as in [SωS26], two
ω-regular languages agreeing on all lassos are equal, and all constructed languages are
visibly ω-regular, so lasso-level statements suffice.

## 2. The profile-matrix stamp

> **Definition 2.1 (profile semiring).** Let `K_F` be the set of ⊆-**antichains** over
> `2^F`, with
>
> - addition `X ⊕ Y := max(X ∪ Y)` (union, then delete dominated profiles),
> - multiplication `X ⊗ Y := max{ x ∪ y : x ∈ X, y ∈ Y }`,
> - zero `∅` (no profile — "no path"), unit `{∅}` (the empty profile).

`K_F` is a finite idempotent semiring; both operations are monotone for the domination
order (`X ⊑ X'` iff every `x ∈ X` is dominated by some `x' ∈ X'`), and `max` is a semiring
congruence for it because `x ⊆ x'` implies `x ∪ y ⊆ x' ∪ y`.

> **Definition 2.2 (the stamp).** For `u ∈ Σ⁺` let `𝒮_A(u)` be the `Q × Q` matrix over
> `K_F` whose `(p,q)` entry is the antichain of ⊆-maximal profiles of `u`-paths from `p` to
> `q` (the zero of `K_F` if there is none). `𝒮_A : Σ⁺ → S_A` is a morphism onto the finite
> semigroup `S_A` it generates. Adjoin a fresh unit for `S_A¹`. The uniform idempotent
> exponent of `S_A` is written `π`.

*Proof note (the product is path concatenation, pruning included).* A composite path
decomposes at its junction state, so the exact achievable profiles of `u·v`-paths `p → r`
are the pairwise unions of achievable halves, summed over junctions. Pruning commutes with
this: each half is dominated by a maximal profile of its half and unions are monotone, so
every achieved composite is dominated by a pairwise union of maximals; and every pairwise
union of maximals is itself achieved. Hence the `K_F`-matrix product computes exactly the
maximal achieved composite profiles. ∎

> **Definition 2.3 (acceptance datum).** A **linked pair** of `S_A` is `(s, e)` with
> `e·e = e` and `s·e = s`. Set
>
> ```
> P_A := { (s, e) linked : ∃ p₀ ∈ Q₀, q ∈ Q.  s_{p₀q} ≠ 0  and  F ∈ e_{qq} }.
> ```
>
> The existential is **joint**: the same `q` must serve both conditions. (`F ∈ e_{qq}` is
> well posed: `F` is the top of `2^F`, so it lies in the antichain iff it is achievable.)

**Remark 2.4 (the classical case, and the general one).**

1. For state-based single-mark Büchi automata, entries take three values — no path / best
   profile `∅` / best profile `{f}` — and Definition 2.2 degenerates to the classical
   `0/1/2` transition-matrix construction of the Büchi–Ramsey line [PP04, CPP08]. The
   stamp is its transition-based, generalized-marks extension. *(Citation TODO: an
   algorithmic use of the `0/1/2` matrices is attributed in folklore to
   Fleischer–Kufleitner; the paper is not in `papers/` — acquire and read before citing,
   or drop the name.)* The term **strongly recognizes** is used in the sense of [CPP08]:
   the congruence saturates the language — here, at lasso level, the verdict is a function
   of the name.
2. The antichain compression is licensed by `Inf`-only acceptance: more marks on a segment
   never hurts, so dominated profiles are redundant *for acceptance* (any use of a
   dominated path can be replaced, same endpoints, same word, by a dominating one — runs
   are assembled from interchangeable segments). For general Emerson–Lei conditions
   (`Fin` present) monotonicity fails; replace antichains by **exact** achievable-profile
   sets (subsets of `2^F`, no pruning) and, in Definition 2.3, replace `F ∈ e_{qq}` by
   `∃ X ∈ e_{qq}. X ⊨ α`. Every proof of §3 goes through — Remark 3.6 spells the two
   inclusion pairs this claim rests on. So the entry covers *nondeterministic Emerson–Lei
   in full generality*; TGBA is the case where it is small enough to like.

**Size.** With `d(k)` the number of antichains of `2^k` (Dedekind), `|S_A| ≤ d(|F|)^{|Q|²}`
(e.g. `d(3) = 20`); exact-profile variant: `≤ (2^{2^{|F|}})^{|Q|²}`. Both are honest
worst-case monsters, as is `(|Q|·2^{|F|})^{|Q|}` in [SωS26]; §6 discusses why this route
still wins for formula-sourced pipelines.

## 3. Strong recognition

Throughout, `u, v` range over `Σ⁺` (empty stems are handled by the normalization of
Definition 3.5) and "verdict" means membership in `L(A)`.

> **Lemma 3.1 (sufficiency).** Let `(s, e) ∈ P_A`, and let `u ∈ 𝒮_A⁻¹(s)`,
> `v ∈ 𝒮_A⁻¹(e)`. Then `u·v^ω ∈ L(A)`.

*Proof.* Definition 2.3 hands a single `q` serving both conditions. `s_{p₀q} ≠ 0` and
`𝒮_A(u) = s` give a `u`-path `p₀ → q`. `F ∈ e_{qq}` and `𝒮_A(v) = e` give a `v`-path
`q → q` whose profile is all of `F` — the matrix value of a word *is* its path data, which
is the whole point of the entry. Repeat that one `v`-path forever — nondeterminism permits
choosing the same path each block: every mark occurs in every block. Accepting. ∎

> **Lemma 3.2 (necessity).** Let `e = 𝒮_A(v)` be idempotent, `s = 𝒮_A(u)` with `(s, e)`
> linked, and suppose `u·v^ω ∈ L(A)`. Then `(s, e) ∈ P_A`.

*Proof.* Fix an accepting run `ρ` from some `p₀ ∈ Q₀` and let `q_i` be its state after the
prefix `u·v^i` (`i ≥ 0`). By pigeonhole choose `q` and an infinite `I ⊆ ℕ` with `q_i = q`
for `i ∈ I`. Color each pair `i < j` in `I` by the **exact** profile `X_{ij} ⊆ F` of `ρ`'s
segment from boundary `i` to boundary `j` — finitely many colors. By infinite Ramsey take
an infinite monochromatic `J ⊆ I`, color `X`. (Additivity `X_{ik} = X_{ij} ∪ X_{jk}` makes
the color idempotent automatically; nothing needs checking.)

The segments between **consecutive** elements of `J` tile the tail of `ρ` beyond boundary
`min J` — no gaps — and each has profile exactly `X`. Since `ρ` is accepting, every mark of
`F` occurs infinitely often, hence beyond boundary `min J`, hence in at least one tile,
hence in `X`: `F ⊆ X ⊆ F`, so `X = F`. Consecutiveness is load-bearing here: segments
between arbitrary pairs of `J` would leave gaps, and the argument would not force `X = F`.

Now read the algebra off the run, at the same `q` the pigeonhole fixed. For consecutive
`i < j` in `J`, `ρ`'s segment is a `v^{j-i}`-path `q → q` of exact profile `F`, so `F` is
achieved in `(e^{j-i})_{qq} = e_{qq}` (idempotence); being the top of `2^F`, `F` is maximal
among achieved profiles and survives pruning: `F ∈ e_{qq}`. The initial segment is a
`u·v^{min J}`-path `p₀ → q`, so `(s·e^{min J})_{p₀q} ≠ 0`; if `min J = 0` this is
`s_{p₀q}` directly, and otherwise `s·e^{min J} = s` by linkage and idempotence — either
way `s_{p₀q} ≠ 0`. The pair `(p₀, q)` witnesses Definition 2.3: `(s, e) ∈ P_A`. ∎

> **Theorem 3.3 (one name, one verdict).** For every linked pair `(s, e)` of `S_A`: either
> every lasso with a factorization valued `(s, e)` lies in `L(A)` (iff `(s, e) ∈ P_A`), or
> none does. Equivalently, `(S_A, 𝒮_A, P_A)` strongly recognizes `L(A)` at lasso level.

*Proof.* Lemma 3.1 and the contrapositive of Lemma 3.2. ∎

> **Corollary 3.4.** `L(A) = ⋃_{(s,e) ∈ P_A} 𝒮_A⁻¹(s)·(𝒮_A⁻¹(e))^ω`: both sides are
> ω-regular and Theorem 3.3 makes them agree on lassos.

> **Definition 3.5 (naming, as in [SωS26]).** The **name** of a lasso `u·v^ω` is
> `(𝒮_A(u·v^π), 𝒮_A(v^π))` — the rewriting `(u, v) ↦ (u·v^π, v^π)` makes the stem nonempty
> and the loop value idempotent, and Theorem 3.3 says the verdict is a function of the
> name.

This is [SωS26, Thm 3.10(i)] with "reached state" replaced by "stamp value"; the
substitution lemma that was one trivial paragraph there is Lemma 3.2 here — the entire
tuition of dropping determinism is concentrated in that single Ramsey argument.

**Remark 3.6 (the exact-profile variant, verified).** Two inclusion pairs carry
Remark 2.4(2), and both fall out of the proofs above. *Necessity*: the Ramsey tile profile
satisfies `X = mk^∞(ρ)` exactly — `X ⊆ mk^∞` since every mark of `X` occurs in every tile,
hence infinitely often; `mk^∞ ⊆ X` since every recurring mark occurs in some tile beyond
`min J`, and every tile is exactly `X`. So `X ⊨ α` for the run's actual recurring set, as a
non-monotone `α` requires, and `X` lies in the exact (unpruned) entry `e_{qq}`.
*Sufficiency*: repeating one chosen `v`-path of exact profile `X` forever gives
`mk^∞ = X` exactly — marks outside `X` occur only in the finite stem. Nothing in §4 touches
monotonicity — it consumes `(S, h, P)` opaquely — so the exact variant strongly recognizes
any nondeterministic Emerson–Lei automaton.

**Remark 3.7 (saturation).** `P_A` is saturated in the sense of [SωS26, Def 3.12]: two
conjugate linked pairs name a common lasso by the rotation lemma [SωS26, 3.11], and
Theorem 3.3 gives that lasso one verdict, so `P_A` contains both pairs or neither. This is
the syntactic precondition the quotient of §4 can be made to consume in place of the
semantic one — see Remark 4.7.

## 4. The quotient, generalized: slots are left values

From here on the automaton is gone.

> **Definition 4.0 (input interface).** A **strongly recognizing stamp** for a regular
> `L ⊆ Σ^ω` is `(S, h, P)`: a surjective semigroup morphism `h : Σ⁺ → S` onto a finite
> semigroup, and a set `P` of linked pairs of `S`, such that every lasso's membership in
> `L` equals the `P`-bit of its name (Definition 3.5 read over `h`). Two instances: §3's
> `(S_A, 𝒮_A, P_A)`; and the deterministic entry of [SωS26] read as a stamp — `S = 𝒞_D`
> with `P_D := { (s, e) linked : A(δ(q₀, s), e) = 1 }`, well defined precisely by the
> collapse [SωS26, Lemma 4.6], which *is* the statement that `𝒞_D` strongly recognizes.

> **Definition 4.1 (bare tests).** For `d ∈ S¹` (a **slot**), `f ∈ E(S)` idempotent,
> define on `c ∈ S`:
>
> ```
> Λ(d, f)(c) := [ (d·c·f, f) ∈ P ]            (bare linear test at slot d, loop f)
> Ω(d)(c)    := [ (d·c^π, c^π) ∈ P ]          (bare ω test at slot d)
> ```

Both are `P`-lookups after `O(1)` products: the seed is computed from `(S, P)` alone, with
no residual-automaton machinery — the nested state-level fixpoint of [SωS26, §4.4]
disappears, because a strongly recognizing stamp already answers every residual question
through `P`. (Sanity: `(d·c·f)·f = d·c·f` and `(d·c^π)·c^π = d·c^π`, so both pairs are
linked; `d·c·f, d·c^π ∈ S` since `c ∈ S`.)

> **Lemma 4.2 (tests exhaust Arnold contexts).** Let `u, u' ∈ Σ⁺` with `c = h(u)`,
> `c' = h(u')`. Then `u ≈_L u'` (Arnold, [SωS26, Def 3.7]) iff for all `g ∈ S¹`, all slots
> `d ∈ S¹`, all `f ∈ E(S)`:
>
> ```
> Λ(d, f)(c·g) = Λ(d, f)(c'·g)      and      Ω(d)(c·g) = Ω(d)(c'·g).
> ```

*Proof.* Any linear context `x·_·y·t^ω` evaluates, by strong recognition, to
`Λ(h(x), h(t)^π)(c·h(y))` — slot `h(x)`, right extension `h(y)`, loop idempotent
`h(t)^π` — and any ω-power context `x·(_·y)^ω` to `Ω(h(x))(c·h(y))`. Surjectivity of `h`
runs the translation in both directions: every idempotent `f` is some `h(t)^π`, every
`g ∈ S¹` is some `h(y)` with `y ∈ Σ*` (the unit by `y = ε`), every slot some `h(x)`. ∎

> **Definition 4.3 (the quotient relation).** `c ∼ c'` iff the displayed condition of
> Lemma 4.2 holds. Equivalently: `∼` is the coarsest **right-invariant** equivalence on `S`
> refining the seed `R`, where `c R c'` iff all bare tests agree on `c, c'` (the `g = 1`
> instance). Right-invariance is by construction (the `g`-closure); coarsest is the
> standard argument.

> **Lemma 4.4 (rotation, at the level of values).** `∼` is a two-sided congruence.

*Proof.* Right-invariance is Definition 4.3. For left-invariance, let `c ∼ c'` and
`b ∈ S`; check the tests on `b·c` against `b·c'`.

*Linear:* `Λ(d, f)((b·c)·g) = Λ(d·b, f)(c·g)` — pure associativity: a left factor is a
**slot shift** — and slots are universally quantified.

*ω:* pick representatives `x, w_b, w_c, w_g` and rotate the word:
`x·(w_b·w_c·w_g)^ω = x·w_b·(w_c·w_g·w_b)^ω`. The two writings name the same ω-word, so by
strong recognition their names' `P`-bits agree:

```
Ω(d)(b·c·g) = Ω(d·b)(c·(g·b)).
```

The right side is a bare ω test at slot `d·b` on a right extension of `c`; `c ∼ c'` makes
it agree with the same on `c'`, and unrotating gives `Ω(d)(b·c·g) = Ω(d)(b·c'·g)`. ∎

This is [SωS26]'s rotation lemma with its proof transposed from runs to values: *a left
factor acts on the linear shape by re-indexing a slot, and on the ω shape by rotating the
loop — a right extension read at a shifted slot.* The deterministic paper's slot set `Q`
was the compression of `S¹` by the left action on states; here the compression is simply
not taken (Proposition 5.1 makes the correspondence exact).

> **Theorem 4.5 (canonicity).** `S/∼`, with the induced letter map, multiplication, and
> the image of `P`, is the syntactic stamp of `L`: by Lemma 4.2, `∼` is the pushforward of
> `≈_L` along the surjection `h`, so `S/∼` and `Σ⁺/≈_L` are the same quotient of `Σ⁺`.
> Keying each class by its shortlex-least word — BFS over the right-Cayley graph of the
> quotient from the adjoined unit, exactly as in [SωS26, Def 4.9] — yields the **same
> normal form byte-for-byte** as the deterministic route: both are `𝓘(L)`, and equality of
> the two pipelines' outputs on a shared corpus is a machine-checkable regression test,
> not a theorem to re-prove.

*Well-definedness of the image of `P`.* The `P`-bit of a linked pair is `∼`-invariant in
each coordinate. Stem: for `(s, e)` linked, `[(s, e) ∈ P] = Λ(1, e)(s)` (linkage
`s·e = s`), and `s ∼ s'` instantiates Lemma 4.2's condition at `d = 1`, `f = e`, `g = 1`.
Loop: `[(s, e) ∈ P] = Ω(s)(e)` (idempotence `e^π = e` and linkage), and `e ∼ e'` gives
`Ω(s)(e) = Ω(s)(e')` — note `e'` need not be idempotent in `S`; the test compares through
`e'^π`, whose `∼`-class is the class of `e` since `∼` is a congruence (Lemma 4.4). So the
bit is constant on class pairs, and the image of `P` is the pair set of the syntactic
invariant. ∎

> **Algorithm 4.6 (pipeline).** (1) Close `{h(a) : a ∈ Σ}` under product, deduplicating
> matrices by hash — the analogue of the `≈_D` closure. (2) Tabulate the seed: for each
> `c ∈ S`, the bit vector over `(d, f)` and `(d)` — `O(|S|·|S¹|·(|E(S)|+1))` entries, each
> one product-chain and one `P`-lookup. (3) Moore/Hopcroft refinement under right
> multiplication by letters (letters generate). (4) Key, serialize. Steps (2)–(4) are
> polynomial in `|S|`; step (1) is the wall, as `|𝒞_D|` was.

The seed table is the honest new cost: `|S¹| ~ |S|` slots where [SωS26] had `|Q|`, so
step (2) is quadratic-times-`|E(S)|` in `|S|`. Two mitigations: slots with identical test
rows merge, and may be merged on the fly, interleaved with the refinement — Proposition 5.1
shows the collapse can be dramatic (`S¹ → Reach`) — and the whole table is Boolean
(§6, symbolic).

**Remark 4.7 (alternative layering: saturation instead of strong recognition).** As
proved, the ω-case of Lemma 4.4 leans on strong recognition — a *semantic* fact about `L` —
where [SωS26]'s rotation lemma (3.11) was pure algebra on any stamp. The identity
`Ω(d)(b·c·g) = Ω(d·b)(c·(g·b))` can instead be derived algebraically from **saturation of
`P`** (conjugacy-closure, [SωS26, Def 3.12]), which §3 establishes once for `P_A`
(Remark 3.7). Same theorems, cleaner module boundary: the quotient then consumes `(S, P)`
under a *checkable syntactic* precondition — finitely many triples, each one product and
two lookups — instead of a semantic one, and becomes usable on candidate `P`'s of unknown
provenance: learned tables, compositional constructions mid-induction, imported files.
The learner fixture of §6 wants exactly this. To be written out when the placement
decision is made.

## 5. What changes relative to [SωS26], exactly

| module | [SωS26] (det EL) | here (nondet TGBA / EL) |
| --- | --- | --- |
| entry object | (δ-vector, mk-vector) over `Q` | profile matrix over `K_F` |
| substitution lemma | trivial (same state ⇒ same future) | Ramsey (Lemma 3.2) — the one new proof |
| slots | reachable states of `D` | left values `S¹` |
| seed residual half | residual langs on states (§4.4 Moore) | bare tests, pure `(S, P)`-lookups |
| rotation lemma | on runs | on values (Lemma 4.4), same statement |
| keying, serialization, read-offs | — | unchanged, verbatim |
| hypotheses on input | deterministic, complete | none: nondet, incomplete, multi-initial |

Nothing downstream of the stamp is touched: linked-pair collapse, normal form,
byte-equality, aperiodicity/LTL read-off, the census harness — all consume a stamp and
never knew where it came from. The det paper is not superseded: its entry is the efficient
one when a deterministic automaton is what you have (the census), and its slot compression
is a real theorem — now stated and proved:

> **Proposition 5.1 (slot compression = determinism).** Let `D` be deterministic and
> complete, read as a strongly recognizing stamp `(𝒞_D, 𝒮_D, P_D)` (Definition 4.0). Then
> every bare test at slot `d` factors through the state `δ(q₀, d)`:
>
> ```
> Λ(d, f)(c) = A(δ(δ(q₀, d), c), f)        Ω(d)(c) = A(δ(q₀, d), c),
> ```
>
> so the map `d ↦ δ(q₀, d)` compresses `S¹` onto `Reach`, slots with one image having
> identical test rows. At a fixed `q ∈ Reach`, the `Λ`-family over `(f, g)` enumerates the
> verdicts of all lassos continued from `q` — by lasso density, exactly residual equality
> at `q`, i.e. [SωS26]'s `∼lin` — and the `Ω`-family over `g` is [SωS26]'s `∼ω` at `q`.
> Hence this note's seed, quotiented by the state action, is the deterministic paper's
> seed, partition for partition; the two quotients coincide.

*Proof.* The displayed identities are [SωS26, Lemma 4.6] (the collapse): the verdict of
`w_d·w_c·(w_f)^ω` from `q₀` depends on the stem only through the state it reaches, and
likewise for `w_d·(w_c)^ω`. For the seed identification: agreement of `Λ(d, f)(c·g)` with
`Λ(d, f)(c'·g)` over all `(f, g)` at the slots reaching `q` says the residuals
`L(δ(q, c))` and `L(δ(q, c'))` agree on all lassos — every lasso is `w_g·(w_f)^ω` for some
`g ∈ S¹` and idempotent `f`, by surjectivity and normalization — and two regular
ω-languages agreeing on all lassos are equal [PP04, Ch. I, Cor. 9.8]. The `Ω`-half at `q`
is `A(q, c·g) = A(q, c'·g)` over all `g`, which is `∼ω` verbatim. ∎

The compression is generally strict — `|Reach| ≪ |S¹|` — which is the honest statement of
what determinism was buying: a small slot set, never a hypothesis of the theory.

## 6. Where it opens up

**LTL → SωS with no Safra.** Couvreur-style tableau emits a nondeterministic TGBA
syntax-directed from the formula's closure; §2–4 take it to `𝓘(L)` directly. The pipeline
`formula → tableau → profile stamp → right-only quotient → normal form` has no
determinization anywhere, and each stage is either syntax-directed or partition
refinement. And since Spot compiles PSL (SEREs included) to TGBA, the same pipeline gives
**PSL → SωS**: the "is this PSL property actually LTL?" read-off of [SωS26, §5.3] becomes
reachable from the PSL source itself, no deterministic automaton ever built.

**The compositional path shares the back end.** A per-operator construction of stamps
(product for `∧/∨`, `P`-flip for `¬`, enrichment for `X`, a cascade for `U`) would produce
strongly recognizing stamps by induction; §4 is its minimizer at every node. Two entries,
one quotient — if the second-paper route is taken, §4 is literally shared code and shared
theorem between the tableau route and the direct algebra route.

**Emerson–Lei generality for free.** Remarks 2.4(2) and 3.6: the exact-profile variant
strongly recognizes any nondeterministic EL automaton. So the *theory* of this note
strictly subsumes the det paper's entry in scope (while losing to it in constants); worth
one theorem statement, not more.

**Symbolic implementation.** Entries of `K_F` are antichains of subsets — Boolean through
and through; matrix product is relational composition; the closure of step (1) is a
fixpoint of set operations. The BDD remarks of [SωS26, §5.1] apply with more force here,
since the matrices, unlike state vectors, are already set-shaped.

**A structural bonus.** Because the quotient consumes only `(S, P)`, the construction
factors cleanly as *entry ⊣ quotient*, and the quotient module doubles as a minimizer for
any strongly recognizing stamp from any source — learned tables included: the learner's
export and this note's §4 are the same fixture. Under Remark 4.7's layering, the
precondition on such imports is even checkable (saturation), not assumed.

## 7. Status ledger

**Reviewed and confirmed** (adversarial pass, 2026-07-18):

1. **Lemma 3.2** — proof walked link by link: pigeonhole, Ramsey on exact profiles, the
   tiling argument forcing `X = F` (consecutiveness is load-bearing and now stated), the
   joint `∃(p₀, q)`, the `min J = 0` boundary case, top-survives-pruning. The text above
   incorporates the hardened wording.
2. **Remark 2.4(2)** — the exact-profile variant covers full EL; the two inclusion pairs
   it rests on are now spelled in Remark 3.6.
3. **Slot compression** — was "believed, stated, not yet proven"; now Proposition 5.1,
   proved.

**Routine, to be written out:** associativity of `K_F` and of matrix product over it
(standard semiring facts plus the `max`-congruence observation of Definition 2.1); the
`g`-closure/coarsest bookkeeping in Definition 4.3; Remark 4.7's algebraic derivation of
the rotation identity from saturation, if that layering is adopted.

**Engineering spec items** (to be issued when placement is decided):

- Counterexample search on Lemma 3.2: small random TGBA, compare `P_A`-verdicts to
  explicit run search on random lassos — cheap, self-bounded, per-example.
- Byte-equality regression: this pipeline vs the deterministic one of [SωS26] on every
  corpus automaton both can consume — Theorem 4.5 says identical files, the harness
  checks it (e.g. `GFaa`'s tableau TGBA must reproduce the §5.2 serialized file of
  [SωS26] byte for byte).

**Open (paper-structure, not mathematics):** placement per the header note; whether §4
adopts Remark 4.7's saturation layering; the citation TODO of Remark 2.4(1).
