# SoS Learner — Implementation and Experimentation Specification

**Status:** specification / declaration of intent. Everything below is to be
implemented; nothing below exists yet except where explicitly marked
*(exists in-repo)*.

**Revision 2026-07-06 (theory thread).** Triggered by the M2 findings in
`sos_learning_report.md` (the reply appended there explains the *why* of each
change). New: section 1.1 (identity convention, normative), milestone M2.5
(section 8), section 9 (expected failures — read it before filing any bug).
Corrected: sections 3.3 and 5 item 6 (pre-saturation exports are diagnostic
only; acceptor checks target the Cayley hypothesis until saturation exists).

**Revision 2026-07-07 (M3 integration).** M3 is done (`sos_learning_report.md`). One
normative correction fed back from the implementation: section 3.2 step 4,
first escalation branch, omega sort — the mint is `(x.r, y.r)`, NOT the bare
`(x.r, y)` (rationale at the step; without it the `GF(aa)` sweep never
converges). The section 8 M3 gate's counterfactual column is updated to
match.

**Revision 2026-07-07b (M4 preparation).** Section 6 sharpened against the
M3 state (corpus manifest; per-experiment design notes, including how ROLL
equivalence queries are answered); section 7 gains three fields
(`n_classes_initial`, `stall_class`, `cex_policy`); section 8 splits M4 into
ordered sub-gates M4.a–M4.d; section 9 gains rows P5 / F6 / F7. The M3
probes named in `sos_learning_report.md` are the campaign's starting points, not
throwaways.

**Revision 2026-07-08 (M4.a integration).** M4.a is done (`sos_learning_report.md`:
driver + E0 gate green). One normative correction fed back from the E0 table,
which mislabelled the two proven-permanent specimens `transient` on their
saturation-on rows: `stall_class` is now pinned as a **per-language** property
read from the **no-saturation + exact leg alone**, and every saturation-on run
carries `stall_class = n/a` — never `transient`/`permanent` (section 7,
tightened; section 6 E2; new section 9 row P6). This must be corrected before
E2 aggregates, or the frequency table contradicts Proposition 4.4.

**Revision 2026-07-08b (M4.b + census-E2 + E5 integration).** All three landed
(`sos_learning_report.md`), the P6 stall_class fix is adopted, and the results are in
the paper (§6). Recorded here: E5's `first` policy coincides with `minimal`
for the minimal-order oracles (§6 E5, so E5 is two series not three); the
census-backed E2 over the frontier shapes (`2state1ap1acc` + parity twin, 258
languages) is SOUND on all 258 and enumerates 44 permanent-stall languages,
promoting §4.2's finding from two specimens to a family. Still open toward M4
close: E3 (ROLL, M4.c) and the full-census N-spread for E1's scatter; and a
per-structural-feature breakdown of the 44 permanent languages would close the
last §6.3 frequency-table TBD in the paper.

**Revision 2026-07-08c (M4.c / E3 delivered, RABIT accepted).** The E3 baseline
landed on the named cases, and it deviated from this spec's original plan: ROLL
is certified by its **native RABIT** equivalence against a state-based Büchi
presentation, not by our teacher's bounded oracle. The deviation is *accepted*
as the fairer design — both learners now certify exactly, by different
mechanisms — and this spec is brought into line: the §6 E3 design note and the
row-F6 text are rewritten accordingly, and the paper's §6.4 states the size
comparison as competitive-within-`N + N²` (never "smaller", which 5.3(b)
forbids) with the LTL-definability read-off as the sole capability
differentiator. Open toward M4 close: census-wide ROLL medians and the
full-census N-spread for E1's scatter.

**Revision 2026-07-08d (E2 structural buckets; necessity downgraded).** The E2
renderer now cross-tabulates the 44 permanent census languages by
prefix-independence and acceptance type (`census_e2_exhibits`,
`prefix_independence_check`): all 44 prefix-dependent, all Büchi. This closes
the §6.3 frequency-table TBD as **census data**. One theory correction: the
report framed permanence as *implying* prefix-dependence ("the language must be
prefix-dependent"); that necessity is **not** established — a left factor inside
an ω-power loop is a rotation, not a deletable prefix (paper §2.2), so
prefix-independence does not remove all left contexts, and the natural proof
does not close. The paper carries it as a regularity + intuition, open. Next E2
ask (M4.b tail): the same cross-tabulation at deeper census shapes, to promote
the regularity toward a theorem or refute it with one prefix-independent
permanent stall.

**Revision 2026-07-08e (theory review pass — consistency + paper-close
deliverables).** A theory review of `sos_learning.md` against the campaign
data landed three things here. (1) The paper now *displays* the stalled
`a_implies_xa` export next to the canonical algebra (§4.2) and states its
multiplication table is **non-associative** —
`([a]·[a])·[a] = [!a] ≠ [a!a] = [a]·([a]·[a])` — with the `a^ω` verdicts of
both specimens derived from it. That display is paper-anchored data: it gains
a stats field (section 7, `export_associative`), two harness rows (section 9,
P7/F8), and a fixture (section 8, M4.e item 2). (2) One **blocker-grade
audit** is opened: the census-E1 per-N table reports 32 languages at `N = 2`,
but `|S(L)₊¹| = 2` forces every lasso onto the single linked pair, i.e.
`L ∈ {∅, Σ^ω}` — at most two languages. Either `ref_classes` excludes the
identity (then every `N` axis the paper cites is off by one) or language
dedup is incomplete across shapes (then "541 languages" overcounts). Resolve
before any further census aggregation (section 8, M4.e item 1). (3) The
remaining paper TBDs are promoted to explicit deliverables (M4.e items 3–6);
the paper side has already integrated the E0 named-case metric rows into
§6.2, restated the teacher's equivalence-certification ladder (default runs
certify `bounded:8`, backed by byte-equality; exact on the ablation leg), and
scoped the census fill-envelope claim (median fill exceeds `N²·|Σ|` by up to
~30% at `N = 3–5`; inside from `N = 6` up — the paper no longer claims
"within" unqualified).

**Revision 2026-07-08g (witness lock banked; 7d retired by theorem;
reproducibility floor).** The witness lock (section 8 item 7 a–c) is
delivered and green on all four prefix-independent witnesses; the paper's
§6.3 refutation is closed on the positive side. Item 7(d) — an
exhaustive-shape witness — is **retired as provably empty**: paper Lemma 4.8
(a prefix-independent closed or open language is trivial) rules out every
`c = 0` shape including the unfinished `3state1ap0acc`, all other exhaustive
shapes are completely swept with zero prefix-independent permanent stalls,
and the smallest shapes not ruled out lie beyond the enumeration wall
(`≥ 4.3·10⁹` ids). Replaced by gate (d′): assert the exhaustive negative,
per shape, at sweep completion. New section 8 item 9, normative: the report
must be self-sufficient — validated campaign outputs (raw CSV, summaries,
rendered tables, claim-bearing `.sos`) are copied out of `logs/` into a
curated committed `reference/` tree, and every reported figure cites its
committed source; `logs/`-only numbers do not enter the paper.

**Revision 2026-07-08h (exact oracle re-based on the calculus; the closure
demoted).** The exact oracle's transformation closure of `D` is exponential
in `D`'s *presentation* — it is what `OVERSIZE` measures — while the
language's own algebra is the minimal decision structure and the teacher
already holds it. Re-specified (section 3.2 `exact`): equivalence is decided
against the reference invariant `R = 𝓘(L)` as symmetric-difference emptiness
in the SoS calculus — complement is the free `P`-flip, **align** generates
the `≤ N_H·N_R` hypothesis×reference pairs lazily (the memoized DAG), and a
disagreeing cell's canonical witness lasso is the shortlex-least
counterexample. Polynomial; `D` is out of the equivalence loop entirely.
The closure form survives only for referenceless targets (E6), with lazy
exploration + subsumption, where `OVERSIZE` stays the honest verdict. New
section 8 item 10: implement, cross-check against the closure oracle on the
named cases, re-run the deferred `OVERSIZE` classifications; after that,
`OVERSIZE` on the census is a defect (row F9 rescoped).

**Revision 2026-07-09 (item 10 delivered; three corrections adopted; the
functionality guard; `bounded` retired from the campaign legs).** Item 10 is
delivered (`sos_learning_report.md` 2026-07-09) and its three corrections are
adopted: (1) section 3.2 `exact`, per-cell verdicts — the hypothesis side is
its **prediction on the cell's canonical lasso**, never a bare class-pair
read (which forgets the loop word stabilization iterates; F3-violating —
the `gf_aa_parity` finding); (2) the teacher *holds* the reference
(constructor parameter; built once from `D` and cached when absent;
referenceless targets take the closure fallback); (3) the five deferred
`OVERSIZE` cases are decided (2 permanent / 3 transient) and enter E2's
counts. One theory addition is **normative**: certification and
counterexample-minimality of exact-by-reference are theorems *conditional on
the aligned graph being functional* — no two nodes share their `R`-component;
equivalently, non-identity node count `= N_R` — because the one-word-per-node
argument needs the hypothesis fold to factor through `≈_L` on all words,
which witnessed splits guarantee only on table words. The oracle asserts
functionality on the built graph at every query; a firing assert is a
recorded outcome and a first-class theory finding, not a bug (fall back to
the closure oracle; new section 9 row F10; F9 rescoped accordingly). A
returned counterexample is sound without the guard (both verdicts are
evaluated on the concrete keyed lasso). With the guard in place the
default escalation drops `bounded`: now `reps`, then `exact` —
`eq_certification = exact` on every campaign row; `bounded` survives for
black-box teachers and diagnostics only. New section 8 item 11 (guard,
re-runs, default-leg switch, the `075976` dual).

