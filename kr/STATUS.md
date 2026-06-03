# kr/ Current Status (before further coding)

**Goal of kr/**: Full general algebraic Büchi-to-LTL via Krohn-Rhodes holonomy cascade (Boker-Lehtinen-Sickert 2022), *without any pattern matching* on specific SCC structures (unlike the old buchi2ltl/ heuristics with f2/tN).

This is separate from the heuristic path. We want the systematic construction: decomp -> config paths -> inductive reachability K operators -> Fin/Inf -> acceptance encoding -> top LTL.

## What is implemented (as of now)

### Decomposition + Data (Paper Step 1 + part of 2)
- Full end-to-end: `decompose_aut(det_spot_aut)` (requires deterministic aut; use "Deterministic" in translate).
- Uses extract + generated GAP script (LoadPackage("SgpDec"), HolonomyCascadeSemigroup, AsCoords etc. adapted for SgpDec 1.x) + parse.
- `Cascade` dataclass is rich and general:
  - num_levels, levels (size + kind from SgpDec)
  - state_to_config / config_to_state (coords, 1-based)
  - generator_images (list of images; augmented with dead trap for incomplete auts)
  - aps, letter_masks, letter_valuations (full dicts of prop->bool for every 2^|AP| letter — exactly for guards in LTL)
  - original_aut ref (for acc lifting)
  - Methods (general, no patterns):
    - move_config(config, letter_idx) — lift via original state rep + images (homomorphism)
    - all_configs()
    - build_config_transitions() — config -> {letter_idx: next_config}
    - build_configuration_automaton() — returns {"states": list of configs, "aps", "transitions": list of (li, next_c, val_dict) per config} 
    - accepting_configs() (heuristic: configs that have some acc outgoing in original)
- Extraction now completes incomplete auts (common in Spot) with a dedicated dead rejecting trap state (n = original n, dead = n). This preserves the *language* (undefined letters cannot continue to acc runs). Generators become total on 0..n.
- Works on trivials (1-state), simples, and the motivating G(p -> (q U r)) (gives usable config aut).
- GAP bridge, install.sh, check_gap_available all general.
- Synthetic path (decompose_gens) exists for testing without Spot.

This part is solid and general (algebraic, no heuristic patterns).

### Reachability Operators (Paper Step 3, base)
- In reachability.py:
  - Helpers: letters_to_prop(valuation) -> "p & !q", make_guard for OR of satisfying letters.
  - 1-level base cases (following paper's K operators for reset level):
    - one_level_reach_stay(S, B, T, tau, vals, aps, trans_dict)
    - one_level_reach_strong (avoids B)
    - one_level_reach_weak (release dual)
  - These are *general* for any 1-level reset: use the trans dict (from any config) to compute stay/change guards, build (stay U (change & tau)), with B avoidance.
  - build_1level_reachability(...) returns dict of the variants.
- These can be called on any config in a 1-level cascade using data from build_config_transitions().
- No hard-coded formula patterns here; pure from the trans + valuations.
- Fin_1level / inf_1level exist but are still dummies (not using K yet).

This is the general base for induction. Not ad-hoc.

### Top-level Reconstruction
- reconstruct_ltl_1level_buchi(casc) exists.
- **Problem**: It contains significant ad-hoc structural logic (if 1-state early return using original_aut, if len(configs)<=1, if dead_c and acc_permanent, has_bad_self, special "q" filter for until cases, fallback to specific guarded U + G F).
- This produces *correct equivalent* formulas for many trivials and simples (true/false/a/Fa/Ga via the early 1-state path or dead analysis).
- For the motivating G(p->(qUr)) (1-level): it runs and outputs a formula, but it is **not equivalent** (confirmed with are_equivalent + emptiness of diffs).
- This is the part that has "pattern matching on structure" (dead/permanent sink detection, special enter logic) — exactly what we want to avoid. It was a prototype to get some cases working while building the operators.

### Induction / Multi-level (main missing piece for full general)
- Nothing. No recursive implementation of the paper's compound formulas.
- The paper's K operators for >1 levels have 4 cases for "top level unchanged" (with sub-reach on lower for Stay/Leave) + the change case (with Enter subcalls + lower reach).
- We have the 1-level as base; induction is the next step (combine with lower-level reachability on the compound Stay/Leave/Enter conditions from the current level).

### Fin/Inf, Acceptance, Top Formula (Paper Steps 4-5)
- Placeholders only.
- reconstruct tries a top-level for Büchi (G(core) & G(F ...)) but it's tied to the ad-hoc logic and not general/correct.
- No proper use of reachability to define "visit config C i.o." (Fin(C) = cannot return to C i.o. while avoiding..., Inf via G F reach).
- No encoding of the original acceptance (Büchi as disj Inf(c) for c in F, lifted via homomorphism; general Muller etc.).

### Testing / Examples / Other
- Examples (spot_det.py, synthetic.py) demo Phase A (config aut + trans with vals) + calling the 1-level reach ops directly. Generated .gap scripts for inspection.
- Simples (true/false/a/Fa/Ga) often give equivalent output now (via special paths), but not purely from the K operators.
- G(p->(qUr)): Decomp covers (1-level usable config aut). Reconstruction runs but not equivalent.
- No dependence on old f2/tN patterns.
- Still limited to small |AP| (explicit 2^aps letters).
- Cascade is serializable-ish; data from SgpDec is faithfully represented.
- The operators are closer to the "full general" than the reconstruct.

## Gaps for the full general approach
- Reconstruct is not general (has structural ifs/patterns on dead/permanent/1-state/enter). Should be a thin pure builder on top of the K operators.
- No induction: cannot handle cascades with >1 levels (or even clean 1-level for complex obligations like the until example without ad-hoc).
- Fin/Inf not implemented using the reachability.
- Acceptance encoding + full top-level formula not general.
- Acc is only heuristic on configs; paper needs precise on transitions/moves for the K defs.
- For the motivating example: decomp yes (step 1+2), but the LTL side not yet giving equivalent via general method.

## On the roadmap steps
- Step 1 (decomp semi-aut to cascade): Covered, general.
- Represent runs as config paths (step 2): Covered (config aut).
- Define reachability inductively (step 3): Base 1-level K operators exist and general. **Ready for the induction** (implement the recursive multi-level versions of the 5 operators per the paper's defs, using sub-reach on lower levels for the Stay/Leave/Enter cases). This is the core missing piece for "full general".
- Fin/Inf (step 4), acceptance (step 5): Not yet.

We are ready for dealing with the induction (the recursive part of step 3), after cleaning the reconstruct to be pure K-based. The 1-level operators give us the foundation to recurse on.

The decomp/config part is in good general shape. The LTL construction is at "1-level operators + ad-hoc top for some cases".

No more coding until we agree on next (e.g. clean reconstruct + implement inductive K defs).

### Progress after resume (post-crash)
- Step 1 of refactor done: old ad-hoc body isolated as `reconstruct_ltl_1level_buchi_heuristic`.
- New thin `reconstruct_ltl_1level_buchi` + `build_infinitely_often_accepting` implemented as the main path for 1-level (exactly the skeleton requested: uses one_level_reach_strong on init->acc with tau=true, F/GF chosen based on whether the target acc is absorbing per its trans dict).
- Split operators into smaller `kr/reachability_operators.py` (and `bdd_utils.py`) to make future edits safer and functions cleaner.
- Stabilized the root cause of segfaults: precomputed buddy var map once (in `bdd_utils.get_ap_bdd_vars` + `build_point_bdd`) before the per-letter loop in extract; removed interleaving of var discovery with main-aut bdd & operations. Xa and other cases now reliable in repeated runs.
- For pure 1-level cases (Fa, Ga, false): clean path is taken, produces simple formulas (F(reach) for absorbing acc sinks, G F for non-absorbing). "false" and Fa now give correct equivalent LTL via the pure K path (no structural ifs).
- Both versions + the operators remain exported; heuristic available for A/B comparison during further tuning of the 1-level K combination / acceptance lift.
- Still to do (per plan): more cases may need refined top-level (safety vs recurrence obligations), improve guard simplification (long DNFs), then the multi-level induction.
