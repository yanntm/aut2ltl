# Synthesizing LTL from the syntactic ω-semigroup — the Diekert–Gastin route

**STATUS: DRAFT** — design document, pre-implementation, now grounded
clause-by-clause against the reference text (`papers/Diekert_Gastin_2008`,
§5 for recognition, §8 for the construction; cited below as [DG], with the
proposition/lemma numbers of that text). This is the companion and consumer
of `../oracle/algorithm.md`: the objects defined there (`D`, `EM(D)`, the
quotient `S(L)₊ = EM(D)/~`, profiles `Aprof`, shortest representatives) are
used without being redefined. Open points are collected in layer 11.

## 0 — Why this exists

The oracle decides LTL-definability by materializing the syntactic
ω-semigroup — the canonical algebra of the language. On the negative side it
hands out a replayable certificate; on the positive side it answers **LTL**
with a theorem but no artifact (the trust asymmetry its layer 11 records).
This module makes the positive verdict constructive: from the aperiodic
quotient it **synthesizes a defining LTL formula**, implementing [DG]
Proposition 8.1 (*AP ⊆ LTL*, by local-divisor induction). Three properties
no other engine in the portfolio has at once:

- **Complete on the fragment.** Every LTL-definable language gets a formula.
  There is no counter-free-presentation precondition: the construction runs
  on the canonical algebra, where a group exists iff the language is
  genuinely not LTL — the kr cascade's form constraint (a proven-LTL
  language whose given automaton still carries an encoding group) has
  nothing to attach to here.
- **Presentation-independent.** Any two inputs with the same language reach
  the identical quotient, and every choice the synthesis makes is pinned
  deterministic (layer 8). Same language ⟹ same formula — hash-consed
  identity, not mere equivalence. The output is a **normal form** for the
  LTL fragment of ω-regular, canonical modulo the fixed choices.
- **Self-certifying.** The formula, verified equivalent to the input, is the
  checkable certificate the LTL verdict lacked.

The theory is settled — [DG] proves the synthesis exists — but the
literature is proof, not construction-you-can-run: to our knowledge the
local-divisor synthesis has never been implemented, because it consumes a
recognizing morphism onto an aperiodic monoid and nobody materializes the
canonical one. The oracle now does. This module is the cash-out.

## 1 — The recognition frame ([DG] §5)

Everything runs over `Σ^∞ = Σ* ∪ Σ^ω` — finite and infinite words in one
frame; our input language `L ⊆ Σ^ω` is the ω-special case and loses nothing.

- **Recognition.** A monoid morphism `h : Σ* → M` *recognizes* `L` when `L`
  is saturated by `≈h`, the transitive closure of blockwise similarity
  (`u ∼h v` iff they admit factorizations into non-empty blocks with equal
  `h`-images, [DG] §5). `≈h` has finite index: at most `1 + |M| + |M|²`
  classes — one for `ε`, the fibers `h⁻¹(m)` for finite words, and at most
  `|M|²` classes of infinite words, by the Ramsey/linked-pair argument
  ([DG] Lemma 5.2): every `w ∈ Σ^ω` lies in `h⁻¹(s)·(h⁻¹(e))^ω` for some
  **linked pair** (`se = s`, `e² = e`).
