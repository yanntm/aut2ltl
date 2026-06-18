# aut2ltl.simplify_ltl — the `Simplify` Translator decorator

`Simplify(child, level)` wraps any `Translator`: it forwards the `Language` to
`child` and, when `child` returns an **OK** result, replaces the formula with a
language-preserving simplification. A **NOK** result (declined / NOT_LTL) passes
through untouched, and the child's technique tags are kept as-is — simplification is
representation, not a reconstruction method.

Two levels:

- **`lo`** — our DAG-size-aware rules only (`ltl.builders.own_simplify`). Cheap; the
  same own-rules pass the portfolio combinators already use to fold recombined nodes.
- **`hi`** — our rules *followed by* Spot's `tl_simplifier` (`ltl.builders._simp_f`),
  to a fixpoint. Smaller output, more cost.

It lives here, not in `ltl/`, only to respect the dependency graph: a Translator
decorator must import the contract floor (`translator` / `result` / `language`),
which `ltl/` — an engine-agnostic leaf — may not. The simplification rules themselves
and their rationale live in **`aut2ltl/ltl/simplify/`** (see its README); this
package is just the thin Translator seam over them.
