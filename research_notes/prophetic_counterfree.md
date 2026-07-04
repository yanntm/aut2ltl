# Counter-Free Prophetic Automata Characterize Star-Free ω-Languages

**Claude (Anthropic)** and **Yann Thierry-Mieg**

*Working draft — 2026-07-04*

## Abstract

Over finite words, Schützenberger's theorem has a clean automaton-theoretic
face: a language is star-free (equivalently first-order or LTL definable) if and
only if the transition monoid of its *minimal deterministic automaton* is
aperiodic, i.e. the automaton is counter-free (McNaughton–Papert). Over infinite
words this bridge breaks at the automaton level: there is no canonical minimal
deterministic ω-automaton, and — as observed by Diekert and Gastin — a
minimal-size automaton of a star-free ω-language need not be counter-free. The
obstruction is real: forward determinism can force a group into the transition
monoid (e.g. a parity bit) that the language itself does not possess.

We observe that the bridge is *restored* if one replaces the (nonexistent)
minimal deterministic automaton by the canonical **prophetic** (Carton–Michel)
automaton, which is co-deterministic. Concretely, let `A_S` be the Carton–Michel
automaton built from the syntactic ω-semigroup `S` of an ω-regular language `L`.
We prove that **`A_S` is counter-free if and only if `S₊` is aperiodic, i.e. if
and only if `L` is star-free.** As a corollary, the per-state *loop languages* of
`A_S` — the "infinitary fraction" in the sense of Preugschat–Wilke, i.e. the
per-state recurrence conditions — are all star-free whenever `L` is. The proof is
short: the two coordinates of a Carton–Michel state each carry an action by
left-multiplication in `S₊`, and aperiodicity of `S₊` propagates to both, using
Carton and Michel's cutting-transition lemma to control the chain-expansion
coordinate.

The result gives the "right" canonical object for the star-free/counter-free
correspondence over infinite words, and explains a phenomenon observed while
studying automaton-to-LTL translation: per-state recurrence questions on a
star-free language are language invariants, definable in LTL, even though a
particular deterministic presentation may encode them with a group.

---

## 1. Introduction

**Motivation.** This note grew out of an empirical puzzle in the implementation
of the Boker–Lehtinen–Sickert (BLS) translation from deterministic ω-automata to
LTL [BLS22]. That construction is proved correct for *counter-free* input
automata; its technical core builds, for each configuration `C` of a reset
cascade, an LTL formula for "`C` is visited only finitely often" (`Fin(C)`), and
composes these into the output formula. In practice the implementation runs the
construction on minimized deterministic parity automata that are frequently *not*
counter-free — their transition monoids carry groups — and yet it produces
correct LTL on every star-free (LTL-definable) input we could check. The obvious
explanation, "minimization removes the groups," is false: minimal deterministic
ω-automata of star-free languages can and do carry groups. The correct
explanation must instead be that the *sub-questions* the construction asks —
per-state and per-configuration recurrence languages of the form "state `q` is
visited infinitely often" — remain star-free even when the transition monoid does
not. That is a statement about a canonical object, not about a particular
deterministic presentation, and it is the statement this note isolates and
proves.

**The finite-word picture.** For languages of finite words the situation is
completely understood. Schützenberger [Sch65] characterized the star-free
languages as those whose syntactic monoid is aperiodic (group-free); McNaughton
and Papert [MP71] gave the automaton face: `L ⊆ A*` is star-free iff its *minimal
deterministic automaton* is counter-free (no word induces a nontrivial
permutation of any reachable subset of states). The minimal DFA is canonical, so
"counter-free" is a well-defined property of the language.

**The infinite-word gap.** Over infinite words the algebraic characterization
survives verbatim — an ω-regular language is star-free iff its syntactic
ω-semigroup is aperiodic [Tho79, PP04, CPP08] — but the automaton face does not
transfer, for a structural reason. As Diekert and Gastin note ([DG08],
Remark 11.13): *there is no canonical minimal Büchi automaton for languages of
infinite words*, and a minimal-size automaton of a star-free ω-language need not
be counter-free. Their notion of a counter-free Büchi automaton does characterize
star-freeness ([DG08], Prop. 11.11: `L` star-free iff some counter-free Büchi
automaton accepts it), but the counter-free witness they construct is neither
canonical nor, in general, deterministic. Determinism is exactly the culprit: to
*detect* an ω-property a forward-deterministic automaton may have to track
transient positional information, and that tracking can be a genuine group in the
transition monoid even when the language is aperiodic.

