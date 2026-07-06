# SoS Learner — Implementation and Experimentation Specification

**Status:** specification / declaration of intent. Everything below is to be
implemented; nothing below exists yet except where explicitly marked
*(exists in-repo)*.

**Revision 2026-07-06 (theory thread).** Triggered by the M2 findings in
`sosl_report.md` (the reply appended there explains the *why* of each
change). New: section 1.1 (identity convention, normative), milestone M2.5
(section 8), section 9 (expected failures — read it before filing any bug).
Corrected: sections 3.3 and 5 item 6 (pre-saturation exports are diagnostic
only; acceptor checks target the Cayley hypothesis until saturation exists).

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
  (presentation-independence is what makes `.sosg` byte-equality a language
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

**Serialized format (`.sosg`, v1).** Plain text, canonical, byte-comparable:

```
SOSG v1
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

Two languages over the same `AP` are equal iff their `.sosg` files are
byte-equal. A *reference builder* for `I(L)` from an HOA automaton
*(exists in-repo)* is used by the teacher and the validator; the learner never
calls it.

---

## 2. Tool I/O

### 2.1 `sos_learn` (the deliverable)

```
sos_learn --teacher hoa:<file.hoa>            # white-box teacher (default)
          [--teacher proc:<command>]          # black-box teacher over pipes
          [--out learned.sosg]                # learned invariant (default stdout)
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
  -> {"op":"equiv", "sosg": "<serialized hypothesis, section 2.3>"}
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
classes: <n>          # with keys, as in .sosg
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
  - `exact` — decision via the product of `D` with the *transformation
    closure* of the hypothesis (`loop` words act on hypothesis classes as
    functions; close the function monoid under the letters; a mismatchable
    pair (stem-value, loop-transformation) yields a concrete counterexample).
    Complete; can be expensive; intended for the small instances of the
    campaign. Default: `reps`, then `bounded:8`, then `exact`.
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
   - let `kappa` be a column separating `rep(c_a)` from `rep(c_b)` (one must
     exist); query the two bits of `r.p` and `r.r0` under `kappa`'s context,
     where `r = rep(d)`;
   - if the bits differ: mint the column with `r` absorbed into the prefix
     (`(x.r, y, t)` or `(x.r, y)`); this splits `class(p)`;
   - if they agree: one of the two words disagrees with the representative of
     its own fold class under `kappa`; run the **frozen-prefix chain** (below)
     on that word inside `kappa`'s context; this splits some class.
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
   - *frozen-prefix chain* (used by saturation): same as the stem chain but
     with a fixed extra prefix `x0` riding along inside the queried context
     and the flip column minted as `(x0 . key(...), ..., ...)`.
   - Every flip splits exactly one class: the frontier word
     `key(c_i).letter` leaves the class of `key(c_{i+1})`.
6. **export** — at fixpoint: `M(c, c') = fold(c, key(c'))`; re-key every class
   by BFS over `step` from `[eps]` in shortlex letter order (the first word
   reaching a class is its canonical key); enumerate linked pairs of `M`
   over non-identity classes only (section 1.1 shows `[eps]` cannot occur in
   a linked pair — assert `s != [eps]` and `e != [eps]`) and fill `P` by one
   membership query each (or from cache) on `member(key(s), key(e))` — both
   keys non-empty by section 1.1; emit `.sosg`.

   Export soundness caveat: the exported invariant decides lassos by
   multiplying *classes* (`M` substitutes a representative in the middle of
   a product), which is meaningful only for a **two-sided** (saturated)
   congruence. An export taken from a fixpoint reached without saturation
   may be acceptance-wrong even though the hypothesis's own predictions are
   all correct (observed on `F(a & Xa)` — see `sosl_report.md`). Such
   exports are diagnostic artifacts, not deliverables; see sections 3.3
   and 9.

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

`sos_validate learned.sosg reference.sosg` — byte comparison after parsing and
re-canonicalization (defensive: re-sort accept pairs, normalize whitespace).
Also `sos_validate --acceptor learned.sosg <file.hoa> --bound B`: checks the
invariant's membership read-off against direct simulation on all lassos up to
`B` — used to certify *acceptance-correctness* separately from canonicity
(needed by experiment E2).

Scope rule (normative): `--acceptor` accepts either a `.sosg` invariant or a
`CAYLEY` hypothesis. For any fixpoint reached **without** saturation (M2
builds, `--no-saturation` runs), it MUST be pointed at the Cayley form: the
`.sosg` read-off presumes a two-sided congruence (section 3.2 step 6 caveat)
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
   reference.sosg                learned.sosg + stats.json + audit.log
        |                                |
        +---------> sos_validate <-------+
                        |
              per-case verdict: SOUND / MISMATCH / BUDGET
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
4. **End-to-end gate.** On the full corpus: `learned.sosg` byte-equals
   `reference.sosg`. This is the soundness criterion. A `MISMATCH` is always
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
   tested bound). Their *exported* `.sosg` is NOT required to pass — the
   export read-off presumes a two-sided congruence and may legitimately
   disagree (sections 3.2/3.3); record the run as `ACCEPTOR_ONLY`. Both
   outcomes are recorded, not hidden.

---

## 6. Experiments

Corpus note. The primary corpus is the in-repo *census* of small deterministic
Emerson-Lei automata (fixed shape families: 2 states / 1 AP / 1 acceptance
set, and the neighboring shapes already enumerated in-repo), for which
reference invariants are computable. Three named languages are mandatory
worked cases in every experiment ("the triptych"):

