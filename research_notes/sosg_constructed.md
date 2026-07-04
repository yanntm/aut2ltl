# The SOSG, Constructed

**Claude (Anthropic)** and **Yann Thierry-Mieg**

*Working draft — 2026-07-04*

## Abstract

The syntactic ω-semigroup (SOSG) of a regular ω-language `L` is its canonical
algebra: the ω-analogue of the syntactic monoid that underpins the entire
finite-word theory of regular languages. Introduced by Arnold in 1985 as the
coarsest congruence saturating `L`, it is presentation-independent and complete —
it determines membership, equivalence, and every definability property of `L`,
including whether `L` is expressible in linear temporal logic. Yet, unlike the
finite-word syntactic monoid, which has been computed routinely for three decades,
the SOSG has never been constructed from an automaton. The obstruction is not
merely its size: computing it requires two ingredients the literature holds only
separately — a recognizer that remembers *acceptance along runs* rather than only
transitions, and a way to compute the inherently *two-sided* syntactic congruence
without ever quantifying over two-sided contexts. We supply both. The first is the
acceptance-enriched monoid `EM(D)`, read off any deterministic form `D` of `L`; we
prove it recognizes `L` and that the SOSG is a quotient of it. The second is a
collapse of Arnold's two context shapes into two independently checkable
relations — pointwise residual equality and right-invariant acceptance-profile
equality — together with a rotation lemma proving that the two-sided congruence is
computable by right multiplications alone. This yields the SOSG explicitly, for the
first time, as a canonical and *exportable* semantic representation of an ω-regular
language, LTL-definable or not. From that one object several familiar artifacts
fall out as exports: the exact LTL-definability decision; a portable,
representation-independent certificate refuting definability when it fails; a
defining LTL formula when it holds (the language reified *as a formula*); a
canonical counter-free automaton (the language reified *as an automaton*); and a
complete invariant that turns language equality into table equality. The
construction is uniform over finite and infinite words; its finite-word
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
saturates `L` — whose quotient is the **syntactic ω-semigroup**, which we abbreviate
**SOSG**. It is presentation-independent and it is *complete*: it fixes membership,
equivalence, and definability, and — by the classical chain
`LTL = FO[<] = star-free = aperiodic SOSG` [Kam68, Tho79, Per84, DG08] — reading
aperiodicity off it decides LTL-definability exactly, in both directions.

And yet the SOSG is, in practice, a phantom. It is defined everywhere and built
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

Our contribution is to supply both missing pieces and thereby construct the SOSG.
For (1) we define the **acceptance-enriched monoid** `EM(D)` and prove it recognizes
`L`, with the SOSG a quotient of it (§3). For (2) we **collapse** Arnold's two
shapes: the linear shape becomes pointwise residual equality, the ω-power shape
becomes right-invariant profile equality, and a two-line **rotation lemma** proves
the two-sided congruence is computable with right multiplications alone (§4). The
main theorem is that this right-computable quotient *is* the SOSG (Theorem 4.5).

**The object first, its uses second.** Having built the SOSG, we reify it as a
canonical, complete, *exportable* representation of the language — what a minimal
deterministic ω-automaton would be if one existed, which for ω-words it does not
(§5). The definability questions then become exports (§6): the decision (is `L`
LTL?), a portable witness when the answer is no, and — the two ways to render the
algebra back into a familiar object — a defining formula (`L` *as an LTL formula*,
via Diekert–Gastin) and a counter-free automaton (`L` *as an automaton*, via the
Cayley construction). We keep the tool out of the argument entirely: every claim
below is about the object.

Three small examples run throughout, chosen to exercise both halves of the
construction and both of Arnold's context shapes. Their automata are collected in
Figure 1 and their algebraic fingerprints in Table 1; every notion introduced below
is stated once and then immediately read off these three.

- **`GF(aa) := GF(a ∧ Xa)`** — "infinitely many `aa`-factors." It *is* LTL, but a
  natural presentation encodes the letter `a` as a transposition, so its transition
  monoid carries a spurious group. The SOSG *destroys* that group.
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
LTL — simpler, and far better tool-supported — is itself a use of the object (§6);
these two are its minimal witnesses. Both are built directly from their SERE text by a
standard PSL front end, so Figure 1 needs no hand construction.

