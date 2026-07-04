# Deciding and Constructing LTL over the Syntactic ω-Semigroup

**Claude (Anthropic)** and **Yann Thierry-Mieg**

*Working draft — 2026-07-04*

## Abstract

Given an ω-regular language `L` as a deterministic automaton, two questions are
classically settled in theory and unsettled in practice: *is `L` definable in
linear temporal logic (LTL)?*, and, if so, *produce a defining formula.* The
decision is equivalent to aperiodicity of the syntactic ω-semigroup of `L`
(Thomas; Perrin; Arnold), and the synthesis exists by Diekert and Gastin's
local-divisor induction — but both statements are proofs, not procedures one can
run: neither the canonical algebra nor the synthesis has, to our knowledge, been
materialized. We give a single engine that does both. We compute the syntactic
ω-semigroup explicitly, as the quotient of an *acceptance-enriched monoid*
`EM(D)` read off any deterministic form `D`, by a syntactic congruence that
collapses into two independently checkable halves — pointwise residual equality
and right-invariant acceptance-profile equality — computable with right
multiplications alone, licensed by a short *rotation lemma*. Aperiodicity of the
quotient decides LTL-definability exactly. On the negative side we extract a
**representation-independent, replayable certificate** — a *counting family* of
one of Arnold's two context shapes — that refutes definability by membership
queries alone, trusting nothing about the machine that produced it. On the
positive side we run the Diekert–Gastin synthesis on the materialized quotient,
obtaining a defining LTL formula that is *fragment-complete* (every LTL language
gets one), a *canonical normal form* (same language, same formula, up to fixed
algebraic choices), and *self-certifying* (verified equivalent to the input, it
is the witness the positive verdict otherwise lacks). Both constructions are
presentation-independent: they run on the algebra, which is canonical exactly
where deterministic ω-automata are not. We close with the construction the
engine invites but does not need — a canonical *counter-free* automaton for `L`,
the right-Cayley automaton of the aperiodic quotient — whose one open point is
the acceptance condition.

---

## 1. Introduction

Linear temporal logic is the working specification language of verification, and
"is this ω-regular property expressible in LTL, and if so how?" is a question
practitioners ask constantly and answer heuristically. The theory has been
complete for four decades. Kamp's theorem identifies LTL with first-order logic
over `(ℕ, <)`; the star-free ω-languages are exactly the first-order definable
ones (Thomas [Tho79]; Perrin [Per84]); and, algebraically, a regular ω-language
is star-free if and only if its **syntactic ω-semigroup** is aperiodic — has no
nontrivial group (Perrin; Perrin–Pin [PP04]; the modern survey Diekert–Gastin
[DG08]). The synthesis side is settled too: Diekert and Gastin give a
constructive proof that every aperiodic monoid recognizing a language yields an
LTL formula for it, by induction on *local divisors* [DG08, §8].

Yet neither result is a procedure one runs. The decision is stated over the
syntactic ω-semigroup — the canonical algebra of the language — and **nobody
materializes it** from an automaton; existing complexity arguments (Cho–Huynh
[CH91]; Diekert–Gastin [DG08, Prop. 12.3]) are nondeterministic on-the-fly walks
with astronomical constants, emitting no evidence. The synthesis consumes a
recognizing morphism onto an aperiodic monoid and, to our knowledge, has never
been implemented, precisely because the canonical morphism was never built.

This paper closes both gaps with one engine over one object.

**Contributions.**

1. **A decision procedure with a certificate.** We materialize the syntactic
   ω-semigroup `S(L)₊` as an explicit quotient of an acceptance-enriched monoid
   read off *any* deterministic form of `L`, decide LTL-definability by reading
   aperiodicity off the quotient, and on the negative side hand out a
   **counting family**: a finite, representation-independent object that refutes
   LTL-definability by membership queries against `L`, trusting nothing about our
   computation. We are aware of no prior packaging of non-star-freeness as a
   replayable, presentation-independent witness, on finite or infinite words.

