# The reachability operators

This package implements the **technical core** of the construction of Ulrich Boker,
Karoliina Lehtinen and Salomon Sickert, *On the Translation of Automata to Linear
Temporal Logic*, **FoSSaCS 2022**: the family of inductively-defined **reachability
formulas** that read a future-only LTL formula off a reset-cascade
(Krohn–Rhodes–Holonomy) decomposition of a counter-free deterministic ω-automaton.

The authoritative working reference is the in-package digest
[`../paper/automata-to-ltl-construction.md`](../paper/automata-to-ltl-construction.md)
— a self-contained distillation of the paper's Sections 4–4.4 (definitions, the five
reachability formulas, the acceptance encoding, the worked example); the original text
is [`../paper/Automata2LTL.txt`](../paper/Automata2LTL.txt) (and `.pdf`). **Section
numbers below refer to that digest.** This document airs the digest out so each
operator gets its own paragraph, and maps it onto the code: one operator per file,
each named exactly as the reference names it.

## Setting — cascades, configurations, Enter/Stay/Leave (digest §4)

The construction works on a **reset cascade** `A = ⟨Σ, A₁,…,Aₙ⟩`: level `i` reads the
real letter together with the current states of all lower levels, and every level is a
*reset* semiautomaton (each letter is the identity, or resets the level to one fixed
state). A **configuration** is a tuple `S = ⟨q₁,…,qᵢ⟩`; the empty tuple `⟨⟩` is the
level-0 base. For a level-`i` state `q`, the formulas branch over three classes of
combined letters (digest §4.2): **`Enter(q)`** (reset the level to `q`), **`Stay(q)`**
(keep it at `q` — identity letters and resets to `q`), **`Leave(q)`** (move it off
`q`); with `Enter(q) ⊆ Stay(q)` and `Leave(q)` the complement of `Stay(q)`. These three
sets are *the* primitives the reachability formulas are defined over.

In the code, `support._combined_letters_at_level` enumerates the observable combined
letters at a level, and each operator filters them into the stay / leave / enter
partitions it needs.

## reach — Formula 1, the main (strong) operator (digest §6(1), §7) — `reach.py`

`reach(S, B, β, T, τ)` holds on `w` iff the run from `S` reaches configuration `T`
with the suffix satisfying `τ`, *without* first being at the bad configuration `B`
with the suffix satisfying `β`. At the level-0 base case (`S = ⟨⟩`) it is plainly
`(¬β) U τ`. Otherwise it splits on whether the top-level state is unchanged or changed:

    reach  =  solid ∨ dashed

By Lemma 5, with `β ∈ Πᵢ` and `τ ∈ Σᵢ`, `reach` is **co-safety (Σᵢ)**. The function
`reach` carries the base case and that disjunction, memoised per build on
`casc.reach_memo`.

## wreach — Formula 2, the weak (release) dual (digest §6(2), §7) — `wreach.py`

`wreach` is the literal dual of `reach` with the bad and target roles swapped:

    wreach(S, B, β, T, τ)  :=  ¬ reach(S, T, τ, B, β)        -- (B,β) ↔ (T,τ)

It reads as "reaching `T(τ)` *releases* not reaching `B(β)`"; with no bad configuration
the release antecedent never fires (vacuously true), and at level 0 it is `τ R ¬β`. By
Lemma 5 (`β ∈ Σᵢ`, `τ ∈ Πᵢ`) it is **safety (Πᵢ)**.

## solid — Formula 3, reach while the top state stays `s` (digest §6(3), §7) — `solid.py`

`solid(⟨S,s⟩, ⟨B,b⟩, β, ⟨T,t⟩, τ)` is `reach` constrained so the level's state never
leaves `s` (so it forces `t = s`). It is four cases on whether the source equals the
bad and/or the target configuration, over a nonempty-prefix core **`solid⁺`**
(`solid_plus`). `solid⁺` picks the *last* `Stay(s)` letter `⟨σ,T'⟩` that lands on
`⟨T,t⟩`, and at the **lower level** freely reaches the firing point `T'` with
continuation `σ ∧ Xτ`, while (a) never taking a `Leave(s)` letter beforehand and
(b) never stepping into the bad configuration beforehand (the bad-step check is pushed
one letter back, with obligation `ρ ∧ Xβ`). The recursion is strictly to `level+1`.
`solid` is **co-safety (Σᵢ)**.

