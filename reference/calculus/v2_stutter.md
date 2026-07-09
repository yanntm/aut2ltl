date: 2026-07-10
git: f40832e74
seed: full sweep (no sampling)
corpus: genaut/corpus/flat_canon

# V2 — stutter read-off vs Spot

Our verdict is the `.cat` `stutter:` tag (classify's Prop 3.3 read-off); Spot's is `spot.is_stutter_invariant` on the paired deterministic HOA. 3938 languages, 3938 scored.

## Census — the stutter read-off, split by the LTL bit

Stutter-invariance is the X-free refinement of LTL, so every stutter-invariant language is LTL-definable.

| | LTL | non-LTL | total |
|---|--:|--:|--:|
| stutter-invariant | 648 | 0 | 648 |
| stutter-sensitive | 1592 | 1698 | 3290 |
| total | 2240 | 1698 | 3938 |

Stutter-invariant share: **16.5%** of the census (648/3938), **28.9%** of the LTL languages.

## Agreement with Spot

| | Spot invariant | Spot sensitive |
|---|--:|--:|
| **ours invariant** | 648 | 0 |
| **ours sensitive** | 0 | 3290 |

Agreement: **3938/3938 = 100.00%** (perfect). Spot `is_stutter_invariant` on these tiny deterministic automata is near-instant: median 0.010 ms, max 0.07 ms.

## Disagreement dossier

None — the algebraic read-off and Spot agree on every scored language.