*Example.* The language `GF(a ∧ Xa)` ("infinitely many `aa`-adjacencies") is
star-free, yet it has a minimal deterministic parity presentation whose
transition monoid contains a `ℤ₂` (a parity bit toggled every step). The group is
an artifact of forward determinism, not of the language: the language's syntactic
ω-semigroup is aperiodic.

**This note.** We point out that the correspondence is restored by changing the
canonical object. The *prophetic* automata of Carton and Michel [CM03] — the
co-deterministic, co-complete Büchi automata in which every infinite word labels
exactly one accepting run — are canonical when built from the syntactic
ω-semigroup, and they are backward- rather than forward-deterministic. We prove
(Theorem 1) that the Carton–Michel automaton `A_S` of `L` is counter-free iff the
syntactic `S₊` is aperiodic, iff `L` is star-free. The counter-example above
dissolves: the co-deterministic canonical form of `GF(a ∧ Xa)` carries no group.

As a corollary (Corollary 2), the per-state *loop languages* of `A_S` — Preugschat
and Wilke's [PW13] representation of the "infinitary fraction" of `L`, i.e. the
per-state recurrence conditions — are star-free whenever `L` is. This is the
language-invariant fact behind the empirical observation about the BLS
implementation: recurrence questions of a star-free language are themselves LTL
definable, on the canonical object.

**What is new.** Every ingredient is classical: the Carton–Michel construction
[CM03], the aperiodic/star-free equivalence [Sch65, Tho79], and Diekert–Gastin's
deterministic-vs-nondeterministic counter-freeness [DG08]. The observation that
combining them yields a *canonical, counter-free* automaton for exactly the
star-free ω-languages — the precise ω-analogue of McNaughton–Papert — does not
appear to be recorded, and it is what we make explicit. The proof is elementary
given the construction.

---

## 2. Preliminaries

We fix a finite alphabet `A`. `A*` (`A⁺`) is the set of finite (nonempty finite)
words, `Aᵂ` the set of infinite words.

**Star-free languages.** The star-free subsets of `Aᵂ` are those built from the
`⟨U⟩ᵂ` and `U·⟨V⟩ᵂ`-style expressions using boolean operations and concatenation
without Kleene star; equivalently the languages definable in first-order logic
`FO(<)`, equivalently in future LTL [Tho79, GPSS80]. We use the algebraic
characterization as the working definition.

**ω-semigroups and linked pairs.** An ω-semigroup is a two-sorted algebra
`S = (S₊, S_ω)` with an associative product and an infinite product compatible
with it [PP04, CPP08]. A morphism `φ : A⁺ → S₊` recognizes `L ⊆ Aᵂ` if
`L = φ⁻¹(P)` for a set `P` of behaviours. A **linked pair** of the finite
semigroup `S₊` is a pair `(s, e)` with `se = s` and `e² = e`; by Ramsey's theorem
every infinite word admits a *Ramseyan factorization* `x = x₀x₁x₂…` with
`φ(x₀) = s`, `φ(xₙ) = e` (`n ≥ 1`) for some linked pair, and the pair is unique up
to **conjugacy** (`(s₁,e₁) ∼ (s₂,e₂)` iff they generate overlapping ω-behaviours;
[CM03], Prop. 60). We write `S̃` for the set of conjugacy classes and `[s,e]` for a
class; `φ` extends to `φ : Aᵂ → S̃`. There is a well-defined left action
`a · [s,e] = [φ(a)s, e]` ([CM03], §6.3.1). Every ω-regular `L` has a *syntactic*
ω-semigroup, the minimal recognizer, and **`L` is star-free iff `S₊` is
aperiodic** (contains no nontrivial subgroup) [Tho79, PP04].

**Counter-free automata.** Following Diekert–Gastin [DG08], a Büchi automaton
`A = (Q, A, δ, I, F)` (with transition relation `δ`, `L_{p,q}` the set of finite
words labelling `p→q` paths) is **counter-free** if for all `p ∈ Q`, `u ∈ A⁺`,
`m ≥ 1`: `uᵐ ∈ L_{p,p} ⟹ u ∈ L_{p,p}`. The definition depends only on the
transition structure, and is invariant under reversal of all transitions. For a
**deterministic** automaton counter-freeness is equivalent to aperiodicity of the
transition monoid ([DG08], Lemma 11.6): if `A` is deterministic and its
transition monoid is aperiodic then `A` is counter-free, and counter-freeness
always implies aperiodicity of the transition monoid.