## wsolid — Formula 4, the weak version of `solid` (digest §6(4), §7) — `wsolid.py`

`wsolid` has the same four-case shape as `solid` but its **4th case differs**
(`(Q ∨ τ) ∧ ¬β` instead of `solid`'s `(P ∧ ¬β) ∨ τ` — they are not duals; both must
independently enforce "stay in `s`"). Its core **`wsolid⁺`** (`wsolid_plus`) has two
lines: line (1) eventually reaches `⟨T,t⟩` still staying in `s` — `solid⁺` without the
free-reach conjunct (weak ⇒ reaching is optional), with all avoids done by `wreach`;
line (2) never reaches `⟨T,t⟩` and simply stays in `s` forever, never blocked (target
`false`, so `wreach(…, S, false)` means "never trigger the avoid"). `wsolid` recurses
to `wreach` and is **safety (Πᵢ)**.

## dashed — Formula 5, reach while the top state changes `s ⤳ t` (digest §6(5), §7) — `dashed.py`

The hardest formula. Before reaching `⟨T,t⟩` the run reads an `Enter(t)` letter
`⟨σ,T'⟩` that switches the top state to `t`; from there it stays in `t` (via `solid`)
and reaches `⟨T,t⟩` avoiding `⟨B,b⟩(β)`. Line (1) freely reaches the firing lower
config `T'` then enters and stay-reaches; line (2) additionally avoids the bad
top-state `b` on the way, using **`wsolid` with `⟨B,b⟩` and `⟨T,t⟩` swapped** — `wsolid`
(not `solid`) precisely so that `dashed` stays **co-safety (Σᵢ)**; line (3) forces the
run to actually `Leave(s)`. Line (1) is needed on its own for the corner case
`Enter(b) = ∅` (line (2) then vacuous). `dashed` recurses to `reach` at the lower level
and to `solid` / `wsolid` at the same level inside `X(…)`.

## Fin(C) and reach_to — the acceptance bridge (digest §9) — `fin.py`

The acceptance condition is expressed over the cascade's configurations through one
atom: **`Fin(C)`**, true exactly when the run visits configuration `C` finitely often
(Lemma 7):

    Fin(C)  :=  ¬ reach_to(ι, C)  ∨  reach_to(ι, C, ¬ reach_to⁺(C, C))

where `reach_to(S, T, τ) := reach(S, T, false, T, τ)` ("reach `T`, no real bad") and
`reach_to⁺` forces a nonempty prefix (a strict return). `Fin(C) ∈ Σ₂`, so
`¬Fin(C) ∈ Π₂`. These are the only atoms needed: the acceptance-class members build
their formula as a Boolean combination of `Fin(C)` (Büchi `⋁ ¬Fin(C)`, coBüchi
`⋀ Fin(C)`, the Muller DNF, the looping/weak `reach_to` forms — digest §9.3). `fin_c`
computes `Fin(C)`; `_uncond_reach_strict` is `reach_to⁺`.

## Mutual recursion and termination (digest §7, §8)

The five formulas are mutually recursive **within a level**, well-founded because the
recursion always descends to a strictly lower level before closing the loop:

    reach   →  solid, dashed                 (same level)
    wreach  →  reach                          (dual, same level)
    solid   →  reach          at the LOWER level
    wsolid  →  wreach         at the LOWER level
    dashed  →  reach          at the LOWER level,  and  solid / wsolid  (same level, inside X)

Lemma 4 establishes correctness against the intended semantics (digest §6) by
induction on the level; Lemma 5 places each formula in its syntactic fragment, which
is what makes the final `φ` land in the class matching the automaton's acceptance
(Theorem 2). Because the operators live one per file, this cycle is carried by
module-qualified calls (`from . import sibling` then `sibling.fn()`), resolved at call
time — see `support.py` for the shared, non-recursive machinery they all build on.

---

# Beyond the paper — implementation choices

Everything above is the construction as the paper defines it. The implementation adds
machinery the paper does not spell out, to make the naively-exponential recursion
tractable and to keep the output compact. **None of it changes the language of the
produced formula** — each is a soundness-preserving optimisation or a faithful
encoding of an implicit side condition.

## Hash-consing, skeleton templates and per-build memoisation

The recursion fans in heavily (the same machine position is reached along many
paths), so three layers of sharing turn it from a tree blow-up into a DAG build:

