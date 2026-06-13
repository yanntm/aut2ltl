# kr/ TODO

Forward-looking work items only. Current state: `kr/STATUS.md`. History: `git log`.
Construction reference: `paper/automata-to-ltl-construction.md`; ground truth:
`paper/Automata2LTL.txt` (Sec 4.2 + Table 1 + Formulas 3/4/5 ≈ lines 440–1040).

Context for prioritization: the FoSSaCS construction is implemented and
semantically validated (see STATUS). The thesis we are now chasing is that the
paper's double-exponential is a *flat-rendering* artifact: every case measured
so far builds a small hash-consed DAG in fractions of a second while only the
unfolded tree/string explodes. P0 below is the work that turns that
observation into a usable pipeline (and a SOTA claim).

## P0 — practice beats the bound (active)

Analysis, measurements and OPEN questions behind these items live in
`kr/dag_folding.md` (item numbering there: plumbing → vacuity pruning →
fold pass → interning). Items below are the actionable queue.

1. **Fold pass — step A DONE 2026-06-12** (per-DAG-node memoized
   tl_simplifier, hybrid full≤2000-nodes/basics policy + reach dead-tail
   early-out): `G(p->(qUr))` distinct temporal 4115→559, `G(a->Xb)` tree
   85.5M→3.6M, `a&Xa` subproblems 752→311. Remaining candidates, in the
   order the tail-anatomy data suggests (probe_tail_anatomy.py: TAILS drive
   the explosion — ×2–10 distinct tails per level — not the avoid web):
   - ~~**B. letter fusion**~~ **DONE 2026-06-12** (soundness:
     dag_folding.md "Letter fusion"; numbers: STATUS — XXa/XXXa collapse
     to the literal formulas, 3 survey cases flip True, G(a->Xb) under
     the acc cap). Remaining wall is fusion-neutral cases (1 AP, all
     letters distinct futures): `X(a&Xa)` 3.1×10¹⁰, `G(a->Xa)` 11.3M —
     they need C/D/E below or the 1c rewrite pass.
   - **C. cascade-aware vacuity pruning** of the combined-letter enumeration
     (unreachable pre-configs, empty Enter/Stay) — prunes memo keys at the
     b^k base; soundness argument needed (see dag_folding.md OPEN).
   - **D. tail normalization** (canonical letter-word prefix + continuation
     form) — syntactic, internal, targets the wrapping count directly;
     expected partially subsumed by B (fewer distinct tails by construction).
   - **E. budgeted semantic interning** of small subterms.
1c. **Own syntactic rewrite pass — IN PROGRESS (kr/simplify/, 2026-06-12).**
   Rule 1 (context pass: sibling-context propagation over the boolean
   skeleton, identity domination incl. temporal nodes, Shannon at Or,
   context reset at temporal boundaries) DONE + validated
   (kr/simplify/testing/test_context_pass.py, 16/16 with per-case Spot
   equivalence). Rule 2 (now-evaluation: one-step unroll of G/F/U/R/W/M
   heads under boolean context, shrink-only, identity + BDD entailment)
   DONE + validated (test_now_eval.py, 18/18). Rule 3 (partial factoring,
   the sound form + Minato minimization of guard groups) DONE + validated
   (test_factor_pass.py, 10/10 incl. the draft-bug regression).
   ~~Pipeline integration~~ **DONE 2026-06-12** (KR_SIMP_OWN per-node hook
   in _simp_f, persistent memos, size cap 2000, shared bdd_dict; numbers
   in STATUS — gates green, fuzz 1500 ALL EQUIVALENT).
   ~~Rule 4: unroll-inverse folding~~ **DONE 2026-06-12** (fold_pass.py —
   expansion-law pair folds + first-occurrence/induction + S1/S2
   Formula-5 subsumption; the census-reducing realization of the
   "eventuality-aware rewriting" item: F(a&Xa) census 55→33, G(a->Xb)
   flipped survey True; numbers in STATUS). Refinement queue:
   ~~Context-aware subsumption~~ **DONE 2026-06-13** (initial-state
   opening + ctx_subsume; F(a&Xa) UNDER the 32-acc cap, census 26;
   numbers in STATUS). Remaining:
   - **eventuality census, remaining**: F(a&Xb) still 74 distinct
     temporals (cap 32). Next: deeper-shifted ladder forms (only the
     one-step shift is matched), and the multi-AP variants.
   - **opening flow direction**: one-way (earlier→later in canonical
     child order) misses openings whose source sorts after the target;
     alternating the direction across the pipeline's repeated context
     passes is sound (each pass a fixed direction) and would double
     coverage — needs the direction in the context-pass memo key.
   - giant nodes are skipped by the cap, so the X(a&Xa)/reactivity wall
     is barely moved — needs either O(n) factoring on big Ors or the
     C/D/E fold candidates. NB the cap measures UNFOLDED tree size; with
     per-node memoized passes a DAG-size cap is the honest poly bound
     and would let the top of big formulas be processed.
   - fold pass changes memo keys → construction takes different paths
     (X(a&Xa) unfolded count moved both ways across tools); re-baseline
     the size censuses in kr/testing/logs/.
   - the 32-acc abort path in equiv children dies with free(): invalid
     pointer (teardown, cosmetic but masks the real verdict — make the
     harness report it as ACC_CAP). Background
   (user rule set, Java lineage): Spot's
   tl_simplifier, even at full strength on 5-node inputs, does NOT do
   present-literal cofactoring or guard factoring: `a & (!a | G(!a|Xa))`
   (≡ Ga) and `(!a & Xa) | (a & Xa)` (≡ Xa) both survive full simplify
   untouched (probe_guard_fusion part A). Candidate rules, sharing-aware
   per DAG node (the "grow our own rule set" hatch in ltl_builders):
   (i) cofactoring `a ∧ (¬a ∨ φ) → a ∧ φ`; (ii) Or-factoring
   `(g₁∧Xt) ∨ (g₂∧Xt) → (g₁∨g₂)∧Xt` + Minato guard minimize (catches
   tails that become equal only after simplification, which construction-
   time fusion cannot see); (iii) induction `x ∧ G(x→Xx) ≡ Gx` (riskier,
   parked separately).
