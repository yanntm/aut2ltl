# The cascade ladder: the loop side beyond windows and parks

**Working note toward a new section of `sos_toltl.md`** — drafted standalone,
numbered `C.*` throughout so it can land as its own section (proposed
placement: between §5 and §6, as §5′ "The cascade ladder"; the only touch to
existing text would be pointer sentences at §4.4, §5.1's residual bullet,
step 4 of §5.4, the residual row of Table 2, and §9's cascade paragraph).
Source construction: U. Boker, K. Lehtinen, S. Sickert, *On the Translation
of Automata to Linear Temporal Logic*, FoSSaCS 2022 [BLS22] — implemented in
this repository as `aut2ltl/bls` (reset-cascade via GAP/SgpDec holonomy,
reach-formula family, `Fin(C)` acceptance encoding).

*Working draft — placeholders marked ⟨TBD⟩. Revised after the K-E0
gate (see `bls_cascade_report.md`, K-F1/K-F2): the completeness
conjecture C.12 and its sandwich reduction C.17 are **refuted** — by
the residual floor witness itself, whose canonical invariant is not
what the first draft's hand derivation (run in the profile monoid, not
its syntactic quotient) said it was. C.3's worked witness is now
`G(a → F b)`; the floor witness moves to C.5 as the fallback's worked
instance; C.4 states the refutation and the no-go it yields. Second
revision: the K-E1–E4/E7 measurements integrated (K-F7–K-F11). Third
revision (the extended corpus — 6 222 languages, Wagner ceiling
ω³/ω⁴): the coverage, mechanism and one-sidedness numbers re-based
(K-F7/K-F8/K-F10); Cor C.9's census read-off promoted to
Theorem C.9′ (prefix-independence freezes the terminal layers — no
aperiodicity needed); the every-width criterion Theorem C.12″ added;
the Lemma C.5(i) second-strictness ⟨TBD⟩ discharged; and the floor
claim REVERSED (K-F12): the earlier cut's "zero conflicts" was a
property of its ω² Wagner ceiling, not of the census axis — the
extended frame inhabits the floor track in bulk, type specimen on
paper.*

---

## C.0 The gap this section closes

Two strata of the extraction still pay the generic DG price (§2.3): the stem
side's no-width layers (§4.4 — scoped to the layer action monoid, tolerable),
and the loop side's residual stratum (§5.1), where the fallback "DG on the
tail algebra" is broken by design: the tail algebra is *not smaller* —
`T_c = L` whenever `L` is prefix-independent (Lemma 5.2(ii), the no-recursion
trap) — and DG's ω-level wrapper recurses on the language itself. The paper's
main open problem, an ω-specific descent beating DG on that stratum, lives
exactly there, with the named instance `GF(a ∧ X((!a∧!b) U a))`.

[BLS22] translates a counter-free deterministic automaton to LTL through a
Krohn–Rhodes reset cascade, and its structural trick is the one to import:
**it never recurses on the language for the ω-part.** Its entire ω-content is
a family of `Fin(C)` atoms — "configuration `C` of the cascade is visited
finitely often", a `Σ₂` formula built from finite-prefix reachability — and
the acceptance condition is a Boolean combination of them, chosen per
acceptance class (Büchi `⋁ ¬Fin`, co-Büchi `⋀ Fin`, Muller the exact-set
product). The descent is on the *machine* (cascade levels), never on the
language or its algebra, which is precisely how it escapes the trap that
stops DG on prefix-independent tails.

The construction is worse than the transcription engine *in general* — it
manufactures a cascade blindly (up to `2ⁿ` levels, [BLS22, Prop 6]) where
§4 reads the layer structure off the canonical object. But the two are not
rivals; C.1 shows the transcription engine's loop side *is* a BLS encoding on
a degenerate cascade, and the rest of the section extends the ladder along
the axis BLS opens: from pure-reset memory (windows) through one
identity-bearing level (parks) to the full configuration machine (this
section), with the manufactured cascade as the terminal fallback that
retires DG from the loop side entirely.

What the extension does *not* do is close the open problem. C.4 proves
the ladder has a floor, and the floor is the named instance itself:
on the canonical invariant the floor witness's loop content sits on a
frozen layer, where configurations collapse to windows (Lemma C.10)
and §5.1's window-blindness kills every width. The section's yield is
therefore three-fold: a strictly stronger rung with real width gains
(condition (C), worked on `G(a → F b)` at width 0); a refutation with
an exact algebraic localization (the sandwich identity fails
aperiodically, by zero absorption — C.4); and the promotion of the
C.5 fallback from transitional to load-bearing, with the floor witness
as its worked instance.

## C.1 The reset-cascade reading of the existing engine

Fix a layer `R` with entry classes as in §4.2, over the quotient alphabet
`Σ_λ`. Recall from [BLS22] (§4.1 of its construction): a *reset
semiautomaton* is one where every letter acts as the identity or as a
constant ("reset"); a *reset cascade* is a sequence of levels, each a reset
semiautomaton reading the letter together with the states of all lower
levels; per level-state `q` the combined letters split into
`Enter(q) ⊆ Stay(q)` and `Leave(q) = Stay(q)^c`.

**Definition C.1 (confined machine; shift register).** The *confined
machine* `A_R = (R, Σ_λ, ·)` is the partial deterministic semiautomaton of
the layer's within-layer actions: `q·a` defined iff `q·a ∈ R`
(Proposition 4.11(i) makes the partial composition associative on confined
words). The *width-`k` shift register* `SR_k` is the semiautomaton with
states `Σ_λ^{≤k}`, transition `push`: append the letter, keep the last `k`.

**Proposition C.2 (the Rosetta).** (i) `SR_k` is a pure-reset cascade of `k`
levels — level 1 resets to the letter read, level `i` resets to level
`(i−1)`'s state; every combined letter is a reset, no identity letters — and
on any tail `β` its recurring-state set is exactly `Win_k(β)`. Consequently
**condition (B) at width `k` says precisely that the verdict on confined
tails factors through the recurring-state set of the pure-reset cascade**,
and Proposition 5.4's exact-set form is [BLS22]'s Muller encoding
`⋀_{C∈G} ¬Fin(C) ∧ ⋀_{C∉G} Fin(C)` over `SR_k`, with the `Fin` atoms
collapsed: `SR_k` is synchronizing (any `k` letters determine the state), so
"at state `w` now" is the letter pattern `ŵ` and `¬Fin(w)` collapses from
`Σ₂`-with-reach-recursion to `GF ŵ`, `Fin(w)` to `FG ¬ŵ`.