- **Hash-consing.** Formulas are native `spot.formula` end to end; equal subterms are
  the *same* node, so the result is a shared DAG (the paper's "size" measure, digest
  §1). Stringification happens only at the very top.
- **Skeleton templates.** The context parameters `β`/`τ` are NOT part of any memo
  key: every recursion step manufactures a fresh context (`solid⁺` pushes `σ ∧ Xτ`
  and `ρ ∧ Xβ`, `dashed` swaps them into `wsolid`), so keying on them makes every
  key path-unique and multiplies machine positions by contexts — exponential in
  cascade height. Instead each operator is built once per machine **skeleton**
  `(S, B, T, level)` as a template whose `β`/`τ` positions hold two reserved
  placeholder APs (`support.PH_BETA`/`PH_TAU`); every call plugs its own context in
  via `support._instantiate`, a per-node-memoized simultaneous substitution
  (`builders._subst_f`) that re-simplifies rebuilt nodes so constant plugs fold.
  Plugs may themselves contain the placeholders (the manufactured contexts above):
  substitution is single-pass, so they denote the caller's parameters. Total cost is
  O(#skeletons × template DAG) instead of positions × contexts.
- **Per-build memo.** Each distinct skeleton is expanded once and cached:
  `reach` on `casc.reach_memo`, the `solid`/`wsolid`/`dashed` helpers on
  `casc.helper_memo` (via the `support._memo_reach_helper` decorator), instantiation
  node-maps per plug pair on `casc.inst_memo`, and `fin`'s `reach_to⁺` on
  `casc.uncond_memo`. The memos live on the `CascadeHolder` threaded as `casc` —
  never module globals — so a fresh holder is a fresh build and discarding it *is*
  the reset.
- **Runaway guard.** `REACH_GUARD` (`KR_REACH_GUARD`) counts **distinct** `reach`
  skeleton expansions (memo misses, not raw calls), so it trips only on a genuine
  same-level blow-up, not on healthy high-fan-in workloads.

## Letter enumeration and fusion (equivalence classes)

The paper reasons over the abstract `Enter/Stay/Leave` letter classes; the code must
enumerate them and avoid one disjunct per concrete letter.

- **Observable enumeration.** `support._combined_letters_at_level` enumerates combined
  letters over all **h-image** configurations (`state_to_config`) — the observable
  approximation of the full product cascade, exact when `h` covers the reachable
  configs. (Enumerating only from the source config `S` was the breaker on 2-level
  cascades, where an entering letter fires only from another config's lower part.)
- **Dedup.** The same combined letter can surface from several configs; `_dedupe`
  collapses them by the paper's combined-letter identity `(letter, lower-config suffix)`.
- **Fusion.** The paper emits one summand per concrete letter; `support._fuse_letters`
  fuses letters whose summand is identical *up to the guard* into a single summand whose
  guard is the Minato-minimised OR of their valuations. It is sound because every
  summand reads the letter only through that guard. `KR_FUSE_LETTERS=0` restores the
  literal per-letter paper shape (for grounding comparisons). This is counter-measure B
  of `docs/dag_folding.md`.

## Early-outs (sound short-circuits not in the paper)

Subproblems whose value is forced are returned immediately, which also prunes every
descendant they would have seeded:

- **`reach`** — `τ ≡ false ⇒ false` (a dead tail: the base case is `¬β U false ≡ false`
  and every inductive line conjoins `τ` at the claim point); already at the target with
  `τ = true ⇒ true`.
- **`solid`** — top state `s ≠ t ⇒ false` (strong `solid` forces `t = s`); source equals
  target with `τ = true ⇒ true`.
- **`dashed`** — `Enter(t) = ∅` or `Leave(s) = ∅ ⇒ false` (a state-changing path is
  impossible).
- **`fin`** — the empty configuration makes `reach_to⁺` `false`; a per-build `fin_calls`
  guard catches a `Fin` that repeats without converging.

## Dropping vacuous `Fin(C)` conjuncts (a consumer concern)

A related fold — keeping `Fin(C)` only for configurations `C` reachable from the good
set, dropping the rest as vacuous (`kr.fold_fin_reach`) — shapes *which* `Fin(C)` are
ever built. It lives at the acceptance-assembly level, not in the operators: see the
Muller member's `algorithm.md`.
