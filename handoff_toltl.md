# Handoff — toltl thread (main paper, SoS → LTL)

Paper: `research_notes/sos_toltl.md`. Spec: `sos_toltl_spec.md` (head
= done/todo map). Ledger: `sos_toltl_report.md`. Corpus:
`genaut/corpus/flat_canon` — **6 222 languages (3 738 LTL / 2 484
non-LTL), Wagner ceiling ω³/ω⁴**. Tracked data: `reference/census/`
(reports cite tracked files + regen commands only, never `logs/`).

## State

- **§6 "the cascade import" is in the paper** (slim: the (C) rung, the
  floor example with no completeness claimed, the decomposition
  fallback); old §§6–10 renumbered §§7–11; [BLS22]/[Cas26] in the
  references. The companion note `bls_cascade.md` holds all proofs and
  everything that does not transition.
- **Every census number in the report and the paper is stale** — the
  corpus moved under them (report bench still says 3 938). Policy,
  absolute: stale data is EVICTED, not annotated — no "on the old cut"
  asides; a number traces to the current corpus through a tracked
  artifact + regen command, or it leaves the document. Known flips on
  the new frame (from `reference/cascade/`, ledger K-F7..K-F12):
  Table 3's "(B) failures: 0" is false; the `2state2ap` shape is
  in-frame and populated (type specimen
  `2state2ap1acc_parity_3772037665`); prefix-independent stratum is
  1 104; the (A)-fallback stratum count is unknown pending recount.
- Engine sound catalogue-wide on the old cut; `python3 -m
  tests.sos2ltl.e0_gate` (fixtures, corpus-independent) is the landing
  gate.
- Deferred marks in the paper awaiting the drops below: ⟨TBD: §9
  re-based⟩ in §5.1 and §8; §6's stem-half ledger ⟨TBD⟩.

## Todo — Engineering (in order; spec head has the details)

0. **Simplify propositional tier — LANDED, recipe effect UNVERIFIED
   (next action).** `ltl/simplify/context_pass.py` + algorithm.md
   ("pass 1" propositional tier): a purely-propositional And/Or
   sibling now asserts as a whole into the context, and a
   propositional node consumes the context's care-set via
   `prop_cofactor` (strictly-smaller acceptance = termination). This
   targets the engine's NNF-guard folding gap —
   `(a∧b) ∨ ((¬a∨¬b) ∧ XF(a∧b))` should collapse to `F(a∧b)` (guard
   dies under Shannon, then pass-4 pair-fold). Package tests green:
   `tests/probes/ltl/simplify/test_context_pass.py` CLEAN,
   `test_random_equiv.py` 500/500 EQUIVALENT, 21.9% avg shrink, zero
   growth. **NOT yet confirmed** that it collapses the target
   specimens at the recipe level: last main run
   (`survey --use sos2ltl_pairs --logs …`, CSV
   `logs/rerun-pairs/validation/`) wrote a PARTIAL CSV (diff saw only
   45 common rows) and size movers barely moved (recurrence_l10 95→94)
   — re-run the full main, re-diff vs
   `results/reference/validation/default.csv`, and eyeball
   `guarantee.ltl:11` (`F(a&b)`, was 33ch/dag10) +
   `obligation.ltl:4` (`Fa|Gb`, was 53ch/dag13). Specimens picked by
   joining the two CSVs on `source` for daisy/daisy+strength2 rows
   over the 20-char bar.

