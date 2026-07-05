# learn — the learner algorithm

Dev-facing. How the observation table is grown, how classes split, and why the
saturation phase and the counterexample chains are what let the learner recover
the *two-sided* congruence (not merely a right-congruence). Code-level layout is
in the README orientation map; this file is the level above the code.

The specification of record is `research_notes/sos_learner_spec.md` §3.2; this
document is the working reconstruction the implementation follows.

## Data structures (contracts, not layout)

- **Table.** Rows = a set of *access words* (`ε`, the letters, and promoted
  frontier words `rep·letter`). The frontier is `rows · Σ`. Two column lists
  distinguish rows:
  - `E_lin` — linear columns, each a triple `(x, y, t)`; the entry of a word `p`
    is `member(x·p·y, t^ω)` i.e. `member` of the lasso `(x·p·y, t)`;
  - `E_om` — omega columns, each a pair `(x, y)`; the entry of `p` is
    `member(x, (p·y))` read as the lasso `(x, p·y)` — `p` sits in the *period*.
  `entry[word][column]` is the resulting bit matrix. `ε` never enters omega-column
  comparisons; it is a permanent singleton class, the identity.
- **Partition.** Classes over rows+frontier by equal bit-rows. Each class has a
  representative `rep(c)` = its shortlex-least word, and a step
  `step(c, a) = class(rep(c)·a)`.
- **Fold.** `ψ(w)` = the letterwise `step` from `[ε]`. Debug invariant, asserted
  after every table op: `ψ(p) == class(p)` for every table word `p`. A
  `fold(d, w)` variant starts the letterwise fold at class `d` rather than `[ε]`.
- **P-cache.** `(s, e) → bit`, filled lazily by `member(key(s), key(e))`, never
  invalidated: keys are words, so a class split mints new keys and hence new
  cache lines; stale lines are dead, not wrong.

## Procedures

All query counts are logged by phase (fill / harvest / saturation / P).

1. **fill** — complete missing `entry` cells with membership queries.
2. **close** — if a frontier word matches no row class, promote it to a row.
3. **consist** — if `p == q` (same class) but `p·a ≠ q·a`, mint the column that
   migrates the letter across: from a separating column of the successors,
   `(x, a·y, t)` (linear) or `(x, a·y)` (omega). Bookkeeping identity (assert):
   the entry of `p` at the minted column equals the entry of `p·a` at the source
   column.
4. **saturate** — the phase that promotes a right-congruence table to the full
   syntactic congruence. See its own section below.
5. **counterexample processing** — turn a mispredicted lasso into exactly one
   class split. See the chains section.
6. **export** — at fixpoint: `M(c, c') = fold(c, key(c'))`; re-key every class by
   BFS over `step` from `[ε]` in shortlex letter order; enumerate the linked
   pairs of `M` and fill `P` by one membership query each (or from cache); emit
   the canonical invariant.

**Main loop.** `fill; close; consist;` to fixpoint, then `saturate` (restart on
any split), then `equiv`. On a counterexample, process it (one split) and
restart. On `eq`, run `export` and stop. With saturation disabled, step 4 is
skipped entirely — the learner still converges to an acceptance-correct
fixpoint, but not necessarily the canonical one.

## Counterexample chains

A counterexample is a lasso `(w, z)` where the hypothesis prediction and the
teacher disagree. Processing it isolates a single adjacent bit flip by binary
search and mints the column that separates the two words straddling the flip.

- **normalize.** Let `k` be the prediction's stabilization power; replace
  `(w, z)` by `(w·z^k, z^k)` so the loop is already at its idempotent power.
- **junction.** One query `member(key(ψ(w')), z')` decides whether the fault is
  on the stem side or the loop side.
- **stem chain.** Bits `g_i = member(key(ψ(w'[1..i]))·w'[i+1..], z')`,
  `i = 0..|w'|`. The endpoints differ; binary-search an adjacent flip at `i`;
  mint the linear column `(ε, w'[i+2..], z')`.
- **loop chain.** Bits `d_i = member(key(ψ(w')), key(ψ(z'[1..i]))·z'[i+1..])`,
  `i = 0..|z'|`. Binary-search a flip; mint the omega column
  `(key(ψ(w')), z'[i+2..])`.
- Every flip splits exactly one class: the frontier word `key(c_i)·letter`
  leaves the class of `key(c_{i+1})`. The `log`-many queries per counterexample
  come from the binary search — the cost claim to verify in E5.

## Saturation (the crux)

A table closed under fill/close/consist is only a **right-congruence**: rows
agree on the linear/omega columns *seen so far*, but two rows in one class may
still be distinguishable when placed as a *left* factor. Saturation hunts those
by a zero-query fold comparison, then escalates to targeted queries only where a
mismatch is found.

For every table word `p` whose class representative `r0 = rep(class(p))` is not
`p` itself, and every class `d`, compare `fold(d, p)` against `fold(d, r0)` — no
queries, pure table folding. On a mismatch `c_a ≠ c_b`:

- let `κ` be a column separating `rep(c_a)` from `rep(c_b)` (one must exist);
  with `r = rep(d)`, query the two bits of `r·p` and `r·r0` under `κ`'s context;
- **if the bits differ** — mint the column with `r` absorbed into the prefix
  (`(x·r, y, t)` or `(x·r, y)`); this splits `class(p)`;
- **if the bits agree** — one of the two words disagrees with the representative
  of its own fold class under `κ`; run the **frozen-prefix chain** (the stem
  chain with a fixed extra prefix `x0` riding inside the queried context, the
  flip column minted as `(x0·key(...), …)`) on that word; this splits some
  class.

Either branch produces exactly one split; the main loop restarts. Saturation
reaching a fixpoint with no mismatch is the certificate that the table is a full
two-sided congruence. This is precisely the phase whose absence makes the
`--no-saturation` ablation stall on prefix-independent languages (the `T3`
worked case).

## Hard invariants (assert; record in the audit log)

- every class split stores its witness — the column and the two differing
  membership bits, with the exact queried lassos — and is replayable;
- the class count never decreases and (in white-box runs, checked post hoc by
  the harness, not by the learner) never exceeds the reference class count;
- a run is deterministic given the teacher's answers.
