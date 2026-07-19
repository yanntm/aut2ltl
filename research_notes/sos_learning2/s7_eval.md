## 7. Evaluation

*Status note (to be removed once regeneration lands).* The numbers in this
section were measured with the implementation as of the committed census
record: a learner enforcing stamp legality with an on-demand pair cache,
and an align-and-scan oracle with a functionality guard. The presentation
of §3–§5 additionally holds the belief canonicalized with a total,
pair-legal `P` at every equivalence query, and simplifies the oracle to the
product scan of §2.3. No verdict is expected to change — the relaxed leg of
§7.3 *is* §6's learner, unchanged, and every certified run was already
validated by byte-equality of its export — but per-phase query counts will
shift (a `legality` phase absorbs part of `fill`/`P`); regeneration is
queued in the engineering plan.

The algorithm of §3–§5 is implemented as a pure query learner: its only
source of truth is the teacher interface, and no automaton is ever visible
to it. The evaluation answers three questions, each measured against the
canonical target `N`. **Q1 — cost:** do measured queries track the
output-polynomial bounds of Proposition 5.3? **Q2 — necessity at scale:**
how often does the relaxed learner of §6 stall, and are the stalls
permanent? **Q3 — the baseline:** against an established FDFA learner on
identical teachers, what does the algebra cost, and what does it buy? A
fourth, smaller question calibrates a constant: how sensitive is the cost
to the teacher's counterexample policy — the `log(N·ℓ)` term of
Proposition 5.3.

### 7.1 Protocol

**Teacher.** As fixed in §2.3: membership is one deterministic run,
`O(|u| + |Q|·|v|)`; equivalence is an exact align-and-scan against the
reference invariant `𝓘(L)`, computed once by the construction of [SωS26],
with minimal counterexamples (shortest stem, then shortest loop, then
shortlex). One honesty note: the oracle and the byte-equality validation
share their trust anchor, the constructed `𝓘(L)`; independence from the
automaton is retained through a teacher self-check, which cross-checks
direct simulation against the invariant read-off on 10⁴ random lassos per
case. One lasso membership is one query; equivalence queries are counted
separately (§2.1).

**Corpus.** The census is a flat, complement-closed catalogue of **6222**
ω-regular languages over one to three atomic propositions (`|Σ| = 2^AP`,
up to 8): each language appears exactly once, one canonical representative
up to atomic-proposition relabeling, and each is accompanied by its
complement. Every language with a small presentation is in the catalogue —
nondeterministic presentations count: `a → Xa`, whose smallest
*deterministic* acceptor has four states (its four residuals force them),
enters through a two-state presentation. Every input is determinized on
import; ground truth is computed by the construction of [SωS26]: the
reference `𝓘(L)`, its class count `N` — from 2 to 208 — and its LTL
verdict. The three running examples are mandatory in every experiment, as
are the two stall specimens of §6. One convention governs every count that
depends on a per-case budget: the relaxed-leg classification of §7.3 is
made at a stated 60 s budget, decided verdicts are floors — a decided case
never flips between drops — and undecided cases are reported, never folded
into a count.

**Reproducibility and validation.** Runs are deterministic — the legality
scan order is pinned (§4.2), counterexamples are minimal — so the traces of
§3–§5 are the transcripts of the corresponding runs. Validation is Theorem
5.2 exercised end-to-end: the learned invariant is byte-equal to the
constructed reference, on **all 6222** languages, `N` from 2 to 208, zero
mismatches. Two automata for `GF(aa)` yield byte-identical ledgers and
signature matrices: presentation-independence, on the learner's side.

### 7.2 Cost against the canonical target (Q1)

For every case we record membership queries by phase — table fill,
counterexample harvest, legality escalations, the `P`-cache — plus
equivalence queries, splits, and columns by sort, against `N`. The named
cases in full, the two §5 ledgers among them:

| case | `N` | initial | splits | member (fill/harvest/leg/`P`) | equiv | cex |
|---|--:|--:|--:|---|--:|--:|
| `a ∧ XG¬a` | 4 | 2 | 2 | 35 (26/3/2/4) | 2 | 1 |
| `a → Xa` | 5 | 4 | 1 | 43 (32/0/2/9) | 1 | 0 |
| `Even` | 5 | 3 | 2 | 51 (32/4/7/8) | 2 | 1 |
| `GF(aa)` | 6 | 3 | 3 | 74 (51/4/9/10) | 2 | 1 |
| `EvenBlocks` | 8 | 3 | 5 | 99 (67/4/14/14) | 2 | 1 |

