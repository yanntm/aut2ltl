# BuchiToLTL

Experimental prototype for backward LTL reconstruction from Transition-based Generalized Büchi Automata (TGBA).

## Current Status

This is research / exploration code. The reconstruction is **incomplete by design**.

We now have a working **size-2 non-accepting SCC absorption heuristic** ("fusion test" / "f2"). When it succeeds, previously unsupported formulas become reconstructible.

Key current capabilities:
- Explicit recursion with visiting set + depth limit (finite recursion)
- Early rejection of multi-state SCCs
- Size-2 non-accepting SCC absorption (when language-equivalent)
- Trivial acceptance normalization (treat all transitions as accepting when `Acceptance: t`)
- "Technique" reporting: `sl` (basic) or `sl+f2` (basic + fusion heuristic)
- Dual output: constructive formula + version after Spot simplification (`ltlfilt` equivalent)

## Project Organization

```
buchi2ltl.py                  # Thin CLI / backward-compat entry point
buchi2ltl/                    # Main package
    __init__.py               # Public API
    reconstruction.py         # Core reconstruct_ltl + labeling logic
    heuristics/
        size2_overapprox.py   # Size-2 over-approximation heuristic (the "fusion" technique)
    utils.py                  # simplify_ltl() etc.
evaluate.py                   # Evaluation harness (stable samples + random round-trip testing)
samples/                      # Curated LTL formulas and HOAs (for regression / stable testing)
testing/                      # Heavy debugging and experimental scripts
    visualize_fusion.py       # Automaton visualization helper (before/after)
    inspect_failures.py
    ...
README.md
```

## Quick Start

```bash
python3 buchi2ltl.py
```

Runs a small set of formulas and shows:
- Original vs recovered LTL
- **Technique** used (`sl` or `sl+f2`)
- Equivalence result
- Constructive formula + simplified version

## Evaluation Harness

`evaluate.py` is the main tool for batch testing the reconstruction.

It supports **stable test sets** (important for regression work) in addition to random generation:

```bash
# Run only the curated samples from samples/formulas.py (stable set)
python3 evaluate.py --samples --no-random -o stable.csv

# Curated samples + 200 random formulas afterwards
python3 evaluate.py --samples -n 200 --seed 42 -o mixed.csv

# Load your own formulas (Python file with lists, or plain text one-per-line)
python3 evaluate.py -f my_hard_cases.py --no-random -o custom.csv

# Classic random-only mode (still fully supported)
python3 evaluate.py -n 500 --seed 7 --aps 3 -o results.csv
```

Key features:
- Explicit formulas are always processed **first** (stable ordering).
- Output CSV includes a `source` column (`samples/formulas.py`, `random(seed=42)`, or `file:yourfile.txt`).
- `UNSUPPORTED` cases are recorded cleanly as `equivalent=unsupported` instead of noisy errors.
- Use `--only-failures` to collect interesting cases.

See `python3 evaluate.py --help` for all options.

The `samples/` directory contains hand-curated formulas (including cases that require the fusion heuristic) and example HOAs.

## Public API

```python
from buchi2ltl import reconstruct_ltl, try_size2_overapprox, simplify_ltl

recovered, state_labels, technique = reconstruct_ltl(aut)
```

## Notes

- Many formulas will still return `"UNSUPPORTED: ..."` (especially those with complex SCCs).
- The fusion heuristic (`f2`) is the main current way to handle certain formulas that would otherwise fail.
- Debug traces in the size-2 over-approximation heuristic are guarded behind `DEBUG_SIZE2_OVERAPPROX = False`.
- Generated images and CSVs are gitignored.
- `samples/` contains the main stable test set used by `evaluate.py --samples`.
- `testing/recovered_working_fusion_heuristic.py` holds the historical version of the fusion logic that successfully handled certain size-2 cases (kept for reference).

This repository is used for interactive development of the reconstruction technique.
