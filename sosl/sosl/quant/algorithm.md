# The measure algorithms (M1–M4)

What the code computes and why it is sound, at the level of the paper
(`research_notes/sos_measure.md`, §3–§4.2, §5). Notation: `𝒞` the classes,
`[ε]` the adjoined identity, `S = 𝒞 \ {[ε]}`, `p` a full-support
rational Bernoulli measure on `Σ`.

## 1. The random walk and its bottom SCCs (`chain.py`)

A random ω-word walks the right-Cayley graph `c → M(c, λ(a))` on all of
`𝒞`, starting at `[ε]`. The graph is finite and complete, so the walk
almost surely enters a **bottom SCC** (an SCC with no leaving edge) and
never leaves it. Bottom SCCs are returned sorted by the shortlex key of
their least class — this fixed order is what makes the θ-profile and
the absorption certificate canonical.

Sanity asserted: `λ(a) ≠ [ε]` for every letter (no nonempty word folds
to the adjoined identity), `[ε]` lies in no bottom SCC, and at least
one bottom SCC exists.

The SCC pass itself is the calculus's right-Cayley Tarjan
(`sosl.sos.calculus.surgery._right_cayley_sccs`), reused, not
re-derived.

## 2. The kernel idempotent (`kernel.py`)

The **kernel** `K` is the unique minimal two-sided ideal of the finite
semigroup `S`. Operationally: build the two-sided Cayley graph on `S`
(edges `c → M(λ(a), c)` and `c → M(c, λ(a))`), compute its SCCs — they
are the `J`-classes — and keep the sink SCCs. Exactly one sink must
exist (the `J`-order has a unique minimum); two sinks convict the table
as corrupted and raise. `k := idem(t)` for the least-keyed `t ∈ K`; `K`
is closed under powers, so `k ∈ K` and `M(k, k) = k` (asserted).

Products of non-identity classes are asserted to stay in `S`: the
identity is *adjoined*, so no edge of the two-sided graph may reach it.

## 3. The θ-profile (`theta.py`)

For each bottom SCC `C`, the **generic verdict** is one table lookup:

```
θ_C := Val(c, k) = ((M(c, k), k) ∈ P),    any c ∈ C
```

(`k` is idempotent, so `Val` absorbs no extra power.) Soundness is the
paper's §3: almost every word absorbed in `C` factors as
`y·z₁·z₂⋯` with `fold(z_i) = k` and `fold(y) ∈ c·S¹·k` (Lemma 3.1,
doubled-word cut + group cancellation in `H(k)`); `Val(·, k)` is
constant on those stems (Lemma 3.2, conjugacy inside `H(k)`); and the
constant depends neither on the representative `c ∈ C` nor on the
choice of idempotent in `K` (Lemma 3.3). Hence the bit is canonical and
`1_{α ∈ L} = θ_C` a.s. on the absorption event of `C` (Theorem 3.4).

`PARANOID` (default on) re-checks Lemma 3.3 numerically on every call:
θ from a second class of the same SCC, and θ under `k' = idem(t')` for
a second kernel element, must agree; the profile length must equal the
bottom-SCC count.

The profile is `p`-free: whether `μ_p(L)` is `0`, `1`, or strictly
interior is decided by the profile being all-0, all-1, or mixed, for
*every* full-support `p`.

## 4. The measure (`measure.py`)

By Theorem 3.4, `μ_p(L) = Σ_C θ_C · Pr[absorption in C]`, and the
absorption probabilities solve the standard transient system: with
`transient` = classes in no bottom SCC (this always includes `[ε]`),

```
x_c = Σ_{a ∈ Σ} p(a) · rhs(M(c, λ(a)))
rhs(c') = x_{c'}     if c' transient
        = 1_{c' ∈ C} if c' lies in bottom SCC C   (per-C boundary)
```

The system is solved once with one right-hand-side column per bottom
SCC (Gauss–Jordan over `Fraction`, hand-rolled, partial search for a
nonzero pivot). The matrix `I − Q` is nonsingular because every
transient class reaches some bottom SCC, so a missing pivot is an
assertion failure, not a case. The absorption row of `[ε]` is the
certificate; it must sum to exactly 1, and

```
μ_p(L) = Σ_{C : θ_C = 1} absorption([ε], C).
```

Rationality of `μ_p(L)` for rational `p` is a corollary of the
elimination itself.

## 5. The Route A oracle (`routea.py`)

