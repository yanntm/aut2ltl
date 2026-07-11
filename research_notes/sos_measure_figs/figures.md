# Measure, Distance, and Entropy on the Syntactic ω-Semigroup — Figures

Companion artifact for [`sos_measure.md`](../sos_measure.md), built to the spec
in [`sos_measure_figures.md`](../sos_measure_figures.md). Every number, node,
edge, tag and probability shown is produced by the probe named in each figure's
provenance footer; nothing is transcribed by hand. See
[`reproduction.md`](reproduction.md) to regenerate and [`notes.md`](notes.md)
for the measured facts and drawing decisions the figures rest on.

Inputs are language-canonical `.sos` invariants, bundled in
[`sources/`](sources/): `fe.sos` (the five-class algebra of "`b` occurs and the
first `b` is at an even position", paper §4.1) and `fd.sos` (the nine-class
algebra of "some `a` at infinitely many even positions", paper §3.4). Neither
language is aperiodic, so neither comes from an LTL formula; both are coded from
the paper's own algebra and put through the shared `canonicalize` normal form,
so each `.sos` is language-canonical (`sources.py`, which also replays every
measure the paper states).

Drawing conventions, shared by the figures:

| ink | meaning |
|---|---|
| solid blue arrow | a right-Cayley step under the letter `a` |
| dashed amber arrow | a right-Cayley step under `!a` (the paper's `b`) |
| solid black arrow | a step both letters agree on (one merged arrow) |
| rounded grey box | one SCC of the right-Cayley graph |
| double circle | a class in a **bottom** SCC |
| thick dark border | a class in the **kernel** |
| green / red badge | the bottom SCC's verdict `θ = 1` / `θ = 0` |
| annotation `x = …` | the class's exact measure at `p` (`value_vector`) |

Class nodes are labelled by their canonical shortlex key (`[ε]`, `[¬a]`,
`[a·a]`, …) with the class id beneath; the paper's mnemonic names map on as the
captions note.

---

## FIG-1 — the worked read-off, end to end (paper §4.1, Example)

![the read-off of F-E, end to end](img/fig1_readoff.png)

**The whole §4.1 algorithm in one picture, on `fe.sos`.** The five classes are
`[ε]`; the `b`-free pair `A₁ = [a]` (odd length) and `A₀ = [a·a]` (even length),
which exchange under `a` and exit under `b` — the one transient SCC, boxed; and
the two absorbing sinks `F₀ = [¬a]` ("first `b` at an even position") and
`F₁ = [a·¬a]` ("first `b` at an odd position"), each its own bottom SCC, double
-circled with a self-loop on both letters. The **kernel spans both bottom SCCs**
— its two `R`-classes — so `F₀` and `F₁` both carry the thick border, the
caption's point: one global idempotent `k = F₀` serves both components, each
`θ`-lookup staying inside its own closed `R`-class. The badges read
`θ_{F₀} = 1`, `θ_{F₁} = 0`. Under each node its exact `x`-value at uniform `p`
— `2/3` (`[ε]`), `1/3` (`A₁`), `2/3` (`A₀`), `1` (`F₀`), `0` (`F₁`) — solving
the transient system `x_{A₁} = p_a x_{A₀}`, `x_{A₀} = p_a x_{A₁} + p_b`; the
result line is `μ_p(L) = x_{[ε]} = 2/3`, matching the paper's
`p_b / (1 − p_a²)`.

<!-- from: cd sosl && python3 -m tests.quant.figs.fig1 research_notes/sos_measure_figs/sources/fe.sos research_notes/sos_measure_figs/sources/fig1_readoff.tex -->

---

## FIG-2 — the doubled-word cut (paper §3.1, Lemma 3.1)

![the doubled-word cut on one sampled word](img/fig2_cut.png)

**Lemma 3.1's mechanism on one concrete random word over `fd.sos`.** The kernel
idempotent is `k = fold(aa)` and `H(k) ≅ ℤ/2`, so every fold in the maximal
group renders as a parity `r̄ ∈ {0, 1}` (`k` the even one). The probe samples a
uniform length-56 word (seed in the reproduction guide), highlights the disjoint
occurrences of the doubled word `w·w = aaaa`, and cuts at their midpoints
(vertical bars). Each inter-cut block reads `w·x·w`, so its fold lands in `H(k)`;
its parity `r̄` is printed beneath. The cumulative product is a running XOR; its
value at each cut is shown, and the cuts where it equals the recurring value
`g = 0` are **circled — those are the `J`-cuts**. Between consecutive `J`-cuts
the block folds to `k` exactly (the brackets, each tagged `fold = k`), including
the middle bracket that spans the one **excursion** — two `r̄ = 1` blocks about
a non-`J` cut whose product returns to `k`. Left of the first cut the stem folds
into `Stems(c, k)`. A reader who follows the ruler has re-run the proof: almost
every word factors over the kernel idempotent.

<!-- from: cd sosl && python3 -m tests.quant.figs.fig2 research_notes/sos_measure_figs/sources/fd.sos research_notes/sos_measure_figs/sources/fig2_cut.tex -->

---

## FIG-3 — the kernel group and the phase contrast (paper §3.4, Example)

![the kernel group and the phase contrast](img/fig3_kernel.png)

**Why only the kernel forgets phases — `fd.sos`'s two halves side by side.**
Left: the right-Cayley graph of the nine classes `(r, E)` plus `[ε]`, its four
SCCs boxed; the unique bottom SCC `K = {[a·a], [¬a·a·a]} = {fold(aa),
fold(baa)}` is double-circled and thick-bordered, tagged `K ≅ ℤ/2` and
`θ_K = 1` — so `μ_p(L) = 1` for every full-support `p`. Right: the phase
contrast, every verdict computed by `Val`. The non-kernel idempotent
`e' = fold(ba)` **splits** the `R`-equivalent stems `fold(b)` and `fold(bb)` —
`Val(fold(b), e') = 1` (`b·(ba)^ω ∈ L`) against `Val(fold(bb), e') = 0`
(`bb·(ba)^ω ∉ L`) — so `Val(·, e')` is not an `R`-class function and no
generic-verdict statement can hold there. The kernel loop `k = fold(aa)`
**merges** them — `Val(fold(b), k) = Val(fold(bb), k) = 1` — because the
re-bracketing `u·(aa)^ω = (u·a)·(aa)^ω` forgets the phase, exactly as Lemma 3.2
forces. This is the negative control M2 asserts: the engine must read `θ` only
at a kernel idempotent.

<!-- from: cd sosl && python3 -m tests.quant.figs.fig3 research_notes/sos_measure_figs/sources/fd.sos research_notes/sos_measure_figs/sources/fig3_kernel.tex -->

---

## Blocked figures

FIG-4 (the null-class tower `L → sh(L) → ess(L)`) and FIG-5 (the census data
figures) are specified in [`sos_measure_figures.md`](../sos_measure_figures.md)
but not built here: FIG-4 needs the M3 `shadow`/`essential` fixtures green,
FIG-5 needs the M4/M6 census CSVs. The M3 engine has since landed in
`sosl/sosl/quant/` (`shadow`, `essential`, `distance`), so FIG-4 is likely now
unblocked pending its F-G/F-H fixtures.
