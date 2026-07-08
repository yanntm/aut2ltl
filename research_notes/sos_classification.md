# Classifying an ω-Regular Language from its Syntactic ω-Semigroup

**Yann Thierry-Mieg**

With significant inputs from
**Claude (Anthropic)**

*Working draft — 2026-07-08 — extends §7 of [SωS26]*

## Abstract

The syntactic ω-semigroup of a regular ω-language `L` is its canonical
algebra; the core paper [SωS26] constructs it from any deterministic
Emerson–Lei automaton and reifies it as the exportable invariant
`𝓘(L) = (𝒞, λ, M, P)`. This note turns the classification claims of
[SωS26 §7] into decision procedures: for each band of the classification
table — identity, the aperiodic (LTL) cut, the safety–progress/topological
ladder, the acceptance index, and up to the exact Wagner degree — an
algorithm that reads the verdict off `𝓘(L)` by finite search in the
multiplication table, polynomial in `N = |𝒞|`. The searches transport
Carton and Perrin's chains and superchains to the invariant. One step
resists the transport: Wagner's derivative is not an algebraic operation —
no re-marking of the accepting pairs computes it (Proposition 8.1) — yet it
remains a table computation, running on the right regular representation
with the marking unchanged and the admissible stems shrinking
(Theorem 8.5). Beyond the single language, a spectrum theorem bounds the
Wagner degrees any generalized-Büchi input family can reach
(Proposition 11.1), and a reference catalogue of 3938 small ω-languages —
every language small deterministic automata realize, counted once up to
atom renaming and closed under complement — yields the first measured
Wagner-degree profile of such a class: 43% of it lies beyond LTL, the
profile is exactly duality-symmetric, and every internal consistency law
holds on every case.

## Introduction

The core paper [SωS26] builds the syntactic ω-semigroup of a regular
ω-language `L` from any deterministic Emerson–Lei automaton and exports it
as the invariant `𝓘(L) = (𝒞, λ, M, P)`: the classes of Arnold's syntactic
congruence, the letter map, the multiplication table, and the accepting
linked pairs. Its §7 argues that the classical taxonomy of ω-regular
languages — the safety–progress and topological hierarchies, the acceptance
index, LTL-definability, and, subsuming them all, the exact Wagner degree —
is a taxonomy of that one object's structure. This note is that section
made effective: the decision procedures themselves, each pinned to its
source theorem, each a finite search in the multiplication table. The
exponential price was paid once, constructing `𝓘(L)` [SωS26 §8];
everything below is polynomial in `N = |𝒞|`.

**Contributions.**

- *The transport* (§5–7). Chains and superchains — the two combinatorial
  quantities the whole classification reduces to — are computed exactly on
  `𝓘(L)`: completeness comes from Carton and Perrin's transfer theorems,
  soundness of the normal-form search is proved directly on the table, and
  every rung of the ladder and the acceptance index becomes an inequality
  on four integers `(m⁺, m⁻, n⁺, n⁻)` (§7).
- *An obstruction* (Proposition 8.1). The Wagner derivative `∂X` — the
  recursion step of Carton–Perrin's ordinal formula — is not an algebraic
  operation: there is an `X` whose derivative is not saturated by the
  syntactic congruence of `X`, so no re-marking of the accepting pairs of
  `𝓘(X)` recognizes `∂X`.
- *Its bypass* (Theorem 8.5). The derivation is nonetheless a table
  computation: on the right regular representation of `𝓘(X)` it becomes a
  restriction of the admissible stems — the marking never changes, the same
  chain and superchain engines run at every level, the recursion trace is
  the Cantor normal form of the degree, and every level's witnesses are
  lassos over `𝒞`.
- *A spectrum bound* (Proposition 11.1). The acceptance family of an input
  corpus fixes, a priori, which Wagner degrees it can reach: deterministic
  generalized-Büchi inputs never need the derivative and stay within an
  explicit finite list of degrees.
- *A measured profile* (§12). Over a reference catalogue of 3938 small
  ω-languages — systematically enumerated, deduplicated up to atom
  renaming, closed under complement — the classifier produces the first
  measured Wagner-degree profile of such a class: 43% non-LTL, a profile
  exactly symmetric under duality, Proposition 11.1's spectrum verified
  with its converse, and every consistency law holding on every case.

**Related work.** Priority for computing the Wagner degree on the syntactic
ω-semigroup belongs to Cabessa and Duparc [CD09a, CD09b], who reach it by a
route that never forms the derivative; §8.3 details the relation, and the two
procedures cross-validate each other. The mathematical spine is Carton and
Perrin's pair of papers on chains and superchains [CP97, CP99]: their
theorems are stated on arbitrary recognizing ω-semigroups and on Muller
automata, and what this note adds at each step is the transport to `𝓘(L)`.
Around that spine: the ladder's verification vocabulary and its canonical
temporal-formula schemes are Manna and Pnueli's [MP92]; the bottom rungs,
their original cycle conditions, and the first effective classifier are
Landweber's [Lan69]; the complexity landscape on automaton *presentations*
— against which the algebra's read-offs are measured — is Selivanov and
Wagner's [SW08].

The note is self-contained — every definition it uses is restated — and
relies on the core paper only for the object itself: its construction,
canonicity, and serialized `.sos` form. §1 fixes the input and the claim,
§2 the toolkit. §§3–4 dispatch the identity band and the aperiodic cut.
§§5–6 compute chains and superchains, §7 reads the ladder and the index off
them, and §8 computes the Wagner degree, derivative included. §9 classifies
the running examples end to end, §10 collects the complexity. §11 and §12
leave the single language: the spectrum bound for acceptance families, and
the measured profile. The implementation and the experimental protocol are
documented in the engineering companion [Spec26, Rep26].

---

## 1. Input and claim

**Input.** The invariant `𝓘(L) = (𝒞, λ, M, P)` of [SωS26 §5]: the classes
`𝒞` of Arnold's syntactic congruence with the fresh identity `[ε]` adjoined,
the letter map `λ`, the multiplication table `M`, and the accepting
linked pairs `P ⊆ 𝒞 × 𝒞`. Write `𝒞₊ = 𝒞 \ {[ε]}` for the word classes —
the syntactic semigroup `S(L)₊` — and `𝒞¹` for the same set `𝒞` used
multiplicatively, `[ε]` acting as the unit (so `t·𝒞¹ = {t} ∪ t·𝒞₊`), and
recall that a **linked pair** is
`(s, e)` with `e·e = e`, `s·e = s`, both in `𝒞₊`, and that membership of any
lasso is decided by folding to its linked pair and consulting `P`. Write
`φ : Σ⁺ → 𝒞₊` for the syntactic morphism — a word folds letter by letter
through `λ` and `M` — so the lasso `u·z^ω` folds to the pair `(φ(u)·e, e)`
with `e` the idempotent power (§2) of `φ(z)`.

