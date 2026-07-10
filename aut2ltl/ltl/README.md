# aut2ltl.ltl — the shared LTL / Spot / BDD toolbox

A leaf library of generic operations on LTL as hash-consed `spot.formula` DAGs,
plus the buddy-BDD plumbing and the Spot-automaton helpers. It knows nothing of
automata-to-LTL: it depends only
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

## Automata — `twa.py`, `canon.py`

`twa.py` — copying and serializing a `twa_graph`. `clone` is Spot's own
`make_twa_graph(aut, prop_set)`; **never copy an automaton by round-tripping it
through HOA**, because the parser re-infers the properties the text does not
carry (`state_acc`, `complete`), so what comes back is not what was copied.
`clone_structural` drops the two properties an acceptance rewrite invalidates.
`reroot` is the `A↓state` copy-and-trim.

`dump_hoa` is the canonical serialization, and `aut.to_str("hoa")` is not one: it
re-declares state-based acceptance whenever it can — even after `prop_state_acc`
was cleared — lists the atomic propositions in the bdd dictionary's variable
order, so two Spot builds emit different bytes for one automaton, and prints
whatever state numbering it was handed. `dump_hoa` forces the acceptance onto the
edges, registers the APs in name order on a fresh dictionary, then renumbers the
states with `canon.normalize`. The AP pass runs first, because `canon.normalize`
orders successors by the *printed* edge condition. Persisted HOA, and any identity
key taken over HOA bytes, goes through it.

`canon.py` — `normalize`, the canonical state numbering: `0` is initial, then BFS
visiting successors in `(cond, acceptance)` order. Exact on a deterministic
automaton, where the condition picks the successor and no tie can arise;
heuristic otherwise, ties falling back to the old index.

Neither determinizes. Serialization normalizes a *presentation*; obtaining the
presentation worth serializing is the caller's business.

---

Members are imported directly (`from aut2ltl.ltl.builders import _simp_f`); the
`__init__` stays thin to avoid import-order surprises.