- `T1`: "infinitely many `aa`" — `GF(a & Xa)` as a 2-state Buchi automaton;
- `T2`: "an even block of `a` then `!a`, then anything" —
  `(aa)*.!a.Sigma^omega`, 4-state Buchi;
- `T3`: "infinitely many `!a` and eventually every completed `a`-block has
  even length" — 2 states, `Fin(0) & Inf(1)` (prefix-independent; the
  hard case for right-congruence-based methods).

**E0 — Validation campaign.** Run the full harness (section 5) over the
corpus. Deliverable: a one-page report — cases, per-case verdict, query
budgets used, zero mismatches. Gate for everything below.

**E1 — Scaling against the target.** Question: do measured costs track the
designed bounds (splits <= number of classes `N`; membership queries
`O(N^2 . |Sigma|)` for the table plus logarithmic counterexample analysis)?
Procedure: for every corpus case record `N` (reference), splits, membership
queries by phase (fill / harvest / saturation / P), equivalence queries,
table dimensions, wall time. Deliverable: scatter plots of each metric vs
`N`, with the designed bound overlaid; a table of the triptych rows in full.

**E2 — Saturation ablation.** Question: how often, and on which languages,
does the learner without saturation stall on a non-canonical fixpoint?
Procedure: run everything twice (`--no-saturation` vs default); classify each
case: (a) identical invariant, (b) acceptance-correct but byte-different or
class-deficient (stall), (c) budget. Deliverable: stall frequency overall and
by structural features (prefix-independence, acceptance type); the *minimal
stall exhibits* — the smallest automata in class (b) — reported individually
with both fixpoints. These exhibits feed the theory side; treat them as a
first-class output, not a statistic.

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

**E4 — Worked transcripts (paper figures).** For the triptych: full audit-log
renderings — table snapshots at each split, every minted column with its
provenance (consistency / stem chain / loop chain / saturation escalation),
every saturation escalation with its witness. Deliverable: three
machine-generated, human-readable traces (markdown), stable across reruns.

**E5 — Counterexample sensitivity.** Question: how much does teacher
counterexample policy affect cost (the `log` term and constants)?
Procedure: re-run the corpus with equivalence strategies returning
(i) minimized counterexamples (default), (ii) first-found from bounded
enumeration, (iii) deliberately padded counterexamples (stem and loop
inflated by pumping a factor 2..32). Metrics: total membership queries,
harvest queries specifically, wall time. Deliverable: sensitivity table;
confirmation (or refutation) that cost grows logarithmically with
counterexample length.

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
max_cex_stem, max_cex_loop, max_query_word_len,
eq_certification (reps|bounded:<B>|exact),
wall_seconds, verdict (SOUND|MISMATCH|BUDGET|ACCEPTOR_ONLY)
```

`ACCEPTOR_ONLY` is reserved for `--no-saturation` runs that pass the acceptor
check but fail byte-equality.

---

## 8. Milestones and acceptance criteria

- **M1 — Teacher + validator.** White-box teacher (member + `reps`/`bounded`
  equiv), `.sosg`/Cayley parsers, `sos_validate`. Accept: harness layer 1
  green on the census; teacher self-check clean.
- **M2 — Learner without saturation.** Table, fill/close/consist, chains,
  export. Accept: harness layers 2–3 green; every census case passes the
  *acceptor* check (on the Cayley hypothesis — section 3.3 scope rule);
  byte-equality passes on all cases where it passes (no claim yet on the
  rest).
- **M2.5 — Convention alignment** *(added 2026-07-06; do this before M3).*
  (a) Fix the reference builder to the fresh-identity convention of
  section 1.1. Regression gate: `GF(aa)` stays 6 and `Even` stays 5;
  `EvenBlocks` moves 7 -> **8** (the previously published 7 was itself an
  instance of this bug — see section 1.1 and the correction in
  `sosl_report.md`); `GF a` moves 2 -> 3; `F a` stays 3; `a U b` stays 4.
  Also regenerate `research_notes/sosg_figs/sources/*.md` (the current
  `evenblocks.md` embeds the buggy 7-class algebra in every table it
  contains). (b) Revert the
  learner's eps-merge (restore the section 3.2 singleton rule) in the same
  working session as the fixture regeneration, so reference and learner
  never disagree for a spurious reason in between. (c) Re-baseline the M2
  status table by *appending* to `sosl_report.md` (never overwrite the old
  table); the theory reply there ("What to expect after M2.5") lists the
  predicted per-case outcomes. Accept: reference and learner agree on
  `GF a`; no assertion fires on the census; the re-baselined table is
  committed.
- **M3 — Saturation + exact equivalence.** Accept: end-to-end gate (layer 4)
  green on the full census; metamorphic checks green; E0 report produced.
  Additionally: run `--no-saturation --eq-mode exact` on `F(a & Xa)` and
  record whether the stall is permanent — this either mints the paper's
  open exhibit or closes the candidate; **both outcomes are wanted
  results**, do not tune anything to make this run "pass".
- **M4 — Campaign.** Driver, ROLL wrapper, E1–E5 executed, results CSV and
  figures generated by script (no hand-edited numbers anywhere).

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
| F2 | acceptor check on the exported `.sosg` | M2 / `--no-saturation` | MAY be red | export presumes two-sidedness (3.2 step 6 caveat); diagnostic only |
| F3 | equivalence returns a lasso the hypothesis already predicts correctly | any | must NOT happen | teacher bug (equivalence strategy or minimization) |
| F4 | budget exhausted on a census case | any | should not happen | flag it; census cases are sized to finish |

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
