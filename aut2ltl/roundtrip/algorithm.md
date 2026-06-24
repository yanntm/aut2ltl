# The roundtrip algorithm

A decorator translator that **re-derives one node of a seed formula**. It asks a
child labeler `Λ` for a faithful formula for the input language, lets an injected
**cutpoint finder** pick any one node of that formula's DAG, reconstructs the
language of the sub-DAG rooted there (relabels it with `Λ`), and relinks the new
label in place. It is a **local, single cut**: one seed, one node, one relabel, one
relink. It is agnostic to *why* a node was chosen — the finder owns that — and owns
no global concern (iterating to a fixpoint, choosing the smaller of two answers,
bounding the recursion); those belong to the assembly.

The whole-seed relabel of the previous `roundtrip` (now `roundtrip_top`) is the
special case **finder = root**: cutting the root re-derives the entire language.

## Setting

A translator maps a language to a label; this one is parameterized by the child `Λ`
it both **seeds from** and **relabels with**, and by the finder `Φ`:

```
Label       =  Some φ  |  ⊥                  -- φ an LTL formula; ⊥ = decline
Translator  =  Language → Label
```

It uses three floor operations — the formula builder and two DAG primitives:

```
lang(φ)            =  the Language whose description is the LTL formula φ
sub(D, n)          =  the sub-DAG of D rooted at node n  (itself an LTL formula)
relink(D, n, ψ)    =  D with the sub-DAG at n replaced by ψ
```

`D` is the **hash-consed DAG** of the seed formula; a *node* `n` is a shared
sub-formula occurrence in `D`. `relink` substitutes by node identity, so a shared
node is replaced at *every* occurrence at once — one re-derivation, reused across
the DAG.

## The finder

```
Finder  =  Dag → Node | ⊥                    -- configured/curried at build time
```

The finder inspects the seed DAG and returns **one node**, or **declines** (`⊥`).
Its single hard guarantee is that the returned node **occurs in `D`** — so `relink`
has a target; soundness needs nothing more, since by congruence (below) *any*
occurring node is safe to re-derive. The finder is **not** responsible for the node
being a *useful* cut (size is a `best_of` gate's concern) nor for progress under
iteration (the assembly bounds that; a finder *may* additionally promise strict
descent, but that is an optional strength, not the contract). One node per call:
multi-cut is the assembly iterating the brick until the finder declines.

## The cut

Three moves — **seed**, **cut & relabel**, **relink**:

```
roundtrip(Λ, Φ)(L) =
    let s = Λ(L)                          -- SEED:   a faithful formula for L  (or ⊥)
    in  if s = ⊥        then ⊥            --         nothing to cut; propagate the decline
        else let n = Φ(s.formula) in
             if n = ⊥   then s            -- finder declines: the seed VERBATIM, no self-credit
             else let ψ = Λ( lang( sub(s.formula, n) ) ) in       -- CUT & RELABEL
                  if ψ = ⊥ then ⊥         --         a declined relabel is OUR decline; we do not mask it
                  else relink(s, n, ψ)    -- RELINK: splice ψ in at n; THIS is the answer (credited)
```

### The three moves

- **Seed** (`Λ(L)`). roundtrip has no formula of its own; its input is an automaton.
  It asks `Λ` for *any* faithful formula — typically the heavy general floor (the
  cascade), large but structurally characteristic. A declined seed propagates: there
  is nothing to cut.
- **Cut & relabel** (`Λ(lang(sub(D,n)))`). The finder names a node `n`; its sub-DAG
  `sub(D,n)` is a self-contained formula denoting an ω-language. Re-describe *that*
  language by `lang(·)` and relabel it with `Λ` — a fresh presentation of the node's
  language, on which `Λ` often produces a far smaller formula (a daisy peel, a clean
  split, a terminal SCC) than the node the seed carried.
- **Relink** (`relink(s, n, ψ)`). Splice the new label `ψ` back into the seed DAG at
  `n`. The surrounding formula is untouched; only the one node changes. The result
  carries our stamp plus `ψ`'s and the seed's provenance — then roundtrip steps aside.

### Outcome table (no masking, no special-casing)

| event | result |
| --- | --- |
| seed `Λ(L)` declines | `⊥` |
| finder declines (`Φ = ⊥`) | the seed **verbatim** — passthrough, **no self-credit** |
| relabel `Λ(lang(sub))` declines | `⊥` — our decline; the cut bought nothing and we do *not* echo `sub` |
| relabel succeeds | `relink(s, n, ψ)`, **credited** — even if larger; degradation is the gate's call |

### Degenerate cases

- **finder = root**: `sub` is the whole formula, `relink` replaces all of `D` ⇒
  `Λ(lang(s))` — exactly `roundtrip_top`.
- **node is a leaf** (an atom / constant): `lang(a)` relabels to `a` — a harmless
  no-op cut.
- **already canonical**: when re-describing the node yields a presentation `Λ`
  handles no differently, the relabel reproduces the node and the relink is identity.
  (Repeated cuts reach this fixpoint fast; iterating up to it is the assembly's call.)

## Soundness

roundtrip is **faithful-or-declines**, by construction, never by post-hoc checking.
Every emitted formula is language-equivalent to `L`:

1. `Λ` is faithful ⇒ the seed `s ≡ L`; so it suffices to preserve `L(s)` under the cut.
2. ω-language equivalence is a **congruence** in LTL: `w, i ⊨ φ ⇔ w[i:] ∈ L(φ)`, so
   two ω-equivalent formulas are interchangeable at *any* position. The node `n`
   denotes the language `L(sub(D,n))`; `lang(·)` denotes exactly that language and
   `Λ` labels it faithfully, so `ψ ≡ sub(D,n)`. Substituting an ω-equivalent
   sub-formula for `n` therefore leaves `L(relink(s,n,ψ)) = L(s) = L` unchanged —
   wherever `n` sits in the DAG, under whatever temporal context.

Declines propagate (a `⊥` seed or relabel yields `⊥`); a finder-decline returns the
already-faithful seed untouched. roundtrip adds no soundness obligation of its own —
it only ever returns one of `Λ`'s own faithful-or-declined results, possibly with one
node swapped for an ω-equivalent re-derivation.

## Why it fires

The seed is faithful but often *ugly* because the input presented the language in a
shape `Λ`'s structural translators could not exploit — and that ugliness is
frequently **local to a sub-formula**: one node sits on a hard presentation while the
rest is already clean. The product automaton hides any such factoring, but the seed
*formula* exposes it as DAG structure. Cutting that node and re-describing only its
language hands `Λ` a fresh, simpler presentation of the part that needs it, leaving
the good structure in place. (`roundtrip_top` re-derives the whole and so cannot keep
the good part; the generalization is exactly the freedom to cut *below* the root.)

## Out of scope (the assembly's concern)

roundtrip computes one local cut and trusts its inputs. Pushed to the assembly that
drives it:

- the **finder strategy** — which node (a top `∧`/`∨` operand, the largest sub-DAG,
  a temporal scope, …); the brick treats `Φ` as opaque and is sound for any node.
- **multi-cut / fixpoint** — closing the open recursion to cut repeatedly until the
  finder declines, and any termination bound on that iteration.
- the **never-regress gate** — keeping the relink only when a comparator says it beat
  the seed (`best_of`); the brick returns its result unconditionally, larger or not.
- **memoization / sharing** — preserving DAG sharing across cuts.

Stripping these out is the point: roundtrip *is* just seed, cut, relabel, relink.
