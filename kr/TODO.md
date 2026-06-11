# kr/ TODO

Forward-looking work items only. Current state: `kr/STATUS.md`. History: `git log`.
Construction reference: `paper/automata-to-ltl-construction.md`; ground truth:
`paper/Automata2LTL.txt` (Sec 4.2 + Table 1 + Formulas 3/4/5 ≈ lines 440–1040).

## HANDOFF — where debugging stands (written at end of 2026-06-11 session)

**What just happened:** All five operators were rewritten to the LITERAL paper
forms (see STATUS "Operators"). The former approximations (from-S letter
enumeration, first-step recursion, bespoke weak forms, wrong weak base) were
the 2L breakers — each was found by semantic grounding with witness words, and
each fix was verified against `paper/Automata2LTL.txt` directly.

**Examples used and why they fail/pass:**
- `GFa` (1L, 2 states, ι==C) — the minimal Fin-postponement canary. GROUNDED OK.
- `G(a -> X b)` (2L [2,2], safety; states: (1,1) init, (1,2) obligation, (2,1)
  sink) — first 2L target. Diagnosis chain that fixed it: (i) `r_to((1,1)→(2,1))`
  was `false` because no letter from S enters top 2 (entry fires only from
  lower config (2)) → combined-letter enumeration over ALL configs + lower-level
  prefix reach (solid⁺/Formula 5 literal); (ii) the remaining `r_with` failure
  (witness `a&b; !a&b; !a&b; cycle{a&b}`) was in the leave-avoid conjuncts —
  cursor-1 reaches with a REAL bad config exercising the weak cluster for the
  first time (1L never passes B≠None at top) → literal wreach dual + wsolid⁺.
  Now: ALL SUB-TERMS GROUNDED OK.
- Probe script for that diagnosis: `kr/testing/probe_2l_rwith.py` (drills into
  solid⁺ last-step disjuncts and checks each conjunct against the witness word).

**Why it "fails" now — the current blocker is SIZE, not semantics:**
`G(a->Xb)`'s assembled formula is ~3.2 MB. Construction terminates; Spot
translation for equivalence checking is what stalls. USE 10s TIMEOUTS and treat
TIMEOUT as a result. Root cause: operators round-trip strings (`_str_f` → parse
→ `simplify()`) between every call — no DAG sharing, every conjunct physically
copies its nested tail, and re-simplification runs on megastrings.

**Exact next steps (P0-perf, do these before more semantics):**
1. Keep `spot.formula` objects end-to-end through the operator recursion:
   operators accept/return formula objects; convert to str ONLY at the very
   top (reconstruct) and in traces. `simplify()` at most once per operator
   return — never inside `_str_f` per conversion.
2. Add lru/memo to `reach_weak` (it has none; reach_strong's lru exists) and
   key memos on formula object identity/hash instead of strings.
3. Re-run: `trace_fin_semantics` GFa + "G(a -> X b)" (must stay ALL GROUNDED OK),
   `test_kr_r4_audit.py` (audit may need its body-grep patterns updated to the
   new literal function shapes — the import of `_dashed_change_weak` was already
   removed), then `survey_mp_cascade.py` — expect G(a->Xb) to flip True and
   watch the rest of the ladder: `a U b`, `F(a&Xb)`, `Fa|Gb`, `Fa&Gb`, `Ga|Fb`,
   `Ga|Gb`. Next semantic target after that: `G(p -> (q U r))` (user request),
   then 3L (`Xa`).
4. If size is still prohibitive after sharing: simplify aggressively only at
   low levels (cheap), prune vacuous conjuncts (Enter(b)=∅, unreachable pre),
   and consider per-subformula equivalence-based interning.

## P1 — coverage

- Full acceptance dispatch per construction-ref §9.3 (looping-Büchi/coBüchi direct
  Σ₁/Π₁ forms, Büchi/coBüchi Π₂/Σ₂ forms, weak Δ₁ end_in(G)) instead of always going
  through the Muller DNF; keeps outputs in the matching hierarchy class.
- Muller lift exactness for n>2 levels (h⁻¹ powerset lift with SCC pruning + dedup).
- Trivial (size-1) level collapse to reduce effective depth.
- Remove/make-dynamic the >3L dev guard once multi-level is correct.

## P2 — feasibility

- Simplify at every construction step (inside R*/Fin builders), not only post-hoc.
- Systematic early-outs (Enter(t)=∅ ⇒ dashed false; Stay(s)=∅ ⇒ solid τ/false).
- Larger |AP| (on-demand letters or BDD guards instead of explicit 2^k).
- Hierarchy class tagging of outputs (Σᵢ/Πᵢ/Δᵢ per Lemma 5).

## P3 — testing & docs

- Extend semantic grounding from fin_c sub-terms to arbitrary reach calls
  (GT automaton for "reach T from S avoiding B" with β/τ obligations — needed for
  the 2L ladder work above).
- Word-sampling validator (ultimately-periodic u·v^ω: automaton acceptance ⇔ formula,
  per construction-ref pitfall #10).
- More multi-level round-trips + size/depth metrics vs paper bounds.
- Finite-word variant (weak next in wsolid, construction-ref §10) — stretch.
- Counter-free verification for external HOA inputs (GAP IsAperiodic) — stretch.
