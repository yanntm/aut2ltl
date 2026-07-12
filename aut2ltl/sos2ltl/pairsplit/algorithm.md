# Acceptance-pair decomposition (pairsplit)

A language-plane combinator: split a translation problem into per-acceptance-pair
sub-languages over the SAME deterministic body, translate each piece
independently, OR the labels — complementing first when the complement is the
side where that split is finer. Purely a `Translator → Translator` decorator:
no engine, pipeline, or delegate is touched; every piece re-enters the standard
pipeline as an ordinary `Language`.

## The identity

Fix any automaton `A` and put its acceptance condition in disjunctive normal
form over the `Fin(m)`/`Inf(m)` atoms:

    Acc  =  ⋁_p  D_p        with   D_p = ⋀_i Fin(E_i) ∧ ⋀_j Inf(F_j)

A run is accepting iff it satisfies some disjunct, so with `A_p` = the same
body carrying acceptance `D_p` alone:

    L(A)  =  ⋃_p L(A_p)                                            (union split)

Each `A_p` is a generalized-Rabin-1 automaton. The identity is presentational —
it needs nothing from `A` (not even determinism), only that the body is shared.

## The complement move

The split only exists on a disjunctive condition. A conjunctive condition
(one fat disjunct — the generalized-Büchi `⋀ Inf(F_j)` shape) does not split;
but on a DETERMINISTIC body the dual automaton (same body completed, negated
acceptance) recognizes the complement, and negation turns the fat conjunct
into many thin disjuncts:

    ¬(Inf(0) ∧ Inf(1))  =  Fin(0) ∨ Fin(1)

LTL is closed under ∨ and ¬, so both moves are free at the formula level:

    φ_L  =  ⋁_p φ_p            (split side = L)
    φ_L  =  ¬ ⋁_p φ_p          (split side = ¬L)

## The choice rule

The cost driver per piece is the WIDTH of its disjunct (its atom count) — a
piece with acceptance `Inf(0) ∧ Inf(1)` is the whole original problem again,
while `Fin(0)` alone is co-Büchi-shaped and easy. The pair COUNT is secondary:
pieces multiply inner runs linearly, atoms compound one run. So, with both
sides' acceptance in DNF,

    score(side)  =  ( max_p |D_p| ,  #disjuncts )      (lexicographic)

pick the side with the smaller score; ties go to `L` (no outer negation).
Worked on the type specimen `GFa ∧ GFb` (deterministic generalized-Büchi,
one state):

    L  : Inf(0) ∧ Inf(1)      score (2, 1)
    ¬L : Fin(0) ∨ Fin(1)      score (1, 2)   ← chosen

so the emission is `¬(φ_{FG¬a} ∨ φ_{FG¬b})`, two trivial co-Büchi
translations instead of one conjunctive-recurrence timeout. On an input that
is already disjunctive (`FG¬a ∨ FG¬b`) the rule keeps `L` and splits it
directly. A parity chain scores near-identically on both sides and stays
uncomplemented.

## Recursion — the split is a fixpoint at the language plane

A chosen side can still contain fat disjuncts (a DNF `D_1 ∨ D_2` with
`|D_1| > 1`). No further union split applies to `D_1` — but `D_1`'s OWN
complement is again disjunctive. So pieces are handed back to the DECORATED
translator (self), not to the inner one: each piece is re-scored and re-split
as a fresh problem. Termination: a piece carries one disjunct; if `|D| = 1`
the score is (1, 1) on the piece side and the pass-through fires; if `|D| > 1`
its complement splits it into `|D|` single-atom pieces — the max width
strictly decreases. The recursion depth is bounded by the atom count of the
original condition.

Pass-through (the degenerate case): when the chosen side is `L` and its DNF
is a single disjunct of width ≤ 1 — or the split would yield one piece
identical to the input — the ORIGINAL `Language` goes to the inner translator
unchanged. The decorator is invisible on inputs it cannot help.

(The finer, in-engine variant — applying the same move per LAYER label inside
the loop-half delegate — is pending the Σᵢ/Πᵢ fragment bookkeeping; see the
handoff's theory queue. This combinator is the language-plane instance, whose
soundness needs only closure under ∨/¬.)

## Verdict discipline

- **Success is exact.** If every piece translates to LTL, `L` IS LTL (closure
  under ∨/¬) and the assembled formula defines it — no new proof obligation
  beyond the inner translator's own.
- **A piece's NOT_LTL is inconclusive for `L`.** The pieces are artifacts of
  one presentation of `L`; `L` can be LTL while a piece is not. Any piece
  outcome other than success makes the combinator DECLINE, carrying the
  piece's diagnosis. It never converts a piece verdict into a language
  verdict; NOT_LTL for `L` can only come from a translator that saw `L`
  itself.

## Normalization and cost

The vehicle is `Language.det_generic()` — the deterministic generic-acceptance
form, whose condition keeps the natural generalized structure (a parity
normalization would re-encode `Inf(0) ∧ Inf(1)` into a bigger body and hide
the split). The dual side is Spot's `dualize` on that body (deterministic ⇒
complement; a completion sink may be added). Both DNFs are O(|Acc|); the
split is one acceptance rewrite per piece on a structural clone
(`aut2ltl.ltl.twa.clone_structural` — the clone that drops the properties an
acceptance rewrite invalidates); pieces are interned `Language`s
(`Language.of`), so repeated pieces across a portfolio run are translated
once. Total: ≤ #atoms inner runs on strictly-simpler acceptances, plus one
OR and at most one outer negation per recursion level.