- **Our instance.** `h` is the syntactic morphism onto `M = S(L)₊¹` — the
  oracle's quotient with identity adjoined. It recognizes `L` (oracle layers
  3–5), and the LTL verdict says it is aperiodic. From the oracle's output
  this module materializes, once:
  - the **class multiplication table** `S¹ × S¹ → S¹` (compose enriched
    representatives, look the product's class up in the element index);
  - the **accepting-pair table** `P(s, e)` = acceptance of `u·z^ω` with
    `[u] = s`, `[z] = e`: one lookup, `Aprof(rep(e))[st_{rep(s)}(init)]`.
    `P` is the membership evaluator for ultimately-periodic words presented
    algebraically; every "is this in `L`?" question below bottoms out here.

Precondition, load-bearing: **aperiodicity**. The strict-decrease lemma of
layer 3 is proved *for aperiodic `M`* in [DG]; the module refuses
group-bearing input rather than risking non-termination.

## 2 — The logic and the recursion contract ([DG] §7, Prop 8.1)

The internal logic is `LTL_Σ[XU]` — pure-future, with **strict next-until**
as the only modality (`φ XU ψ` ≡ "at some strictly later position `ψ`, and
`φ` strictly in between"). Models are words in `Σ^∞ ∖ {ε}` *with a
position*; derived operators `X φ = ⊥ XU φ`, `φ U ψ = ψ ∨ (φ ∧ (φ XU ψ))`,
`F`, `G` as usual. Since `ε` cannot be a model, [DG] evaluates through the
**prepended-letter device**: for a letter `c` (not necessarily in `A`),

```
L_{c,A}(φ)  =  { v ∈ A^∞  |  cv, 0 ⊨ φ }
```

— the formula reads `v` from an anchor position *before* it. This device is
what makes the empty word, the "first block", and position-0 anchoring all
disappear as special cases; it is used at every recursion level and only
unwound at the very end (layer 7).

**The contract ([DG] Prop 8.1(2)).** Given `(Δ, h : Δ* → T, N, c)` — an
alphabet, a morphism onto a finite aperiodic monoid, a language `N ⊆ Δ^∞`
recognized by `h` (presented finitely by its `≈`-classes: an explicit `ε`
flag — `{ε}` is its own `≈`-class, no fiber covers it — a set of elements
of `T` for the non-empty finite words, and for the ω-part a set of
ω-classes, each named by a **conjugacy class of linked pairs** — layer 6's
calculus), and the prepend letter — synthesize `φ ∈ LTL_Δ[XU]` with `N = L_{c,Δ}(φ)`.
Induction on `(|T|, |Δ|)`, lexicographic. The root call is
`(Σ, h, L, fresh)`.

## 3 — Base case and the local divisor ([DG] §8.1–8.2)

- **Base: every letter is invisible** — `h(a) = 1` for all `a ∈ Δ`. Then
  `N` is a boolean combination of `{ε}`, `Δ⁺`, `Δ^ω`, and
  `{ε} = L_{c,Δ}(¬X⊤)`, `Δ⁺ = L_{c,Δ}(XF¬X⊤)`, `Δ^ω = L_{c,Δ}(¬F¬X⊤)`.
  This subsumes `|T| = 1` and `Δ = ∅`; there is no erasure machinery and no
  per-letter invisibility case — invisible letters simply survive into
  sub-alphabets until only they remain.
- **Otherwise fix a pivot** `c ∈ Δ` with `h(c) ≠ 1` (the deterministic
  choice is layer 8's) and let `A = Δ ∖ {c}`. The **local divisor** of `T`
  at `m = h(c)`:

  ```
  T' = mT ∩ Tm        xm ◦ my := xmy        identity: m
  ```

  Well-defined, associative, and a **divisor** of `T` (image of the
  submonoid `{x | xm ∈ mT}` under `x ↦ xm`), hence aperiodic when `T` is.
  **Strict decrease** ([DG] §8.1): if `T` is aperiodic and `m ≠ 1`, then
  `1 ∉ mT ∩ Tm` — else `1 = mx` gives `mⁿ = mⁿ⁺¹ ⟹ 1 = m` — so
  `|T'| < |T|`. Aperiodicity is exactly what makes *every* visible pivot
  shrink the first coordinate.

## 4 — The `c`-factorization and the compressed word ([DG] Lemma 8.2)

Every `v ∈ Δ^∞` factors at its `c`'s:

```
v = v₀ c v₁ c v₂ c ⋯                v_i ∈ A*          (c infinitely often)
v = v₀ c v₁ c ⋯ v_{k-1} c v_k       v_i ∈ A*, v_k ∈ A^∞, k ≥ 0   (else)
```

The **compressed alphabet** is `T = T₁ ⊎ T₂` (disjoint):

- `T₁ = h(A*) ⊆ T` — the block images: the submonoid generated by the
  `A`-letters, *as letters*;
- `T₂ = { [u]_{h|A} | u ∈ A^∞ }` — the `≈`-classes of `A^∞`-words under the
  restricted morphism: the finite-word fibers, plus the ω-classes, which
  layer 6 represents exactly as **conjugacy classes of linked pairs over
  the subsemigroup `h(A⁺)`** (block images of *non-empty* `A`-words — the
  identity participates only when some non-empty block reaches it).

The **compression** `σ : Δ^∞ → T^∞` maps `v` to `h(v₀) h(v₁) h(v₂) ⋯ ∈
T₁^ω` in the infinite-`c` case, and to `h(v₀) ⋯ h(v_{k-1}) [v_k] ∈ T₁* T₂`
otherwise — *all* blocks are compressed, the prefix block included (it
becomes position 0 of `σ(v)`, which the prepend device will read), and the
whole possibly-infinite last block is one `T₂`-letter.

The **compressed morphism** `g : T* → T'` sends `n ∈ T₁` to `h(c)·n·h(c)`
and every `T₂`-letter to the neutral `h(c)`. Then ([DG] Lemma 8.2) there is
`K ⊆ T^∞`, definable in `LTL_T[XU]`, with `L = σ⁻¹(K)`, assembled from
three pieces:

```
K₀ = { [u]  |  u ∈ N ∩ A^∞ }                                      (no c at all)
K₁ = ⋃_{n ∈ T₁, m ∈ T₂}  n T₁* m  ∩  n [ n⁻¹σ(N) ∩ T₁* m ]_g      (c finitely often, ≥ 1)
K₂ = ⋃_{n ∈ T₁}          n T₁^ω  ∩  n [ n⁻¹σ(N) ∩ T₁^ω ]_g       (c infinitely often)
```

where `[·]_g` is `≈g`-saturation. Each saturation is recognized by `g` —
a morphism onto the *strictly smaller* aperiodic `T'` — so the monoid
induction yields its formula in the `L_{n,T}` form, with the leading block
`n` as the prepend letter. The regime guards and shapes are directly
`[XU]`-definable over `T`, from the phantom position (writing `⋁T₁` for
the disjunction of the `T₁`-letters, `end` for `¬X⊤`, `inf` for `G X⊤`):

```
K₀-shape (one T₂-letter m)  :   X(m ∧ end-of-word: ¬X⊤)
n T₁* m                     :   X( n ∧ ( (⋁T₁) XU (m ∧ ¬X⊤) ) )
n T₁^ω                      :   X( n ∧ G(⋁T₁) ) ∧ inf
```

(the `XU` in the middle shape allows an empty `T₁*` — the `m` may
immediately follow `n`; a one-letter word has no middle case at all).

**The saturation is a table on the finite side.** For `w ∈ T₁*`, membership
of `n·w·m` in `σ(N)` depends on `w` only through `g(w)`: the `Δ`-word it
denotes has prefix value `n·g(w)` in `T` (the interleaved `c`'s are exactly
`g`'s boundary `c`'s) and tail class `m`, so

```
[ n⁻¹σ(N) ∩ T₁* m ]_g  =  { w·m  |  g(w) ∈ X_{n,m} },
X_{n,m}  =  { x ∈ T' | Accept(n·x, m) }
```

— for an ω-letter `m` with representative pair `(s, e)`, `Accept(n·x, m)`
classifies the pair `(n·x·s, e)` in the node's own ω-universe and tests
the target's ω-part (at the root that is exactly the `P` lookup
`P(n·x·s, e)`); for the finite tail letters it is a fiber test of the
target's finite part (`[ε]`: `n·x ∈ fin`; fiber `f`: `n·x·f ∈ fin`).
No search, no witnesses: the finite-side recursion target is
computed by pure table arithmetic. On the ω side (`K₂`) the analogous
class-set is well-defined by [DG]'s three auxiliary results inside Lemma
8.2 (σ-images of `(A*c)^ω`-words that are `≈g`-equivalent have
`≈h`-equivalent `c`-prepended originals); computing it goes through the
ω-class calculus of layer 6.

## 5 — The two substitution lemmas ([DG] Lemmas 8.3, 8.4)

The compressed formula over `T` is translated back to `Δ` by two exact,
paper-given transformations — these are the implementation's workhorses and
neither is improvised:

- **Lifting ([DG] 8.3).** For a letter `b`, `φ ↦ φ^b` evaluates `φ` on the
  largest `b`-free factor starting at the current position (the current
  letter exempt). Structural clauses: `a^b = a`; homomorphic through `¬`,
  `∨`; and

  ```
  (φ XU ψ)^b  =  (¬b ∧ φ^b)  XU  (¬b ∧ ψ^b)
  ```

- **Substitution ([DG] 8.4).** `ξ ↦ ξ̃` with `cv, 0 ⊨ ξ̃  ⟺  σ(v), 0 ⊨ ξ`:
  the positions of `σ(v)` correspond to the `c`-positions of `cv` (the
  prepended `c` is position 0 — this is why the device exists). Clauses:
  - `T₁`-atom `n`: `ñ = φₙ^c ∧ XF c` — "the `A`-block starting here has
    `h`-image `n`, and there is a later `c`". The block formula `φₙ`
    (`L_{c,A}(φₙ) = A* ∩ h⁻¹(n)`) comes from the **alphabet induction**:
    the recursion node `(A, h|A, ·, c)` — same monoid, one letter fewer.
  - `T₂`-atom `m`: `m̃ = ψₘ^c ∧ ¬XF c` — "the block starting here is the
    infinite `A`-tail and lies in class `m`", `ψₘ` from the same alphabet
    induction (`L_{c,A}(ψₘ) = A^∞ ∩ m`). That this target is *legal* — a
    recognized language, presentable by a pair set — is exactly what
    layer 6's fact 3 buys; a single pair language would not be (the gap
    the deep pass of 2026-07-03 caught before code did).
  - homomorphic through `¬`, `∨`; and

  ```
  (ξ₁ XU ξ₂)~  =  (¬c ∨ ξ̃₁)  U  (c ∧ ξ̃₂)
  ```

The assembly of one visible-pivot node is exactly: compress (layer 4),
recurse (monoid side for the saturations, alphabet side for the block
formulas), substitute (this layer). Block formulas are substituted at every
occurrence of their `T`-atom across the compressed formula — this is
precisely where the project's hash-consed DAG is load-bearing: the flat
form may repeat `φₙ` hundreds of times, the DAG holds it once.

## 6 — The ω-word letters: conjugacy classes of linked pairs

The one construction-level piece [DG] leaves implicit is the finite
handling of the infinite-word classes. The calculus is classical and lives
in [PP] (Perrin–Pin, *Infinite Words*, 2004 — chapter II, §2; the local
companion `papers/Carton_Perrin_Pin_2008` restates it): two linked pairs
`(s, e)`, `(s′, e′)` are **conjugate** when

```
∃ x, y ∈ S¹ :   e = x·y,   e′ = y·x,   s′ = s·x
```

— an equivalence relation on linked pairs ([PP] Prop 2.6). Three facts
make it the exact ω-class calculus; the first is self-contained, the
others are the cited theorems:

1. **Conjugate pairs denote one class** (two lines, no citation): the
   single word `u·(vw)^ω` with `h(u), h(v), h(w) = s, x, y` factors
   blockwise as `(s, e, e, …)` and — regrouped `(uv)(wv)(wv)…` — as
   `(s′, e′, e′, …)`, so the two pair renderings are `∼`-connected
   through it.
2. **All pairs of one word are conjugate, and non-conjugate pairs have
   disjoint pair languages** ([PP] Prop 2.8 / Cor 2.9: two pairs are
   conjugate *iff* their pair languages intersect). Hence *word ↦ the
   conjugacy class of its Ramsey pairs* is a well-defined function — `σ`'s
   last letter needs nothing more.
3. **The class language is recognized.** The union of a conjugacy class's
   pair languages is `∼`-saturated: if `w ∼ w′` blockwise, Ramsey-grouping
   the *shared image sequence* yields a pair admitted by both words, so
   `w` and `w′`'s pair sets meet, hence coincide as conjugacy classes (by
   2). With every word one `∼`-step from the rendering of each of its
   pairs ([DG] 5.2 + blockwise match), the union is moreover
   `∼`-connected: **it is exactly one `≈`-class**. ω-classes ↔ conjugacy
   classes, bijectively.

