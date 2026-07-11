# Handoff — cascade thread (companion note [Cas26]) — PARKED

The note is standalone: `research_notes/bls_cascade.md`, cited from
the main paper as [Cas26]. The main paper's §6 imports the slim core
(the (C) rung, the floor example, the decomposition fallback);
everything else — completeness apparatus and its refutation, transfer,
corollary tier (C.8/C.9/C.9′), mechanism cartography, the K-series
record — stays here and does not transition. Spec:
`bls_cascade_spec.md`; ledger: `bls_cascade_report.md`; data:
`reference/cascade/` (all on the current 6 222-language corpus).

## State

- Draft current: extended-corpus numbers, Theorem C.9′, Theorem C.12″,
  the K-F12 floor reversal; no stale-cut residue.
- **Migrated to the toltl thread**: the decomposition experiments
  (were K-E5/K-E6 here) → `sos_toltl_spec.md` **E11**; the (C)-decider
  + config-emitter production wiring (was K-E4's remainder) → toltl
  census-regeneration item. This thread runs nothing the main paper
  needs.

## Todo — parked (reopen only if the floor cartography becomes a paper)

1. K-E8(a) padded-block certificate scan over the 246 aperiodic
   persisters (Theorem C.12″; table-only, type specimen = positive
   control) — promotes width-≤1 conflicts to every-width floor
   membership in the note's K-F12 claim.
2. K-E8(b) (B̃)-at-rescue-width probe on the moving rescued layers —
   the non-degenerate C.5(i) strictness witness.
3. k=2 pass on the 640 budget-open layers (`k_e1_verify <id> <layer> 2`,
   sharded, raised budget).
4. Theory follow-ups: every-width status of non-certifying persisters;
   the general lift of Cor C.9; C.19's full product bookkeeping.

## Machinery (all under `tests/cascade/`, see its README)

- `config_machine.py` (ALG-1/2/5/6, `find_c_conflict`), `sandwich.py`
  (K-E7 scan), `emit.py` (K-E4 emitter, DAG-only), probes `k_e0*`,
  `k_e1_*`, `k_e2_transfer`, `k_e3_*`, `k_e7_*`.
- Gotchas: import an `aut2ltl.sos2ltl.*` module before `sosl.*`;
  verdict oracle `Val(s,d) = (M(s,π(d)),π(d)) ∈ P`; frozen layer ⟹
  (C)@k = (B)@(k+1) (Lemma C.10); conflicts are cheap, proving (C)
  holds is expensive; NEVER stringify LTL / stay DAG; 15 s local /
  60 s cluster, TIMEOUT and BUDGET are data.
