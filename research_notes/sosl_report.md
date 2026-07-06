# SoS Learner — Status Report

Where the `sosl/` implementation stands against the plan in
`research_notes/sos_learner_spec.md` (the normative document), the paper
`research_notes/sos_learning.md` (whose running examples are computed by hand),
and the `.sos` normal form of `research_notes/sos_format.md`. This report answers
the questions the spec raises; it describes the implementation as it is.

## Milestones (spec §8)

- **M1 — Teacher + validator.** Done.
- **M2 — Learner without saturation** (table; fill / close / consist; chains;
  export). Done.
- **M2.5 — Convention alignment** (fresh-identity reference builder; the
  learner's `[ε]` singleton rule; the `.sos` fixtures). Done.
- **M3 — Saturation + exact equivalence.** Next; not started.
- **M4 — Campaign.** Not started.

## Ground truth: reference builder vs the paper

`sosl.sos.build.reference_of_hoa` reads the canonical syntactic ω-semigroup
`S(L)₊¹` from each source automaton in `research_notes/sos_figs/sources/`. Class
counts match the paper's fingerprint tables:

| example | source HOA | paper `\|S(L)₊¹\|` | reference |
|---|---|:--:|:--:|
| GF(aa) | `gf_aa_parity.hoa` | 6 | 6 |
| Even | `even.hoa` | 5 | 5 |
| EvenBlocks | `evenblocks.hoa` | 8 | 8 |

The ground-truth leg reproduces the paper's hand-computed canonical objects.

## M2 learner status (no saturation)

The learner reaches the canonical object on every language in the census: the
exported `.sos` is byte-equal to the reference, and the Cayley hypothesis is
acceptance-correct on the exhaustive lasso check (`|stem|, |loop| ≤ 3`).

| language | classes | vs reference | acceptor | member / equiv / cex |
|---|:--:|---|---|:--:|
| GF a | 3 | byte-equal | correct | 6 / 1 / 0 |
| F a | 3 | byte-equal | correct | 6 / 1 / 0 |
| a U b | 4 | byte-equal | correct | 41 / 1 / 0 |
| GF(aa) | 6 | byte-equal | correct | 63 / 4 / 3 |
| Even | 5 | byte-equal | correct | 40 / 3 / 2 |
| EvenBlocks | 8 | byte-equal | correct | 80 / 4 / 3 |
| F(a ∧ Xa) | 6 | byte-equal | correct | 62 / 4 / 3 |

Every fixpoint the learner settles on before its first equivalence query is
broken by a counterexample and refined to the canonical congruence: on this
census no stall survives to the exported object. Saturation is nonetheless
mandatory for the general case (below).

## Identity convention

The class set is the classes of non-empty words **plus a fresh identity class
`[ε]`, always** — even when some non-empty word acts neutrally. The class count
is `(number of non-empty-word classes) + 1`, and comes out the same from every
automaton presenting the same language (a canonicity requirement of Theorem 5.1:
byte-equality must equal language equality, independent of presentation).

`[ε]` is a permanent singleton: never entered into a class comparison, nothing
ever merged into it. The reason is the prediction machinery. Predictions and the
P-cache answer through the representative lasso `key(s)·key(e)^ω`. Every
non-identity class is keyed by a non-empty word, so every representative lasso is
well-formed; if a non-empty word were merged into `[ε]`, a loop could fold to
`e = [ε]` and its representative lasso would have an empty loop — no such lasso
exists, and the P-cache would have nothing well-defined to query. The singleton
rule makes that failure structurally impossible.

- *Reference builder:* quotient only the elements reachable as images of
  non-empty words; adjoin the identity as a fresh element no word class can
  collide with; key every non-identity class by its shortlex-least non-empty
  word. A word whose enriched element equals `⟦ε⟧` (e.g. `!a` in a one-state
  `GF a` automaton) is an ordinary class keyed `!a`.
- *Learner:* `[ε]` is seeded as its own class before the bit-row grouping, and
  the grouping skips it (`sosl/learn/partition.py`).

A non-empty class **may** act as an identity on all the *other* non-empty
classes and still be its own class. `[aa]` in Even does: it is neutral on every
class but is distinct from `[ε]` (keyed `a;a`). Both `M(c, [ε]) = c` and
`M([ε], c) = c` hold for every `c`, including such a `c`; there is no reason to
merge or special-case it.

## Why saturation is mandatory (the M3 step)

`Invariant.member` reduces a lasso through the class multiplication table
`mult[c][d] = fold(c, rep[d])`, substituting a class representative in the middle
of a product. That substitution is sound only when the partition is a **two-sided
congruence** (`u ~ v` implies both `u·x ~ v·x` and `x·u ~ x·v`). Without
saturation the table guarantees only the right half, so a pre-saturation export
can be acceptance-wrong even where the hypothesis is correct — the hypothesis
folds the literal letters of the queried lasso and never substitutes a
representative, which is why the two read-offs of one partition can disagree.

Saturation (spec §4.3) is the left-context split that turns the right congruence
into the two-sided syntactic one, after which the exported invariant is
well-defined. The plan is as specced:

- The frozen-prefix chain is the stem chain with one extra parameter — a fixed
  prefix riding inside every queried context. Reuse the stem-chain code.
- Loop order (spec §3.2): fill / close / consist to fixpoint, then the saturation
  sweep, restart on any split, and pose an equivalence query only after a sweep
  comes back clean.
- Sweep checks are pure table computations (zero queries). Each escalation costs
  two membership queries plus at most one binary search and splits a class, so
  the total is bounded by the final class count — no termination risk.

Saturation is required by the correctness theorem even though the current census
shows no surviving stall: nothing guarantees every stall is transient, and when
saturation fires it is cheaper than an equivalence round (two membership queries
versus a full counterexample harvest).

## `F(a ∧ Xa)` and the permanence question

`F(a ∧ Xa)` reaches the canonical 6-class object at M2 under the default
equivalence mode (`[ε] [!a] [a] [!a;a] [a;!a] [a;a]`, byte-equal, export sound).
It is the language where the pre-saturation right-congruence-only stall is most
visible: the merge `a·!a → [ε]` is separated only by a context with a non-empty
*left* prefix (`a·(a!a)·(!a)^ω ∈ L` but `a·(!a)^ω ∉ L`) — precisely the witness a
right-congruence harvest cannot mint, and precisely what saturation adds.

Whether *any* language admits a **permanent** stall — a non-canonical fixpoint no
counterexample breaks — is decided per language by `--no-saturation --eq-mode
exact` (an M3 item; exact mode is not yet built). Exact mode is a decision
procedure: it either returns a counterexample (the stall is transient) or
certifies equivalence at a non-canonical fixpoint (the stall is permanent — a
headline exhibit for the paper's §4.2 open question). Both outcomes are wanted
results; this run is not to be tuned to "pass".

## Minimal stall specimens

An exhaustive learner census over the smallest 1-AP shapes (`tests/sosl/genaut_census.py`
over `genaut/corpus/`; nondeterministic inputs are determinized by the sos import
layer, so every automaton is covered) locates the smallest languages whose M2
fixpoint is non-canonical — a surviving stall under the default (bounded)
equivalence mode. Everything at one state is canonical; the stalls begin at two
states (`2state1ap0acc`). Two specimens, of different character, are reported
here. In both, the Cayley hypothesis is acceptance-correct (spec §9 P1 holds) and
the exported `.sos` is a class short of canonical (F2 fails).

### `a_once` — `L = { a·(¬a)^ω }` (LTL `a & X G !a`)

The single ω-word. Canonical form `D`:
[`sos_figs/sources/a_once.hoa`](sos_figs/sources/a_once.hoa); full algebra in
[`sos_figs/sources/a_once.md`](sos_figs/sources/a_once.md).

![a_once](sos_figs/img/a_once.png)

The reference invariant has **4 classes** (accepting pair `([a],[!a])`):

```
classes: 4        0 eps   1 !a   2 a   3 !a;a
mult   0: 0 1 2 3   1: 1 1 3 3   2: 2 2 3 3   3: 3 3 3 3     accept: 2 1
```

The learner stalls at 2 classes (`{ε}`, everything else), a single counterexample
refines it to **3**, and the bounded oracle then certifies. The exported `.sos`
merges the canonical `[!a;a]` into `[!a]`:

```
classes: 3        0 eps   1 !a   2 a
mult   0: 0 1 2   1: 1 1 1   2: 2 2 1                        accept: 2 1
```

The `a`-idempotent collapses onto `[!a]` (`a·a = [!a;a]` in the reference, `[!a]`
in the export), so the linked-pair read-off wrongly **accepts `a^ω`** (the
shortlex-least divergence: exported `True`, teacher `False`). The canonical
algebra keeps `[!a;a]` distinct; the context that separates `!a` from `!a;a`
needs a non-empty *left* prefix.

### `a_implies_xa` — `L = { w : w[0]=a ⇒ w[1]=a }` (LTL `a → X a`)

Canonical form `D`:
[`sos_figs/sources/a_implies_xa.hoa`](sos_figs/sources/a_implies_xa.hoa); full
algebra in [`sos_figs/sources/a_implies_xa.md`](sos_figs/sources/a_implies_xa.md).

![a_implies_xa](sos_figs/img/a_implies_xa.png)

The reference has **5 classes** (six accepting pairs). The learner stalls at
**4** and — the sharp point — with **zero counterexamples**: the first
closed/consistent fixpoint is already what the equivalence oracle certifies. The
export merges the canonical `[a;a]` into `[!a]` (both accepting idempotents in the
reference), so it wrongly **rejects `a^ω`** (exported `False`, teacher `True`).

### The shared moral

Both languages are LTL-definable (aperiodic) and minimal. In each, the M2
right-congruence merges the `a`-idempotent class into `[!a]`, and the class the
canonical algebra keeps is separated only by a left context — invisible to lasso
membership from the initial state. So the equivalence oracle (bounded here, and
structurally exact) has no counterexample to give: the coarser hypothesis is
acceptance-equivalent to `L`. Saturation's left-context split is what recovers the
class. `a_implies_xa` is the cleanest candidate for the paper's §4.2 permanent
stall — a 5-vs-4 gap reached with no counterexample — and smaller than
`F(a ∧ Xa)`, which is transient. Permanence is definitively settled by
`--eq-mode exact` (M3); the structure indicates it holds.

## Probes (under `tests/sosl/`)

- `paper_examples.py` — the three paper examples from their source HOA: reference
  size against the fingerprint tables, learned status, byte-equality, and a dump
  of the pre-equivalence stall partition for word-for-word comparison against the
  hand traces.
- `reference_vs_learner.py` — per-formula reference-vs-learned byte compare plus a
  budgeted acceptor check (exhaustive when the lasso space is small, else a
  deterministic sample).
- `diag_export_vs_hyp.py` — isolates export-vs-hypothesis divergence, separating a
  two-sided read-off defect from a learner-core defect.
- `genaut_census.py` — learns every automaton under a folder to its fixpoint and
  classifies it (canonical / surviving stall / P1 bug) against the spec's
  expected-failure table; a prototype of the campaign driver.
- `study_stall.py` — the full anatomy of one automaton's stall: canonical `D`,
  reference and learned `.sos`, stall and learned partitions, and the shortlex
  divergence lasso.
- `emit_canonical.py` — writes an input's canonical form `D` (the sos import
  layer's output) as HOA; the form reported for a specimen in `research_notes/`.

---

# Theory thread feedback — 2026-07-06, on the report above

This is the strongest report of the project so far, and the "Minimal stall
specimens" section is its best part — not because the specimens exist, but
because of *how* they were found and presented: the census run as the spec's
E2 prescribes, surviving stalls treated as first-class output, and each
specimen delivered with exactly what the theory side needs (canonical `D`,
both `.sos` objects, both partitions, the shortlex divergence lasso, links to
the generated sources). Keep that anatomy as the template for every future
exhibit. The identity-convention and saturation sections restate the theory
correctly in your own words — that is how we can tell it landed. The
phantom-pair fix is verified on all six generated files: totals are now the
true ones (1 of 10, 1 of 10, 3 of 8, 6 of 14, and the specimens' 6 of 9 and
1 of 4, each of which the theory thread re-derived by hand-enumeration and
confirmed).

One upgrade to your findings: where the report says permanence "is decided
per language by `--eq-mode exact`" and "the structure indicates it holds" —
it no longer merely indicates. The paper now *proves* both specimens
permanent (Proposition 4.4 in `sos_learning.md` §4.2, which quotes your
census as its source). For `a_implies_xa`: the predicting stem class
`s = ψ(w·z^k)` is always a commitment class, because the only uncommitted
non-empty word is the single letter `a` and normalization can never leave it
as a stem (`z = a` forces `k = 2`); commitment classes have faithful
representatives, so every prediction equals the teacher's verdict and no
counterexample exists — against *any* oracle. For `a_once`: the alive class
squares to dead, so the loop idempotent is always dead, and an alive stem
class forces a pure-`!a` loop, on which the representative lasso answers
correctly. Consequence for M3: the `--no-saturation --eq-mode exact` runs on
these two are no longer decision procedures — they are **fixtures for exact
mode itself** (spec §9, new row P4): if exact returns a counterexample there,
exact mode has the bug. And `F(a ∧ Xa)` is retired as a candidate — your own
census resolved it transient (byte-equal at M2).

Before starting M3, re-read spec §3.2 steps 4–5, §8 (M3 bullet), and §9 —
all revised today. The one that matters most: **step 5's frozen-prefix-chain
line was wrong in the spec** (it minted `(x0 . key(...), ...)`, absorbing a
representative into the prefix; correct is the frozen prefix `x0` alone, the
unconsumed segment migrating into the middle component — paper Lemma 4.5).
Implementing the old line would have failed the Even paper-trace conformance
gate in confusing ways. Also pinned: `kappa` selection (first separating
column in creation order) and the branch-2 side selection (exactly one side
disagrees — assert it, no tie-break exists). Two expectations so nothing
looks like a regression: with saturation on, Even completes with ONE
counterexample (the `a·!a` split moves from a harvest to the sweep — the
paper's §4.3 trace, now a conformance gate), and census query ledgers will
drift from this report's M2 table — record the new ones, don't chase the old.
When the EvenBlocks run lands, send the theory thread its split ledger and
the two query ledgers: the paper's Table 8 and Proposition 5.2's grounding
are waiting on exactly those.
