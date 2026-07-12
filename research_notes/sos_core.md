# Materializing the Syntactic ω-Semigroup — outline draft

**Working title:** *Materializing the Syntactic ω-Semigroup: a Canonical
Representation of Regular ω-Languages*

Restructure of `sos_constructed.md`: object first, construction second. All content
borrowed from there unless marked NEW. Bullets only at this stage — one sentence per
idea, no definitions, no filled text.

---

## Abstract

- The syntactic ω-semigroup: canonical, complete, defined since Arnold 1985, never built.
- Contribution 1: the object itself, reified as the tuple `𝓘 = (𝒞, λ, M, P)` with a
  standalone lasso-membership semantics — a canonical normal form for ω-regular
  languages, which the domain has never had.
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

We work over a fixed finite alphabet `Σ` (for LTL applications `Σ = 2^AP`), writing `Σ*`
for finite words, `Σ^ω` for infinite words, `Σ^∞ = Σ* ∪ Σ^ω`, and taking `L ⊆ Σ^ω`
regular. The running examples use the single atom `a`, so `Σ = {a, !a}` with `!a` the
letter on which `a` fails. This section recalls the classical notions the object rests
on, adapting Perrin and Pin [PP04]; what this paper adds is listed at the close.

One further specimen threads §§2–3 alongside them, small enough that every notion is
worked on it in full — Carton–Perrin's [CP97, Ex. 10] `L = a*·b^ω` over `Σ = {a, b}`:
some `a`'s, then `b`'s forever (one atom `p`, read `a = ¬p`, `b = p`).

**We only ever look at lassos.** A **lasso**, or ultimately-periodic word, is `u·v^ω`: a
finite **stem** `u ∈ Σ*` followed by a finite nonempty **loop** `v ∈ Σ⁺` repeated
forever. Lassos suffice: *two regular ω-languages are equal iff they agree on all lassos*
[PP04]. Classifying `L` is therefore sorting lassos into finitely many types, and every
object below is machinery for naming and sorting them.

*Specimen.* `b^ω`, `ab·b^ω` and `aab·(bb)^ω` are lassos of `L`; `ba·(ab)^ω` is a lasso
outside it; and the word `a·b·a·a·b·b·a·a·a·b·b·b·⋯`, its blocks growing forever, is no
lasso at all — yet `L` is pinned by its verdicts on lassos alone.

**A finite monoid, plus one operation.** Finite words are classified by a finite
**monoid**: an associative product with unit, concatenation collapsed onto finitely many
values by a morphism `φ(uv) = φ(u)φ(v)`. Infinite words need exactly one thing more — a
way to read "loop forever" — since no finite product expresses `v^ω`. Classically one
adjoins an **ω-power** `s ↦ s^ω` and obtains a two-sorted **ω-semigroup** `(S₊, S_ω)`
[PP04, Ch. II], with a morphism `φ : Σ^∞ → S` **recognizing** `L` when `L = φ⁻¹(P)` for a
set `P` of accepting ω-types. We record this framing but do not carry the second sort as
a standalone algebra: §3 reads "loop forever" *inside* the finite monoid, so the object
is a finite monoid together with a set of accepting names.

*Specimen.* For `a*·b^ω` concatenation collapses onto five values — §3.1 exhibits
them — and "loop forever" will be read inside those five, with no second sort.

**The idempotent power.** In a finite monoid the powers `s, s², s³, …` of any element
cannot all be distinct, so the sequence is eventually periodic and contains a unique
**idempotent**, written `s^ω` — the unique `s^n` (`n ≥ 1`) with `s^n·s^n = s^n`. Read a
loop `v` through `φ`: its repeated image settles on `φ(v)^ω`. Concretely, "loop forever"
is "iterate the loop's value to its idempotent."

*Example.* In the multiplicative monoid of the integers mod 12, the powers of `2` run
`2, 4, 8, 4, 8, …` — eventually periodic; the unique idempotent among them is `4`
(`4·4 = 16 = 4`), so `2^ω = 4`.