**Revision 2026-07-09b (the guard fires; conjecture refuted; retraction).**
The functionality guard is implemented (item 11a) and **fires on
learner-reachable tables** — the factoring conjecture is refuted
(`2state1ap2acc_parity_2195145216`, ablation leg: 8 firings, 20–24 aligned
nodes over 17 reference classes, every fired query decided by the closure
fallback), and sweep-clean tables fire too, so left-saturation does not buy
functionality and the guard is irreducible. Consequence adopted: `013908`
and `075976` guard-fire and their closure fallback hits the cap, so the
**five `OVERSIZE` cases stay deferred** — the 2026-07-09 instruction to bank
them into E2 is void, and the paper's counts are reverted (1180). The
default escalation gains a cap-escape (section 3.2): a guard-fired query
goes to the closure; a capped closure falls to `bounded:8` on the default
leg (recorded; byte-equality still validates) and records `OVERSIZE` on the
ablation leg. Row F10 rewritten to the observed reality, with one new hard
edge: a firing on the *final* certifying query of a `SOUND` run is a defect
(a canonical table's fold is the syntactic morphism). Item 11 updated in
place with the new sub-asks (per-leg firing tallies; the final-query assert;
a committed firing exhibit with two witness words).

**Revision 2026-07-09c (retraction accepted; fallback localization
approved).** The unguarded by-reference ablation sweep disagreed with the
committed closure drop on 74 of 3796 jointly-decided rows — every one a
guard firing, so the sweep is void and not banked; conversely, zero
disagreements on guard-green rows: the conditional certification theorem
passes its first campaign-scale test, and the committed closure drop stands
untouched. With the closure fallback now the cost centre (~33 → ~2.5
cases/s once firings begin), section 8 gains item 12 — the localized
fallback: quiet cells (loop-power orbit and stabilized stem class avoiding
the split reference classes) remain decided by their keyed lasso even on a
fired graph, and only the split-touching residue needs the closure —
instrumentation-first, gated byte-identical against the unlocalized
fallback. Item 11's remaining opens (sweep tallies, E2 recount, item-8
dual-symmetry assertion) land with the completed guarded sweep.

**Revision 2026-07-11 (theory ruling — the ablation's object; export refusal;
the congruence gate).** The open defect (`sos_learning_report.md` "Open
defect" + "Theory ruling (2026-07-11)") is ruled. (1) The no-saturation
fixpoint is the **certified Cayley acceptor** — the hypothesis itself; export
is a *partial* map, defined exactly on congruent fixpoints. Paper Lemma 5.4 /
Theorem 5.5: with an exact oracle a certified fixpoint is canonical **or its
partition is not a congruence** — "export byte-differs while a genuine algebra
exists" is impossible on that leg, so `ACCEPTOR_ONLY` re-glosses to "correct
acceptor, no algebra" (one verdict, no split; section 7). (2) The proposed
`O(n·|Σ|)` letter test is **unsound as a certifier** — vacuous whenever no two
letters share a class; the stalled `a_implies_xa` export passes it — the
normative congruence test is the saturation sweep's **check phase** on the
final table, zero queries (section 3.2 step 6). (3) `export` refuses on a
non-congruent partition; a `--unchecked` diagnostic export survives for the
P7/F8 fixtures. New stats field `fixpoint_congruent` (section 7); new rows
P9/P10 (section 9); new section 8 item 13 (the fix, the congruence-column
ablation re-run, the E2 recount folding the 17 ex-`CRASH` rows into
`permanent` = 3170). The 2026-07-10 verdict vocabulary (`MISMATCH`→`FAIL`,
new `CRASH`) is **ratified**.

**One-line goal.** Build `sos_learn`, an active-learning tool that reconstructs
the *syntactic omega-semigroup invariant* of an unknown omega-regular language
from lasso membership queries and equivalence queries — plus the harness that
proves it sound and the experiment suite that measures it.

---

## 1. Objects (self-contained)

**Alphabet.** `Sigma = 2^AP` for a set of atomic propositions `AP`. A letter is
a valuation of `AP`.

**Lasso.** A pair `(u, v)` of finite words, `v` non-empty, denoting the
ultimately-periodic infinite word `u . v^omega` (stem `u`, loop `v` repeated
forever). Two omega-regular languages are equal iff they agree on all lassos,
so lassos are the only words any component ever exchanges.

**Target language.** An omega-regular `L` over `Sigma`, presented to the
*teacher* as a deterministic, complete, transition-based Emerson-Lei automaton
`D` in HOA format (states `Q`, initial state, total transition function, marks
on transitions, acceptance = positive Boolean formula over `Inf(c)` / `Fin(c)`).

**Syntactic congruence.** Finite words `p, q` are congruent for `L` when they
are interchangeable in both context shapes:

```
  (linear)     for all x, y in Sigma*, t in Sigma+ :  x.p.y.t^omega in L  <=>  x.q.y.t^omega in L
  (omega)      for all x, y in Sigma*               :  x.(p.y)^omega in L  <=>  x.(q.y)^omega in L
```

The quotient is a finite monoid (with the empty word as adjoined identity).

### 1.1 Identity convention (normative)

The class set is: the congruence classes of the **non-empty** words, plus a
**fresh** adjoined identity class `[eps]` — always, even when some non-empty
word already acts neutrally. Consequences, all mandatory:

- The class count is (number of non-empty-word classes) + 1, and it must be
  the same from every automaton presenting the same language
  (presentation-independence is what makes `.sos` byte-equality a language
  test).
- `[eps]` is never merged with the class of any non-empty word. This holds
  even for a word `w` that acts neutrally (`w.u ~ u` and `u.w ~ u` for all
  non-empty `u`): such classes exist — `[aa]` in `Even` acts as the identity
  on every non-identity class — and they remain ordinary classes of their
  own, keyed by their shortlex-least non-empty word. There is no
  contradiction with `[eps]`: `M(c,[eps]) = c` and `M([eps],c) = c` hold for
  every `c`, including a neutral one.
- `[eps]` can never occur in a linked pair. (Why, for the assert: a linked
  pair needs `M(s,e) = s`; if `s = [eps]` then `M([eps],e) = e`, forcing
  `e = [eps]`, and an empty loop is not a lasso. So enumerate pairs over
  non-identity classes only, and assert `s != [eps]` and `e != [eps]`.)
- Every non-identity class therefore has a non-empty key, so every
  representative lasso `key(s).key(e)^omega` is well-formed. The whole
  prediction / P-cache design relies on this property.
- The **reference builder** must realize the identity as a fresh element,
  not as the enriched monoid's identity element: in some presentations a
  letter's enriched element literally equals the enriched identity (e.g.
  `!a` in a 1-state automaton for `GF a` — same state map, no marks), and a
  quotient over elements alone then silently merges `[!a]` into `[eps]`,
  making the class count presentation-dependent. Correct: quotient only the
  images of non-empty words; adjoin the identity as a fresh element; a word
  whose element equals the enriched identity is an ordinary class (key `!a`
  for `GF a`, giving 3 classes from every presentation). The same collision
  sits inside the census flagship: in the 2-state `EvenBlocks` presentation
  the element of `aa` equals the enriched identity, and the buggy merge is
  what produced the previously-published count of 7 — the correct count is
  **8**, with `aa` its own class, acting neutrally on the word classes.

**The invariant `I(L)`.** The tuple `(C, key, lambda, M, P)`:

- `C` — the finite set of congruence classes;
- `key : C -> Sigma*` — the shortlex-least word of each class (canonical);
- `lambda : Sigma -> C` — class of each letter;
- `M : C x C -> C` — the multiplication table;
- `P subset C x C` — the accepting *linked pairs*: pairs `(s, e)` with
  `M(e,e) = e`, `M(s,e) = s`, such that `key(s).key(e)^omega in L`.

Membership of any lasso `(u, v)` is decided from `I(L)` alone: fold `u`, `v`
to classes, iterate `v`'s class to an idempotent `e`, set `s = [u].e`, accept
iff `(s, e) in P`.

**Serialized format (`.sos`, v1).** Plain text, canonical, byte-comparable:

```
SOS v1
ap: <ap names, space-separated>
classes: <n>
<id>  <key as ;-separated letters, 'eps' for empty>
...
letters: <letter>-><id>  ...
mult:
  <n x n table of ids, row-major, header row/col of ids>
accept:
  <one line per pair: s_id e_id>
```

Two languages over the same `AP` are equal iff their `.sos` files are
byte-equal. A *reference builder* for `I(L)` from an HOA automaton
*(exists in-repo)* is used by the teacher and the validator; the learner never
calls it.

---

## 2. Tool I/O

### 2.1 `sos_learn` (the deliverable)

```
sos_learn --teacher hoa:<file.hoa>            # white-box teacher (default)
          [--teacher proc:<command>]          # black-box teacher over pipes
          [--out learned.sos]                # learned invariant (default stdout)
          [--stats stats.json]                # metrics (see section 7)
          [--audit audit.log]                 # full query/decision transcript
          [--no-saturation]                   # ablation switch (experiment E2)
          [--eq-mode reps|bounded:<B>|exact]  # equivalence strategy (section 3.2)
          [--budget-queries N] [--budget-seconds S]
          [--seed N]                          # ties in tie-breaking only; runs are
                                              # otherwise deterministic
```

Exit codes: `0` success (invariant emitted); `2` budget exhausted (partial
stats still emitted, no invariant); `3` teacher protocol error; `4` internal
invariant-violation (assertion failure — always a bug, never masked).

### 2.2 Black-box teacher wire protocol (mode `proc:`)

Line-oriented JSON over stdin/stdout of the spawned process:

```
  -> {"op":"member", "stem":[<letters>], "loop":[<letters>]}
  <- {"ok":true, "value":true|false}
  -> {"op":"equiv", "sos": "<serialized hypothesis, section 2.3>"}
  <- {"ok":true, "value":"eq"} | {"ok":true, "value":"neq", "stem":[...], "loop":[...]}
```

Letters are serialized as sorted lists of true APs. The white-box teacher
implements the same interface internally.

### 2.3 Hypothesis serialization

Mid-learning hypotheses are *not* full invariants (no multiplication table is
trusted before the end). A hypothesis is shipped as its **Cayley form**:

```
CAYLEY v1
ap: ...
classes: <n>          # with keys, as in .sos
step:
  <n x |Sigma| table: step(class, letter) = class>
accept:
  <pairs (s, e) with cached verdicts>       # the P-cache, possibly partial
```

