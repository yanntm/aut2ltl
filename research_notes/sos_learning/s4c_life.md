### 4.3 Alignment, assembled

The learner's ground truth is its **evidence** `E`: the finite set of
teacher bits witnessed so far, one per queried lasso, however the query
arose — a fill, a probe, a chain step, a `P`-slot, a counterexample.
Everything else is derived: the table arranges the evidence for
comparison, the classes partition it, the belief completes it into a
language. The **normal form** asks four things of the derived state,
each checkable without a query:

- **closed and consistent** — the table presents a classifier
  (Definition 3.2);
- **morphism** — the induced product is well defined (Lemma 3.4);
- **saturated** — the pair set gives one lasso one verdict through all
  its presentations (§3.2);
- **evidence-coherent** — the exported belief contradicts no bit of
  `E`: every prediction replayed against the cache.

**Repair** resolves the first failure in pinned order. Bits the table
or the pair set demand and the evidence does not yet hold are fetched —
the confirm motion: evidence grows, nothing moves. A closedness failure
promotes; a consistency failure mints (Definition 3.2). A morphism
failure escalates (Lemma 4.3); a saturation failure escalates
(Lemma 4.4); an evidence failure is a discordant lasso whose teacher
bit is already in hand — no query at all, the chain directly
(Theorem 4.2). Every resolution splits at least one class, witnessed by
an Arnold context.

**Align is the fixpoint**: seed the evidence with one discordant lasso,
repair until the normal form holds. The fixpoint exists and is reached:
evidence only grows, the partition only refines — every split is
`≈_L`-witnessed, so distinct classes stay `≈_L`-distinct — and
refinement is bounded by `N` across the entire run, not per call: at
most `N` resolutions ever, anywhere. At the fixpoint the export,
canonicalized ([SωS26, Thm II]), is a well-formed invariant — the
syntactic invariant of its own belief language (§3.2). That is the
paper's thesis in one statement:

> **At every fixpoint the belief is an ω-regular language, held in
> canonical form, contradicting no bit of evidence — a potentially
> correct worldview, built and rebuilt from membership queries alone.**

Only new evidence can move a fixpoint belief: a bit the learner elects
to fetch (a probe), or one the teacher is asked to find (§4.5).

*Example (the `EvenBlocks` run: one align call).* The whole run is
bootstrap, one align call, and a certifying equivalence query. The call
is seeded by the teacher-found discordance traced in §4.1 — the lasso
`(ε, b·aa)` — and its repair fires two stamp escalations,
carrying the table from four to its eight classes — keys
`ε, b, a, b·a, a·b, a·a, b·a·b, a·b·a`, the count and keys fixed by the
reference invariant. Table 7 is the call as a split ledger, one row per
event, from the implementation's transcript — deterministic under the
pinned scan and minimal-counterexample policies, and reproducing §4.1's
row exactly. One reading note: a single mint can split more than one
class once the table re-stabilizes — rows 2 and 3 each split two.

| # | trigger | chain | minted column | splits | `\|𝒞_T\|` after |
|:--:|---|---|---|---|:--:|
| 1 | EQ: `(ε, b·aa)` | loop | `(a, a)_ω` | `b·a` out of `⟨a⟩` | 4 |
| 2 | stamp escalation | in-context | `(a, b·a)_ω` | `aa` out of `⟨a⟩`; `a·b` out of `⟨b·a⟩` | 6 |
| 3 | stamp escalation | in-context | `(ε, b)_ω` | `a·b·a` out of `⟨b⟩`; `b·a·b` out of `⟨aa⟩` | 8 |

**Table 7.** The `EvenBlocks` align call as a split ledger: trigger (the
teacher-found seed, then legality escalations), the chain that processed
it, the minted column, the words separated. The day-one checks are
clean — Figure 3(b) is a legal frame — so row 1, §4.1's split, is the
call's first event; rows 2–3 are the stamp check enforcing
two-sidedness: no second discordance is ever teacher-found, and the
run's second equivalence query certifies. Every one of the four columns
is of the ω-sort: prefix-independence in action (the linear shape is
blind, Proposition 4.5, so every separation lives in the loop). The
final escalation mints `(ε, b)` — the very column §3.1 exhibited by
inspection. The resulting bit-signatures are the fixpoint (the Table 6
analogue), pairwise distinct — with `[ε]`, the `N = 8` classes of
`𝓘(EvenBlocks)`:

