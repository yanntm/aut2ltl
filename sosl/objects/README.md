# sosl.objects — the shared vocabulary

Pure data types every other component speaks: no automata, no spot, no queries.
This is the floor of the tool. If two components exchange something, it is
defined here.

## Services

- **Letters and the alphabet.** A letter is a valuation of the atomic
  propositions `AP` (the alphabet is `Σ = 2^AP`). Canonical letter encoding and
  ordering used everywhere else.
- **Lassos.** `Lasso(u, v)` denotes the ultimately-periodic infinite word
  `u.v^ω` (stem `u`, non-empty loop `v`). Two ω-regular languages are equal iff
  they agree on all lassos, so a lasso is the only kind of word any component
  ever exchanges.
- **The invariant `I(L)`.** The learned/reference algebra
  `(C, key, λ, M, P)` — congruence classes, canonical shortlex keys, letter
  map, class multiplication table, accepting linked pairs — together with the
  membership read-off (decide any lasso from `I(L)` alone). The classes are
  those of the non-empty words plus a **fresh** adjoined identity `[ε]`, never
  merged with any word's class (see `algorithm.md`, "the identity convention").
- **The Cayley hypothesis.** The *mid-learning* object exchanged during an
  equivalence query. It is deliberately weaker than an invariant (no
  multiplication table is trusted before the end): a step table plus a cache of
  accepting-pair verdicts, with a normative prediction semantics shared by
  teacher and learner.
- **Canonical serialization.** Byte-comparable text formats: the invariant
  form (`.sos`) and the Cayley form. Two languages over the same `AP` are equal
  iff their serialized invariants are byte-equal — this equality *is* the
  soundness criterion of the whole tool.

## Orientation map

    alphabet    letters / Σ = 2^AP; encoding + ordering
    lasso       Lasso(u, v) and lasso algebra (fold, pump)
    invariant   Invariant(C, key, λ, M, P) + membership read-off
    cayley      the Hypothesis (step table + pair-cache) and its prediction
    serialize   .sos (invariant) and Cayley (hypothesis) canonical text I/O

## See also

`algorithm.md` — why the forms are canonical and how membership is read off the
algebra (the subtle part). The specification of record is
`research_notes/sos_learner_spec.md` §1–2.
