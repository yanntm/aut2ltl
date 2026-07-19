## 6. Evaluation

*⟨Open, marked ⟨TBD-M4⟩ below: §6.3's final counts, gap distribution, and
per-shape confirmation of the exhaustive negative (the E2 drop, pending the
prefix-independence recount), plus the section's remaining 3938-era numbers
to restate from the committed 6222 record.⟩*

The algorithm of §3–5 is implemented as a pure query learner: its only source
of truth is the teacher interface, and no automaton is ever visible to it. The
evaluation answers three questions, each measured against the canonical target
`N`. **Q1 — cost:** do measured queries track the
output-polynomial bounds of Proposition 5.4? **Q2 — the ablation:** how often
does the learner without saturation stall, and are the stalls §4.2's — is
saturation doing real work across a corpus, not only on Proposition 4.4's two
specimens? **Q3 — the baseline:** against an established FDFA learner on
identical teachers, what does the algebra cost, and what does it buy? A
fourth, smaller question calibrates a constant: how sensitive is the cost to
the teacher's counterexample policy — the `log(N·ℓ)` term of Proposition 5.4.
Across a complement-closed census of 3938 languages the learner returns every
canonical invariant exactly; saturation is indispensable on over a thousand of
them, prefix-independent languages included — no counterexample can deliver
their algebras; and the invariant answers LTL-definability, which no FDFA
does.

### 6.1 Protocol

**Teacher.** As fixed in §2.3: membership is one deterministic run,
`O(|u| + |Q|·|v|)`; equivalence is a cheap representative audit followed by
an exact *align-and-scan* against the reference invariant. The hypothesis's
fold automaton is aligned with `𝓘(L)`: the letter-generated graph of pairs
`(ψ(w), 𝒮_L(w))` — the hypothesis's fold against the syntactic stamp —
is built lazily and memoized, and on every cell (stem node, loop node) two
verdicts are compared: the hypothesis's prediction on the cell's keyed
lasso, and the invariant's algebraic verdict `(s·e^π, e^π) ∈ P`. A flagged
cell's keyed lasso is a genuine counterexample outright — both verdicts are
evaluated on that concrete lasso. That one keyed lasso per cell also
*decides* the cell — the certification and minimality claims — because both
verdicts are constant on cells: the invariant's is, since membership
factors through `𝒮_L` of stem and loop; the hypothesis's is *provided the
aligned graph is functional* — no two nodes share their `𝓘(L)`-component,
i.e. the fold never splits a syntactic class — for then the loop orbit, the
stabilization power, and the predicting pair are all determined by the
cell. Functionality is not assumed, and it genuinely fails mid-run — the
fold of a closed, consistent table can *split* a syntactic class beyond its
table words (realized on a census language: `!a·!a·a ≈_L a·!a·!a`, yet the
two words fold to different classes), so a mid-run hypothesis is not merely
coarser than the algebra (§4.2) but incomparable with it. The oracle
therefore asserts functionality on the built graph at every query, and a
firing hands the query to the fallback — the product of the automaton with
the hypothesis's transformation closure, which needs no such assumption —
so certification stays exact wherever the fallback finishes inside its work
cap — in the event, everywhere: the guard fires on 2694 of the 6222
default-leg runs (3398 firings) and the fallback finished within its cap on
every one, so every default-leg certification is exact; only the ablation
leg records runs that never reach certification, deferred (§6.3). The
ablation leg of §6.3 leans
hardest on that exactness — a permanence verdict certifies a *non-canonical*
fixpoint, the one claim byte-equality cannot re-validate — while every other
reported run is additionally validated end-to-end by byte-equality of the
exported invariant against the constructed reference. One honesty note: the
oracle and the byte-equality validation now share their trust anchor, the
constructed `𝓘(L)`; independence from the automaton is retained through the
teacher self-check, which cross-checks `D`-simulation against the invariant
read-off on 10⁴ random lassos per case. Counterexamples are minimal
(shortest stem, then shortest loop, then shortlex) — keys being
shortlex-least and cells scanned in lasso order, the least disagreeing cell
yields exactly that. One lasso membership is
one query; equivalence queries are counted separately (§2.1).

