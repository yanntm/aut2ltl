# sosl.validate — invariant checkers

Decide whether a learned invariant is correct, at two strengths: exact
canonical equality (the soundness criterion) and a weaker acceptance check
(used where exactness is not expected, e.g. the saturation ablation).

## Services

- **`sos_validate learned reference`** — parse both invariants, re-canonicalize
  defensively (re-sort accepting pairs, normalize whitespace), and compare
  byte-for-byte. Byte-equality is the tool's soundness verdict: `SOUND` /
  `FAIL`.
- **`sos_validate --acceptor learned <hoa> --bound B`** — check a membership
  read-off against direct automaton simulation on all lassos up to bound `B`.
  This certifies *acceptance-correctness* separately from canonicity: a
  `--no-saturation` run can be acceptance-correct yet not byte-equal
  (`ACCEPTOR_ONLY`), and this check is how that outcome is recognized rather
  than hidden.

  **Scope rule (normative).** `--acceptor` accepts either a `.sos` invariant or
  a `CAYLEY` hypothesis. For any fixpoint reached **without** saturation it must
  be pointed at the **Cayley hypothesis**: the `.sos` read-off multiplies
  classes and so presumes a two-sided congruence (`objects/algorithm.md` /
  `learn/algorithm.md` export caveat), which a pre-saturation partition does not
  yet satisfy — the exported `.sos` can legitimately fail the acceptor check
  there while the hypothesis passes it. That divergence is an expected outcome
  (spec §9, row F2), not a bug.

Thin wrapper: the invariant read-off is `sosl.sos`, the reference and the
simulator are `sosl.sos.build` / `sosl.teacher`. No `algorithm.md` — the
subtlety is in what is being checked (see `objects/algorithm.md` for the
read-off and canonical form), not in the checking.

## See also

Spec of record: `research_notes/sos_learner_spec.md` §3.3 and the harness in §5.
