# The Homomorphism Rendering: the SωS Pipeline in Saturation Idiom

**Yann Thierry-Mieg**

With significant inputs from
**Claude (Anthropic)**

*Companion note — 2026-07-07 — peer of `sos_symbolic.md` [SωSD26]*

**Scope.** [SωSD26] designs the symbolic construction of the syntactic
ω-semigroup against an abstract relational engine (`2k`-variable
relations, image/preimage, fixpoints, quotient). This note re-expresses
the same seven phases in the *homomorphism* idiom of hierarchical
decision-diagram libraries — operations as diagram-traversing
homomorphisms with locality-driven automatic saturation, in the
libDDD/libITS style — because the pipeline turns out to sit closer to
that idiom than to the relational one: every iterated operation is a
*map* (deterministic), so the primed-variable half of the relational
encoding disappears, and the one genuinely relational step (preimage in
the refinement) is covered by the engine's inverse mechanism. Nothing
here repeats [SωSD26]'s justifications, phase semantics, or correctness
anchors; only the equations change. **Sourcing note:** the published
lineage (homomorphisms, saturation, hierarchical diagrams) is
library-request territory for the biblio sweep; the inverse-homomorphism
mechanism — reversal intersected with a forward-reachable constraint,
trivial when the map is reversible — exists in the engine (used for CTL
and counterexample extraction) but is undocumented in papers; this note
is its first written account, and §2.5 argues it gets an unusually clean
showcase here.

---

## 1. The idiom, abstractly

Operations are **homomorphisms** `h : Set(V^k) → Set(V^k)`, built from:

| constructor | meaning |
|---|---|
| `loc_q(f)` | apply `f : V → V` (partial: selector+map) at level `q`, identity elsewhere |
| `map(f)` | `loc_q(f)` at every level — a uniform per-level map |
| `sel_q(S)` | keep paths whose level-`q` value lies in `S ⊆ V` |
| `h + h′` | union of results |
| `h ∘ h′` | composition (commuting when supports are disjoint) |
| `h^*` | least fixpoint of `id + h` (accumulating), evaluated with **automatic saturation**: nested at the highest level of `h`'s support |
| `cap_q(v ⇒ h⟨v⟩)` | *inductive/capture* homomorphism: read the level-`q` value into parameter `v`, continue with `h⟨v⟩` below |
| `h⁻¹ ∥ K` | **inverse**: reversal of `h` intersected with the constraint set `K`; exact when `K` contains the codomain of interest; trivial (no intersection) when `h` is reversible |

The **support** of a homomorphism is the set of levels it reads or
writes; saturation's dividend is proportional to how confined supports
are. Parameters of capture homomorphisms multiply cache entries; the
constructions below keep every capture to a *single* `V`-value
(cache `O(k·|V|)` per pass), never a tuple.

Variable layout as in [SωSD26]: one level per slot `q ∈ Q`, domain
`V = Q × 2^C`; pair diagrams stack a second block of `k` levels below
the first (upper block read, lower block written — captures descend).

## 2. The pipeline, re-equated

### 2.1 Letters and closure (Phases 0–1)

Right multiplication by a letter is a uniform map — no primed variables,
no quantification:

```
f_a : V → V,   (s, m) ↦ ( δ(s, a),  m ∪ mk(s, a) )

h_a  =  map(f_a)                              support: all levels (flat input)

EM¹  =  ( Σ_{a ∈ Σ} h_a )^*  ( { 1 } )        1 = the point  ⋀_q (q, ∅)
```

Layers for shortlex: `L₀ = {1}`, `L_{i+1} = (Σ_a h_a)(L_i) \ ⋃_{j≤i} L_j`,
kept. In factored coordinates for an asynchronous product
[SωSD26, §4.2], `h_a` for `a ∈ Σ₁` is `map(f_a)` on the component-1
block and the *identity* on the component-2 block — support confined,
and the closure `h^*` saturates component-wise: the evaluation strategy
coincides with the interleaving factorization, which is the strongest
form of that proposition (not only is the diagram additive, the fixpoint
never leaves the block).

### 2.2 The crossing as single-capture passes (Phase 2)

Composition `z = y·x` reads, at slot `q`, the `x`-slot indexed by
`st_y(q)`. In this idiom it is not one big relation but `|Q|`
commuting single-capture passes over a pair diagram (`x`-block above,
`z`-block below, initialized to `y`):

```
G_p  =  cap_{x_p}( v ⇒  map_{z-levels}( (s, m) ↦ if s = p then (st_v, m ∪ mk_v) else (s, m) ) )

Comp =  ∘_{p ∈ Q}  G_p
```

Each pass rewrites exactly the lower-block slots targeting `p`; the
slot-subsets are disjoint across passes, so the composition order is
irrelevant, and every capture is one `V`-value. The pair layout is
load-bearing: squaring in place would read slots already rewritten;
`{(y, y)} → (∘_p G_p) → {(y, y·y)}` reads captures from the pristine
upper copy. Squaring and the power pairing:

```
Sq       =  project₂ ∘ Comp ∘ pair-diagonal          y ↦ y·y
PowStep  =  Comp with the upper block fixed to x     (x, y) ↦ (x, y·x)
```

Idempotency is a selector of the same shape — for each `p`, capture
`y_p = (s_p, m_p)` and keep paths where every level `q` with
`st(y_q) = p` satisfies `s_p = p ∧ m_p ⊆ m_q`:

```
Idem  =  ∘_{p ∈ Q}  cap_{y_p}( (s_p, m_p) ⇒ sel-all_q [ st = p ⟹ s_p = p ∧ m_p ⊆ m_q ] )
```

