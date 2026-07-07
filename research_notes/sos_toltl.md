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
ladder suffice — is mapped on the same corpus. On its first census —
exhaustive at one atomic proposition and two states — nothing fails either
precondition: every layer anchors at width ≤ 2, every decided final layer
is window-determined at width ≤ 2, the fallback stratum is unwitnessed,
and all 90 non-LTL specimens were refused with a replayed counting family
each.

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
preconditions the transcription is exact by construction (§5.2, graded
to arbitrary anchoring width in §5.7): that
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
  persistence / reactivity [MP92] as closure conditions on `P`
  [SωS26, §7.1].
- *residual count* — one residual ⟺ prefix-independent ⟺ the linear half
  is blind [SωS26, Prop 4.6].
- *absorbing classes* — two-sided zeros; runs that reach them have committed.
- *until-rank* — the minimal until-nesting depth, computable from the
  syntactic semigroup: level `k` of the until hierarchy is characterized
  by a `k`-fold semidirect power of the level-1 variety
  (Thérien–Wilke's effective characterization, surveyed in [Wil99,
  Thm 8]); a lower bound on the depth of any defining formula. ⟨TBD:
  freeze the exact semigroup condition from the source paper (library
  request: Thérien–Wilke, FOCS'96) — and note the characterization is
  stated on finite words; the ω-word transfer is this paper's own
  obligation.⟩
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
having no sharing. The measurement, on the running example itself: on the
six-class algebra of `GF(aa)` the memoized recursion takes 19 recursion
nodes and a shared arena of 1 287 nodes, while the flat tree unfolds to
1 991 717 nodes — 4.4 MB of rendered formula, Spot-equivalent to
`GF(a ∧ Xa)` — and the output is canonical: two presentations of the
language (a parity and a reset automaton) bridge to the byte-identical
invariant and the character-identical formula. The bottleneck is not
computation but the deliverable
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

These class contexts are complete for separation — the totality engine of
the scan below:

**Lemma 4.3 (separation descends to classes).** For any two distinct
classes `c ≠ d` in `𝒞 \ {[ε]}` some class context of one of the two
shapes separates them: `Val(x·c·y, t) ≠ Val(x·d·y, t)` for some linear
`(x, y, t)`, or `Val(x, c·y) ≠ Val(x, d·y)` for some ω-power `(x, y)`.

*Proof.* Pick non-empty representatives `w_c, w_d` of the two classes
(the shortlex keys serve — only the fresh `[ε]` lacks one). `𝒞` is the
class set of the syntactic congruence [SωS26, Thm 4.5], and Arnold's
congruence is *defined* by two families of word contexts [Arn85; SωS26,
§2]: `u ≈_L v` iff `x̂·u·ŷ·t̂^ω ∈ L ⟺ x̂·v·ŷ·t̂^ω ∈ L` for all
`x̂, ŷ ∈ Σ*`, `t̂ ∈ Σ⁺`, and `x̂·(u·ŷ)^ω ∈ L ⟺ x̂·(v·ŷ)^ω ∈ L` for all
`x̂, ŷ ∈ Σ*`. So `w_c ≉_L w_d` hands over a separating *word* context of
one of the two shapes. Word contexts evaluate through classes: by
[SωS26, Thm 5.1], `x̂·u·ŷ·t̂^ω ∈ L ⟺ Val([x̂]·[u]·[ŷ], [t̂]) = 1` and
`x̂·(u·ŷ)^ω ∈ L ⟺ Val([x̂], [u]·[ŷ]) = 1` — and the identity being
fresh, the non-empty `t̂` has `[t̂] ≠ [ε]`. The class context
`([x̂], [ŷ], [t̂])`, resp. `([x̂], [ŷ])`, lies in the scanned range and
inherits the separation. ∎

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

The scan cannot exhaust: the cycle classes are pairwise distinct, so
`g^m ≠ g^{m+1}` (`p > 1` keeps both on the closed cycle), and Lemma 4.3
supplies a scanned context assigning them different verdicts; its
pattern differs at phases `i = 0` and `i = 1` — `m` and `m + 1` are
distinct residues mod `p`, again since `p > 1` — hence is non-constant.

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

**Theorem 4.4 (totality and cost).** If `S(L)₊` is not aperiodic the
extraction emits a valid family. Every component word is a shortlex key, of
length `< |𝒞|`; the absorbed index power `vᵐ` costs a further
`m·|v| < |𝒞|²` letters, and this quadratic term is the only super-linear
one. The computation is `O(|𝒞|²)` table steps to precompute all idempotent
powers, then at most `|𝒞¹|²·|𝒞|` contexts of `p ≤ |𝒞| − 1` verdicts each,
two products and one `P`-lookup per verdict — `O(|𝒞|⁴)` table operations
worst case, with no call outside the table.

*Proof.* Totality: step 1 as argued, step 2 by Lemma 4.3 applied to the
distinct cycle classes `g^m ≠ g^{m+1}`; validity and the declared period as
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
verdict. The duality is in fact visible *before* any certificate is
extracted, in §5's own statistics run on these invariants: every layer of
`Even` passes window-determinacy (Definition 5.7) trivially — each
within-layer cycle of its group layer folds to one rejecting class — so
the ω-power side has nothing to say on `Even`, exactly as the linear side
has nothing to say on `EvenBlocks` (Proposition 4.2). One specimen is
blind in each eye, and each blindness is a read-off.

### 4.4 The verification contract

A family is *material*; the deliverable is the family plus its check:

- **The toggle check** — `2p′ + 1` lasso membership queries (`n = 0 … 2p′`)
  against the verifier's own acceptor of `L`, confirming the pattern is
  `p′`-periodic and non-constant on the window. Under Theorem 4.4 the
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
presentation (§5.3); the worked example (§5.4); the frozen-layer
handover that completes the architecture (§5.5); the decomposition
combinators (§5.6); and the graded engine and the scoped fallback,
discharging the walk side's two remaining debts (§5.7).

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
coordinate* `s = [u·w₁⋯w_j]` of the accepting pair is a walk value. (ii)
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
exactly on a stratum (Definition 5.7). The consequence is architectural,
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
condition (A) below the within-layer letters additionally carry **anchor**
sets — `A(c) = { a : a resets R onto c }`, overlapping `L(c)` exactly on
diagonals (below) — and `I(c) = L(c) ∪ A(c)` collects the letters
*consistent with sitting at `c`*. The phase of the walk, the class
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
shape, and classifying it as a reset arms the law with its trigger. The
classification overlaps rather than repartitions: a diagonal anchor
*remains* in `L(c)` — the sojourn arms need it there, a letter of `A(c)`
read at `c` and staying in the layer being just a stutter, which
Lemma 5.8's proof leans on — and the overlap is confined to the diagonal,
since `a ∈ L(c) ∩ A(c')` makes `c` a source of a partial constant that
fixes it: `c' = c`. The stutter letters no stateless observer can
attribute are the *shared* ones, `L(c) \ A(c)`; they are what the graded
ladder's `I`-weakening tolerates (Definition 5.5). (One reporting
convention, fixed here because letter tables appear below: a letter's
*kind* is reported identity-first — a letter neutral wherever it acts is
reported as a stutter, even where the diagonal makes it the anchor of its
sole class — while `A(c)` membership stays constant-action, diagonals
included; §5.4's frozen layer reads "both letters neutral" under this
convention.) Identity-or-reset is the
Krohn–Rhodes reset brick — the atomic layer of the aperiodic cascade —
surfacing as the transcribable case, which is not a coincidence ⟨TBD:
remark tying to the cascade literature [KR65, Mal10]⟩.

**Definition 5.5 (anchored layer, graded).** For a word
`w = a₁⋯a_k ∈ Σ_λ^k`, say `w` is *readable in `R`* if some `c ∈ R` has
`c·a₁⋯a_j ∈ R` for every `j ≤ k`; the *within-layer action* `act_R(w)` is
the partial map carrying each such `c` to `c·w`. The layer `R` is
**k-anchored** if the within-layer action of every word readable in `R`
of length **at least** `k` is a partial identity or a partial constant.
The length-`k` words with constant action are the layer's **anchor
windows** — `A_k(c) = { w : act_R(w) is constant onto c }`, with
`A_1 = A` — and those with identity action are its **neutral windows**,
the graded shared stutters, attributing nothing.

The prose that motivated the grading survives in it exactly. The window
is over `k` *adjacent letters*, never over the last `k` anchors —
unbounded stutter stretches between anchors would demand `U`-nested
triggers and break the `X`-shaped law. No special clause absorbs a
stretch: a block interleaving stutters around a reset still acts as a
constant (a reset absorbs neutral padding on both sides), so the rigid
window already tolerates what the earlier intuition called `I`-weakened
positions. And the equational content is Definition 5.4's dichotomy
verbatim, letters replaced by blocks: a long-enough block either resets
the layer — the class before it is forgotten, the graded
`x·s₁⋯s_k = s₁⋯s_k` — or acts neutrally, attributing nothing, like a
shared stutter letter at width 1.

