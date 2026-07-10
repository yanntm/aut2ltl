# 1state2ap2acc — spot-determinized, structural dedup

- TGBA survivors in: 83
- byte-distinct determinized forms (md5): 79
- polarity/name twins folded: 7
- **kept (AP-canonical determinized forms): 72**
- TGBA-to-det collapse: 1.15x
- distinct languages (semantic `𝓘` dedup, see `det`/`sos`): 66  → det-to-language 1.09x

The deterministic automaton `D` (`importer.canonical`) deduplicated by its AP-canonical bytes, **not** by language — contrast the `det`/`sos` tiers, which dedup the same `D` by the syntactic `𝓘` key. Built by `python3 genaut/gen/canonize.py 1state2ap2acc`.
