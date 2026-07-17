# Worked examples

The paper's four running languages, numbered Ex. 1–4 and cited that way from
the prose, each presented on its own page along the same axes: an
**informal** description, its **ω-regular** word over the two
letters `{a, b}`, its **formula** (LTL, or PSL/SERE where mod-2 counting takes it
out of LTL), a **classification** block, its deterministic **Emerson–Lei
automaton** `D` (the input of §4), and its syntactic **invariant** `𝓘` (§3).

**The classification block.** Three verdicts head each page — facts about a
language that are usually hard to come by, here tool-computed from the page's
invariant; the procedures are out of scope of this paper. *LTL*:
definability in linear temporal logic, with its stutter sensitivity.
*Geometry*: the
rung on the safety–progress ladder of Manna and Pnueli [MP92] — safety,
guarantee, obligation, recurrence, persistence, reactivity — the coarse view
of Wagner's hierarchy [Wag79]; `properly` marks an exact position.
*Recognizer*: the weakest deterministic acceptance recognizing the language,
tied to the geometry by Landweber's theorem [Lan69] — DBA / DCA abbreviate
deterministic Büchi / co-Büchi automata, accepting when marked transitions
recur / eventually cease. Each page is self-contained. The formulas live over the single atom
`a`, so the second letter is the literal `!a`; **throughout this paper the
LTL/PSL forms are read with `b` in place of `!a`.**

**Reading key.** `D` is drawn deterministic, complete, transition-based: each
edge carries a letter — `a`, `b`, or `a,b` for the both-letters (true) edge —
and the coloured bullets on an edge are its acceptance marks, the condition
`Acc` named in the header. `𝓘` is the stamp core of §3.1: vertices are the
congruence classes, edges are the letter-action table, and the letter map `λ`
and the saturated set of accepting linked pairs `P` are listed beneath; the
label `𝒞` abbreviates a self-loop carrying every class.

**The construction table.** Each page closes on the table §4 builds from its
`D`: one row per class of the automaton congruence `≈_D`
(Definition 4.2), written `⟨w⟩` for the class of its shortlex-least word `w`.
The `at q` columns hold
`(δ(q, w), mk(q, w))` — where reading `w` from state `q` lands, and
the marks collected on the way: the two maps that determine the class, so
the row *is* the class. The `·⟨b⟩`,
`·⟨a⟩` columns name the class reached by extending on the right by one
letter — the step the construction iterates, and the table is closed: every
entry names a row. The last column is the image of the row's class in the
quotient of §4.3 — its class in `𝒞`.

- Ex. 1 — [`aUGb`](Ex_aUGb.md)
- Ex. 2 — [`GFaa`](Ex_GFaa.md)
- Ex. 3 — [`Even`](Ex_Even.md)
- Ex. 4 — [`EvenBlocks`](Ex_EvenBlocks.md)
