# The non-LTL certificate — a counting family from the invariant

This package extracts, from a non-aperiodic invariant `𝓘(L) = (𝒞, λ, M, P)`,
a *counting family*: a finite, portable refutation of LTL-definability that
any third party can check by lasso membership queries alone, against any
acceptor of `L`. Reference: `research_notes/sos_toltl.md` §4, whose numbering
is used below.

## The certificate shape

Non-LTL-ness is never exhibited by one ω-word; the obstruction is a family
that toggles. Two shapes suffice — Arnold's two context shapes at the word
level:

    linear     F₁(u, v, x, p) :  n ↦ [ u·vⁿ·x ∈ L ]        toggles with n mod p
    ω-power    F₂(u, v, y, p) :  n ↦ [ u·(vⁿ·y)^ω ∈ L ]    toggles with n mod p

with `p > 1`, and "toggles" meaning: membership of the `n`-th sample equals
a declared non-constant pattern at phase `n mod p`, for **all** `n ≥ 0`.
Every sample is a lasso.

**Soundness (Thm 4.1).** A valid family of either shape refutes aperiodicity
of the syntactic algebra: membership of the `n`-th sample depends on `n`
only through the class `[vⁿ]`; were the algebra aperiodic, `[vⁿ]` would be
eventually constant, making the pattern eventually constant — contradicting
an exact period `p > 1` holding for all `n`. Hence `L` is not LTL by the
classical chain (LTL ⟹ star-free ⟹ syntactic aperiodicity). The verifier
needs only the sample verdicts and that one implication — neither the
algebra nor the extraction is trusted.

**Both shapes are load-bearing (Prop 4.2).** On a prefix-independent
language every linear family is constant (`P` is loop-determined:
`(s, e) ∈ P ⟺ (e, e) ∈ P`), so the ω-power shape is a requirement, not an
optimization — `EvenBlocks` is the specimen.

## Extraction: three scans of the tables (`extract.py`)

Write `d^π` for the idempotent power of a class `d`, and

    Val(c, d)  =  [ (c·d^π, d^π) ∈ P ]

for the membership verdict of any lasso `w·z^ω` with `[w] = c`, `[z] = d`.
Class ids ascending are shortlex order of the canonical keys, so every scan
below is a plain ascending loop and the output is a function of `L` alone —
two presentations of the language yield the byte-identical certificate.

1. **The group.** Power-iterate each class, skipping classes met inside an
   earlier orbit; stop at the first orbit with period `p > 1`
   (`sosl.sos.classify.aperiodic`). Its class `g` is the carrier,
   `v = key(g)`, with index `m ≥ 1` and cycle `g^m … g^{m+p−1}` of pairwise
   distinct classes.
2. **The separating context.** Scan linear class contexts `(x, y, t)`,
   `t ≠ [ε]`, in lexicographic id order, then ω-power contexts `(x, y)`
   likewise; for each, evaluate the pattern
   `π = (verdict at g^{m+i})_{i=0..p−1}` — linear:
   `Val(x·g^{m+i}·y, t)`; ω-power: `Val(x, g^{m+i}·y)` — and stop at the
   first non-constant `π`. The scan cannot exhaust: the syntactic
   congruence separates the distinct cycle classes `g^m ≠ g^{m+1}` through
   a context of one of the two shapes (Lemma 4.3), and that context's
   pattern is non-constant.
3. **Assembly.** Let `p′` be the minimal cyclic period of `π` (`p′ | p`,
   `p′ > 1`). Emit, absorbing the orbit index so the toggle is exact from
   `n = 0`:

        linear    F₁( key(x)·vᵐ,  v,  key(y)·key(t)^ω,  p′ )
        ω-power   F₂( key(x),     v,  vᵐ·key(y),        p′ )

   The `n`-th sample carries the power `v^{m+n}`, whose class is the cycle
   entry rotated by `n`: membership is `π[n mod p′]` for every `n ≥ 0`.

**Totality and cost (Thm 4.4).** On a non-aperiodic invariant the
extraction always emits a valid family. Every component word is a shortlex
key of length `< |𝒞|`; the absorbed power `vᵐ` costs `< |𝒞|²` letters — the
only super-linear term. At most `|𝒞|²·(|𝒞|−1)` linear and `|𝒞|²` ω-power
contexts of `p ≤ |𝒞|−1` verdicts each: `O(|𝒞|⁴)` table operations, nothing
outside the table.

## Verification (`replay.py`)

The deliverable is the family plus its check: `2p′ + 1` lasso membership
queries (`n = 0 … 2p′`) against the verifier's own oracle, confirming the
pattern on the window. The family references no automaton and no algebra —
words and one period, attachable to the specification it refutes. A
skeptic can settle the "for all `n`" claim with finitely many further
queries: the run behavior of `vⁿ` in any deterministic acceptor is
eventually periodic with computable index and period, and one stabilized
cycle of toggles proves the pattern forever.