**Lemma 5.6 (the width ladder).** (i) At `k = 1` Definition 5.5 is
Definition 5.4. (ii) The ladder is monotone: `k`-anchored implies
`(k+1)`-anchored. (iii) The quantifier "length **at least** `k`" is
load-bearing: the exact-length-`k` condition is not monotone. (iv)
*Suffix pinning:* on any trajectory confined to a `k`-anchored `R` with
`≥ k` letters read, the last `k` letters `w` decide: `w ∈ A_k(c)` puts
the walk at `c`, whatever preceded; `w` neutral puts it where it was `k`
steps earlier. (v) `k`-anchoredness, and the first passing width, are
decided by one fixpoint computation on the layer's action semigroup.

*Proof.* (i) Restricting to letters gives one direction. Conversely,
partial identities compose to partial identities, and a partial constant
absorbs on both sides (`f` then a constant is a constant; a constant onto
`c` then `f` is a constant onto `c·f`), so every product of
identity-or-reset letters is an identity or a reset. (ii) Words of length
`≥ k + 1` are among the words of length `≥ k`. (iii) A scheme on
`R = {1, 2, 3}`: letters `p` (`1 ↦ 1, 3 ↦ 2`) and `q` (`1 ↦ 1, 2 ↦ 3`),
all unlisted actions exiting; strong connectivity is restored by `z`
(`1 ↦ 3`) and `y` (`3 ↦ 1`), whose every 2-word has a singleton domain.
Every readable 2-word then acts as an identity or a constant — `pq` is
the identity on `{1, 3}`, `qp` the identity on `{1, 2}` *via the
excursion* `2 → 3 → 2` — yet the 3-word `pqp` acts as `1 ↦ 1, 3 ↦ 2`,
mixed; and `pqp·(qp)^n` stays mixed at every length, so the layer is
`k`-anchored for no `k`, as the semantics demands: its phase is not a
function of any window. (iv) The last `k` letters are readable by the
trajectory itself; a constant action lands on its target regardless of
history, an identity action returns the class held `k` steps earlier.
(v) Let `𝒜_j` be the set of within-layer actions of readable words of
length exactly `j`; `𝒜_{j+1}` is a function of `𝒜_j` (extend by one
letter), so the sequence over a finite space is eventually periodic and
computable; `R` is `k`-anchored iff every `𝒜_j` with `j ≥ k` holds only
identities and constants — checked on the cycle — and the first-fit
width is the first index from which the tail stays clean. ∎

*Remark (excursions — what grading changes).* At `k = 1` a neutral
letter fixes every class it touches; at `k ≥ 2` a neutral window may
move and return, as `qp` above — and it may even hide a move at its
*last* step: reading `qp` from `2` runs the excursion `2 → 3 → 2`, so
the neutral window ends at phase `2` while the phase one step earlier
was `3` — a move at the window's final step, invisible to its identity
action (the scheme anchors at no width, but the mechanism is general:
in a `k`-anchored layer a `k`-window's `(k−1)`-prefix is
unconstrained). Anchor windows are immune — constant action fires
truthfully at any history, that is (iv) — but a width-`k` sojourn would
have to legislate what neutral windows did at their last step, which is
exactly what they do not reveal: a genuinely *mod-`k`* bookkeeping,
which no window sees. The obstruction is real at width `k`, and it
dissolves one letter wider: a `(k+1)`-window contains a law-bound word
ending strictly before its last letter, and that single extra
constraint forces a clean dichotomy — every within-layer `(k+1)`-window
is an anchor, or its identity action *proves* the phase did not move at
its final step (Lemma 5.22). In particular an all-neutral stretch
cannot cycle its phase at width `k + 1`: it parks. The graded bricks
and exactness theorem are §5.7's (Theorem 5.23); Theorem 5.10 below is
the width-1 case, whose grammar §5.7 lifts verbatim with
`(k+1)`-windows in place of letters.

*Remark (small layers always anchor).* Every layer with `|R| ≤ 2` of an
aperiodic invariant is 1-anchored. For `|R| = 1` there is nothing to
show. For `R = {c, c′}`: a within-layer action on two classes is a
partial identity, a partial constant, or contains the swap
`c ↦ c′, c′ ↦ c`; a letter `x` acting as the swap has
`act(x^{2m}) = id ≠ swap = act(x^{2m+1})` on `R` for every `m`, so no
power stabilizes — `[x^N] = [x^{N+1}]` fails for all `N`, contradicting
aperiodicity (equal classes act equally). Mixed actions therefore need
`|R| ≥ 3`, exactly the size at which Lemma 5.6(iii)'s scheme lives; on
census-scale invariants, whose layers are tiny, condition (A) at width 1
is the generic case — predicted as E1 in the companion spec, and now
measured: on the exhaustive 1-AP census (≤ 2 states; 2 898 layers over
891 aperiodic languages) no layer anchors at no width, none needs width
3, and the large majority anchor at width 1 (§8). The data also sharpen
an open question: Lemma 5.6(iii)'s non-anchoring scheme spends four
letters, and whether a layer over a *two-letter* alphabet can anchor at
no width — or even demand width 3 — is open; a negative proof would turn
the census column into a theorem and start the (A)-failure hunt (H2)
honestly at two propositions.

Anchoring is the *stem-side* precondition: it makes the walk transcribable.
Lemma 5.2(ii) forces a second, independent precondition on the *loop side*:

**Definition 5.7 (window-determined acceptance).** For `c ∈ 𝒞¹` and an
ω-word `β`, write `V(c, β) ∈ {0, 1}` for the invariant's verdict of `β`
*read from `c`* — the `P`-membership of the pair induced by any Ramsey
factorization of `β` folded from `c`, one verdict for all factorizations
(Lemma 5.9 below). A layer `R` is **(B)-determined at width `k`** if for
every `c ∈ R` and any two ω-tails `β, β′` confined to `R` from `c` whose
sets of recurring length-`k` factors are equal, `V(c, β) = V(c, β′)`: on
`R`-confined tails, the verdict from each class of `R` is a function of
the recurring `k`-window set. (The quantification is over the class the
tail is read *from*; the induced pair's stem coordinate moves with the
tail's own prefix and is folded inside `V` — fixing it would understate
the condition.)

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
STAY∞(R,r)  =  sojourn(r) ∧ G step ∧ W(R, r)          -- confined to R forever, accepting
Final(r)    =  STAY∞(R,r) ∨ LEAVE(r)
```

where `W(R, r)` is the acceptance term owned by the window engine (§5.5),
*per entry class*: under condition (B) at width `k'`, the exact-set normal
form of Proposition 5.15 — one disjunct `⋀ GF(w) ∧ ⋀ FG(¬w)` per
realizable recurring-window set whose verdict from `r` accepts; its
width-1 fringe is the *park*, a pure pair lookup (`(c, e) ∈ P` for the
stutter fold `e`).
The design carries three deliberate asymmetries:

- **The trigger identifies, the consequence legislates.** An anchor fires
  exactly at its target — that is condition (A) — and the consequence
  constrains what follows to actual Cayley edges of the identified class.
  A law cannot be conditioned on "the walk is at `c`": the phase is what
  the formula is *transcribing*, not something it can consult, so every law
  is necessarily **eager**, firing on every letter that looks like an
  anchor. Condition (A) is exactly the price of that eagerness — every
  look-alike firing promises something true, a lemma below (Lemma 5.8),
  not a hope — so the eager law is not a tolerable over-approximation:
  it *is* the transcription, and no tighter law exists to compare it
  against.
- **The sojourn's arms exclude exits, on purpose.** Inside `STAY∞` the law
  is precisely what confines the walk to `R`; inside `LEAVE` the
  `U`-witness ends the law's reign strictly before the exit letter, so an
  exit is never constrained by a law it is escaping. On the complete
  canonical machine this yields a structural collapse: `sojourn(c) ≡ ⊤`
  exactly when `E(c) = ∅`, so a **terminal layer sheds its entire law**
  and `STAY∞` reduces to the window term `W(R, r)` alone — the reason §5.4's
  prediction comes out literally `GF(a ∧ Xa)`, with no simplifier.
- **Legality and acceptance never mix.** The `W`'s weak arm makes parking
  *legal*; whether a parked tail *accepts* is `P`'s business inside
  `W(R, r)`.
  The split keeps every `U`-vs-`W` case analysis out of the law, and is the
  walk-side face of Lemma 5.2's division of labor.

