# E0 — Validation campaign

Manifest `m4a-2026-07-08`, 10 runs (named cases; census tier deferred).

| case | config | ref | init | learned | splits | member (f/h/s/p) | eq | cex | sat | cert | stall | byte | verdict |
|---|---|--:|--:|--:|--:|--:|--:|--:|--:|---|---|:--:|---|
| gf_aa_parity | default | 6 | 3 | 6 | 3 | 74 (51/4/9/10) | 2 | 1 | 2 | exact | n/a | yes | SOUND |
| gf_aa_reset | default | 6 | 3 | 6 | 3 | 74 (51/4/9/10) | 2 | 1 | 2 | exact | n/a | yes | SOUND |
| even | default | 5 | 3 | 5 | 2 | 51 (32/4/7/8) | 2 | 1 | 1 | exact | n/a | yes | SOUND |
| evenblocks | default | 8 | 3 | 8 | 5 | 99 (67/4/14/14) | 2 | 1 | 2 | exact | n/a | yes | SOUND |
| a_implies_xa | default | 5 | 4 | 5 | 1 | 43 (32/0/2/9) | 1 | 0 | 1 | exact | n/a | yes | SOUND |
| a_once | default | 4 | 2 | 4 | 2 | 35 (26/3/2/4) | 2 | 1 | 1 | exact | n/a | yes | SOUND |
| a_implies_xa | no-sat-exact | 5 | 4 | 4 | 0 | 21 (17/0/0/4) | 1 | 0 | 0 | exact | permanent | no | ACCEPTOR_ONLY |
| a_implies_xa | exact | 5 | 4 | 5 | 1 | 43 (32/0/2/9) | 1 | 0 | 1 | exact | n/a | yes | SOUND |
| a_once | no-sat-exact | 4 | 2 | 3 | 1 | 18 (13/3/0/2) | 2 | 1 | 0 | exact | permanent | no | ACCEPTOR_ONLY |
| a_once | exact | 4 | 2 | 4 | 2 | 35 (26/3/2/4) | 2 | 1 | 1 | exact | n/a | yes | SOUND |

**Totals.** 8 SOUND · 2 ACCEPTOR_ONLY · 0 FAIL · 0 BUDGET · 0 CRASH. Query budget used: 493 membership, 17 equivalence.

**E0 gate: PASS** — zero failures, zero budget overruns, zero crashes; the permanent specimens certify ACCEPTOR_ONLY under no-saturation (spec §9 P4/F5).
