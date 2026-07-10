# Measure, Distance, and Entropy on the Syntactic ω-Semigroup

**Yann Thierry-Mieg**

With significant inputs from
**Claude (Anthropic)**

*Working draft — 2026-07-10. Structure complete; §3 at full rigor; §6
carries ⟨TBD⟩ slots to be filled from `sos_measure_report.md`.*

## Abstract

The syntactic ω-semigroup of an ω-regular language `L`, reified as the
invariant `𝓘(L) = (𝒞, λ, M, P)`, is by now a computational substrate: the
qualitative toolbox — Boolean operations, decision procedures,
classification — runs on it as surgeries and scans, canonical and
certificate-bearing. This paper adds numbers. The technical heart is a
**generic-verdict theorem**: under any Bernoulli measure with full support
(more generally, along any finite-state Markov source), almost every word
is absorbed into a bottom strongly connected component of the invariant's
right-Cayley graph, and its membership verdict is a single canonical bit
per component — read off by *one* table lookup at an idempotent of the
kernel of the transition semigroup. The proof is two moves on the held
object: a doubled-word cut that factors almost every word over a kernel
idempotent `k`, and a conjugacy argument showing the achievable stems form
a single orbit of the finite group `H(k)`, on which the verdict is
constant. Everything quantitative follows as read-offs. The measure
`μ_p(L)` is one linear system over the rationals — `O(n³)` exact
arithmetic, rationality included, certificate the θ-labeled component map.
The probability that a finite Markov chain satisfies `L` is the same
computation on a product chain: the classical probabilistic-verification
algorithm with the deterministic automaton replaced by the canonical
algebra, normal-formed and shared across a whole verification campaign.
On an aligned table, measure turns the free `xor` into a computable
pseudometric whose null pairs are exactly characterized. Topological
entropy is one Perron eigenvalue over the live classes, and the entropy of
a language provably equals that of its safety closure. Each quantity
becomes a census column, and the census of small ω-regular languages
becomes a measured metric space. ⟨TBD: one-sentence headline number from
the census campaign.⟩

## 1. Introduction

Three quantities attach to an ω-regular language `L ⊆ Σ^ω` beyond its
membership relation. Its **measure**: fix a Bernoulli measure `p` on `Σ`
(letters drawn i.i.d.; uniform as default) — what is the probability
`μ_p(L)` that a random word belongs to `L`? Its **distance** to another
language: how much probability mass sits in the symmetric difference
`L₁ Δ L₂`? Its **entropy**: at what exponential rate does the number of
finite prefixes of `L` grow — how fast does the language branch? The
**syntactic ω-semigroup** is the canonical finite algebra Arnold's
congruence assigns to `L`, held as the exportable invariant
`𝓘(L) = (𝒞, λ, M, P)`: a keyed class set, a letter map, a multiplication
table, and the accepting linked pairs [SωS26]. It determines `L` exactly,
and the qualitative calculus [SωSC26] operates the everyday toolbox on it:
complement is a bit-flip, equivalence a byte comparison, classification a
scan.

The quantitative questions matter for three reasons. First, they are the
missing half of the substrate thesis. If the invariant is to replace
automata as *the* held form of a specification, it must answer what
probabilistic model checkers answer: the flagship query of that world —
the probability that a finite-state Markov chain satisfies a linear-time
specification [CY95] — is answered today by product constructions against
a deterministic (or determinized) automaton, an object that is neither
canonical nor stable under the pipeline's rewrites. Second, quantities
compose with the calculus's economy: on one aligned table, the measure of
any Boolean combination of two held languages is available at no further
alignment cost, so regression after a rewrite can report not just
*whether* the language moved (byte comparison) but *how much* (a
distance) — and a census of languages becomes a metric space with
computable geometry. Third, there is a structural payoff independent of
any application: probability *localizes* in the algebra. Almost sure
behavior is kernel behavior — the minimal ideal of the transition
semigroup decides the verdict of almost every word, the transient
structure carries only the arithmetic — and this refines, quantitatively,
the qualitative picture in which the same bottom components carry the
safety hull and the obligation band.

Contributions:

1. **The generic-verdict theorem** (§3): for a.e. word absorbed into a
   bottom SCC `C` of the right-Cayley graph, the membership verdict is a
   constant `θ_C`, computed by one `Val` lookup at any idempotent of the
   kernel; the constant is independent of the entry class, of the chosen
   kernel idempotent, and of the (full-support) measure. The proof —
   a doubled-word factorization and an `H(k)`-orbit conjugacy argument —
   uses only the conjugacy law and classical structure theory of finite
   semigroups. The theorem relativizes to any product with a finite
   Markov chain, the kernel taken in the cycle semigroup of the absorbing
   component (§3.5).
2. **The measure read-off** (§4): `μ_p(L)` is one linear system on the
   held object — polynomially many exact rational operations — with
   rationality as a corollary rather than an import; the **θ-profile**
   (the per-component bit vector) is a new, measure-free canonical
   invariant of `L`, deciding in particular whether `μ_p(L)` is `0`, `1`,
   or strictly between, uniformly over all full-support `p`.
3. **Probabilistic model checking on the canonical spec object** (§4.3):
   `Pr_M(L)` for a labeled Markov chain `M` by the same theorem on the
   product chain — the algorithm of Courcoubetis–Yannakakis [CY95] with
   the automaton replaced by the invariant, inheriting the calculus's
   canonicity dividend (normal form, byte-comparable, one spec object per
   campaign); stationary Markov letter sources subsume the Bernoulli case
   at no extra cost.
4. **Distance and entropy as read-offs** (§4.2, §5): on an aligned table,
   `d_p(L₁, L₂) = μ_p(L₁ Δ L₂)` is computable exactly, is a pseudometric
   whose null pairs are characterized by an all-zero θ-profile of the
   aligned `xor`; topological entropy is `log ρ` of the letter-count
   matrix restricted to the live classes — one Perron eigenvalue on top
   of the calculus's liveness scan — with `h(cl(L)) = h(L)` as a
   structural corollary.
5. **The census as a measured metric space** (§6): measure, θ-profile,
   entropy, and sampled distance geometry as columns of the census of
   small ω-regular languages, under the reproducibility discipline of the
   prior campaigns. ⟨TBD: findings.⟩

§2 recalls the objects and the classical facts we build on. §3 proves the
generic-verdict theorem. §4 derives measure, distance, and the Markov
product. §5 handles entropy. §6 reports the campaign. §7 positions the
work; §8 concludes.

## 2. Background

Nothing in this section is new to this paper; we fix notation and quote
what the proofs consume.

### 2.1 The invariant and its membership oracle

`Σ` is a finite alphabet, `L ⊆ Σ^ω` ω-regular,
`𝓘(L) = (𝒞, λ, M, P)` its syntactic invariant as in [SωS26]: classes `𝒞`
(`n = |𝒞|`, fresh identity `[ε]` adjoined), letter map `λ`, multiplication
table `M`, accepting linked pairs `P`. `S := fold(Σ⁺) ⊆ 𝒞` denotes the
image semigroup, `fold` the evaluation of finite words, `idem(d)` the
unique idempotent power of `d`, and the membership oracle is
`Val_P(c, d) := (M(c, idem(d)), idem(d)) ∈ P`, with
`u·v^ω ∈ L ⟺ Val_P(fold(u), fold(v))`. We use the **strong factoring
theorem** throughout [SωS26; PP04]: for any ω-word `α` and any
factorization `α = w₀·w₁·w₂⋯` whose blocks `w_{j≥1}` all fold to one
idempotent `e`, membership is decided by the associated pair,
`α ∈ L ⟺ (fold(w₀)·e, e) ∈ P`. We also use the **conjugacy law**
[SωSC26, Prop 3.1]: for a linked pair `(s, e)` and any factorization
`e = x·y` (`x, y ∈ S`), the cells `(s, e)` and `(s·x, y·x)` carry one
verdict, the conjugate renormalizing to the linked pair
`((s·x)·f, f)`, `f = (y·x)^π`.