The first asymmetry's promise is a lemma:

**Lemma 5.8 (the eager-firing license).** Let `R` be a 1-anchored layer,
`α = α_0 α_1 ⋯` an ω-word, and `(q_j)` its Cayley trajectory from a class
`q_t ∈ R` at position `t` (`q_{j+1} = q_j·α_j`). Say the class *changes*
at `j` when `q_{j+1} ≠ q_j`.

(i) *Triggers are disjoint and truthful.* The sets `{A(c)}_{c ∈ R}` are
pairwise disjoint; if `q_i ∈ R`, `q_i·α_i ∈ R` and `α_i ∈ A(c)`, then
`q_{i+1} = c` — whatever class the anchor fired from; a within-layer
letter that is no anchor fixes its source; hence every within-layer
change reads an anchor onto its destination, `M(c) ⊆ ⋃_{c' ≠ c} A(c')`.

(ii) *Confined suffixes satisfy the law.* If `q_j ∈ R` for all `j ≥ t`,
then `α, i ⊨ step` for every `i ≥ t`, and `α, t ⊨ sojourn(q_t)`.

(iii) *Exiting prefixes satisfy it up to the last change.* Suppose
`q_j ∈ R` exactly for `t ≤ j ≤ T`, the exit letter being `α_T ∈ E(q_T)`,
and let `μ` be the last position in `[t, T)` at which the class changes,
if any. If there is none, every `α_j` with `j ∈ [t, T)` lies in `L(q_t)`.
If `μ` exists: `α, i ⊨ step` for every `i ∈ [t, μ)`;
`α, t ⊨ sojourn(q_t)`; `α_μ ∈ A(q_T)`; and every `α_j` with `j ∈ (μ, T)`
lies in `L(q_T)`. These are verbatim the witnesses `LEAVE(q_t)` demands —
its first disjunct in the no-change case, its `U`-witness at `μ`
otherwise — modulo the child obligation `φ_{q_T·α_T}` from `T + 1` on,
which belongs to the R-order induction, not to the layer.

*Proof.* Throughout, a letter read while the class does not change fixes
it, and so lies in `L(·)` by that set's definition — diagonal anchors
included.

(i) A letter of `A(c) ∩ A(c')` has one within-layer action, a partial
constant with image `{c}` and `{c'}`: `c = c'`. If `α_i ∈ A(c)` with
`q_i, q_i·α_i ∈ R`, then `q_i` is a source of that partial constant, so
`q_{i+1} = c`. A within-layer action that is no partial constant is, by
Definition 5.4, a partial identity, fixing every source; and a change is
no identity at its source, hence a reset onto its destination.

(ii) Fix `i ≥ t` and a conjunct `A(c) → X sojourn(c)` of `step`; at most
one is triggered, by disjointness, and the rest hold vacuously. If
`α_i ∈ A(c)` then `q_{i+1} = c` by (i) — the trajectory never leaves `R`,
so the firing is within-layer. For `sojourn(c) = L(c) W M(c)` at `i + 1`:
let `ν` be the first position `> i` at which the class changes. The
letters of `[i+1, ν)` fix `c` and land in `L(c)`; if `ν` exists then
`α_ν`, read at `c` with `q_{ν+1} ∈ R` — no exit ever happens — lies in
`M(c)` and discharges the `W`; if not, the weak arm holds.
`α, t ⊨ sojourn(q_t)` is the same argument anchored at `t`.

(iii) *No change:* the class holds `q_t` on `[t, T]`, so every letter of
`[t, T)` fixes it and lies in `L(q_t)`. *`μ` exists:* the class never
changes after `μ`, so `q_{μ+1} = q_T`; the change at `μ` reads an anchor
onto its destination — `α_μ ∈ A(q_T)` by (i); the letters of `(μ, T)` fix
`q_T` and lie in `L(q_T)`. For `step` at `i ∈ [t, μ)`: if `α_i ∈ A(c)`,
the firing is within-layer (`i + 1 ≤ μ < T`), so `q_{i+1} = c`; the first
change `ν` after `i` exists (`ν ≤ μ`), the letters of `[i+1, ν)` lie in
`L(c)`, and `α_ν` — read at `c`, staying in `R` since `ν + 1 ≤ T` — lies
in `M(c)` and discharges the `W` strictly inside `R`. `sojourn(q_t)` at
`t`: likewise, with `ν₀ ≤ μ` the first change at all, letters of
`[t, ν₀)` in `L(q_t)` and `α_{ν₀} ∈ M(q_t)`. ∎

The license is the completeness half of a layer's exactness: on any word
whose walk conforms, every brick the label asserts is true — eager
firings included. The converse, that a word satisfying the label walks
conformingly, is the soundness leg of the theorem below.

Exactness needs one more preliminary, the ω-word generalization of the
membership fold:

**Lemma 5.9 (tail verdicts and transport).** For every `c ∈ 𝒞¹` and every
ω-word `β`: (i) `V(c, β)` is well-defined — all Ramsey factorizations of
`β`, folded from `c`, yield pairs with one `P`-verdict; (ii) *transport:*
`V(c, u·β) = V(c·[u], β)` for every finite `u`; (iii)
`V([ε], β) = [β ∈ L]`. Consequently the **tail language**
`T_c := { β : V(c, β) = 1 }` satisfies `T_{[u]} = u⁻¹L` for every finite
word `u`, and `T_{[ε]} = L`.

*Proof.* (i) Pick a representative `w` of `c` (a shortlex key; `w = ε`
for `c = [ε]`). A Ramsey factorization of `β` folded from `c` induces
the same linked pair as the corresponding factorization of the ω-word
`w·β` with `w` merged into the stem block. The invariant *recognizes*
`L`: the `P`-verdict of a linked pair equals the membership of every
ω-word it is computed from [SωS26, Lemma 3.2, Thm 5.1] — one semantic
referent, `[w·β ∈ L]`, for every factorization, so all of them agree.
(ii) A Ramsey factorization of `β` folded from `c·[u]` is a
factorization of `u·β` folded from `c` with `u` absorbed into the stem
coordinate — the same pair. (iii) is the invariant's membership
evaluation itself. For the consequence:
`β ∈ T_{[u]} ⟺ V([u], β) = V([ε], u·β) = [u·β ∈ L]`. ∎

Lemma 5.9's identity `T_{[u]} = u⁻¹L` also shows the memoized children
are exactly the residual tails, keyed by class — the DAG of §6 is a DAG
of residuals with canonical names. The section's centerpiece can now be
stated and proved:

**Theorem 5.10 (two-condition exactness, width 1).** Assume:

- **(A)** every layer of `Cay(L)` is 1-anchored;
- **(B)**, as a contract: for every layer `R` and every `c ∈ R` a formula
  `W(R, c)` over `Σ_λ` with `β ⊨ W(R, c) ⟺ V(c, β) = 1` for every
  ω-word `β` confined to `R` from `c` (Proposition 5.15 constructs it
  when `R` is (B)-determined at some width; a layer no run can stay in
  forever needs none, and an all-rejecting layer takes
  `W(R, c) = false`).

Then for every class `c`, `L(Final(c)) = T_c`; in particular
`L(Final([ε])) = L` — the assembled label defines the language.

*Proof.* Noetherian induction on the R-order of the layer `R` of `c`:
assume every memoized child `φ_d = Final(d)`, `d` in a strictly lower
layer, defines `T_d`. Let `(q_j)` be the trajectory of `α` from
`q_0 = c`.

*Completeness (`α ∈ T_c ⟹ α ⊨ Final(c)`).* If the trajectory stays in
`R` forever, Lemma 5.8(ii) gives `sojourn(c) ∧ G step`, and
`V(c, α) = 1` gives `α ⊨ W(R, c)` by the contract: together,
`STAY∞(R, c)`. If it exits at `T` with `α_T ∈ E(q_T)` toward
`d = q_T·α_T`, transport gives `V(d, α_{>T}) = V(c, α) = 1`, so the tail
lies in `T_d` and satisfies `φ_d` by induction; Lemma 5.8(iii) supplies
every remaining witness of `LEAVE(c)` — the first disjunct when the
class never changes before `T`, otherwise `sojourn(c)`, `step` up to the
last change `μ`, the `U`-witness `α_μ ∈ A(q_T)`, and the `leave(q_T)`
block through the exit.

