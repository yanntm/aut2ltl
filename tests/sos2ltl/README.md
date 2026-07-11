# tests/sos2ltl — E-series probes (the transcription engine experiments)

Probes for the sos2ltl experiments: spec
`research_notes/sos_toltl_experiments.md`, report
`research_notes/sos_toltl_report.md`, paper `research_notes/sos_toltl.md`.
Run every probe from the repo root:

    python3 -m tests.sos2ltl.<probe> [args]

## Module map

- `e<N>_*.py` — probe / ledger for experiment E`<N>` of the spec (`e0_*` the
  gate probes, `e4_ledger.py`, `e7_*` the dual-scan and mechanism tiers,
  `e9_*` profile scans, `e10_*` ledgers/reports).
- `census_build.py` — per-language census records over a `corpus/sos` folder
  (one json object per line): the per-layer condition-(A)/(B) read-offs each
  language's invariant yields, tagged by the `.sos` basename.
- `census_report.py` — the E1/E2 tables rendered from a `census_build` output.
- `bridge_stages.py`, `engine_diff.py`, `engine_fails.py`, `seam_gate.py`,
  `decline_split.py`, `profile_build.py`, `cat_sidecar.py` — engine
  cross-checks and corpus utilities; each carries its pydoc.
- `figs/` — figure generators; `logs/` — gitignored scratch.

## Data formats and logs/

`logs/` is gitignored scratch — regenerable, never cited by a report.

`census_build.py`'s line-json record format is **local to this probe layer
and `tests/cascade/`** (which consumes it for the K-series sweeps) and may be
retired in a repo-wide cleanup: do not build anything outside those two
folders against it. Paper-grade outputs are copied out of `logs/` into a
tracked `reference/` folder (CSVs plus a rendered summary md carrying date,
git hash, corpus and the exact regeneration commands) — reports cite only
those tracked files.
