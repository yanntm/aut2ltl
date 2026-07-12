# Calculus Paper — Garbage Bin (cut / rejected material)

*This file is a **garbage bin**: text cut from the calculus paper
(`sos_calculus.md`) and directions explored and rejected. Being here means
NOT being in the paper — nothing in this file is queued, promised, or a
direction; work exists only where the spec (`sos_calculus_spec.md`) or
`handoff_calculus.md` points at it. Appended to, never groomed. Sister
memos (separate papers, not bin content): `sos_quantitative.md`
(measure/distance/entropy), `sos_giventhat.md` (the [DPT25] port).*

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

## 4. PARKED — the DELA exit adequacy notes (2026-07-12, out of scope)

**Not a paper item and not queued anywhere.** User call 2026-07-12: this
direction is a spiral away from the calculus paper; §7.3 stays a prospect.
The notes below are archived as-is in case the question ever becomes
load-bearing (it would, only if paper §8's claim that the corpus `D` comes
from this exit is confirmed *and* a soundness statement is demanded).
Caveats if ever revived: the sufficiency direction rests on Simon's
path-congruence proposition, seen only *stated* in [CPP08] (proof is in
Eilenberg Vol. B, which we do not hold); nothing below has been machine-
checked; the syntactic-case question is open.

**Setting.** `Cay(L)` per [SωS26, Def 5.2]: nodes `𝒞` (fresh identity root
`[ε]`), edges `c →ᵃ c·λ(a)`. Deterministic and complete, and with one gift no
other automaton has: *the state after reading `w` is `fold(w)`* — stems pin to
their own class. For `u ∈ Σ^ω` let `T(u)` be the set of edges its run
traverses infinitely often. *Adequacy* = membership is a function of `T(u)`;
equivalently the Muller-over-edges family `𝒯 = {T(u) : u ∈ L}` (an EL
condition over edge colors) completes `Cay(L)` into a DELA for `L`.

**Claimed criterion (unverified — see header caveats).** Adequacy holds iff for all
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
`reduce` (to the true syntactic table of `L(P)`) kills the violation. (A CAL7 work order for this was drafted and withdrawn the same day —
spec §9.6 now asks only the `D`-provenance question.)

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
(2) the §3.4 completion + `X` middle band — cheap, closes the frontier
story; (3) LTL-over-SoS as a remark, section if the evaluator gets built;
(4) the one-liners opportunistically. §4 is parked, not prioritized. The
sister memos are separate papers, not paper sections.

## Status update (2026-07-11)

- Paper restructured (ten sections; renumber map in
  `sos_calculus_report.md` addendum). Item 3's **polynomial middle
  band** is now IN the paper (§4: `X L`, prefix-code `W·L`, free-AP
  drop); what remains of item 3 is the frontier family completion
  (direct images/transductions, shuffle, `lim`/`W^δ`).
- **Alphabet hygiene** (free-AP read-off + drop, equality up to AP
  renaming) landed in paper §3.2/§7.1; implementation is spec §9.3
  (CAL6).
- **DELA adequacy**: explored 2026-07-12, judged a spiral, PARKED (§4
  above). Paper §7.3 keeps the prospect wording; no work order stands
  except the spec §9.6 `D`-provenance paragraph.

## 6. GARBAGE (2026-07-12) — classification material excised from the paper

**We are not going this direction at all.** The paper had drifted into
doing its own classification — obligation via hull-generation (Thm 6.6),
Wagner degrees in the band (Prop 6.7), ladder / acceptance-index / Wagner
read-off bullets, and a measured census that duplicated the classification
paper's §8 profile (its rung counts are exact coarsenings of that table).
Classification is *diagnosis*, not an algebraic operator on the SoS; it
belongs to `sos_classification.md`, where all of it is already treated in
proper depth (§2.5 rung table, §3.3–3.4 chain/superchain engines, §4
derivative, §8 measured profile). Do NOT reintegrate any of this. The
paper keeps only the hull *operators* (Prop 6.1, Cor 6.2–6.3). Cut text
dumped verbatim below.

