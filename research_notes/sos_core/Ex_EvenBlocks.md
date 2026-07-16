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

**Construction (§4).** `|EM¹| = 16` elements folding onto `|S(L)₊¹| = 8` —
the seven classes above plus `[ε]`. Here the identity row hosts *two*
classes at once: `⟨aa⟩ = ⟨ε⟩` — two `a`'s toggle back and collect nothing —
so id 0's fold column reads both `[ε]` and `[a·a]`, the collision §3.1's
fresh basepoint is built for (and `EM₊(D)` is the whole monoid: nothing is
spared, `|EM₊| = 16`). The language lives entirely in the marks: six
elements (ids 7, 10, 11, 13–15), state maps and mark patterns all varying,
are one behavior for `L` and fold onto the zero `[b·a·b]`. And unlike
`GF(aa)`'s page, the parity `Z₂` *survives* the fold — `[a]·[a] = [a·a]`,
`[a·a]·[a] = [a]` — this group is `L`'s own.

| id | word | st | mk | rmul | → class |
|---|---|---|---|---|---|
| 0 | `eps` | [0 1] | [{} {}] | 1 2 | 0 `eps` / 5 `a;a` |
| 1 | `b` | [0 0] | [{1} {0}] | 3 4 | 1 `b` |
| 2 | `a` | [1 0] | [{} {}] | 5 0 | 2 `a` |
| 3 | `b;b` | [0 0] | [{1} {0,1}] | 3 6 | 1 `b` |
| 4 | `b;a` | [1 1] | [{1} {0}] | 7 1 | 3 `b;a` |
| 5 | `a;b` | [0 0] | [{0} {1}] | 8 9 | 4 `a;b` |
| 6 | `b;b;a` | [1 1] | [{1} {0,1}] | 10 3 | 3 `b;a` |
| 7 | `b;a;b` | [0 0] | [{0,1} {0}] | 10 11 | 6 `b;a;b` |
| 8 | `a;b;b` | [0 0] | [{0,1} {1}] | 8 12 | 4 `a;b` |
| 9 | `a;b;a` | [1 1] | [{0} {1}] | 13 5 | 7 `a;b;a` |
| 10 | `b;b;a;b` | [0 0] | [{0,1} {0,1}] | 10 14 | 6 `b;a;b` |
| 11 | `b;a;b;a` | [1 1] | [{0,1} {0}] | 7 7 | 6 `b;a;b` |
| 12 | `a;b;b;a` | [1 1] | [{0,1} {1}] | 10 8 | 7 `a;b;a` |
| 13 | `a;b;a;b` | [0 0] | [{0} {0,1}] | 10 15 | 6 `b;a;b` |
| 14 | `b;b;a;b;a` | [1 1] | [{0,1} {0,1}] | 10 10 | 6 `b;a;b` |
| 15 | `a;b;a;b;a` | [1 1] | [{0} {0,1}] | 13 13 | 6 `b;a;b` |