**The right-Cayley graph** of the invariant has vertex set `𝒞` and edges
`c → c·λ(a)` for `a ∈ Σ`: a complete deterministic automaton with initial
state `[ε]`, canonical because the invariant is. Its SCCs are exactly the
`R`-classes of `𝒞` (mutual right-divisibility), and a *bottom* SCC `C` is
a closed `R`-class: `c·S ⊆ C` for every `c ∈ C` [SωSC26, §3.6].

### 2.2 Finite semigroups: kernel and maximal groups

Every finite semigroup `S` has a unique minimal two-sided ideal, the
**kernel** `K`, which is completely simple; for every idempotent
`k ∈ K`, the set `H(k) = k·S·k = k·K·k` is a finite group with identity
`k` (Suschkewitsch; see [PP04]). We freely use `k·t·k ∈ H(k)` for
`t ∈ S¹` and the existence, for any `t ∈ K`, of the idempotent
`t^π ∈ K`.

### 2.3 Measures on `Σ^ω` and the probabilistic verification problem

Equip `Σ^ω` with the Borel σ-field generated by the cylinders `w·Σ^ω`. A
**Bernoulli measure** `p` assigns i.i.d. letters,
`μ_p(w·Σ^ω) = Π p(w_i)`; it has *full support* if `p(a) > 0` for all
`a`. A **labeled Markov chain** `M` is a finite-state chain whose
transitions emit letters (every present transition with positive
probability); a run of `M` emits an ω-word, and `Pr_M(L)` is the
probability that the emitted word lies in `L`. Both `μ_p(L)` (a
one-state chain) and `Pr_M(L)` are measurable for ω-regular `L`, and
computable in polynomial time from a *deterministic* ω-automaton for `L`
by the classical recipe — product with the chain, classification of the
bottom SCCs of the product, one linear system for the absorption
probabilities [CY95, §4.1]. Our §3–§4 re-derive this pipeline with the
canonical algebra in the spec-side seat; no probability theory beyond
Borel–Cantelli and finite Markov chain absorption is needed.

### 2.4 Entropy of an ω-language

The **topological entropy** of `L` is the exponential growth rate of its
prefix set: `h(L) := limsup_n (1/n)·log₂ |pref_n(L)|`, where `pref_n(L)`
is the set of length-`n` finite prefixes of members of `L`. This is
Staiger's entropy of an ω-language — defined through the structure
function of the prefix language [Sta93, Eq. (2.3) and p. 168:
`H_F := H_{A(F)}`], itself the classical entropy of symbolic dynamics
read on prefix sets rather than block sets [LM95, Def. 4.1.1]. Two
classical facts we will meet again: for shift spaces presented by
graphs, entropy is the log of the Perron eigenvalue of the adjacency
matrix [LM95, Thm 4.3.1, Thm 4.3.3, and §4.4 for the reducible case];
and the entropy of an ω-language equals that of its topological closure
[Sta93, p. 168]. (Staiger normalizes `log` to base `|Σ|`; we keep
base 2.) We prove what we use in §5, on our own object.

## 3. The generic-verdict theorem

Throughout, `p` is a full-support Bernoulli measure on `Σ`. A random word
`α` walks the right-Cayley graph; since the graph is finite and complete,
`α` almost surely reaches a state from which only one bottom SCC is
reachable and enters it — we say `α` is **absorbed** in the bottom SCC
`C`, **entering at** `c ∈ C` (the first class of the walk lying in `C`).
The entry time is a stopping time, so the tail after entry is again an
i.i.d. word. Fix once and for all the kernel `K` of `S` and an idempotent
`k ∈ K`; fix a word `w ∈ Σ⁺` with `fold(w) = k` (take any `w₀` with
`fold(w₀) ∈ K` — a representative of any kernel class — and raise it to
its idempotent power).

For `c ∈ 𝒞` and idempotent `k`, write
`Stems(c, k) := c·S¹·k = { c·t·k : t ∈ S¹ }` — the **achievable stems**.
Every `s ∈ Stems(c, k)` satisfies `s·k = s`, so `(s, k)` is a linked pair
and `Val(s, k) = ((s, k) ∈ P)`.

### 3.1 Almost every word factors over a kernel idempotent