**Claim.** Every classification in this note — the Wagner degree included,
derivative tail and all — is a function of `𝓘(L)` alone, computed by table
search: no automaton presentation, no residuals block, no external tool.
One step earns that claim rather than inheriting it: the degree's derivative
recursion provably cannot be carried by a re-marking of `P`
(Proposition 8.1), and runs instead on the right regular representation of
the same table — the marking never changes, the admissible stems shrink
(Theorem 8.5).

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
contains exactly one idempotent power `c^k = c^{2k}`, written `c^π`. Write
`E ⊆ 𝒞₊` for
the set of idempotents. (The identity `[ε]` is excluded throughout: linked
pairs range over word classes [SωS26 §5].)

**Green's preorders** ([CP97, §6.1]). On `𝒞₊`, with `𝒞¹` allowing the
empty factor (§1):

```
    s ≤_R t  ⟺  s ∈ t·𝒞¹        (right-Cayley reachability)
    s ≤_L t  ⟺  s ∈ 𝒞¹·t        (left-Cayley reachability)
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

Read-offs of [SωS26, Thm. 5.1], restated to fix the conventions used
throughout:

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
artifacts possible. The cut is also complement-blind: the test reads only
`M`, and `𝓘(L̄)` differs only in `P` (§2).

**Procedure.** Compute `p(c)` for every class (each orbit is at most `N`
products; `O(N²)` total). Report **LTL** iff all periods are 1; otherwise
report the **witness**: the first class `c` (in shortlex key order) with
`p(c) > 1` and its cycle
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

(Products, `+`, `*` and `(·)^ω` are lifted to sets — `+` is union, each
`z_i` read as a singleton, `(·)^ω` the set of infinite products — so each
`W_i ⊆ S_ω`.)
`C` is an **X-chain** iff the `W_i` are alternately included in `X` and
disjoint from `X`; its **length** is `m` (the number of alternations); it is
**positive** if `W₀ ⊆ X`, **negative** if `W₀ ∩ X = ∅`. `m⁺(X)` (resp.
`m⁻(X)`) is the maximal length of positive (resp. negative) X-chains, with
the convention `−1` when none exists; `m(X) = max(m⁺, m⁻)`. For ω-rational
`X` these are finite, `|m⁺ − m⁻| ≤ 1`, and complementation swaps them:
`m⁺(X) = m⁻(X̄)` ([CP97, Prop. 6]).

**The finite normal form** ([CP97, Thm. 6]). In a *finite* ω-semigroup,
every X-chain yields one of the same length and sign in **normal form**
`C' = ({s}, E)`: a singleton stem and a sequence `E = e₀, e₁, …, e_m` of
idempotents such that

1. every `(s, e_i)` is a linked pair (`s·e_i = s`, `e_i² = e_i`), and
2. the sequence is strictly decreasing for the `H`-order:
   `e₀ >_H e₁ >_H ⋯ >_H e_m`.

**Transport to `𝓘(L)`.** Take `X` = the image of `L` in `S(L)_ω`, i.e.
membership of `(s, e)` in `P`. Two directions make the search exact:

- *Completeness.* By [CP97, Cor. 1] the chain numbers of `L` are those
  computed in the syntactic ω-semigroup, and by [CP97, Thm. 6] every chain
  there reduces to the normal form — so searching normal forms alone misses
  nothing.
- *Soundness.* Every normal-form candidate **is** a chain. For idempotents,
  `e_i >_H e_j` (`i < j`) means `e_i·e_j = e_j·e_i = e_j` (§2), i.e. later
  idempotents absorb earlier ones. Then any element of `(E_i^*·e_i)^ω`
  collapses: each block of `E_i^*·e_i` multiplies out to `e_i` (the
  `H`-least factor absorbs the rest), so the ω-product is `e_i^ω`; the
  finite factor `E_m^*` is absorbed into the stem the same way
  (`s·e_j = s` for every `j`, the linkage fact below), so
  `W_i = {s·e_i^ω}` — a singleton whose membership in `X` is exactly
  `(s, e_i) ∈ P`. The alternation of the `W_i` is the alternation of the
  pairs, and the linkage of intermediate pairs is automatic
  (`s·e_i = s·e_m·e_i = s·e_m = s`).

**Procedure.** Compute the strict order `>_H` on `E` — as a DAG this is the
full order relation, at most `|E|²` edges, not its Hasse covers: a chain may
skip levels. For each idempotent `e` and each stem `s` with `s·e = s`, the
candidate chains ending at `e` are the `>_H`-descending sequences through
`E` ending at `e`, scored by the alternation of `(s, ·) ∈ P` along the
sequence. Longest-alternating-sequence by dynamic programming over the DAG,
once per stem: `m⁺` is the best score over sequences whose top pair is
accepting, `m⁻` over rejecting tops. `O(N·|E|²)`.

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
X-superchain reduces to `C'_i = (s_i, E_i)` where each `C'_i` is a
normal-form chain ([CP97, Thm. 6]), and the stems are strictly decreasing
for the `R`-order:
`s₀ >_R s₁ >_R ⋯ >_R s_n`.

**Transport to `𝓘(L)`.** Completeness as before (the normal form
[CP97, Thm. 7] plus the morphism transfer of chains, [CP97 §4.4/§5]);
soundness again by direct
check: for singleton chains, accessibility `s_{i−1}·E^*·u ⊆ {s_i}` is
exactly `s_i ∈ s_{i−1}·𝒞₊` (the `E`-factors are absorbed into `s_{i−1}`),
which is `s_i <_R s_{i−1}`, strict by [CP97, Prop. 11] once signs
alternate.

**Procedure.** From §5, mark every stem `s` that carries a maximal-length
chain, with its available signs (a stem can carry both). `n⁺`/`n⁻` are the
longest sign-alternating, strictly `R`-descending paths through the marked
stems (DP over the `R`-order DAG restricted to `R`-classes of marked
stems), starting positive resp. negative. `O(N²)` after §5.

*Worked instance (`GF(aa)`, continued).* Every maximal (length-1) chain of
§5 is negative, at the single stem `[a·a]`: no sign alternation is
available, and `n⁺ = −1`, `n⁻ = 0`.

---

## 7. The read-offs: ladder and index as inequalities

The four integers `(m⁺, m⁻, n⁺, n⁻)` decide every rung of [SωS26 §7.1] and
the acceptance index of [SωS26 §7.3]. The characterizations are Carton and
Perrin's, stated on their Wagner-indexed classes `Σ_α / Π_α / Δ_α`
[CP99 §3–5]: for an ordinal `α < ω^ω`, `Σ_α` is the class of languages of
Wagner degree at most `(α, σ)` in the sense of §8, `Π_α` its dual, and
`Δ_α = Σ_α ∩ Π_α`. The table gives all three namings — the verification
vocabulary with its canonical temporal scheme ([MP92 §4.2]; `p`, `q` range
over *past* formulas), the Wagner class, and the test.

