# sosl.teacher — teachers that answer queries about a known language

Concrete implementations of the `sosl.contract.Teacher` interface: a correct
membership + equivalence oracle for a language whose presentation *is* known,
exposed to the learner only through queries.

## Services

- **White-box teacher over an HOA automaton.** Wrap a deterministic, complete,
  transition-based Emerson-Lei automaton `D` as a teacher:
  - `member(u, v)` — decided by simulating `D` (no external tools, no
    timeouts); cost `O(|u| + |Q|·|v|)`.
  - `equiv(H)` — three combinable strategies (`reps`, `bounded:B`, `exact`)
    with a documented default escalation; the returned counterexample is
    minimized for determinism. The strategy that certified an `eq` answer is
    recorded so a run certified only by bounded enumeration can be flagged.
- **Black-box teacher over a process.** A client for the line-oriented JSON wire
  protocol (`proc:` mode), so a teacher can live in another process/language and
  still be driven identically. The white-box teacher implements the same
  interface internally.

The equivalence strategies and the reference-key audit lean on `sosl.sos.build`
(hence on `aut2ltl`/spot); membership does not. `exact` additionally leans on
`sosl.sos.calculus`, which decides it against the language's reference invariant
rather than against the automaton. The learner sees none of this — only `member`
and `equiv`.

## Orientation map

    whitebox    Teacher over an HOA automaton D (member by simulation)
    equiv       the reps / bounded strategies + cex minimization
    exact_ref   exact by alignment with the reference invariant (polynomial)
    exact       exact by transformation closure (the referenceless fallback)
    blackbox    the proc: JSON wire client
    selfcheck   two independent membership impls compared (harness layer 1)

## See also

`algorithm.md` — how membership is simulated on a lasso and how each
equivalence strategy searches for (and minimizes) a counterexample. Spec of
record: `research_notes/sos_learner_spec.md` §3.1.