2. ~~**Output representation**~~ **DONE 2026-06-12**: reconstruct returns the
   hash-consed `spot.formula` DAG; flattening is opt-in (`reconstruct_ltl_str`
   historical entry, `_str_f_gated` under `KR_FLATTEN_TREE_LIMIT`). The former
   CONSTRUCT_TIMEOUT cases now report measured sizes in seconds (`G(a->Xa)`:
   5.1×10¹¹ tree nodes from ~2k DAG nodes). This is the native input for the
   planned BDD-style analysis layer.
3. **Verification beyond Spot translation — now the verification front**:
   compositional checking (trace_fin is the per-sub-term oracle),
   word-sampling validator (ultimately-periodic u·v^ω, construction-ref
   pitfall #10), equivalence-based interning of subterms. Probed and CLOSED
   (2026-06-12, `probe_object_translate.py`): translating from the formula
   OBJECT (Couvreur fm / translator class) does not dodge the wall — one acc
   set per distinct eventuality (cap 32 compile-time) and the tableau state
   space is subformula SETS, which sharing doesn't shrink. So: either fold
   the distinct-eventuality count below 32 (item 1 + interning), or verify
   without translation. Spot authors are in the loop on sharing-aware
   translation; revisit when they ship anything.

## P1 — coverage

- **Full acceptance dispatch per construction-ref §9.3 — NOW EVIDENCE-BACKED
  as the structural fix for the census wall (probe_muller_overlap,
  2026-06-13, numbers in STATUS):** the Fin(C)/¬Fin terms carry ~100 of
  G(p->(qUr))'s 84-census while the reach part (~25 census) already
  contains a conjunct literally equivalent to the target body. Direct
  Σ₁/Π₁ (looping), Π₂/Σ₂ (Büchi/coBüchi), Δ₁ (weak end_in(G)) forms
  replace the Fin web for the matching input classes and keep outputs in
  the right hierarchy class. Candidate next major iteration.
- **Decompose-and-recombine at the root — the implementable form of the
  acceptance dispatch (NEXT, 2026-06-13).** Sound because kr is
  language-faithful and a ROOT operator is a pure position-0 language op (no
  temporal-placement / acceptance-coupling caveats — contrast the P4 internal
  injection): `L(A)=⋃L(Aᵢ) ⟹ ⋁ kr(Aᵢ) ≡ L(A)`, and dually
  `L(A)=⋂L(Aᵢ) ⟹ ⋀ kr(Aᵢ) ≡ L(A)`. Two splits, both run the EXISTING kr on
  acceptance-trivial pieces (Fin web → singleton good-set per piece) and
  recombine:
  - **OR-decompose by STRENGTH** (Spot strength decomposition: weak / terminal
    / strong sub-automata whose union is language-equivalent — Renkin &
    Duret-Lutz, "decomposition of automata by strength"). Targets
    disjunctive / mixed-strength: `Ga|Fb`, `FGa|FGb`, `(aUb)|Gc`.
  - **AND-decompose by ACCEPTANCE SET** (generalized Büchi accepts iff it
    visits every mark i.o.: `L(A)=⋂ᵢ L(A|only Sᵢ)`, each piece single-Büchi).
    Targets conjunctive recurrence the union split can't (it's a product, not
    a union): `GFa&GFb`, `(GFa&FGb)`.
  This hoists the Muller disjunction/conjunction OUT of the Fin web up to the
  root, instead of hand-coding the §9.3 Σ/Π/Δ forms above — cleaner, reuses
  all of kr, composes with the P0 folds. SCOPE: attacks the ACCEPTANCE-driven
  census (the reactivity/recurrence/persistence wall); does NOT help the
  REACH/cascade-driven census (`G(a->Xb)` is pure safety, decomposes to ONE
  piece, census 79 unchanged — that is the P0 fold/simplify job; right
  division of labor). OPEN CHECKS before committing to it: (1) pin the exact
  Spot strength-decomposition API and confirm the union is language-exact on
  our normalized det parity D (not just on Büchi); (2) probe that kr on a
  single-Büchi / single-strength piece actually yields a small census — split
  `GFa&GFb` into its two single-Büchi pieces and compare total recombined
  census vs the monolithic 9.1×10¹⁶-tree baseline; (3) decide where the split
  lives (a front-end wrapper over decompose_aut + reconstruct, mirroring the
  reverted invariant-peel front-end shape, with OR/AND assembly of the per-
  piece DAGs). Lineage: this is the same root-soundness that makes `φ ∧ kr`
  sound when the INITIAL state carries an arbitrary φ (position-0 assertion =
  root conjunction); decomposition is that observation applied to ⋃/⋂.
