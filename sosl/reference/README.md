# sosl.reference — the reference invariant from a known automaton

Build the canonical invariant `I(L)` directly from an HOA automaton, as an
independent oracle to check the *learned* invariant against. This is the
ground truth of the soundness harness.

## Services

- **`reference(hoa) → Invariant`.** Compute the canonical
  `(C, key, λ, M, P)` for the language of a deterministic Emerson-Lei automaton
  and hand it back as a `sosl.objects` invariant, serializable to the same
  canonical form the learner emits.

This is mostly an **adapter**: the acceptance-enriched monoid it starts from is
computed by the in-repo definability pipeline (`tests/probes/dg_common` over
`aut2ltl/bls/definability`), which is spot-backed and heavy. This module wraps
that behind the `sosl.objects` vocabulary so the teacher and the validator can
use one reference without knowing where it comes from.

It is not *only* plumbing, though. The pipeline quotients over monoid
*elements*, which merges a non-empty word into the identity whenever their
enriched elements coincide (e.g. `!a` in one-state `GF a`) — a
presentation-dependent class count that breaks byte-equality. Adjoining the
identity as a **fresh** element, so no word class collides with it, is this
wrapper's own obligation. See `algorithm.md`.

## Who uses it, who must not

- **The teacher** uses it for the `reps`/`exact` equivalence strategies and for
  the membership self-check.
- **The validator** uses it as the byte-equality reference.
- **The learner must never import it.** The learner is a pure query algorithm;
  pulling the reference in would let automaton structure bypass the teacher
  interface. The layering forbids the edge.

## See also

`algorithm.md` — the fresh-identity adjunction this wrapper owns (the one part
that is not plumbing) and the regression fingerprints it must reproduce. The
enriched-monoid construction underneath lives in the definability pipeline
(`aut2ltl/bls/definability`, `docs/algorithm.md`), not here. The specification
of record is `research_notes/sos_learner_spec.md` §1.1.
