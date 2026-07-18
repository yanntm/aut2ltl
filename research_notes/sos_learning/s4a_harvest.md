## 4. The learner

### 4.1 The harvest: every disagreeing lasso surrenders a column

Let `w·z^ω` be a lasso on which prediction and teacher disagree. **Normalize**
`(w', z') = (w·z^k, z^k)` with `k` as in the prediction — the same ω-word, now
with `s = ψ(w')`, `e = ψ(z')` the predicting pair. Write `n = |w'|`, `m = |z'|`.
Interpolate between the counterexample and its representative collapse by two
chains of teacher bits, each replacing a growing prefix by its class
representative:

```
    stem chain:   γ_i = [ rep(ψ(w'[1..i])) · w'[i+1..n] · z'^ω ∈ L ]      i = 0..n
    loop chain:   δ_i = [ w_s · ( rep(ψ(z'[1..i])) · z'[i+1..m] )^ω ∈ L ]  i = 0..m
```

Then `γ_0 = [w'·z'^ω ∈ L]` is the teacher's bit on the counterexample,
`γ_n = δ_0 = [w_s·z'^ω ∈ L]` is the junction, and `δ_m = [w_s·(w_e)^ω ∈ L]` is
the prediction. The concatenated bit sequence has differing endpoints, so it
flips at an adjacent pair; **one junction query** decides the half, and a
Rivest–Schapire binary search [RS93] — each probe one membership query — finds a
flip in `O(log n)` resp. `O(log m)` queries.

**Lemma 4.1 (stem harvest).** A flip `γ_i ≠ γ_{i+1}` yields the frontier word
`u = rep(ψ(w'[1..i]))·w'[i+1]` and the row `v = rep(ψ(w'[1..i+1]))`, currently
assigned the same class, separated by the **linear column**
`(ε, w'[i+2..n], z')`.

**Lemma 4.2 (loop harvest).** A flip `δ_i ≠ δ_{i+1}` yields the frontier word
`u = rep(ψ(z'[1..i]))·z'[i+1]` and the row `v = rep(ψ(z'[1..i+1]))`, currently
assigned the same class, separated by the **ω-column** `(w_s, z'[i+2..m])`.

*Proof of both.* The two flipped bits are exactly the entries of `u` and `v` at
the stated column — substitute and compare — and the columns are Arnold contexts,
so the separation is genuine: `u ≉_L v`. That `u` and `v` currently share a class
is the definition of `step`. Replacing the prefix *at the head of the loop* and
letting the ω-column's `(x, y)` format carry the rest is the rotation lemma
[SωS26, Lem 4.1] enacted: no search over rotations is ever needed. ∎

**Theorem 4.3 (harvest).** Each counterexample adds the flip column and splits
one class — the frontier word `u` leaves the class of `v` — so `|𝒞_T|` grows by
one per equivalence query, at a cost of `O(log(|w| + |𝒞_T|·|z|))` membership
queries: the normalized lengths are `n ≤ |w| + 2|𝒞_T|·|z|` and
`m ≤ 2|𝒞_T|·|z|`, since the stabilization power satisfies `k ≤ 2|𝒞_T|`.

*Proof.* A flip exists: the concatenated chain runs from the teacher's bit on
the counterexample to the (wrong) prediction, so its endpoints differ, and
the junction bit `γ_n = δ_0` decides which half flips. The flip splits a
class by Lemma 4.1 resp. 4.2: the frontier word `u` differs from the row `v`
on the minted column, so `u` leaves `v`'s class when the table refills. The
cost: the two chains total `n + m` positions with the stated bounds, and one
junction query plus a binary search over a bit sequence with differing
endpoints finds an adjacent flip in the stated logarithm. ∎

