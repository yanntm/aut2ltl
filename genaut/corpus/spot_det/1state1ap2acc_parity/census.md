# 1state1ap2acc_parity — spot-determinized, structural dedup

- TGBA survivors in: 12
- byte-distinct determinized forms (md5): 5
- polarity/name twins folded: 0
- **kept (AP-canonical determinized forms): 5**
- TGBA-to-det collapse: 2.4x
- distinct languages (semantic `𝓘` dedup, see `det`/`sos`): 5  → det-to-language 1.0x

The deterministic automaton `D` (`importer.canonical`) deduplicated by its AP-canonical bytes, **not** by language — contrast the `det`/`sos` tiers, which dedup the same `D` by the syntactic `𝓘` key. Built by `python3 genaut/gen/canonize.py 1state1ap2acc_parity`.