`T₂`'s ω-letters are therefore the conjugacy classes of linked pairs over
`h(A⁺)`, each keyed by its canonically least member pair (layer 8), with
the identity test an `O(|S¹|²)` scan of the multiplication table for
`(x, y)`. Fact 3 is what makes the `T₂`-atom targets of layer 5 *legal*:
`A^∞ ∩ m` is a recognized language, presentable to the alphabet induction
by its pair set — the conjugacy closure of any representative.

**Query independence** (the lemma the tables lean on): every entry the
assembly reads about an ω-letter is representative-independent. All
members of one pair language factor with the image sequence
`s, e, e, …`, so a recognized `N` contains the pair language entirely or
not at all and `P(s, e) = [w ∈ N]` for every `w` admitting `(s, e)`;
conjugate representatives agree because they denote the same class (fact
1 + 3). Prefixing preserves admission — `h(u) = y` and `w` admitting
`(s, e)` make `u·w` admit `(y·s, e)` — so the `X_{n,m}` lookups
`P(n·x·s, e)` are likewise invariant. The `K₂` class sets one level down
repeat the argument verbatim with `g` and the saturation target; the
recursion's targets are always morphism-recognized, which is all the
argument uses.

**Evaluation.** Every query the assembly issues is one level of table
arithmetic — no block is ever rendered as a word of the original
alphabet. ω-letters and ω-targets are always presented in the issuing
node's own universe, so `Accept` is a multiplication plus a pair-class
lookup in that universe; the `K₂` class sets render a class's least pair
as words over the *compressed* letters (shortlex reps from the BFS over
the `T₁`-images), fold the denoted prefix and cycle values in the node's
monoid (`h(z) = n₁·m·⋯·n_j·m`), raise the cycle value to its idempotent
power ([PP] Prop 2.11 licenses the exact-image splitting; aperiodicity
makes the power sequence a fixpoint), and classify the resulting pair one
level up. Constancy across the class is the query-independence lemma.
One closure note makes `K₂`'s bookkeeping legal: conjugacy over the full
compressed alphabet and over its `T₁`-letters agree (`T₂`-images are the
neutral element, so both generate the same `S¹`), hence the `T₁^ω`
classes inject into the child's universe and the class sets are reported
in the child's own ids — the universe the child target speaks.

