# Handoff — cascade ladder experiments (K-series)

Bootstrap to current state + todos. NOT history (git holds that). Mission:
`research_notes/bls_cascade_spec.md` (K-E0..E7). Ledger:
`research_notes/bls_cascade_report.md` (findings K-F1..K-F12). Draft:
`research_notes/bls_cascade.md`. All measurement data + regen commands:
`reference/cascade/k_series.md` (reports cite only these tracked files,
never `logs/`).

## Where things stand

- **Corpus**: `genaut/corpus/flat_canon/sos`, **6222** languages (3738 LTL /
  2484 non-LTL), Wagner ceiling ω³/ω⁴.
- **K-E0 gate COMPLETE** (K-F1..F6): decider validated five ways; C.3
  worked witness is `G(a→F b)`; floor witness is C.5's fallback instance;
  Conjectures C.12/C.17 refuted (Theorem C.12′), mechanism = zero
  absorption.
- **K-E1 COMPLETE on the extended corpus** (three cluster passes, data in
  `reference/cascade/`): of 8786 census-undecided layers, 6610 decide under
  (C), **all at k≤2**; of the 2176 heavy rest, **1021 genuine
  (C)@0-conflicts (806 aperiodic / 215 group)**, each ALG-7-verified; at
  k=1, **263 persist (246 aperiodic)**, 118 ladder-rescued, 640
  budget-open.
- **K-F12 — the floor is inhabited IN-FRAME, at scale**: ≥246 aperiodic
  layers genuinely fail (C) at widths 0 and 1. Type specimen
  `2state2ap1acc_parity_3772037665` (13 classes, Wagner (ω³,σ), frozen
  singleton layers, verdict-splitting zero absorption, three 𝒥-minimal
  classes). The draft edit HAS LANDED (floor reversal everywhere).
  Every-width membership is reduced to **Theorem C.12″**'s padded-block
  certificate — a table-only check, specced as **K-E8(a)**, unrun.
- **K-E7 mechanism map**: over everything decided, absorption + group only,
  **0 verdict-splitting `other`** — still no third mechanism.
- **K-E3 COMPLETE**: one-sidedness over the 74 ≥2-class families:
  16 up / 16 down / 28 both / 14 neither (the up/down tie is forced by
  complement closure of the catalogue). Cor C.9 gating stratum: **0**;
  prefix-independent languages: **1104, all with frozen final layers**.
- **K-E2 (K-F9)**: transfer specimen verified — moving-layer floor
  inhabitant beyond the frame. **K-E4 (K-F11)**: emitter conformance-gated
  on the worked witness; production wiring pending.
- **Paper state (2026-07-11)**: `bls_cascade.md` is CURRENT — extended
  corpus numbers throughout, floor reversal landed, plus two new
  theorems: **Theorem C.9′** (prefix-independence ⟹ frozen singleton
  terminal layers; unconditional, kernel-row proof) and **Theorem
  C.12″** (padded-block every-width floor certificate). Lemma C.5(i)'s
  second strictness is discharged (degenerately: `GF(aa)`@k=1 via
  Lemma C.10 + C.9′; moving witness = K-E8(b)). Spec + report synced
  (Theory response appended to the report).

## Todo — Theory

(2026-07-11 cycle done: K-F12 paper edit, Theorem C.9′, Theorem C.12″,
C.5(i) strictness, spec/report sync. Next Theory session:)

1. **Respond to K-E8 when it lands**: certified count → K-F12 paragraph
   update ("N of the 246 outright"); any non-certifying persister is a
   hand-analysis specimen (longer-block certificate vs a genuinely new
   every-width mechanism — the latter would be a finding against C.4's
   two-mechanism map).
2. Remaining draft ⟨TBD⟩s, long-term: the general lift of Cor C.9
   (non-prefix-independent recurrence languages), the graded-lift
   remark of C.3, Prop C.19's full syntactic-product bookkeeping.
3. When the cascade section lands in the main paper: `sos_toltl.md` §8
   open-hunt sentence (the 2state2ap witness now exists, K-F12).

## Todo — Engineering