1. **E11 — the decomposition fallback: IMPLEMENTED; operator-memo
   rewrite landed, pendency stall open.**
   `aut2ltl/sos2ltl/cascade/` (algorithm.md there), wired below the
   engine via `engine.LayerFallback`, exposed as the registered recipe
   **`sos2ltl_casc`** (hi simplifier at the recipe boundary only).
   Stem half: Prop 4.14 with the reach family's `τ` as the insertion
   point (no standalone LTLf pass — deviation from spec wording,
   user-sanctioned). Loop half: product `D × confined-walk` acceptor →
   `decompose_aut` → bls member ladder. The reach-family memos are now
   **skeleton-keyed templates** (β/τ factored out into placeholder
   APs, plugged by memoized substitution — `bls/operators/algorithm.md`
   "Skeleton templates"; the fin uncond-memo key-shadowing bug is also
   fixed). E0 gate green; `fin_ground` EQUIVALENT on validation
   fixtures; distinct reach expansions drop ~5× on the 2-level
   fixtures (guarantee_l12: 174→36; probe
   `tests/probes/bls/memo_stats.py`, run under `KR_SIMP_OPTS=basics`).
   Floor witness ([2,2,2] pendency): construction 0.98 s, DAG
   3 125→2 680, flat 2.5·10¹¹→7.8·10⁹ — the old probe's 15 s blowout
   was its INLINE Spot equivalence call, now removed
   (`e11_pendency` is construction-only; any label→automaton step goes
   behind `spotrun`, never inline in a probe).
   `survey --folder samples/validation --use sos2ltl_casc`: SUCCESS —
   83 inputs, 70 LTL + 3 not-LTL, 73 TRUE / 0 FAIL, 10 TIMEOUT (all in
   the GF-conjunction recurrence family, e.g. `GFa & GFb`;
   default-recipe parity on those lines unverified).
   **Pair decomposition: SoS level, IMPLEMENTED — piece-quality
   problem open.** `aut2ltl/sos2ltl/pairsplit/` (algorithm.md):
   saturation atoms over one table (`sosl.sos.calculus`), candidate
   sides = ≥2 atoms, least atoms wins (P̄ = free flip, outer ¬),
   per-piece `reduce` + `remove_free_aps`; seam in
   `sos2ltl/translator.py::sos2ltl_pairs` (engine-whole gate → split
   → cascade assembly fallback); recipe **`sos2ltl_pairs`**; anatomy
   probe `python3 -m tests.sos2ltl.pairsplit_probe '<ltl>'`.
   Current wiring (user-set): pieces run engine-then-dg, NO cascade
   delegate; a split label above the conformance oracle's flatten
   gate DECLINES and the whole falls back to the cascade assembly —
   decline-and-fallback, no per-piece acceptor for now ("complete D
   later"). Main on that wiring: 73 TRUE / 0 FAIL / 10 TIMEOUT —
   casc-equal. Diffed against the default-portfolio reference
   (`survey --folder samples/validation --use sos2ltl_pairs --logs
   logs/…` then `survey.diff.results
   results/reference/validation/default.csv logs/…/survey_*.csv`):
   reference is fully green (83 TRUE, 10 s, total DAG 458); ours is
   CONSISTENT (0 FAIL, 0 clash) but 10 no-answers, DAG ×2, tree
   ×6.5, build ×20 — e.g. recurrence_l10: daisy DAG 7 vs our 95.
   The gap to the automata baseline is the actual problem statement;
   the split's verified gains need engine-shaped pieces.
   **Quality bar (user-set): on the validation smalls, any printed
   label above ~20 characters is a defect**; the automata-level
   baselines met it (e.g. `G(Fa & Fb)`) because pieces were FEW (one
   per acceptance reason, overlapping covers) and carried
   presentations — the SoS finest atoms over-fragment (8 vs 2 on
   `GFa & GFb`). Paper §5.3b (NEW) now states the lever inventory;
   coarse/overlapping covers are the implementation lead once theory
   adjudicates. Then: corpus sweep (`genaut/corpus/flat_canon/det`,
   background), delegate firing stats, stem ledger vs DG. **Open problem:** loop
   labels are still too large flat (7.8·10⁹ on the floor witness), so
   the Spot equivalence oracle cannot consume them raw; the
   flat-column risk is confirmed, conformance story on the loop
   branch pending.
2. **Census regeneration on the current corpus**: E1, E2, E7, E10,
   frontier counts; report bench + every finding re-based, flips
   flagged `PAPER-EDIT:`. Includes wiring the (C) decider into the
   step-4 read-off (machinery in `tests/cascade/config_machine.py`;
   emitter `tests/cascade/emit.py`, conformance-gated on the worked
   witness) so the coverage tables speak the paper's widened branch.
3. **Full E4 — run it, measured**: DAG + printed size, engine vs DG,
   portfolio as internal yardstick, over the current corpus — the
   §7/§9 deliverable. E5 rides along once C6 lands.
4. The spec's item-4 queue (E9 candidates, H7, E3, E8, E10 graded
   re-run, C6+E5, H8).

