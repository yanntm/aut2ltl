# 2state1ap1acc — spot-determinized, structural dedup

- TGBA survivors in: 929
- byte-distinct determinized forms (md5): 337
- polarity/name twins folded: 18
- **kept (AP-canonical determinized forms): 319**
- TGBA-to-det collapse: 2.91x
- distinct languages (semantic `𝓘` dedup, see `det`/`sos`): 129  → det-to-language 2.47x

The deterministic automaton `D` (`importer.canonical`) deduplicated by its AP-canonical bytes, **not** by language — contrast the `det`/`sos` tiers, which dedup the same `D` by the syntactic `𝓘` key. Built by `python3 genaut/gen/canonize.py 2state1ap1acc`.
