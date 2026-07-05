# sosl.reference — the reference invariant from a known automaton

Build the canonical invariant `I(L)` directly from an HOA automaton, as an
independent oracle to check the *learned* invariant against. This is the
ground truth of the soundness harness.

## Services

- **`reference(hoa) → Invariant`.** Compute the canonical
  `(C, key, λ, M, P)` for the language of a deterministic Emerson-Lei automaton
  and hand it back as a `sosl.objects` invariant, serializable to the same
  canonical form the learner emits.

This is an **adapter**. The real construction already exists in-repo
(`tests/sosg/` over `aut2ltl/bls/definability` and `tests/probes/dg_common`); it
is spot-backed and heavy. This module wraps it behind the `sosl.objects`
vocabulary so the teacher and the validator can use one reference without
knowing where it comes from.

## Who uses it, who must not

- **The teacher** uses it for the `reps`/`exact` equivalence strategies and for
  the membership self-check.
- **The validator** uses it as the byte-equality reference.
- **The learner must never import it.** The learner is a pure query algorithm;
  pulling the reference in would let automaton structure bypass the teacher
  interface. The layering forbids the edge.

## Status

Skeleton. Wraps the existing `tests/sosg` builder for now; a planned *SoS*
refactor promotes that builder out of `tests/` into a first-class module, at
which point this adapter thins to a rename. No `algorithm.md` here — the
algorithm lives in the definability pipeline (`docs/algorithm.md`,
`aut2ltl/bls/definability`), not in this wrapper.
