# 3state1ap0acc — spot-determinized, structural dedup

- TGBA survivors in: 4033
- byte-distinct determinized forms (md5): 1841
- polarity/name twins folded: 178
- **kept (AP-canonical determinized forms): 1663**
- TGBA-to-det collapse: 2.43x
- distinct languages (semantic `𝓘` dedup, see `det`/`sos`): 1645  → det-to-language 1.01x

The deterministic automaton `D` (`importer.canonical`) deduplicated by its AP-canonical bytes, **not** by language — contrast the `det`/`sos` tiers, which dedup the same `D` by the syntactic `𝓘` key. Built by `python3 genaut/gen/canonize.py 3state1ap0acc`.
