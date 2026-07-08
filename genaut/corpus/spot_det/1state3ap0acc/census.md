# 1state3ap0acc — spot-determinized, structural dedup

- TGBA survivors in: 52
- byte-distinct determinized forms (md5): 52
- polarity/name twins folded: 0
- **kept (AP-canonical determinized forms): 52**
- TGBA-to-det collapse: 1.0x
- distinct languages (semantic `𝓘` dedup, see `det`/`sos`): 52  → det-to-language 1.0x

The deterministic automaton `D` (`importer.canonical`) deduplicated by its AP-canonical bytes, **not** by language — contrast the `det`/`sos` tiers, which dedup the same `D` by the syntactic `𝓘` key. Built by `python3 genaut/gen/canonize.py 1state3ap0acc`.