(*initial* = classes of the first stabilized table; on every row the split
count is exactly `N −` initial.) Note the `a → Xa` row: one legality
escalation, zero counterexamples, a single assenting equivalence query —
the legal learner never even presents the acceptor §6's relaxed learner
stalls on. The `GF(aa)` row pays off §2.3's promise: the learned
invariant's power orbits all have period one — aperiodic, the
presentation's `Z₂` destroyed — so its LTL verdict is read off the learned
object, as `Even`'s non-LTL verdict was in Table 8(b). The designed bounds
hold on every case: `splits ≤ N`, the fill term inside `N²·|Σ|` (at
`N = 8`, 67 against 128), harvest and legality adding the analysis term.
Over the whole census `splits ≤ N` holds on every language — the sharpest,
at `N = 208`, splits 194 times — and the fill term tracks the quadratic
envelope at every alphabet size; the per-`N` aggregates mix alphabets, so a
bucket reads against `N²·|Σ|` at its own `|Σ|`. Equivalence queries never
leave the single digits — at most 6, across the entire catalogue,
`N = 208` included. Median membership by class count traces the quadratic
growth (the two `N = 2` languages are `∅` and `Σ^ω`, as the adjoined
identity demands):

| `N` | 2 | 4 | 8 | 13 | 21 | 32 | 50 | 72 | 97 | 121 | 208 |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| median member | 3 | 151 | 124 | 262 | 567 | 1007 | 2043 | 3098 | 4768 | 7449 | 27054 |
| median equiv | 1 | 1 | 2 | 2 | 2 | 2 | 2 | 2 | 1 | 2 | 1 |

The fill term dominates, harvest is logarithmic (§7.4), legality a small
constant per split. Soundness is uniform across the LTL cut; raw cost is
not — the genuinely ω-counting half is the expensive half:

| definability | languages | median `N` | median splits | median member |
|---|--:|--:|--:|--:|
| LTL (aperiodic) | 3738 | 12 | 9 | 291 |
| non-LTL | 2484 | 20 | 16 | 557 |

But the entire signal is `N` itself. Normalized by the designed bounds the
cut disappears — median `splits/N` is 0.71 against 0.81, the fill envelope
ratio 0.71 against 0.57 — and the same holds across the Wagner hierarchy:
no degree is intrinsically harder to learn. The group structure that
defeats LTL-definability inflates the algebra the learner must reconstruct;
given its size, the learner is classification-blind. Wall time follows the
same account: the full census costs 10733 s single-threaded — median
0.12 s per language, the worst case 49.6 s at `N = 68`.

### 7.3 Necessity at scale (Q2)

The relaxed learner of §6 runs under the exact oracle, and each language is
classified by its stall: **none** — the first closed, consistent fixpoint
is already canonical; **transient** — a non-canonical fixpoint, broken by a
later counterexample; **permanent** — a non-canonical fixpoint the exact
oracle certifies, which no counterexample breaks. By Theorem 6.2 a
certified stall's partition is never a congruence, so there is no algebra
on its classes to export: on the relaxed leg "export" is a refusal, the
recorded outcome *correct acceptor, no algebra*. Theorem 6.2 is also
performed at census scale: on every one of the 3137 certified permanent
stalls, the stamp-legality check fails, and on every one of the 2336
byte-equal recoveries it passes — zero off-diagonal mass, and the verdicts
agree on all 2733 dual pairs with both sides decided. At the 60 s budget
the partition reads 3137 permanent / 2336 recovered / 736 undecided, with
13 languages beyond the exact oracle's reach in the recording pipeline,
recorded as deferred and never folded into the counts, while their legal
runs remain byte-exact. Decided counts are floors: undecided cases can
later resolve, decided ones never flip.

Permanent stalls are not rare — they are the majority of decided cases.
**3137 of the 6222 languages stall permanently**: without the legality
discipline the learner loses the algebra on half the catalogue. The gap
between the stalled right congruence and the syntactic algebra reaches
**53** classes; its head:

| gap `N − stall` | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | ⋯ | 46 | 48 | 53 |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| languages | 661 | 533 | 467 | 332 | 242 | 140 | 149 | 99 | 75 | 31 | ⋯ | 2 | 2 | 2 |

The median gap is 3 — most stalls are a few classes short — but the tail is
long, and its sharpest specimens come in dual pairs: at gap 53, a language
and its complement with `N = 68` stalled at 15 classes, the stalled
acceptor barely a fifth of its algebra. Permanence and gap are
complement-invariant — a run on the complement of `L` is the bit-flip of
the run on `L` — and the data confirms it wherever both duals are decided;
the raw counts above are budget-censored floors, so buckets need not pair
off exactly.