### From paper §6 (the obligation rung and its Wagner band)

First, the generated sublattice has a concrete description. The closed
pair sets of the table are exactly the sets

```
Q_S := { (s, e) ∈ linked : Reach(s) ∩ S ≠ ∅ },     S ⊆ linked stems,
```

where `Reach(s) := s·𝒞 ∩ (linked stems)` — Proposition 6.1 makes any
hull a `Q_S` (take `S = stems(P)`), and each `Q_S` is its own hull (by
transitivity of reachability). The Boolean subalgebra generated by the
`Q_S` is generated by the singletons `Q_{{t}}`, whose indicator on a
pair `(s, e)` is `[t ∈ Reach(s)]`; its atoms are therefore the fibers
of `(s, e) ↦ Reach(s)`. And `Reach(s) = Reach(s')` iff `s` and `s'`
divide each other on the right — Green's relation `R` (§2.2). So:

> `P` is **hull-generated** iff `Val_P(s, e)` depends only on the
> `R`-class of the stem `s` — in particular, not on the loop at all.

The Wagner-side characterization of obligation is classical: `L` is a
Boolean combination of open (equivalently closed) sets iff its Wagner
degree is finite, iff `m(L) = 0` — no chain of length 1 (§2.2), the
chains living in the syntactic ω-semigroup by the Carton–Perrin
normal form [CP97, Thm 6; Wag79; CP99, Thm 6 and Cor 7; SW08]. Two
lemmas take us from `m = 0` to stem-only verdicts. Throughout, note that if
`(s, e)` and `(s, f)` are linked then `s` absorbs the whole
subsemigroup `⟨e, f⟩` on the right: `s·(any product of e's and f's) = s`,
letter by letter — so every element of `⟨e, f⟩` below is again a loop
of `s`, and every conjugacy move fixes the stem.

**Lemma 6.4 (loops over one stem are connected).** Let `P` be
saturated with `m = 0`. Then `Val_P(s, e) = Val_P(s, f)` for every two
loops `e, f` of a common linked stem `s`.

*Proof.* Fix an idempotent `k` in the kernel (minimal ideal) `K` of
`⟨e, f⟩`, and set `g := (e·k·e)^π`, `g' := (f·k·f)^π`.

*Descent.* From `(eke)·e = ek(ee) = eke = e·(eke)` we get
`(eke)^m·e = (eke)^m = e·(eke)^m` for all `m ≥ 1`, so `g·e = e·g = g`:
`g ≤_H e`. Also `g ∈ K` (`K` is an ideal, closed under powers), and
`(s, g)` is linked by the absorption remark. If `g ≠ e`, the pair
`e >_H g` with differing verdicts would be a chain of length 1, so
`m = 0` forces `Val(s, g) = Val(s, e)`; likewise
`Val(s, g') = Val(s, f)`.

*Conjugacy in the kernel.* `T := ⟨g, g'⟩ ⊆ K` is completely simple: a
subsemigroup of a completely simple semigroup is completely simple
(for `t, u ∈ T`, `tut` lies in the group H-class of `t` in `K`, so
`(tut)^π` is that group's identity and `t = (tut)^π·t ∈ T·u·T`; thus
`T` is simple, and finite simple with idempotents is completely
simple). We exhibit `x, y ∈ T` with `x·y = g` and `y·x = g'`. If
`g R g'` or `g L g'` this is the classical pair of identities
(`g·g' = g'`, `g'·g = g` when `g R g'`; take `x = g'`, `y = g`, giving
`xy = g'g = g` and `yx = gg' = g'`; dually for `L`). Otherwise
normalize `T`'s Rees presentation (§2.2) over its rows `{1, 2}` and columns
`{1, 2}` so that the sandwich entries are
`p₁₁ = p₁₂ = p₂₁ = 1, p₂₂ = γ`, with `g = (1, 1, 1)` and
`g' = (2, γ⁻¹, 2)`. Then `x := g·g' = (1, γ⁻¹, 2)` and
`y := (g'·g)^{ord(γ)} = (2, 1, 1)` are in `T`, and