**Lemma 3.1 (doubled-word cut).** For a.e. `α` absorbed in `C` entering
at `c`, there is a factorization `α = y·z₁·z₂⋯` with `fold(z_i) = k` for
all `i` and `fold(y) ∈ Stems(c, k)`; consequently
`α ∈ L ⟺ Val(fold(y), k)`.

*Proof.* Partition the tail after entry into consecutive blocks of length
`2|w|`; each equals `w·w` with probability `p(w)² > 0`, independently, so
by Borel–Cantelli the tail a.s. contains infinitely many disjoint
occurrences of `w·w`. Cut at the *midpoints* of these occurrences. Every
inter-cut block starts and ends with a full `w`, hence folds into
`k·S¹·k = H(k)` — a finite group (§2.2); this is the point of doubling
`w` (a block guaranteed to *end* with `w` folds only into `S¹·k`, where
no group structure is available). The cumulative products of the block
folds live in `H(k)` and take finitely many values, so some value recurs
along an infinite set `J` of cut points; between consecutive `J`-cuts the
blocks multiply to `π^{-1}·π = k` — *exactly* the identity, by group
inverses. Take the `z_i` to be the inter-`J`-cut blocks and `y` the
prefix of `α` up to the first `J`-cut: `y` ends with a full `w`, so
`fold(y) = c'·k` for some `c' ∈ c·S¹` ... more precisely
`fold(y) = c·(fold of the tail prefix)` ends in `k`, so
`fold(y) ∈ c·S¹·k`. The strong factoring theorem (§2.1) gives
`α ∈ L ⟺ (fold(y)·k, k) ∈ P = Val(fold(y), k)`. ∎

### 3.2 The achievable stems form one `H(k)`-orbit

**Lemma 3.2 (stem invariance).** Let `C` be a closed `R`-class,
`c ∈ C`, `k ∈ K` idempotent. Then `Val(·, k)` is constant on
`Stems(c, k)`.

*Proof.* Let `s₁, s₂ ∈ Stems(c, k)`. Closedness puts both in `C`, so
`s₁ R s₂` and `s₂ = s₁·u` for some `u ∈ S¹` (if `u = 1` there is nothing
to prove). Since `s₁·k = s₁` and `s₂·k = s₂`:

```
s₂ = s₁·u·k = s₁·k·u·k = s₁·m,        m := k·u·k ∈ H(k).
```

Factor the loop as `k = m·m^{-1}` — the identity of the group `H(k)` —
and apply the conjugacy law (§2.1) to the linked pair `(s₁, k)`: the
cells `(s₁, k)` and `(s₁·m, m^{-1}·m) = (s₂, k)` carry one verdict, the
renormalization being trivial because `m^{-1}·m = k` is already
idempotent. ∎

The mechanism deserves one line of intuition: `s₁·k^ω` and
`(s₁·m)·k^ω` are *the same ω-word class* — a phase inside the kernel
group is invisible at infinity. This is exactly where the argument
evades the standard obstruction that `R` is not a right congruence: the
multiplier connecting two achievable stems can always be *chosen inside*
`H(k)`, and there conjugacy cancels it.

### 3.3 The bit is canonical

**Lemma 3.3.** The common value of Lemma 3.2 depends neither on the
entry class within `C` nor on the choice of `k`:

1. for `c, c' ∈ C`: `Stems(c', k) ⊆ Stems(c, k)` whenever `c' ∈ c·S¹`,
   and both sets carry a constant `Val(·, k)` — so the constants agree;
2. for idempotents `k, k' ∈ K`, set `g := k·k'·k ∈ H(k)` and let
   `g^{-1}` be its group inverse. With `x := g^{-1}·k'` and `y := k'·k`:
   `x·y = g^{-1}·(k·k'·k) = g^{-1}·g = k` (using `g^{-1}·k = g^{-1}`),
   while `y·x = k'·g^{-1}·k' ∈ H(k')` has idempotent power `k'`. The
   conjugacy law transports the cell `(c·k, k)` to a cell with loop `k'`
   and stem `c·g^{-1}·k' ∈ Stems(c, k')`, where Lemma 3.2 applies. ∎

