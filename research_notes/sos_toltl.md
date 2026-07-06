# The LTL Frontier from the Syntactic ω-Semigroup: Certificates, Formulas, and the Shape of the Cut

**Yann Thierry-Mieg**

With significant inputs from
**Claude (Anthropic)**

*Skeleton draft — 2026-07-06 — placeholders marked `⟨TBD: …⟩`*

## Abstract

Whether an ω-regular language is expressible in linear temporal logic is a
single read-off of its syntactic ω-semigroup — aperiodicity — and that object
is now constructible from any deterministic automaton [SωS26] and learnable
from lasso queries alone [SωSL26]. This paper is about what lies on either
side of the read-off: given the invariant `𝓘(L) = (𝒞, λ, M, P)`, *rebuild the
object the verdict calls for*. On the non-LTL side, a portable witness
certificate — the group, packaged as a checkable counting family. On the LTL
side, a defining formula — where the only prior route, the local-divisor
induction of Diekert and Gastin [DG08], is an existence proof that consumes an
anonymous recognizer, ignores every structural fact the algebra knows, and
explodes. We give an extraction driven by the algebra's own read-offs. Its
engine is a *transcription*: the deterministic walk of prefix classes on the
right Cayley graph of `S(L)₊¹` is transcribed layer by layer into a fixed set
of flat LTL bricks — anchored laws, `GF`-windows, park terms — where the layers
are the R-classes of the monoid, an anchor is a letter acting as a reset on
its layer, stuttering is locally-neutral action, and a park is nothing but a
linked pair of `P`. The preconditions for each layer are equations on the
multiplication table, decided once, on the canonical object: whether a
language transcribes flatly, and at which width, is a property of the
language, not of any machine presenting it. The walk carries exactly the *stem*
coordinate of the accepting pair, and provably not the *loop* coordinate —
no acceptance condition on recurring states or edges makes the class machine
a recognizer of `L`, the running example refuting both — so a second engine
transcribes the loop side from the recurring windows of the tail, with
`GF`/`FG` templates read off `P`: the stem and loop engines are Arnold's two
context shapes, met a third time. Nesting appears only
where the algebra provably demands it — the until-rank read-off certifies the
depth — and the formula is computed as a class-indexed DAG that scales;
flattening it is the language's own intrinsic cost, which we measure, bound,
and, in a definitional output format, avoid. An exhaustive census of small
automata shapes the frontier empirically: below ⟨TBD: census thresholds⟩ no
non-LTL language exists, and the inner frontier — which rungs of the flat-brick
ladder suffice — is mapped on the same corpus. ⟨TBD: experimental headline.⟩

---

## 1. Introduction

The classical chain `LTL = FO[<] = star-free = aperiodic` [Kam68, Tho79,
Per84, DG08] makes LTL-definability of an ω-regular language `L` a property
of one canonical object: the syntactic ω-semigroup `S(L)`, aperiodic exactly
when `L` is LTL. For four decades the chain was a classification without a
workflow — the object was never built. It now is [SωS26], and is even
learnable from membership queries on lassos [SωSL26]. The verdict is a table
lookup: power-iterate every class of the multiplication table; a cycle of
period `> 1` is a group, and the language is not LTL; no cycle, and it is.

This paper is about the day after the verdict. A verdict, alone, satisfies
nobody:

- If `L` is **not** LTL, the user holds a specification (typically PSL/SERE,
  where mod-`p` counting enters through an innocuous `{·}[*2]`) and deserves a
  *witness*: a concrete, portable, independently checkable certificate of the
  group — which words, pumped how, flip membership forever.
- If `L` **is** LTL, the user deserves the *formula*. Existence has been known
  since Kamp; the only effective route from an algebra, the local-divisor
  induction of Diekert and Gastin [DG08, §8], recalled in §3, is a proof of
  doability — blind to the structure of its input, never implemented against a
  real object, and explosive by construction.

Both rebuilds consume the same input: the exportable invariant
`𝓘(L) = (𝒞, λ, M, P)` of [SωS26] — classes keyed by shortlex representatives,
letter map, multiplication table, accepting linked pairs. The non-LTL side is
the shorter story and is closed in §4. The LTL side is the body of the paper,
and its thesis is:

**The formula should be a *transcription* of the canonical object, not the
residue of a generic induction.** The invariant contains, as read-offs, every
structural fact a formula must express — which letters the language actually
distinguishes (`λ`), where it sits on the safety–progress ladder (`P`'s
closure structure), whether prefixes matter at all (the residual count),
where runs commit irrevocably (absorbing classes), and, we show, *which parts
of the language are expressible by flat temporal bricks and which genuinely
need nesting*. An extraction that consults these read-offs emits formulas
whose shape mirrors the language's shape; one that does not — DG's — pays for
its blindness in output size, and the paper quantifies the difference.

The engine of the transcription is a *phase discipline* on the canonical
deterministic machine inside the invariant — the right Cayley graph of
`S(L)₊¹`, whose states are the classes and whose walk computes the class of
every prefix. The machine is transcribed into a fixed vocabulary of flat
LTL bricks — anchored laws, sojourns, parks, exit chains — *exactly*, with
no equivalence oracle, whenever the class occupied by the walk (its
*phase*) is recoverable from the last `k` letters of the word, modulo
stuttering. Every ingredient of the discipline is a named algebraic object
(§5): the machine's components are the R-classes of the monoid, its
anchors are reset actions, stuttering is locally neutral action, the
park/fairness dichotomy is the linked pairs of `P`, and the graded window
ladder is a ladder of definiteness equations on the multiplication table.
Each precondition is an equation on `𝓘(L)`, decided once, on the canonical
object — so whether a language transcribes flatly, and at which width, is
itself a definability property of `L` (§5.3) — and under the two
preconditions the transcription is exact by construction (§5.2): that
exactness theorem is one of the paper's two central technical claims.

The second claim emerged from working the engine on the running example
and reads like a moral (§5.5): the class walk transcribes exactly the
*linear* half of Arnold's congruence, and where the walk freezes with
acceptance still open — which for a prefix-independent language is
essentially everywhere — the remaining content is exactly the *ω-power* half,
requiring its own engine with `GF`/`FG`-shaped templates read off `P`.
**Arnold's two context shapes, which [SωS26] computed as two relations and
[SωSL26] harvested as two column sorts, resurface in extraction as two
engines.** The construction is one family: the same split, met a third time.

**Contributions.**
1. The frontier, both directions, from one object: the aperiodicity verdict
   with, on failure, a portable non-LTL witness certificate (§4), and, on
   success, a defining formula (§5–§7).
2. A presentation-independent transcription engine targeting the accepting
   pair `(s, e)`: the walk on the right Cayley graph of `S(L)₊¹` (layers =
   R-classes) transcribes the stem coordinate under an anchoring condition
   (A), and — the walk provably cannot carry the loop coordinate (Lemma
   5.2) — a window engine transcribes `e` under a determinacy condition
   (B); both conditions are equations on the object, and together they
   yield exactness by construction (§5).
3. The deliverable split, stated as a result: extraction is
   output-polynomial as a class-indexed DAG (which our implementation
   computes at scale); the flat formula is the language's intrinsic cost,
   bounded by the R-depth and until-rank read-offs, and avoidable in a
   definitional format (§6).
4. The inner frontier: within LTL, the algebra grades which layers admit
   flat transcription and which demand nesting, with the until-rank as a
   per-language lower-bound certificate on formula depth (§7).
5. ⟨TBD: census evaluation contribution line.⟩

## 2. Background: the object and its read-offs

We assume [SωS26]'s construction and reuse its notation and running
examples; this section only fixes what extraction consumes.

**The invariant.** `𝓘(L) = (𝒞, λ, M, P)`: finite class set `𝒞` with a fresh
identity `[ε]` (adjoined unconditionally — every other class carries a
non-empty shortlex key), letter map `λ : Σ → 𝒞`, multiplication table
`M : 𝒞 × 𝒞 → 𝒞`, accepting linked pairs `P ⊆ 𝒞 × 𝒞`. Membership of a lasso
`u·v^ω`: fold `u, v` through `λ` and `M`, iterate the loop class to its
idempotent `e`, and accept iff `(u-class·e, e) ∈ P`. Two languages are equal
iff their invariants are byte-equal [SωS26, Thm 5.1].

