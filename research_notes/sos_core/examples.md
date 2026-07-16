# Worked examples

The paper's four running languages, numbered Ex. 1–4 and cited that way from
the prose, each presented on its own page along the same axes: an
**informal** description, its **ω-regular** word over the two
letters `{a, b}`, its **formula** (LTL, or PSL/SERE where mod-2 counting takes it
out of LTL), a **classification** — two facts read off `𝓘` and stated without
justification: LTL-definability (§6.2) and the Wagner degree (§8) — its
deterministic **Emerson–Lei automaton** `D` (the input of §4),
and its syntactic **invariant** `𝓘` (§3). The pages are transverse to the
paper — self-contained, meant to be read at leisure. The formulas live over the single atom
`a`, so the second letter is the literal `!a`; **throughout this paper the
LTL/PSL forms are read with `b` in place of `!a`.**

**Reading key.** `D` is drawn deterministic, complete, transition-based: each
edge carries a letter — `a`, `b`, or `a,b` for the both-letters (true) edge —
and the coloured bullets on an edge are its acceptance marks, the condition
`Acc` named in the header. `𝓘` is the stamp core of §3.1: vertices are the
congruence classes, edges are the letter-action table, and the letter map `λ`
and the saturated set of accepting linked pairs `P` are listed beneath; the
label `𝒞` abbreviates a self-loop carrying every class.

- Ex. 1 — [`aUGb`](Ex_aUGb.md)
- Ex. 2 — [`GF(aa)`](Ex_GFaa.md)
- Ex. 3 — [`Even`](Ex_Even.md)
- Ex. 4 — [`EvenBlocks`](Ex_EvenBlocks.md)
