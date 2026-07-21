# hsc/leaves — algorithms

A leaf is a *theory*: an external domain imported through a finite window.
One module per theory. The window, not the domain, is what the calculus
sees, and a leaf's job is to make the window narrow and the codes small.

---

## 1. The tier ledger

Cumulative; a leaf declares its tier and implements up to it, and the kernel
calls only what the operation at hand consumes.

| tier | adds | used by |
|---|---|---|
| E | canonical codes, equality, emptiness | every decision the kernel makes |
| J | finite joins | assembling sections, `(F)`-compression |
| G | finite meets, **relative** differences | maintaining `(D)` inside `normalize` |
| B | top, complement | nothing in the kernel |

Tier G is the working tier and deliberately has **no top**. A leaf without a
top is legal and expected.

**There is no preimage in this interface, absolute or relative, and none is
planned.** Undoing a destructive assignment needs a reachable set to move
within; that is a different problem for a different iteration, and the
interface must not grow a hole for it in the meantime.

---

## 2. `split_equiv` — where a leaf earns its keep

```
split_equiv(code, expr) -> {residual expression : nonempty piece}
```

Partition the code by the residual of the classifier after substituting this
leaf's coordinate.

Enumerating the carrier is a legal implementation and is what `enum.py`
does, because its carrier is explicitly finite and enumeration is honest
there. It is also the *only* thing a leaf can do badly. A leaf earns its
keep by returning few, structured codes where enumeration would return many
singletons — that ratio is the third factor of the cost model, and it is the
one factor decided entirely by the leaf.

A leaf may also normalise the classifier terms it understands. That strength
is a **cost parameter, never a soundness one**: an equality it misses costs
redundant subqueries which the kernel merge recovers retroactively.

---

## 3. Contract for a new theory module

- codes are hashable and canonical — two codes denoting the same set must be
  equal, since the kernel's canonical sort keys on them;
- `is_empty` is total and exact; it is the one semantic decision canonicity
  leans on;
- `diff` is the *relative* difference;
- every method is call-counted through `core.stats`, because the bill is a
  product of this repository and not telemetry;
- `elements` is the shadow's door, for oracle tests over small carriers
  only; nothing in the kernel calls it.

---

## 4. Modules

| module | carrier | tier | notes |
|---|---|---|---|
| `enum.py` | an explicit finite set | B | codes are frozensets; splits by enumeration, which is honest for a finite carrier and is the baseline every other leaf should beat |