**Read-offs used below** (each a polynomial scan of the table):
- *aperiodicity* — no power orbit of period `> 1`; the frontier verdict.
- *the letter quotient* — `λ` collapses letters the language never
  distinguishes; extraction works over `λ(Σ)` and restores atomic
  propositions last.
- *the ladder position* — safety / co-safety / obligation / recurrence /
  persistence / reactivity as closure conditions on `P` [SωS26, §7.1].
- *residual count* — one residual ⟺ prefix-independent ⟺ the linear half
  is blind [SωS26, Prop 4.6].
- *absorbing classes* — two-sided zeros; runs that reach them have committed.
- *until-rank* — Wilke's grading of until-nesting as a semigroup power
  condition [Wil99]; a lower bound on the depth of any defining formula.
- *complementation* — `P ↦ P^c` for free; extraction may choose the cheaper
  of `L`, `L̄` and negate.

**Running examples.** The triptych of [SωS26]: `GF(aa)` (LTL; the extraction
specimen, worked in §5.4), `Even` and `EvenBlocks` (not LTL; the certificate
specimens, §4). Their invariants — six, five, and eight classes — are
reproduced in [SωS26, Table 3] and used here without re-derivation.

## 3. The prior route, and why it explodes

The Diekert–Gastin induction takes any morphism `h : Σ* → M` onto a finite
aperiodic monoid recognizing `L` and builds `φ` by a double induction on
`(|M|, |Σ|)`. One step: fix any letter `c` with `h(c) ≠ 1`; factor every word
at its `c`'s; abstract each `c`-free block to a *letter* of a new alphabet
`T` (one letter per block image in `M`, one per class of `c`-free tails);
recognize the abstracted language by the **local divisor**
`M' = h(c)M ∩ Mh(c)` (product `xm ∘ my = xmy`, neutral `h(c)`), which is
aperiodic and *strictly smaller* — the only use of aperiodicity in the whole
construction; recurse on `M'` for the block-sequence language and on the
smaller alphabet `Σ \ {c}` for each block language; lift back through
relativized (`µ`-confined) subformulas and a sentinel letter.

Four sources of explosion, each a blindness:
1. the recursion is two-dimensional and multiplicative — depth up to
   `|M|·|Σ|`, and each level *inflates* the alphabet to `O(|M| + |M|²)`
   letters before shrinking the monoid;
2. every occurrence of a `T`-letter unfolds to a full recursive formula for
   `h⁻¹(m)`, rebuilt at every occurrence — no sharing;
3. the separator `c` is arbitrary, though it determines the recursion tree;
4. nothing consults the input's structure: not the ladder position, not
   prefix-independence, not the ideal structure, not even that the
   *syntactic* algebra (the coarsest recognizer, with the smallest block
   alphabets and the smallest J-depth) is available.

Our implementation experience sharpens the diagnosis: with class-indexed
memoization the DG-style recursion *computes* at scale — the formula-DAG is
tractable — and what explodes is exclusively the *flat* rendering, LTL syntax
having no sharing. The bottleneck is not computation but the deliverable
format; §6 makes that split a stated result rather than an engineering
apology. The extraction of §5 attacks what remains: the flat size, by making
the formula's shape follow the language's.

## 4. The non-LTL side: the witness certificate

On this side the read-off is a power orbit of eventual period `p > 1` among
the classes of `M` — a group, and by canonicity never a presentation
artifact [SωS26, Prop 3.4, Thm 4.5]. A verdict alone, though, is exactly
what §1 said satisfies nobody: the user holds a PSL/SERE specification in
which the offending mod-`p` count may sit in one innocuous `{·}[*2]`, and
is owed a refutation checkable *without trusting us or our algebra*. This
section defines that refutation, extracts it from `𝓘(L)` by pure table
computation — no automaton, no group-theory oracle, no language-equivalence
product is ever consulted — and proves the extraction total: on the non-LTL
side it cannot fail to assemble.

### 4.1 Counting families

Non-LTL-ness is never exhibited by a single ω-word: membership of any one
word is consistent with some LTL formula. The obstruction is inherently a
*family that toggles*, and two shapes of family suffice — Arnold's two
context shapes [Arn85], met at the word level:

```
linear     F₁(u, v, x, p) :  n ↦ [ u·vⁿ·x ∈ L ]         toggles with n mod p
ω-power    F₂(u, v, y, p) :  n ↦ [ u·(vⁿ·y)^ω ∈ L ]     toggles with n mod p
```

with `p > 1`, words `u, v, y ∈ Σ*`, `x` a lasso. "Toggles with `n mod p`"
means: membership of the `n`-th sample is determined by `n mod p` for
**all** `n ≥ 0`, and is not constant in `n`. Every sample of either shape
is a lasso, so a family is checkable by lasso-membership queries alone —
against any acceptor of `L` whatsoever.

**Theorem 4.1 (soundness).** A valid family of either shape refutes
aperiodicity of `S(L)₊`; hence `L` is not LTL, by the classical chain of §1.

*Proof.* Membership of the `n`-th sample depends on `n` only through the
class `[vⁿ]`: writing `x = x_s·(x_ℓ)^ω`, the F₁ sample's verdict is the
lasso verdict of `([u]·[v]ⁿ·[x_s], [x_ℓ])`, the F₂ sample's that of
`([u], [v]ⁿ·[y])`. Were `S(L)₊` aperiodic, `[vⁿ]` would be eventually
constant in `n`, making both membership functions eventually constant —
contradicting a non-constant pattern of exact period `p > 1` holding for
all `n`, which takes both verdicts infinitely often. ∎

Soundness is deliberately independent of everything upstream: a verifier
needs only the sample verdicts and the one classical implication
(LTL ⟹ star-free ⟹ syntactic aperiodicity). Neither the algebra, nor the
construction that produced the family, nor even its declared group is
trusted.

**Proposition 4.2 (both shapes are load-bearing).** If `L` is
prefix-independent, every linear family is constant, on every choice of
`(u, v, x)`; prefix-independent non-LTL languages exist (`EvenBlocks`), so
F₂ is a requirement, not an optimization. On the invariant the blindness
is one equation: prefix-independence makes `P` *loop-determined* —
`(s, e) ∈ P ⟺ (e, e) ∈ P` — so no stem manipulation moves any verdict.

*Proof.* `σα ∈ L ⟺ α ∈ L` gives `u·vⁿ·x ∈ L ⟺ x ∈ L`: constancy. For the
equation: a linked pair `(s, e)` names the lassos `w·z^ω` with `[w] ∈ s`
and `e` the idempotent power of `[z]`; prefix-independence gives
`w·z^ω ∈ L ⟺ z^ω ∈ L`, and the pair of `z^ω` is `(e, e)`. ∎

The converse blindness — a non-LTL language whose group is visible to
linear contexts only, every ω-power pattern constant — has, to our
knowledge, neither a witness nor an impossibility proof; the census hunts
it (§8, H5).

### 4.2 Extraction: three scans of the table

Everything below is a computation on `(𝒞, λ, M, P)` alone. Write `d^π` for
the unique idempotent among the powers of a class `d` (iterate `d, d², …`
to the first repeat; the closed cycle contains exactly one idempotent), and

```
Val(c, d)  =  [ (c·d^π, d^π) ∈ P ]           c ∈ 𝒞¹,  d ∈ 𝒞 \ {[ε]}
```

for the membership verdict of any lasso `w·z^ω` with `[w] = c`, `[z] = d`
[SωS26, Thm 5.1]: `Val` is the invariant's membership oracle, and Arnold's
two context shapes evaluate through it —

```
linear   (x, y, t) ∈ 𝒞¹ × 𝒞¹ × (𝒞 \ {[ε]}) :   phase h  ↦  Val(x·h·y, t)
ω-power  (x, y)    ∈ 𝒞¹ × 𝒞¹               :   phase h  ↦  Val(x, h·y)
```

**Step 1 — the group.** Power-iterate each class (shortlex order of keys,
skipping classes already met in an earlier orbit); the first repeated class
id closes the orbit, giving index `m ≥ 1` and period `p`. The first class
`g` whose orbit has `p > 1` is the group carrier; set `v = key(g)`. The
powers `g, g², …, g^{m+p−1}` are pairwise distinct classes, none of them
`[ε]` (products of non-identity classes never reach the fresh identity), so
`m + p ≤ |𝒞|`.

