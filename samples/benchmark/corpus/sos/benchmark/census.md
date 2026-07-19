# benchmark — canonical (language) dedup

- TGBA survivors in (AP-canonical `kept`): 336
- **distinct languages (syntactic `𝓘` dedup): 241**
- TGBA-to-language collapse: 1.39x (19 capped, 2 timeout, 2 oversize)
- enumeration abundance per language: median 1, max 4
- `N = |𝒞|` over languages: 2 / 7 / 380  (min / median / max)

Built by `python3 genaut/gen/canonize.py benchmark` from `corpus/tgba/benchmark/`.

## Skipped (budget-tripped, recorded)

- `kinska_counting-1ap-counting_buchi_1ap_31`: capped (closure > 20000)
- `kinska_counting-1ap-counting_buchi_1ap_32`: capped (closure > 20000)
- `kinska_counting-1ap-counting_buchi_1ap_33`: capped (closure > 20000)
- `kinska_counting-1ap-counting_buchi_1ap_34`: capped (closure > 20000)
- `kinska_counting-1ap-counting_buchi_1ap_35`: capped (closure > 20000)
- `kinska_counting-1ap-counting_buchi_1ap_36`: capped (closure > 20000)
- `kinska_counting-1ap-counting_buchi_1ap_37`: capped (closure > 20000)
- `kinska_counting-1ap-counting_buchi_1ap_38`: capped (closure > 20000)
- `kinska_counting-1ap-counting_buchi_1ap_39`: capped (closure > 20000)
- `kinska_counting-1ap-counting_buchi_1ap_40`: capped (closure > 20000)
- `kinska_counting-2ap-counting_buchi_2ap_33`: oversize (.sos 3208726 > 1048576 bytes)
- `kinska_counting-2ap-counting_buchi_2ap_34`: oversize (.sos 19050959 > 1048576 bytes)
- `kinska_counting-2ap-counting_buchi_2ap_35`: timeout (>15.0s)
- `kinska_counting-2ap-counting_buchi_2ap_36`: timeout (>15.0s)
- `kinska_counting-2ap-counting_buchi_2ap_37`: capped (closure > 20000)
- `kinska_counting-2ap-counting_buchi_2ap_38`: capped (closure > 20000)
- `kinska_counting-2ap-counting_buchi_2ap_39`: capped (closure > 20000)
- `kinska_counting-2ap-counting_buchi_2ap_40`: capped (closure > 20000)
- `kinska_counting-2ap-counting_buchi_2ap_41`: capped (closure > 20000)
- `kinska_counting-2ap-counting_buchi_2ap_42`: capped (closure > 20000)
- `kinska_counting-2ap-counting_buchi_2ap_43`: capped (closure > 20000)
- `kinska_counting-2ap-counting_buchi_2ap_44`: capped (closure > 20000)
- `kinska_counting-2ap-counting_buchi_2ap_45`: capped (closure > 20000)
