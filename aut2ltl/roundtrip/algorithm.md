# The roundtrip algorithm

A `Rewriter` that **re-presents one located node**. `roundtrip(R, Φ)` locates a node
`n = Φ(φ)` of the input formula, re-presents the subformula at `n` with the Rewriter
`R`, and relinks the result in place. It carries no seed — seeding (automaton →
formula) is `as_translator`'s, see `ltl_rewriter`.

## Setting

```
Rewriter  =  LTLResult → LTLResult
R         :  Rewriter               -- the node's re-presentation (e.g. relabel(Λ))
Φ         :  Formula → (Node | ⊥)   -- the node finder
```

A node `n` is a subformula occurrence, so `φ↓n = n`; `φ[n ↦ ψ]` substitutes by
hash-consed identity (`subst`).

## The construction

```
roundtrip(R, Φ) : Rewriter
roundtrip(R, Φ)(r) =
    let φ = r.formula; n = Φ(φ) in
    if n = ⊥ then r                              -- finder declines → identity (no self-credit)
    else case R( success(φ↓n) ) of
           ⊥        →  that decline              -- not masked
           Some p   →  start(tag).credit(r).credit(p)  with formula  φ[n ↦ p.formula]
```

## Faithfulness

`R` is a Rewriter, so `R(success(φ↓n)) ≡ φ↓n` (or declines). By congruence
(`w,i ⊨ φ ⇔ w[i:] ∈ L(φ)`), replacing `n` with an ω-equivalent subformula preserves
`L(φ)` under any context. A finder decline returns `r` unchanged; a declined
re-presentation propagates. Faithful-or-`⊥`.

## Relation to roundtrip_decomp

`roundtrip` re-presents the located node itself; `roundtrip_decomp` re-presents that
node's *operands*, and is a fold of `roundtrip` over them. With `R = relabel(Λ)` the
re-presentation is the language round trip; with `R = roundtrip_decomp` (tied via
`recurse`) the re-derivation compounds bottom-up.

---

# The round-trip family (package map)

This package hosts one re-presentation idea at four scopes. The base `roundtrip`
(above) and its shared machinery live at the package top; the other three scopes are
submodules, each with its own `algorithm.md`. All four are re-exported from the
package `__init__`, so callers import them from `aut2ltl.roundtrip` without depending
on where each lives.

| entry | kind | scope of one re-presentation |
|---|---|---|
| `roundtrip` (this file) | Rewriter | one located node `Φ(φ)` |
| `roundtrip_decomp/` | Rewriter | the *operands* of a located node `Φ(φ)` |
| `roundtrip_deep/` | Rewriter | the *whole formula DAG*, bottom-up, memoized |
| `roundtrip_top/` | **Translator** | the whole input *language* (seed → re-describe → relabel) |

Two levels sit here. The three Rewriters (`LTLResult → LTLResult`) re-present the
structure of an *existing* formula, increasing scope node → operands → whole-DAG. The
one Translator (`Language → Label`, `Roundtrip`) re-presents a *language* with no
formula yet in hand — it seeds a formula from a child labeler, re-describes the language
by it, and relabels. Common to all four: faithful-or-declines by construction, never by
post-hoc checking (ω-equivalent substitution preserves the language under any context).

## Shared machinery (package top)

`finder.py` (the `Finder` node-locator contract), `subst.py` (hash-cons-identity
substitution), and `cutpoints/` (concrete finders: `root`, `toplevel`) are the base
rewriter's own parts, reused by the operand submodule. The whole-DAG and Translator
submodules need no finder — their descent, resp. their language seed, is the search.
