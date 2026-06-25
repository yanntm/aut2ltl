# The Muller (general-case) cascade translator

The fallback leaf of the kr cascade engine: the full, general **Muller-DNF**
construction of Boker, Lehtinen & Sickert, *On the Translation of Automata to Linear
Temporal Logic* (**FoSSaCS 2022**) — the Muller case of the acceptance encoding. It
accepts every cascade an LTL-definable language produces — the dispatch chain reaches
it only when no simpler acceptance class (`acc` / `weak` / `buchi` / `cobuchi`)
applies — and never declines in practice (LTL input is counter-free). It is the
explosive-but-complete form, landing in **Δ₂** (reactivity, per the hierarchy of
digest §2); the simpler members exist to avoid it where they can.

Section numbers below refer to the in-package digest
[`../paper/automata-to-ltl-construction.md`](../paper/automata-to-ltl-construction.md).

## Setting

```
Label             =  Some φ  |  ⊥                  -- φ an LTL formula; ⊥ = decline
CascadeTranslator =  CascadeHolder → Label
```

See [`bls/cascade_translator.py`](../cascade_translator.py) and the adapter
[`bls/aut2cas.py`](../aut2cas.py).

## The formula (digest §9.3)

The acceptance condition is first lifted from the normalized `D` onto the cascade's
configurations (Prop. 7/8): `good_muller_sets` reads the family of **good config-sets**
`M` — the recurrent sets `D` actually exhibits. A run accepts iff the set of
configurations it visits infinitely often is *exactly* some good `M`:

    φ  =  ⋁_{M good}  ( ⋀_{C ∈ M} ¬Fin(C)  ∧  ⋀_{C ∉ M} Fin(C) )

with `Fin(C)` the "only finitely often in configuration `C`" formula (Lemma 7, digest
§9.2; [`bls/operators/fin.py`](../operators/fin.py), built on the five inductive
reachability operators in [`bls/operators/`](../operators)). Each disjunct pins the
infinity-set to one good `M`; the disjunction covers them all. `φ` is a Boolean
combination of `Σ₂` formulas, hence **Δ₂**. `assemble_muller_dnf` builds it.

## Degenerate cases

- A trivial cascade (`num_levels == 0`) collapses to `⊤`/`⊥` by the acceptance of the
  normalized `D`.
- An empty good-set family ⇒ the empty disjunction ⇒ `φ = false` (the empty language).

## Soundness & cost

Exact for any LTL-definable ω-regular language (the construction is complete), but the
flat form is **exponential** in the configuration count (up to `2^{O(mn)}` good sets,
digest §9.3) — the size cost the whole portfolio exists to avoid where a structured
fragment applies. The hash-consed DAG shares the repeated `Fin(C)` sub-terms (each
computed once, reused across disjuncts).

---

# Beyond the paper — implementation choices

## Fin-reach fold (dropping implied conjuncts)

Default on (`KR_FOLD_FIN_REACH=0` restores the full Muller term). For a good set `M`, a
run with `Inf ⊇ M` — forced by the `¬Fin(C ∈ M)` conjuncts — has a strongly-connected
infinity-set, so every configuration it visits is reachable from `M`. Hence a `C`
*unreachable* from `M` is necessarily visited finitely often and its `Fin(C)` conjunct
is already implied by the kept ones. Those conjuncts are dropped
(`config_graph.configs_reachable_from`) **before** `fin_c` is built — the explosive
step — so dropped configurations cost nothing. The fold removes only entailed
conjuncts, so the language is unchanged.