**Step 2 — the separating context.** Scan linear contexts in shortlex order
of `(key(x), key(y), key(t))`, then ω-power contexts likewise; for each,
evaluate the **pattern** `π = (verdict at g^{m+i})_{i=0..p−1}`; stop at the
first non-constant `π`.

The scan cannot exhaust: the cycle classes are *distinct classes of the
syntactic congruence*, so already `g^m ≉_L g^{m+1}`, and Arnold's
definition [Arn85] hands over a separating word context of one of the two
shapes; word contexts act on verdicts only through the classes of their
components, so the corresponding class context differs at two phases — a
non-constant pattern.

**Step 3 — assembly.** Let `p′` be the minimal cyclic period of `π` (the
rotation-invariance periods of a length-`p` cycle form a subgroup of `Z_p`,
so `p′ | p`, and `p′ > 1` by non-constancy). Emit, absorbing the index so
the toggle is exact from `n = 0`:

```
linear    F₁( key(x)·vᵐ,  v,  key(y)·key(t)^ω,  p′ )
ω-power   F₂( key(x),     v,  vᵐ·key(y),        p′ )
```

Membership of the `n`-th sample is the pattern at phase `n mod p` — for
every `n ≥ 0`, since `m + n ≥ m` keeps the power on the closed cycle. The
family is valid, with declared period `p′`.

**Theorem 4.3 (totality and cost).** If `S(L)₊` is not aperiodic the
extraction emits a valid family. Every component word is a shortlex key, of
length `< |𝒞|`; the absorbed index power `vᵐ` costs a further
`m·|v| < |𝒞|²` letters, and this quadratic term is the only super-linear
one. The computation is `O(|𝒞|²)` table steps to precompute all idempotent
powers, then at most `|𝒞¹|²·|𝒞|` contexts of `p ≤ |𝒞| − 1` verdicts each,
two products and one `P`-lookup per verdict — `O(|𝒞|⁴)` table operations
worst case, with no call outside the table.

*Proof.* Totality: steps 1–2 as argued; validity and the declared period as
in step 3. Key lengths: a shortest representative of a class has length
`< |𝒞|` — in a longer word two prefixes share a class and the repeat
excises, by congruence — and the shortlex-least representative is a
shortest one. The operation counts are read off the loops. ∎

Note what the extraction does *not* need: no group-theory oracle (the group
is a cycle of class ids), no language-equivalence products (separation is a
finite scan that provably succeeds), no sampling on faith (the toggle is
exact by construction, classes being exactly periodic). Canonicity also
transfers to the output: with the scan orders fixed as above, the emitted
family is a function of `L` alone — two presentations of the language yield
the byte-identical certificate.

### 4.3 The specimens, extracted

Running the three scans on the triptych's invariants [SωS26, Table 3]:

- **`Even`.** Step 1: `[a]² = [a·a]`, `[a·a]·[a] = [a]` — carrier
  `g = [a]`, `v = a`, index `m = 1`, period `p = 2`, cycle `{[a], [a·a]}`.
  Step 2 stops at the very first linear context
  `(x, y, t) = ([ε], [ε], [!a])`: at phase `[a]` the pair is
  `([a]·[!a], [!a]) = ([a·!a], [!a]) ∉ P` — reject; at phase `[a·a]` it is
  `([a·a]·[!a], [!a]) = ([!a], [!a]) ∈ P` — accept. Pattern `(0, 1)`,
  `p′ = 2`. Emitted: `F₁(u = a, v = a, x = (!a)^ω, p′ = 2)` — samples
  `a^{n+1}·(!a)^ω`, accepted iff `n` is odd: Table 1's linear witness of
  [SωS26], in canonical dress (same shape and period, the tail and index
  shift chosen by the scan order rather than by hand).
- **`EvenBlocks`.** Step 1: carrier `g = [a]`, `v = a`, index `m = 1`,
  period `p = 2`, cycle `{[a], [a·a]}`. Step 2: every linear context comes
  back constant — not an unlucky scan but Proposition 4.2 arriving as data:
  the language is prefix-independent, `P` is loop-determined, the linear
  half has nothing to say. The ω-power scan stops at
  `(x, y) = ([ε], [!a])`: at phase `[a]` the loop class is
  `[a]·[!a] = [a·!a]`, whose idempotent power is `[!a·a·!a]`, and
  `([!a·a·!a], [!a·a·!a]) ∉ P` — reject; at phase `[a·a]` the loop class is
  `[a·a]·[!a] = [!a]`, idempotent, and `([!a], [!a]) ∈ P` — accept. Pattern
  `(0, 1)`, `p′ = 2`. Emitted: `F₂(u = ε, v = a, y = a·!a, p′ = 2)` —
  samples `(a^{n+1}·!a)^ω`, accepted iff `n` is odd: Table 1's ω-power
  witness.
- **`GF(aa)`.** Step 1 exhausts with every period 1: no group, the side is
  not taken, extraction proceeds to §5. The run-parity `Z₂` of its
  transition monoid died in the quotient [SωS26, §4]; nothing of it reaches
  this section — the scan runs on the invariant, where artifacts cannot
  live.

The two derivations also exhibit the factoring of §5's engines one section
early: `Even`'s toggle is caught by a *stem* manipulation against a fixed
tail (the linear shape — the walk side), `EvenBlocks`' only by a *loop*
manipulation (the ω-power shape — the window side). The certificate
machinery is the extraction machinery, run on the other side of the
verdict.

### 4.4 The verification contract

A family is *material*; the deliverable is the family plus its check:

- **The toggle check** — `2p′ + 1` lasso membership queries (`n = 0 … 2p′`)
  against the verifier's own acceptor of `L`, confirming the pattern is
  `p′`-periodic and non-constant on the window. Under Theorem 4.3 the
  universal claim is structural, so the finite window's role is to certify
  *transport*: that the concrete words, rendered over the verifier's
  alphabet, denote what the extraction meant.
- **The skeptic's closure** — a verifier trusting nothing but their own
  deterministic acceptor `D′` can settle the "for all `n`" claim with
  finitely many further queries: the run behavior of `vⁿ` in `D′` (states
  reached and acceptance marks collected) is eventually periodic in `n`,
  with index and period bounded by a count of run behaviors computable from
  `D′`; checking the toggle over one full stabilized cycle proves it
  forever. The certificate supports full independence, at a price the
  verifier chooses.
- **Portability** — the family references no automaton and no algebra: it
  is words and one period, `O(|𝒞|²)` symbols in total, attachable to the
  specification it refutes.

In the assembled architecture (§5.5) this extraction runs at step 0, on
`𝓘(L)` itself, before any decomposition or combinator — so there is no
boundary a negative verdict must cross, and no lifting question: the
certificate is born at the top, canonical.

## 5. The LTL side: transcribing the Cayley walk

This section is the paper's core. The plan: the canonical deterministic
machine hiding in `𝓘(L)` (§5.1); the per-layer vocabulary, the two
conditions (A) and (B), and the flat-brick label they license (§5.2), with
anchoring stated as a property of the language rather than of any
presentation (§5.3); the worked example (§5.4); and the frozen-layer
handover that completes the architecture (§5.5).

### 5.1 The Cayley walk

**Definition 5.1 (the class machine).** `Cay(L)` is the deterministic,
complete automaton with states `𝒞`, initial state `[ε]`, and transitions
`c →^a M(c, λ(a))`. Reading a finite word `u` from `[ε]` lands exactly on
its class `[u]` — the *prefix-class walk* `ψ(u)`.

`Cay(L)` is a function of `L` alone: canonical where no minimal
deterministic ω-automaton exists. Its transition structure is counter-free
exactly when `L` is LTL (aperiodicity of `M` is aperiodicity of its right
regular representation).

**Lemma 5.2 (what the walk carries — and what it cannot).** (i) The walk
computes the full syntactic class of every prefix, `ψ(u) = [u]`; in
particular, for any Ramsey factorization `α = u·w₁w₂⋯` the *stem
coordinate* `s = [u·w₁⋯w_k]` of the accepting pair is a walk value. (ii)
The *loop coordinate* `e` is **not** a function of the walk, nor of any
inf-set acceptance on `Cay(L)`: no Muller condition on recurring states and
no Emerson–Lei condition on recurring edges makes `Cay(L)` a recognizer of
`L` in general.