Prediction semantics (normative, used by teacher and learner identically):
fold the literal stem and loop through `step` from class `[eps]`; find least
`k <= 2n` with `fold(loop^2k) = fold(loop^k)`; answer the cached/queried bit
for the pair `(fold(stem.loop^k), fold(loop^k))`.

---

## 3. Components

### 3.1 Teacher (white-box)

- **member(u, v):** simulate `D` on `u`, then on `v` repeated from the reached
  state until the (state, position-in-`v`) pair repeats; collect the marks on
  the closed cycle; evaluate the Emerson-Lei condition on that mark set.
  Cost: `O(|u| + |Q|.|v|)`. No external tools, no timeouts.
- **equiv(H):** three strategies, combinable (see `--eq-mode`):
  - `reps` — audit lassos built from all pairs of hypothesis keys and all
    pairs of reference keys (`key(s), key(e)` for linked `(s,e)`); fast,
    incomplete; used as a first pass.
  - `bounded:<B>` — exhaustive over lassos with `|u| <= B`, `|v| <= B`,
    enumerated via the product of `D` and the hypothesis `step` automaton so
    that only distinguishable candidates are materialized; doubling `B` on
    demand. Complete in the limit.
  - `exact` (revised 2026-07-08h — **exact-by-reference**; the closure form
    is demoted to referenceless fallback). Decision by the SoS calculus
    against the reference invariant `R = 𝓘(L)` the teacher already holds
    (the corpus `.sos`; `D`'s only remaining role is to have built it once):
    complement is the free flip `P ↦ P^c`, and equivalence is the emptiness
    of the symmetric difference `(H ⊗ R̄) ∪ (H̄ ⊗ R)`. Procedure: **align**
    the hypothesis's Cayley graph with `R` — the pair set of
    `(fold_H, ψ_R)` values generated by the letters from the two identities,
    built lazily and memoized, `≤ N_H·N_R` nodes, `O(N_H·N_R·|Σ|)` edges —
    then scan the (stem cell, loop cell) grid for a cell where the two
    verdicts differ; that cell's canonical witness lasso, built from the
    shortlex keys, is the counterexample, and an all-agree scan is the
    certificate. Per-cell verdicts (corrected 2026-07-09): `H`'s is its
    **prediction on the cell's canonical lasso** `key(c)·key(d)^ω`,
    stabilizing the literal keyed word exactly as any prediction does —
    NEVER the P-cache bit of the bare class pair, which has forgotten the
    loop word that stabilization iterates and answers a different question
    (F3-violating counterexamples; the mid-run Cayley form has no
    multiplication to absorb a loop into a stem with, which is also why no
    linked-pair law is ever applied on the `H` side); `R`'s is algebraic,
    `(s·e^π, e^π) ∈ P_R` with `e^π` the idempotent power. Polynomial
    throughout; the exponential transformation closure of `D` never enters.
    Three normative points: (i) aligned keys are shortlex-least, so the least
    disagreeing cell yields the shortlex-least counterexample — the
    minimal-order guarantee that E5 and run determinism depend on is a
    stated requirement, not an accident of the closure; (ii) certification
    base: the trust anchor is `R` (the construction's output, independently
    cross-checked by the census byte-equality gate), not a product with
    `D` — same certification level, different mechanism (the F6/RABIT
    precedent); (iii) the **functionality guard** (2026-07-09) — one keyed
    lasso decides a cell only if prediction is constant on the cell, which
    holds iff the aligned graph is *functional*: no two nodes share their
    `R`-component (equivalently, non-identity node count `= N_R`'s
    non-identity class count; the graph is the full image
    `{(fold_H(w), ψ_R(w)) : w ∈ Σ*}`, so the check verifies the needed
    factoring on ALL words, not a sample). The oracle asserts this on the
    built graph at every query. Certification and minimality (i) are
    theorems *conditional on the assert*; a returned counterexample is
    sound without it (both verdicts are evaluated on the concrete keyed
    lasso). A firing assert is NOT a bug: record it, fall back to the
    closure oracle for that query, and hand the graph to the theory
    thread — it is a counterexample to the factoring conjecture (row F10).
    (A cell-level localization of this fallback was proved sound but
    refuted by instrumentation and is NOT to be built — split classes are
    absorbing in the orbit structure, and the closure's cost and cap live
    in its build, not its scan; section 8 item 12, CLOSED. The one open
    performance lever is incremental closure reuse across a run's
    queries, gated by the build-vs-scan measurement named there.)
    Referenceless targets (E6) fall back to the previous form —
    the product of `D` with the hypothesis's transformation closure, now
    explored lazily with pointwise subsumption (Ramsey-based inclusion à la
    Fogarty–Vardi / Abdulla et al.; `D` deterministic makes domination a
    cheap pointwise test) — where `ExactTooLarge`/`OVERSIZE` remains the
    honest verdict. Default (2026-07-09; amended 09b now that the guard is
    known to fire): `reps`, then `exact` under the guard; a guard-fired
    query is decided by the closure; if the closure exceeds its cap, the
    default leg falls back to `bounded:8` (recorded in `eq_certification`;
    byte-equality still validates the run end-to-end) while the ablation
    leg records `OVERSIZE` (permanence is undecidable below the cap —
    a bounded answer cannot certify a stall). `bounded` survives as that
    cap-escape, for black-box teachers, and for diagnostics; no campaign
    row certifies by it except recorded cap-escapes.
  - Whatever strategy fires, the returned counterexample is minimized
    (shortest stem, then shortest loop, then shortlex) before being returned —
    determinism of the whole run depends on this.
- The teacher records which strategy certified each `eq` answer; the stats
  file exposes it (a run certified only by `bounded` is flagged).

### 3.2 Learner core

Data structures (the engineer owns the concrete layout; these are the
contracts):

- **Table.** Rows = a set of *access words* (`eps`, the letters, and promoted
  frontier words `rep.letter`); frontier = `rows . Sigma`; two column lists,
  `E_lin` of triples `(x, y, t)` and `E_om` of pairs `(x, y)`; a bit matrix
  `entry[word][column]` where the entry of word `p` is
  `member(x.p.y, t)` for a linear column and `member(x, p.y)`-style
  `member(x.(p.y)^omega)` — i.e. `member(x, p.y)` as a lasso — for an omega
  column. (`eps` never enters any class comparison; it is a permanent
  singleton class, the fresh identity of section 1.1. No non-empty word may
  ever be merged into `[eps]` — otherwise a loop can fold to `[eps]` and the
  P-cache is asked for the representative lasso `key(s).eps^omega`, which
  does not exist. Any "eps-merge" shortcut is wrong even when the merged
  word acts neutrally; see section 9 note on convention changes.)
- **Partition.** Classes over rows+frontier from the bit rows; per class a
  representative `rep(c)` = shortlex-least row; `step(c, a)` = class of
  `rep(c).a`.
- **Fold.** `psi(w)` = letterwise `step` from `[eps]`. Invariant (asserted in
  debug builds): `psi(p) == class(p)` for every table word `p`.
- **P-cache.** Map `(s, e) -> bit`, filled lazily by
  `member(key(s), key(e))`; never invalidated (keys are words; if classes
  split, new keys mean new cache lines — stale lines are dead, not wrong).

Procedures (all query counts logged by phase):

1. **fill** — complete missing entries (membership queries).
2. **close** — promote any frontier word not matching a row class.
3. **consist** — if `p == q` (same class) but `p.a != q.a`, *mint* the column
   that migrates the letter: `(x, a.y, t)` from a separating linear column
   `(x, y, t)` of the successors, `(x, a.y)` from an omega one. (Bookkeeping
   identity: the entry of `p` at the minted column equals the entry of `p.a`
   at the source column — assert it.)
4. **saturate** — for every table word `p` with `rep(class(p)) = r0 != p`, and
   every class `d`: compare `fold(d, p)` vs `fold(d, r0)` (zero queries; a
   `fold(d, w)` starts the letterwise fold at `d`). On a mismatch
   `c_a != c_b`, *escalate*:
   - let `kappa` be a column separating `rep(c_a)` from `rep(c_b)` — one must
     exist; if several do, take the FIRST in creation order (the initial
     omega column, then minted columns in mint order — pinned for
     reproducibility); query the two bits of `r.p` and `r.r0` under `kappa`'s
     context, where `r = rep(d)`;
   - if the bits differ: mint the column that reproduces "`r.w` under
     `kappa`" as a bit on the bare candidate `w` — and the two sorts differ
     here. Linear `kappa`: the candidate sits in the finite prefix, so `r`
     prepends there — `(x.r, y, t)`. Omega `kappa`: the candidate rides in
     the period, and peeling one `r` off the repeating block
     (`x.(r.w.y)^omega = x.r.(w.y.r)^omega`) means `r` must seed BOTH the
     prefix and the period suffix — `(x.r, y.r)`. NEVER the bare `(x.r, y)`:
     that keeps the period `w.y` and need not separate at all — a
     prefix-independent language swallows the prefix, and with the bare form
     the `GF(aa)` sweep never converges (M3 finding, `sos_learning_report.md`; the
     omega analog of step 5's frozen-prefix correction). This splits
     `class(p)`;
   - if they agree: one of the two words disagrees with the representative of
     its own fold class under `kappa` — EXACTLY one: the two representative
     bits differ and the two queried bits are equal, so the shared bit
     matches one side and mismatches the other; no tie-break exists, assert
     it. Run the **frozen-prefix chain** (below) on that word inside
     `kappa`'s context; this splits some class.

   Scan order (normative — transcripts must be byte-reproducible): subjects
   `p` in shortlex order, classes `d` in class-id order; escalate on the
   FIRST divergence, split, and restart the main loop. Shortlex letter order
   is the serialization's (valuation bitvectors ascending: `!a` before `a`).
   The scan order changes which cell fires first — hence the minted column
   and the whole trace, though never the fixpoint — so it is pinned here.
   The paper's section 4.3 worked example assumes exactly this order; note
   its first firing cell is an *innocently merged* subject whose fold merely
   walks through the guilty merge — the second escalation branch fires, and
   that is correct behavior, not a mis-selected subject.
5. **counterexample processing** — given a lasso `(w, z)` where prediction and
   teacher differ:
   - *normalize*: `k` = the prediction's stabilization power;
     `(w', z') = (w.z^k, z^k)`;
   - *junction*: one query `member(key(psi(w')), z')` decides stem-side vs
     loop-side;
   - *stem chain*: bits
     `g_i = member( key(psi(w'[1..i])) . w'[i+1..], z' )`, `i = 0..|w'|`;
     endpoints differ on the stem side; binary-search an adjacent flip;
     mint linear column `(eps, w'[i+2..], z')`;
   - *loop chain*: bits
     `d_i = member( key(psi(w')), key(psi(z'[1..i])) . z'[i+1..] )`,
     `i = 0..|z'|`; binary-search a flip; mint omega column
     `(key(psi(w')), z'[i+2..])`;
   - *frozen-prefix chain* (used by saturation): the stem chain's replacement
     scheme, run on the segment `g = r.p` INSIDE the separating column
     `kappa`'s context, with `kappa`'s own prefix `x0` frozen in place. For a
     linear `kappa = (x0, y0, t0)`: bits
     `member(x0 . rep(psi(g[1..j])) . g[j+1..] . y0, t0)`, flip column
     `(x0, g[j+2..] . y0, t0)`. For an omega `kappa = (x0, y0)`: bits
     `member(x0, rep(psi(g[1..j])) . g[j+1..] . y0)`, flip column
     `(x0, g[j+2..] . y0)`. In both sorts the minted column's prefix is `x0`
     ALONE — the unconsumed segment migrates into the middle component, never
     into the prefix. (An earlier revision of this line wrote the mint as
     `(x0 . key(...), ...)`; that was WRONG — only the first branch of step 4
     absorbs a representative into the prefix. Reference: paper Lemma 4.5 and
     the §4.3 worked chain.)
   - Every flip splits exactly one class: the frontier word
     `key(c_i).letter` leaves the class of `key(c_{i+1})`.
6. **export** — at fixpoint: `M(c, c') = fold(c, key(c'))`; re-key every class
   by BFS over `step` from `[eps]` in shortlex letter order (the first word
   reaching a class is its canonical key); enumerate linked pairs of `M`
   over non-identity classes only (section 1.1 shows `[eps]` cannot occur in
   a linked pair — assert `s != [eps]` and `e != [eps]`) and fill `P` by one
   membership query each (or from cache) on `member(key(s), key(e))` — both
   keys non-empty by section 1.1; emit `.sos`.

   Export refusal (normative, 2026-07-11; replaces the former "diagnostic
   artifact" caveat): the exported invariant decides lassos by multiplying
   *classes* (`M` substitutes a representative mid-product), which is
   well-defined only for a **two-sided** congruence. Before emitting, run
   the congruence test — the saturation sweep's **check phase** on the
   final table: for every table word `p` with `rep(class(p)) != p` and
   every class `d`, compare `fold(d, p)` vs `fold(d, rep(class(p)))`; zero
   queries; clean ⟺ the partition is a congruence (paper Lemma 5.4). On a
   clean check, export as above. On a dirty check there is **no algebra to
   export** (paper Theorem 5.5): the campaign path REFUSES — no `.sos` is
   written, the run records `fixpoint_congruent = false`, verdict
   `ACCEPTOR_ONLY` (section 7) — and the `canonicalize` assertion stays as
   a backstop on its own contract. A separate `--unchecked` diagnostic
   export remains available for the fixtures that display what the
   assumption would produce (rows P7/F8, the paper's §4.2 display); its
   output is never a deliverable. On a saturated run the final sweep
   already ran clean, so `fixpoint_congruent = true` is recorded without
   recomputation. NOT an acceptable implementation of the test:
   `mult[c][class(a)] == step(c, a)` over letters only — `rep(class(a))`
   is always a letter, so the check is vacuous whenever no two letters
   share a class, and it passes the non-congruent `a_implies_xa` export.

Main loop: `fill; close; consist;` to fixpoint, then `saturate` (restart on
split), then `equiv`; on counterexample process and restart; on `eq` run
`export` and stop. With `--no-saturation` step 4 is skipped entirely.

Hard invariants (assert, and record in the audit log):

- every class split stores its *witness*: the column and the two differing
  membership bits (with the exact queried lassos) — replayable;
- the class count never decreases and never exceeds the reference class count
  in white-box runs (checked post hoc by the harness, not by the learner;
  both counts under the section 1.1 identity convention — if this check
  trips right after a convention-affecting change, regenerate the reference
  fixtures before suspecting the learner);
- all runs are deterministic given the teacher's answers.

### 3.3 Validator *(thin wrapper, mostly exists in-repo)*

`sos_validate learned.sos reference.sos` — byte comparison after parsing and
re-canonicalization (defensive: re-sort accept pairs, normalize whitespace).
Also `sos_validate --acceptor learned.sos <file.hoa> --bound B`: checks the
invariant's membership read-off against direct simulation on all lassos up to
`B` — used to certify *acceptance-correctness* separately from canonicity
(needed by experiment E2).

Scope rule (normative): `--acceptor` accepts either a `.sos` invariant or a
`CAYLEY` hypothesis. For any fixpoint reached **without** saturation (M2
builds, `--no-saturation` runs), it MUST be pointed at the Cayley form: the
`.sos` read-off presumes a two-sided congruence (section 3.2 step 6 caveat)
and can legitimately fail on such runs while the hypothesis is fully
correct. That divergence is an expected outcome (section 9, row F2), not a
learner bug.

---

## 4. Workflow

```
                 corpus (HOA files)
                        |
        +---------------+----------------+
        |                                |
   reference builder (in-repo)      sos_learn  <-- teacher(D) via queries
        |                                |
   reference.sos                learned.sos + stats.json + audit.log
        |                                |
        +---------> sos_validate <-------+
                        |
              per-case verdict: SOUND / FAIL / BUDGET
                        |
                 experiment driver -> results.csv -> tables/plots
```

The experiment driver is a batch runner: iterates a manifest of cases, applies
per-case budgets, never lets one case kill the campaign, and aggregates the
stats files into one CSV with one row per (case, configuration).

---

## 5. Soundness harness

Layered; every layer is automated and green before any experiment is reported.

1. **Teacher self-check.** Two independent membership implementations (the
   simulator of 3.1 and the invariant read-off through the reference builder)
   compared on randomized lassos per corpus automaton (say 10^4 per case,
   seeded). Any disagreement is a build-stopping bug.
2. **Definitional property tests** (random tables/words, seeded):
   - prediction on a representative lasso equals the cached teacher bit —
     definitional, must hold at all times;
   - minted-column bookkeeping identity (entry of `p` at minted = entry of
     `p.a` at source);
   - fold coherence `psi(p) == class(p)` after every table operation.
3. **Split audit replay.** After each run, re-issue the two witness queries of
   every recorded split against the teacher and confirm the bits still differ.
   (Catches transcript/bookkeeping corruption and any nondeterminism.)
4. **End-to-end gate.** On the full corpus: `learned.sos` byte-equals
   `reference.sos`. This is the soundness criterion. A `FAIL` is always
   treated as a learner bug until proven otherwise; the audit log localizes
   the first divergent decision.
5. **Metamorphic checks** (cheap, high-value):
   - complementing the acceptance of `D` must yield a learned invariant
     identical except for `P` complemented (against linked pairs);
   - permuting `AP` names / letter encodings must commute with learning;
   - re-running with the same seed must reproduce the transcript bit-for-bit.
6. **Ablation coherence.** `--no-saturation` runs must pass
   `sos_validate --acceptor` **on their Cayley hypothesis** (the learner's
   own prediction function is acceptance-correct at the fixpoint, to the
   tested bound). Their *exported* `.sos` is NOT required to pass — the
   export read-off presumes a two-sided congruence and may legitimately
   disagree (sections 3.2/3.3); record the run as `ACCEPTOR_ONLY`. Both
   outcomes are recorded, not hidden.

---

## 6. Experiments

Corpus note (revised 2026-07-08f). The primary corpus is the flat,
complement-closed catalogue `genaut/corpus/flat_canon` — 3938 languages up
to AP relabeling, one representative per language, dual included
(`corpus/flat_canon/STUDY.md`), with precomputed reference invariants — which
supersedes the per-shape census for E1/E2/E3. Exhaustive claims (the
permanent-stall family at the smallest non-LTL shape) stay scoped to the
exhaustively enumerated `2state1ap1acc`. Because the catalogue is
complement-closed and a run on `¬L` is the bit-flip of the run on `L` (same
partition, same splits, same counterexamples, same query counts), every
E1/E2 statistic must be exactly dual-symmetric at sweep completion — the
report generators should assert this, not assume it. Three named languages
are mandatory worked cases in every experiment ("the triptych"):

- `T1`: "infinitely many `aa`" — `GF(a & Xa)` as a 2-state Buchi automaton;
- `T2`: "an even block of `a` then `!a`, then anything" —
  `(aa)*.!a.Sigma^omega`, 4-state Buchi;
- `T3`: "infinitely many `!a` and eventually every completed `a`-block has
  even length" — 2 states, `Fin(0) & Inf(1)` (prefix-independent; the
  hard case for right-congruence-based methods).

Two further named cases are mandatory wherever the ablation is involved
(E0, E2): `a_implies_xa` and `a_once`, the proven-permanent stall specimens
(paper Prop. 4.4; sources in `research_notes/sos_figs/sources/`). The census
manifest is the `flat_canon` catalogue plus the named cases above —
nondeterministic inputs are covered through the sos import layer's
determinization. The manifest file is itself a deliverable: cases are named
and versioned, never selected ad hoc.

**E0 — Validation campaign.** Run the full harness (section 5) over the
corpus. E0 subsumes the M3 gates, now run under the driver: the saturation
gate, the Even AND EvenBlocks paper-trace conformances, and the exact-mode
fixtures; the Even / EvenBlocks split-and-query ledgers must reproduce the
M3 baselines in `sos_learning_report.md` (section 9 row P5). Deliverable: a one-page
report — cases, per-case verdict, query budgets used, zero mismatches. Gate
for everything below.

**E1 — Scaling against the target.** Question: do measured costs track the
designed bounds (splits <= number of classes `N`; membership queries
`O(N^2 . |Sigma|)` for the table plus logarithmic counterexample analysis)?
Procedure: for every corpus case record `N` (reference), splits, membership
queries by phase (fill / harvest / saturation / P), equivalence queries,
table dimensions, wall time. Deliverable: scatter plots of each metric vs
`N`, with the designed bound overlaid; a table of the triptych rows in full.

**E2 — Saturation ablation.** Question: how often, and on which languages,
does the learner without saturation stall on a non-canonical fixpoint?
Procedure: run everything twice (`--no-saturation` vs default), the ablation
leg under `--eq-mode exact`; classify each case's `stall_class` (section 7):
`none` — the first closed/consistent fixpoint is already canonical;
`transient` — some pre-equivalence fixpoint was non-canonical but a
counterexample broke it; `permanent` — the exact oracle certifies a
non-canonical fixpoint (with exact equivalence, every *surviving* stall is
permanent by definition; a bounded oracle can only under-report, which is
why the ablation leg runs exact). The classification is **per language, read
from the ablation (no-saturation + exact) leg alone**: a saturation-on run
carries `stall_class = n/a` and never contributes to the frequency counts —
otherwise a proven-permanent language, whose saturated run breaks its stall by
the sweep with `cex 0`, is miscounted `transient` (the M4.a E0 table exhibited
exactly this mislabel; see section 7 and row P6). Cross-check against theory:
`a_implies_xa` and `a_once` MUST land in `permanent` (rows P4/F5);
`F(a & Xa)`, `Even`, `GF(aa)` in `transient`. Deliverable: stall frequency
by class and by structural features (prefix-independence, acceptance type);
every `permanent` case beyond the two known specimens reported individually
with both fixpoints and the separating left context. These exhibits feed
the theory side; treat them as a first-class output, not a statistic.

*Recorded outcome (flat_canon, preliminary — `sos_learning_report.md` 2026-07-08).*
1180 permanent-stall languages on the partial sweep, gap to 53; permanence
cuts the LTL boundary (582/1180 aperiodic); and **four prefix-independent
entries — two languages and their complements**
(`2state1ap2acc_parity_0088836118`, `_1178851077`), the refutation witnesses
of the prefix-dependence necessity conjecture. **New deliverable — the
witness lock (blocks the paper's §6.3 claim):**

- (a) assert prefix-independence on each witness's *canonical* invariant —
  `(s, e) ∈ P ⟺ (c·s, e) ∈ P` for every class `c` and linked pair `(s, e)`;
- (b) assert the ω-sort signature (paper Cor. 4.7(b); row P8): every column
  minted in the witness's saturated run is of the ω-sort — a linear mint
  means the prefix-independence predicate or the sweep is wrong,
  build-stopping either way;
- (c) emit the full exhibits (coarse and canonical `.sos`, complete split
  ledger with every escalation and minted column) into the report;
- (d) RETIRED (2026-07-08g) — the hunt has no quarry. Theory: a
  prefix-independent language that is closed (safety) or open is trivial
  (paper Lemma 4.8). A `c = 0` shape recognizes only safety languages
  (every run accepting; finite branching + König: a word has an infinite
  run iff each of its prefixes has a run), so the unfinished
  `3state1ap0acc` can never yield a witness at any point of its sweep;
  every other exhaustive shape is already completely swept with zero
  prefix-independent permanent stalls (the E2 Wagner table's
  `prefix-indep` column); and the smallest shapes not so ruled out sit
  beyond the enumeration wall (`2state1ap2acc` at `4^16 ≈ 4.3·10⁹`
  generator ids, and up). No exhaustive-shape witness is reachable — and
  none is needed: the refutation is an existence claim carried by the
  per-witness lock (a)–(b), which certifies on the canonical invariant,
  independent of provenance.
- (d′) NEW gate, replaces (d): at sweep completion, assert the
  **exhaustive negative** — zero prefix-independent permanent stalls over
  the entire exhaustive tier, emitted as a machine-generated one-line
  count per shape. This grounds the paper's §6.3 complementary claim:
  prefix-independent permanent stalls first arise beyond the wall.

*Ruling 2026-07-11 (the recount; unblocks E2 at the 6222 scale).* Permanence
is a property of the **certified partition** (class count vs `N`,
byte-comparison), never of the export bytes, so E2's frequency counts stand
as defined. The ruling sharpens them: by Theorem 5.5 every `permanent` row
must carry `fixpoint_congruent = false` and every ablation `SOUND` row
`true` (rows P9/P10). The recount (section 8 item 13): (a) the 17 ex-`CRASH`
export-assert rows join `permanent` (certified, non-congruent — always
stalls; only the export assert crashed): **permanent = 3170** of 5527
decided ablation rows, `BUDGET` 680 + `OVERSIZE` 15 deferred; (b) the
ablation leg is re-run once with the `fixpoint_congruent` column — the
theorem performed at census scale. Deliverable: the two-way table
verdict × congruent with zero off-diagonal mass, dual-symmetric.

**E3 — Baseline: FDFA learning (ROLL).** Question: cost and capability
comparison against the established FDFA learner on identical teachers.
Procedure: wrap our white-box teacher in ROLL's interface; run ROLL's
periodic / syntactic / recurrent modes per case; record its membership and
equivalence counts under the *same counting rules* (one lasso query = one
membership; document any protocol mismatch rather than adjusting numbers
silently), output sizes (sum of DFA states) vs our class count `N`.
Additionally record capability: whether each output can answer "is the
language LTL-definable" directly (FDFA: no — mark N/A; ours: read off the
learned invariant by the group test). Deliverable: paired table per case,
summary medians, and the capability column reported as a result in itself.

Design note (revised 2026-07-08c to the delivered E3): ROLL's equivalence
queries carry an *automaton* hypothesis (FDFA/NBA), not a Cayley form, so our
exact oracle of 3.1 does not apply to them. Two options were live — answer them
with our bounded product enumeration (recording `bounded:<B>`), or let ROLL use
its **native** automaton equivalence. The delivered baseline takes the latter:
ROLL runs its own RABIT equivalence against a **state-based Büchi** presentation
of the target (Spot `SBAcc`; a transition-based Büchi ROLL misreads as a trivial
language). Both learners are then certified **exactly**, by *different* oracles —
ours the Cayley transformation-closure product, ROLL's RABIT — so the reported
asymmetry (row F6) is *mechanism*, not certification level. Because the target is
presented to ROLL as its own automaton, absolute membership counts are
presentation-sensitive; the comparison's robust axes are output size (summed FDFA
states vs `N`, against Proposition 5.3's `N + N²` envelope) and capability
(LTL-definability read-off — ours only). Pin the ROLL version and JVM in the
manifest.

**E4 — Worked transcripts (paper figures).** For the triptych: full audit-log
renderings — table snapshots at each split, every minted column with its
provenance (consistency / stem chain / loop chain / saturation escalation),
every saturation escalation with its witness. Deliverable: three
machine-generated, human-readable traces (markdown), stable across reruns.
`sosl/tests/sosl/m3_ledgers.py` is the prototype; the normative rendering is the
paper's ledger format (trigger / chain / minted column / splits / class
count, plus per-phase query totals) AND the final *signature matrix* —
class keys against discovered columns, the companion of the paper's
Tables 6 and 8. The EvenBlocks signature matrix currently in
`sos_learning.md` section 5 is hand-derived from the M3 ledger; E4 makes it
machine-generated like everything else.

**E5 — Counterexample sensitivity.** Question: how much does teacher
counterexample policy affect cost (the `log` term and constants)?
Procedure: re-run the corpus with equivalence strategies returning
(i) minimized counterexamples (default), (ii) first-found from bounded
enumeration, (iii) deliberately padded counterexamples (stem and loop
inflated by pumping a factor 2..32). Metrics: total membership queries,
harvest queries specifically, wall time. Deliverable: sensitivity table;
confirmation (or refutation) that cost grows logarithmically with
counterexample length. Implementation hook: the teacher grows a
`--cex-policy minimal|first|padded:<k>` flag; `minimal` is the existing
shortlex-least cell of the exact oracle, the other two are new.

*Recorded outcome (M4, `sos_learning_report.md`).* `first` **coincides with
`minimal`** for both the bounded and the exact oracles — they enumerate in
shortlex-least order, so first-found *is* minimal and contributes no separate
series. E5 is therefore two policies in effect (`minimal`/`first` identical,
vs `padded:<k>`), not three; the paper states this rather than implying three
distinct data points. The `padded:<k>` leg confirmed the design: the harvest
term grows `+1` per doubling of counterexample length (`harvest ≈ log₂ ℓ`)
with the learned invariant unchanged.

**E6 — Stretch: beyond the census.** Random deterministic Emerson-Lei
automata (parameters: `|Q| in 3..8`, `|AP| in 1..3`, acceptance sets `1..3`,
seeded), filtered to a target class-count spread; per-case budget 120 s.
Deliverable: success/budget profile vs `N` and vs automaton size; the largest
solved instances, to calibrate what the writeup may honestly claim.

---

## 7. Metrics file (`stats.json`)

One flat JSON object per run; the driver concatenates them into CSV. Required
fields:

```
case_id, config_id, seed,
ap_count, ref_classes, learned_classes,
n_member_total, n_member_fill, n_member_harvest, n_member_saturation, n_member_pcache,
n_equiv, n_splits, n_columns_lin, n_columns_om,
n_saturation_checks, n_saturation_escalations,
n_classes_initial, stall_class (none|transient|permanent|n/a),
cex_policy (minimal|first|padded:<k>),
max_cex_stem, max_cex_loop, max_query_word_len,
n_guard_firings, guard_fired_final (true|false),
eq_certification (reps|bounded:<B>|exact),
export_associative (true|false|n/a),
wall_seconds, verdict (SOUND|FAIL|BUDGET|ACCEPTOR_ONLY|OVERSIZE|CRASH)
```

`n_classes_initial` is the class count of the first stabilized table (the
ledgers' starting point); `cex_policy` is `minimal` everywhere except E5.

`eq_certification` (revised 2026-07-09): every campaign row must read
`exact` — `bounded` is retired from the campaign legs (section 3.2 default),
so a `bounded:<B>` certification on a campaign row is a driver defect, not a
recorded outcome — except a recorded **cap-escape** (amended 09b: a
guard-fired query whose closure fallback exceeds its cap certifies
`bounded:8` on the default leg, distinguishably recorded). The field keeps
its enum for black-box and diagnostic runs.

`n_guard_firings` / `guard_fired_final` (added 2026-07-09): the count of
functionality-guard firings over the run's equivalence queries (row F10),
and whether the *final*, certifying query fired — which on a `SOUND`
(byte-equal) run is a defect: a canonical table's fold is the syntactic
morphism.

`stall_class` is the E2 classification (section 6): a **per-language**
property determined **solely by the no-saturation + exact leg** — `permanent`
if that leg certifies a non-canonical fixpoint, else `transient` if a
non-canonical fixpoint was observed before a counterexample broke it, else
`none`. On any **saturation-on** run `stall_class` is `n/a` — a saturated run
resolves the stall by the sweep, which the trichotomy does not name, so it
must never carry `transient` or `permanent` (a saturated run of a
proven-permanent language would otherwise be mislabelled `transient`, its
stall being broken with `cex 0`; the M4.a E0 table did exactly this). E2 reads
the ablation-leg row only and never folds a saturated-run label into the
frequency counts.

`ACCEPTOR_ONLY` is reserved for `--no-saturation` runs that pass the acceptor
check but produce no canonical export. Re-glossed 2026-07-11: on the exact
ablation leg this verdict means **"correct acceptor, no algebra — export
refused"** — by Theorem 5.5 an exact-certified fixpoint is canonical or
non-congruent, so "export byte-differs while a genuine (coarser) algebra
exists" cannot occur there. Under `bounded` oracles (diagnostics, black-box
teachers) that case IS possible, and the `fixpoint_congruent` field below
distinguishes it; the verdict is not split.

`fixpoint_congruent (true|false|n/a)` (added 2026-07-11): the Lemma 5.4
congruence check on the final table (section 3.2 step 6). `true` on every
saturated run (its final sweep ran clean — recorded, not recomputed);
computed by the check phase on ablation runs; `n/a` when no fixpoint was
reached (`BUDGET`, `CRASH`). Gated by rows P9/P10; E2's recount keys on it.

`OVERSIZE` (added 2026-07-08f) records the exact oracle exceeding its
transformation-closure work cap (`ExactTooLarge`): an honest "too large to
certify exactly", occurring only on the ablation leg of the largest
languages. The run's `stall_class` is deferred (`n/a`) and never enters E2's
frequency counts; `FAIL` stays reserved for a genuine byte mismatch
(row F9). *Rescoped 2026-07-08h: with exact-by-reference (section 3.2) the
census ablation leg never builds the closure, so `OVERSIZE` can arise only
on the referenceless fallback path (E6); once section 8 item 10 lands, an
`OVERSIZE` on a census run is a defect, not a recorded outcome. Rescoped
again 2026-07-09: also legal on a census query whose functionality guard
fired and whose closure fallback then hit the cap (row F10 → F9) — observed
(2026-07-09b): the guard fires in practice, and the five formerly-deferred
cases stay deferred by exactly this path.*

`export_associative` is computed on the exported multiplication table
(`n/a` when no export was produced — including a 2026-07-11 refusal; the
`a_implies_xa` display fixture of M4.e item 2 / row F8 computes it on the
`--unchecked` diagnostic export): brute-force check of
`M(M(a,b),c) = M(a,M(b,c))` over all class triples — `O(n³)` on tables of
this size, negligible. On a saturated run it must be `true` (the export is a
two-sided congruence quotient — section 9 row P7); on an ablation-leg
permanent stall it is expected `false`, and the first violating triple is
recorded as the witness (row F8): non-associativity is the §4.2 display's
sharpest evidence that a stalled export is not an algebra at all.

---

## 8. Milestones and acceptance criteria

- **M1 — Teacher + validator.** White-box teacher (member + `reps`/`bounded`
  equiv), `.sos`/Cayley parsers, `sos_validate`. Accept: harness layer 1
  green on the census; teacher self-check clean.
- **M2 — Learner without saturation.** Table, fill/close/consist, chains,
  export. Accept: harness layers 2–3 green; every census case passes the
  *acceptor* check (on the Cayley hypothesis — section 3.3 scope rule);
  byte-equality passes on all cases where it passes (no claim yet on the
  rest).
- **M2.5 — Convention alignment** *(added 2026-07-06; **DONE 2026-07-06**).*
  Landed: (a) fresh-identity builder + regenerated fixtures; (b) learner
  eps-merge reverted to the section 3.2 singleton rule; (c) M2 table
  re-baselined append-only in `sos_learning_report.md`. Outcome exceeded the predictions: all
  four of `GF a`/`GF(aa)`/`Even`/`EvenBlocks` are byte-equal to the reference
  at M2 without saturation (every stall was transient). Original text follows.
  (a) Fix the reference builder to the fresh-identity convention of
  section 1.1. Regression gate: `GF(aa)` stays 6 and `Even` stays 5;
  `EvenBlocks` moves 7 -> **8** (the previously published 7 was itself an
  instance of this bug — see section 1.1 and the correction in
  `sos_learning_report.md`); `GF a` moves 2 -> 3; `F a` stays 3; `a U b` stays 4.
  Also regenerate `research_notes/sos_figs/sources/*.md` (the current
  `evenblocks.md` embeds the buggy 7-class algebra in every table it
  contains). (b) Revert the
  learner's eps-merge (restore the section 3.2 singleton rule) in the same
  working session as the fixture regeneration, so reference and learner
  never disagree for a spurious reason in between. (c) Re-baseline the M2
  status table by *appending* to `sos_learning_report.md` (never overwrite the old
  table); the theory reply there ("What to expect after M2.5") lists the
  predicted per-case outcomes. Accept: reference and learner agree on
  `GF a`; no assertion fires on the census; the re-baselined table is
  committed.
- **M3 — Saturation + exact equivalence** *(**DONE 2026-07-07** —
  `sos_learning_report.md`: end-to-end gate green on the census, Even conformance
  exact, exact-mode fixtures green, EvenBlocks ledger delivered to
  `sos_learning.md` §5; one normative correction fed back into section 3.2
  step 4, branch 1, omega sort)*. Accept: end-to-end gate (layer 4)
  green on the full census; metamorphic checks green; E0 report produced.
  Plus three M3-specific gates *(revised 2026-07-06: the permanence question
  is now settled by theory — paper Proposition 4.4 proves the `a_implies_xa`
  and `a_once` stalls permanent; `F(a & Xa)` was resolved transient by the
  census — so the exact-mode runs change role from decision to fixture)*:
  - *Paper-trace conformance (Even).* With saturation on, the Even run must
    reproduce the paper's §4.3 trace exactly: day-one sweep clean; one
    equivalence counterexample `(eps, a;a;!a)` splits `a;a`; the four-class
    sweep then fires FIRST at cell `(!a;a, [a])`, second branch (probes
    equal), frozen chain flips at `j = 1 -> 2`, mints the linear column
    `(eps, a;!a, a;a;!a)`. If the run mints an omega column instead —
    `(a, a)` under the corrected step-4 omega mint — the sweep scan order is
    not per spec (step 4): fix the order, not the paper.
  - *Exact-mode fixtures.* `--no-saturation --eq-mode exact` on
    `a_implies_xa` and `a_once` MUST certify their stalled fixpoints (4 and
    3 classes): Proposition 4.4 proves no counterexample exists, so a
    returned counterexample here is an exact-mode bug, full stop. With
    saturation AND exact, both must reach canonical (5 and 4) byte-equal.
  - *Deliverables to the theory thread.* The EvenBlocks split ledger (the
    paper's Table 8 rows 2–5: trigger, chain, minted column, split, per
    split) and the per-phase query ledgers of the Even and EvenBlocks runs —
    both waiting as `TBD-M3` slots in `sos_learning.md` §5.
- **M4 — Campaign** *(refined 2026-07-07; attack in this order — the ROLL
  leg is the schedule risk and must not block the rest)*:
  - **M4.a — Driver + E0** *(**DONE 2026-07-08** — the `sosl.experiment`
    package (driver / manifest / per-run stats / E0/E4 reports) is landed; the
    E0 gate is green (10 runs, zero mismatch), the Even/EvenBlocks ledgers are
    byte-stable to the M3 baselines (row P5), the E4 signature matrix is
    machine-generated, and `evenblocks_conformance.py` is adopted as-is).*
    Promote `sosl/tests/sosl/genaut_census.py` (case
    iteration, classification) and `sosl/tests/sosl/m3_ledgers.py` (audit
    rendering, extended with the signature matrix — E4 note) into the batch
    driver of section 4: manifest in, one `stats.json` per (case, config),
    concatenated CSV out, per-case budgets, a crash or budget never kills
    the campaign; long output under `sosl/tests/sosl/logs/`, never `/tmp`.
    Accept: E0 report generated by the driver; the M3 gates green under it;
    Even / EvenBlocks ledgers byte-stable vs the M3 baselines (row P5).
    Add the EvenBlocks conformance probe (mirror of `even_conformance.py`,
    asserting the paper's Table 8: initial stabilized 3 classes, day-one
    sweep clean, first cex `(eps, !a;a;a)` via the loop chain, columns
    `(a, a)` / `(a, !a;a)` / `(eps, !a)` in order, splits 3->4->6->8, the
    67/4/14/14 query ledger, byte-equal export) — the paper now anchors
    that run too. A candidate implementation already exists in the working
    tree, `sosl/tests/sosl/evenblocks_conformance.py`, green on first run
    (2026-07-07): check it out — it meets this requirement as written;
    review and adopt it rather than rewriting from scratch.
  - **M4.b — E1 + E2** *(**DONE 2026-07-08** — the E1 scaling table
    (`splits ≤ N`, fill under `N²·|Σ|`) and the E2 stall table are script-
    generated; the two proven-permanent specimens land in `permanent`; the
    census-backed ablation hunt over the exhaustive `2state1ap1acc` frontier
    found **44 distinct permanent-stall languages** (gap up to 5), reported
    individually with both fixpoints and the separating left context. The E1
    *scatter plots* still wait on the census N-spread — the generator already
    emits the per-metric columns.)* Accept: scatter data and the stall table
    generated by script; the two proven-permanent specimens land in `permanent`
    (rows P4/F5); any NEW permanent stall reported individually
    (first-class output).
  - **M4.c — E3 (ROLL).** Accept: paired table on the census with the
    certification asymmetry recorded, and the protocol-mismatch list. If
    ROLL cannot be brought to acceptance within budget, deliver the wrapper
    plus the blocking record and move on — M4.d does not wait for it.
  - **M4.d — E5 + figures** *(**E5 DONE 2026-07-08** — the teacher grows
    `--cex-policy minimal|first|padded:<k>`; the sensitivity table shows the
    harvest term grows +1 per doubling of `|cex|` (i.e. `≈ log|cex|`), the
    invariant unchanged; `first` coincides with `minimal` for the minimal-
    ordered oracles. The one-script figure/table regeneration remains.)*
    Accept: sensitivity table; every figure and
    table regenerated from `results.csv` by one script (no hand-edited
    numbers anywhere). E6 remains stretch, after M4.d.
  - **M4.e — Paper-close deliverables** *(added 2026-07-08e, theory review
    pass; these are what still stands between the campaign and a submittable
    §6)*:
    1. **`N`-semantics / dedup audit — BLOCKER.** State, in one line, what
       `ref_classes` counts (`|S(L)₊¹|` with the fresh identity, per
       section 1.1 — or not), and reconcile the census-E1 per-N table with
       the algebra: 32 languages at `N = 2` is impossible for
       `N = |S(L)₊¹|` (`L ∈ {∅, Σ^ω}` are the only two). If the convention
       is off by one, regenerate the per-N medians under the stated one; if
       dedup across shapes is incomplete, recount and restate the census
       total. *(Update 2026-07-08f: the flat_canon rerun reports 2 languages
       at `N = 2` — consistent with `N = |S(L)₊¹|` — so the anomaly was the
       old census's; the one-line convention statement is still owed, and a
       new low-`N` anomaly replaces it: the `N = 4` bucket's median fill of
       145 against an `N²·|Σ| = 32` envelope at median splits 0 — explain
       it.)* Deliverable: convention line + explanation of the `N = 4` fill
       + a note in `sos_learning_report.md`.
    2. **Associativity probe + stalled-export fixture.** Implement
       `export_associative` (section 7) and rows P7/F8 (section 9). Emit the
       stalled `a_implies_xa` 4-class export and assert it matches the
       paper's §4.2 display cell-for-cell (keys `eps/!a/a/a!a`; row `a` =
       `a, a!a, !a, !a`; witness triple `([a],[a],[a])`) — a paper-anchored
       conformance lock, same status as the Even/EvenBlocks traces (row P5).
    3. **Parity-twin identity check.** Byte-compare the reference `.sos`
       *sets* of `2state1ap1acc` and `2state1ap1acc_parity`. Expected:
       identical 129-language sets — the paper's §6.1 now states the twin
       re-presents the same languages; if the sets differ, report the delta
       and the paper adjusts (§6.1/§6.3/§6.4).
    4. **LTL read-off agreement count.** Over the (post-item-1) census:
       learned invariant's aperiodicity verdict vs ground truth, expected
       agreement on every case. Closes the §6.4 `⟨TBD-M4: n cases⟩`.
    5. **Wall-time line.** Total and worst-case census wall time, one
       sentence. Closes the §6.2 `⟨TBD-M4⟩`.
    6. **Shape manifest.** Emit the per-shape family/count table from
       `manifest.py` (shapes, presentations, languages after dedup). Closes
       the §6.1 corpus `⟨TBD-M4⟩`.
    7. **The witness lock** (section 6, E2 recorded-outcome note,
       2026-07-08f): gates the paper's §6.3 refutation claim. Items
       (a)–(c) DELIVERED (report 2026-07-08, the lock green on all four
       witnesses). Item (d) — the exhaustive-shape witness hunt — is
       RETIRED as provably empty (2026-07-08g; see the rewritten (d) in
       section 6); its replacement is the exhaustive-negative gate (d′)
       there, asserted at sweep completion.
    8. **Complete the flat_canon sweep** (`3state1ap0acc` outstanding):
       final E1/E2/E3 figures replace the paper's §6 ⟨TBD-M4⟩ markers; at
       completion assert the dual-symmetry of every E2 count (section 6
       corpus note — the current 440/441 guarantee/safety split and the odd
       gap-bucket counts are partial-sweep artifacts that must vanish).
    9. **Data persistence — the reproducibility floor (2026-07-08g).**
       Every figure the report states must trace to a git-committed,
       machine-generated file. `tests/**/logs/` stays scratch and is never
       cited as evidence; when a campaign drop is validated, its
       load-bearing outputs — the raw `results.csv`, the analyzer
       summaries, the rendered tables, the exhibit `.sos` where a specimen
       carries a claim — are **copied** into a curated, committed folder
       (`reference/`, the pattern `witness_lock_exhibits.md` already
       follows; nest `reference/<campaign>/` and `.../sos/` as needed),
       immutable per drop. The report cites the committed path next to
       each table it reads off. A number that traces only to a
       build-machine file does not enter the paper.
    10. **Exact-by-reference (2026-07-08h; DELIVERED 2026-07-09 —
       `sos_learning_report.md`, gates green; three corrections adopted, see the
       revision-2026-07-09 block).** Re-base `--eq-mode exact` on
       the calculus form (section 3.2): align the hypothesis Cayley graph
       with the reference invariant, scan the symmetric difference, return
       the canonical-witness counterexample. Gate: on the E0 named cases,
       every counterexample, ledger, and learned invariant must be
       byte-identical to the closure oracle's — both decide the same
       question and both minimize shortlex, so any drift convicts one of
       them. Then re-run the deferred `OVERSIZE` cases: their
       permanent-vs-transient classification enters E2's frequency counts,
       and `OVERSIZE` disappears from the census (row F9 rescoped to the
       referenceless fallback).
    11. **Functionality guard + default-leg switch (2026-07-09).**
       (a) Implement the guard of section 3.2 point (iii) in `exact_ref`
       (non-identity aligned-node count `= N_R`'s non-identity class
       count), wired as row F10; assert it on every query of the in-flight
       ablation sweep and report the firing count (predicted 0, node count
       exactly `N_R` on every run). (b) Re-run the two newly-permanent
       cases (`3state1ap0acc_013908` + complement) under the guard BEFORE
       E2 banks them — a permanence certification is the one verdict
       byte-equality cannot re-validate. (c) Locate `075976`'s dual partner
       and record where it classified (expected `transient`; under the old
       oracle it presumably sat in the `BUDGET` rows — the item-8
       dual-symmetry assert must ultimately agree). (d) With (a)–(b) green:
       switch the default leg to `--eq-mode exact` (section 3.2 default),
       re-run the default sweep, confirm the Even / EvenBlocks ledgers stay
       byte-stable (row P5) and `eq_certification = exact` on every row
       (section 7). *(Updated 2026-07-09b — (a) DONE and the guard FIRES:
       the factoring conjecture is refuted on learner-reachable tables
       (`2state1ap2acc_parity_2195145216`, ablation leg, 8 firings, 20–24
       aligned nodes over 17 reference classes), and even sweep-clean
       tables fire, so the guard is irreducible. (b) answered NO:
       `013908` and `075976` guard-fire and their closure fallback hits
       the cap — the five `OVERSIZE` cases remain deferred and are NOT
       banked. (c) now expects the dual partner `OVERSIZE` as well.
       (d) proceeds under the amended escalation of section 3.2:
       guard-fired queries go to the closure; a capped closure falls to
       `bounded:8` on the default leg (recorded in `eq_certification`;
       byte-equality still validates end-to-end) and records `OVERSIZE`
       on the ablation leg. New sub-asks: sweep-wide `n_guard_firings`
       tallies per leg; an assert that no `SOUND` run fires on its FINAL
       certifying query (a canonical table's fold is the syntactic
       morphism, so a final-query firing convicts the run); a committed
       exhibit of one firing with two concrete witness words `y ≈_L y'`,
       `ψ(y) ≠ ψ(y')`.)* *(Closed 2026-07-09 except the tallies: the
       amended escalation and the default-leg switch are DONE — E0 green,
       `eq_certification = exact` on all ten rows, Even / EvenBlocks
       ledgers byte-stable (P5) through the oracle swap; the firing
       exhibit is DELIVERED (`y = !a;!a;a ≈_L a;!a;!a = y'`, one R-class,
       fold values differ; re-verified against reference and fold) and
       displayed in the paper §2.3 — copy the verified probe output under
       `reference/` at the next drop (item 9); `guard_fired_final` is
       implemented and `013908`'s default leg conforms (one mid-run
       firing, clean final query, byte-equal); `075976` and its dual both
       guard-fire and cap — both `OVERSIZE`, the deferred set is
       dual-symmetric. Outstanding: the sweep-wide tallies, which retire
       the paper's two guard ⟨TBD-M4⟩ markers.)*
    12. **Fallback localization (2026-07-09; performance, optional but
       approved — instrumentation first).** The closure fallback is the
       campaign's cost centre once firings begin (~33 → ~2.5 cases/s).
       Theory supplies the localization (proof in `sos_learning_report.md`,
       2026-07-09 reply): on a fired graph let `Split` be the reference
       classes with ≥ 2 H-partners; a cell `(c, d)` is *quiet* when every
       class in the power orbit of `d_R` is unsplit and so is
       `c_R·d_R^k`, `k` the stabilization power of the orbit's
       unique-partner sequence. Every quiet cell is decided by its keyed
       lasso even on a fired graph; only the residue (split-touching
       cells) needs the closure, restricted to residue lassos. Minimality:
       return the smaller of the quiet scan's first flagged keyed lasso
       and the closure's residue-restricted minimum. Steps: (a) measure
       the residue fraction on the known firing cases — build only if it
       is small (expected: 3 split classes of 17 on the exhibit case);
       (b) gate by byte-identical counterexamples, ledgers and verdicts vs
       the unlocalized fallback on every fired query of the named firing
       cases plus a seeded fired sample; (c) incremental closure reuse
       across a run's successive queries (one split apart) is a second,
       independent option — engineering's choice. *(CLOSED 2026-07-09 —
       step (a) refuted it; DO NOT BUILD. A split class is absorbing in
       the orbit structure, so one split class of 57 already leaves 26.8%
       residue and the parity firing cases run 58–84%; and a firing means
       `Split ≠ ∅`, so the residue is never empty and the closure —
       whose cost and `ExactTooLarge` cap live in the build
       (`_loop_elements`), not the scan — is built regardless: no
       `OVERSIZE` lifted, the throughput collapse untouched. The theorem
       stands as mathematics only. Surviving candidate: option (c),
       incremental closure reuse (the `D`-profile monoid constant per
       case, the hypothesis side one split apart between queries),
       decided by one measurement — the closure's build-vs-scan wall-time
       split on a fired, non-capped query.)*
    13. **Export refusal + the congruence gate + the E2 recount (2026-07-11
       ruling; unblocks the E2 side of items 6/8).**
       (a) Implement the Lemma 5.4 check as the final-table classifier
       (reuse `saturate`'s scan with escalation disabled; zero queries);
       wire `fixpoint_congruent` (section 7). The letter test
       (`mult[c][λ(a)]` vs `step(c,a)`) is REJECTED — it passes
       `a_implies_xa`'s stalled export; fix `congruence_audit` accordingly
       and re-run it on the report's 14-case sample first: theory predicts
       **all 14** flip to non-congruent — a cheap local confirmation
       before the drop.
       (b) `export` refuses on a dirty check (section 3.2 step 6); the
       `canonicalize` assert stays; add `--unchecked` for fixtures; adapt
       the P7/F8 fixture (M4.e item 2) to it.
       (c) Local gates before the drop: `a_implies_xa` + `a_once` ablation
       = refusal + `congruent=false`; the E0 saturated named cases `true`;
       the named crasher `2state2ap2acc_parity_1618…` ablation = refusal,
       no `CRASH`; P5 ledgers untouched (saturated leg unaffected).
       (d) One cluster drop: re-run the **ablation leg only** (6222 cases)
       with the new column — the default leg's column is `true` by
       construction, E3 untouched, and `--done` cannot apply (the column
       needs the final table, which only a re-run reconstructs). Expected
       and gated: `false` on all 3153 `ACCEPTOR_ONLY` + 17 ex-`CRASH`
       rows; `true` on all 2357 ablation-`SOUND` rows; dual-symmetric
       (congruence is complement-invariant). An `ACCEPTOR_ONLY ∧ true` row
       is build-stopping (P9); a `SOUND ∧ false` row is a first-class
       theory finding (P10) — stop and report, either way.
       (e) E2 recount off the merged CSV (`permanent = 3170`); then the
       E2 exhibits, gates, and the paper's ⟨TBD⟩ fills proceed.
    Standing science ask — ANSWERED in the refutation direction
    (2026-07-08f): the flat_canon sweep surfaced two prefix-independent
    permanent stalls (plus complements), and the witness lock (item 7,
    DELIVERED) certifies them; the necessity conjecture is dead. The
    remaining M4 science deliverables are the completed sweep (item 8)
    with the exhaustive-negative gate (item 7 d′), under the persistence
    floor (item 9).

Non-goals for this iteration: performance tuning beyond the budgets above,
black-box teachers other than the wire protocol, alphabets beyond `2^AP`,
any use of external solvers in the learner path. The learner must remain a
pure query algorithm: its only source of truth is the teacher interface.

---

## 9. Expected failures — read this before filing a bug

A red check is only a bug if this table says so. "A" rows must always be
green; "P" rows must be green in the stated config; "F" rows are *allowed*
(sometimes *expected*) to be red in the stated config, and a red there is a
recorded outcome, not a defect.

| # | check | config | expectation | on failure |
|---|---|---|---|---|
| A1 | teacher self-check (5.1) | all | always green | build-stopping bug; fix before anything else |
| A2 | definitional property asserts (5.2) | all | always green | learner-core bug |
| A3 | split-audit replay (5.3) | all | always green | bookkeeping or nondeterminism bug |
| A4 | same-seed transcript reproduction | all | always green | hidden state; find it |
| P1 | acceptor check on the CAYLEY hypothesis | any fixpoint, any config | green to the tested bound | real bug: the learner's own predictions disagree with the teacher after equivalence assented |
| P2 | byte-equality vs reference | M3+, default config | green on every census case | bug — but first suspect stale fixtures from before M2.5 |
| P3 | learned classes <= reference classes | all (post-M2.5) | green | a split happened without an Arnold witness; replay the split audit |
| F1 | byte-equality vs reference | M2 / `--no-saturation` | MAY be red | the predicted section-4.2 stall (paper); record `ACCEPTOR_ONLY` and move on |
| F2 | acceptor check on the exported `.sos` | M2 / `--no-saturation` | MAY be red | export presumes two-sidedness (3.2 step 6 caveat); diagnostic only |
| F3 | equivalence returns a lasso the hypothesis already predicts correctly | any | must NOT happen | teacher bug (equivalence strategy or minimization) |
| F4 | budget exhausted on a census case | any | should not happen | flag it; census cases are sized to finish |
| P4 | exact mode certifies the proven-permanent stalls (`a_implies_xa`, `a_once` under `--no-saturation`) | M3+ | always green | a counterexample here = exact-mode bug — paper Prop. 4.4 proves none exists |
| F5 | byte-equality on `a_implies_xa` / `a_once` under `--no-saturation` | any | red, FOREVER | that is the theorem, not a flake; record `ACCEPTOR_ONLY` |
| P5 | Even / EvenBlocks ledgers match the M3 baselines (trigger sequence, minted columns, per-phase counts — `sos_learning_report.md`) | M4 driver, default config | always green | behavior drift: diff the audit logs and reconcile before touching paper or baselines |
| F6 | ROLL certified by its native RABIT equivalence, not our teacher's oracle | E3 | expected | record it; both learners certify exactly by different mechanisms — the asymmetry is a reported result, not a defect (design note revised 2026-07-08c) |
| F7 | budget exhausted on an E6 random case | E6 | allowed | record `BUDGET`; census sizing (F4) does not apply to E6 |
| P6 | `stall_class` on any saturation-on run | M4.b+ (E2) | must be `n/a` | driver bug: a saturated run must never carry `transient`/`permanent` (section 7) — the M4.a E0 table had this wrong; E2's frequency counts read the ablation leg only |
| P7 | exported `M` is associative (`export_associative = true`) | any **saturated** run | always green | the sweep failed to deliver a two-sided congruence — learner bug; a two-sided quotient's table is associative by construction |
| F8 | exported `M` is associative | `--no-saturation` runs | MAY be red; on `a_implies_xa` MUST be red with witness triple `([a],[a],[a])` | record the witness triple, never "fix" it — it anchors the paper's §4.2 display (a green here on `a_implies_xa` means the export or the check is wrong) |
| P8 | ω-sort discipline on prefix-independent cases: every column ever minted in a default-config run is of the ω-sort (paper Cor. 4.7(b)) | any prefix-independent case (`GF(aa)`, `EvenBlocks`, the E2 witnesses) | always green | a linear mint means the prefix-independence predicate or the sweep is wrong — build-stopping either way; the corollary's proof leaves no third option |
| F9 | exact oracle raises `ExactTooLarge` | referenceless fallback (E6), or the closure fallback of a guard-failed census query (F10) | allowed there; on any other census run it is a defect (exact-by-reference builds no closure) | record `OVERSIZE` (section 7); permanence classification deferred, default-leg soundness stands — never `FAIL` |
| F10 | functionality guard on the aligned graph (section 3.2 point (iii): non-identity node count `= N_R`) fires | any exact-by-reference query | MAY be red — it IS red in practice (2026-07-09b: the factoring conjecture is refuted; mid-run tables, sweep-clean ones included, split syntactic classes beyond their table words); a red is a recorded outcome, not a bug. Exception: a firing on the FINAL certifying query of a `SOUND` run is a defect — a canonical table's fold is the syntactic morphism | record it and fall back to the closure oracle for that query; certification/minimality claims for that query then rest on the fallback (cap-escape per section 3.2 default) |

| P9 | `fixpoint_congruent = false` on every exact-ablation `ACCEPTOR_ONLY` row | M4+ ablation leg | always green (Theorem 5.5: exact-certified + congruent ⟹ byte-equal ⟹ `SOUND`) | build-stopping: an exact-certified congruent non-canonical fixpoint contradicts Theorem 5.5 — suspect the oracle or the fold before the theorem |
| P10 | `fixpoint_congruent = true` on every exact-ablation `SOUND` row | M4+ ablation leg | expected green (byte-equality from a non-congruent partition has no known mechanism, but is not excluded by Theorem 5.5) | NOT build-stopping: an accidental byte-equality is a first-class theory finding — report the case id to theory, do not bank the row |

Two "surprising green" notes, so nobody distrusts a passing run:

- After M2.5, cases previously reported as coarser stalls may become
  byte-equal at M2, *without* saturation. Stalls of the Even / GF(aa) kind
  are transient: a later equivalence query returns a counterexample that
  breaks them (paper sections 4.2–4.3). This is correct behavior, not an
  accidentally weakened test.
- Saturation (M3) is still required even if many M2 cases pass: the
  correctness theorem needs it (transience of every stall is not
  guaranteed — that is exactly the `F(a & Xa)` question), and where a stall
  is transient, saturation resolves it for two membership queries instead of
  a whole equivalence round.

Convention changes (like M2.5) invalidate fixtures wholesale: if many checks
go red at once right after one, regenerate the reference fixtures first and
re-run before reading any individual failure.

Ledger drift at M3 is expected, not a regression: turning saturation on
changes the census query counts recorded at M2 — some equivalence rounds
become two-probe sweep escalations. Concretely, Even should complete with ONE
counterexample instead of two (the `a;!a` split moves from a harvest to the
sweep). Record the new ledgers; do not chase the old numbers.
