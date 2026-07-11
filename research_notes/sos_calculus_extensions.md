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

## 4. One-liners and small open items

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
(2) the §3.4 completion + `X` middle band — cheap, closes the frontier
story; (3) LTL-over-SoS as a remark, section if the evaluator gets built;
(4) the one-liners opportunistically. The sister memos are separate papers,
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
- **New queued theory item — the canonical DELA exit, adequacy
  proposition** (paper §7.3 ⟨TBD⟩): on the right-Cayley structure the
  verdict of a run is a function of its recurrent transition set, so an
  EL condition over the edges completes core's Def 5.2 prospect. Proof
  sketch scoped: reduces to "idempotent folds of T-covering cycle
  products at a common state share their verdict"; check the
  saturating-right-congruence literature (Le Saëc) in `papers/` first.
  The transformation itself is already implemented (corpus pairs
  sos/det). This now outranks item 2 in priority; item 1 (mixed
  product) stays first.
