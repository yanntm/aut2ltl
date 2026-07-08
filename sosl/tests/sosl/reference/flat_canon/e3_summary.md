# E3 census — ROLL FDFA baseline (flat_canon)

3938 languages. Paired medians (our class count N vs ROLL's FDFA size = leading + progress states):

| metric | ours | ROLL periodic | ROLL syntactic | ROLL recurrent |
|---|--:|--:|--:|--:|
| median size | 16 | 17 | 24 | 13 |

**Size comparison over 3937 languages** (algebra N vs ROLL's smallest FDFA): algebra smaller **1352**, larger **2394**, tied **191**. The objects trade places inside the `N+N²` envelope — a wash, not a win (Prop. 5.3(a)); the capability column (LTL-definability, ours only) is the result.

Size comparison ventilated by the LTL cut (the capability our invariant reads off and ROLL's FDFAs cannot):

| definability | smaller | larger | tied |
|---|--:|--:|--:|
| LTL (aperiodic) | 1015 | 1114 | 110 |
| non-LTL | 337 | 1280 | 81 |