**Definition.** For a bottom SCC `C` of the right-Cayley graph, the
**generic verdict** of `C` is

```
θ_C := Val(c, k)          any c ∈ C, any idempotent k ∈ K
```

— one table lookup (`Val(c, k) = ((c·k, k) ∈ P)`, and `c·k` is itself an
achievable stem).

### 3.4 The theorem

**Theorem 3.4 (generic verdict).** For a.e. `α` (any full-support
Bernoulli `p`): `1_{α ∈ L} = θ_C`, where `C` is the bottom SCC absorbing
`α`'s walk. Consequently

```
μ_p(L) = Σ_C θ_C · Pr[absorption in C],
```

and the absorption probabilities solve the standard transient system
`x_c = Σ_a p(a)·x_{c·λ(a)}` with boundary `x_c = θ_C` on bottom SCCs:
`μ_p(L) = x_{[ε]}`, a system of at most `n` rational linear equations.

*Proof.* Lemmas 3.1–3.3: a.e. absorbed word has its verdict computed at
a cell `(s, k)` with `s ∈ Stems(c, k)`, where `Val` is the constant
`θ_C`. The decomposition of `μ_p(L)` over the (a.s. exhaustive,
disjoint) absorption events and the linear system for absorption
probabilities are classical finite-chain facts. ∎

Two corollaries are worth displaying. **Rationality**: `μ_p(L) ∈ ℚ` for
rational `p`, by Gaussian elimination — re-proved rather than imported.
**Measure-freeness of the profile**: the bit vector `(θ_C)` over bottom
SCCs — the **θ-profile** of `L` — is computed without any reference to
`p`; since every full-support `p` charges every bottom SCC positively,
whether `μ_p(L)` is `0`, `1`, or strictly interior is the same for all
full-support `p`, decided by the profile being all-`0`, all-`1`, or
mixed.

### 3.5 The product form: Markov chains and Markov sources

Theorem 3.4 relativizes to the product with a finite labeled Markov
chain `M`; the only change is *where the kernel is taken* — the tail
alphabet is now constrained to the cycles of the absorbing component.

**Theorem 3.5.** Let `M` be a finite labeled Markov chain, and form the
product chain on the reachable part of `states(M) × 𝒞` (the chain moves
by `M`, the second coordinate folds the emitted letter). For a bottom
SCC `B` of the product, fix a base point `(q̂, ĉ) ∈ B`, let
`T := { fold(z) : z reads a cycle q̂ → q̂ inside B }` — a subsemigroup of
`S` — and let `k` be an idempotent in the kernel of `T`, realized by a
cycle word `w` at `q̂`. Then for a.e. run absorbed in `B`, the emitted
word's verdict is the constant `θ_B := Val(c, k)` (any `(q̂, c) ∈ B`),
and `Pr_M(L) = Σ_B θ_B · Pr[absorption in B]`, one linear system on the
product chain.

*Proof sketch (the Bernoulli proof relativizes).* A.e. run absorbed in
`B` visits `q̂` infinitely often, and at successive visits reads the
doubled cycle word `w·w` infinitely often (conditional Borel–Cantelli:
each visit gives an independent positive-probability trial). Mid-cutting
those occurrences yields blocks `w·x·w` with `x` a `B`-internal cycle
word at `q̂`, folding into `k·T¹·k = H_T(k)` — a group, since `k` lies in
the kernel *of `T`* — and the pigeonhole of Lemma 3.1 again produces
loop blocks folding exactly to `k`. Achievable stems again form one
`H_T(k)`-orbit: for stems based at an entry `(q₀, c₀) ∈ B`, strong
connectivity of `B` provides a return path to `(q₀, c₀)` from any
mid-cut configuration, and the composition of that return with the next
stem's path is a cycle at `q̂`, so two stems differ by
`k·(element of T)·k ∈ H_T(k)`, and Lemma 3.2's conjugacy applies
verbatim. Constancy across entry points as in Lemma 3.3(1) (strong
connectivity nests the stem sets); independence of `q̂` and `k` because
two full-measure readings of the same event agree. ∎