*Soundness (`α ⊨ Final(c) ⟹ α ∈ T_c`).* The pivot is an **escort
invariant**: if `sojourn(c)` holds at position `0` and `step` holds at
every position `< N`, then the trajectory stays in `R` through `N` and
every position `i ≤ N` sits under an *active sojourn* licensing
`α_i ∈ L(q_i) ∪ M(q_i)`. Induction on renewals: an active
`sojourn(q_p)` confines the letters after `p` to `L(q_p)` until a first
`M(q_p)`-letter — stutters keep the walk sitting, so the formula's class
and the walk's agree — and at the discharge `ν` the move lands in `R`;
by Lemma 5.8(i) the moving letter is an anchor onto exactly
`q_{ν+1}`, so when `ν < N`, `step` at `ν` fires
`A(q_{ν+1}) → X sojourn(q_{ν+1})` and the escort renews; a sojourn that
never discharges keeps the walk sitting forever. In particular no letter
before `N` exits `R` — the law confines. Now the three shapes:

- `α ⊨ STAY∞(R, c)`: the escort with `N = ∞` confines the trajectory
  forever; the contract turns `α ⊨ W(R, c)` into `V(c, α) = 1`.
- `α ⊨ leave(c)`: the letters before the `U`-witness lie in `L(c)`, so
  the walk still sits at `c` there; the witness letter `a ∈ E(c)` steps
  to `d = c·a` and the tail satisfies `φ_d`, hence lies in `T_d` by
  induction; transport folds back: `V(c, α) = V(d, tail) = 1`.
- `α ⊨ sojourn(c) ∧ (step U ⋁_{c′}(A(c′) ∧ X leave(c′)))`: run the
  escort to the `U`-witness `w`. The active sojourn at `w` licenses
  `α_w ∈ L(q_w) ∪ M(q_w)` — **not** an exit — so the anchor fires
  truthfully (Lemma 5.8(i)): `q_{w+1} = c′`, the formula's class and the
  walk's re-synchronize, and `leave(c′)` from `w + 1` concludes as in
  the previous shape, transport folding the whole prefix onto `c`. ∎

Three remarks. *Uniqueness* is free throughout: `Cay(L)` is
deterministic and complete, every word has exactly one trajectory.
*Degeneracies* fall out with no case analysis: an all-rejecting final
layer has `W(R, c) = false`, killing `STAY∞`; a terminal layer has
`E ≡ ∅`, killing `LEAVE` and shedding its law; a frozen singleton
reduces to `W(R, c)` alone (§5.5). And the escort is where the
third asymmetry of the bricks earns its keep: the sojourn arms exclude
exits, so the one letter the formula cannot vouch for — the anchor that
would exit rather than reset — is exactly the letter the active sojourn
forbids.

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

**Claim 5.11 (the finest phase suffices).** When (A) and (B) hold, the
transcription is exact for `L` (Theorem 5.10), and nothing finer is ever
needed: the syntactic class is the finest
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
(an all-rejecting final layer has `W(R, ·) = false`; no rejecting-layer test
exists anywhere), and only their `LEAVE` chains survive.
*Predicted output*, then, for the whole extraction of `GF(aa)`: `LEAVE`
chains through `{1,3}` / `{2,4}` into the memoized child at `5`, whose
label is `GF(a ∧ Xa)` — an `F(…)`-shaped reach wrapper around the child —
and since the reach wrapper is implied by the child (recurrence implies
occurrence), the simplified form is `GF(a ∧ Xa)` exactly. A
prefix-independence read-off (one residual ⟹ the reach wrapper is always
redundant — Lemma 5.13 below) would emit it directly.
The experiment suite checks this prediction end to end (E0 in the companion
spec); the M1 run confirms the layer tables, the widths, and the Lemma-5.2
witness pair above exactly — the emitted-formula check awaits the engine.

### 5.5 The window engine is Arnold's second shape

Lemma 5.2(ii) assigns every acceptance decision to a second engine; the
*frozen* layer — all letters neutral, the walk stabilized — is only that
engine's purest case, where nothing else remains. This is not a corner
case; it is a theorem-shaped fact:

**Proposition 5.12 (the division of labor).** Let `α ∈ Σ^ω`, `(q_j)` its
prefix-class walk, `R` the final layer where the walk stabilizes
(Lemma 5.3), and `(s, e)` its accepting pair (one verdict for all
factorizations, Lemma 5.9(i)). Then:

(i) *the walk owns the stem*: `s` is a walk value, attained at every
merge cut of the factorization, and membership folds along the walk —
`[α ∈ L] = V(q_j, α_{≥j})` for every `j`;

(ii) *no walk function owns the loop*: membership is not a function of
the walk — no Muller condition on its recurring states and no
Emerson–Lei condition on its recurring edges decides it;

(iii) *windows own the loop*: if `R` is (B)-determined at width `k`,
then for every `j` past the walk's entry into `R`, membership is the
window read-off of the tail — `[α ∈ L] = f_{q_j}(Win_k(α_{≥j}))` —
realized in LTL by `W(R, q_j)`;

(iv) *jointly they suffice*: under (A) and the window contract, the two
engines assemble to a defining label.

*Proof.* (i) Lemma 5.2(i) for the walk values; Lemma 5.9(ii) applied to
each prefix, with 5.9(iii) at `j = 0`, for the fold. (ii) Lemma 5.2(ii).
(iii) Past entry the tail is confined to `R` from `q_j`, so
`[α ∈ L] = V(q_j, α_{≥j}) = f_{q_j}(Win_k(α_{≥j}))` by transport and
Definition 5.7, and Proposition 5.15 realizes `f` as a formula. (iv)
Theorem 5.10. ∎

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
emits is either `false` or redundant (Lemma 5.13), and the language lives
entirely in the window engine.

**Lemma 5.13 (reach absorption).** Let `L` be prefix-independent. Then
(i) `Σ*·L = L`, and `L(F φ) = Σ*·L(φ)` for every formula `φ`; (ii)
`T_c = L` for *every* frozen class `c` (frozen tails, Lemma 5.14 below);
(iii) consequently any formula `ψ` defining a frozen tail `T_c` already
defines `L`: every exact label — in particular one carrying `ψ` as a
disjunct — is equivalent to `ψ` alone, and the reach wrapper is
redundant, `L(F ψ) = L`; the extractor may emit `ψ` directly.

*Proof.* (i) `u·α ∈ L ⟺ α ∈ L` gives `Σ*·L ⊆ L`; `u = ε` gives the other
inclusion. For any `φ`: `α ⊨ F φ` iff some suffix of `α` satisfies `φ`,
iff `α ∈ Σ*·L(φ)` — LTL being future-only, a suffix's satisfaction never
consults the prefix spliced before it. (ii) By Proposition 4.2, `P` is
loop-determined: `(s, e) ∈ P ⟺ (e, e) ∈ P`. So `α ∈ T_c ⟺ (c, e(α)) ∈ P
⟺ (e(α), e(α)) ∈ P ⟺ α ∈ L` — the frozen class drops out. (iii)
`L(ψ) = T_c = L` by (ii); an exact label also defines `L`, so the two are
equivalent; and `L(F ψ) = Σ*·L(ψ) = Σ*·L = L` by (i). ∎

The hypothesis of (iii) — that `ψ` *defines* `T_c` — is a semantic fact
about the emitted child, and it is exactly what Theorem 5.10 certifies
for the memoized label at a frozen class. The dependency
runs one way: exactness first proves the label, absorption then discards
the wrapper; nothing here feeds back into the exactness proof.

**The no-recursion trap.** The frozen tail language at a frozen class `c` is
`T_c = {α : (c, e(α)) ∈ P}` — well-defined and prefix-independent:

**Lemma 5.14 (frozen tails).** At a frozen class `c`, `T_c` is exactly the
residual `u⁻¹L` of any representative `u` of `c`; in particular it does not
depend on the choice of Ramsey idempotent `e(α)`, and it is
prefix-independent.

*Proof.* `c` frozen means every letter is neutral at `c`, so `c·[w] = c`
for every finite `w`; in particular `(c, e)` is linked for every
idempotent `e` arising from a tail. Well-definedness and `T_c = u⁻¹L`
are Lemma 5.9(i) and its consequence; prefix-independence is transport,
`V(c, w·α) = V(c·[w], α) = V(c, α)` (Lemma 5.9(ii)). ∎

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
  Boolean combination. The general read-off is Proposition 5.15 below.
  ⟨TBD: bound the needed width by a layer-local definiteness degree; align
  the (B)-stratum with the locally-(threshold-)testable ω-varieties
  (Beauquier–Pin / Wilke — sources to be added to the library) so the
  stratum is a known class with our operational reading.⟩
- **(B) fails at every affordable width** — the genuine nesting case: the
  recurring windows do not determine the verdict, because acceptance hangs
  on *order* among recurring factors, the classical separator between
  `FO[<]` and locally testable (`FO[+1]`, Thérien–Weiss; cite-TBD). Here
  and only here does a DG-style descent survive, demoted to "the engine
  inside one frozen layer" and scoped to that layer's tail algebra — which
  is not smaller in general (`T_c = L` whenever `L` is prefix-independent,
  Lemma 5.13(ii)), so the honest statement is: this stratum is where
  extraction still pays DG's price, and the census measures how rare it is
  (§8). An ω-specific descent that beats DG on this stratum is the paper's
  main open problem.

