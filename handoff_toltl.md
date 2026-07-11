# Handoff — toltl thread (main paper, SoS → LTL)

Bootstrap to current state + todos. NOT history (git holds that).
Paper: `research_notes/sos_toltl.md`. Spec: `sos_toltl_spec.md` (its
head is the done/todo map). Ledger: `sos_toltl_report.md` (results in
force, current-state only). Corpus: `genaut/corpus/flat_canon`.
Tracked measurement data: `reference/census/` (extend it; reports cite
only tracked files + regen commands, never `logs/`).

## ⚠ THE CORPUS MOVED UNDER THE PAPER — every census number is stale

The corpus is now **6 222 languages (3 738 LTL / 2 484 non-LTL),
Wagner ceiling ω³/ω⁴** (the campaign added ~1 000 primals above the
old ω² ceiling, plus a late pair). The report's bench section still
says 3 938 (2 240/1 698), and every census-derived figure in the
report and the paper — E1/E2 tables, E7 dual scan, E10, H2/H4, all of
§8, Table 3 and every sentence quoting it — was computed on the old
cut.

**Policy (user-set, absolute): stale data is EVICTED, not annotated.**
There is no "historical" old census worth keeping: no "on the old cut
it was X" parentheticals, no old/new contrasts, no stale number kept
for color. A number either traces to the current corpus through a
tracked artifact + regen command, or it leaves the document. This
binds both roles: **Engineering regenerates the report on the new
corpus; Theory then fixes every number in the paper.**

Known FLIPS the regeneration will surface (already established by the
cascade thread on the new corpus — `reference/cascade/k_series.md`,
ledger `bls_cascade_report.md` K-F7..K-F12; do not re-derive, just
reconcile):

- **Table 3's "(B) failures: 0" is FALSE on the new frame.** The
  window decider leaves 8 786 final-layer readings undecided (over
  2 114 languages); the exact decider finds ≥ 1 021 genuine
  (C)@0-conflicts, 263 persisting at k=1; frozen-singleton conflicts
  are plain-(B) failures (Lemma C.10). Type specimen
  `2state2ap1acc_parity_3772037665`.
- **§7/§8's "a (B)-failing final layer needs 2 states × 2 AP at once,
  a shape the frame omits" is FALSE** — the shape is in the frame and
  populated. The `2state2ap` open-hunt sentences (§7 frontier
  discussion, §8 census-next axis, §10 hunts) must be rewritten: the
  witness exists, in-corpus.
- Prefix-independent stratum: **1 104** languages frame-wide (all with
  frozen final layers — now Theorem C.9′ in `bls_cascade.md`); every
  percentage ventilated by Wagner degree needs recomputing.