An independent computation of `μ_p(L)` from a *deterministic, complete*
automaton with Emerson–Lei acceptance on transitions (the corpus's
`det/*.hoa`), sharing nothing with §1–§4 but the linear solver. Under a
full-support Bernoulli `p`, the automaton's run is a finite Markov
chain on its states (`δ(q, a)` unique; `Pr[q → q'] = Σ { p(a) :
δ(q, a) = q' }`, an exact `Fraction`). The run is a.s. absorbed in a
bottom SCC `B`, inside which every transition has positive probability
per step, so every edge of `B` recurs infinitely often a.s.; the limit
set of the run is exactly `B`'s edge set. Acceptance of the run is
therefore the EL condition evaluated on the marks occurring on `B`'s
edges — `Inf(m)` true iff `m` sits on some `B`-edge, `Fin(m)` true iff
on none — one evaluation per bottom SCC, and

```
μ_A = Σ_{B accepting} Pr[absorption in B]
```

by the same transient system as §4 (if the initial state already lies
in a bottom SCC, `μ_A` is that component's bit). Spot's role is
bounded to parsing the HOA and exposing the acceptance condition; no
automaton construction, no determinization. Agreement `μ = μ_A`,
exact, is the M2 gate — it tests the θ bits themselves, which the
complement flip law of §6 cannot (any consistent per-SCC lookup flips
pointwise; only an independent oracle convicts a wrong bit).

## 6. Complement compatibility

Nothing above reads anything but `(𝒞, λ, M)` and membership of pairs in
`P`. The calculus complement flips `P` against the linked pairs on the
*same* table, so on a flipped invariant every `θ_C` negates pointwise
and the absorption vector is unchanged — hence the M1 gate law
`μ_p(L) + μ_p(¬L) = 1`, exactly, with no reduction anywhere.

## 7. The distance (`distance.py`)

`d_p(L₁, L₂) := μ_p(L₁ Δ L₂)`. The calculus `align` builds the
letter-generated product of the two folded languages; `materialize`
turns it into one table carrying both pair sets. On a shared table,
membership of a cell in `L₁ Δ L₂` is the xor of the two lookups, so the
symmetric difference of the *pair sets* presents `L₁ Δ L₂` outright,
and `μ_p` of that (non-reduced) invariant is the distance — §4's solver
is reduction-insensitive by construction.

The result carries the xor's θ-profile. By §3's `p`-freeness, the
profile is all-zero iff `d_p(L₁, L₂) = 0` for *every* full-support `p`
— the **null-disagreement** read-off (paper §4.2), decided with no
second measure run.

Pseudometric laws (gate-sampled, all exact): symmetry (`Δ` is
symmetric), `d_p(L, L) = 0` (empty xor), and the triangle inequality —
`L₁ Δ L₃ ⊆ (L₁ Δ L₂) ∪ (L₂ Δ L₃)`, and `μ_p` is monotone and
subadditive.

## 8. The shadow (`shadow.py`)

Paper Prop 4.1: on `L`'s own table, with `D` the union of the `θ = 1`
bottom SCCs,

```
P_sh := { (s, e) linked : s ∈ D },
```

then `reduce`. The result accepts exactly the lassos whose stem class
already lies in the almost-sure-acceptance region, so
`d_p(L, shadow(L)) = 0` for every full-support `p`, the operation is
idempotent, and it is `p`-free outright — the construction never reads
`p` (no `p` parameter exists).

Shadow equality is *sufficient* for `d_p = 0`, not necessary (paper
§4.2 warning): two languages can differ by a null set yet have
byte-different reduced shadows. That gap is the essential form's job.

## 9. The essential form (`essential.py`)

Paper Thm 4.4. The **value vector** extends §4's solve to every class:
`x(c)` is the θ-weighted absorption row of a transient `c`, and `θ_C`
on the classes of a bottom SCC `C` (`measure.value_vector`). The
**congruence**

```
c ≈ c'  iff  x(M(w, M(c, z))) = x(M(w, M(c', z)))  for all w, z ∈ 𝒞
```

(`w`, `z` ranging over all classes *including* `[ε]`) is computed by
grouping classes on their full context signature — `O(n³)` table
lookups, exact `Fraction` comparisons, no refinement loop needed. It is
a two-sided congruence by construction (`c ≈ c'` transfers to `c·d` and
`d·c` by reassociating the contexts); the representative-built quotient
is asserted against every product anyway.

**Identity convention.** `[ε]` is held out of the quotient and
re-adjoined fresh, as everywhere in the calculus (`.sos` canonicity).
Thm 4.4's abstract `≈` may merge `[ε]` with a neutral word class; the
held-out quotient is finer by exactly that split and presents the same
language — an `[ε]`-stem cell `([ε], ē)` reads the pair `(ē, ē)` either
way, and word-class blocks, right-Cayley bottom SCCs, linked pairs and
`D̄` below are untouched.

On the quotient: `x` descends to `x̄` (asserted constant on blocks);
Thm 4.4(2) makes `x̄` constant `0` or `1` on every *bottom SCC of the
quotient* — a violation raises, it convicts the paper, not the input.
`D̄` := the value-1 bottom classes, the pair set is the shadow read-off
`{ (s̄, ē) linked : s̄ ∈ D̄ }`, then `reduce`. Prop 4.5 says the result
does not depend on `p` at all — the gate asserts byte-equality of the
dumps across `p`'s and a difference is a stop-the-line finding.

`ltl_up_to_null` is aperiodicity of the quotient monoid — the classify
orbit scan (`is_aperiodic`), run on the quotient before the final
`reduce`.

## 10. The entropy (`entropy.py`)

Paper Prop 5.1: `h(L) = log₂ ρ(A)` with `A` the **letter-count matrix**
on the live classes — `Live` is the calculus liveness scan
(`live(table, P)`: the classes with a nonempty residual), and
`A[c][c'] = |{a ∈ Σ : M(c, λ(a)) = c'}|`, restricted to `Live × Live`.
This is the only float-bearing computation in the package, and the
float is quarantined to the final `log₂`: everything up to the bracket
on `ρ(A)` is exact `Fraction` arithmetic, returned as a replayable
certificate (the live set, the irreducible blocks, each block's exact
rational bracket).

`A` is reducible whenever some live class is transient among live
classes — the common case — and on a reducible matrix a single
Collatz–Wielandt bracket never tightens (on `diag(2, 1)` every positive
`v` gives min-ratio 1 and max-ratio 2, forever). So the computation is
per irreducible block [LM95 §4.4]: SCC-condense the live subgraph
(edges `c → M(c, λ(a))` inside `Live`; `kernel._sccs`, reused) and take

```
ρ(A) = max over diagonal blocks B of ρ(A_B).
```

Per block: a singleton with no self-loop is nilpotent (`ρ = 0`,
skipped); a singleton with self-loops has `ρ = A[c][c]` exactly, width
0. A nontrivial block `B` is irreducible by construction; `B' := I +
A_B` is then primitive and `ρ(A_B) = ρ(B') − 1` (a nonnegative shift).
Power-iterate `v ↦ B'·v` from `v = (1, …, 1)`: for EVERY strictly
positive `v`, Collatz–Wielandt puts `ρ(B')` in
`[min_j (B'v)_j/v_j, max_j (B'v)_j/v_j]`, so soundness never depends
on convergence; primitivity contracts the bracket geometrically. The
brackets of successive iterations are intersected (each is valid on
its own `v`). Iteration stops when the width drops under `10⁻⁹` or at
10 000 steps — a non-converged bracket is still a valid enclosure,
reported as a datum.

To cap `Fraction` bit growth, `v` is kept in fixed point: strictly
positive integer numerators over the common denominator `10⁴⁰`
(renormalized by the max entry and floored each step, clamped `≥ 1`).
This is the spec's `limit_denominator(10**40)` rounding realized on a
common denominator — per-entry denominators make the exact products
`B'·v` blow up through their lcm — and it inherits the same soundness
argument: rounding only perturbs `v`, which stays strictly positive,
so every step's bracket is still exact CW on the `v` actually used;
only convergence speed is affected.

`h_lo, h_hi := log₂` of the exact bracket ends, each widened one
`math.nextafter` ulp outward — the ONLY float step. `Live = ∅` (iff
`L = ∅`) short-circuits to `h = 0` exactly with width 0 (paper §5
convention). If `L ≠ ∅` every live class has a live letter-successor
(peel one letter off a witnessing continuation; for a stem `c` with
linked loop `e = fold(a·z')`, `c·λ(a)·fold(z') = c·e = c`), so the
live subgraph has a cycle and `ρ ≥ 1` — a violation convicts the
liveness scan, asserted in the gate, not silently absorbed.

The closure law `h(cl(L)) = h(L)` is checked structurally, never on
floats: `cl` is the calculus `safety_closure` on the same table, and
the gate asserts `Live(cl(L)) = Live(L)` as sets and the letter-count
submatrices identical — Prop 5.1's entropy then agrees by
construction.