**Carton–Michel (prophetic) automata.** A Büchi automaton is **prophetic** (a
Carton–Michel automaton) if every infinite word labels *exactly one* accepting
run [CM03, PW13]. Equivalently it is co-deterministic and co-complete. The main
theorem of [CM03] is that every ω-regular language is recognized by a prophetic
automaton. For a state `q`, a word `u ∈ A⁺` is a **loop at `q`** if `u·q = q` and
`u` labels a path through a final transition; the set of loops at `q` is `S(q)`,
and by the anchor lemma ([CM03], Lemma; [PW13], Lemma 2.2) the `S(q)` **partition
`A⁺`**. Preugschat and Wilke [PW13] define the **loop language**
`LL(q) = ⋃_{q' ≡ q} S(q')` (union over the left-congruence class of `q`) and show
that the left quotient of a prophetic automaton captures the "finitary fraction"
of `L` while the loop languages capture its "infinitary fraction" — the per-state
recurrence conditions.

**The construction `A_S` [CM03, §6.3.3].** Given a morphism `φ : A⁺ → S₊`
recognizing `L = φ⁻¹(P)`, Carton and Michel build a prophetic automaton `A_S`
whose states are pairs

```
Q = { ([s,e], (s₁,…,sₙ)) ∈ S̃ × Ŝ  :  s R sₙ } ,
```

where `S̃` is the set of linked-pair conjugacy classes and `Ŝ` is the set of
**strict R-chains** of `S₊` (sequences strictly decreasing for the R-order,
finite because their length is bounded by `|S₊|`). A letter `a` acts on both
coordinates by left-multiplication by `φ(a)`:

```
a · [s,e]        = [ φ(a)s , e ]
a · (s₁,…,sₙ)    = = ( φ(a), φ(a)s₁, …, φ(a)sₙ )
```

where `=` is the R-order reduction that deletes an element R-equivalent to its
left neighbour ([CM03], §6.3.2). The automaton is co-deterministic and complete;
a distinguished set of transitions is final. Running `A_S` on `x = a₀a₁a₂…`, the
unique accepting run visits, at position `i`, the state `(φ(xᵢ), φ̂(xᵢ))` where
`xᵢ = aᵢaᵢ₊₁…` is the suffix and `φ̂` is the (non-morphic) chain map — so the
state is a function of the *future*, the defining property of a prophetic
automaton.

When `φ` is the syntactic morphism of `L`, we call `A_S` the **canonical
prophetic automaton** of `L`.

The one lemma of [CM03] we use is the control on the chain coordinate:

> **Lemma ([CM03], Prop. 70).** For any finite word `w` and any strict chain
> `c ∈ Ŝ`: if the path `w · c` contains more than `|c|` cutting transitions, then
> `w · c = φ̂(w)`.

Here a step is *cutting* when the R-order reduction `=` discards the newly
produced last element; since chains have length at most `|S₊|`, a period that
never cuts would grow the chain without bound, so cutting transitions are forced
to accumulate along any sufficiently long run.

---

## 3. Result

Throughout, `L ⊆ Aᵂ` is ω-regular, `φ : A⁺ → S₊` its syntactic morphism, and
`A_S` the canonical prophetic automaton of §2. Let `M(A_S)` be the transition
monoid of `A_S` (the monoid of maps on `Q` generated by the letter actions;
because `A_S` is co-deterministic these are partial, but counter-freeness is a
statement about loops and is reversal-invariant, so we may argue on the monoid
directly).

> **Theorem 1.** `A_S` is counter-free if and only if `S₊` is aperiodic — that
> is, if and only if `L` is star-free.

**Proof.**

*(⟸) `S₊` aperiodic ⟹ `A_S` counter-free.* It suffices to show `M(A_S)` is
aperiodic: for a co-deterministic automaton this is equivalent to counter-freeness
by [DG08], Lemma 11.6 applied to the (deterministic) reverse automaton, using that
counter-freeness is reversal-invariant. We show that for every `u ∈ A⁺` the
`u`-action stabilizes, `uⁿ = uⁿ⁺¹` in `M(A_S)` for all large `n`, coordinate by
coordinate.

- *First coordinate (linked pairs).* The `u`-action sends `[s,e]` to
  `[φ(u)s, e]`, so `uⁿ · [s,e] = [φ(u)ⁿ s, e]`. Since `S₊` is aperiodic there is
  `N₁` (e.g. `N₁ = |S₊|`) with `φ(u)ⁿ = φ(u)ⁿ⁺¹` for `n ≥ N₁`, whence
  `uⁿ·[s,e] = uⁿ⁺¹·[s,e]`. (This coordinate is precisely a left-regular action
  of `S₊`; it is where a group in `S₊` would obstruct aperiodicity.)

