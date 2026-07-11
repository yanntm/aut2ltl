# The decomposition fallback (paper §6, spec E11)

Where the walk+window engine's stratum ends, the layer — never the
language — descends to a Krohn–Rhodes cascade. Two failure modes, two
halves, one machinery: the `aut2ltl.bls` engine (the SgpDec holonomy
bridge, the [BLS22] reach family, `Fin(C)`), consumed *scoped per
layer*. The peelers of the automaton portfolio already floor on this
engine for whole languages; here it serves as the per-layer delegate
below the sos2ltl engine.

- **Stem half** — condition (A) fails at every affordable width:
  Prop 4.14's scoped fallback with the inner extractor swapped from DG
  to the holonomy cascade of the totalized within-layer machine.
- **Loop half** — condition (C) (and with it (B)) fails at every
  affordable width on a final-candidate layer, or (A) fails on one:
  the acceptance term `W(R)` is read off a KR decomposition of the
  *source deterministic acceptor* restricted to the layer's tails —
  the one branch of the whole extraction that consults a presentation
  (Lemma 4.2(ii): no machine derived from the invariant carries its
  acceptance on recurring configurations). Its only correctness
  authority is the conformance gate.

## Inputs

- `Cayley` (C1) and the layer's `LayerAnchoring` (C2): the classes of
  `R`, the per-class letter sets `L(c)/M(c)/E(c)/A(c)`, `width` (None
  = (A) FAIL).
- The engine's class-memoized children labels `Final(c·a)` for every
  exit target — the delegate emits *into* the same R-order descent,
  one label per entry class, memoized like any brick.
- Loop half only: the deterministic acceptor `D` of the language
  (`Language.det_parity_sbacc()` — the same normalization the gap
  bridge itself performs), and per class of `R` a witness stem `u_c`
  landing in `c` (any readable walk; only the class matters).

## The shared seam: scoped machine → reset cascade

Both halves reduce their layer to a small deterministic transformation
machine and hand it to the existing bridge:

    machine (states, per-letter images) ──decompose──▶ Cascade ──▶ CascadeHolder

- Stem half: `decompose_gens` on the totalized machine's per-letter
  transformation images (no Spot normalization — the machine is ours).
- Loop half: `decompose_aut` on the scoped Spot acceptor (the bridge's
  own normalization applies).

Recorded at this seam, per layer: cascade height and per-level state
counts — ledger columns (paper §6 expects far below `2^{|R|}`).

## Stem half ((A) fails at every width — Prop 4.14, extractor swapped)

1. **Totalize.** The within-layer machine `A_R`: states = classes of
   `R` plus an absorbing sink `⊥`; letter `a` maps `c ↦ c·a` when
   `c·a ∈ R`, everything else (exits, unreadable letters) to `⊥`;
   `⊥·a = ⊥`. Counter-free by Prop 4.11, so the holonomy decomposition
   applies and yields a *reset* cascade — every level 1-anchored in
   the paper's own sense.

2. **Decompose** through the shared seam; `ι_R` is the cascade config
   covering the entry class `r` (`state_to_config`).

3. **Emit the exit disjunction.** For each class `c ∈ R` with
   `E(c) ≠ ∅`, the exit continuation

       θ_c  =  ⋁_{a ∈ E(c)} ( â ∧ X Final(c·a) )

   (guards through `guards.py`, children from the engine memo), and
   the per-class reach term

       ρ_c  =  ⋁_{C ∈ h⁻¹(c)}  reach_to(ι_R, C, θ_c)

   over the configs covering `c`. `reach_to(S, T, τ)` is the [BLS22]
   family's unconditional reach (`fin.py`'s form): "the run from `S`
   is at `T` at some position with the suffix satisfying `τ`". This
   *is* Prop 4.14's `⟨ψ_{r→c}; a; φ_{c·a}⟩`, insertion wrapper
   included: the family's continuation parameter `τ` is the insertion
   point, so `ψ_{r→c}` is never materialized as a standalone LTLf
   formula — the finite-word variant of [BLS22, Rem 2] (weak next
   inside `wsolid` only, strong `X` elsewhere) is exactly what
   evaluating the family against a continuation implements. Soundness
   of the disjunction needs no side condition: the totalized walk is
   deterministic and `⊥` absorbing, so being at a config covering
   `c ∈ R` means "not yet exited", and an exit letter firing there is
   the unique first exit — at most one disjunct can fire, Prop 4.14's
   proof verbatim. Memoization: the family's per-holder memos make the
   `ρ_c` a class-indexed DAG across the whole layer.

