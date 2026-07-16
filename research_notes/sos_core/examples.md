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
`D`: every element of the enriched monoid `EM(D)` (Definition 4.2) — its
state map `st` and collected marks `mk`, one slot per state of the drawing;
its right multiplications by `b` then by `a` (`rmul`, as element ids) — and,
in the last column, the class it folds onto in the quotient of §4.3. The
tables are the construction tool's reports under a single mechanical rename,
the paper's `b` for the tool's literal `!a` (the single-atom alphabet the
formulas live over; only the serialized `.sos` of §6.1 keeps the raw
letters). Everything else is verbatim, the tool's monoid convention
included: counts are `|EM¹|` folding onto `|S(L)₊¹| = |𝒞| + 1`, identity
included and printed `eps`; keys read `x;y` for the paper's `x·y`; ids
enumerate in the tool's letter order, `b` before `a`.

- Ex. 1 — [`aUGb`](Ex_aUGb.md)
- Ex. 2 — [`GF(aa)`](Ex_GFaa.md)
- Ex. 3 — [`Even`](Ex_Even.md)
- Ex. 4 — [`EvenBlocks`](Ex_EvenBlocks.md)
