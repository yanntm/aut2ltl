# Example 1 — `aUGb`

| aspect | `aUGb` |
|---|---|
| Language (informal) | "a finitely until always b" |
| ω-regular | `a*·b^ω` |
| LTL | `a U G !a` |
| Det. Emerson–Lei `D` | ![aUGb automaton](../sos_figs/img/aUGb.png) |
| Invariant `𝓘` | ![aUGb invariant](../sos_core_figs/img/core_F0_astar_bomega_b_pairs.png) |

`[a]` is the class of finite words `a⁺` only containing `a`. `[a·b]` is words of
the form `a⁺b⁺` that start with a sequence of `a`'s then a sequence of `b`'s.
`[b]` is the class `b⁺` of words only containing `b`. `[b·a]` the class of words
that have met an `a` after `b` (somewhere in the word).

Acceptance is in two pairs: `([b], [b])` representing the word `b^ω`, and
`([a·b], [b])` the words of the form `a⁺·b^ω`. Note that these are classes:
`([a·b], [b])` represents `a·b^ω`, `ab·b^ω`, `aabbb·b^ω`, `ab·bbb^ω`, …

Consider the lasso `ababba·b^ω`. Compute
`𝒮(ababba) = [a]·[b]·[a]·[b]·[b]·[a] = [a·b]·[a·b]·[b·a]` (an arbitrary
parenthesizing, since `𝒮` is associative); note `[a·b]·[a·b] = [b·a]` and
`[b·a]` right-extended by anything is still `[b·a]`, so `𝒮(ababba) = [b·a]`. The
class of `b` is `[b]`. The pair `([b·a], [b])` is not accepted, so the lasso
represented by `ababba·b^ω` is not in the language.
