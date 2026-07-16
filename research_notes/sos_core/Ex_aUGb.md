# Example 1 — `aUGb`

| aspect | `aUGb` |
|---|---|
| Language (informal) | "a finitely until always b" |
| ω-regular | `a*·b^ω` |
| LTL | `a U G !a` |
| LTL | **yes** — stutter insensitive |
| Geometry | obligation, properly level 2: a Boolean combination of safety and guarantee, no single one suffices |
| Recognizer | weak deterministic — one automaton serves as both DBA and DCA |
| Det. Emerson–Lei `D` | ![aUGb automaton](../sos_figs/img/aUGb.png) |
| Invariant `𝓘` | ![aUGb invariant](../sos_core_figs/img/core_F0_astar_bomega_b_pairs.png) |

`[a]` is the class of finite words `a⁺` only containing `a`. `[a·b]` is words of
the form `a⁺b⁺` that start with a sequence of `a`'s then a sequence of `b`'s.
`[b]` is the class `b⁺` of words only containing `b`. `[b·a]` the class of words
that have met an `a` after `b` (somewhere in the word).

Acceptance is in two pairs: `([b], [b])` representing the word `b^ω`, and
`([a·b], [b])` the words of the form `a⁺·b^ω`. Note that these are classes:
`([a·b], [b])` represents `a·b^ω`, `ab·b^ω`, `aabbb·b^ω`, `ab·bbb^ω`, …

The LTL row is a read-off of the drawing: every power sequence
settles with period 1 — `[a]`, `[b]`, `[b·a]` are idempotent, and `[a·b]`
falls onto the idempotent `[b·a]` in one step — so the invariant is
aperiodic: LTL.

Reading a lasso (Definition 3.5). Take `ababba·b^ω`. The loop first:
`𝒮(b) = [b]` is already idempotent, so `e = [b]`. The stem:
`𝒮(ababba) = ([a]·[b])·([a]·[b])·([b]·[a]) = [a·b]·[a·b]·[b·a]` (an arbitrary
parenthesizing, since `𝒮` is associative); `[a·b]·[a·b] = [b·a]`, and `[b·a]`
right-extended by anything is still `[b·a]`, so `𝒮(ababba) = [b·a]`. The
queried stem is `s = 𝒮(u)·e = [b·a]·[b]`, and absorption simplifies it away:
`s = [b·a]`. The name `([b·a], [b])` is not in `P`, so the lasso `ababba·b^ω`
is not in the language.

**Construction (§4).** The table §4 builds from this page's `D`: the enriched
monoid, `|EM¹| = 7` elements folding onto `|S(L)₊¹| = 5` — the four classes
above plus `[ε]`. The excess the quotient removes is two mark-only splits:
`⟨b⟩ ≠ ⟨bb⟩` (ids 1, 3) and `⟨ab⟩ ≠ ⟨abb⟩` (ids 5, 6) differ solely in a
mark collected along the way — membership in `aUGb` never counts `b`'s — and
each pair folds to one class.

| id | word | st | mk | rmul | → class |
|---|---|---|---|---|---|
| 0 | `eps` | [0 1 2] | [{} {} {}] | 1 2 | 0 `eps` |
| 1 | `b` | [0 0 2] | [{0} {} {}] | 3 4 | 1 `b` |
| 2 | `a` | [2 1 2] | [{0} {} {}] | 5 2 | 2 `a` |
| 3 | `b;b` | [0 0 2] | [{0} {0} {}] | 3 4 | 1 `b` |
| 4 | `b;a` | [2 2 2] | [{0} {0} {}] | 4 4 | 3 `b;a` |
| 5 | `a;b` | [2 0 2] | [{0} {} {}] | 6 4 | 4 `a;b` |
| 6 | `a;b;b` | [2 0 2] | [{0} {0} {}] | 6 4 | 4 `a;b` |

Reading note: the tool takes the Büchi condition state-based, so the mark
rides *every* edge leaving the accepting state — including the dead edge into
the sink, which is why `mk_{⟨a⟩}` shows `{0}` at slot `0`; the drawing above
paints the transition-based form, the mark on the `b`-loop only. The algebra
is indifferent — a mark on a dead edge recurs on no run — and the invariant
is byte-identical either way.