*Proof.* (i) is the definition of `Cay(L)`. (ii) is refuted on `GF(aa)`
itself, at both levels, off the table of [SωS26, Table 3(a)]
(classes `0..5 = [ε], [!a], [a], [!a·a], [a·!a], [a·a]`; `P = {(5,5)}`).
*States:* `aa·(!a)^ω` and `aa·a^ω` have the identical prefix-class walk
`2, 5, 5, 5, …` (class `5` is absorbing), hence the same recurring-state
set `{5}`; their accepting pairs are `(5, [!a])` and `(5, [a·a])` — one
rejected, one accepted. *Edges:* the tails `(a·!a)^ω` and `(aa·!a)^ω`,
both read from class `5`, traverse the same recurring-edge set
`{(5, a), (5, !a)}`; their loop idempotents are `[a·!a]` and `[a·a]` —
verdicts again opposite. ∎

Lemma 5.2(ii) deserves a pause, because a first draft of this section
asserted the opposite ("the walk decides membership") and the running
example itself refutes it. It is [SωS26, Prop 3.4] reborn: the frozen class
`5` *is* that proposition's one-state automaton with trivial action, where
no amount of state bookkeeping recovers acceptance. There the repair was
enrichment — marks along runs. `Cay(L)` has no marks to enrich with; the
only letter-visible substitute is the **recurring window structure** of the
tail (which finite factors recur), and recovering `e` from it is possible
exactly on a stratum (Definition 5.6). The consequence is architectural,
and it sharpens rather than weakens the two-engine picture: **the
transcription target is the accepting pair `(s, e)` — the walk engine
transcribes `s`, and a window engine must transcribe `e`.** Acceptance is
*never* the walk's business, in any layer, frozen or moving.