> **Figure 1** (rendered in the companion [figures](sosg_figs/figures.md)). The
> deterministic Emerson–Lei automata `D` of the three running examples: **(a)**
> `GF(aa)` — 2 states, `a` a transposition, `Inf(0)` closing each `aa` (a `Z₂` in the
> transition monoid); **(b)** `Even` — 4 states, `Inf(0)`, a parity pair with an
> accepting and a rejecting sink; **(c)** `EvenBlocks` — 2 states, `Fin(0) ∧ Inf(1)`,
> prefix-independent.

> **Table 1** (in the companion [figures](sosg_figs/figures.md)). Algebraic
> fingerprints — PSL/SERE source, `|Q|`, `|EM(D)¹|`, `|S(L)₊¹|`, group in the
> transition monoid?, group in `S(L)₊`?, LTL?, and either the certificate shape
> (`F₁`/`F₂`) or the synthesized formula. The `GF(aa)` row is the story in miniature:
> `|EM¹| = 10` with a `Z₂`, `|S(L)₊¹| = 6` with *no* group, LTL, formula `GF(a ∧ Xa)`;
> the `Even` (`7 → 5`) and `EvenBlocks` (`16 → 7`) rows carry a real group into
> `S(L)₊` and a `{·}[*2]`-rooted witness out.

---

## 2. The objects, in plain terms

The reader we write for practices ω-automata — Büchi acceptance, ω-regular languages —
but need not keep Perrin–Pin open. This section fixes the few algebraic objects the
construction stands on, each with the intuition we ourselves had to reconstruct from
the book, shown on the three running examples. There is one genuinely new idea; the
rest is boolean bookkeeping.

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
`Σ^∞ = Σ* ∪ Σ^ω`, and take `L ⊆ Σ^ω` regular. The input is any **deterministic,
complete** automaton `D = (Q, ι, δ, C, Acc)` with `L(D) = L`: `δ : Q × Σ → Q`, a
finite set `C` of acceptance **marks** carried on transitions, and an **Emerson–Lei**
acceptance condition `Acc` — a positive Boolean combination of `Inf(c)` and `Fin(c)`
over `c ∈ C`, the most general ω-regular acceptance, subsuming Büchi, co-Büchi,
Rabin, and Muller. For a state `q`, its **residual** is the ω-language
`L(q) = { α ∈ Σ^ω : the run of D from q on α satisfies Acc }`; determinism makes
`L(ι·u) = u⁻¹L` for every finite prefix `u`.

*Example (Figure 1).* The three running automata instantiate `Acc` across the
Emerson–Lei range. `GF(aa)` reads `Inf(c)` for a single mark `c` placed on the
`a`-transition taken from the "just saw an `a`" state — the run passes `c`
infinitely often iff `aa` recurs. `Even` is a guarantee: `Inf(acc)` for the mark on
the accepting sink's self-loops — the run reaches the sink (after an even `a`-prefix
closed by `!a`) or never does. `EvenBlocks` needs the full `Fin(0) ∧ Inf(1)` shape:
`Inf(1)` forces infinitely many `!a`'s (block completions), `Fin(0)` forbids an
odd-length completed block infinitely often. The residuals separate `Even`'s four
states pairwise (`q₀ ≠ q₁` because one `!a` accepts, the other rejects) but collapse
both states of `EvenBlocks` to a single residual — the prefix-independence that
Proposition 4.6 will read algebraically.

With the objects named, the algebra is built by settling one question: *when are two
finite words the same ingredient* — interchangeable inside every lasso, so that
swapping one for the other never changes membership? Agreement on the **stem** side is
just agreement of residuals (the futures `L(q)` above), the finitary half which §4 will
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
and they are exactly the stem/loop split of the on-ramp. Two finite words `u, v ∈ Σ*` are **syntactically congruent** for
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
completion `S(L)`, is the **SOSG**. The two shapes are genuinely independent — §4.4
and Proposition 4.6 exhibit a language separated by one shape and blind to the other —
so a construction may not drop either.

