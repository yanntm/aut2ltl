# Classifying an ω-Regular Language on its Syntactic ω-Semigroup

**Yann Thierry-Mieg**

With significant inputs from
**Claude (Anthropic)**

*Working draft — 2026-07-07 — extends §7 of [SωS26]*

This note expands §7 of the core paper [SωS26] into the decision procedures
themselves: for each band of the classification table — identity, the
aperiodic (LTL) cut, the safety–progress/topological ladder, the acceptance
index, and up to the exact Wagner degree — the algorithm that reads the
verdict off the invariant `𝓘(L)`, with its justification pinned to the
sources. It is standalone in the sense that every definition it uses is
restated; it relies on the core paper for the object itself (its
construction, canonicity, and the serialized `.sos` form). The engineering
companion is `sos_learner_spec.md`'s sibling, `sos_classifier_spec.md`.
Two closing sections leave the single language: §11 bounds what an entire
acceptance *family* of inputs can reach, and §12 reports the measured
Wagner-degree profile of the first systematically enumerated corpus.

The mathematical spine is Carton and Perrin's pair of papers on chains and
superchains [CP97, CP99]. Their theorems are stated on arbitrary recognizing
ω-semigroups and on Muller automata; what this note adds is the transport to
the invariant `𝓘(L) = (𝒞, λ, M, P)` — the syntactic ω-semigroup in its
exportable form — where each classification becomes a finite search in the
multiplication table, polynomial in `N = |𝒞|`. The exponential price was
paid once, constructing `𝓘(L)` [SωS26 §8]; everything below is cheap.
Around that spine: the ladder's verification vocabulary and its canonical
temporal-formula schemes are Manna and Pnueli's [MP92]; the bottom rungs,
their original cycle conditions, and the first effective classifier are
Landweber's [Lan69]; the complexity landscape on automaton *presentations*
— against which the algebra's read-offs are measured — is Selivanov and
Wagner's [SW08].

---

## 1. Input and claim

**Input.** The invariant `𝓘(L) = (𝒞, λ, M, P)` of [SωS26 §5]: the classes
`𝒞` of Arnold's syntactic congruence with the fresh identity `[ε]` adjoined,
the letter map `λ`, the multiplication table `M`, and the accepting
linked pairs `P ⊆ 𝒞 × 𝒞`. Write `𝒞₊ = 𝒞 \ {[ε]}` for the word classes —
the syntactic semigroup `S(L)₊` — and recall that a **linked pair** is
`(s, e)` with `e·e = e`, `s·e = s`, both in `𝒞₊`, and that membership of any
lasso is decided by folding to its linked pair and consulting `P`.

**Claim.** Every classification in this note is a function of `𝓘(L)` alone,
computed by table search — no automaton, no residuals block, no external
tool. The single exception is the tail of the Wagner degree (§8): when the
degree's recursion genuinely needs the *derivative* language, the procedure
re-enters through a presentation of `L`; the base invariants `m±`, `n±`,
`µ`, and the sign are still read off `𝓘(L)` directly.

**Why this is legitimate.** Chains and superchains — the two combinatorial
quantities the whole classification reduces to — are *syntactic invariants*:
a morphism that is syntactic with respect to `X` maps chains to chains
bijectively, preserving length and sign ([CP97, Prop. 7]), so their maximal
lengths "can be computed in any ω-semigroup recognizing the set `X`. In
particular, this can be done in the syntactic ω-semigroup of `X`"
([CP97, Cor. 1] for chains; [CP97, Thm. 5] with the same transfer for
superchains). The finite normal forms of §5–6 below ([CP97, Thms. 6, 7])
are what make the computation a search.

---

## 2. Primitives

Everything below reuses a small toolkit, computed once from `M`.

**Powers and idempotents.** For `c ∈ 𝒞₊` iterate `c, c², c³, …` until the
orbit closes; the orbit's cycle gives the **eventual period** `p(c)` and
contains exactly one idempotent power `c^k = c^{2k}`. Write `E ⊆ 𝒞₊` for
the set of idempotents. (The identity `[ε]` is excluded throughout: linked
pairs range over word classes [SωS26 §5].)

**Green's preorders** ([CP97, §6.1]). On `𝒞₊`, with `S¹` denoting "allow
the empty factor":

```
    s ≤_R t  ⟺  s ∈ t·S¹        (right-Cayley reachability)
    s ≤_L t  ⟺  s ∈ S¹·t        (left-Cayley reachability)
    s ≤_H t  ⟺  s ≤_R t and s ≤_L t
```

each computable as graph reachability in the right (resp. left) Cayley graph
of `M`. For **idempotents** the `H`-order has a one-line test
([CP97, §6.1]): `e ≤_H f ⟺ e·f = f·e = e`.

**Duality for free.** `𝓘(L̄)` is `𝓘(L)` with `P` complemented against the
set of all linked pairs [SωS26 §5]. Every procedure below therefore
classifies the complement at no extra cost, and the dualities it must
satisfy (`m⁺ ↔ m⁻`, `n⁺ ↔ n⁻`, `σ ↔ π`; [CP97, Props. 6, 10]) are the
classifier's cheapest correctness oracle.