2. **A synthesis that is canonical and self-certifying.** On the positive side we
   run the Diekert–Gastin local-divisor synthesis on the materialized quotient.
   The output is fragment-complete (every LTL language gets a formula, with no
   counter-free-presentation precondition), a **canonical normal form** (equal
   languages produce the identical formula under fixed algebraic choices), and
   self-certifying (verified equivalent, it is the checkable witness the positive
   verdict lacked). We also correct a printed modality in [DG08]'s substitution
   lemma.

3. **One presentation-independent object.** Both constructions run on the
   algebra, not on the automaton. Any two automata for the same language reach
   the *identical* quotient, hence the identical decision and the identical
   formula — a canonicity no automaton-level route can offer, because no minimal
   deterministic ω-automaton exists.

The engine is a decider whose positive answers come with a formula and whose
negative answers come with a refutation; it sits exactly in the seam Boker–
Lehtinen–Sickert [BLS22] leave open — *decide first, then construct* — and
supplies both halves.

---

## 2. Context

**Words and automata.** Fix atomic propositions `AP` and `Σ = 2^AP`. We work over
`Σ^∞ = Σ* ∪ Σ^ω`; the input language `L ⊆ Σ^ω` is the ω-special case. The input
is one deterministic form `D` of `L`, with states `Q`, a total transition
function, and **Emerson–Lei** (generalized `Inf`/`Fin`) acceptance carried as a
set `C` of marks on transitions — the most permissive standard acceptance, of
which Büchi, co-Büchi, Rabin, and Muller are instances. No minimality is assumed;
completion adds at most an absorbing sink.

**ω-semigroups and linked pairs.** An ω-semigroup carries a finite product on
finite words and an infinite product compatible with it [PP04]. By Ramsey's
theorem every `w ∈ Σ^ω` admits a factorization into blocks with, from some point
on, a constant image `e`, so `w` lies in `h⁻¹(s)·(h⁻¹(e))^ω` for a **linked pair**
`(s, e)` — `se = s`, `e² = e` — of the finite part. Linked pairs are the
algebraic addresses of ultimately-periodic words, and two ω-regular languages
coincide iff they agree on ultimately-periodic words, so the acceptance of a
linked pair is the atom every membership question reduces to.

**The syntactic ω-semigroup and the characterization.** The syntactic congruence
of an ω-regular `L` (Arnold [Arn85]) is the coarsest congruence saturating `L`;
its quotient `S(L)` is the canonical algebra of `L`, independent of any
presentation. Arnold shows the congruence separates two finite words by exactly
two context shapes,

```
    linear:   x · _ · y · t^ω          ω-power:   x · (_ · y)^ω
```

The characterization chain we decide against is entirely classical:

```
    LTL-definable  =  FO[<]-definable  =  star-free  =  syntactic ω-semigroup aperiodic
```

*Aperiodic* = group-free: no element has a nontrivial cyclic orbit
`s, s², …, s^{a+p} = s^a` with `p > 1`. A nontrivial group is exactly the ability
to count modulo `p`, which star-free logic cannot express. Because `S(L)` is
presentation-independent, aperiodicity read from it is exact in *both*
directions.

**Counting families (the certificate shape).** A negative answer will be handed
out as one of two shapes, mirroring Arnold's two contexts:

```
    F₁(u, v, x, p) :  n ↦ [ u · vⁿ · x   ∈ L ]      toggles with n mod p
    F₂(u, v, y, p) :  n ↦ [ u · (vⁿ·y)^ω ∈ L ]      toggles with n mod p
```

with `p > 1`, `u, v, y` finite, `x` a lasso. "Toggles with `n mod p`" means the
membership is determined by `n mod p` for *all* `n ≥ 0` and is non-constant.
Every sample is ultimately periodic, hence checkable by a membership query.