## 7 — Unwinding the device at the root

The root call returns `φ` with `L = L_{fresh,Σ}(φ)` — evaluated on
`fresh·w` at position 0, the phantom position whose letter is `fresh`.
[DG] Remark 7.1 converts this to an ordinary formula by **partial
evaluation at the phantom position** — a top-down pass touching only the
subterms evaluated at position 0:

```
PE(a)         =  ⊤ if a = fresh, else ⊥        (the phantom's letter is known)
PE(¬φ)        =  ¬PE(φ)
PE(φ ∨ ψ)     =  PE(φ) ∨ PE(ψ)
PE(φ XU ψ)    =  φ U ψ        — anchored at position 0 of w; the operands
                                speak of real positions and pass through
```

`L = L_Σ(PE(φ))` since `L` never contains `ε`. The result is pure-future
LTL over `Σ^ω`; the remaining internal `XU` nodes render as `X(· U ·)` in
the host DAG. The internal `Σ^∞` semantics never leaks: every finite-word
formula lives inside a lifted (`·^c`) context, where the block's end is a
real position of the host word.

## 8 — Canonicity: the fixed choices

The claim of layer 0 — same language, same DAG — holds exactly when every
choice is a function of the algebra alone, never of `D`:

- **Class identity.** The oracle's class ids come from the closure BFS — an
  artifact of `D`. This module re-keys every class by its **shortlex-least
  representative word** (total order on `AP` = declaration order,
  `Σ = 2^AP` lexicographic) — a language invariant. All enumerations
  (`T₁`, `T₂`, the `K` unions, class sets) iterate in this key order.
- **The pivot rule.** v0: the least letter `c` (in the fixed order) with
  `h(c) ≠ 1`. (Deterministic alternatives — e.g. minimizing `|T'|` — are
  open point O3; they change the normal form, not its canonicity.)
- **`T₂` keys.** Linked pairs ordered by their element-id pair `(s, e)`
  after the O2 merge — element ids are shortlex-canonical at the root and
  every deeper id is derived from them — each conjugacy class keyed by its
  least member pair.

Consequence, and the headline experiment: two different presentations of
the same language — `gf_aa_parity.hoa` and a fresh Spot translation of
`GF(a ∧ Xa)` — must synthesize the **identical DAG**, hash-consed. That
diff is a one-probe test and a paper-grade claim: no minimization-based
route can offer it, because no canonical minimal deterministic ω-automaton
exists — the algebra is canonical exactly where the automata are not.

## 9 — Cost: where the explosion lives

Write `n = |S(L)₊¹|`. The recursion is a DAG of nodes keyed by
`(monoid, morphism, alphabet)`; per node the work is polynomial. The
drivers, ranked:

1. **The entry toll (upstream, shared with the oracle):** materializing
   `EM(D)`, bounded by `(|Q|·2^{|C|})^{|Q|}`, capped into INCONCLUSIVE.
   `n ≤ |EM(D)|`, and `n` is the *minimum over all presentations* — the
   quotient can only shrink the base every later cost is measured in.
