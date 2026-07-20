## 4. The loop: reap and sow

The loop alternates two motions. **Reap**: a disagreement is in hand — turn
it into a class split. **Sow**: re-stabilize the table, re-certify
legality, re-export the belief — and, in doing so, surface the next
disagreements for free. Every split in the entire algorithm is one event in
three guises:

> **Two concrete lassos bear one name, and the teacher's bits on them
> differ.**

The name is a pair `(s, e)` of current classes; the two lassos are
interpolated by a *chain* that substitutes, position by position, a growing
prefix by its class's key; the chain's bits flip at some adjacent step; the
flip convicts a frontier word against a row — currently one class, provably
`≈_L`-distinct — and mints the separating Arnold context as a new column.
The three guises differ only in where the disagreeing lassos come from:

- the teacher's equivalence counterexample, against the keyed lasso of its
  name (§4.1 — the only guise that costs an equivalence query);
- a stamp-legality violation, escalated through two probe queries (§4.2);
- a pair-legality violation: two conjugate pairs with differing cached
  bits, whose common rotated lasso the learner queries itself (§4.2).

### 4.1 Reap: the harvest

Let `w·z^ω` be a lasso on which belief and teacher disagree. **Normalize**
`(w', z') := (w·z^k, z^k)`, `k` least with `𝒮_T(z)^k` idempotent
(`k ≤ 2·|𝒞_T|`) — the same ω-word, now presented so that `s = 𝒮_T(w')`,
`e = 𝒮_T(z')` is the predicting pair. Write `n = |w'|`, `m = |z'|`.
Interpolate between the counterexample and the keyed lasso of its name by
two chains of teacher bits, each replacing a growing prefix by the key of
its class:

```
    stem chain:   γ_i = [ u_{⟨w'[1..i]⟩} · w'[i+1..n] · z'^ω ∈ L ]          i = 0..n
    loop chain:   δ_i = [ u_s · ( u_{⟨z'[1..i]⟩} · z'[i+1..m] )^ω ∈ L ]     i = 0..m
```

Then `γ_0 = [w'·z'^ω ∈ L]` is the teacher's bit on the counterexample,
`γ_n = δ_0 = [u_s·z'^ω ∈ L]` is the junction, and `δ_m = [u_s·(u_e)^ω ∈ L]`
is the belief's answer — the cached `P(s, e)`. The concatenated bit sequence
has differing endpoints, so it flips at an adjacent pair; **one junction
query** decides the half, and a Rivest–Schapire binary search [RS93] — each
probe one membership query — finds a flip in `O(log n)` resp. `O(log m)`
queries.

**Lemma 4.1 (stem harvest).** A flip `γ_i ≠ γ_{i+1}` yields the frontier
word `u = u_{⟨w'[1..i]⟩}·w'[i+1]` and the row `v = u_{⟨w'[1..i+1]⟩}`,
currently assigned the same class, separated by the **linear column**
`(ε, w'[i+2..n], z')`.

**Lemma 4.2 (loop harvest).** A flip `δ_i ≠ δ_{i+1}` yields the frontier
word `u = u_{⟨z'[1..i]⟩}·z'[i+1]` and the row `v = u_{⟨z'[1..i+1]⟩}`,
currently assigned the same class, separated by the **ω-column**
`(u_s, z'[i+2..m])`.

*Proof of both.* The two flipped bits are exactly the entries of `u` and `v`
at the stated column — substitute and compare — and the columns are Arnold
contexts, so the separation is genuine: `u ≉_L v`. That `u` and `v`
currently share a class is Lemma 3.3's agreement. Replacing the prefix *at
the head of the loop* and letting the ω-column's `(x, y)` format carry the
rest is the rotation lemma [SωS26, Lem 4.1] enacted: no search over
rotations is ever needed. ∎

**Theorem 4.3 (harvest).** Each disagreeing lasso funds the flip column and
splits one class — the frontier word `u` leaves the class of `v` — at a cost
of `O(log(|w| + |𝒞_T|·|z|))` membership queries: the normalized lengths are
`n ≤ |w| + 2|𝒞_T|·|z|` and `m ≤ 2|𝒞_T|·|z|`.

*Proof.* A flip exists: the concatenated chain runs from the teacher's bit
on the counterexample to the belief's (wrong) answer, so its endpoints
differ, and the junction bit `γ_n = δ_0` decides which half flips. The flip
splits a class by Lemma 4.1 resp. 4.2: the frontier word `u` differs from
the row `v` on the minted column, so `u` leaves `v`'s class when the table
refills. The cost: the two chains total `n + m` positions with the stated
bounds, and one junction query plus a binary search over a bit sequence
with differing endpoints finds an adjacent flip in the stated logarithm. ∎