- H2/H4's "(A)-failing stratum = 258 languages / 1 432 layers, all
  1 AP, floor |𝒞| = 15" is unverified on the new frame — recount
  (also the preflight of the cascade thread's K-E5).

## Where things stand (apart from the corpus)

- Engine theory closed in the paper: Thm 4.10 (width-1), Thm 4.13
  (graded, seam bricks + `step_th` thread law — seam-only grammar
  refuted, report F15); window relaxation (B̃) + normal form
  (Prop 5.7); TW01 until-rank read-off frozen.
- Engine live and sound catalogue-wide on the OLD cut (0 FAIL,
  graded stratum included — F8/F15); gate
  `python3 -m tests.sos2ltl.e0_gate` (29 fixture cases, 15 s each) is
  corpus-independent and stays the landing gate.
- Spec head lists the open experiment queue: E9 candidates 3/3a/3b/5,
  H7, E3, full E4 + E8, E10 graded re-run, C6 + E5, H8. **H6 /
  smallest-H3 ("census-next 2state2ap") is OBSOLETE** — the shape is
  in-corpus; re-scope against the K-F12 conflict stratum.
- The cascade section (`research_notes/bls_cascade.md`, numbered C.*)
  is drafted to land as §5′; its header lists the touch points. Its
  data is ALREADY on the new corpus — it is the model to follow.

## Todo — Engineering

1. **Regenerate the report on the current corpus** (the big one; shard
   on the cluster, 60 s/command, recipe as in `tests/cascade/README.md`,
   contract `cluster/README.md`):
   - bench section first (counts, degenerates, shape funnel pointer);
   - E1/E2 (anchoring + windows by Wagner degree — Table 3's feed);
   - E7 dual certificate scan (non-LTL side, ω-blind count);
   - E10 ledger; H2/H4 recount ((A)-fallback stratum);
   - land per-experiment CSVs under `reference/census/` + regen
     commands in the report; every finding `Fn` recomputed — a flipped
     finding is flagged `PAPER-EDIT:` with its paper location, per the
     report contract (reproduce before correcting).
2. E0 gate green throughout; `python3 -m survey --folder
   samples/validation` SUCCESS before landing code.
3. Then resume the spec queue (E9 3/3a/3b/5, H7, E3, full E4/E8, E10
   graded re-run, C6+E5, H8) — on new-corpus data only.

## Todo — Theory

1. **After the data drop: fix every number in `sos_toltl.md`.** Sweep
   §8 wholesale (corpus paragraph, Table 3 + discussion, percentages,
   certificate-scan counts), §7's frontier/inner-frontier discussion,
   and the frontier-hunt sentences (~l.1117, ~l.1395, §7 ~l.2874–2886,
   §8 ~l.2955–2968, §10 ~l.3111). Rewrite the `2state2ap` open-hunt
   claims — closed by K-F12's in-frame witness (cite the regenerated
   census data, reconciled with `reference/cascade/`). Eviction policy
   above applies: no old-cut residue.
2. React to any `PAPER-EDIT:` flags from the regeneration (flipped
   findings are theory's to adjudicate).
3. Land the cascade section as §5′ when ready (pointer edits listed in
   `bls_cascade.md`'s header: §4.4, §5.1 residual bullet, §5.4 step 4,
   Table 2 residual row, §9 cascade paragraph — §9's KR ⟨TBD⟩ is
   discharged by C.1's dictionary).
4. Open math carried over: §5.1 width-bound-by-definiteness-degree
   ⟨TBD⟩; §2.3 arena bound (gated on full E4).

## Machinery

- Pipeline `aut2ltl/sos2ltl/`: `cayley.py` (C1), `anchoring.py` (C2),
  `windows.py` (C3), `readoffs.py` (C5), `witness/`, `dg/` (E4b
  baseline), `engine.py` (C4). Probes under `tests/sos2ltl/`
  (`e0_gate`, `e0_*`, `e7_dualscan`, `seam_gate`, `engine_diff`,
  `census_build`).
- Census records: `python3 -m tests.sos2ltl.census_build
  genaut/corpus/flat_canon/sos --out …` (one jsonl record per
  language; the cascade thread consumes the same records).
- Aperiodicity read-off is consumed from
  `sosl/sosl/sos/classify/aperiodic/`, not duplicated.

## Key facts / conventions (user-set; keep)

- Roles: theory holds the paper lock, does math, reads `papers/`;
  engineering implements the spec and fills the report
  (current-state contract). Cite only what was read.
- The paper is science only: no tool names outside §8's oracle
  sentence, no probe/provenance talk.
- The `.sos` unit IS the language (byte-equal iff equal, [SωS26,
  Thm 5.1]); the catalogue is complement-closed; Wagner degree `ϕ` is
  the ventilation axis.
- Timeouts: 15 s/example local, 60 s/command cluster; TIMEOUT/BUDGET
  are data. Honest failure attribution (ours vs downstream).
- Library gaps: Thérien–Weiss, *Graph congruences and wreath
  products*, JPAA 35 (1985); an ω-word locally-testable source.
- Scope rule vs the classification thread: toltl keeps strata
  operational with kinship citations; variety-alignment theorems
  belong to `sos_classification`.