Two consequences. `Pr_M(L)` — the flagship query of probabilistic model
checking [CY95] — is computable with the *canonical* object on the spec
side: polynomial in `|M|·n`, exact rational arithmetic, the spec held
once per campaign, byte-comparable across rewrites, every verdict
certificate-bearing (the θ-labeled product-component map). And a
**stationary Markov letter source** is just such an `M`, so the measure
of `L` under Markov (not merely Bernoulli) sources is the same read-off;
Theorem 3.4 is the one-state case.

## 4. Measure and distance read-offs

### 4.1 The algorithm

On the held invariant, computing `μ_p(L)`:

1. SCC pass on the right-Cayley graph, `O(n·|Σ|)` (shared with the
   calculus's hull/obligation scans); identify bottom SCCs.
2. Kernel idempotent: the two-sided Cayley graph (edges
   `c → λ(a)·c` and `c → c·λ(a)`) has a unique bottom SCC, the kernel
   `K`; take any `t ∈ K` and `k := idem(t)`. `O(n·|Σ|)`.
3. `θ_C := Val(c, k)` for one representative `c` per bottom SCC —
   `O(1)` lookups each.
4. Solve the transient linear system over `ℚ`; `μ_p(L) = x_{[ε]}`.
   Polynomially many arithmetic operations on rationals of polynomial
   bit size (fraction-free Gaussian elimination).

The certificate is the θ-labeled bottom-SCC map plus the linear system
itself; a checker replays steps 3–4 independently of steps 1–2.

### 4.2 Distance on an aligned table

For `L₁, L₂` held on one aligned table [SωSC26, §3.3], the pair set of
`L₁ Δ L₂` is the free surgery `P₁ xor P₂`, and

```
d_p(L₁, L₂) := μ_p(L₁ Δ L₂)
```

is computable by §4.1 on the same table. `d_p` is a **pseudometric**
(symmetry and triangle inequality from measure additivity), not a
metric: ω-regular null sets exist, and `d_p(L₁, L₂) = 0` iff the
θ-profile of the aligned `xor` is all-zero — a decidable, `p`-free
characterization of "the disagreement is measure-null". That is a
feature, not a defect: exact separation remains the byte comparison of
the reduced invariants, while `d_p` measures the *mass* of the
disagreement, and the two verdicts together distinguish "different but
almost surely agreeing" from "different where it counts". Uses:
quantitative regression after a rewrite (the byte test says *whether*
the language moved, `d_p` says *how much*); nearest-neighbor queries in
the census ("the closest LTL-definable language to this non-LTL one" is
a scan); weighting of counterexamples (the minimal witness of
[SωSC26, Prop 3.2] is the *shortest* disagreement, `d_p` its mass).

### 4.3 The verification pipeline

The applied shape of Theorem 3.5: a specification held once as `𝓘(L)`,
checked against a family of chains `M₁, M₂, …` — one product and one
linear system each, the spec side never re-translated, re-determinized,
or re-simplified; qualitative queries (emptiness of the product support,
witness lassos) and the quantitative `Pr_{M_i}(L)` read off the same
product. ⟨TBD: the worked pipeline from the report — a spec, a family of
chains, wall-clock and canonicity dividends against the automata-side
baseline.⟩ Markov decision processes stay out of scope: optimization
over schedulers is a branching problem, the same wall the qualitative
calculus refuses.

## 5. Entropy

**Proposition 5.1.** Let `Live ⊆ 𝒞` be the live classes (nonempty
residual — the `O(n²)` scan of [SωSC26, §3.6]), and `A` the
`Live × Live` letter-count matrix `A[c][c'] = |{a : c·λ(a) = c'}|`.
For nonempty `L`: `h(L) = log₂ ρ(A)`, the Perron eigenvalue of `A`.
Moreover `h(cl(L)) = h(L)` for the safety closure `cl(L)`.

*Proof.* `pref(L) = { u : fold(u) ∈ Live }`: liveness is a class
property, and a finite word is a prefix of a member iff its class has a
nonempty residual. Liveness propagates to prefixes, so every state on a
path from `[ε]` to a live state is itself live: `|pref_n(L)|` is exactly
the number of length-`n` paths from `[ε]` staying inside `Live` (note
`[ε] ∈ Live` iff `L ≠ ∅`). The growth rate of the number of such paths
is `log₂ ρ(A)` by Perron–Frobenius on the nonnegative matrix `A`. For
the closure: `cl(L)` is the set of words all of whose prefixes are live
[SωSC26, Prop 3.5], so `pref(cl(L)) = pref(L)` — a live word extends to
a member of `cl(L)` by König's lemma — and the two entropies are growth
rates of one prefix set. ∎

The closure identity is classical — Staiger derives `H_F = H_{cl(F)}`
directly from `A(cl(F)) = A(F)` [Sta93, p. 168] — and our proof is the
same identity read on the invariant; what the proposition adds is the
*read-off*: `pref(L)` is recognized by the right-Cayley DFA with
accepting set `Live`, so the entropy rides the same `O(n²)` liveness
scan that already computes the safety hull, with no pruning or
co-reachability analysis (co-reachability to `Live` *is* `Live`).

Conventions and refinements: `h(∅) := 0` (Staiger's convention
[Sta93, Eq. (2.3)]; [LM95] uses `−∞` — empty `Live` either way);
`h(L) ≤ log₂|Σ|` always, with equality iff `Live` supports the full
branching; entropy is monotone under inclusion (prefix sets nest) —
a metamorphic law for the harness; on an aligned table the *relative*
entropy of `L₁` inside `L₂` (growth of `pref(L₁ ∩ L₂)` against
`pref(L₂)`) is the same computation on the product's live part. Unlike
§3–§4, the eigenvalue is algebraic rather than rational; the read-off
reports a certified enclosure, and the *certificate* is the `Live`
submatrix itself. ⟨TBD: census distribution of entropies per Wagner
degree — do higher degrees concentrate at full entropy?⟩

## 6. The census as a measured metric space

⟨TBD — this section is fed by `sos_measure_report.md`; the paper cites
no artifact directly. Planned content: (i) measure and θ-profile columns
over the census, distribution per Wagner degree and per
safety-progress band; (ii) the conjectured concentration of measure-0/1
in the safety/co-safety rungs, tested; (iii) entropy distribution per
degree; (iv) sampled distance geometry — diameter, clustering by degree,
nearest-LTL-neighbor for the non-LTL languages; (v) the pipeline
demonstration of §4.3 with its baseline comparison.⟩

## 7. Related work

**Probabilistic verification.** The measure of an ω-regular property
against a Markov chain is classical: Vardi [Var85] posed the problem and
solved qualitative ("probability 1") verification by the
automata-theoretic route; Courcoubetis–Yannakakis [CY95] settled the
complexity of both qualitative and quantitative verification, with the
recipe §2.3 recalls — product with a deterministic automaton,
recurrent-class analysis, linear system (their §4.1). The textbook
consolidation is [BK08, Ch. 10: the product of a Markov chain with a
deterministic Rabin automaton, accepting-BSCC analysis], and the
industrial embodiment PRISM ⟨Kwiatkowska–Norman–Parker 2011,
*PRISM 4.0*, CAV — pending library⟩. Our Theorem 3.5 changes none of the
asymptotics and does not intend to: the contribution is *which object
sits on the spec side* — canonical, normal-formed after every surgery,
byte-comparable, shared across a campaign — and the generic-verdict
theorem showing the canonical object suffices, deterministically, with
certificates. Measure-1 satisfaction as a notion of correctness
("fairly correct systems") is studied in [VV06]; the θ-profile gives
that notion a canonical carrier (all-1 profile ⟺ fairly correct under
every full-support noise model).

**Measure and entropy of ω-languages.** The entropy machinery is
symbolic dynamics: block-growth entropy and its Perron-eigenvalue
computation for graph and sofic presentations are [LM95, Ch. 4]; the
prefix-set entropy of ω-languages, its finite-state theory, and the
closure identity `H_F = H_{cl(F)}` are Staiger's [Sta93, §2] (his 1985
entropy paper being unobtainable to us, [Sta93] is our citable carrier
of that line). Rationality of `μ_p(L)` we re-derive (§3.4), with [CY95]
as the classical carrier. Our §5 is thus a transposition of classical
facts onto the canonical object; the new content is the identification
`pref(L) = Live` — entropy as a one-eigenvalue read-off over the same
class set the calculus's hull theory already computes.