*Soundness (either shape ⟹ `L` not LTL), independent of any machine.* Were `L`
star-free, `S(L)` would be aperiodic, so `[vⁿ]` would be eventually constant in
`n`, making membership eventually constant — contradicting a genuine period
`p > 1` holding for all `n`.

*Completeness (two shapes, no third).* Arnold's congruence separates two finite
words by only the linear and ω-power contexts. If `L` is not star-free, some
`[v]` has a period-`p > 1` cycle in `S(L)`; two of its powers are separated by a
context of one of the two shapes, and unrolling that separation along the cycle
yields a toggling family of the corresponding shape. Both shapes are load-bearing:
prefix-independent languages (`σw ∈ L ⟺ w ∈ L`) make every linear family
constant, so `F₂` is a requirement, not an optimization.

---

## 3. Computing the syntactic ω-semigroup

### 3.1 The acceptance-enriched monoid

The algebraic handle on `D` must remember what acceptance reads — the marks
visited *along* a run, not only its endpoints. The **acceptance-enriched monoid**
`EM(D)` assigns to a finite word `w` the map

```
    q  ↦  ( δ(q, w),  the marks collected from q along w ) ,
```

a transformation monoid on `Q × 2^C` generated by the letters, with composition
tracking both the state map and the accumulated marks. Write `EM¹` for the monoid
with the empty-word identity adjoined.

**Skeleton lemma.** Two finite words with the same enriched element are
interchangeable in every ω-context: a run through either lands in the same states
and collects the same marks per start state, so — `D` deterministic — the run
skeleton and acceptance of every surrounding ω-word are identical. Consequently
the syntactic morphism factors through `Σ⁺ → EM(D)`, and the induced map

```
    EM(D)  ─►  S(L)₊
```

is a surjective morphism: `EM(D)` recognizes `L`, and `S(L)₊` is a computable
quotient of it. The enrichment is essential — the plain transition monoid (marks
forgotten) does *not* recognize `L`: two words with equal state maps but different
intermediate marks are separable by an ω-power context. This is why a group in
the transition monoid proves nothing (it may be an encoding artifact), while a
group in the quotient of `EM(D)` proves non-definability.

### 3.2 The congruence, and its collapse

By the skeleton lemma, Arnold's two contexts act on words only through their
enriched elements, so the syntactic congruence is a relation on the finite monoid.
Its virtue is that it **factors into two independently checkable halves**. Write
`st_e`, `mk_e` for the state and mark components of an element `e`, and, for an
idempotent-style "cycle" element `c`, let `A(q, c)` be the Emerson–Lei verdict of
iterating `c` from `q` (walk `st_c` from `q` to the closed cycle, union `mk_c`
around it, evaluate the condition), with profile `Aprof(c) = (q ↦ A(q, c))`. Then

```
    e ~ f     ⟺     e ~lin f      ∧     e ~ω f
    e ~lin f  ⟺     ∀ q ∈ Q :  L(st_e(q)) = L(st_f(q))       (pointwise residual equality)
    e ~ω  f   ⟺     ∀ b ∈ EM¹ :  Aprof(e·b) = Aprof(f·b)      (right-invariant profile equality)
```

- **The linear half** collapses the acceptance of a prefix to the *single* state
  it reaches (a prefix visits its marks finitely often, never touching the
  inf-set). It becomes pointwise residual equality of the state maps — the mark
  parts are irrelevant, and at the initial slot alone it is the classical
  syntactic right congruence of `L` (Maler–Staiger [MS97]). It is computed once,
  on `D`, with no monoid involved. On a prefix-independent language every residual
  is `L` itself and `~lin` is trivially total — the blindness that makes `F₂`
  necessary, now a computational fact.
- **The ω half** is a right-congruence condition seeded by the profile; no left
  translation appears anywhere in it.
- **One pass suffices.** `~lin` is itself right-invariant (derivatives of equal
  languages are equal), so `~` is the coarsest right-invariant refinement of a
  single seed — one Moore-style refinement to fixpoint.