## Todo — Theory

1. On the census drop: fix every number in the paper — §9 wholesale
   (bench, Table 3 + discussion, percentages), §8's frontier text,
   the hunt sentences (§11; the `2state2ap` hunts close against
   K-F12) — and resolve the ⟨TBD: §9 re-based⟩ markers.
2. On the E11 drop: resolve §6's stem-half ⟨TBD⟩ (the ledger picks
   step 3(b)'s inner extractor); adjudicate any conformance
   stop-the-line.
3. Open math, unblocked by nothing: §5.1's
   width-bound-by-definiteness-degree ⟨TBD⟩; §2.3's arena bound
   (gated on full E4).
4. **Integrate §5.3b (NEW)** — the decomposition-levers section
   (atoms as the finest union split, the complement trick for the
   union form, saturated covers with overlaps): polish, renumber,
   resolve its ⟨TBD⟩s (specimen table + atom partition; atom counts
   on the census). Decomposition is under-emphasized in the paper —
   user marks it as a KEY. The open math behind the covers: which
   coarse/overlapping covers keep pieces nameable and extractable
   (the automata baselines suggest one-piece-per-acceptance-reason);
   the pieces' presentations (the Cayley/Muller reference acceptor —
   deferred, "complete D later"; library gap: the ω-semigroup →
   Muller automaton source, Perrin–Pin). The exact cover-SELECTION
   optimizer (interval → smallest-algebra member via the bounded
   quotient test / `hull_π`) is the `sos_giventhat` operation — that
   link is for giventhat to make, NOT us: giventhat is downstream of
   this paper in the publication DAG (it cites us [SωSX26]). §5.3b
   states only the levers + the liberty and stops there.

## Machinery / conventions (user-set; keep)

- Pipeline `aut2ltl/sos2ltl/` (cayley, anchoring, windows, readoffs,
  witness, dg, engine); probes `tests/sos2ltl/`; census records
  `python3 -m tests.sos2ltl.census_build genaut/corpus/flat_canon/sos
  --out …`; cluster recipe `tests/cascade/README.md`, contract
  `cluster/README.md` (60 s/command; TIMEOUT/BUDGET are data).
- Loading/serialization via `sosl.sos.build` / `sosl.sos.io` /
  `aut2ltl.ltl.twa` — no raw Spot or hand-parsing, probes included.
- Runs go through `./aut2ltl.sh` (deps env: GAP, Spot, PYTHONPATH).
  `survey` self-times per example — never wrap it in a shell timeout;
  background it and wait for completion. Formulas are DAG-only: sizes
  via `aut2ltl.ltl.metrics`, display via `printers.format_gated`.
- Simplifier policy (user-set): own-rules freely; Spot's hi simplifier
  only at critical junctures (the recipe boundary — `Simplify(x,
  "hi")`); cascade hot loops run `KR_SIMP_OPTS=basics` (the default
  hybrid stalls >15 s already on 3-level cascades).
- Roles: theory holds the paper lock, reads `papers/`; engineering
  fills the report (current-state contract). Cite only what was read.
  The paper is science only — no tool names outside §9's oracle
  sentence.
- Aperiodicity read-off consumed from
  `sosl/sosl/sos/classify/aperiodic/`, never duplicated.
- Library gaps: Thérien–Weiss JPAA 35 (1985); an ω-word
  locally-testable source.
- Scope rule: strata stay operational here; variety-alignment theorems
  belong to the classification thread.