The first bullet's read-off, in full:

**Proposition 5.15 (the window normal form).** Let `R` be (B)-determined
at width `k` and `c ∈ R`. For `S ⊆ Σ_λ^k` say `S` is *realizable from
`c`* if some ω-tail confined to `R` from `c` has recurring-window set
exactly `S`; write `Win_k(β)` for that set. Then:

(i) the verdict map `f_c(S) := V(c, β)` — `β` any confined tail with
`Win_k(β) = S` — is well-defined on realizable sets, and

```
W(R, c)  =  ⋁_{S realizable from c, f_c(S) = 1}
              ( ⋀_{w ∈ S} GF ŵ  ∧  ⋀_{w ∈ Σ_λ^k \ S} FG ¬ŵ ),
ŵ        =  w₁ ∧ X w₂ ∧ ⋯ ∧ X^{k−1} w_k
```

satisfies the contract of Theorem 5.10: `β ⊨ W(R, c) ⟺ V(c, β) = 1`
for every `β` confined to `R` from `c`.

(ii) *Computation.* In the memory graph `G(R, c)` — nodes `(q, m)` with
`q ∈ R` and `m` the last `k` letters read, edges the `R`-confined Cayley
steps out of the `c`-cone — `S` is realizable from `c` iff some strongly
connected subgraph `H`, reachable with full memory, has window
projection exactly `S`; a covering tour of `H` yields an ultimately
periodic witness `u·v^ω`, and `f_c(S) = Val(c·[u], [v])`.

(iii) *Deciding (B).* Confined tails reduce to lassos: every confined
`β` admits an ultimately periodic `β̂`, confined with
`Win_k(β̂) = Win_k(β)` and `V(c, β̂) = V(c, β)`. Hence (B) at width `k`
holds iff for each `c ∈ R` and each realizable `S`, all covering tours
of all `S`-projecting subgraphs, from all full-memory entries, yield one
verdict. Two cautions make the check precise, both load-bearing. First,
the verdict factors through the tour's *loop class*, **not** through the
subgraph: one subgraph carries tours of several loop classes, and two
covering tours of the same `H` can disagree — on `EvenBlocks`' frozen
layer at `k = 3`, `(a⁴·!a)^ω` and `(a⁵·!a)^ω` traverse the same
recurring edge set with opposite verdicts, their loop classes on
opposite phases of the group. The object to compute per subgraph `H` is
its **loop-class closure** `{ [w] : w labels a closed covering walk of
H }` — a subset of `𝒞`, computable by a `(node, class, covered-edges)`
closure — and (B) holds iff, grouping across subgraphs sharing one
window projection `S`, all induced pair verdicts agree. Second, the
finiteness of the check lives in `𝒞`, never in the layer: the loop
class is folded through the whole algebra even where the walk is
frozen, so no length cap in `|R|` and `|Σ_λ|` alone bounds the tours
that must be compared (the same specimen refutes the cap `2·|R|·|Σ_λ|`:
the conflicting loops have length 5, the cap value 4). The closure is
accordingly the *normative* decision procedure for (B): per subgraph `H`
its state space is `O(|H|·|𝒞|·2^{|E(H)|})` — exponential only in the
layer-local edge count of `H`, with the class coordinate contributing the
factor `|𝒞|` linearly — and bounded enumeration under any cap remains
admissible as a pre-filter, its conflicts exact, its conflict-free
outcomes evidence rather than proof until the closure has run (no
sufficiency theorem is known for any cap, the excision route foundering
on window-set preservation).

(iv) *Sizes.* Each disjunct has modal depth `k + 1` and at most
`|Σ_λ|^k` conjuncts; the disjuncts number at most the realizable sets,
`≤ 2^{|Σ_λ|^k}` — the generic price of the exact-set form, collapsing
under structure: an upward-closed accepting family keeps only its
minimal sets, `⋁_S ⋀_{w ∈ S} GF ŵ`, and on `GF(aa)`'s frozen layer the
single minimal set `{aa}` gives `GF(a ∧ X a)` — no simplifier involved.

*Proof.* (i) Well-definedness is Definition 5.7 verbatim. For confined
`β`: `β ⊨ GF ŵ` iff the window `w` occurs at infinitely many positions
iff `w ∈ Win_k(β)`, and `β ⊨ FG ¬ŵ` iff `w ∉ Win_k(β)`; so `β` satisfies
the `S`-disjunct iff `Win_k(β) = S` exactly — disjuncts are pairwise
exclusive — and `Win_k(β)` is realizable, `β` being its own witness:
`β ⊨ W(R, c) ⟺ f_c(Win_k(β)) = 1 ⟺ V(c, β) = 1`.

(ii) A covering tour traverses every edge of `H` infinitely often and
eventually only `H`: its recurring windows are exactly `H`'s.
Conversely the infinitely-traversed edges of a confined tail form a
reachable strongly connected subgraph whose window projection is the
recurring set. The witness verdict is the invariant's lasso evaluation.

(iii) Cut points of a Ramsey factorization of `β` carry finitely many
(idempotent, length-`(k−1)` boundary context) colors; passing to an
infinite monochromatic subsequence of cuts re-factors `β` with one
color. Wrap a block stretch `w_{i+1}⋯w_{i+m}` starting beyond the last
occurrence of every non-recurring window and long enough to contain
every recurring one — its interior windows are then *exactly* the
recurring set: the loop class is the same idempotent `e` (idempotency
absorbs the grouping), the stem class is `[w₀⋯w_i] = [w₀]·e`, so the
pair — hence the verdict — is unchanged; and every seam window of the
wrap already occurs at each original cut (one boundary context), so it
recurs in `β`: `Win_k` is preserved. The finiteness of the check: tours
enter through finitely many classes, and per subgraph the loop classes
of covering tours form the loop-class closure — computed, not sampled:
extend `(node, accumulated class, edge subset covered)` states to
closure and collect the classes closing at the base node with all of
`H` covered; the state space is finite, the class coordinate ranging
over `𝒞`.

(iv) Counting is immediate. For an upward-closed family, a confined `β`
satisfies `⋁_min ⋀ GF` iff `Win_k(β)` contains some minimal accepted set
iff `f_c(Win_k(β)) = 1`. On `GF(aa)`, acceptance from the frozen class
is "the window `aa` recurs" (§5.4): upward-closed, minimum `{aa}`. ∎

The architecture, assembled — the paper's picture:

```
extract(𝓘):
  0. aperiodicity scan — group ⟹ certificate (§4), stop
  1. quotient the alphabet by λ; choose L or L̄ by P-shape (cheaper side)
  2. ladder read-off: safety/co-safety/obligation ⟹ finite-word extraction
     of the class-defined prefix language + fixed template, stop
  2.5 combinators (§5.6): OR-split P by final layer; AND-split by subdirect
      factorization; re-canonicalize each piece (a divisor — never leaves
      LTL, Prop 5.16), recurse on pieces whose read-offs improved, combine
      with ∨ / ∧
  3. walk engine (stem side): descend the R-order of Cay(L); per layer:
       (A) at k ≤ cap  ⟹ flat law/leave bricks (width 1 at k = 1, window
                          width k+1 else — §5.7, Thm 5.23), exits to
                          memoized class children
       (A) fails       ⟹ (a) retry after the step-2.5 combinators — an
                          OR/AND piece re-canonicalizes to its own smaller
                          table whose layers may anchor (Thm 5.19); (b)
                          else the scoped fallback (§5.7, Prop 5.24): DG
                          run on the layer action monoid 𝒜_R — a quotient
                          of M¹, aperiodic with it (Prop 5.21) — choosing
                          the separator c as a width-1 partial-constant
                          letter if one exists (the least blind choice —
                          it is an anchor of the failed test, repairing
                          §3's blindness (3)), the emitted subformula
                          rooted at the layer entry and memoized as
                          usual; DG's price is paid on |𝒜_R|, never on
                          |M|
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

**Proposition 5.16 (decomposition never leaves LTL).** Any language
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
form — and the operation has its classical name, with one twist the
worked specimen below makes vivid. Throughout, `Val` is the lasso-verdict
map of §4.2, a pair set is identified with its verdict map, and a
factorization is

```
    Val_P = Val_{P₁} ∧ Val_{P₂}  (pointwise),   Val_{Pᵢ} factoring through a
    proper congruence θᵢ,   both factors proper: Val_{Pᵢ} ≠ Val_P.
