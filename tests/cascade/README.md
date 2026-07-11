# tests/cascade — K-series probes (the cascade ladder)

Probes for the cascade-ladder experiments: spec
`research_notes/bls_cascade_experiments.md` (K-E0..E7), findings ledger
`research_notes/bls_cascade_report.md` (K-F1..), paper draft
`research_notes/bls_cascade.md`. Run every probe from the repo root:

    python3 -m tests.cascade.<probe> [args]

## Module map

- `config_machine.py` — the config machine `M_k(R)` and the (C)/(B) decider
  (ALG-1/2/5/6): `build_cone`, `entry_stems`, `closure_at`, `decide`,
  `find_c_conflict` (early-exit BFS + ALG-4 loop-word reconstruction),
  saturation helpers.
- `sandwich.py` — the K-E7 sandwich-identity scan over idempotent loop
  classes: `two_sided_ideals` / J-order, `scan` (absorption / group / other +
  verdict splits), `scan_layer`.
- `emit.py` — the K-E4 config normal-form emitter (atoms `A_e`, `omega`,
  `park_verdict`, `letterset`), DAG-only (`spot.formula` hash-consed, never
  stringified).
- `k_e0*.py` — the K-E0 gate probes (worked witnesses, saturation, (B)-cross).
- `k_e1_sweep.py` — (C) over the census-undecided stratum, sandwich scan
  piggybacked (one CSV row per layer).
- `k_e1_one.py` — the per-language shard of the same sweep (cluster unit:
  writes `$OARRUN_OUT.csv`, recomputes its census record in-process). Shard
  the whole stratum with one `cmds.txt` line per language carrying an
  undecided layer, then `cluster/oarrun.sh` + reap (see `cluster/README.md`).
  The cluster is large — split wide, e.g. for the ~2100-command stratum:
  `--split 500 --timeout 1800 --walltime 3:00:00` (≈ 4–5 commands per
  2-core job; the walltime covers a job drawing several heavy layers).
- `k_e1_verify.py` — ALG-7 triage of one raw (C)-conflict (`<id> <layer> <k>`):
  `find_c_conflict` + `inv.member` toggle + non-conjugacy (Lemma C.11).
- `k_e2_transfer.py` — the Prop C.19 transfer specimen.
- `k_e3_sweep.py` / `k_e3_pfxind.py` — one-sidedness statistics / the
  prefix-independence frozen-final-layer scan.
- `k_e4_atoms.py` / `k_e4_gaFb.py` — emitter conformance probes.
- `k_e7_controls.py` / `k_e7_triage.py` — sandwich-scan positive controls /
  per-layer mechanism triage.

## Data formats and logs/

`logs/` is gitignored scratch — regenerable, never cited by a report.

The sweep probes consume a per-language census record file built by
`tests/sos2ltl/census_build.py` (one json object per line). That format is
**local to these probe layers** and may be retired in a repo-wide cleanup:
do not build anything outside `tests/sos2ltl/` and `tests/cascade/` against
it. Regeneration:

    python3 -m tests.sos2ltl.census_build genaut/corpus/flat_canon/sos \
        --out tests/cascade/logs/census_flat_canon.jsonl

**Paper-grade outputs are copied out of `logs/` into `reference/cascade/`**
(tracked CSVs plus a rendered summary md carrying date, git hash, corpus and
the exact regeneration commands) — reports cite only those tracked files.
