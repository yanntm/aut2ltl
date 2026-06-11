# Symbolic DAG representation & folding — working notes

Status: **research direction, not concluded.** This document stores our
current understanding of WHY the FoSSaCS'22 construction explodes in
practice, the measurements that support that reading, and the candidate
counter-measures. Sections marked **OPEN** are unresolved on purpose.
Current implementation state: `kr/STATUS.md`; work queue: `kr/TODO.md`.

## Thesis

The double-exponential of the paper prices the output formula as a **tree**.
The construction as implemented produces a hash-consed **DAG**, and on every
case measured so far the DAG stays small and cheap while only its unfolding
(tree / flat string) explodes. If that observation survives folding and
larger benchmarks, the practical complexity of automata→LTL via cascades is
governed by the DAG, and the paper bound is a statement about an artifact —
the insistence on flat rendering.

## Measurements (2026-06-11 session, true-cascade pipeline)

| case | aut | cascade | build | DAG nodes | unfolded tree | sharing | distinct temporal |
|---|---|---|---|---|---|---|---|
| `G(a->Xb)` | 3 st | 2L [2,2] | 0.08s | 1,173 | ~1.5M | 1,270x | 192 |
| `Ga\|Gb` | 4 st | 2L [4,3] | 0.08s | 988 | 2.0M | 2,044x | 191 |
| `G(p->(qUr))` | 3 st | 2L [2,2], 8 letters | 0.14s | 9,024 | 64.8M | 7,179x | 4,115 |
| `XXXa` | 6 st | 5L [2,2,2,2,2] | 0.18s | 4,948 | 72.0M | 14,559x | 1,076 |
| `(a U b)\|Gc` | — | 3L [2,4,3], 8 letters | 9.5s | (284,608 distinct subproblems) | — | — | — |

Corroborating facts:

- **Construction is never the wall.** All of the above build in ≤10s; the
  five ladder failures labeled CONSTRUCT_TIMEOUT are dominated by the final
  flat `str()` of the result, not by the recursion (e.g. `(a U b)|Gc`:
  9.5s build, serialization blows a 30s budget; one `G(p->(qUr))` fin
  sub-term flattens to 108MB).
- **Sharing compounds with depth and alphabet** (1,270x at 2L/2AP →
  7,179x at 2L/3AP → 14,559x at 5L) — exactly the multiplicative growth the
  bound predicts, and it lands entirely in the unfolding.
- **Memoization is load-bearing.** Before the helper memo, `(a U b)|Gc`
  showed 437k raw reach calls at 91.5% cache-hit rate without finishing;
  with one-expansion-per-distinct-subproblem it completes (284k distinct).
  The subproblem space IS the b^k tail space (see below) — finite, but only
  traversable once each.
- **External rewriting does not help and can't be waited on.** Spot's
  `tl_simplifier` is not sharing-aware; it stalled >10s inside C++ on
  formulas under 2,000 unfolded nodes (watchdog-confirmed). It is out of the
  construction path by policy; this also means *nothing currently folds
  vacuous structure* — the numbers above are raw.
- **Semantics are not in question.** MP ladder: 21 equiv=True (through 4
  levels: `XXa`), zero equiv=FALSE; cover-aware grounding: zero
  contradictions at every depth probed (incl. `XXXa`, `X(a&Xa)` at 5L).
- **Known irreducible answers exist for the X-ladder.** The shape-based
  heuristic (`buchi2ltl/`, `sl` technique) returns `X(X(X(a & XG(1))))` for
  `XXXa` — ~5 tokens. The kr/ construction needs 4,948 DAG nodes for the
  same language. The gap is foldable structure, not information.

## Why it explodes (mechanics, condensed)

The construction speaks one cascade level at a time. Three multiplicative
mechanisms stack:

1. **Tail wrapping.** When level l delegates "reach the firing context" to
   level l+1, the target obligation is wrapped: τ → σ ∧ Xτ, one variant per
   candidate letter σ. Distinct tails ⇒ distinct subproblems ⇒ ~b^k nested
   tail combinations after k levels (b = combined letters per level). This
   is the exponential-in-depth, purest on the X-ladder where each X is one
   level (the cascade is a shift register).
2. **Avoid-conjuncts.** "Stay in s until σ fires" is expressed as one
   recursive reach per leave-letter η ("η does not fire first"), each with
   its own wrapped tail. Directions that spell out, at every junction, the
   full directions for every wrong turn — recursively.
