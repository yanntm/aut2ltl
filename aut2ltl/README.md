# aut2ltl — source map

The root source package. This is the developer index; for the user-facing tool see
the [top-level README](../README.md).

## Architecture: `Language → LTLResult = Translator`

Everything here is built from one contract. A **Translator** is a callable

```
Translator :  Language  →  LTLResult
```

- **`language.py` — `Language`**: the input. It denotes one ω-language and hands out
  the automaton *representation* a translator asks for (`tgba`, `det_parity_sbacc`,
  `det_generic`, `det_generic_minimal`, …), derived lazily and cached. A translator
  pulls the shape it wants rather than being handed a fixed automaton.
- **`result.py` — `LTLResult`**: the output. A formula (when OK) or a decline, plus
  the contributing `technique` tags, a three-valued `Status` (OK / DECLINED /
  NOT_LTL), and a diagnosis. The load-bearing invariant: a result is
  **language-faithful or it declines — never a wrong formula**. See the module
  docstring for the type and the combine algebras.
- **`translator.py` — `Translator`**: the behavioral contract (a `Protocol`). The
  floor; it names no implementor. The kr-private cascade peer `CascadeTranslator`
  lives in [`bls/cascade_translator.py`](bls/cascade_translator.py). (`contract.py` is
  a deprecated shim re-exporting both until the portfolio is reworked.)

Because every translator is faithful-or-declines, translators **compose soundly**.

## Assembly

- **`combinators/`**: the general-purpose combinator bricks — `first_success` (⊕
  choice), `best_of` (⊞ size-choice), `compose` (∘, unit `identity`), `recurse` (fix
  self-reference), `memo` (sharing). A composite is itself a Translator, so it nests.
  See its [`README.md`](combinators/README.md) for the algebra.
- **`options.py`**: the runtime configuration compartment — an explicit key-value
  store threaded through construction (never a singleton). Pointer here; see the file
  for the spec.
- **`proc.py`**: process-group hygiene so heavy external children (GAP) never outlive
  us. Rarely touched.

## The translators (folder index)

Each engine/approach folder declares one or more Translator (or, in kr,
`CascadeTranslator`) implementations — each sound on the fragment it targets, by a
different algorithm. Many are **compositional**: a decorator/composite that takes a
child or leaf Translator and delegates to it.

- **[`bls/`](bls/README.md)** — the systematic construction: a family of
  `CascadeTranslator` members implementing the Boker–Lehtinen–Sickert / Krohn-Rhodes
  cascade (no pattern matching). The largest engine; see its README for the pipeline.
- **`daisy/`** — the pure self-loop *daisy* peel: a local, context-free combinator
  that labels one self-loop center and delegates its exits to a child.
- **`decomp/`** — (de)composition approaches, one isolated subpackage each, all of the
  shape *split → label parts → recombine*: `scc` (∨ over accepting SCCs), `strength`
  (∨ over weak/terminal/strong), `acceptance` (∧ over acceptance conjuncts), `inv`
  (factor a safety invariant out of the suffix).
- **`partscc/`** — a leaf translator for a single terminal SCC (the "stay here
  forever" sub-language), via a validated state partition.
- **`sl/`** — the heuristic self-loop engine: backward labeling with the f2 / tN SCC
  rescue heuristics (verify-before-use).
- **`ltl/`** — engine-agnostic LTL machinery: builders, BDD utilities, size metrics,
  printers, and the `simplify/` rules. Used by every engine.
- **`ltl/twa.py`** — the Spot-facing helpers: `clone` / `clone_structural` /
  `reroot`, and `dump_hoa`. Copy an automaton with Spot's own `make_twa_graph`,
  never by round-tripping it through HOA — a serialize/parse loses the properties
  the text does not carry and the parser re-infers others (`state_acc`,
  `complete`), so the copy is not the automaton that was copied. `reroot` is the
  `A↓state` rebase every peeling engine hands to a child. `dump_hoa` is the
  canonical serialization: acceptance forced onto the edges, APs registered in
  name order, states renumbered by `canon.normalize` — a function of the automaton
  rather than of the Spot build. Persisted HOA and any identity key over HOA bytes
  go through it; `aut.to_str("hoa")` is not a normal form.
- **`portfolio/`** — the assembled default: combinators that wire the translators into
  the best-effort pipeline behind the CLI. *(In flux — being reworked.)*
- **`__main__.py`** — the command-line front end (`python3 -m aut2ltl`).

> The "one folder, one or more sound Translators" discipline is the target shape; a
> few folders are still being aligned to it.
