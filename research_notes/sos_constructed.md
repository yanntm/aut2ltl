# The Syntactic ω-Semigroup, Constructed

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
the syntactic ω-semigroup has never been constructed from an automaton. The obstruction is not
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

| example | PSL/SERE source | \|Q\| | \|EM¹\| | \|S(L)₊¹\| | group in TM? | group in `S(L)₊`? | LTL? | witness shape / defining formula |
|---|---|:--:|:--:|:--:|:--:|:--:|:--:|---|
| `GF(aa)` | `G F(a & Xa)` | 2 | **10** | **6** | yes (`Z₂`) | **no** | **yes** | defining formula ≡ `GF(a ∧ Xa)` |
| `Even` | `{ {a[*2]}[*] ; !a }!` | 4 | 7 | 5 | yes | **yes (`Z₂`)** | no | `F₁` (linear): `aⁿ·!a·a^ω ∈ L ⟺ n` even |
| `EvenBlocks` | `GF!a ∧ FG(!a → X{a[*2][*];!a}!)` | 2 | **16** | 8 | yes | yes (`Z₂`) | no | `F₂` (ω-power): `(aⁿ·!a)^ω`, by parity of `n` |

**Table 1.** Algebraic fingerprints of the three examples. `|EM¹|` is the
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
product of finite pieces expresses `v^ω`. Adjoin that single operation, an **infinite
power** `s ↦ s^ω`, to a finite monoid and you have an **ω-semigroup** `S = (S₊, S_ω)`:
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
`u ∈ Σ*`.

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

*Example (Table 2).* On `GF(aa)`, the elements `⟦a⟧` and `⟦aa⟧` already differ in
`EM`, and precisely in the *mark* part: reading a second `a` closes an `aa` and
collects the `Inf`-mark that reading a single `a` (from a fresh state) does not. Their
*state* parts can nonetheless coincide, which is the whole point of the enrichment
(Proposition 3.4). Closing `⟦a⟧`, `⟦!a⟧` under composition yields the ten elements of
`EM(GF(aa))` — the empty word, the four `aa`-free "(first letter, last letter)"
behaviors, and the absorbing "contains `aa`" behavior, each in one or two mark states —
tabulated in Table 2 alongside their fold to the six SωS classes of §4.

---

| `⟦w⟧` | at state `0` | at state `1` | → `S(L)₊` class |
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

**Table 2.** The `10` elements of `EM(GF(aa))` as `(st, mk)` vectors over `Q = {0,1}`,
folded onto the `6` classes of `S(GF(aa))₊`. Reading a second `a` collects the
`Inf`-mark `0` — the only difference between `⟦a⟧` and `⟦aa⟧`, invisible to the
transition monoid. Four distinct elements collapse into the absorbing "contains `aa`"
class and `a·!a·a` rejoins `[a]`: **10 → 6**.

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
has 10 elements; that of `Even` has the four sink-and-parity behaviors closed under
the two letters. Both carry a group in `EM` — the question §4 answers is which one
survives the quotient.

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
    e ~lin f   ⟺   ∀ q ∈ Q :   L(st_e(q)) = L(st_f(q)),
    e ~ω  f    ⟺   ∀ b ∈ EM(D)¹ :   Aprof(e·b) = Aprof(f·b),        where  Aprof(c) = (q ↦ A(q, c)).
```

Here `b` ranges over `EM(D)¹`, the identity **included**: `b = 1` is the ω-power
context with empty right padding `y = ε`, whose loop is `e` itself — a case we must
keep. This is harmless: `e` is the image of a non-empty word, so the loop `e·b` is
non-empty for every `b`, and `A(·, e·b)` is a genuine loop verdict; the degenerate
`A(·, 1)` (an empty loop) would arise only from comparing the identity class with
itself, which is trivial.

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
`st_{x·e·y}(ι) = st_y(st_e(st_x(ι)))`. As `x` ranges over `EM¹`, `st_x(ι)` ranges over
exactly the reachable states; fix such a `q`. The linear condition then reads
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

`S(GF(aa))₊`, classes `0=[ε] 1=[!a] 2=[a] 3=[!a·a] 4=[a·!a] 5=[a·a]`, letter map
`λ(!a) = [!a]`, `λ(a) = [a]`:

```
 ·    [ε] [!a] [a] [!a·a] [a·!a] [a·a]