**A linked pair names a lasso.** Reading `u·v^ω` through a finite `φ` (Ramsey): the loop
settles on the idempotent `e = φ(v)^ω` and the stem on `s = φ(u)·e`, with `s·e = s` (the
stem precedes the loop and is absorbed by it). A **linked pair** is any `(s, e)` with
`e² = e` and `s·e = s`; `s` names the stem, `e` the loop, `(s, e)` the lasso. A
recognizer is fixed by which lassos it accepts, hence by its set of **accepting linked
pairs** — which is why (§3) the acceptance datum of the object is a *set of pairs*, not a
subset of the monoid.

*Specimen.* Read `aab·b^ω` through the five-value algebra of §3.1: the loop settles on
`e = ⟦b⟧^ω = [b]`, the stem on `s = ⟦aab⟧·[b] = [a·b]`, and the pair `([a·b], [b])`
names the lasso — as it does every lasso with stem in `a⁺b*` and loop in `b⁺`.

**One lasso, many names.** A single ω-word has many presentations —
`u·v^ω = (uv)·v^ω = u·(v²)^ω = (u v₁)·(v₂ v₁)^ω` — and, as §3 shows, these need not name
it by the same linked pair. Reconciling them is not bookkeeping: it is the **rotation
lemma** (§3), the paper's structural pivot, and the one nontrivial constraint the object
must satisfy.

*Specimen.* `a·(ba)^ω = ab·(ab)^ω = ab·(abab)^ω`: one ω-word, three presentations.
Whether all presentations of a word receive one name is exactly the subtlety §3
confronts.

**Recalled, and new.** Recalled from [PP04] and classical theory: that lassos suffice,
the monoid/ω-power framing, and linked pairs. New here: the reification of the syntactic
ω-semigroup as a concrete finite tuple with a self-contained membership semantics (§3);
the **rotation lemma**, which both fixes that semantics (§3) and makes the two-sided
syntactic congruence computable by right multiplications alone (§7); and the construction
of the tuple from a deterministic Emerson–Lei automaton, proved correct against the
semantics (§6–8). Arnold's syntactic congruence, on which the object's canonicity rests,
is recalled where it is used, in §5.

## 3. The object

The syntactic ω-semigroup of `L` is reified as a finite tuple

```
    𝓘(L) = (𝒞, λ, M, P),
```

read and queried with no automaton in sight. It has two layers. The first three
components are the **algebra** `(𝒞, λ, M)` — a finite monoid carrying an alphabet
labelling — which holds the language's structural content. The fourth, `P`, is the
**acceptance layer**: a set of accepting linked pairs over the algebra, selecting *which*
language over that algebra `L` is. The division is structural, not cosmetic. The algebra
alone fixes everything invariant under changing the accepting set — most consequentially
the group content, hence LTL-definability (§4–5), so that `L` and its complement, which
share every table and differ only by `P ↦ P^c`, are LTL together or not at all.
Membership, equality, and the acceptance-sensitive classifications read `P`. We define
the algebra, then the layer; the only new mathematics of this section is that a set of
pairs is a *legal* layer exactly when it is closed under the rotation lemma (Lemma 3.5).

### 3.1 The algebra

**Definition 3.1 (algebra).** An **algebra** over `Σ` is a triple `(𝒞, λ, M)`:

- `𝒞` is a finite set of **classes**, each **keyed** by a word over `Σ`, with a
  distinguished `[ε]` keyed by the empty word;
- `M : 𝒞 × 𝒞 → 𝒞` is **associative** with `[ε]` a two-sided **identity**, so `(𝒞, M)`
  is a finite monoid; write `s·t := M(s, t)`;
- `λ : Σ → 𝒞` is the **letter map**, and the algebra is **letter-generated**: the
  **fold** `⟦·⟧ : Σ* → 𝒞`, defined by `⟦ε⟧ = [ε]` and `⟦w·a⟧ = ⟦w⟧·λ(a)`, is onto.

