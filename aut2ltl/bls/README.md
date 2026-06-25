# aut2ltl.bls — the cascade engine (source map)

The systematic engine: it translates a deterministic ω-automaton to LTL via a
Krohn-Rhodes / holonomy **cascade**, following Boker, Lehtinen & Sickert (FoSSaCS
2022) — algebraic, no pattern-matching on the automaton's shape. Reconstruction is a
family of **cascade translators** dispatched by acceptance class.

## Architecture: `CascadeTranslator`

```
CascadeTranslator =  CascadeHolder → LTLResult
```

- **`cascade_translator.py`** — the contract: a member is a self-gating singleton
  with a fixed `name` that inspects the cascade and either returns a
  language-faithful `LTLResult` or DECLINES (the cascade-level peer of the
  `aut2ltl.translator.Translator` floor).
- **`aut2cas.py`** — the adapter that lifts a member to a `Language → LTLResult`
  `Translator` (decompose the Language, then run the member).
- **`hierarchy_class.py`** — the builder that assembles the members into the dispatch
  chain `acc → weak → buchi → cobuchi → muller` (via `aut2ltl.first_success`), exposed
  to the CLI as the `str` technique.

```
spot automaton ──decompose (gap/)──▶ Cascade ──dispatch chain──▶ LTLResult (formula DAG)
```

## Members (one folder each, with its own algorithm.md)

- **`acc/`** — the bounded "X-ladder" fragment (direct unroll over a ⊤/⊥ oracle).
- **`weak/`** — Δ₁ (obligation): pure reachability, settle in an accepting SCC.
- **`buchi/`** — Π₂ (recurrence): `⋁ ¬Fin(C)`.
- **`cobuchi/`** — Σ₂ (persistence): `⋀ Fin(C)`.
- **`muller/`** — the general-case fallback: the full Muller-DNF (`assemble_muller_dnf`).

## Support / infrastructure

- **`operators/`** — the five inductive reachability formulas + `Fin(C)` (Lemma 7),
  the mutually-recursive core the members are built on.
- **`cascade/`** — the `Cascade` data model + config-graph analysis (reachable /
  accepting configs, good Muller sets) + the build `holder`.
- **`gap/`** — the GAP / SgpDec holonomy bridge (`decompose_aut`); see `gap/README.md`.
- **`extract.py`** — transformation-generator extraction for SgpDec.
- **`definability/`** — the LTL-definability gate: the verdict oracle (`tester/`), the
  non-LTL witness extractor (`witness/`), and the gate decorator (`gate.py`) that
  intercepts a non-LTL language as NOT_LTL (with a witness) before the cascade builds;
  see `definability/README.md`. **`options.py`** — engine options.

Engine-agnostic LTL machinery (builders, simplify, BDD utils, metrics, printers)
lives in `aut2ltl/ltl/`, shared across engines.

## More

- Construction reference: `paper/automata-to-ltl-construction.md` (in this package);
  ground truth for fidelity questions: `paper/Automata2LTL.txt`.
- Engine state: `STATUS.md`.
- Tests: `tests/probes/bls/` (cascade unit tests + probes).