**Corpus.** The census is a flat, complement-closed catalogue: **3938**
ω-regular languages up to atomic-proposition relabeling, one representative
per language, every language accompanied by its complement. Its sources are
automaton *shapes* — transition-based generalized-Büchi automata over one to
three atomic propositions (`|Σ| = 2^AP`, up to 8) with `n` states and `k`
acceptance sets (`nstate·map·kacc`), nondeterminism allowed, each shape
doubled by a parity-acceptance variant of the same skeleton — the smallest
enumerated exhaustively, the deeper reached by reproducible sampling, all
deduplicated by language. Nondeterminism matters for where a language first appears:
`a → Xa`, whose smallest *deterministic* acceptor has four states (its four
residuals `L`, `a·Σ^ω`, `Σ^ω`, `∅` force them), has a two-state
nondeterministic presentation and so belongs to the two-state shapes. Every
input is determinized on import; ground truth is computed by the construction
of [SωS26]: the reference `𝓘(L)`, its class count `N` — from 2 to 121 — and
its LTL verdict. The three running examples are mandatory in every
experiment, as are the two permanent-stall specimens of §4.2. The smallest
shape at which non-LTL languages appear, `2state1ap1acc` (129 languages; its
parity twin re-presents the same languages), is enumerated exhaustively and
carries §6.3's exhaustive claims. Every language appears exactly once, and
every language with a small presentation is in the catalogue; per-shape
composition is corpus provenance, not evaluation data.

**Reproducibility and validation.** Runs are deterministic — the sweep's scan
order is pinned (§4.3), counterexamples are minimal — so the traces of §3–5 are
the transcripts of the corresponding runs. Validation is Theorem 5.1 exercised
end-to-end: the learned invariant is byte-equal to the constructed reference.
This holds on every language the sweep has reached — **2492** of the 3938,
`N` from 2 to 121, zero mismatches ⟨TBD-M4: the completed sweep⟩ — and
includes an exhaustive enumeration of the smallest non-LTL shape
(`2state1ap1acc` and its parity twin). Two automata for `GF(aa)` yield
byte-identical ledgers and signature matrices: Theorem 5.1's
presentation-independence, on the learner's side.

### 6.2 Cost against the canonical target (Q1)

For every case we record membership queries by phase — table fill,
counterexample harvest, saturation, the `P`-cache — plus equivalence queries,
splits, and columns by sort, against `N`. The named cases in full, the two
§5 ledgers among them:

| case | `N` | initial | splits | member (fill/harvest/sat/`P`) | equiv | cex |
|---|--:|--:|--:|---|--:|--:|
| `a ∧ XG¬a` | 4 | 2 | 2 | 35 (26/3/2/4) | 2 | 1 |
| `a → Xa` | 5 | 4 | 1 | 43 (32/0/2/9) | 1 | 0 |
| `Even` | 5 | 3 | 2 | 51 (32/4/7/8) | 2 | 1 |
| `GF(aa)` | 6 | 3 | 3 | 74 (51/4/9/10) | 2 | 1 |
| `EvenBlocks` | 8 | 3 | 5 | 99 (67/4/14/14) | 2 | 1 |

(*initial* = classes of the first stabilized table; on every row the split
count is exactly `N −` initial.) The `GF(aa)` row also pays off §2.3's
promise: the learned invariant's power orbits all have period one — aperiodic,
the presentation's `Z₂` destroyed — so its LTL verdict is read off the
learned object, as `Even`'s non-LTL verdict was in Table 7(b). The designed
bounds hold on every case:
`splits ≤ N`, the fill term inside `N²·|Σ|` (at `N = 8`, 67 against 128),
harvest and saturation adding the counterexample-analysis term. Over the
whole census `splits ≤ N` holds on every language — the sharpest, at
`N = 121`, splits 118 times — and the fill term tracks the quadratic
envelope at every alphabet size; the per-`N` aggregates mix alphabets, so a
bucket reads against `N²·|Σ|` at its own `|Σ|` — the `N = 4` bucket's
median fill of 145, dominated by `|Σ| = 8` languages, sits at their
envelope of 128, its `|Σ| = 2` minority at 17 against 32. Equivalence
queries stay in the single digits across the entire range, `N = 121`
included. Median membership by class count traces the quadratic growth
(the two `N = 2` languages are `∅` and `Σ^ω`, as the adjoined identity
demands):

| `N` | 2 | 4 | 8 | 13 | 21 | 32 | 50 | 72 | 97 | 121 |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| median member | 3 | 151 | 104 | 248 | 514 | 883 | 2028 | 3028 | 4665 | 5696 |
| median equiv | 1 | 1 | 2 | 2 | 2 | 2 | 2 | 2 | 1 | 2 |

