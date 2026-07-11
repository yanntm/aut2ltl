# Constructing the Syntactic ω-Semigroup from a Deterministic Emerson–Lei Automaton

**Yann Thierry-Mieg** 

With significant inputs from
**Claude (Anthropic)** 

*Working draft — 2026-07-05*

## Abstract

The syntactic ω-semigroup of a regular ω-language `L` is its canonical
algebra: the ω-analogue of the syntactic monoid that underpins the entire
finite-word theory of regular languages. Introduced by Arnold in 1985 as the
coarsest congruence saturating `L`, it is presentation-independent and complete —
it determines membership, equivalence, and every definability property of `L`,
including whether `L` is expressible in linear temporal logic. Yet, unlike the
finite-word syntactic monoid, which has been computed routinely for three decades,
the syntactic ω-semigroup has, to our knowledge, never been constructed from an automaton. The obstruction is not
merely its size: computing it requires two ingredients the literature holds only
separately — a recognizer that remembers *acceptance along runs* rather than only
transitions, and a way to compute the inherently *two-sided* syntactic congruence
without ever quantifying over two-sided contexts. We supply both. The first is the
acceptance-enriched monoid `EM(D)`, read off any deterministic form `D` of `L`; we
prove it recognizes `L` and that the syntactic ω-semigroup is a quotient of it. The second is a
collapse of Arnold's two context shapes into two independently checkable
relations — pointwise residual equality and right-invariant acceptance-profile
equality — together with a rotation lemma proving that the two-sided congruence is
computable by right multiplications alone. This yields the syntactic ω-semigroup explicitly, for the
first time, as a canonical and *exportable* semantic representation of an ω-regular
language, LTL-definable or not. That one object is a *semantic benchmark*: the
classical taxonomy of ω-regular languages falls out as read-offs of its structure —
language equality as table equality, LTL-definability as aperiodicity, the
safety–progress and topological hierarchies, the minimal acceptance (parity) index,
and, subsuming them, the exact Wagner degree — several of them with no practical tool
today. The construction is uniform over finite and infinite words; its finite-word
specialization is the classical syntactic monoid, of independent interest to the
learning community.

---

## 1. Introduction

Finite-word regular language theory has a keystone: the **syntactic monoid**. It is
canonical (a function of the language, not of any accepting automaton), it is
computable (from a minimal DFA, in standard tools since AMoRE in the 1990s), and it
is the object through which the deepest structural facts are read — most famously
Schützenberger's theorem, that a language is star-free (equivalently first-order
definable) exactly when its syntactic monoid is aperiodic [Sch65]. Learning,
classification, and decision procedures for finite-word languages all pass through
this one algebra.

Infinite words have the exact analogue in principle. Arnold [Arn85] defined the
**syntactic congruence** of a regular ω-language `L` — the coarsest congruence that
saturates `L` — whose quotient is the **syntactic ω-semigroup** (SωS). It is
presentation-independent and it is *complete*: it fixes membership,
equivalence, and definability, and — by the classical chain
`LTL = FO[<] = star-free = aperiodic SωS` [Kam68, Tho79, Per84, DG08] — reading
aperiodicity off it decides LTL-definability exactly, in both directions.

And yet the syntactic ω-semigroup is, in practice, a phantom. It is defined everywhere and built
nowhere: no tool, to our knowledge, materializes it from an ω-automaton, and the
existing algorithmic accounts of aperiodicity for ω-languages are nondeterministic
on-the-fly complexity arguments [DG08, Prop. 12.3] that emit no algebra and no
evidence. This paper asks why, and removes the obstruction.

**The obstruction is structural, not just size.** Two difficulties, each solved in
the literature *in isolation*, were never combined into a construction:

1. **Recognition must see acceptance along runs.** A recognizing algebra for an
   ω-language cannot forget the marks a run passes through — only its endpoints —
   because acceptance is a property of the infinitely-visited marks. Carton, Perrin
   and Pin [CPP08] give such a recognizer (Boolean matrices over `Q × Q` recording
   whether a path exists and whether it passes an accepting state) but they read the
   *syntactic quotient* only by brute-force saturation over all context triples — an
   example, not a procedure.

2. **The syntactic congruence is two-sided.** Arnold's congruence quantifies over
   both a left context and a right one, inside two shapes (a linear tail and an
   ω-power loop). Maler and Staiger [MS97] display the congruence as a conjunction
   of a finitary and an infinitary part — but compute no quotient, and their
   infinitary part still quantifies a two-sided context inside the loop.

Our contribution is to supply both missing pieces and thereby construct the SωS.
For (1) we define the **acceptance-enriched monoid** `EM(D)` and prove it recognizes
`L`, with the SωS a quotient of it (§3). For (2) we **collapse** Arnold's two
shapes: the linear shape becomes pointwise residual equality, the ω-power shape
becomes right-invariant profile equality, and a two-line **rotation lemma** proves
the two-sided congruence is computable with right multiplications alone (§4). The
main theorem is that this right-computable quotient *is* the SωS (Theorem 4.5).

**The object first, its uses second.** Having built the SωS, we reify it as a
canonical, complete, *exportable* representation of the language — what a minimal
deterministic ω-automaton would be if one existed, which for ω-words it does not
(§5). The classifications then become read-offs (§7): not merely *is `L` LTL*, but
where `L` sits in the safety–progress and topological hierarchies, which acceptance
condition it needs, and — subsuming these — its exact Wagner degree, each a structural
property of the one algebra. Rendering the algebra back into a defining formula or a
counter-free automaton, or packaging a portable non-LTL certificate, are downstream
constructions that consume the syntactic ω-semigroup; this paper builds it.

Three small examples run throughout, chosen to exercise both halves of the
construction and both of Arnold's context shapes. Their automata are collected in
Figure 1 and their algebraic fingerprints in Table 1; every notion introduced below
is stated once and then immediately read off these three.

- **`GF(aa) := GF(a ∧ Xa)`** — "infinitely many `aa`-factors." It *is* LTL, but a
  natural presentation encodes the letter `a` as a transposition, so its transition
  monoid carries a spurious group. The SωS *destroys* that group.
- **`Even := (aa)*·!a·Σ^ω`** — over the single atom `a`, an even number of `a`'s then a
  `!a` then anything; in PSL, the words with a prefix matching the SERE
  `{a[*2]}[*] ; !a`. The canonical mod-2 language; *not* LTL, its group genuine, and —
  because a prefix fixes the parity — refuted by Arnold's *linear* (first) shape.
- **`EvenBlocks`** — "infinitely many `!a`'s, and eventually every completed `a`-block
  has even length"; the same `{a[*2]}` even-block SERE, now recurring. Also *not* LTL
  with a genuine mod-2 group, but *prefix-independent*: no finite prefix changes
  membership, so its group is invisible to the linear shape and only Arnold's
  *ω-power* (second) shape can witness it. This is the example that keeps both shapes
  honest.

The two non-LTL examples are deliberately PSL/SERE properties: SEREs are the standard
ω-regular superset of LTL used in hardware specification (IEEE 1850), and the mod-`p`
counting that takes a property out of the star-free/LTL fragment lives *syntactically*
in an even-repetition `{·}[*2]`. Deciding whether a written PSL property is in fact
LTL — simpler, and far better tool-supported — is itself a use of the object (§7);
these two are its minimal witnesses.

---

<table>
<tr>
<td align="center"><img src="sos_figs/img/gf_aa.png" alt="GF(aa) run-parity automaton" width="280"></td>
<td align="center"><img src="sos_figs/img/even.png" alt="Even automaton" width="280"></td>
<td align="center"><img src="sos_figs/img/evenblocks.png" alt="EvenBlocks automaton" width="280"></td>
</tr>
<tr>
<td align="center"><b>(a) <code>GF(aa)</code></b><br>2 states, <code>Inf(0)</code> (Büchi).<br>The <code>a</code>-letter transposes the<br>two states — a <code>Z₂</code> in the<br>transition monoid.</td>
<td align="center"><b>(b) <code>Even</code></b><br>4 states, <code>Inf(0)</code> (Büchi).<br>Parity pair <code>2/1</code>, an accepting<br>sink <code>0</code>, a rejecting sink <code>3</code>.</td>
<td align="center"><b>(c) <code>EvenBlocks</code></b><br>2 states, <code>Fin(0) ∧ Inf(1)</code>.<br>Prefix-independent; the parity<br>of a completed block lives on<br>the <code>!a</code>-transitions' marks.</td>
</tr>
</table>

**Figure 1.** The deterministic, complete, transition-based Emerson–Lei automata
`D` of the three running examples, as Spot renders them — a transposition-carrying `GF(aa)`, a four-state
`Even`, a prefix-independent `EvenBlocks`. Every value in this paper is read off
these three examples.

---