**Theorem.** `EM(D)/~ = S(L)₊`. Hence `L` is LTL-definable iff `EM(D)/~` is
aperiodic, and a group in the quotient is never a presentation artifact — the
quotient *is* the presentation-independent invariant.

**The rotation lemma (why right moves compute a two-sided congruence).** Class
arithmetic below needs `~` two-sided, yet nothing above ever multiplies on the
left. A left factor `a` acts on the seed only by re-indexing the slot: for `~lin`
by determinism (`st_{a·e}(q) = st_e(st_a(q))`), and for `~ω` by conjugacy —
`(a·e·b)^ω` read from `q` equals `a·(e·b·a)^ω`, whose finite `a`-prefix is
invisible past the prefix-collapse, so `Aprof(a·e·b)(q) = Aprof(e·b·a)(st_a(q))`,
a *right* extension read at a shifted slot. Seeds equal under all right extensions
therefore stay equal under every two-sided context. This two-line argument
licenses computing the two-sided syntactic congruence with right multiplications
alone — the one operation a monoid's breadth-first closure table gives for free.

### 3.3 The decision, and a free screen

Materialize `EM¹` by breadth-first closure under a size cap (a blown cap is an
honest *inconclusive*, never a guess), compute residual classes on `Q` and
per-element profiles, refine to `~ = ~lin ∩ ~ω`, and read aperiodicity by
power-iterating each class: the class of `v^{k+1}` is a function of the classes of
`v^k` and `v` (two-sided congruence), so the power sequence is detected by its
first repeated class. Every period 1 ⟹ aperiodic ⟹ **LTL**.

A cheap sufficient screen precedes the quotient: **if the plain transition monoid
of `D` is aperiodic, so is the quotient.** Aperiodicity is inherited upward through
the enrichment — an enriched power `e^n = (f^n, q ↦ ⋃_{i<n} mk_e(f^i(q)))` has, once
the state part `f` stabilizes, a mark part that grows monotonically in a finite
lattice and stabilizes one step later. This is Thomas's counter-free theorem,
here a corollary of the engine's own algebra. The screen is one-directional — a
transition-monoid group may be an encoding artifact — so a group there decides
nothing and the quotient is consulted; the screen only ever accelerates the
positive answer.

### 3.4 Extracting the certificate

A group class `[v]` of period `c > 1` yields a family that cannot fail to
assemble. The classes around the power cycle are pairwise non-congruent, hence
*separated*: two consecutive powers already differ. A **chase** — the
distinguishing-word construction of DFA minimization, run forward over the pair
graph of the right-translation table — produces a shortest word `b` on which the
seeds of `vᵃ·b` and `vᵃ⁺¹·b` diverge, and *where* they diverge names the shape:

- a **residual difference** at slot `q` yields **`F₁`**: one language-inequivalence
  product returns a lasso `w` accepted from exactly one of the two reached states,
  and the `n`-th sample `u·vⁿ·b·w` toggles as `n` rides the cycle;
- a **profile difference** yields **`F₂`**: the `n`-th sample `u·(vⁿ·b)^ω` toggles
  by a pure lookup in the already-computed profile table.

Here `u` is a shortest word from the initial state to `q`. Absorbing the cycle
index into the anchor (`F₁`) or the return word (`F₂`) makes the pattern
`c`-periodic from `n = 0`; the declared period is its minimal cyclic period,
`> 1` because the chased pair differs. The family is then **replayed** by
membership against the *input* — not the discovery form — so not even our own
representation is trusted; a successful replay yields **NOT_LTL** with the family
attached, a failed one degrades to *inconclusive*. A decided answer never rests
on unreplayed material.

### 3.5 Complexity