(ii) A layer is **1-anchored (Definition 4.4) iff `A_R` is a partial reset
semiautomaton** — anchors are the resets, stutters the identities, the
diagonal allowance is `Enter(q) ⊆ Stay(q)`. Condition (A) at width 1 is the
statement that the canonical machine carries a KR reset level on its own
R-class, no decomposition manufactured (§4.2's remark, now an equivalence).

(iii) The park brick `F(An(d) ∧ X G St(d))` and [BLS22]'s
`Fin(C) = ¬reach(ι,C) ∨ reach(ι, C, ¬reach⁺(C,C))` are the two polarities of
one *last-event idiom* — "there is a last entry, never left" / "there is a
last visit, never re-entered" — both instances of the template
`reach(·, target, "never-again")`.

*Proof.* (i) States of `SR_k` after `≥ k` letters are exactly the last-`k`
windows, each visited at the positions where its word ends; the `≤ k`
warm-up states occur once each and drop out of every recurring set. A
recurring-state set is therefore a recurring-window set, and Definition 4.8
quantifies over exactly that. The cascade presentation and the collapse are
displayed. (ii) Definition 4.4's dichotomy — every letter's within-layer
action a partial identity or a partial constant — is the reset condition on
`A_R` verbatim, the diagonal case being a reset that is also an identity at
its own target. (iii) is the displayed reading of the two formulas. ∎

The dictionary, for §9's pending cascade comparison:

| [BLS22] | this paper |
|---|---|
| reset level (identity-or-reset letters) | 1-anchored layer (Def 4.4) — Prop C.2(ii) |
| `Enter(q) / Stay(q) / Leave(q)` | `An(c) / St(c) ∪ An(c) / (Mo ∪ Ex)-side` (§4.2) |
| homomorphism `h`; acceptance lifted via `h⁻¹` (Props 7/8) | division; transport (Lemma 4.7(ii)) |
| cascade level order (manufactured, ≤ `2ⁿ` levels) | the R-order (read off, depth = R-depth of the *syntactic* monoid) |
| Muller exact-set encoding over configurations | Prop 5.4's exact-set window form (over `SR_k` — Prop C.2(i)) |
| Büchi `⋁ ¬Fin(C)` ∈ Π₂ / co-Büchi `⋀ Fin(C)` ∈ Σ₂ | *missing* — Prop 5.4 always pays the exact-set (Muller) price; repaired in C.3 |
| `Fin(C)` last-visit idiom | parks (Prop 5.7) — Prop C.2(iii) |
| configurations finer than the presented states | *missing* — the config ladder of C.2–C.3 below |
| descent on cascade levels for the ω-part | *missing* — the loop-side fallback recursed on the tail algebra; retired in C.5 |

The two missing rows on our side are this section's content; the two
manufactured rows on theirs are what §4 already replaces with read-offs.

## C.2 The configuration machine and condition (C)

Lemma 4.2(ii) proved that no acceptance condition on the recurring states or
edges of `Cay(L)` recognizes `L`; §5.1 confined acceptance to windows and
parks. Both verdicts are about the wrong machine and the right machine
respectively — and the right machine has a finer presentation the engine
already computes but never transcribes: the memory graph of
Proposition 5.4(ii). This subsection names it as a machine and states the
determinacy condition it carries.

**Definition C.3 (the configuration machine).** For a layer `R` and width
`k ≥ 0`, the *configuration machine* is the product
`M_k(R) = A_R × SR_k`: states `(q, m)` with `q ∈ R`, `m ∈ Σ_λ^{≤k}`,
transition `((q, m), a) ↦ (q·a, push(m, a))`, defined iff `q·a ∈ R`. A tail
`β` confined to `R` from `c` has the trajectory from `(c, ε)`; write
`RecE_k(β) ⊆ Edges(M_k(R))` for its set of infinitely-traversed edges. Note
`M_0(R) = A_R` with `RecE_0` the recurring within-layer Cayley edges, and
the memory graph `G(R, c)` of Proposition 5.4(ii) is the `c`-cone of
`M_k(R)` — the same object, so far consumed only by the decision procedure.

Edges rather than states: a state `(q', m)` sees its letter (the last of
`m`) and its destination class but not its source class, and the source is
what the atoms of C.3 anchor on; recurring edges of `M_k` are not in general
a function of recurring states of any `M_{k'}`.

**Definition C.4 (condition (C): configuration-determinacy).** A layer `R`
is **(C)-determined at width `k`** if for every `c ∈ R` and any two ω-tails
`β, β′` confined to `R` from `c` with `RecE_k(β) = RecE_k(β′)`:
`V(c, β) = V(c, β′)`.

**Lemma C.5 (ladder facts).** Let `R` be a layer.

(i) *(C) closes the ladder from below:* (B) at width `k` implies (C) at
width `k`; on a 1-anchored `R`, (B̃) at width `k` implies (C) at width `k`.
The first implication is strict at width 0 (C.3's worked witness:
`G(a → F b)` is (C)-determined at width 0 while plain (B) fails there).
The second is strict at width 1 — degenerately, on a frozen layer. A
frozen layer is 1-anchored with no anchors (every letter an identity),
so every confined tail is parked at its one class and (B̃) collapses
to (B); meanwhile (C) at `k` is (B) at `k+1` (Lemma C.10). Any frozen
singleton terminal layer whose window width is at least 2 therefore
witnesses it, and `GF(aa)`'s terminal layer `{5}` is a measured one
(K-F6: (B) fails at width 1, passes at width 2 — so (B̃) fails at
width 1 while (C) holds there; the layer is frozen by Theorem C.9′,
`GF(aa)` being prefix-independent). The witness is honest but does no
configuration work — the strictness is Lemma C.10's width shift. A
*moving* layer (C)-determined at a width where (B̃) fails — strictness
the class coordinate itself earns — remains the open hunt (K-E8(b):
run the (B̃)-decider at the rescue width on the ladder-rescued conflict
layers).

(ii) *Monotone:* (C) at `k` implies (C) at `k + 1`.

(iii) *The regimes are edge-visible* (`R` 1-anchored): `β` parks at `d` iff
every edge of `RecE_k(β)` is a self-loop at class `d`; `β` is
anchor-recurring iff `RecE_k(β)` contains edges at two distinct classes,
including anchor edges onto two distinct classes.

(iv) *(C) subsumes the park precondition:* if `R` is 1-anchored and
(C)-determined at width `k`, every frozen restriction `({d}, St(d))` is
(B)-determined at width `k` (Definition 5.6(i) comes free).

(v) *Deciding (C) is a prefix of deciding (B).* Confined tails reduce to
lassos preserving `RecE_k` and the verdict; hence (C) at width `k` holds iff
for every reachable strongly connected subgraph `H` of `M_k(R)` (from every
full-memory entry of every `c`-cone), all covering tours of `H` from all its
entries yield one verdict — Proposition 5.4(iii)'s loop-class closure run
per subgraph, **without** the final grouping of subgraphs by window
projection. The computation the closure already performs decides (C) before
its last step coarsens it to (B); the cautions of 5.4(iii) (verdicts factor
through the tour's loop class, not the subgraph; finiteness lives in `𝒞`)
carry over verbatim.

*Proof.* (i) Edges of `M_k` project onto states of `SR_k` (drop the class,
take the pushed buffer), so `RecE_k(β) = RecE_k(β′)` forces
`Win_k(β) = Win_k(β′)`, and (B) applies. For (B̃): by (iii) the two tails
are in the same regime; parked tails share the parking class `d` (read off
the edges) and their parked window sets (the projection), so
Definition 5.6(i) gives one verdict; anchor-recurring tails share `Win_k`
and Definition 5.6(ii) applies. (ii) Edges of `M_{k+1}` project onto edges
of `M_k` (truncate the buffer), so equal `RecE_{k+1}` forces equal
`RecE_k`. (iii) If `β` parks at `d` (Lemma 5.5(i)), every position past the
last change sits at `d` reading `St(d)`: cofinitely all traversed edges are
self-loops at `d`, and only those recur. If `β` is anchor-recurring, changes
recur onto two distinct classes and every change reads an anchor onto its
destination (Lemma 4.9(i)): anchor edges onto two distinct classes recur.
The two conclusions are exclusive and exhaustive by Lemma 5.5. (iv) A tail
of the frozen restriction at `d` is a confined tail parked at `d` with no
change; its `RecE_k` is its recurring window set decorated with the constant
class `d`, so equal window sets give equal `RecE_k`, and (C) gives one
verdict. (v) The lasso reduction is Proposition 5.4(iii)'s wrap argument
with the Ramsey cuts colored by `(idempotent, M_k-state at the cut)` instead
of `(idempotent, length-(k−1) boundary context)` — finitely many colors,
same excision, and the wrapped lasso's recurring edges are exactly the
edges of the recurring subgraph `H`, its verdict unchanged by the same
pair computation. Tours enter `H` through finitely many
`(entry class, full-memory state)` pairs; per entry the loop-class closure
collects the covering-tour loop classes; (C) holds iff each `(entry, H)`
group is verdict-constant — which is 5.4(iii)'s check with the
window-projection grouping removed. ∎

Two remarks. First, the asymmetry of the ladder is now stated exactly:
windows are the *class-blind* projection of the configuration machine, parks
restore the class coordinate on parked tails only, and (C) restores it
everywhere. Second, (v) has a practical consequence, now measured
(K-E1): any (B)-conflict on a *moving* layer is to be re-read
under (C) first — a (B)-conflict between two subgraphs with *different*
edge sets is no (C)-conflict at all, and the existing closure
implementation decides this with the grouping step disabled. On the
census (6 222 languages, Wagner ceiling ω³/ω⁴) the window decider
leaves **8 786** final-layer readings undecided, over 2 114 languages
— cap/budget gaps, not conflicts. The exact (C)-decider (60 s per
language) decides 6 610 of them, every one at width ≤ 2
(6 105 / 346 / 159 at widths 0/1/2); 505 conflict at width 0 yet
decide at 1 or 2 — the ladder's rungs doing real work. The 2 176
remaining layers (their language over the budget) are not undecided
noise: the conflict hunt resolves them into **1 021 genuine
(C)@0-conflicts** (806 aperiodic / 215 group, each ALG-7-verified),
625 clean, 530 budget; at width 1 the conflicts thin to 263 (246
aperiodic; 118 ladder-rescued, 640 budget-open). The census stratum
therefore *does* populate C.4's floor track, at scale — the reversal
is K-F12's, worked in C.4. (On frozen layers a (C)-decision is
Lemma C.10's bookkeeping — (C) at `k` is (B) at `k+1`, the grouping
cost relieved, no logical power added; the logical gain of (C) lives
on moving layers alone. The earlier 4 248-language cut of this
experiment decided its whole 1 164-layer stratum with zero conflicts —
a property of that frame's ω² Wagner ceiling, not of the census axis.)

## C.3 The transcription: anchored edge atoms and the config normal form

Throughout this subsection `R` is **1-anchored** (condition (A) at width 1;
the graded lift is the closing remark) and every formula is evaluated on
tails **confined to `R`** — the window contract's own quantification, which
is what keeps every proof escort-free: on confined tails, anchors fire
truthfully at any history (Lemma 4.9(i)) and no exit ever needs excluding.

**The atoms.** Fix an edge `e = ((q, m), a)` of `M_k(R)`, `|m| = k`. Under
1-anchoring each letter of `m` acts within the layer as an identity or a
constant. If some letter of `m` acts as a constant, let `i*` be the last
such; its target, fixed by the identities after it, is the *pin* of `m`,
and reachability of `(q, m)` on confined tails forces `q = pin(m)`.
Otherwise (`m` all-identity, including `m = ε` at `k = 0`) the class is
carried from before the window and `m`'s letters all lie in `St(q)`. Define

```
A_e  =  m̂ ∧ X^k a                                   if pin(m) is defined
A_e  =  An(q) ∧ X( St(q) U ( m̂ ∧ X^k a ) )          otherwise
```

(`m̂ = m₁ ∧ X m₂ ∧ ⋯ ∧ X^{k−1} m_k` as in §4.3; at `k = 0` the second form
reads `An(q) ∧ X( St(q) U a )`). Both shapes are built from literals, `∧`,
`X`, `U` alone: `A_e ∈ Σ₁`, so `GF A_e ∈ Π₂` and `FG ¬A_e ∈ Σ₂` — the atoms
sit exactly where [BLS22]'s `¬Fin`/`Fin` sit.

**Lemma C.6 (atom fidelity on confined tails).** Let `β` be confined to `R`
from `c`, with trajectory `(q_j)` on `M_k(R)`.

(i) *Soundness:* every position at which `A_e` holds marks a genuine
traversal of `e` — the walk sits at `q` with buffer `m` and reads `a` — at
the position of the `a` (the pinned form fires at the window's start, the
carried form at the anchor).

(ii) *Completeness up to the entry:* every traversal of `e` that is either
pinned (the window contains an anchor) or preceded by at least one
within-layer change is marked by a firing of `A_e`. The unmarked traversals
— at a class held since the entry with no change ever — are finitely many
unless `β` never changes class at all.

(iii) Consequently, on **anchor-recurring** `β`:
`β ⊨ GF A_e ⟺ e ∈ RecE_k(β)`, and `β ⊨ FG ¬A_e ⟺ e ∉ RecE_k(β)`.

*Proof.* (i) Pinned form: the anchor at `i*`, read within the layer (β is
confined), lands the walk on its target whatever the history
(Lemma 4.9(i)); the identities after it fix that class; so at the window's
end the walk is at `pin(m) = q` with buffer `m`, and reads `a`. Carried
form: the `An(q)`-letter lands the walk at `q`; the letters granted by the
`U` lie in `St(q)` and fix `q`; the witness block `m̂` consists of letters
that, being identities defined at `q`, lie in `St(q)` and fix `q` through
the window; the `a` is then read at `(q, m)`. (ii) A pinned traversal fires
unconditionally by (i)'s first computation run backwards: the traversal's
own window contains the anchor, so `m̂ ∧ X^k a` holds at its start. For a
carried traversal with a prior change, let `μ` be the last change before
the window's start: `α_μ ∈ An(q)` (Lemma 4.9(i)) and every letter of
`(μ, traversal]` fixes `q`, hence lies in `St(q)` — the `U`-witnesses are
exactly the displayed ones and `A_e` fires at `μ`. A traversal with no
prior change sits at the entry class; if `β` ever changes class, only the
traversals before the first change are unmarked — finitely many. (iii) If
`e ∈ RecE_k(β)` and `β` is anchor-recurring, changes recur, so cofinitely
every traversal has a prior change and (ii) yields infinitely many
firings; conversely infinitely many firings are infinitely many traversals
by (i). The `FG` half is the contrapositive with (i): no spurious firing
exists to break `FG ¬A_e`. ∎

The one gap in (ii) — the never-changing tail — is the entry park, and the
assembly below hands it, together with every parked tail, to the park
disjuncts, exactly as Proposition 5.7 did: parked tails *cannot* be served
by `GF`-atoms (their anchors fire finitely often — a last change is one
firing, not a recurrence), and this is not a defect but the park dichotomy
resurfacing at the atom level.

**Proposition C.7 (the config normal form).** Let `R` be 1-anchored and
(C)-determined at width `k`, `c ∈ R` an entry class. Say
`S ⊆ Edges(M_k(R))` is *realizable anchor-recurring from `c`* if some
anchor-recurring tail confined to `R` from `c` has `RecE_k = S` —
equivalently (Lemma C.5(v)) `S` is the edge set of a reachable strongly
connected subgraph of the `c`-cone spanning at least two classes — and let
`f_c(S)` be its verdict, well-defined by (C). Let `Ω_d` be
Proposition 5.4's window term for the frozen restriction `({d}, St(d))`
(well-defined under (C) by Lemma C.5(iv)). Then

```
Ω(R, c)  =  ⋁_{S realizable anchor-recurring from c, f_c(S) = 1}
                ( ⋀_{e ∈ S} GF A_e  ∧  ⋀_{e ∈ E_c \ S} FG ¬A_e )
            ∨  ⋁_{d ∈ R}  F( An(d) ∧ X ( G St(d) ∧ Ω_d ) )
            ∨  ( G St(c) ∧ Ω_c )
```

— `E_c` the edges of the `c`-cone — satisfies the window contract of
Theorem 4.10: `β ⊨ Ω(R, c) ⟺ V(c, β) = 1` for every `β` confined to `R`
from `c`.

*Proof.* *Parked tails.* The two park lines are Proposition 5.7's, verbatim
— their soundness and completeness arguments (the any-history pin, the
last change, transport) consulted only 1-anchoring and the frozen
restrictions' window terms, both available here. A parked tail satisfies
no exact-set disjunct: `S` spans two classes, so it contains an edge
`e = ((q, ·), ·)` with `q` distinct from the parking class `d`; on the
parked tail, letters of `An(q)` eventually never occur (`An(q) ∩ St(d) = ∅`
for `q ≠ d`, the diagonal argument of §4.2) and no window of the tail
eventually pins `q`, so `A_e` eventually never fires and `GF A_e` fails.

*Anchor-recurring tails.* Such a `β` satisfies no park disjunct (`G St(d)`
pins the walk — the tail would be parked). On `β`, Lemma C.6(iii) makes the
`S`-disjunct hold iff `RecE_k(β) = S` exactly — the disjuncts are pairwise
exclusive — and `RecE_k(β)` is realizable anchor-recurring, `β` its own
witness. So `β` satisfies `Ω(R, c)` iff `f_c(RecE_k(β)) = 1` iff
`V(c, β) = 1` by (C). Both regimes covered, both directions. ∎

**Sizes and fragment position.** `|E_c| ≤ |R|·|Σ_λ|^{k+1}`; atoms have
modal depth `k + 2`; the exact-set disjuncts number at most the realizable
sets — the Muller price again, `≤ 2^{|E_c|}` generic. The collapse under
structure is where [BLS22]'s Theorem 2 finally transposes in full:

**Corollary C.8 (one-sided encodings).** Whether the accepting family
`{S : f_c(S) = 1}` is upward-closed (downward-closed) among realizable
anchor-recurring sets is decided during Lemma C.5(v)'s enumeration
(monotonicity of the verdict along `H ⊆ H′`). If upward-closed,

```
Ω^rec(R, c)  =  ⋁_{S minimal accepted}  ⋀_{e ∈ S} GF A_e
```

is exact on anchor-recurring tails — a pure-`GF` (Büchi-shaped) term in
`Π₂`; dually a downward-closed family yields a pure-`FG` (co-Büchi-shaped)
term `⋀_{e ∈ S_max^c} FG ¬A_e`-shaped in `Σ₂`; the general case keeps the
exact-set (Muller-shaped) `Δ₂` form. With the parks normalized by the
standard hoist `F(G φ ∧ GF ψ) ≡ FG φ ∧ GF ψ`, the whole `Ω(R, c)` stays in
`Δ₂`, and in `Π₂` when the family is upward-closed and every parked verdict
is rejecting (the parks vanish). *Proof of the upward-closed case:* an
anchor-recurring `β` satisfies `⋁_min ⋀ GF A_e` iff `RecE_k(β)` contains
some minimal accepted set (Lemma C.6(iii)) iff `f_c(RecE_k(β)) = 1` by
upward closure. ∎

This is the analog of [BLS22, Thm 2]'s matching-fragment guarantee, per
layer; it also applies at `(C) = (B)` strength, where it strictly improves
Proposition 5.4(iv)'s remark by making the one-sidedness *decided* rather
than observed. Measured (K-E3, extended corpus): of the 74 census
final layers (C)-decided with a ≥ 2-class collected family, 16 are
upward-closed, 16 downward-closed, 28 both, 14 neither. The exact
up/down tie is structural, not a sampling accident: the catalogue is
complement-closed, and complementation swaps the closure direction, so
the two one-sided strata biject. No upward skew exists at the raw
level (the recurrence-rung stratified recount, over `P|_R`, is
pending). The prefix-independent case lifts to the whole label at
once:

**Corollary C.9 (global one-sided form, prefix-independent case).** Let
`L` be prefix-independent with a terminal final layer `R*` (no class of
`R*` carries an exit), 1-anchored, (C)-determined at width `k`, entry
`r`, accepting family upward-closed and every parked verdict rejecting.
Then the extraction emits `⋁_{S minimal} ⋀_{e ∈ S} GF A_e` — a `Π₂`
formula defining `L` outright.

*Proof.* A terminal layer sheds its law and its exit chain (§4.2:
`sojourn ≡ ⊤`, empty exit fans), so `Final(r) = Ω(R*, r)`, which under
the hypotheses is the pure-`GF` form with vanished parks
(Corollary C.8). Exactness at `r` (Proposition C.7 discharging the
window contract in Theorem 4.10) gives `⟦Ω(R*, r)⟧ = T_r`;
prefix-independence gives `T_r = L` (Lemma 5.2(ii)), and Lemma 5.2(iii)
emits it directly. ∎

No instance of the full hypothesis set exists, and the obstruction is
a theorem. On a prefix-independent `L` every verdict is *class-blind*:
`V(s·e^ω) = V(e^ω)` — the stem is a finite prefix and washes — so `P`
depends only on the idempotent coordinate. Worse, a frozen layer has
no anchors, no anchor-recurring tails, and an empty accepting family —
the corollary is vacuous there — and the final layer of a
prefix-independent language is **always frozen**: measured first
(K-E3, extended corpus: of the census's 1 104 prefix-independent
languages, **zero** have a non-frozen final layer), and now proved,
with no aperiodicity hypothesis (matching the census, where the 1 104
span LTL and non-LTL alike):

**Theorem C.9′ (prefix-independence freezes the terminal layers).**
Let `L` be prefix-independent. Then every terminal layer of `𝓘(L)` is
a frozen **singleton**: the terminal layers are exactly the
`R`-classes (rows) of the minimal ideal `K` of the syntactic
ω-semigroup, and the syntactic congruence collapses each row to a
single class, on which every letter acts neutrally. In particular
Corollary C.9's hypothesis set (terminal, 1-anchored, **non-frozen**)
is unsatisfiable on prefix-independent languages — its global
bare-`Π₂` form is vacuous everywhere, not merely on the census.

*Proof.* Prefix-independence makes stems wash twice over. Through the
congruence: `u ≈ v` asks that finite-word contexts
(`x·u·β ∈ L ⟺ x·v·β ∈ L`) and loop contexts
(`x(yuz)^ω ∈ L ⟺ x(yvz)^ω ∈ L`) agree; the finite-word condition is
vacuous — `xuβ` and `β` share a tail, so both sides reduce to
`β ∈ L` — and the loop condition sheds its `x`. So for
prefix-independent `L`: `u ≈ v` **iff** `(yuz)^ω ∈ L ⟺ (yvz)^ω ∈ L`
for all `y, z`. Through the verdicts: `V(s, e) = [e^ω ∈ L]` depends on
the loop alone.

(1) *Terminal layers are the rows of `K`.* A terminal layer `R`
carries no exit: `R·Σ ⊆ R`, so `R` is a right ideal, and it contains a
minimal right ideal, which is an `R`-class of the minimal two-sided
ideal `K` [PP04]; a layer being a single `R`-class, `R` *is* that row.
`K` is completely simple: every element of `K` lies in a maximal
subgroup, and right multiplication by anything maps a row into itself
(`t·x ≤_R t` inside one `J`-class forces `R`-equivalence). Conversely
every row of `K` is exit-free, and a layer outside `K` properly
reaches `K` — it carries an exit; so terminal layers = rows of `K`.

(2) *The verdict on `K` is a function of the row.* Let `e, f` be
`R`-equivalent idempotents of `K`. Then `e·f = f` and `f·e = e`
(`f = e·x` gives `e·f = e·e·x = f`; symmetrically), so `(x, y) = (f, e)`
is conjugation data — `x·y = f·e = e`, `y·x = e·f = f` — and
`(s, e) ~ (s·f, f)` are conjugate (Lemma C.11), sharing their verdict;
prefix-independence erases the stems: `V(e) = V(f)`. An arbitrary
`t ∈ K` lies in a subgroup with identity `e_t = t^π` in `t`'s own
`H`-class, and the linked pairs of `t^ω` sit at `e_t`: the verdict of
`t^ω` is `V(e_t)`, a function of `row(t)`.

(3) *Rows are syntactically inseparable.* Suppose the syntactic
ω-semigroup had two distinct `R`-equivalent elements `u ≠ v` of `K`,
say `v = u·x`. For any context `(y, z)`: `[y]·v·[z] = [y]·u·(x[z])`
and `[y]·u·[z]` differ by a right factor, so they share their row (1),
hence `(yuz)^ω` and `(yvz)^ω` share their verdict (2) — for *every*
context. By the reduced congruence, `u ≈ v`, contradicting
distinctness in the syntactic quotient. So each row of `K` is a single
syntactic class `q`.

(4) Right multiplication keeps `q` in its row (1), which is `{q}`:
`q·a = q` for every letter — the terminal layer is a frozen singleton.
∎

The proof pins C.4's saturation story down in general: the verdict,
stem-washed, lives on the rows of the kernel; the column coordinate —
the phase a moving layer would carry — is invisible to every context a
prefix-independent language can build, and the syntactic congruence
eats it. This is K-F2's mechanism generalized: the pending bit cannot
survive in a prefix-independent language's absorbing class. Cor C.8's
one-sided win is thus confined to non-prefix-independent languages
(`G(a → F b)`, K-F1, is the worked one). The corollary's live scope is
the general lift — recurrence languages that are not
prefix-independent, where the peel above the final layer wraps the
`Π₂` leaf in reach chains — which remains open ⟨TBD: the semantic
recurrence class absorbs the wrappers; the syntactic statement needs
proof⟩.

**The worked witness: `G(a → F b)` at width 0** (tool-confirmed, K-F1).
Five classes; the final layer is `R = {2, 4}` — `2 = [!a∧b]`
(answered), `4 = [!a∧b · a∧!b]` (owing a `b`) — terminal, moving,
1-anchored over the quotient letters `b` (the `b`-letters, constant
onto `2`), `a` (`a∧!b`, constant onto `4`), `s` (`!a∧!b`, neutral):
`An(2) = {b}`, `An(4) = {a}`, `St(2) = {b, s}`, `St(4) = {a, s}`
(diagonals included). Take `k = 0`: `M_0(R) = A_R`, six edges
`(2,b)→2, (2,s)→2, (2,a)→4, (4,a)→4, (4,s)→4, (4,b)→2`. The closure
is verdict-constant per subgraph, so **`R` is (C)-determined at width
0**, while plain (B) fails at width 0 (the §5.1 idle pair) — and at
every width. The collected family reads "accept iff an edge at class
`2` is covered": upward-closed, minimal accepted sets `{(2,s)}`,
`{(2,b)}`, `{(2,a), (4,b)}`. Split per Proposition C.7's regimes: the
two single-class minima are the parks (`Ω_2 = ⊤`, `Ω_4 = ⊥` — parked
at `2` every loop is answered, parked at `4` the owed `b` never
comes), and the anchor-recurring stratum has the single two-class
minimal set, so Corollary C.8's pure-`GF` term plus the parks give

```
Ω(R, 2)  =  ( GF A_{(2,a)} ∧ GF A_{(4,b)} )  ∨  F( b ∧ X G St(2) )  ∨  G St(2)
```

with `A_{(2,a)} = b ∧ X( (b∨s) U a )` and `A_{(4,b)} = a ∧ X( (a∨s) U b )`
(carried form, `k = 0`) — equivalent on confined tails to
Proposition 5.7's width-1 output `(GF(a∧!b) ∧ GF b) ∨ …`, and the
emitter is built and gated (K-F11): the atoms come out Spot-equivalent
to the displayed forms, and the assembled `Ω(R, 2)`, emitted as a
shared DAG (27 nodes raw, 15 simplified), is equivalent to
`G(a → F b)` outright — the layer being terminal with no safety, the
window contract here is the whole language. The point of the rung is
visible in the width: 5.7 needed width 1 because at width 0 the window vocabulary is
*empty* — no window can even say "anchor-recurring". The config atoms
say it at width 0, the class coordinate supplying what the first
window letter did: the determinacy is the same, the *transcription*
starts one width earlier. (C) never degrades a lower rung, and here it
strictly beats plain (B) at equal width.

**Remark (the graded lift).** For a layer anchored at width `k_R ≥ 2` the
atoms lift with Lemma 4.12 in the role of Lemma 4.9(i): the pin of a buffer
is computed by the `(k_R+1)`-window dichotomy, the carried form's trigger
becomes an anchor window `ŵ, w ∈ An_κ(q)` with the `U` over the graded
neutral vocabulary, and the entry transient is threaded exactly as in
Proposition 5.7's graded remark (one explicit brick per readable entry word
of length `≤ k_R`). ⟨TBD: write out and prove; no new mechanism is
expected — every ingredient is §4.3's.⟩ Note the division of labor:
condition (A) on the layer is consumed by the *transcription* of the atoms
(the phase must be letter-recoverable); the *decision* of (C)
(Lemma C.5(v)) never consults (A). A final layer failing (A) at every
width sends its `Ω` to C.5's fallback.

## C.4 Completeness refuted: the floor of the ladder

Every rung so far is sufficient, and none is complete — provably: this
subsection shows the ladder has a floor, and the floor is §5.1's
residual witness itself, once its canonical invariant is read
correctly (the first draft's hand derivation ran in the profile
monoid, not its syntactic quotient — K-E0/K-F2 caught the gap). Two
lemmas calibrate what completeness would have meant; the conjecture is
stated for the record and refuted — determinacy fails at every width,
in both halves — and the sandwich identity it reduces to has a
seven-element aperiodic counterexample. The mechanism of the failure,
*zero absorption*, is the subsection's real finding: it identifies
exactly what any ω-specific descent cannot be built from.

**Lemma C.10 (frozen coincidence).** On a frozen layer `R = {q}` (every
letter neutral), `M_k(R) = {q} × SR_k`, and for tails from `q` the map
`((q, m), a) ↦ m·a` is a bijection between recurring `M_k`-edges and
recurring `(k+1)`-windows: `RecE_k(β)` and `Win_{k+1}(β)` determine one
another. Hence **(C) at width `k` coincides with (B) at width `k + 1` on
frozen layers**: the config ladder gains nothing there — correctly, since
Proposition 5.4 is already exact — and it inherits the frozen (B)-question
whole: an aperiodic frozen layer failing (B) at every width would refute
Conjecture C.12 below.

*Proof.* The class coordinate is constant, so an edge is traversed at
position `i` iff the word `m·a` is the factor ending at position `i + 1`;
recurring edges and recurring `(k+1)`-factors are in the displayed
bijection (the `< k`-memory warm-up edges occur once each and drop out).
Determinacy over one data set is determinacy over the other. ∎

The lemma cuts the other way from what the first draft hoped: §5.1
exhibits precisely such a layer. The floor witness's final layer *is*
frozen — the singleton `{z}` — and its window question fails at every
width on the growing-gap pair. Table 3's 0 failures over 12 516
final-candidate layers were bounded-width and in-frame — a (B)-failing
final layer needs two states and two propositions at once, a shape
that cut omitted. The extended census (Wagner ceiling ω³/ω⁴) contains
the shape and populates it at once (K-F12): 1 021 of its heavy layers
genuinely fail (C) at width 0, 263 still at width 1, and on the type
specimen's frozen singleton the width-0 (C)-conflict *is* a plain-(B)
failure at width 1 by this lemma — a genuine in-frame (B)-failing
final layer, the `2state2ap` open hunt of the main paper's §8 closed.
Their every-width persistence is Theorem C.12″'s criterion below.
C.10's warning fires, and the conjecture is refuted on arrival. It is
stated anyway, because its *reduction* (C.14–C.18) is unconditionally
correct and turns the refutation into an explicit algebraic identity
failure one can exhibit in seven elements and scan for census-wide.

**Lemma C.11 (the conjugacy floor).** Linked pairs `(s, e)`, `(s′, e′)`
are *conjugate* if `e = x·y`, `e′ = y·x`, `s′ = s·x` for some `x, y`
[PP04]. `P` is a union of conjugacy classes; consequently two confined
tails whose induced pairs are conjugate always share their verdict, and a
counterexample to determinacy — at any width or at all widths — must
manufacture **non-conjugate** pairs out of tails with equal recurring
data.

*Proof.* Conjugate pairs are induced by a common ω-word (shift the
factorization across `x`), and the invariant's verdict is per-word
well-defined (Lemma 4.7(i)): the verdict is constant on conjugacy
classes, so `P`, a union of induced-pair verdicts, is conjugacy-closed. ∎

The floor is exactly how the group case escapes: `EvenBlocks`' tails with
growing even- versus odd-length `a`-blocks share every window at every
width, and their pairs — the accepting even idempotent against the
rejecting zero — are *not* conjugate; the parity that keeps them apart is
the group's. The conjecture asserted that aperiodicity closes that
door — that only cancellative, group-style accounting can assemble
non-conjugate pairs from identical data. It does not: there is a
second, purely aperiodic escape, and the floor witness realizes it.

**Conjecture C.12 (refuted — Theorem C.12′).** Let `R` be a layer of
an aperiodic invariant.

(a) *Limit determinacy:* two tails confined to `R` from `c` with
`RecE_k(β) = RecE_k(β′)` for **every** `k` induce conjugate linked
pairs — hence `V(c, β) = V(c, β′)`.

(b) *Uniformization:* `R` is (C)-determined at some finite width `k`,
bounded by a computable function of `|𝒞|`.

**Theorem C.12′ (the floor).** Let `𝓘 = 𝓘(GF(a ∧ X((!a∧!b) U a)))` —
seven classes (§5.1): the unit, `[s]`, the four unflagged profiles
`(f, l, 0)`, and the two-sided zero `z` into which the flagged
profiles merge — and let `R = {z}` be its frozen terminal layer. Then
§5.1's growing-gap tails, both confined to `R` from `z`,

```
β   =  a s^{n₁} b s^{n₂} a s^{n₃} b ⋯       rejected
β′  =  a s^{n₁} a s^{n₂} b s^{n₃} a s^{n₄} a ⋯   accepted
```

satisfy `RecE_k(β) = RecE_k(β′)` for **every** `k` simultaneously
while `V(z, β) ≠ V(z, β′)`. Hence limit determinacy C.12(a) fails —
the induced pairs are non-conjugate — and `R` is (C)-determined at no
width: C.12(b) fails at every candidate bound.

*Proof.* On the frozen `R`, `RecE_k` and `Win_{k+1}` determine one
another (Lemma C.10). With gaps outgrowing every fixed width, the
recurring window set of either tail at width `w` is exactly the
single-non-silent-letter set
`{s^w} ∪ {s^i x s^{w−1−i} : x ∈ {a, b}}` — any window holding two
non-silent letters occurs but never recurs — the same set for both,
at every `w`. The verdicts differ: `β` alternates `a` and `b`, so no
`a·s^*·a` factor ever occurs; `β′` completes one at every returning
`a`-pair. Equal data at every width with distinct verdicts refutes
(a) directly, and its restriction to any one width defeats (C) there,
refuting (b); non-conjugacy of the pairs is Lemma C.11 read backwards
(conjugate pairs cannot split the verdict). ∎

The growing-gap argument is not specific to the floor witness's
algebra; it generalizes into a *finite, scan-able criterion* for
every-width failure on any frozen singleton — the shape K-F12's entire
conflict stratum takes:

**Theorem C.12″ (the padded-block criterion).** Let `{z}` be a frozen
singleton layer of any invariant (group or aperiodic), `Σ_z` its
within-layer alphabet, and `s ∈ Σ_z`. Since the powers `[s]^n` are
eventually periodic, there is an idempotent `σ` with `[s^N] = σ` for
all `N` in some arithmetic progression of arbitrarily large terms. For
a finite set `B` of non-empty words over `Σ_z` (*blocks*) and a
sequence `w₁ … w_r` covering `B` (each block occurring at least once),
write

```
ε(w₁ … w_r)  =  π( [w₁]·σ·[w₂]·σ ⋯ [w_r]·σ )
```

for the idempotent power of the padded product. If two covering
sequences of the **same** block set `B` satisfy
`V(z, ε) ≠ V(z, ε′)`, then `{z}` fails (C) at **every** width — the
two padded tails have equal `RecE_k` for all `k` simultaneously,
distinct verdicts, and non-conjugate linked pairs.

*Proof.* Take gap exponents `N₁ < N₂ < ⋯` along the progression and
the tails `β = w₁ s^{N₁} ⋯ w_r s^{N_r} · w₁ s^{N_{r+1}} ⋯`, `β′`
likewise from the second sequence — both confined to `{z}` from `z`
(every letter of `Σ_z` fixes `z`). On the frozen singleton, `RecE_k`
is the recurring `(k+1)`-window set (Lemma C.10). Fix a width `k`:
once the gaps outgrow `k + 1`, a window either lies inside a gap
(`s^{k+1}`) or meets a single block occurrence (an `s`-padded factor
of `s^∞·w·s^∞` for some `w ∈ B`); windows meeting two blocks occur
finitely often and drop out of the recurring set. The recurring set is
therefore determined by the block *set* `B` alone — equal for `β` and
`β′`, at every `k` simultaneously. The linked pairs: cutting at the
sequence boundaries, every chunk of `β` has class
`[w₁]·σ ⋯ [w_r]·σ` (each `[s^{N_i}] = σ` along the progression), so
`β` induces `(z, ε)` and `β′` induces `(z, ε′)`; the verdicts differ
by hypothesis, Lemma C.11 read backwards makes the pairs
non-conjugate, and the restriction to any one width defeats (C) there.
∎

Theorem C.12′ is the instance `B = {a, b}`, `s` the silent letter
(`σ = [s]`), sequences `(a, b)` against `(a, a, b)`:
`ε(a, b) = (a, b, 0)` rejects, `ε(a, a, b) = z` accepts. The point of
the generalization is operational: the criterion consumes only the
multiplication table and `P` — no cone, no closure, no budget — and
small block sets with short covering sequences already realize the
known mechanisms, so it scans across K-F12's 246-layer conflict
stratum (K-E8): wherever two covering sequences split the verdict,
that layer is a floor inhabitant outright, its width-bounded conflicts
promoted to every-width failure.

**The sandwich reduction.** The refutation gains its algebraic form
through the reduction the first draft built toward the conjecture: the
three lemmas below are unconditionally true, and they concentrate any
(C)-failure into the failure of a single identity between idempotents.
Throughout, a *loop at `q`* is a non-empty word
`v` with `q·[v] = q`; read from `q`, its positions carry classes
(`q·[prefix]`), so its decorated windows are well-defined, and
`W_w(q, v^ω)` denotes the set of decorated width-`w` windows of the
periodic word `v^ω` read from `q` — the cyclic data, seams included.

**Lemma C.14 (aligned factorizations).** Let `β, β′` be confined to `R`
from `c` with `RecE_w(β) = RecE_w(β′)` for one width `w`. Then there are
a class `q`, a word `ω ∈ Σ_λ^w`, and idempotents `f, f′` with
`q·f = q·f′ = q`, such that both tails admit Ramsey factorizations with
every cut at class `q` with backward window `ω`, constant block class
`f` (for `β`) and `f′` (for `β′`), every block carrying `ω` as suffix,
and

```
W_w(q, B^ω)  =  the shared recurring decorated window set     (every block B of either tail).
```

Consequently `V(c, β) = [(q, f) ∈ P]` and `V(c, β′) = [(q, f′) ∈ P]`.

*Proof.* The endpoints of recurring `M_w`-edges recur, and the edge sets
are shared, so some node `x = (q, ω)` is visited infinitely often by
both tails. Restrict to `β`'s visits of `x`: infinitely many positions,
each at class `q` with backward window `ω`. Color pairs of visit
positions by the class of the enclosed factor; Ramsey yields an infinite
subset with one color `f`, and merged blocks being blocks forces
`f·f = f`. Sparsify: keep cuts far enough apart and late enough that
every block contains every recurring width-`w` decorated window (each
recurs beyond any horizon) and no non-recurring one (the finitely many
non-recurring window types have a last occurrence). Each block ends at a
cut and is longer than `w`, so `ω` is its suffix. Its cyclic seams are
genuine tail windows: a window crossing a cut of the tail is a window at
a late position, hence recurring; and `B^ω`'s seam `(ω)(prefix of B)` is
exactly the tail's window at the cut. So `W_w(q, B^ω)` is the shared
recurring set. Cuts sit at prefix-class `q`, so the induced pair is
`(q, f)` and the verdict its `P`-membership (Lemma 4.7(i)). The same
construction runs on `β′` at its own `x`-visits. ∎

**Lemma C.15 (conjugation criterion).** Let `e, e′` be idempotents with
`q·e = q·e′ = q`. If

```
e·e′·e = e      and      e′·e·e′ = e′                (the sandwich identities)
```

then `(q, e)` and `(q, e′)` are conjugate, hence `P`-equivalent
(Lemma C.11).

*Proof.* Take `x = e·e′`, `y = e′·e`. Then
`x·y = e·e′·e′·e = (e·e′·e)·e = e·e = e`,
`y·x = e′·e·e·e′ = e′·e·e′ = e′`, and
`q·x = (q·e)·e′ = q·e′ = q`: the conjugation data of Lemma C.11, stems
preserved. ∎

**Lemma C.16 (aperiodic localization).** In a finite aperiodic monoid,
`m ∈ e·S·e` and `m J e` imply `m = e`. Hence the sandwich identities
are equivalent to the corresponding `J`-equivalences:
`e·e′·e J e ⟺ e·e′·e = e`.

*Proof.* `m = e·m·e` gives `m ∈ eS` and `m ∈ Se`, so `m ≤_R e` and
`m ≤_L e`; in a finite semigroup, `≤_R` together with `J`-equivalence
forces `R`-equivalence, and dually for `L` [PP04]; so `m H e`, and
aperiodicity is `H`-triviality: `m = e`. The equivalence follows since
`e·e′·e ∈ eSe` always. ∎

The conjecture was, equivalently, one statement:

**Conjecture C.17 (the sandwich identity — refuted below).** There is a computable
`w₀(|𝒞|)` such that on every aperiodic invariant: for every class `q`,
window `ω ∈ Σ_λ^{w₀}`, and idempotents `e = [v]`, `e′ = [v′]` of loops
at `q` carrying `ω` as suffix with equal cyclic data
`W_{w₀}(q, v^ω) = W_{w₀}(q, v′^ω)`:

```
e·e′·e  J  e        and        e′·e·e′  J  e′.
```

**Theorem C.18 (conditional resolution).** Conjecture C.17 implies both
halves of Conjecture C.12; moreover condition (C) then holds at the
*uniform* width `w₀(|𝒞|)` on every layer of every aperiodic invariant.

*Proof.* Let `β, β′` be confined from `c` with
`RecE_{w₀}(β) = RecE_{w₀}(β′)`. Lemma C.14 aligns them: idempotent loops
`f, f′` at a common `q`, common suffix `ω`, equal cyclic data (both
sides equal the shared recurring set). Conjecture C.17 gives the
`J`-equivalences, Lemma C.16 upgrades them to the identities,
Lemma C.15 conjugates the pairs, and Lemma C.11 equates the verdicts:
`V(c, β) = V(c, β′)`. That is (C) at width `w₀` — uniformization (b) —
and the pairs of any two all-width-equal tails are conjugate — limit
determinacy (a). ∎

**The refutation, in seven elements.** Theorem C.18 stands as a true
conditional; with Theorem C.12′ it reads contrapositively — C.17 is
false — and Lemma C.14's alignment says where the identity failure
sits. On the floor witness it is explicit. Fix any candidate width
`w₀` and take `q = z` with the loops `v = a s^n b s^m` and
`v′ = a s^n a s^{n′} b s^m`, `n, n′, m > w₀`: both loop at `z`, both
carry `ω = s^{w₀}` as suffix, their cyclic data agree (only
single-non-silent-letter windows, decorated by the constant `z`), and
their classes are idempotents — `e = [v] = (a, b, 0)` and
`e′ = [v′] = z`. Then

```
e·e′·e  =  (a,b,0) · z · (a,b,0)  =  z ,        z  <_J  (a, b, 0)
```

— the first sandwich identity fails, at every `w₀`. The mechanism is
not cancellation but **absorption**: the flagged zero dominates every
product it enters, so `e·e′·e` falls `J`-below `e` because `e′` was
already at the bottom. On `EvenBlocks` the reduction fails at the same
step — the aligned blocks of the growing-even and growing-odd tails
give `f·z·f = z <_J f`, the parity group doing the separating — so the
two known mechanisms for non-conjugate pairs under equal cyclic data
are *group cancellation* and *zero absorption*, and the second is
purely aperiodic. (The first draft "verified" the identity on the
floor witness by hand — in the profile monoid, where the flagged
profiles stay distinct, no zero exists, and
`(f,l,1)·(f′,l′,1)·(f,l,1) = (f,l,1)` does hold. A correct computation
in the wrong algebra: the syntactic quotient merges the flagged
profiles and reverses the outcome. K-E0's sandwich scan on the true
invariant dumps exactly this failure — the aperiodic positive control
fires at the zero, beside `EvenBlocks`' group control (K-F5).) The
identity is machine-checkable on every output of the closure — per
collected `(F, base)` group, pairwise over the idempotent loop
classes — and K-E7 ran it census-wide, re-aimed from falsification to
cartography. The map is two-colored (K-F8): over the extended census's
6 610 decided layers the scan sums **14 050 absorption pairs**
(aperiodic, one idempotent 𝒥-below the other — the floor witness's
mechanism) against **7 387 group pairs** (non-aperiodic), and among
the 3 076 aperiodic 𝒥-equivalent sandwich drops **none is
verdict-splitting** — a non-splitting drop is an ordinary 𝒥-class
fall, not a (C)-conflict. The conflict stratum confirms the dichotomy
from the failing side (K-F12): its 806 aperiodic conflicts carry the
verdict-splitting absorption signature — the type specimen drops over
*three* 𝒥-minimal classes, a richer bottom than the floor witness's
single zero — and its 215 non-aperiodic ones the group escape. No
third mechanism appears anywhere in the frame.

**Post-mortem of the dichotomy, and the transfer to moving layers.**
The first draft's argument for C.17 was a dichotomy: a pattern
`x·(stutter)^*·y` distinguishing `v′` from `v` is either tracked by
the syntactic classes (pendency — then the decorated windows differ)
or congruence-irrelevant (then it cannot move the class). The floor
witness walks between the horns: the pattern `a·s^*·a` is maximally
congruence-*relevant* — its recurrence is the verdict — yet
class-invisible, because each completion is **absorbed**: on the
frozen layer the walk already sits at `z`, the decoration is constant
and tracks nothing. Saturation erases pendency exactly where the flag
dominates. Nor does the failure stay frozen:

**Proposition C.19 (saturation transfers to moving layers).** Let `L₁`
be the floor witness over `Σ₁`, `L₂ = G(c → F d)` over a disjoint
`Σ₂`, and `L = π₁⁻¹(L₁) ∩ π₂⁻¹(L₂)` over the product alphabet. The
final layer of `𝓘(L)` is `{(z, 2), (z, 4)}` — **moving** and
1-anchored, the `L₂`-pendency flipping the class while the
`L₁`-coordinate sits saturated at `z` — and it fails (C) at every
width.

*Proof sketch.* The classes `(z, 2) ≠ (z, 4)` survive the syntactic
quotient because `L₂` is not prefix-independent (a `Σ₂`-silent tail
accepts from `2`, rejects from `4`), while the flagged `L₁`-coordinate
merges exactly as in §5.1, so on the layer the walk sees only the
`L₂`-pendency. Ride Theorem C.12′'s growing-gap pair on the
`Σ₁`-track under one identical anchor-recurring `Σ₂`-schedule: the two
tails differ only at the `a`/`b` swap positions, whose two-non-silent
windows never recur, so `RecE_k` agree at every `k`; the verdicts
split on the `L₁` conjunct. ⟨TBD: the full syntactic-product
bookkeeping.⟩ ∎

Tool-confirmed (K-E2, K-F9): the specimen's invariant has 25 classes,
aperiodic, terminal layer `{(z, 2), (z, 4)}` — moving, 1-anchored,
exactly as predicted — and the (C)-decider conflicts at widths 0
and 1, each conflict verified genuine (ALG-7): the two reconstructed
lassos share their recurring edge set, membership toggles on the
language itself, and the induced linked pairs are non-conjugate
(Lemma C.11). Widths ≥ 2 exceed the tool's covered-set budget (nine
quotient letters); the conflict is Theorem C.12′'s window-blind
`a·s^*·a` mechanism decorated by a fixed recurrence, so it persists at
every width structurally. **The floor track is thus inhabited on both
sides of the frame boundary: beyond it by construction — the transfer
specimen, the first moving-layer inhabitant — and *inside* it at
scale (K-F12).** Over the extended census's 2 176 heavy layers, 1 021
genuinely fail (C) at width 0 and 263 persist at width 1 (246
aperiodic), every conflict ALG-7-verified — membership toggles,
non-conjugate pairs, zero closure artifacts. The type specimen
`2state2ap1acc_parity_3772037665` (13 classes, aperiodic, Wagner
(ω³, σ), canonical acceptor 6 states / 2 AP) fails on frozen singleton
layers by verdict-splitting zero absorption over three 𝒥-minimal
classes; by Lemma C.10 its width-0 (C)-conflict is a plain-(B) failure
at width 1 — the first in-frame inhabitant of the `2state2ap` shape
Table 3's cut omitted. A width-bounded conflict is not yet floor
membership — the ladder rescues 118 of the width-0 conflicts at
width 1 — and the promotion instrument is Theorem C.12″'s padded-block
criterion (K-E8), with 640 layers budget-open at width 1 the remaining
unknowns.

Consequence: no re-scoping of Conjecture C.12 by layer shape survives —
"frozen" is where the failure is native, not where it is confined.
What the failure respects is the *coordinate*, not the kinematics: it
lives wherever a verdict-carrying recurrence has saturated the
congruence, and it enters any layer by product.

**The unconditional analysis.** Independently of the reduction, failure
at every width has a structure — and one honest gap.

**Lemma C.13 (coherent branches, and their realization).** Suppose `R`
fails (C) at every width. (i) There is a *coherent branch*: subgraphs
`(H_k)_{k≥1}`, each `H_k` a mixed-verdict strongly connected subgraph of
`M_k(R)` witnessing the failure at width `k`, with the width-`k` data of
the width-`(k+1)` witness pair projecting onto `H_k`. (ii) Every coherent
branch is realized: there is a single confined tail `τ` with
`RecE_k(τ) = E(H_k)` for **all** `k`.

*Proof.* (i) A width-`(k+1)` witness pair — equal `RecE_{k+1}`, distinct
verdicts — is verbatim a width-`k` witness pair (Lemma C.5(ii)'s
projection), and its width-`k` recurring subgraph is the projection of
its width-`(k+1)` one. Witness structures at width `k` are finitely many
(subgraphs of the finite `M_k`, entries bounded through
`(state, class)`-reachability); every width-`(k+1)` structure has a
width-`k` parent; every width is inhabited: König's lemma yields the
branch. (ii) Realization is a diagonal: let `t_j` label a closed covering
walk of `H_j` (a late factor-loop of the width-`j` witness tail — late
enough that its every traversed edge is recurring), and glue `t_j` to
`t_{j+1}` along the witness tail's own late trajectory. Reachability
between the pieces is state-determined (`M_k`'s future depends only on
`(class, buffer)`), so the glue exists; a glue segment taken late in the
width-`(j+1)` witness traverses only `E(H_{j+1})`-edges, whose width-`k`
projections lie in `E(H_k)` for every `k ≤ j + 1` by coherence. Fix a
width `k`: past `t_{k−1}`, every letter of `τ` traverses, at width `k`, an
edge of `E(H_k)` — tours `t_j` (`j ≥ k`) because `E(H_j)` projects onto
`E(H_k)`, glue by the previous sentence — and every edge of `E(H_k)` is
traversed by each `t_j`: `RecE_k(τ) = E(H_k)`. ∎

What Lemma C.13 does *not* give is the verdict split: the realization
carries the edge data, not the mixing — the diagonal's own linked pair
is contaminated by the glue. The same contamination closes the cheap
route to C.17: Lemma C.14 makes an *interleave* of the two tails' blocks
legal at width `w₀` (every seam is a `(q, ω)`-cut), and such a tail
realizes pairs assembled from both `f` and `f′` — but its recurring data
exceeds the shared set above the alignment width, so its
well-definedness constrains nothing about `β` and `β′` themselves. The
content of C.17 was irreducibly about the algebra, not about a third
word — and the algebra said no. With C.17 refuted, Lemma C.13 is what
failure-at-every-width *does* look like, and the floor witness
realizes the branch in its simplest form: every `H_k` is the full
width-`k` shift register at `z`, the coherent branch is the window
ladder itself, and Theorem C.12′'s pair realizes it with no diagonal
glue.

**The consequences, now unconditional.** First, a **no-go**: on the
floor witness's final layer the decorated walk is constant, so *any*
condition of the (B)/(B̃)/(C) family — a verdict factoring through
bounded-width recurring data of the canonical invariant's own
decorated walk — reduces there to window data, and Theorem C.12′
defeats it at every width. The bounded-recurrence axis, windows
through configurations and any graded refinement, is exhausted: the
residual stratum cannot be emptied from `𝓘`'s walk. The main open
problem is therefore *not* closed by the ladder, and is sharpened by
it: an ω-specific descent must consume something the canonical walk
does not carry, and the two known carriers are C.5's two routes — the
chains-expansion `A_S` (canonical; its states hold exactly the erased
pendency, as R-chain data) or a KR-decomposed presentation
(non-canonical, certified by the conformance gate). Second, what the
ladder keeps unconditionally: (C) at width `k` is decidable
(Lemma C.5(v), the closure with grouping disabled), strictly beats
plain (B) at equal width with real transcription gains (C.3), and the
sandwich scan is a census-wide instrument whose first map is drawn
(K-E7/K-F8): absorption and group are the only mechanisms in the
frame — measured on the decided mass and on the conflict stratum
alike — and the floor track is populated on both sides of the frame
boundary: in-frame at scale on frozen singletons (K-F12; per-layer
promotion to every-width via Theorem C.12″'s criterion, K-E8), and
beyond it on a moving layer by Proposition C.19's transfer specimen
(K-F9).

## C.5 The manufactured cascade: the fallback that retires DG

Where the transcription's preconditions fail at every affordable width, the
fallback should still be a machine descent, never a language recursion.
[BLS22] supplies both halves, each scoped exactly like Proposition 4.14.

**Stem side ((A) fails at every width).** The confined machine `A_R`,
totalized with an absorbing exit sink, is counter-free (its transition
monoid is `𝒜_R` plus a zero — aperiodic by Proposition 4.11(ii)). Run the
holonomy decomposition on it [BLS22, Prop 6]: a reset cascade `A′`
homomorphic to `A_R`,
every level identity-or-reset over its combined alphabet — that is, every
level *1-anchored* over combined letters (Prop C.2(ii)). The confined-walk
languages `L_{r→c}` of Proposition 4.14 are then emitted by [BLS22]'s
finite-word reach family (`reach`/`solid`/`dashed` with the weak-next
adjustment of its Remark 2) on `A′`, and Proposition 4.14's `SAFE`/insertion
assembly is unchanged — only the inner extractor is swapped. Against DG on
`𝒜_R`, every one of §2.3's blindnesses falls: no alphabet inflation (the
combined letters are structured pairs, not fresh block-image letters), no
per-occurrence substitution (reach formulas memoize per
`(level, S, B, T, β, τ)` — a class-indexed DAG in this paper's own sense),
no separator choice (the level order is the holonomy's), and the output
lands in syntactic co-safety, which DG never guaranteed. The cost moves
from DG's `(|𝒜_R|·|Σ_λ|)`-deep multiplicative recursion to the cascade
height — up to `2^{|R|}` levels of up to `2^{|R|}` states
[BLS22, Prop 6], every reset cascade re-normalizable to `n·log j` levels
of two states each [BLS22, §4.1] — and expected far below the bound in
practice ⟨TBD: measure both routes on the (A)-fallback stratum — K-E5;
258 languages on the old cut, recount on the extended corpus is the
preflight; the floor specimens are 3-class layers, where the
comparison is by hand⟩.
Alternatively the levels, being 1-anchored, admit this paper's own width-1
brick grammar with combined-letter triggers — the phase of each lower level
letter-recoverable by its own anchors, which is precisely what [BLS22]'s
`solid`/`dashed` thread through levels ⟨TBD: decide which presentation to
adopt — K-E5's ledger decides; they should emit the same DAG up to brick
naming⟩.

**Loop side ((C) fails at every width, or (A) fails on a final layer).**
The last resort must supply a formula for `T_c` on confined tails, and
Lemma 4.2(ii) is the wall: no machine derived from `Cay(L)` — hence none
derived from the invariant's multiplication alone — has its acceptance on
recurring configurations. [BLS22] never faced this because its *input* was
an acceptor whose recurring states decide; the honest transposition is to
consume one too: the deterministic automaton the pipeline started from
(the [SωS26] input), restricted to the states realizing the layer's tails,
KR-decomposed, its acceptance lifted to configurations
([BLS22, Props 7–8]), and encoded as the Muller combination of `Fin(C)`
atoms — `Σ₂` atoms, Boolean-combined, no language recursion, terminating
where "DG on the tail algebra" provably could not shrink
(Lemma 5.2(ii)). The price is stated plainly: this branch, alone in the
whole extraction, consults a presentation — canonicity fails on it exactly
as it failed on DG's separator choice, and the emitted formula is
certified by the conformance gate, not by construction.

**The floor witness, worked through the fallback.** The input acceptor
for `L = GF(a ∧ X(s U a))` is the pendency machine — two states, "was
the last non-`s` letter an `a`", Büchi on the completion transition —
and its KR decomposition is essentially the profile machine's terminal
layer: the two-class reset semiautomaton `{A, B}` with `a` constant
onto `A`, `b` onto `B`, `s` neutral — the exact six-edge machine the
first draft mistook for a layer of `𝓘`. In its true home the
derivation is correct: config recurrence on this *presentation*
decides at width 0 — the completion edge `(A, a)`, an exit on every
unflagged canonical layer and an invisible self-loop at `z`
(Theorem C.12′), is here an honest recurring edge — the accepting
family is upward-closed with single minimal set `{(A, a)}`, and the
emitted formula is

```
GF A_{(A,a)}  =  GF( a ∧ X( (a ∨ s) U a ) )  ≡  GF( a ∧ X( s U a ) )
```

— the defining formula, at the language's own until-rank. One
phenomenon, stated plainly: the recurrence data the canonical walk
provably cannot carry (Theorem C.12′) is carried by a two-state
presentation, and the whole cost is canonicity — this branch's stated
price. (The computation is the six-edge closure already tool-validated
on `G(a → F b)`'s isomorphic canonical layer, K-F1; running it on the
pendency machine is K-E6's first item.)

The canonical repair route, promoted by C.4's no-go from companion
result to the open problem's main candidate: **the
invariant-to-machine construction exists and is
counter-free exactly on this paper's side of the frontier.** Carton and
Michel construct, from any recognizing morphism — hence, instantiated on
the *syntactic* morphism, canonically from `𝓘(L)` — a prophetic
(complete unambiguous, co-deterministic) Büchi automaton `A_S`, via the
**chains expansion**: states pair a linked-pair conjugacy class with a
*strict R-chain* of `S₊` [CM03, §6.3] — the R-descent structure of
Lemma 4.3 resurfacing as the state space of the canonical acceptor.
Every ω-word labels exactly one accepting run, so the verdict is by
construction a Büchi condition on the recurring transitions of the
canonical run — exactly the property `Cay(L)` lacks (Lemma 4.2(ii)) and
this fallback needs. And the object sits on the right side of the cut:
`A_S` is counter-free iff `S₊` is aperiodic iff `L` is LTL
[CF26, Thm 1] — the ω-analogue of McNaughton–Papert, recovered on the
co-deterministic side after [DG08, Rem 11.13] showed no
forward-deterministic presentation can carry it — with the corollary
that every per-state loop language of `A_S` (the recurrence conditions;
[PW13]'s infinitary fraction) is star-free whenever `L` is
[CF26, Cor 2]. Every ingredient of a transcription is therefore
LTL-definable; what remains open is the *assembly* — an LTL rendering of
the unique run's recurrence structure from LTLf formulas of the
star-free loop languages: the **prophetic transcription problem**. A
prophetic state is a predicate on the suffix (the state at position `i`
is a function of `α_{≥i}`) — precisely the shape of the label contract
(`T_c`, §4.2) and of future-only LTL — and [PW13]'s fragment
characterizations are the precedent, stopping below full LTL. Solved,
the prophetic transcription replaces this subsection's non-canonical
branch outright; conversely, the non-canonical branch's correctness gap
— relating a deterministic presentation's configuration recurrence to
the canonical loop languages — is exactly the bridge [CF26, §4] leaves
open. The config ladder is the letter-visible special case: an anchored
edge atom `GF(An(q) ∧ X(St(q) U ·))` asserts the recurrence of a loop
pattern whose loop language happens to be window-recognizable given the
class decoration.
This whole branch is load-bearing, not transitional: the residual
floor stratum of C.4 lands here — the floor witness's entire loop
content sits on a frozen layer failing (C) at every width, and
Proposition C.19 transfers the failure to moving layers — in addition
to any (A)-failing final layer (§8: expected none in the census frame
⟨TBD: verify this read-off explicitly (K-E5 preflight) — the old
cut's 258 languages' failing layers are all at Wagner depth 1; recount
on the extended corpus, then check none is a layer a run can end
in⟩).

## C.6 What does not transfer

For the record, the negative space of the adaptation. (1) No
`Fin`-on-`Cay(L)` shortcut exists: Lemma 4.2(ii) is not circumvented but
*localized* — the class coordinate of `M_k(R)` carries phase, never
acceptance, and every verdict still factors through `P` via the loop-class
closure. (2) The frozen layer keeps its information deficit: there
`A_R` is trivial, `M_k(R) = SR_k`, and the config ladder collapses to the
window ladder (Lemma C.10) — and that is where the residual floor
lives (C.4): the deficit is not repaired but proven irreparable from
the canonical walk. (C)'s gain lives strictly on moving layers, and
only below the floor. (3) [BLS22]'s global pipeline
(decompose the whole semiautomaton, encode the whole acceptance) is not
imported: run globally it pays cascade height where §4 reads the R-order,
which is the measured reason the in-repo `bls` engine loses to the
transcription wherever the transcription applies. The import is the
*ladder axis* (reset memory → configurations) and the *encoding
discipline* (per-rung one-sidedness, the last-event idiom), each scoped to
one layer.

## C.7 Consequences for the assembled paper (if this section lands)

- **§5.4 step 4 rewrite:** `(B) at k′ ⟹ windows; (B̃) ⟹ +parks;
  (C) at k′ ⟹ config normal form (Prop C.7), one-sided when the family
  closes (Cor C.8); else the manufactured cascade (C.5) — DG exits the
  loop side.` Step 3's (A)-fallback swaps DG for C.5's stem half.
- **Table 2:** the residual row splits — a new "config-transcribable" row
  (condition (C), atoms `GF(An ∧ X(St U ·))`) above a residual row now
  proven inhabited: its floor is `GF(a ∧ X(s U a))` (Theorem C.12′),
  and its census population is K-F12's conflict stratum.
- **§8:** the extended-corpus measurements (6 222 languages, Wagner
  ω³/ω⁴) — coverage: of 8 786 census-undecided final-layer readings,
  6 610 decide under (C), every one at width ≤ 2 (K-F7); conflicts:
  1 021 genuine at width 0, 263 persisting at width 1, 246 of them
  aperiodic — the floor track inhabited in-frame (K-F12), the
  `2state2ap` open-hunt witness found, per-layer promotion to
  every-width by Theorem C.12″'s scan (K-E8), 640 layers budget-open;
  the mechanism map: absorption and group only, zero verdict-splitting
  `other` over the decided mass (K-F8); Prop C.19's specimen the
  moving-layer floor inhabitant beyond the frame (K-F9); the
  prefix-independent stratum 1 104/1 104 frozen — Theorem C.9′,
  census-confirmed (K-F10); one-sidedness balanced 16/16/28/14, the
  tie structural by complement closure (K-E3); still pending:
  DG-vs-cascade on the stem stratum (K-E5; the 258-language count is
  the old cut, recount first).
- **§9:** the cascade paragraph's ⟨TBD⟩ is discharged by Prop C.2 and the
  dictionary; [BLS22] enters the references.
- **§10:** the main open problem *stands*, sharpened from both sides:
  negatively, the bounded-recurrence axis on the canonical walk is
  exhausted (Theorem C.12′ and C.4's no-go — no (B)/(B̃)/(C)-style
  condition at any width reaches the floor), so an ω-specific descent
  must consume what the walk does not carry; positively, the carriers
  are named (C.5: the chains expansion `A_S`, canonically; or a
  certified presentation), making the prophetic transcription problem
  the open problem's concrete form. The sandwich identity — refuted
  aperiodically, by zero absorption — is the scan-able signature of
  where the floor extends (K-E7), and Theorem C.12″ turns the
  signature into a per-layer floor certificate (K-E8).
- **Implementation note (repo-local, not for the paper):** the decision
  side of (C) is the existing loop-class closure with its last grouping
  step disabled; the atoms and the normal form are emitters, built
  DAG-only and conformance-gated on the worked witness (K-F11),
  production wiring into the window engine pending; the C.5 fallback
  can consume `aut2ltl/bls` (holonomy
  bridge, reach family, `Fin`) nearly as-is, scoped per layer.

## References (additions)

- **[BLS22]** U. Boker, K. Lehtinen, S. Sickert. *On the Translation of
  Automata to Linear Temporal Logic.* FoSSaCS 2022.
- **[CF26]** Y. Thierry-Mieg, with Claude (Anthropic). *Counter-Free
  Prophetic Automata Characterize Star-Free ω-Languages.* Working
  draft, 2026.
- **[CM03]** O. Carton, M. Michel. *Unambiguous Büchi automata.* TCS 297
  (2003) 37–81.

(`[DG08]`, `[PP04]`, `[PW13]`, `[KR65]`, `[TW01]` as in the paper's
reference list; the uses here are [DG08, Prop 11.11, Lemma 11.6,
Rem 11.13], [PP04]'s linked-pair conjugacy, [PW13]'s loop languages.)