- π-preimage exactness in the non-primary paths: `accepting_configs` and the
  config_graph fallbacks still map states through the lift only (the primary
  pruned-config-aut path is already correct via `state_of` = π). With covers
  real (duplicated sinks), the fallbacks should classify every closure config
  through π.
- Trivial (size-1) level collapse to reduce effective depth.

## P2 — feasibility

- Larger |AP| (on-demand letters or BDD guards instead of explicit 2^k —
  8 letters already multiply the combined-letter fan-out visibly).
- Hierarchy class tagging of outputs (Σᵢ/Πᵢ/Δᵢ per Lemma 5).

## P3 — testing & docs

- Extend semantic grounding from fin_c sub-terms to arbitrary reach calls
  (GT automaton for "reach T from S avoiding B" with β/τ obligations).
- More multi-level round-trips + size/depth metrics vs paper bounds (the
  DAG-vs-tree table in STATUS is the seed of the empirical argument).
- Finite-word variant (weak next in wsolid, construction-ref §10) — stretch.
- Counter-free verification for external HOA inputs (GAP IsAperiodic) — stretch.

## P4 — heuristic/kr mixin via suffix-formula injection (LOW PRIO, deferred)

Revisit only once the main census-wall path (P0 folds + P1 acceptance
dispatch) is stable. The idea: hand a hard component to a heuristic that
returns a formula φ_q labeling a state q of the original aut, then splice φ_q
into the kr reconstruction at the precise time points where the construction
"enters" q (config c with `state_of(c)=π(c)=q`; the config↔state map is the
traceability bridge — `state_of`/`state_to_config` already exist). Cleanest
realization: STUB q to terminal-accepting (its sub-automaton reduces to True,
the cascade handles the trivial residual) and conjoin φ_q once at the
`reach_strong(c,…)` arrival, UNDER the arriving X.

Conclusions from the 2026-06-13 exploration (what kinds of φ / side effects
work, and why — keep these; the exploratory code was reverted):

- The augmented language is `L(A) ∩ L(G(at_q → φ))`, `at_q` a deterministic
  state predicate. Always ω-regular; the question is whether kr can inject φ
  WITHOUT paying an exponential.
- kr has NO localized "language-from-q" subterm Ψ_q — it characterises
  acceptance globally (Muller DNF over i.o. config sets + reach/Fin). So
  "AND φ on top of what kr asserts at q" is well-defined as a LOCAL edit only
  where q's contribution collapses to one point: a terminal stub (Ψ_q=True)
  or a single transient (Fin) arrival. (Contrast: compositional
  state-elimination / the buchi2ltl backward labeling DO have L(q), so their
  `scc_fragments` splice is trivial — `buchi2ltl/reconstruction.py`.)
- SOUND + cheap to inject locally  ⟺  φ is ACCEPTANCE-NEUTRAL at q:
  * safety/invariant φ (small deterministic monitor; the extreme case is
    G(inv), a 1-state monitor) — does not perturb the Muller condition; only
    the loop encoding must be un-fused to expose the per-visit hook
    `G(at_q_letter → φ ∧ …)` (a size cost, NO exponential);
  * terminal stub — q stops participating in acceptance, so φ is asserted
    once at the single arrival.
- NOT a free lunch for LIVENESS φ at a RECURRENT q: the correct meaning
  `G(at_q → φ)` changes the acceptance question, forcing the product A×B_φ and
  re-derivation of the Muller condition. The exponential reappears in the
  product's recurrent structure — kr pays for acceptance, and renaming the
  liveness as "a formula on q" does not move it out of the Muller machinery.

Concrete from the attempt (reverted, recorded here): per-state downstream
invariants are computable by live-edge constancy on the aut (skip sinks =
states not co-reachable to an accepting SCC), validated against a semantic
oracle (`L` restarted at q ⊨ G(inv_q)); `a & XGb` is caught at the post-a
state (init has none). The GLOBAL front-end peel (project a forced literal
out of the input aut, run the chain, recombine `& G(inv)`; `Fa & Gb` 12→2
census, equiv=True) was DROPPED on purpose — it is the "poor man's" degenerate
case (init-config invariant only) and not the direction we want; per-config
injection above subsumes it when/if pursued.