The dominant object is `|EM(D)| ≤ (|Q|·2^{|C|})^{|Q|}`; the `|Q|` in the exponent
is the explosion, converted by the cap into an honest inconclusive. The explosion
is intrinsic, not an engineering apology: the decision is PSPACE-complete
(Cho–Huynh [CH91] transfer the finite-word hardness from minimal input;
Diekert–Gastin [DG08, Prop. 12.3] give the ω upper bound), so a cap somewhere is a
mathematical necessity. Around materialization the work is polynomial: residual
classes by language-equivalence over `D`; profiles by one functional-graph pass
per element; refinement by Moore's algorithm; the chase and separator on demand,
touching one pair. Every enriched element is a vector of `|Q|` slots over the
small domain `Q × 2^C`, and every operation is a slot-wise right multiplication —
the shape symbolic (decision-diagram) fixpoint methods are built for, an opening
on the `|Q|` exponent that nothing in the construction forbids.

---

## 4. Constructing the formula from the aperiodic quotient

When the quotient is aperiodic, the positive verdict can be made *constructive*:
from `S(L)₊`, synthesize a defining LTL formula by the Diekert–Gastin
local-divisor induction [DG08, §8]. The quotient is exactly the input that
synthesis wants — a recognizing morphism onto a *canonical* aperiodic monoid —
which is why the construction becomes runnable only once the algebra is
materialized.

### 4.1 The internal logic and the recursion

The synthesis works in `LTL[XU]`, pure-future with strict next-until as the only
modality (`φ XU ψ`: at some strictly later position `ψ`, with `φ` strictly in
between; `X`, `U`, `F`, `G` derived). Because the empty word is no model, [DG08]
evaluates through a **prepended-letter device**: `L_{c,A}(φ) = { v : cv, 0 ⊨ φ }`
reads `v` from a phantom anchor before it, dissolving the empty word, the "first
block", and position-0 anchoring as uniform non-cases.

The induction is on `(|monoid|, |alphabet|)`, lexicographic, its contract: given a
morphism onto a finite aperiodic monoid and a language it recognizes (presented by
its finitely many congruence classes — an `ε` flag, a set of finite-word fibers,
and a set of ω-classes), synthesize a defining `LTL[XU]` formula. The root call is
the whole language over `Σ`.

### 4.2 The local divisor and strict decrease

If every letter maps to the identity, the language is a boolean combination of
`{ε}`, `Δ⁺`, `Δ^ω`, each directly definable — the base case, with no per-letter
erasure machinery. Otherwise fix a **pivot** `c` with `h(c) = m ≠ 1`, and form the
**local divisor**

```
    T' = mT ∩ Tm ,      x ◦ y := x m y ,      identity  m .
```

`T'` is a divisor of `T`, hence aperiodic when `T` is; and aperiodicity forces
**strict decrease**: if `m ≠ 1` then `1 ∉ mT ∩ Tm` (else `1 = mx` gives
`mⁿ = mⁿ⁺¹ ⟹ m = 1`), so `|T'| < |T|`. Every visible pivot shrinks the monoid —
this is precisely where aperiodicity, i.e. the LTL verdict, is spent.

### 4.3 Compression, recursion, substitution

Factor each word at its `c`'s, `v = v₀ c v₁ c ⋯` with `c`-free blocks `v_i`.
Compress to the alphabet `T = T₁ ⊎ T₂`, the block images (finite part) and the
congruence classes of `c`-free factors (the **ω-part** being conjugacy classes of
linked pairs, §4.4). A compressed morphism into the strictly-smaller `T'` sends
each interior block through `m·(·)·m`. The language becomes `σ⁻¹(K)` for a
`K ⊆ T^∞` assembled from three regimes — no `c`, finitely many `c`, infinitely
many `c` — each an intersection of a `[XU]`-definable shape guard with a
`T'`-recognized saturation. The saturations recurse on the *smaller divisor*; the
per-block formulas recurse on the *smaller alphabet* (same monoid, one letter
fewer). Crucially, each saturation is a **table**: whether a block sequence lies
in the target depends on the block only through its compressed image, so the
recursion target is computed by pure monoid arithmetic — no search, no witnesses.