2. **Alphabet squaring per descent (the DG-specific driver):** one monoid
   descent replaces the alphabet by `T = T₁ ⊎ T₂` with `|T₁| ≤ n_i` and
   `|T₂| ≤ n_i²`. The alphabet induction at a level strips one letter per
   node, so a level of monoid size `n_i` carries up to `O(n_{i-1}²)`
   alphabet nodes, each spawning its own divisor descent. Crude worst-case
   node count: `∏ O(n_i²) = n^{O(n)}` — single-exponential-with-log-factor
   in the *quotient* size, before DAG collapse of coinciding
   `(monoid, alphabet)` nodes.
3. **Per-node width (benign):** the `K₁` union is `O(|T₁|·|T₂|) = O(n_i³)`
   disjuncts of constant assembly; lifting and substitution are
   size-linear with `O(1)` per connective; block formulas are DAG-shared
   across all their atom occurrences.

We commit to **no tighter bound** here: [DG] proves effectiveness, not
economy, and this project's rule is measure, then argue. The synthesis runs
under caps (node count, DAG size, time); a blown cap is a **decline** —
never a wrong formula. Two structural mitigations are native: recursion
nodes memoize on hash-consed keys (the descent is a DAG, not a tree), and
`T₁ = h(A*)` is the generated submonoid, in practice often far below `n_i`.

## 10 — Literature and positioning

- **[DG] Diekert–Gastin 2008, "First-order definable languages"**
  (`papers/Diekert_Gastin_2008.pdf`) — THE reference implemented: §5
  (recognition over `Σ^∞`, Ramsey/linked pairs), §7 (`LTL[XU]`, the
  `L_{c,A}` device), §8 (local divisors, Prop 8.1, Lemmas 8.2–8.4). Already
  cited by the oracle for the characterization chain; here its *proof*
  becomes the program.
- **[PP] Perrin–Pin, *Infinite Words: Automata, Semigroups, Logic and
  Games*** (Elsevier 2004; chapter II §2, pages 79–85 — local scan
  `papers/infinite-words-automata-semigroups-logic-and-games.pdf`, and
  the companion survey `papers/Carton_Perrin_Pin_2008`) — the ω-class
  calculus of layer 6: conjugacy of linked pairs (Prop 2.6), all pairs
  of one word conjugate / disjointness across conjugacy classes
  (Prop 2.8, Cor 2.9), exact-image splitting of ultimately periodic
  words (Prop 2.11).
- **BLS FoSSaCS 2022** — the sibling systematic core (`aut2ltl/bls`): a
  Krohn–Rhodes cascade on the *transition monoid of the given form*. The
  comparison for the paper: presentation-dependent vs canonical input;
  form-preconditioned vs fragment-complete; holonomy machinery vs monoid
  induction. Neither dominates on output size a priori — that is an A/B.
- Extend `../oracle/related_work.md` with the positioning digest when this
  lands; this document cites only what roots a definition.

## 11 — Open points (why this is a draft)

- **O1 — RESOLVED by the paper.** No separate finite-word logic: one
  `LTL[XU]` over `Σ^∞`, the `L_{c,A}` prepend device, `ε` never a model.
  The earlier draft's "LTLf boundary discipline" dissolves into Lemmas
  8.3/8.4's exact clauses.
- **O2 — CLOSED: the exact ω-class identity is linked-pair conjugacy**
  (layer 6; [PP] Prop 2.6/2.8/Cor 2.9). History, kept because each step
  taught something: the first candidate key (left-context acceptance
  vectors) was falsified by layer 13 — strictly coarser than `≈`; the
  second attempt (pairs unmerged, no identity at all) was sound for the
  table queries but made the `T₂`-atom targets of layer 5 unrecognized
  languages — illegal induction targets, caught in the deep pass;
  conjugacy is exact in both directions, canonical, and one table scan.
  Nothing of O2 remains open.
- **O3 — pivot heuristics.** v0 pins least-visible-letter; deterministic
  size-minimizing pivots are a later, measured change of normal form.
- **O4 — worked examples: DONE** (both instalments, layers 12–13, from
  `tests/probes/dg_dump.py` tables). Between them the two walks cover:
  divisor-carried vs `T₂`-carried assembly, `K` pieces trivializing to
  `⊤` and to `⊥`, an invisible letter in the wild, multiple accepting
  pairs, prefix-independence arriving as a constant row, and one
  falsified design assumption (see O2). A third walk is only warranted
  when implementation surfaces a shape neither covers.
- **O5 — RESOLVED: the architecture is layer 14** (module map,
  responsibilities, build order).
- **O6 — wiring.** Whether this surfaces as a `Translator`, and where it
  sits relative to the gate (an LTL verdict with a formula attached), is
  the assembly's concern — out of scope here, exactly as gate wiring was
  for the oracle.

## 12 — Worked example: `gf_aa_parity`, by hand

`L = GF(a ∧ Xa)` — infinitely many `aa`-factors — from the fixture whose
2-state presentation carries the `Z2` that blocks the TM cascade. All data
below is `tests/probes/dg_dump.py` output (canonical keying, layer 8):