- *Second coordinate (chains).* Fix a chain `c ∈ Ŝ`. Along the run
  `c, u·c, u²·c, …`, cutting transitions accumulate (a non-cutting period would
  grow the chain past the bound `|S₊|`), so there is `N₂` such that for `n ≥ N₂`
  the path `uⁿ · c` contains more than `|c|` cutting transitions; by
  [CM03] Prop. 70, `uⁿ · c = φ̂(uⁿ)`. Finally `φ̂(uⁿ)` is eventually constant in
  `n`: it is the strict R-chain of the sequence `φ(u), φ(u²), φ(u³), …`, which is
  R-decreasing and, by aperiodicity of `S₊`, R-stabilizes at the idempotent
  `φ(u)^π = φ(u)^{|S₊|}`. Hence there is `N₃ ≥ N₂` with `uⁿ·c = uⁿ⁺¹·c` for all
  `n ≥ N₃`, and `N₃` does not depend on the starting chain `c`.

Taking `N = max(N₁, N₃)` gives `uⁿ = uⁿ⁺¹` in `M(A_S)` for `n ≥ N`, for every
`u`. So `M(A_S)` is aperiodic and `A_S` is counter-free.

*(⟹) `A_S` counter-free ⟹ `S₊` aperiodic.* By [DG08], Lemma 11.6.1, a
counter-free automaton has an aperiodic transition monoid, so `M(A_S)` is
aperiodic. The first-coordinate action realizes the left-regular representation
of `S₊` (the maps `[s,e] ↦ [ts,e]` for `t ∈ φ(A⁺) = S₊`), which is a divisor of
`M(A_S)`; aperiodicity is inherited by division, so `S₊` is aperiodic. By the
syntactic characterization of star-freeness [Tho79, PP04], this is equivalent to
`L` being star-free. ∎

> **Corollary 2 (loop languages are star-free).** If `L` is star-free, then every
> loop language `LL(q)` of `A_S` is a star-free language of finite words.

**Proof.** Fix a state `q`. The loop set `S(q) = { u ∈ A⁺ : u·q = q and some
factorization `u = vw` has `w·q` final }` is recognized by `M(A_S)` enriched with
a single monotone boolean recording whether a final transition has been crossed:
the enrichment is a cascade of the aperiodic `M(A_S)` with the two-element
"latch" monoid `U₁` (once true, stays true), which is aperiodic and introduces no
group, so the enriched monoid is aperiodic. A language recognized by an aperiodic
monoid is star-free (Schützenberger [Sch65]); hence `S(q)` is star-free. By
Theorem 1 `M(A_S)` is aperiodic when `L` is star-free, so this applies, and
`LL(q) = ⋃_{q' ≡ q} S(q')` is a finite union of star-free languages, hence
star-free. ∎

**Remarks.**

1. *Canonicity.* `A_S` built from the *syntactic* ω-semigroup is canonical, as
   the syntactic ω-semigroup is. Theorem 1 is therefore a property of the
   language, not of a presentation — unlike counter-freeness of a deterministic
   automaton, which by [DG08] Remark 11.13 is not determined by the language for
   minimal-size deterministic ω-automata.

2. *The group is a forward-determinism artifact.* Theorem 1 pinpoints where a
   group can hide. In any deterministic recognizer of a star-free `L` the residual
   (right-congruence) monoid divides `S₊` and is aperiodic, so a group in the
   transition monoid must live inside a single residual class — it tracks
   transient information used to *detect* the acceptance condition, not to
   distinguish futures. The co-deterministic canonical form keys on the future
   directly and never needs such tracking, which is why it stays counter-free.

3. *Sanity checks.* For `L = a·Aᵂ` the syntactic semigroup is the left-zero
   semigroup (aperiodic) and `A_S` is counter-free; for `L = GF(b)` it is `U₁`
   (aperiodic) and `A_S` is counter-free ([CM03], Examples 72–73). For the modular
   language "the number of `a`'s before stabilization is `≡ 0 mod 3`" the syntactic
   `S₊` contains `ℤ₃` and `A_S` is not counter-free, matching non-star-freeness.

---

## 4. Discussion

