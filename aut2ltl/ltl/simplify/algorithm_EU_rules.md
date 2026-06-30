# Spot's eventual/universal rewrite rules (reference for `spot_EU_rules.py`)

**Source.** Spot 2.15.1 documentation §5.4.2 ("Simplifications for Eventual &
Universal Formulas"), cross-checked against the implementation in
`~/git/Spot-BinaryBuilds/spot-2.14.5.dev/spot/tl/simplify.cc` (the `mospliter`
event/universal split and the `simplify_visitor` unary/binary cases). This file
is the rule catalogue; `spot_EU_rules.py` implements the subset noted below.

## Notation

| Symbol     | Meaning                                      |
|------------|----------------------------------------------|
| `f, g`     | Any PSL formula                              |
| `e`        | Pure eventuality   (`F e ≡ e`, `f.is_eventual()`)   |
| `u`        | Purely universal   (`G u ≡ u`, `f.is_universal()`)  |
| `q`        | Both = "suspendable" (`is_eventual() and is_universal()`) |

The three classes are **cached node bits** on Spot's hash-consed DAG (a bottom-up
boolean recurrence over the children's bits), so testing them is O(1) per node and
a rule guarded by them stays O(DAG). They are sound-but-incomplete syntactic
classes (e.g. `a ∨ Fa` is semantically eventual but not flagged) — every guarded
rule is still a true equivalence wherever it fires; we just miss some chances.

**Legend** (which option in `tl_simplifier_options` gates the rule)
- `≡`  — always applied (never increases size).
- `↗`  — may increase size; disabled by `reduce_size_strictly`.
- `[E]` — applied only when `favor_event_univ = true` (push toward event/univ form).
- `[¬E]`— applied only when `favor_event_univ = false`.

---

## Rules

### Basic absorption & distribution

- `F e ≡ e`
- `f U e ≡ e`
- `e M g ≡ e ∧ g`
- `u₁ M u₂  ↗  (F u₁) ∧ u₂`
- `F(u ∨ q) ∨ q  [¬E]  F(u ∨ q)`
- `f U (g ∨ e)  [E]  (f U g) ∨ e`
- `f M (g ∧ u)  [E]  (f M g) ∧ u`
- `q U X f ≡ X(q U f)`
- `f U (g ∧ q)  [E]  (f U g) ∧ q`
- `(f ∧ q) M g  [E]  (f M g) ∧ q`

### Universal-side rules (duals)

- `G u ≡ u`
- `u W g ≡ u ∨ g`
- `f R u ≡ u`
- `e₁ W e₂  ↗  (G e₁) ∨ e₂`
- `f W (g ∨ e)  [E]  (f W g) ∨ e`
- `f R (g ∧ u)  [E]  (f R g) ∧ u`
- `q R X f ≡ X(q R f)`

### X / q interaction (leading-X removal)

- `X q ≡ q`
- `q ∧ X f  [¬E]  X(q ∧ f)`
- `q ∨ X f  [¬E]  X(q ∨ f)`
- `X(q ∧ f)  [E]  q ∧ X f`
- `X(q ∨ f)  [E]  q ∨ X f`

### Lifting inside G (drop X when subformula is eventual)

- `G(f₁ ∧ … ∧ fₙ ∧ X e₁ ∧ … ∧ X eₚ) ≡ G(f₁ ∧ … ∧ fₙ ∧ e₁ ∧ … ∧ eₚ)`
- `G(f₁ ∧ … ∧ fₙ ∧ F(g₁ ∧ … ∧ g_p) ∧ X e₁ ∧ … ∧ X e_m) ≡ G(… ∧ F(…) ∧ e₁ ∧ … ∧ e_m)`

### Lifting inside F (drop X when subformula is universal)

- `F(f₁ ∨ … ∨ fₙ ∨ X u₁ ∨ … ∨ X uₚ) ≡ F(f₁ ∨ … ∨ fₙ ∨ u₁ ∨ … ∨ uₚ)`
- `F(f₁ ∨ … ∨ fₙ ∨ G(g₁ ∨ … ∨ g_p) ∨ X u₁ ∨ … ∨ X u_m) ≡ F(… ∨ G(…) ∨ u₁ ∨ … ∨ u_m)`

### G/F distribution with q

- `G(f₁ ∨ … ∨ fₙ ∨ q₁ ∨ … ∨ qₚ) ≡ G(f₁ ∨ … ∨ fₙ) ∨ q₁ ∨ … ∨ qₚ`
- `F(f₁ ∧ … ∧ fₙ ∧ q₁ ∧ … ∧ qₚ)  [E]  F(f₁ ∧ … ∧ fₙ) ∧ q₁ ∧ … ∧ qₚ`
- `G(f₁ ∧ … ∧ fₙ ∧ q₁ ∧ … ∧ qₚ)  [E]  G(f₁ ∧ … ∧ fₙ) ∧ q₁ ∧ … ∧ qₚ`
- `GF(f₁ ∧ … ∧ fₙ ∧ q₁ ∧ … ∧ qₚ) ≡ G(F(f₁ ∧ … ∧ fₙ) ∧ q₁ ∧ … ∧ qₚ)`

### Further G/F lifting with eventual/universal subformulas

- `G(f₁ ∧ … ∧ fₙ ∧ e₁ ∧ … ∧ e_m ∧ G(e_{m+1}) ∧ … ∧ G(eₚ))  [E]  G(f₁ ∧ … ∧ fₙ) ∧ G(e₁ ∧ … ∧ eₚ)`
- `G(f₁ ∧ … ∧ fₙ ∧ G(g₁) ∧ … ∧ G(g_m)) ≡ G(f₁ ∧ … ∧ fₙ ∧ g₁ ∧ … ∧ g_m)`
- `F(f₁ ∨ … ∨ fₙ ∨ u₁ ∨ … ∨ u_m ∨ F(u_{m+1}) ∨ … ∨ F(uₚ))  [E]  F(f₁ ∨ … ∨ fₙ) ∨ F(u₁ ∨ … ∨ uₚ)`
- `F(f₁ ∨ … ∨ fₙ ∨ F(g₁) ∨ … ∨ F(g_m)) ≡ F(f₁ ∨ … ∨ fₙ ∨ g₁ ∨ … ∨ g_m)`
- `G(F f₁) ∧ … ∧ G(F fₙ) ∧ G(e₁) ∧ … ∧ G(eₚ)  [E]  G(f₁ ∧ … ∧ fₙ) ∧ G(e₁ ∧ … ∧ eₚ)`
- `F(G f₁) ∨ … ∨ F(G fₙ) ∨ F(u₁) ∨ … ∨ F(uₚ)  [E]  F(f₁ ∨ … ∨ fₙ) ∨ F(u₁ ∨ … ∨ uₚ)`

### Final absorption (only when no other terms in OR)

- `F(f₁) ∨ … ∨ F(fₙ) ∨ q₁ ∨ … ∨ qₚ  [¬E]  F(f₁ ∨ … ∨ fₙ ∨ q₁ ∨ … ∨ qₚ)`

---

## What `spot_EU_rules.py` implements

Phase 1 — the **always-applied (`≡`) unary/binary** rules only, the size-non-
increasing ones that are unambiguously O(DAG) and free of ping-pong (no inverse is
also `≡`):

- unary: `F e ≡ e`, `G u ≡ u`, `X q ≡ q`
- binary: `f U e ≡ e`, `f R u ≡ u`, `u W g ≡ u ∨ g`, `e M g ≡ e ∧ g`
- X-rotation: `q U X f ≡ X(q U f)`, `q R X f ≡ X(q R f)`

Deferred (need n-ary regrouping at And/Or, or are size-increasing / `favor_event_univ`-
gated): the lifting-inside-G/F blocks, the G/F-with-q distribution, and the `↗`
rules. These overlap our own folding (`fold_pass`) and must be reconciled before
wiring — see `algorithm.md` for the existing GF/FG cofactoring.