| word | `(ε,ε)_ω` | `(a,a)_ω` | `(a,b·a)_ω` | `(ε,b)_ω` |
|---|:--:|:--:|:--:|:--:|
| `b` | `1` | `0` | `0` | `1` |
| `a` | `0` | `0` | `1` | `0` |
| `b·a` | `0` | `1` | `0` | `0` |
| `a·b` | `0` | `1` | `1` | `0` |
| `a·a` | `0` | `0` | `0` | `1` |
| `b·a·b` | `0` | `0` | `0` | `0` |
| `a·b·a` | `1` | `0` | `0` | `0` |

### 4.4 What alignment mints: prefix-independence and the two shapes

The left contexts the escalations enforce come in Arnold's two shapes,
and prefix-independence silences exactly one of them:

**Proposition 4.5 (prefix-independence and the two shapes).** Let `L` be
prefix-independent (`w ∈ L ⟺ σ·w ∈ L` for every finite `σ`). Then the
prefix slot `x` of every Arnold context is vacuous —
`x·u·y·t^ω ∈ L ⟺ u·y·t^ω ∈ L` and `x·(u·y)^ω ∈ L ⟺ (u·y)^ω ∈ L` — so the
*linear* shape degenerates to pure right extensions: a linear context
separates `u` from `v` iff one with `x = ε` does. The *ω-power* shape does
not degenerate: in `(u·y)^ω` every occurrence of `u` after the first is
preceded by `y`, so the context acts on `u` from the left through the
wrap-around — a left action that is a rotation of the loop, not a deletable
prefix.

*Proof.* The vacuity of `x` is prefix-independence applied to the finite
prefix `x`. For the wrap-around: `(u·y)^ω = u·(y·u)^ω`, so by
prefix-independence `(u·y)^ω ∈ L ⟺ (y·u)^ω ∈ L` — the membership constraint
on `u` under the ω-context `(_·y)^ω` is exactly its behavior under the left
factor `y`, read as a rotation (§2.2), which deleting finite prefixes never
touches. ∎

**Corollary 4.6 (a prefix-independent gap is ω-sorted).** Let `L` be
prefix-independent. (a) `u ≈_L v` iff `u` and `v` agree under every pure
right extension (`u·y·t^ω ∈ L ⟺ v·y·t^ω ∈ L` for all `y ∈ Σ*, t ∈ Σ⁺` —
that is, `u ~_L v`, the right congruence) *and* under every bare ω-power
(`(u·y)^ω ∈ L ⟺ (v·y)^ω ∈ L` for all `y ∈ Σ*`). Consequently two words the
right congruence identifies but `≈_L` separates are separated by ω-power
contexts *only*. (b) On the learner's side the sort discipline is absolute:
every column of every run on `L` is of the ω-sort.

