# Historical relaxed learner on the current atlas

## Implementation and controls

The experimental branch preserves the pre-deletion seeded observation-table
learner and both original exact oracles. `adapter.py` transfers current symbolic
stamps through public constructors and supplies their faithful right actions to
the existing closure oracle. No learner core file was changed. The newer
zero-column bootstrap, evidence ledger and state-key local chains are not part
of this experiment.

The known nine-class witness reproduces its seven-class certified fixpoint.
The historical native teacher and stamp adapter give identical counterexamples,
columns and final step tables; the functionality guard fires six times. A
closure-only run agrees on the same complete transcript and final table. The
saved control result records these comparisons.

From this clone:

```sh
PYTHONDONTWRITEBYTECODE=1 timeout 15s ../../../dev.sh -m atlas_search.tests.control \
  atlas_search/results/nine-class-control.sos \
  atlas_search/results/nine-class-control.hoa \
  --output atlas_search/tests/logs/control-comparison.json
```

## Minimal three-class cyclic stall with multiple residual states

The complete through-four stamp population has 9,430 languages with multiple
residual states, requiring 146,056 letter permutations for a full scan. A
single-SCC filter selects 156 languages and 2,132 permutations. The ordered
pilot stops after thirteen runs: twelve canonical outcomes followed by the
three-class witness `sos1_s3_c3_t010011012_p4`, in order `c < a < b`. Its two
residual states form a single SCC; its canonical local algebra is the whole
three-class syntactic algebra. The pilot does not exhaust the four-class scope.

Over exclusive symbols `a,b,c`, the language is `Sigma* b c^omega`, equivalently
`F(b & XG c)`: some `b` is followed only by `c` forever. The residual graph
remembers whether the last non-`c` letter was `b`. Letter `a` resets it to the
rejecting residual, `b` to the accepting residual, and `c` acts as identity.
Both residuals are mutually reachable via these reset letters.

The algebra has three idempotents, named `a,b,c`, with
`x*a=a`, `x*b=b`, and `x*c=x`. Its only accepting pair is `(b,c)`.
The relaxed learner identifies `a` with `c`, keeping only the keys `c,b`.
From the initial residual these letters agree, but left prefix `b` separates
them: `b c^omega` is accepted, while `b a c^omega` is rejected. This is a
missing distinction inside the single cyclic block, not transient information.
The concrete alignment witness is retained in the one-input result.

All six letter orders are exactly certified. The two orders beginning with
`c`, namely `c<a<b` and `c<b<a`, stall at two classes; the remaining four
orders recover all three. Each stalled run uses one counterexample, with
order `c<a<b` returning `(b,c)`. Closure-only comparison produces the same
counterexamples, columns, final step table and cyclic witness. Original
saturation recovers all three classes.

The AP encoding `a=(p&q)`, `b=(p&!q)`, `c=!p` gives
`F(p & !q & XG !p)`. Public formula construction yields the same canonical ID;
exact comparison with the realized referent returns no counterexample.

### Complete exclusion below three classes

Saved atlas coverage through two positive classes is COMPLETE: nine languages
across all effective alphabets and residual graphs. Their sixteen distinct
language/permutation pairs all reach the canonical reference algebra, exactly,
with no timeout, crash or oracle limit. Six outcomes come from the completed
prefix-independent search; the ten remaining multi-state outcomes were run
separately. The combined receipts were checked against every permutation of
every language in the full nine-language selection, with no omissions or
duplicates.

The three-class witness is therefore minimal in positive syntactic-class count
for the historical seeded learner with its fixed shortest-counterexample
policy, allowing arbitrary residual graphs and every effective-letter order.
This is stronger than the earlier prefix-independent five-class minimum.
Other learner bootstraps, refinement schedules and counterexample policies
remain outside the claim.

The ten smaller cases, six three-class orders and two witness controls were
coordinated as eighteen independent invocations with at most fifteen concurrent
processes. Each invocation kept its own fifteen-second outer bound. The larger
146,056-run sweep was not launched because the minimality question was already
settled.

The cyclic audit was checked against two boundaries: it marks the five-class
one-state witness cyclic, but marks the four-class `a -> Xa` global stall as
having no missed cyclic-block distinction. Those controls and their inputs
are saved with the results.

Reproduce the discovery:

