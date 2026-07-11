# E3 census — ROLL FDFA baseline (flat_canon)

4248 languages. Paired medians (our class count N vs ROLL's FDFA size = leading + progress states):

| metric | ours | ROLL periodic | ROLL syntactic | ROLL recurrent |
|---|--:|--:|--:|--:|
| median size | 15 | 17 | 24 | 13 |

**Size comparison over 4238 languages** (algebra N vs ROLL's smallest FDFA): algebra smaller **1488**, larger **2551**, tied **199**. The objects trade places inside the `N+N²` envelope — a wash, not a win (Prop. 5.3(a)); the capability column (LTL-definability, ours only) is the result.

Size comparison ventilated by the LTL cut (the capability our invariant reads off and ROLL's FDFAs cannot):

| definability | smaller | larger | tied |
|---|--:|--:|--:|
| LTL (aperiodic) | 1128 | 1228 | 117 |
| non-LTL | 360 | 1323 | 82 |