**The algebraic line.** The syntactic ω-semigroup and its structure
theory are [PP04]; the Wagner-degree and chain machinery on the algebra
is Carton–Perrin [CP97, CP99] and Selivanov–Wagner [SW08], which the
qualitative calculus already exploits. The present paper adds, to our
knowledge, the first *probabilistic* exploitation of the syntactic
algebra: the localization of almost-sure behavior in the kernel
(Theorem 3.4) appears to be new in this form, though its ingredients —
Ramsey-type factorizations, the group structure of `H(k)` — are
classical [PP04].

**Quantitative semantics.** Weighted/quantitative languages in the
sense of ⟨Chatterjee–Doyen–Henzinger 2010, *Quantitative languages*,
ACM ToCL — pending library⟩ generalize the verdict beyond Booleans; §3's
proof is an invocation of conjugacy-invariance, so any semiring
respecting the conjugacy law inherits the generic-verdict mechanism —
we leave the weighted canonical object as future work.

## 8. Conclusion

The generic-verdict theorem localizes almost-sure membership in the
kernel of the syntactic ω-semigroup: one canonical bit per absorbing
component, one lookup each. Everything a probabilistic toolbox asks of a
specification then rides the invariant — measure, model-checking
probability, distance, entropy — in exact arithmetic, with certificates,
on an object that never needs re-simplification. The exponential
frontier of the calculus is untouched (entry still costs
determinization; MDP optimization stays refused), and the quantitative
layer inherits the same honesty: every quantity is a read-off precisely
because the qualitative object already paid for canonicity. Open
directions: the weighted invariant (semiring-valued `Val` under the
conjugacy law), Hausdorff dimension and finer fractal data alongside
entropy, and the census geometry as an instrument for conjecture-hunting
on the LTL frontier.