| verdict (ladder / index name) | canonical scheme [MP92] | Wagner class | test on `𝓘(L)` | source |
|---|:--:|---|---|---|
| **guarantee** (open, co-safety) | `◇p` | `Σ₁` | `m = 0 ∧ n⁺ ≤ 0` | [CP99, Thm. 6] |
| **safety** (closed) | `□p` | `Π₁` | `m = 0 ∧ n⁻ ≤ 0` | dual of the above |
| level `k` of the boolean (Hausdorff) hierarchy over open | — | `Σ_k` | `m = 0 ∧ n⁺ ≤ k−1` | [CP99, Thm. 6] |
| **obligation / weak** (Staiger–Wagner, BC(open)) | `⋀ᵢ(□pᵢ ∨ ◇qᵢ)` | `Δ_ω` | `m = 0` | [CP99, Cor. 7] |
| **response / recurrence** (DBA-realizable; Borel `Gδ = Π⁰₂`) | `□◇p` | `Σ_ω` | `m⁺ ≤ 0` | [Lan69, Thms. 3.3, 4.5; CP99, Thm. 11] |
| **persistence** (DCA-realizable; Borel `Fσ = Σ⁰₂`) | `◇□p` | `Π_ω` | `m⁻ ≤ 0` | dual |
| deterministic **parity of length `k`** (priorities `{0,…,k}`) | — | `Σ_{ω^k}` | `m⁺ ≤ k−1` | [CP99, Thm. 11] |
| co-parity of length `k` | — | `Π_{ω^k}` | `m⁻ ≤ k−1` | dual |
| coarse Wagner class ((k, l−1)-superparity-realizable) | — | `Σ_{ω^k·l}` | `m < k`, or `m = k ∧ n⁺ ≤ l−1` | [CP99 §3, Thm. 14] |
| **reactivity** | `⋀ᵢ(□◇pᵢ ∨ ◇□qᵢ)` | — | always (m, n finite, [CP97 Props. 6, 10]) | — |

On the vocabulary column: [MP92 §4.2] defines each class as the properties
specifiable by its canonical scheme, and proves obligation is *the largest
class obtained by finite boolean combinations of safety and guarantee
properties* — the algebraic test `m = 0` is that closure made checkable.
The scheme column also explains the two names of the `□◇` rung: Manna and
Pnueli say *response* (every stimulus is answered), the topological
tradition says *recurrence*; the core paper's §7.1 uses both.

**Remark (naming).** Carton–Perrin's `Σ_ω` is the **rational `Gδ` class** —
Wagner-hierarchy indexing puts the DBA class on the `Σ` side,
while Borel notation calls the same class `Π⁰₂` (Landweber's own notation is
`G₂` for `Gδ`, `F₂` for `Fσ` [Lan69 §2]). The core paper's §7.1 speaks
Borel; this table is the dictionary.

**Remark (history).** Landweber 1969 already decided the bottom of the
ladder effectively: his Theorem 4.1 characterizes the open sets of a Muller
automaton by a condition on realizable cycles, his Theorem 4.2 the `Gδ`
sets by a **union-closure** condition — `D ∈ 𝒟 ∩ 𝓗_s` and `E ∈ 𝓗_s` imply
`D ∪ E ∈ 𝒟`, accepting cycles absorb co-reachable cycles — and his
Theorems 4.3–4.4 assemble "an effective procedure for deciding the
complexity of `T(𝓜)` … whether `T(𝓜)` is in `G₁, F₁, G₂, F₂` or
`G₃ ∩ F₃`" [Lan69 §4]: a five-verdict classifier on presentations, in
1969. Wagner's chains, in Carton–Perrin's algebraic form, subsume those
conditions and extend them to the whole hierarchy — and the correspondence
is visible in the construction behind [CP97, Thm. 6] (§5): each next
idempotent
`e_{i+1} = (e_i·z_{i+1}·e_i)^π` loops through strictly more behavior, so
descending the `H`-order is Landweber's cycle growth, and `m⁺ ≤ 0` — no
accepting pair with a rejecting `H`-descendant — is his union-closure
condition transported to the algebra, where "realizable cycle at `s`"
has become "idempotent linked to `s`".

The **minimal deterministic acceptance** of [SωS26 §7.3] falls out of the
parity rows: the least `k` with `m⁺ ≤ k−1` is the minimal parity length for
`L`, the least `k` with `m⁻ ≤ k−1` the minimal one for `L̄`, and the pair
locates the exact parity/Rabin index — Büchi at `(m⁺ ≤ 0)`, co-Büchi at
`(m⁻ ≤ 0)`, weak at `m = 0`, a genuine Rabin pair strictly above.

---

## 8. The Wagner degree

§7 read every rung of the ladder and the acceptance index off the four
integers `(m⁺, m⁻, n⁺, n⁻)`. Above all the rungs sits the complete
invariant: the **Wagner degree**, which classifies ω-rational languages
exactly up to continuous reducibility and refines everything computed so
far. Carton and Perrin give the degree in ordinal form, as a formula in the
same quantities [CP99 §3] — a direct read-off of `𝓘(L)`, except in one
tied case, where the formula recurses through a *derivative* `∂X` of the
language. That recursion is the one step of the classification that resists
the transport to the algebra, and it structures the section: §8.1 restates
the formula and the derivative from [CP99], in enough detail to be read
without returning to that paper; §8.2 proves the two results this note
adds — the derivative is *not* an algebraic operation (no re-marking of the
accepting pairs of `𝓘(X)` recognizes `∂X`, Proposition 8.1), yet it *is* a
computation on the multiplication table once the table is read as a machine
(the marking never changes, only the admissible stems shrink,
Theorem 8.5); §8.3 places both results against Cabessa and Duparc's
earlier, derivative-free route to the same degree.

