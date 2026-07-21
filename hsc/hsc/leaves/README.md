# hsc/leaves — imported support algebras

A leaf module implements `core.leaf.Leaf` up to its declared tier and
nothing above it. The kernel only ever compares codes (equality, emptiness)
or hands them back to their module (meet, join, relative difference).

| module | carrier | tier | notes |
|---|---|---|---|
| `enum.py` | an explicit finite set | B | codes are frozensets; call-counted, and `bill()` returns the invoice |

Contract for a new leaf:

- codes are hashable and canonical — two codes denoting the same set must
  be equal, since the kernel's canonical sort keys on them;
- `is_empty` is total and exact; the kernel leans on it for the one
  semantic decision canonicity requires;
- `diff` is the *relative* difference; a leaf without a top is legal and
  expected, and no kernel path calls `top` or `complement`;
- there is no preimage in the interface, by design.

`split_equiv(code, expr)` is the partition primitive: return realised
residual expression -> nonempty piece. Enumerating the carrier is a legal
implementation and the one `enum.py` uses; a leaf earns its keep by not
doing that — returning one periodic code where enumeration would return
many singletons is exactly where the cost model's third factor is decided.