```sh
PYTHONDONTWRITEBYTECODE=1 ../../../dev.sh -m atlas_search.campaign \
  --collection ../full-psl --max-classes 4 --residuals multiple \
  --strongly-connected --all-orders --stop-on cyclic-stall \
  --output atlas_search/tests/logs/multiple-strong-through-four
```

Reproduce the lower multi-state scope (a serial equivalent of the ten parallel
one-input invocations), or independently repeat all sixteen smaller runs:

```sh
PYTHONDONTWRITEBYTECODE=1 ../../../dev.sh -m atlas_search.campaign \
  --collection ../full-psl --max-classes 2 --residuals multiple \
  --all-orders --keep-going --output atlas_search/tests/logs/multiple-through-two-parallel
PYTHONDONTWRITEBYTECODE=1 ../../../dev.sh -m atlas_search.campaign \
  --collection ../full-psl --max-classes 2 --residuals any \
  --all-orders --keep-going --output atlas_search/tests/logs/all-through-two
PYTHONDONTWRITEBYTECODE=1 timeout 15s ../../../dev.sh -m atlas_search.one \
  atlas_search/results/three-class.sos --order 2,0,1 --closure-only \
  --output atlas_search/tests/logs/three-class-closure.json
PYTHONDONTWRITEBYTECODE=1 timeout 15s ../../../dev.sh -m atlas_search.one \
  atlas_search/results/three-class.sos --order 2,0,1 --saturated \
  --output atlas_search/tests/logs/three-class-saturated.json
```

For the six-order control, use separate `one.py` invocations with the six
`--order` values listed for the five-class witness below. Formula verification
uses that same recorded formula command with input `three-class.sos` and
formula `F(a & !b & XG !a)` (AP names `a,b` stand for `p,q`).
After saving those six order results under `tests/logs/three-class-orders/`,
`python3 -m atlas_search.tests.summarize_minimum` checks coverage and regenerates
the two aggregate result files without running the learner again.

## Search through four positive classes

The current `atlas/work/full-psl` collection certifies complete stamp coverage
through four classes: 9,462 languages modulo effective-symbol permutation.
Saved recurrent FDFA descriptors select 32 languages with one residual state;
no descriptors are missing in this scope. All effective alphabet sizes are
included. Exhausting every letter permutation gives 382 runs, all reaching
the canonical reference algebra, with no timeout, crash or oracle limit.
Execution takes 44.297 seconds. The result receipts were independently checked
against the full set of language/permutation pairs: all 382 are present exactly
once.

| Positive classes | Exact canonical runs |
|---|---:|
| 1 | 2 |
| 2 | 4 |
| 3 | 28 |
| 4 | 348 |

Thus the five-class witness below is minimal in positive reference-class count
among prefix-independent languages for this historical seeded learner with
its fixed shortest-counterexample policy, allowing every effective-letter
order. This does not exclude smaller cyclic stalls with several residual
states, or stalls under other counterexample policies or other learners. The
earlier 62-run forward/reverse subset is also retained as scientific evidence.

```sh
PYTHONDONTWRITEBYTECODE=1 ../../../dev.sh -m atlas_search.campaign \
  --collection ../full-psl --max-classes 4 --all-orders --keep-going \
  --output atlas_search/tests/logs/atlas-through-four-permutations
```

## Five-class cyclic stall

The observed five-to-eight-class population contains 102 one-state languages,
giving 204 selected input/order pairs. Stamp coverage there is PARTIAL. Search
stops after nine runs: eight canonical outcomes, then one exact stall. No
timeout, crash or oracle limit occurs before stopping.

Witness: `sos1_s3_c5_t030314042333344_p2a4`. Its effective symbols are `a,b,c`;
the canonical residual graph has one state. With order `a < b < c`, the
five-class reference yields a four-class relaxed fixpoint after the single
counterexample `(epsilon,abc)`, then exact assent. Both equivalence queries fire
the functionality guard and are decided by transformation closure. A run forced
through closure on every query produces the same transcript and table.
Enabling the original saturation repair recovers the exact five-class algebra.
Reversing the alphabet order also recovers all five classes, using two
counterexamples. All six orders have now been run, with exact certification:

| Letter order | Outcome | Learned positive classes |
|---|---|---:|
| a < b < c | stall | 4 |
| a < c < b | stall | 4 |
| b < a < c | canonical | 5 |
| b < c < a | canonical | 5 |
| c < a < b | stall | 4 |
| c < b < a | canonical | 5 |

The witness stalls exactly when `a` precedes `b`; the position of `c` does not
change the outcome. All three stalls identify the reference keys `bc` and `c`
(possibly named `cb` under the chosen order). Each stall uses one
counterexample and each canonical run two. These statements concern the fixed
historical shortest-counterexample policy. Full results are preserved in
`results/five-class-orders.json`.

Each row is a separate invocation with a fifteen-second bound. Use the respective
`--order` argument `0,1,2`, `0,2,1`, `1,0,2`, `1,2,0`, `2,0,1` or `2,1,0`:

```sh
PYTHONDONTWRITEBYTECODE=1 timeout 15s ../../../dev.sh -m atlas_search.one \
  atlas_search/results/five-class.sos --order 0,2,1 \
  --output atlas_search/tests/logs/five-class-orders/0-2-1.json
```

The target is the commutative idempotent algebra with keys `a,b,c,ab,bc`;
`ab` is zero, `ac=a`, and `bc` is distinct from `c`. The relaxed fold identifies
the reference keys `bc` and `c`. Left multiplication by `a` exposes the missing
distinction: `abc` has class `ab` whereas `ac` has class `a`. In particular
`(abc)^omega` is accepted and `(ac)^omega` rejected. The forced coarse product
is nonassociative: `(a*b)*c=ab` but `a*(b*c)=a`.

Over the three exclusive symbols, the language is

`GF b & (GF a | FG !c)`.

That is, `b` occurs infinitely often and either `a` occurs infinitely often or
`c` occurs only finitely often. For the shared minimal AP encoding
`a=(p&q)`, `b=(p&!q)`, `c=!p`, it becomes
`GF(p & !q) & (GF(p & q) | FG p)`.
Construction from that AP formula gives the same canonical SOS ID; exact
comparison against the realized atlas referent returns no counterexample.
The original atlas already retains two other LTL expressions for this language.
No atlas entry was changed.

The exact formula check is preserved in `results/five-class-formula.json`:

```sh
PYTHONDONTWRITEBYTECODE=1 timeout 15s ../../../dev.sh -c 'import json; from pathlib import Path; from synomega.calculus.comparison import counterexample
from synomega.sosio import load_sos,dump_sos_id; from synomega.alphabetconv import canonicalize_alphabet,symbols_to_ap
from synomega.workflows import from_formula
formula="GF(a & !b) & (GF(a & b) | FG a)"; obj=from_formula(formula); ref=load_sos(Path("atlas_search/results/five-class.sos").read_text()); witness=counterexample(obj,symbols_to_ap(ref)); assert witness is None
print(json.dumps(dict(formula=formula,canonical_id=dump_sos_id(canonicalize_alphabet(obj)),exact_counterexample=witness),indent=2))' > atlas_search/tests/logs/five-class-formula.json
```

```sh
PYTHONDONTWRITEBYTECODE=1 ../../../dev.sh -m atlas_search.campaign \
  --collection ../full-psl --min-classes 5 --max-classes 8 --both-orders \
  --output atlas_search/tests/logs/atlas-five-through-eight
PYTHONDONTWRITEBYTECODE=1 timeout 15s ../../../dev.sh -m atlas_search.one \
  atlas_search/results/five-class.sos --closure-only \
  --output atlas_search/tests/logs/five-class-closure.json
PYTHONDONTWRITEBYTECODE=1 timeout 15s ../../../dev.sh -m atlas_search.one \
  atlas_search/results/five-class.sos --saturated \
  --output atlas_search/tests/logs/five-class-saturated.json
PYTHONDONTWRITEBYTECODE=1 timeout 15s ../../../dev.sh -m atlas_search.one \
  atlas_search/results/five-class.sos --reverse \
  --output atlas_search/tests/logs/five-class-reverse.json
```

All individual learning and formula checks have a fifteen-second outer bound;
campaign children are bounded separately through `synomega.runner`. Population
selection and coverage use saved data only. The five-class witness uses three
symbols versus the earlier witness's two; a minimum restricted to two symbols
has not been established.
