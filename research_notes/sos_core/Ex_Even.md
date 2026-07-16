# Example — `Even`

| aspect | `Even` |
|---|---|
| Language (informal) | "even number of a's met when first b encountered" |
| ω-regular | `(aa)*·b·(a\|b)^ω` |
| PSL/SERE | `{ {a[*2]}[*] ; !a }!` |
| Det. Emerson–Lei `D` | ![Even automaton](../sos_figs/img/even.png) |
| Invariant `𝓘` | ![Even invariant](../sos_core_figs/img/core_F2_even_pairs.png) |

`[a]` is the class of words that have seen only an odd number of `a`'s (and no
`b` yet); `[a·a]` the class of words that have seen only an even number of
`a`'s. Reading one more `a` flips the parity, so `[a]` and `[a·a]` form a small
strongly connected component — the parity counter. We leave it only by reading a
`b`.

Where the `b` lands us records the parity at that moment. From `[a]`, an odd
count, we go to `[a·b]`: the class of all words with an odd number of `a`'s
before the first `b` — a sequence of `a`'s was left unpaired. It is a sink: any
extension stays in the same class. From `[a·a]`, an even count, we go to `[b]`.

`[b]` is the most subtle class to interpret. It coalesces not only `b⁺`, as in
the earlier figures, but also any even number of `a`'s followed by at least one
`b`. Once `[b]` is reached the stamp classifier is content, and `[b]` absorbs any
suffix.

Acceptance therefore fixes the stem to `[b]`: an even number of `a`'s until a
`b` is met. The loop, on the other hand, can be essentially anything — `[a·b]`
and `[a·a]` canonically cover the cases where it extends by `a`'s — giving the
three accepted pairs `([b], [b])`, `([b], [a·a])`, `([b], [a·b])`.

Reading a word. Take `aaaba·ba^ω`: the stem `aaaba` gives
`([a]·[a]·[a])·([b]·[a]) = [a]·[b] = [a·b]`, and the loop `ba` gives
`[b]·[a] = [b]`; the pair `([a·b], [b])` is not accepted. Try again with `aaba`
as stem: `([a]·[a])·([b]·[a]) = [a·a]·[b] = [b]`, and `([b], [b])` is accepted.
