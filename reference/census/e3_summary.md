# E3 census — ROLL FDFA baseline (flat_canon)

6222 languages. Paired medians (our class count N vs ROLL's FDFA size = leading + progress states):

| metric | ours | ROLL periodic | ROLL syntactic | ROLL recurrent |
|---|--:|--:|--:|--:|
| median size | 16 | 16 | 21 | 12 |

**Size comparison over 5960 languages** (algebra N vs ROLL's smallest FDFA): algebra smaller **2032**, larger **3574**, tied **354**. The objects trade places inside the `N+N²` envelope — a wash, not a win (Prop. 5.3(a)); the capability column (LTL-definability, ours only) is the result.

Size comparison ventilated by the LTL cut (the capability our invariant reads off and ROLL's FDFAs cannot):

| definability | smaller | larger | tied |
|---|--:|--:|--:|
| LTL (aperiodic) | 1524 | 1842 | 207 |
| non-LTL | 508 | 1732 | 147 |

## Query cost

Membership (one lasso = one query on both sides) and equivalence queries, per kind. A ROLL count is the whole FDFA family's total, relative to the Büchi presentation it is handed.

**Coverage.** Ours returns a result on **6222** of 6222 languages; ROLL on 5825 (periodic), 5920 (syntactic), 5913 (recurrent). On **262** languages no ROLL mode returns one, so every paired count below excludes them — the comparison set is 5960, not 6222.

| metric | ours | ROLL periodic | ROLL syntactic | ROLL recurrent |
|---|--:|--:|--:|--:|
| median MQ | 180 | 132 | 212 | 167 |
| median EQ | 2 | 6 | 6 | 7 |

**Membership head-to-head over 5960 languages** (ours vs ROLL's cheapest mode): ours fewer **2650**, tied **27**, more **3283**; median ratio ours/ROLL **1.14**.

**Equivalence head-to-head** over 5960 languages: ours fewer **5840**, tied **109**, more **11**.

Ventilated by the LTL cut:

| definability | MQ fewer | tied | more | EQ fewer | tied | more |
|---|--:|--:|--:|--:|--:|--:|
| LTL (aperiodic) | 1801 | 13 | 1759 | 3473 | 92 | 8 |
| non-LTL | 849 | 14 | 1524 | 2367 | 17 | 3 |
