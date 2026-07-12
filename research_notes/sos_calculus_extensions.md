# Calculus Paper — Queued Extensions

*Working notes, 2026-07-10. Sections the calculus paper (`sos_calculus.md`)
should grow, sketched far enough that a session can draft them cold. Sister
memos: `sos_quantitative.md` (measure/distance/entropy),
`sos_giventhat.md` (the [DPT25] port). These three files are the research
directions that came out of the post-CAL5 "what is not yet covered" audit.*

## 1. The mixed product — §3.7 candidate (the load-bearing gap)

The ledger's intersection row assumes both operands entered the calculus.
Model checking proper is `L(K) ∩ L(𝓘) = ∅?` with `K` a system (Kripke
structure / NBA) that must never pay entry. It doesn't have to:

- Product state `(q, c)`, `q` a system state, `c ∈ 𝒞` the fold of the trace
  so far; edges `(q, c) →_a (q', c·λ(a))` — only the successor function of
  `K` is needed, so the exploration is on-the-fly in the model checker's own
  sense.
- Acceptance is *not* an inf-set condition: a counterexample is a reachable
  `(q, c)` carrying a closed walk back to `(q, c)` whose *fold* `d`
  satisfies `Val(c, d)` (and hits `K`'s own acceptance if it has any). So
  no plain NDFS; instead track achievable cycle folds — either a second `𝒞`
  component (`O(|K|·n²)` states) or a per-SCC fixpoint over the ≤ `n`
  achievable fold values. Polynomial; scan order gives the minimal witness
  discipline as usual.
- Payoffs to state: the spec side is one held, canonical, byte-comparable
  object across a whole campaign of systems; certificates come from the
  same scan. Probabilistic version (chains): `sos_quantitative.md` D4.

This is the section that makes the calculus usable inside a model checker;
easy theory, write it first.

## 2. LTL operators over SoS — remark or section

Read the LTL constructors as (partial) operators on invariants, with the
calculus's price tags:

- Boolean connectives: free after align (§3.2–3.3 as they stand).
- `X`: polynomial but *not* a surgery — `XL = Σ·L` has a deterministic
  split (position 1), no powerset; a new small table, constructible
  directly (residuals: `a⁻¹(XL) = L` for every `a`).
- `F`, `G`, `U`: cross the §4 frontier — `F L = Σ*·L` is concatenation by
  a prefix set with maximal split ambiguity, `G` dually, `U` likewise;
  Prop 4.1's argument applies as-is.
- Aperiodicity is preserved by *all* of them (FO-definability is closed
  under the LTL constructors), so a bottom-up formula→invariant evaluator
  never leaves the variety even where the table blows up: a
  canonical-by-construction alternative to `ltl2tgba`, paying exponentials
  only at `U`/`F` nesting. Pleasant corollary to state: the calculus's
  per-operator price list localizes LTL's PSPACE-hardness on exactly the
  operators that carry it.

## 3. §4 completion — name the whole frontier family

Members to add so the frontier reads closed: direct morphic images and
transductions (inverse ones are free §3.2; direct ones guess preimages),
shuffle/interleaving, Büchi's `lim` / `W^δ` constructors from finite-word
languages (entry-shaped). And name the **polynomial middle band** the
current free-vs-exponential dichotomy skips: `X L`, and `W·L` when `W` is a
prefix code / the factorization is unambiguous — deterministic split, new
table, polynomial, no powerset.

## 4. The canonical DELA exit — adequacy reduced to two equations (2026-07-12)

Worked state of the paper §7.3 ⟨TBD⟩ (was "queued theory item" below; the
proposition is now *stated and proved as a criterion*, with one open half).

**Setting.** `Cay(L)` per [SωS26, Def 5.2]: nodes `𝒞` (fresh identity root
`[ε]`), edges `c →ᵃ c·λ(a)`. Deterministic and complete, and with one gift no
other automaton has: *the state after reading `w` is `fold(w)`* — stems pin to
their own class. For `u ∈ Σ^ω` let `T(u)` be the set of edges its run
traverses infinitely often. *Adequacy* = membership is a function of `T(u)`;
equivalently the Muller-over-edges family `𝒯 = {T(u) : u ∈ L}` (an EL
condition over edge colors) completes `Cay(L)` into a DELA for `L`.

**Proposition (adequacy criterion).** Adequacy holds iff for all
`y, t, h, g ∈ 𝒞` with `y·t = y·h = y·g = y`:

- **(E1)** `Val_P(y, (t·g)^π) = Val_P(y, (t²·g)^π)`
- **(E2)** `Val_P(y, (t·h·g)^π) = Val_P(y, (h·t·g)^π)`

*Necessity.* Realize `y, t, g` by words `w_y, w_t, w_g`. The walks of `w_t`,
`w_g` from state `y` are closed (`y·t = y`), and the walk of `w_t²` is the
walk of `w_t` twice — same edges. So `w_y(w_t w_g)^ω` and `w_y(w_t² w_g)^ω`
have the *same* recurrent edge set (the union of the two closed walks), and
their memberships are the two sides of (E1). Same word game for (E2). ∎

*Sufficiency* (LSPW's skeleton [CPP08 §5.4], cover-free). Let `T(u) = T(v)`.
Pick `s` on `T`; both runs visit `s` infinitely often. Cut `u` at `s`-visits
so every block covers `T` exactly; each cut prefix has fold `s` (state =
fold — this kills the (5.6)/(5.7) machinery of [CPP08]). Ramsey-group blocks
to a constant idempotent fold `e`: `u ∈ L ⟺ Val_P(s, e)` with `e` the fold of
a `T`-covering loop word `p` at `s`; likewise `v ↦ (s, f)`, loop word `q`.
Define on `Cay`-paths: `p ∼ q` iff coterminal and
`∀w ([w] = origin), ∀r (return path): w(p̂r̂)^ω ∈ L ⟺ w(q̂r̂)^ω ∈ L`. This is
a path congruence (context closure is literal re-cutting of one ω-word, no
algebra). Its Simon premises are *exactly* (E1)/(E2) anchored at states: a
loop at `x` has fold in `Stab(x)`, every stem to `x` has fold `x`. By Simon's
path-congruence proposition ([CPP08, Prop 5.6]; proof in Eilenberg Vol. B),
coterminal same-edge-set paths are `∼`-equivalent, so `p ∼ q`; with stem
`u₀` and the empty return, `Val_P(s, e) = Val_P(s, f)`. ∎

**Why saturation alone cannot do it.** `L = Σ*a^ω`: at `y = β`
("contains b") the stabilizer is `{α, β}`, both idempotent,
`Val(β, α) = 1 ≠ Val(β, β) = 0`. Verdicts are *not* constant on stabilizer
idempotents; (E1)/(E2) hold there anyway (any product mixing both letters
folds to `β`). The anchored equations are precisely what edge-covering buys.

**Relation to Le Saëc–Pin–Weil.** They start from *weak* recognition and
must first pass to a cover with idempotent, R-trivial right stabilizers
(`x² = x`, `xyx = xy`) — identities that imply (E1)/(E2) outright but change
the automaton. We start from the saturated `(𝒞, P)` and keep `Cay(L)`
itself; the price is that (E1)/(E2) become a *hypothesis* — but a decidable
one: `O(Σ_y |Stab(y)|³)` resp. `|Stab(y)|⁴` `Val`-lookups per table. The
exit prices itself, per language.

**Open half + candidate counterexample.** Do (E1)/(E2) hold in *every
syntactic* ω-semigroup? Rotation/absorption arguments give only conjugacy
orbits (`(t g)^π ~ (g t)^π` at anchored stems); parity-style invariants die
under `^π`, order-style under rotation — every hand attempt at a violation
is "protected" by the states recording the left context. But at the *table*
level (saturated, not reduced) a candidate exists in `T₄` (right action,
`(u·v)(x) = v(u(x))`): `y = const-1`, `t = (2 3 4)`, `g = [1,2,2,4]`; then
`y·t = y·g = y`, `(tg)^π = [1,2,2,2] =: F`, `(t²g)^π = [1,2,4,4] =: F' ≠ F`.
If `(y,F)` and `(y,F')` are non-conjugate in `S = ⟨y,t,g⟩`, the saturated
`P := closure{(y,F)}` violates (E1) — and the question becomes whether
`reduce` (to the true syntactic table of `L(P)`) kills the violation. That
is CAL7b (spec §9.6). Outcomes: conjecture dead → paper §7.3 states the
criterion + per-corpus certificate (still a clean result); conjecture
survives corpus + probe → prove (E1)/(E2) from syntacticity (open).

**Theory debts.** (1) Reprove Simon's path-congruence proposition ourselves
(elementary; [CPP08] states it, proof is in Eilenberg Vol. B which we do not
hold). (2) Acquisitions for `papers/`: Eilenberg Vol. B (1976); Le Saëc–Pin–
Weil FSTTCS 1991 + IJAC 1991; Le Saëc, *Saturating right congruences*,
RAIRO 1990 (checked: none present; [CPP08] is our only read source).

## 5. One-liners and small open items

- **Monitor extraction** (Spot's safety monitors): the monitor *is* the
  right-Cayley DFA restricted to `Live` — CAL5's `live()` already computes
  the state set. One sentence in §6; the finite-word/LTLf story beyond it
  belongs to the learner paper.
- **Strength decomposition for parallel MC** (Spot's `decompose_scc`):
  beyond the Alpern–Schneider split (done, Cor 6.3), the
  terminal/weak/strong factoring of `L` into pieces recombined by ∧/∨ is
  not yet given as surgeries. Likely doable per rung with the hull
  machinery; small.
- **Bisimulation**: nothing to add, but worth the sentence — between two
  specifications, canonicity subsumes it (anything finer than language
  equivalence is about presentations, which the invariant forgot); against
  a system, bisimulation reduction is presentation-side preprocessing of
  `K` and the remaining language question is §1's mixed product.

## Priority

(1) mixed product first — it is the practical claim of the whole paper;
(2) DELA adequacy §4: close the open half (CAL7 outcomes decide the route);
(3) the §3.4 completion + `X` middle band — cheap, closes the frontier
story; (4) LTL-over-SoS as a remark, section if the evaluator gets built;
(5) the one-liners opportunistically. The sister memos are separate papers,
not paper sections.

## Status update (2026-07-11)

- Paper restructured (ten sections; renumber map in
  `sos_calculus_report.md` addendum). Item 3's **polynomial middle
  band** is now IN the paper (§4: `X L`, prefix-code `W·L`, free-AP
  drop); what remains of item 3 is the frontier family completion
  (direct images/transductions, shuffle, `lim`/`W^δ`).
- **Alphabet hygiene** (free-AP read-off + drop, equality up to AP
  renaming) landed in paper §3.2/§7.1; implementation is spec §9.3
  (CAL6).
- **DELA adequacy** (paper §7.3): advanced 2026-07-12 from queued sketch
  to the criterion of §4 above — adequacy ⟺ (E1) ∧ (E2), necessity and
  sufficiency proved, the syntactic-case conjecture open, CAL7
  (spec §9.6) probing it. Le Saëc checked: not in `papers/`; [CPP08]
  §5.4 is the read source.
