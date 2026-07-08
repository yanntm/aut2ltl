# 1state1ap3acc_parity — spot-determinized, structural dedup

- TGBA survivors in: 23
- byte-distinct determinized forms (md5): 7
- polarity/name twins folded: 1
- **kept (AP-canonical determinized forms): 6**
- TGBA-to-det collapse: 3.83x
- distinct languages (semantic `𝓘` dedup, see `det`/`sos`): 6  → det-to-language 1.0x

The deterministic automaton `D` (`importer.canonical`) deduplicated by its AP-canonical bytes, **not** by language — contrast the `det`/`sos` tiers, which dedup the same `D` by the syntactic `𝓘` key. Built by `python3 genaut/gen/canonize.py 1state1ap3acc_parity`.