---

## 3. Band 0 — identity

Read-offs of [SωS26, Thm. 5.1], stated for completeness because they pin the
conventions everything else uses:

- **equality** — two languages over the same `Σ` are equal iff their `𝓘`
  serializations are byte-equal;
- **complement** — flip `P` within the linked pairs;
- **emptiness** — `P = ∅`; **universality** — `P` is all linked pairs.

---

## 4. Band 1 — the aperiodic cut (LTL-definability)

`S(L)₊` is **aperiodic** iff every power orbit has eventual period 1:
`p(c) = 1` for all `c ∈ 𝒞₊`. By the classical chain of equivalences
assembled in [SωS26 §7.2], aperiodicity of the *syntactic* algebra is
exactly LTL-definability, in both directions and with no presentation
artifacts possible.

**Procedure.** Compute `p(c)` for every class (each orbit is at most `N`
products; `O(N²)` total). Report **LTL** iff all periods are 1; otherwise
report the **witness**: the first class `c` with `p(c) > 1` and its cycle
`{c^k, c^{k+1}, …, c^{k+p-1}}` — a genuine group in the canonical algebra,
the portable non-LTL certificate of [SωS26].

*On the examples.* `GF(aa)`: all periods 1 — LTL. `Even` and `EvenBlocks`:
the orbit `[a] → [a·a] → [a]` has period 2 — not LTL. (Values from the
tables of [SωS26 §4].)

---

## 5. Chains — the quantity `(m⁺, m⁻)`

**Definition** ([CP97, §4.1]). Let `S = (S₊, S_ω)` be an ω-semigroup and
`X ⊆ S_ω`. A pair `C = (Y, Z)`, with `Y ⊆ S₊` non-empty and
`Z = z₀, z₁, …, z_m` a sequence of elements of `S₊`, defines for
`Z_i = z₀ + ⋯ + z_i` the sets

```
    W_i = Y·Z_m^*·(Z_i^*·z_i)^ω        0 ≤ i ≤ m .
```

`C` is an **X-chain** iff the `W_i` are alternately included in `X` and
disjoint from `X`; its **length** is `m` (the number of alternations); it is
**positive** if `W₀ ⊆ X`, **negative** if `W₀ ∩ X = ∅`. `m⁺(X)` (resp.
`m⁻(X)`) is the maximal length of positive (resp. negative) X-chains, with
the convention `−1` when none exists; `m(X) = max(m⁺, m⁻)`. For ω-rational
`X` these are finite, `|m⁺ − m⁻| ≤ 1`, and complementation swaps them:
`m⁺(X) = m⁻(X̄)` ([CP97, Prop. 6]).

**The finite normal form** ([CP97, Thm. 6]). In a *finite* ω-semigroup,
from any X-chain a strong X-chain `C' = (Y', E)` of the same length and sign
may be deduced with `Y' = {s}` a singleton and `E = e₀, e₁, …, e_m` such
that

1. every `(s, e_i)` is a linked pair (`s·e_i = s`, `e_i² = e_i`), and
2. the sequence is strictly decreasing for the `H`-order:
   `e₀ >_H e₁ >_H ⋯ >_H e_m`.

**Transport to `𝓘(L)`.** Take `X` = the image of `L` in `S(L)_ω`, i.e.
membership of `(s, e)` in `P`. Two directions make the search exact:

- *Completeness.* By [CP97, Cor. 1] the chain numbers of `L` are those
  computed in the syntactic ω-semigroup, and by Theorem 6 every chain there
  reduces to the normal form — so searching normal forms alone misses
  nothing.
- *Soundness.* Every normal-form candidate **is** a chain. For idempotents,
  `e_i >_H e_j` (`i < j`) means `e_i·e_j = e_j·e_i = e_j` (§2), i.e. later
  idempotents absorb earlier ones. Then any element of `(E_i^*·e_i)^ω`
  collapses: each block of `E_i^*·e_i` multiplies out to `e_i` (the
  `H`-least factor absorbs the rest), so the ω-product is `e_i^ω` and
  `W_i = {s·e_i^ω}` — a singleton whose membership in `X` is exactly
  `(s, e_i) ∈ P`. The alternation of the `W_i` is the alternation of the
  pairs, and the linkage of intermediate pairs is automatic
  (`s·e_i = s·e_m·e_i = s·e_m = s`).

**Procedure.** Build the Hasse diagram of `(E, >_H)`. For each idempotent
`e` and each stem `s` with `s·e = s`, the candidate chains ending at `e` are
the `>_H`-descending paths through `E` ending at `e`, scored by the
alternation of `(s, ·) ∈ P` along the path. Longest-alternating-path by
dynamic programming over the DAG, once per stem: `m⁺` is the best score over
paths whose top pair is accepting, `m⁻` over rejecting tops. `O(N·|E|²)`.