1. **K-E8 (NEW, run first — cheap, table-only, biggest paper payoff)**:
   (a) padded-block certificate scan over the K-F12 conflict layers
   (spec §K-E8; positive control = the type specimen); (b) (B̃) at the
   rescue width on the moving rescued layers. Land CSV in
   `reference/cascade/` + `k_series.md` section + report finding.
2. **k=2 pass on the 640 budget-open layers** (`k_e1_verify <id> <layer> 2`
   sharded; consider `--cores 4 --timeout 300` and/or a raised
   `find_c_conflict` budget arg — cone growth saturates 10⁶ states at k=1
   already). Extend `reference/cascade/` + `k_series.md` with the result.
3. **K-E4 engine integration**: wire `tests/cascade/emit.py` into
   `aut2ltl/sos2ltl/engine.py`; full conformance sweep over the
   (C)-decided layers (rebuild-𝓘 gate on the assembled label) + the DG
   size ledger.
4. **K-E5**: DG vs manufactured cascade on the (A)-fallback stratum
   (recount the stratum on the extended corpus first — the "258" is the
   old cut; needs the `aut2ltl/bls` bridge).
5. **K-E6**: floor-witness pendency machine + prophetic `A_S` cross-check.
6. Housekeeping: E3's rung-stratified (`P|_R`) one-sidedness recount;
   `k_e1_verify` exits 2 on BUDGET which reap tallies as `fail` (cosmetic —
   rows are data; consider exit 0 + status column only); the probe-local
   line-json census format is slated for retirement — keep dependencies
   inside `tests/sos2ltl/` + `tests/cascade/`.

## Machinery (all under `tests/cascade/`, see its README)

- `config_machine.py` — ALG-1/2/5/6: `build_cone`, `entry_stems`,
  `closure_at`, `decide`, `find_c_conflict` (early-exit BFS + ALG-4
  loop-word reconstruction), saturation helpers.
- `sandwich.py` — K-E7 scan (absorption/group/other + verdict-`splits`).
- `emit.py` — K-E4 emitter (DAG-only). Probes: `k_e0*`, `k_e1_sweep`,
  `k_e1_one` (cluster shard unit), `k_e1_verify` (ALG-7 triage, CSV row),
  `k_e2_transfer`, `k_e3_sweep`/`k_e3_pfxind`, `k_e7_controls`/`k_e7_triage`.
- Census records: `python3 -m tests.sos2ltl.census_build
  genaut/corpus/flat_canon/sos --out tests/cascade/logs/census_flat_canon.jsonl`.
- Cluster: shard per language/layer, `--split` wide (≈500), 60 s/command;
  recipe in `tests/cascade/README.md`, contract in `cluster/README.md`.

## Key facts / gotchas

- Build `𝓘` from LTL: `invariant_of_language(Language.of(spot.translate(f)))`.
  Load `.sos`: `sosl.sos.load_invariant`. Import an `aut2ltl.sos2ltl.*`
  module BEFORE `sosl.*` (its init puts sosl on sys.path).
- Verdict oracle: `Val(s,d) = (M(s,π(d)),π(d)) ∈ P`; `π` = `inv.idempotent_power`.
- Frozen layer ⟹ (C)@k = (B)@(k+1) (Lemma C.10) — a frozen-layer
  (C)@0-conflict is a plain-(B)@1 failure.
- A width-k conflict does NOT imply floor membership — the ladder rescues
  many at k+1 (505 in pass 1, 118 at the k=1 pass). Floor claims need
  persistence + the structural argument.
- Conflicts are cheap (early-exit `find_c_conflict`); proving (C) *holds*
  is the expensive side (full closure) — design sweeps accordingly.
- **NEVER stringify LTL / stay DAG** (K-E4 emitter constraint). DG synth's
  `to_spot` blows up — do not call it.
- Timeout convention: 15 s/example local, 60 s/command cluster; TIMEOUT and
  BUDGET are data.
- Gate before landing code: `python3 -m survey --folder samples/validation`
  SUCCESS. Commit as you go (terse `git commit -F -`).
