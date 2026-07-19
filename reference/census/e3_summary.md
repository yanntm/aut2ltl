# E3 census — ROLL FDFA baseline (flat_canon)

6222 languages. Paired medians (our class count N vs ROLL's FDFA size = leading + progress states):

| metric | ours | ROLL periodic | ROLL syntactic | ROLL recurrent |
|---|--:|--:|--:|--:|
| median size | 16 | 16 | 21 | 12 |

**Size comparison over 5783 languages** (algebra N vs ROLL's smallest FDFA): algebra smaller **2026**, larger **3406**, tied **351**. The objects trade places inside the `N+N²` envelope — a wash, not a win (Prop. 5.3(a)); the capability column (LTL-definability, ours only) is the result.

Size comparison ventilated by the LTL cut (the capability our invariant reads off and ROLL's FDFAs cannot):

| definability | smaller | larger | tied |
|---|--:|--:|--:|
| LTL (aperiodic) | 1520 | 1777 | 206 |
| non-LTL | 506 | 1629 | 145 |

## Query cost

Membership (one lasso = one query on both sides) and equivalence queries, per kind. A ROLL count is the whole FDFA family's total, relative to the Büchi presentation it is handed.

**Coverage.** Ours decides **6222** of 6222 languages; ROLL decides 5825 (periodic), 5920 (syntactic), 5913 (recurrent). ROLL decides all three modes on **5783**, some but not all on 177, and none on 262. Every paired count below is over the **5783** languages ROLL decides completely — a partially-failed language is not scored on its surviving modes.

| metric | ours | ROLL periodic | ROLL syntactic | ROLL recurrent |
|---|--:|--:|--:|--:|
| median MQ | 180 | 132 | 212 | 167 |
| median EQ | 2 | 6 | 6 | 7 |

**Membership head-to-head over 5783 languages** (ours vs ROLL's cheapest mode): ours fewer **2616**, tied **27**, more **3140**; median ratio ours/ROLL **1.11**.

**Equivalence head-to-head** over 5783 languages: ours fewer **5663**, tied **109**, more **11**.

Ventilated by the LTL cut:

| definability | MQ fewer | tied | more | EQ fewer | tied | more |
|---|--:|--:|--:|--:|--:|--:|
| LTL (aperiodic) | 1788 | 13 | 1702 | 3403 | 92 | 8 |
| non-LTL | 828 | 14 | 1438 | 2260 | 17 | 3 |