The compressed formula is translated back to `Δ` by two exact [DG08]
transformations: **lifting** (`φ ↦ φ^b`, evaluating `φ` on the largest `b`-free
factor from the current position) and **substitution** (`ξ ↦ ξ̃`, mapping the
compressed positions to the `c`-positions of `cv`). We note an **erratum**: the
paper prints a non-strict `U` in the substitution of `XU`, which would admit the
always-`c` anchor as its own witness; the strict `XU` is what transports exactly,
and it is what we use.

### 4.4 The ω-letters: conjugacy classes of linked pairs

The one construction-level piece [DG08] leaves implicit is the finite handling of
the infinite-word classes. The calculus is classical [PP04]: two linked pairs are
**conjugate** when `e = xy`, `e′ = yx`, `s′ = sx` for some `x, y`. Three facts make
this the exact ω-class arithmetic: conjugate pairs denote one word-class; all
pairs of a single word are conjugate and non-conjugate pairs have disjoint pair
languages (so *word ↦ conjugacy class of its Ramsey pairs* is well-defined); and
the union of a conjugacy class's pair languages is exactly one congruence class.
Hence the ω-classes are the conjugacy classes of linked pairs, keyed by a
canonical least member — the presentation the block recursion consumes, and the
guarantee (a *recognized* target, not a single pair language) that makes the
substitution targets legal.

### 4.5 Root, canonicity, self-certification

At the root the prepend device is unwound by partial evaluation at the phantom
position, yielding pure-future LTL over `Σ^ω`. Two properties elevate the output
above "a formula":

- **Canonicity — a normal form.** Fix every choice as a function of the algebra
  alone: re-key classes by their shortlex-least representative word (a language
  invariant, not an artifact of `D`), pin the pivot rule and the linked-pair keys.
  Then *same language ⟹ same formula*, hash-consed to identical structure. Two
  presentations of one language — a group-bearing automaton and a fresh
  translation of the corresponding formula — synthesize the *identical* object.
  No minimization-based route can offer this, because no canonical minimal
  deterministic ω-automaton exists: the algebra is canonical exactly where the
  automata are not.
- **Self-certification.** The formula, verified equivalent to the input, is the
  checkable witness the positive verdict of §3 otherwise lacked — completing the
  symmetry with the negative side's counting family.

The synthesis runs under caps (node count, formula size); a blown cap is a
*decline*, never a wrong formula. Its cost is single-exponential-with-log-factor
in the *quotient* size — the alphabet squares by `T₁ ⊎ T₂` per descent while the
monoid strictly shrinks — measured in the minimum-over-presentations base, and
mitigated natively by hash-consed memoization of the recursion DAG.

### 4.6 Two illustrations

*`GF(a ∧ Xa)` — "infinitely many `aa`".* A two-state presentation can encode the
letter `a` as a transposition, so the transition monoid carries a `Z₂` and the
screen abstains. The quotient does not: ten enriched elements fold to six aperiodic
classes — the parity words the transition monoid keeps apart are Arnold-equivalent
(at infinity, modular counts collapse to thresholds) — and the verdict is a
definitive **LTL**. Synthesis then pivots on the *idle* letter `¬a` (blocks are the
units of counting), discovers via the local divisor that an `aa` never straddles a
`¬a` (single-`a` blocks become invisible), and reassembles `FG a ∨ GF(block with
aa)  ≡  GF(a ∧ Xa)` — the language back from the algebra alone.

*`GFa ∧ FGb` — the mirror.* Here every local divisor is trivial and the whole
construction rides on the ω-class calculus: six ω-classes, two accepting, the
`c`-infinitely-often regime empty because the pivot is a `¬b`-letter and `FGb`
forbids it. The identity class is *fat* — the letter `¬a∧b` maps to it, an
invisible letter that survives into every sub-alphabet and dissolves only at the
all-invisible base — a genuine specimen of the base-case machinery, not a
special case.

---

## 5. Related work

