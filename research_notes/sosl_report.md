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