*Worked instance (`GF(aa)`, table in [SωS26 §4]).* `E = {[!a], [!a·a],
[a·!a], [a·a]}`; `[a·a]` is the two-sided zero, so `[a·a] <_H e` for the
other three, which are pairwise `H`-incomparable. The only stem linked to
`[a·a]` is `[a·a]` itself. The pair `([a·a], [a·a])` is the unique accepting
pair, so the descent `[!a] >_H [a·a]` at stem `[a·a]` scores the alternation
(reject, accept): a **negative chain of length 1**, and no positive chain of
length 1 exists (an accepting top would force `e₀ = [a·a]`, which has
nothing below). Hence `m⁺ = 0`, `m⁻ = 1`.

---

## 6. Superchains — the quantity `(n⁺, n⁻)`

**Definition** ([CP97, §5.1]). An **X-superchain** of length `n` is a
sequence `C₀, C₁, …, C_n` of X-chains `C_i = (Y_i, Z_i)`, *all of maximal
length* `m = m(X)`, such that (i) each `C_i` is accessible from `C_{i−1}`:
there is `u_i ∈ S₊` with `Y_{i−1}·Z_{i−1}^*·u_i ⊆ Y_i`; and (ii) the chains
are alternately positive and negative. Signs and `n⁺(X)`, `n⁻(X)`,
`n(X) = max` as for chains (convention `−1` when empty). For ω-rational `X`:
`n(X)` is finite, `|n⁺ − n⁻| ≤ 1`, `n⁺(X) = n⁻(X̄)`, and `n(X) ≥ 1` forces
`m⁺(X) = m⁻(X)` ([CP97, Prop. 10]). Two maximal chains accessible from each
other have the same sign ([CP97, Prop. 11]) — accessibility between
maximal chains of opposite signs is strict.

**The finite normal form** ([CP97, Thm. 7]). In a finite ω-semigroup every
X-superchain reduces to `C'_i = (s_i, E_i)` where each `C'_i` is a Theorem-6
normal-form chain, and the stems are strictly decreasing for the `R`-order:
`s₀ >_R s₁ >_R ⋯ >_R s_n`.

**Transport to `𝓘(L)`.** Completeness as before (Theorem 7 plus the
morphism transfer of chains, [CP97 §4.4/§5]); soundness again by direct
check: for singleton chains, accessibility `s_{i−1}·E^*·u ⊆ {s_i}` is
exactly `s_i ∈ s_{i−1}·S₊` (the `E`-factors are absorbed into `s_{i−1}`),
which is `s_i <_R s_{i−1}`, strict by Proposition 11 once signs alternate.

**Procedure.** From §5, mark every stem `s` that carries a maximal-length
chain, with its available signs (a stem can carry both). `n⁺`/`n⁻` are the
longest sign-alternating, strictly `R`-descending paths through the marked
stems (DP over the `R`-order DAG restricted to `R`-classes of marked
stems), starting positive resp. negative. `O(N²)` after §5.

---

## 7. The read-offs: ladder and index as inequalities

The four integers `(m⁺, m⁻, n⁺, n⁻)` decide every rung of [SωS26 §7.1] and
the acceptance index of [SωS26 §7.3]. The characterizations are Carton and
Perrin's, stated on their Wagner-indexed classes `Σ_α / Π_α / Δ_α`
[CP99 §3–5]; the table gives all three namings — the verification
vocabulary with its canonical temporal scheme ([MP92 §4.2]; `p`, `q` range
over *past* formulas), the Wagner class, and the test.

| verdict (ladder / index name) | canonical scheme [MP92] | Wagner class | test on `𝓘(L)` | source |
|---|:--:|---|---|---|
| **guarantee** (open, co-safety) | `◇p` | `Σ₁` | `m = 0 ∧ n⁺ ≤ 0` | [CP99, Thm. 6] |
| **safety** (closed) | `□p` | `Π₁` | `m = 0 ∧ n⁻ ≤ 0` | dual of the above |
| level `n` of the boolean (Hausdorff) hierarchy over open | — | `Σ_n` | `m = 0 ∧ n⁺ ≤ n−1` | [CP99, Thm. 6] |
| **obligation / weak** (Staiger–Wagner, BC(open)) | `⋀ᵢ(□pᵢ ∨ ◇qᵢ)` | `Δ_ω` | `m = 0` | [CP99, Cor. 7] |
| **response / recurrence** (DBA-realizable; Borel `Gδ = Π⁰₂`) | `□◇p` | `Σ_ω` | `m⁺ ≤ 0` | [Lan69, Thms. 3.3, 4.5; CP99, Thm. 11] |
| **persistence** (DCA-realizable; Borel `Fσ = Σ⁰₂`) | `◇□p` | `Π_ω` | `m⁻ ≤ 0` | dual |
| deterministic **parity of length `m`** (priorities `{0,…,m}`) | — | `Σ_{ω^m}` | `m⁺ ≤ m−1` | [CP99, Thm. 11] |
| co-parity of length `m` | — | `Π_{ω^m}` | `m⁻ ≤ m−1` | dual |
| coarse Wagner class ((m, n−1)-superparity-realizable) | — | `Σ_{ω^m·n}` | `m(X) < m`, or `m(X) = m ∧ n⁺ ≤ n−1` | [CP99 §3, Thm. 14] |
| **reactivity** | `⋀ᵢ(□◇pᵢ ∨ ◇□qᵢ)` | — | always (m, n finite, [CP97 Props. 6, 10]) | — |

