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
evaluate.py                   # Random LTL round-trip tester (batch experiments)
samples/                      # Interesting formulas and HOAs (for testing / regression)
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
- Useful test data lives in `samples/`.

This repository is used for interactive development of the reconstruction technique.
