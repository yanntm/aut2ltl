# sosl.teacher — teachers that answer queries about a known language

Concrete implementations of the `sosl.contract.Teacher` interface: a correct
membership + equivalence oracle for a language whose presentation *is* known,
exposed to the learner only through queries. A hypothesis is an `Invariant`
(the contract's type), so both equivalence strategies read it algebraically —
no operational prediction machinery exists on this side of the wall.

## Services

- **White-box teacher over an HOA automaton** (`HoaTeacher`). Wrap a
  deterministic, complete, transition-based Emerson-Lei automaton `D`:
  - `member(lasso)` — one simulation of `D` (no external tools, no
    timeouts); cost `O(|u| + |Q|·|v|)`.
  - `equiv(invariant)` — per `eq_mode`: `"exact"` (complete; the calculus
    align-and-scan against the language's reference invariant, zero
    membership queries) or `"bounded"` (lasso enumeration up to a bound;
    complete only in the limit). The certifying strategy is recorded on
    assent, so a run certified only by bounded enumeration can be flagged;
    counterexamples are minimal (shortest stem, then loop, then shortlex),
    which the learner's determinism depends on.
  - `cex_policy` — `minimal` (default) or `padded:<k>` (pump the minimal
    counterexample, kept only if still a genuine disagreement): the
    counterexample-sensitivity experiment's knob.

The reference invariant is supplied at construction or built once from `D`
(`sosl.sos.core.quotient`); after that the automaton leaves the equivalence
loop. Membership leans on spot only to compile `D`'s tables; `exact` leans on
`sosl.sos.calculus`. The learner sees none of this — only `member` and
`equiv`.

## Orientation map

    whitebox    HoaTeacher: member by simulation, equiv dispatch, cex policy
    equiv       the bounded:B strategy (hypothesis read via Invariant.member)
    exact_ref   exact: align-and-scan of hypothesis vs reference invariant

## See also

`algorithm.md` — how membership is simulated on a lasso, and how each
equivalence strategy searches for (and why it returns minimal)
counterexamples.
