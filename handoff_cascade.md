# Handoff — cascade ladder experiments (K-series)

Bootstrap to current state + todos. NOT history (git + `docs/HISTORY.md` hold
that). Mission: `research_notes/bls_cascade_spec.md` (K-E0..E7). Ledger:
`research_notes/bls_cascade_report.md` (findings K-F1..). Draft: `bls_cascade.md`.

## Where things stand (current, 2026-07-11 evening)

- **K-E0 COMPLETE** (gate). Steps 1–3 refuted the draft's floor model →
  PAPER-EDIT landed (K-F2); C.3 witness is now `G(a→F b)`, floor witness is a
  C.5 fallback / C.4 refutation instance. Steps 3/4/5/6 green (K-F1,F3–F6).
- **PAPER: K-F7..K-F11 integrated** into `bls_cascade.md` (commit 9bd764dd9)
  — but with the OLD 4248-cut numbers. **The corpus was extended to 6222**
  (campaign +1000 primals, Wagner ω³/ω⁴; late pair
  `3state1ap2acc_parity_0009241386589983080592`(+`_c`) folded 07-11 — benign:
  not pfxind, no undecided layers, frozen final layers). All K-F7/F8/F10
  numbers are being re-measured on the extended frame; the draft/ledger
  numbers are STALE until that pass lands.
- **K-E1 PASS 1 DONE on the cluster** (`20260711-190325-k_e1`, 500 jobs,
  60 s/command, 17 min): 6610/8786 undecided layers decide, **all at k≤2**
  (6105/346/159), 0 verdict-splitting `other`; 1642 languages ok, **472
  TIMEOUT** (2176 layers) = the heavy stratum. No CONFLICT row can appear in
  pass 1 (`sweep_layer` needs 4 full decides > 60 s) — **every potential
  conflict sits in the timeout stratum.** Data + provenance committed:
  `reference/cascade/k_series.md` (+ `k_e1_cluster.csv`).
- **K-E1 PASS 2 DONE** (`20260711-203139-k_e1v2`, one --resume): of the
  2176 heavy layers, **1021 genuine (C)@0-conflicts (ALG-7 inline, every
  one genuine): 806 aperiodic / 215 group**; 625 CLEAN; 530 BUDGET. Data:
  `reference/cascade/k_e1v_conflicts_k0.csv`. (Reap tallies count
  `k_e1_verify`'s exit-2 BUDGET rows as `fail` — they are data.)
- **K-E1 k=1 PERSISTENCE PASS DONE** (`20260711-210851-k_e1w1`, one
  --resume): of the 1021, **263 conflict again at k=1 — all genuine, 246
  aperiodic**; 118 CLEAN (ladder rescues); 640 BUDGET (cone growth
  saturates the 10⁶-state budget). Data:
  `reference/cascade/k_e1w_conflicts_k1.csv`.
- ⚠ **K-F12 AT SCALE**: the aperiodic floor-track stratum is **≥246
  in-frame layers genuinely failing (C) at widths 0 and 1** (type specimen
  `2state2ap1acc_parity_3772037665`, Wagner (ω³,σ), frozen singletons —
  `reference/cascade/kf12_specimen_alg7.txt`). The "floor empty on the
  census frame" claim (K-F7/K-F9, draft C.2/C.19/C.7) FALLS — PAPER-EDIT
  is now unblocked, all numbers final in `reference/cascade/k_series.md`.
  Every-width failure (full C.12′ floor membership) still needs the
  structural absorption argument or a k=2 pass (640 budget-open layers).
- **K-E3 RERUN DONE** (extended): 5050 (C)-decided final layers at k≤3;
  one-sidedness over the 74 ≥2-class-family layers: 16 up / 16 down /
  28 both / 14 neither — still balanced; up=down is forced by complement
  closure of the catalogue (complement swaps the closure direction) — say so
  in the draft. Cor C.9 gating stratum: 0. Pfxind scan: **1104**
  prefix-independent (was 132), **0** with a non-frozen final layer.
- **K-E2 (K-F9) / K-E4 (K-F11)** unchanged: transfer specimen verified;
  emitter conformance-gated on `G(a→F b)`; K-E4 production wiring pending.
- **Data discipline**: reports cite only git-tracked data —
  **`reference/cascade/` is committed** (k_e1_cluster.csv, k_e3.csv,
  k_e3_pfxind.txt, kf12_specimen_alg7.txt, `k_series.md` with provenance +
  regen commands); extend it with pass-2 results, never cite `logs/`.
  READMEs added to `tests/cascade/` + `tests/sos2ltl/` (the line-json census
  format is probe-local, may be retired — depend on nothing outside those
  folders). Timeout convention: 15 s/example local, 60 s/command cluster;
  TIMEOUT is data.

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
  Corpus: `genaut/corpus/flat_canon/sos` (**6222** langs, 3738 LTL / 2484
  non-LTL). Logs gitignored (regen); paper-grade copies go to
  `reference/cascade/` (tracked).

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

1. **Recover or resubmit K-E1 pass 2** (see Where-things-stand: reap the
   lost `*k_e1v*` run, or resubmit `cmds_k_e1_verify.txt` as `k_e1v2`);
   reap per `cluster/README.md`. Its results.csv rows carry
   `status ∈ CONFLICT|CLEAN|BUDGET` and a `genuine` bit (ALG-7 inline) —
   tally conflicts by `aperiodic`; genuine aperiodic rows = in-frame floor
   inhabitants (K-F12 stratum); non-aperiodic = the group escape.
2. Append pass-2 CSV + updated tables to `reference/cascade/` (extend
   `k_series.md`), then rewrite `bls_cascade_report.md` K-F7/F8/F10/F12
   (and K-F9's subsumption note) against the tracked files, and sync
   `bls_cascade.md` — sites: C.2 remark ~l.240 (coverage + conflicts), after
   Cor C.8 ~l.380 (16/16/28/14, note the complement-closure symmetry),
   Cor C.9 ~l.424 (1104/1104), C.4 ~l.720+769 (mechanism map + "floor empty
   on the census frame" FALLS — K-F12), C.19 closing bold ~l.769, C.7 §8
   bullet ~l.1003; `bls_cascade_spec.md` (stale "372"/"1164" input
   descriptions); this handoff.
3. **K-E4 engine integration**: wire the emitter into
   `aut2ltl/sos2ltl/engine.py`, full conformance sweep over K-E1-decided
   layers + DG size ledger.
4. **K-E5**: DG vs manufactured cascade on the (A)-fallback stratum (recount
   the 258 on the extended corpus first; needs `aut2ltl/bls` bridge).
5. **K-E6**: floor witness pendency machine + prophetic `A_S` cross-check.
- Gate before landing code: `python3 -m survey --folder samples/validation`
  SUCCESS.
- Commit as you go (terse `git commit -F -`, several files ok, no need to ask).
