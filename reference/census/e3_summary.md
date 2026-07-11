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
