# The partscc algorithm

A leaf translator that reconstructs the LTL formula of an ω-language whose automaton
is a single strongly-connected component — a bottom SCC the run never leaves. It
partitions the component by the letters that enter each state; when that partition
is deterministic it reads off one closed-form formula and adopts it after a
language-equivalence check.

## Setting

A translator maps a language to a label:

```
Label       =  Some φ  |  ⊥                  -- φ an LTL formula; ⊥ = decline
Translator  =  Language → Label
```

partscc asks the Language for its **state-based** form `A = sbacc(tgba(L))`, with
`A = (Q, Σ, δ, q0, {F_1,…,F_m})`, `Σ = 2^AP`, edges `(s, g, t) ∈ δ` carrying a
Boolean guard `g` (a BDD over `AP`), and **state-based generalized-Büchi**
acceptance: each color `F_i ⊆ Q` is a set of states, and a run is accepting iff it
visits every `F_i` infinitely often (`m = 0` ⇒ every run accepts).

partscc applies only when `A` is a **single SCC with `|Q| ≥ 2`**: strongly connected
and, being the whole automaton, escape-free — so every run stays inside it forever
and `L(A)` is its steady-state ω-language. Otherwise it declines.

## Labels

Each state carries two guard-disjunctions:

```
L(s)  =  ⋁ { g : (·, g, s) ∈ δ }        -- entry label: letters that move into s
O(s)  =  ⋁ { g : (s, g, ·) ∈ δ }        -- exit label:  letters available from s
```

## The partition

The labels `{L(s)}` form a **valid partition** when

1. each is non-trivial: `false ⊊ L(s) ⊊ true`, and
2. they are pairwise disjoint: `L(s) ∧ L(t) = false` for `s ≠ t`.

Disjointness makes `A` **deterministic**: a letter `σ` enters at most one state, the
unique `δ(σ) = s` with `σ ∈ L(s)`. The occupied state is then a function of the last
letter read, so the explicit states become redundant. Absent a valid partition,
partscc declines.

## The formula

Being deterministic, the component has one run per word, so from `q0` a word `w` is
in `L(A)` iff every step is legal and the run is accepting:

```
φ  =  O(q0)                                -- anchor:        first letter is a move out of q0
   ∧  G( ⋀_s ( L(s) → X O(s) ) )           -- transition law: having entered s, the next letter exits s
   ∧  ⋀_{i=1..m} G F( ⋁_{s ∈ F_i} L(s) )   -- fairness:       each color's states are entered i.o.
```

- **Anchor.** Position 0 has no incoming letter, so the occupied state is fixed by
  the input (`q0`); the first letter must lie in `O(q0)`.
- **Transition law.** For `i ≥ 1` the letter `w[i-1]` entering `s = δ(w[i-1])`
  triggers `X O(s)`, forcing `w[i] ∈ O(s)` — the run's legality, step by step.
- **Fairness.** "occupying `s` at step `i ≥ 1`" ⟺ "`w[i-1] ∈ L(s)`"; as `GF` is
  shift-invariant, "visit `F_i` infinitely often" ⟺ `GF(⋁_{s ∈ F_i} L(s))`. The
  generalized-Büchi condition is thus transcribed onto the input. With `m = 0` the
  conjunction is empty and `φ` is the bare safety skeleton.

The fairness conjuncts are formed only when the acceptance is generalized Büchi;
under any other shape they are omitted and the gate decides.

## The translator

```
partscc : Translator
partscc(L) =
    let A = sbacc(tgba(L)) in
    if A is not a single SCC with |Q| ≥ 2        then ⊥
    else let labels = { L(s) : s ∈ Q } in
         if labels is not a valid partition       then ⊥
         else let φ = formula(A, labels) in
              if are_equivalent(A, translate(φ))  then Some φ
              else                                     ⊥
```

## Soundness

`φ` is adopted only when `are_equivalent(A, translate(φ))` holds. partscc therefore
never returns a non-equivalent answer: a partition that is not in fact
deterministic, or an acceptance shape the fairness conjunct cannot express, fails
the check and declines. The construction widens coverage; the equivalence gate
guarantees correctness.