### 8.1 The ordinal formula and Wagner's derivative

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
`Y`, i.e. `X = f⁻¹(Y)` for some continuous `f : Σ^ω → Σ^ω`
([CP99, Thm. 4] — Wagner's theorem). Degrees are ordered by
`(γ, s) ≤ (γ′, s′)` iff `γ < γ′`, or `γ = γ′` and (`s = s′` or `s = δ`):
at equal `γ` the self-dual sign `δ` sits below the incomparable pair
`σ`, `π`. The sum defining `γ` is the Cantor normal form of an ordinal
`< ω^ω`.

**The self-dual degrees, named.** The sign `δ` arises in two ways. Directly,
when `m = 0` and `n⁺ = n⁻ = n`: then `µ = ω⁰·(n+1) = n+1`, so the degree is
`(n+1, δ)` with coordinates `(0, 0, n, n)` — by the §7 table these languages
lie in `Σ_{n+1} ∩ Π_{n+1}` and in neither `Σ_n` nor `Π_n`, i.e. they are
exactly the **properly `Δ_{n+1}`** level of the boolean hierarchy. In
particular `(1, δ)`, coordinates `(0, 0, 0, 0)`, is the **nontrivial clopen**
class — both the open and the closed test of §7 pass — properly `Δ₁`, one
notch *below* the properly open/closed pair, not above it; the first properly
`Δ₂` degree is `(2, δ)`, coordinates `(0, 0, 1, 1)`. Indirectly, `δ`
propagates through the derivative (`s(X) = s(∂X)`, the last clause of `s`
above), producing self-dual
degrees with infinite `γ` — §9's fourth specimen is one. The profile table
of §12 names these levels by this dictionary.

**Reading the formula.** Only one branch is not a direct read-off of the
§5–6 numbers. When `m = 0`, or when one sign dominates the maximal
superchains (`n⁺ ≠ n⁻`), `γ = µ` is a single term and the degree is
immediate from `𝓘(L)`. The remaining case `m ≥ 1 ∧ n⁺ = n⁻` is a *tie*:
the maximal nests chain equally far under either leading sign, a symmetry
the four integers cannot resolve, and there — and only there — the formula
recurses through the **derivative** `∂X`, Wagner's derivation, realized by
Carton–Perrin as an automaton transformation [CP99 §3] and restated below.
Since `m(∂X) < m(X)`, the recursion terminates within `m(X)` steps, and its
successive terms `µ₀, µ₁, …` have strictly decreasing exponents: the sum
they form is the Cantor normal form of `γ`. The analogy with polynomials is
exact — each derivative lowers the leading exponent and exposes the next
coefficient of the degree. §8.2 shows how to run this recursion without
leaving the table: not by re-marking `P` (that is provably impossible), but
through the right regular representation.

**Chains on an automaton** ([CP99 §2]). On a deterministic Muller automaton
the same quantities take a loop form: a chain of length `m` at a state `q`
is a nest of loops `R₀ ⊂ R₁ ⊂ ⋯ ⊂ R_m` around a common base state reachable
from `q`, alternately accepting and rejecting for the acceptance table
(positive if `R₀` accepts); a superchain is a sequence of maximal-length
nests, each reachable from the last, alternately signed. These automaton
quantities coincide with the language quantities `m^±`, `n^±`
([CP99, Thms. 1–2]).

**The derivative, informally.** In the tied case, sort the states of a
deterministic automaton for `X` into three zones by what remains reachable:
a state is *committed positive* if the full positive superchain structure
is still accessible from it but the negative one no longer is, *committed
negative* dually, and *undecided* if both are still accessible (states
retaining neither are grouped with the committed-negative zone). The
derivation truncates every run at the moment of commitment — entering the
committed-positive zone accepts immediately, entering the committed-negative
zone rejects immediately — and retains only the undecided core. `∂X` is
thus the part of `X` decided before either commitment, a strictly simpler
language: every maximal nest dies in the collapse.

**A running example.** Over `Σ = {a, b, c, d}` take the *escape language*

```
    X = c*·a·K⁻ ∪ c*·b·K⁺ ,     K⁺ = {α ∈ {a,b}^ω : infinitely many a} ,
                                K⁻ = {α ∈ {a,b}^ω : finitely many a} ,
```

so any occurrence of `d`, or of `c` past the leading `c`-block, is fatal.
Its evident deterministic presentation has six states:

```
          COMMITTED +           UNDECIDED            COMMITTED −
   ┌───────────────────┐    c ⟲ ┌───────┐       ┌───────────────────┐
   │ K⁻ : finitely     │        │ hub h │       │ K⁺ : infinitely   │
   │      many a       │◀── a ──┤       ├─ b ──▶│      many a       │
   │   all-b loop  ✓   │        └───┬───┘       │   all-b loop  ✗   │
   │   full loop   ✗   │          d │           │   full loop   ✓   │
   │   = positive nest │     ┌──────▼─────┐     │   = negative nest │
   └───────────────────┘     │  ⊥  (dead) │     └───────────────────┘
                             └────────────┘
                            no nest reachable
        (transitions not drawn are fatal: they lead to ⊥)

     one maximal nest of each sign, mutually unreachable:
     m⁺ = m⁻ = 1 ,  n⁺ = n⁻ = 0  —  the tied case
```

The `K⁻`-component carries a positive chain of length 1 (its all-`b` loop
is accepting inside its rejecting full loop), the `K⁺`-component the dual
negative chain; the two components are mutually unreachable, and no loop
combines the hub with a component (the hub is left forever on its first
`a` or `b`), so no nest reaches depth 3: `m⁺ = m⁻ = 1`, `n⁺ = n⁻ = 0` —
the derivative regime, in its smallest instance.

**The derivation, precisely** ([CP99 §3]). Let `𝒜 = (Q, i, T)` — states,
initial state, accepting family `T ⊆ 2^Q` of infinity sets — be a
deterministic complete Muller automaton recognizing `X`, with `m(X) ≥ 1` and
`n⁺ = n⁻ = n`. Call a state *positive* (resp. *negative*) if a maximal —
length `n`, sign `+` (resp. `−`) — superchain is accessible from it, and
write `Q⁺`, `Q⁻`; the zones of the informal picture are `Q⁺ − Q⁻` and
`Q⁻ − Q⁺` (committed) and `Q⁺ ∩ Q⁻` (undecided). The derived automaton
`∂𝒜` keeps `Q⁺ ∩ Q⁻`, adds an accepting sink `q₊` and a rejecting sink
`q₋`, redirects every transition
entering `Q⁺ − Q⁻` to `q₊` and every other transition leaving `Q⁺ ∩ Q⁻` to
`q₋`, and accepts by `{S ⊆ Q⁺∩Q⁻ : S ∈ T} ∪ {{q₊}}`. The definition is
deliberately asymmetric: states from which *no* maximal superchain is
accessible are merged with `q₋` [CP99 §3]. Then `∂𝒜` recognizes a language
`∂X` that depends only on `X` ([CP99, Prop. 3] — their §3 also gives the
presentation-free form `∂X = (X − V_X·Σ^ω) ∪ U_X·Σ^ω`, where `U_X` collects
the finite words whose future retains the full positive but not the full
negative superchain structure, and `V_X` those whose future has lost `m` or
`n⁺`), and `m(∂X) < m(X)`, so the recursion of `γ` terminates within `m(X)`
steps.

On the running example the collapse is immediate — the hub keeps only its
(rejecting) `c`-loop, `a` commits positive, `b` and `d` negative, the dead
sink merging into `q₋`:

```
                      c ⟲ ┌───────┐
                          │ hub h │        kept: Q⁺ ∩ Q⁻ = {h}
                          └┬─────┬┘
                       a   │     │  b, d
                   ┌───────▼─┐ ┌─▼────────┐
                   │  q₊  ✓  │ │  q₋  ✗   │
                   └─────────┘ └──────────┘
        K⁻ collapsed into q₊ ;  K⁺ and ⊥ both merged into q₋

        ∂X = c*·a·Σ^ω  —  properly open,  ϕ(∂X) = (1, σ)

  recursion trace:  level 0   (m, n⁺, n⁻) = (1, 0, 0)     →  µ₀ = ω
                    level 1   ∂X: (0, 0, 1), tie broken   →  µ₁ = 1 , s = σ
                    γ(X) = ω + 1  —  the trace is the Cantor normal form
```

### 8.2 The derivative leaves the algebra — but not the table

One could hope the derivation is an algebraic operation: that `∂X` is
recognized by `𝓘(X)` itself under a re-marked accepting set `P′`, so that
the recursion of `γ` never leaves the invariant. The running example
refutes this. Trace two ω-words through its six-state presentation:

```
              in X ?     trajectory                          in ∂X ?
   a·d^ω        ✗        h ──a──▶ K⁻ ──d──▶ ⊥                   ✓
   d^ω          ✗        h ──d──▶ ⊥                             ✗
```

No left context rescues either word — every `u·a·d^ω` and every `u·d^ω`
lies outside `X` — so the syntactic congruence of `X` identifies them. Yet
the first entered the committed-positive zone before reaching the sink and
the second did not, and `∂X` separates them. Hence:

**Proposition 8.1.** There is an ω-rational `X` with `m = 1`, `n⁺ = n⁻ = 0`
whose derivative is not saturated by the syntactic congruence of `X`: no
marking `P′` of the linked pairs of `𝓘(X)` recognizes `∂X`.

*Proof.* The escape language of §8.1, with `∂X = c*·a·Σ^ω` as computed
there. Then `a·d^ω ∈ ∂X` and `d^ω ∉ ∂X`, yet for every `u ∈ Σ^*` neither
`u·a·d^ω` nor `u·d^ω` is in `X` — no left context separates them, so the
two ω-words have the same image in the ω-component of the syntactic
ω-semigroup, and any language recognized by `𝓘(X)`, under any marking of
its linked pairs, is a union of such image classes: it contains both or
neither. ∎

The failure is structural, not an artifact of the example: membership in
`∂X` records whether the prefix trajectory *visited* the committed region
`Q⁺ − Q⁻`, an event the ω-image — which only remembers where the
trajectory *ends up* — cannot see.

**The bypass: the table as a machine.** The object that does carry the
derivation is the **right regular representation** of `𝓘(X)`: the *Cayley
automaton* `A_X` with states `𝒞`, initial `[ε]`, transitions
`t · a := t·λ(a)`, and accepting family
`T_X = {S : S admissible, pair(S) ∈ P}`. Here `S ⊆ 𝒞` is
**admissible** iff it is the infinity set of some run of `A_X`; such an `S`
is contained in one `R`-class and folds to a linked pair
`pair(S) = (s, φ(w)^π)` — base `s ∈ S`, loop word `w` covering `S` — and
conjugacy invariance of `P` (a linked pair and its conjugates carry the same
verdict [PP04, Ch. II]) makes the choices immaterial, so `A_X`
recognizes `X`. `A_X` *is* the table read as a machine — its runs are
trajectories over `𝒞`, and a trajectory retains exactly the visit
information the ω-image discards. Applying the derivation to it stays a
table search, by the following three steps.

**Lemma 8.2 (transport at a location).** For every `t ∈ 𝒞`: the
`A_X`-chains (resp. superchains) accessible from state `t` correspond,
preserving length and sign, to the normal-form chains (superchains) of §5–6
whose stem (top stem) lies in `t·𝒞¹`.

*Proof sketch.* Realization: a normal-form chain `(s, e₀ >_H ⋯ >_H e_m)`
yields nested loops at state `s` — loop `R_i` reads one word of each of
`e₀, …, e_i` in order (the product collapses to `e_i` by absorption), so
`R_{i−1} ⊆ R_i` and `pair(R_i) = (s, e_i)`; alternation of the `P`-bits
forces the inclusions strict. Superchain connectors become Cayley paths.
Extraction: from nested accessible loops `R₀ ⊂ ⋯ ⊂ R_m` at a base `s′`, take
`e₀ := φ(v₀)^π` for a loop word `v₀` of `R₀`, and
`e_{i+1} := (e_i·z_{i+1}·e_i)^π` where `z_{i+1}` is the product of a loop of
`R_{i+1}` threaded through the `R_i`-loop — the construction of
[CP97, Thm. 6] — giving an `H`-descent at stem `s′` with the same bits
(each `e_{i+1}` absorbs `e_i` on both sides by construction, strictly since
the alternating `P`-bits force `e_{i+1} ≠ e_i`); for
superchains the connecting paths give `R`-descents, strict by
[CP97, Prop. 11]. Accessibility from `t` is right multiplication, i.e.
membership in `t·𝒞¹`, in both directions. ∎

**Corollary 8.3 (zones).** `Q^±(A_X) = T^± := {t ∈ 𝒞 : some maximal
±-superchain has its top stem in t·𝒞¹}` — unions of `R`-classes (plus
`[ε]`, which is in both), computed from §6's DP output by one right-Cayley
reachability pass. Write `U := T⁺ − T⁻` and `B := T⁺ ∩ T⁻` (the kept
states).

**Lemma 8.4 (committed tops).** The top stem of a maximal positive
superchain lies in `U`; dually for negative.

*Proof.* If a maximal negative superchain were accessible from the top stem
`s₀`, prepending `s₀`'s (positive, maximal) top chain to it would give a
positive superchain of length `n+1`, contradicting `n⁺ = n`. ∎

Three consequences. (i) Every element of `B` reaches, inside its `R`-ideal,
both a `U`-element and a `T⁻−T⁺`-element — in `∂A_X` both sinks are
admissible. (ii) A stem carrying a maximal chain is never in `B` (its chain
would prepend as above) — all maximal chains die in the collapse, and
`m(∂X) < m(X)` falls out in one line. (iii) `B` is `≤_R`-upward closed
(`t ∈ t′·𝒞¹` gives `t·𝒞¹ ⊆ t′·𝒞¹`, so `t′` inherits `t`'s reachable tops),
and a Cayley path between `B`-elements never leaves `B`: accessibility
inside the kept part is plain ideal containment.

**Theorem 8.5 (derivation on the invariant).** Let `X` be in the derivative
regime. Then the classification data of `∂X` are computed on `𝓘(X)` by the
§5–6 engines with the marking `P` **unchanged** and the stems **restricted**
to those whose `R`-class lies in `B`:

- `m^±(∂X) = max(0, restricted §5 numbers)` — each sink contributes a
  length-0 chain of its sign and nothing longer (a loop containing an
  absorbing sink is that sink alone);
- if `m′ := m(∂X) ≥ 1`: `n^±(∂X)` are the restricted §6 numbers (the sinks
  carry no `m′`-chain);
- if `m′ = 0`: the §6 search additionally allows each descent to end with
  one virtual stem of sign opposite to its last chain — a sink, accessible
  from every `B`-stem, from which nothing continues — and the empty descent
  with a single sink floors both signs at `0`.

The `γ`/`s` recursion then proceeds with these numbers, re-zoning within `B`
(the level-`k` superchain tops within `B_k` give `B_{k+1} ⊆ B_k`; the
previous sinks, carrying no maximal chain once the recursion continues, are
merged into the new `q₋`). It terminates in at most `m(X)` levels; each
level costs one engine pass, `O(N·|E|² + N²)`; the recursion trace
`µ₀, µ₁, …` is the Cantor normal form of `γ`, with `s` read at the last
level; and every level's witnesses remain lassos over `𝒞`.

*Proof.* By Corollary 8.3 the derived Cayley automaton `∂A_X` is exactly the
zone collapse of the table; by [CP99, Prop. 3] it recognizes `∂X`; by
[CP99, Thms. 1–2] its chains and superchains (in the loop form above)
compute `m^±(∂X)`, `n^±(∂X)`.
Its admissible loops are the two sink loops plus the Cayley loops at
`B`-stems (a loop stays inside one `R`-class, and `B` is a union of
`R`-classes); its internal accessibility is ideal containment
(Lemma 8.4 (iii)); and Lemma 8.2 converts its chains and superchains into
the restricted normal-form searches, strictness both ways by
[CP97, Prop. 11]. For `m′ = 0` the maximal chains of `∂A_X` are its linked
pairs, the two sink pairs included; a superchain passes through a sink only
as its final element (the sinks are absorbing), which is the virtual stem,
and the sinks alone realize the empty-descent floor. Termination is
Lemma 8.4 (ii). ∎

**Procedure.** Compute `(m±, n±)` (§5–6), then `µ` and the sign. If
`m = 0 ∨ n⁺ ≠ n⁻`, emit `ϕ = (µ, s)` and stop. Otherwise compute the
superchain tops and the zones (Corollary 8.3), restrict the stems to `B`,
and recurse by Theorem 8.5 — never leaving the multiplication table.

**Worked checks.** On `Fork` (§9): the negative maximal chain's stem `[a]`
is its own `R`-ideal, so `[a] ∈ T⁻−T⁺`; `[!a]` and `[!a·a]` lie in
`T⁺−T⁻` (a `!a`-prefix has already committed: `[!a·a] ∈ [!a]·𝒞¹` tops the
positive chain, and no negative top does). Hence `B ∩ 𝒞₊ = ∅`: the kept part
is the hub `[ε]` alone, the restricted engines see only the two sinks,
`(m′, n′⁺, n′⁻) = (0, 0, 0)`, `ϕ(∂Fork) = (1, δ)`, `γ(Fork) = ω + 1` — the
§9 record, no presentation touched. On the running example of §8.1: the
single `B`-pair `([c], [c])` is rejecting; descending from it to `q₊` gives
`n′⁻ = 1 > n′⁺ = 0`, so `ϕ(∂X) = (1, σ)` and `γ(X) = ω + 1`, `s = σ` — the
trace of §8.1's collapse figure, recovered without ever building the
six-state presentation. [CP99]'s own Example 4 (their Figs. 4–5) has the
same shape, and their published `γ(X₃) = ω + 1` agrees.

### 8.3 Discussion: two routes to the degree

The gap this section closes was first crossed, by a different route, by
Cabessa and Duparc [CD09a, CD09b]: they prove the Wagner degree is a
syntactic invariant, define a Wadge-like reduction game directly on finite
pointed ω-semigroups, and give an algorithm ([CD09b, Alg. 4.1]) computing
the degree — sign and self-duality included — by a single backward
induction over the DAG of `R`-classes of stems, each node labeled by the
sign and length of a *main vein* (a maximal sign-alternating idempotent
chain in the node's flower, refining [CP97, Thm. 6]); the ordinal
composition rule along the DAG absorbs both the superchain count and the
derivative recursion, which their procedure never forms. Priority for
computing the degree on the syntactic ω-semigroup is therefore theirs.

What the present section adds is complementary. Proposition 8.1: the
derivative *itself* is not an algebraic operation — which is why [CP99]'s
own recursion stalls at presentations, and why a bypass like [CD09b]'s, or
a change of object like Theorem 8.5's, is necessary rather than convenient.
Theorem 8.5: the derivative-faithful form — [CP99]'s actual recursion
running on the invariant through its right regular representation, reusing
the §5–6 engines unchanged, with a lasso witness at every level and the
recursion trace as the Cantor normal form.

The two procedures compute the same value by disjoint routes — a one-pass
DAG labeling against a re-zoned recursion — and their agreement over a
corpus is the natural cross-oracle for an implementation of either
([CD09b] states no complexity bound; both routes are polynomial in `N`).

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
[a·a], [a]}`, checked against `M`. Exhausting the two descents against their
admissible stems yields *no* alternation anywhere — every stem sees
constant acceptance along both descents — so all chains have length 0:
`m⁺ = m⁻ = 0`, `Even` is **weak**. Superchains: the positive pairs all have
stem `[!a]`, which is `R`-minimal (`[!a]·𝒞₊ = {[!a]}`), so no positive
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

The `EvenBlocks` row's two witnesses both sit at the zero class
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
letter and accumulate the contains-`a` bit — in full (`λ(!a) = [!a]`,
`λ(a) = [a]`):

```
 ·        [ε] [!a] [a] [!a·a]
[ε]        0   1    2    3
[!a]       1   1    3    3
[a]        2   2    2    2
[!a·a]     3   3    3    3
```

`[a]` and `[!a·a]` are left-absorbing, `[!a]·[a] = [!a]·[!a·a] = [!a·a]`,
`[!a]·[!a] = [!a]`. All
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
scores (accept, reject) — a **positive chain of length 1**. The `H`-order
has depth two, so `m⁺ = m⁻ = 1`.

*Superchains.* The two maximal chains sit at stems `[a]` (negative) and
`[!a·a]` (positive), and both stems are `R`-minimal singletons
(`[a]·𝒞₊ = {[a]}`, `[!a·a]·𝒞₊ = {[!a·a]}`), mutually unreachable: no
superchain of length 1 exists in either sign, `n⁺ = n⁻ = 0`.

*The degree, through the derivative.* `m = 1` and `n⁺ = n⁻`:
`µ = ω¹·(0+1) = ω` and, for the first time, §8's recursion is genuinely
needed. On the three-state presentation below, the derivation `∂` of
[CP99 §3] collapses the two maximal-chain basins — the `a`-successor
component (negative) onto a rejecting sink, the `!a`-successor (positive)
onto an accepting sink — leaving `∂Fork = !a·Σ^ω`: nontrivial clopen,
`ϕ(∂Fork) = (1, δ)` by §8.1's dictionary. Hence

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
never sees `0`, so it reduces to `Fin(1)` — finitely many `a`. `Fork` is a
fixture of the implementation [Spec26]: by Theorem 8.5 its degree is read
off `𝓘(Fork)` alone — the table derivation collapses all of `𝒞₊` into the
two sinks and returns `ϕ(∂Fork) = (1, δ)` directly (§8.2, worked checks) —
and the presentation-level derivation of [CP99 §3], run on this three-state
automaton, is kept as an independent cross-check of the collapse.

---

## 10. Complexity

Every procedure above is a polynomial search in the table: power orbits
`O(N²)`; the Green preorders, graph reachability; chains, a
longest-alternating-path DP over the idempotent order DAG per admissible
stem; superchains, the same over the `R`-order; the degree, arithmetic on
the results plus at most `m(X)` derivation levels, each one more engine pass
on a shrunken stem set (§8.2, Theorem 8.5). Carton and Perrin note that on
*presentations* the picture is harsher — computing `m(𝒜)` is NP-complete
for Rabin automata, polynomial for Muller and parity ones (results of
Krishnan–Puri–Brayton and of Wilke–Yoo, reported in [CP97, §7]) — which
sharpens the division of labor: the hardness lives in getting from a
presentation to the canonical object ([SωS26 §8], PSPACE-hard already for
the aperiodicity coordinate), and once `𝓘(L)` is in hand the entire
classification tower, Wagner degree included, is a cheap read-off.

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
maximal (length-0) chains, so `n⁺, n⁻ ≥ 0` and §8.1 gives `γ = µ` finite `≥ 1`
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
in the other. The state budget is sharp: the two basins are mutually
unreachable yet both reachable, so neither contains the initial state and
three states are the floor — and three suffice, since `Fork`'s
`Inf(0) ∨ Fin(1)` acceptance (§9) is a two-colour (min-even) parity
condition. A parity census therefore first meets the derivative regime at
that three-state, two-colour shape; no two-state sample, however long, can
produce one. Conversely the proposition is a free corpus-level oracle: a
generalized-Büchi input classified outside the list is a bug, in the
classifier or in the corpus's acceptance labeling.

---

## 12. The profile, measured

The measured object is the **reference catalogue** of the engineering
companion [Spec26, Rep26]: every ω-language realized by a small
deterministic, complete, transition-based automaton, **counted once**. From
19 shape families (states × atomic propositions × colours × acceptance
family, within 3 states, 3 atoms, 3 colours) exhaustively enumerated across
the **generalized-Büchi** and **parity** acceptance families, plus one
uniform random sample of a two-state, two-colour parity shape beyond the
enumeration wall (id-space `4.3·10⁹`), the sweep's redundancies are folded
— sub-shape inclusion, unused atoms, and renaming/polarity of the atoms
(the invariant is minimized over its letter-permutation orbit, an operation
[SωS26, Thm. 5.1] makes exact) — and the result is **closed under
complement**, a step that is free at the invariant level (§2: same table,
`P` flipped). The funnel: 3790 languages at a fixed labeling → 2007 up to
renaming (the **primals**: 1764 exhaustively enumerated, 243 sampled) →
**3938** languages once complement-closed. Each language carries its
classification as a corpus artifact, a pure read-off of its stored `𝓘(L)`
— no automaton, no external tool, about one second for the whole catalogue
— with the internal laws of §5–6 and the witness replay asserted on every
case: zero violations, zero partial verdicts.

**The aperiodic cut.** 2240 of the 3938 languages are LTL-definable and
1698 — **43%** — are not: among the small ω-languages, genuine ω-counting
is not a corner case but almost half the population. The cut is
complement-blind (§4), so it splits the primals in the same proportion
(1142 LTL / 865 non-LTL of 2007).

**The profile**, ordered by Wagner degree, weakest first — `non-LTL` is
the row's share beyond the aperiodic cut, `primals` its shape-realized
share (the rest are added complements):

| `ϕ = (γ, s)` | `(m⁺, m⁻, n⁺, n⁻)` | class (§7–8 dictionary) | languages | non-LTL | primals |
|---|---|---|--:|--:|--:|
| `(0, σ)` | `(−1, 0, −1, 0)` | empty | 1 | 0 | 1 |
| `(0, π)` | `(0, −1, 0, −1)` | universal | 1 | 0 | 1 |
| `(1, δ)` | `(0, 0, 0, 0)` | clopen — properly `Δ₁` | 62 | 0 | 36 |
| `(1, σ)` | `(0, 0, 0, 1)` | properly open — guarantee | 1356 | 678 | 4 |
| `(1, π)` | `(0, 0, 1, 0)` | properly closed — safety | 1356 | 678 | 1356 |
| `(2, σ)` | `(0, 0, 1, 2)` | properly `Σ₂` | 4 | 0 | 4 |
| `(2, π)` | `(0, 0, 2, 1)` | properly `Π₂` | 4 | 0 | 1 |
| `(ω, σ)` | `(0, 1, −1, 0)` | properly `Gδ` — DBA-proper | 466 | 98 | 365 |
| `(ω, π)` | `(1, 0, 0, −1)` | properly `Fσ` — DCA-proper | 466 | 98 | 128 |
| `(ω·2, σ)` | `(1, 1, 0, 1)` | one Rabin pair — `σ` side (superchain `n = 1`) | 12 | 12 | 0 |
| `(ω·2, π)` | `(1, 1, 1, 0)` | one Rabin pair — `π` side (superchain `n = 1`) | 12 | 12 | 12 |
| `(ω², σ)` | `(1, 2, −1, 0)` | parity-`{0,1,2}`-proper | 99 | 61 | 99 |
| `(ω², π)` | `(2, 1, 0, −1)` | co-parity-`{0,1,2}`-proper | 99 | 61 | 0 |

The trivial pair sits apart below the hierarchy proper; the triptych sits
inside the spectrum, and `γ` never exceeds `ω²`. Four readings.

**The duality laws, as a corpus identity.** The `languages` column is
exactly symmetric under `σ ↔ π` — 1 = 1, 1356 = 1356, 4 = 4, 466 = 466,
12 = 12, 99 = 99 — with the self-dual `(1, δ)` row standing alone, and the
`non-LTL` column is symmetric too (the cut is complement-blind, §4). On a
one-sided corpus the duality gate of §2 can only check each language
against its computed complement, record by record; on a complement-closed
catalogue it becomes an identity of the whole table. The `primals` column
is where asymmetry survives, and it is the real measurement of the
enumeration: small `Inf`-shapes realize the safety row directly (1356
primals) and its guarantee dual almost never (4), and the deep degrees are
reached on one side only (`(ω², σ)`: 99 primals against 0). What an
enumeration *produces* is one-sided; what it *determines*, through the free
closure, is not.

**Proposition 11.1, read off the coordinates.** The Büchi-vs-not split
needs no presentation: `m⁺ ≤ 0` is generalized-Büchi-realizability — 3250
languages, the trivial, weak, and `(ω, σ)` rows; `m⁺ = 1 ∧ m⁻ = 0` is the
co-Büchi-proper row (`(ω, π)`, 466); and `m⁺ ≥ 1 ∧ m⁻ ≥ 1` — the 222
languages of the `(ω·2, ·)` and `(ω², ·)` rows — needs genuine parity. So
688 of 3938 languages sit strictly above the generalized-Büchi ceiling,
exactly at the co-Büchi and parity degrees: the proposition and its
converse at catalogue scale, with the independent Spot-vs-algebra spectrum
gate agreeing on the presentation tier [Rep26]. The deep band is reached
only through the beyond-wall parity sample — and the derivative regime
stays empty, as §11's sharp budget requires: its first inhabitant sits at
the three-state, two-colour parity shape, past the current wall.

**Depth and countability are independent, in the numbers.** The non-LTL
mass does not sit at the deep end: half of the *safety* row (678 of 1356)
is already beyond LTL, a third of the deepest parity rows (38 of 99 per
side) is LTL-definable, and only the one-Rabin-pair rows are wholly
non-LTL. The two axes read off the same object — §4's cut and §7–8's
degree — are exhibited by the catalogue as a full cross-product.

**The cost claim of §10 holds.** Classifying is a read-off of the stored
invariant — the entire catalogue in about one second — and the practical
ceiling remains the construction of `𝓘(L)`, never the classification.

**Future work (size versus depth).** The remaining measurement is the
distribution of the algebra size `N = |𝒞|` across the catalogue,
cross-tabulated against the degree. The
dependence is one-directional: a chain of length `m` needs `m + 1` strictly
`H`-descending idempotents and a superchain of length `n` needs `n + 1`
strictly `R`-descending stems, so a deep degree forces `N` up — but not
conversely, since a large algebra can be topologically shallow (a safety
language with an intricate finite-word core keeps `N` high at degree
`(1, π)`, while `EvenBlocks` reaches `ω²` with `N = 8`). The expected picture
is triangular — deep degrees only above a size floor, shallow degrees at
every size — and where the catalogue sits inside that triangle measures
what small shapes actually exercise.

---

## Conclusion

The classical taxonomy of ω-regular languages is decidable on the syntactic
ω-semigroup by table search alone. The exponential price is paid once,
constructing `𝓘(L)`; after that, identity, the aperiodic cut, every rung of
the safety–progress/topological ladder, the acceptance index, and the exact
Wagner degree are polynomial read-offs — [SωS26 §7]'s "semantic benchmark"
claim made executable: one object in, every verdict out, each with a
witness — a group cycle, an alternating chain, a superchain descent — that
is itself a set of lassos replayable against any presentation of `L`.

The Wagner degree earns its verdict rather than inheriting it. Its
derivative recursion is not an algebraic operation — no re-marking of the
accepting pairs can carry it (Proposition 8.1) — but it is a table
computation: on the right regular representation the derivation becomes a
restriction of the admissible stems, the same chain and superchain engines
run at every level, and the recursion trace is the Cantor normal form of
the degree (Theorem 8.5). This complements Cabessa and Duparc's one-pass
computation of the same value [CD09b]: two disjoint routes to the complete
invariant, whose agreement over a corpus is the natural cross-oracle for an
implementation of either.

Beyond the single language, the acceptance family of an input corpus fixes
its reachable degrees a priori (Proposition 11.1), and the catalogue of
§12 measures the first Wagner-degree profile of the small ω-languages —
3938 of them, counted once and closed under complement: 43% beyond LTL, a
profile exactly symmetric under duality, the spectrum bound and its
converse verified, classification never the bottleneck. The
size-versus-depth picture is the next measurement on the same data.

---

## References

- **[CD09a]** J. Cabessa, J. Duparc. *A game theoretical approach to the
  algebraic counterpart of the Wagner hierarchy: Part I.* RAIRO Theor.
  Inform. Appl. 43(3) (2009) 443–461.
- **[CD09b]** J. Cabessa, J. Duparc. *A game theoretical approach to the
  algebraic counterpart of the Wagner hierarchy: Part II.* RAIRO Theor.
  Inform. Appl. 43(3) (2009) 463–515.
- **[CP97]** O. Carton, D. Perrin. *Chains and superchains for ω-rational
  sets, automata and semigroups.* Int. J. Algebra Comput. 7(6) (1997)
  673–695.
- **[CP99]** O. Carton, D. Perrin. *The Wagner hierarchy.* Int. J. Algebra
  Comput. 9(5) (1999) 597–620.
- **[Lan69]** L. H. Landweber. *Decision problems for ω-automata.* Math.
  Systems Theory 3(4) (1969) 376–384.
- **[MP92]** Z. Manna, A. Pnueli. *The Temporal Logic of Reactive and
  Concurrent Systems: Specification.* Springer, 1992.
- **[PP04]** D. Perrin, J.-É. Pin. *Infinite Words: Automata, Semigroups,
  Logic and Games.* Elsevier, 2004.
- **[Rep26]** Y. Thierry-Mieg, with Claude (Anthropic). *The SoS classifier:
  experiment reports.* Companion document, 2026
  (`research_notes/sos_classifier_report.md`).
- **[Spec26]** Y. Thierry-Mieg, with Claude (Anthropic). *The SoS classifier:
  engineering specification.* Companion document, 2026
  (`research_notes/sos_classifier_spec.md`).
- **[SW08]** V. Selivanov, K. W. Wagner. *Complexity of topological
  properties of regular ω-languages.* Fund. Inform. 83(1–2) (2008).
- **[SωS26]** Y. Thierry-Mieg, with Claude (Anthropic). *Constructing the
  syntactic ω-semigroup from a deterministic Emerson–Lei automaton.* Working
  draft, 2026 (`research_notes/sos_constructed.md`).
- **[Wag79]** K. Wagner. *On ω-regular sets.* Information and Control 43
  (1979) 123–177.