[ε]    0   1    2    3      4      5
[!a]   1   1    3    3      1      5
[a]    2   4    5    2      5      5
[!a·a] 3   1    5    3      5      5
[a·!a] 4   4    2    2      4      5
[a·a]  5   5    5    5      5      5
```

`[a·a]` = "contains `aa`" is two-sided absorbing and every power cycle has period `1`,
so the transition monoid's `Z₂` is gone; the single accepting linked pair is
`([a·a], [a·a])`. For `Even` the group survives — `S(Even)₊`, classes
`0=[ε] 1=[!a] 2=[a] 3=[a·!a] 4=[a·a]`, letter map `λ(!a) = [!a]`, `λ(a) = [a]`:

```
 ·    [ε] [!a] [a] [a·!a] [a·a]
[ε]    0   1    2    3      4
[!a]   1   1    1    1      1
[a]    2   3    4    1      2
[a·!a] 3   3    3    3      3
[a·a]  4   1    2    3      4
```

**Table 3.** Multiplication tables of the two SωSs. In `S(Even)₊`, `[a]·[a] = [a·a]`
and `[a·a]·[a] = [a]`: the pair `{[a], [a·a]}` is a **period-2 cycle**, the `Z₂` that
makes `Even` non-LTL. Read `[a·a]`'s full row and column against the headers:
it multiplies as the identity on all four word classes — `S(Even)₊` owns a
neutral element, the very situation §2's fresh-identity convention is fixed
for; `[ε]` remains a separate class regardless. Its accepting linked pairs are `([!a],[!a])`, `([!a],[a·!a])`,
`([!a],[a·a])` — once the accepting sink (class `[!a]`) is reached, every loop accepts.
In these single-atom examples `λ` is injective — each letter keys its own class — but
in general it collapses interchangeable letters: over `Σ = 2^{a,b}` a property depending
only on `a ⊕ b` maps `a!b` and `!ab` (the two `a⊕b`-true letters) to one class.

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

*Example (canonicity you can see).* Compute `𝓘(GF(aa))` from the run-parity
presentation of Figure 1(a) — two states, a `Z₂` transition monoid — and again from
the minimal reset presentation — a different state count, a different, aperiodic
transition monoid. The two runs return the *identical* `𝓘`: six classes keyed
`[ε], [!a], [a], [!a·a], [a·!a], [a·a]`, one multiplication table, the single accepting
pair `([a·a],[a·a])` (Table 3). No automaton-level object does this — the two
presentations are not isomorphic and neither is "the" minimal one — which is the
precise sense in which the algebra is canonical where the automata are not. Swapping
`P` for its complement, keeping every other table byte-for-byte, yields `𝓘` of the
complement language: the algebra is shared between `L` and `L̄`, and `P` alone
separates them — the reason `P` is part of the invariant.

---

`𝓘(GF(aa))` serialized (format v1, [`sos_format.md`](sos_format.md)):

```
SOS v1
ap: a
classes: 6
0  eps
1  !a
2  a
3  !a;a
4  a;!a
5  a;a
letters: !a->1  a->2
mult:
     0 1 2 3 4 5
  0  0 1 2 3 4 5
  1  1 1 3 3 1 5
  2  2 4 5 2 5 5
  3  3 1 5 3 5 5
  4  4 4 2 2 4 5
  5  5 5 5 5 5 5
accept:
  5 5
residuals: 1
0  eps
res-mult:
     !a a
  0  0 0
