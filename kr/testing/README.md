# kr/testing/

Internal development and verification scripts for the Krohn-Rhodes (kr/) pure algebraic path (Boker et al.).

## Purpose
- Exercise the paper construction: decompose_aut (to det parity complete minimized + SgpDec cascade) + reconstruct_ltl_1level_buchi (inductive reach formulas + fin_c + Muller assembly).
- Stability via bdd_utils precompute + per-case subprocess isolation (no segvs from Spot/buddy state).
- Isolated repeatable tests (no /tmp, no long -c pastes in dev).

## Running
From the project root:

    python3 kr/testing/test_kr_basic.py          # normal path I/O + counters + basic equiv + segv wrap; argv e.g. `... a Fa`
    python3 kr/testing/test_kr_reconstruct.py   # isolated decomp + pure paper reconstruct + Spot equiv on CASES
    python3 kr/testing/diag_stability.py

Subproc isolation detects rc 139 and prevents accumulation. Full CASES preserved; argv for single formulas. Direct invocation preferred.

## Key things tested
- decompose_aut + reconstruct_ltl_1level_buchi (paper path) on 0/1/multi-level.
- LTL output, levels, acc configs, REACH/FIN/MAXSZ counters.
- Spot are_equivalent (False on some multi until 5-formula polish).
- No segvs on repeats of Xa etc.; finite construction.
- Spot 0/1 normalization tolerance.

## Notes on discipline
Scripts + artifacts under kr/testing/.

See kr/README.md + kr/STATUS.md + kr/algorithm.md for the construction.