On the vocabulary column: [MP92 §4.2] defines each class as the properties
specifiable by its canonical scheme, and proves obligation is *the largest
class obtained by finite boolean combinations of safety and guarantee
properties* — the algebraic test `m = 0` is that closure made checkable.
The scheme column also explains the two names of the `□◇` rung: Manna and
Pnueli say *response* (every stimulus is answered), the topological
tradition says *recurrence*; the core paper's §7.1 uses both.

One naming caution, worth a box: **Carton–Perrin's `Σ_ω` is the rational
`Gδ` class** — Wagner-hierarchy indexing puts the DBA class on the `Σ` side,
while Borel notation calls the same class `Π⁰₂` (Landweber's own notation is
`G₂` for `Gδ`, `F₂` for `Fσ` [Lan69 §2]). The core paper's §7.1 speaks
Borel; this table is the dictionary.

The table's history is worth one paragraph, because it *is* the history of
this classifier. Landweber 1969 already decided the bottom of the ladder
effectively: his Theorem 4.1 characterizes the open sets of a Muller
automaton by a condition on realizable cycles, his Theorem 4.2 the `Gδ`
sets by a **union-closure** condition — `D ∈ 𝒟 ∩ 𝓗_s` and `E ∈ 𝓗_s` imply
`D ∪ E ∈ 𝒟`, accepting cycles absorb co-reachable cycles — and his
Theorems 4.3–4.4 assemble "an effective procedure for deciding the
complexity of `T(𝓜)` … whether `T(𝓜)` is in `G₁, F₁, G₂, F₂` or
`G₃ ∩ F₃`" [Lan69 §4]: a five-verdict classifier on presentations, in
1969. Wagner's chains, in Carton–Perrin's algebraic form, subsume those
conditions and extend them to the whole hierarchy — and the correspondence
is visible in Theorem 6's construction (§5): each next idempotent
`e_{i+1} = (e_i·z_{i+1}·e_i)^π` loops through strictly more behavior, so
descending the `H`-order is Landweber's cycle growth, and `m⁺ ≤ 0` — no
accepting pair with a rejecting `H`-descendant — is his union-closure
condition transported to the algebra, where "realizable cycle at `s`"
has become "idempotent linked to `s`".

The **minimal deterministic acceptance** of [SωS26 §7.3] falls out of the
parity rows: the least `m` with `m⁺ ≤ m−1` is the minimal parity length for
`L`, the least `m` with `m⁻ ≤ m−1` the minimal one for `L̄`, and the pair
locates the exact parity/Rabin index — Büchi at `(m⁺ ≤ 0)`, co-Büchi at
`(m⁻ ≤ 0)`, weak at `m = 0`, a genuine Rabin pair strictly above.

---

## 8. The Wagner degree

The complete invariant is Wagner's, in Carton–Perrin's ordinal form
[CP99 §3]. From `(m, n⁺, n⁻)` define

```
    µ(X) = n(X)                 if m(X) = 0 and n⁺(X) ≠ n⁻(X)
         = ω^m(X) · (n(X)+1)    otherwise

    s(X) = σ  if n⁻ > n⁺          (then s(X̄) = π)
         = π  if n⁻ < n⁺
         = δ  if n⁻ = n⁺ and m = 0
         = s(∂X)  otherwise

    γ(X) = µ(X)                 if m(X) = 0 or n⁺(X) ≠ n⁻(X)
         = µ(X) + γ(∂X)         otherwise .
```

