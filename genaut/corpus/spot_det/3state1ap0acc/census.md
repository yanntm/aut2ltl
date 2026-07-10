# 3state1ap0acc — spot-determinized, structural dedup

- TGBA survivors in: 4033
- byte-distinct determinized forms (md5): 1645
- polarity/name twins folded: 214
- **kept (AP-canonical determinized forms): 1431**
- TGBA-to-det collapse: 2.82x
- distinct languages (semantic `𝓘` dedup, see `det`/`sos`): 1645  → det-to-language 0.87x

The deterministic automaton `D` (`importer.canonical`) deduplicated by its AP-canonical bytes, **not** by language — contrast the `det`/`sos` tiers, which dedup the same `D` by the syntactic `𝓘` key. Built by `python3 genaut/gen/canonize.py 3state1ap0acc`.