*Example.* `Even` is separated by the *linear* shape and only it: taking `x = ε`,
`y = ε`, tail `t = !a·a` (any lasso opening with `!a`), the words `a` and `aa` give
`a·!a·(a)^ω ∉ Even` (odd prefix) but `aa·!a·(a)^ω ∈ Even` (even prefix) — so `a ≉_L aa`
witnessed linearly. `EvenBlocks` is the opposite: *no* linear context separates any
two words (prefix-independence — a finite mutation is swallowed), yet the *ω-power*
shape does, with `y` closing a block: `(a·!a)^ω` completes odd blocks forever and is
rejected, `(aa·!a)^ω` completes even blocks and is accepted, so `a ≉_L aa` witnessed
only in the loop. The two examples are exactly the two shapes made concrete.

*On the threads.* For `Even`, the letter `a` toggles the a-count parity before the
first `!a`, and no finite context can undo that parity: `a` has order 2 in `S(Even)₊`
— a real group, so `Even` is not LTL. For `GF(aa)`, a run-parity presentation makes
`a` a transposition of two states, but at infinity the parity is invisible to
membership (an `aa` factor either recurs or not, a threshold not a count); the group
is an artifact of the presentation and, as §4 shows, is absent from `S(GF(aa))₊`,
which is aperiodic.

The task is to build `S(L)` from `D`. The two keys follow.

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
(Proposition 3.4). Closing `⟦a⟧`, `⟦¬a⟧` under composition yields the ten elements of
`EM(GF(aa))` — the empty word, the four `aa`-free "(first letter, last letter)"
behaviors, and the absorbing "contains `aa`" behavior, each in one or two mark states —
tabulated in Table 2 alongside their fold to the six SOSG classes of §4.

> **Table 2** (in the companion [figures](sosg_figs/figures.md)). The `10` elements of
> `EM(GF(aa))` as `(st, mk)` vectors over `Q = {0,1}`, and their fold onto the `6`
> classes of `S(GF(aa))₊`: four distinct elements collapse into the absorbing
> "contains `aa`" class and `a·!a·a` rejoins `[a]`. The mark part alone separates
> `⟦a⟧` from `⟦aa⟧` — the enrichment doing its one job.

**Lemma 3.2 (skeleton).** If two ω-words `α, β` factor into blocks with the same
sequence of enriched elements read from `ι` — i.e. `α = w₁w₂⋯`, `β = w'₁w'₂⋯` with
`⟦w₁⋯w_k⟧ = ⟦w'₁⋯w'_k⟧` for all `k` — then `α ∈ L ⟺ β ∈ L`.

*Proof.* Determinism gives a unique run for each. At every block boundary `k` the two
runs are at the same state `p_k = st_{⟦w₁⋯w_k⟧}(ι) = st_{⟦w'₁⋯w'_k⟧}(ι)`, and the
marks collected within block `k` are equal, `mk(p_{k-1}, w_k) = mk(p_{k-1}, w'_k)`, by
equality of the enriched elements and the composition law. Hence the two runs visit
the same states at boundaries and the same multiset of marks within each block, so
they have the same set of marks visited infinitely often — and `Acc`, an Emerson–Lei
condition, is a function of that inf-set alone. Thus the runs agree on acceptance. ∎

**Corollary 3.3 (`EM` recognizes `L`; the SOSG is a quotient).** The syntactic
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
can be pure encoding, invisible to `EM` and hence to the SOSG. (Symmetrically,
aperiodicity of the transition monoid is *sufficient* for aperiodicity of `S(L)₊`,
inherited upward through the enrichment — a one-directional convenience, not part of
the object.) The `GF(aa)` thread is exactly this situation, resolved in §4.

*On the threads.* The enriched monoid of `GF(aa)`'s 2-state run-parity presentation
has 10 elements; that of `Even` has the four sink-and-parity behaviors closed under
the two letters. Both carry a group in `EM` — the question §4 answers is which one
survives the quotient.

---

## 4. Key II — the two-sided congruence, computed with right moves

Corollary 3.3 leaves us the syntactic congruence `≈_L` transported to a relation `~`
on the finite monoid `EM(D)` — congruent elements are those interchangeable in both
context shapes. Naively `~` quantifies over left context, right context, and loop.
We now collapse it into two relations that quantify over none of these on the left,
and prove the two-sided congruence is a right-refinement.

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
`A(0, ⟦a⟧) = A(1, ⟦a⟧) = 1`, so `Aprof(⟦a⟧) = (1, 1)` — matching `aᵂ ∈ GF(aa)`. By
contrast `⟦!a⟧` resets both states to `0` with no mark, so its cycle `{0}` carries `∅`,
`Inf(0)` fails, and `Aprof(⟦!a⟧) = (0, 0)` — matching `(!a)ᵂ ∉ GF(aa)`. The profile is
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