**Placement.** Theorem 1 is the ω-word counterpart of McNaughton–Papert, with the
canonical prophetic automaton in the role the minimal DFA plays over finite words.
Diekert and Gastin [DG08] establish that star-freeness of an ω-language is
equivalent to acceptance by *some* counter-free Büchi automaton, and observe that
no *minimal deterministic* automaton can serve as a canonical counter-free
witness. Theorem 1 supplies a canonical witness after all — one must only pass to
the co-deterministic side. Preugschat and Wilke [PW13] develop, for *fragments*
of LTL, effective characterizations phrased as separate conditions on the left
quotient (finitary fraction) and the loop languages (infinitary fraction) of a
prophetic automaton; their tables stop below full LTL. Corollary 2 is the
"top-of-the-lattice" instance those tables omit: for the full star-free class,
the loop languages are exactly the star-free languages of finite words, and the
left quotient is counter-free.

**Consequence for automaton-to-LTL translation.** The motivating puzzle resolves
as follows. Per-state (and per-configuration) recurrence questions of a star-free
language — "is `q` visited infinitely often" — are the loop languages of the
canonical prophetic form, and Corollary 2 makes them star-free, hence LTL
definable, as *language invariants*. Any correct translation that internally
computes such recurrence conditions is therefore asking questions that always have
LTL answers, independent of whether the particular deterministic presentation it
runs on is counter-free. This does not by itself prove any specific
implementation correct on a specific (possibly non-canonical) deterministic input
— that requires relating the presentation's recurrence structure to the canonical
loop languages — but it identifies the invariant that makes such correctness
possible and locates the residual obligation precisely.

**Limits and open ends.**

- Theorem 1 is stated for the canonical `A_S`. A non-syntactic recognizing
  semigroup may carry a group even for star-free `L`, and then `A_S` need not be
  counter-free; canonicity (the syntactic choice) is essential.
- The bridge to a *forward-deterministic* presentation `D` of `L` is left open:
  when does a state-minimal deterministic parity automaton's configuration
  recurrence inherit star-freeness from the canonical loop languages? A minimal
  deterministic form can carry a forward-determinism group (Remark 2), and a
  non-minimal one can make a recurrence language genuinely non-star-free while `L`
  stays star-free, so any such bridge must use state-minimality.

---

## 5. Conclusion

Over infinite words the star-free/counter-free correspondence does not fail; it
merely requires the correct canonical object. The minimal deterministic automaton,
which serves over finite words, does not exist canonically for ω-languages and can
carry groups a star-free language does not have. The canonical **prophetic**
automaton, built from the syntactic ω-semigroup, restores the correspondence
exactly: it is counter-free iff the language is star-free (Theorem 1), and its
per-state loop languages — the recurrence conditions — are star-free whenever the
language is (Corollary 2). The proof is a two-line propagation of aperiodicity
through the two coordinates of a Carton–Michel state, using Prop. 70 of [CM03] to
tame the chain expansion. The result is the ω-analogue of McNaughton–Papert on the
object where it belongs, and it isolates the language-invariant behind the
practical success of counter-freeness-assuming automaton-to-LTL translators on
inputs whose presentations are not counter-free.

---

## References

- **[BLS22]** U. Boker, K. Lehtinen, S. Sickert. *On the Translation of Automata
  to Linear Temporal Logic.* FoSSaCS 2022.
- **[CM03]** O. Carton, M. Michel. *Unambiguous Büchi automata.* Theoretical
  Computer Science 297 (2003) 37–81.
- **[CPP08]** O. Carton, D. Perrin, J.-É. Pin. *Automata and semigroups
  recognizing infinite words.* 2008.
- **[DG08]** V. Diekert, P. Gastin. *First-order definable languages.* 2008.
  (Counter-free Büchi automata; Prop. 11.11, Lemma 11.6, Remark 11.13.)
- **[GPSS80]** D. Gabbay, A. Pnueli, S. Shelah, J. Stavi. *On the temporal
  analysis of fairness.* POPL 1980. (LTL = FO over ω-words.)
- **[MP71]** R. McNaughton, S. Papert. *Counter-Free Automata.* MIT Press, 1971.
- **[PP04]** D. Perrin, J.-É. Pin. *Infinite Words: Automata, Semigroups, Logic
  and Games.* Elsevier, 2004.
- **[PW13]** S. Preugschat, T. Wilke. *Effective Characterizations of Simple
  Fragments of Temporal Logic Using Carton–Michel Automata.* LMCS 9(2:08) 2013.
- **[Sch65]** M. P. Schützenberger. *On finite monoids having only trivial
  subgroups.* Information and Control 8 (1965) 190–194.
- **[Tho79]** W. Thomas. *Star-free regular sets of ω-sequences.* Information and
  Control 42 (1979) 148–156.