The pair `ϕ(X) = (γ(X), s(X))` is a **complete invariant for the Wadge
preorder on ω-rational sets**: `ϕ(X) ≤ ϕ(Y) ⟺ X` reduces continuously to
`Y` ([CP99, Thm. 4] — Wagner's theorem). The sum defining `γ` is the Cantor
normal form of an ordinal `< ω^ω`.

**The self-dual degrees, named.** The sign `δ` arises in two ways. Directly,
when `m = 0` and `n⁺ = n⁻ = n`: then `µ = ω⁰·(n+1) = n+1`, so the degree is
`(n+1, δ)` with coordinates `(0, 0, n, n)` — by the §7 table these languages
lie in `Σ_{n+1} ∩ Π_{n+1}` and in neither `Σ_n` nor `Π_n`, i.e. they are
exactly the **properly `Δ_{n+1}`** level of the boolean hierarchy. In
particular `(1, δ)`, coordinates `(0, 0, 0, 0)`, is the **nontrivial clopen**
class — both the open and the closed test of §7 pass — properly `Δ₁`, one
notch *below* the properly open/closed pair, not above it; the first properly
`Δ₂` degree is `(2, δ)`, coordinates `(0, 0, 1, 1)`. Indirectly, `δ`
propagates through the derivative (`s(X) = s(∂X)` below), producing self-dual
degrees with infinite `γ` — §9's fourth specimen is one. Profile tables
should name these levels by this dictionary.

**When the recursion is needed.** Only in the case `m ≥ 1 ∧ n⁺ = n⁻` does
`γ` involve the **derivative** `∂X` — Wagner's derivation, realized by
Carton–Perrin as an automaton transformation `∂𝒜` (collapse the states
reaching maximal positive resp. negative superchains onto two fresh sinks;
[CP99 §3]) with `m(∂X) < m(X)`, so the recursion terminates within `m(X)`
steps. On all other inputs — including every language whose maximal
superchains are of a single sign — `γ = µ` and the degree is a direct
read-off of `𝓘(L)`.

**Procedure.** Compute `(m±, n±)` (§5–6), then `µ` and the sign. If
`m = 0 ∨ n⁺ ≠ n⁻`, emit `ϕ = (µ, s)` and stop. Otherwise construct `∂X`
from a deterministic presentation of `L` via `∂𝒜`, rebuild `𝓘(∂X)` by the
construction of [SωS26], and recurse — the one step in this note that leaves
the single invariant. Whether the derivative's `(m±, n±)` can be read off
`𝓘(X)` directly, without rebuilding, is left open here as a research
direction; nothing downstream depends on it.

---

## 9. The triptych, classified

The three running examples of [SωS26], classified end to end on their
published tables — the values below are hand-computed from `𝓘` alone and
double as fixtures for the implementation.

*`Even`, in full.* From `S(Even)₊¹` ([SωS26, Table 3b];
`P = {([!a],[!a]), ([!a],[a·!a]), ([!a],[a·a])}`): the idempotents are
`E = {[!a], [a·!a], [a·a]}`; the `H`-order has `[a·a]` on top with `[!a]`
and `[a·!a]` strictly below it and incomparable to each other. Stems linked
to `[!a]` are `{[!a], [a·!a]}`; to `[a·!a]`, `{[!a], [a·!a]}`; every
`H`-descent tops out at `[a·a]`, whose linked stems are `{[!a], [a·!a],
[a·a], [a]}`-checked against `M`. Exhausting the two descents against their
admissible stems yields *no* alternation anywhere — every stem sees
constant acceptance along both descents — so all chains have length 0:
`m⁺ = m⁻ = 0`, `Even` is **weak**. Superchains: the positive pairs all have
stem `[!a]`, which is `R`-minimal (`[!a]·S₊ = {[!a]}`), so no positive
superchain extends: `n⁺ = 0`. Negatively, `([a],[a·a]) ∉ P` at the
`R`-maximal class of `[a]`, descending strictly to `[!a]` with
`([!a],[!a]) ∈ P`: `n⁻ = 1`, and `[!a]` ends the descent. So
`(m⁺, m⁻, n⁺, n⁻) = (0, 0, 0, 1)`: **open, not closed** (guarantee);
`µ = n = 1`, `s = σ`, `γ = 1` — `ϕ(Even) = (1, σ)`, the exact class
`Σ₁ − Π₁`: *properly* open.

| | `m⁺` | `m⁻` | `n⁺` | `n⁻` | `µ` | `γ` | `s` | `ϕ` | reading |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|---|
| `Even` | 0 | 0 | 0 | 1 | 1 | 1 | σ | `(1, σ)` | properly open — guarantee, weak, not closed |
| `GF(aa)` | 0 | 1 | −1 | 0 | ω | ω | σ | `(ω, σ)` | properly `Gδ` — DBA/recurrence, not DCA, not weak |
| `EvenBlocks` | 1 | 2 | −1 | 0 | ω² | ω² | σ | `(ω², σ)` | properly parity-`{0,1,2}` — one genuine Rabin pair, neither DBA nor DCA |

The `EvenBlocks` row deserves its two witnesses, both at the zero class
`z = [!a·a·!a]` (the only stem linked to `z`, and `z <_H` every idempotent):
the descent `[a·a] >_H [!a] >_H z` scores (reject, accept, reject) — a
negative chain of length 2 — and `[a·a] >_H [a·!a·a] >_H z` scores the
same; the positive best is `[!a] >_H z` at `z`, (accept, reject), length 1.
So `m⁺ = 1 < m⁻ = 2`: `L` fits a deterministic parity automaton with
priorities `{0, 1, 2}` and nothing shorter, while `L̄` needs `{1, 2, 3}` —
the asymmetry `m⁺(X) = m⁻(X̄)` made concrete. All maximal chains being
negative, `n⁺ = −1 ≠ n⁻ = 0` and no derivation is needed anywhere in the
triptych.

Every row satisfies the internal laws `|m⁺ − m⁻| ≤ 1`, `|n⁺ − n⁻| ≤ 1`, and
`n ≥ 1 ⟹ m⁺ = m⁻` ([CP97, Props. 6, 10]) — the consistency web the
implementation inherits as free assertions.

**A fourth specimen: `Fork`, into the derivative.** Nothing in the triptych —
and, by Proposition 11.1, nothing in any generalized-Büchi corpus — reaches
the derivative regime `m ≥ 1 ∧ n⁺ = n⁻` of §8. The regime needs maximal
chains of both signs (`m⁺ = m⁻ ≥ 1`) whose stems no superchain connects, and
the minimal recipe is to route between a properly-`Gδ` and a properly-`Fσ`
behavior on the first letter:

```
    Fork  =  (a ∧ GF a) ∨ (¬a ∧ FG ¬a)
```

over the single atom `a`: a word starting with `a` must carry infinitely many
`a`, a word starting with `!a` finitely many. `Fork` is LTL-definable — the
derivative regime is orthogonal to the aperiodic cut of §4.

*The invariant.* A nonempty word acts only through its first letter and
whether it contains an `a`, so `S(Fork)₊¹` has four classes
`[ε], [!a], [a], [!a·a]` — first letter `a` (hence containing one), first
letter `!a` without / with a later `a`. Products keep the left factor's first
letter and accumulate the contains-`a` bit: `[a]` and `[!a·a]` are
left-absorbing, `[!a]·[a] = [!a]·[!a·a] = [!a·a]`, `[!a]·[!a] = [!a]`. All
three word classes are idempotent, so the algebra is aperiodic. The accepting
pairs, each checked on its lasso:

```
    P = { ([a],[a]),  ([a],[!a·a]),  ([!a],[!a]),  ([!a·a],[!a]) }
```

(`a·a^ω` and `a·(!a·a)^ω` recur `a` after an `a`-start; `!a·(!a)^ω` and
`!a·a·(!a)^ω` see finitely many `a` after a `!a`-start).

*Chains.* On `E = {[!a], [a], [!a·a]}` the `H`-order has the single strict
descent `[!a] >_H [!a·a]` (each product of the two is `[!a·a]`); `[a]` is
`H`-isolated (`[!a]·[a] = [!a·a] ≠ [a]`). The descent admits the stems `[a]`
and `[!a·a]`. At stem `[a]` it scores (reject, accept) — `([a],[!a]) ∉ P`,
`([a],[!a·a]) ∈ P` — a **negative chain of length 1**; at stem `[!a·a]` it
scores (accept, reject) — a **positive chain of length 1**. The Hasse diagram
has depth two, so `m⁺ = m⁻ = 1`.

*Superchains.* The two maximal chains sit at stems `[a]` (negative) and
`[!a·a]` (positive), and both stems are `R`-minimal singletons
(`[a]·S₊ = {[a]}`, `[!a·a]·S₊ = {[!a·a]}`), mutually unreachable: no
superchain of length 1 exists in either sign, `n⁺ = n⁻ = 0`.

*The degree, through the derivative.* `m = 1` and `n⁺ = n⁻`:
`µ = ω¹·(0+1) = ω` and, for the first time, §8's recursion is genuinely
needed. On the three-state presentation below, the derivation `∂` of
[CP99 §3] collapses the two maximal-chain basins — the `a`-successor
component (negative) onto a rejecting sink, the `!a`-successor (positive)
onto an accepting sink — leaving `∂Fork = !a·Σ^ω`: nontrivial clopen,
`ϕ(∂Fork) = (1, δ)` by §8's dictionary. Hence

```
    γ(Fork) = µ + γ(∂Fork) = ω + 1,      s(Fork) = s(∂Fork) = δ .
```

| | `m⁺` | `m⁻` | `n⁺` | `n⁻` | `µ` | `γ` | `s` | `ϕ` | reading |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|---|
| `Fork` | 1 | 1 | 0 | 0 | ω | ω+1 | δ | `(ω+1, δ)` | self-dual, off every rung — the derivative regime, one derivation |

The first composite ordinal and the first recursive sign: `Fork` is
self-dual (its complement is the same construction with the branches
swapped), fails all five rung tests of §7, has parity and co-parity length
both 2, and needs exactly one derivation. The duality laws hold on the nose:
`m⁺ ↔ m⁻` and `n⁺ ↔ n⁻` are fixed points, `δ ↔ δ`, `γ` equal.

*The presentation.* `Fork` has a three-state deterministic EL automaton:
initial `q_ι` with `δ(q_ι, a) = q_a`, `δ(q_ι, !a) = q_b`; `q_a` and `q_b`
each a sink of self-loops; marks `{0,1}` on `q_a`'s `a`-loop, `{1}` on
`q_a`'s `!a`-loop, `{1}` on `q_b`'s `a`-loop, none on `q_b`'s `!a`-loop;
acceptance `Inf(0) ∨ Fin(1)`. A run through `q_a` sees mark `1` forever, so
acceptance reduces to `Inf(0)` — infinitely many `a`; a run through `q_b`
never sees `0`, so it reduces to `Fin(1)` — finitely many `a`. This is the
K4 fixture of the engineering companion: exit 2 with `PARTIAL(ω)` from the
`.sos` alone, `ϕ = (ω+1, δ)` with the presentation supplied.

---

## 10. Complexity, and the point

Every procedure above is a polynomial search in the table: power orbits
`O(N²)`; the Green preorders, graph reachability; chains, a
longest-alternating-path DP over the idempotent Hasse DAG per admissible
stem; superchains, the same over the `R`-order; the degree, arithmetic on
the results plus at most `m(X)` derivations. Carton and Perrin note that on
*presentations* the picture is harsher — computing `m(𝒜)` is NP-complete
for Rabin automata, polynomial for Muller and parity ones (results of
Krishnan–Puri–Brayton and of Wilke–Yoo, reported in [CP97, §7]) — which
sharpens the division of labor: the hardness lives in getting from a
presentation to the canonical object ([SωS26 §8], PSPACE-hard already for
the aperiodicity coordinate), and once `𝓘(L)` is in hand the entire
classification tower, Wagner degree included, is a cheap read-off. That is
[SωS26 §7]'s "semantic benchmark" claim, made executable: one object in,
every verdict out, each with a witness — a group cycle, an alternating
chain, a superchain descent — that is itself a set of lassos replayable
against any presentation of `L`.

---

## 11. What an acceptance family can reach

The classifications above are per-language. One step up, the same machinery
bounds an entire *input family*: the acceptance condition a corpus of
deterministic automata is allowed to carry fixes, a priori, which Wagner
degrees the corpus can contain at all — no matter how many states, colours,
or letters are enumerated.

**Proposition 11.1 (generalized-Büchi spectrum).** Let `L` be recognized by a
deterministic, complete automaton whose acceptance is
`Inf(c₀) ∧ ⋯ ∧ Inf(c_{k−1})` (generalized Büchi, any `k ≥ 1`). Then
`m⁺(L) ≤ 0`, and the Wagner degree of `L` is one of

```
    (0, σ), (0, π)                        —  the trivial pair (empty / universal),
    (n, s),  1 ≤ n < ω,  s ∈ {σ, π, δ}    —  the weak (boolean-hierarchy) levels,
    (ω, σ)                                —  properly Gδ ,
```

and every degree in the list is attained already by a deterministic Büchi
automaton (`k = 1`). In particular the derivative regime `m ≥ 1 ∧ n⁺ = n⁻`
of §8 — which forces `m⁺ = m⁻ ≥ 1` — is unreachable: on such a corpus
`γ = µ` always, and a classifier without the derivation is complete.

*Proof.* For deterministic complete `D` the run over `α` is a letter-by-letter
function of `α`, so `{α : the run visits mark c infinitely often}`
`= ⋂_n {α : the run visits c after step n}` is a `Gδ` set; a finite
conjunction of `Inf` is a finite intersection of `Gδ` sets, hence `Gδ`, i.e.
`m⁺(L) ≤ 0` by the §7 table. Case `m⁺ = −1`: no positive chain means no
accepting pair, `L = ∅`, degree `(0, σ)`. Case `m⁺ = 0, m⁻ = −1`: dually `L`
is universal, `(0, π)`. Case `m⁺ = m⁻ = 0`: `L` is weak; both signs carry
maximal (length-0) chains, so `n⁺, n⁻ ≥ 0` and §8 gives `γ = µ` finite `≥ 1`
with any of the three signs. Case `m⁺ = 0, m⁻ = 1` (`|m⁺ − m⁻| ≤ 1` allows no
more): every maximal chain is negative, and a superchain of length `≥ 1`
needs maximal chains of both signs, so `(n⁺, n⁻) = (−1, 0)`:
`µ = ω¹·(0+1) = ω`, `s = σ`, `γ = µ`. Attainment with `k = 1`: weak and
properly-`Gδ` languages are DBA-realizable (`m⁺ ≤ 0`, §7), and every listed
degree is inhabited [Wag79]. Finally `n⁺ = n⁻ ≥ 0` requires maximal chains of
both signs, i.e. `m⁺ = m⁻`, contradicting `m⁺ ≤ 0` once `m ≥ 1`. ∎

The contrast, off the same §7 rows: a deterministic **parity** condition with
priorities `{0, …, k}` recognizes exactly the languages with `m⁺ ≤ k − 1`
([CP99, Thm. 11]) — the full `ω^k` band of the hierarchy, superchain
dimension unbounded — and a general Emerson–Lei (equivalently Muller)
condition reaches every ω-regular degree. Three consequences for corpus
design. First, a census's degree ceiling is set by its acceptance family
*before* its state count: generalized-Büchi enumeration, however exhaustive,
stays inside Proposition 11.1's list. Second, the `Fin`/`Inf`-alternating
(parity) family is the cheapest door to the deep degrees. Third, the
derivative regime needs maximal chains of both signs in `R`-incomparable
basins — a `Fork`-shaped budget (§9): at least a routing state plus two
components, and an acceptance able to accept in one component and co-accept
in the other. Conversely the proposition is a free corpus-level oracle: a
generalized-Büchi input classified outside the list is a bug, in the
classifier or in the corpus's acceptance labeling.

---

## 12. The profile, measured

The engineering companion's classifier, run over the genaut census
(iteration 1, 2026-07-07): **18 239** deterministic, complete,
transition-based automata with **generalized-Büchi** acceptance
`Inf(0) ∧ ⋯ ∧ Inf(c−1)`, exhaustively enumerated over small shape families
(states × atomic propositions × colours × guard alphabet), plus the triptych
and two stall specimens as the only non-generalized-Büchi inputs. For every
input the reference invariant `𝓘(L)` was built by the construction of
[SωS26 §8] and classified; the duality gate and the internal laws of §5–6 ran
on every case. Result: 18 239 SOUND, zero law violations, zero over budget,
zero PARTIAL — and the first measured Wagner-degree profile of a
systematically enumerated ω-language class:

| `ϕ = (γ, s)` | `(m⁺, m⁻, n⁺, n⁻)` | class (§7–8 dictionary) | count |
|---|---|---|--:|
| `(0, σ)` | `(−1, 0, −1, 0)` | empty | 16 |
| `(0, π)` | `(0, −1, 0, −1)` | universal | 352 |
| *— the trivial pair, set apart: the weakest class —* | | | *368* |
| `(1, δ)` | `(0, 0, 0, 0)` | clopen (properly `Δ₁`) | 470 |
| `(1, σ)` | `(0, 0, 0, 1)` | properly open — guarantee | 68 |
| `(1, π)` | `(0, 0, 1, 0)` | properly closed — safety | 15 432 |
| `(2, σ)` | `(0, 0, 1, 2)` | properly `Σ₂` | 5 |
| `(2, π)` | `(0, 0, 2, 1)` | properly `Π₂` | 6 |
| `(ω, σ)` | `(0, 1, −1, 0)` | properly `Gδ` — DBA-proper | 1 887 |
| `(ω, π)` | `(1, 0, 0, −1)` | properly `Fσ` — DCA-proper | 2 |
| `(ω², σ)` | `(1, 2, −1, 0)` | parity-`{0,1,2}`-proper | 1 |

The table is ordered by Wagner degree, weakest first. 12 205 of the languages
are LTL-definable, 6 034 are not: the aperiodic axis cuts across the degree
rows, as §7.1 of the core paper promised.

Three readings. **The profile is Proposition 11.1, verified.** Every row lies
in the generalized-Büchi list except the three outliers — `(ω, π)` twice and
`(ω², σ)` once — and those are exactly the non-generalized-Büchi inputs: the
two stall specimens and `EvenBlocks` (`Even` and `GF(aa)` fold into the
`(1, σ)` and `(ω, σ)` rows). The zero-PARTIAL column is likewise the
proposition's prediction, not luck: no generalized-Büchi input *can* need the
derivative. And the pilot extension of the generator with a parity acceptance
family confirms the converse immediately: a single one-state parity shape
(98 surviving languages) realizes `(ω², σ)` eighteen times and `(ω, π)`
thirty times — degrees the 18 239-case generalized-Büchi census reaches once
and twice respectively, and only through hand-made specimens. **The census
is heavily one-sided.** Properly-closed languages dominate (15 432 against
68 properly open): the enumeration meets each dual pair on one side, chosen
by how `Inf`-acceptance interacts with small shapes — the duality gate, which
classifies both sides of every case, is what keeps the other side honest.
**The cost claim of §10 holds.** Classification never exceeded 0.039 s on any
input and every budget slot is empty; the practical ceiling met throughout
was the construction of `𝓘(L)`, never the read-off.

Two per-shape quantities are queued for the next iteration's manifest
(engineering spec §5), both read off the same run. *How many languages does a
shape carry?* Distinct-`𝓘` counts per shape family — Theorem 5.1's hash join
makes counting languages, rather than automata, a one-pass operation, and a
shape's automaton-to-language compression ratio is a datum no other tool
computes. *How big are the algebras, and does size track depth?* The
distribution of `N = |𝒞|` per shape, cross-tabulated against the degree. The
dependence is one-directional: a chain of length `m` needs `m + 1` strictly
`H`-descending idempotents and a superchain of length `n` needs `n + 1`
strictly `R`-descending stems, so a deep degree forces `N` up — but not
conversely, since a large algebra can be topologically shallow (a safety
language with an intricate finite-word core keeps `N` high at degree
`(1, π)`, while `EvenBlocks` reaches `ω²` with `N = 8`). The expected picture
is triangular — deep degrees only above a size floor, shallow degrees at
every size — and where the census sits inside that triangle measures what
small shapes actually exercise.

---

## References

- **[CP97]** O. Carton, D. Perrin. *Chains and superchains for ω-rational
  sets, automata and semigroups.* Int. J. Algebra Comput. 7(6) (1997)
  673–695.
- **[CP99]** O. Carton, D. Perrin. *The Wagner hierarchy.* Int. J. Algebra
  Comput. 9(5) (1999) 597–620.
- **[SωS26]** Y. Thierry-Mieg, with Claude (Anthropic). *Constructing the
  syntactic ω-semigroup from a deterministic Emerson–Lei automaton.* Working
  draft, 2026 (`research_notes/sos_constructed.md`).
