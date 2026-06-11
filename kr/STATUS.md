# kr/ Current Status

Factual snapshot of the current state. History lives in `git log`; work items in
`kr/TODO.md`; doc map in `kr/README.md`.

## Pipeline (done, general)

- `decompose_aut`: Spot norm to det complete min-even parity with **state-based
  acceptance** (`sbacc` — soundness requirement: the Muller condition is lifted over
  configurations, so the infinitely-visited state set must determine acceptance)
  → generators (explicit 2^|AP| letters) → GAP/SgpDec holonomy → parsed `Cascade`.
- `Cascade`: levels, state↔config (1-based), letter valuations, `move_config`,
  Enter/Stay/Leave helpers, pruned config automaton, accepting configs.
- Good Muller sets: enumeration of strongly-connected **accepting subsets** of
  non-rejecting SCCs of the pruned config aut (`acc().accepting(in-M edge-mark union)`
  oracle, exact under sbacc; `KR_MULLER_SCC_LIMIT=12` gate, logged whole-SCC fallback).
- Stability: `bdd_utils` buddy-var precompute + per-case subprocess isolation in tests.

## Operators — LITERAL paper forms, spot.formula objects end-to-end

All five formulas are now the literal constructions of paper Sec 4.2 /
construction-ref §7 (the former from-S / first-step approximations are gone):

- `_stay_gt0_strong` = solid⁺: last-step decomposition over combined letters
  ⟨σ,T'⟩ enumerated over ALL h-image configs (`_combined_letters_at_level`),
  lower-level prefix reach to T', stay enforced by Leave-avoid conjuncts,
  bad-predecessor conjuncts.
- `_dashed_change_strong` = Formula 5 lines (1)+(2)+(3): Enter(t)/Enter(b)/Leave(s)
  as combined letters, lower prefix reaches, parameterized-bad line(2) with the
  SWAPPED wsolid, line(3) solid-to-leave-point. No s==t guard (leave-and-return).
- `reach_weak` = the literal dual ¬reach(S,T,τ,B,β) (old G(τ|¬β) base was wrong:
  Table 1 gives τ R ¬β). The bespoke `_dashed_change_weak` was a non-paper
  invention and is deleted.
- `_solid_stay_weak`/`_stay_gt0_weak` = literal wsolid/wsolid⁺ (lines (1)+(2),
  no free-reach, wreach avoids); the s≠t early-false was removed (wrong for
  weak: degrades to "never blocked"). Case dispatches compare FULL configs.
- `fin_c` per Lemma 7 with working ι==C postponement.
- **No string round-trips (P0-perf step 1 done):** all operators + fin_c accept
  and return hash-consed `spot.formula` objects (str still accepted at entry
  for probes); one shared `spot.tl_simplifier` (persistent cache) does at most
  one simplify per operator return; `_str_f` is a pure stringifier; assembly
  in `reconstruct_ltl_paper_style` builds formula objects (fin_c computed once
  per config, reused across Muller terms) and stringifies only the final
  result. The `PAPER_STYLE_TOO_LARGE` sentinel guard is gone — the real
  formula is always returned; callers run equiv checks under timeouts.

## Semantic validation state (trace_fin_semantics grounding)

- **GFa: ALL SUB-TERMS GROUNDED OK** (1L regression green).
- **G(a -> X b): ALL SUB-TERMS GROUNDED OK** — every fin_c sub-term (r_to, r_gt0,
  r_with, fin, !fin) for every config is language-equivalent to ground truth.
  This was the first 2L target; the level recursion is now semantically right.

## Open problem: equiv-checking large outputs (size = serialization artifact)

Measured after the object rewrite (`kr/testing/measure_formula_dag.py`):
G(a->Xb) builds in **0.08s**; the formula is **781 unique DAG nodes** but
unfolds to 1.26M tree nodes / **3.2MB string** (sharing factor ~1600x) — the
blowup was always the *flat rendering*, never the construction. The remaining
blocker is verification: the formula has **126 distinct temporal subformulas**,
and Spot's tableau translation wants one acceptance set each → hard error
"Too many acceptance sets used. The limit is 32" (fast fail, not a stall).
Options (TODO P0-verify): shrink distinct temporal subterms (vacuous-conjunct
pruning, equivalence-based interning), compositional checking (trace_fin
already grounds every sub-term), or word-sampling validation.

## Survey snapshot (2026-06-11, post object rewrite)

- 1L regressions hold: `Fa`, `GFa` True.
- 2L now passing equiv end-to-end: `a U b`, `Fa | Gb`, `Fa & Gb`, `Ga | Fb`.
- `G(a -> X b)`: semantically grounded OK (all sub-terms), but equiv check
  infeasible (32-acc-set limit above).
- `F(a & X b)`: TIMEOUT >45s (not yet diagnosed: construction vs translate).
- **`Ga | Gb`: equiv=FALSE** — new minimal failing case (safety, sizes=[1,4],
  trivial top level). Next semantic target.

## Tooling for targeted work

- `kr/testing/survey_mp_cascade.py` — MP-class × depth ladder.
- `kr/testing/trace_fin_semantics.py` — per-config semantic grounding of fin_c
  sub-terms vs ground-truth automata, with witness words.
- `kr/testing/ltl_diff.py` — containment direction + witness words.
- `kr/testing/test_kr_r4_audit.py` — structural checklist + drift grounding
  (gate for operator commits).
- `kr/testing/measure_formula_dag.py` — DAG vs string size of the assembled
  formula (unique nodes, unfolded tree, distinct temporal subformulas, build
  time).
