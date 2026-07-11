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
- **K-E1 RERUN IN FLIGHT** (extended census, patched decider — the pre-patch
  closure had a loop bug; its partial rows were discarded). ⚠ **K-F12
  CONFIRMED on the first specimen**: `2state2ap1acc_parity_3772037665`
  (13 classes, aperiodic, Wagner (ω³,σ), frozen singleton layers 5/7) has an
  ALG-7-verified GENUINE width-0 (C)-conflict (= plain-(B) failure in-frame,
  Lemma C.10) — probe `python3 -m tests.cascade.k_e1_verify <id> <layer> <k>`
  (committed). The "floor empty on the census frame" claim (K-F7/K-F9, draft
  C.2/C.19/C.7) FALLS; PAPER-EDIT queued behind the full rerun tally.
  Remaining aperiodic CONFLICT rows still need per-specimen ALG-7 triage;
  non-aperiodic ones are the expected group escape (EvenBlocks-style).
  Every-width failure (full C.12′ floor membership) not yet established
  (k≥1 BUDGET) — structural analysis TODO.
- **K-E3 RERUN DONE** (extended): 5050 (C)-decided final layers at k≤3;
  one-sidedness over the 74 ≥2-class-family layers: 16 up / 16 down /
  28 both / 14 neither — still balanced; up=down is forced by complement
  closure of the catalogue (complement swaps the closure direction) — say so
  in the draft. Cor C.9 gating stratum: 0. Pfxind scan: **1104**
  prefix-independent (was 132), **0** with a non-frozen final layer.
- **K-E2 (K-F9) / K-E4 (K-F11)** unchanged: transfer specimen verified;
  emitter conformance-gated on `G(a→F b)`; K-E4 production wiring pending.
- **Data discipline (new)**: reports may cite only git-tracked data. Once
  K-E1 lands: create `reference/cascade/` (k_e1.csv, k_e3.csv,
  k_e3_pfxind.txt + `k_series.md` in the style of `reference/quant/m2_laws.md`
  — date, git hash, corpus, regen commands, rendered tables), commit, and
  re-point the ledger at it. READMEs added to `tests/cascade/` +
  `tests/sos2ltl/` (the line-json census format is probe-local, may be
  retired — depend on nothing outside those folders).

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

1. **K-E1 rerun lands** → tally (coverage/width histogram, conflicts by
   aperiodicity, K-E7 mechanism columns). **Triage every aperiodic CONFLICT
   with ALG-7** (`k_e7_triage <id> <layer> <k>`): verified-genuine ⟹ in-frame
   floor inhabitant ⟹ rewrite the floor claim (draft C.2 remark, C.19
   closing bold, C.4 map paragraph, C.7 §8 bullet); artifacts ⟹ claim
   survives, numbers only.
2. Create + commit `reference/cascade/` (see Where-things-stand); re-point
   `bls_cascade_report.md` K-F7/F8/F10 (and K-F9 subsumption note) at the
   tracked files with the extended-corpus numbers; sync `bls_cascade.md`
   (sites: C.2 remark ~l.240, after Cor C.8 ~l.380, Cor C.9 ~l.424, C.4
   ~l.720+769, C.7 bullet ~l.1003), `bls_cascade_spec.md` (stale "372"
   input descriptions), this handoff.
3. **K-E4 engine integration**: wire the emitter into
   `aut2ltl/sos2ltl/engine.py`, full conformance sweep over K-E1-decided
   layers + DG size ledger.
4. **K-E5**: DG vs manufactured cascade on the (A)-fallback stratum (recount
   the 258 on the extended corpus first; needs `aut2ltl/bls` bridge).
5. **K-E6**: floor witness pendency machine + prophetic `A_S` cross-check.
- Gate before landing code: `python3 -m survey --folder samples/validation`
  SUCCESS.
- Commit as you go (terse `git commit -F -`, several files ok, no need to ask).
