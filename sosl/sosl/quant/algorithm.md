# The measure algorithm (M1)

What the code computes and why it is sound, at the level of the paper
(`research_notes/sos_measure.md`, §3–§4.1). Notation: `𝒞` the classes,
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
