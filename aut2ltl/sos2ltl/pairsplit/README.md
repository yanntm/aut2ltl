# aut2ltl.sos2ltl.pairsplit — acceptance-pair decomposition combinator

Recurses on the ∧/∨ structure of the acceptance condition over one
deterministic body, translates the atomic pieces independently, recombines
the labels with the same connective. `algorithm.md` holds the construction
(the union and intersection identities, the structural recursion, pair
fusion, verdict discipline, the `decomp/` relatives); this file maps it to
the code.

## Shape

A pure decorator on the `Translator` protocol:

    PairSplit(inner: Translator) -> Translator

`PairSplit(inner)(lang)`:

1. normalizes `lang.det_generic()` and reads the top connective of its
   acceptance code: ∨ → union split (any body), ∧ → intersection split
   (determinism checked — the unique-run identity of `decomp/acceptance`);
   atomic → pass-through to `inner`;
2. fuses sibling atoms of matching polarity (pure `Inf` under ∨, pure `Fin`
   under ∧) into single leaf pieces — the mark-set union;
3. rewrites the body's acceptance once per piece
   (`aut2ltl.ltl.twa.clone_structural`), wraps each as a fresh `Language`;
4. recurses split pieces through ITSELF (structurally bounded; a depth cap
   guards renormalization pathologies), fused pieces go to `inner` directly;
5. on all-success: recombines with the node's connective —
   `LTLResult.success`, techniques fused from the pieces plus `pairsplit`.
   Any piece failure (decline OR not-LTL) is a DECLINE with that piece's
   diagnosis: a piece's NOT_LTL says nothing about `L` (algorithm.md
   "Verdict discipline").

## Files

- `split.py` — everything: DNF/scoring helpers, piece construction,
  `PairSplit`.

## Consumption

Orthogonal by construction — no existing module changes. A recipe injects it
around any translator, e.g. `PairSplit(sos2ltl_casc)` under the usual
recipe-boundary `hi` simplifier. Target stratum: conjunctive recurrence
(`GFa ∧ GFb` and friends — the validation TIMEOUT family).