Two structural facts. Permanence **cuts across the LTL boundary** — 1741 of
the 3137 are LTL-definable, tracking the catalogue's own composition: the
permanent stall measures the gap between the right and the two-sided
congruence, not ω-counting power; aperiodic languages stall as readily as
group-bearing ones. And prefix-dependence is **not necessary** — but where
prefix-independent stalls live is sharply structured. Of the 3137, **231
are prefix-independent** (the check is algebraic, on the canonical
invariant: acceptance invariant under every left multiplication of the stem
class), and every one of them sits at a transfinite Wagner degree: all 2164
permanent stalls of finite degree — safety and guarantee prominent among
them — are prefix-dependent. That is the mechanism split of §4 realized at
census scale: a permanent stall is a separation only a left context
recovers; prefix-independence silences the linear shape's left contexts
(Proposition 4.6), while the ω-power shape's left action survives it as a
rotation (Corollary 4.7) — and it is from the ω-th degree upward, starting
at deterministic-Büchi and co-Büchi power, that prefix-independent
permanent stalls in fact appear. Two of them, with their complements, carry
the full Corollary 4.7 certificate: `N = 10` stalled at 8 and `N = 16`
stalled at 14, prefix-independence verified algebraically on the canonical
invariant, and every column their legal runs mint an ω-column (4.7(b)) —
the recovering left contexts acting inside the loop, where no prefix
exists to delete. On every one of the 3137, at every scale, the legality
discipline recovers the canonical algebra (the census-wide soundness of
§7.1); `a → Xa` does it with zero counterexamples and a single equivalence
query: the escalations supply what the oracle cannot (Proposition 6.1).

### 7.4 The FDFA baseline (Q3)

The baseline is ROLL [LCZL21, LSTCX19], the classification-tree FDFA
learner, in its periodic / syntactic / recurrent modes, on the same census
languages under the same counting rule (one lasso = one membership query).
Two adaptations follow from ROLL's interface. ROLL learns the language of a
Büchi automaton, so it receives a state-based Büchi presentation of each
language (ROLL misreads a transition-based Büchi input as a trivial
language): the language is the same, the presentation ROLL's, so membership
counts are presentation-sensitive and the comparison rests on output size
and capability. And the two learners certify equivalence by different but
both exact mechanisms — ours the align-and-scan against the language's
invariant (§2.3), ROLL's its native automaton equivalence (RABIT).

The named-case paired table (ROLL's size is the summed states of its FDFA,
leading plus progress DFAs):

| case | ours `N` (MQ/EQ) | ROLL periodic | syntactic | recurrent |
|---|---|:--:|:--:|:--:|
| `GF(aa)` | 6 (74/2) | 4 | 4 | 4 |
| `Even` | 5 (51/2) | 12 | 15 | 9 |
| `EvenBlocks` | 8 (99/2) | 8 | 8 | 8 |
| `a → Xa` | 5 (43/1) | 12 | 14 | 9 |
| `a ∧ XG¬a` | 4 (35/2) | 8 | 10 | 7 |

Every entry lies inside Proposition 5.4(a)'s `N + N²` envelope, and within
it the two objects trade places. Across the census the median class count
is `N = 16`, against FDFA-size medians 16 / 21 / 12 (periodic / syntactic /
recurrent); over the 5960 languages both learners decide, against each
language's smallest FDFA the algebra is smaller on 2032, larger on 3574,
tied on 354. Size is comparable — a wash inside the envelope; the
exponential separation of Proposition 5.4(b) needs larger algebras than the
census reaches. The trade is not noise, though — it correlates with the LTL
cut. On aperiodic languages the two objects are near parity (algebra
smaller on 1524, larger on 1842, tied on 207); on group-bearing languages
the FDFA usually wins the size comparison (508 / 1732 / 147): the group
structure that blocks LTL-definability is also what inflates the algebra
against an acceptor — Proposition 5.4(b)'s mechanism, visible at census
scale.

The comparison's result is capability. From the learned invariant,
LTL-definability is a read-off — the aperiodicity test of §2.2 — computed
on every case and agreeing with ground truth on all 6222: every run
certifies exact, so the read-off is evaluated on an invariant byte-equal to
the reference. From an FDFA it is not answerable without a further
construction. One learner returns the language's algebra, from which
definability is read; the other returns an acceptor, from which it is not.

### 7.5 Counterexample sensitivity

Proposition 5.3 depends on the teacher only through the `log(N·ℓ)` harvest
term. The counterexample-bearing named cases are re-run under
counterexample policies — minimal (the default) and adversarially padded,
stem and loop pumped by factors 2 to 32 — comparing total and harvest-only
membership queries. As the loop is pumped from length 3 to 96 the harvest
term grows from 4 to 9 queries: one query per doubling,
`harvest ≈ log₂ ℓ`, the binary search over the stem/loop chain, the
learned invariant unchanged. Padding costs queries, not correctness. (A
first-found policy coincides with minimal for the shortlex-least oracles
used here, so it forms no separate series.)