*Example (the two halves divide the labor).* The two non-LTL threads sit at opposite
ends. In `Even`, `~lin` is already discriminating — the four states have four distinct
residuals — and the group is visible on the *state* side: `st_{⟦a⟧}` swaps `q₀ ↔ q₁`,
an order-2 action `~lin` sees directly. In `EvenBlocks`, `~lin` is *total* (one
residual, prefix-independence), so the linear half sees nothing at all; the entire
order-2 group is carried by `~ω`. Concretely, right-extend by `b = ⟦!a⟧` (close the
block): the loop `⟦a·!a⟧` is a length-1 (**odd**) block, so `(a·!a)ᵂ` violates `Fin(0)`
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

**Theorem 4.5 (the SOSG, constructed).** `EM(D)/~ = S(L)`, where `~ = ~lin ∧ ~ω` is
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

> **Table 3** (in the companion [figures](sosg_figs/figures.md)). `S(GF(aa))₊`: the
> six classes keyed `[ε], [¬a], [a], [¬a·a], [a·¬a], [a·a]`, the multiplication table,
> and the single accepting linked pair `([a·a], [a·a])`. An `aa`-free word is fixed by
> its (first letter, last letter); `[a·a]` = "contains `aa`" is two-sided absorbing;
> every power cycle has period `1`, so the transition monoid's `Z₂` is gone. The
> companion `S(Even)₊`, where `{[a], [a·a]}` is a period-2 cycle, is the group that
> survives.

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
repair. This is precisely why the negative certificate must come in two shapes (§6.2),
and why `EvenBlocks`, blind to the linear shape, can be refuted only in the ω-power
one.

*On the threads, resolved.* For `GF(aa)`, the ten enriched elements refine to **six**
`~`-classes, every class power-cycle of period 1: the run-parity words the transition
monoid kept apart are `~`-equivalent (at infinity the parity collapses to the
threshold "contains `aa`"), so `S(GF(aa))₊` is aperiodic — `GF(aa)` is LTL, its
group destroyed by the quotient. For `Even`, the letter `a`'s order-2 action survives
into `S(Even)₊`: a genuine `Z₂`, so `Even` is not LTL, and §6.2 extracts its witness.

---

## 5. The reified object

Theorem 4.5 produces `S(L)` as concrete data: a set of classes, a multiplication
table, the images of the letters, and — to recover `L` and not merely its algebra —
the set of **accepting linked pairs** `P = { (s, e) : e² = e, se = s, u·z^ω ∈ L for
⟦u⟧ ∈ s, ⟦z⟧ ∈ e }`. We key each class by its **shortlex-least representative word**
over `Σ` (a language invariant, independent of `D`), so the data is a function of `L`
alone. `P` is read directly off the automaton: for each pair of classes `(s, e)` with
`e·e = e` and `s·e = s`, take their shortlex-least representative words `w_s, w_e` and
test the ultimately-periodic word `w_s·(w_e)^ω` for acceptance on `D`; put `(s, e)` in
`P` iff it accepts. Any representatives give the same verdict — that is exactly what
`(s, e)` being a linked pair guarantees (Lemma 3.2).

**Theorem 5.1 (complete invariant).** For a fixed `Σ`, the tuple `𝓘(L) = ` (keyed
classes, multiplication table, letter map, accepting-pair set `P`) determines `L`
exactly: two regular ω-languages over `Σ` are equal iff their `𝓘` coincide.

*Proof.* `𝓘(L)` encodes the syntactic morphism `⟦·⟧` up to the canonical keying and
the accepting set. Membership of any ultimately-periodic word `u·z^ω` is decided by
computing `(⟦u⟧, ⟦z⟧)`, reducing to its linked pair, and testing `P`. Since regular
ω-languages are equal iff they agree on ultimately-periodic words, `𝓘(L)` determines
`L`. Conversely `𝓘` is a function of `L` (Theorem 4.5, canonical keying), so equal
languages have equal `𝓘`. ∎

