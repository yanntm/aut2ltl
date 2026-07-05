# samples/sosl — fixtures for the sosl tool

Input automata and expected outputs the `sosl` probes and campaign run against.

## What lives here

- The **triptych** — the three mandatory worked languages, as HOA:
  - `T1` — "infinitely many `aa`", `GF(a & Xa)`, a 2-state Büchi automaton;
  - `T2` — "an even block of `a` then `!a`, then anything",
    `(aa)*.!a.Σ^ω`, 4-state Büchi;
  - `T3` — "infinitely many `!a`, and eventually every completed `a`-block has
    even length", 2 states, `Fin(0) & Inf(1)` (prefix-independent — the hard
    case for right-congruence methods).
- The small **census** of deterministic Emerson-Lei automata (fixed shape
  families) used as the primary corpus.
- Expected reference invariants (canonical serialization) alongside their
  sources, where pinned as golden files.

## See also

Corpus and experiment definitions: `research_notes/sos_learner_spec.md` §6.
Probes that consume these: `tests/sosl/`.
