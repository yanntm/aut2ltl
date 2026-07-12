# aut2ltl.sos2ltl.pairsplit — acceptance-pair decomposition combinator

Splits a translation problem by acceptance pair over the same deterministic
body and ORs the piece labels, complementing first when the complement side
splits finer. `algorithm.md` holds the construction (the union split, the
complement move, the choice rule, verdict discipline); this file maps it to
the code.

## Shape

A pure decorator on the `Translator` protocol:

    PairSplit(inner: Translator) -> Translator

`PairSplit(inner)(lang)`:

1. normalizes `lang.det_generic()`, builds the dual body, puts both
   acceptance conditions in DNF;
2. scores both sides `(max disjunct width, #disjuncts)` and picks the smaller
   (ties → uncomplemented); pass-through to `inner` when the split cannot
   help;
3. rewrites the chosen body's acceptance once per disjunct
   (`aut2ltl.ltl.twa.clone_structural`), wraps each piece as a fresh
   `Language`;
4. translates each piece through ITSELF (recursion at the language plane —
   a still-conjunctive piece flips disjunctive under its own complement;
   bounded by the atom count), `inner` being the base of the recursion;
5. on all-success: `Or` of the piece formulas, negated if the dual side was
   chosen — `LTLResult.success`, techniques fused from the pieces plus
   `pairsplit`. Any piece failure (decline OR not-LTL) is a DECLINE with
   that piece's diagnosis: a piece's NOT_LTL says nothing about `L`
   (algorithm.md "Verdict discipline").

## Files

- `split.py` — everything: DNF/scoring helpers, piece construction,
  `PairSplit`.

## Consumption

Orthogonal by construction — no existing module changes. A recipe injects it
around any translator, e.g. `PairSplit(sos2ltl_casc)` under the usual
recipe-boundary `hi` simplifier. Target stratum: conjunctive recurrence
(`GFa ∧ GFb` and friends — the validation TIMEOUT family).