```
D        : 2 states, letters ['!a', 'a'], acc Inf(0)
quotient : |EM1| = 10 elements -> 6 classes
  0: [eps]     idempotent          letters: !a -> 1, a -> 2
  1: [!a]      idempotent
  2: [a]                           mult    0 1 2 3 4 5
  3: [!a;a]    idempotent               1: 1 1 3 3 1 5
  4: [a;!a]    idempotent               2: 2 4 5 2 5 5
  5: [a;a]     idempotent (absorbing)   3: 3 1 5 3 5 5
                                        4: 4 4 2 2 4 5
  P: only accepting linked pair = (5,5) 5: 5 5 5 5 5 5
```

The classes are readable invariants: for an `aa`-free word, (first letter,
last letter) — `1/3/4/2` are `¬a·¬a / ¬a·a / a·¬a / a·a` — and class `5`
is "contains `aa`", two-sided absorbing. `w ∈ L` iff its Ramsey pair is
`(5, 5)`: the accepting-pair set of the root call is the singleton.

**The root node** `(Σ = {¬a, a}, h, L, fresh)`. Pivot: the least letter
with `h ≠ 1` is `c = ¬a` (`h(¬a) = 1`, the class — not the identity `0`).
`A = {a}`.

**The local divisor** at `m = 1`: `1·S = {1,3,5}`, `S·1 = {1,4,5}`, so
`T' = {1, 5}` with `∘`-identity `1` and `5 ∘ 5 = 5` — the two-element
absorbing monoid. One descent: `6 → 2`.

**The compressed alphabet.** `T₁ = h(a*) = {0, 2, 5}` (`ε`, `a`,
`a^{≥2}`). `T₂` = the `≈_{h|A}`-classes of `{a}^∞`: three finite ones
(`[ε]`, `[a]`, `[a^{≥2}]`) and one infinite, `[a^ω]` — so even on a pure
ω-input, finite `T₂`-letters exist from depth 1 on: the `Σ^∞` frame is
load-bearing immediately, exactly as layer 2 contracts. The compressed
morphism `g` reads `g(0) = 1·0·1 = 1`, `g(2) = 1·2·1 = 1`, `g(5) =
1·5·1 = 5`: **single-`a` blocks are invisible in the divisor; only
`aa`-blocks survive** — the algebra has silently discovered that an `aa`
never straddles a `¬a`.

**The three pieces** for the target `{(5,5)}`:

- `K₀` (no `¬a`): `a^ω ∈ L`, so `K₀ = {[a^ω]}` — one `T₂`-letter, in.
- `K₁` (finitely many `¬a`): the tail is `a^ω`, and
  `X_{n,[a^ω]} = {x ∈ T' : P(n·x·5, 5)} = T'` for every `n` (column 5 of
  the multiplication table is constantly 5, and `P(5,5) = 1`): the
  saturation-is-a-table lemma of layer 4, exercised — **every** such word
  is in `L`, the sub-target is the trivial `⊤`-class set, no recursion
  needed. Semantically: `K₀ ∪ K₁` is exactly `FG a ⟹ accept`.
- `K₂` (infinitely many `¬a`): the compressed word lives in
  `{0, 2, 5}^ω ⊆ T₁^ω`, and `≈g` on it has exactly three ω-classes — the
  pairs `(1,1)` and `(5,1)` (finitely many visible `5`'s; conjugacy-
  distinct, both rejected) and `(5,5)` (infinitely many, accepted: the
  class set is this singleton for every leading `n`). The `(T, T')`-node
  pivots on the letter `5`
  (the only one `g` sees), its local divisor is `5T'∩T'5 = {5}` — the
  trivial monoid, `2 → 1`, base case — and the compressed formula is the
  `GF`-shape "infinitely many `5`-letters".

**Reassembly** (layer 5): the `T₁`-atom `5` substitutes as
`φ₅^{¬a} ∧ XF ¬a` — "the `a`-block starting here has ≥ 2 `a`'s" — with
`φ₅` from the alphabet node `({a}, h|A, h⁻¹(5))`, a two-step chain to the
all-invisible base. Modulo the final simplification pass the assembled
formula reads

```
FG a  ∨  GF( ¬a-anchored block with aa )    ≡    GF(a ∧ Xa)
```

— the language back, from the algebra alone, with the descent chain
`6 → 2 → 1` and never more than seven letters of compressed alphabet. The
walk validates, concretely: the pivot rule (the *idle* letter `¬a` is the
right pivot — blocks are the units of counting), the `X_{n,m}` table lemma
(`K₁` computed by two table lookups), the depth-1 appearance of finite
`T₂`-letters, and the collapse behavior the cost layer hopes for (`T₁` =
3 of a possible 6, `T₂` = 4 of a possible 36).

## 13 — Worked example: `fairness_example`, by hand

`L = GFa ∧ FGb` (`samples/fixtures/hoa/various/fairness_example.hoa`) — the
mirror image of layer 12: there the divisor carried everything and `T₂` was
a bystander; here the divisor is trivial at every turn and the whole
construction rides on the ω-class calculus. Probe output:

```
D        : 1 state, letters ['!a&!b', 'a&!b', '!a&b', 'a&b'], acc Fin(0) & Inf(1)
quotient : |EM1| = 4 elements -> 3 classes
  0: [eps]     idempotent      letters: !a&!b -> 1, a&!b -> 1,
  1: [!a&!b]   idempotent               !a&b -> 0, a&b -> 2
  2: [a&b]     idempotent
                                mult    0: 0 1 2   P: (1,2) = (2,2) = 1,
                                        1: 1 1 1      all other linked
                                        2: 2 1 2      pairs = 0
```

