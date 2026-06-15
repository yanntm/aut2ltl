# aut2ltl.sl — the heuristic backward-labeling engine

The separate heuristic engine (ex-`buchi2ltl/`). It reconstructs LTL by
**self-loop backward labeling** over a TGBA, DAG-native: every label is built as a
hash-consed `spot.formula`, an adopted core is spliced as a child WITHOUT
flattening. It is EXACT on the very-weak (1-weak) fragment — automata whose only
cycles are self-loops — and DECLINES off it: a state re-entered on the recursion
stack, or a successor inside a genuine multi-state SCC with no validated fragment,
poisons the result with the `UNSUPPORTED` sentinel that surfaces as
`LTLFormulaResult.declined`. Soundness is BY CONSTRUCTION (exact-on-fragment +
decline-otherwise), never post-hoc checking.

It is wired into the portfolio only through `Sl` / `SlDriven` in
`aut2ltl/portfolio/`; the kr core imports nothing from here but the contract.

## Modules

- **`reconstruction.py`** — the engine: `reconstruct_ltl` and its recursive `label`.
  Runs the backward labeling, injects validated SCC fragments, and returns a
  `LTLFormulaResult` (DAG on success, declined otherwise).
- **`reconstruction_helpers.py`** — the automaton-side helpers `reconstruction`
  leans on: per-state invariant computation, downstream-invariant application,
  tN-fragment injection + bad-state marking, the reachable-from-q sub-automaton
  (the unit of full-suffix delegation), and the technique-tag builder.
- **`invariants.py`** — generic invariant-literal computation across a set of BDD
  formulas: an atom constantly true/false on all edges reachable from a state.
- **`utils.py`** — small generic helpers (`simplify_ltl` over a formula string).
- **`heuristics/`** — the verify-before-use SCC rescuers (f2 / t2). See its README.

## Layering

Imports `spot` / `buddy` and the `aut2ltl.contract` floor; its rescue heuristics
live one level down in `heuristics/`. Nothing in the kr core depends on this
package — composition happens above, in `portfolio/`.