Theorem 5.1 is what makes the SOSG worth building as an object rather than as a means
to a verdict. It is a **canonical, complete, presentation-independent semantic
representation** of `L` — what a minimal deterministic ω-automaton would be, except
that for ω-words no canonical minimal deterministic automaton exists. It is
*exportable*: a serialization of `𝓘(L)` is a portable artifact — a semantic HOA — that
any downstream consumer can read, and two such artifacts are language-equal iff
byte-equal after canonical keying. Notably `𝓘` needs no aperiodicity: it is defined
for *all* regular ω-languages, LTL or not. What one does with the object is the
subject of §6; that one *has* it is the point of this section.

*Example (canonicity you can see).* Compute `𝓘(GF(aa))` from the run-parity
presentation of Figure 1(a) — two states, a `Z₂` transition monoid — and again from
the minimal reset presentation — a different state count, a different, aperiodic
transition monoid. The two runs return the *identical* `𝓘`: six classes keyed
`[ε], [¬a], [a], [¬a·a], [a·¬a], [a·a]`, one multiplication table, the single accepting
pair `([a·a],[a·a])` (Table 3). No automaton-level object does this — the two
presentations are not isomorphic and neither is "the" minimal one — which is the
precise sense in which the algebra is canonical where the automata are not. Swapping
`P` for its complement, keeping every other table byte-for-byte, yields `𝓘` of the
complement language: the algebra is shared between `L` and `L̄`, and `P` alone
separates them — the reason `P` is part of the invariant.

> **Figure 2** (in the companion [figures](sosg_figs/figures.md); format
> [`sosg_format.md`](sosg_format.md)). The exportable artifact `𝓘(GF(aa))`: a
> "semantic HOA" block listing the keyed classes, the letter map, the multiplication
> table, the saturated accepting-pair set, and an optional residuals section — the
> serialization two tools compare byte-for-byte (on its core) to decide language
> equality.

A first, aperiodicity-free use: **language equality is table equality.** Where
pairwise equivalence of `N` languages costs `O(N²)` automaton products, hashing `𝓘`
buckets a corpus by true language in a hash join — the natural operation for
deduplicating large language sets.

---

## 6. Exports

From the one object, the definability questions and two reifications follow. We keep
these deliberately short: each is a corollary of §§4–5, not a construction of its own.

### 6.1 Deciding — is `L` LTL?

Read aperiodicity off `S(L)₊`: power-iterate each class (the class of `v^{k+1}` is a
function of those of `v^k` and `v`, since `~` is a two-sided congruence by
Lemma 4.4), and detect a group by a repeated class in a power sequence. Aperiodic ⟺
LTL, exactly and in both directions, because `S(L)₊` *is* the presentation-independent
invariant (Theorem 4.5) — a group in it is never an artifact. This is the whole
decision; there is no separate screen.

### 6.2 Refuting — a portable witness of non-LTL

When `S(L)₊` has a group, non-LTL-ness can be handed out as an object checkable
against `L` by membership alone, trusting nothing about the SOSG computation. Two
shapes mirror Arnold's two contexts:

```
    F₁(u,v,x,p) :  n ↦ [ u·vⁿ·x   ∈ L ]      F₂(u,v,y,p) :  n ↦ [ u·(vⁿ·y)^ω ∈ L ],
```

`p > 1`, each sample ultimately periodic, membership determined by `n mod p` and
non-constant.

**Proposition 6.1 (soundness, representation-free).** Either family with `p > 1`
proves `L` is not star-free.

*Proof.* If `L` were star-free, `S(L)₊` would be aperiodic, so `[vⁿ]` would be
eventually constant in `n`; by Lemma 3.2 membership of the samples would be eventually
constant, contradicting a genuine period `p > 1` holding for all `n`. The argument
mentions no automaton and no algebra — only `L` and the samples. ∎

**Proposition 6.2 (completeness — two shapes suffice).** If `L` is not LTL, a family
of shape `F₁` or `F₂` exists; no third shape is needed.

*Proof.* Arnold's congruence separates finite words by exactly the linear and
ω-power contexts [Arn85]. A group of period `p > 1` in `S(L)₊` has two powers `v^a,
v^{a+1}` that are non-congruent, hence separated by a context of one shape; unrolling
that separation along the power cycle yields a toggling family of the matching shape.
Both shapes are load-bearing: on a prefix-independent `L` (Proposition 4.6) every
linear sample is constant, so `F₂` is required. ∎

