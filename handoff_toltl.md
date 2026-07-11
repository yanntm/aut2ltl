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
  tests.sos2ltl.e0_gate` (fixtures, corpus-independent) stays the
  landing gate, with `python3 -m survey --folder samples/validation`
  SUCCESS before any code lands.
- Deferred marks in the paper awaiting the drops below: ⟨TBD: §9
  re-based⟩ in §5.1 and §8; §6's stem-half ledger ⟨TBD⟩.

## Todo — Engineering (in order; spec head has the details)

1. **E11 — the decomposition fallback: IMPLEMENTED, measuring now.**
   `aut2ltl/sos2ltl/cascade/` (algorithm.md there), wired below the
   engine via `engine.LayerFallback`, exposed as the registered recipe
   **`sos2ltl_casc`** (hi simplifier at the recipe boundary only).
   Stem half: Prop 4.14 with the reach family's `τ` as the insertion
   point (no standalone LTLf pass — deviation from spec wording,
   user-sanctioned). Loop half: product `D × confined-walk` acceptor →
   `decompose_aut` → bls member ladder. E0 gate green; default-recipe
   validation green. **In flight:** `survey --folder
   samples/validation --use sos2ltl_casc` (background). Next: corpus
   sweep (`genaut/corpus/flat_canon/det`, same recipe, background),
   delegate firing stats, stem ledger vs DG. **Open problem:** loop
   labels are stupid large (floor witness: DAG 3 125, flat ≈ 2.5·10¹¹
   — at parity with the bare bls floor on the same language), so the
   Spot equivalence oracle cannot consume them raw; the flat-column
   risk is confirmed, conformance story on the loop branch pending.
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