*Proof.* (a) By Proposition 4.5 the prefix `x` is vacuous in both shapes.
The linear shape's remaining contexts `y·t^ω` range over the lassos of the
residual languages, which are ω-regular and hence determined by them
[PP04] — agreement under all of them is exactly `u ~_L v` — and the ω-power
shape's remaining contexts are the bare ω-powers. If `u ~_L v` and
`u ≉_L v`, the separating Arnold context is therefore of the ω-power shape.
(b) By induction over the run's mints — under the bootstrap of §4.5 no
column is given: every column is minted. A consistency mint preserves its
source column's sort (Definition 3.2); a stamp escalation preserves `κ`'s
sort in both branches (branch 1 reproduces `κ` in `κ`'s own sort; branch 2
is the chain run in `κ`'s own context, the segment migrating into the
middle component). Every remaining mint comes from processing a discordant
lasso (Theorem 4.2 — a bootstrap probe's, the teacher's, or the pair
escalation's, Lemma 4.4: the same chains), and on a prefix-independent
language every stem chain is *flat*: its bits belong to words differing
only in their finite prefixes, so every flip lands in the loop chain,
whose mint is an ω-column (Lemma 4.1). The run's first column is therefore
already ω-sorted, and no later mint can introduce the linear sort. ∎

Table 7's run is the corollary performed — four columns, all ω.

Prefix-independence also has a floor, which bounds where such witnesses can
live at all:

**Lemma 4.7 (prefix-independence needs depth).** A prefix-independent
language that is topologically closed — a safety language — is `∅` or
`Σ^ω`; dually for open. A nontrivial prefix-independent language is
therefore neither closed nor open.

*Proof.* Let `L` be closed, prefix-independent, and nonempty, and pick
`w ∈ L`. Every `x ∈ Σ^ω` is the limit of the words `x[0..n]·w`, each in `L`
by prefix-independence; closedness puts the limit in `L`, so `L = Σ^ω`. An
open prefix-independent language has a closed prefix-independent
complement. ∎

### 4.5 The learner's life: bootstrap and alternation

**Bootstrap.** The learner opens with the least state the definitions
admit: `R = {ε}` and no columns at all. Repair runs on it as on any
state: closedness promotes the shortlex-least letter — no other row
exists to absorb it — and every remaining letter merges with it, no
column yet separating anything; the induced product is the one-class
semigroup, and the `P`-fill of its single linked pair poses the run's
first membership query, the ω-power of the promoted letter. That single bit decides the zeroth belief: the
empty language or `Σ^ω`, the two smallest invariants there are
(`N = 2`). Nothing is ever assumed — the opening belief is the answer
to the opening query.

A one-class belief coheres with its one bit of evidence — nothing
self-served remains — so the learner probes: each remaining letter's
ω-power, queried in
shortlex order and treated by the general rule — concordant, recorded;
discordant, one align call seeded by `(ε, a)`. **Day one** is the
belief at the fixpoint of this sweep: every contradiction among the
opening bits resolved by membership queries alone, no equivalence query
anywhere. The letter sweep is the minimal self-served probe policy —
the only experiments available before anything is known — and it is the
last a-priori experimentation the learner ever performs: every column
of every run is *minted* by a discordance; no experiment is given, all
are found.

**Alternation.** The whole learner is now a few lines around align:

```
    learner:
        R ← {ε};   E_lin ← ∅;   E_ω ← ∅
        𝓘 ← repair                   # the first query decides ∅ vs Σ^ω
        for each remaining letter a, in shortlex order:    # probe sweep
            query a^ω; on discordance:  𝓘 ← align((ε, a))
        repeat:                                            # alternation
            pose EQ(𝓘)
            if assent:  output 𝓘 and stop
            else:       𝓘 ← align(counterexample)
```

An equivalence query is the **delegated discordance search** — "is there
a lasso I would get wrong?" — and it is posed exactly at quiescence:
the belief in normal form, every self-served finder exhausted —
evidence reread, legality checked, letters probed — no computation of
the learner's own points at any lasso as suspect. Answering it is a
comparison of two languages at invariant level (§2.3), and its return
is a witness: one lasso in one language and not the other. A failed query contributes precisely one discordant lasso and
nothing else; even its bit is redundant, the flip of the belief's
prediction. There is no counterexample-processing phase distinct from
alignment — the teacher's lasso enters align exactly as a pair
escalation's self-found one does. And assent is not a learning event at
all: it is *global* concordance, agreement on every lasso — a
certificate no finite set of membership bits can supply — and the exit.
The alternation is thus extreme by design: membership queries as much as
needed, equivalence queries only when the learner cannot help itself.

The belief sequence `𝓘_0, 𝓘_1, …` is the run's *frame sequence*, each
frame an ω-regular language, opening at the one-class frame the first
query decides and closing at Figure 2; successive frames differ by
exactly one align call.