*Specimen.* The algebra of `a*·b^ω` (§2's specimen) has five classes, named by their
keys:

```
 ·       [ε] [a] [b] [a·b] [b·a]
[ε]       0   1   2   3     4
[a]       1   1   3   3     4
[b]       2   4   2   4     4
[a·b]     3   4   3   4     4
[b·a]     4   4   4   4     4
```

with `λ(a) = [a]`, `λ(b) = [b]` (ids `0..4` in key order). `[a]` holds the words in
`a⁺`, `[b]` those in `b⁺`, `[a·b]` those in `a⁺b⁺`, and `[b·a]` the *dead* words — once
an `a` follows a `b`, no continuation can rescue the word.

By associativity the fold is a monoid morphism `Σ* ↠ (𝒞, M)`; two words are **equivalent
in the algebra** when they fold alike. Each class is **keyed by its shortlex-least word**
(shortest, ties alphabetical), a datum recomputable from `(𝒞, λ, M)` by breadth-first
enumeration from `[ε]`, so the whole algebra is a canonical block of data once `M` and
`λ` are fixed. The identity `[ε]` is keyed by the empty word and is its own class even
when the monoid owns another neutral element: a nonempty word folding to a neutral class
keeps its own nonempty key — as `[a·a]` does in two of the running examples — a
convention that earns its keep in §5's acceptance read-off, where every accepting
component must carry a nonempty key.

*Specimen.* `⟦aab⟧ = [a]·[a]·[b] = [a·b]`: the word `aab` folds with `ab`, and `ab` —
the shortlex-least word reaching that class — is the key. No nonempty class of this
algebra acts neutrally; `Even` (§3.5) has one, and keeps it apart from `[ε]` by exactly
the convention above.

**The idempotent power, internally.** Each class `s` has its unique idempotent power
`s^ω` (§2). This is the algebra's entire access to "loop forever": there is no second
sort — a lasso's loop is read by folding it to a class and taking that class's idempotent
power.

*Specimen.* `[a]`, `[b]` and `[b·a]` are their own idempotent powers; `[a·b]` is not —
`[a·b]² = [b·a]`, already idempotent, so `[a·b]^ω = [b·a]`: iterating "`a`'s then `b`'s"
forces an `a` after a `b`.

**Definition 3.2 (Cayley graph).** The **Cayley graph** of the algebra has nodes `𝒞`,
root `[ε]`, and an edge `s →^a s·λ(a)` for each `s ∈ 𝒞, a ∈ Σ`. Rooted, deterministic,
and complete — every node reached from the root along its key — it is the algebra drawn
as a machine: the right regular representation acting on itself.

*Specimen.* From `[ε]`, `a` leads to `[a]` and `b` to `[b]`; `[a]` loops on `a` and
advances to `[a·b]` on `b`; `[b]` and `[a·b]` loop on `b` and fall to `[b·a]` on `a`;
`[b·a]` absorbs both letters. Each node sits at the end of the path spelled by its own
key:

```
          a                  b
   [ε] ─────▶ [a] ───────▶ [a·b]
    │         ⟲ a           ⟲ b
    │ b                      │ a
    ▼                        ▼
   [b] ─────────a────────▶ [b·a]
    ⟲ b                     ⟲ a, b
```

The graph is the matrix made visible, and losslessly: any product `s·t` is read by
walking `key(t)` from `s`. Its reachability shape is the algebra's right-ideal order
(here a graph falling into the dead sink), and a group would show as a cycle that is
not a self-loop — none here; `Even`'s `Z₂` (§3.5) draws as one.

### 3.2 Naming lassos, and the rotation lemma

A **linked pair** of the algebra is `(s, e) ∈ 𝒞 × 𝒞` with `e² = e` and `s·e = s`. It
**names** every lasso `u·v^ω` with `⟦u⟧·⟦v⟧^ω = s` and `⟦v⟧^ω = e`. Loops are nonempty,
so both components of a naming pair are folds of nonempty words; since no nonempty word
folds to `[ε]` (the identity is keyed by `ε` — §3.1), a naming pair lies in
`(𝒞∖{[ε]})²`.

*Specimen.* Six linked pairs: `([a],[a])`, `([b],[b])`, `([a·b],[b])`, `([b·a],[a])`,
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

*Specimen.* `a·(ba)^ω ↦ ab·(ab)^ω` is a `loop-rotate`; `ab·(ab)^ω ↦ ab·(abab)^ω` a
`loop-power`. All three presentations fold to the one name `([b·a], [b·a])` — this
specimen's stems absorb, so its moves happen to fix the name; `Even` (§3.5) has a move
that does not, and the lemma below is what makes the verdicts survive even those.

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

*Specimen.* The degenerate case on `(a, b) ↦ (ab, b)`: the stem gains `[b]`, which
`[a·b]` absorbs — both presentations carry the name `([a·b], [b])`.

Call two linked pairs **conjugate**, `(s, e) ≈ (s', e')`, when connected by rotations —
the equivalence generated by `(s, (gh)^ω) ≈ (s·g, (hg)^ω)`. Lemma 3.3 says conjugate
pairs name the same lassos, so a recognizer must accept them together.

*Specimen.* All six conjugacy classes are singletons — every rotation fixes the pair,
the dead class absorbing whatever factor moves. The genuine two-pair conjugacy waits
for `Even`: `([a·a],[a·a]) ≈ ([a],[a·a])`, two names for `a^ω`, worked in §3.5.

**The rotation lemma is the structural pivot of the paper.** Here it constrains the
acceptance layer (§3.3). In §7, applied not to the loop of a single lasso but to the
two-sided contexts of Arnold's syntactic congruence, the same rotation carries a *left*
context around the loop into a *right* extension at a shifted starting point — collapsing
the two-sided congruence to a right-invariant refinement, computable by the one operation
a monoid's table offers for free. That collapse is the construction's core; it is
Lemma 3.3 read at the level of contexts, and §7 only instantiates it.

### 3.3 The acceptance layer, and well-definedness

**Definition 3.4 (acceptance layer; object).** An **acceptance layer** over an algebra
`(𝒞, λ, M)` is a set `P` of linked pairs that is **saturated** — closed under conjugacy:

```
    (s, (gh)^ω) ∈ P  ⟺  (s·g, (hg)^ω) ∈ P     for all s, g, h ∈ 𝒞 with s·(gh)^ω = s.
```

An **object** is a tuple `𝓘 = (𝒞, λ, M, P)` with `(𝒞, λ, M)` an algebra and `P` an
acceptance layer. Saturation is a finite, mechanical closure — checkable directly on the
multiplication table, with no automaton and no external theory (§3.5 verifies it by hand
on the examples).

*Specimen.* `P = { ([b],[b]), ([a·b],[b]) }` — the two behaviors of `a*·b^ω`: "reading
`b`'s after nothing but `a`'s (if any), keep reading `b`'s". Saturation is immediate,
each pair being its own conjugacy class (§3.2). The flip `P^c` — the other four linked
pairs — is an equally legal layer, and denotes the complement (§4).

**The membership query.** Given a lasso `u·v^ω`, the object answers membership by folding
and one lookup:

```
    e := ⟦v⟧^ω,   s := ⟦u⟧·e,   accept  u·v^ω  ⟺  (s, e) ∈ P.
```

`(s, e)` is a linked pair (`e² = e`; `s·e = ⟦u⟧·e·e = s`) — the pair naming `u·v^ω`.

*Specimen.* Three runs. `b^ω`: the loop `[b]` is already idempotent, the empty stem
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
`s = s·(gh)^ω = (gh)^ω`, but `(gh)^ω` is a fold of nonempty words and no nonempty word
folds to `[ε]`). Letter-generation realizes `s, g, h` by words, and Lemma 3.3's two
presentations of the one word `w(pq)^ω` carry the pairs `(s, (gh)^ω)` and
`(s·g, (hg)^ω)`. Presentation-independence forces one verdict, i.e. both pairs lie in `P`
or neither. ∎

