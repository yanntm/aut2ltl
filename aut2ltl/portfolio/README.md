# aut2ltl.portfolio — the combinators that assemble the translators

This package wires the two engines (`kr` cascade, `sl` heuristic) into the shipped
default translator and the `--use` technique vocabulary. Every member here is a
`Translator` (`Language -> LTLResult`, see `aut2ltl.contract`) or a builder
of one; the engines stay pure and are composed, not modified. The object graph IS
the config graph — one shared `Options` is threaded through the whole assembly.

The default path: `Decompose / SlDriven / Decompose / first_success` — split the
language by acceptance strength, try the cheap `sl` gate, then fall to the kr
cascade. The `sl` gate is a SOUND pre-filter (exact-on-fragment or decline), so a
wrong formula is never adopted; it is the single seam through which the kr core
touches `sl` (via `aut2ltl/portfolio/heuristic_gate.py`).

## Modules

- **`build.py`** — `build_portfolio` (assembles the default graph from an
  `Options`) and the `TECHNIQUES` vocabulary for `--use`: the kr leaves
  (`acc / weak / buchi / cobuchi / bls`), the integrated cascade `str`, the `sl`
  gate, and the two wrappers (`sl_driven` / `decompose`). Groups the cited kr
  leaves into ONE cascade-level `first_success` (one GAP decomposition).
- **`decompose.py`** — `Decompose`, the decompose-and-recombine Composite: splits a
  language on top-level acceptance conjuncts/disjuncts (recursing on itself), else
  delegates the whole to its leaf; transparent on the technique tag. Plus
  `split_report` (diagnose how the root would split, no reconstruction).
- **`sl.py`** — `Sl`, the `sl` engine as a Translator: the sound gate, exact on the
  very-weak (1-weak) fragment and declining off it. Config is the `portfolio.sl.*`
  Options (enabled / max_states / verify).
- **`sl_driven.py`** — `SlDriven`, "kr under sl": sl peels what it can and delegates
  each remaining sub-automaton's full suffix to a cascade-based `delegate`
  Translator (which must NOT itself contain `SlDriven`, the no-ping-pong rule).
- **`options.py`** — the `portfolio.sl.*` `OptionSpec`s (enabled / max_states /
  verify), seeded from the legacy `KR_GATE_*` env vars; `PORTFOLIO_OPTIONS`.
- **`__init__.py`** — builds the env-seeded default `Options`, exposes the shipped
  `reconstruct_decomposed`, the standalone `sl` / `cascade` Translators, and
  `build_portfolio` / `TECHNIQUES` for callers wanting a variant.

## Layering

Above both engines; imports the engines (`kr`, `sl`) and the `aut2ltl.contract`
floor, never the reverse. A caller builds a variant by rebuilding with
`build_portfolio` + a cited technique set or a cloned `Options` (the A/B move).