*Example (two counterexamples, one wrong name, two shapes).* The two
running examples' first equivalence queries return different lassos —
`Even`'s teacher hands back `(ε, aab)`, `EvenBlocks`' the shortlex-earlier
`(ε, b·aa)` — but the same failure: each is named `(⟨a⟩, ⟨a⟩)`, i.e.
answered through the keyed lasso `a·a^ω`, and each is truly in its
language. Normalization is trivial in both (`k = 1`, so `w' = z'` is the
loop itself), the stem key is `u_s = a` in both, and the junction query
routes them oppositely. On `Even`, `[a·(aab)^ω] = 0` — the prepended `a`
flips the parity — against `γ_0 = [(aab)^ω] = 1`: the flip is in the
**stem chain**, Table 3(a). On `EvenBlocks`, `[a·(b·aa)^ω] = 1` — a prefix
cannot harm a prefix-independent language — equal to `γ_0`, so the stem
chain is flat and the flip is in the **loop chain**, Table 3(c). Both flips
sit at position `1 → 2` of their chains, but they convict different words:
from (a), the frontier word `u = u_{⟨a⟩}·a = aa` against the row
`v = u_{⟨aa⟩} = a`, minting the linear column `(ε, b, aab)`, entries `1`
for `aa` and `0` for `a` — the parity merge of day one, split; from (c),
the frontier word `u = u_{⟨b⟩}·a = b·a` against the row
`v = u_{⟨b·a⟩} = a`, minting the ω-column `(a, a)` — a rotated cousin of
the `(ε, b)` we exhibited in §3.1, found by the machinery rather than by
inspection. Tables 3(b) and 3(d) show the tables after the split. Two
lassos, one wrong name, Arnold's two shapes: the counterexample analysis is
the two-shape split of the congruence, run backwards.

*(a) `Even`, the stem chain `γ` — replace a growing stem prefix by its
key:*

| `i` | prefix | its key | queried lasso | `γ_i` |
|:--:|---|:--:|---|:--:|
| 0 | — | — | `aab·(aab)^ω` | `1` |
| 1 | `a` | `a` | `a·ab·(aab)^ω` | `1` |
| 2 | `aa` | `a` | `a·b·(aab)^ω` | **`0`** |
| 3 | `aab` | `a` | `a·(aab)^ω` | `0` |

*(b) `Even`, after the stem harvest:*

| word | `(ε,ε)_ω` | **`(ε, b, aab)_lin`** | class |
|---|:--:|:--:|---|
| `a` | `0` | **`0`** | `⟨a⟩` |
| `b` | `1` | **`1`** | `⟨b⟩` |
| **`aa`** | `0` | **`1`** | **`⟨aa⟩`** |
| *frontier:* | | | |
| `a·b` | `0` | **`0`** | → `⟨a⟩` ✗ still |
| `aa·b` | `1` | **`1`** | → `⟨b⟩` |

*(c) `EvenBlocks`, the loop chain `δ` — stem pinned to `u_s = a`, replace a
growing loop prefix by its key:*

| `i` | prefix | its key | queried lasso | `δ_i` |
|:--:|---|:--:|---|:--:|
| 0 | — | — | `a·(b·aa)^ω` | `1` |
| 1 | `b` | `b` | `a·(b·aa)^ω` | `1` |
| 2 | `b·a` | `a` | `a·(a·a)^ω` | **`0`** |
| 3 | `b·aa` | `a` | `a·(a)^ω` | `0` |

*(d) `EvenBlocks`, after the loop harvest:*

| word | `(ε,ε)_ω` | **`(a, a)_ω`** | class |
|---|:--:|:--:|---|
| `a` | `0` | **`0`** | `⟨a⟩` |
| `b` | `1` | **`0`** | `⟨b⟩` |
| **`b·a`** | `0` | **`1`** | **`⟨b·a⟩`** |

**Table 3.** The two first counterexamples, processed (minted column and
promoted row in bold; `ε`-row and unchanged frontier omitted). In both
chains, row `i = 1` replaces a one-letter prefix by its own key — a no-op,
bit unchanged — and the flips sit at `1 → 2`. In (a), row 3 is the junction
`γ_3 = δ_0`, already `0`: the stem chain flipped, minting a *linear*
column. In (c) the junction is `1` and the loop chain flips instead,
minting an *ω-column*; note row 3's lasso is `a·a^ω` — the keyed lasso of
the name, i.e. the belief's answer, closing the chain. (a) pulls `aa` out
of `⟨a⟩`; (c) pulls `b·a` out — and in (b) the doomed `a·b` still hides in
`⟨a⟩`, which is §4.2's catch.
