# The gen algorithm

A **shape-parametric exhaustive generator** of tiny ω-automata for the census: fix
a shape (a count of states, atomic propositions, acceptance sets), enumerate
*every* automaton of that shape under a fully general slot model, reduce each with
one Spot pass, and fold relabeling-twins with two pre-write dedup gates. Its output
is a corpus of byte-distinct, AP-canonical HOA automata — the raw material the
survey harness then runs `aut2ltl` over. It generates; it does not translate or
curate.

## Setting

A **shape** fixes the three axes of the enumeration:

- **`n`** — number of states,
- **`k`** — number of atomic propositions,
- **`c`** — number of acceptance sets (generalized-Büchi colours).

Written `Shape(n, k, c)`, with tag `"<n>state<k>ap<c>acc"` — so `Shape(2,1,1)` is
the historical `2state1ap1acc` census and `Shape(1,1,0)` is `1state1ap0acc`, the
first new instance.

A shape induces a finite **generator-id space** `[0, N)` and a bijection `combo_at`
from an id to one concrete automaton, so every survivor is reproducible from its id
alone (its filename `aut_<id>.hoa`). States are `Q = {q_0, …, q_{n-1}}`, with
**`q_0` always initial**.

## The slot model

The unit of choice is an **edge slot**. For every ordered state pair and every
**markset** (a subset of the acceptance colours) there is exactly one slot:

```
Markset  =  2^{0,…,c-1}                 -- |Markset| = 2^c ; c = 0 ⇒ {∅}
Slot     =  Q × Q × Markset             -- |Slots|   = n² · 2^c
```

A separate slot per markset is what lets two parallel edges with the same
`(src,dst)` but different colours coexist — so the model is **fully general**: every
slot is always present with its full choice set, and we never a priori drop a
`(src,dst,markset)` slot as "useless". Full enumeration + dedup therefore cannot
accidentally miss a language.

Each slot is independently assigned a **guard** — a Boolean function over the `k`
APs. Order the `2^k` minterms `0..2^k-1` (minterm `m`'s bit `i` = the value of AP
`i`); a guard is then a **truth-table bitmask** over those minterms, giving a clean
general index:

```
Guards_k  =  { 0 … 2^(2^k) − 1 }        -- |Guards_k| = 2^(2^k) ; guard 0 = ∅ = absent
```

**Guard `0` (the empty bitmask, the all-false function) means "edge absent".** This
per-slot off-switch is the *only* structural pruning in the model — choosing it
removes that edge; nothing else is dropped a priori.

For `k = 1` there are two minterms — `m0 = {a:false}` (literal `!a`), `m1 = {a:true}`
(literal `a`) — so the four guards, **in bitmask order**, are:

```
0 = ∅        → absent          2 = {m1}      → a
1 = {m0}     → !a              3 = {m0,m1}   → true (1)
```

(This is the general truth-table order; it **renumbers** the historical corpus,
which used `0,1,a,!a` — see *Validation*.)

A **combo** is one guard per slot; the combos are the generator-id space:

```
combos     =  Guards_k ^ Slots
N          =  |combos|  =  (2^(2^k)) ^ (n² · 2^c)
combo_at   :  [0, N) → combos          -- id ↦ combo bijection (slots ordered
                                          src-outer / dst / markset by increasing
                                          size then lex; product, last slot fastest)
```

For `Shape(2,1,1)`: `|Slots| = 4·2 = 8`, `|Guards_1| = 4`, so `N = 4⁸ = 65536`.
For `Shape(1,1,0)`: `|Slots| = 1·1 = 1`, so `N = 4` — the four self-loop guards on a
single state under acceptance `t`: absent ⇒ no run ⇒ **`0`** (false / empty), `!a`
⇒ **`G!a`**, `a` ⇒ **`Ga`**, true ⇒ **`1`** (universal / `Σ^ω`). The `Ga`/`G!a`
pair folds by polarity; the degenerate absent combo is kept and generated like any
other.

## Build and reduce

`combo_at(id)` is realised as a `twa_graph`: `n` states, the shape's acceptance
condition over its `c` sets (below), and one edge per non-absent slot carrying its
guard BDD and its markset as colours.

### The acceptance family

The three axes above fix the *combos*; a fourth, optional axis fixes how the `c`
colours are read as an **acceptance condition**. It is orthogonal to the
enumeration — same slots, marksets, guards, ids and `N` — so it moves no existing
index; only the acceptance *formula* changes. `Shape.acc` selects it, defaulting to
`"gba"`:

- **`gba`** (default) — generalized Büchi `Inf(0) & … & Inf(c-1)` (so `c = 0` is
  the `t` condition, every run accepting). This is the historical census; its tag
  is the bare `<n>state<k>ap<c>acc` and its output is byte-identical to before.
- **`parity`** — parity max even over the `c` colours (`c = 3` gives
  `Inf(2) | (Fin(1) & Inf(0))`), tag `<n>state<k>ap<c>acc_parity`. Requires
  `c >= 1`. Its **Fin/Inf alternation is what generalized Büchi cannot express** —
  the persistence rung and the deeper parity/Wagner degrees only appear here.

An edge's markset may carry several colours under either family; the acceptance is
just the formula evaluated on the colour-sets seen infinitely often, so the
enumeration stays fully general. Realised in `build._set_acceptance`.

Each raw automaton is passed through **one** structural reduction:

```
reduce  =  spot.postprocess(type=generic, level=high, pref=small)
```

the same convenience `aut2ltl`'s own input cleanup uses (`language.py::_clean`).
**Generic** keeps the acceptance *family* (no degeneralization / determinization);
**Small** is the polynomial structural reducer. We deliberately do *not* use the
`deterministic` pref — universality stays undecided by Spot, exactly as the tool
will see it (this is the point of the "true" finding; see `../README.md`).

## The two dedup gates (pre-write, in order)

A twin is **never built into a file**. After reduction, the HOA string passes two
gates; only survivors are written:

1. **byte-identical** — skip a result whose md5 was already emitted (first id
   wins). Cheap pre-filter.
2. **AP-canonical** — fold the `a ↔ !a` polarity / AP-rename twins via the shared
   key `polarity ∘ names` from `survey/normalize` (only the byte-distinct
   survivors pay this cost). Trusted sound for this purpose: folding a relabeling
   is the *same* test of `aut2ltl` under a renamed alphabet, not a new one.

We intentionally dedup **only up to relabeling** — never by language or by
isomorphism beyond renaming. Language-equivalent but genuinely
differently-*shaped* encodings are **kept**: that a round-trip recovers the same
formula is the thing the census measures, not an assumption it bakes in.

## Validation (regenerating a known shape)

The index is **not** required to match the historical corpus — the first census was
a first attempt, and a more general scheme may renumber it. Correctness of a
regeneration is checked by **language-set parity, not filenames**: regenerating
`Shape(2,1,1)` must yield the same survivor *set* (the AP-canonical dedup-key set is
identical → still 929 survivors), and re-running the survey over the renumbered
corpus must reproduce the same counts and ventilation (LTL / not-LTL / ambiguous,
verified-equivalent totals). Reindexing is cheap and acceptable; a drift in those
counts is the regression signal.

## Scope

All three axes — `n` (states), `k` (APs), `c` (acceptance) — are parametric and
realised. A guard is a subset of the **letters** of `2^AP`; the letters are the
`2^k` minterms, walked once (`build._minterm_bdds`, the `APBDDIterator` idea from
sogits/libITS, over Spot/BuDDy BDDs), and `Guards_k` is their **powerset**, so for
`k = 2` the 16 guard codes realise *all 16 Boolean functions over two variables*
(`false`, the 4 minterms, `a`,`!a`,`b`,`!b`, `a|b`, `a^b`, …, `true`). Both
degenerate ends fall out of the one minterm walk: `k = 0` is the one-letter
alphabet (guards `{absent, true}`, cf. `EmptyAPIterator`) and `c = 0` is the
acceptance `t`.

Enumeration does not scale far in any axis (`N` is doubly exponential in `k`,
exponential in `n²` and `2^c`), so this stays a one-off census per small shape, not
a general corpus engine.

## Realisation (module map)

```
gen/shape.py      Shape(n,k,c): the slot model, Guards_k, marksets, |Slots|, N,
                  combo_at — pure, stdlib only (no Spot).
gen/build.py      build_aut(shape, combo) → twa_graph, reduce_aut, aut_at — the
                  Spot/BuDDy realisation of a combo.
gen/enumerate.py  the driver: enumerate combos → reduce → two dedup gates → write
                  raw/<shape.tag>/aut_<id>.hoa. CLI: shape + optional smoke limit.
```

Output: `raw/<tag>/` is regenerable scratch (gitignored); the validated snapshot is
promoted to `corpus/<tag>/` (git-tracked), where `tag = "<n>state<k>ap<c>acc"`.
