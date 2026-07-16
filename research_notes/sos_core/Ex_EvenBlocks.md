# Example 4 — `EvenBlocks`

| aspect | `EvenBlocks` |
|---|---|
| Language (informal) | "Infinitely often b, and all sequences of a are eventually even in length" |
| ω-regular | `(a\|b)*·((aa)*·b)^ω` |
| PSL/SERE | `GF!a ∧ FG(!a → X{ {a[*2]}[*] ; !a }!)` |
| Det. Emerson–Lei `D` | ![EvenBlocks automaton](../sos_figs/img/evenblocks.png) |
| Invariant `𝓘` | ![EvenBlocks invariant](../sos_core_figs/img/core_F3_evenblocks_pairs.png) |

As in `Even`, `[a]` and `[a·a]` are classes of words that have seen only `a`'s,
in odd and even count respectively. Exiting the SCC with an even number of `a`'s
before the `b`, in both cases, brings us to class `[b]`. So `[b]`, like in
`Even`, agglomerates all words with an even number of `a`'s up to a `b`. But
additionally to `Even`, using the cycle `[b]`/`[b·a]`, `[b]` also agglomerates
even `a`-blocks interrupted by arbitrary numbers of `b`'s, returning to `[b]`
after stabilizing. So `[b]` is any sequence made of only even `a`-blocks or
`b`'s, finishing on a `b`.

Logically `([b], [b])` is accepted, as it covers most of the cases we expected
to capture. The other accepting pairs all carry either `[b]` in their loop, or
`[a·b·a]`, which covers the rotated cycle containing only words where every
block of `a`'s is even in length. All classes can be the stem of at least one
accepting continuation: the language is prefix agnostic. However every accepting
stem of an accepted pair of this canonical representation contains at least some
`b` — a constraint enforced by the canonical form using rotation, since the loop
must already contain at least one `b` (there are infinitely many). Rotation
pushes this `b` from the loop back into the stem.

Reading a word. Take `aabaab·baa`, grouped `(aa)·(baab)` and reduced on each
side before conjoining. `(aa) = [a]·[a] = [a·a]` is the parity cycle;
`(baab) = [b]·[a]·[a]·[b] = [b·a]·[a]·[b] = [b]·[b] = [b]` runs the `[b]`/`[b·a]`
cycle, closing on an even count. Conjoining, `[a·a]·[b] = [b]`, so
`𝒮(aabaab) = [b]`. The loop `baa = [b]·[a]·[a] = [b·a]·[a] = [b]` is idempotent,
so `e = [b]`. The stem is `s = [b]·[b] = [b]`, and the name `([b], [b])` is
accepted.
