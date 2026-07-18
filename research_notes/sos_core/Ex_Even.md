# Example 3 — `Even`

| aspect | `Even` |
|---|---|
| Language (informal) | "even number of a's met when first b encountered" |
| ω-regular | `(aa)*·b·(a\|b)^ω` |
| PSL/SERE | `{ {a[*2]}[*] ; !a }!` |
| LTL | **no** |
| Geometry | guarantee, properly open: a good finite prefix decides |
| Recognizer | reachability — an accepting sink to reach, the weakest acceptance there is |
| Det. Emerson–Lei `D` | ![Even automaton](../sos_figs/img/even.png) |
| Invariant `𝓘` | ![Even invariant](../sos_core_figs/img/core_F2_even_pairs.png) |

`[a]` is the class of words that have seen only an odd number of `a`'s (and no
`b` yet); `[a·a]` the class of words that have seen only an even — and
nonzero — number of `a`'s, again with no `b` yet. Reading one more `a` flips
the parity, so `[a]` and `[a·a]` form a small strongly connected component
(SCC) —
the parity counter. We leave it only by reading a `b`. The counter is a
genuine period-2 power cycle — `[a]·[a] = [a·a]`, `[a·a]·[a] = [a]` — a
group: the LTL row's *no*, read off the drawing.

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

Reading a lasso (Definition 3.5). Take `aaaba·(ba)^ω`. The loop first:
`𝒮(ba) = [b]·[a] = [b]`, already idempotent, so `e = [b]`. The stem:
`𝒮(aaaba) = ([a]·[a]·[a])·([b]·[a]) = [a]·[b] = [a·b]`, and the queried stem
is `s = 𝒮(u)·e = [a·b]·[b] = [a·b]` — the sink absorbs. The name
`([a·b], [b])` is not in `P`: rejected, an odd run of `a`'s was left
unpaired. A *different* lasso, one `a` shorter — stem `aaba`, an even
prefix — lands elsewhere: `𝒮(aaba) = ([a]·[a])·([b]·[a]) = [a·a]·[b] = [b]`,
`s = [b]·[b] = [b]`, and `([b], [b])` is accepted.

One lasso, two names. A word's verdict never depends on its presentation, but
its name can. Present `b·(ab)^ω` as written: the loop's class
`𝒮(ab) = [a]·[b] = [a·b]` is the sink, already idempotent, and the stem is
absorbed, `s = [b]·[a·b] = [b]`:
the name `([b], [a·b])`, accepted. Rotate one letter onto the stem —
`b·(ab)^ω = ba·(ba)^ω`, the same ω-word — and the loop's class is now
`𝒮(ba) = [b]·[a] = [b]`, also idempotent, with `s = [b]·[b] = [b]`: the name
`([b], [b])`, accepted again. Two distinct pairs naming the one ω-word,
connected by a single rotation — and both in `P`, as saturation (§3.4)
demands.

**Construction (§4).** `|𝒞_D| = 6` classes quotiented onto the `|𝒞| = 4`
classes above. The delicate row is `⟨a·a⟩`: its transition map is the
*identity* — two `a`'s return every state to itself — and only the mark
collected at the accepting sink (state `0`) sets its mark map apart from
empty. The quotient
keeps the distinction too, as §3.1 demands: `[a·a]` is a neutral class of
nonempty words — its row and column in `𝒞`'s table move nothing — while
`[ε]` is the fresh basepoint: the neutral-vs-identity distinction of §3.1,
exhibited by the machine. The quotient merges the mark-only splits
`⟨b⟩, ⟨b·b⟩` and `⟨a·b⟩, ⟨a·b·b⟩`.

| ⟨w⟩ | at 0 | at 1 | at 2 | at 3 | ·⟨b⟩ | ·⟨a⟩ | → class |
|---|---|---|---|---|---|---|---|
| `⟨b⟩` | `(0, {0})` | `(3, ∅)` | `(0, ∅)` | `(3, ∅)` | `⟨b·b⟩` | `⟨b·b⟩` | `[b]` |
| `⟨a⟩` | `(0, {0})` | `(2, ∅)` | `(1, ∅)` | `(3, ∅)` | `⟨a·b⟩` | `⟨a·a⟩` | `[a]` |
| `⟨b·b⟩` | `(0, {0})` | `(3, ∅)` | `(0, {0})` | `(3, ∅)` | `⟨b·b⟩` | `⟨b·b⟩` | `[b]` |
| `⟨a·b⟩` | `(0, {0})` | `(0, ∅)` | `(3, ∅)` | `(3, ∅)` | `⟨a·b·b⟩` | `⟨a·b·b⟩` | `[a·b]` |
| `⟨a·a⟩` | `(0, {0})` | `(1, ∅)` | `(2, ∅)` | `(3, ∅)` | `⟨b⟩` | `⟨a⟩` | `[a·a]` |
| `⟨a·b·b⟩` | `(0, {0})` | `(0, {0})` | `(3, ∅)` | `(3, ∅)` | `⟨a·b·b⟩` | `⟨a·b·b⟩` | `[a·b]` |
