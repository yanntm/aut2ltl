# 1state1ap1acc — spot-determinized, structural dedup

- TGBA survivors in: 5
- byte-distinct determinized forms (md5): 4
- polarity/name twins folded: 0
- **kept (AP-canonical determinized forms): 4**
- TGBA-to-det collapse: 1.25x
- distinct languages (semantic `𝓘` dedup, see `det`/`sos`): 4  → det-to-language 1.0x

The deterministic automaton `D` (`importer.canonical`) deduplicated by its AP-canonical bytes, **not** by language — contrast the `det`/`sos` tiers, which dedup the same `D` by the syntactic `𝓘` key. Built by `python3 genaut/gen/canonize.py 1state1ap1acc`.
