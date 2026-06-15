# aut2ltl.ltl — the shared LTL / Spot / BDD toolbox

A leaf library of generic operations on LTL as hash-consed `spot.formula` DAGs,
plus the buddy-BDD plumbing. It knows nothing of automata-to-LTL: it depends only
on LTL syntax, `spot`, and `buddy`. The Spot/buddy dependency is concentrated here
so the engines above can treat LTL as an opaque service.

What it offers, by concern:

## Construction — `builders.py`

Native `spot.formula` builders (`_And` / `_Or` / `_X` / `_U` / …) that build
SHARED DAGs with automatic sub-term sharing and hashable cache keys, plus
guard-string helpers (valuation → `p & !q`) and the simplify/normalize entries
(`_simp_f` / `simplify_ltl` / `normalize_ltl`).

## Simplification — `simplify/`

The "own simplify" rewrite passes — context, now-evaluation, factoring, folding —
that Spot's `tl_simplifier` does NOT perform. `builders._simp_f` applies them per
DAG node. Self-contained rule set with its own README.

## Size — `metrics.py`

Sharing-aware measurement of a formula DAG, because a SHARED DAG's real size is its
DISTINCT-node count while its unfolded `str()` can be orders of magnitude bigger (a
small DAG can unfold to a gigabyte):

- `dag_node_count` — distinct nodes (the honest size);
- `tree_node_count` — the unfolded-tree size, computed in O(DAG) by memoizing each
  shared node's subtree size, with an optional early-saturating `limit`;
- the acceptance-set count that bounds Spot's 32-set tableau.

## Rendering — `printers.py`

Size-gated stringification (the output peer of `metrics`): flatten a DAG to a
string only when its unfolded tree is below a gate, else print a placeholder naming
the size. Includes `to_dot` for the DAG itself (O(distinct nodes), never the
unfolded tree).

## BDD plumbing — `bdd_utils.py`

Reliable buddy-BDD construction from a Spot automaton: the AP→buddy-var map
(computed once) and point/cube BDDs for a concrete letter.

---

Members are imported directly (`from aut2ltl.ltl.builders import _simp_f`); the
`__init__` stays thin to avoid import-order surprises.