The fill term dominates, harvest is logarithmic (§6.5), saturation a small
constant per split. Soundness is uniform across the LTL cut; cost is not —
the genuinely ω-counting half is the expensive half:

| definability | languages | median `N` | median splits | median member |
|---|--:|--:|--:|--:|
| LTL (aperiodic) | 1486 | 7 | 4 | 151 |
| non-LTL | 1006 | 17 | 13 | 349 |

The group structure that defeats LTL-definability is also what the learner
pays to reconstruct — though only through `N`: normalized by the designed
bounds, cost is classification-blind. Wall time stays modest: the full
default-leg sweep totals 10733 s, median 0.12 s per language, the worst case
49.6 s at `N = 68`.

### 6.3 The saturation ablation (Q2)

The learner runs with and without the sweep, the ablated leg under the exact
oracle, and each language is classified by its stall: **none** — the first
closed, consistent fixpoint is already canonical; **transient** — a
non-canonical fixpoint, broken by a counterexample; **permanent** — a
non-canonical fixpoint the exact oracle certifies, which no counterexample
breaks. Only the left-context sweep splits a permanent stall; without it the
learner stops on the Cayley acceptor and nothing more — by Theorem 5.3 a
certified stall's partition is never a congruence, so there is no algebra on
its classes to export: on the ablation leg "export" is a refusal, the
recorded outcome *correct acceptor, no algebra*. ⟨TBD: the congruence-column
recount — every permanent stall fails Lemma 5.2's check, Theorem 5.3
performed at census scale; on a handful of languages the ill-defined product
cannot even reach every class from `ε`.⟩

Permanent stalls are not rare. Of the 2492 languages the census sweep has
reached, **1180 stall permanently** ⟨TBD-M4: final counts — the unfinished
largest shape supplies the large-gap tail⟩; the gap between the stalled
right congruence and the syntactic algebra reaches **53** classes (`N = 68`
stalled at 15, recovered by 3 counterexamples and 12 saturation
escalations). The head of the gap distribution:

| gap `N − stall` | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | ⋯ | 53 |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| languages | 274 | 205 | 183 | 126 | 82 | 50 | 58 | 44 | 24 | 10 | ⋯ | 2 |

Exhaustively over the smallest non-LTL shape (`2state1ap1acc`, 129
languages; its single `Inf`-set makes every member Büchi, so acceptance
carries no signal there), 44 stall permanently — the family is dense already
at the frontier, and the two specimens of §4.2 are its two smallest members.
`a → Xa` reaches its canonical five-class algebra under saturation with zero
counterexamples and a single equivalence query: the sweep supplies what the
oracle cannot (Proposition 4.4). Every member, at every scale, recovers to
its canonical algebra under saturation (the census-wide soundness of §6.1).
Since a run on the complement of `L` is the bit-flip of the run on `L`,
permanence and gap are complement-invariant, and on the complement-closed
census every count above must pair off exactly — a standing consistency
check the completed sweep must pass.

Two structural facts. Permanence **cuts across the LTL boundary** — 582 of
the 1180 are LTL-definable: the permanent stall measures the gap between the
right and the two-sided congruence, not ω-counting power; aperiodic
languages stall as readily as group-bearing ones. And prefix-dependence is
**not necessary**. At the smallest shape all 44 permanent stalls are
prefix-dependent, which fits the linear mechanism — a permanent stall is a
separation only a left context recovers, and prefix-independence silences
the linear shape's left contexts (Proposition 4.6) — but the ω-power shape's
left action survives prefix-independence as a rotation (Corollary 4.7), and
the census realizes it: two prefix-independent languages, with their
complements, stall permanently — `N = 10` stalled at 8, `N = 16` at 14, both
exact-certified, both properly requiring a three-priority parity acceptance
(beyond deterministic Büchi and co-Büchi power). The Corollary 4.7 certificate holds on all
four: prefix-independence is verified algebraically on the canonical
invariant — acceptance invariant under every left multiplication of the
stem class — and every column their saturated runs mint is an ω-column
(4.7(b)), the recovering left contexts acting inside the loop, where no
prefix exists to delete. Both witnesses come from the census's sampled
tier — necessarily: every exhaustively enumerated shape either is
completely swept with zero prefix-independent permanent stalls, or
carries trivial acceptance and so recognizes only safety languages, which
Lemma 4.8 bars from nontrivial prefix-independence. The refutation loses
nothing to sampling — an existence claim is carried by its per-language
certificate — and what exhaustion contributes is the complementary
negative: prefix-independent permanent stalls first arise beyond the
enumeration wall. Between
Lemma 4.8's floor and the witnesses' three-priority degree the territory
stays open: no witness has appeared at deterministic-Büchi, co-Büchi, or
single-Rabin-pair power. ⟨TBD-M4: the completed sweep's per-shape
confirmation of the exhaustive negative.⟩

