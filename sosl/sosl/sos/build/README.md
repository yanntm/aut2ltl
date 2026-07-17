# sos.build — the reference invariant from a known automaton

Build the canonical invariant `I(L)` directly from an HOA automaton, as an
independent oracle to check the *learned* invariant against. This is the
ground truth of the soundness harness.

## Services

- **`reference(hoa) → Invariant`.** Compute the canonical
  `(C, key, λ, M, P)` for the language of a deterministic Emerson-Lei automaton
  and hand it back as a `sos` invariant, serializable to the same
  canonical form the learner emits.

This is an **adapter** over the canonical construction (`sos.core`): spot
enters only through the importer (`canonical` — determinize, complete,
transition-based Emerson-Lei), and the resource policy (the closure cap, the
`ReferenceError` on blowing it) lives here. The algebra itself — enriched
monoid, congruence, fresh-identity freeze — is `sos.core`'s, documented in
`core/algorithm.md`.

`residuals_of_hoa` reads the residual (right-congruence) automaton off the
same construction: the state partition comes from the core's
`residual_classes` on the closed monoid's loop verdicts, keyed canonically by
shortlex-least reaching words.

## Who uses it, who must not

- **The teacher** uses it for the `reps`/`exact` equivalence strategies and for
  the membership self-check.
- **The validator** uses it as the byte-equality reference.
- **The learner must never import it.** The learner is a pure query algorithm;
  pulling the reference in would let automaton structure bypass the teacher
  interface. The layering forbids the edge.

## See also

`algorithm.md` — why the fresh-identity adjunction matters (the canonicity
argument and its fingerprints; the obligation itself is discharged by
`sos.core`'s freeze today). The construction underneath is `sos.core`
(`core/algorithm.md`). The specification of record is
`research_notes/sos_learning_spec.md` §1.1.
