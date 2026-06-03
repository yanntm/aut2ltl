# Gist of "On the Translation of Automata to Linear Temporal Logic" (Boker, Lehtinen, Sickert, FoSSaCS 2022)

**Reference**: Full version of the FoSSaCS 2022 paper. Goal of the kr/ project: implement *this* systematic algebraic translation (no ad-hoc pattern matching on SCC shapes, terminal components, etc., as done in the separate buchi2ltl/ heuristic engine).

## High-Level Goal and Challenge
- LTL and ω-automata (det/nondet/alt) both describe ω-regular languages.
- LTL is a *strict subset* of ω-regular (corresponds to counter-free / aperiodic / star-free / first-order / very-weak alternating automata).
- Translation *LTL → automata* is well-understood (with known exponential/double-exp blowups).
- Translation *automata → LTL* (when the language is LTL-definable) had no known *elementary* upper bound on size blowup before this paper, even for the simplest case of deterministic counter-free automata.
- This paper gives the first elementary bound: **double-exponential temporal nesting depth** and **triple-exponential length** for translating counter-free deterministic ω-regular automata (any acceptance condition) to LTL.
- Bonus: the construction *preserves the acceptance condition* in the sense that it maps automata in certain classes (looping-Büchi, weak, Büchi, coBüchi, Muller) to LTL formulas in the matching level of the *syntactic future hierarchy* of LTL (safety/co-safety fragments etc.). E.g., a safety automaton can be turned into a safety LTL formula.

The method is **completely systematic and algebraic**, based on decomposition into "simple" components, followed by a recursive syntactic translation. No case analysis on particular automaton structures (no "if this SCC is terminal of size 2 and has mutually exclusive labels..." heuristics).

