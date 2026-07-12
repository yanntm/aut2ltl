# Acceptance-pair decomposition (pairsplit)

A language-plane combinator: recurse on the ∧/∨ structure of the acceptance
condition over one deterministic body, translate the atomic pieces
independently, recombine the labels with the same connective. Purely a
`Translator → Translator` decorator: no engine, pipeline, or delegate is
touched; every piece re-enters the standard pipeline as an ordinary
`Language`.

It is the acceptance-plane member of the `aut2ltl/decomp/` family and
generalizes `decomp/acceptance` (the one-level, ∧-only split) with the dual
∨-branch and a structural recursion; see "Relatives" below.

## The two identities

Fix an automaton `A` and read its acceptance condition as a formula over the
`Fin(m)`/`Inf(m)` atoms. With `A[acc := c]` = the same body carrying
sub-condition `c` alone:

    Acc = ⋁_p c_p   ⇒   L(A) = ⋃_p L(A[acc := c_p])          (union, any A)
    Acc = ⋀_i c_i   ⇒   L(A) = ⋂_i L(A[acc := c_i])          (intersection, A deterministic)

The union is presentational — a run satisfies some disjunct. The intersection
needs determinism (`decomp/acceptance`'s identity): each word has exactly ONE
run, and that run satisfies `⋀ c_i` iff it satisfies every `c_i`; on a
nondeterministic body different conjuncts may be met by different runs and the
intersection over-accepts. Determinism is established by the query — the
vehicle is `Language.det_generic()` — never assumed of the input.

LTL is closed under ∨ and ∧, so both identities transcribe to labels:

    φ = ⋁_p φ_p          (∨ at the top)
    φ = ⋀_i φ_i          (∧ at the top)

## The recursion

Split at the TOP connective of the acceptance code; pieces (one per child)
re-enter the decorated translator as fresh `Language`s; an ATOMIC acceptance
(no top ∧/∨ of arity ≥ 2) passes through to the inner translator — the base
case, and the pass-through that makes the decorator invisible where it cannot
help. Each level strictly shrinks the code, so the recursion is structurally
bounded; a small depth cap guards the one indirect risk (a piece's own
`det_generic` normalization re-widening its condition).

No complement move is needed: dualizing only swaps ∧↔∨ and Fin↔Inf, and both
connectives split natively — the worked specimen `GFa ∧ GFb`
(one-state body, `Inf(0) ∧ Inf(1)`) splits directly into the two
generalized-Büchi atoms and recombines as `φ_{GFa} ∧ φ_{GFb}`.

## Pair fusion — pieces that pair well stay together

The split need not be maximally fine: sibling atoms of matching polarity fuse
EXACTLY, the acceptance analogue of letter fusion (one summand per outcome
class, guards OR-ed):

    Inf(i) ∨ Inf(j)  ≡  "some mark of {i,j} recurs"     (one piece, at an ∨ node)
    Fin(i) ∧ Fin(j)  ≡  "all marks of {i,j} die out"    (one piece, at an ∧ node)

At each node the pure-`Inf`-atom children (under ∨) or pure-`Fin`-atom
children (under ∧) are grouped into a single piece whose acceptance is their
connective; the piece's own normalization merges the marks. Fused pieces go
to the INNER translator directly — re-entering the recursion would just
re-split them. The opposite polarities do NOT fuse (`Fin(i) ∨ Fin(j)` and
`Inf(i) ∧ Inf(j)` are genuine two-piece splits). Fusion is exact and strictly
reduces the piece count, so it runs unconditionally.

A finer grouping is open: pieces identical up to an AP permutation (the
`FG¬a` / `FG¬b` symmetry — one machine, relabeled) could translate once and
instantiate per piece by atom substitution (`aut2ltl.ltl.builders._subst_f`),
the acceptance analogue of the operators' skeleton templates. Needs a
relabeling-canonical fingerprint to detect the class; queued, not
implemented.

## Verdict discipline

- **Success is exact.** If every piece translates to LTL, `L` IS LTL (closure
  under ∨/∧) and the assembled formula defines it — no new proof obligation
  beyond the inner translator's own.
- **A piece's NOT_LTL is inconclusive for `L`.** The pieces are artifacts of
  one presentation of `L`; `L` can be LTL while a piece is not. Any piece
  outcome other than success makes the combinator DECLINE, carrying the
  piece's diagnosis. It never converts a piece verdict into a language
  verdict; NOT_LTL for `L` can only come from a translator that saw `L`
  itself.

## Relatives (the `decomp/` family) and limits

- `decomp/acceptance` — the ∧-only, one-level ancestor (top conjuncts,
  intersection, leaf delegation). This module subsumes it on the acceptance
  plane and adds the ∨-branch, the mixed recursion, and pair fusion.
- `decomp/scc`, `decomp/strength` — the STATE-plane unions (per accepting
  SCC / per Manna–Pnueli strength). They catch what this split cannot see:
  acceptance minimization can compile a union into state structure —
  `FGa ∨ FGb` normalizes to a single-`Fin` co-Büchi on a restructured body,
  atomic here, but its disjuncts sit in separate SCCs there. The two planes
  compose as decorators around the same inner.
- `decomp/inv` — the AP-plane factorization (strip the guard-disjunction
  invariant `G(Σ)`, translate the simplified residual, re-assert): drops an
  obligation and can free an AP entirely. Also composes.
- Their cost caveat carries: a split inflates the answer wherever the leaf
  already succeeds whole — the historic route parks these under a
  cost/`best_of` gate. Here the atomic pass-through covers the current
  stratum; a gate remains an option when the corpus says so.

## Normalization and cost

The vehicle is `Language.det_generic()` — deterministic (the ∧-branch's
precondition) with GENERIC acceptance, whose condition keeps the natural
∧/∨ structure (a parity normalization would re-encode `Inf(0) ∧ Inf(1)` into
a bigger body and hide the split). The split is one acceptance rewrite per
piece on a structural clone (`aut2ltl.ltl.twa.clone_structural` — the clone
that drops the properties an acceptance rewrite invalidates); pieces are
interned `Language`s (`Language.of`), so repeated pieces across a portfolio
run are translated once. Total: ≤ #atoms inner runs on strictly-simpler
acceptances, plus one ∨/∧ recombination per level.