```
x·y = (1, γ⁻¹·p₂₂·1, 1) = (1, γ⁻¹γ, 1) = g,
y·x = (2, 1·p₁₁·γ⁻¹, 2) = (2, γ⁻¹, 2) = g'.
```

So the loop `g` factors as `x·y` with `y·x = g'`; by Proposition 3.1
the cells `(s, g)` and `(s·x, (y·x)^π) = (s, g')` carry one verdict
(the stem is fixed since `x ∈ ⟨e, f⟩`). Chaining:
`Val(s,e) = Val(s,g) = Val(s,g') = Val(s,f)`. ∎

(The kernel step is where chains alone are powerless: inside a
completely simple semigroup distinct idempotents are `H`-incomparable,
so `m = 0` says nothing there — and indeed `(e·k·e)^π = e` whenever
`e` itself lies in the kernel. It is *saturation* — the conjugacy law
of Proposition 3.1 — that connects the kernel loops. The conjugacy of
`D`-equivalent idempotents is classical; the point of the computation
is that `x, y` can be taken inside `⟨e, f⟩`, which is what keeps the
stem absorbed.)

**Lemma 6.5 (blind verdicts are `R`-invariant).** Let `P` be saturated
and loop-blind (`Val_P(s, e) =: θ(s)` for every loop `e` of `s`). Then
`θ(s) = θ(s')` whenever `s R s'`.

*Proof.* Write `s' = s·x`, `s = s'·y`. Then `E := (xy)^π` is a loop of
`s` and `(yx)^π` a loop of `s'`. Factor `E = X·Y` with
`X = (xy)^π·x`, `Y = y·(xy)^{π−1}`: then `X·Y = (xy)^{2π} = E` and
`Y·X = (yx)^{2π} = (yx)^π`. Proposition 3.1 sends the cell `(s, E)` to
`((s·X)·(yx)^π, (yx)^π) = (s', (yx)^π)`, so
`θ(s) = Val(s, E) = Val(s', (yx)^π) = θ(s')`. ∎

**Theorem 6.6 (the obligation rung is hull-generated).** For an
ω-regular `L` with syntactic invariant `(𝒞, λ, M, P)`, the following
are equivalent:

1. `L` is an obligation (Staiger–Wagner) property — a Boolean
   combination of safety properties;
2. `m(L) = 0`: no linked stem carries two `H`-comparable loops with
   different verdicts;
3. `Val_P(s, e)` depends only on the stem `s` — equivalently, only on
   the `R`-class of `s`;
4. `P` belongs to the Boolean sublattice of saturated pair sets
   generated by the closed pair sets of the table.

*Proof.* (1)⟺(2) is Wagner's theorem in the Carton–Perrin form: the
Boolean closure of the open ω-rational sets is exactly the finite
Wagner degrees, i.e. `m(X) = 0` [Wag79; CP99, Thm 6, Cor 7; SW08],
with chains transported to the syntactic ω-semigroup by [CP97, Thm 6].
(2)⟹(3): Lemma 6.4 gives stem-only; Lemma 6.5 upgrades stem-only to
`R`-class-only (saturation alone). (3)⟹(4): a loop-blind, `R`-constant
`P` is a union of the atoms of the generated subalgebra, by the
description above. (4)⟹(1): each `Q_S` is a safety language
(Proposition 6.1), and Boolean combinations of safety properties are
obligations by definition. ∎

