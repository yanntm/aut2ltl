# 1state2ap2acc — spot-determinized, structural dedup

- TGBA survivors in: 83
- byte-distinct determinized forms (md5): 80
- polarity/name twins folded: 1
- **kept (AP-canonical determinized forms): 79**
- TGBA-to-det collapse: 1.05x
- distinct languages (semantic `𝓘` dedup, see `det`/`sos`): 66  → det-to-language 1.2x

The deterministic automaton `D` (`importer.canonical`) deduplicated by its AP-canonical bytes, **not** by language — contrast the `det`/`sos` tiers, which dedup the same `D` by the syntactic `𝓘` key. Built by `python3 genaut/gen/canonize.py 1state2ap2acc`.