*Specimen.* Presentation-independence is immediate here — singleton conjugacy classes.
`Even` shows the force of the ⇒ direction: a `P` containing `(4,4)` but not `(2,4)`
would answer `a^ω` two ways (§3.5's saturation check).

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

*Specimen.* `(aab, bb)` reduces: `loop-power`⁻¹ to `(aab, b)`; the stem's last letter
`b` lies in the periodic part, so `loop-rotate`⁻¹ pulls it in, giving `(aa, b)` — the
canonical presentation (`t = 2`, `π = 1`), reached from any presentation of `aab·b^ω`.

By Lemma 3.5 a saturated `P` makes the query a function of the ω-word. Read as a
recognizer, the object accepts exactly the lassos of a unique regular ω-language
`L(𝓘)` — agreement on lassos determining a regular ω-language (§2) — and this is the
language the object denotes.

*Specimen.* The two accepting names admit exactly the lassos with stem in `a*b*` and
loop in `b⁺` — the lassos of `a*·b^ω`, and no others: `L(𝓘) = L`.

### 3.4 Residuals are derived data

Started at any class, the object answers membership of a residual.

**Proposition 3.7 (residuals).** For `s ∈ 𝒞` set
`L_s := { y·t^ω : (s·⟦y⟧·⟦t⟧^ω, ⟦t⟧^ω) ∈ P }` — the query run from `s` — with
`L_{[ε]} = L(𝓘)`. Then each `L_{s·λ(a)} = a⁻¹L_s`, residual equality is right-invariant
(`L_s = L_{s'} ⟹ L_{s·λ(a)} = L_{s'·λ(a)}`), and the residual automaton is a quotient of
the Cayley graph — all recomputable from `(𝒞, λ, M, P)`.

*Proof.* `L_{s·λ(a)} = a⁻¹L_s` is immediate from the fold:
`y·t^ω ∈ L_{s·λ(a)} ⟺ (s·λ(a)·⟦y⟧·⟦t⟧^ω, ⟦t⟧^ω) ∈ P ⟺ (s·⟦a·y⟧·⟦t⟧^ω, ⟦t⟧^ω) ∈ P
⟺ a·y·t^ω ∈ L_s`. Right-invariance follows, so quotienting the Cayley graph (Def 3.2) by
residual equality yields a deterministic, complete letter-graph — the residual
automaton. ∎

*Specimen.* `L_{[a]} = a⁻¹L = L` (the `a*` absorbs); `L_{[b]} = L_{[a·b]} = {b^ω}`;
`L_{[b·a]} = ∅`. The five-node Cayley graph quotients to a three-state residual
automaton — `{[ε],[a]}`, `{[b],[a·b]}`, `{[b·a]}` — strictly coarser than the algebra:
the residuals cannot tell `[b]` from `[a·b]`, the two-sided congruence can.

No congruence and no automaton is invoked. The residuals are derived data and rightly
enter no equality test between objects (§3.5, Figure 2).

### 3.5 Concrete form, read on the examples

Recall the three running examples (introduced fully in §1): **`GF(aa)`** — infinitely
many `aa`-factors, an LTL property; **`Even`** — an even number of `a`'s before the first
`!a`, then anything, *not* LTL; **`EvenBlocks`** — infinitely many `!a` and eventually
every completed `a`-block even, *not* LTL and prefix-independent. Each is met here only as
a table; its automaton waits until §6.

The object serializes as a portable artifact — a *semantic HOA* — listing the keyed
classes, letter map, multiplication table, and saturated accepting-pair set:

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

**Figure 2.** The exportable object `𝓘(GF(aa))` — keyed classes, letter map,
multiplication table, and saturated accepting-pair set (this core is the complete
language invariant, Theorem 5.1), plus an optional residuals block (here one state,
`GF(aa)` being prefix-independent) that is derived data (Proposition 3.7) and does not
enter the equality test. To test membership of `u·z^ω`: fold `u, z` to class ids, iterate
`z` to its idempotent `e`, set `s = u·e`, and accept iff `(s, e)` is listed under
`accept`. For `(a·!a)^ω`: `z = a·!a` folds to class `4`, already idempotent, so `s = 4`;
`4 4` is not in `accept`, so it is rejected — correctly, no `aa` recurs.

---

The three algebras side by side (class ids in cells; in all three
`λ(!a) = [!a]`, `λ(a) = [a]`; the wide row scrolls):

<table>
<tr>
<td valign="top">

**(a) `S(GF(aa))₊¹`**

```
 ·      [ε] [!a] [a] [!a·a] [a·!a] [a·a]
[ε]      0   1    2    3      4      5
[!a]     1   1    3    3      1      5
[a]      2   4    5    2      5      5
[!a·a]   3   1    5    3      5      5
[a·!a]   4   4    2    2      4      5
[a·a]    5   5    5    5      5      5
```

</td>
<td valign="top">

**(b) `S(Even)₊¹`**

```
 ·      [ε] [!a] [a] [a·!a] [a·a]
[ε]      0   1    2    3      4
[!a]     1   1    1    1      1
[a]      2   3    4    1      2
[a·!a]   3   3    3    3      3
[a·a]    4   1    2    3      4
```

</td>
<td valign="top">

**(c) `S(EvenBlocks)₊¹`**

```
 ·          [ε] [!a] [a] [!a·a] [a·!a] [a·a] [!a·a·!a] [a·!a·a]
[ε]          0   1    2    3      4      5       6        7
[!a]         1   1    3    3      6      1       6        6
[a]          2   4    5    7      1      2       6        3
[!a·a]       3   6    1    6      1      3       6        3
[a·!a]       4   4    7    7      6      4       6        6
[a·a]        5   1    2    3      4      5       6        7
[!a·a·!a]    6   6    6    6      6      6       6        6
[a·!a·a]     7   6    4    6      4      7       6        7
```

</td>
</tr>
</table>

**Table 3.** The algebras of the three examples, keyed shortlex. **(a)** `GF(aa)`:
`[a·a]` = "contains `aa`" is two-sided absorbing and every power cycle has period `1`;
the single accepting pair is `([a·a], [a·a])`. **(b)** `Even`: `[a]·[a] = [a·a]` and
`[a·a]·[a] = [a]`, so `{[a], [a·a]}` is a **period-2 cycle** — a `Z₂` visible on the raw
table. Read `[a·a]`'s row and column against the headers: it multiplies as the identity
on all four word classes, so `S(Even)₊` owns a neutral element (the fresh-identity
convention of §3.1); `[ε]` stays a separate class. Accepting pairs `([!a],[!a])`,
`([!a],[a·!a])`, `([!a],[a·a])`: once the accepting behaviour `[!a]` is reached, every
loop accepts. **(c)** `EvenBlocks`: the *same* period-2 cycle `{[a], [a·a]}` returns;
`[a·a]` is again neutral on the word classes, and `[!a·a·!a]` — a completed odd block —
is the two-sided zero. Six accepting pairs: `([!a],[!a])`, `([a·!a],[!a])`,
`([!a·a·!a],[!a])`, `([!a·a],[a·!a·a])`, `([!a·a·!a],[a·!a·a])`, `([a·!a·a],[a·!a·a])`.
In these single-atom examples `λ` is injective; in general it collapses interchangeable
letters — over `Σ = 2^{a,b}` a property depending only on `a ⊕ b` maps `a!b` and `!ab` to
one class.

---

**Reading the object by hand.** Three checks, all on the tables above and none touching
an automaton.

*Membership by one fold.* Is `(a·a)^ω ∈ Even`? Fold the loop `a·a` to class `[a·a] = 4`,
already idempotent (`4·4 = 4`); with empty stem `s = [ε]·4 = 4`. The pair `(4, 4)` is not
among `Even`'s accepting pairs, so it is rejected — correctly, `(aa)^ω` never sees a `!a`.

*The group is on the table.* In `Even`, `[a]·[a] = [a·a]` and `[a·a]·[a] = [a]`: the pair
`{[a], [a·a]}` is a cycle of period 2, a `Z₂` sitting in the algebra. Since (as §5 makes
exact) aperiodicity of the algebra is LTL-definability, this cycle *is* the reason `Even`
is not LTL — read straight off `M`, before any acceptance is consulted. `GF(aa)`'s table,
by contrast, has every power-cycle of period 1: aperiodic, hence LTL.

*Saturation, checked.* The query on `a^ω` presented two ways must agree, and does:
`(ε, a)` folds to the pair `([ε]·[a]^ω, [a]^ω) = ([a·a], [a·a]) = (4, 4)`, while `(a, a)`
folds to `([a]·[a]^ω, [a]^ω) = ([a]·[a·a], [a·a]) = ([a], [a·a]) = (2, 4)` — a conjugacy
step `(s, (gh)^ω) ≈ (s·g, (hg)^ω)` with `s = g = h = [a]`. Both `(4, 4)` and `(2, 4)` are
absent from `Even`'s accepting set, as saturation (Definition 3.4) demands; a `P`
containing one but not the other would be an *illegal* acceptance layer, its query
self-contradictory on the single word `a^ω`.

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
- The syntactic tuple: the quotient by Arnold's congruence, keyed shortlex, is a
  well-formed tuple and a function of `L` alone.
- Complete invariant theorem (current Thm 5.1): two languages are equal iff their
  tuples are byte-equal.
- Two minimality senses, both exact: coarsest congruence saturating `L` (Arnold);
  unique canonical complete invariant. (Minimal-recognizer claim dropped.)
- The two shapes double as the specification the construction must meet — hand-off
  to Part B.

## 6. The construction, I: seeing acceptance

- The input: any deterministic complete Emerson–Lei automaton `D` (current §2 automaton
  block, moved here).
- The first obstruction: the transition monoid forgets the marks acceptance reads.
- The acceptance-enriched monoid `EM(D)` (current Def 3.1) and the skeleton lemma
  (current Lemma 3.2).
- Necessity (current Prop 3.4): the one-state witness with trivial transition monoid
  under a nontrivial language.
- The enriched monoids of the three examples (current Table 2).

## 7. The construction, II: the rotation lemma

- The second obstruction: Arnold's congruence is two-sided, but a monoid's closure
  table offers only right multiplication.
- The collapse (current Lemma 4.1): a prefix acts only through the single state it
  reaches — evaluation factors through a finite left action on slots.
- The rotation lemma, stated at its natural generality: a left factor acts on a
  two-sided context only by re-indexing the slot — `a·e·b` at slot `q` equals `e·b·a`
  at slot `st_a(q)` — so the two-sided congruence is the coarsest right-invariant
  refinement of a slot-indexed seed; three-line proof.
- Discussion, factual: MS97 displayed the finitary × infinitary split with two-sided
  quantification still inside the loop; CPP08 saturated over context triples; the
  conjugation `a·e·b ↦ e·b·a` is the step neither took.
- Template remarks, only what we have: the right-extension-at-slots discipline is
  exactly an observation-table discipline (AF21's obstruction answered), and the
  one-sided fixpoint is what a symbolic implementation computes.
- Instantiation on `EM(D)`: `~lin` (residual equality at reached slots) and `~ω`
  (right-invariant profile equality), current Def 4.2 and Prop 4.3; the worked
  `EvenBlocks` split.

## 8. The algorithm and the two theorems

- Moore partition refinement from the seed `R = (~lin-class, Aprof)`, split by right
  letters to fixpoint (current Thm 4.5's procedure).
- Reading `P` off `D`: test one shortlex lasso per candidate linked pair.
- NEW — Theorem A (correctness, self-contained): `𝓘(D)` is well-formed (saturation
  proved, not assumed) and `L(𝓘(D)) = L(D)`; proof from the skeleton lemma and the
  collapse only, no Arnold.
- Theorem B (canonicity): `𝓘(D)` is the syntactic tuple of §5 — the constructed
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
  supplied, and the tuple is the deliverable.
- The rotation lemma stands on its own as the mathematical core.
- The family builds on `(𝒞, λ, M, P)`: companions consume the object this paper defines
  and constructs.

---

## Not transferred (parked, decide later)

- Current §6 (finite-word specialization, LTLf) — at most a one-line degeneration
  remark somewhere in Part B if we want the sanity check.
- Current §7 use-case development beyond the §4 teaser — lives in the companion papers.
- No prospects beyond material we have (no prophetic extraction, no learning-paper
  promises beyond the two factual template remarks in §7).
