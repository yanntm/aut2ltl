# 1state2ap1acc_parity — spot-determinized, structural dedup

- TGBA survivors in: 25
- byte-distinct determinized forms (md5): 23
- polarity/name twins folded: 2
- **kept (AP-canonical determinized forms): 21**
- TGBA-to-det collapse: 1.19x
- distinct languages (semantic `𝓘` dedup, see `det`/`sos`): 22  → det-to-language 0.95x

The deterministic automaton `D` (`importer.canonical`) deduplicated by its AP-canonical bytes, **not** by language — contrast the `det`/`sos` tiers, which dedup the same `D` by the syntactic `𝓘` key. Built by `python3 genaut/gen/canonize.py 1state2ap1acc_parity`.