```

**Definition 5.17 (ω-congruence for a pair set).** A monoid congruence
`θ` on `(𝒞, M)` is an **ω-congruence for** a pair set `P′` if `Val_{P′}`
factors through `θ` in both coordinates: `c θ c′` and `d θ d′` imply
`Val_{P′}(c, d) = Val_{P′}(c′, d′)`. (Checkable in `O(|𝒞|²)` lookups once
`Val_{P′}` is tabled.)

**Proposition 5.18 (quotients recognize).** If `θ` is an ω-congruence for
`P′`, the quotient invariant `𝓘/θ = (𝒞/θ, λ/θ, M/θ, P′/θ)` — pair
verdicts inherited through the factoring — recognizes `L(P′)`: the
standard membership rule, evaluated in the quotient, returns `Val_{P′}`
on every lasso. Consequently the syntactic ω-semigroup of `L(P′)`
divides `M/θ`, of size `< |𝒞|` for proper `θ`.

*Proof.* Two ingredients. *Idempotent-power stability:* `⟨d^j⟩ ⊆ ⟨d⟩`
share their unique idempotent, so `(d^j)^π = d^π` and
`Val_{P′}(c, d^j) = Val_{P′}(c, d)` — literally the same lookup.
*Descent:* the quotient rule folds a lasso `(u, v)` to
`([u]_θ, [v]_θ)`, iterates the loop to an idempotent of the quotient —
`[v^j]_θ` for some `j`, `v^j` not necessarily idempotent in `𝒞` — and
looks up the induced pair; by the factoring that lookup equals
`Val_{P′}([u·v^j], [v^j])`, the verdict of `u·v^j·(v^j)^ω = u·v^ω`,
which by stability is `Val_{P′}([u], [v])`. (One convention wrinkle: `θ`
may merge the fresh identity with a neutral word class — Proposition 5.20
shows that is the *only* extra collapse possible — and the quotient then
carries its unit inside a word class; re-canonicalization restores the
freshness convention.) ∎

**Theorem 5.19 (the AND-split).** Given a factorization as displayed,
`L = L(P₁) ∩ L(P₂)`, each factor recognized by the strictly smaller
quotient `𝓘/θᵢ` (Proposition 5.18), each factor's own invariant obtained
by re-canonicalization. Moreover the search is complete on
*saturations*: for a congruence `θ`, let `Val^θ` be the least
`θ`-factoring verdict map `≥ Val_P` (pointwise `∨` over `θ`-blocks); if
*any* factorization with congruences `(θ₁, θ₂)` exists, then already
`Val^{θ₁} ∧ Val^{θ₂} = Val_P`. Hence enumerating congruence pairs with
their canonical saturations — coarsest first, the census-sized lattice
being enumerable — finds a factorization iff one exists, and otherwise
certifies `P` **irreducible**, the honest fallback. (Properness has
teeth, but fewer than one might hope: even `GFa` factors, as
`Fa ∧ (GFa ∨ G¬a)`, both congruences the neutral-unit merge of
Proposition 5.20 — the stem coordinate of `Val` sees distinctions that
pure loop verdicts blur, and the slack class carries them. Whether a
found split is *adopted* is the guard's business, read-offs in hand;
exhibiting a language irreducible outright is a census query ⟨TBD⟩.)

*Proof.* Languages agree on lassos, and on lassos the displayed verdicts
conjoin. Completeness: `Val_P ≤ Val^{θᵢ} ≤ Val_{Pᵢ}` — the middle map is
the least `θᵢ`-factoring map above `Val_P`, and `Val_{Pᵢ}` is such a
map — so `Val_P ≤ Val^{θ₁} ∧ Val^{θ₂} ≤ Val_{P₁} ∧ Val_{P₂} = Val_P`. ∎

**Proposition 5.20 (subdirectness is automatic).** On the reduced
invariant, an ω-congruence for `P` itself can identify two *word*
classes never, and the fresh identity `[ε]` only with a neutral word
class (which is then unique). Consequently, in any factorization,
`θ₁ ∩ θ₂` restricted to the word classes is the equality: the two
quotients form a subdirect representation of `S(L)₊` in Birkhoff's
sense, with no side condition imposed — the Δ-condition is a theorem,
not a hypothesis, the only slack being the conventional freshness of
`[ε]`.

*Proof.* Let `θ` be an ω-congruence for `P` and `c θ c′`, both word
classes. For every linear context, `x·c·y θ x·c′·y` (congruence), so
`Val_P(x·c·y, t) = Val_P(x·c′·y, t)`; for every ω-power context,
`c·y θ c′·y`, so `Val_P(x, c·y) = Val_P(x, c′·y)`: `c` and `c′` are
identified by the two-shape syntactic congruence, which is equality on
word classes of the reduced object [SωS26, Thm 4.5]. If `[ε] θ n` for a
word class `n`, then `x θ x·n` for every `x`; the freshness convention
keeps `x·n` a word class, so `x = x·n` for every word class `x`: `n` is
neutral (and unique, two neutrals absorbing each other). For the
consequence: `θ₁ ∩ θ₂` is an ω-congruence for `P` — both `Val_{Pᵢ}`
factor through it, hence so does their conjunction `Val_P` — and the
first part pins it to equality on word classes. ∎

**The type specimen, corrected by its own algebra.** `GFa ∧ FGb` —
infinitely many `a`, eventually always `b` — looks like it should factor
"forget `b` / forget `a`". Its syntactic invariant refuses the naive
reading, instructively. The classes are `[ε]` and three word classes:
`⊥` = "contains a `!b`-letter" (two-sided absorbing), `β₀` = "all-`b`,
no `a`", `β₁` = "all-`b`, with `a`"; every word class is idempotent, and
`P` accepts exactly the pairs with loop coordinate `β₁`. `GFa` is *not
recognized on this table at all*: `⊥` has swallowed the `a`-bit — an `a`
inside a spoiled block is syntactically invisible, `a!b ≈_L !a!b`. The
split exists nonetheless. Take `θ_A` merging `{β₀, β₁}` and `θ_B`
merging `{⊥, β₁}` (both are congruences; check the four products each);
their saturations are `Val^{θ_A} = [loop ≠ ⊥]` and
`Val^{θ_B} = [loop ≠ β₀]`, both factoring, conjoining to
`[loop = β₁] = Val_P`, and the quotients are the 3-class algebras of
`FGb` and of `GF(a ∨ !b)` respectively:

```
    GFa ∧ FGb   =   FGb  ∧  GF(a ∨ !b)