At the top of the range a handful of languages exceed the exact oracle's
reach — their aligned graphs are non-functional and the fallback product
exceeds its work cap — so their permanent-vs-transient classification is
recorded as deferred and never folded into the counts, while their saturated
runs remain byte-exact. The deferred set is itself complement-closed, as the
bit-flip symmetry demands.

### 6.4 The FDFA baseline (Q3)

The baseline is ROLL [LCZL21, LSTCX19], the classification-tree FDFA learner,
in its periodic / syntactic / recurrent modes, on the same census languages
under the same counting rule (one lasso = one membership query). Two adaptations
follow from ROLL's interface. ROLL learns the language of a Büchi automaton, so
it receives a state-based Büchi presentation of each language (Spot's `SBAcc` —
ROLL misreads a transition-based Büchi input as a trivial language): the language is the same, the
presentation ROLL's, so membership counts are presentation-sensitive and the
comparison rests on output size and capability. And the two learners certify
equivalence by different but both exact mechanisms — ours the align-and-scan
against the language's invariant (§2.3), ROLL's its native automaton
equivalence (RABIT).

The named-case paired table (ROLL's size is the summed states of its FDFA,
leading plus progress DFAs):

| case | ours `N` (MQ/EQ) | ROLL periodic | syntactic | recurrent |
|---|---|:--:|:--:|:--:|
| `GF(aa)` | 6 (74/2) | 4 | 4 | 4 |
| `Even` | 5 (51/2) | 12 | 15 | 9 |
| `EvenBlocks` | 8 (99/2) | 8 | 8 | 8 |
| `a → Xa` | 5 (43/1) | 12 | 14 | 9 |
| `a ∧ XG¬a` | 4 (35/2) | 8 | 10 | 7 |

Every entry lies inside Proposition 5.5(a)'s `N + N²` envelope, and within it
the two objects trade places. Across the census the median class count is
`N = 12`, against FDFA-size medians 14 / 18 / 11 (periodic / syntactic /
recurrent); against each language's smallest FDFA the algebra is smaller on
1102, larger on 1239, tied on 150. Size is comparable; the exponential
separation of Proposition 5.5(b) needs larger shapes than the census
reaches. But the trade is not noise — it correlates with the LTL cut. On
aperiodic languages the algebra is more often the smaller object (862
smaller / 534 larger / 89 tied); on non-LTL languages the FDFA usually is
(240 / 705 / 61): the group structure that blocks LTL-definability is also
what inflates the algebra against an acceptor — Proposition 5.5(b)'s
mechanism, already visible at census scale. ⟨TBD-M4: restate this paragraph
from the committed 6222-scale `e3_summary` — the LTL-cut direction *inverts*
there (on LTL the algebra is more often the larger object, 1524 v 1842); the
old headline was a small-shape artifact — keep the correlation, drop the
direction claim.⟩

The comparison's result is capability. From the learned invariant,
LTL-definability is a read-off — the aperiodicity test of §2.2 — computed
on every case, agreeing with ground truth on all 6222 — every default-leg
run certifies exact, so the read-off is evaluated on an invariant byte-equal
to the reference; from an FDFA it is
not answerable without a further construction. One learner returns the
language's algebra, from which definability is read; the other returns an
acceptor, from which it is not.

### 6.5 Counterexample sensitivity

Proposition 5.4 depends on the teacher only through the `log(N·ℓ)` harvest
term. The counterexample-bearing named cases are re-run under counterexample
policies — minimal (the default) and adversarially padded, stem and loop
pumped by factors 2 to 32 — comparing total and harvest-only membership
queries. As the loop is pumped
from length 3 to 96 the harvest term grows from 4 to 9 queries: one query per
doubling, `harvest ≈ log₂ ℓ`, the binary search over the stem/loop chain, the
learned invariant unchanged. Padding costs queries, not correctness. (A
first-found policy coincides with minimal for the shortlex-least oracles used
here, so it forms no separate series.)
