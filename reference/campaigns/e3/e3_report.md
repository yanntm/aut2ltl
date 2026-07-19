# E3 — ROLL FDFA baseline

`ours`: syntactic-ω-semigroup class count N and (MQ/EQ). `ROLL <mode>`: FDFA size (leading+progress states) and (MQ/EQ). Certification: ours exact, ROLL RABIT/sampling (F6).

| case | ours N (MQ/EQ) | ROLL periodic (MQ/EQ) | ROLL syntactic (MQ/EQ) | ROLL recurrent (MQ/EQ) | LTL-def? |
|---|---|---|---|---|:--:|
| gf_aa_parity | 6 (31/2) | 4 (20/2) | 4 (20/2) | 4 (20/2) | ours: yes · FDFA: N/A |
| gf_aa_reset | 6 (31/2) | 4 (20/2) | 4 (20/2) | 4 (20/2) | ours: yes · FDFA: N/A |
| even | 5 (25/2) | 12 (79/5) | 15 (112/5) | 9 (92/5) | ours: yes · FDFA: N/A |
| evenblocks | 8 (44/2) | 8 (74/4) | 8 (74/4) | 8 (74/4) | ours: yes · FDFA: N/A |
| a_implies_xa | 5 (20/2) | 12 (64/4) | 14 (145/7) | 9 (128/7) | ours: yes · FDFA: N/A |
| a_once | 4 (10/2) | 8 (52/4) | 10 (75/4) | 7 (63/4) | ours: yes · FDFA: N/A |

**Capability.** Only our invariant answers LTL-definability (the aperiodicity/group test on the algebra); an FDFA cannot — reported as a result, not a gap.