4. **Assemble.**

       Final(r)  =  ( SAFE(r) ∧ Ω(R, r) )  ∨  ⋁_{c ∈ R} ρ_c
       SAFE(r)   =  ¬ ⋁_{c ∈ R} ⋁_{C ∈ h⁻¹(c)} reach_to(ι_R, C, exit_c ∧ X⊤)

   with `exit_c = ⋁_{a ∈ E(c)} â`. *Preflight:* assert the layer is
   not a final candidate (no internal cycle a run can stay in) — then
   `Ω(R, r) = ⊥` and the `SAFE` arm drops entirely, leaving the exit
   disjunction alone. A failing layer that *is* final also needs the
   loop half for `Ω`: report it (`PAPER-EDIT` on §6) and combine.

5. **Gate and ledger.** Conformance-gate the assembled label (exact by
   construction, gated anyway). Ledger vs DG-on-`𝒜_R` on the same
   layers: DAG size, printed (flat) size, modal and until depth, wall
   time. The ledger picks step 3(b)'s inner extractor — §6's ⟨TBD⟩
   resolves either way.

## Loop half ((C) fails at every affordable width, or (A) fails final)

1. **Scope the acceptor.** For each `c ∈ R` run `D` on the witness
   stem `u_c`: state `q_c` (well-defined — `D` minimal deterministic,
   and `a⁻¹T_c = T_{c·a}` makes `c ↦ q_c` functional). The scoped
   acceptor: states `{q_c : c ∈ R}` with `D`'s own acceptance marks;
   within-layer transitions `q_c →^a q_{c·a}`; every exit letter to a
   rejecting absorbing sink. The scoped language only has to be exact
   on *confined* tails — the label is consumed as `W(R)` inside
   `STAY∞`'s confinement context, which masks the sink's verdict
   (and on the (A)-fails-final combination it serves as `Ω(R, r)`
   under `SAFE`, same masking).

2. **Decompose** through the shared seam (`decompose_aut`).

3. **Lift acceptance and encode.** Acceptance lifts to cascade
   configurations ([BLS22, Props 7–8] — the bls `config_graph`
   machinery), encoded per acceptance class as a Boolean combination
   of `Fin(C)`: Büchi `⋁ ¬Fin(C)`, co-Büchi `⋀ Fin(C)`, Muller the
   exact-set form — the existing bls member assembly, dispatched by
   the scoped acceptor's class. DAG-only throughout — never
   stringify. Expected on the corpus: gba is an Inf-conjunction and
   parity a Fin/Inf chain, so the lifted acceptance stays *linear in
   the number of configurations* (spec E11's size prediction); the
   Muller exact-set price never arises.

4. **Gate and ledger.** The conformance gate is the *only* correctness
   authority on this branch (it consults a presentation; exactness is
   not by construction). Any conformance failure is stop-the-line —
   theory adjudicates. Ledger as in the stem half but with no DG
   comparison column: DG on the tail algebra provably cannot shrink
   its input here (Lemma 5.2(ii)) — record that fact, not a race.

## Build order (worked instances gate each half)

1. The shared seam, exercised standalone.
2. Loop half, worked instance first: the floor witness's pendency
   machine — two states, "last non-`s` letter was an `a`", Büchi on
   the completion transition — must emit a label conformance-equal to
   `GF(a ∧ X(s U a))`. Then the residual-stratum inhabitants (the
   K-F12 conflict layers, `reference/cascade/`), each gated.
3. Stem half on the (A)-fallback stratum (recount first — that
   recount is E1-regeneration data), ledgered vs DG.

## References

[BLS22] Boker, Lehtinen, Sickert, FoSSaCS 2022 — construction digest
`aut2ltl/bls/paper/automata-to-ltl-construction.md`. [Cas26] the
companion note `research_notes/bls_cascade.md`. Paper sections cited
are `research_notes/sos_toltl.md` (§4.4 Prop 4.14, §5.4, §6).