3. **Fin/Muller fan-out.** Acceptance is a DNF over candidate inf-sets M;
   each term conjoins fin(C)/¬fin(C) for EVERY config C, each fin a full
   reach construction.

Hash-consing merges identical recitations, which is why the DAG is 10³–10⁴
nodes where the tree is 10⁶–10⁸. The residual DAG bloat (4,948 vs ~5 for
`XXXa`) is structure the construction emits but cannot see is vacuous:
unreachable firing contexts, avoid-conjuncts over letters that cannot occur
there, tails through dead configs, time-shifted copies of the same
obligation.

## The BDD analogy — what we have, what we lack

| BDD ingredient | our status |
|---|---|
| unique table (node sharing) | HAVE — spot.formula hash-consing |
| computed table (memo) | HAVE — reach lru + helper memo, one expansion per distinct subproblem |
| reduction rules (local canonicalization) | **LACK** — nothing folds since tl_simplifier left the path; only constructor-level constant folding |
| canonical form ⇒ equivalence = pointer equality | **UNREACHABLE in full** — LTL language equivalence is PSPACE-complete, no cheap per-node canonicity exists. Approximations only. |

## Candidate counter-measures (with expected effect)

Ordered; none implemented yet. Success metric throughout: DAG nodes and
distinct temporal subterms on the X-ladder falling from thousands toward
O(depth), with ladder equiv/groundings unchanged.

1. **Object-out API (plumbing, first).** `reconstruct` hands out the
   `spot.formula` object; `str()` on demand only. No semantic effect;
   converts the 7 serialization-bound CONSTRUCT_TIMEOUTs into measurable
   outputs and gives any analysis layer its native input.
2. **Cascade-aware vacuity pruning, during construction.** The builder can
   consult the config graph: drop avoid-conjuncts for letters that cannot
   occur from the relevant contexts, disjuncts whose firing context is
   unreachable, empty Enter/Stay cases. Prunes *memo keys*, so fewer
   subproblems are ever expanded — attacks b^k at its base. Expected to be
   the largest single win on the X-ladder (one live path through the shift
   register).
3. **Own sharing-aware fold pass.** Bottom-up over unique nodes (memoized by
   id, O(DAG) not O(tree)): absorption, X-pulling where it merges tails,
   dead-branch elimination using facts from (2). This is the "reduce" step
   of the BDD analogy, done by us because no external tool walks DAGs.
4. **Budgeted semantic interning.** For subterms under a size cap, decide
   language equality (Spot, subprocess, ≤10s budget per our external-call
   policy) and merge equivalence classes to one representative. Collapses
   the time-shifted-variant axis (`XXXa`'s 1,076 distinct temporal subterms
   are largely the same obligation at different delays). Directly targets
   the 32-acc-set verification wall.

## OPEN questions

- **Soundness boundary of pruning (2).** Which vacuity arguments are
  justified by the paper's invariants vs. by reachability facts the formulas
  quantify over implicitly? Pruning by config-graph reachability is a
  semantic strengthening of the construction — it needs its own correctness
  argument (grounding gives per-case evidence, not a proof). NOT settled.
- **Hierarchy preservation under folding.** The paper's outputs land in the
  right MP class by construction (Lemma 5). Do rewrites (3) and interning
  (4) preserve the syntactic class, or do we need class-aware rule sets?
- **How far does interning get?** If most of the b^k tails are
  language-equal modulo delay, interning is near-canonicalization for this
  formula family; if not, the DAG floor stays well above the heuristic's
  answers. Needs measurement, X-ladder first.
- **Is the DAG the right exchange format at all?** Downstream consumers
  (model checkers, Spot) want flat LTL or automata. A DAG-aware translation
  (Spot authors contacted — our outputs are the ideal client) would close
  the loop without ever flattening; until then verification is grounding +
  word sampling, not translation.
- **Does the thesis survive bigger alphabets?** 2^|AP| explicit letters
  multiply b directly (visible already at 3 APs). On-demand letters / BDD
  guards (TODO P2) may be required before any larger benchmark is honest.

## Benchmark protocol (X-ladder)

For each rung `X^k a` (k = 1..): record build time, DAG nodes, distinct
temporal subterms, unfolded tree, and the irreducible reference (heuristic
`sl` output, ~k+2 tokens). Current raw-pipeline rungs: `Xa` 3L (equiv=True),
`XXa` 4L (equiv=True), `XXXa` 5L (4,948 nodes / 1,076 distinct / grounding
clean). Re-measure after each counter-measure lands; the table belongs in
this file.
