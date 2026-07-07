# sosl — the SoS learner

Active learning of the *syntactic ω-semigroup invariant* `I(L)` of an unknown
ω-regular language from lasso membership and equivalence queries, plus the
soundness harness and experiment suite that prove and measure it. Specification:
`../research_notes/sos_learner_spec.md`; report: `../research_notes/sosl_report.md`.

This directory is a **self-contained subtree** — its own package, tests, samples
and `pyproject.toml` — and depends on nothing in the enclosing `aut2ltl` repo. It
is intended to graduate to its own repository.

## Layout

```
sosl/            <- this project root (make it your working directory)
  sosl/          <- the importable package  (import sosl, sosl.sos, ...)
  tests/         <- probes and gates
    sos/         <- sos-core tests
    sosl/        <- learner tests
  samples/       <- HOA fixtures the tests read
  pyproject.toml
```

## Running

Work with this folder as the current directory; then it mirrors the enclosing
repo's "`python3 -m` from the root" convention, rooted here:

```
cd sosl
python3 -m tests.sosl.saturation_gate      # an end-to-end gate
python3 -m tests.sos.core_fingerprints     # a sos-core check
```

From this directory `import sosl` resolves to the package with no setup. An
editable install (`pip install -e .`) is **optional** — only needed to import
`sosl` from a different working directory; ordinary development does not require
it. (The one in-repo consumer outside this subtree, `aut2ltl/sos2ltl`, puts this
directory on `sys.path` itself, so it needs no install either.)
