# 2state1ap1acc_parity — spot-determinized, structural dedup

- TGBA survivors in: 929
- byte-distinct determinized forms (md5): 352
- polarity/name twins folded: 18
- **kept (AP-canonical determinized forms): 334**
- TGBA-to-det collapse: 2.78x
- distinct languages (semantic `𝓘` dedup, see `det`/`sos`): 129  → det-to-language 2.59x

The deterministic automaton `D` (`importer.canonical`) deduplicated by its AP-canonical bytes, **not** by language — contrast the `det`/`sos` tiers, which dedup the same `D` by the syntactic `𝓘` key. Built by `python3 genaut/gen/canonize.py 2state1ap1acc_parity`.
