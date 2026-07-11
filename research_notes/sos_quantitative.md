# Quantitative Read-offs on the Syntactic ω-Semigroup — Directions

*Exploratory memo, 2026-07-10; revised the same day: the generic-verdict
question (Q1) is settled, positively, with proofs — see §1. Not a paper; a
map of candidate results for one, whose technical heart now exists at memo
rigor. Companion to `sos_calculus.md` (the qualitative calculus); notation
and the object `𝓘(L) = (𝒞, λ, M, P)` as there. **The paper now exists:
`sos_measure.md`, with `sos_measure_spec.md` (engineering direction) and
`sos_measure_report.md` (results interface); this memo stays as the map.*

## 0. Premise

The calculus answers qualitative questions (membership, inclusion,
classification) by scans of `Val` over a fixed table. A second family of
questions about a held language is *quantitative*: how big is it, how far
apart are two languages, how fast does it branch. The automata world answers
these with separate machinery (linear algebra over a deterministic automaton,
probabilistic model checkers); Spot itself mostly does not answer them at
all. The premise of this direction: the invariant already *is* a
deterministic presentation — the right-Cayley DFA on `𝒞` (`n` states,
deterministic, complete, canonical) with `Val_P` judging the tail — so every
quantity below should be a polynomial computation on the held object, in the
same pay-canonicity-once economy. The deliverables would be: a small set of
theorems ("the following quantity is rational and computable in `O(...)` from
`(𝒞, λ, M, P)`"), read-off implementations, and census columns.

## 1. The measure of a language (D1) — the generic-verdict theorem

Fix a Bernoulli measure `p` on `Σ` with full support (uniform `1/|Σ|` as the
default; any rational `p` works). `μ_p(L)` is defined and rational for every
ω-regular `L`, computable in polynomial time from a deterministic automaton
[CY95]. The original sketch of this section asked whether the same holds as
a *read-off* on the invariant, hinging on one question (Q1): is the a.s.
verdict of a word absorbed in a bottom SCC of the right-Cayley DFA
independent of the random cut stem? **It is.** The machinery: `S = fold(Σ⁺)`
(the image semigroup), `K` the kernel (minimal ideal) of `S` — completely
simple, so `k·S·k = k·K·k = H(k)` is a finite group with identity `k` for
every idempotent `k ∈ K` (Suschkewitsch; [PP04]). Recall (CAL5) that the
SCCs of the right-Cayley graph are the `R`-classes, so a bottom SCC `C` is a
*closed* `R`-class: `c·S ⊆ C` for `c ∈ C`.

**Lemma Q1-A (a.e. word factors over a kernel idempotent — the doubled-word
cut).** Fix any `w ∈ Σ⁺` with `k := fold(w)` idempotent in `K` (exists:
pick `w₀` with `fold(w₀) ∈ K` and raise to the idempotent power). For a.e.
`α` entering its bottom SCC `C` at class `c`, there is a factorization of
`α` with stem folding to some `s ∈ c·S¹·k` and every loop block folding to
`k` exactly; hence `α ∈ L ⟺ Val(s, k)` by the strong factoring theorem
(calculus paper §2).

*Proof.* The entry time is a stopping time, so the tail `β` is again i.i.d.;
partitioning it into consecutive blocks of length `2|w|`, each equals `w·w`
with probability `p(w)² > 0` independently, so a.s. `β` contains infinitely
many disjoint occurrences of `w·w` (Borel–Cantelli). Cut at the *midpoints*
of these occurrences. Every inter-cut block then starts and ends with a full
`w`, so it folds into `k·S¹·k = H(k)` — a genuine group; this is the point
of doubling. (Cutting at occurrence *ends*, as the original sketch did,
gives blocks folding to `fold(x)·k ∉ H(k)`, and "equal partial products"
then only traps blocks in a stabilizer, from which blocks `= k` do not
follow — the gap the doubling closes.) The cumulative block products
`π_m ∈ H(k)` take finitely many values, so some value recurs on an infinite
set `J` of cut points; between consecutive `J`-cuts the block folds to
`π_j^{-1}·π_{j'} = k` exactly — group inverses do what a stabilizer cannot.
The stem (start of `α` to the first `J`-cut) ends with a full `w`, so it
folds to `s = c·fold(y)·k ∈ c·S¹·k` with `s·k = s`. ∎

**Lemma Q1-B (stem invariance: achievable stems are one `H(k)`-orbit).**
For `c` in a closed `R`-class `C`, any idempotent `k ∈ K`, and any
`s₁, s₂ ∈ c·S¹·k`: `Val(s₁, k) = Val(s₂, k)`.

*Proof.* Closedness puts `s₁, s₂ ∈ C`, so `s₁ R s₂` and `s₂ = s₁·u` for
some `u ∈ S¹` (if `u = 1`, trivial). Since `s₁·k = s₁` and `s₂·k = s₂`:
`s₂ = s₁·u·k = s₁·k·u·k = s₁·m` with `m := k·u·k ∈ H(k)`. Factor the loop
as `k = m·m^{-1}` — the group identity — and apply the conjugacy law
(calculus paper Prop 3.1): the cells `(s₁, k)` and
`(s₁·m, m^{-1}·m) = (s₂, k)` carry one verdict, the renormalization being
trivial because `m^{-1}·m = k` is already idempotent. ∎

The mechanism, said plainly: `s₁·k^ω` and `(s₁·m)·k^ω` are *the same
ω-word class* — phases inside the kernel group are invisible at infinity.
This is why the worry that `R` is not a right congruence never bites: the
multiplier is chosen inside `H(k)`, where conjugacy cancels it. Note the
proof needs none of the Rees/sandwich-matrix machinery of the calculus
paper's Lemma 3.8 — only Prop 3.1 plus `kSk = H(k)`.

**Lemma Q1-C (the constant is canonical).** The bit does not depend on the
entry class, nor on the choice of kernel idempotent:

- *Per-BSCC, not per-entry-class.* For `c' = c·t` with `c, c' ∈ C`, the
  achievable stems nest: `c'·S¹·k ⊆ c·S¹·k`; both sets carry a constant
  `Val` (Q1-B), so the constants agree.
- *Independence of `k`.* For idempotents `k, k' ∈ K`, set
  `g := k·k'·k ∈ H(k)`, `x := g^{-1}·k'`, `y := k'·k`. Then
  `x·y = g^{-1}·k'·k = g^{-1}·(k·k'·k) = g^{-1}·g = k` (using
  `g^{-1}·k = g^{-1}`), while `y·x = k'·g^{-1}·k' ∈ H(k')` has idempotent
  power `k'`. Prop 3.1 transports `(c·k, k)` to a cell with loop `k'` and
  stem `c·g^{-1}·k' ∈ c·S¹·k'`, and Q1-B at `k'` finishes. (Probabilistically
  obvious — two full-measure readings of one event — but the algebraic proof
  keeps the theorem oracle-free.)

So each bottom SCC `C` carries a single canonical bit, computed by **one
`Val` lookup**:

```
θ_C  :=  Val(c, k)        any c ∈ C, any idempotent k ∈ K
```

(`Val(c, k) = ((c·k, k) ∈ P)` and `c·k` is itself an achievable stem).

**Theorem (measure read-off).** For a.e. `α`, `1_{α ∈ L} = θ_C` where `C`
is the absorbing bottom SCC of the run; hence

```
μ_p(L)  =  Σ_C  θ_C · Pr[absorption in C]  =  x_{[ε]},
x_c = Σ_a p(a)·x_{c·λ(a)}  (c transient),    x_c = θ_C  (c ∈ C bottom)
```

— `O(n³)` exact rational arithmetic on the held object, after an
`O(n·|Σ|)` SCC pass and one kernel-idempotent computation (polynomial:
bottom `J`-class of the two-sided reachability order, then one power walk).
Certificate: the `θ`-labeled BSCC map. Rationality of `μ_p(L)` falls out of
the linear system rather than being imported.

Sanity checks. *Infinitely many `a`'s*: single bottom SCC, `k = [contains
a]` is the kernel idempotent, `θ = 1`, `μ = 1` — the lemma correctly
selects the generic loop (the measure-zero tail `b^ω` folds outside `K`).
Its complement flips `P`, hence every `θ_C`: `μ(L) + μ(L^c) = 1` is
structural. `L = a·Σ^ω`: two bottom SCCs with `θ = 1, 0`; `μ = p(a)`.

Two remarks on the shape of the result. First, the **θ-profile** — the bit
vector `(θ_C)` over bottom SCCs — is a canonical, `p`-free invariant of
`L`; in particular whether `μ_p(L)` is `0`, `1`, or strictly interior is
the same for every full-support Bernoulli `p` (the absorption distribution
charges every bottom SCC). Second, the pleasant inversion of the original
sketch stands but is now subsumed: for *obligation* languages Q1 was
trivial (verdict an `R`-class function of the stem, calculus Thm 6.6); the general
theorem is no harder, so there is no reason to publish the band alone.

*Status: proofs written this session, unrefereed; Q1-B in particular wants
an adversarial re-read, and the read-off wants the usual harness (oracle:
Route A below; metamorphic: the flip law, and `p`-independence of the
profile).* Route A — exiting to the `O(|P|·n)`-state acceptor and paying a
determinization before the classical BSCC analysis [CY95] — is thereby
demoted to what it wanted to be: the independent oracle for the harness,
never the algorithm.

## 2. Distances between two languages (D2)

On an aligned table, `xor` is free and measure turns it into a metric:
`d_p(L₁, L₂) = μ_p(L₁ Δ L₂)`. Uses:

- **Quantitative regression**: after a rewrite, the byte comparison says
  *whether* the language moved; `d_p` says *how much*. A pipeline column.
- **Nearest neighbor in the census**: the census becomes a metric space;
  "the closest LTL-definable language to this non-LTL one" is a scan. Ties
  into the [SωSX26] frontier story.
- **Weighted counterexamples**: the minimal witness (Prop 3.2) is the
  *shortest* disagreement; `d_p` weights the disagreement mass. Both are
  read off the same aligned object.

All of D2 is downstream of D1, now unconditionally: no new theory at all.
(Also free on the aligned table: conditional measure
`μ_p(L₁ | L₂) = μ_p(L₁ ∩ L₂)/μ_p(L₂)`.)

## 3. Entropy and growth (D3)

The topological entropy `h(L)` — the exponential growth rate of the set of
finite prefixes of `L` — is the log spectral radius of the letter-count
adjacency matrix restricted to the `Live` classes (attribution: Staiger —
[Sta97], *chapter still to be acquired*; the growth-rate-of-a-regular-
language fact itself is classical). On the invariant this is rigorous with
no pruning subtleties, by a cute collapse: `pref(L) = {u : fold(u) ∈ Live}`
(liveness is a class property, calculus paper §6), and since liveness
propagates to prefixes, *co-reachability to `Live` equals `Live`* — so the
number of length-`n` prefixes is exactly the number of length-`n` paths
staying inside `Live`, and `h(L) = log ρ(A|_Live)`: one Perron eigenvalue
on top of CAL5's `live()`, `O(n³)`. Refinements: `h(cl(L)) = h(L)` since
the prefix sets coincide (a live word extends to a word all of whose
prefixes are live, by König); relative entropy of `L₁` inside `L₂` on the
aligned table; the census distribution of entropies per Wagner degree (do
higher degrees concentrate at full entropy?).

This is the cheapest of the directions — a section, not a paper.

## 4. The system-side product, probabilistically (D4)

The right theorem to prove is this one; D1 is its one-state corollary, and
the proofs of §1 generalize verbatim once the kernel is taken in the right
subsemigroup — which is *why* the original sketch's instinct ("the
subsemigroup generated by `C`'s letters") was correct: in a product, the
tail alphabet is constrained to the cycles of the absorbing component.

**Setting.** `M` a finite labeled Markov chain (letters on transitions,
positive probability on every present transition), `L` held as `𝓘(L)`.
Form the product chain on `states(M) × 𝒞` (reachable part; the qualitative
mixed product of the calculus paper, now with numbers). Let `B` be a bottom
SCC of the product.

**Generic-verdict lemma, product form.** Fix a base point `(q̂, ĉ) ∈ B` and
let `T := { fold(z) : z reads a cycle q̂ → q̂ inside B }` — a finite
subsemigroup of `S`, computed by one BFS over `B × 𝒞`-pairs. Take `k`
idempotent in `kernel(T)`, realized by a cycle word `w` at `q̂`. A.e. run
absorbed in `B` visits `q̂` infinitely often and reads the doubled cycle
`w·w` from `q̂` infinitely often (conditional Borel–Cantelli over visits);
mid-cutting those occurrences gives blocks `w·x·w` with `x` a `B`-internal
cycle word, folding into `k·T¹·k = H_T(k)` — the same group trick — and the
pigeonhole again yields loop blocks folding to `k` exactly. Achievable
stems again form one `H_T(k)`-orbit: for two stems based at entries
`(q₀,c₀)`, strong connectivity of `B` provides a return path, whose
composition with the second stem's path is a cycle at `q̂`, so the stems
differ by `k·(fold ∈ T)·k ∈ H_T(k)` and Q1-B's conjugacy applies unchanged.
Hence a single bit per product BSCC, `θ_B = Val(c, k)` for any
`(q̂, c) ∈ B`; independence of the base point `q̂` and of `k` by the
two-full-measure-readings argument.

**Theorem shape.** `Pr_M(L) = Σ_B θ_B · Pr[absorption in B]`, one linear
system on the product chain: polynomial in `|M|·n`, exact rational
arithmetic, certificate = the `θ`-labeled product-BSCC map. This is
Courcoubetis–Yannakakis for a deterministic spec object — their §4.1
recurrent-state analysis (Def. 4.1.1, Lemma 4.1.2: bottom SCCs of the
product decide, then a linear system aggregates) [CY95] — with the
deterministic automaton replaced by the canonical algebra, and the usual
canonicity dividend: the spec-side object is normal-formed, byte-comparable,
and shared across all queries of a campaign. A free generalization falls
out: `μ` under a *stationary Markov letter source* is just `Pr_M(L)` with
`M` the source, so D1 extends beyond Bernoulli at no cost. MDPs (max/min
probability) stay out of scope — optimization over schedulers is the
branching wall the calculus already refuses.

## 5. Census columns (D5)

Whatever lands becomes sidecar data, in the `.cat`/CSV discipline (no JSON):
`measure: p/q`, `entropy: log2(λ)`, and the `p`-free `theta_profile` bits
per language, a distance matrix sample per alphabet slice. Cheap, and it
feeds the empirical questions: the measure distribution per Wagner degree;
whether measure-0/1 concentrates in the safety/co-safety rungs (it should:
clopen ⟹ μ ∈ {0,1} is false — finite unions of cylinders — but the *bands*
should show structure); the metric geometry of the census (diameter,
clustering by degree). The θ-profile column is available *before any
arithmetic* — it is a scan — and doubles as a cross-check on the measure
column (profile all-0 ⟺ μ = 0, all-1 ⟺ μ = 1, mixed ⟺ interior).

## 6. Beyond the bit: semiring-valued `Val` (D6, speculative)

`P ⊆ linked` is a Boolean-valued function on linked pairs. Replacing the
Boolean semiring by another (probabilities, tropical/discounted, counting)
suggests a *weighted* invariant: `Val : cells → S`. The qualitative calculus
survives wherever the semiring respects the conjugacy law (Prop 3.1 becomes
an equation in `S`); the syntactic congruence needs a semiring-appropriate
replacement (Schützenberger-style weighted recognition over ω is known
territory but the canonical-object story is not). One datum from §1: the
proof of Q1-B is *exactly* an invocation of conjugacy-invariance, so any
semiring in which the conjugacy law holds inherits the generic-verdict
mechanism verbatim — a concrete entry point if this direction is ever
opened. High risk, high novelty; park until D1–D4 exist.

## 7. What would make it a paper

1. ~~The generic-verdict lemma (Q1) settled~~ — **done at memo rigor**
   (§1, §4: the doubled-word cut, the `H(k)`-orbit stem invariance, the
   canonical per-BSCC bit, at product generality). Remaining for the paper:
   an adversarial re-read of Q1-B/Q1-C, and the harnessed `O(n³)` read-off
   with Route A as oracle.
2. D2 + D3 as corollaries with read-off implementations under the usual
   harness (oracle: Route A / Spot-side product measure where available;
   metamorphic laws: `μ(L) + μ(L^c) = 1` free from the flip, `d_p` triangle
   inequality sampled, entropy monotone under inclusion, `p`-independence
   of the θ-profile).
3. D4 as the applied payoff — now the *statement* of the main theorem, with
   D1 its one-state corollary — one worked pipeline (a spec held once,
   checked against a family of chains).
4. The census section (D5) as the empirical backbone, same reproducibility
   floor as CAL4.

Title shape: *"Measure, Distance, and Entropy on the Syntactic ω-Semigroup"*.
Dependency: none on the learner; reuses CAL5's `live`/R-class machinery and
the aligned product throughout. The proof toolkit of §1 leans only on
Prop 3.1, the strong factoring theorem, and [PP04]-classical kernel facts —
no new mathematical dependencies.

## References (delta over the calculus paper)

- [CY95] Courcoubetis, Yannakakis. *The complexity of probabilistic
  verification.* JACM 42(4), 1995. **In library**
  (`Coucourbetis_Yannakakis_1995_JACM.pdf`, sic filename); relevant bits:
  §4.1 recurrent product states, Def. 4.1.1 / Lemma 4.1.2, linear-system
  aggregation.
- [Sta97] Staiger. *ω-Languages.* Handbook of Formal Languages, vol. 3,
  Springer 1997. **In library** (`Rozenberg_Salomaa_1997_HandbookVol3.pdf`,
  two-up scan, chapter at PDF pages 179–203) — inspected: it is a
  Büchi/topology/Wagner-hierarchy survey and contains **no entropy or
  measure material**; the entropy load is carried by Lind–Marcus 1995
  (`Lind_Marcus_1995_Book.pdf`, in library) and the ω-transposition ask is
  now Staiger, *Kolmogorov complexity and Hausdorff dimension*, Inf.
  Comput. 103(2), 1993 — the memo's original [Sta93] pointer was right all
  along. (The in-library `Staiger_1983_JCSS` is the structural-classes
  paper, not this.)
- [PP04], [SωS26], [SωSX26], [SωSN26]: as in `sos_calculus.md`.