| example | PSL/SERE source | \|Q\| | \|EM\| | \|S(L)₊¹\| | group in TM? | group in `S(L)₊`? | LTL? | witness shape / defining formula |
|---|---|:--:|:--:|:--:|:--:|:--:|:--:|---|
| `GF(aa)` | `G F(a & Xa)` | 2 | **10** | **6** | yes (`Z₂`) | **no** | **yes** | defining formula ≡ `GF(a ∧ Xa)` |
| `Even` | `{ {a[*2]}[*] ; !a }!` | 4 | 7 | 5 | yes | **yes (`Z₂`)** | no | `F₁` (linear): `aⁿ·!a·a^ω ∈ L ⟺ n` even |
| `EvenBlocks` | `GF!a ∧ FG(!a → X{{a[*2]}[*];!a}!)` | 2 | **16** | 8 | yes | yes (`Z₂`) | no | `F₂` (ω-power): `(aⁿ·!a)^ω`, by parity of `n` |

**Table 1.** Algebraic fingerprints of the three examples. `|EM|` is the
acceptance-enriched monoid, `|S(L)₊¹|` the constructed SωS (a fresh identity
adjoined unconditionally — the convention fixed in §2); a group
in the *transition* monoid may be a presentation artifact, whereas a group in `S(L)₊` is
intrinsic and equivalent to non-LTL-definability. The `GF(aa)` row is the story in
miniature — a `Z₂` in `EM` but **none** in `S(L)₊`, hence LTL — while `Even` and
`EvenBlocks` carry a real group into `S(L)₊` and a `{·}[*2]`-rooted witness out.

---

## 2. The objects, in plain terms

We assume the reader is comfortable with ω-automata — Büchi acceptance, ω-regular languages — and
with linear temporal logic (LTL). This section fixes the few algebraic objects the construction
stands on, adapting the presentation of Perrin and Pin [PP04], each paired with the intuition tying
the algebra back to infinite-word languages, illustrated on the three running examples.

**We only ever look at lassos.** A **lasso** (ultimately-periodic word) is `u·v^ω`: a
finite stem `u`, then a finite loop `v` repeated forever. The organizing fact: *two
ω-regular languages are equal iff they agree on all lassos* [PP04]. Classifying `L` is
therefore nothing but sorting lassos into finitely many **types**, and every object
below is machinery for naming and sorting them.

**The algebra is a finite monoid plus one operation — "loop forever."** Finite words
are classified by a finite **monoid**: an associative product with a unit,
concatenation collapsed onto finitely many values (`φ(uv) = φ(u)φ(v)`). Infinite words
need exactly one thing more — a way to say "repeat this loop forever" — because no
product of finite pieces expresses `v^ω`. Adjoining that single operation, an **infinite
power** `s ↦ s^ω`, to a finite monoid yields an **ω-semigroup** `S = (S₊, S_ω)`:
`S₊` the types of finite words, `S_ω` the types of ω-words [PP04, Ch. II]. That is the
whole exotic content. A morphism `φ : Σ^∞ → S` **recognizes** `L` when membership
depends only on the type — `L = φ⁻¹(P)` for a set `P` of accepting ω-types.