The witness is *extracted* by locating a group cycle in `S(L)₊` and running the DFA
distinguishing-word construction forward over the right-multiplication table to a
separating extension, whose location (a residual difference or a profile difference)
names the shape; it is then replayed by membership against `L` itself, so not even our
representation is trusted. Following the certifying-algorithms discipline [MMNS11],
this is *negative-side* certification with a **language-level** witness — where the
classical evidence for non-aperiodicity (a forbidden cycle in a minimal DFA, a
finite-order element of a group `H`-class) is representation-bound and meaningless
without trusting the construction under audit. We know of no prior packaging of
non-star-freeness as a replayable, representation-independent certificate.

*Thread.* `Even`: `v = a`, `p = 2`, `x = !a·a^ω`; the sample `aⁿ·!a·a^ω ∈ Even ⟺ n
even` — a linear `F₁`. (The prefix-independent mod-2 "every `a`-block eventually
even" is the `F₂` cameo: `~lin` blind, the witness necessarily an ω-power.)

### 6.3 Reifying `L` as a formula — the Diekert–Gastin synthesis

When `S(L)₊` is aperiodic, the algebra can be turned back into an LTL formula by
Diekert and Gastin's local-divisor induction [DG08, §8], whose input is precisely a
recognizing morphism onto a *canonical* aperiodic monoid — supplied, for the first
time, by Theorem 4.5. The induction pivots on a visible letter `c`, replaces the
monoid by its strictly smaller local divisor `mT ∩ Tm` (strict decrease is where
aperiodicity is spent), compresses words at their `c`'s, and recurses on the smaller
monoid and the smaller alphabet, translating back by two substitution lemmas; the
infinite-word letters are handled as conjugacy classes of linked pairs [PP04]. (We
note in passing that the paper's substitution clause prints a non-strict `U` where a
strict next-until is required, and that the synthesized formula, being a function of
the canonical algebra, is a normal form — same language, same formula.) The formula,
verified equivalent, is the checkable certificate the positive verdict of §6.1
otherwise lacks. *Thread:* `GF(aa)` pivots on the idle letter `¬a`, discovers that an
`aa` never straddles a `¬a`, and reassembles to `GF(a ∧ Xa)`.

### 6.4 Reifying `L` as an automaton — the Cayley construction

The parallel reification turns the algebra into an automaton. The **right-Cayley
automaton** of `S(L)₊¹` has the classes as states and `s ↦ s·⟦a⟧` as its transition
on letter `a`.

**Proposition 6.3.** The transition monoid of the right-Cayley automaton is the
right-regular representation of `S(L)₊`, hence isomorphic to `S(L)₊`; it is
therefore aperiodic — i.e. the automaton is **counter-free** — exactly when `L` is
LTL.

*Proof.* The maps `s ↦ s·t` for `t ∈ S(L)₊` generate a monoid isomorphic to `S(L)₊`
(the right-regular representation of a monoid is faithful); aperiodicity transfers.
Diekert–Gastin's counter-free theorem [DG08] equates counter-free with aperiodic
transition monoid for deterministic automata. ∎

This is a **forward, deterministic, constructible counter-free automaton** for any
LTL language — the object no minimal deterministic ω-automaton provides, and the
forward mirror of the co-deterministic prophetic form. Any construction assuming
counter-freeness — the Krohn–Rhodes cascade of [BLS22] among them — can be re-run on
it. One point remains open: the **acceptance condition** on the Cayley transitions,
an Emerson–Lei table filled from the profiles via the linked pairs, and whether it is
well-defined from the infinity set of states alone; Maler–Staiger [MS97] is the entry
point, and the residual quotient alone is provably too coarse (that of a 2-state
parity form of `GF(aa)` is a single state). We record this as the natural sequel, not
a claim.

---

## 7. Finite words

*(Placeholder — deferred to a later iteration.)* The construction is uniform over
`Σ^∞`: restricted to finite words `Σ*`, the enriched monoid degenerates to the
transition monoid with a "reached final" flag, the profiles and linked-pair calculus
vanish, `~ω` collapses, and `EM/~` is the classical **syntactic monoid**. The
finite-word specialization — its relation to the learning community's families of
right congruences and syntactic FDFAs [Kla94, AF16, ABF18, AF21], and to the
finite-word Schützenberger decision [Sch65, CH91] — is the subject of a companion
treatment.

---

## 8. Feasibility

The construction is dominated by `|EM(D)| ≤ (|Q|·2^{|C|})^{|Q|}`; the `|Q|` in the
exponent is the explosion. It is intrinsic, not an engineering apology: deciding
aperiodicity of a regular ω-language is PSPACE-complete (hardness transferred from
minimal-DFA finite-word aperiodicity [CH91]; the ω upper bound is [DG08, Prop. 12.3]),
so a size bound somewhere is a mathematical necessity. Around materialization the work
is polynomial in `|EM|` and `|Q|`. Every enriched element is a vector of `|Q|` slots
over the small local domain `Q × 2^C`, and every operation the construction uses is a
slot-wise right multiplication — the shape symbolic (decision-diagram) fixpoint
methods are built for, an opening on the `|Q|` exponent that nothing in §§3–4 forbids.
We claim no economy beyond effectiveness.

---

## 9. Conclusion

The syntactic ω-semigroup is the canonical algebra of an ω-regular language and, for
four decades, a phantom — defined, central, and never built from an automaton. It was
never built because construction needs a recognizer that sees acceptance along runs
and a way to compute a two-sided congruence with one-sided moves; the acceptance-
enriched monoid and the rotation-collapsed Arnold decomposition are exactly those two
keys, and Theorem 4.5 assembles them into the object. Reified, it is a canonical,
complete, exportable semantic representation of the language, LTL or not, from which
the decision, a portable non-LTL witness, and the two reifications — as a formula and
as a counter-free automaton — all follow as exports. The syntactic ω-semigroup is not
only definable; it is buildable, and worth building.

---

## References

- **[Arn85]** A. Arnold. *A syntactic congruence for rational ω-languages.* TCS 39
  (1985) 333–335.
- **[ABF18]** D. Angluin, U. Boker, D. Fisman. *Families of DFAs as acceptors of
  ω-regular languages.* LMCS 14(1) 2018.
- **[AF16]** D. Angluin, D. Fisman. *Learning regular omega languages.* TCS 650
  (2016) 57–72.
- **[AF21]** D. Angluin, D. Fisman. *Regular ω-languages with an informative right
  congruence.* Inf. Comput. 278 (2021).
- **[BLS22]** U. Boker, K. Lehtinen, S. Sickert. *On the Translation of Automata to
  Linear Temporal Logic.* FoSSaCS 2022.
- **[CPP08]** O. Carton, D. Perrin, J.-É. Pin. *Automata and semigroups recognizing
  infinite words.* 2008.
- **[CH91]** S. Cho, D. T. Huynh. *Finite-automaton aperiodicity is PSPACE-complete.*
  TCS 88 (1991) 99–116.
- **[DG08]** V. Diekert, P. Gastin. *First-order definable languages.* In *Logic and
  Automata*, 2008.
- **[Kam68]** H. Kamp. *Tense Logic and the Theory of Linear Order.* PhD thesis, UCLA,
  1968.
- **[Kla94]** N. Klarlund. *A homomorphism concept for ω-regularity.* CSL 1994.
- **[MS97]** O. Maler, L. Staiger. *On syntactic congruences for ω-languages.* TCS 183
  (1997) 93–112 (rev. 2008).
- **[MMNS11]** R. McConnell, K. Mehlhorn, S. Näher, P. Schweitzer. *Certifying
  algorithms.* Computer Science Review 5(2) 2011.
- **[Per84]** D. Perrin. *Recent results on automata and infinite words.* MFCS 1984.
- **[PP04]** D. Perrin, J.-É. Pin. *Infinite Words: Automata, Semigroups, Logic and
  Games.* Elsevier, 2004.
- **[Sch65]** M. P. Schützenberger. *On finite monoids having only trivial subgroups.*
  Information and Control 8 (1965) 190–194.
- **[Tho79]** W. Thomas. *Star-free regular sets of ω-sequences.* Information and
  Control 42 (1979) 148–156.