Three consequences. **A read-off**: obligation membership — Spot's
`is_obligation`, answered there through weak-automaton realizability
constructions — is one scan: bucket the linked pairs by stem, check
each bucket is constant, check constancy across each `R`-class (the
strongly connected components of the right-Cayley graph):
`O(|linked| + n·|Σ|)`. **A normal form**: an obligation language is a
Boolean combination of the *canonical* closed sets `Q_{{t}}` of its
own table — no foreign safety constituents are ever needed. **A
boundary**: the lattice of hulls captures the safety-shaped hierarchy
*exactly up to* obligation; from the next rungs on (recurrence,
persistence and above), verdicts are provably loop-sensitive
(`m ≥ 1`), so no Boolean combination of fixpoints can express them —
the hull story is complete, not truncated. And the fine structure
*inside* the band comes for free — Wagner's superchain coordinates
`n±`, which stratify the obligation class by its difference level
`D_n(Σ₁)` and side `σ/π/δ` [Wag79, CP99], transcribe exactly to the
`θ`-labeled DAG:

**Proposition 6.7 (the Wagner degree of an obligation language, on
the DAG).** Let `m(L) = 0` and let `θ` be the stem verdict of
Theorem 6.6. For a polarity `b ∈ {0, 1}`, let `alt_b` be the maximal
`n` for which there exist linked stems
`s₀ ≥_R s₁ ≥_R ⋯ ≥_R s_n` (each `s_{i+1} ∈ s_i·𝒞`) with
`θ(s₀) = b` and `θ(s_i) ≠ θ(s_{i+1})` for all `i`. Then
`n⁺(L) = alt₁` and `n⁻(L) = alt₀`: the superchain coordinates are the
longest alternating paths in the `θ`-labeled `R`-class DAG, computable
in `O(n·|Σ|)` after the SCC pass of Theorem 6.6 (condense, then one
dynamic-programming sweep in reverse topological order per polarity).

*Proof.* (≤) By the superchain normal form [CP97, Thm 7], any
`X`-superchain of length `n` can be brought to chains
`C'_i = (s_i, E_i)` with every pair linked and the stems *strictly*
`R`-decreasing; with `m(L) = 0` each chain is a single linked pair,
the alternation of the chains' signs is alternation of
`Val(s_i, e_i) = θ(s_i)` (Theorem 6.6(3)), and a strictly
`R`-decreasing stem sequence is a path in the DAG of the required
shape. (≥) Conversely, an alternating path yields a superchain
directly: take `C_i = ({s_i}, (e_i))` for any loop `e_i` of `s_i` — a
chain of the required maximal length `0`, of sign `θ(s_i)`;
accessibility needs a nonempty word class `u_i` with
`s_i·u_i = s_{i+1}`, which exists
because `s_{i+1} ∈ s_i·𝒞` while `s_i R s_{i+1}` is impossible —
`R`-equivalent stems share `θ` (Lemma 6.5) and `θ` alternates. ∎

The running example closes its arc here. Every linked stem carries
loops of one verdict — `θ(A) = 0`, `θ(B) = θ(C) = 1`, `θ(D) = 0`,
buckets constant, `R`-classes singletons — so `a*·b^ω` *is* an
obligation (it is not closed: `a^ω` lies in its closure; not open:
its interior is empty; but it is `cl(L)` minus the closed set
`{a^ω}`). The `θ`-labeled DAG carries the alternating paths
`A → C → D` (`0, 1, 0`) and `C → D` (`1, 0`), so
`(n⁺, n⁻) = (1, 2)` — exactly the values computed by chain-juggling
in [CP97, Ex. 10], here a two-edge longest-path read-off.

### Scope note (2026-07-12) — publication plan and the stutter move

Plan: core → (calculus, classification) siblings → learn / toltl.
The two siblings each depend ONLY on core [SωS26] and never cite each
other. The calculus paper's tables keep exactly ONE classification row —
the LTL cut (aperiodicity), important downstream and trivial on the
table — and mention no other classification. **Stutter invariance was
NOT binned**: it moved to its proper home, `sos_classification.md` §3.2
(Proposition 3.1b there, full proof, [MD15] reference moved with it);
the V2 data (3938/3938 Spot agreement, 648 positives) stays in
`sos_calculus_report.md`.

### Other excised fragments (verbatim)

