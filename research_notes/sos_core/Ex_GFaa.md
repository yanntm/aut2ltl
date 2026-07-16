# Example 2 — `GF(aa)`

| aspect | `GF(aa)` |
|---|---|
| Language (informal) | "infinitely many aa : an a followed by an a." |
| ω-regular | `((a\|b)*·a·a)^ω` |
| LTL | `G F(a ∧ X a)` |
| LTL | **yes** — stutter sensitive |
| Geometry | recurrence, properly `Gδ`: strictly above every obligation |
| Recognizer | DBA-proper — deterministic Büchi suffices, no deterministic co-Büchi can |
| Det. Emerson–Lei `D` | ![GF(aa) run-parity automaton](../sos_figs/img/gf_aa.png) |
| Invariant `𝓘` | ![GF(aa) invariant](../sos_core_figs/img/core_F1_gf_aa_pairs.png) |

`[a]` is the class of words that start with an `a`, have never seen two `a`'s
in a row, and most recently read an `a`. `[a·b]` is the class of words that
start with an `a`, most recently read a `b`, and so far contain only isolated
`a`'s — no block of two. The last letter is what separates them: an `a` may
pair with the next letter, a `b` cannot. These two classes cycle: extending
`[a·b]` by `[a]` returns to `[a]` (`[a·b]·[a] = [a]`, forgetting that `b`'s
were ever seen), and `[a]·[b] = [a·b]` goes back. The cycle is *not* a
counter: the trip around it multiplies by `[b]` then by `[a]`, two different
classes, and no single class powers around it — `[a·b]·[a·b] = [a·b]`, while
`[a]·[a] = [a·a]` leaves. Every power sequence settles with period 1 (though
only at exponent 2: `[a]` needs one step to stabilize), so the invariant is
aperiodic — the LTL row's verdict, read off the drawing.

`[a·a]` is the class of all words that contain at least one block of two
consecutive `a`'s. It is a sink: once two `a`'s in a row have been seen the
stamp classifier is content, and any further extension is absorbed and stays
in `[a·a]`. In the drawing it is entered by reading one more `a` from the two
classes that end on an unpaired `a`: `[a]`, and `[b·a]` on the `b`-side.

Since acceptance asks for infinitely many such blocks, the only accepted pair
is `([a·a], [a·a])`, and it is only logical that `[a·a]` be the loop
component. Less obvious is that the stem component must also be `[a·a]`: this
is always arrangeable by the rotation lemma, which pushes letters of the
looped part back into the prefix until the prefix, too, is seen to carry two
consecutive `a`'s. That is the canonical presentation of all accepted lassos
of the language here.

The classes `[b]` and `[b·a]` play the same waiting-room game for words that
start with a `b` — `[b]` on a last-read `b`, `[b·a]` on an unpaired `a` —
until the first block of two `a`'s is met.

Reading a lasso (Definition 3.5). Take `(aab)^ω`, the empty-stem presentation
`(ε, aab)`. The loop first: `𝒮(aab) = [a]·[a]·[b] = [a·a]·[b] = [a·a]` — the
sink absorbs — already idempotent, so `e = [a·a]`. The stem is empty, and
absorption lands the query in `𝒞` anyway: `s = 𝒮(ε)·e = [ε]·[a·a] = [a·a]`.
The name `([a·a], [a·a])` is in `P`: accepted — an `aa` closes in every turn
of the loop. Against it, `(ab)^ω`: the loop `𝒮(ab) = [a·b]` is idempotent,
`s = [ε]·[a·b] = [a·b]`, and `([a·b], [a·b])` is not in `P`: rejected — the
`a`'s stay isolated forever.

**Construction (§4).** `|EM¹| = 10` elements folding onto `|S(L)₊¹| = 6` —
the five classes above plus `[ε]`. The enrichment at work: `⟨a⟩` (id 2) and
`⟨aaa⟩` (id 8) have the *same* state part — the transposition — and differ
only in marks, the longer word having closed an `aa`; the transition monoid
identifies them, the enrichment keeps them apart. The fold then does the
reverse service: four "contains `aa`" behaviors (ids 5, 6, 8, 9), distinct
as vectors, collapse onto the sink `[a·a]`, and `⟨aba⟩` (id 7) rejoins
`[a]` — the `Z₂` visible in the `st` column is pure presentation, and §4.4
is where it dies.

| id | word | st | mk | rmul | → class |
|---|---|---|---|---|---|
| 0 | `eps` | [0 1] | [{} {}] | 1 2 | 0 `eps` |
| 1 | `b` | [0 0] | [{} {}] | 1 3 | 1 `b` |
| 2 | `a` | [1 0] | [{} {0}] | 4 5 | 2 `a` |
| 3 | `b;a` | [1 1] | [{} {}] | 1 6 | 3 `b;a` |
| 4 | `a;b` | [0 0] | [{} {0}] | 4 7 | 4 `a;b` |
| 5 | `a;a` | [0 1] | [{0} {0}] | 6 8 | 5 `a;a` |
| 6 | `b;a;a` | [0 0] | [{0} {0}] | 6 9 | 5 `a;a` |
| 7 | `a;b;a` | [1 1] | [{} {0}] | 4 6 | 2 `a` |
| 8 | `a;a;a` | [1 0] | [{0} {0}] | 6 5 | 5 `a;a` |
| 9 | `b;a;a;a` | [1 1] | [{0} {0}] | 6 6 | 5 `a;a` |
