# Atlas stall search

Experimental client of the restored, seeded-table global learner. This branch
starts immediately before removal of the Cayley hypothesis. The learner,
substitution chains and exact oracles are unchanged. Results describe this
historical algorithm, not the zero-column or local learners of the newer draft.

## Input and exact teacher

`adapter.py` reads current symbolic SOS through `synomega.sosio.load_sos`, then
uses the historical public `canonicalize` constructor to transfer the finite
algebra, letter map and acceptance into an `Invariant`. An explicit permutation
of effective symbols fixes the learning order. A finite-symbol subclass of the
historical alphabet supplies exactly those letters; it does not add AP
valuations or duplicate letters. All reported class counts exclude the fresh
identity. Queries use the historical lasso type against the transferred stamp.

The teacher first uses the historical guarded reference oracle. If its
functionality guard fires, the unchanged transformation-closure oracle receives
the reference stamp's right Cayley action as its target transition graph, with
empty mark sets. This is exact: a loop transformation determines the loop's
stamp value by applying it to the identity; the stem's reached class and this
value determine target membership. The oracle already evaluates concrete
lassos through the supplied membership function, rather than interpreting the
marks as an acceptance formula. Thus its existing finite abstraction is
sufficient here without an automaton construction. Closure-cap failures stay
undecided; no bounded assent is accepted.

`one.py` drives the original stabilization, hypothesis and counterexample
procedures without legality repairs. On exact assent it runs the original
left-divergence check. Clean fixpoints must export the reference algebra;
dirty fixpoints are certified acceptors without a congruence. JSON retains the
step table, columns, counterexamples, first divergence and reference-key
collisions. Those collisions concern the keys' folds, not an asserted quotient
of all reference classes. Membership counts include oracle calls and are not
the published query-cost measure.

## Execution

Run from this clone with the enclosing SynOmega `dev.sh`, so both public
SynOmega services and historical sources are available. `one.py` selects this
clone's historical `sosl` import path. Each invocation handles one input; use
an outer fifteen-second bound. `--reverse` reverses effective symbol order;
`--order 2,0,1` explicitly lists current symbol indices in learning order.
These options are mutually exclusive, and an explicit order must be a complete
permutation of the input alphabet. Transfer re-keys the reference under that
order before any learner query.

```sh
PYTHONDONTWRITEBYTECODE=1 timeout 15s ../../../dev.sh -m atlas_search.one \
  ../../../atlas/work/full-psl/languages/KEY/referent.sos
```

The known-witness boundary control compares the native historical teacher with
the stamp adapter and then forces closure-only equivalence. It checks the full
counterexample sequence, columns and final step table, not only class counts:

```sh
PYTHONDONTWRITEBYTECODE=1 timeout 15s ../../../dev.sh -m atlas_search.tests.control \
  atlas_search/results/nine-class-control.sos \
  atlas_search/results/nine-class-control.hoa \
  --output atlas_search/tests/logs/control-comparison.json
```

`campaign.py` selects current atlas entries through public collection,
classification and descriptor APIs. It saves its selection and stamp-coverage
assessment before running one bounded child per input/order. The initial scope
is prefix-independent languages (one saved leading state), ordered by reference
class count, symbols, key and letter order. Child output and errors go under
`tests/logs/`; timeout, capacity limit and crash remain distinct. A found stall
can stop the search; negative results state the exact population and orders
examined. Complement entries are not silently omitted. Scope coverage does not
turn a partial run into a complete negative search.

`--all-orders` lazily enumerates every symbol permutation in lexicographic
index order, independently for every selected language. It is mutually
exclusive with `--both-orders`. The selection records its order policy, and
each result records the actual index permutation. With `--keep-going`, all
selected permutations run even if a stall is found. This exhausts letter
orders, not alternative counterexample policies or refinement schedules.

Scientific controls: reproduce the archived nine-to-seven stall with the native
historical teacher, then obtain the same counterexamples and final step table
from this stamp teacher under the matching letter order. Check the opposite
letter order separately. No legacy coarse SOS is loaded as a valid algebra.

Source map: `adapter.py` (finite alphabet, reference transfer, exact teacher),
`one.py` (one run and its JSON result), `campaign.py` (saved-data selection and
bounded execution), `tests/` (controls and experiment receipts),
`report.md` and `results/` (scientific outcomes and preserved evidence).
