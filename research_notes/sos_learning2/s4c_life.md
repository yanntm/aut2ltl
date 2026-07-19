### 4.3 Alignment, assembled

One procedure, **stabilize**, drives the table to a certified fixpoint —
it is where every membership bit lands, concordant bits as recorded
entries, discordant ones as splits — and **align** is a chain split
followed by stabilization:

```
    stabilize:                        # membership queries only
        loop:
            fill entries; promote (closure) and mint (consistency)
                to fixpoint                          (Definition 3.2)
            stamp check — zero queries; on violation:
                escalate (Lemma 4.3): split, continue
            fill P on the linked pairs of the induced product
                (memoized queries)
            pair check — zero queries; on violation:
                escalate (Lemma 4.4): split, continue
            return 𝓘 := canonicalize ⟨𝒮_T, P⟩       ([SωS26, Thm II])

    align(w·z^ω):                     # teacher's bit ≠ belief's answer
        chain split (Theorem 4.2)
        return stabilize
```

The two levels of discordance are visible in stabilize. Table-level
discordances — a frontier word matching no row, a consistency
violation — split directly, by promotion and mint (Definition 3.2), no
chain needed. Lasso-level discordances — the legality violations — are
chained down to table level by the escalations of §4.2. Checks are free;
escalations are bounded by the total number of splits. What stabilize
returns is the next belief: a well-formed invariant, the syntactic
invariant of its own belief language (§3.2), reached from one seed
discordance by membership queries alone.

*Example (the `EvenBlocks` run: one align call).* The whole run is
bootstrap, one align call, and a certifying equivalence query. The call
is seeded by the teacher-found discordance traced in §4.1 — the lasso
`(ε, b·aa)` — and its stabilization fires two stamp escalations,
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
(b) By induction over the run. The initial column is the ω-column `(ε, ε)`,
and every mint inherits the sort of the column it derives from: consistency
mints by Definition 3.2, both branches of a stamp escalation by Lemma 4.3
(branch 1 reproduces `κ` in `κ`'s own sort; branch 2 is the chain run in
`κ`'s own context, minting `κ`'s sort — the segment migrating into the
middle component). The remaining source of columns is the processing of a
discordant lasso (Theorem 4.2 — teacher-found, or the pair escalation's
self-found, Lemma 4.4: the same chains) — and on a prefix-independent
language every stem chain is *flat*: its bits belong to words differing
only in their finite prefixes, so every flip lands in the loop chain,
whose mint is an ω-column (Lemma 4.1). ∎

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

**Bootstrap.** The learner opens on an assumption chosen to be minimal
and legal at once: *no lasso is accepted* — the empty language, whose
invariant is the smallest there is (`N = 2`: one absorbing class, the
adjoined identity, an empty pair set). It is an opening belief, not an
axiom: about `L` it assumes nothing that an accepted lasso cannot
refute. Day one replaces it with knowledge scoped by letters: rows
`R = {ε} ∪ Σ`, the single ω-column `(ε, ε)` — the weakest question a
context can ask, "is your own ω-power in `L`?" — and one call to
stabilize. Everything day one does is already the interior machinery:
fills, promotions, mints — and, when a day-one table is born illegal,
escalations: on `a → Xa`, bootstrap alone fires a stamp escalation and
delivers the five-class target before the first equivalence query. On
the running examples the day-one tables are legal as they
stand (Tables 1–2), and the exported beliefs are Figure 3's frames.

**Alternation.** The whole learner is now three lines around align:

```
    learner:
        R ← {ε} ∪ Σ;   E_ω ← {(ε, ε)};   E_lin ← ∅
        𝓘_0 ← stabilize                            # bootstrap
        repeat:
            pose EQ(𝓘_i)
            if assent:  output 𝓘_i and stop
            else:       𝓘_{i+1} ← align(counterexample)
```

An equivalence query is the **delegated discordance search** — "is there
a lasso I would get wrong?" — and it is posed exactly at quiescence:
belief legal, hence internally coherent, both self-served sources
exhausted — no computation of the learner's own points at any lasso as
suspect. A failed query contributes precisely one discordant lasso and
nothing else; even its bit is redundant, the flip of the belief's
prediction. There is no counterexample-processing phase distinct from
alignment — the teacher's lasso enters align exactly as a pair
escalation's self-found one does. And assent is not a learning event at
all: it is *global* concordance, agreement on every lasso — a
certificate no finite set of membership bits can supply — and the exit.
The alternation is thus extreme by design: membership queries as much as
needed, equivalence queries only when the learner cannot help itself.

The belief sequence `𝓘_0, 𝓘_1, …` is the run's *frame sequence*, each
frame an ω-regular language, opening at Figure 3 and closing at
Figure 2; successive frames differ by exactly one align call.
