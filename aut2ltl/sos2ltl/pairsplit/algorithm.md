# The SoS pair decomposition (pairsplit)

Decompose a translation problem on the invariant itself: the language is a
set `P` of accepting linked pairs over the algebra `(𝒞, λ, M)`, and
`h⁻¹` commutes with every Boolean operation — so complement, union and
intersection of languages over the SAME algebra are set operations on `P`
(`sosl.sos.calculus`), exact with no side condition. The decomposition
splits `P`, translates each part as its own language over the same table,
and recombines the labels. This is the general form that the automaton-level
`aut2ltl/decomp/` family (acceptance / scc / strength / inv) shadows through
presentations; here there is no presentation to fight — no determinization,
no dualize, no acceptance minimization hiding the structure.

## The atoms

A subset of linked pairs is a language iff it is SATURATED (closed under the
equivalence of linked pairs that denote the same ω-class —
`calculus.surgery.saturate` / `pair_language`). The finest split of `P` is
therefore its partition into saturation orbits — the accepting ω-classes:

    P = ⊎_k  A_k          ⇒        L(P) = ⋃_k L(A_k)

one atom = one "accepting pair" in the operative sense, and the union is
exact by preimage. Every piece `L(A_k)` lives on the same table; `reduce`
(partition refinement) returns its canonical invariant.

## The general form

1. **Least pairs, complement free.** `L(P̄)` is the complement on the same
   table (a set flip, `calculus.surgery`). Work on whichever of `P` / `P̄`
   has fewer atoms; an outer `¬` on the label undoes the flip. This is the
   whole ∧/∨ business of the automaton route collapsed by De Morgan: with a
   free complement, ONE connective (∨ over atoms) plus negation expresses
   both — the conjunctive-recurrence stratum (`GFa ∧ GFb`) is precisely the
   case where `P̄` splits into trivial atoms while `P` is one hard block.
2. **Fuse the pairs that pair well.** Atoms need not be translated one by
   one; a grouping criterion coarsens the partition (below), and each group
   is one piece — the acceptance analogue of letter fusion.
3. **Translate the pieces** — same pipeline, per piece: `reduce` to the
   canonical invariant, engine on that invariant. Recombine:

       φ  =  ⋁_g φ_g            (¬ outside iff the complement side was taken)

## Fusion criteria (pairing well)

- **Same loop.** Atoms sharing their loop ω-class differ only in the stems
  that reach it: one piece per loop class, stems unioned — the loop content
  is translated once, the stem disjunction fuses (letter-fusion shape:
  many guards, one summand).
- **Same layer.** Group atoms by the layer (R-class of the right-Cayley DAG)
  their loop class lives in — the SoS shadow of the scc / strength
  decompositions: one piece per recurrence site, prefixes shared.
- **Free APs per piece** (the `decomp/inv` shadow, exact here): restricting
  `P` can make an AP free — the piece does not depend on it although `L`
  does. `sosl.sos.minimize.remove_free_aps` projects the piece onto its
  minimal alphabet BEFORE the engine sees it: dropping an obligation frees
  an AP, and the piece's whole construction shrinks with the alphabet.
- **Alphabet symmetry** (queued): atoms equal up to an AP permutation
  translate once and instantiate by substitution
  (`aut2ltl.ltl.builders._subst_f`), the label-level analogue of the
  operators' skeleton templates. Needs the invariant's canonical form up to
  renaming (the `.sos` byte-equality machinery) to detect the class.

## Verdicts inherit — the piece caveat (almost) vanishes

Every piece is recognized by the SAME algebra, and `reduce` only merges
classes: aperiodicity is inherited. So when `𝓘(L)` is aperiodic (L is LTL),
EVERY piece is aperiodic — definable, no piece can come back NOT_LTL. This
is the structural advantage over the automaton-level split, where pieces
were artifacts of a presentation and their verdicts said nothing about `L`.
When `L` is NOT definable, closure under ∨/¬ forces some piece to be
non-definable too — its witness (from its own canonical invariant) is a
genuine certificate for that piece; the combinator still reports `L` only
through what saw `L` itself. A piece the engine declines poisons the split:
DECLINE, with the piece's diagnosis.

## Where it sits

Below the bridge, above the engine:

    Language ──bridge──▶ 𝓘(L) = (𝒞, λ, M, P)
                              │ split P (atoms → fused groups; side by least pairs)
                              ▼
                 per piece: reduce → minimal alphabet → engine
                              │
                              ▼
                    ⋁ labels  (¬ outside iff complemented)

One injection seam in the sos2ltl assembly; the engine, the delegate and the
calculus are consumed as-is. Interface point to resolve at wiring time: the
cascade delegate's loop half consults the language's deterministic acceptor
presentation (`det_parity_sbacc`) — a piece needs one too (from its reduced
invariant via the reference construction, or by restricting the acceptance
of `D`); the stem half and the engine proper consume the invariant alone.

## Cost

The table is shared by all pieces; `reduce` is `O(|𝒞|²)` partition
refinement per piece; free-AP projection can only shrink the alphabet; each
engine run sees the same-or-smaller algebra with a one-atom (or one-group)
accepting set. The corpus stratum this targets — the conjunctive-recurrence
TIMEOUTs — is exactly "multi-atom `P̄`, trivial atoms": pieces the engine
already handles in milliseconds. As with every decomposition, the split can
inflate the answer where the engine succeeds whole; the atomic pass-through
(singleton `P` side chosen uncomplemented) keeps it invisible there, and a
cost gate stays an option when the corpus says so.
