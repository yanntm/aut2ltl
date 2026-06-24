# The non-LTL witness

When the definability gate (`bls/definability`) finds the transition monoid
non-aperiodic, the language is not LTL-definable and the cascade reports `NOT_LTL`.
A bare verdict asks the user to trust the oracle. This module produces a **witness**:
a finite object that exhibits the counting forbidding LTL, carried alongside the
`NOT_LTL` as a diagnosis complement. It is a variant of the definability decision —
same input, same oracle machinery — that on the non-aperiodic branch extracts
witness material from GAP instead of stopping at the boolean.

It produces the material; checking it is a separate concern (see
`research_notes/non_ltl_certificates.md` and the witness verifier).

## The input

The same representation the gate reads: `det_generic_minimal()`, completed, then
`extract_generators` → `(gens, masks, valuations)`. The form is read for the same
reason — on a state-minimal deterministic automaton the transition monoid is faithful
to the **syntactic semigroup**, so the group it carries is the language's, not an
encoding artifact. One difference: the witness variant keeps `masks` / `valuations`
(the gate discards them as `_`), because lifting a group element back to concrete
letters needs the letter↔generator correspondence.

## What it produces — the counting family

A witness is a counting family `(u, v, x, p)` with period `p > 1` (research note
§3): finite words `u`, `v`, an ultimately-periodic tail `x`, such that membership of
`u·vⁿ·x` toggles with `n mod p`. `v` is the group element (the period), `u` reaches
a state where `v` acts with a non-trivial orbit, `x` discriminates the phases.

The family is the readable narration of the underlying proof object: a `p`-cycle of
inequivalent residuals that `v` permutes (research note §3.2). The module emits the
words; the verifier replays them.

## Extracting the group element from GAP

The aperiodicity oracle (`gap/aperiodic`) returns a boolean. The witness needs more,
so it drives a second, witness-only GAP script in `gap/`, alongside the aperiodicity
script. It returns:

- a non-trivial group H-class — a regular H-class that is a group, exactly what a
  non-aperiodic semigroup contains (Green's theory);
- a generator `g` of its Schützenberger group, of order `p > 1`;
- a `Factorization` of `g` over the monoid generators — a word in generator indices.

Lift: generator index `i` corresponds to letter `i` (its `valuations[i]`), so the
factorization is a finite word `v` over concrete letters. Gotcha: GAP acts on the
right; the composition order must match the image-list convention or `v` comes out
reversed — the lifted `v` is checked against the automaton before it is trusted.

## Completing the family (u, x)

From the automaton and `v`'s induced transformation:

- `u` — a word reaching a state `q` on a non-trivial `v`-orbit (`q, v(q), …`
  distinct), found by search from the initial state.
- `x` — an ultimately-periodic word separating two phases of the orbit (a tail in
  the residual of one phase and not the other). Distinguishability on the minimal
  form guarantees it exists; it must not be a power of `v` (research note §3.3).

## Scope

Verification of the produced witness is a separate concern (the witness verifier);
this module only emits the material. Whether a completed witness upgrades a
non-conclusive verdict to a proof (research note §5) is a property of the object,
asserted in the diagnosis, not computed here.

## Modules

- `witness.py` — the variant entry: prep the form (shared helpers), call the witness
  GAP script, lift the factorization to `v`, complete `u` / `x`, return the family.
- the witness GAP script in `gap/` — from the generator images, find a non-trivial
  group H-class and a factorization of one of its generators; print `p` and the
  factorization. A new sibling of `gap/aperiodic.py`.

## Layering

Same as the gate: above the floor, the GAP oracle, and the extractor; it imports
neither `Cascade` nor any `Translator`. The non-definable branch of the cascade gate
(`aut2cas`) carries the returned witness as a `NOT_LTL` diagnosis complement.
