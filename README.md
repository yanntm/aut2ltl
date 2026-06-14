# aut2ltl

Translation of ω-automata to Linear Temporal Logic. The project pairs two
engines, composed by a portfolio that picks the winning method at each node:

* **`aut2ltl.kr`** — the *systematic* algebraic construction: Krohn-Rhodes
  holonomy cascade decomposition (SgpDec + GAP) following Boker, Lehtinen &
  Sickert, *"On the Translation of Automata to Linear Temporal Logic"*
  (FoSSaCS 2022) — no pattern matching on automaton shape. To our knowledge the
  first practical implementation of that construction.
* **`aut2ltl.sl`** — the *heuristic* engine: self-loop backward labeling, exact
  on the very-weak fragment and declining elsewhere, plus the f2 / tN SCC
  rescue heuristics (verify-before-use).

Both are language-faithful-or-decline, so the portfolio can compose them
soundly. On the Manna-Pnueli class ladder the combined path is a clean sweep
(every case verified equivalent). See `aut2ltl/kr/STATUS.md`.

## Layout

```
aut2ltl/                  the root package (layering: floor -> engines -> portfolio -> cli)
  contract.py            ReconResult + Translator (the contract floor)
  cli.py                 command-line front-end:  python3 -m aut2ltl.cli
  kr/                    pure cascade FoSSaCS engine (cascade, reachability,
                         fin, acceptance_dispatch, gap_bridge, simplify/, ...)
  sl/                    heuristic engine (backward labeling + f2/tN heuristics)
  portfolio/             combinators: decompose_recombine, heuristic_gate, sl_driven
tests/
  kr/                    cascade-engine harnesses (gates: test_kr_r4_audit, survey_mp_cascade)
  sl/                    heuristic-engine debug/search scripts
  fixtures/             curated formula + HOA fixtures
  eval_roundtrip.py      batch round-trip evaluation harness
paper/                   construction reference + ground-truth paper text
```

## Quick start

```bash
# sl-engine CLI demo (original vs recovered LTL, technique, equivalence)
python3 -m aut2ltl.cli
```

```python
# Recommended top-level entry: automaton in, LTL formula DAG + technique out.
import spot
from aut2ltl.portfolio import reconstruct_decomposed

aut = spot.formula("GFa & GFb").translate()
res = reconstruct_decomposed(aut)          # ReconResult
print(res.formula, res.technique_str())    # formula DAG, e.g. "and2+sl"

# The pure cascade engine, per-automaton:
from aut2ltl.kr import decompose_aut, reconstruct_bls
casc = decompose_aut(spot.formula("Fa").translate())
print(reconstruct_bls(casc))
```

The reconstruction result is a `ReconResult` (`aut2ltl.contract`): `.formula`
(a hash-consed `spot.formula` DAG) or `.status == DECLINED`, plus `.technique`
(the set of methods that contributed).

## Dependencies

Runtime deps are NOT pip-installable; install them at system level:

* **Spot** (the `spot` and `buddy` Python bindings) — both engines.
* **GAP 4.12+** with the **SgpDec** package — the `kr` cascade engine only.
  Run `aut2ltl/kr/install.sh` once (user-local under `~/.gap/pkg`).

`pyproject.toml` carries the package metadata (`pip install -e .` installs the
`aut2ltl` package itself, not the external tools above).

## Evaluation harness

`tests/eval_roundtrip.py` batch-tests reconstruction over curated and random
formulas:

```bash
python3 tests/eval_roundtrip.py --samples --no-random -o stable.csv
python3 tests/eval_roundtrip.py -n 200 --seed 42 --aps 3 -o results.csv
```

Curated fixtures live in `tests/fixtures/` (`formulas.py`, `f2_successes.py`,
`terminal_2scc_labeled.py`, sample HOAs). See `--help` for all options.

## More

* `aut2ltl/kr/README.md` — kr engine doc map, pipeline, module map, testing tools.
* `aut2ltl/kr/STATUS.md` / `aut2ltl/kr/TODO.md` — current state / work items
  (incl. the P-ARCH reorganization campaign).
* `paper/automata-to-ltl-construction.md` — the construction reference;
  `paper/Automata2LTL.txt` — ground-truth paper text.