**Lemma 5.3 (monotone descent).** `[u·a] ≤_R [u]` for every letter `a`
(right multiplication never climbs Green's R-order). Consequently the SCCs
of `Cay(L)` are exactly the R-classes of `S(L)₊¹`, the SCC DAG is the
R-order, and every walk eventually stays inside one final R-class.

*Proof.* `[ua] ∈ [u]·M¹` gives the inequality; mutual right-reachability
*is* R-equivalence; a monotone walk in a finite order stabilizes. ∎

Lemma 5.3 hands us, for free, the recursion skeleton that DG had to
manufacture: **peel the initial R-class, delegate exits to the R-classes
below, descend the R-order** — with depth the R-depth of the *syntactic*
monoid, minimal over all recognizers of `L`. What remains is to label one
layer, and that is §5.2's brick vocabulary.

### 5.2 The layer vocabulary, the two conditions, and the bricks

Fix a layer `R` — an R-class of `S(L)₊¹`, an SCC of `Cay(L)` by Lemma 5.3 —
and work over the λ-quotient alphabet `Σ_λ = λ(Σ)` (§2); wherever a set of
quotient letters appears in a formula it denotes the disjunction of its
concrete letters, restored last. `Cay(L)` being deterministic and complete,
every letter does exactly one thing at a class `c ∈ R`, and the three sets

```
L(c) = { a ∈ Σ_λ : c·a = c }               -- stutter at c
M(c) = { a ∈ Σ_λ : c·a ∈ R, c·a ≠ c }      -- move within the layer
E(c) = { a ∈ Σ_λ : c·a ∉ R }               -- exit: strict R-descent (Lemma 5.3)
```

partition `Σ_λ`. (The one-argument `L(·)`, `M(·)`, `E(·)`, `A(·)` are letter
sets local to the engine; the two-argument `M(·,·)` remains the
multiplication table, a bare `L` the language.) For a letter `a`, its
**within-layer action** is the
partial map `c ↦ c·a` restricted to sources and images in `R`. Under
condition (A) below the within-layer letters sort further into **anchors** —
`A(c) = { a : a resets R onto c }` — and `I(c) = L(c) ∪ A(c)` collects the
letters *consistent with sitting at `c`*. The phase of the walk, the class
of the prefix read so far, is what the bricks must recover from letters
alone; a park — a walk that stutters at `c` forever — is acceptance-wise
nothing but a linked pair `(c, e)`, `e` the fold of the recurring stutter
content, looked up in `P`; and the child label `φ_d` at an exit toward class
`d` is the extraction rooted at `d`, **memoized per class**: at most `|𝒞|`
distinct children ever, the output DAG is class-indexed. One thing the
vocabulary deliberately does **not** contain is any acceptance marking of
classes or edges — Lemma 5.2(ii) — acceptance lives on pairs, never on
classes.

**Definition 5.4 (anchored layer, k = 1).** A layer `R` is *1-anchored* if
the within-layer action of every letter is either a partial identity
(stutter — shared idleness across several classes is allowed) or a partial
constant (reset — the diagonal case, a constant fixing its own target, is
allowed). Mixed actions — identity at one class, while also sending another
class of `R` somewhere in `R` — are what the condition excludes.

Note what the condition is *not*: it is not a property of any automaton the
user supplied; it is an equation schema on the multiplication table,
letterwise, `∀c, c' ∈ R` with images in `R`:
`c·a = c  ∨  c·a = c'·a`. The diagonal
allowance is deliberate and does real work: a letter that stutters at `c`
and touches no other class of `R` *names its class* — any in-layer reading
of it lands the walk at `c` — so it is an anchor in everything but edge
shape, and admitting it into the reset case leaves in `L(c)` only the
**necessary** stutter letters, those shared with another class of `R`,
which no stateless observer can attribute. Identity-or-reset is the
Krohn–Rhodes reset brick — the atomic layer of the aperiodic cascade —
surfacing as the transcribable case, which is not a coincidence ⟨TBD:
remark tying to the cascade literature [KR65, Mal10]⟩.

**Definition 5.5 (anchored layer, graded).** ⟨TBD: the k-graded version.
The window is over `k` *adjacent letters*, never over the last `k` anchors —
unbounded stutter stretches between anchors would demand `U`-nested
triggers and break the `X`-shaped law; a stretch is instead absorbed by
weakening a context position's constraint from `A(v)` ("just entered `v`")
to `I(v)` ("consistent with sitting at `v`") — the stutter abstraction,
keeping the window rigid. The clean equational form: products of `k`
within-layer actions with `I`-weakened stutter positions act as constants —
`x·s₁⋯s_k = s₁⋯s_k` (k-definiteness) localized to the layer's action
semigroup modulo its neutral part; monotonicity of the ladder in `k`,
first-fit adoption of the smallest passing width, exactness at every rung
so no gate anywhere.⟩

Anchoring is the *stem-side* precondition: it makes the walk transcribable.
Lemma 5.2(ii) forces a second, independent precondition on the *loop side*:

**Definition 5.6 (window-determined acceptance).** A layer `R` is
**(B)-determined at width `k`** if for every stem class `s ∈ R` and any two
ω-tails confined to `R` from `s` whose sets of recurring length-`k` factors
are equal, the accepting pairs `(s, e)` and `(s, e')` they induce have equal
`P`-verdicts. (Equivalently: on tails confined to `R`, the loop coordinate's
verdict is a function of the recurring `k`-window set.)

Call anchoring **condition (A)** and window-determinacy **condition (B)**.
They are the two halves of Lemma 5.2's division of labor, stated as
preconditions: (A) makes the *stem* coordinate letter-recoverable — the
walk can be transcribed — and (B) makes the *loop* coordinate's verdict
letter-recoverable — acceptance can be. The two are independent conditions
on `(𝒞, λ, M, P)`: a frozen layer passes (A) vacuously with all its content
in (B), and §7's census hunts the dual — layers anchoring at width 1 whose
verdicts defeat every affordable window. The exactness theorem needs both:
condition (A) on every layer the walk traverses, condition (B) on every
layer a run can remain in forever.

**The bricks.** For a 1-anchored layer `R`, rooted at its **entry class**
`r` — the class the walk holds when it enters `R`, always known exactly:
the parent's exit brick names it, and at the top `r = [ε]`:

```
sojourn(c)  =  L(c) W M(c)                            -- stutter at c, then move on within R
step        =  ⋀_{c ∈ R} ( A(c) → X sojourn(c) )      -- the anchored law of the layer
leave(c)    =  L(c) U ⋁_{a ∈ E(c)} ( a ∧ X φ_{c·a} )  -- stutter, then exit to the child
LEAVE(r)    =  leave(r)  ∨  ( sojourn(r) ∧ ( step U ⋁_{c ∈ R} ( A(c) ∧ X leave(c) ) ) )
STAY∞(R,r)  =  sojourn(r) ∧ G step ∧ W(R)             -- confined to R forever, accepting
Final(r)    =  STAY∞(R,r) ∨ LEAVE(r)
```

where `W(R)` is the acceptance term owned by the window engine (§5.5): under
condition (B) at width `k'`, a Boolean combination of `GF(window)` terms
over the length-`k'` windows, selected by which recurring-window sets induce
accepting pairs ⟨TBD: the exact selection — per recurring-set stratum, a
conjunction `⋀ GF(wᵢ) ∧ ⋀ FG(¬wⱼ)` normal form; sizes⟩; its width-1 fringe
is the *park*, a pure pair lookup (`(c, e) ∈ P` for the stutter fold `e`).
The design carries three deliberate asymmetries:

- **The trigger identifies, the consequence legislates.** An anchor fires
  exactly at its target — that is condition (A) — and the consequence
  constrains what follows to actual Cayley edges of the identified class.
  A law cannot be conditioned on "the walk is at `c`": the phase is what
  the formula is *transcribing*, not something it can consult, so every law
  is necessarily **eager**, firing on every letter that looks like an
  anchor. Condition (A) is exactly the price of that eagerness — it forces
  every look-alike firing to promise something true — so the eager law is
  not a tolerable over-approximation: it *is* the transcription, and no
  tighter law exists to compare it against.
- **The sojourn's arms exclude exits, on purpose.** Inside `STAY∞` the law
  is precisely what confines the walk to `R`; inside `LEAVE` the
  `U`-witness ends the law's reign strictly before the exit letter, so an
  exit is never constrained by a law it is escaping. On the complete
  canonical machine this yields a structural collapse: `sojourn(c) ≡ ⊤`
  exactly when `E(c) = ∅`, so a **terminal layer sheds its entire law**
  and `STAY∞` reduces to the window term `W(R)` alone — the reason §5.4's
  prediction comes out literally `GF(a ∧ Xa)`, with no simplifier.
- **Legality and acceptance never mix.** The `W`'s weak arm makes parking
  *legal*; whether a parked tail *accepts* is `P`'s business inside `W(R)`.
  The split keeps every `U`-vs-`W` case analysis out of the law, and is the
  walk-side face of Lemma 5.2's division of labor.

Exactness is a three-leg argument per layer ⟨TBD: the two-condition
exactness theorem, stated and proved: (A) on every traversed layer + (B) on
every final layer ⟹ the assembled label defines `L`. *Uniqueness* — free:
`Cay(L)` is deterministic and complete, every word has exactly one walk.
*Completeness* — an accepting word either stays in some final layer forever,
its walk satisfying the sojourns and the law (eager firings included, by the
license above) with its tail's recurring windows (B)-accepted, or descends,
each descent a `LEAVE` witness handing over to a named child.
*Soundness* — the formula forces the walk by induction along the word: each
active sojourn confines the next letter to genuine Cayley edges, each
trigger hands over to the entered class's law, and `W(R)` certifies the
accepting pair against `P` under (B). The argument never consults whether a
layer is accepting, rejecting, or terminal; the degeneracies (all-rejecting
final layer ⟹ `W(R) = false` ⟹ `STAY∞ = false`; terminal ⟹
`LEAVE = false`; frozen singleton ⟹ §5.5) fall out with no case
analysis.⟩

### 5.3 Anchoring is a property of the language

Conditions (A) and (B) are equations on `(𝒞, λ, M, P)`: their verdicts, the
widths at which they pass, the split of every layer's letters into
stutter, anchor, and exit — all of it is read off the canonical object, and
is therefore a function of `L` and nothing else. Whether a language admits
a flat transcription, and at which width, is thus itself a *definability
property* of the language, sitting in the inner-frontier table of §7 next
to the ladder rung and the until-rank. No machine chosen to present `L`
enters the question; a presentation's states are not even comparable to
the phases the discipline tracks (two words reaching the same state of
some acceptor share a residual but not necessarily a class, and states may
duplicate residuals — the class is the phase the *language* owns).

**Claim 5.7 (the finest phase suffices).** When (A) and (B) hold, the
transcription is exact for `L` (the two-condition exactness theorem of
§5.2), and nothing finer is ever needed: the syntactic class is the finest
phase, and `P` the complete acceptance datum.

A corollary worth stating: with the scan and tie-break orders fixed, the
entire emitted object — the layer decomposition, the passing widths, the
bricks, the class-indexed DAG — is canonical, a function of `L` alone,
like the invariant it is read from and like §4's certificate. Two
presentations of the same language cannot yield two different formulas,
because neither presentation is ever consulted.

### 5.4 Worked example: `GF(aa)` on its own algebra

`S(GF(aa))₊¹` has six classes `[ε], [!a], [a], [!a·a], [a·!a], [a·a]`
(indices `0..5`) and multiplication table [SωS26, Table 3(a)]. Reading the
Cayley edges `c →^x M(c, λ(x))` off that table:

```
0: !a → 1    a → 2          3: !a → 1    a → 5
1: !a → 1    a → 3          4: !a → 4    a → 2
2: !a → 4    a → 5          5: !a → 5    a → 5
```

The SCC decomposition — the R-order — is:

```
        {0}                       layer R₀: the start, transient
       /   \
   {1,3}   {2,4}                 two parallel layers ("last was !a" side,
       \   /                      "started with a" side)
        {5}                       layer R∞: "contains aa", absorbing
```

Per-layer letter actions, and the k = 1 test:

- **Layer `{1,3}`**: `!a` maps `1 ↦ 1, 3 ↦ 1` — image `{1}`, a partial
  constant (fixing its own target: the allowed diagonal). `a` maps `1 ↦ 3`
  (and exits from `3`) — image `{3}`, constant. **1-anchored**: `!a` anchors
  `[!a]`, `a` anchors `[!a·a]`, no residual stutter.
- **Layer `{2,4}`**: symmetric — `!a` anchors `[a·!a]`, `a` anchors `[a]`
  (from `4`; exits from `2`). **1-anchored.**
- **Layer `{5}`**: both letters neutral everywhere. All-stutter: the walk is
  frozen. (§5.5.)

Two observations, each earning its keep:

**Anchoring is layer-local, and locality is what makes it cheap.** The
letter `a` is globally ambiguous in `GF(aa)` — depending on the phase it
opens an `aa`, closes one, or extends a block, and no single letter could
name the phase of the whole machine at once. Per layer the ambiguity
vanishes: the R-decomposition separates into different layers the phases
that must coexist globally, an anchor need only disambiguate *within* its
layer, and exits are entirely unconstrained — so on `{1,3}` and `{2,4}`
each letter is a clean reset and width 1 suffices. The genuinely two-letter
content of the language is not smeared over the layers; it surfaces exactly
where it lives, as the frozen layer's width-2 window below.

**The walk, alone, is not the language — and the example proves it twice.**
The walk reaching layer `{5}` says "an `aa` has occurred", and `GF(aa)` is
not "eventually `aa`": Lemma 5.2(ii)'s two refutation instances live in this
very layer. Acceptance turns on what recurs after the walk freezes — the
single accepting pair `([a·a], [a·a])` demands a tail whose recurring loop
idempotent is `[a·a]` — and condition (B) holds here at width 2: among
tails confined to `{5}`, the recurring 2-window set determines the verdict.
The check is two lines: a tail `α` induces the pair `(5, e)` with `e` a
Ramsey idempotent of `α`, and `(5, e) ∈ P ⟺ e = [a·a]`; since `[a·a]` is
the class of the words containing `aa`, `e = [a·a]` iff sufficiently
merged Ramsey blocks contain `aa` iff the window `aa` recurs in `α`. This
yields the frozen-layer brick `GF(a ∧ Xa)`. The moving layers,
by contrast, are *rejecting* as final layers — no pair off class `5` is in
`P` — so their `STAY∞` branches are `false` by the label's own degeneracy
(an all-rejecting final layer has `W(R) = false`; no rejecting-layer test
exists anywhere), and only their `LEAVE` chains survive.
*Predicted output*, then, for the whole extraction of `GF(aa)`: `LEAVE`
chains through `{1,3}` / `{2,4}` into the memoized child at `5`, whose
label is `GF(a ∧ Xa)` — an `F(…)`-shaped reach wrapper around the child —
and since the reach wrapper is implied by the child (recurrence implies
occurrence), the simplified form is `GF(a ∧ Xa)` exactly. A
prefix-independence read-off (one residual ⟹ the reach wrapper is always
redundant — Lemma 5.9 below) would emit it directly.
The experiment suite checks this prediction end to end (E0 in the companion
spec).

### 5.5 The window engine is Arnold's second shape

Lemma 5.2(ii) assigns every acceptance decision to a second engine; the
*frozen* layer — all letters neutral, the walk stabilized — is only that
engine's purest case, where nothing else remains. This is not a corner
case; it is a theorem-shaped fact:

**Proposition 5.8 (the division of labor).** The transcription target is
the accepting pair `(s, e)`. The walk engine computes exactly the stem
coordinate `s` (Lemma 5.2(i)); every acceptance decision — the `STAY∞`
fairness of a final layer, every park verdict, every frozen tail — is a
property of the loop coordinate `e`, which no function of the walk
determines (Lemma 5.2(ii)) and which the word exposes only through its
recurring window structure, recoverable under condition (B). ⟨TBD: precise
statement and proof.⟩

*Remark (the Arnold echo).* This is not literally the `~lin`/`~ω` split of
[SωS26, §4] — `~lin` compares residuals, and the walk computes classes,
which are finer — but it is its exact operational echo: Arnold's linear
shape constrains what stems can do, his ω-power shape what loops can do,
and the extraction splits its labor the same way, stems to the walk, loops
to the windows. The construction computed the two shapes as two relations
[SωS26], the learner harvested them as two column sorts [SωSL26], and here
they are two engines. For a prefix-independent `L` (one residual, [SωS26,
Prop 4.6]) the stem side carries no membership information at all — the
walk still runs (classes move even when residuals do not: `GF(aa)` has one
residual and four layers), but every `STAY∞` and every reach wrapper it
emits is either `false` or redundant (Lemma 5.9), and the language lives
entirely in the window engine.

**Lemma 5.9 (reach absorption).** Let `L` be prefix-independent. Then
(i) `Σ*·L = L`; (ii) `T_c = L` for *every* frozen class `c` (frozen tails,
Lemma 5.10 below); (iii) consequently, if the extraction's exact label
contains a frozen-class disjunct `ψ` — necessarily defining `T_c = L` —
the whole label is equivalent to `ψ`, and every reach wrapper
(`L(F ψ) = Σ*·L(ψ)`) is redundant: the extractor may emit `ψ` directly.

*Proof.* (i) `u·α ∈ L ⟺ α ∈ L` gives `Σ*·L ⊆ L`; `u = ε` gives the other
inclusion. (ii) By Proposition 4.2, `P` is loop-determined:
`(s, e) ∈ P ⟺ (e, e) ∈ P`. So `α ∈ T_c ⟺ (c, e(α)) ∈ P ⟺
(e(α), e(α)) ∈ P ⟺ α ∈ L` — the frozen class drops out. (iii) `ψ` and the
full label both define `L`, so they are equivalent; and
`L(F ψ) = Σ*·L(ψ) = Σ*·L = L` by (i). ∎

**The no-recursion trap.** The frozen tail language at a frozen class `c` is
`T_c = {α : (c, e(α)) ∈ P}` — well-defined and prefix-independent:

**Lemma 5.10 (frozen tails).** At a frozen class `c`, `T_c` is exactly the
residual `u⁻¹L` of any representative `u` of `c`; in particular it does not
depend on the choice of Ramsey idempotent `e(α)`, and it is
prefix-independent.

*Proof.* `c` frozen means every letter is neutral at `c`, so `c·[w] = c`
for every finite `w`; hence `(c, e)` is linked for every idempotent `e`
arising from a tail. For `[u] = c`, membership of `u·α` is evaluated by
the invariant through *any* Ramsey factorization of `α`, with one verdict
[SωS26, Thm 5.1], and that verdict is `(c, e(α)) ∈ P` for each choice of
factorization — so all choices agree and `T_c = u⁻¹L`. Prefix-independence:
membership of `u·w·α` is the lookup `(c·[w], e(α)) = (c, e(α))` — the same
lookup, so `w·α ∈ T_c ⟺ α ∈ T_c`. ∎

It is tempting to "recurse" on `T_c` — build
its invariant, extract, wrap. The temptation must be resisted, and `GF(aa)`
shows why: there `T_5 = GF(aa) = L` itself. Prefix-independent languages
are fixed points of the walk-then-tail decomposition; the frozen engine is
not a recursive call, it is the *other base case*, and it needs its own
method:

The frozen-layer engine has a closed form of its own. A frozen class `c` is
a **daisy**: a one-"state" machine whose letters are *petals* (stutter) or
*stems* (exit), labeled `STAY∞ ∨ LEAVE` with `LEAVE` the exit chain of §5.2
and `STAY∞` a pure acceptance term. Two structural commitments shape that
term:

- **Acceptance sits on the loops, never on the class.** What accepting at
  `c` depends on is *which loops recur* — the idempotents `e` with
  `(c, e) ∈ P`, the algebra's per-petal marks. This is [SωS26]'s §2 point
  that ω-acceptance is a set of *pairs*, not a subset of classes, arriving
  operationally: at width one the term is a `⋀_i GF(σ_i)` over petal
  letters, and in general the petal is a *window* — a finite word whose
  fold from `c` contributes to an accepting idempotent — and `GF(σ_i)`
  generalizes to `GF(window)`. `GF(aa)` parked at `[a·a]` is a daisy whose
  accepting petal is the length-2 window `a ∧ Xa`.
- **Union absorbed by disjunction.** Each `(c, e) ∈ P` is one more way to
  accept, never a constraint on the others: overlapping accepting loop
  sets are a `∨`, and nothing ever determinizes. The walk never needed
  this power — `Cay(L)` is deterministic by construction — but acceptance
  is inherently a union over pairs, and disjunction is its exact shape.

Because the algebra's "marks" are class values of *words*, the frozen-layer
petals are inherently `k`-windows, and the single-letter case is the
degenerate rung. The frozen-layer engine, then, must express:
*accept iff the recurring finite factors of the tail, folded through `M`
from the frozen class `c`, form loops `e` with `(c, e) ∈ P`*. Its templates
are the ladder's:

- **(B) holds at width `k`** — the verdict is a function of the recurring
  `k`-window set, and the label is a Boolean combination of `GF(window)`
  terms (equivalently `FG(¬window)` for the forbidden ones), shaped by the
  ladder rung of `P` restricted to `c × idempotents`: recurrence rungs give
  positive `GF` shapes (`GF(aa)`: accept iff the window `aa` recurs —
  `GF(a ∧ Xa)`), persistence rungs the dual `FG`, reactivity the general
  Boolean combination. ⟨TBD: the general window read-off — from the
  accepting idempotents at `c`, derive the window set and the normal form;
  bound the needed width by ⟨the layer's local definiteness degree?⟩; align
  the (B)-stratum with the locally-(threshold-)testable ω-varieties
  (Beauquier–Pin / Wilke, cite-TBD) so the stratum is a known class with
  our operational reading.⟩
- **(B) fails at every affordable width** — the genuine nesting case: the
  recurring windows do not determine the verdict, because acceptance hangs
  on *order* among recurring factors, the classical separator between
  `FO[<]` and locally testable (`FO[+1]`, Thérien–Weiss; cite-TBD). Here
  and only here does a DG-style descent survive, demoted to "the engine
  inside one frozen layer" and scoped to that layer's tail algebra — which
  is not smaller in general (`T_c = L` whenever `L` is prefix-independent,
  Lemma 5.9(ii)), so the honest statement is: this stratum is where
  extraction still pays DG's price, and the census measures how rare it is
  (§8). An ω-specific descent that beats DG on this stratum is the paper's
  main open problem.

The architecture, assembled — the paper's picture:

```
extract(𝓘):
  0. aperiodicity scan — group ⟹ certificate (§4), stop
  1. quotient the alphabet by λ; choose L or L̄ by P-shape (cheaper side)
  2. ladder read-off: safety/co-safety/obligation ⟹ finite-word extraction
     of the class-defined prefix language + fixed template, stop
  2.5 combinators (§5.6): OR-split P by final layer; AND-split by subdirect
      factorization; re-canonicalize each piece (a divisor — never leaves
      LTL, Prop 5.11), recurse on pieces whose read-offs improved, combine
      with ∨ / ∧
  3. walk engine (stem side): descend the R-order of Cay(L); per layer:
       (A) at k ≤ cap  ⟹ flat law/leave bricks, exits to memoized class
                          children
       (A) fails       ⟹ ⟨TBD: layer-internal decomposition; DG local
                          division as last resort, scoped to the layer⟩
  4. window engine (loop side), on every layer a run can end in:
       (B) at k' ≤ cap ⟹ GF/FG window combination read off P (STAY∞,
                          parks) — includes every frozen layer
       (B) fails       ⟹ DG on the tail algebra: the residual stratum,
                          measured, not hidden
  5. finite-word sub-extractor (shared with step 2): the same rules one
     level down on S(L)₊'s finite part — the LTLf story of [SωS26, §6]
  output: class-indexed formula DAG; render flat or definitional (§6)
```

*Step 2, validated.* For co-safety `L` the good-prefix set
`W = {u : u·Σ^ω ⊆ L}` is a union of `≈_L`-classes — whether *every*
continuation of `u` is accepted is a property of `[u]` alone, since each
continuation's pair is `([u]·s', e')` — so `W` is recognized by the finite
part of the algebra, the finite-word extractor (step 5) applies to it, and
the wrapper is the standard strong/weak insertion of a finite-word formula
into LTL over ω-words ("some prefix satisfies `φ_W`": strong next in
positive positions, weak under negation ⟨TBD: cite the LTLf/RV lineage,
De Giacomo–Vardi and the weak-next tradition⟩). Safety is the dual through
`P ↦ P^c`; obligation, Boolean combinations of the two.

### 5.6 Combinators: decomposition on the invariant

Extraction composes. Three *decomposition combinators* complete the
engine — an OR-split by final layer, a strength stratification, and an
AND-split by subdirect factorization — each a named algebraic operation on
the invariant. The common foundation
is Theorem 5.1 of [SωS26] read as a *calculus*: on a fixed table
`(𝒞, λ, M)`, **every pair set is a language**, so union, intersection and
complement of same-table languages are Boolean operations on `P` — and any
restriction can then be *re-canonicalized* by re-running the construction's
quotient with the new pair set, yielding the piece's own, smaller algebra.

**(1) The OR-split is restriction of `P` to a final layer.** Every
word's stem class `s` lies in exactly one final layer, so

```
    L  =  ⊎_{R final layer}  L_R,      L_R recognized by (𝒞, λ, M, P|_R),
    P|_R = { (s, e) ∈ P : s ∈ R }
```

— a *disjoint* union, exact by construction, with no surgery of any kind.
Two properties come with it:

**Proposition 5.11 (decomposition never leaves LTL).** Any language
recognized by `(𝒞, λ, M)` with *any* pair set — every `L_R`, every
single-pair piece, every Boolean combination — has a syntactic ω-semigroup
dividing `M`. In particular if `L` is LTL, so is every piece, and every
re-canonicalized piece algebra is no larger than `𝓘(L)`'s.

*Proof.* The syntactic morphism of `L` recognizes the piece (membership
depends only on the pair), and the syntactic algebra of any language
divides each of its recognizers. Divisors of aperiodic monoids are
aperiodic. ∎

*The guard.* Pieces can climb the *Wagner* ladder even while staying LTL
(a single-pair piece asserts "the pair is exactly `(s, e)`", which can sit
strictly higher than `L` itself — the pair split is the finest granularity
and should be reserved for the window engine's interior). The combinator
therefore splits by final layer first, and — the operational gain —
*checks the read-offs of each re-canonicalized piece before
extracting anything*: `|𝒞'|`, ladder rung, (A)/(B) widths. Try-and-see
becomes read-and-decide.

**(2) The strength stratification is the (B)-stratification, per layer.**
Final layers sort into three strengths the engine of §5.2–5.5 already
dispatches on: *terminal* = commitment (the stem class `s` satisfies
`(s·x, f) ∈ P` for every linked continuation — step 2's co-safety
template, localized); *weak* = condition (B) at width 0 (all idempotent
verdicts at the layer agree — acceptance is "stay here", no window
needed); *strong* = the genuine window engine. This is not a decomposition
producing copies of anything; it is a per-layer read-off selecting the
template — the engine's own case analysis, given its classical names.

**(3) The AND-split is subdirect decomposition.** Intersections are where
a decomposition usually pays a determinization price; on the invariant
there is nothing to pay — the object *is* its own canonical deterministic
form — and the operation has its classical name. An
**ω-congruence** `θ` on the invariant is a monoid congruence on `(𝒞, M)`
⟨TBD: plus the pair-saturation condition making `P` θ-definable⟩; a
factorization

```
    P = P₁ ∩ P₂,   Pᵢ saturated by θᵢ,   θ₁ ∩ θ₂ = Δ
```

gives `L = L(P₁) ∩ L(P₂)` with each factor recognized by the *proper
quotient* `M/θᵢ` — a subdirect representation in Birkhoff's sense, each
factor strictly smaller, each factor's own invariant obtained by
re-canonicalization. `GFa ∧ FGb` is the type specimen: its table factors
onto a `GFa`-quotient (forget `b`) and an `FGb`-quotient (forget `a`), and
the extraction of each factor is a one-layer window brick. ⟨TBD: (i) the
pair-saturation definition and the proof that the factorization is exactly
the AND-split; (ii) existence — Birkhoff guarantees subdirect
representations of the monoid, the `P`-compatible version needs its own
statement, with the honest fallback "no proper factorization exists" (the
subdirectly irreducible case); (iii) algorithmics — the congruence lattice
of a census-sized monoid is enumerable, and the search wants maximal
proper congruences first; (iv) the worked `GFa ∧ FGb` factorization,
tables shown.⟩

The combinators compose (OR of ANDs, complement flips via `P^c` choosing
the cheaper side), they all commute with re-canonicalization, and
Proposition 5.11 makes the whole combinator layer safe: no move ever
leaves LTL or grows the algebra. They slot into the architecture as step
2.5, between the ladder templates and the walk engine.

## 6. The deliverable: DAG, flat, and definitional forms

Extraction as computed is a **class-indexed DAG**: one node per
(class, engine-context) pair, children memoized — the implementation
computes it at scale ⟨TBD: cite the implementation's numbers once §8
exists⟩. Three renderings:

1. **The DAG itself** — the working format, and polynomial on the
   anchored+ladder fragment: the walk side has one label per layer and one
   memoized child per class, each class contributing its letter split and
   exit disjuncts — `O(|𝒞|·|Σ_λ|)` in total — and the window side one term
   per final layer, `O(k′·|Σ_λ|^{k′})` apiece (the exact constant awaits
   the `W(R)` normal form, §5.2). Not an LTL formula, but every downstream
   *computation* (model checking the formula against the automaton,
   equivalence tests) can consume it directly.
2. **Flat LTL** — the standard, and the intrinsically large one: no sharing
   in the syntax, so DAG unfolding multiplies along the R-order antichains.
   Two honest statements about depth. The upper bound is structural: every
   brick of §5.2 has fixed modal depth — a constant depending only on the
   widths, four at `k = 1`, `k′ + 2` for a window term — and a child label
   occurs only under `leave(·)`, strictly lower in the R-order; so when all
   layers anchor, flat nesting depth is at most `c(k)·d + c′(k′)` for
   R-depth `d`: linear in the R-depth, the constant owned by the widths.
   The lower bound is the language's: the until-rank read-off
   *lower-bounds* the depth any extraction whatsoever can achieve — so on
   census specimens we certify "the flat explosion is the language's, not
   ours". ⟨TBD: the until-rank lower bound, blocked on the §2 read-off
   (C6); the size ledger DG vs. ours on the triptych + census.⟩
3. **LTL with definitions** — one fresh proposition `p_n` per DAG node `n`,
   a conjunction of `G(p_n ↔ brick_n(…))` definitions plus a root: linear
   in the DAG, printable, and defining `L` exactly, in the following
   sense. Let `Def = ⋀_n G(p_n ↔ brick_n)` over the extended alphabet
   `2^{AP ∪ {p_n}}`, each `brick_n` reading only `AP` and propositions of
   DAG-lower nodes. The DAG being acyclic, every ω-word `α` over `2^{AP}`
   has *exactly one* extension `α̂` satisfying `Def` — by induction along
   the DAG order, each `p_n`'s truth at each position is a function of `α`
   and the lower traces — and `α ∈ L ⟺ α̂ ⊨ p_root`. So `L` is the
   projection of `L(Def ∧ p_root)` onto `AP`, and the second-order
   quantifier hidden in that projection is *deterministic*: a definitional
   extension, never a guess. That is the remark the format deserves:
   *inside* the transcription a fresh disambiguating proposition is
   refused — there it would be a genuine guess, its projection leaves LTL
   for QPTL, and that wall *is* the (A)-fail stratum — while as an output
   wrapper the quantifier adds no expressive power and the semantics stays
   exact.

## 7. The inner frontier

Aperiodicity is the outer cut. Inside it, the extraction's case analysis
induces a second, finer map, and every coordinate is a read-off:

| stratum | algebraic condition | formula shape | where decided |
|---|---|---|---|
| ladder-low (safety/co-safety/obligation) | closure of `P` | fixed template over a finite-word formula | step 2 |
| stem-transcribable, k = 1 | (A): identity-or-reset per layer | flat bricks, depth O(R-depth) | step 3 |
| stem-transcribable, k ≤ K | (A): local k-definiteness mod stutter | graded windows, same depth | step 3 |
| loop-transcribable | (B) at width k′ ⟨TBD: align with local ω-testability⟩ | `GF`/`FG` window combinations | step 4 |
| residual | (A) or (B) fails at every affordable width | genuine nesting; until-rank certifies | steps 3–4 fallback |

**Table 2.** The inner frontier: which fragment of LTL a language actually
needs, decided on `𝓘(L)` before any formula is built. ⟨TBD: align the
strata with the known sub-LTL hierarchies — definite / locally testable /
TL[F] of Cohen–Perrin–Pin / until hierarchy [Wil99, PW13] — so each row is
a known variety with our operational reading; the census then *maps* the
strata empirically: at 2 states / 1 AP everything is expected in the first
three rows; find the smallest specimen in each lower row.⟩

The inner frontier is also the size story of §6 made structural: flat cost
concentrates exactly in the residual stratum, and the strata above it are
the reason extraction on real specimens is small — which DG, treating every
language as residual, cannot see.

## 8. Evaluation

⟨TBD: entire section — after implementation. Fixed decisions, so the
section can be written into: corpus = the census of small automata (ground
truth 𝓘 and LTL status already computed) plus the triptych and the paper's
worked specimens; comparisons = (i) flat size and depth: this extraction
vs. the DG baseline; (ii) DAG size vs. |𝒞| — the scaling claim; (iii)
per-layer anchoring statistics — which k fires, how often frozen layers
appear, the inner-frontier map; (iv) the until-rank vs. emitted depth
ledger — optimality gaps. Verdicts checked by
the construction of [SωS26]: every emitted formula's 𝓘 must be byte-equal
to the input's — the equivalence oracle is the object itself.⟩

## 9. Related work

⟨TBD: full pass. The skeleton of the section:⟩

**Algebra to formula.** [DG08, §8] is the reference construction (§3); its
local divisor descends from Meyberg's local algebras, and the finite-word
analogues (Kufleitner et al.'s local-divisor proofs) choose separators no
less blindly. Wilke's and Diekert–Kufleitner's fragment characterizations
[Wil99, DK09] decide *membership* of sub-LTL fragments on the algebra; we
use them as extraction strata and depth certificates rather than as
verdicts. Preugschat–Wilke [PW13] decide the simple fragments via
Carton–Michel automata — the nearest decision-side relative of our frozen-
layer templates.

**Cascades.** Krohn–Rhodes for aperiodic monoids = wreath products of
resets; Maler's work on cascaded decomposition translates automaton
cascades to LTL. Our 1-anchored layer *is* the reset
brick surfacing on the canonical machine; the R-order walk is a cascade
whose levels the algebra names. ⟨TBD: precise comparison — what the Cayley
transcription emits vs. what a KR cascade of Cay(L) would; the claim that
R-depth ≤ cascade height obtainable blindly.⟩

**Local languages and definiteness.** The anchoring ladder relaxes local /
k-definite / k-testable recognizability modulo stuttering
(Chomsky–Schützenberger locals; Perles–Rabin–Shamir definiteness;
Brzozowski–Simon local testability — cites pending the biblio sweep); the
algebraic counterparts (varieties `D`, `LI`, locally testable) are
classical, and our per-layer equations are their localizations to
R-classes. ⟨TBD: nail the exact variety statements.⟩

**Companions.** This paper is the third member of a family in which the
same two-shape structure was constructed [SωS26] and learned [SωSL26]: the
construction paper supplies the object and its read-offs, the learner its
acquisition from lasso queries alone, and this paper the rebuild on either
side of the aperiodicity verdict.

## 10. Conclusion

⟨TBD — the arc, once the theory sections close: The syntactic ω-semigroup
was built to decide one question; on either side of that decision it now
rebuilds the object the answer calls for — a portable refutation, or a
defining formula that is a transcription of the algebra's own shape:
letters quotiented by λ, templates chosen by P's ladder, layers walked down
the R-order, flat bricks where the layers anchor, ω-templates where the
walk freezes — Arnold's two shapes, met for the third time, now as the two
engines of extraction — and nesting only where the until-rank proves it
unavoidable. The formula was always going to be large sometimes; the
algebra says exactly when, and exactly why.⟩

---

## References

- **[Arn85]** A. Arnold. *A syntactic congruence for rational ω-languages.*
  TCS 39 (1985) 333–335.
- **[DG08]** V. Diekert, P. Gastin. *First-order definable languages.* In
  *Logic and Automata*, 2008.
- **[DK09]** V. Diekert, M. Kufleitner. *Fragments of first-order logic
  over infinite words.* STACS 2009.
- **[Kam68]** H. Kamp. *Tense Logic and the Theory of Linear Order.* PhD
  thesis, UCLA, 1968.
- **[KR65]** K. Krohn, J. Rhodes. *Algebraic theory of machines I.* Trans.
  AMS 116 (1965).
- **[Mal10]** O. Maler. *On the Krohn–Rhodes cascaded decomposition
  theorem.* In *Time for Verification* (Pnueli memorial), LNCS 6200, 2010.
- **[MP92]** Z. Manna, A. Pnueli. *The Temporal Logic of Reactive and
  Concurrent Systems: Specification.* Springer, 1992.
- **[Per84]** D. Perrin. *Recent results on automata and infinite words.*
  MFCS 1984.
- **[PP04]** D. Perrin, J.-É. Pin. *Infinite Words: Automata, Semigroups,
  Logic and Games.* Elsevier, 2004.
- **[PW13]** S. Preugschat, T. Wilke. *Effective characterizations of
  simple fragments of temporal logic using Carton–Michel automata.* LMCS
  9(2:08), 2013.
- **[SωS26]** Y. Thierry-Mieg, with Claude (Anthropic). *Constructing the
  syntactic ω-semigroup from a deterministic Emerson–Lei automaton.*
  Working draft, 2026.
- **[SωSL26]** Y. Thierry-Mieg, with Claude (Anthropic). *Learning the
  syntactic ω-semigroup.* Working draft, 2026.
- **[Tho79]** W. Thomas. *Star-free regular sets of ω-sequences.*
  Information and Control 42 (1979).
- **[Wil99]** T. Wilke. *Classifying discrete temporal properties.* STACS
  1999.
- ⟨TBD: Cohen–Perrin–Pin (TL[F]); Brzozowski–Simon (locally testable);
  Perles–Rabin–Shamir (definite); De Giacomo–Vardi (LTLf template);
  Landweber; Schützenberger.⟩