```

— the conjunction the table itself chooses. The second factor is `GFa`
*relativized* by the first: infinitely many good events, a good event
being an `a` or a (transient) `!b`. The AND-split does not recover the
conjunction the user wrote; it recovers one whose factors are languages
of the object's own quotients — self-relativizing, and exact. Each
factor extracts as a one-layer window brick. ⟨TBD: display the two
quotient tables; conformance-check the factorization in the tool
(E-series); the irreducible-vs-split census fractions live in
[SωSN26].⟩

The combinators compose (OR of ANDs, complement flips via `P^c` choosing
the cheaper side), they all commute with re-canonicalization, and
Proposition 5.16 makes the whole combinator layer safe: no move ever
leaves LTL or grows the algebra. They slot into the architecture as step
2.5, between the ladder templates and the walk engine.

### 5.7 The graded engine and the scoped fallback

Two debts remain on the stem side: the brick grammar for layers that
anchor only at a width `k ≥ 2` (Definition 5.5 defined the ladder;
§5.2's bricks and Theorem 5.10 consumed only its first rung), and the
fallback for layers that anchor at no affordable width (the
architecture's step 3). Both are settled by the same move — name the
algebraic object the layer already owns, then run a known engine on
it: the width-1 grammar on `(k+1)`-windows for the first, the DG
induction on the layer's own action monoid for the second. One
preliminary serves both.

**Proposition 5.21 (the layer action monoid).** For every layer `R`:

(i) *readability is free*: for `c ∈ R` and any word `w`, `c·w ∈ R`
already forces every intermediate `c·a₁⋯a_j` into `R`; hence
`dom(act_R(w)) = { c ∈ R : c·w ∈ R }`.

(ii) `act_R(w)` depends on `w` only through `[w]`, and
`m ↦ (c ↦ c·m, where in R)` is a multiplicative map from `M¹` onto the
**layer action monoid** `𝒜_R` of all within-layer actions: `𝒜_R` is a
quotient of `M¹` — it divides `M¹`, and is aperiodic whenever `M` is.

(iii) for `r, c ∈ R`, the *confined-walk language*
`L_{r→c} = { u ∈ Σ_λ* : the walk from r stays in R and ends at c }`
equals `{ u : act_R(u)(r) = c }`: a finite-word language recognized by
`𝒜_R` through `u ↦ act_R(u)`.

*Proof.* (i) Right multiplication descends the R-order (Lemma 5.3):
`c ≥_R c·a₁⋯a_j ≥_R c·w`, and `c·w` R-equivalent to `c` squeezes every
intermediate into `R`. (ii) By (i), `act_R(w)` is computed from `[w]`
alone — sources the `c` with `M(c, [w]) ∈ R`, images `M(c, [w])` — and
multiplicativity is (i) applied to a product: `c·mm′ ∈ R` iff
`c·m ∈ R` and `(c·m)·m′ ∈ R`. A surjective multiplicative image of a
monoid is a quotient; quotients divide, and divisors of aperiodic
monoids are aperiodic. (iii) "Stays in `R`" is exactly
`r ∈ dom(act_R(u))`, by (i). ∎

**The graded engine.** The obstruction recorded after Lemma 5.6 was
that neutral windows reveal nothing, and at width exactly `k` that
silence is fatal: a neutral window can end on a phase move. One letter
wider, the silence becomes testimony:

**Lemma 5.22 (the last-step dichotomy).** Let `R` be `k`-anchored and
let a trajectory satisfy `q_j ∈ R` for `i ≤ j ≤ i + k + 1`, reading
the `(k+1)`-window `w = α_i ⋯ α_{i+k}`. Then either

(i) `act_R(w)` is a partial constant onto some `c` — and
`q_{i+k+1} = c` *whatever* `q_i` was: anchor windows are pairwise
disjoint across targets and fire truthfully at any history; or

(ii) `act_R(w)` is a partial identity — and `q_{i+k+1} = q_{i+k}`:
the phase did not move at the window's last step.

(On a diagonal window, constant and identity at once, both conclusions
hold and agree.)

*Proof.* `w` is readable (the trajectory reads it), so its action is
non-empty; `k`-anchoredness applies to `w` (length `k+1`) and to its
prefix `z = α_i ⋯ α_{i+k−1}` (length `k`). If `act_R(z)` is a constant
onto `e`, every value of `act_R(w)` is `e·α_{i+k}`: `w` is a constant.
Contrapositively, if `w` is not a constant, `z` is a partial identity,
so `q_{i+k} = q_i·z = q_i`; and `w`, identity-or-constant but not
constant, is a partial identity, so
`q_{i+k+1} = q_i·w = q_i = q_{i+k}`. In case (i),
`q_{i+k+1} = act_R(w)(q_i) = c` by constancy, and a partial map has
one image. ∎

The extra letter is exactly what width `k` lacked: the `(k+1)`-window
contains a law-bound word ending *strictly before* its last letter,
and that word either resets — making the whole window a reset — or
certifies that the source of the last step equals the phase at the
window's start, turning the window's own identity action into a proof
that the last step moved nothing. At width `k` the corresponding
prefix has length `k − 1` and is unconstrained. Two consequences. The
mod-`k` crux is void: along a confined stretch whose `(k+1)`-windows
are all neutral, (ii) applies at every position — the phase is
*constant*; an all-neutral stretch parks, and every phase move
completes an anchor window. And `k + 1` is the honest operating width,
`k` being insufficient whenever some neutral `k`-window hosts a
completed excursion — whether a census specimen realizes that
insufficiency, making `k + 1` tight and not merely sufficient, is a
frontier hunt (H6 in the companion spec).

**The graded bricks.** Fix a layer anchored at width `k ≥ 2`, write
`κ = k + 1`, `A_κ(c) = { w ∈ Σ_λ^κ : act_R(w) constant onto c }`, and
`ŵ = w₁ ∧ X w₂ ∧ ⋯ ∧ X^{κ−1} w_κ` (Proposition 5.15's rendering). The
letter sets `L(c), M(c), E(c)`, `sojourn(c) = L(c) W M(c)` and
`leave(c)` are §5.2's, unchanged; the law's trigger moves from letters
to windows, and a **transient fold** of depth `k` covers the entry,
where a trailing window would still straddle it:

```
step_κ   =  ⋀_{c ∈ R} ⋀_{w ∈ A_κ(c)} ( ŵ → X^κ sojourn(c) )

TR_0(c)  =  sojourn(c)
TR_j(c)  =  ⋁_{a ∈ L(c) ∪ M(c)} ( a ∧ X TR_{j−1}(c·a) )            j = 1..k
TL_0(c)  =  leave(c) ∨ ( sojourn(c) ∧
              ( step_κ U ⋁_{c′ ∈ R} ⋁_{w ∈ A_κ(c′)} ( ŵ ∧ X^κ leave(c′) ) ) )
TL_j(c)  =  ⋁_{a ∈ E(c)} ( a ∧ X φ_{c·a} )
              ∨  ⋁_{a ∈ L(c) ∪ M(c)} ( a ∧ X TL_{j−1}(c·a) )       j = 1..k