From paper §2.2 (toolkit that only served Thm 6.6 / Prop 6.7):

> On idempotents we use the natural order:
> `f ≤_H e` iff `e·f = f·e = f`.
>
> **The kernel.** Every finite semigroup has a least two-sided ideal `K`,
> its *kernel*, and `K` is completely simple: by Rees–Suschkewitsch it is
> isomorphic to a matrix semigroup over a group `G` — elements are
> triples `(i, g, λ)` (row, group element, column), multiplication is
> `(i, g, λ)·(j, h, μ) = (i, g·q_{λj}·h, μ)` with sandwich entries
> `q_{λj} ∈ G`, and every subsemigroup of a completely simple semigroup
> is completely simple. Lemma 6.4 computes inside one such presentation;
> only the multiplication rule is needed.
>
> **Chains and the Wagner coordinates.** Fix a saturated pair set `P` on
> the table. A *chain of length `n`* is a linked stem `s` carrying
> idempotent loops `e₀ >_H e₁ >_H ⋯ >_H e_n` whose verdicts
> `Val_P(s, e_i)` alternate; its *sign* is the first verdict. `m⁺(L)`
> (resp. `m⁻(L)`) is the maximal length of a chain of sign 1 (resp. 0),
> with the convention `m^b = −1` when no linked pair of verdict `b`
> exists at all, and `m(L) = max(m⁺, m⁻)`. A *superchain of length `n`*
> is a sequence of chains `C₀, …, C_n` of alternating signs whose stems
> are strictly `R`-decreasing and successively accessible
> (`s_{i+1} ∈ s_i·𝒞`); `n⁺(L)` / `n⁻(L)` are the maximal lengths of
> superchains of first sign 1 / 0. These coordinates, evaluated in the
> syntactic ω-semigroup, determine the Wagner degree of `L`
> [Wag79, CP97, CP99, SW08]. §6 imports exactly two facts from that
> theory: `m(L) = 0` iff `L` is a Boolean combination of open sets
> (Wagner's theorem in the Carton–Perrin form [CP99, Thm 6, Cor 7]), and
> the superchain normal form [CP97, Thm 7].

From paper §5 (the classification-battery bullets — all of this is
classification-paper territory, see its §2.5 / §3.3–3.5 / §4):

> - **The safety–progress ladder** (safety, co-safety/guarantee,
>   obligation, recurrence, persistence, reactivity): each rung is a
>   closure condition on the accepting set `P` over the linked-pair
>   structure [SωS26, §7.2; Lan69, MP92, PW13] — Spot's `is_safety`,
>   `is_obligation`, … as scans, uniform over one object where the
>   automata-side answers are model-specific checks.
> - **Acceptance strength needed** (Spot's parity/Rabin-index style
>   queries): the acceptance index — the minimal deterministic condition
>   the *language* needs — is the maximal alternating chain in the
>   algebra, computable in the syntactic ω-semigroup by Carton–Perrin
>   [CP97, Cor. 1]; a property of the language, not of a chosen condition.
> - **Wagner degree**: the complete classification up to Wadge
>   reducibility is fixed by the chain and superchain structure of the
>   algebra [CP97, CP99, SW08]; every hierarchy query above specializes
>   it.

From paper §7.1 (ledger rows dropped):

> | stutter-invariance | `cl`/`sl` closures + product emptiness [MD15] | `λ(a)² = λ(a)` scan (Prop 5.1) |
> | safety/obligation/… tests | model-specific checks | safety/co-safety: `P = P̄` / `P = P̊` (Cor 6.2); obligation: stem-only verdict scan (Thm 6.6) |
> | acceptance index / Rabin index | condition transforms + tests | alternating-chain read-off [CP97] |

From paper §7.2 (cost rows dropped):

> | stutter-invariance | `O(|Σ|)` | bit (Prop 5.1) |
> | obligation test | `O(|linked| + n·|Σ|)` | bit (Thm 6.6: stem-only verdict) |
> | Wagner degree within the obligation band | `O(n·|Σ|)` after SCCs | `(n⁺, n⁻)` = longest alternating DAG paths (Prop 6.7) |
> | ladder / index / Wagner read-offs | polynomial scans of the table | verdicts [SωS26, §7.2] |

From paper §8.5 (the V2 stutter bullet, the obligation/degree bullet,
and the V4 battery bullet — the battery's rung census was an exact
coarsening of the classification paper's §8 profile; the F-series data
stays in `sos_calculus_report.md`, which remains their source of
truth):

> - *Stutter invariance* (Prop 5.1) against Spot's
>   `is_stutter_invariant` [MD15], on the 3938-language edition:
>   agreement on **3938 / 3938**, zero disagreements. 648 corpus
>   languages are stutter-invariant — 16.5% of the corpus, 28.9% of its
>   LTL-definable class, and every one of them LTL-definable.
> - *Obligation and degree* (Thm 6.6, Prop 6.7): the one-scan verdict and
>   the `(n⁺, n⁻)` longest-path read-off agree, on every corpus language,
>   with Wagner coordinates computed independently by chain and
>   superchain search — the calculus reading off in one SCC pass what
>   the classification side establishes by chain juggling.
> - *The classification battery against Spot*, on the full 6222-language
>   edition. The comparison had to be built: Spot 2.14 has **no
>   automaton-level Manna–Pnueli classifier** — `mp_class`,
>   `is_obligation` and kin are formula-level, the automaton only an
>   optional accelerator, and translation is no escape because 2484 of
>   the 6222 corpus languages are not LTL-definable, so no formula
>   exists to pass. The automaton-level oracle assembled instead is
>   language-level and exact: safety by Spot's acceptance-trivialization
>   fixpoint, co-safety by the same test on the dual (the inputs are
>   deterministic and complete, so dualizing complements), obligation by
>   WDBA-minimization plus equivalence — the inside of Spot's own
>   obligation check, minus the formula; the oracle is pinned against
>   `mp_class` on formulas of known class before use. Against it, the
>   algebraic scans agree on **6222 / 6222** languages, on all three
>   verdicts (safety, co-safety, obligation; 1514 / 1514 / 3182
>   positives), with an empty disagreement dossier. The rung census:
>   51.1% of the corpus is obligation — 84 bottom, 1430 safety-only,
>   1430 co-safety-only (equal by complement-closure, a printed
>   consistency check), 238 properly obligation — and **46.7% of the
>   obligation rung is not LTL-definable**: the ladder is topological,
>   the LTL cut is aperiodicity, and this is what makes the formula
>   route a dead end rather than an inconvenience. The degree read-off
>   stratifies the rung exactly (degree ≤ 0 ⟺ bottom, `(1,0)` ⟺ S,
>   `(0,1)` ⟺ G, above ⟺ O, with the histogram symmetric under polarity
>   swap on every entry) and has no Spot counterpart at all — Spot
>   decides the rung but does not measure the superchain. Timings are
>   reported and not sold: everything on both sides is sub-10-µs on
>   tables of median 15 classes (Spot faster on safety and co-safety,
>   slower on obligation — the one test where it builds and minimizes an
>   automaton while the scan stays linear in the held table); the
>   asymptotics, not the clock, are the claim.

From paper §9 (related-work paragraph dropped):

> **Hierarchy computations on the algebra.** That the Wagner hierarchy is
> computable in the syntactic ω-semigroup is Carton–Perrin [CP97, CP99],
> completed by Selivanov–Wagner's complexity analysis [SW08]; Landweber's
> ladder [Lan69] and its effective characterizations on canonical automata
> [PW13] are the automata-side counterparts. §5–§6 claim none of these
> results — they claim their *placement*: on one shared table, as scans
> among other scans, downstream of one entry price.

References dropped from the paper (no longer cited there): [CP99],
[Lan69], [PW13], [SW08], [Wag79]; [MD15] moved to the classification
paper with the stutter proposition.