**The characterization we transport.** Thomas [Tho79], Perrin [Per84],
Perrin–Pin [PP04], Arnold [Arn85], and the Diekert–Gastin survey [DG08] establish
`LTL = FO[<] = star-free = aperiodic syntactic ω-semigroup` and the two-context
syntactic congruence. We claim the construction and the certificate, not one inch
of the characterization; every soundness argument bottoms out on one of these
theorems. Diekert–Gastin additionally provide the synthesis [DG08, §8] whose
proof §4 turns into a program.

**The recognizer's ancestry.** Carton–Perrin–Pin [CPP08] give the transition
ω-semigroup as `Q × Q` matrices over `{−∞, 0, 1}` and, in an example, the
syntactic quotient by brute-force saturation over all context *triples*. Our
`EM(D)` is the deterministic Emerson–Lei instance — rows collapse to a function,
the accepting bit upgraded to the exact mark set — and our quotient is the
sharpest contrast: a state relation plus one right refinement (the rotation lemma),
never a left translation, in place of triple saturation.

**Splitting the congruence.** Maler–Staiger [MS97] define the syntactic right
congruence — our `~lin` at the initial state — and display Arnold's congruence as
finitary × infinitary; they compute no state collapse, profiles, refinement, or
aperiodicity application. Preugschat–Wilke [PW13] realize the same
finitary × infinitary split *co-deterministically*, on a prophetic (Carton–Michel)
automaton where right-invariance is free, but only for the simple fragments — the
`{U}` case taking LTL-definability as a precondition and citing [DG08] to decide
it. The full-LTL border is their *input* and our *output*; our forward route earns
right-invariance (rotation lemma) where co-determinism hands it to them, and their
loop-language automata are the natural independent cross-check of `~ω`.

**Right congruences as representations.** The FDFA line (Klarlund; Angluin–Fisman
[AF16, AF21]; Angluin–Boker–Fisman [ABF18]) is the machine model of Maler–
Staiger's families of right congruences, structurally our residuals + profiles.
Angluin–Fisman document from that side why the plain right congruence cannot see
LTL-ness — LTL languages with a trivial right congruence exist — which is our
prefix-independent blindness, repaired by the profile half. The line stops at
representation, canonicity, and learning; none of it decides definability, and its
canonical FDFAs are learning targets, never computed from an automaton. The
quotient's data is a syntactic FDFA in all but serialization — a cheap exportable
by-product.

**Complexity and the converse.** Cho–Huynh [CH91] give finite-word aperiodicity
PSPACE-complete from minimal input; Diekert–Gastin [DG08, Prop. 12.3] the ω upper
bound — a nondeterministic on-the-fly walk, no certificate, not via Arnold's
congruence. The oracle is its deterministic, certificate-producing counterpart.
Boker–Lehtinen–Sickert [BLS22] give the converse map (counter-free deterministic
automaton → LTL, with elementary bounds) but assume aperiodicity and decide
nothing: the seam *decide, then construct* is exactly what this engine fills.

**Certification and tools.** Following the certifying-algorithms discipline
[MMNS11], the engine is *negative-side certifying*: every NOT_LTL carries a
replayable, **language-level** witness — checkable against any presentation of `L`
— where the classical evidence (a forbidden cycle in the minimal DFA, a
finite-order element in a group `H`-class) is representation-bound and meaningless
without trusting the construction under audit. No published packaging of
non-star-freeness as a replayable, representation-independent certificate is known
to us. On tools: AMoRE decided the finite-word analog three decades ago with no
ω successor; Spot classifies by the Manna–Pnueli hierarchy and stutter-invariance
(neither necessary nor sufficient for LTL); Owl translates and synthesizes; ROLL
learns FDFAs; none decides LTL-definability of an ω-automaton.

---

## 6. Discussion: the canonical algebra as a hub

Materializing the syntactic ω-semigroup is worth more than the two verdicts it was
built for; the same tables are a hub other constructions plug into.