STAY∞_κ(R, r)  =  TR_k(r) ∧ G step_κ ∧ W(R, r)
Final(r)       =  STAY∞_κ(R, r) ∨ TL_k(r)
```

The trees thread the fold explicitly — during the first `k` in-layer
steps the phase is a known function of the entry class and the letters
read, so nothing is guessed — and they are class-indexed like
everything else: `TR_j(c)`, `TL_j(c)` depend on `(c, j)` only,
`O(|R|·k)` DAG nodes of `O(|Σ_λ|)` edges each, while `step_κ` carries
at most `|Σ_λ|^κ` triggers. Timing inherits width 1's asymmetry:
`step_κ`'s consequences lag its triggers by `κ`, so triggers asserted
on `[t, i)` govern moves on `[t+k, i+k)` — coverage ends exactly where
`TL_0`'s `U`-witness window takes over, the witness's own last step
being the final move that `leave(c′)` then unwinds. The law's reign
still ends strictly before the exit letter, and the degeneracies of
§5.2 survive verbatim: a terminal layer sheds trees and law alike
(`sojourn ≡ ⊤`, no consequence bites), a frozen layer reduces to
`W(R, r)`.

**Theorem 5.23 (graded exactness).** Let every layer of `Cay(L)` be
anchored at some width `k_R`, each transcribed at width 1 where
`k_R = 1` (§5.2) and at `κ = k_R + 1` as above where `k_R ≥ 2`, with
(B)'s contract as in Theorem 5.10. Then `L(Final(c)) = T_c` for every
class `c`; the assembled label defines `L`.

*Proof.* Noetherian induction on the R-order as in Theorem 5.10; fix a
layer `R` with `k = k_R ≥ 2`, entry `r` at position `t`, trajectory
`(q_j)` with `q_t = r`, and write `c_j` for the threaded classes,
`c_0 = r`, `c_{j+1} = c_j·α_{t+j}`; while the walk is in `R`,
`c_j = q_{t+j}` — the trees thread the true fold — and `Cay(L)` being
complete, each letter lies in exactly one of `L, M, E` at its class.

*Completeness (`α ∈ T_r ⟹ α ⊨ Final(r)`).* If the walk exits at
`T < t + k`, the `TL`-branches follow the true letters to the exit
disjunct, whose child obligation holds by induction and transport
(Lemma 5.9(ii)). If it exits at `T ≥ t + k`, `TL_k(r)` reaches
`TL_0(c_k)` along true branches, and `sojourn(c_k)` holds as at
width 1. If the class never changes on `[t+k, T)`, `leave(c_k)`
concludes. Otherwise let `μ` be the last change in `[t+k, T)`: the
window covering `[μ−k, μ]` sits inside the layer and moves the phase
at its last step, so it is an anchor onto `q_{μ+1}` (Lemma 5.22(ii),
contraposed) — the `U`-witness at `μ−k`, with `X^κ leave(q_{μ+1})`
supplied by the stutters of `(μ, T)` and the exit. For the left arm, a
trigger at `p ∈ [t+k, μ−k)` has its window inside the layer and its
pin truthful (Lemma 5.22(i)), say onto `c`; the next change after it
exists (`μ` at the latest, and `p + κ ≤ μ`), lands within `R` strictly
before `T`, and discharges `sojourn(c)` — so `step_κ` holds throughout
`[t+k, μ−k)`. If the walk never exits, the same trigger argument gives
`G step_κ` (a triggered sojourn discharges at the next change or holds
by its weak arm), `TR_k(r)` follows the true branches into
`sojourn(c_k)`, and `V(r, α) = 1` yields `W(R, r)` by the contract:
`STAY∞_κ`.

*Soundness (`α ⊨ Final(r) ⟹ α ∈ T_r`).* The transient trees pin the
walk: branch letters lie in the threaded class's own `L ∪ M` (or `E`,
in `TL`'s exit disjuncts), so formula and walk agree through the
transient and no unlicensed exit occurs; an exit branch hands a tail
in `T_{c_j·a}` (induction) and transport folds the verdict onto `r`.
Past the transient, Theorem 5.10's escort runs verbatim with
Lemma 5.22 in the role of Lemma 5.8(i): an active `sojourn(c)`
licenses only `L(c) ∪ M(c)` — never an exit — and holds the phase
through stutters; at a discharge `ν` the window covering `[ν−k, ν]` is
in-layer (its letters are sojourn-licensed) and is an anchor onto
exactly `q_{ν+1}` (the dichotomy, contraposed), so `step_κ` at `ν−k` —
asserted, since `ν−k` precedes the `U`-witness position inside the `U`
and is unrestricted under `G step_κ` — renews the escort at `ν+1` on
the walk's true class. In `STAY∞_κ` the escort confines forever and
the contract turns `W(R, r)` into `V(r, α) = 1`. In `TL_0`, run the
escort to the `U`-witness `i`: coverage on `[t+k, i)` governs every
move through `i+k−1`, the witness window's letters are licensed (hence
in-layer), its pin is truthful — the walk sits at `c′` at `i+κ` — and
`leave(c′)`, stutters then an exit with its child obligation,
concludes by induction and transport. ∎

Whether a layer anchors, at which width, and hence at which width each
layer's engine runs are equations on `𝓘(L)` (Lemma 5.6(v)): §5.3's
canonicity statement covers the graded engine unchanged.

**The scoped fallback.** When a layer anchors at no affordable width,
the stem side falls back to the prior route — but on the layer's own
monoid, never on `M`:

**Proposition 5.24 (the scoped fallback).** Let `R` be a layer, `r`
its entry class. (i) Each `L_{r→c}` is a finite-word language over
`Σ_λ` recognized by the aperiodic monoid `𝒜_R` (Proposition 5.21), so
the DG induction — or any step-5 finite-word extractor — yields an
LTLf formula `ψ_{r→c}` defining it, at a cost that is a function of
`(|𝒜_R|, |Σ_λ|)` and never of `|M|`. (ii) With `⟨ψ; a; φ⟩` the strong
insertion of an LTLf prefix followed by the letter `a` and the
ω-obligation `φ` (the step-2/5 wrapper), and
`SAFE(r) = ¬ ⋁_{c ∈ R} ⋁_{a ∈ E(c)} ⟨ψ_{r→c}; a; ⊤⟩`,

```
Final(r)  =  ( SAFE(r) ∧ W(R, r) )  ∨  ⋁_{c ∈ R} ⋁_{a ∈ E(c)} ⟨ ψ_{r→c} ; a ; φ_{c·a} ⟩
```

defines `T_r` exactly. (iii) The scoping is real: `𝒜_R` is a quotient
of `M¹` that collapses, among much else, every class acting emptily on
`R`; DG's price is paid locally. Its separator blindness (§3, (3)) is
also repaired locally: prefer as separator a width-1 partial-constant
letter — an anchor of the failed test — when one exists.

*Proof.* (i) is Proposition 5.21(ii)–(iii) with [DG08]. (ii) `Cay(L)`
being deterministic and complete, a word either exits `R` at a unique
first position, with a unique exit class `c` and letter `a ∈ E(c)` —
its prefix lies in `L_{r→c}`, and no other disjunct can fire: earlier
positions have confined prefixes followed by non-exit letters, later
prefixes are no longer confined — or is confined forever, where
`SAFE(r)` holds (every confined prefix is followed by a non-exit
letter) and every exit disjunct fails. In the first case membership
folds through transport onto the child, `T_{c·a}` by induction; in the
second the contract reads the verdict off `W(R, r)`. Both directions
follow disjunct by disjunct from the uniqueness of that decomposition.
(iii) is Proposition 5.21(ii). ∎

If (B) also fails on `R` at every affordable width, `W(R, r)` is the
window engine's own fallback (§5.5) — the residual stratum, unchanged
and independently entered: the two conditions fail separately, and the
paper's main open problem (an ω-specific descent beating DG there)
remains exactly where §5.5 left it.

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
   Proposition 5.15's normal form). Not an LTL formula, but every downstream
   *computation* (model checking the formula against the automaton,
   equivalence tests) can consume it directly.
2. **Flat LTL** — the standard, and the intrinsically large one: no sharing
   in the syntax, so DAG unfolding multiplies along the R-order antichains.
   Two honest statements about depth. The upper bound is structural: every
   brick of §5.2/§5.7 has fixed modal depth — a constant depending only on
   the widths, four at `k = 1`, `2k + 4` at anchoring width `k` (§5.7),
   `k′ + 2` for a window term — and a child label
   occurs only under `leave(·)`, strictly lower in the R-order; so when all
   layers anchor, flat nesting depth is at most `c(k)·d + c′(k′)` for
   R-depth `d`: linear in the R-depth, the constant owned by the widths.
   The lower bound is the language's: the until-rank read-off
   *lower-bounds* the depth any extraction whatsoever can achieve — so on
   census specimens we certify "the flat explosion is the language's, not
   ours". ⟨TBD: the until-rank lower bound — gated on §2's until-rank
   read-off, itself gated on the Thérien–Wilke source (library request)
   and on the ω-transfer; component C6 of the companion experiment spec
   implements whatever is frozen there; plus the size ledger DG vs. ours
   on the triptych + census.⟩
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
| stem-transcribable, k ≤ K | (A): local k-definiteness mod stutter | graded bricks at width k+1 (Thm 5.23), same depth | step 3 |
| loop-transcribable | (B) at width k′ ⟨TBD: align with local ω-testability⟩ | `GF`/`FG` window combinations | step 4 |
| residual | (A) or (B) fails at every affordable width | genuine nesting; until-rank certifies | steps 3–4 fallback, stem side scoped (Prop 5.24) |

**Table 1.** The inner frontier: which fragment of LTL a language actually
needs, decided on `𝓘(L)` before any formula is built. ⟨TBD: align the
strata with the known sub-LTL hierarchies — definite / locally testable /
TL[F] of Cohen–Perrin–Pin / until hierarchy [Wil99, PW13] — so each row is
a known variety with our operational reading; the census then *maps* the
strata empirically — first data in §8: at 1 AP / ≤ 2 states the residual
row is unwitnessed, and width 2 covers both (A) and (B) everywhere the
tests decide; find the smallest specimen in each lower row (H2/H3/H4 of
the companion spec).⟩

The inner frontier is also the size story of §6 made structural: flat cost
concentrates exactly in the residual stratum, and the strata above it are
the reason extraction on real specimens is small — which DG, treating every
language as residual, cannot see.

## 8. Evaluation

⟨TBD: full section — after implementation. Fixed decisions, so the
section can be written into: corpus = the census of small automata (ground
truth 𝓘 and LTL status already computed) plus the triptych and the paper's
worked specimens; comparisons = (i) flat size and depth: this extraction
vs. the DG baseline; (ii) DAG size vs. |𝒞| — the scaling claim; (iii)
per-layer anchoring statistics — which k fires, how often frozen layers
appear, the inner-frontier map; (iv) the until-rank vs. emitted depth
ledger — optimality gaps. Verdicts checked by
the construction of [SωS26]: every emitted formula's 𝓘 must be byte-equal
to the input's — the equivalence oracle is the object itself.⟩

**First data** (the M1 run of the companion spec; the tables are to be
re-issued under its census reporting discipline — frame declared with its
acceptance family, per-shape rows, counts keyed by distinct canonical
invariant with automata as presentation multiplicity, degenerate stratum
separated — before any figure here is final; first multiplicity soundings
put the distinct languages an order of magnitude below the automaton
counts, with the universal language alone claiming two-fifths of one
shape's answers). The six 1-AP shapes
(one state with zero to three acceptance sets, two states with zero or
one; 981 automata) split 891 aperiodic / 90 not, with no decline, timeout
or crash; every refusal carried a certificate replayed against the input
automaton, `Even`'s and `EvenBlocks`' byte-equal to §4.3's derivations.
On the aperiodic side, 2 898 layers: none anchors at no width, none needs
width 3, the large majority anchor at width 1, and roughly half are
frozen; of 1 921 final-candidate layers none fails (B), and every decided
layer is window-determined at width ≤ 2 (a small UNDECIDED residue awaits
the normative closure of Proposition 5.15(iii)). The residual stratum of
§7 is so far unwitnessed: at one atomic proposition and two states, the
flat-brick ladder covers everything the tests decide. ⟨TBD: final
per-shape tables; the acceptance-family axis (parity corpora); the E4
size ledgers and DAG-vs-|𝒞| scatter once the engine emits; the E7
witness-length ledger and dual-scan (H5) column.⟩

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
