# Round-trip experiments — collapsing the buchi towers (2026-06-25)

Dated log of the experiments that adopted **`deep_nobls`** as the shipped default and
raised the language retranslate budget **100 → 1000**. Reproducibility commands +
results over all four reference corpora + conclusions. (Research note — not cited from
the durable docs; the mechanism itself is documented in
`aut2ltl/roundtrip_deep/algorithm.md`, the recipe in `aut2ltl/portfolio/recipes/`.)

## What we were chasing

The bls cascade leaves (`buchi` especially) are *sound but explosive*: on some U/R
sub-languages they emit correct "blob" formulas hundreds-to-thousands× the input — the
**buchi towers** — which then blow past Spot's verification gate (the `SIZE` non-checks).
The fix is a **semantic re-presentation pass**: walk the seed's DAG **bottom-up** and at
each node re-derive its sub-language through the automaton using only the *cascade-free*
methods (`nobls`), keeping whichever is smaller. Bottom-up matters: a blown root is over
the translate bound and can't be re-presented top-down, but a child re-presented smaller
shrinks its parent until the parent drops under the bound — the collapse climbs from the
leaves. The retranslate budget (`language.translate_tree_limit`) is exactly the gate on
"is this node small enough to re-present", so it is the lever the whole effect rides on.

`deep_nobls` = `cakedsdet` seed → `deep_roundtrip(best_of([identity, relabel(nobls)]))`
→ `hi` simplify. Faithful-or-⊥ at every node (congruence + never-regress floor), so
**sound by construction** — confirmed 0 FAIL on every corpus below.

## Reproducibility

Code state: `RECIPES["default"] = deep_nobls` (commit `a243126`), retranslate budget
default `1000` (commit `ef35e34`). All runs from the repo root.

```bash
# Default path (no flags) == deep_nobls @ budget 1000:
python3 -m survey --folder samples/validation --logs logs/run/validation
python3 -m survey --folder samples/kinska     --logs logs/run/kinska
python3 -m survey --folder samples/benchmark  --logs logs/run/benchmark
python3 -m survey --folder genaut/corpus/2state1ap1acc --logs logs/run/genaut

# Budget sweep (the knob is an env-read process-wide gate; --use pins the recipe):
KR_TRANSLATE_TREE_LIMIT=100  python3 -m survey --folder <corpus> --use deep_nobls --logs <dir>
KR_TRANSLATE_TREE_LIMIT=500  python3 -m survey --folder <corpus> --use deep_nobls --logs <dir>
KR_TRANSLATE_TREE_LIMIT=1000 python3 -m survey --folder <corpus> --use deep_nobls --logs <dir>

# Compare a run vs a committed reference (keyed on source; exits 1 on TRUE->FAIL):
python3 -m survey.diff.results results/reference/<corpus>/<ref>.csv <new>/survey_*.csv

# genaut frontier digest (+ a PDF next to the CSV):
python3 genaut/analyze_frontier.py <csv>
```

## Result 1 — adoption: deep_nobls @1000 vs the prior default (cakedsdet @100)

`DAG` is total reconstructed size over the common set; `val` = verified-TRUE count.
0 FAIL / 0 CLASH everywhere.

| corpus (inputs) | cakedsdet @100  DAG (val) | deep_nobls @1000  DAG (val) | ΔDAG |
|---|---|---|---|
| validation (81) | 472 (80) | 458 (80) | −3.0% |
| kinska (165)    | 11394 (89) | 576 (99) | **−94.9%** |
| benchmark (334) | 16769 (255) | 2938 (266) | **−82.5%** |
| genaut (929)    | 211884 (745) | 5340 (750) | **−97.5%** |

Net verified coverage rises on every corpus (kinska +10, benchmark +11, genaut +5,
validation flat) while size collapses — the towers that were `SIZE`-unverifiable shrink
below the gate and become checkable. genaut frontier corroborates: distinct idiom
structures 121 → 75, gated-out blobs 53 → 2, the ≥20-node size tail 19.8% → 4.9%,
verified 745/799 → 750/752 (both CLEAN, 0 FALSE); not-LTL decisions (123) and the
routes-to-`true` are unchanged — definability is stable, only the LTL *forms* shrink.

## Result 2 — the budget knob (deep_nobls @100 / @500 / @1000)

DAG (val); validation is flat across budget (its formulas never reach the gate).

| corpus | @100 | @500 | @1000 |
|---|---|---|---|
| validation | 458 (80) | — | 458 (80) |
| kinska     | 5481 (95) | — | 576 (99) |
| benchmark  | 10132 (262) | — | 2938 (266) |
| genaut     | 19439 (762) | 5481 (750) | 5340 (750) |

On the **real** corpora (kinska/benchmark) the bigger budget is strictly better — *more*
verified **and** smaller — because mid-size tower nodes in the 100–1000 flat band now
clear the gate and collapse (kinska counting blobs: DAG 2175 → 51, 451 → 23).

The **genaut census** (929 pathological tiny automata) exposes the tradeoff the real
corpora hide: peak verified coverage is at **@100 (762)**; @500 and @1000 drop to **750**
(−12) while shrinking DAG 3.5× further. The coverage cost **saturates by 500** (@500 ≈
@1000 on answered/timeout/validated: 752/54/750), so @1000 over @500 is free on genaut
and wins on the real corpora. The 12 lost answers are a *census artifact*: pathological
automata whose 100–500-node blobs are slow to retranslate under the survey's 15 s build
budget — they time out, not crash, and 0 FAIL holds. genaut build cost ≈2.2× (704 s →
1570 s); the one benchmark `LTL → TIMEOUT` (`terminal_2scc.ltl:35`) is uncheckable at
*every* budget (31.5 M flat nodes), so no verified answer was lost there either.

**Blobs down, timeouts up — these are different things.** We do *not* produce more
blobs; we produce far fewer (gated 53 → 2, ≥20-node tail 19.8% → 4.9%). The old default
emitted a blob *fast* and moved on; the new one spends time *collapsing* it, and on the
hardest census cases that collapse work overruns the 15 s build budget → a timeout (no
answer) where the old default returned a fast unverifiable blob. The cost is latency on
the de-blobbing, not blob quality. It is also entangled with **coarse Spot control**: the
construction's `ltl2tgba` calls are guarded only by a *flat-size* proxy
(`translate_tree_limit`), never time-bounded per call, so one runaway translate inside the
round trip blows the *whole-survey* build budget and nukes an answer that was nearly fully
collapsed — rather than declining that one node (which `best_of([identity, …])` would
absorb). Pushing a per-call time+size bound down into `language.translate` (and decoupling
construction-translate from the verify oracle) is the right refinement — see `TODO.md`.

## Conclusions

1. **`deep_nobls` is the shipped default.** It dominates the prior `cakedsdet` default on
   every corpus — more verified coverage, dramatically smaller DAGs, 0 FAIL — and is
   sound by construction (faithful-or-⊥ at each node).
2. **Budget = 1000 is the shipped default.** Strictly better on validation/kinska/
   benchmark; on genaut @1000 ≈ @500 in coverage and marginally smaller, so 1000 costs
   nothing there relative to 500. This is our current reference implementation — we
   believe in it. It **may want refining** (the genaut census shows the budget trades a
   little coverage for size on pathological inputs, and the cost is entangled with the
   15 s build budget — a per-input build budget or an adaptive per-node budget could
   recover the genaut tail), but it stands as the baseline.
3. **Definability is untouched.** not-LTL counts and the true-routes are identical across
   recipe and budget — the round trip only reshapes the LTL it produces, never the
   LTL-vs-not decision.
