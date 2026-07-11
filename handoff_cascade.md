# Handoff — cascade ladder experiments (K-series)

Bootstrap to current state + todos. NOT history (git + `docs/HISTORY.md` hold
that). Mission: `research_notes/bls_cascade_experiments.md` (K-E0..E7). Ledger:
`research_notes/bls_cascade_report.md` (findings K-F1..). Draft: `bls_cascade.md`.

## Where things stand (current)

- **K-E0 COMPLETE** (gate). Steps 1–3 refuted the draft's floor model →
  PAPER-EDIT landed (K-F2); C.3 witness is now `G(a→F b)`, floor witness is a
  C.5 fallback / C.4 refutation instance. Steps 3/4/5/6 green (K-F1,F3–F6).
- **K-E1 DONE** (K-F7): all 1164 C3-`UNDECIDED` census layers decide under (C)
  at k≤3 (914/156/94 at k=0/1/2), 0 conflict, 0 budget. 842 are moving (R≥2).
- **K-E7 census map DONE** (K-F8): only absorption (aperiodic) + group
  (non-aperiodic) mechanisms; 0 verdict-splitting `other` → no third mechanism.
- **K-E2 DONE** (K-F9): Prop C.19 transfer specimen
  `(GF(a∧X((!a&!b)U a))) ∧ (G(c→F d))` → moving terminal layer `{21,24}` with
  verified genuine (C)-conflicts at k=0,1 (ALG-7: member toggles + non-conjugate)
  = first moving-layer floor inhabitant. k=2,3 BUDGET (tooling).

## Machinery (all under `tests/cascade/`)

- `config_machine.py` — ALG-1/2/5/6: `build_cone`, `entry_stems`, `closure_at`,
  `decide` (retains per-base `closures` + `entryst`), `find_c_conflict`
  (early-exit BFS + ALG-4 loop-word reconstruction), saturation helpers.
- `sandwich.py` — K-E7: `two_sided_ideals`/J-order, `scan` (absorption/group/
  other + verdict-`splits`), `scan_layer`.
- Probes: `k_e0*.py` (gate), `k_e0_sat.py` (saturation), `k_e7_controls.py`,
  `k_e7_triage.py`, `k_e1_sweep.py`, `k_e2_transfer.py`, `k_e3_sweep.py` (WIP).
- Census: `tests/cascade/logs/census_flat_canon.jsonl` (regen:
  `python3 -m tests.sos2ltl.census_build genaut/corpus/flat_canon/sos --out …`).
  Corpus: `genaut/corpus/flat_canon/sos` (4248 langs). Logs gitignored (regen).

## Key facts / gotchas

- Build `𝓘` from LTL: `invariant_of_language(Language.of(spot.translate(f)))`.
  Load `.sos`: `sosl.sos.load_invariant`. Import an `aut2ltl.sos2ltl.*` module
  BEFORE `sosl.*` (its init puts sosl on sys.path).
- Verdict oracle: `Val(s,d) = (M(s,π(d)),π(d)) ∈ P`. `π` = `inv.idempotent_power`.
- Frozen layer ⟹ (C)@k = (B)@(k+1) (Lemma C.10); class coord absent.
- Covered-set closure explodes on frozen / high-|Σ_λ| layers → use
  `find_c_conflict` (early-exit) to detect conflicts, not full `decide`.
- **NEVER stringify LTL / stay DAG** (K-E4 emitter constraint). DG synth's
  `to_spot` blows up — do not call it.

## Todo (next)

- **K-E3** (WIP): one-sidedness stats + Cor C.9 count. Prediction: C.9 gating
  stratum = 0 (prefix-independence forces frozen final layer). Run
  `k_e3_sweep.py`, record K-F10.
- **K-E4**: config-normal-form emitter (Prop C.7 / Cor C.8), DAG-only, never
  stringify; conformance-gate on `G(a→F b)` then K-E1-decided layers.
- **K-E5**: DG vs manufactured cascade on the 258 (A)-fallback stratum
  (needs `aut2ltl/bls` bridge). Independent.
- **K-E6**: floor witness pendency machine + prophetic `A_S` cross-check.
- Gate before landing: `python3 -m survey --folder samples/validation` SUCCESS.
- Commit as you go (terse `git commit -F -`, several files ok, no need to ask).