*Example (two counterexamples, one wrong name, two shapes).* The two running
specimens' first equivalence queries return different lassos — `Even`'s
teacher hands back `(ε, aa!a)`, `EvenBlocks`'s the shortlex-earlier
`(ε, !a·aa)` — but the same failure: each is predicted `0` through the pair
`([a],[a])`, i.e. through the representative lasso `a·a^ω`, and each is truly
in its language. Normalization is trivial in both (`k = 1`, so `w' = z'` is
the loop itself), the stem representative is `w_s = a` in both, and the
junction query routes them oppositely. On `Even`, `[a·(aa!a)^ω] = 0` — the
prepended `a` flips the parity — against `γ_0 = [(aa!a)^ω] = 1`: the flip is
in the **stem chain**, Table 3(a). On `EvenBlocks`, `[a·(!a·aa)^ω] = 1` — a
prefix cannot harm a prefix-independent language — equal to `γ_0`, so the
stem chain is flat and the flip is in the **loop chain**, Table 3(c). Both
flips sit at position `1 → 2` of their chains, but they convict different
words: from (a), the frontier word `u = rep(ψ(a))·a = aa` against the row
`v = rep(ψ(aa)) = a`, minting the linear column `(ε, !a, aa!a)`, entries `1`
for `aa` and `0` for `a` — the parity merge of day one, split; from (c), the
frontier word `u = rep(ψ(!a))·a = !a·a` against the row
`v = rep(ψ(!a·a)) = a`, minting the ω-column `(a, a)` — a rotated cousin of
the `(ε, !a)` we exhibited in §3, found by the machinery rather than by
inspection. Tables 3(b) and 3(d) show the tables after the split. Two lassos,
one wrong name, Arnold's two shapes: the counterexample analysis is the
two-shape split of the congruence, run backwards.

*(a) `Even`, the stem chain `γ` — replace a growing stem prefix by its rep:*

| `i` | prefix | its rep | queried lasso | `γ_i` |
|:--:|---|:--:|---|:--:|
| 0 | — | — | `aa!a·(aa!a)^ω` | `1` |
| 1 | `a` | `a` | `a·a!a·(aa!a)^ω` | `1` |
| 2 | `aa` | `a` | `a·!a·(aa!a)^ω` | **`0`** |
| 3 | `aa!a` | `a` | `a·(aa!a)^ω` | `0` |

*(b) `Even`, after the stem harvest:*

| word | `(ε,ε)_ω` | **`(ε, !a, aa!a)_lin`** | class |
|---|:--:|:--:|---|
| `a` | `0` | **`0`** | `[a]` |
| `!a` | `1` | **`1`** | `[!a]` |
| **`aa`** | `0` | **`1`** | **`[aa]`** |
| *frontier:* | | | |
| `a·!a` | `0` | **`0`** | → `[a]` ✗ still |
| `aa·!a` | `1` | **`1`** | → `[!a]` |

*(c) `EvenBlocks`, the loop chain `δ` — stem pinned to `w_s = a`, replace a
growing loop prefix by its rep:*

| `i` | prefix | its rep | queried lasso | `δ_i` |
|:--:|---|:--:|---|:--:|
| 0 | — | — | `a·(!a·aa)^ω` | `1` |
| 1 | `!a` | `!a` | `a·(!a·aa)^ω` | `1` |
| 2 | `!a·a` | `a` | `a·(a·a)^ω` | **`0`** |
| 3 | `!a·aa` | `a` | `a·(a)^ω` | `0` |

*(d) `EvenBlocks`, after the loop harvest:*

| word | `(ε,ε)_ω` | **`(a, a)_ω`** | class |
|---|:--:|:--:|---|
| `a` | `0` | **`0`** | `[a]` |
| `!a` | `1` | **`0`** | `[!a]` |
| **`!a·a`** | `0` | **`1`** | **`[!a·a]`** |

**Table 3.** The two first counterexamples, processed (minted column and
promoted row in bold; `ε`-row and unchanged frontier omitted). In both
chains, row `i = 1` replaces a one-letter prefix by its own representative —
a no-op, bit unchanged — and the flips sit at `1 → 2`. In (a), row 3 is the
junction `γ_3 = δ_0`, already `0`: the stem chain flipped, minting a *linear*
column. In (c) the junction is `1` and the loop chain flips instead, minting
an *ω-column*; note row 3's lasso is `a·a^ω` — the representative lasso of
the predicting pair, i.e. the prediction itself, closing the chain. (a) pulls
`aa` out of `[a]`; (c) pulls `!a·a` out — and in (b) the doomed `a·!a` still
hides in `[a]`, which is §4.3's catch.
