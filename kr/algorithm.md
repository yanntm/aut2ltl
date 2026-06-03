# KR Algorithm Description: Translation of Counter-Free Deterministic ω-Regular Automata to LTL via Krohn-Rhodes Cascades

**Source**: Synthesis of the Boker–Lehtinen–Sickert FoSSaCS 2022 paper ("On the Translation of Automata to Linear Temporal Logic") with implementation-oriented clarifications for the `kr/` project.

**Core Goal of kr/**: Realize *this* fully systematic, algebraic translation. No ad-hoc pattern matching on specific SCC structures, terminal components, fusion opportunities, "nice" labelings, or other automaton-shape heuristics (those live in the separate `buchi2ltl/` engine). Everything must be driven uniformly by the algebraic structure of a Krohn-Rhodes reset cascade and the recursive definition of reachability formulas.

The paper gives the first *elementary* upper bound: for a counter-free deterministic ω-regular automaton with n states, an equivalent LTL formula of **double-exponential temporal nesting depth** and **triple-exponential length**. The construction also preserves the acceptance condition in the syntactic future hierarchy of LTL.

## High-Level Algorithm: `TranslateToLTL(D)`

**Input**: Counter-free deterministic ω-regular automaton  
`D = (Σ = 2^{AP}, Q, ι, δ, α)` with |Q| = n (any acceptance condition α: Müller, Büchi, coBüchi, weak, looping, etc.).

**Output**: Equivalent LTL formula ϕ over AP, with the complexity and hierarchy guarantees above.

1. **Normalize to Müller form** (standard, polynomial)  
   Produce an equivalent deterministic Müller automaton D' on the *same* semiautomaton (same Q, ι, δ). Every deterministic ω-regular language has a Müller automaton on the identical transition structure.

2. **Krohn-Rhodes / Holonomy reset-cascade decomposition** (Proposition 6 + Eilenberg)  
   Compute a reset cascade (wreath product / hierarchical product)  
   `A = ⟨Σ, A₁, A₂, …, Aₘ⟩`  
   with m ≤ O(n) levels and ≤ O(n) states per level, together with a homomorphism h from configurations of A to states of D'.  
   - Each level Aᵢ is a simple "reset" semiautomaton.  
   - The cascade is counter-free because D is.  
   - Total configurations of A: at most (O(n))^{O(n)}.  
   Pick any initial configuration ι_A with h(ι_A) = ι.

   (In the current `kr/` implementation this step is already performed by `decompose_aut` → SgpDec `HolonomyCascadeSemigroup` → parsed `Cascade` object whose `state_to_config` tuples are exactly the configurations and whose `levels` describe the per-level reset components.)

3. **Lift the acceptance condition to configurations of the cascade** (Propositions 7–8)  
   - For Büchi / coBüchi / Rabin: direct lift (same number of pairs for Rabin).  
   - For Müller: obtain an equivalent Müller condition α' on the configurations of A (at most 2^{O(mn)} accepting sets).  
   - For weak / looping variants: special direct constructions (single sink SCC, etc.).

4. **Build the family of reachability formulas (core inductive construction)**  
   By induction on cascade level i, define five families of parameterized LTL formulas that express "reachability from configuration S to T while avoiding bad configuration B, under guard β, attaching tail τ".  
   See the detailed inductive definition below (the five formulas of Section 4.2 / Table 1).  
   The base (level 0) is ordinary Until. Higher levels case on whether the top component stays the same (Stay) or changes (Leave/Enter), using disjunctions over the appropriate letter sets and recursing to lower-level sub-configurations with adjusted guards (σ ∧ Xτ, ρ ∧ Xβ, etc.).

5. **Encode "visit a configuration only finitely often" (Lemma 7)**  
   For any configuration C of A define the unconditional reachability shorthands  
   `S ↝ T` and `S^{>0} ↝ T` (the "main" and "after-first-letter" versions).  
   Then  
   `Fin(C) := ¬(ι_A ↝ C) ∨ ι_A ↝ C ( ¬ (C^{>0} ↝ C) )`  
   `Fin(C) ∈ Σ₂` and holds on w exactly when the unique run of A on w starting at ι_A visits C only finitely often.

6. **Assemble the final formula from the (lifted) acceptance condition**  
   For a Müller condition α' on configurations:  
   ϕ = ⋁_{M ∈ α'} ( ⋀_{C ∈ M} ¬Fin(C)  ∧  ⋀_{C ∉ M} Fin(C) )  
   Each disjunct says "the set of configurations visited infinitely often is exactly M".

   For weaker conditions the construction specializes (looping-Büchi → disjunction of reach-to-sink formulas in Σ₁, etc.).

7. **(Optional) Finite-word variant**  
   Replace selected X operators by the weak next in the "stay-weak" auxiliary formula; the rest of the construction is identical and yields a formula in the corresponding finite-word safety/co-safety fragment.

**Correctness** (by induction on cascade level + homomorphism properties):  
- The reachability formulas have exactly the intended semantics w.r.t. the runs of the cascade (Lemma 4).  
- They lie in the expected levels of the syntactic future hierarchy (Lemma 5).  
- `Fin(C)` correctly captures finite visits.  
- The Boolean combination exactly encodes the lifted Müller (or weaker) condition.  
- The homomorphism h preserves runs and acceptance.  
Hence L(D) = L(ϕ).

**Complexity** (Lemma 6 + Theorem 2)  
- Depth of the main reachability formula at level i: ≤ d + 3i (linear in #levels).  
- Length at level i: singly exponential in i (polynomial factor |Σ|·n per level, raised to 4^i).  
- Overall for the full construction: double-exponential depth (O(2^{O(n)})) and triple-exponential length (2^{2^{O(2n)}}).  
(The dominant cost is the exponential number of disjuncts at each level plus the recursive blow-up of the "change top level" case.)

## The Five Reachability Formulas (Core of the Inductive Translation)

Fix a reset cascade A. Configurations of level i are tuples. For a state q of level i+1 let Stay(q), Leave(q), Enter(q) be the obvious partitions of combined letters.

For configurations S, B, T of level i and formulas β, τ the five formulas are defined by induction on i (see the paper's Table 1 for the exact intended semantics and the four-case distinctions for the "stay" and "change" auxiliaries).

**Formula 1 (main strong reachability)**  
S ∼_B(β)^X T (τ) :=  
- if level 0: (¬β) U τ  
- otherwise: (solid-arrow stay version) ∨ (dashed-arrow change version)

The solid-arrow version requires the top-level state to stay the same throughout the path (using Stay letters and lower-level reachability on the sub-configurations).  
The dashed-arrow version allows (and requires) a change of the top-level state (using Enter/Leave letters).

**Formula 2 (weak dual / release)**  
The dual of Formula 1: "as long as we have not satisfied the target under τ, we must not hit the bad situation under β".

**Formulas 3 & 4 (stay in top-level state – solid arrow)**  
Strong (3) and weak (4) versions that enforce the top component never changes.  
They case on the four possibilities (source == bad? source == target?) and differ only in whether β/τ must hold on the very first letter.  
The common " >0 " sub-formula is a big disjunction over σ ∈ Stay(s) of lower-level reachability formulas on the projected sub-configurations, conjoined with avoidance of leaving s or hitting the bad pair (using the appropriate lower-level formula).

**Formula 5 (change top-level state – dashed arrow, most complex)**  
Requires:  
- eventually seeing a combined letter that enters the new top state t (while avoiding bad so far),  
- after that entry the new top state is preserved and bad is avoided,  
- the path from S to the entry point itself avoided bad (using the weak stay formula),  
- the top state actually did change (a final disjunct that forces a Leave).

All five formulas are mutually recursive; the recursion bottoms out at level 0 (plain Until). By construction they stay inside the expected syntactic classes (strong versions co-safety Σ_i, weak versions safety Π_i).

The exact case distinctions and the auxiliary ">0" / solid / dashed arrows are given in full in the paper (pages 10–13 of the extract). In an implementation they are generated by enumerating the Stay/Leave/Enter sets at the current top level (which are directly computable from the generators of the cascade / the `move_config` function) and recursing on the projected lower-level configurations.

## Relation to the Current kr/ Code Base

- `Cascade` + `state_to_config` tuples + per-level `levels` + `letter_valuations` + `build_config_transitions` / `move_config` already give us exactly the reset cascade + the Stay/Leave partitions per top-level state.
- The existing 1-level operators (`one_level_reach_strong`, `build_1level_reachability`, guard helpers in `reachability_operators.py`) together with `build_infinitely_often_accepting` + the absorbing check are a first working approximation / special case of the base (level-0/1) reachability formulas plus the Fin(C) encoding of Lemma 7.
- `decompose_aut` already performs the holonomy decomposition step.
- The clean `reconstruct_ltl_1level_buchi` is already trying to be the "thin pure builder" on top of the operators (the ideal style demanded by the paper).

The missing pieces for the full algorithm are precisely the higher-level cases of Formulas 3–5 (the four-case distinctions + >0 variants + Enter/Leave disjunctions + proper recursion on sub-configurations of lower levels), the general Fin(C) construction, and the final assembly from the lifted acceptance condition.

## Why This Approach (No Pattern Matching)

Every step is driven by the algebraic structure of the cascade:
- The decomposition is canonical (holonomy).
- The letter partitions Stay/Leave/Enter are combinatorial objects derived from the generators.
- The LTL formulas are generated by a uniform recursive syntactic translation whose only data are the above objects plus the sub-formulas β and τ.
- No inspection of the original automaton's SCC graph, no special cases for "terminal 2-SCC with mutually exclusive labels", no fusion heuristics, no ad-hoc entry/exit timing rules that look at the concrete shape of D. All such information is already compiled into the cascade and its Stay/Leave sets.

This is the "pure" target for the kr/ folder.

(For the full proofs, the exact syntactic definitions of the auxiliary formulas, the unary warm-up bounds, and the detailed complexity recurrences, consult the original paper or the extracted text in `paper/Automata2LTL.txt`.)