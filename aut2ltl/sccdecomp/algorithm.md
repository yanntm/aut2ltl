# The sccdecomp algorithm

A composite translator that decomposes a language by the **accepting SCCs** of its
automaton: it splits into one "lasso here" sub-language per accepting component —
whose union is the original — labels each, and recombines with `∨`, delegating
atomic parts to a leaf. It is the per-SCC refinement of a strength decomposition:
one piece per accepting SCC rather than per weak / terminal / strong bucket.

## Setting

A translator maps a language to a label; this one is parameterized by the leaf `Λ`
it delegates to:

```
Label       =  Some φ  |  ⊥                  -- φ an LTL formula; ⊥ = decline
Translator  =  Language → Label
```

sccdecomp asks the Language for a generalized-Büchi automaton `A = tgba(L)`,
`A = (Q, Σ, δ, q0, {F_1,…,F_m})` with acceptance `⋀_i Inf(F_i)` (a run accepts iff
it meets every color `F_i` infinitely often). It manipulates only acceptance marks,
never the transition structure, so no determinism is assumed or required.

## The per-SCC restriction

For an SCC `C ⊆ Q`, let `A↾C` be `A` with acceptance marks kept **only inside `C`**
and dropped everywhere else (an edge keeps its marks iff both of its endpoints lie
in `C`). `C` is **accepting** iff its internal marks meet every color — so `⋀_i Inf`
is satisfiable within `C`; write `acceptingSCCs(A)` for the set of such components.

`L(A↾C)` is the language of words with a run that **lassos in `C`**: it eventually
stays in `C` and accepts there. A run that lingers in the prefix or escapes `C` into
the suffix can no longer accept — those regions are now mark-free.

(Handed to `Λ` through `of(A↾C)`, the part is cleaned at the Language boundary:
purging dead states drops everything that cannot reach an accepting run in `C`, so
`A↾C` arrives trimmed to the sub-automaton that can actually lasso in `C`.)

## The identity

```
L(A)  =  ⋃_{C ∈ acceptingSCCs(A)}  L(A↾C)
```

exact in both directions:

- **⊆**: an accepting run's infinity-set is strongly connected, hence lies inside a
  single SCC `C`, and meets every color there — so the run accepts in `A↾C`.
- **⊇**: `A↾C`'s accepting marks are a subset of `A`'s, so any run accepting in
  `A↾C` also accepts in `A`.

It is a **union** — a pure position-0 language operation, exact on a
nondeterministic automaton (`L(⋃) = ⋃ L`), needing no determinization.

## The composite

```
sccdecomp(Λ) : Translator
sccdecomp(Λ)(L) =
    let A = tgba(L); {C_1,…,C_k} = acceptingSCCs(A) in
    if k < 2 then Λ(L)                                  -- atomic: nothing to split
    else let φ_j = sccdecomp(Λ)( of(A↾C_j) )  for each j
         in if any φ_j = ⊥ then ⊥                       -- a part we cannot label poisons it
            else Some( ⋁_j φ_j )
```

It recurses on **itself**, so nested structure unfolds, and reaches `Λ` only at the
base case (`k ≤ 1` — a single accepting SCC, atomic for this split). The recombined
label declines if any part declines: the split is sound only when every part
reconstructs. The recombined `∨` is simplified (own rules) so overlapping parts and
shared prefixes fold.

## Termination

`A↾C_j` keeps marks only in `C_j`, so its sole accepting SCC is `C_j`:
`acceptingSCCs(A↾C_j) = {C_j}`, of size 1. Every recursive call therefore drops to
the base case — the split strictly reduces the accepting-SCC count (`k → 1`) and
bottoms out in one level.

## Cost

Each part keeps the structure leading into its `C`, so the disjuncts share their
prefixes: the hash-consed DAG dedups them, but the flat form repeats them. The
split is an **enabler** — it turns a multi-recurrence automaton into a union of
single-recurrence languages a single-SCC leaf (e.g. `partscc`) can crack — yet it
inflates the answer wherever the leaf already succeeds whole. So it belongs under a
cost / `best_of` gate that keeps it only when it converts a decline into a smaller
answer.
