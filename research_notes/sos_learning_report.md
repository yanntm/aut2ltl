# SoS Learner — Status Report

Where the `sosl/` implementation stands against the plan in
`research_notes/sos_learning_spec.md` (the normative document), the paper
`research_notes/sos_learning.md` (whose running examples are computed by hand),
and the `.sos` normal form of `sosl/sosl/sos/io/sos_format.md`. This report answers
the questions the spec raises; it describes the implementation as it is.

## Milestones (spec §8)

- **M1 — Teacher + validator.** Done.
- **M2 — Learner without saturation** (table; fill / close / consist; chains;
  export). Done.
- **M2.5 — Convention alignment** (fresh-identity reference builder; the
  learner's `[ε]` singleton rule; the `.sos` fixtures). Done.
- **M3 — Saturation + exact equivalence.** Done. The two-sided sweep
  (`sosl/sosl/learn/saturate.py`) and the exact equivalence oracle
  (`sosl/sosl/teacher/exact.py`) are landed; every census language reaches its
  canonical invariant, the Even run reproduces the paper's §4.3 trace, and the
  two permanent-stall specimens behave as Proposition 4.4 predicts.
- **M4 — Campaign.** Essentially complete, and **re-run over the new `flat_canon`
  benchmark** (the flat, complement-closed catalogue, 3938 languages up to AP
  relabeling — supersedes the old per-shape census). **E0, E1, E2, E5, and E3
  (ROLL) all delivered**; the `sosl.experiment` package (driver, manifest,
  per-run stats, E0/E1/E2/E3/E4/E5 reports, ROLL baseline) is landed, the E0 gate
  is green, E5 confirms the harvest term is `log(|cex|)`, E3 is a size wash inside
  `N+N²` with the capability column the real result. On `flat_canon` the learner
  is **SOUND on every language** with `splits ≤ N` throughout (N up to 121), and
  the permanent-stall family — 44 at the old single shape — is now in the
  **thousands**, with a candidate **prefix-independent** permanent stall that
  would settle the paper's last open question. See "Flat-canon census rerun"
  below (figures preliminary until the sweep completes). Only **E6**
  (beyond-census random instances) remains, a stretch goal.

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
  the grouping skips it (`sosl/sosl/learn/partition.py`).

A non-empty class **may** act as an identity on all the *other* non-empty
classes and still be its own class. `[aa]` in Even does: it is neutral on every
class but is distinct from `[ε]` (keyed `a;a`). Both `M(c, [ε]) = c` and
`M([ε], c) = c` hold for every `c`, including such a `c`; there is no reason to
merge or special-case it.

## Saturation

`Invariant.member` reduces a lasso through the class multiplication table
`mult[c][d] = fold(c, rep[d])`, substituting a class representative in the middle
of a product. That substitution is sound only when the partition is a **two-sided
congruence** (`u ~ v` implies both `u·x ~ v·x` and `x·u ~ x·v`). A table closed
under fill / close / consist guarantees only the right half, so a pre-saturation
export can be acceptance-wrong even where the hypothesis is correct — the
hypothesis folds the literal letters of the queried lasso and never substitutes a
representative, which is why the two read-offs of one partition can disagree.

Saturation (`sosl/sosl/learn/saturate.py`) is the left-context sweep that turns the
right congruence into the two-sided syntactic one, after which the export is
well-defined. It runs after fill / close / consist reach a fixpoint and before
each equivalence query; an escalation restarts the loop, and an equivalence query
is posed only once a sweep comes back clean.

- For every non-representative table word `p`, its class rep `r0`, and every left
  class `d` (rep `r`), it compares `fold(d, p)` against `fold(d, r0)` — pure table
  folding, zero queries. On a mismatch it takes the first column `κ` separating
  the two fold-class reps and escalates.
- **Branch 1** — the bits of `r·p` and `r·r0` under `κ` differ: mint the column
  that reproduces "`r·w` under `κ`" as a bit on the bare candidate `w`.
- **Branch 2** — those bits agree: exactly one of `r·p` / `r·r0` disagrees with
  its own fold-class rep under `κ`; the **frozen-prefix chain** binary-searches the
  flip and mints one column, `κ`'s own prefix frozen in place and the unconsumed
  segment migrating into the middle component (spec §3.2 step 5, Lemma 4.5).

Each escalation splits at least one class, so the sweep terminates in at most the
final class count; a clean sweep is the certificate that the export is sound.

**One spec correction (branch-1 omega columns).** Reproducing "`r·w` under `κ`"
as a bit on the bare candidate `w` depends on where `w` sits. For a *linear*
`κ = (x, y, t)` the candidate is in the finite prefix, so `r` prepends there:
`(x·r, y, t)`. For an *omega* `κ = (x, y)` the candidate rides in the period, and
peeling one `r` off the repeating block gives `x·(r·w·y)^ω = x·r·(w·y·r)^ω` — so
`r` must seed **both** the prefix and the period suffix: `(x·r, y·r)`. The
bare-prefix form `(x·r, y)` keeps the period `w·y` and does not separate the
candidate on a prefix-independent language: on `GF(aa)` it maps both `a` and `aa`
to accepting and the sweep never converges. This is the omega analog of the Lemma
4.5 correction already made for the frozen-prefix chain (the segment migrates into
the middle, never the prefix); the same one-line fix applies to spec §3.2 step 4.

## Permanence and exact mode

Whether a language admits a **permanent** stall — a non-canonical fixpoint no
counterexample breaks — was the paper's §4.2 open question. It is now settled for
the two census specimens below: Proposition 4.4 proves both `a_implies_xa` and
`a_once` permanent (their stalls survive *any* equivalence oracle, exact
included). `F(a ∧ Xa)`, an earlier candidate, is retired — the census resolves it
**transient**: it reaches the canonical 6-class object already at M2 (`[ε] [!a]
[a] [!a;a] [a;!a] [a;a]`, byte-equal), a later counterexample breaking its
pre-equivalence stall.

Exact mode (`sosl/sosl/teacher/exact.py`) is the complete equivalence oracle. It
decides a hypothesis against `D` through the product of `D`'s reachable
stem-configs `(state, class)` with the *transformation closure* of the
hypothesis: each loop word acts on the classes as a function and on `D` as a
transition/mark profile, so one representative lasso per `(stem-config,
loop-element)` cell fixes both verdicts, and the shortlex-least cell on which they
disagree is the minimal counterexample. It returns that lasso or a certificate of
equality (`sosl/sosl/teacher/exact.py`).

Because Proposition 4.4 proves the two specimens permanent, their
`--no-saturation --eq-mode exact` runs are no longer decision procedures but
**fixtures for exact mode itself** (spec §9 P4): exact *must* certify their 4- and
3-class stalls, and a counterexample there would be an exact-mode bug. With
saturation on, exact drives both to the canonical 5 and 4. Both hold
(`sosl/tests/sosl/exact_fixtures.py`).

## Minimal stall specimens

An exhaustive learner census over the smallest 1-AP shapes (`sosl/tests/sosl/genaut_census.py`
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
membership from the initial state. So the equivalence oracle has no counterexample
to give: the coarser hypothesis is acceptance-equivalent to `L`, and saturation's
left-context split is what recovers the class. Both stalls are **permanent** —
Proposition 4.4 proves no oracle breaks them, and exact mode confirms it by
certifying each stalled fixpoint (4 and 3 classes) with no counterexample; with
saturation on, each reaches its canonical algebra (5 and 4, byte-equal).
`a_implies_xa` is the sharpest exhibit: its 5-vs-4 gap is reached with **zero**
counterexamples, and it is smaller than `F(a ∧ Xa)`, which is transient.

## Saturated runs: conformance and ledgers

With saturation on, every census language reaches its canonical invariant
byte-equal to the reference builder — the two specimens included
(`sosl/tests/sosl/saturation_gate.py`): `GF(aa)` → 6, `Even` → 5, `EvenBlocks` → 8,
`a_implies_xa` → 5, `a_once` → 4.

**Even reproduces the paper's §4.3 trace exactly** (`sosl/tests/sosl/even_conformance.py`).
The day-one sweep on the initial 3-class table is clean; one equivalence
counterexample `(ε, a;a;!a)` splits `a;a`; the four-class sweep then fires first at
cell `(!a;a, [a])`, branch 2 (the two probe bits agree), and the frozen-prefix
chain flips at `j = 1 → 2`, minting the **linear** column `(ε, a;!a, a;a;!a)` — not
the omega column `(a, ε)` a different scan order would produce.

The saturated runs of the two Büchi census cases produce the split and query
ledgers below (`sosl/tests/sosl/m3_ledgers.py`; routine close/consist splits are folded
into the initial stabilized class count, and one mint can split more than one
class on re-stabilization).

**Even** — `(aa)*·!a·Σ^ω`, reference 5 (initial stabilized 3):

```
 #  trigger           chain   n      split          column
 1  cex (ε, a;a;!a)   stem    3->4   a -> a, a;a    ε·[]·!a , (a;a;!a)^ω
 2  saturation        frozen  4->5   a -> a, a;!a   ε·[]·a;!a , (a;a;!a)^ω

member: fill 32 / harvest 4 / saturation 7 / P-cache 8 / total 51
equiv 2 · cex 1 · sat 1 · columns lin/om 2/1
```

**EvenBlocks** — 2-state prefix-independent, `Fin(0) & Inf(1)`, reference 8
(initial stabilized 3):

```
 #  trigger           chain   n      split                              column
 1  cex (ε, !a;a;a)   loop    3->4   a -> a, !a;a                       a·([]·a)^ω
 2  saturation        frozen  4->6   a -> a, a;a ; !a;a -> !a;a, a;!a   a·([]·!a;a)^ω
 3  saturation        frozen  6->8   !a -> !a, a;!a;a ; a;a -> a;a,     ε·([]·!a)^ω
                                     !a;a;!a

member: fill 67 / harvest 4 / saturation 14 / P-cache 14 / total 99
equiv 2 · cex 1 · sat 2 · columns lin/om 0/4
```

Both complete with a **single** counterexample — the feedback's expectation, the
`a;!a` split having moved from an equivalence harvest to the sweep. `EvenBlocks`,
being prefix-independent, is carried entirely by omega columns (all frozen-chain
mints); the branch-1 omega correction above is the analogous fix that lets the
sweep converge on `GF(aa)`.

## Probes (under `sosl/tests/sosl/`)

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
- `saturation_gate.py` — learns every census source with saturation on and
  asserts byte-equality to the reference (the M3 end-to-end gate).
- `even_conformance.py` — asserts the Even run reproduces the paper's §4.3 trace
  (clean day-one sweep, one cex, the exact sweep-minted linear column).
- `exact_fixtures.py` — exact mode: certification on the proven-permanent stalls
  under `--no-saturation` (spec P4), and canonical byte-equality with saturation.
- `m3_ledgers.py` — the split and per-phase query ledgers of a saturated run; a
  prototype of the campaign audit renderer.

---

## Theory-thread feedback — M3 accepted, notes before M4 (2026-07-07)

M3 is accepted as delivered, and everything above is now integrated: the
EvenBlocks ledger is the paper's Table 8, the per-phase query ledgers ground
Proposition 5.2 in `sos_learning.md` §5, and the branch-1 omega correction is
adopted as *normative* — spec §3.2 step 4 now states the `(x.r, y.r)` mint with
your `GF(aa)` non-convergence as the rationale, and the paper's Lemma 4.5
carries the same fix. The transcript did more than fill placeholders: it
overturned a paper prediction. The minimal teacher's first EvenBlocks
counterexample is `(ε, !a;a;a)`, shortlex-earlier than the hand-predicted
`(ε, a;a;!a)`, and the paper's §1/§3/§4.1 traces were rewritten to match
(loop chain, ω-column `(a, a)`, `!a;a` pulled out of `[a]`). Consequence for
you: the EvenBlocks run is now paper-anchored exactly as Even's is. A draft
probe for it sits uncommitted in the working tree,
`sosl/tests/sosl/evenblocks_conformance.py` (mirror of `even_conformance.py`,
built on `m3_ledgers.py`'s instrumentation): it asserts first cex
`(ε, !a;a;a)`, columns `(a, a)` / `(a, !a;a)` / `(ε, !a)` in that order,
splits 3→4→6→8, the 67/4/14/14 ledger, and byte-equality — and it ran green
once (2026-07-07). It is yours: review, adapt, and commit it as the M4.a
conformance lock (spec §8), or rewrite it if it does not fit your idioms.
One trace fact it established that this report's ledger did not state: the
EvenBlocks *day-one sweep is clean*, as on Even — the counterexample is
genuinely the run's first event. Any drift on this run is henceforth a paper
regression, not a free choice.

Two notes for the record. First, one slip in this report: the
even-conformance paragraph says a different scan order "would produce the
omega column `(a, ε)`" — under your own branch-1 omega correction it would be
`(a, a)`; the spec's gate text now says `(a, a)`, nothing to fix beyond
awareness. Second, the EvenBlocks signature matrix now in the paper (7 keys ×
4 ω-columns) was derived *by hand* from your ledger and cross-checked against
the split sequence; have the E4 renderer emit the final signature matrix so
that table becomes machine-generated like everything else — it is a natural
extension of `m3_ledgers.py`.

For M4, work from the revised spec (revision 2026-07-07b): §6 has the corpus
manifest and per-experiment design notes, §7 three new stats fields
(`n_classes_initial`, `stall_class`, `cex_policy`), §8 the ordered sub-gates
M4.a–M4.d, §9 the new rows P5/F6/F7. Two scheduling points worth
internalizing before you start. Build the driver by promoting
`genaut_census.py` and `m3_ledgers.py`, not from scratch — M4.a is mostly
plumbing you already have. And treat the ROLL leg as the schedule risk it is:
its equivalence queries carry automata, not Cayley forms, so the exact oracle
does not apply — answer them bounded, record the certification asymmetry as a
result (row F6), and if the integration fights back, deliver the wrapper plus
a blocking record and keep moving; M4.d does not wait for it. The place new
science can fall out is E2: with saturation off and `--eq-mode exact`, every
*surviving* stall is a proven-permanent specimen — the census found the two
smallest, and anything new at larger shapes is a first-class exhibit for the
paper. Report those individually, with both fixpoints and the separating left
context, before aggregating anything.

---

## M4.a — Driver + E0 (2026-07-08)

_Reproduce (from `sosl/`):_ `python3 -m tests.sosl.campaign_e0` — the campaign is
its own gate, so a nonzero exit *is* the failure report. Committed record:
`reference/campaigns/e0/{results.csv, e0_report.md, e4_transcripts.md}`
(manifest: `reference/campaigns/README.md`, generated). The tables below are analysis
read off that `results.csv`. The named cases do not depend on the corpus, so a re-run
*is* a reproduction.

The `sosl.experiment` package (previously a README stub) is built by promoting
the two M3 prototypes into the campaign layer, as spec §8 M4.a directed:

    stats.py     RunStats (spec §7 verbatim, incl. n_classes_initial /
                 stall_class / cex_policy) -> stats.json + CSV
    run.py       Config + run_case: one instrumented run -> stats + split
                 ledger + signature matrix; per-case wall-clock budget;
                 crash-isolated (a fault becomes a recorded verdict)
    manifest.py  versioned corpus (m4a-2026-07-08): the triptych + the two
                 permanent specimens + a T1 alternate presentation; the census
                 tier (genaut/corpus/) is guarded/deferred (curated elsewhere)
    driver.py    manifest x config matrix -> one stats.json per run +
                 results.csv; one case never kills the campaign
    report.py    the E0 one-pager (with a PASS/FAIL gate) and the E4
                 ledger / signature-matrix renderers

`run_case` reuses the learner procedures unchanged behind a phase-tagged,
counting `member` wrapper, so its per-run metrics are the same numbers the M3
ledgers reported — the row-P5 stability lock (`tests/sosl/campaign_e0.py`)
asserts the Even (`32/4/7/8`) and EvenBlocks (`67/4/14/14`) ledgers byte-stable
against the M3 baselines above.

**E0 gate: PASS.** Ten runs over the named cases; zero MISMATCH, zero BUDGET.
The default config is SOUND on every case; the permanent specimens certify
`ACCEPTOR_ONLY` under `--no-saturation --eq-mode exact` (spec §9 P4/F5) and
reach canonical under saturation+exact.

| case | config | ref | init | learned | member (f/h/s/p) | eq | cex | sat | cert | stall | verdict |
|---|---|--:|--:|--:|--:|--:|--:|--:|---|---|---|
| gf_aa_parity | default | 6 | 3 | 6 | 74 (51/4/9/10) | 2 | 1 | 2 | bounded:8 | n/a | SOUND |
| gf_aa_reset | default | 6 | 3 | 6 | 74 (51/4/9/10) | 2 | 1 | 2 | bounded:8 | n/a | SOUND |
| even | default | 5 | 3 | 5 | 51 (32/4/7/8) | 2 | 1 | 1 | bounded:8 | n/a | SOUND |
| evenblocks | default | 8 | 3 | 8 | 99 (67/4/14/14) | 2 | 1 | 2 | bounded:8 | n/a | SOUND |
| a_implies_xa | default | 5 | 4 | 5 | 43 (32/0/2/9) | 1 | 0 | 1 | bounded:8 | n/a | SOUND |
| a_once | default | 4 | 2 | 4 | 35 (26/3/2/4) | 2 | 1 | 1 | bounded:8 | n/a | SOUND |
| a_implies_xa | no-sat-exact | 5 | 4 | 4 | 21 (17/0/0/4) | 1 | 0 | 0 | exact | permanent | ACCEPTOR_ONLY |
| a_implies_xa | exact | 5 | 4 | 5 | 43 (32/0/2/9) | 1 | 0 | 1 | exact | n/a | SOUND |
| a_once | no-sat-exact | 4 | 2 | 3 | 18 (13/3/0/2) | 2 | 1 | 0 | exact | permanent | ACCEPTOR_ONLY |
| a_once | exact | 4 | 2 | 4 | 35 (26/3/2/4) | 2 | 1 | 1 | exact | n/a | SOUND |

The two T1 presentations (`gf_aa_parity`, `gf_aa_reset`) produce identical
ledgers and signature matrices — a presentation-independence witness the driver
gets for free. The E4 renderer now machine-generates the signature matrix (class
keys x discovered columns), the companion to the paper's Tables 6/8 that was
previously hand-derived; the committed artifacts are
`reference/campaigns/e0/` (`results.csv`, `e0_report.md`, `e4_transcripts.md`).

The census tier is intentionally not wired: `genaut/corpus/` is being curated
separately, so E0 runs the named cases alone. E1's scaling scatter and E2's
broad permanent-stall hunt (M4.b) fold the census back in through
`manifest.census_cases` once it is ready.

---

## Theory-thread feedback — M4.a accepted, one blocker before E2 (2026-07-08)

M4.a is accepted. The E0 gate PASS, the row-P5 byte-stability lock, and the
machine-generated signature matrix (which retires our last hand-derived table)
are exactly what M4.a asked for. Two E0 facts are already integrated into the
paper, `sos_learning.md` §6 (they are landed campaign data, not predictions,
so they belong there now): the E0 named-case gate in §6.1, and — the result we
value most — `a_implies_xa` reaching its canonical five-class algebra under
saturation with **zero counterexamples and a single equivalence query**, in
§6.3. That row is the cleanest exhibit in the whole campaign of what
saturation buys: on the flagship permanent-stall language the sweep alone
produces the algebra and the oracle merely rubber-stamps it — the ablation's
difference is the algebra itself, not a query count. Keep that run
paper-anchored; any drift on it is a paper regression. The presentation-
independence freebie (`gf_aa_parity` and `gf_aa_reset` returning byte-identical
ledgers and signature matrices) is also now in §6.1 as a learner-side witness
of Theorem 5.1's canonicity — a genuine metamorphic check you got for free;
please keep it wired as an assertion in the E0 lock.

**One blocker before E2 — the `stall_class` labels are a category error on the
saturated rows, and E2's whole deliverable rides on this field.** The E0 table
labels both proven-permanent specimens `transient` on their saturation-on rows
(`a_implies_xa` default and exact; `a_once` default and exact). By the spec's
*own* §6 definition, `transient` means "a pre-equivalence fixpoint was
non-canonical **but a counterexample broke it**." On `a_implies_xa` default the
count is `cex 0` — the 4→5 split came from the **sweep**, not a counterexample —
so the run satisfies neither `transient` (no counterexample), nor `none` (the
first fixpoint was non-canonical, 4≠5), nor `permanent` (it did reach
canonical). It falls outside the trichotomy, which was written for the
ablation (saturation-off) leg only; the driver defaulted it to `transient`, and
that word now sits on the paper's flagship *permanent* stall.

This is harmless in E0 (the verdicts are all correct; only the label is wrong)
but it is *not* harmless in E2: E2's headline is the stall-frequency table, and
the paper (§6.3) pins `a → Xa` and `a ∧ XG¬a` as **permanent**. If
`stall_class` is aggregated per-run across configs, those two land `transient`
in half their rows and the frequency table contradicts the theorem. The fix is
a definition, not driver guesswork — we are tightening it in the spec (see the
§6/§7 revision landing with this note):

- `stall_class` is a **per-language** property, determined **solely by the
  no-saturation + exact leg** — `permanent` if that leg certifies a
  non-canonical fixpoint, else `transient` if a non-canonical fixpoint was
  observed before a counterexample broke it, else `none`.
- On any **saturation-on** run, `stall_class` is reported as `n/a` (never
  `transient`, never `permanent`) — a saturated run resolves the stall by the
  sweep, which the trichotomy does not name, so it must not carry a class.
- E2's per-language classification reads the ablation-leg row only; the driver
  must not fold saturated-run labels into the frequency counts.

Concretely for the E0 table: the four saturated-run `stall` cells for the two
specimens should read `n/a`, and the two `no-sat-exact` rows keep `permanent`.
Regenerate that column under the tightened rule before E2 aggregates anything —
otherwise the first thing E2 produces will disagree with Proposition 4.4.

For M4.b, the E2 leg is where new science can appear, exactly as before: with
saturation off and `--eq-mode exact`, every *surviving* stall is a
proven-permanent specimen. The named-case census found the two smallest; fold
in `genaut/corpus/` (E1/E2), and any new permanent stall at a larger shape is a
first-class exhibit — report it individually with both fixpoints and the
separating left context before it enters any aggregate.

---

## M4.b — E1 scaling + E2 ablation (2026-07-08)

_Reproduce (from `sosl/`):_ `python3 -m tests.sosl.campaign_m4b` — its own gate.
Committed record: `reference/campaigns/m4b/{results.csv, e1_report.md, e2_report.md}`
(manifest: `reference/campaigns/README.md`, generated). The two tables below are read
off that `results.csv`.

Both experiments run over the named cases through the driver
(`tests/sosl/campaign_m4b.py`); the census tier stays deferred, so E1's scatter
plots and E2's broad specimen hunt fold in later via `manifest.census_cases`.

**E1 — scaling.** The default-config run metrics against the reference class
count `N`, with the designed bounds overlaid (`splits ≤ N`; table/fill membership
`~ O(N²·|Σ|)`). `splits ≤ N` holds on every case, and the fill count stays inside
the `N²·|Σ|` envelope; harvest and saturation add the counterexample-analysis
term on top.

| case | N | \|Σ\| | init | splits | fill | N²·\|Σ\| | member | eq |
|---|--:|--:|--:|--:|--:|--:|--:|--:|
| a_once | 4 | 2 | 2 | 2 | 26 | 32 | 35 | 2 |
| a_implies_xa | 5 | 2 | 4 | 1 | 32 | 50 | 43 | 1 |
| even | 5 | 2 | 3 | 2 | 32 | 50 | 51 | 2 |
| gf_aa_parity | 6 | 2 | 3 | 3 | 51 | 72 | 74 | 2 |
| gf_aa_reset | 6 | 2 | 3 | 3 | 51 | 72 | 74 | 2 |
| evenblocks | 8 | 2 | 3 | 5 | 67 | 128 | 99 | 2 |

The named cases give only `N ∈ {4,5,6,8}`; the scatter plots wait on the census
N-spread (the generator already emits the per-metric columns they consume).

**E2 — saturation ablation.** Every named case under both `default` (saturation
on) and the ablation leg `--no-saturation --eq-mode exact` (with exact
equivalence every *surviving* stall is provably permanent). The ablation-leg
stall class matches theory on all six cases:

| case | prefix-indep | ref | no-sat learned | stall class | expected |
|---|:--:|--:|--:|---|---|
| a_implies_xa | no | 5 | 4 | permanent | permanent |
| a_once | no | 4 | 3 | permanent | permanent |
| even | no | 5 | 5 | transient | transient |
| evenblocks | yes | 8 | 8 | transient | transient |
| gf_aa_parity | no | 6 | 6 | transient | transient |
| gf_aa_reset | no | 6 | 6 | transient | transient |

Stall-class frequency: permanent 2 · transient 4. No new permanent specimen
among the named cases — as expected; the census tier is where new ones surface.

The report renders each permanent specimen as a first-class exhibit
(`e2_report`): the coarse (certified non-canonical) `.sos`, the canonical `.sos`,
and the **separating left context** — the saturation escalation invisible to
lasso membership from the start. `a_once` merges `[!a;a]` into `[!a]`, split by
the left prefix `a` (`a·[]·!a`); `a_implies_xa` merges `[a;a]` into `[!a]`,
reaching its 5-vs-4 gap with zero counterexamples and one escalation
(`a·([]·a)^ω`). Committed artifacts: `reference/campaigns/m4b/`
(`results.csv`, `e1_report.md`, `e2_report.md`).

---

## Census-backed E2 — permanent stalls at the LTL frontier (2026-07-08)

With the census tier wired (`manifest.census_shapes`, precomputed `corpus/sos/`
references), the ablation hunt runs over the exhaustive `2state1ap1acc` and its
parity twin `2state1ap1acc_parity` — the smallest shapes where non-LTL languages
appear (SHAPES.md: "not-LTL first appears at `2state1ap0acc`; the LTL frontier is
n ≥ 2 ∧ k ≥ 1"). 258 languages, two configs, `tests/sosl/census_campaign.py`.

_Reproduce (from `sosl/`):_ the harvest —
`python3 -m tests.sosl.census_campaign 2state1ap1acc 2state1ap1acc_parity`; the
exhibits + structural buckets — `python3 -m tests.sosl.census_e2_exhibits
2state1ap1acc` → `tests/sosl/logs/census_e2/{2state1ap1acc_runs/results.csv,
2state1ap1acc.md}`. The figures below are read off those runs.

**Soundness across the frontier.** Default config (saturation on) is **SOUND on
all 258** — byte-equal to the precomputed reference, zero MISMATCH. The learner
is correct on the entire exhaustive shape (spec §9 P2/P3 at scale).

**The permanent-stall harvest.** Under `--no-saturation --eq-mode exact`, **44
distinct languages** (88 gba+parity presentations, every one exact-certified)
sit on a permanent stall — a non-canonical right-congruence fixpoint no
counterexample breaks. Saturation recovers the canonical algebra for every one
of them (which is why default is 258/258 SOUND). This exhaustively enumerates
*all* permanent-stall languages at this shape — the two named specimens
`a_once` (ref 4) and `a_implies_xa` (ref 5) are no longer isolated exhibits but
the smallest members of a populated family.

Gap (reference − stalled) distribution over the 88 runs:

| gap | 1 | 2 | 3 | 4 | 5 |
|---|--:|--:|--:|--:|--:|
| runs | 52 | 16 | 6 | 10 | 4 |

The sharpest exhibits reach gap 5 (`ref 13 → learned 8`, `ref 15 → learned 10`),
far past the minimal `a_implies_xa` (gap 1): the right congruence can fall many
classes short of the syntactic one, all recovered by the left-context sweep.
**Exhibits delivered.** `tests/sosl/census_e2_exhibits.py` deduplicates the
permanent runs to the 44 distinct languages and renders the sharpest as
first-class exhibits (`logs/census_e2/<shape>.md`): for each, the coarse
(certified non-canonical) `.sos`, the canonical `.sos`, and the separating left
context (the saturation escalations, with their splits and minted columns). Gap
distribution over the 44 **distinct languages**:

| gap | 1 | 2 | 3 | 4 | 5 |
|---|--:|--:|--:|--:|--:|
| languages | 26 | 8 | 3 | 5 | 2 |

The two gap-5 specimens are the headline: `2state1ap1acc_06496`
(`ref 13 → stall 8`, recovered by 1 counterexample and **5** saturation
escalations — three branch-1, two frozen-chain) and `2state1ap1acc_19552`
(`ref 15 → stall 10`). The beyond-wall shapes are reached by reproducible
sampling (`genaut/gen/sample.py`), not exhaustive enumeration.

**Structural cross-tabulation (closes the §6.3 TBD).** The renderer now buckets
the 44 by prefix-independence (exact, from the invariant: acceptance invariant
under left-multiplication of `s`) and acceptance type (from the canonical `D`).
The result is uniform and telling: **all 44 are prefix-*dependent* (0 of 44
prefix-independent) and all Büchi-acceptance**. That is the structural signature
of a permanent stall — the class the right congruence merges is separated only
by a left context, so the language must be prefix-dependent; a prefix-independent
language (like `EvenBlocks`, whose stall is *transient*) never lands here. The
predicate is validated against known languages
(`tests/sosl/prefix_independence_check.py`: `GF(aa)`, `EvenBlocks`
prefix-independent; `Even`, `a_once`, `a_implies_xa` not).

---

## M4 — E5 counterexample sensitivity (2026-07-08)

_Reproduce (from `sosl/`):_ `python3 -m tests.sosl.campaign_e5` — its own gate.
Committed record: `reference/campaigns/e5/{results.csv, e5_report.md}` (manifest:
`reference/campaigns/README.md`, generated). The table below is read off that
`results.csv`.

The teacher grows a `--cex-policy minimal|first|padded:<k>` hook
(`sosl/sosl/teacher/whitebox.py`). `minimal` is the oracle's shortlex-least
counterexample (both the bounded and exact oracles enumerate in minimal order,
so no separate minimization pass exists). `first` is a recorded **coincidence**:
first-found *is* minimal for these oracles, so it reproduces `minimal` exactly.
`padded:<k>` pumps the minimal counterexample by k — `(u, v) -> (u·v^(k-1), v^k)`,
the same ω-word — and is used only if the pumped lasso is still a genuine
hypothesis/teacher disagreement (never violate spec §9 F3).

Over the counterexample-bearing named cases (`tests/sosl/campaign_e5.py`), with
the loop length driven from 3 up to 96 by `padded:2..32`, the **harvest** term
(the counterexample-analysis membership queries) grows by exactly **+1 per
doubling** of the counterexample length — i.e. `harvest ≈ log₂|cex|`, the binary
search over the stem/loop chain — while the learned invariant is unchanged (every
run SOUND, same class count):

| padded k | 1 (min) | 2 | 4 | 8 | 16 | 32 |
|---|--:|--:|--:|--:|--:|--:|
| loop length | 3 | 6 | 12 | 24 | 48 | 96 |
| harvest (gf_aa / even / evenblocks) | 4 | 5 | 6 | 7 | 8 | 9 |

This is the design's logarithmic counterexample term, confirmed empirically:
padding changes only the query cost, never the outcome. Artifacts under
`reference/campaigns/e5/` (`results.csv`, `e5_report.md`).

---

## Theory-thread feedback — M4.b + census-E2 + E5 accepted (2026-07-08)

Accepted, and integrated into `sos_learning.md` §6 this round. The three drops
are clean and the numbers cross-check, so this is mostly a "banked" note with
one small ask and the paper deltas recorded.

**The stall_class fix took.** E2's table now reads the class off the
`no-sat learned` (ablation) leg — `permanent 2 / transient 4`, matching theory
— and the saturated runs no longer carry a spurious `transient`. That closes
the M4.a blocker (spec §7, row P6); nothing further owed there.

**Census-backed E2 is the round's real result, and it is now the paper's.**
258 languages exhaustively, byte-exact on all 258 under saturation, and 44
distinct permanent-stall languages under ablation — the two §4.2 specimens
revealed as the two smallest of a populated family, with the right-vs-syntactic
gap reaching 5 (`ref 13 → 8`, `ref 15 → 10`). We checked the internal
consistency (88 = 44×2, every gap bucket exactly doubled) and it holds. This
upgrades the paper's §4.2 argument from a two-example finding to a generic one:
`sos_learning.md` §6.3 now carries the census family and its gap distribution,
resolving the old `⟨TBD-M4: the list … or the statement that none exists⟩` in
the strong direction, and the abstract/§6.1/§8 headlines now cite the 258/44
result. Keep the `census_e2_exhibits` renderer and the two gap-5 headliners
(`2state1ap1acc_06496`, `_19552`) stable — they are paper-anchored now.

**E1 bounds and E5 log-term** both land in the paper as confirmations, not
predictions: §6.2 states `splits ≤ N` and fill inside `N²·|Σ|` on every named
case; §6.5 states the harvest term at `≈ log₂ ℓ` (+1 per doubling), with the
honest note that `first` coincides with `minimal` for these minimal-order
oracles, so E5 is two series, not three — the paper now says so rather than
implying three distinct policies.

**One small ask, to close the last §6.3 TBD.** The frequency table "stall class
against structural features (prefix-independence, acceptance type, `N`)" is
still open on the paper side — the census-E2 exhibits have the per-language
fixpoints but not that cross-tabulation. If the E2 renderer can emit the 44
permanent languages bucketed by prefix-independence and acceptance shape (even
just counts), that TBD closes too; it is a natural column on `e2_report`.

**Two housekeeping notes.** The milestone bullet at the top of this report
(§"Milestones") still reads "M4.a done … M4.b–M4.d next" — stale now that
M4.b, the census E2, and E5 have all landed; worth a one-line refresh. And the
remaining campaign legs the paper is still waiting on are **E3 (ROLL baseline,
M4.c)** and the **full-census N-spread** that E1's scatter needs — those two
keep the last handful of `⟨TBD-M4⟩` markers open; everything else in §6 is now
filled.

---

## M4.c — E3 ROLL FDFA baseline (2026-07-08)

ROLL (`~/git/roll-library`, built from source) learns the language of a target
Büchi automaton, so the baseline (`sosl/sosl/experiment/baseline.py`) feeds it a
**state-based** Büchi presentation of each census language (Spot, `SBAcc` — a
transition-based Büchi is misread by ROLL as a trivial language) and runs its
three canonical FDFA learners, harvesting `#MQ`/`#EQ` and the FDFA size (leading
+ progress DFA states) from ROLL's own `Statistics`.

_Reproduce (from `sosl/`):_ `python3 -m tests.sosl.campaign_e3` →
`tests/sosl/logs/e3/e3_report.md`. Named-case paired table (read off that run):

| case | ours N (MQ/EQ) | ROLL periodic | ROLL syntactic | ROLL recurrent |
|---|---|--:|--:|--:|
| gf_aa_parity | 6 (74/2) | 4 (20/2) | 4 (20/2) | 4 (20/2) |
| even | 5 (51/2) | 12 (79/5) | 15 (112/5) | 9 (92/5) |
| evenblocks | 8 (99/2) | 8 (74/4) | 8 (74/4) | 8 (74/4) |
| a_implies_xa | 5 (43/1) | 12 (64/4) | 14 (145/7) | 9 (128/7) |
| a_once | 4 (35/2) | 8 (52/4) | 10 (75/4) | 7 (63/4) |

The size comparison is a **wash, not a win**: every entry sits inside
Proposition 5.3(a)'s `N + N²` envelope, and within it the two objects **trade
places** — the algebra is smaller on `even` (5 vs 9–15), `a_implies_xa`
(5 vs 9–14) and `a_once` (4 vs 7–10), **larger** on `gf_aa` (6 vs 4), and tied on
`evenblocks` (8). We do **not** claim "the algebra is smaller" — the census is
too small to reach the 5.3(b) separation, and that claim would contradict it.
**The real result is the capability column:** only our invariant answers "is `L`
LTL-definable" (the aperiodicity / group test on the algebra); none of ROLL's
three FDFAs can — that asymmetry, not any size or query count, is the point.
**Certification (F6):** both learners certify *exactly*, by different mechanisms
— ours the Cayley transformation-closure product, ROLL's native RABIT against a
state-based Büchi presentation; the asymmetry is mechanism, not level.

**Census-wide medians.** Reproduce:

```
cd sosl && python3 -m tests.sosl.census_e3 2state1ap1acc
```

Data: one row per language in `tests/sosl/logs/census_e3/results.csv`
(`our_N`, and each mode's `fdfa`/`MQ`/`EQ`); the summary in
`logs/census_e3/2state1ap1acc.md`. Read off those 129 rows: median class count
`N = 8` against ROLL FDFA-size medians 10 / 12 / 8 (periodic / syntactic /
recurrent). Against ROLL's *smallest* FDFA per language, the algebra is smaller
on 66, larger on 42, tied on 21 of 129 — the wash confirmed at scale, the objects
trading places inside the `N+N²` envelope. The capability asymmetry, not size,
remains the result.

---

## Theory-thread feedback — E3/ROLL accepted, RABIT is the right call (2026-07-08)

Accepted, and integrated into `sos_learning.md` §6.4. One design point to log,
because it departs from the spec-as-written and we are *ratifying* the
departure rather than asking you to undo it. The original E3 design note (spec
§6) had ROLL's equivalence answered by *our* teacher's bounded product
enumeration, with the certification asymmetry "ours exact / ROLL bounded"
reported as F6. You instead let ROLL certify by its **native RABIT** oracle
against a state-based Büchi presentation. That is the fairer baseline — ROLL
runs at full strength, and both learners now certify *exactly*, by different
mechanisms — so we adopt it: spec §6 E3 design note and row F6 are rewritten to
"exact by different oracles, asymmetry is mechanism not certification level"
(revision 2026-07-08c), and §6.4 says the same.

Two things we held the paper to, so the numbers are not over-read. First, the
state-based-Büchi feed (Spot `SBAcc`) makes ROLL's *membership* counts
presentation-sensitive — the paper compares on **output size and capability**,
not raw MQ. Second, and firmly: the size table is a **wash, not a win**. Every
entry is inside Proposition 5.3(a)'s `N + N²` envelope, and within it the
objects trade places (algebra smaller on Even / a→Xa / a∧XG¬a, larger on
GF(aa), tied on EvenBlocks). The paper must **not** — and does not — say "the
algebra is smaller"; that contradicts 5.3(b), where the algebra is
*exponentially larger* than a smallest acceptor. The census is simply too small
to reach that separation. The real result of E3 is the **capability column**:
LTL-definability is a read-off from our invariant and unanswerable from any of
ROLL's three FDFAs — that asymmetry, not any query or size count, is the point,
and it matches §6.4's framing exactly.

Remaining for M4 close: the census-wide ROLL medians (this table over the full
census, not just the named cases) and the full-census N-spread that E1's
scatter needs. Those are the last `⟨TBD-M4⟩` markers open in the paper.

---

## Theory-thread feedback — E2 buckets accepted, one over-claim trimmed (2026-07-08)

The structural cross-tabulation is exactly what closes the §6.3 frequency-table
TBD, and it is now in the paper — but with one framing change you should know
about, because we are *weakening* a claim your commit message and report make.

**Accepted as data.** 44/44 permanent census languages prefix-dependent, 0/44
prefix-independent, all Büchi — folded into §6.3. The `prefix_independence_check`
validation (`GF(aa)`, `EvenBlocks` independent; `Even`, `a_once`, `a_implies_xa`
not) is a good predicate to keep.

**Trimmed: "all Büchi" is not a signature.** At `2state1ap1acc` there is a
*single* acceptance set, so every language at the shape is Büchi (or co-Büchi) by
construction — the uniformity is the shape, not a property of permanence. The
paper says so and does not read into it; please don't headline it either.

**Trimmed, and this is the real one: "the language must be prefix-dependent" is
not established.** The report states permanence *implies* prefix-dependence as
though it were a theorem ("so the language must be prefix-dependent"). We do not
have that, and the natural argument does not close. The argument would be:
prefix-independence removes the left context, and permanent stalls are exactly
the left-context separations, so a prefix-independent language cannot stall
permanently. The hole: prefix-independence removes the left context only in the
*linear* shape (Prop 4.6). In the *ω-power* shape a left factor sits *inside the
loop*, where it is a **rotation**, not a deletable prefix — this is the paper's
own rotation lemma (§2.2), and it is precisely why `EvenBlocks`, prefix-
independent, still requires the sweep's rotation to reach its 8 classes. So a
prefix-independent language does face genuine left contexts, and "no left
context ⇒ no permanent stall" is invalid as stated.

So we integrated 44/44 as a **census regularity at the smallest shape**, with
the mechanism as *intuition*, and explicitly left open whether a
prefix-independent language can stall permanently. The way to settle it is
empirical first: run the same cross-tabulation at the **deeper census shapes**
(more states / acceptance sets, where prefix-independent non-LTL languages are
richer). If prefix-dependence still holds 100% there, it becomes worth a proof
attempt; a single prefix-independent permanent stall refutes the necessity
outright. That deeper-shape cross-tab is the ask — it is the same renderer you
just built, pointed at a bigger manifest.

---

## Census-backed E1 — cost vs N (2026-07-08)

_Reproduce (from `sosl/`):_ `python3 -m tests.sosl.census_e1
../reference/census/sweep_results.csv` → `reference/census/e1_summary.md` (the full
per-N table; the committed sweep CSV is the source, and it is the record — the corpus
grows, so a re-run is not a reproduction of an earlier drop).

The learner runs (default leg) over the **whole catalogue — 6222 languages,
`N ∈ [2, 208]`, every one SOUND** (byte-equal to the precomputed reference).
Soundness holds across the entire frontier, not merely the named cases, and not
merely the small shapes: there is no non-SOUND row anywhere on the default leg.

The designed bound **`splits ≤ N` holds on all 6222** (0 violations); the sharpest
observed is `N = 10` with 8 splits. Table membership (`fill`) tracks the
`O(N²·|Σ|)` envelope, and equivalence queries stay in the low single digits across
the whole `N` range — the shape the E1 scatter plots consume.

The per-N medians are not reproduced here: they are a generated artifact
(`reference/census/e1_summary.md`), regenerated by the command above.

---

## Theory-thread feedback — census-wide E3 + E1 in; 541 is the headline (2026-07-08)

Both landed and both integrated (`sos_learning.md` §6.2, §6.4). The census-wide
E3 medians confirm the size wash at scale (median `N = 8` vs FDFA 10/12/8;
66 smaller / 42 larger / 21 tied), and the E1 census closes the last scatter
TBD: 541 languages, `N ∈ [2, 21]`, `splits ≤ N` on all 541, membership inside
the `N²·|Σ|` envelope. The paper's §6.2 now carries the per-N median growth.

**The 541-language census is now the paper's headline number, replacing 258.**
The earlier count ambiguity (258 vs 129 vs 44/88) is resolved by promoting the
*whole* census — 541 languages, all SOUND — to the top-line claim, and scoping
the smaller numbers precisely: 129 = the `2state1ap1acc` shape (E3 size, and the
permanence hunt), 44 = the permanent-stall family at that shape. Abstract, §6.1,
§6.2, §6.3, §6.4, §8 are all consistent on this now, and "258" no longer appears.
One point to confirm so we don't misstate the frontier: we read `2state1ap1acc`
as **129 distinct languages** (your E3 "one row per language"), with the parity
twin a second acceptance encoding rather than 129 new languages. If the twin
does contribute distinct languages, tell us and we adjust §6.3/§6.4.

**Two asks to close the last paper TBDs.** (1) §6.4 capability column: the
LTL-definability read-off must be checked against ground truth on the census —
the count of agreements (should be 541/541). That is the *result* of the Q3
comparison and the one capability number still marked `⟨TBD-M4⟩`. (2) A wall-time
note for §6.2 (census completes in … at most). Both are one line off runs you
already have.

**Still the standing science ask** (unchanged): the permanence cross-tabulation
at deeper shapes — whether prefix-dependence stays 100% of permanent stalls past
`2state1ap1acc`, or a prefix-independent permanent stall appears and refutes the
necessity. That is the one open question the paper flags rather than answers.

---

## Flat-canon census rerun (2026-07-08) — PRELIMINARY

> **Status: preliminary.** The whole campaign is re-run over the new benchmark,
> the flat, complement-closed catalogue `genaut/corpus/flat_canon` (**3938**
> languages up to AP relabeling — one representative per language, dual included;
> `corpus/flat_canon/STUDY.md`), which supersedes the old per-shape census (541
> languages, the `2state1ap1acc` frontier). This replaces the census-backed E1 /
> E2 / E3 sections above; the named-case sections (E0, M4a/b named tables, E5)
> are `samples/`-driven and unchanged. **Figures below are read off a partial
> sweep of `2492 / 3938` languages** — every shape complete *except*
> `3state1ap0acc` (≈46% done), which supplies the large-`N`, high-gap tail — so
> the counts grow and the extreme tail lengthens, but the structure and the
> qualitative results are settled. Final values land when the sweep completes.

The census procedures are refactored to the genaut pattern — a **streaming
sweep** that produces raw per-run data, and **a-posteriori analyzers** that
compute the study from it. Everything is ventilated by the **SoS category** (the
`.cat` sidecar: the LTL-definability cut and the Wagner degree `ϕ = (γ, s)`, read
off the syntactic invariant 𝓘(L)).

_Reproduce (from `sosl/`):_

```
python3 -m tests.sosl.census_campaign --budget 30   # stream results.csv (both legs)
python3 -m tests.sosl.census_e1                     # E1 soundness + cost + SoS cut
python3 -m tests.sosl.census_e2_exhibits            # E2 permanent-stall family
python3 -m tests.sosl.census_e3                     # E3 ROLL baseline (+ --summary-only)
```

### E1 — soundness and cost across the whole catalogue

Default config (saturation on) is **SOUND on all 2492** languages swept so far —
byte-equal to the precomputed reference, zero MISMATCH — across `N ∈ [2, 121]`
(the old census reached `N = 21`). The designed **`splits ≤ N` holds on every
one**; the sharpest so far is `N = 121` with 118 splits. Per-`N` cost medians (a
representative ladder; full table in `logs/census_e1/summary.md`):

| N | languages | median splits | max splits | median fill | median member | median equiv |
|--:|--:|--:|--:|--:|--:|--:|
| 2 | 2 | 0 | 0 | 2 | 3 | 1 |
| 4 | 500 | 0 | 2 | 145 | 151 | 1 |
| 8 | 105 | 5 | 6 | 84 | 104 | 2 |
| 13 | 104 | 10 | 11 | 188 | 248 | 2 |
| 21 | 56 | 18 | 18 | 429 | 514 | 2 |
| 32 | 42 | 28 | 29 | 714 | 883 | 2 |
| 50 | 44 | 47 | 47 | 1716 | 2028 | 2 |
| 72 | 9 | 69 | 69 | 2609 | 3028 | 2 |
| 97 | 14 | 93 | 94 | 4094 | 4665 | 1 |
| 121 | 6 | 118 | 118 | 4859 | 5696 | 2 |

Fill tracks the `O(N²·|Σ|)` envelope; equivalence queries stay in the single
digits (1–4) across the entire range, including `N = 121`.

Two reading notes on this table. **The per-`N` fill mixes alphabet sizes**, so a
row must be read against `N²·|Σ|` with *that bucket's* `|Σ|`, not `|Σ| = 2`. The
low-`N` buckets are dominated by `k = 3` languages (the `1state3ap1acc` shape):
the `N = 4` bucket, 500 languages, is 396× `k = 3` (`|Σ| = 8`) with median fill
145 ≈ `N²·|Σ| = 128`, only 42× `k = 1` (median fill 17 vs 32) — the aggregate 145
is envelope-consistent once split by `|Σ|`, not an anomaly. **Convention:** the
class count is `N = |S(L)₊¹|` (the syntactic ω-semigroup with adjoined identity);
the two `N = 2` languages are exactly `∅` and `Σ^ω`, as that identity demands.

**Ventilation by the LTL cut.** Soundness is uniform, but cost is not — the
non-LTL (genuinely ω-counting) languages are the expensive half:

| definability | languages | SOUND | median N | median splits | median member |
|---|--:|--:|--:|--:|--:|
| LTL (aperiodic) | 1486 | 1486 | 7 | 4 | 151 |
| non-LTL | 1006 | 1006 | 17 | 13 | 349 |

**Ventilation by Wagner degree** (duality-symmetric, as the catalogue is
complement-closed — every `σ` row matches its `π` dual):

| ϕ = (γ, s) | class | languages | SOUND | median N | median splits |
|---|---|--:|--:|--:|--:|
| (0, σ) / (0, π) | empty / universal — trivial | 1 / 1 | ✓ | 2 | 0 |
| (1, δ) | clopen — properly Δ₁ | 27 | ✓ | 8 | 4 |
| (1, σ) / (1, π) | guarantee / safety | 650 / 651 | ✓ | 19 | 16 |
| (2, σ) / (2, π) | properly Σ₂ / Π₂ | 4 / 4 | ✓ | 5 | 2 |
| (ω, σ) / (ω, π) | Gδ / Fσ — DBA/DCA-proper | 466 / 466 | ✓ | 4 | 0 |
| (ω·2, σ) / (ω·2, π) | one Rabin pair | 12 / 12 | ✓ | 15 | 10 |
| (ω², σ) / (ω², π) | parity / co-parity {0,1,2} | 99 / 99 | ✓ | 13 | 10 |

### E2 — the permanent-stall family, exploded

Under the ablation leg (`--no-saturation --eq-mode exact`, every surviving stall
provably permanent), the partial sweep already surfaces **1180 distinct
permanent-stall languages** — the old single-shape census found **44**. The
right-vs-syntactic **gap reaches 53** (`ref 68 → stall 15`,
`3state1ap0acc_015752`, recovered by 3 counterexamples and 12 saturation
escalations), an order of magnitude past the old maximum of 5. Gap distribution
(head; a long single-language tail runs out to 53):

| gap | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | … | 53 |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| languages | 274 | 205 | 183 | 126 | 82 | 50 | 58 | 44 | 24 | 10 | … | 2 |

Permanence **cuts across the LTL boundary**: **582 / 1180** of the permanent
stalls are LTL-definable, the rest non-LTL — the permanent stall is a property of
the right-vs-two-sided congruence gap, not of countability. By Wagner degree
(one row per side — every cell a per-side count, no σ/π folding):

| ϕ = (γ, s) | class | languages | prefix-indep | LTL | max gap |
|---|---|--:|--:|--:|--:|
| (1, δ) | clopen — properly Δ₁ | 23 | 0 | 23 | 5 |
| (1, σ) | properly open — guarantee | 440 | 0 | 220 | 53 |
| (1, π) | properly closed — safety | 441 | 0 | 221 | 53 |
| (ω, σ) | Gδ — DBA-proper | 91 | 0 | 44 | 13 |
| (ω, π) | Fσ — DCA-proper | 91 | 0 | 44 | 13 |
| (ω·2, σ) | one Rabin pair — σ | 10 | 0 | 0 | 4 |
| (ω·2, π) | one Rabin pair — π | 10 | 0 | 0 | 4 |
| (ω², σ) | parity {0,1,2} | 37 | **2** | 15 | 13 |
| (ω², π) | co-parity {0,1,2} | 37 | **2** | 15 | 13 |

(The `440/441` and `220/221` σ/π counts are partial-sweep artifacts — at
completion the dual-symmetry assertion requires each `σ` row to equal its `π`
row exactly.)

**Result — the prefix-dependence necessity conjecture is refuted (witness lock
passes).** The old census found permanence **100% prefix-dependent** (0/44), and
the paper left open whether a prefix-independent language can stall permanently —
a single one "refutes the necessity outright." The sweep finds **4 (2 languages
× their complements)**, both in the parity-`{0,1,2}` degree:

- `2state1ap2acc_parity_0088836118` — `ref 10 → stall 8`, gap 2 (parity {0,1,2})
- `2state1ap2acc_parity_1178851077` — `ref 16 → stall 14`, gap 2 (parity {0,1,2})

The **witness lock** (`tests/sosl/witness_lock.py`, spec item 7 / row P8) is a
build-stopping gate that (a) asserts prefix-independence on each witness's
**canonical** invariant (`(s,e) ∈ P ⟺ (c·s,e) ∈ P`, all `c`), and (b) asserts the
**ω-sort column signature** of Corollary 4.7(b): every column minted in the
saturated run is of the ω-sort — a single linear mint would convict the predicate
or the sweep, no third option. **It passes on all four**, and retroactively on
`GF(aa)` and `EvenBlocks`. This is consistent with the rotation lemma: a
prefix-independent language still faces a left factor *inside the loop*, as a
rotation — which is exactly why the separating columns are ω-power, not linear.

The saturation escalations that recover the merged classes — every minted column
`…^ω`, i.e. ω-sort, the visible P8 signature (full exhibits, both `.sos` +
complete ledger, in `sosl/tests/sosl/reference/witness_lock_exhibits.md`):

`_0088836118` — coarse 8 → canonical 10 (1 cex, 5 escalations):

| chain | split | minted column |
|---|---|---|
| branch1 | a → a, !a;a | !a·([]·!a)^ω |
| frozen | a → a, a;a | !a·([]·!a;!a)^ω |
| branch1 | !a → !a, !a;!a;a ; !a;a → !a;a, a;!a | a;!a;!a·([]·a;!a;!a)^ω |
| frozen | !a → !a, a;!a;!a | a·([]·!a;a)^ω |
| frozen | !a;a → !a;a, a;!a;!a;a | a·([]·!a;!a;a)^ω |

`_1178851077` — coarse 14 → canonical 16 (2 cex, 10 escalations); every minted
column likewise ω-sort (ledger in the exhibit file).

The two witnesses are *sampled*-tier (`2state1ap2acc_parity`); an
exhaustive-shape witness is the remaining ask (spec item 7d) so §6.3 can claim a
shape, not a sample.

### E3 — ROLL FDFA baseline (still a wash)

Over the **6222 languages** of the catalogue, median class count `N = 16` against
ROLL's FDFA-size medians 16 / 21 / 12 (periodic / syntactic / recurrent). Against
ROLL's *smallest* FDFA per language the algebra is smaller on **2032**, larger on
**3574**, tied on **354** (the comparison is over the 5960 languages where ROLL
returns a size for all three modes) — the size wash confirmed at full scale, the
objects trading places inside the `N + N²` envelope (Prop. 5.3(a)), not a win. The
**capability column** (LTL-definability, a read-off from our invariant, unanswerable
from any FDFA) remains the result. The size trade **correlates with the LTL cut**:

| definability | algebra smaller | larger | tied |
|---|--:|--:|--:|
| LTL (aperiodic) | 1524 | 1842 | 207 |
| non-LTL | 508 | 1732 | 147 |

**The full catalogue corrects an earlier reading of this table.** On the 2491-language
sweep the algebra came out *more often smaller* on LTL languages (862 vs 534), and the
report drew the line there. At 6222 that no longer holds: on LTL the algebra is
smaller 1524 and larger **1842** — more often the *larger* object, as it already was on
non-LTL. The direction that survives is the **correlation**, not the absolute claim:
the algebra's size disadvantage is much milder on LTL (smaller/larger ≈ 0.83) than on
non-LTL (≈ 0.29). The earlier headline was an artifact of the smaller corpus, whose
shapes were the small ones; the parity families v2 added are where the algebra pays.

The aggregate is unchanged, and it is the honest one: a **wash** inside the `N + N²`
envelope (Prop. 5.3(a)), never a size win. The **capability column** is the result —
LTL-definability is a read-off from our invariant and is unanswerable from any FDFA,
at any size.

### Reporting note — the `OVERSIZE` verdict

At the very top of the shape range (`ref 57 / 93`, `3state1ap0acc`) the **exact
oracle** cannot build its transformation closure within its 200 000-element work
cap and raises `ExactTooLarge` — an honest "too big to decide exactly", now
recorded as a distinct **`OVERSIZE`** verdict (not `MISMATCH`). It affects **only
the E2 ablation leg** of the few largest languages; the learner is **SOUND** on
every one under the default leg, so their E1/soundness result stands and only
their exact permanent-vs-transient classification is deferred. `MISMATCH` stays
reserved for a genuine byte mismatch (of which there are none).

---

## Theory-thread feedback — flat-canon rerun integrated; the conjecture is dead (2026-07-08)

The preliminary drop is accepted, and the paper is re-based on it now rather
than after the sweep (`sos_learning.md`, rev 2026-07-08b): abstract, §6.1,
§6.2, §6.3, §6.4 and §8 carry the flat_canon census — the 3938 catalogue,
byte-exact on all 2492 swept, `N` to 121, the 1180-strong permanent family,
gap to 53, and all three LTL-cut ventilations (cost §6.2, permanence §6.3,
the E3 size trade §6.4) — with ⟨TBD-M4⟩ markers exactly where the unfinished
`3state1ap0acc` sweep will move a figure. The 44-at-`2state1ap1acc` result
survives where exhaustiveness is the claim (§6.3); "541" no longer appears.
Your Wagner ventilation is used in the paper for one thing — locating the
prefix-independent witnesses — and otherwise stays report-side.

**The refutation is integrated as the finding, not as a flag.** The
necessity conjecture (permanent ⇒ prefix-dependent) is dead, and §6.3 now
says so with your two witnesses. The theory side added the instrument that
makes the claim checkable — new **Corollary 4.7** (§4.3): for
prefix-independent `L`, (a) `≈_L` is the joint kernel of pure right
extensions and *bare* ω-powers, so any separation beyond the right
congruence is ω-power-only; and (b) — learner-side, and stronger — **every
column of every run on a prefix-independent language is of the ω-sort**: the
initial column is, every mint inherits the sort of the column it derives
from (Definition 3.2; both Lemma 4.5 branches), and the harvest's stem chain
is *flat* under prefix replacement, so every flip lands in the loop chain.
Part (b) is the machine-checkable signature the witness lock below asserts —
and it is retroactively a gate on `GF(aa)` and `EvenBlocks` too (both
prefix-independent; EvenBlocks' 0/4 lin/ω column ledger already conforms).

**New deliverables** (spec revised 2026-07-08f — §6 corpus note + E2
recorded-outcome, §7 `OVERSIZE`, §8 M4.e items 7–8, §9 rows P8/F9):

1. **The witness lock — blocks the §6.3 claim.** For
   `2state1ap2acc_parity_0088836118` / `_1178851077` and their complements:
   prefix-independence asserted on the *canonical* invariant
   (`(s,e) ∈ P ⟺ (c·s,e) ∈ P`, all `c`); the Cor. 4.7(b) ω-sort signature
   asserted on the saturated run (row P8 — a linear mint is build-stopping:
   it convicts the predicate or the sweep, no third option); full exhibits
   (both `.sos` + complete split ledger) into this report.
2. **An exhaustive-shape witness.** The two known ones are sampled-tier;
   exhaustive `2state1ap2acc_parity` if tractable, else the smallest shape
   that yields one — §6.3 wants to claim a shape, not a sample.
3. **Complete the sweep**, then assert **dual-symmetry** everywhere in E2: a
   run on `¬L` is the bit-flip of the run on `L` (same partition, splits,
   counterexamples, query counts), so permanence and gap are
   complement-invariant and every count must pair off exactly. The current
   440/441 guarantee/safety split and the odd gap-2 bucket (205) are
   partial-sweep artifacts that must vanish; an asymmetry surviving the full
   sweep is a bug, not a finding.

**Cross-checks done, and three nits.** E1's ventilations sum exactly
(1486 + 1006 = 2492; the Wagner rows likewise). E2's report-side Wagner
table mixes per-side and σ/π-split entries (the LTL cells `44` and `15` are
per-side where `220 / 221` is split) — the exhibit file is unambiguous;
normalize the report table to the split form so nobody imports a doubled or
halved count. E3 covers 2491 of 2492 and the missing language is aperiodic
(862 + 534 + 89 = 1485 vs 1486): name it and record why it dropped. And the
`N = 4` bucket is anomalous — median fill 145 over 500 languages against an
`N²·|Σ| = 32` envelope, *above* the `N = 8` bucket's 84, at median splits 0;
the paper's §6.2 says only "the low-`N` buckets sit above the envelope" with
a ⟨TBD-M4⟩ audit marker until you explain the 145 (stabilization mints
without splits? more than one AP in that bucket? a convention issue?). The
old M4.e item-1 anomaly (32 languages at `N = 2`) is meanwhile resolved by
flat_canon — 2 languages at `N = 2`, as `N = |S(L)₊¹|` demands; the one-line
convention statement is still owed.

**`OVERSIZE` is ratified** and now normative (spec §7 + row F9): an honest
"too large to certify exactly", ablation leg only, `stall_class` deferred
and never folded into frequency counts, `MISMATCH` reserved for byte
mismatch.

---

## Theory-thread feedback — witness lock banked; 7d retired by theorem; reproducibility floor (2026-07-08)

**The witness lock is accepted, and §6.3's positive side is closed.** The
lock green on all four witnesses — canonical-invariant prefix-independence
plus the Corollary 4.7(b) ω-sort signature, with the minted-column ledgers
embedded — is exactly the certificate the paper needed, and it is
integrated: §6.3 now states the refutation with the certificate language,
and the exhibits pattern (`reference/witness_lock_exhibits.md`) is the model
for everything below.

**Item 7(d) is retired — there is no exhaustive-shape witness to hunt, and
we can prove it.** New paper **Lemma 4.8** (prefix-independence needs
depth): *a prefix-independent closed — safety — language is `∅` or `Σ^ω`;
dually for open.* Proof in one line: for `w ∈ L` and any `x ∈ Σ^ω`, the
words `x[0..n]·w` all lie in `L` by prefix-independence and converge to `x`,
so closedness forces `x ∈ L`. Three consequences. (i) A `c = 0` shape
recognizes only safety languages (every run accepting; finite branching +
König), so the unfinished `3state1ap0acc` can never contribute a witness —
at any point of its sweep, `OVERSIZE` deferrals included. (ii) Every other
exhaustive shape is completely swept, and your E2 Wagner table's
`prefix-indep` column is zero on all of them. (iii) The smallest shapes not
ruled out sit beyond the wall (`2state1ap2acc` at `4^16 ≈ 4.3·10⁹` ids and
up). So the exhaustive tier provably contains no witness, the ask was
unsatisfiable — and nothing is lost: the refutation is an existence claim
carried by the per-witness lock, which is provenance-independent. §6.3 now
claims the *frontier* instead of a shape: prefix-independent permanent
stalls first arise beyond the enumeration wall. The lemma also upgrades
three rows of your Wagner table from census fact to theorem: `prefix-indep
= 0` at `(1, δ)`, `(1, σ)`, `(1, π)` could not have been otherwise. What
remains genuinely open, and worth watching as the sweep and any deeper
sampling proceed: whether a prefix-independent permanent stall exists at
intermediate depth — `(ω, ·)` or `(ω·2, ·)`; the witnesses are `(ω², ·)`
and the lemma only forbids depth one.

In place of 7(d), one cheap gate — **(d′), spec 2026-07-08g**: at sweep
completion, assert the exhaustive negative (zero prefix-independent
permanent stalls over the whole exhaustive tier), emitted as a
machine-generated one-line count per shape.

**Reproducibility floor — the report must be self-sufficient as a source
(spec 2026-07-08g, section 8 item 9, normative).** Every flat-canon table
above says "read off `results.csv`", but nothing under `tests/sosl/logs/`
is committed: the numbers currently trace only to build-machine files, and
the reproduce commands re-run full sweeps. The one committed evidence file
— `reference/witness_lock_exhibits.md` — is exactly the right pattern, so
generalize it: when a drop is validated, **copy** its load-bearing outputs
out of `logs/` into the curated, committed `reference/` tree (nest
`reference/<campaign>/` and `.../sos/` for claim-bearing specimens),
immutable per drop, and cite the committed path next to each table the
report reads off. From this drop on, a figure that traces only to `logs/`
does not enter the paper. The final-sweep drop (item 8) should land under
this rule — the paper's ⟨TBD-M4⟩ replacements will cite those paths.

**Standing items, unchanged otherwise:** the completed sweep with the
dual-symmetry assertion (item 8), the wall-time line, the LTL-agreement
count, and the shape manifest (items 3–6) — all now landing as curated
`reference/` artefacts under item 9.

**Addendum (spec 2026-07-08h) — the exact oracle is re-based; `OVERSIZE` is
curable.** The transformation closure is exponential in `D`'s presentation
— that is what the 200 000 cap measures — while the teacher already holds
the minimal decision structure, the reference `R = 𝓘(L)`. Spec §3.2 `exact`
is rewritten as **exact-by-reference**: equivalence = emptiness of the
symmetric difference `(H ⊗ R̄) ∪ (H̄ ⊗ R)` in the SoS calculus — complement
the free `P`-flip, **align** the lazily generated, memoized `≤ N_H·N_R`
pair DAG (`H`-side verdicts through the P-cache discipline, never
linked-pair laws the mid-run form may not satisfy; `R`-side algebraic), the
disagreeing cell's canonical witness the shortlex-least counterexample.
Polynomial; `D` exits the equivalence loop (its one job, building `R`, the
corpus did). Section 8 item 10 has the gate (byte-identical to the closure
oracle on the named cases) and the payoff: re-run the deferred `OVERSIZE`
classifications — the `ref 57/93` stragglers enter E2's counts, and
`OVERSIZE` becomes fallback-only (row F9 rescoped; the closure survives
solely for referenceless E6 targets, there with lazy exploration +
subsumption à la Fogarty–Vardi / Abdulla et al.).

---

## Exact-by-reference delivered — spec item 10, and three spec defects it exposed (2026-07-09)

`--eq-mode exact` no longer products the automaton with the hypothesis's
transformation closure. It decides against the reference invariant
`R = 𝓘(L)` in the SoS calculus, exactly as spec §3.2 (rev 2026-07-08h) asks:
`align` the hypothesis's Cayley graph with `R` into the letter-generated node
set (`≤ n_H·n_R` nodes, memoized, keyed by shortlex BFS), scan the cells
`(stem node, loop node)` in the counterexample discipline, and return the first
disagreeing cell's canonical lasso. Polynomial throughout; `D` has left the
equivalence loop, its one remaining job being to have built `R` once.

New module `sosl/sosl/teacher/exact_ref.py`, a client of the calculus package
(`align`, `Table.language`, `equivalent`, `Witness`). The closure oracle
(`sosl/sosl/teacher/exact.py`) survives as the **referenceless fallback** — the
E6 path — and is the only place `ExactTooLarge` can still fire.

### Three places the spec was wrong, and what they cost

**(1) The hypothesis side cannot be read on a bare class pair.** Spec §3.2 says
`H`'s per-cell verdict is "read through its own P-cache / representative-lasso
discipline". Taken literally — the cache bit of the class pair `(s, e)`, or a
membership query on `key(s)·loop(e)^ω` — it is *wrong*, and the item-10 gate
caught it on the first non-trivial case: `gf_aa_parity` under
`--no-saturation`, third counterexample, exact-by-reference returned
`loop = a;!a;a;!a` where the closure returned `loop = a;!a`.

The reason is that a class pair has forgotten the loop **word**, and
stabilizing a loop means iterating that word: the P-cache is indexed by
*stabilized* pairs `(fold(u·v^k), fold(v^k))`, never by the raw
`(fold(u), fold(v))`. Absorbing the loop into the stem is a multiplication, and
a mid-run Cayley form has none — which is the very reason the spec forbids
applying linked-pair laws to `H`. The pair-level read-off therefore answers a
different question, and a cell it flags need not be a lasso the hypothesis
predicts wrongly at all — a silent §9 F3 violation, i.e. the learner would be
handed a "counterexample" whose chains have equal endpoints.

Correction, now normative in the module: `H`'s verdict on a cell is its
**prediction on that cell's canonical lasso** `key(c)·key(d)^ω`
(`resolve_prediction`, which stabilizes the actual word). One word per node
suffices, and here is why — the argument the spec owes:

> An equivalence query is issued at a closed, consistent table, so `step` is a
> right action and every hypothesis class is a union of syntactic classes of
> `L` (every split carries a witness, so the hypothesis never separates two
> `≈_L`-equivalent words). Take two words `y, y'` of one aligned node: they
> share an `R`-class, hence so do `y^j` and `y'^j` for every `j`, hence they
> share a hypothesis class too. Both therefore stabilize to the same pair, and
> prediction is constant on the node. Same for the stem. So the scan decides
> every lasso, not merely the keyed ones — and since keys are shortlex-least
> and cells are scanned in the discipline order, the first disagreeing cell
> yields the globally minimal counterexample.

With this reading the two oracles agree byte-for-byte. With the spec's reading
they do not, and the spec's own minimality claim ("the disagreeing cell's
canonical witness lasso is the shortlex-least counterexample") is false.

**(2) The teacher did not, in fact, "already hold" `R`.** Spec §3.2 asserts the
teacher holds the reference invariant. `HoaTeacher` held only `D`. Wired:
`HoaTeacher(..., reference=...)` takes it, the experiment driver feeds the
corpus `.sos` (`run.py::_reference` now returns the parsed `Invariant`, not a
regex-scraped class count), and a teacher constructed without one builds it
once from `D` and caches it. A language whose algebra blows the construction's
cap has no reference, and exact mode then takes the closure fallback — which is
precisely the E6 scoping row F9 asks for.

**(3) `OVERSIZE` on a census run is now a defect, as row F9 (rescoped) says.**
Because `run_case` always has a reference, the closure is unreachable on the
census. The five deferred cases decide, and fast:

| case | `ref_classes` | closure oracle | exact-by-reference |
|---|--:|---|---|
| `3state1ap0acc_013908` (+ `_c`) | 57 | `OVERSIZE` after 11.0 s | `permanent`, 0.1 s |
| `3state1ap0acc_013892` (+ `_c`) | 93 | `OVERSIZE` after 23.4 s | `transient`, 0.4 s |
| `3state1ap0acc_075976` | 121 | `OVERSIZE` after 23.9 s | `transient`, 0.9 s |

Two permanent, three transient. They enter E2's frequency counts; `OVERSIZE`
leaves the census vocabulary. (Dual symmetry holds on the two pairs present.)

### Gates

- **Item-10 gate** (`tests/sosl/exact_ref_gate.py`): on the six E0 named cases,
  under **both** saturation settings, the two oracles must agree byte-for-byte
  on the counterexample sequence, the run ledger (per-phase counters, splits,
  equivalence rounds) and the exported invariant. Green. The demanding half is
  `a_implies_xa` / `a_once` under `--no-saturation`, where the oracle must
  *certify* the proven-permanent stalls (4 and 3 classes, row P4) — certification
  is where an incomplete scan would silently succeed.
- **Census consistency** (`tests/sosl/exact_ref_census_check.py`): a seeded
  25-case replay of the committed drop's decided `no-sat-exact` rows reproduces
  `verdict`, `stall_class` and `learned_classes` on every one. The published E2
  table is not invalidated.
- **Deferred cases** (`tests/sosl/exact_ref_oversize.py`): `--list` reads the
  committed drop; a case id re-runs it.
- Unchanged and green: `exact_fixtures`, `even_conformance`,
  `evenblocks_conformance`, `saturation_gate`, `witness_lock`, and the E0
  campaign (Even / EvenBlocks ledgers byte-stable, row P5).

_Reproduce (from `sosl/`):_ `python3 -m tests.sosl.exact_ref_gate [case]` (one
case per invocation); `python3 -m tests.sosl.exact_ref_oversize --list` then
`... <case_id>`; `python3 -m tests.sosl.exact_ref_census_check [COUNT] [SEED]`.
`census_campaign` grows an `--out DIR` flag (its output directory was hardcoded,
so a fresh sweep could not escape the resume-skip on the previous CSV).

### Proposal — retire `bounded` from the default leg

The default config still certifies with `bounded:8`, at roughly **3.5 s per
case** on the catalogue (≈ 4 h for a full default sweep) against the ablation
leg's **~33 cases/s**. That gap is now pure waste, and the case for switching
the default leg to `--eq-mode exact` is stronger than speed:

- **It is a certification upgrade, not a trade.** `bounded:B` is complete only
  in the limit; a run it certifies is *flagged* in the stats
  (`bounded:8:capped` when the lasso work cap fires first), and the paper has to
  say default runs certify `bounded:8` backed by byte-equality. Exact-by-
  reference certifies exactly, so `eq_certification = exact` everywhere and the
  caveat disappears from §6.
- **It changes no cost number.** The oracle's own membership queries never
  entered the learner's counters (the counting wrapper sits on the learner's
  side of the teacher), and both oracles return the shortlex-least
  counterexample — so the same cexes, the same splits, the same ledgers. The E0
  table already shows it: the `default` and `exact` rows of `a_implies_xa` and
  `a_once` are identical, `43 (32/0/2/9)` and `35 (26/3/2/4)`.
- **It should clear the 137 `BUDGET` rows** of the ablation leg, and would make
  a full both-legs sweep a minutes-scale job instead of an overnight one.

What it costs: `bounded` stays in the tree for the black-box teacher and as the
cheap first pass, but no campaign row would use it. This is a spec-level change
(§3.2's default escalation `reps` → `bounded:8` → `exact`, and §7's
`eq_certification` semantics), so it is **not done** — flagging it for the
theory thread. A full ablation-leg sweep under the new oracle is in flight; its
verdict tally and the dual-symmetry assertion (spec item 8) land in the next
drop, under the `reference/` persistence floor.

---

## Theory-thread feedback — exact-by-reference accepted; one hole in the constancy argument, plugged by a guard the oracle can run on itself (2026-07-09)

**All three corrections are adopted** (spec revision 2026-07-09; the paper is
updated in the same pass, rev. 2026-07-09 — §2.3, §6.1, §6.3, §6.4). In
particular: the bare-pair read was indeed wrong, and for exactly the reason
you state — a class pair has forgotten the loop *word*, prediction is defined
by stabilizing the literal word, and the mid-run Cayley form has no
multiplication to absorb a loop into a stem with. `resolve_prediction` on the
cell's canonical lasso is the right and unique reading; it is now the spec's
text. The teacher holding `R` is what rev 08h asserted and should have said
in wiring terms; done. And the five decided `OVERSIZE` cases enter E2 —
subject to one re-run noted below.

**But the constancy argument you supply has a real hole, and E2's new
`permanent` verdicts stand on it.** The chain is: two words of one aligned
node share an `R`-class, hence so do their powers `y^j, y'^j`, *"hence they
share a hypothesis class too."* That last step invokes "every hypothesis
class is a union of syntactic classes of `L`, because every split carries a
witness" — and the witness invariant delivers this **for table words only**:
distinct classes have representatives separated by a column, so two
`≈_L`-equivalent *table* words are never split. `y^j` for `j ≥ 2` is far
outside the table, and there the hypothesis class of a word is whatever the
fold computes. That the fold's kernel on all of `Σ*` coarsens `≈_L` — call it
**factoring** — does not follow from closed + consistent + witnessed splits:
consistency constrains *rows*, not fold-intermediates, so the fold can in
principle be signature-incoherent one step beyond the frontier. This is
precisely the coherence gap the paper flags after Lemma 3.3 ("nothing yet
says `fold(d, u)` and `fold(d, w_{ψ(u)})` agree, and §4.2 turns exactly on
that gap"). Note also that your argument never uses the H-component of the
node: were it sound as stated, it would prove `fold_H` factors through `ψ_R`
outright — forcing the aligned graph to have **exactly `N_R` nodes, always**,
the `≤ N_H·N_R` bound never tight. An argument that proves that much from a
table-word invariant is leaning on something unstated.

Three sharpenings of where this bites:

- **The closure oracle never needed the claim.** It tracked each loop word's
  full action `d ↦ fold(d, v)` on the hypothesis classes; the aligned node
  `(fold_H(v), ψ_R(v))` is a *coarsening* of that action, and the new oracle
  is sound exactly when the coarsening is lossless.
- **The saturated leg does not rescue it.** Theorem 5.1 does prove
  `u ≈_L w_{ψ(u)}` for all words — which yields factoring — but that step of
  the proof consumes *equivalence granted*. Using it to prove the equivalence
  oracle sound is circular.
- **The unbacked exposure is the ablation leg's `permanent` verdicts.** A
  permanence certification blesses a *non-canonical* fixpoint as
  language-equivalent; byte-equality cannot re-validate it (it is supposed to
  fail byte-equality). Everywhere else the certificate ladder still ends at
  byte-equality against the reference.

**The repair costs nothing, because the oracle has already built the
universally-quantified object.** The aligned graph *is*
`{(fold_H(w), ψ_R(w)) : w ∈ Σ*}` — the memoized letter-generated closure. So
the property the argument needs is decidable by inspection of the graph the
scan walks anyway:

> **Functionality guard (normative, spec §3.2).** At every exact-by-reference
> query, assert that no two aligned nodes share their `R`-component —
> equivalently, that the non-identity node count equals `R`'s non-identity
> class count (every `R`-class is reached, so functionality is exactly
> `node count = N_R`).

With the guard green the certification theorem is airtight; we checked it end
to end. Write `f : 𝒞_R → 𝒞_H` for the function the guard certifies
(`fold_H = f ∘ ψ_R` on **all** words, since the graph contains every word's
image). For any lasso `(u, v)` in cell `(c, d)`: the loop orbit
`ψ_H(v^j) = f(d_R^j)` is determined by the cell, hence so are the
stabilization power `k`, the pair
`(s, e) = (f(c_R·d_R^k), f(d_R^k))`, and the prediction — a teacher truth on
`(w_s, w_e)`. So the hypothesis's prediction is constant on every cell and
equals its prediction on the cell's keyed lasso; the `R`-side verdict is
constant on cells unconditionally (membership factors through
`(ψ_R(stem), ψ_R(loop))`). An all-agree scan therefore certifies the
hypothesis's prediction function against `L` on *every* lasso; and global
minimality of the returned counterexample follows as in the calculus's
Proposition 3.2 — every wrongly-predicted lasso is dominated componentwise by
its own cell's keyed lasso, which is itself wrong. Two scopes worth keeping
straight: a **returned counterexample is sound unconditionally** (both
verdicts are evaluated on the concrete keyed lasso — no guard needed), while
**certification and minimality are conditional on the guard**.

If the guard ever fires, that is *not a bug* (new §9 row F10): record it,
fall back to the closure oracle for that query, and hand the graph to the
theory thread — a firing is a **counterexample to the factoring conjecture**
(that the fold factors through `≈_L` at every closed, consistent table the
learner reaches at equivalence time) and a first-class finding. We could
neither prove the conjecture nor refute it: our suspicion is that it fails
for adversarially built closed/consistent tables and may hold on
learner-reachable ones. The census is now the experiment. Row F9 rescopes
once more: `OVERSIZE` is legal on the referenceless fallback (E6) *and* on a
guard-failed census query's fallback; expected census count zero.

**The `bounded` retirement is approved**, with two riders. (i) The guard is a
precondition: `eq_certification = exact` everywhere may not rest on an
unproved lemma. (ii) The trust-anchor note moves into the paper honestly:
with exact-by-reference, the teacher's equivalence *and* the final
byte-equality validation share the anchor `R`. Not circular in practice —
harness layer 1 independently cross-checks `D`-simulation against the `R`
read-off on 10⁴ random lassos per case, so `D` still validates `R` through
membership — but §6.1 may no longer imply the oracle and the certificate are
independent evidence. Spec: default escalation is now `reps` → `exact`;
`bounded` survives for black-box teachers and diagnostics; no campaign row
uses it.

**Census bookkeeping.** The five decided cases move the permanent family
1180 → **1182** on the reached set; the paper's §6.3 deferred-cases paragraph
is deleted and the count updated (still ⟨TBD-M4⟩ until the sweep completes).
Bank the two new `permanent` entries (`3state1ap0acc_013908` + complement)
only after re-running them **under the guard** — a permanence verdict is
exactly the unbacked case above, and the re-run is seconds.

**Asks back** (spec section 8, item 11):

1. Implement the guard in `exact_ref` and assert it on every query of the
   in-flight sweep; report the firing count (predicted: 0, with node count
   exactly `N_R` on every run).
2. Re-run the `013908` pair under the guard before E2 banks them.
3. Locate `075976`'s dual partner and say where it classified: a run on `¬L`
   is the bit-flip of the run on `L`, so under the old oracle the partner
   should have been `OVERSIZE` too — presumably it sat among the 137 `BUDGET`
   rows instead. Confirm it lands `transient` (the item-8 dual-symmetry
   assert would catch a mismatch anyway, but the report should say where the
   partner went).
4. After the guard is green on the named cases: switch the default leg to
   `--eq-mode exact`, re-run the default sweep, and confirm the Even /
   EvenBlocks ledgers stay byte-stable (row P5) with
   `eq_certification = exact` on every row.

---

## Theory-thread feedback — the guard fires: conjecture refuted, retraction banked, escalation amended (2026-07-09)

The guard did exactly what it was built for, and the finding is yours: the
**factoring conjecture is refuted on learner-reachable tables** (commit
`5e83cfae8`; theory predicted zero firings and was wrong). On
`2state1ap2acc_parity_2195145216`'s ablation leg the fold of a closed,
consistent table splits three syntactic classes beyond its table words —
R-classes 8, 12 and 14 each spread over two or three fold values, 20–24
aligned nodes over 17 — on eight equivalence queries, every one decided
soundly by the closure fallback, final stall 16-vs-17 as before. Two
readings worth recording:

- **The conditional theorem was the right shape.** Nothing in the delivered
  oracle is invalidated — certification was never claimed beyond the guard —
  and the fallback is load-bearing, not ceremonial. Had the constancy
  argument been taken at face value, eight certifications on this one case
  would have been unsound.
- **Left-saturation does not buy functionality.** Your note that saturated
  runs fire mid-run too is sharper than it looks: every default-leg
  equivalence query is posed at a *sweep-clean* table, so the sweep's fold
  coherence (the claim inside Theorem 5.1) does not imply factoring — the
  guard is irreducible. One structural expectation survives, downgraded
  from conjecture to assert-worthy: on a run whose export is byte-equal,
  the **final** certifying query sits on a canonical table, whose fold *is*
  the syntactic morphism — so a firing on a final default-leg query should
  never happen (it would convict the run before byte-equality does). Worth
  a per-run assert: `n_guard_firings` on the certifying query itself must
  be 0 whenever the run ends `SOUND`.

**The retraction is adopted.** The five `OVERSIZE` cases are *not* decided:
`013908` (pair) and `075976` guard-fire and their closure fallback hits the
cap, so they return to deferred and never entered E2's published counts. The
paper is reverted in the same pass (1182 → 1180; §6.3's deferred-cases note
restored; §2.3/§6.1 now state that the guard fires and what happens then).
Theory's earlier instruction to bank-after-re-run is void — the re-run
answered *no*.

**Escalation policy, amended (spec §3.2).** With the guard firing in
practice, "retire `bounded`" needs one more rung than the last reply gave
it. Normative order per equivalence query: `reps`, then exact-by-reference
under the guard; on a firing, the closure product decides; if the closure
exceeds its cap, the two legs part ways — the **default leg** falls back to
`bounded:8` (recorded in `eq_certification`; byte-equality still validates
the run end-to-end, so nothing is lost but the "exact everywhere" headline),
while the **ablation leg** records `OVERSIZE` (permanence is genuinely
undecided below the cap; a bounded answer cannot certify a stall). So
`bounded` survives as the cap-escape of guard-fired default-leg queries and
nowhere else.

**Asks** (spec item 11, updated in place):

1. Sweep-wide tallies: `n_guard_firings` per leg, how many runs are entirely
   guard-green, and — separately — whether any `SOUND` run fired on its
   *final* query (expected 0, per the assert above).
2. A committed exhibit for one firing: the colliding nodes *with two
   concrete witness words* `y ≈_L y'`, `ψ(y) ≠ ψ(y')` (the probe prints node
   ids; the words are the display — a mid-run table is not merely coarser
   than the algebra (§4.2), its fold is *incomparable* with it, and that
   deserves the same first-class treatment as the non-associative export).
3. Still owed from last round: `075976`'s dual partner — now expected
   `OVERSIZE` too, which would restore dual symmetry among the deferred.
4. The default-leg switch (item 11d) proceeds under the amended escalation.

---

## Theory-thread feedback — item 11 closed but for the sweep; the exhibit enters the paper (2026-07-09)

All four asks are answered (commit `902ed1f96`); accepted as delivered, and
the campaign's certification story is now settled end to end.

- **The default leg certifies exact.** Escalation as amended, `manifest`
  moved, E0 green with `eq_certification = exact` on all ten rows, Even /
  EvenBlocks ledgers byte-stable — P5 held through the oracle swap, which is
  the strongest regression evidence the design admits. The retire-`bounded`
  decision is discharged in its final form: `bounded` certifies nothing on
  the campaign except recorded cap-escapes.
- **The exhibit is the display we wanted, and it is in the paper.**
  `y = !a·!a·a ≈_L a·!a·!a = y'` — one syntactic class, two fold values, on
  a closed, consistent, learner-reached table, re-verified against the
  reference and the fold. The paper's §2.3 now carries the witness pair
  inline as the realization of "the fold can split a syntactic class", and
  §6.3's deferred note states the complement-closure of the deferred set.
  One persistence ask remains: when the sweep drop lands, copy the exhibit
  (the probe's verified output, witness words included) under `reference/`
  per item 9 — it is claim-bearing now that the paper displays it.
- **`guard_fired_final` conforms to the theory shape.** `013908`'s default
  leg — one mid-run firing, clean final query, byte-equal — is exactly the
  predicted pattern: firings are a mid-run phenomenon, and the certifying
  query of a sound run sits on a canonical table. The assert stands as a
  permanent gate (row F10's hard edge).
- **Dual symmetry is restored among the deferred.** `075976` and its dual
  both guard-fire and blow the cap: the deferred set is complement-closed,
  as the bit-flip argument demands. The last asymmetry question from the
  2026-07-09 review is closed.

Open toward the next drop, and nothing else: the sweep-wide tallies
(item 11a — per-leg `n_guard_firings`, guard-green run count, cap-escape
count, `guard_fired_final = 0` across all `SOUND` rows), which replace the
paper's two remaining guard ⟨TBD-M4⟩ markers (§2.3 firing tally, §6.1
guard/cap tallies), under the `reference/` persistence floor.

---

## The guard fires — conjecture refuted, retraction banked, escalation and default leg landed (2026-07-09)

Answering the four asks of the 2026-07-09b reply. Commits: `5e83cfae8` (guard),
`902ed1f96` (escalation, exhibit, default leg).

### Retraction first — the earlier "E2 is not invalidated" claim was wrong

The 2026-07-09 entry above certified exact-by-reference on a 25-case replay of
the committed drop and concluded the published E2 table stood. That check was
too small. A full unguarded ablation sweep (3938 runs) disagreed with the
committed drop on **74 of the 3796 jointly-decided rows, in both directions** —
16 where the by-reference oracle certified a stall the closure had broken, 14
where it found a counterexample the closure had certified away, and 44 where
both said `permanent` at different class counts. Every one is a guard firing:
that sweep is void and is not banked. The guarded sweep is in flight.

### Ask 2 — one firing, exhibited (committed)

`NotFunctional` now carries the shortlex keys of the colliding nodes, so a
firing ships its own witness pair, and `exact_ref_guard` re-verifies both halves
against the reference invariant and the hypothesis's fold rather than trusting
the guard. Exhibit committed at
`sosl/tests/sosl/reference/guard_firing_exhibit.md`
(`2state1ap2acc_parity_2195145216`, ablation leg, 8 firings, 20–24 aligned nodes
over 17 reference classes). The first:

> `y = !a;!a;a` and `y' = a;!a;!a` — both in reference class 8 — fold to
> hypothesis classes 3 and 2.

Three syntactic classes (8, 12, 14) are split this way across the eight queries.
Your reading is the right one and the exhibit's headline: a mid-run table is not
merely *coarser* than the algebra, **its fold is incomparable with it**.

### Ask 3 — `075976`'s dual, and dual symmetry among the deferred

Under the old oracle the partner `3state1ap0acc_075976_c` sat among the 137
`BUDGET` rows (ref 121, hit the 30 s wall), not among the `OVERSIZE` rows — as
you predicted. Under the guard **both** guard-fire and both blow the closure's
200 000-element cap, so both record `OVERSIZE`. The deferred set is
dual-symmetric. `013908` and its complement likewise: the re-run answered *no*,
and the five formerly-deferred cases stay deferred. `exact_ref_oversize` now
reads an `OVERSIZE` as `DEFERRED` (rows F10 → F9), and a defect only when the
guard never fired.

### Ask 4 — the amended escalation, and the default leg

`_exact` walks exact-by-reference under the guard → closure on a firing →
`bounded:8` on a capped closure, the cap-escape enabled only where a later
byte-equality still validates the run (`cap_escape = config.saturation`). The
ablation leg leaves it off and lets `ExactTooLarge` propagate: a bounded answer
cannot certify permanence. `manifest.DEFAULT` now carries `eq_mode="exact"`.

E0 is green under it: `eq_certification = exact` on all ten rows, 8 SOUND /
2 ACCEPTOR_ONLY / 0 MISMATCH, and the Even / EvenBlocks ledgers byte-stable to
the M3 baselines — `99 (67/4/14/14)` and `43 (32/0/2/9)` (row P5).

Your structural expectation holds where you placed it. `3state1ap0acc_013908`'s
**default** leg reaches byte-equal `SOUND` with one mid-run firing and a **clean
final query** — the canonical table's fold *is* the syntactic morphism. That is
now a per-run field, `guard_fired_final`, and the probe treats a firing on the
final query of a byte-equal run as a defect.

Cost, since it bears on the retirement: the default leg ran at ~3.5 s per case
under `bounded:8` (≈ 4 h for the catalogue) and now sweeps at **~33 cases/s** —
until the guard fires, where the closure fallback drops it to ~2.5 cases/s. The
switch pays for itself and the fallback is where the remaining cost lives.

### Ask 1 — sweep tallies (partial; the sweep is in flight)

Both legs, guarded, `--budget 30`. At 380 of 7876 runs: every run guard-green,
`eq_certification = exact` throughout, all `SOUND`, no final-query firing. These
are the small shapes; the firings begin at the parity and 3-state shapes. Full
per-leg tallies — total firings, runs entirely guard-green, and whether any
`SOUND` run fired on its final query (expected 0) — land with the completed
sweep, together with the E2 recount and the item-8 dual-symmetry assertion, as a
committed `reference/` drop.

_Reproduce (from `sosl/`):_ `python3 -m tests.sosl.exact_ref_guard <case_id>
[--nosat]`; `python3 -m tests.sosl.exact_ref_oversize --list`;
`python3 -m tests.sosl.campaign_e0`; the sweep is
`python3 -m tests.sosl.census_campaign --config both --budget 30 --out <dir>`.

---

## Theory-thread feedback — the 74 rows validate the theorem; the fallback localizes (2026-07-09)

**The retraction is accepted, and it is better news than it reads.** The 74
disagreements (16 + 14 verdict flips, 44 permanent-at-different-counts) are
the campaign-scale measurement of what unguarded by-reference certification
does — and since *every one is a guard firing*, the converse holds too:
**zero disagreements on guard-green rows across 3796 jointly-decided
cases**. That is the conditional certification theorem passing its first
mass test: the guard predicate is not merely sufficient in the proof, it is
empirically exactly where the unsoundness lives. The void sweep is correctly
void; the committed closure drop never depended on by-reference and stands
untouched; nothing in the paper moves this round.

The exhibit is banked as asked — on the same shelf as
`witness_lock_exhibits.md`, which is the right one — the `075976` dual
landed among the `BUDGET` rows as predicted and both now cap symmetrically,
and the E0 conformance under the switched default leg closes item 11 b–d
for good. `guard_fired_final` on `013908`'s default leg is the predicted
shape realized; keep it as a permanent gate.

**The cost flag is a theory question, and the answer is: localize the
fallback.** A firing does not poison the whole query — it poisons the cells
that *touch the split classes*, and the aligned graph already says which
those are. Let `Split ⊆ 𝒞_R` be the reference classes holding ≥ 2
H-partners in the built graph. Call a cell `(c, d)` **quiet** when every
class in the power orbit `{d_R^j}` is unsplit and so is `c_R·d_R^k`, where
`k` is the stabilization power of the orbit's unique-partner sequence
(well defined under quietness: `h_j` := the unique H-partner of `d_R^j`;
`k` := least with `h_{2k} = h_k`, which exists since `{d_R^j}` is
eventually periodic).

> **Localization.** Every quiet cell is decided by its keyed lasso, even on
> a fired (non-functional) graph.
>
> *Proof.* Take any `(u, v)` in the cell. For each `j` the word `v^j` has
> an aligned node in the graph with R-component `d_R^j`; that class being
> unsplit forces `ψ_H(v^j) = h_j`. So the fold orbit — hence the
> stabilization power `k` — is the same for every `v` in the cell; and
> `u·v^k`, whose R-class `c_R·d_R^k` is unsplit, folds to *its* unique
> partner. Predicting pair and P-cache bit are therefore constant on the
> cell, and equal to the keyed lasso's. ∎
>
> (`Split = ∅` recovers the functionality theorem — the guard is the
> special case.)

Only the **residue** — cells whose loop orbit or stabilized stem class
touches `Split` — needs the closure, restricted to residue lassos.
Minimality survives: a wrong lasso in a quiet cell is dominated by its
keyed lasso, one in a residue cell is found by the closure's own minimal
scan, so return the smaller of the quiet scan's first flagged keyed lasso
and the closure's residue-restricted minimum. On the exhibit case the split
classes are 3 of 17 — if that shape is typical the residue is a sliver, and
~2.5 cases/s should climb back toward ~33.

**Instrumentation before construction:** measure the residue fraction
(quiet cells over all cells) on the known firing cases first, and build
only if it is small; gate by byte-identical counterexamples, ledgers and
verdicts against the unlocalized fallback on every fired query of the named
firing cases plus a seeded fired sample. Incremental reuse of the closure
across a run's successive queries (they differ by one split) is a second,
independent option — engineering's choice. Spec: section 8 item 12, with a
pointer at §3.2 point (iii).

Unchanged and still open toward the drop: the completed-sweep tallies with
`guard_fired_final = 0` on every `SOUND` row, the E2 recount, and the
item-8 dual-symmetry assertion, all under the persistence floor.

---

## Item 12 instrumented — the residue is not a sliver; recommend not building the localization (2026-07-09)

Per the ask ("instrumentation before construction"), `NotFunctional` now carries
the whole partner map, and `tests/sosl/exact_ref_residue.py` measures, per fired
query, `|Split|` against `N_R` and the residue fraction (cells that are not
quiet, over all `N_R·(N_R−1)` cells). Quietness is implemented as the theorem
states it: every class of the loop's power orbit `{d^j}` unsplit, the orbit's
unique-partner sequence stabilizing at some `k`, and `c·d^k` unsplit.

| case | leg | firings | `\|Split\|` / `N_R` | residue (min / median / max) |
|---|---|--:|---|---|
| `3state1ap0acc_013908` | default | 1 | 1 / 57 | 26.8% |
| `2state1ap2acc_parity_2195145216` | ablation | 8 | 1–6 / 17 | 57.7% / 67.6% / 81.6% |
| `2state1ap2acc_parity_0006272130` | ablation | 5 | 1–2 / 10 | 63.3% / 76.7% / 84.4% |

**The residue is not a sliver, and the shape of the payoff is worse than the
number.** Two observations, the second decisive:

1. *A single split class poisons a quarter of the cells.* The mildest firing we
   have — `013908`, one split class out of 57 — still leaves 26.8% residue. A
   split class is absorbing in the orbit structure: it lies in the power orbit of
   every loop that reaches it, and in `c·d^k` for every stem `c` that multiplies
   into it. Split-class *count* is therefore a poor predictor of residue size,
   which is why 1-of-57 (26.8%) and 1-of-17 (57.7%) sit where they do.

2. *The residue is never empty on a fired query, so the closure gets built
   anyway.* If `d ∈ Split` then the cell `(c, d)` is residue for every `c` — the
   loop orbit contains `d` itself. A firing means `Split ≠ ∅`, hence residue
   `≠ ∅`, hence the closure fallback still runs. And the closure's cost, and its
   `ExactTooLarge` cap, live in `_loop_elements` — the construction of the
   transformation monoid — which is **independent of which cells one intends to
   scan**. Localization shrinks the closure's `configs × elements` scan by
   18–73%, never its construction. So it lifts **no** `OVERSIZE`, and the ~33 →
   ~0.9 cases/s collapse is not where it bites.

Recommendation: **do not build the localization** as specified. It is a
constant-factor win on a phase that is not the bottleneck, bought with a
correctness-critical quietness predicate that would need its own gate. The
second option in the ask is the better one and we would take it instead:
**incremental reuse of the closure across a run's successive queries.** The
closure's elements are pairs `(D-profile, H-transformation)`; the profile monoid
is *constant for the whole case* — only the hypothesis side changes between
queries, and successive hypotheses differ by one split. Building the profile side
once per case, and extending the transformation side per query, attacks the phase
that actually costs and that actually caps.

Before either is built, the honest next measurement is a split of the closure's
wall time into build vs scan on a fired, non-capped query. We have not made it,
and it decides between "reuse the profile monoid" and "the fallback is simply
expensive, accept it".

_Reproduce (from `sosl/`):_ `python3 -m tests.sosl.exact_ref_residue <case_id>
[--nosat]` — one case per invocation.

### Ask 1 — sweep tallies, still in flight

The guarded both-legs sweep is at ~900 of 7876 runs, all guard-green and
`SOUND` so far (the small shapes); throughput fell from ~33 to ~0.9 cases/s as
the fired shapes arrived. Full per-leg tallies (`n_guard_firings`, guard-green
run count, cap-escape count, `guard_fired_final = 0` across all `SOUND` rows),
the E2 recount and the item-8 dual-symmetry assertion land with it, under the
persistence floor.

---

## Theory-thread feedback — item 12 closed without construction; nothing further proposed (2026-07-09)

**Accepted; item 12 is closed as refuted-by-instrumentation — the outcome
the instrumentation-first clause exists for.** The theorem stands as
mathematics and buys nothing here, for two reasons the measurement exposed —
the second of which theory should have seen structurally before asking:

- a split class is **absorbing in the orbit structure** — every loop whose
  power orbit reaches it drags its entire cell row into the residue — so
  `|Split|` does not predict residue mass (1 of 57 already poisons 26.8%);
- a firing *means* `Split ≠ ∅`, so the residue is never empty, the closure
  is built on every fired query regardless, and both the cost and the
  `ExactTooLarge` cap live in the build (`_loop_elements`), which no scan
  restriction touches.

Cell-level localization of this oracle is structurally dead, not merely
unprofitable on these three cases; the absorbing observation is worth
keeping for that reason alone. Spec item 12 is annotated CLOSED — do not
build — and the §3.2 pointer is corrected so the spec no longer advertises
it.

**Your recommendation is endorsed as-is.** Incremental closure reuse — the
`(D-profile, H-transformation)` factorization with the profile monoid
constant per case — is the only named lever that attacks the phase that
costs and caps, and your build-vs-scan wall-time split on a fired,
non-capped query is the right and sufficient discriminator; if it comes
back scan-dominant, the residue numbers already bound that path's best case
and the honest conclusion is the one you wrote — the fallback is simply
expensive, accept it. Theory has no cheaper exact decision procedure for a
fired query to offer, and proposes nothing further. The measurement is
yours to schedule; the remaining opens are unchanged and all land with the
sweep drop.

---

## Correction — the build/scan measurement refutes my own recommendation (2026-07-09)

Theory endorsed incremental closure reuse "as-is", on the strength of a claim I
made in the item-12 entry above without measuring it: that the closure's cost
lives in the build (`_loop_elements`). I then made the measurement theory named
as the discriminator (`tests/sosl/exact_closure_profile.py`, which times a fired
query's build and scan phases separately). **The claim is false on every
non-capped fired query, and the endorsed lever is worthless.** Recorded here
before it reaches the paper.

| case | leg | fired non-capped queries | build | scan |
|---|---|--:|--:|--:|
| `2state1ap2acc_parity_2195145216` | ablation | 8 | 2.1 ms (1%) | 172.1 ms (99%) |
| `2state1ap2acc_parity_0006272130` | ablation | 5 | 0.9 ms (2%) | 45.1 ms (98%) |
| `3state1ap0acc_013908` | default | 1 | 0.2 ms (4%) | 3.5 ms (96%) |

Three consequences, and they do not all point the same way:

1. **Incremental profile-monoid reuse is dead.** It attacks the build, which is
   1–4% of a non-capped fired query. Amdahl caps the win at 4%. My
   recommendation was wrong and theory's endorsement of it rests on my error, not
   on theirs.
2. **Cell-level localization is not "structurally dead" as a scan optimization.**
   It attacks the phase that *is* 96–99%, and `exact_ref_residue` bounds its win
   at 18–73% of it. The one thing I said about it that survives is the thing that
   matters: `Split ≠ ∅` on a firing, so the residue is never empty, the closure
   is still built, and **no `OVERSIZE` is lifted**.
3. **Neither lever touches the sweep's collapse, because neither phase is the
   sweep's cost.** A non-capped fired query costs 3–45 ms per *run*. The sweep's
   time is in the **capped** queries, where the build runs all the way to the
   200 000-element cap before raising: `3state1ap0acc_013908` (ablation) burns
   **10.7 s**, `_075976` **23.5 s** — and on the default leg that cost is paid
   *and then* `bounded:8` runs as the cap-escape. That is the ~33 → ~0.9 cases/s
   collapse, and it is 100% build, in the runs that end `OVERSIZE` or `BUDGET`
   anyway.

So the honest ranking of levers is the reverse of what I proposed. The one that
addresses the observed cost is neither of the two on the table: **make the cap
cheap to hit.** A capped query's verdict is already decided — `OVERSIZE` on the
ablation leg, `bounded:8` on the default leg — so the 10–24 s spent proving the
closure is large is pure waste. A time-based cap, or a much lower element cap,
reaches the same verdict in milliseconds. The measurable risk is the middle band:
languages whose closure exceeds a lowered cap but would have finished under
200 000, which would change verdict from decided to deferred. That count is
exactly what a lowered-cap re-run of the fired cases would report, and it is the
next measurement, not a build.

I am not proposing to implement any of this — the sweep is in flight and its
tallies come first. The correction is what needed recording: theory's item-12
close ("cell-level localization is structurally dead") is right about
`OVERSIZE` and wrong about the scan, and its endorsement of reuse should be
withdrawn.

_Reproduce (from `sosl/`):_ `python3 -m tests.sosl.exact_closure_profile
<case_id> [--nosat]` — one case per invocation.

## Status note — the sweep died with its session; the campaign moves to the cluster (2026-07-10)

The guarded both-legs sweep reported "in flight" above **crashed with its
session at 4275 / 7876 runs** (partial tallies: SOUND 3308, ACCEPTOR_ONLY 916,
BUDGET 46, OVERSIZE 4, MISMATCH 1; guard firings in 2234 runs — routine at the
3-state shapes, far past the early all-green extrapolation — and
`guard_fired_final = 0` on every SOUND row so far). The lone MISMATCH is a
**driver defect, not a byte mismatch**: `census_campaign`'s catch-all records
any exception leaked by `run_case` as `verdict=MISMATCH`
(`3state1ap0acc_013604`, ablation, `CAUGHT: _Budget`) — row F9 reserves
MISMATCH for genuine byte mismatches, so the misfile must be fixed before any
tally is banked. The partial CSV (`tests/sosl/logs/census_guard/`) is
superseded, not resumed: the sweep re-runs fresh on the OAR cluster at
`--budget 60`, which also discharges the `gates.txt` ask to redo the 72
deferred dual-symmetry comparisons at a higher budget.

Infra landed for that (2026-07-10, commits `af759d0de..3d5380462`): the
cluster runner is the interface (`cluster/README.md`; shards write private
`$OARRUN_OUT.csv`, `reap.sh` merges — which suits the sweep-now-study-later
analyzers directly), and **ROLL is deployed cluster-side**:
`deps/build_roll.sh` builds `opt/roll/ROLL.jar` from ROLL's GitHub HEAD where
a JDK exists, and on the JDK-less compute nodes (headless JRE + maven, no
`javac`/`jar` anywhere — probed) the locally built jar was copied once into
the cluster checkout's `opt/roll/` (documented exception, `deps/README.md`).
`baseline.py` now resolves `$ROLL_JAR` with the repo's own `opt/roll` as
default — no path outside the tree. The named-case E3 gate reproduces the
paired table above **byte-for-byte** through the new path (same jar revision
`54d32d2`, ROLL HEAD unmoved since the paper numbers). A node-side smoke run
answers green. Also fixed in passing: `cluster/oarsub.sh` lost argv quoting
on multi-word commands (its README overstated); re-quoted, regression-tested
on the node, contract documented.

The next drop is unchanged in content — item-11a per-leg guard tallies, the
E2 recount, the item-8 dual-symmetry assertion, wall-time line and
LTL-agreement count — now produced from the cluster run's merged
`results.csv`, under the `reference/` persistence floor. Owed first, in order:
the MISMATCH-misfile fix, `--cases`/`--out-csv` sharding on `census_campaign`
(the runner forbids shared output files), a planner cutting the catalogue to
the runner's caps (60 s per run, ~300 s per command, 5-minute walltime), and
the E3 leg as one command per (case, mode) submitted `--cores 4`.

## Item 1 done — the fault-verdict misfile is fixed; verdict `MISMATCH`→`FAIL`, new `CRASH` (2026-07-10)

The census drivers' catch-alls recorded *any* leaked exception as the soundness
verdict. Row F9 reserves that verdict for a genuine byte inequality, so the
crashed sweep's lone such row (`3state1ap0acc_013604`, ablation,
`CAUGHT:_Budget`) was misfiled: it was not a byte mismatch but a leaked
`_Budget` — the SIGALRM/`finally` race in `run_case`, the alarm firing in the
narrow window inside `run_case`'s own `finally` after its `except _Budget` is no
longer reachable, so the one-shot alarm escapes the function.

**Two vocabulary decisions you should ratify (spec §7 updated in lockstep):**

1. **`MISMATCH` → `FAIL`.** The soundness verdict is renamed. "Mismatch" is too
   weak for what it certifies — a run that *ran to completion and produced an
   unsound byte* (P1 red, or byte-differs under saturation). That is a failure,
   and the verdict should read as one. `FAIL` stays reserved for exactly that
   (row F9). Spec §7 (the `sos_validate` diagram, the end-to-end gate wording,
   the field enum, row F9) and `sosl/validate/README.md` are renamed to match;
   `classify_census` keeps its own separate `MISMATCH` (a neutral duality /
   spectrum-law file comparison — "mismatch" is apt there), and the local
   diagnostic prints in the ad-hoc probes are untouched.

2. **New sixth verdict `CRASH`.** A leaked exception is a run that **never
   completed** — categorically outside soundness. Folding it into `FAIL` (or
   naming it "ERROR", which connotes a bad *result*) would inflate the one count
   that means "the learner is unsound". So a leaked fault routes by kind:
   `_Budget` → `BUDGET` (a clean timeout; the race changes *where* the alarm is
   caught, not the verdict it earns), anything else → `CRASH`. Spec §7's enum is
   now `SOUND | FAIL | BUDGET | ACCEPTOR_ONLY | OVERSIZE | CRASH`.

**Scope.** The misfile lived in *two* drivers, not one: `census_campaign`'s
catch-all (the handoff item) and `driver.py`'s defensive outer guard (the same
bug, unlisted). Both now split `_Budget`→`BUDGET` / other→`CRASH`. `run_case`'s
own internal catch-all is aligned too (in-body crash → `CRASH`). `report.py`'s
E0 gate now fails on `CRASH` as well as `FAIL`/`BUDGET`, and its totals line
counts crashes. The `census_e1`/`census_e2` analyzers treat every non-`SOUND`
verdict generically, so nothing downstream shifts; the F9 count of genuine byte
failures is now clean of faults.

Guard: `tests/sosl/fault_verdict_probe.py` monkeypatches `run_case` to force each
leak path and asserts `_Budget → BUDGET`, other `→ CRASH`. Green. Standing gates
re-run green (`saturation_gate`, `exact_fixtures`, `campaign_e0` byte-stable,
`witness_lock`). The partial `census_guard` misfiled row is thereby explained and
retired; the fresh cluster sweep at `--budget 60` banks the tally.

## Cluster infra for the sweep + E3 is in place (items 2–4) (2026-07-10)

The sharding infrastructure the cluster drop needs is landed and verified
locally against the current catalogue (now **4248 languages** — the concurrent
genaut rewrite is enriching the corpus with higher-Wagner-degree samples; every
tally below re-runs fresh, so the growth is immaterial to what is banked).

- **`census_campaign --cases i:j --out-csv FILE`** — the learner sweep shards by
  a half-open slice of the fixed `flat_canon_cases()` order into a private file
  (the runner forbids a shared output — `O_APPEND` is not atomic over NFS).
  Verified: `0:3` and `3:6` are disjoint and partition `0:6`.
- **`census_e3`** rebuilt to a **long CSV** (`case, kind, size, MQ, EQ`, kind ∈
  {ours} ∪ the three ROLL FDFA modes) so per-`(case, mode)` shards concatenate;
  `--cases` / `--only KIND` / `--out-csv` shard it, `--summary-only` pivots the
  merged CSV to the same paired medians / size-comparison / LTL-cut. The
  paper-anchored `campaign_e3` and `baseline.py` are untouched.
- **`cluster_plan`** (modeled on `survey/cluster/plan.py`) cuts either sweep into
  a `cmds.txt`, chunk size packed to `OARRUN_TIMEOUT` sourced from
  `cluster/config.sh` (no drift; env override honoured by planner and runner
  alike). Default plans the learner sweep; `--e3` plans the ROLL census, one line
  per `(kind, case-slice)`. At cap 130: sweep 4248 commands (1 case/cmd, both
  legs = 120 s); E3 6443 commands (3 ROLL modes × 2124 at 2 cases/cmd + ours ×
  71). Raising the cap repacks (cap 300 → 2 cases/cmd on the sweep).

Owed next (items 5–6): push (needs the user's OK) + `sync_cluster.sh`, submit
both cmds lists, reap, run the analyzers (`census_e1`, `census_e2_exhibits`,
`census_e3 --summary-only`) and gates (`witness_lock`, dual-symmetry / (d′),
`guard_fired_final = 0` on every SOUND row) off the merged CSVs, commit the drop
under `reference/`, and hand theory the item-6 tallies (which replace the paper's
9 `⟨TBD-M4⟩`).

## Cluster ops — how a census drop is run

The campaign runs on the OAR cluster (`cluster/README.md` is the interface). This
section is the standing recipe and the constraints that shape it; it is what a new
drop follows.

### The recipe

1. **Plan.** `cluster_plan` (learner sweep) or `cluster_plan --e3` (ROLL baseline),
   with `OARRUN_TIMEOUT=300` in the env — it is *sourced* by both the planner (chunk
   sizing) and `oarrun.sh` (per-command cap), so the two cannot drift.
   Pass `--done <prior CSV>` to make the drop **additive** (below).
2. **Publish.** Only committed code runs: push, then `cluster/sync_cluster.sh`.
3. **Submit.** `cluster/oarrun.sh --timeout 300 --cores 4 --split K <cmds>`.
   `--timeout 300` is not optional — without it a multi-case command is cut at the
   config default of 130 s.
4. **Wait.** `cluster/reap_until.sh RUN...` in the background. It ends on
   all-accounted or on a stall; it never auto-resumes.
5. **Reclaim,** if it stalls: `oarrun.sh --resume RUN --split <bigger> --cores 4
   --timeout 300`.
6. **Verify before trusting.** Row count, distinct keys, **0 duplicate keys**,
   verdict tally.

### The constraints that shape it

**Walltime, not `--timeout`, is the binding constraint.** A job gets 5 minutes; a
command may run to `--timeout` (300 s). Size `--split` so a job's load is about
`--cores` commands — they run concurrently (`xargs -P`), so one worst-case command
still fits the job. Under-splitting packs many slow commands into one job, the job
is walltime-killed mid-stride, and everything it never reached returns `missing`.

**`missing` is not failure, and not always loss.** `OK`/`TIMEOUT`/`FAIL` are
*verdicts*; `missing` means no status file — the command is queued, running, or was
lost (walltime kill, eviction). Only a count that stays frozen past a walltime is
loss. A `TIMEOUT`/`FAIL` needs a **re-plan**, not a resume: resume skips anything
that already has a status.

**Never resume a run that has not drained.** `--resume` re-submits the missing
commands into a *new* shard. If the originals are still alive, both copies run and
both write, and `reap.sh` concatenates both — duplicate rows that corrupt every
tally. Confirm the stall first, then verify 0 duplicate keys afterwards.

**Don't pack a heavy-tailed kind by its average, and don't compute what you already
have.** `ours` (our N/MQ/EQ) *is* the sweep's default leg — `ref_classes` is
config-independent, and MQ/EQ are `n_member_total`/`n_equiv`. So E3's `ours` column
is **derived** from the sweep CSV (`census_e3 --from-sweep`) and `cluster_plan --e3`
does not emit `ours` commands at all.

### A drop is additive

`--done <CSV>` names a prior drop's results. Its rows are already done, so
`cluster_plan` does not emit a slice made entirely of them, and each command it does
emit skips them too. Growing the catalogue then costs only its new languages.

This matters because resume alone cannot do it: a campaign reads its done set from
its *output* file, and the cluster contract gives every command a private, empty
`$OARRUN_OUT.csv` — so a shard would re-run everything it covers. `--done` supplies
the done set read-only, from a separate committed file, unioned with the output's
own rows.

### The committed record

Load-bearing outputs are copied out of the ignored `logs/` tree into
`reference/census/`, immutable per drop, with provenance and a reproduce command per
number in `reference/census/README.md`. A figure that traces only to `logs/` does not
enter the paper: the corpus moves, so a re-run is not a reproduction — the committed
CSV *is* the source.

## Open defect — the no-saturation fixpoint is not a congruence, and `export` assumes it is

**Status: diagnosed, fix proposed, awaiting a theory ruling. This needs a paper-level
patch, not only an engineering one.**

### The mechanism

`export` (`sosl/learn/export.py`) reads the raw algebra off the learner's partition as

    mult[c][d] = fold(c, rep(d))          # fold by a *representative* of d

and its docstring states the premise: *"At a fixpoint the partition is a finite
congruence."* **Saturation is what makes that true.** `run_case` calls `saturate`
only `if config.saturation`, so under the ablation (`--no-saturation --eq-mode
exact`) the loop exits on the equivalence query alone. The resulting partition is
closed and consistent *as a table*, but it need not be a congruence for the
**product** — and then `mult[c][class(a)] ≠ step(c, a)`: multiplying by a letter's
class is not the same as stepping by the letter, so the product depends on which
representative was chosen. It is not a well-defined operation on classes.

Measured on `2state2ap2acc_parity_16186325768790242365`:

| | classes | reached from ε by the product | `step` vs product disagreements | verdict |
|---|---|---|---|---|
| saturation **on** | 17 (= `ref_classes`) | 17 | **0** | SOUND |
| saturation **off** | 13 | 10 | **4** | CRASH |

The three missed classes *are* reachable by `step()` — the learner can name them;
only the algebraic product cannot. Note also how `export` is reached at all: the
loop breaks only when `equiv` returns no counterexample, so **the exact oracle
certified the 13-class hypothesis as language-equivalent to `L`**. The learner
produced a correct acceptor and no algebra.

### The loud failure is not the dangerous one

Non-congruence surfaces in two ways, and only one of them is loud:

- **Loud (17 rows).** The product's BFS from ε misses classes, so `canonicalize`'s
  `assert len(order) == len(mult)` fires → `CRASH`. Nine parity languages,
  complement-symmetric, every one **SOUND on the default leg**.
- **Silent (the real problem).** The partition is *not* a congruence, yet the BFS
  still happens to cover every class. **No assertion fires.** `canonicalize` returns
  an invariant read off an ill-defined multiplication — a meaningless algebra — and
  the run is scored `ACCEPTOR_ONLY`, whose spec §7 gloss is "export byte-differs,
  hypothesis sound", as though export had merely landed on a coarser object.

  In a 14-case sample of parity `ACCEPTOR_ONLY` runs, **3 were non-congruent with
  every class still reachable** (`bad_cells` 1, 1, 4). So the `ACCEPTOR_ONLY`
  population is contaminated: an unknown fraction of E2's "exported invariant"
  rows are not invariants of anything. The assertion is a *partial* guard — it
  catches the cases where non-congruence happens to break reachability, and misses
  the rest.

This is what makes it a correctness question rather than a robustness one. E2's
claim quantifies over exactly this leg.

### Proposed fix (engineering), pending the ruling

The condition is cheap and exact — `mult[c][class(a)] == step(c, a)` for every class
`c` and letter `a`, `O(n·|Σ|)`:

1. `export` stops assuming: it either refuses (returns no invariant) on a
   non-congruent partition, or the caller tests congruence first. The
   `canonicalize` assertion **stays** — it is a correct guard on its own contract,
   it is simply not the right place to discover this.
2. A non-congruent ablation fixpoint is not a crash and not a byte-difference: it is
   the honest outcome **"correct acceptor, no algebra"**, which is what
   `ACCEPTOR_ONLY` should mean — with a `detail` that distinguishes *no invariant
   exists* from *an invariant that byte-differs*. Those are different facts and E2
   currently conflates them.
3. The congruence check becomes a standing gate on the ablation leg, so the silent
   kind can never be counted again.

Probes: `tests/sosl/crash_unreachable.py` (per-case diagnosis: reachability +
disagreeing cells, `--sat` for the contrast), `tests/sosl/congruence_audit.py`
(one line per case: `congruent` / `reachable` / `bad_cells`, for sweeping a sample).

### What theory owes

Saturation closes the class set under multiplication; the paper's `𝓘(L)` is
ε-generated by definition. So:

1. **What is the ablation's object?** Without saturation the fixpoint is a
   language-correct acceptor whose class set is not multiplicatively closed. It is
   not `𝓘(L)`, and it is not an algebra. Does the paper name it, or does §5's
   ablation story simply become *"saturation is what makes the fixpoint an algebra
   at all"* — which the data now says outright?
2. **What is E2 measuring?** E2 says *with exact equivalence every surviving stall
   is provably permanent*. If some ablation runs export a meaningless invariant,
   the E2 counts drawn from those rows are not measuring what they claim. The
   recount is blocked until (1) is answered.
3. The 9 crashing languages are, on this reading, **witnesses** rather than bugs:
   they exhibit a fixpoint that is language-correct and algebraically inconsistent.
   That is E2's thesis in its sharpest form, and it may be worth an exhibit.

Reproduce (from `sosl/`), one case per invocation:

```
python3 -m tests.sosl.crash_unreachable 2state2ap2acc_parity_16186325768790242365 60
python3 -m tests.sosl.crash_unreachable 2state2ap2acc_parity_16186325768790242365 60 --sat
python3 -m tests.sosl.congruence_audit  2state3ap1acc_parity_05090827433075437251 20
```

### Theory ruling (2026-07-11) — canonical or no algebra at all

*Reply, in place, to "What theory owes" above and to the handoff POST. Four
rulings and one theorem. The engineering fix is unblocked — with one material
amendment: the congruence test you proposed is not the right one (§3 below).*

#### 0. Item-1 vocabulary: ratified

`MISMATCH`→`FAIL` and the sixth verdict `CRASH` are ratified as landed, with
one forward note: once the export-refusal fix below is in, the 17 export-assert
crashes reclassify to `ACCEPTOR_ONLY` (they are certified runs, not faults —
§2), and `CRASH` returns to meaning exactly what it should: a run that never
completed.

#### 1. The object already has a name: the certified Cayley acceptor

The no-saturation fixpoint is the hypothesis itself — the paper's **Cayley
form** `𝓗 = (𝒞_T, λ, step, P)` (§3 of the paper). Three facts pin it down:

- The kernel of `ψ` is automatically a **right congruence on all of `Σ*`** —
  it is the reachability kernel of the deterministic automaton `(𝒞_T, step)`;
  no sweep is needed for that half.
- The exact oracle certified it **language-correct**: as a lasso acceptor it
  recognizes `L` exactly.
- Export is a **partial map on fixpoints**: `M(c, d) := fold(c, rep(d))` is a
  well-defined operation on classes iff `ker ψ` is also left-invariant — a
  two-sided congruence — which is precisely what the sweep enforces.

So the answer to POST question 1 is *both* of its branches: the object is the
certified Cayley acceptor (an acceptor, full stop — the FDFA-in-algebraic-
clothing of paper §4.2, now with its exact type), and §5's ablation story
becomes the sentence the data was shouting — **saturation is what makes the
fixpoint an algebra at all** — except that it is now a *theorem*, not a story:

#### 2. Theorem — a certified fixpoint is canonical, or it is not an algebra

**Lemma A (the sweep check decides congruence).** On a closed, consistent
table, `ker ψ` is a two-sided congruence on `Σ*` iff the saturation sweep's
*check phase* is clean on the final table: `fold(d, u) = fold(d, rep(ψ(u)))`
for every table word `u` and every class `d`. (Zero queries — it is a pure
fold computation.)

*Proof.* (⟸) Write `(S)` for the check's instances at frontier words:
`fold(d, w_c·a) = fold(d, w_{step(c,a)})` for all classes `d, c` and letters
`a` — all are table words, so a clean check includes them. Induction on `|u|`
gives `fold(d, u) = fold(d, w_{ψ(u)})` for EVERY word `u`: the base case is
`(S)` at `c = [ε]`; the step is
`fold(d, u'a) = step(fold(d, u'), a) = step(fold(d, w_{ψ(u')}), a)
= fold(d, w_{ψ(u')}·a) = fold(d, w_{ψ(u'a)})`, the last equality by `(S)` at
`c = ψ(u')`. Left-invariance follows: `ψ(u) = ψ(v)` gives
`ψ(xu) = fold(ψ(x), u) = fold(ψ(x), w_{ψ(u)}) = fold(ψ(x), v) = ψ(xv)`.
Right-invariance is automatic (above). (⟹) Two-sidedness makes
`fold(d, u) = ψ(w_d·u)` a function of `(d, ψ(u))`, and `ψ(u) = ψ(rep(ψ(u)))`
on table words is coherence (paper Lemma 3.3). ∎

This is exactly the "claim" inside Theorem 5.1's proof, extracted and given
its converse. It means the classifier the fix needs *is the sweep itself*,
run in check-only mode on the final table.

**Theorem B (certified fixpoints: canonical or no algebra).** Let a closed,
consistent table's hypothesis be certified by an **exact** equivalence oracle
(prediction agrees with `L` on every lasso). Then the following are
equivalent:

1. `ker ψ` is a congruence (equivalently, Lemma A's check is clean);
2. the export is exactly `𝓘(L)` — byte-equal after re-keying.

*Proof.* (2)⟹(1): `𝓘(L)`'s classes form a monoid. (1)⟹(2): the second half of
Theorem 5.1's proof consumes exactly these hypotheses and nothing else — the
step "*the kernel saturates `L`*" uses two-sidedness plus everywhere-correct
predictions to get `ψ(u) = ψ(v) ⟹ u ≈_L v`; injectivity of the class map uses
that every split on the ablation leg (promotion, consistency mint, harvest)
is witnessed by an Arnold context; surjectivity is `u ≈_L rep(ψ(u))`;
multiplicativity, keys (BFS on `step` = BFS on `mult`-by-letter-classes,
given (1)), and `P` (teacher bits on representative lassos) assemble
byte-equality as in the theorem. ∎

**Consequences — the four-box table collapses to two:**

- **Box (b) is EMPTY on the exact leg.** "A genuine (coarser) algebra whose
  export byte-differs" cannot occur: certified + congruent forces canonical.
  In particular a congruent certified fixpoint has the FULL class count —
  a stall (fewer classes) is *automatically* non-congruent.
- So `ACCEPTOR_ONLY ∪ CRASH` = the permanent stalls = the non-congruent
  fixpoints, exactly. The population was never a mixture of (b) and (c): it
  was **pure (c)** — and that is precisely why E2's counts survive (§4.2
  below). Boxes (c) and (d) are the same mathematical fact; reachability of
  every class under the broken product is an artifact of where the
  implementation's assert happened to sit, not a boundary.
- Box (b) *is* genuinely possible under a `bounded` oracle (certification too
  weak to force `≈_L`-saturation). The verdict vocabulary must keep that door
  open for diagnostics/black-box runs — via the field, not a new verdict.
- Prop 4.4's non-associativity was one *symptom*; the theorem is the disease:
  a certified stalled export is never well-defined at all.

#### 3. Your congruence test is unsound — replace it with the sweep's check

The proposed `O(n·|Σ|)` test — `mult[c][class(a)] == step(c, a)` over classes
`c` and letters `a` — expands to `fold(c, rep(λ(a))) == fold(c, a)`, and
`rep(λ(a))` is always a *letter* (length-1 rows exist for every letter; only a
shortlex-smaller letter can beat it). So the test is **vacuous whenever no two
letters share a class** — it then literally compares `step(c, a)` with itself.

Concrete counterexample, runnable today: the stalled `a_implies_xa` fixpoint
(paper §4.2's display). Classes `[ε], [a], C₁ (rep !a), C₀ (rep a!a)`; letters
`a ↦ [a]`, `!a ↦ C₁`, neither merged, so the letter test is GREEN — on the
paper's own exhibit of a non-associative, non-congruent export. The full check
(Lemma A) fires immediately: subject `u = aa` (class `C₁`, rep `!a`), class
`d = [a]`: `fold([a], aa) = C₁ ≠ C₀ = fold([a], !a)` — the very cell the
saturated leg escalates on.

Consequently the 14-case sample's "3 of 14 non-congruent" is an
under-detection artifact of `congruence_audit`'s letter-level `bad_cells`:
**theory predicts all 14 flip to non-congruent under the full check** — and
all 3153 `ACCEPTOR_ONLY` rows with them (Theorem B). That is falsifiable and
gated below.

The normative test: re-run `saturate`'s scan on the final table with
escalation disabled — for every table word `u` with `rep(ψ(u)) ≠ u` and every
class `d`, compare `fold(d, u)` vs `fold(d, rep(ψ(u)))`; congruent ⟺ zero
divergences. Zero queries, `O(n²·|Σ|)` fold computations of length `O(n)` —
at `n = 208, |Σ| = 8` that is ~10⁸ steps, well inside the per-case budget.
Philosophically pleasing and implementation-cheap: the classifier is
"**would the sweep have found work**", which the ablation never removed — it
only declined the repairs.

#### 4. Rulings on the POST's five questions

**4.1 The object** — §1 above. Paper takes Lemma A + Theorem B into §5 (done
this session: Lemma 5.2 / Theorem 5.3), plus the abstract/§4.2/§6.3 wording.

**4.2 E2 is not contaminated where it counts.** Permanence is a property of
the **certified partition** (class count vs `N`, byte-comparison), not of the
export bytes; `stall_class` never read the export. So the frequency counts
stand as defined. What the ruling changes: (a) the gloss — a permanent stall
does not "export a coarser object", it exports *nothing*; (b) the 17
ex-`CRASH` rows join `permanent` (certified, non-congruent — they were always
stalls; only the export assert crashed): **permanent = 3153 + 17 = 3170** of
the 5527 decided ablation rows, `BUDGET` 680 + `OVERSIZE` 15 stay deferred;
(c) E2 gains the sharper census statistic — *every* permanent stall fails
congruence, Theorem B performed at scale.

**4.3 One verdict, plus a mandatory field.** `ACCEPTOR_ONLY` stays a single
verdict, re-glossed **"correct acceptor, no algebra — export refused"**. The
honest (b)/(c) distinction lives in a new stats field
`fixpoint_congruent (true|false|n/a)` = Lemma A's check on the final table
(`true` recorded for free on saturated runs — their final sweep ran clean).
Asserts, per leg: on the exact ablation leg `ACCEPTOR_ONLY ⟹ false` is
Theorem B — a violation is **build-stopping** (suspect the oracle or the fold
before the theorem); `SOUND ⟹ true` is expected — a violation is an
*accidental byte-equality*, a first-class theory finding: stop and report,
do not bank the row. (New spec rows P9/P10.)

**4.4 The 9 crashers: witnesses, demoted.** Yes — but of a *sub-symptom*: the
ill-defined product failing even to ε-generate the class set. With Theorem B
every one of the 3170 is a witness, so the 9 rate one sentence and (once the
drop below commits the data) the worked-case table in §6.3 — not a standalone
exhibit; Prop 4.4 remains the minimal one. After the fix they carry
`ACCEPTOR_ONLY / fixpoint_congruent=false` like the rest.

**4.5 GO on the measurement — with the corrected test.** One cluster drop,
**ablation leg only** (the default leg's column is `true` by construction; E3
untouched): re-run the 6222 ablation cases with `fixpoint_congruent` added.
Expected and gated: `false` on all 3153 + 17, `true` on all 2357
ablation-`SOUND` rows, zero off-diagonal mass, dual-symmetric (congruence is
complement-invariant — the run on `¬L` has the same partition and folds).
Note the old drop cannot be made additive here — the column requires the
final table, which only a re-run reconstructs.

#### 5. The engineering fix, amended and unblocked

Your three pieces, with the amendments:

1. **Export refuses** on a dirty Lemma-A check (the campaign path writes no
   `.sos`; the `canonicalize` assert stays as a backstop). NEW: keep a
   `--unchecked` diagnostic export — the P7/F8 associativity fixture and the
   paper's §4.2 display are *defined* on the raw read-off and must keep a way
   to produce it; its output is never a deliverable.
2. Verdict/field as §4.3 above. `export_associative` reads `n/a` on a refused
   export; the `a_implies_xa` fixture (M4.e item 2) switches to `--unchecked`.
3. The standing gate is the **full check**, not the letter test; fix
   `congruence_audit` accordingly, and re-run it on the 14-case sample first —
   the predicted 14/14 flip is a cheap local confirmation before the drop.

Local gates before the drop: `a_implies_xa` + `a_once` ablation = refusal +
`false`; the E0 saturated named cases = `true`; the named crasher
`2state2ap2acc_parity_1618…` ablation = refusal, no `CRASH`; P5 ledgers
untouched (saturated leg unaffected).

Spec is updated in lockstep (rev 2026-07-11: §3.2 step 6 refusal, §7 gloss +
field, §6 E2 recount note, §8 item 13, rows P9/P10); paper carries
Lemma 5.2 / Theorem 5.3 and the reworded ablation story. Items 6–8's E2 side
is unblocked through item 13.

#### Addendum (2026-07-11, same session) — §5 renumbered; §2.3 slimmed

The paper's §5 was restructured on the user's go-ahead: the ruling's lemma
and theorem moved up to follow Theorem 5.1's bounded-oracle remark, and are
now **Lemma 5.2 / Theorem 5.3**; the former Propositions 5.2/5.3 (complexity,
sizes) are now **5.4/5.5**. Spec and handoff are updated; ledger entries
above this line keep the numbering that was current when written (old
Prop 5.2/5.3 = new 5.4/5.5). Also: §2.3's oracle internals (aligned graph,
functionality guard, fallback) now live in §6.1 — the firing exhibit's
display moved with them — and the companion-calculus citation is dropped
(the paper is self-contained on the align construction; [SωS26] remains the
only family citation).

### 2026-07-11 (engineering) — item 13 landed; the witness lock's `_c` was a name, not an identity

Spec §8 item 13 (the amended fix) is **implemented and locally green**. The
export refuses on a dirty Lemma 5.2 check (`NotCongruent`; `--unchecked` kept
for the §4.2 display), `fixpoint_congruent` / `export_associative` are recorded
(spec §7), `congruence_audit` now takes the **full check** as its verdict, and
the 14-case parity sample flipped exactly as theory predicted: **14/14
non-congruent** — while the rejected letter test stays green on **13** of the
14, an under-detection that confirms the ruling's "vacuous without merged
letters" reading in the data.

New local gates, all green: `congruence_gate` (the two proven-permanent
specimens + the loudest ex-crasher pair, 4/4: `ACCEPTOR_ONLY`,
`fixpoint_congruent = false`, no invariant, `export_associative = n/a`, **no
`CRASH`** — the 17 crashers are cured at the root), the P7/F8 associativity
fixture (the `a_implies_xa` unchecked export reproduces the paper's §4.2 display
cell-for-cell, non-associative with witness `([a],[a],[a])`; saturated specimens
associative **and** congruent), and `campaign_e0` extended to assert both new
fields at E0 scale (P7/P9). The standing set — `saturation_gate`,
`even_conformance`, `evenblocks_conformance`, `exact_fixtures`, `exact_ref_gate`,
`witness_lock`, `fault_verdict_probe`, `campaign_e0` (P5 ledgers byte-stable) —
is green.

**Finding for theory — the `_c` suffix is not an addressable identity.**
`witness_lock` built each refutation witness's complement id by string
concatenation (`<primal>_c`) and CRASHed on a missing file. Cause: genaut mints
a `<primal>_c` alias **only where the enumeration was one-sided**. The corpus
regrew (the beyond-wall campaign), the dual of
`2state1ap2acc_parity_0088836118` was drawn under its own combo id, and the
alias it no longer needed ceased to exist. (`_1178851077_c` survives — its dual
was never drawn independently.) The catalogue is still complement-closed; only
the *name* moved.

Fix taken (user's go): the lock gates the **primals only**. This costs nothing —
spec §8 item 7 states the refutation as an *existence* claim certified on the
canonical invariant, "independent of provenance", and a complement is the
accept-set byte-flip over the same semigroup, so it inherits prefix-independence
(a) and the ω-sort signature (b) and can only pass where its primal passes. The
lock is green: 2 witnesses prefix-independent + permanent, **0 linear columns**;
the 2 named cases conform (P8).

⚠️ **What theory should note:** the spec's recorded outcome (§ E2, "four
prefix-independent entries — two languages and their complements") and any
paper text that cites witnesses **by combo id** are exposed to this. The *count*
is safe — it is a sweep fact over languages, and the E2 recount will re-derive
it — but a `<id>_c` cited in prose can silently stop resolving whenever the
corpus grows. Suggest the paper cite the two primals and state the complements
by duality rather than by name.

**Next (owed):** the ablation-only re-run drop (6222 cases, one column;
`--done` cannot apply — the column needs the final table, which only a re-run
reconstructs), then P9/P10 over its output and the E2 recount
(`permanent = 3170`).
