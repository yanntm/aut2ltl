# 2state2ap0acc — spot-determinized, structural dedup

- TGBA survivors in: 11542
- byte-distinct determinized forms (md5): 11312
- polarity/name twins folded: 654
- **kept (AP-canonical determinized forms): 10658**
- TGBA-to-det collapse: 1.08x
- distinct languages (semantic `𝓘` dedup, see `det`/`sos`): 11312  → det-to-language 0.94x

The deterministic automaton `D` (`importer.canonical`) deduplicated by its AP-canonical bytes, **not** by language — contrast the `det`/`sos` tiers, which dedup the same `D` by the syntactic `𝓘` key. Built by `python3 genaut/gen/canonize.py 2state2ap0acc`.