Readable invariants: `1` = "contains a `¬b`" (left-absorbing: row 1 is
constant), `2` = "all-`b`, contains an `a`", `0` = the identity class —
which is *fat*: the letter `¬a∧b` maps to it. **An invisible letter in the
wild**: inserting or deleting `¬a∧b` changes no membership in any context
(it feeds neither `GFa` nor `¬FGb`), and the construction's stance on it —
never pivotable, survives into every sub-alphabet, dissolved by the
all-invisible base case — is exercised for real. Two accepting pairs,
`(1,2)` and `(2,2)`; the language is prefix-independent and `D` has one
state, so the `~lin` side is fully blind and every distinction above is
profile-borne (oracle layer 9, arriving here as data).

**The root node.** Pivot: least visible letter = `c = ¬a∧¬b` (`h = 1`).
`A = {a¬b, ¬ab, ab}` — note `A` keeps a `¬b`-letter.

**The local divisor is trivial**: `1·M = M·1 = {1}`, so `T' = {1}` — the
descent `3 → 1` in one step, and the entire monoid-side recursion is the
base case: under `g` *every* compressed letter is invisible, `≈g` merges
everything, and the saturations are full shapes. All discrimination
migrates into the `K`-assembly's table tests and the `T₂`-letters.

**The compressed data.** `T₁ = h(A*) = {0, 1, 2}` (all of `M`: `A` still
generates `1` through `a¬b`). `T₂`: four finite classes and **six
ω-classes** — `(s, e)` with `s·e = s`: `(0,0), (1,0), (2,0)` (tails dying
into `(¬ab)^ω`, distinguished by their prefix content), `(1,1)`
(`¬b` forever recurring), and the accepting `(1,2), (2,2)`. Thirteen
letters of `T` against the bound `3 + 3² = 12`-ish — the ceiling brushed,
harmlessly, because the divisor below is trivial.

**The three pieces** for the target `{(1,2), (2,2)}`:

- `K₀` (no `c`): the `A^ω`-words of `L` — exactly the two accepting
  `T₂`-letters. In.
- `K₁` (finitely many `c`, ≥ 1): the prefix through the last `c` has
  `M`-value `n·1·… = 1` *whatever happened before* — row 1 is constant:
  prefix-independence arrives as one row of the multiplication table. The
  table test `P(1·s′, e′) = P(1, e′)` keeps exactly `e′ = 2`: the tail
  must be one of the same two accepting letters. Every `n`, every `x`:
  the `X_{n,m}` sets are again decided without recursion.
- `K₂` (infinitely many `c`): `c` is a `¬b`-letter, so `FGb` fails on
  every preimage — the class set is **empty**, `K₂ = ⊥`. The flagship's
  carrier is this walk's contradiction.

**Reassembly.** The formula is `K₀ ∪ K₁` lifted: "(no `¬a¬b` ever, or
finitely many) and the `A`-tail after the last one satisfies `ψ_m`" for
the two accepting `T₂`-letters — whose formulas come from the *alphabet*
induction on `(A, h|A)`: pivot `a¬b` (divisor at `1`: trivial again), then
`(\{¬ab, ab\}, ·)`: pivot `ab`, whose divisor `2M ∩ M2 = {1, 2}` with
identity `2` and `1` absorbing is the first non-trivial inner algebra —
"a `¬b` in the cycle is poison", which is `FGb` speaking through a
divisor two levels down. Semantically the assembly collapses to
`FGb ∧ GFa` ≡ the input.

**What this walk bought, beyond symmetry with layer 12:** it *falsified*
the draft's O2 candidate. The three rejecting ω-classes `(0,0), (1,0),
(2,0)` are pairwise `≈`-distinct (their members' prefixes are separated by
first-block images) yet share the all-zero left-context acceptance vector
— so the vector is a strict coarsening of `≈`, not an identity key. Here
the merge happens to be harmless (every query the assembly issues factors
through `P(1, e′)`), which is exactly the shape of the congruence lemma
O2 now demands before any such merge is allowed. Ground truth from a
six-line probe output; this is what the walks are for.

## 14 — Architecture: the module map and the build order

One module per role, mirroring the oracle's discipline: each owns one
algorithmic step and one data shape, consumes value objects from above,
and is exercisable alone. The driver owns **no algorithm** — sequencing,
the pivot rule, memoization and caps only.

```
        oracle output  (Monoid, class ids, profiles)
                          │
                    morphism.py         the algebra as a value: canonical ids
                          │             (shortlex re-key), mult table, letter
                          │             map, P, the linked pairs   (layers 1, 8)
                     frame.py           the recursion node's value: letters,
                          │             images, monoid, ω-universe (pairs +
                          │             conjugacy), Target       (layers 2, 6)
        ┌─────────────────┼─────────────────┐
   divisor.py        compress.py       formulas.py
   table × m → ∘     one node's data:  the internal [XU]-AST over abstract
   carrier, ∘,       fa/fc frames, T₁, letter atoms: build, lift^b, tilde,
   strict-decrease   T₂, g, X_{n,m},   PE-unwind, render to the host DAG
   assert (lyr 3)    K sets (lyr 4–6)  (layers 2, 5, 7)
        └─────────────────┼─────────────────┘
                      synth.py          the induction driver: base case,
                          │             pivot, K assembly, memo, caps —
                          │             the only sequencing   (all layers)
              tests/probes/dg_probe.py      end-to-end + Spot verify
              tests/probes/dg_canon.py      the layer-8 DAG-identity claim
