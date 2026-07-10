# 1state3ap1acc — spot-determinized, structural dedup

- TGBA survivors in: 1512
- byte-distinct determinized forms (md5): 1480
- polarity/name twins folded: 286
- **kept (AP-canonical determinized forms): 1194**
- TGBA-to-det collapse: 1.27x
- distinct languages (semantic `𝓘` dedup, see `det`/`sos`): 1480  → det-to-language 0.81x

The deterministic automaton `D` (`importer.canonical`) deduplicated by its AP-canonical bytes, **not** by language — contrast the `det`/`sos` tiers, which dedup the same `D` by the syntactic `𝓘` key. Built by `python3 genaut/gen/canonize.py 1state3ap1acc`.
