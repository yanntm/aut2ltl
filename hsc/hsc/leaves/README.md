# hsc/leaves — imported support algebras

A leaf module implements `core.leaf.Leaf` up to its declared tier and
nothing above it. The kernel only ever compares codes (equality, emptiness)
or hands them back to their module (meet, join, relative difference).

| module | carrier | tier | notes |
|---|---|---|---|
| `enum.py` | an explicit finite set | B | codes are frozensets; call-counted, and `bill()` returns the invoice |

The tier ledger, the `split_equiv` contract and what a new theory module
owes are in `algorithm.md` in this folder. One module per theory.