```

- **`morphism.py`** — consumes the oracle's `Monoid` + refined classes;
  produces the frozen `Alg` value: canonically re-keyed class ids, the
  multiplication table, the letter map, `P`, the linked-pair enumeration.
  `tests/probes/dg_dump.py` becomes its display client.
- **`frame.py`** — the recursion node's value `Frame`: abstract letters,
  their images, the monoid table, and the ω-class universe (linked pairs
  over the letter-generated subsemigroup, conjugacy classes keyed by least
  member pair, shortlex letter-word reps); `Target`, the `≈`-class
  presentation of layer 2 (ε flag, fiber set, ω-class set);
  `root_frame`/`root_target` bridge from `Alg` — the latter asserts
  `P`-constancy per conjugacy class, the query-independence lemma checked
  on ground data.
- **`divisor.py`** — `mult table × element → Divisor`: the `∘`-algebra of
  `mT ∩ Tm` (uniform over the base `Alg` and over a `Divisor`'s own table
  further down), carrier as ascending base ids, and the strict-decrease
  invariant as an assert.
- **`compress.py`** — `Frame × Target × pivot → NodeData`: the
  sub-alphabet frame `fa` (its ω-classes are `T₂`'s ω-letters), `T₁`, the
  `g`-letter map into the divisor, the child frame `fc`, the `X_{n,m}`
  tables, the `K₀`/`K₂` sets (`K₂` computed on the `T₁`-only frame,
  reported in `fc` ids). Pure tables — produces no formula.
- **`formulas.py`** — the internal hash-consed `[XU]`-AST whose atoms are
  *abstract letters* of whatever alphabet a node speaks; the three exact
  [DG] transformations (lift `·^b`, substitution `·~`, the phantom
  partial evaluation) as structural recursions; the final render to the
  host DAG (`XU ↦ X(· U ·)`, root letters ↦ AP cubes). By construction
  only `Σ`-letters survive to the render — every `T`-atom is eliminated
  by a tilde one level up.
- **`synth.py`** — the recursion node
  `(alphabet, Alg, target, prepend) → formula`, memoized on canonical
  keys; the base case; the pivot rule; the `K` assembly; the caps
  (node count, DAG size, time) exiting as a decline. The only impure-ish
  module in the sense of owning policy.

**Build order** — each step lands with its check green before the next,
and layers 12–13 are the precomputed expected values (the walks *are* the
unit fixtures):

1. `morphism.py`, re-basing `dg_dump.py` on it — expected output: the
   exact tables printed in layers 12–13.
2. `divisor.py` — expected: `6 → {1, 5}` on the flagship, `3 → {1}` on
   fairness, assert fires on a group-bearing input.
3. `frame.py` + `compress.py` — expected: the `T₁`/`T₂`/`g`/`X_{n,m}`/`K`
   numbers of both walks, digit for digit.
4. `formulas.py` — the three transformations tested standalone on toy
   ASTs against the [DG] clause semantics (no automata involved).
5. `synth.py` + `tests/probes/dg_probe.py` — first targets the two walked
   fixtures: Spot-equivalence to `GF(a ∧ Xa)` and `GFa ∧ FGb`; then the
   LTL-definable slice of the validation corpus.
6. `tests/probes/dg_canon.py` — the headline: `gf_aa_parity.hoa` vs a
   fresh Spot translation of `GF(a ∧ Xa)`, assert hash-consed DAG
   identity.

Each module sits well under the 500-LOC discipline; `synth.py` is the
largest and owns no table computation.

## Related ideas

**The Cayley construction → back into the current loop.** The quotient can
also be reified as an automaton: the right-Cayley automaton of `S(L)₊¹` —
states = classes, transitions = right multiplication by the letter classes,
acceptance derived from the profiles. Its transition monoid is the
right-regular representation of the quotient, faithful, hence counter-free
exactly when the verdict is LTL — a *canonical counter-free presentation* of
the language, on which the existing pipeline (the kr cascade, and for that
matter every translator in the portfolio) can be re-run when it declined the
original form. That makes the Cayley automaton a natural **fallback for
cascade declines**: not a rival to this module but a second consumer of the
same materialized algebra, re-entering the loop we already have instead of
building a new one. Its own open lemma is the acceptance condition — whether
an Emerson–Lei/Muller table on the Cayley transitions, filled from `Aprof`
via linked pairs, is well-defined from the infinity set alone (Maler–Staiger
1997 is the entry point; the residual quotient alone is provably too coarse
— `gf_aa_parity`'s is a single state). Parked here, not pursued: the DG
route needs none of those layers.

**The canonical hash — language identity without the formula.** The
synthesized formula would decide language equivalence by normal-form
comparison, but the path stops one object earlier: the formula is a
*function* of the algebra, so it adds nothing to the invariant. The
canonically keyed presentation — classes keyed by shortlex-least
representative over `Σ`, the letter map, the multiplication table, and the
acceptance data (the accepting ω-classes; the algebra alone would confuse
`L` with its complement) — is already a **complete language invariant**:
two languages over the same `AP` are equal iff these tables are identical.
Hash the tables and language equality becomes hash equality. Notably this
needs no aperiodicity — it covers *all* ω-regular languages, LTL-definable
or not — and its sweet spot is many-to-many identity (bucketing a corpus by
true language, e.g. deduplicating the genaut census by hash join) where
pairwise product checks cost quadratically many Spot calls. Per pair it is
rarely cheaper than one product check: the `EM` toll gates it, as always.