## References

In-library (see `papers/`): [PP04] Perrin, Pin, *Infinite Words:
Automata, Semigroups, Logic and Games*, Elsevier 2004. [CY95]
Courcoubetis, Yannakakis, *The complexity of probabilistic
verification*, JACM 42(4), 1995. [Var85] Vardi, *Automatic verification
of probabilistic concurrent finite-state programs*, FOCS 1985 (scan —
read via images). [BK08] Baier, Katoen, *Principles of Model Checking*,
MIT Press 2008. [VV06] Varacca, Völzer, *Temporal logics and model
checking for fairly correct systems*, LICS 2006. [LM95] Lind, Marcus,
*An Introduction to Symbolic Dynamics and Coding*, CUP 1995. [Sta05]
Staiger, *The entropy of Łukasiewicz-languages*, RAIRO-ITA 39(4), 2005
(context-free family; background only). [Sta93] Staiger,
*Kolmogorov complexity and Hausdorff dimension*, Inform. Comput.
103(2):159–194, 1993 (scan — read via images; entropy of ω-languages:
§2, Eq. (2.3), closure identity p. 168). [Sta97H] Staiger,
*ω-Languages*, Handbook of Formal Languages vol. 3, 1997 (in library as
`Rozenberg_Salomaa_1997_HandbookVol3.pdf`, printed pp. 339–387; Wagner
hierarchy survey — contains no entropy or measure material). [CP97]
Carton, Perrin, *Chains and superchains for ω-rational sets…*, IJAC
1997. [CP99] Carton, Perrin, *The Wagner hierarchy*, IJAC 1999. [SW08]
Selivanov, Wagner (Fund. Inform. 2008). [SωS26],
[SωSC26 = `sos_calculus.md`], [SωSX26], [SωSN26]: the project's own
line, as in the calculus paper.

Pending library acquisition (do not cite in submitted form until read):
Kwiatkowska–Norman–Parker CAV 2011; Chatterjee–Doyen–Henzinger ToCL
2010.