**A linked pair is the name of a lasso.** Read a lasso `u·v^ω` through a finite `φ`
(Ramsey's theorem): the loop's repeated image settles on an **idempotent** value
`e = e·e` — in a finite monoid, powers `φ(v), φ(v)², …` cannot stay new forever, so one
of them is idempotent — and the stem settles on an `s` with `s·e = s` (the stem sits
before the loop and is absorbed by it). The pair `(s, e)` with `s·e = s`, `e² = e` is a
**linked pair**: `s` names the stem, `e` names the loop, and together they name the
lasso `u·v^ω` (`φ(u) = s`, `φ(v) = e`). Since a recognizer is fixed by which lassos it
accepts, it is fixed by its set of **accepting linked pairs** — which is why (§5) the
acceptance datum of our object is a *set of pairs*, not merely a subset of a monoid.

*Example (where each language keeps its verdict).* `GF(aa)` decides on the **loop** `e`:
`u·v^ω` has infinitely many `aa` iff the loop does, so the accepting pairs are those
with an `aa` in `e`, any `s`. `Even` decides on the **stem** `s`: once a `!a` is seen
the loop is irrelevant, and acceptance is fixed by whether the stem is "an even block
of `a`'s then `!a`". `EvenBlocks` decides on the loop again but is **stem-blind** — a
finite stem never matters — accepting iff the loop completes only even blocks. Loop,
stem, loop-but-stem-blind: the three cases the construction must cover.

We fix a finite alphabet `Σ` (for LTL applications `Σ = 2^AP`), write `Σ*`, `Σ^ω`,
`Σ^∞ = Σ* ∪ Σ^ω`, and take `L ⊆ Σ^ω` regular. The running examples use the single
atom `a`, so `Σ = {a, !a}`, with `!a` the letter where `a` does not hold. The input
is any **deterministic,
complete** automaton `D = (Q, ι, δ, C, Acc)` with `L(D) = L`: a finite state set `Q`,
an **initial** state `ι ∈ Q`, a transition function `δ : Q × Σ → Q`, a finite set `C`
of acceptance **marks** carried on transitions, and an acceptance condition `Acc`
(below). Reading a word steps `D` from state to state: at `q`, a letter `a` moves to
the single successor `δ(q, a)` — *deterministic* because `δ` is a function (one
successor, never a choice), *complete* because it is total (a successor for every
letter, so no run ever stalls). An ω-word `α = a₀a₁⋯` thus traces one infinite
**run** `q₀ →^{a₀} q₁ →^{a₁} ⋯` from `q₀ = ι`, with `q_{i+1} = δ(q_i, a_i)` — unique,
and defined for every `α`; each step's transition carries a (possibly empty) subset
of `C`, the marks collected there. Determinization of an arbitrary Emerson–Lei
automaton is always possible, if worst-case exponential [Saf88], so such a `D` exists
for any regular `L`.

Acceptance reads only which marks *recur* — the set of marks seen infinitely often
along the run. `Acc` is an **Emerson–Lei** condition — a positive Boolean combination
of `Inf(c)` ("`c` occurs infinitely often") and `Fin(c)` ("`c` occurs only finitely
often") over `c ∈ C` — evaluated on that infinitely-often set; it is the most general
ω-regular acceptance, subsuming Büchi, co-Büchi, Rabin, and Muller as special shapes.
A word is **accepted** — a member of `L(D)` — exactly when its run from `ι` satisfies
`Acc`, and we require `L(D) = L`. More generally, for any state `q` its **residual**
is the ω-language `L(q) = { α ∈ Σ^ω : the run of D from q on α satisfies Acc }` — what
`D` would accept were `q` the start. Determinism ties residuals to the language: a
finite prefix `u` read from `ι` lands in one state, so `L(ι·u) = u⁻¹L` for every
`u ∈ Σ*`. We write `Reach = δ(ι, Σ*) ⊆ Q` for the set of states some finite
prefix reaches.

*Example (Figure 1).* The three running automata instantiate `Acc` across the
Emerson–Lei range. `GF(aa)` reads `Inf(0)` for a single mark `0` placed on the
`a`-transition taken from the "just saw an `a`" state — the run passes `0`
infinitely often iff `aa` recurs. `Even` is a guarantee: `Inf(0)` for the mark on
the accepting sink's self-loops — the run reaches the sink (after an even `a`-prefix
closed by `!a`) or never does. `EvenBlocks` needs the full `Fin(0) ∧ Inf(1)` shape,
each `!a`-transition marked by the parity of the block it closes — mark `1` on an
even block, mark `0` on an odd one: `Inf(1)` forces infinitely many even-block
completions, `Fin(0)` forbids an odd one infinitely often, so together eventually
every completed block is even and infinitely many blocks are completed. The residuals separate `Even`'s four
states pairwise (`q₀ ≠ q₁` because one `!a` accepts, the other rejects) but collapse
both states of `EvenBlocks` to a single residual — the prefix-independence that
Proposition 4.6 will read algebraically.

With the objects named, the algebra is built by settling one question: *when are two
finite words the same ingredient* — interchangeable inside every lasso, so that
swapping one for the other never changes membership? Agreement on the **stem** side is
just agreement of residuals (the futures `L(q)` above), the finitary half, which §4 will
call `~lin`; agreement on the **loop** side is subtler. Arnold's congruence pins both
down at once. (This is also the one place a linked pair is *computed* rather than
named: reading a lasso, iterate the loop's image until it stops changing — that fixed
value is the idempotent `e`; §5 uses exactly this.)

**The syntactic congruence (Arnold), recalled in full.** Everything downstream
transports one 1985 definition of Arnold [Arn85], so we state it precisely and say
what it delivers. On finite words, the syntactic congruence declares `u ≈ v` when
they are interchangeable in every context `x·_·y` — same membership under any left
and right finite padding. On infinite words a context must yield a lasso, and the
mutation can sit in only two places: in the **stem** (a finite change, with a loop
appended to make it infinite), or **inside the loop**. These are Arnold's two shapes,
and they are exactly the stem/loop split of a lasso. Two finite words `u, v ∈ Σ*` are **syntactically congruent** for
`L`, written `u ≈_L v`, when interchangeable in both:

```
    (linear)    ∀ x, y ∈ Σ*, t ∈ Σ⁺ :   x·u·y·t^ω ∈ L  ⟺  x·v·y·t^ω ∈ L
    (ω-power)   ∀ x, y ∈ Σ*         :   x·(u·y)^ω  ∈ L  ⟺  x·(v·y)^ω  ∈ L
```

Arnold proves three facts we rely on. First, `≈_L` has **finite index** (its classes
are the finitely many behaviors an ω-regular `L` can distinguish). Second, its
quotient, completed with the linked-pair (infinite-power) data, is a finite
ω-semigroup that **recognizes `L`** — the quotient morphism is a recognizer. Third,
it is the **coarsest** congruence saturating `L`, hence *canonical*: any two automata
for `L` yield the same quotient. This quotient `S(L)₊ = Σ⁺/≈_L`, with its linked-pair
completion `S(L)`, is the **syntactic ω-semigroup** (SωS).

A notational convention is fixed here, deliberately: `S(L)₊¹` denotes
`S(L)₊` with a **fresh** identity `[ε]` adjoined *unconditionally* — not the
standard `S¹` of semigroup theory, which adjoins a unit only when none
exists. The distinction is not idle, because `S(L)₊` can own a neutral
element of its own: in `S(Even)₊` below, `[a·a]` multiplies as the identity
on every word class (Table 3) — and the same holds of `[a·a]` in
`S(EvenBlocks)₊`, so two of the three running specimens carry one. Under the
convention such an element nonetheless remains a
class of its own, keyed by a non-empty word, and `[ε]` is always a separate
class keyed by the empty word. Canonicity is unaffected — the fresh
adjunction is a function of `L` — and every class except `[ε]` carries a
non-empty key, which the acceptance read-off of §5 depends on. The two shapes are genuinely independent —
Proposition 4.6 exhibits a language separated by one shape and blind to the other —
so a construction may not drop either.

*Example.* `Even` is separated by the *linear* shape and only it: taking `x = ε`,
`y = ε`, tail `t = !a·a` (any lasso opening with `!a`), the words `a` and `aa` give
`a·!a·(a)^ω ∉ Even` (odd prefix) but `aa·!a·(a)^ω ∈ Even` (even prefix) — so `a ≉_L aa`
witnessed linearly. `EvenBlocks` is the opposite: *no* linear context separates any
two words (prefix-independence — a finite mutation is swallowed), yet the *ω-power*
shape does, with `y` closing a block: `(a·!a)^ω` completes odd blocks forever and is
rejected, `(aa·!a)^ω` completes even blocks and is accepted, so `a ≉_L aa` witnessed
only in the loop. The two examples are exactly the two shapes made concrete.

*On the examples.* For `Even`, the letter `a` toggles the a-count parity before the
first `!a`, and no finite context can undo that parity: `a` has order 2 in `S(Even)₊`
— a real group, so `Even` is not LTL. For `GF(aa)`, a run-parity presentation makes
`a` a transposition of two states, but at infinity the parity is invisible to
membership (an `aa` factor either recurs or not, a threshold not a count); the group
is an artifact of the presentation and, as §4 shows, is absent from `S(GF(aa))₊`,
which is aperiodic.

The task is to build the syntactic ω-semigroup `S(L)` from the deterministic
automaton `D`. The two keys to do so follow.

---

## 3. Key I — the acceptance-enriched monoid

The recognizer must remember what acceptance reads. The transition monoid of `D` —
the maps `q ↦ δ(q, w)` — does not: it forgets the marks a run collects, which is
exactly the data an Emerson–Lei condition consumes. We therefore enrich it.

**Definition 3.1 (enriched monoid).** For a finite word `w`, its **enriched
element** is the map

```
    ⟦w⟧ : q ↦ ( δ(q, w),  mk(q, w) ),
```

where `mk(q, w) ⊆ C` is the set of marks on the transitions of the run from `q` on
`w`. `EM(D)` is the set of enriched elements under composition

```
    ⟦w⟧·⟦w'⟧ : q ↦ ( δ(δ(q,w), w'),  mk(q,w) ∪ mk(δ(q,w), w') ),
```

a transformation monoid on the finite set `Q × 2^C`, generated by the letter
elements `⟦a⟧` (`a ∈ Σ`), with identity `⟦ε⟧ : q ↦ (q, ∅)`.

Write `st_e(q)`, `mk_e(q)` for the two components of `e ∈ EM(D)` at `q`. The map
`⟦·⟧ : Σ* → EM(D)` is a monoid morphism by construction.

*Example (Table 2).* On `GF(aa)`, the elements `⟦a⟧` and `⟦a·a·a⟧` have the *same*
state part — both transpose the two states, so the transition monoid identifies
them — yet differ in the *mark* part: the longer word closes an `aa` and collects
the `Inf`-mark that a single `a` does not. Separating equal state maps by their
marks is the whole point of the enrichment (Proposition 3.4). Closing `⟦a⟧`, `⟦!a⟧`
under composition yields the ten elements of `EM(GF(aa))` — the empty word, five
`aa`-free elements, and the absorbing "contains `aa`" behavior in four state-map
variants (all four carry the full mark everywhere) —
tabulated in Table 2(a) alongside their fold to the six SωS classes of §4, with
the sibling monoids of the other two examples beside it: the enrichment run on
all three presentations at once (the wide row scrolls).

---

<table>
<tr>
<td valign="top">

**(a) `EM(GF(aa))`**, Fig. 1(a)

| `⟦w⟧` | at `0` | at `1` | → class |
|---|:--:|:--:|:--:|
| `ε` | `(0, ∅)` | `(1, ∅)` | `[ε]` |
| `!a` | `(0, ∅)` | `(0, ∅)` | `[!a]` |
| `a` | `(1, ∅)` | `(0, {0})` | `[a]` |
| `!a·a` | `(1, ∅)` | `(1, ∅)` | `[!a·a]` |
| `a·!a` | `(0, ∅)` | `(0, {0})` | `[a·!a]` |
| `a·a` | `(0, {0})` | `(1, {0})` | `[a·a]` |
| `!a·a·a` | `(0, {0})` | `(0, {0})` | `[a·a]` |
| `a·!a·a` | `(1, ∅)` | `(1, {0})` | `[a]` |
| `a·a·a` | `(1, {0})` | `(0, {0})` | `[a·a]` |
| `!a·a·a·a` | `(1, {0})` | `(1, {0})` | `[a·a]` |

</td>
<td valign="top">

**(b) `EM(Even)`**, Fig. 1(b)

| `⟦w⟧` | at `0` | at `1` | at `2` | at `3` | → class |
|---|:--:|:--:|:--:|:--:|:--:|
| `ε` | `(0, ∅)` | `(1, ∅)` | `(2, ∅)` | `(3, ∅)` | `[ε]` |
| `!a` | `(0, {0})` | `(3, ∅)` | `(0, ∅)` | `(3, ∅)` | `[!a]` |
| `a` | `(0, {0})` | `(2, ∅)` | `(1, ∅)` | `(3, ∅)` | `[a]` |
| `!a·!a` | `(0, {0})` | `(3, ∅)` | `(0, {0})` | `(3, ∅)` | `[!a]` |
| `a·!a` | `(0, {0})` | `(0, ∅)` | `(3, ∅)` | `(3, ∅)` | `[a·!a]` |
| `a·a` | `(0, {0})` | `(1, ∅)` | `(2, ∅)` | `(3, ∅)` | `[a·a]` |
| `a·!a·!a` | `(0, {0})` | `(0, {0})` | `(3, ∅)` | `(3, ∅)` | `[a·!a]` |

</td>
<td valign="top">

**(c) `EM(EvenBlocks)`**, Fig. 1(c)

| `⟦w⟧` | at `0` | at `1` | → class |
|---|:--:|:--:|:--:|
| `ε` | `(0, ∅)` | `(1, ∅)` | `[ε]` / `[a·a]` |
| `!a` | `(0, {1})` | `(0, {0})` | `[!a]` |
| `a` | `(1, ∅)` | `(0, ∅)` | `[a]` |
| `!a·!a` | `(0, {1})` | `(0, {0,1})` | `[!a]` |
| `!a·a` | `(1, {1})` | `(1, {0})` | `[!a·a]` |
| `a·!a` | `(0, {0})` | `(0, {1})` | `[a·!a]` |
| `!a·!a·a` | `(1, {1})` | `(1, {0,1})` | `[!a·a]` |
| `!a·a·!a` | `(0, {0,1})` | `(0, {0})` | `[!a·a·!a]` |
| `a·!a·!a` | `(0, {0,1})` | `(0, {1})` | `[a·!a]` |
| `a·!a·a` | `(1, {0})` | `(1, {1})` | `[a·!a·a]` |
| `!a·!a·a·!a` | `(0, {0,1})` | `(0, {0,1})` | `[!a·a·!a]` |
| `!a·a·!a·a` | `(1, {0,1})` | `(1, {0})` | `[!a·a·!a]` |
| `a·!a·!a·a` | `(1, {0,1})` | `(1, {1})` | `[a·!a·a]` |
| `a·!a·a·!a` | `(0, {0})` | `(0, {0,1})` | `[!a·a·!a]` |
| `!a·!a·a·!a·a` | `(1, {0,1})` | `(1, {0,1})` | `[!a·a·!a]` |
| `a·!a·a·!a·a` | `(1, {0})` | `(1, {0,1})` | `[!a·a·!a]` |

</td>
</tr>
</table>

**Table 2.** The enriched monoids of the three examples, each element a
`(st, mk)` vector over its automaton's states, folded onto the SωS classes of
§4. **(a)** `GF(aa)`: reading a third `a` collects the `Inf`-mark `0` at state
`0` — the only difference between `⟦a⟧` and `⟦a·a·a⟧`, whose state parts are
the same transposition, so the pair is invisible to the transition monoid;
four elements collapse into the absorbing "contains `aa`" class and `a·!a·a`
rejoins `[a]`: **10 → 6**. **(b)** `Even` (states: `2` initial/even parity,
`1` odd parity, `0` accepting sink, `3` rejecting sink): `⟦aa⟧`'s *state*
part is the identity map — only the mark collected at the accepting sink
keeps it apart from `⟦ε⟧`: **7 → 5**. **(c)** `EvenBlocks`: here nothing
keeps them apart — `⟦aa⟧` *equals* `⟦ε⟧`, the identity element hosts two
classes (`[ε]` and the neutral `[a·a]`), which is the collision §2's
fresh-identity convention is built for; the language lives entirely in the
marks: **16 → 8**. Across the triptych, the quotient's compression is the
story: `10→6`, `7→5`, `16→8`.

---

**Lemma 3.2 (skeleton).** If two ω-words `α, β` factor into blocks with the same
sequence of enriched elements read from `ι` — i.e. `α = w₁w₂⋯`, `β = w'₁w'₂⋯` with
`⟦w₁⋯w_k⟧ = ⟦w'₁⋯w'_k⟧` for all `k` — then `α ∈ L ⟺ β ∈ L`.

*Proof.* Determinism gives a unique run for each. At every block boundary `k` the two
runs are at the same state `p_k = st_{⟦w₁⋯w_k⟧}(ι) = st_{⟦w'₁⋯w'_k⟧}(ι)`, and the
marks collected within block `k` are equal, `mk(p_{k-1}, w_k) = mk(p_{k-1}, w'_k)`, by
equality of the enriched elements and the composition law. Hence the two runs visit
the same states at boundaries and the same set of marks within each block, so
they have the same set of marks visited infinitely often — and `Acc`, an Emerson–Lei
condition, is a function of that inf-set alone. Thus the runs agree on acceptance. ∎

**Corollary 3.3 (`EM` recognizes `L`; the SωS is a quotient).** The syntactic
morphism `Σ* → S(L)₊` factors through `⟦·⟧ : Σ* → EM(D)`. Consequently there is a
surjective ω-semigroup morphism `EM(D) ↠ S(L)`, and `S(L)` is a computable quotient
of `EM(D)`.

*Proof.* Recall from §2 (Ramsey) that every ω-word factors into finite blocks whose
enriched images stabilise, and that Lemma 3.2 makes acceptance depend only on that
sequence of images. So if `⟦u⟧ = ⟦v⟧`, replacing one occurrence of `u` by `v` inside
any such block factorization leaves the enriched-element sequence — and hence, by
Lemma 3.2, membership — unchanged. Thus `⟦u⟧ = ⟦v⟧ ⟹ u ≈_L v`: the enriched congruence
refines `≈_L`, so `≈_L` factors through `EM(D)` and its quotient `S(L)` is a quotient
of `EM(D)`. ∎

**Proposition 3.4 (enrichment is necessary).** The transition monoid alone does not
recognize `L`: there are words `u, v` with `st_{⟦u⟧} = st_{⟦v⟧}` (equal state maps)
but `u ≉_L v`.

*Proof (a one-state witness).* Let `D` have a single state `p` over `Σ = {a, b}`, both
letters self-looping, an `Inf`-mark `c` on the `a`-loop only, and `Acc = Inf(c)` — so
`L = ` "infinitely many `a`" `= GF a`. The transition monoid is *trivial*: every word
induces the identity map on `{p}`, so `st_{⟦a⟧} = st_{⟦b⟧}`. Yet `a ≉_L b`, separated
by the ω-power context `_^ω`: `a^ω` collects `c` infinitely often and is accepted,
`b^ω` never collects `c` and is rejected. The enriched elements *do* separate them —
`mk_{⟦a⟧}(p) = {c} ≠ ∅ = mk_{⟦b⟧}(p)` — which is exactly the information the transition
monoid discards. ∎

The starkness is the message: a trivial transition monoid under a nontrivial language.
No amount of state bookkeeping recovers acceptance; the marks-along-the-run are
irreducible data, and `EM` is the smallest recognizer that keeps them.

Proposition 3.4 is why a group in the transition monoid proves nothing about `L`: it
can be pure encoding, invisible to `EM` and hence to the SωS. (Symmetrically,
aperiodicity of the transition monoid is *sufficient* for aperiodicity of `S(L)₊`,
inherited upward through the enrichment — a one-directional convenience, not part of
the object.) The `GF(aa)` example is exactly this situation, resolved in §4.

*On the examples.* The enriched monoid of `GF(aa)`'s 2-state run-parity presentation
has 10 elements (Table 2a); that of `Even` has seven — the sink-and-parity
behaviors closed under the two letters (Table 2b); that of `EvenBlocks` has
sixteen (Table 2c). All three carry a group in `EM` — the question §4 answers
is which survives the quotient.

---

## 4. Key II — the two-sided congruence, computed with right moves

Corollary 3.3 leaves us the syntactic congruence `≈_L` transported to a relation `~`
on the finite monoid `EM(D)` — congruent elements are those interchangeable in both
context shapes. Naively `~` quantifies over left context, right context, and loop.
We now collapse it into two relations, neither of which quantifies over a left
context, and prove the two-sided congruence is a right-refinement.

Throughout, `Acc(x, c)` for `x, c ∈ EM(D)` denotes the acceptance of an
ultimately-periodic word `w·z^ω` with `⟦w⟧ = x`, `⟦z⟧ = c` — well-defined by
Lemma 3.2 — read from `ι`.

**Lemma 4.1 (collapse).** `Acc(x, c)` depends on the prefix `x` only through the
single state `st_x(ι)`. Writing `A(q, c)` for the Emerson–Lei verdict of iterating
`c` from `q` (follow `st_c` from `q` to its closed cycle; take the marks `mk_c`
around that cycle; evaluate `Acc`), we have `Acc(x, c) = A(st_x(ι), c)`.

*Proof.* The prefix `w` (with `⟦w⟧ = x`) is read once; its marks are collected on a
finite run and are visited finitely often, so none lies in the inf-set of `w·z^ω`.
The inf-set is entirely determined by the ultimately-periodic tail `z^ω` read from the
state `st_x(ι)` the prefix reaches — which cycles through the functional graph of
`st_c` and repeats the marks `mk_c` around the closed cycle. Hence `Acc(x, c)` is a
function of `st_x(ι)` and `c` only, namely `A(st_x(ι), c)`. ∎

**Definition 4.2.** For `e, f ∈ EM(D)` (images of non-empty words) let

```
    e ~lin f   ⟺   ∀ q ∈ Reach :   L(st_e(q)) = L(st_f(q)),
    e ~ω  f    ⟺   ∀ b ∈ EM(D) :   Aprof(e·b) = Aprof(f·b),        where  Aprof(c) = (q ∈ Reach ↦ A(q, c)).
```

The slots are `Reach`, not `Q`: an unreachable state names no left context,
and letting it separate would over-refine the quotient on a non-trim `D`.

Here `b` ranges over all of `EM(D)`, the identity **included**: `b = ⟦ε⟧` is the
ω-power context with empty right padding `y = ε`, whose loop is `e` itself — a case
we must keep. This is harmless: `e` is the image of a non-empty word, so the loop
`e·b` is non-empty for every `b`, and `A(·, e·b)` is a genuine loop verdict; the
degenerate `A(·, ⟦ε⟧)` (an empty loop) would arise only from comparing the identity
class with itself, which is trivial.

*Example (a profile, read off the automaton).* In `GF(aa)`'s run-parity form
(Figure 1, Table 2) the letter `⟦a⟧` transposes the two states — `0 → 1` collecting no
mark, `1 → 0` collecting the `Inf`-mark `0`. Iterating `⟦a⟧` from either state runs
around the 2-cycle `{0, 1}`, whose marks are `{0}`; since `Acc = Inf(0)` accepts,
`A(0, ⟦a⟧) = A(1, ⟦a⟧) = 1`, so `Aprof(⟦a⟧) = (1, 1)` — matching `a^ω ∈ GF(aa)`. By
contrast `⟦!a⟧` resets both states to `0` with no mark, so its cycle `{0}` carries `∅`,
`Inf(0)` fails, and `Aprof(⟦!a⟧) = (0, 0)` — matching `(!a)^ω ∉ GF(aa)`. The profile is
exactly this per-state loop verdict, one bit per state.

**Proposition 4.3 (factorization).** `e ~ f  ⟺  e ~lin f  ∧  e ~ω f`.

*Proof.* *Linear shape.* By Lemma 4.1, `x·e·y·t^ω ∈ L ⟺ A(st_{x·e·y}(ι), t)`, and
`st_{x·e·y}(ι) = st_y(st_e(st_x(ι)))`. As `x` ranges over `EM(D)`, `st_x(ι)` ranges over
exactly `Reach`; fix such a `q`. The linear condition then reads
`∀ y, t : A(st_y(st_e(q)), t) = A(st_y(st_f(q)), t)`, i.e. the states `st_e(q)` and
`st_f(q)` accept the same ultimately-periodic words, i.e. (agreement on
ultimately-periodic words being language equality) `L(st_e(q)) = L(st_f(q))`. Over all
`q` this is `~lin`. The mark parts of `e, f` are irrelevant to it.

*ω-power shape.* By Lemma 4.1, `x·(e·y)^ω ∈ L ⟺ A(st_x(ι), e·y)`, and `∀x` collapses
to `∀q` as above, giving `∀ y : A(q, e·y) = A(q, f·y)` for all `q`, i.e.
`∀ y : Aprof(e·y) = Aprof(f·y)`, which is `~ω`. ∎

The linear half is computed **once, on `D`** — it is language-equivalence of reached
states, no monoid involved — and at the slot `q = ι` alone it is the classical
syntactic right congruence of Maler–Staiger [MS97]; `~lin` demands it at every start
state simultaneously. The ω half is a right-congruence condition seeded by profiles.
Neither has a left translation. What remains is to show the *two-sided* congruence
needs none.

*Example (the two halves divide the labor).* The two non-LTL examples sit at opposite
ends. In `Even`, `~lin` is already discriminating — the four states have four distinct
residuals — and the group is visible on the *state* side: `st_{⟦a⟧}` swaps `q₀ ↔ q₁`,
an order-2 action `~lin` sees directly. In `EvenBlocks`, `~lin` is *total* (one
residual, prefix-independence), so the linear half sees nothing at all; the entire
order-2 group is carried by `~ω`. Concretely, right-extend by `b = ⟦!a⟧` (close the
block): the loop `⟦a·!a⟧` is a length-1 (**odd**) block, so `(a·!a)^ω` violates `Fin(0)`
and `Aprof(⟦a·!a⟧)` rejects, whereas `⟦aa·!a⟧` is an **even** block and
`Aprof(⟦aa·!a⟧)` accepts. So `~ω` separates `⟦a⟧` from `⟦aa⟧` — their reached states
being identical, `~lin` never could. One example loads the finitary half, the other
the infinitary — and the construction needs both computed, which is Proposition 4.3
made concrete.

**Lemma 4.4 (rotation).** Let `R` be the equivalence that equates `e` and `f` exactly
when they have the same `~lin`-class *and* the same profile `Aprof`. Then `~` is the
coarsest **right-invariant** equivalence refining `R` — equivalently, two elements
that stay `R`-equal under every right extension are equal under every two-sided
context.

*Proof.* A left factor `a` acts on `R` only by re-indexing a slot. For `~lin`:
`st_{a·e}(q) = st_e(st_a(q))`, so prepending `a` merely evaluates `~lin` at the shifted
slot `st_a(q)` — pure determinism. For `~ω`, take the two mini-steps explicitly. First,
factor the ultimately-periodic word `(a·e·b)^ω = a·(e·b·a)^ω`: its acceptance from `q`
depends only on the loop `(e·b·a)^ω` read from the state reached *after* the prefix
`a`, which is `st_a(q)` — the prefix `a` changes nothing but the loop's starting state.
Second, by Lemma 4.1 that acceptance is exactly `A(st_a(q), e·b·a)`. Combining,

```
    Aprof(a·e·b)(q)  =  A(st_a(q), e·b·a)  =  Aprof(e·b·a)(st_a(q)),
```

so the left factor `a` has turned into a **right** extension `e·b·a` read at the
shifted slot `st_a(q)`, carrying no information of its own. Hence every two-sided
context reduces to a right extension at a re-indexed slot: if `e, f` stay `R`-equal
under all right extensions at all slots, they agree under all two-sided contexts.
Finally `R` is itself right-invariant (`~lin` because derivatives of equal languages
are equal, `L(s) = L(s') ⟹ L(δ(s,a)) = L(δ(s',a))`; `Aprof` by definition), so `~` is
the coarsest right-invariant equivalence refining the single seed `R`. ∎

Lemma 4.4 is the load-bearing step against Maler–Staiger: they *display* the
finitary × infinitary split; the rotation lemma is what makes the two-sided
syntactic congruence computable with the one operation a monoid's closure table
offers for free — right multiplication.

**Theorem 4.5 (the SωS, constructed).** `EM(D)/~ = S(L)`, where `~ = ~lin ∧ ~ω` is
the right-computable congruence of Definition 4.2. Concretely, `S(L)₊` is computed by
partition refinement (Moore's algorithm on `EM(D)`): start with blocks that group
elements sharing the same `~lin`-class and the same profile `Aprof` — the seed `R` of
Lemma 4.4; then repeatedly **split** a block whenever it contains `e, f` and a letter
`a ∈ Σ` with `e·⟦a⟧` and `f·⟦a⟧` in different blocks; stop when no split applies (at
most `|EM(D)|` splits). The final blocks are the classes of `~`.

*Proof.* By Corollary 3.3, `≈_L` factors through `EM(D)`, and by construction its
transported relation is exactly interchangeability in the two shapes, i.e. `~`; by
Proposition 4.3 this is `~lin ∧ ~ω`. So `EM(D)/~ = Σ⁺/≈_L = S(L)₊`, and the
linked-pair data (the accepting pairs, §5) completes it to `S(L)`. The stated
computation realizes `~` by Lemma 4.4: right-invariance of both seed components makes
one Moore-style refinement to fixpoint compute `~lin ∧ ~ω` exactly. ∎

---

The three multiplication tables, side by side (class ids in cells; in all
three, `λ(!a) = [!a]` and `λ(a) = [a]`; the wide row scrolls):

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

**Table 3.** Multiplication tables of the three SωSs. **(a)** `GF(aa)`:
`[a·a]` = "contains `aa`" is two-sided absorbing and every power cycle has
period `1` — the transition monoid's `Z₂` is gone, and `GF(aa)` is LTL; the
single accepting linked pair is `([a·a], [a·a])`. **(b)** `Even`: the group
survives — `[a]·[a] = [a·a]` and `[a·a]·[a] = [a]`, so `{[a], [a·a]}` is a
**period-2 cycle**, the `Z₂` that makes `Even` non-LTL. Read `[a·a]`'s full
row and column against the headers: it multiplies as the identity on all four
word classes — `S(Even)₊` owns a neutral element, the very situation §2's
fresh-identity convention is fixed for; `[ε]` remains a separate class
regardless. Its accepting linked pairs are `([!a],[!a])`, `([!a],[a·!a])`,
`([!a],[a·a])` — once the accepting sink (class `[!a]`) is reached, every
loop accepts. **(c)** `EvenBlocks`: the *same* period-2 cycle `{[a], [a·a]}`
returns, but prefix-independence makes it invisible to every linear context
(Proposition 4.6) — only the ω-power shape witnesses it. `[a·a]` is again
neutral on the word classes (two of the three specimens carry one, §2), and
`[!a·a·!a]` — a completed odd block inside — is the two-sided zero. Six
accepting linked pairs: `([!a],[!a])`, `([a·!a],[!a])`, `([!a·a·!a],[!a])`,
`([!a·a],[a·!a·a])`, `([!a·a·!a],[a·!a·a])`, `([a·!a·a],[a·!a·a])` —
acceptance reads "the recurring loop completes only even blocks, and
completes them infinitely often". In these single-atom examples `λ` is
injective — each letter keys its own class — but in general it collapses
interchangeable letters: over `Σ = 2^{a,b}` a property depending only on
`a ⊕ b` maps `a!b` and `!ab` (the two `a⊕b`-true letters) to one class.

---

**Proposition 4.6 (prefix-independence, as a theorem not a case).** `L` is
prefix-independent (`σα ∈ L ⟺ α ∈ L` for all `σ ∈ Σ*`) iff `L` has a single residual
iff `~lin` is total. In that case all discrimination is carried by `~ω`.

*Proof.* Prefix-independence says every residual `u⁻¹L` equals `L`; determinism then
gives one residual class, so `~lin`, which compares residuals of reached states, is
total. Conversely one residual class forces every prefix to preserve membership. ∎

*Example.* `EvenBlocks` is prefix-independent (deleting or inserting a finite prefix
changes neither "infinitely many `!a`" nor "eventually every completed `a`-block is
even"), so its `~lin` is total — the finitary half is blind, and the whole
non-LTL-ness is invisible until `~ω` is computed. This is not a corner case to be
handled specially; it is the generic situation for tail properties, and it is why a
construction resting on the right congruence alone (or on residuals alone) cannot even
*see* that `EvenBlocks` fails to be LTL.

Angluin and Fisman note the same blindness from the learning side: LTL languages with
a *trivial right congruence* exist, e.g. `FG(a ∨ Xa)` [AF21] — the profile half is the
repair, and the reason `EvenBlocks`, blind to the linear shape, is separated only in the
ω-power one.

*On the examples, resolved.* For `GF(aa)`, the ten enriched elements refine to **six**
`~`-classes, every class power-cycle of period 1: the run-parity words the transition
monoid kept apart are `~`-equivalent (at infinity the parity collapses to the
threshold "contains `aa`"), so `S(GF(aa))₊` is aperiodic — `GF(aa)` is LTL, its
group destroyed by the quotient. For `Even`, the letter `a`'s order-2 action survives
into `S(Even)₊`: a genuine `Z₂`, so `Even` is not LTL.

---

## 5. The reified object

Theorem 4.5 gives the syntactic ω-semigroup `S(L)` concretely, as the tuple
`𝓘(L) = (𝒞, λ, M, P)`:

- `𝒞` — the finite set of **classes**, the `~`-classes of Theorem 4.5, each **keyed**
  by its **shortlex-least representative word** over `Σ` (a language invariant,
  independent of `D`);
- `λ : Σ → 𝒞` — the **letter map** `λ(a) = [a]`, sending each letter to its class;
- `M : 𝒞 × 𝒞 → 𝒞` — the **multiplication table** `M(s, t) = s·t`, the Cayley table of
  `S(L)₊` (Table 3);
- `P ⊆ 𝒞 × 𝒞` — the set of **accepting linked pairs**
  `{ (s, e) : e² = e, se = s, u·z^ω ∈ L for ⟦u⟧ ∈ s, ⟦z⟧ ∈ e }`, both
  components ranging over the word classes (`e = [ε]` would name an empty
  loop, and `se = s` with `e ≠ [ε]` excludes `s = [ε]` too), recovering `L`
  itself and not merely its algebra.

Shortlex keying makes every component a function of `L` alone. `P` is read directly
off the automaton: for each such `(s, e)` of word classes with `e·e = e` and
`s·e = s`, take the shortlex-least words `w_s, w_e` — non-empty by the §2
convention — and test `w_s·(w_e)^ω` for acceptance on `D`; put
`(s, e)` in `P` iff it accepts. Any representatives give the same verdict — exactly
what `(s, e)` being a linked pair guarantees (Lemma 3.2).

**Theorem 5.1 (complete invariant).** For a fixed `Σ`, the tuple `𝓘(L) = (𝒞, λ, M, P)`
determines `L` exactly: two regular ω-languages over `Σ` are equal iff their `𝓘`
coincide.

*Proof.* `𝓘(L)` encodes the syntactic morphism `⟦·⟧` up to the canonical keying and
the accepting set. Membership of any ultimately-periodic word `u·z^ω` is decided by
computing `(⟦u⟧, ⟦z⟧)`, reducing to its linked pair, and testing `P`. Since regular
ω-languages are equal iff they agree on ultimately-periodic words, `𝓘(L)` determines
`L`. Conversely `𝓘` is a function of `L` (Theorem 4.5, canonical keying), so equal
languages have equal `𝓘`. ∎

Theorem 5.1 is what makes the syntactic ω-semigroup worth building as an object rather than as a means
to a verdict. It is a **canonical, complete, presentation-independent semantic
representation** of `L` — what a minimal deterministic ω-automaton would be, except
that for ω-words no canonical minimal deterministic automaton exists. It is
*exportable*: a serialization of `𝓘(L)` is a portable artifact — a semantic HOA — that
any downstream consumer can read, and two such artifacts are language-equal iff
byte-equal after canonical keying. Notably `𝓘` needs no aperiodicity: it is defined
for *all* regular ω-languages, LTL or not. What one does with the object is the
subject of §7; that one *has* it is the point of this section.

*Example (canonicity made visible).* Compute `𝓘(GF(aa))` from the run-parity
presentation of Figure 1(a) — two states, a `Z₂` transition monoid — and again from
the reset presentation of Figure 3 — the *same* two states, but every letter
acting as a reset: an aperiodic transition monoid and a smaller enriched
monoid (7 elements against 10). The two runs return the *identical* `𝓘`: six classes keyed
`[ε], [!a], [a], [!a·a], [a·!a], [a·a]`, one multiplication table, the single accepting
pair `([a·a],[a·a])` (Table 3). No automaton-level object does this — the two
presentations are not isomorphic and neither is "the" minimal one — which is the
precise sense in which the algebra is canonical where the automata are not. Swapping
`P` for its complement, keeping every other table byte-for-byte, yields `𝓘` of the
complement language: the algebra is shared between `L` and `L̄`, and `P` alone
separates them — the reason `P` is part of the invariant.

---

`𝓘(GF(aa))` serialized (format v1):

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

**Figure 2.** The exportable artifact `𝓘(GF(aa))` — a "semantic HOA" listing the keyed
classes, letter map, multiplication table, and saturated accepting-pair set (this core
is the complete language invariant), plus an optional residuals block (here a single
state, `GF(aa)` being prefix-independent) that does not enter the equality test —
derived data, recomputable from the core (Proposition 5.3);
reproduced byte-for-byte from the tool's export. To test
membership of `u·z^ω`: fold `u, z` to class ids, iterate `z` to an idempotent `e`, set
`s = u·e`, and accept iff `(s, e)` is listed under `accept`. For `(a·!a)^ω`: `z = a·!a`
folds to class `4`, already idempotent, `s = 4`; `4 4` is not in `accept`, so it is
rejected — correctly, no `aa` recurs.

---

<table>
<tr>
<td align="center"><img src="sos_figs/img/gf_aa_reset.png" alt="GF(aa) reset automaton" width="280"></td>
<td valign="middle">

| presentation | `\|Q\|` | `a` acts by | group in TM? | `\|EM\|` | `𝓘(GF(aa))` |
|---|:--:|---|:--:|:--:|---|
| run-parity (Fig. 1a) | 2 | transposition | yes — `Z₂` | 10 | Figure 2 |
| reset (left) | 2 | reset | no — aperiodic | 7 | *byte-identical* |

</td>
</tr>
</table>

**Figure 3.** Canonicity, exhibited. The reset presentation of `GF(aa)`: the
same two states as Figure 1(a), but each letter sends *every* state to one
place (`a` to the "just saw `a`" state, whose `a`-self-loop carries the
`Inf`-mark; `!a` to the other). The two automata are not isomorphic, their
transition monoids disagree even on whether a group is present, and their
enriched monoids have different sizes — yet the construction returns the
byte-identical six-class `𝓘(GF(aa))` of Figure 2 from both. The `Z₂` of
Figure 1(a) was pure presentation; Theorem 4.5's quotient is where it dies.

---

**Definition 5.2 (right Cayley graph).** `Cay(L)` is the graph with nodes `𝒞`,
root `[ε]`, and an edge `s →ᵃ M(s, λ(a))` for each `s ∈ 𝒞`, `a ∈ Σ` — the
right regular representation of `S(L)₊¹`, a function of `(𝒞, λ, M)` alone.
Every node is reachable from the root (its shortlex key spells the path) and
carries one out-edge per letter: the algebra of `M`, as a machine.

Rooted, deterministic, and complete, `Cay(L)` is the skeleton of an automaton
with state set `𝒞`; an Emerson–Lei acceptance on its edges, derived from `P`,
would complete it into a canonical — not minimal — deterministic automaton for
`L`. By construction — `Cay(L)` is the algebra acting on itself — this
canonical form is counter-free iff `L` is LTL: where Figure 1(a) smuggled a
`Z₂` into a presentation of an LTL language, the canonical one cannot. We
leave the extraction as a prospect.

**Proposition 5.3 (residuals are derived data).** The residual `u⁻¹L` depends
only on the class `[u]`; write `L_s` for the residual of `s ∈ 𝒞`
(`L_{[ε]} = L`). Membership is one fold and one lookup —
`y·t^ω ∈ L_s ⟺ (s·[y]·e, e) ∈ P`, `e` the idempotent power of `[t]` — and
residual equality is right-invariant, so the residual automaton is the
quotient of `Cay(L)` by it. The residuals block of Figure 2 is thus
recomputable from `(𝒞, λ, M, P)`: shipped for convenience, it rightly enters
no equality test.

*Proof.* If `u ≈_L v`, Arnold's linear shape at `x = ε` gives
`u·y·t^ω ∈ L ⟺ v·y·t^ω ∈ L` for all `y, t`; two regular ω-languages agreeing
on all lassos are equal (§2), so `u⁻¹L = v⁻¹L` and the residual is a function
of `[u]`. The membership formula is Theorem 5.1's fold started at `s` (`e` is
a word class, never `[ε]`, the identity being fresh — §2). Right-invariance:
`L_s = L_{s'}` gives `L_{s·λ(a)} = a⁻¹L_s = a⁻¹L_{s'} = L_{s'·λ(a)}`, so
quotienting `Cay(L)` by residual equality yields again a deterministic,
complete letter-graph — the residuals block. ∎

---

A first, aperiodicity-free use: **language equality is table equality.** Where
pairwise equivalence of `N` languages costs `O(N²)` automaton products, hashing `𝓘`
buckets a corpus by true language in a hash join — the natural operation for
deduplicating large language sets, and the first entry of the calculus §7.2 opens.

---

## 6. The finite-word specialization

Nothing in this section is new — the finite-word syntactic monoid has been computed
routinely for three decades (§1). The point is uniformity: the construction of
§3–4, run on a DFA, lands exactly on that classical object, each key degenerating
in a way that measures what infinity alone costs — and the degenerate case being
the known answer is a check on the machinery. It also addresses two neighboring
communities: LTLf, which lives on finite traces, and automata learning, which
reconstructs languages — finite or ω — from finite observations.

**Proposition 6.1 (degeneration).** Let `D` be a complete DFA for `L ⊆ Σ*`, with
final states in place of marks. Then (i) the enrichment is vacuous and `EM(D)` is
the plain transition monoid of `D`; (ii) the ω-power shape disappears with the
ω-words it quantified over, and the whole congruence is the linear half:
`e ~ f ⟺ ∀ q ∈ Reach : L(st_e(q)) = L(st_f(q))`, with finite-word residuals
`L(q) ⊆ Σ*`; (iii) the quotient is the syntactic monoid of `L`, equal to the
transition monoid of the minimal DFA.

*Proof.* (i) With no marks there is no `mk` component. (ii) is the linear-shape
argument of Proposition 4.3 with the tail `t^ω` deleted: acceptance of `x·e·y`
from `ι` depends on `x` only through the reached state (the Lemma 4.1 collapse,
now trivial — a finite run has no inf-set), so two-sided contexts reduce to
residual equality at every reachable slot. No rotation is needed and no
refinement iterates: residual equality is already left- and right-invariant, so
the seed is the congruence. (iii) follows: quotienting the transition maps by
residual equality of their targets is computing the transition monoid of the
residual (minimal) automaton, the classical presentation of the syntactic
monoid. ∎

Read against §3–4, the specialization audits the two keys. Key I is the price of
acceptance *along* runs: endpoint acceptance costs nothing, and Proposition 3.4
has no finite-word analogue. Key II is the price of the loop: only the ω-power
shape forces the profile relation and the rotation lemma. The invariant
specializes the same way: `𝓘` keeps `(𝒞, λ, M)` and swaps the accepting linked
pairs `P` for a plain accepting subset `F ⊆ 𝒞` — the §2 point that ω-acceptance
is a *set of pairs*, not a subset, in exact counterpoint. One convention
difference is deliberate: on finite words the congruence is taken on `Σ*`
directly — no context shape degenerates on the empty word — so a
neutrally-acting word *shares* the identity's class, exactly as in the
classical syntactic monoid; at ω the identity is fresh (§2), and where a
neutral element exists the two counts differ by that one redundant unit.
One format serves both
worlds. And where §5 noted that no canonical minimal deterministic ω-automaton
exists, on finite words the minimal DFA *does* exist — yet definability is still
read off the algebra, not the automaton: the same moral, in the easier world.

*Example.* The finite core of `Even` is `W = (aa)*·!a`, with `Even = W·Σ^ω` (the
guarantee shape of §7.2's ladder made literal). Its minimal DFA is Figure 1(b) read as a
DFA — the accepting sink cut back to a final state whose successors fall to the
rejecting sink — and its syntactic monoid keeps the same `Z₂`: `[a]·[a] = [a·a]`,
`[a·a]·[a] = [a]`, the period-2 cycle of Table 3. So `W` is not LTLf-definable,
for the same reason and by the same read-off that `Even` is not LTL.

The read-off has the same consumer, one level down. **LTLf** — LTL interpreted on
finite traces, the specification idiom of AI planning, business-process modeling
and runtime verification [DV13] — equals first-order logic on finite words
[DV13, Thm 3], hence star-free [MP71], hence aperiodicity of the syntactic
monoid [Sch65]:
"is this regular trace property actually LTLf?" is the finite twin of §7.1's PSL
question, decided on the same object by the same group search. Finally, for the
**learning** community [Kla94, AF16, ABF18, AF21], whose central obstruction is
that the right congruence alone does not characterize an ω-language [AF21]: the
rotation lemma shows the two-sided syntactic congruence is determined by
right-extension observations at prefix-indexed slots — precisely the row/column
discipline of an `L*`-style observation table — which suggests that learning the
syntactic ω-semigroup *directly*, rather than a presentation-dependent family of
DFAs, is feasible; we leave this as a prospect.

---

## 7. Leveraging the syntactic ω-semigroup

The syntactic ω-semigroup was built to decide one question, and §7.1
settles it: LTL-definability is a single group-theoretic read-off.
But Theorem 5.1 delivers more than one verdict. The invariant is complete,
canonical, and byte-comparable, so a whole family of further decisions —
identity, the classical classifications, operations on languages — become
read-offs of, and surgeries on, the one table. §7.2 opens that program.

### 7.1 Deciding LTL

The cut is a single group-theoretic read-off: `S(L)₊` is **aperiodic**
(group-free) iff `L` is **star-free** `= FO[<] =` **LTL** `=` counter-free
[Sch65, Kam68, Tho79, DG08]. This is the paper's spine (§4) promoted to a decision:
power-iterate each class (the class of `v^{k+1}` is a function of those of `v^k` and `v`,
since `~` is a two-sided congruence by Lemma 4.4); in a finite monoid every power
sequence settles on a cycle, and a cycle of period `≥ 2` is a group — aperiodicity is
every period equal to `1`. The verdict is exact in both directions — because `S(L)₊` *is*
the presentation-independent invariant (Theorem 4.5), a group in it is never an artifact
(Proposition 3.4).

*A practical instance.* PSL/SERE properly extends LTL and is the industrial specification
language (IEEE 1850); a written property in it may or may not fall in the far
better-supported LTL fragment, and "is this PSL property actually LTL?" is asked with no
tool to answer it. It is exactly the aperiodicity test above, and the two non-LTL running
examples — both plain SEREs — are its minimal witnesses.

Below star-free, the first-order fragments (`FO²`, the alternation levels
`Σ₂/Δ₂`, the until-nesting hierarchy) refine the cut and are decidable on the
algebra too — their characterizations pair a variety condition on `S(L)₊`
with a topological side condition [DK09, Wilke99] — data the object carries;
we claim the data, not the procedures.

### 7.2 A calculus over the syntactic ω-semigroup

Theorem 5.1 has operational content beyond canonicity: the operations one
is used to performing on automata exist natively on the invariant, and where
an automaton operation acts on a presentation, the same operation here acts
on the language itself — its effect defined, and its result canonical, at
language level. On the reified invariant,
language equivalence is byte equality of canonical serializations; complement
is one flip, `P ↦ P^c` within the linked pairs (§5); emptiness is `P = ∅`,
universality is `P =` all linked pairs; membership of a lasso `u·v^ω` is one
fold through `λ` and `M` and one `P` lookup; and every nonempty pair set
carries its own certificate — shortlex keys turn any accepting pair `(s, e)`
into the canonical witness lasso. Each entry replaces a construction on
automata — complementation costs `2^{Θ(n log n)}` on nondeterministic Büchi
automata [Saf88], equivalence sits in PSPACE — with a scan of the one
canonical table.

The classical taxonomy of ω-regular
languages is, theorem by theorem, a taxonomy of structural properties of the
same object. Landweber's ladder — safety, guarantee, obligation, recurrence,
persistence, in verification's vocabulary [MP92] — transports rung by rung: a
realizable cycle of a Muller automaton *is* a linked pair, and each rung is a
closure condition on the accepting set `P` [Lan69, SW08, PW13]. The
acceptance index — the minimal deterministic condition `L` needs: Büchi,
co-Büchi, parity `[i, j]`, a genuine Rabin pair — is the maximal length of an
*alternating chain* of ultimately periodic behaviours, introduced on automata
by Wagner [Wag79] and computable in the *syntactic* ω-semigroup by a theorem
of Carton and Perrin [CP97, Cor. 1].

Subsuming every rung and the index, the
exact **Wagner degree** — the complete classification of ω-regular languages
up to continuous (Wadge) reducibility — is fixed by the chain and superchain
structure of `S(L)` [CP97, CP99, SW08]. We claim no economy for a single
verdict — a dedicated algorithm for one class will usually beat materializing
the whole algebra — but a unifying one: build the SωS once, and each decision
is a table search — polynomial for the Wagner coordinates [CP97, CP99] and
every row they project — several of them decisions for which no practical tool
exists today.

On the running examples the axes visibly decouple: `Even` is an
*open* (guarantee) property — a good prefix decides it — yet non-LTL, a
genuine mod-2 group inside an open set; `GF(aa)` is recurrence, needing only
Büchi, and LTL; `EvenBlocks` needs its genuine Rabin pair. The topological
ladder and the aperiodic cut of §7.1 are orthogonal coordinates of one
object.

The table gathers the program in one view: each row is a classical decision,
the reference that defines it, the structural test it becomes on the SωS, and
whether a practical tool answers it today.

| Band | Classification | Defined by | Test on the SωS | Practical tool |
|---|---|---|---|---|
| identity | equality · complement · emptiness | Thm 5.1 | `𝓘` equality · `P ↦ P^c` · `P = ∅` | yes |
| ladder | safety · guarantee · obligation | [MP92, Lan69] | closure conditions on the accepting set `P` | partial (Spot) |
| ladder | recurrence (DBA) · persistence (DCA) | [Lan69] | `Gδ`/`Fσ` linked-pair conditions | partial (Spot) |
| aperiodic | star-free `=` FO `=` **LTL** | [Sch65, DG08] | `S(L)₊` group-free | none |
| aperiodic | FO² · Σ₂ · Δ₂ · until-rank | [DK09, Wilke99] | variety of `S(L)₊` + topological side condition | none |
| index | parity / Rabin / Mostowski `[i,j]` | [CP97, CP99] | longest alternating chain in `S(L)` | partial |
| complete | **Wagner degree** | [CP97, CP99, SW08] | chain / superchain structure of `S(L)` | none |

Every row above the last is a projection of it: the Wagner/Wadge degree is the complete
coordinate, and each classical decision reads one of its facets off the same table.

Beyond verdicts, the same table supports *operations*. Two invariants align
on a generated product table — the only product-priced move — after which
Boolean combinations of languages are pointwise operations on pair sets,
left quotients `u⁻¹L` are pair-set surgeries, and re-quotienting returns the
canonical object of the result: a normal form automata do not have (minimal
deterministic ω-automata do not exist). What stays expensive is exactly what
must: the ω-rational constructors — concatenation by a prefix set,
ω-power — and existential projection embed a powerset, and entering the
calculus costs what determinization always cost (§8). Developing this
calculus, the classification procedures behind the table, the rendering
of the algebra back into defining formulas, and the census of small
ω-regular languages that byte-canonicity makes enumerable — one item per
language, not per presentation — are each downstream of the
object: they consume it, and this paper delivers it.

---

## 8. Complexity

The construction is dominated by the size of the enriched monoid,
`|EM(D)| ≤ (|Q|·2^{|C|})^{|Q|}`, and the `|Q|` in the exponent is the source of the
explosion. That a size bound sits somewhere is a mathematical necessity, not an
engineering apology: deciding aperiodicity of a regular ω-language — the
LTL-definability question of §7.1 — is PSPACE-complete, with hardness transferred from
minimal-DFA finite-word aperiodicity [CH91] and the ω upper bound from [DG08,
Prop. 12.3], and the surrounding classifications are no cheaper. Everything around the
materialized object is benign by contrast. Each enriched element is a vector of `|Q|`
slots over the small local domain `Q × 2^C`, each generator a slot-wise map; the two
congruence relations of §4 and the partition refinement of Theorem 4.5 are polynomial
in `|EM(D)|` and `|Q|`; and each export of §7 is a further polynomial-time read-off of
the resulting table. The cost is entirely the object's size, and that size is intrinsic
to the problem, not to the construction.

On a more optimistic note, every object and operation here is BDD-friendly and the
redundancy is high, so a symbolic approach is likely to alleviate much of this inherent
complexity. The ingredients are all Boolean — the alphabet `2^AP`, the mark-sets over
`C`, the positive-Boolean `Acc` — and every step is a set operation, not an arithmetic
one: closing `EM(D)` under composition, the two congruences, and the partition
refinement are all images, fixpoints, and quotients over sets, native to decision
diagrams.

---

## 9. Conclusion

The syntactic ω-semigroup is the canonical algebra of an ω-regular language and, for
four decades, a phantom — defined, central, and never built from an automaton. It was
never built because construction needs a recognizer that sees acceptance along runs
and a way to compute a two-sided congruence with one-sided moves; the acceptance-
enriched monoid and the rotation-collapsed Arnold decomposition are exactly those two
keys, and Theorem 4.5 assembles them into the object. Reified, it is a canonical,
complete, exportable semantic representation of the language, LTL or not — and, more than
that, the *semantic benchmark*: the classical taxonomy of ω-regular languages, from
safety versus liveness through the acceptance index up to the exact Wagner degree, is a
taxonomy of its structure, decided uniformly by one read-off, with LTL-definability a
single coordinate. Restricted to finite words the construction degenerates to the
classical syntactic monoid (§6), so the same object also serves LTLf and the
finite-word learning program. Turning the algebra back into a defining formula or a
counter-free automaton, packaging the refuting certificate, and implementing and
measuring the construction are all downstream of the object: they consume it, and this
paper delivers it. The syntactic ω-semigroup is not only definable; it is buildable, and
worth building.

---

## References

- **[ABF18]** D. Angluin, U. Boker, D. Fisman. *Families of DFAs as acceptors of
  ω-regular languages.* LMCS 14(1) 2018.
- **[AF16]** D. Angluin, D. Fisman. *Learning regular omega languages.* TCS 650
  (2016) 57–72.
- **[AF21]** D. Angluin, D. Fisman. *Regular ω-languages with an informative right
  congruence.* Inf. Comput. 278 (2021).
- **[Arn85]** A. Arnold. *A syntactic congruence for rational ω-languages.* TCS 39
  (1985) 333–335.
- **[CH91]** S. Cho, D. T. Huynh. *Finite-automaton aperiodicity is PSPACE-complete.*
  TCS 88 (1991) 99–116.
- **[CP97]** O. Carton, D. Perrin. *Chains and superchains for ω-rational sets, automata
  and semigroups.* Int. J. Algebra Comput. 7(6) (1997) 673–695.
- **[CP99]** O. Carton, D. Perrin. *The Wagner hierarchy.* Int. J. Algebra Comput. 9(5)
  (1999) 597–620.
- **[CPP08]** O. Carton, D. Perrin, J.-É. Pin. *Automata and semigroups recognizing
  infinite words.* 2008.
- **[DG08]** V. Diekert, P. Gastin. *First-order definable languages.* In *Logic and
  Automata*, 2008.
- **[DK09]** V. Diekert, M. Kufleitner. *Fragments of first-order logic over infinite
  words.* STACS 2009; Theory Comput. Syst. 48(3) (2011) 486–516.
- **[DV13]** G. De Giacomo, M. Y. Vardi. *Linear temporal logic and linear dynamic
  logic on finite traces.* IJCAI 2013.
- **[Kam68]** H. Kamp. *Tense Logic and the Theory of Linear Order.* PhD thesis, UCLA,
  1968.
- **[Kla94]** N. Klarlund. *A homomorphism concept for ω-regularity.* CSL 1994.
- **[Lan69]** L. H. Landweber. *Decision problems for ω-automata.* Math. Systems Theory
  3(4) (1969) 376–384.
- **[MP71]** R. McNaughton, S. Papert. *Counter-Free Automata.* MIT Press, 1971.
- **[MP92]** Z. Manna, A. Pnueli. *The Temporal Logic of Reactive and Concurrent
  Systems: Specification.* Springer, 1992.
- **[MS97]** O. Maler, L. Staiger. *On syntactic congruences for ω-languages.* TCS 183
  (1997) 93–112 (rev. 2008).
- **[Per84]** D. Perrin. *Recent results on automata and infinite words.* MFCS 1984.
- **[PP04]** D. Perrin, J.-É. Pin. *Infinite Words: Automata, Semigroups, Logic and
  Games.* Elsevier, 2004.
- **[PW13]** S. Preugschat, T. Wilke. *Effective characterizations of simple fragments of
  temporal logic using Carton–Michel automata.* LMCS 9(2:08) (2013).
- **[Saf88]** S. Safra. *On the complexity of ω-automata.* FOCS 1988, 319–327.
- **[Sch65]** M. P. Schützenberger. *On finite monoids having only trivial subgroups.*
  Information and Control 8 (1965) 190–194.
- **[SW08]** V. Selivanov, K. W. Wagner. *Complexity of topological properties of regular
  ω-languages.* Fund. Inform. 83(1–2) (2008).
- **[Tho79]** W. Thomas. *Star-free regular sets of ω-sequences.* Information and
  Control 42 (1979) 148–156.
- **[Wag79]** K. Wagner. *On ω-regular sets.* Information and Control 43 (1979) 123–177.
- **[Wilke99]** T. Wilke. *Classifying discrete temporal properties.* STACS 1999,
  LNCS 1563, 32–46.
