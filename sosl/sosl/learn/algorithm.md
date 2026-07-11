# learn — the learner algorithm

Dev-facing. How the observation table is grown, how classes split, and why the
saturation phase and the counterexample chains are what let the learner recover
the *two-sided* congruence (not merely a right-congruence). Code-level layout is
in the README orientation map; this file is the level above the code.

The specification of record is `research_notes/sos_learning_spec.md` §3.2; this
document is the working reconstruction the implementation follows.

## Data structures (contracts, not layout)

- **Table.** Rows = a set of *access words* (`ε`, the letters, and promoted
  frontier words `rep·letter`). The frontier is `rows · Σ`. Two column lists
  distinguish rows:
  - `E_lin` — linear columns, each a triple `(x, y, t)`; the entry of a word `p`
    is `member(x·p·y, t^ω)` i.e. `member` of the lasso `(x·p·y, t)`;
  - `E_om` — omega columns, each a pair `(x, y)`; the entry of `p` is
    `member(x, (p·y))` read as the lasso `(x, p·y)` — `p` sits in the *period*.
  `entry[word][column]` is the resulting bit matrix. `ε` is a **permanent
  singleton class** — the fresh adjoined identity. It is never grouped with any
  word by its bit-row, not even a non-empty word that happens to have the same
  bit-row (one that is right-congruent to `ε`, or acts neutrally). No word is
  ever merged into `[ε]`. This is not an optimization to skip: if a non-empty
  word `w` joined `[ε]`, a loop could fold to `[ε]`, and the P-cache would be
  asked for the representative lasso `key(s)·ε^ω` — an empty loop, which is not
  a lasso. Keeping `[ε]` a singleton makes that failure structurally impossible:
  every non-identity class then has a non-empty key, so every representative
  lasso is well-formed. (Matches the `objects/algorithm.md` identity convention;
  the reference builder adjoins its `[ε]` the same way.)
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
   pairs of `M` over the **non-identity** classes only (a linked pair can never
   involve `[ε]` — assert `s ≠ [ε]` and `e ≠ [ε]`), fill `P` by one membership
   query each (or from cache) on `member(key(s), key(e))` — both keys non-empty
   by the identity convention; emit the canonical invariant.

   **Two-sidedness is checked, not assumed (export refusal).** The exported
   invariant decides a lasso by multiplying *classes*: `M(c, c') =
   fold(c, key(c'))` substitutes a class representative *in the middle of a
   product*. That substitution is sound only when the partition is a congruence
   on **both** sides (`u ~ v` must give both `u·x ~ v·x` and `x·u ~ x·v`). A
   table closed under fill/close/consist alone guarantees only the right-hand
   half. Export therefore runs the congruence test first — the saturation
   sweep's **check phase** on the final table (`find_left_divergence`: for
   every table word `p` with `rep(class(p)) ≠ p` and every class `d`, compare
   `fold(d, p)` with `fold(d, rep(class(p)))`; zero queries) — and **refuses**
   on a dirty check: a non-congruent partition has *no algebra to read off*,
   and on an exactly-certified fixpoint the check clean forces the export
   canonical (paper Lemma 5.2 / Theorem 5.3). A refused run is still a correct
   *acceptor*: the Cayley hypothesis folds the literal letters of a queried
   lasso and never substitutes a representative. An `unchecked` export
   bypassing the test exists to *display* what the raw read-off would produce
   (it can be acceptance-wrong and non-associative) — a diagnostic artifact,
   never a deliverable. On a saturated run the final sweep just ran clean, so
   no recheck is needed: saturation (below) is what makes the fixpoint a
   congruence at all.

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

- let `κ` be a column separating `rep(c_a)` from `rep(c_b)` (one must exist; if
  several do, the FIRST in creation order); with `r = rep(d)`, query the two bits
  of `r·p` and `r·r0` under `κ`'s context;
- **if the bits differ** — mint the column that reproduces "`r·w` under `κ`" as a
  bit on the bare candidate `w`, which splits `class(p)`. For a **linear** `κ` the
  candidate sits in the finite prefix, so `r` prepends there: `(x·r, y, t)`. For
  an **omega** `κ` the candidate rides in the period; peeling one `r` off the
  block, `x·(r·w·y)^ω = x·r·(w·y·r)^ω`, so `r` seeds BOTH the prefix and the
  period suffix: `(x·r, y·r)`. (`(x·r, y)` keeps the period `w·y` and fails to
  split on a prefix-independent language such as `GF(aa)`.)
- **if the bits agree** — one of the two words disagrees with the representative
  of its own fold class under `κ`; run the **frozen-prefix chain** (the stem chain
  with `κ`'s own prefix `x0` frozen inside the queried context) on that word; this
  splits some class. The minted flip column keeps the prefix `x0` ALONE — the
  unconsumed segment migrates into the middle component, `(x0, seg·y0, t0)` /
  `(x0, seg·y0)` — never into the prefix (spec §3.2 step 5, paper Lemma 4.5).

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