## Key Tool: Krohn-Rhodes Cascade Decomposition (Reset Cascades)
- Every finite semigroup (in particular, the transition monoid of a deterministic automaton) can be decomposed (via the Holonomy theorem / Eilenberg's version) into a "cascade" (wreath product / hierarchical product) of simpler "reset" components.
- A **reset cascade** of depth n (n levels) over alphabet Σ = 2^AP is a deterministic automaton whose states are *configurations* (tuples) (q1, q2, ..., qn), where each qi is a state in a simple "level-i" component.
- Each level is essentially a transformation that, for many letters, "resets" (maps many states to a constant image).
- The run of the cascade on a word w is the sequence of configurations reached by successively applying the letters of w, level by level (higher levels see the "combined letter" that includes the state change in lower levels).
- Counter-free deterministic automata correspond to aperiodic / group-free semigroups, which admit such reset cascades (no non-trivial group factors).
- In the kr/ code, the existing pipeline (extract generators from det Spot aut → generate SgpDec script → HolonomyCascadeSemigroup → parse to Cascade with state_to_config) is exactly producing this kind of hierarchical cascade representation. Configurations are the coordinate tuples (1-based per level).

A word w takes the cascade from configuration S to T while avoiding "bad" configuration B under certain constraints.

## The Core: 5 "Reachability Formulas" Defined Recursively on Cascade Levels
The translation works by defining LTL formulas that describe *reachability between configurations* in the cascade, while respecting "guards" (subformulas that must hold on the letters used for certain transitions) and attaching a "tail" subformula when the target is reached.

There are 5 main reachability formulas (plus weak/strong and " >0 " variants that ignore the first letter). They are defined by induction on the cascade level i (depth).

Intended semantics (from the paper's Table 1; orange parts highlight differences in auxiliary formulas):

1. **Main strong reachability** (S ~_B(β)^X T (τ) or similar notation):
   - Intuitively: "not reaching B while satisfying β, until reaching T and then satisfying τ".
   - Formally: there exists i such that after prefix w[0..i) we are at T, the suffix satisfies τ, and for all proper prefixes, we were not at B or the letter did not satisfy β.
   - Base (level 0, single config hi): simply (¬β) U τ .

2. **Weak version** (dual/release-like): "always, if we reach B under β then the tail τ must have been satisfied earlier" (or we never hit the bad situation before satisfying the target).

3/4/5. **Auxiliary formulas for higher levels** (when top level may stay the same or change):
   - Cases depend on whether source config hS,si equals bad hB,bi or target hT,ti.
   - They distinguish **Stay(s)** (letters that keep the top-level state s unchanged) vs **Leave(s)/Enter(t)** (letters that change the top component from s to something else, or enter t).
   - For "top level unchanged" paths: use disjunctions/conjunctions over σ in Stay(s), and recurse to *lower-level* sub-configurations S' ~ ... T' with adjusted guards like (σ ∧ X τ) or (ρ ∧ X β).
   - For paths that *do change* the top level: require seeing an Enter(t) combined letter at some point, after which the new top level t is preserved, while avoiding bad on the way, and using lower-level reachability for the sub-configs.
   - Weak versions relax the "must actually reach T and satisfy τ" requirement.

The definitions are mutually recursive (formula 1 uses 3 and 5; 3/4/5 recurse to lower level using the main formula on sub-configs; 2 is the dual of 1).

**Key properties proved by induction on level** (Lemmas 4 and 5):
- The formulas have exactly the intended semantics w.r.t. the actual runs δ of the cascade automaton on words w.
- Strong versions (1,3,5) stay in the "co-safety" syntactic class Σi ; weak versions in the "safety" class Πi (w.r.t. the LTL syntactic future hierarchy of Chang/Manna/Pnueli).
- This hierarchy preservation is what allows the final formula to inherit the acceptance type of the original automaton (Büchi → Π2 formula, safety/weak → Δ1 or Σ1/Π1, etc.).

## Complexity (Lemma 6)
Define D(i, d) and L(i, l) = depth and length of the main reachability formula at cascade level i, when input subformulas β,τ have max depth d and length l.

By induction on i (the level):
- Base i=0: depth = d+1 (the U adds 1), length = O(l).
- Inductive step: each higher level adds a constant to depth (because of the X's and the structure of Stay/Leave disjunctions) → overall depth ≤ d + 3i (linear in #levels).
- Length: multiplies by a factor polynomial in |Σ| and n (number of states per level) at each level → singly exponential in i: L(i,l) ≤ l · (10 |Σ|^2 n )^{4^i} or similar (the exact poly is derived from the number of disjuncts over Stay/Leave sets, which are size ≤ n, and the recursion).

Since the Krohn-Rhodes / Holonomy decomposition of the transition semigroup of a counter-free det automaton with n states yields a cascade whose depth and state counts per level yield overall double-exponential depth and triple-exponential length when plugged into the above (combined with the known holonomy decomposition bounds from Eilenberg / Pnueli-Maler), we get the main theorem.

## Main Theorem (Theorem 2 + corollaries)
Every counter-free deterministic ω-regular automaton D with n states (any acceptance) is equivalent to an LTL formula of depth O(2^{2^n}) and length 2^{2^{O(n)}} (double-exp depth, triple-exp length).

Moreover:
- If D is (looping-)Büchi / coBüchi / weak / Muller, the formula lands in the corresponding syntactic class (Π2 / Σ2 / Δ1 / Δ2 etc.).
- This gives a way to "normalize" an LTL formula to the right fragment of the hierarchy (e.g., take an arbitrary LTL safety formula, translate to det aut, decompose, translate back → get a safety LTL formula).

The construction is effective and works for any acceptance condition by reducing to the appropriate Boolean combination of Fin(C) or reach-to-G formulas (using the reachability formulas to express "visit C only finitely often" as ¬(reach C i.o.)).

## Why This Is the "Right" Method for kr/ (No Pattern Matching)
- Everything is driven by the algebraic structure of the cascade (the hierarchical reset components).
- The LTL is built by a *uniform recursive syntactic translation* on the levels/configurations + the Stay/Leave/Enter partition of letters at each level.
- The only "data" used from the original automaton are the combinatorial objects coming out of the decomposition (the cascade components, the Stay/Leave sets per state per level, the mapping from aut states to configurations).
- No need to inspect the original automaton for "nice" SCCs, terminal components with exclusive labels, specific entry/exit patterns, fusion opportunities, etc. Those heuristics are useful in practice for the common case but are ad-hoc and incomplete.
- The cascade view makes the "controlled movement between positions while satisfying guards" explicit, which maps directly onto the Until / Release / X structure of LTL.
- The 1-level base cases already present in the current kr/ code (one_level_reach_strong etc. in reachability_operators.py) are exactly the base case (m=0) and the inductive step for level 1 of the above reachability formulas. The higher-level cases (with the four subcases for source/bad/target equality + the >0 variants + the Enter/Leave disjunctions) are what is needed to go to multi-level cascades.

## Relation to Current kr/ Implementation
- The existing `decompose_aut` + `Cascade` (with levels, state_to_config as coordinate tuples, letter_valuations, build_config_transitions, move_config) already gives us the cascade + the ability to compute Stay/Leave per top-level state (by looking at which letters keep the top coordinate the same).
- The current `build_infinitely_often_accepting` + one_level_reach_strong (with absorbing check using the trans dict) is a first approximation / specialization of the reachability formulas for the top-level "infinitely often visit an accepting configuration" (Fin/Inf via reachability, as in Lemma 7 of the paper).
- Next natural steps (to implement the full method):
  - Generalize the 1-level operators to the full 5 formulas (with the four cases, >0, weak/strong, Stay/Leave/Enter cases, recursion to sub-configs of lower levels).
  - Implement the inductive construction on cascade depth (using the per-level Stay/Leave partitions derived from the generators / move_config).
  - Implement the Fin(C) construction from Lemma 7 (¬ reach-to-C-i.o. or last-visit-to-C then never return).
  - Lift acceptance conditions to the appropriate Boolean combination over configurations (as in the proof of Theorem 2).
  - Use the holonomy decomposition (already available via SgpDec) + the above to get the full aut → LTL.
  - The size will be large (as predicted), but elementary, and systematic.

This is the "pure" goal for the kr/ folder: realize the Boker et al. construction inside the existing Cascade representation, using only the operators and recursive definitions, without ever falling back to pattern-matching on the shape of the original automaton's SCCs.

(Extracted and summarized from the paper text via pdftotext. See the original PDF for full proofs, tables, and the exact syntactic definitions of the five formulas.)
