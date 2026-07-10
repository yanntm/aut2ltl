# 1state2ap2acc_parity — spot-determinized, structural dedup

- TGBA survivors in: 98
- byte-distinct determinized forms (md5): 58
- polarity/name twins folded: 8
- **kept (AP-canonical determinized forms): 50**
- TGBA-to-det collapse: 1.96x
- distinct languages (semantic `𝓘` dedup, see `det`/`sos`): 58  → det-to-language 0.86x

The deterministic automaton `D` (`importer.canonical`) deduplicated by its AP-canonical bytes, **not** by language — contrast the `det`/`sos` tiers, which dedup the same `D` by the syntactic `𝓘` key. Built by `python3 genaut/gen/canonize.py 1state2ap2acc_parity`.
