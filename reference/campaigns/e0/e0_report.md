# E0 — Validation campaign

Manifest `m4a-2026-07-08`, 6 runs (named cases; census tier deferred).

| case | config | ref | init | learned | splits | member (f/h/s/p) | eq | cex | sat | cert | stall | byte | verdict |
|---|---|--:|--:|--:|--:|--:|--:|--:|--:|---|---|:--:|---|
| gf_aa_parity | default | 6 | 2 | 6 | 4 | 31 (22/3/1/5) | 2 | 1 | 2 | exact | - | yes | SOUND |
| gf_aa_reset | default | 6 | 2 | 6 | 4 | 31 (22/3/1/5) | 2 | 1 | 2 | exact | - | yes | SOUND |
| even | default | 5 | 2 | 5 | 3 | 25 (17/4/1/3) | 2 | 1 | 1 | exact | - | yes | SOUND |
| evenblocks | default | 8 | 2 | 8 | 6 | 44 (34/3/2/5) | 2 | 1 | 2 | exact | - | yes | SOUND |
| a_implies_xa | default | 5 | 2 | 5 | 3 | 20 (13/3/0/4) | 2 | 1 | 2 | exact | - | yes | SOUND |
| a_once | default | 4 | 2 | 4 | 2 | 10 (7/1/1/1) | 2 | 1 | 1 | exact | - | yes | SOUND |

**Totals.** 6 SOUND · 0 ACCEPTOR_ONLY · 0 FAIL · 0 BUDGET · 0 CRASH. Query budget used: 161 membership, 12 equivalence.

**E0 gate: PASS** — zero failures, zero budget overruns, zero crashes; the permanent specimens certify ACCEPTOR_ONLY under no-saturation (spec §9 P4/F5).
