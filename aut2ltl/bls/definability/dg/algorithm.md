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
recognized by `h` (presented finitely: a set of elements of `T` for the
finite-word part, a set of `≈h`-classes of infinite words for the ω-part),
and the prepend letter — synthesize `φ ∈ LTL_Δ[XU]` with `N = L_{c,Δ}(φ)`.
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
- `T₂ = { [u]_{h|A} | u ∈ A^∞ }` — the `≈`-classes of *infinite* `A`-words
  under the restricted morphism: at most `|T|²` of them (linked pairs).

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
`n` as the prepend letter. The regime guards and the shapes `nT₁*m`,
`nT₁^ω` are directly definable over `T`.

**The saturation is a table on the finite side.** For `w ∈ T₁*`, membership
of `n·w·m` in `σ(N)` depends on `w` only through `g(w)`: the `Δ`-word it
denotes has prefix value `n·g(w)` in `T` (the interleaved `c`'s are exactly
`g`'s boundary `c`'s) and tail class `m`, so

```
[ n⁻¹σ(N) ∩ T₁* m ]_g  =  { w·m  |  g(w) ∈ X_{n,m} },
X_{n,m}  =  { x ∈ T' | Accept(n·x, m) }
```

— and `Accept(element, ω-class)` is a `P`-table lookup once `m` is
represented by a linked pair (`P(n·x·s, e)` for `m ∋ rep = s·e^ω`-shaped
words). No search, no witnesses: the finite-side recursion target is
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
    induction (`L_{c,A}(ψₘ) = A^∞ ∩ m`).
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

## 6 — The ω-class calculus (`T₂`, and `K₂`'s class sets)

The one genuinely construction-level piece of engineering [DG] leaves
implicit is the finite handling of the infinite-word classes:

- **Representation.** A `T₂`-letter is an `≈_{h|A}`-class of `A^ω`-words
  (plus, on the `Σ^∞` frame, the finite-word tail cases carried by the
  contract's class-set presentation). Every class contains an
  ultimately-periodic word `s·e^ω` for a linked pair of `h|A` ([DG] 5.2),
  so classes are presented by linked pairs — with the caveat that distinct
  pairs can present the same class.
- **Finer is safe.** If pair-identity is tested by a *sound but incomplete*
  equivalence, classes over-split: `T₂` grows, `σ` stays a well-defined
  function, `K₀/K₁` union over more letters, and nothing downstream breaks
  — the cost is alphabet size, never correctness. The implementation may
  therefore start with a cheap sound merge (at the root, where `h` is
  *syntactic*, the left-context acceptance vector `x ↦ P(x·s, e)` is a
  natural exact key candidate) and refine only if measurements demand it.
  Pinning the cheapest *exact* identity test is open point **O2**.
- **Evaluation.** The `K₂` class sets need "is `n·(class member) ∈ σ(N)`":
  render the class's linked-pair representative into `Δ`-words (per-letter
  `A*`-representatives from a BFS over the `A`-generated submonoid), read
  the resulting ultimately-periodic word's pair off the tables, look up
  `P`. Constancy across the class's `T₁^ω`-members is [DG]'s auxiliary
  results; the implementation just evaluates one representative.

## 7 — Unwinding the device at the root

The root call returns `φ` with `L = L_{fresh,Σ}(φ)` — evaluated on `fresh·w`.
Since `L ⊆ Σ^ω` never contains `ε`, [DG] Remark 7.1 / Prop 8.1(1) convert:
strip the anchor by taking the `X`-successor view of `φ` (`L_Σ(φ') = L` for
`φ'` obtained by the Remark's letter-substitution, or directly
`φ' = X-shifted φ` since only position 0 sees the fresh letter). The final
formula is standard pure-future LTL over `Σ^ω`; internal `XU` unfolds as
`X(· U ·)` for the host DAG. The internal `Σ^∞` semantics never leaks: all
finite-word formulas live inside lifted (`·^c`) contexts, where the block's
end is a real position of the host word.

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
- **`T₂` keys.** Linked pairs ordered by (shortlex `s`-rep, shortlex
  `e`-rep) after the O2 merge.

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
- **O2 — the ω-class identity test.** "Finer is safe" (layer 6) makes a
  sound merge sufficient for correctness; the open question is the cheapest
  *exact* test for `[s·e^ω] = [s′·e′^ω]` under `≈_{h|A}`, to keep `T₂`
  minimal and the normal form tight. Candidate at the root: left-context
  acceptance vectors (exactness to argue from syntacticity).
- **O3 — pivot heuristics.** v0 pins least-visible-letter; deterministic
  size-minimizing pivots are a later, measured change of normal form.
- **O4 — worked examples.** Hand-walk `fairness_example` and
  `gf_aa_parity` (the flagship: the input whose cascade is form-blocked;
  `|S¹| = 6`) through layers 3–7; the walks become a layer of this
  document, in the oracle document's style, and double as the first
  fixtures for O2's class calculus.
- **O5 — module map** (draft, one role per module, mirroring the oracle):
  `morphism.py` (the layer-1 tables + canonical re-keying), `divisor.py`
  (the local divisor: carrier, `∘`, the strict-decrease assert),
  `compress.py` (the `c`-factorization data: `T₁`, `T₂`, `σ`-tables, the
  `X_{n,m}` sets), `omega_classes.py` (layer 6), `lift.py` (Lemmas
  8.3/8.4, the only formula-producing module), `dg.py` (the induction
  driver: pivot, the `K` assembly, caps — the only sequencing). Probe:
  `tests/probes/dg_probe.py`, one HOA per invocation, Spot-verifies, ≤15 s.
- **O6 — wiring.** Whether this surfaces as a `Translator`, and where it
  sits relative to the gate (an LTL verdict with a formula attached), is
  the assembly's concern — out of scope here, exactly as gate wiring was
  for the oracle.

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
