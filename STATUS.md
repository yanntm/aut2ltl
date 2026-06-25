# aut2ltl — Project Status

Project-level snapshot. For the **engine** state read `aut2ltl/bls/STATUS.md`
(the FoSSaCS'22 cascade core); for construction history read `docs/HISTORY.md`.

## What works

The FoSSaCS'22 automaton→LTL construction is implemented end-to-end and is sound
on the survey gate (0 verified non-equivalent across the curated corpus, the
373-case benchmark, and the Kinská set).

The portfolio default (`RECIPES["default"]`) is the **`deep_nobls`** recipe: it
seeds a formula with the **`cakedsdet`** assembly (below), then runs a DEEP,
bottom-up round trip — `deep_roundtrip` re-presents every node of the seed's DAG
through the cascade-refusing **`nobls`** labeler, kept per node only when not larger
(`best_of([identity, relabel(nobls)])`), then a final `hi` simplify. A re-derivable
node comes back compact (often collapsing a whole buchi tower from the leaves up);
one `nobls` cannot re-derive is declined and the seed's node is kept. This round
trip leans on the language retranslate budget, **raised to 1000** flat nodes
(`language.translate_tree_limit`, env `KR_TRANSLATE_TREE_LIMIT`): blobs up to that
size are re-presented rather than refused, which is where the bulk of the size
collapse comes from (see `results/reference/`).

The `cakedsdet` seed is the `cakeds` assembly with the deterministic anchored
read-off **`daisystardet`** (peer package `aut2ltl/daisystardet/`, see its
`algorithm.md`) ahead of the flat `daisystar` in the peel trio. The peel layer is
`daisy` (self-loop) → `daisy2`
(length-1 recurrence star) → `daisystardet`/`daisystar` (rejecting star), each
delegating exits to a child and flooring on the `bls` cascade or the `partscc`
leaf. `daisystardet` peels a *rejecting* SCC with a **deterministic L-partition**
and emits an **exact, flat, fixpoint-free** label — `partscc`'s transition law run
`U`-to-an-exit (the reachability dual of `partscc`, not restricted to length-1
stars); the flat `daisystar` is the fallback for a *non-deterministic* rejecting
star. Alternate assemblies are reachable by name under `--use` (the `RECIPES`
registry); the kr cascade core stays pure. Engine internals and the size profile
live in `aut2ltl/bls/STATUS.md`.

## Combinator algebra (2026-06-19)

The portfolio combinators are named into a small (almost-)algebra over
language-manipulators (Translators carrying *faithful-or-⊥*; **soundness is closed
under every operation**, so any writable recipe is sound by construction). See
[`aut2ltl/combinators/`](aut2ltl/combinators/README.md) for the algebra and law table.
Two sorts: translators and `Decorator`s (`aut2ltl/translator.py`). Operations:
`first_success` (`⊕`) / `best_of` (`⊞`) / `compose` (`∘`, unit `identity`) / `recurse`
(`fix`) — all under `aut2ltl/combinators/` — plus the `∧/∨` combine
(`aut2ltl/decomp/decompose.py`). The five recipes are
flat point-free `compose(...)` terms, and the three `decomp` decomposers
(strength/acceptance/scc) collapsed onto the one `decompose(split, connective, tag)` —
all behavior-preserving (survey unchanged at DAG=414). Scope fence: free named
combinators only — no DSL, no AST, no meta-level reflection. Open levers (TODO): the
`best_of` wiring recipe and `recurse` memoization.

## Front end (CLI)

`aut2ltl/__main__.py` (`python3 -m aut2ltl`, console script `aut2ltl`) is the
portfolio front end: an LTL formula or HOA file in, an equivalent LTL formula
out. `--use` cites the techniques that may participate (the producers `acc weak
buchi cobuchi muller bls`, where `muller` is the general Muller-DNF leaf and `bls`
the integrated cascade) or names a recipe (see the `RECIPES` registry);
omit it for the default portfolio.
`-O key=value` overrides any
declared option (`--list-options`/`--list-techniques` to discover). The verbose
report (technique, DAG/temporals/tree sizes, build time) goes to stderr (`-q`
silences); `--dag` dumps the formula DAG as graphviz dot; DECLINE ⇒ exit 1.

## Testing

The front-end survey is the correctness gate — it reconstructs a corpus through
the CLI and verifies each result with a Spot oracle (a test-only check, never a
client cost):

- `survey/` — the survey harness (`python3 -m survey --folder <dir>`): runs a
  corpus through the CLI, emits a per-formula CSV + a compact summary ending in
  `SUCCESS`/`FAIL`. `FAIL` = a verified non-equivalent formula (a definite wrong
  answer); spot timeouts / size explosions / >32-acc-set walls are their own
  categories, NOT failures (a DAG we built that Spot cannot verify is not our
  fault). Corpora live in `samples/` (`validation` is the gate corpus). Sub-tools:
  `survey.diff.ltl_diff` (containment + witness), `survey.diff.results` (CSV diff),
  `survey.ltl2hoa` (generate HOA from an LTL folder).
- Committed release baselines: `results/reference/{validation,benchmark,kinska}/`
  (per-corpus `*.csv` + `SUMMARY.txt`). The benchmark corpus (`samples/benchmark`)
  is the survey set + scalable W/U/R chains + the Kinská automata.

## Layout

`aut2ltl/contract.py` (floor) + `aut2ltl/language.py` ← `aut2ltl/bls` (pure
cascade engine) + the (de)composition translators (`aut2ltl/daisy`,
`aut2ltl/partscc`, `aut2ltl/decomp`) ← `aut2ltl/portfolio` (combinators) ←
`aut2ltl/__main__`. Engine-agnostic helpers in `aut2ltl/ltl`. Tests under `tests/`
(`survey*`, `tests/bls`, `tests/heur`, `tests/fixtures`, `tests/benchmark`).
`aut2ltl/ltl/simplify` carries its own `algorithm.md` spec.
