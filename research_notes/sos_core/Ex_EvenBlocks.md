# Example 4 — `EvenBlocks`

| aspect | `EvenBlocks` |
|---|---|
| Language (informal) | "Infinitely often b, and all sequences of a are eventually even in length" |
| ω-regular | `(a\|b)*·((aa)*·b)^ω` |
| PSL/SERE | `GF!a ∧ FG(!a → X{ {a[*2]}[*] ; !a }!)` |
| LTL | **no** |
| Geometry | reactivity: strictly above recurrence and persistence |
| Recognizer | parity `{0,1,2}`, proper — a genuine Rabin pair; neither DBA nor DCA |
| Det. Emerson–Lei `D` | ![EvenBlocks automaton](../sos_figs/img/evenblocks.png) |
| Invariant `𝓘` | ![EvenBlocks invariant](../sos_core_figs/img/core_F3_evenblocks_pairs.png) |

As in `Even`, `[a]` and `[a·a]` are the classes of words that have seen only
`a`'s, in odd and even count — the same parity SCC, the same period-2
power cycle (`[a]·[a] = [a·a]`, `[a·a]·[a] = [a]`): a genuine group, and the
LTL row's *no*, read off the drawing. A `b` exits the SCC:
from an even count to `[b]`, from an odd count to `[a·b]` — but unlike
`Even`, where the first `b` settled everything, no exit is final here.

`[b]` agglomerates the words made of even `a`-blocks and `b`'s — the leading
block even as read, every block closed inside the word even, a trailing run
of `a`'s allowed if even — containing at least one `b`. The cycle
`[b]`/`[b·a]` grows a trailing block: an unpaired trailing `a` sits in
`[b·a]`, its partner returns to `[b]`. `[a·b]` and `[a·b·a]` are their twins
for a leading block left odd — `[a·b·a]` reads the even-block cycle entered
mid-block, an open run of `a`'s at both ends. The last class, `[b·a·b]` (key
word `bab`), holds the words that have *completed* an odd block, closed by
`b`'s on both sides: it is the two-sided zero, absorbing every extension.
Absorbing is not dead: the language is prefix-independent — no finite prefix
ever decides membership — and the zero reappears below as an accepting stem.

Acceptance is six pairs:

```
P = { ([b], [b]),      ([a·b], [b]),      ([b·a·b], [b]),
      ([b·a], [a·b·a]), ([b·a·b], [a·b·a]), ([a·b·a], [a·b·a]) }
```

— exactly the linked pairs whose loop is `[b]` or `[a·b·a]`, the two readings
of "only even blocks, and `b`'s, forever": block-aligned, or entered
mid-block. The stems are everything such a loop absorbs — every class
carrying at least one `b`, the zero included: finitely many completed odd
blocks are forgiven, prefix independence again. The two all-`a` classes
appear in no pair: the loop holds infinitely many `b`'s, rotation pushes one
of them back into the stem, so a canonical stem must carry a `b` — and `[a]`,
`[a·a]` cannot.

Reading a lasso (Definition 3.5). Take `aabaab·(baa)^ω`. The loop first:
`𝒮(baa) = ([b]·[a])·[a] = [b·a]·[a] = [b]`, already idempotent, so `e = [b]`.
The stem, grouped `(aa)·(baab)` and reduced on each side before conjoining:
`(aa) = [a]·[a] = [a·a]` is the parity cycle;
`(baab) = ([b]·[a])·([a]·[b]) = [b·a]·[a]·[b] = [b]·[b] = [b]` runs the
`[b]`/`[b·a]` cycle, closing on an even count. Conjoining,
`[a·a]·[b] = [b]`, so `𝒮(aabaab) = [b]`. The queried stem is
`s = 𝒮(u)·e = [b]·[b] = [b]`, and the name `([b], [b])` is in `P`:
accepted — every block the word completes is even, and `b`'s recur.

**Construction (§4).** `|EM₊| = 16` elements folding onto the `|𝒞| = 7`
classes above. The first row is the collision §3.1's fresh basepoint is
built for: `⟨a·a⟩ = ⟨ε⟩` — two `a`'s toggle back and collect nothing — so
the identity is itself an image of nonempty words, `EM₊` is the whole
monoid, and the neutral class `[a·a]` is genuine language data. The language
lives entirely in the marks: six elements — `⟨b·a·b⟩` and its five mark
variants below it — are one behavior for `L` and fold onto the zero
`[b·a·b]`. And unlike `GF(aa)`'s page, the parity `Z₂` *survives* the
fold — `[a]·[a] = [a·a]`, `[a·a]·[a] = [a]` — this group is `L`'s own.

| ⟨w⟩ | at 0 | at 1 | ·⟨b⟩ | ·⟨a⟩ | → class |
|---|---|---|---|---|---|
| `⟨a·a⟩` | `(0, ∅)` | `(1, ∅)` | `⟨b⟩` | `⟨a⟩` | `[a·a]` |
| `⟨b⟩` | `(0, {1})` | `(0, {0})` | `⟨b·b⟩` | `⟨b·a⟩` | `[b]` |
| `⟨a⟩` | `(1, ∅)` | `(0, ∅)` | `⟨a·b⟩` | `⟨a·a⟩` | `[a]` |
| `⟨b·b⟩` | `(0, {1})` | `(0, {0,1})` | `⟨b·b⟩` | `⟨b·b·a⟩` | `[b]` |
| `⟨b·a⟩` | `(1, {1})` | `(1, {0})` | `⟨b·a·b⟩` | `⟨b⟩` | `[b·a]` |
| `⟨a·b⟩` | `(0, {0})` | `(0, {1})` | `⟨a·b·b⟩` | `⟨a·b·a⟩` | `[a·b]` |
| `⟨b·b·a⟩` | `(1, {1})` | `(1, {0,1})` | `⟨b·b·a·b⟩` | `⟨b·b⟩` | `[b·a]` |
| `⟨b·a·b⟩` | `(0, {0,1})` | `(0, {0})` | `⟨b·b·a·b⟩` | `⟨b·a·b·a⟩` | `[b·a·b]` |
| `⟨a·b·b⟩` | `(0, {0,1})` | `(0, {1})` | `⟨a·b·b⟩` | `⟨a·b·b·a⟩` | `[a·b]` |
| `⟨a·b·a⟩` | `(1, {0})` | `(1, {1})` | `⟨a·b·a·b⟩` | `⟨a·b⟩` | `[a·b·a]` |
| `⟨b·b·a·b⟩` | `(0, {0,1})` | `(0, {0,1})` | `⟨b·b·a·b⟩` | `⟨b·b·a·b·a⟩` | `[b·a·b]` |
| `⟨b·a·b·a⟩` | `(1, {0,1})` | `(1, {0})` | `⟨b·a·b⟩` | `⟨b·a·b⟩` | `[b·a·b]` |
| `⟨a·b·b·a⟩` | `(1, {0,1})` | `(1, {1})` | `⟨b·b·a·b⟩` | `⟨a·b·b⟩` | `[a·b·a]` |
| `⟨a·b·a·b⟩` | `(0, {0})` | `(0, {0,1})` | `⟨b·b·a·b⟩` | `⟨a·b·a·b·a⟩` | `[b·a·b]` |
| `⟨b·b·a·b·a⟩` | `(1, {0,1})` | `(1, {0,1})` | `⟨b·b·a·b⟩` | `⟨b·b·a·b⟩` | `[b·a·b]` |
| `⟨a·b·a·b·a⟩` | `(1, {0})` | `(1, {0,1})` | `⟨a·b·a·b⟩` | `⟨a·b·a·b⟩` | `[b·a·b]` |