The `π`-map: on the aperiodic side, iterate `Sq` to its pointwise
fixpoint (`O(log ℓ)` passes, [SωSD26, Phase 2]); in general, close
`{(x, x)}` under `PowStep` and select `Idem` on the second block — the
unique idempotent per orbit makes the result functional.

### 2.3 Profiles as bit-writers (Phase 3)

Extend the diagram with `|Q|` fresh Boolean levels `bit_q` and compute
`A(q, x) = Acc(mk_{x^π}(st_{x^π}(q)))` by one double-capture writer per
slot, applied to the `(x, e = x^π)` pairing:

```
W_q  =  cap_{e_q}( (p, ·) ⇒ cap_{e_p}( (·, m) ⇒ write bit_q := Acc(m) ) )

Prof =  ∘_{q ∈ Q}  W_q
```

Two nested captures, each one value — cache `O(|V|²)` per level, the
worst parameterization in the pipeline, still bounded and outside every
fixpoint.

### 2.4 Residuals as emptiness tests (Phase 4)

With the `bit_q` levels in place, the seed of the `≃`-refinement on
`Q × Q` is `|Q|²` selector-emptiness queries — no quantifier machinery:

```
q ≁ q′  at seed   ⟺   EM ∩ sel( bit_q ⊕ bit_{q′} )  ≠  ∅
```

and the gfp refinement over `Q × Q` is explicit-sized, as in
[SωSD26, Phase 4].

### 2.5 Refinement with inverses (Phase 5) — the showcase

The congruence's greatest fixpoint needs preimages of the letter maps on
pair diagrams:

```
~  =  gfp  R ↦ Seed ∩ ⋂_{a ∈ Σ}  ( h_a ⊗ h_a )⁻¹ ∥ (EM × EM)  ( R )
```

This is where the engine's inverse mechanism gets its clean showcase.
In its native uses (CTL, counterexamples) the intersection with the
forward-reachable set is a semantic necessity whose constraint set must
itself be computed and argued about. Here the constraint set is
`EM × EM` — the product of Phase 1's closure with itself, already in
the store — and the algebra *closed the universe first*: right
multiplication maps `EM` into `EM`, so clipping the reversed map to
`EM × EM` is not an approximation being repaired but the exact preimage
on the only universe that exists. The reversible shortcut essentially
never fires (`f_a` merges states through `δ(·, a)` and loses mark bits
through the union — and a letter acting as a nontrivial permutation is
a group suspect, doubly unlikely on the LTL side), so the
intersection path is the operative one, at zero extra cost.

### 2.6 Quotient, keys, and the counterexample correspondence (Phase 6)

The quotient primitive applies to `EM¹/~`; what deserves a remark is
representative extraction. Shortlex keys are recovered by backward
chaining through the kept layers,

```
pick x ∈ κ ∩ L_i  (i minimal)  ;  find a least with  x ∈ h_a( L_{i−1} )  ;  recurse on  (h_a)⁻¹ ∥ L_{i−1} ({x})
```

— which is *verbatim* the engine's counterexample-trace machinery: the
same inverse-with-constraint steps that reconstruct a CTL witness
reconstruct here the lexicographically-least word naming an algebra
class. Shortlex keying **is** counterexample extraction, run on the
Cayley reachability instead of a model's; canonicity comes from choosing
the least letter at each step, exactly as least witnesses do. The
λ-quotient guards and `P`-evaluation are small and explicit as in
[SωSD26, Phase 6].

## 3. Support table (where saturation fires)

| homomorphism | support (flat input) | support (factored coords, product input) |
|---|---|---|
| `h_a`, `a ∈ Σᵢ` | all levels | component-`i` block only |
| closure `(Σ h_a)^*` | global fixpoint | **nested per block** — saturation's case |
| `G_p` (crossing) | level `x_p` + lower block | level `x_p` + lower block (unchanged) |
| `W_q` (profile) | levels `e_q`, `e_{st}`, `bit_q` | same |
| `(h_a ⊗ h_a)⁻¹ ∥ ·` | pair blocks | component pair blocks |
| key extraction | layer-constrained inverses | same, per block |

The moral in one line: on flat inputs the idiom buys the *map* economy
(no primed variables, fused single-traversal letter application); on
structured inputs it additionally buys saturation, and the two
[SωSD26, §4.2] worlds — additive versus exponential — are visible right
in this table's second column.

## 4. What the rendering costs

Honesty items, mirror-images of the wins: the crossing costs `|Q|`
passes with `O(|V|)` parameter instances each and the profile writers
`O(|V|²)` — the cache, not the diagram, is where Phase 2–3 pressure
lands; the gfp of Phase 5 is the one place the idiom leans on inverses
rather than native structure (the relational rendering of [SωSD26]
keeps a symmetric `2k` relation there — which formulation wins is an
implementation A/B, not a theorem); and accumulating `h^*` computes
unions of iterates, so the pointwise *limit* objects (the `π`-map)
need their selector (`Idem`) rather than a bare fixpoint. ⟨TBD:
measurements — pass counts and cache profiles on the census corpus and
the product families; the A/B of §2.5 vs the relational Phase 5.⟩

---

## References

- **[SωSD26]** Y. Thierry-Mieg, with Claude (Anthropic). *A symbolic
  engine for the syntactic ω-semigroup* (`sos_symbolic.md`). Working
  draft, 2026.
- **[SωS26]** Y. Thierry-Mieg, with Claude (Anthropic). *Constructing the
  syntactic ω-semigroup from a deterministic Emerson–Lei automaton.*
  Working draft, 2026.
- ⟨TBD: the homomorphism/saturation lineage (hierarchical set decision
  diagrams, automatic saturation, libDDD/libITS tool papers) — library
  requests; the inverse mechanism is per-engine capability, undocumented,
  first written down here.⟩
