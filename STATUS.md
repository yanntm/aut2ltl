# aut2ltl — Project Status

Project-level snapshot. For the **engine** state read `aut2ltl/kr/STATUS.md`
(the FoSSaCS'22 cascade core); for construction history read `docs/HISTORY.md`.

## What works

The FoSSaCS'22 automaton→LTL construction is implemented end-to-end and
semantically validated. The portfolio front end (`reconstruct_decomposed`:
decompose/recombine + the sl heuristic gate over the acceptance-dispatch
cascade) sweeps the Manna–Pnueli class ladder — every probed case verifies
equiv=True. Details and the current size profile live in `aut2ltl/kr/STATUS.md`.

## How we drive it (main use case: the test scripts)

There is **no production entry point yet** — the package is exercised through
the placed scripts under `tests/` (mainly `tests/kr/`). That is the current
main use case; treat those scripts as the front door:

- `tests/kr/survey_mp_cascade.py` — MP-class × depth ladder, with Spot-equiv
  verdicts (the correctness gate). Run a single case: `… "G(p -> (q U r))"`.
- `tests/kr/survey_sizes.py` — size census (DAG/tree/temporal nodes) on the
  shipped `reconstruct_decomposed` path.
- `tests/kr/compare_sizes.py` — diff two `survey_sizes.py` logs for before/after.
- `tests/kr/test_kr_r4_audit.py` — structural audit gate (must stay CLEAN).

Persisted baselines live in `tests/kr/logs/`. See `aut2ltl/kr/README.md` for the
full tooling map.

## CLI

`aut2ltl/__main__.py` (`python3 -m aut2ltl`, console script `aut2ltl`) is the
portfolio front end: LTL/HOA in, equivalent LTL out, with `--use` technique
selection, `-O key=value` overrides, and `--dag` output. See `aut2ltl/kr/STATUS.md`
"Front end (CLI)" for the full surface. (The old sl-only `cli.py` stub is retired.)

## Layout

`aut2ltl/contract.py` (floor) ← `aut2ltl/kr` (pure cascade engine) +
`aut2ltl/sl` (heuristic engine) ← `aut2ltl/portfolio` (combinators) ←
`aut2ltl/__main__`. Tests under `tests/` (`tests/kr`, `tests/sl`, `tests/fixtures`).
