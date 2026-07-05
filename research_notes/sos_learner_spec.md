# SoS Learner — Implementation and Experimentation Specification

**Status:** specification / declaration of intent. Everything below is to be
implemented; nothing below exists yet except where explicitly marked
*(exists in-repo)*.

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
  column. (`eps` never enters omega-column comparisons; it is a permanent
  singleton class, the identity.)
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
   reaching a class is its canonical key); enumerate linked pairs of `M` and
   fill `P` by one membership query each (or from cache); emit `.sosg`.

Main loop: `fill; close; consist;` to fixpoint, then `saturate` (restart on
split), then `equiv`; on counterexample process and restart; on `eq` run
`export` and stop. With `--no-saturation` step 4 is skipped entirely.

Hard invariants (assert, and record in the audit log):

- every class split stores its *witness*: the column and the two differing
  membership bits (with the exact queried lassos) — replayable;
- the class count never decreases and never exceeds the reference class count
  in white-box runs (checked post hoc by the harness, not by the learner);
- all runs are deterministic given the teacher's answers.

### 3.3 Validator *(thin wrapper, mostly exists in-repo)*

`sos_validate learned.sosg reference.sosg` — byte comparison after parsing and
re-canonicalization (defensive: re-sort accept pairs, normalize whitespace).
Also `sos_validate --acceptor learned.sosg <file.hoa> --bound B`: checks the
invariant's membership read-off against direct simulation on all lassos up to
`B` — used to certify *acceptance-correctness* separately from canonicity
(needed by experiment E2).

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
6. **Ablation coherence.** `--no-saturation` runs must still pass
   `sos_validate --acceptor` (acceptance-correct at their fixpoint) even when
   they fail byte-equality. Both outcomes are recorded, not hidden.

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
  *acceptor* check; byte-equality passes on all cases where it passes (no
  claim yet on the rest).
- **M3 — Saturation + exact equivalence.** Accept: end-to-end gate (layer 4)
  green on the full census; metamorphic checks green; E0 report produced.
- **M4 — Campaign.** Driver, ROLL wrapper, E1–E5 executed, results CSV and
  figures generated by script (no hand-edited numbers anywhere).

Non-goals for this iteration: performance tuning beyond the budgets above,
black-box teachers other than the wire protocol, alphabets beyond `2^AP`,
any use of external solvers in the learner path. The learner must remain a
pure query algorithm: its only source of truth is the teacher interface.