- **A language-identity hash.** The canonically-keyed presentation — classes keyed
  by shortlex-least representative, the multiplication table, the letter map, and
  the accepting ω-classes — is a *complete language invariant*: two ω-regular
  languages over the same `AP` are equal iff these tables coincide. Hashing them
  turns language equality into hash equality, with no aperiodicity assumption (it
  covers all ω-regular languages), whose sweet spot is many-to-many identity —
  bucketing a corpus by true language — where pairwise equivalence checks are
  quadratic.

- **A canonical counter-free automaton (the construction this invites).** The
  quotient can be reified as an automaton: the **right-Cayley automaton** of
  `S(L)₊¹` — states are classes, transitions are right multiplication by the letter
  classes. Its transition monoid is the right-regular representation of the
  quotient, faithful, hence **aperiodic exactly when the verdict is LTL** — a
  *canonical counter-free presentation* of the language, built forward and
  deterministically, of any LTL input. This is the forward mirror of the
  co-deterministic prophetic form and it settles, for the transition structure,
  the object that no minimal deterministic ω-automaton provides: a counter-free
  deterministic form always exists and is constructible from the algebra we already
  build. On it, every construction that assumes counter-freeness — the
  Krohn–Rhodes cascade of [BLS22] among them — can be re-run on inputs it declined
  in group-bearing form. Its one open point is the **acceptance condition**:
  whether an Emerson–Lei/Muller table on the Cayley transitions, filled from the
  profiles via the linked pairs, is well-defined from the infinity set of states
  alone. Maler–Staiger [MS97] is the entry point, and the residual quotient alone
  is provably too coarse — a definitive experiment being that the residual quotient
  of a two-state parity form of `GF(a ∧ Xa)` is a single state. We flag this as the
  natural sequel: a forward, constructible companion to the co-deterministic
  counter-free canonical form.

---

## 7. Conclusion

The two questions — *is it LTL?* and *what is the formula?* — meet on one object,
the syntactic ω-semigroup, which we materialize as an explicit quotient of an
acceptance-enriched monoid and read both answers from. The decision is exact and,
on the negative side, certified by a representation-independent counting family
that trusts nothing about our computation. The synthesis is the first runnable
rendering of the Diekert–Gastin local-divisor induction, and it returns not merely
a formula but a canonical, self-certifying one. Everything is presentation-
independent: the algebra is the invariant, canonical precisely where deterministic
ω-automata are not. The same algebra is a hub — a language-identity hash, and a
forward counter-free canonical automaton — and it is on that last construction, and
its one open acceptance lemma, that the sequel turns.

---

## References

- **[Arn85]** A. Arnold. *A syntactic congruence for rational ω-languages.* TCS
  39 (1985) 333–335.
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
- **[CH91]** S. Cho, D. T. Huynh. *Finite-automaton aperiodicity is
  PSPACE-complete.* TCS 88 (1991) 99–116.
- **[DG08]** V. Diekert, P. Gastin. *First-order definable languages.* In *Logic and
  Automata*, 2008. (§5 recognition, §7 `LTL[XU]`, §8 local-divisor synthesis;
  Prop. 12.3 complexity.)
- **[MS97]** O. Maler, L. Staiger. *On syntactic congruences for ω-languages.* TCS
  183 (1997) 93–112 (rev. 2008).
- **[MMNS11]** R. McConnell, K. Mehlhorn, S. Näher, P. Schweitzer. *Certifying
  algorithms.* Computer Science Review 5(2) 2011.
- **[Per84]** D. Perrin. *Recent results on automata and infinite words.* MFCS 1984.
- **[PP04]** D. Perrin, J.-É. Pin. *Infinite Words: Automata, Semigroups, Logic and
  Games.* Elsevier, 2004.
- **[PW13]** S. Preugschat, T. Wilke. *Effective Characterizations of Simple
  Fragments of Temporal Logic Using Carton–Michel Automata.* LMCS 9(2:08) 2013.
- **[Tho79]** W. Thomas. *Star-free regular sets of ω-sequences.* Information and
  Control 42 (1979) 148–156.