```

**Figure 2.** The exportable artifact `𝓘(GF(aa))` — a "semantic HOA" listing the keyed
classes, letter map, multiplication table, and saturated accepting-pair set (this core
is the complete language invariant), plus an optional residuals block (here a single
state, `GF(aa)` being prefix-independent) that does not enter the equality test. To test
membership of `u·z^ω`: fold `u, z` to class ids, iterate `z` to an idempotent `e`, set
`s = u·e`, and accept iff `(s, e)` is listed under `accept`. For `(a·!a)^ω`: `z = a·!a`
folds to class `4`, already idempotent, `s = 4`; `4 4` is not in `accept`, so it is
rejected — correctly, no `aa` recurs.

---

A first, aperiodicity-free use: **language equality is table equality.** Where
pairwise equivalence of `N` languages costs `O(N²)` automaton products, hashing `𝓘`
buckets a corpus by true language in a hash join — the natural operation for
deduplicating large language sets.

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
`e ~ f ⟺ ∀ reachable q : L(st_e(q)) = L(st_f(q))`, with finite-word residuals
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
guarantee rung of §7.1 made literal). Its minimal DFA is Figure 1(b) read as a
DFA — the accepting sink cut back to a final state whose successors fall to the
rejecting sink — and its syntactic monoid keeps the same `Z₂`: `[a]·[a] = [a·a]`,
`[a·a]·[a] = [a]`, the period-2 cycle of Table 3. So `W` is not LTLf-definable,
for the same reason and by the same read-off that `Even` is not LTL.

The read-off has the same consumer, one level down. **LTLf** — LTL interpreted on
finite traces, the specification idiom of AI planning, business-process modeling
and runtime verification [DV13] — equals first-order logic on finite words
[DV13, Thm 3], hence star-free [MP71], hence aperiodicity of the syntactic
monoid [Sch65]:
"is this regular trace property actually LTLf?" is the finite twin of §7.2's PSL
question, decided on the same object by the same group search. Finally, for the
**learning** community [Kla94, AF16, ABF18, AF21], whose central obstruction is
that the right congruence alone does not characterize an ω-language [AF21]: the
rotation lemma shows the two-sided syntactic congruence is determined by
right-extension observations at prefix-indexed slots — precisely the row/column
discipline of an `L*`-style observation table — which suggests that learning the
syntactic ω-semigroup *directly*, rather than a presentation-dependent family of
DFAs, is feasible; we leave this as a prospect.

---

## 7. One object, every classification

The syntactic ω-semigroup earns the phrase *semantic benchmark*. The classical taxonomy of ω-regular
languages — by acceptance type, by the safety–progress hierarchy, by topological
complexity, by temporal-logic fragment, by acceptance index, and up to the complete
Wagner classification — is, theorem by theorem, a taxonomy of *structural properties of
the syntactic ω-semigroup*. Each question was historically answered by a construction
tailored to a presentation: the cycles of a Muller automaton, the index of a parity
automaton, the variety of a monoid. The SωS answers them all by reading one canonical
object, because each classification *is*, by its own characterization theorem, a
property of that object. We claim no economy for a single verdict — a dedicated
algorithm for one class will usually beat materializing the whole algebra — but a
*unifying* one: build the SωS once and each decision below is a table lookup, several
of them decisions for which no practical tool exists today.

Many of these problems come with dedicated decision procedures already — Landweber's for
the topological ladder [Lan69], the chain-based index tests of Wagner and Carton–Perrin
[CP97, CP99], the variety-membership characterizations of the first-order fragments
[DK09, Wilke99] — and a mature tool such as Spot implements a good number of the
topological and acceptance-type ones. Our contribution is not to decide any of these
faster: materializing the algebra is exponential (§8) and we do not pretend otherwise. It
is that they are all the *same* object, decided by one read-off of it — and that a few of
them, LTL-definability itself and the exact Wagner degree, carry no off-the-shelf
implementation at all.

### 7.1 One ladder under three names

Verification's safety–progress hierarchy of Manna and Pnueli [MP92] (safety, guarantee,
obligation, recurrence/response, persistence, reactivity), Landweber's finite Borel
hierarchy [Lan69], and the deterministic-acceptance hierarchy are three vocabularies for
one ladder, and on the SωS they become literally the same conditions on linked pairs. A
**safety** property (topologically closed, `Π⁰₁`) is one an ω-word fails only by
committing to failure on a finite prefix; a **guarantee** / co-safety property (open,
`Σ⁰₁`) is its dual, witnessed by a good prefix; their Boolean combinations are the
**obligation** (equivalently *weak*, `Δ⁰₂`) properties. **Recurrence** (`GF`-shaped,
`Π⁰₂ = Gδ`) is exactly the deterministic-Büchi-recognizable class — Landweber's original
question — its **persistence** dual (`FG`, `Σ⁰₂ = Fσ`) the deterministic-co-Büchi class,
and their combinations, **reactivity**, exhaust the ladder [Lan69, SW08, PW13].

Landweber decides these on a Muller automaton by conditions on *realizable cycles*: his
`Gδ` test asks that the family of accepting cycles be closed under union with cycles
reachable at the same state [Lan69, Thm 4.2]. Transported to the SωS a realizable cycle
*is* a linked pair, and each rung is a closure condition on the accepting linked-pair set
`P` — the very data Theorem 5.1 isolates. The level in the ladder is read off `P`
directly, with no automaton reanalysis.

The three examples land on three different rungs — and, the point, two of them low.
`Even = (aa)*·!a·Σ^ω` is of the form `W·Σ^ω`, an **open** (guarantee) property: a good
prefix decides it. `GF(aa)` is **recurrence** (`Π⁰₂`, DBA-recognizable — `GF` is the
archetype); no finite prefix commits it. `EvenBlocks`, with its `Fin(0) ∧ Inf(1)`
condition, is a single Rabin pair, a **recurrence-and-persistence** conjunction higher up.
That `Even` sits at the bottom while being *non-LTL* — a genuine mod-2 group inside an
open set — makes the decoupling explicit: the topological ladder of this subsection and
the aperiodic cut of the next are orthogonal axes on one object, and a language may be
simple on one and hard on the other.

### 7.2 The aperiodic cut, and finer logical fragments

The famous cut is a single group-theoretic read-off: `S(L)₊` is **aperiodic**
(group-free) iff `L` is **star-free** `= FO[<] =` **LTL** `=` counter-free
[Sch65, Kam68, Tho79, DG08]. This is the paper's spine (§4) promoted to a decision:
power-iterate each class (the class of `v^{k+1}` is a function of those of `v^k` and `v`,
since `~` is a two-sided congruence by Lemma 4.4), report a repeated class in a power
sequence as a group, and the verdict is exact in both directions — because `S(L)₊` *is*
the presentation-independent invariant (Theorem 4.5), a group in it is never an artifact
(Proposition 3.4). There is no separate screen.

*A practical instance.* PSL/SERE properly extends LTL and is the industrial specification
language (IEEE 1850); a written property in it may or may not fall in the far
better-supported LTL fragment, and "is this PSL property actually LTL?" is asked with no
tool to answer it. It is exactly the aperiodicity test above, and the two non-LTL running
examples — both plain SEREs — are its minimal witnesses.

Below star-free, the first-order fragments refine the classification further, and are
decidable on the algebra too — though not as one-line read-offs. Over infinite
words the two-variable fragment `FO²` is characterized by membership of the finite part
in the variety **DA** *together with* a closure condition in an alphabetic topology, and
`FO² ≠ Δ₂` here, unlike over finite words [DK09]; the quantifier-alternation levels
`Σ₂, Δ₂` likewise pair a variety condition with an openness condition in that topology,
and the until-nesting hierarchy of LTL is graded by a semigroup power condition [Wilke99].
The syntactic ω-semigroup carries exactly the data these tests consume — the variety of `S(L)₊` and the
residual/topological structure of §4 — so each is a decidable property of the object; we
claim the data, not a slogan.

### 7.3 The acceptance index — what condition do you need?

A separate and thoroughly practical question: what is the *minimal* acceptance condition
that recognizes `L` deterministically — Büchi, co-Büchi, parity `[i, j]`, or a genuine
Rabin/Streett-`k`? This is the parity (Rabin, Mostowski) **index**, decidable for
deterministic ω-automata, and its algebraic form is a chain condition: the index is the
length of the longest **alternating chain** — a sequence of ultimately-periodic
behaviours whose membership in `L` flips step by step. Introduced on automata by Wagner [Wag79],
this length is, by a theorem of Carton and Perrin, computable in the *syntactic*
ω-semigroup itself [CP97, Cor. 1].
Deterministic-Büchi realizability (the recurrence rung of §7.1) is the bottom case, where
the chain collapses. This is the most operational classification of all: it names the
acceptance a tool should target, and whether a given Emerson–Lei condition carries more
than the language needs. `GF(aa)` needs only Büchi (`GF` is recurrence); `EvenBlocks`
needs a genuine Rabin pair, its `Fin(0) ∧ Inf(1)` not reducible to a Büchi condition.

### 7.4 The complete invariant — the Wagner degree

Every classification above is a coarsening of one datum. **Wagner's hierarchy** is the
complete classification of ω-regular languages up to continuous (Wadge) reducibility —
the finest topological classification there is, an ordinal-indexed refinement of the
Borel levels of §7.1. Introduced by Wagner in 1979 [Wag79], it was recast by Carton and Perrin,
who define Wagner's *chains* and *superchains* directly in the ω-semigroup and prove
their maximal lengths a function of the language alone — computable in the *syntactic*
ω-semigroup [CP97, Cor. 1, Thm 5; CP99] — with Selivanov supplying the matching
automaton-independent index [SW08]. The exact Wagner degree of `L` is therefore fixed by
the maximal chain and superchain lengths in `S(L)`: one traversal of the object's chain
structure.

This is the precise sense in which the syntactic ω-semigroup is the semantic benchmark. It is a complete
invariant not merely for language identity (Theorem 5.1) but for the entire Wagner
classification, and the classical decision problems — safety versus liveness, the
acceptance index, LTL-definability alongside as the orthogonal aperiodicity axis — are
its projections. The object was built to decide one question, LTL-definability; having
it, that question is a single coordinate, and the SωS is the coordinate system.

The table gathers that coordinate system in one view: each row is a classical decision,
the reference that defines it, the structural test it becomes on the SωS, and whether a
practical tool answers it today.

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

---

## 8. Complexity

The construction is dominated by the size of the enriched monoid,
`|EM(D)| ≤ (|Q|·2^{|C|})^{|Q|}`, and the `|Q|` in the exponent is the source of the
explosion. That a size bound sits somewhere is a mathematical necessity, not an
engineering apology: deciding aperiodicity of a regular ω-language — the
LTL-definability question of §7.2 — is PSPACE-complete, with hardness transferred from
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
