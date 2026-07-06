# The LTL Frontier from the Syntactic ω-Semigroup: Certificates, Formulas, and the Shape of the Cut

**Yann Thierry-Mieg**

With significant inputs from
**Claude (Anthropic)**

*Skeleton draft — 2026-07-06 — placeholders marked `⟨TBD: …⟩`*

## Abstract

Whether an ω-regular language is expressible in linear temporal logic is a
single read-off of its syntactic ω-semigroup — aperiodicity — and that object
is now constructible from any deterministic automaton [SωS26] and learnable
from lasso queries alone [SωSL26]. This paper is about what lies on either
side of the read-off: given the invariant `𝓘(L) = (𝒞, λ, M, P)`, *rebuild the
object the verdict calls for*. On the non-LTL side, a portable witness
certificate — the group, packaged as a checkable counting family. On the LTL
side, a defining formula — where the only prior route, the local-divisor
induction of Diekert and Gastin [DG08], is an existence proof that consumes an
anonymous recognizer, ignores every structural fact the algebra knows, and
explodes. We give an extraction driven by the algebra's own read-offs. Its
engine is a *transcription*: the deterministic walk of prefix classes on the
right Cayley graph of `S(L)₊¹` is transcribed layer by layer into a fixed set
of flat LTL bricks — anchored laws, `GF`-windows, park terms — where the layers
are the R-classes of the monoid, an anchor is a letter acting as a reset on
its layer, stuttering is locally-neutral action, and a park is nothing but a
linked pair of `P`. The preconditions for each layer are equations on the
multiplication table, decided once on the canonical object — where an
automaton-level transcription is form-dependent, passing on one presentation
of `L` and failing on another. Where the walk freezes with acceptance still
undecided, the transcription hands over to the second engine: the frozen
layer is exactly the ω-power half of Arnold's congruence, and its templates
are the `GF`/`FG` shapes of the topological ladder, read off `P`. Arnold's two
context shapes thus become the extraction's two engines. Nesting appears only
where the algebra provably demands it — the until-rank read-off certifies the
depth — and the formula is computed as a class-indexed DAG that scales;
flattening it is the language's own intrinsic cost, which we measure, bound,
and, in a definitional output format, avoid. An exhaustive census of small
automata shapes the frontier empirically: below ⟨TBD: census thresholds⟩ no
non-LTL language exists, and the inner frontier — which rungs of the flat-brick
ladder suffice — is mapped on the same corpus. ⟨TBD: experimental headline.⟩

---

## 1. Introduction

The classical chain `LTL = FO[<] = star-free = aperiodic` [Kam68, Tho79,
Per84, DG08] makes LTL-definability of an ω-regular language `L` a property
of one canonical object: the syntactic ω-semigroup `S(L)`, aperiodic exactly
when `L` is LTL. For four decades the chain was a classification without a
workflow — the object was never built. It now is [SωS26], and is even
learnable from membership queries on lassos [SωSL26]. The verdict is a table
lookup: power-iterate every class of the multiplication table; a cycle of
period `> 1` is a group, and the language is not LTL; no cycle, and it is.

This paper is about the day after the verdict. A verdict, alone, satisfies
nobody:

- If `L` is **not** LTL, the user holds a specification (typically PSL/SERE,
  where mod-`p` counting enters through an innocuous `{·}[*2]`) and deserves a
  *witness*: a concrete, portable, independently checkable certificate of the
  group — which words, pumped how, flip membership forever.
- If `L` **is** LTL, the user deserves the *formula*. Existence has been known
  since Kamp; the only effective route from an algebra, the local-divisor
  induction of Diekert and Gastin [DG08, §8], recalled in §3, is a proof of
  doability — blind to the structure of its input, never implemented against a
  real object, and explosive by construction.

Both rebuilds consume the same input: the exportable invariant
`𝓘(L) = (𝒞, λ, M, P)` of [SωS26] — classes keyed by shortlex representatives,
letter map, multiplication table, accepting linked pairs. The non-LTL side is
the shorter story and is summarized in §4 ⟨TBD: import/condense the
certificate construction from the working notes⟩. The LTL side is the body of
the paper, and its thesis is:

**The formula should be a *transcription* of the canonical object, not the
residue of a generic induction.** The invariant contains, as read-offs, every
structural fact a formula must express — which letters the language actually
distinguishes (`λ`), where it sits on the safety–progress ladder (`P`'s
closure structure), whether prefixes matter at all (the residual count),
where runs commit irrevocably (absorbing classes), and, we show, *which parts
of the language are expressible by flat temporal bricks and which genuinely
need nesting*. An extraction that consults these read-offs emits formulas
whose shape mirrors the language's shape; one that does not — DG's — pays for
its blindness in output size, and the paper quantifies the difference.

The engine of the transcription was found in an unexpected place: an
automaton-level construction from our own toolbox (the `k-anchor` production
of the aut2ltl portfolio [KA26]) that labels a strongly-connected component
of a deterministic ω-automaton *exactly*, with no equivalence oracle, by a
fixed vocabulary of flat LTL bricks — whenever the state occupied by the run
is recoverable from the last `k` letters of the word, modulo stuttering. It
is smart, and it is *shape-dependent*: its preconditions are tests on one
automaton form, and a language can pass in one presentation and fail in
another. Transported onto the right Cayley graph of `S(L)₊¹`, every one of
its ingredients lands on a named algebraic object (§5, Table 2): components
become R-classes, anchors become reset actions, stuttering becomes locally
neutral action, its park/fairness dichotomy becomes the linked pairs of `P`,
and its graded window ladder becomes a ladder of definiteness equations on
the multiplication table — decided once, on the canonical object,
presentation-independently. The hope this transport rests on — that
"anchoring" is at bottom a property of the *language* that the automaton
tests merely approximate — is formalized in §5.3 and is one of the paper's
two central technical claims.

The second claim emerged from working the transport on the running example
and reads like a moral (§5.5): the class walk transcribes exactly the
*linear* half of Arnold's congruence, and where the walk freezes with
acceptance still open — which for a prefix-independent language is
essentially everywhere — the remaining content is exactly the *ω-power* half,
requiring its own engine with `GF`/`FG`-shaped templates read off `P`.
**Arnold's two context shapes, which [SωS26] computed as two relations and
[SωSL26] harvested as two column sorts, resurface in extraction as two
engines.** The construction is one family: the same split, met a third time.

**Contributions.**
1. The frontier, both directions, from one object: the aperiodicity verdict
   with, on failure, a portable non-LTL witness certificate (§4), and, on
   success, a defining formula (§5–§7).
2. A presentation-independent transcription engine: layers = R-classes of
   the right Cayley graph of `S(L)₊¹`; per-layer anchoring as equations on
   `M`; flat-brick emission with exactness by construction; the frozen-layer
   handover to ω-templates (§5).
3. The deliverable split, stated as a result: extraction is
   output-polynomial as a class-indexed DAG (which our implementation
   computes at scale); the flat formula is the language's intrinsic cost,
   bounded by the R-depth and until-rank read-offs, and avoidable in a
   definitional format (§6).
4. The inner frontier: within LTL, the algebra grades which layers admit
   flat transcription and which demand nesting, with the until-rank as a
   per-language lower-bound certificate on formula depth (§7).
5. ⟨TBD: census evaluation contribution line.⟩

## 2. Background: the object and its read-offs

We assume [SωS26]'s construction and reuse its notation and running
examples; this section only fixes what extraction consumes.

**The invariant.** `𝓘(L) = (𝒞, λ, M, P)`: finite class set `𝒞` with a fresh
identity `[ε]` (adjoined unconditionally — every other class carries a
non-empty shortlex key), letter map `λ : Σ → 𝒞`, multiplication table
`M : 𝒞 × 𝒞 → 𝒞`, accepting linked pairs `P ⊆ 𝒞 × 𝒞`. Membership of a lasso
`u·v^ω`: fold `u, v` through `λ` and `M`, iterate the loop class to its
idempotent `e`, and accept iff `(u-class·e, e) ∈ P`. Two languages are equal
iff their invariants are byte-equal [SωS26, Thm 5.1].

**Read-offs used below** (each a polynomial scan of the table):
- *aperiodicity* — no power orbit of period `> 1`; the frontier verdict.
- *the letter quotient* — `λ` collapses letters the language never
  distinguishes; extraction works over `λ(Σ)` and restores atomic
  propositions last.
- *the ladder position* — safety / co-safety / obligation / recurrence /
  persistence / reactivity as closure conditions on `P` [SωS26, §7.1].
- *residual count* — one residual ⟺ prefix-independent ⟺ the linear half
  is blind [SωS26, Prop 4.6].
- *absorbing classes* — two-sided zeros; runs that reach them have committed.
- *until-rank* — Wilke's grading of until-nesting as a semigroup power
  condition [Wil99]; a lower bound on the depth of any defining formula.
- *complementation* — `P ↦ P^c` for free; extraction may choose the cheaper
  of `L`, `L̄` and negate.

**Running examples.** The triptych of [SωS26]: `GF(aa)` (LTL; the extraction
specimen, worked in §5.4), `Even` and `EvenBlocks` (not LTL; the certificate
specimens, §4). Their invariants — six, five, and eight classes — are
reproduced in [SωS26, Table 3] and used here without re-derivation.

## 3. The prior route, and why it explodes

⟨TBD: compress to ~1 page the §8 construction of [DG08], in the form
established in the working discussion:⟩

The Diekert–Gastin induction takes any morphism `h : Σ* → M` onto a finite
aperiodic monoid recognizing `L` and builds `φ` by a double induction on
`(|M|, |Σ|)`. One step: fix any letter `c` with `h(c) ≠ 1`; factor every word
at its `c`'s; abstract each `c`-free block to a *letter* of a new alphabet
`T` (one letter per block image in `M`, one per class of `c`-free tails);
recognize the abstracted language by the **local divisor**
`M' = h(c)M ∩ Mh(c)` (product `xm ∘ my = xmy`, neutral `h(c)`), which is
aperiodic and *strictly smaller* — the only use of aperiodicity in the whole
construction; recurse on `M'` for the block-sequence language and on the
smaller alphabet `Σ \ {c}` for each block language; lift back through
relativized (`µ`-confined) subformulas and a sentinel letter.

Four sources of explosion, each a blindness:
1. the recursion is two-dimensional and multiplicative — depth up to
   `|M|·|Σ|`, and each level *inflates* the alphabet to `O(|M| + |M|²)`
   letters before shrinking the monoid;
2. every occurrence of a `T`-letter unfolds to a full recursive formula for
   `h⁻¹(m)`, rebuilt at every occurrence — no sharing;
3. the separator `c` is arbitrary, though it determines the recursion tree;
4. nothing consults the input's structure: not the ladder position, not
   prefix-independence, not the ideal structure, not even that the
   *syntactic* algebra (the coarsest recognizer, with the smallest block
   alphabets and the smallest J-depth) is available.

Our implementation experience sharpens the diagnosis: with class-indexed
memoization the DG-style recursion *computes* at scale — the formula-DAG is
tractable — and what explodes is exclusively the *flat* rendering, LTL syntax
having no sharing. The bottleneck is not computation but the deliverable
format; §6 makes that split a stated result rather than an engineering
apology. The extraction of §5 attacks what remains: the flat size, by making
the formula's shape follow the language's.

## 4. The non-LTL side: the witness certificate

⟨TBD: this section imports the certificate construction from the working
notes (non_ltl_certificates.md) and [SωS26]'s aperiodicity read-off. Fixed
decisions, so the section can be written into:⟩

- The verdict: a power orbit `c, c², …` of eventual period `p > 1` in `M` — a
  group element, intrinsic by canonicity (never a presentation artifact,
  [SωS26, Prop 3.4 / Thm 4.5]).
- The certificate: a *counting family* — concrete words `x, u, y` (shortlex
  keys of the classes involved) and a context shape (linear or ω-power,
  matching which of Arnold's shapes witnesses the separation) such that
  membership of the family's lassos is periodic in the pump count with
  period `p`. For `Even`: `a^n·!a·a^ω ∈ L ⟺ n even` (linear shape). For
  `EvenBlocks`: `(a^n·!a)^ω ∈ L ⟺ n even` (ω-power shape) — the two shapes'
  minimal witnesses, [SωS26, Table 1].
- Checkability: the certificate is verified against any acceptor of `L` by
  `2p` lasso membership tests — no algebra needed on the verifier's side.
- ⟨TBD: the formal statement — soundness (a valid family refutes
  counter-freeness, hence LTL), completeness (every non-LTL `L` yields one
  with words of length `O(|𝒞|)`), and the extraction algorithm's cost.⟩
- ⟨TBD: relation to the census — at 2 states / 1 AP / 1 acceptance set no
  non-LTL specimen exists; the smallest non-LTL specimens and their
  certificates, tabulated.⟩

## 5. The LTL side: transcribing the Cayley walk

This section is the paper's core. The plan: the canonical deterministic
machine hiding in `𝓘(L)` (§5.1); the transport dictionary from the
automaton-level k-anchor production to that machine, turning per-form tests
into per-language equations (§5.2–5.3); the worked example (§5.4); and the
frozen-layer handover that completes the architecture (§5.5).

### 5.1 The Cayley walk

**Definition 5.1 (the class machine).** `Cay(L)` is the deterministic,
complete automaton with states `𝒞`, initial state `[ε]`, and transitions
`c →^a M(c, λ(a))`. Reading a finite word `u` from `[ε]` lands exactly on
its class `[u]` — the *prefix-class walk* `ψ(u)`.

`Cay(L)` is a function of `L` alone: canonical where no minimal
deterministic ω-automaton exists. Its transition structure is counter-free
exactly when `L` is LTL (aperiodicity of `M` is aperiodicity of its right
regular representation).

**Lemma 5.2 (the walk decides membership).** If two ω-words admit block
factorizations with pointwise-equal prefix-class walks, they are
equi-members of `L`. In particular any acceptance datum consistent with `P`
on ultimately-periodic words makes `Cay(L)` a recognizer of `L`.

*Proof sketch.* The syntactic morphism recognizes `L`; equal walks force
equal images of all block products; conclude by the skeleton argument of
[SωS26, Lem 3.2] applied to the syntactic morphism. ⟨TBD: write out.⟩ ∎

**Lemma 5.3 (monotone descent).** `[u·a] ≤_R [u]` for every letter `a`
(right multiplication never climbs Green's R-order). Consequently the SCCs
of `Cay(L)` are exactly the R-classes of `S(L)₊¹`, the SCC DAG is the
R-order, and every walk eventually stays inside one final R-class.

*Proof.* `[ua] ∈ [u]·M¹` gives the inequality; mutual right-reachability
*is* R-equivalence; a monotone walk in a finite order stabilizes. ∎

Lemma 5.3 hands us, for free, the recursion skeleton that DG had to
manufacture: **peel the initial R-class, delegate exits to the R-classes
below, descend the R-order** — with depth the R-depth of the *syntactic*
monoid, minimal over all recognizers of `L`. What remains is to label one
layer, and that is where the transported production enters.

### 5.2 The transport dictionary

The k-anchor production [KA26] labels the initial SCC `C` of a deterministic
state-based ω-automaton by a disjunction `STAY∞ ∨ LEAVE` of flat bricks —
`sojourn(s) = L(s) W M(s)`, laws `G(trigger → X^k sojourn)`, fairness
`GF(window)`, park terms `F(window ∧ X^k G L(s))`, and one `U`-chain per exit
child — *exact by construction* whenever the state occupied by the run is a
function of the last `k` letters modulo stuttering (preconditions P1/P2 and
their graded versions, decided by BDD tests on the component). Run the same
production on a layer `R` of `Cay(L)` and every ingredient becomes algebra
(for a letter `a`, its *within-layer action* is the partial map
`c ↦ M(c, λ(a))` restricted to sources and images in `R`):

| k-anchor on an automaton SCC [KA26] | on a layer (R-class) of `Cay(L)` |
|---|---|
| component `C` of the run | R-class `R` of the prefix class |
| the phase (occupied state) | the syntactic class of the prefix |
| loop letter at `s` (`L(s)`) | letter *neutral at* `c`: `M(c, λ(a)) = c` |
| promoted loop (names its state) | letter whose within-layer action has singleton image |
| anchor `A(s)` (P1: partition) | letter acting as a **partial constant (reset)** on `R` |
| P2 (loops fake no anchor) | no letter mixes identity and reset behavior on `R` |
| the k-graded window ladder | **definiteness equations** on the layer's action semigroup (§5.3) |
| exits `E(s)` | edges leaving `R` — strict R-descent, delegated below |
| park at `s` on `G L(s)` | a **linked pair** `(c, e)`: `M(c, e) = c`, `e` the stutter class |
| `F_all` (park accepts) | `(c, e) ∈ P` |
| `GF(enter-window)` fairness | the pair formed inside the recurring window set ⟨TBD: exact statement⟩ |
| child label `φ_d` at exit `d` | the extraction rooted at class `d` — **memoized per class**: at most `\|𝒞\|` distinct children ever, the DAG is class-indexed |

**Table 2.** The transport dictionary. Every operational notion of the
automaton-level production is a named object of the algebra; the two columns
are one construction read at two levels.

**Definition 5.4 (anchored layer, k = 1).** A layer `R` is *1-anchored* if
the within-layer action of every letter is either a partial identity
(stutter — shared idleness across several classes is allowed) or a partial
constant (reset — the diagonal case, a constant fixing its own target, is
allowed). Mixed actions — identity at one class, while also sending another
class of `R` somewhere in `R` — are what the condition excludes.

This is kanchor's P1+P2 verbatim, evaluated on canonical states. Note what
it is *not*: it is not a property of any automaton the user supplied; it is
an equation schema on the multiplication table, `∀c, c' ∈ R` with images in
`R`: `M(c, λ(a)) = c ∨ M(c, λ(a)) = M(c', λ(a))` letterwise. Identity-or-
reset is the Krohn–Rhodes reset brick — the atomic layer of the aperiodic
cascade — surfacing as the transcribable case, which is not a coincidence
⟨TBD: remark tying to the cascade literature [KR65, Mal10] and to the bls
engine of aut2ltl⟩.

**Definition 5.5 (anchored layer, graded).** ⟨TBD: the k-graded version —
products of `k` within-layer actions, stutter positions absorbed by
`I`-weakening as in [KA26, §5], act as constants; the clean equational form
`x·s₁⋯s_k = s₁⋯s_k` (k-definiteness) localized to the layer's action
semigroup modulo its neutral part; monotonicity of the ladder in `k`.⟩

**The bricks, transported.** For a 1-anchored layer `R` with anchor targets
`t(a)` per reset letter and stutter sets `N(c)` per class ⟨TBD: full label,
following [KA26, §4.3] with: `sojourn(c) = N(c) W (moves out of c)`, the
anchored law `G(a → X sojourn(t(a)))` per reset letter, parks as linked-pair
lookups in `P`, exits to memoized class children; then the graded version
following [KA26, §6–7]⟩. Exactness transports with the phase lemma: the walk
is deterministic on `Cay(L)` *by construction*, so the uniqueness leg of
[KA26, §10] is immediate, and the completeness/soundness legs are unchanged
⟨TBD: restate the three legs on the algebra; the licence for eager triggers
([KA26, §5.4]) carries verbatim⟩.

### 5.3 Anchoring is a property of the language

The automaton-level production is honest about its form-dependence: its
preconditions are tested on one presentation, "an input can pass in one
automaton form and fail in another" [KA26, §12]. On `Cay(L)` the tests are
evaluated on the canonical object, so *our* pass/fail is a function of `L` —
by fiat. The substantive claims are the two comparisons:

**Claim 5.6 (soundness of the finer phase).** The syntactic class is the
finest phase: if a layer of `Cay(L)` is k-anchored, the transcription is
exact for `L` — no reference to any presentation. (This is §5.2's exactness;
the claim is that nothing more is ever needed.)

**Conjecture 5.7 (the automaton tests approximate a language property).**
If *some* deterministic presentation of `L` passes the automaton-level
preconditions at width `k` on a component, then the corresponding layers of
`Cay(L)` pass at width `⟨TBD: k? f(k)?⟩`. ⟨TBD: this is the delicate
direction — the class phase is finer than any automaton phase, and finer
phases are harder to recover from windows; the conjecture may need the
comparison routed through the *language-level* property ("the class of the
prefix is eventually a function of the last k letters modulo locally-neutral
letters") rather than through the Cayley machine test. Settle on the census:
run both, tabulate agreements and the direction of every disagreement.⟩

If Conjecture 5.7 holds in a usable form, the paper's statement is clean:
the automaton production was computing an approximation, on one
presentation, of an equational property of the syntactic algebra — and the
algebra computes the property itself. If it fails, the failure is itself a
finding (a genuinely presentation-bound transcription), and Claim 5.6 stands
alone as the self-contained engine. Either way the extraction is
well-defined; only the *comparison* is at stake.

### 5.4 Worked example: `GF(aa)` on its own algebra

`S(GF(aa))₊¹` has six classes `[ε], [!a], [a], [!a·a], [a·!a], [a·a]`
(indices `0..5`) and multiplication table [SωS26, Table 3(a)]. Reading the
Cayley edges `c →^x M(c, λ(x))` off that table:

```
0: !a → 1    a → 2          3: !a → 1    a → 5
1: !a → 1    a → 3          4: !a → 4    a → 2
2: !a → 4    a → 5          5: !a → 5    a → 5
```

The SCC decomposition — the R-order — is:

```
        {0}                       layer R₀: the start, transient
       /   \
   {1,3}   {2,4}                 two parallel layers ("last was !a" side,
       \   /                      "started with a" side)
        {5}                       layer R∞: "contains aa", absorbing
```

Per-layer letter actions, and the k = 1 test:

- **Layer `{1,3}`**: `!a` maps `1 ↦ 1, 3 ↦ 1` — image `{1}`, a partial
  constant (fixing its own target: the allowed diagonal). `a` maps `1 ↦ 3`
  (and exits from `3`) — image `{3}`, constant. **1-anchored**: `!a` anchors
  `[!a]`, `a` anchors `[!a·a]`, no residual stutter.
- **Layer `{2,4}`**: symmetric — `!a` anchors `[a·!a]`, `a` anchors `[a]`
  (from `4`; exits from `2`). **1-anchored.**
- **Layer `{5}`**: both letters neutral everywhere. All-stutter: the walk is
  frozen. (§5.5.)

Two observations, each earning its keep:

**The algebra anchors where the automaton could not.** On the minimal
3-state DBA of `GF(aa)`, the k-anchor production needs width `k = 2`: the
letter `a` enters two distinct states and loops at a third, so P1 and P2
both fail at `k = 1` [KA26, §9.2]. On the classes, the same letter is a
clean reset *per layer* — because the R-decomposition separates, into
different layers, states the automaton was forced to hold side by side, and
anchors need only disambiguate within a layer, exits being unconstrained.
The canonical machine is bigger and *easier*. ⟨TBD: is this a theorem
("layer-local anchoring width ≤ any-form anchoring width") or an instance?
Relates to Conjecture 5.7.⟩

**The transcription of the walk, alone, is not the language.** The walk
reaching layer `{5}` says "an `aa` has occurred" — and `GF(aa)` is not
"eventually `aa`". Acceptance turns on what recurs *after* the walk has
frozen: the accepting pairs of `GF(aa)` are exactly `{([a·a], [a·a])}`, and
a tail parked at `5` accepts iff its recurring loop's idempotent power is
`[a·a]` — i.e. iff `aa`-factors recur. The class walk has carried all it
can; the rest is the next subsection's business.

### 5.5 The frozen layer is Arnold's second shape

When the walk stabilizes in its final layer with all letters neutral (or
more generally when a park's acceptance depends on *which* stutter loop
recurs, not merely that one does), the transcription faces a tail language
that the prefix classes cannot see. This is not a corner case; it is a
theorem-shaped fact:

**Proposition 5.8 (the division of labor, transported).** The class-walk
transcription expresses exactly the discrimination carried by the linear
half `~lin` of Arnold's congruence (residual structure: which class the
prefix has reached). The frozen-layer condition — acceptance as a function
of the recurring loop structure at a fixed class — is exactly the
discrimination carried by the ω-power half `~ω`. In particular, for a
prefix-independent `L` (one residual, `~lin` total [SωS26, Prop 4.6]) the
walk carries *no* acceptance information beyond reachability, and the
entire language lives in the frozen-layer engine. ⟨TBD: precise statement
and proof; the GF(aa) instance: prefix-independent, and indeed the parked
tail language at layer `{5}` is `GF(aa)` itself — the walk engine
terminates, it does not recurse, and the handover is mandatory, not an
optimization.⟩

The frozen-layer engine has its own automaton-level ancestor in the
portfolio: the **daisy** production [DA26], which labels a single state
whose only incoming edges are self-loops — petals and stems — in closed
form, `STAY∞ ∨ LEAVE` with `STAY∞ = G(σ) ∧ ⋀_i GF(σ_i)`. Two of daisy's
design commitments, which kanchor lacks, are exactly what the frozen layer
needs, and both transport *better* to the algebra than to any automaton:

- **Transition-based acceptance.** Daisy insists on the TGBA form because
  "a single state encodes a rich generalized-Büchi condition — a different
  petal set per acceptance set — that state-based marking could not express
  without splitting" [DA26]. That is the automaton shadow of [SωS26]'s §2
  point that ω-acceptance is a set of *pairs*, not a subset of classes: a
  frozen class `c` is one "state", and what accepting there depends on is
  *which loops recur* — the idempotents `e` with `(c, e) ∈ P`, the algebra's
  native per-petal marks. Daisy's `⋀ GF(σ_i)` is the frozen-layer template
  with petals of length one; the algebra generalizes the petal to a
  *window* — a finite word whose fold from `c` contributes to an accepting
  idempotent — and `GF(σ_i)` to `GF(window)`. `GF(aa)` parked at `[a·a]` is
  a daisy whose accepting petal is the length-2 window `a ∧ Xa`.
- **Nondeterminism absorbed by disjunction.** Daisy never determinizes:
  overlapping stems are a `∨`. On `Cay(L)` the walk is deterministic by
  construction, so this power is not needed for the walk — but the same
  absorption reappears one level up, as the union over accepting pairs
  (§2's read-offs): each `(c, e) ∈ P` is one more way to accept, never a
  constraint on the others.

What does *not* transport is daisy's reliance on the marks being letter-
visible: on the algebra the "marks" are class values of *words*, so the
frozen-layer petals are inherently `k`-windows, and the single-letter case
is the degenerate rung. The frozen-layer engine, then, must express:
*accept iff the recurring finite factors of the tail, folded through `M`
from the frozen class `c`, form loops `e` with `(c, e) ∈ P`*. Its templates
are the ladder's:

- **recurrence rung** (`Gδ`, deterministic-Büchi): `GF(window)` shapes —
  for `GF(aa)`, accept iff windows folding into `{[a], [a·a]}`-loops recur;
  emitted as `GF(a ∧ Xa)` ⟨TBD: the general window read-off — from the
  accepting idempotents at `c`, derive the finite window set whose
  recurrence is equivalent; this is "locally testable at infinity" when the
  frozen local algebra satisfies ⟨TBD: which equations⟩, and the length of
  the needed windows is bounded by ⟨TBD: the local definiteness degree?⟩⟩;
- **persistence rung** (`Fσ`, co-Büchi): dually `FG(window)`;
- **reactivity**: Boolean combinations, following the pair structure of `P`
  restricted to the frozen class × its idempotents;
- ⟨TBD: the case where the frozen layer is *not* locally-testable-at-
  infinity — the genuine nesting case; here and only here a DG-style local
  division survives, demoted to "the engine inside one frozen layer",
  bounded by the layer's local algebra rather than the whole monoid.⟩

The architecture, assembled — the paper's picture:

```
extract(𝓘):
  0. aperiodicity scan — group ⟹ certificate (§4), stop
  1. quotient the alphabet by λ; choose L or L̄ by P-shape (cheaper side)
  2. ladder read-off: safety/co-safety/obligation ⟹ finite-word extraction
     of the class-defined prefix language + fixed template, stop
  3. walk engine: descend the R-order of Cay(L); per layer:
       anchored at k ≤ cap  ⟹ flat bricks (laws, GF-windows, parks=P-pairs),
                               exits to memoized class children
       else                 ⟹ ⟨TBD: layer-internal decomposition; DG local
                               division as last resort, scoped to the layer⟩
  4. frozen layers: ω-engine — GF/FG window templates from P at the frozen
     class; nesting only where the local algebra demands it
  5. finite-word sub-extractor (shared with step 2): the same rules one
     level down on S(L)₊'s finite part — the LTLf story of [SωS26, §6]
  output: class-indexed formula DAG; render flat or definitional (§6)
```

## 6. The deliverable: DAG, flat, and definitional forms

Extraction as computed is a **class-indexed DAG**: one node per
(class, engine-context) pair, children memoized — the implementation
computes it at scale ⟨TBD: cite the implementation's numbers once §8
exists⟩. Three renderings:

1. **The DAG itself** — the working format; size ⟨TBD: bound —
   polynomial in `|𝒞|` for the anchored+ladder fragment?⟩. Not an LTL
   formula, but every downstream *computation* (model checking the formula
   against the automaton, equivalence tests) can consume it directly.
2. **Flat LTL** — the standard, and the intrinsically large one: no sharing
   in the syntax, so DAG unfolding multiplies along the R-order antichains.
   The honest statements: nesting depth ≤ R-depth when all layers anchor
   (each layer contributes bricks of fixed modal depth; only the exit
   recursion nests), and the until-rank read-off *lower-bounds* the depth
   any extraction can achieve — so on census specimens we certify "the flat
   explosion is the language's, not ours". ⟨TBD: both bounds, stated and
   proved; the size ledger DG vs. ours on the triptych + census.⟩
3. **LTL with definitions** — one fresh proposition `p_n` per DAG node `n`,
   a conjunction of `G(p_n ↔ brick_n(…))` definitions plus a root: linear
   in the DAG, printable, and defining `L` up to projection of the fresh
   atoms. The standard succinctness trick, offered as a first-class export
   format with its semantics stated precisely ⟨TBD: the projection
   statement; relation to QPTL/second-order quantification — note [KA26,
   §12] correctly refuses this move *inside* the transcription (a fresh
   disambiguating proposition would leave LTL); as an *output wrapper* it
   is legitimate and the distinction deserves a remark⟩.

## 7. The inner frontier

Aperiodicity is the outer cut. Inside it, the extraction's case analysis
induces a second, finer map, and every coordinate is a read-off:

| stratum | algebraic condition | formula shape | where decided |
|---|---|---|---|
| ladder-low (safety/co-safety/obligation) | closure of `P` | fixed template over a finite-word formula | step 2 |
| anchored, k = 1 | identity-or-reset per layer | flat bricks, depth O(R-depth) | step 3 |
| anchored, k ≤ K | local k-definiteness mod stutter | graded windows, same depth | step 3 |
| frozen, testable | ⟨TBD: local testability at infinity⟩ | `GF`/`FG` windows | step 4 |
| residual | none of the above | genuine nesting; until-rank certifies | steps 3–4 fallback |

**Table 3.** The inner frontier: which fragment of LTL a language actually
needs, decided on `𝓘(L)` before any formula is built. ⟨TBD: align the
strata with the known sub-LTL hierarchies — definite / locally testable /
TL[F] of Cohen–Perrin–Pin / until hierarchy [Wil99, PW13] — so each row is
a known variety with our operational reading; the census then *maps* the
strata empirically: at 2 states / 1 AP everything is expected in the first
three rows; find the smallest specimen in each lower row.⟩

The inner frontier is also the size story of §6 made structural: flat cost
concentrates exactly in the residual stratum, and the strata above it are
the reason extraction on real specimens is small — which DG, treating every
language as residual, cannot see.

## 8. Evaluation

⟨TBD: entire section — after implementation. Fixed decisions, so the
section can be written into: corpus = the census of small automata (ground
truth 𝓘 and LTL status already computed) plus the triptych and the paper's
worked specimens; comparisons = (i) flat size and depth: this extraction
vs. naive DG vs. the aut2ltl portfolio run on Cay(L) as an ordinary
automaton — the last being the apples-to-apples baseline the canonical
machine enables; (ii) DAG size vs. |𝒞| — the scaling claim; (iii) per-layer
anchoring statistics — which k fires, how often frozen layers appear, the
inner-frontier map; (iv) the until-rank vs. emitted depth ledger —
optimality gaps; (v) Conjecture 5.7 tested: automaton-form anchoring vs.
class anchoring, disagreements tabulated by direction. Verdicts checked by
the construction of [SωS26]: every emitted formula's 𝓘 must be byte-equal
to the input's — the equivalence oracle is the object itself.⟩

## 9. Related work

⟨TBD: full pass. The skeleton of the section:⟩

**Algebra to formula.** [DG08, §8] is the reference construction (§3); its
local divisor descends from Meyberg's local algebras, and the finite-word
analogues (Kufleitner et al.'s local-divisor proofs) choose separators no
less blindly. Wilke's and Diekert–Kufleitner's fragment characterizations
[Wil99, DK09] decide *membership* of sub-LTL fragments on the algebra; we
use them as extraction strata and depth certificates rather than as
verdicts. Preugschat–Wilke [PW13] decide the simple fragments via
Carton–Michel automata — the nearest decision-side relative of our frozen-
layer templates.

**Cascades.** Krohn–Rhodes for aperiodic monoids = wreath products of
resets; Maler's work on cascaded decomposition and the aut2ltl bls engine
translate automaton cascades to LTL. Our 1-anchored layer *is* the reset
brick surfacing on the canonical machine; the R-order walk is a cascade
whose levels the algebra names. ⟨TBD: precise comparison — what the Cayley
transcription emits vs. what a KR cascade of Cay(L) would; the claim that
R-depth ≤ cascade height obtainable blindly.⟩

**Local languages and definiteness.** The anchoring ladder relaxes local /
k-definite / k-testable recognizability modulo stuttering — the lineage
[KA26, §12] identifies (Chomsky–Schützenberger locals; Perles–Rabin–Shamir
definiteness; Brzozowski–Simon local testability); the algebraic
counterparts (varieties `D`, `LI`, locally testable) are classical, and our
per-layer equations are their localizations to R-classes. ⟨TBD: nail the
exact variety statements.⟩

**Internal.** Two productions of the aut2ltl portfolio supplied the
transcription vocabulary and its exactness discipline, and they bracket the
two engines: k-anchor [KA26] — state-based, window-graded — is the walk
engine's ancestor, its anchoring freed here of the automaton into an
equational property of the syntactic algebra; daisy [DA26] —
transition-based, petal/stem closed form, nondeterminism absorbed by
disjunction — is the frozen-layer engine's, its per-petal acceptance the
letter-visible shadow of `P`'s pair acceptance. Both are shape-dependent by
their own admission (a form can pass where another fails [KA26, §12]; the
daisy test is a property of one TGBA's initial state); the algebra is where
their preconditions become properties of the language. Daisy's restricted-
guard witness lift (left-quotient soundness for non-LTL residues) is the
automaton-level cousin of §4's certificates, which, born canonical, need no
lifting. This paper is the third member of a family in which the same
two-shape structure was constructed [SωS26] and learned [SωSL26].

## 10. Conclusion

⟨TBD — the arc, once the theory sections close: The syntactic ω-semigroup
was built to decide one question; on either side of that decision it now
rebuilds the object the answer calls for — a portable refutation, or a
defining formula that is a transcription of the algebra's own shape:
letters quotiented by λ, templates chosen by P's ladder, layers walked down
the R-order, flat bricks where the layers anchor, ω-templates where the
walk freezes — Arnold's two shapes, met for the third time, now as the two
engines of extraction — and nesting only where the until-rank proves it
unavoidable. The formula was always going to be large sometimes; the
algebra says exactly when, and exactly why.⟩

---

## References

- **[DA26]** aut2ltl, *The daisy algorithm* (construction note,
  `aut2ltl/daisy/algorithm.md`), 2026.
- **[DG08]** V. Diekert, P. Gastin. *First-order definable languages.* In
  *Logic and Automata*, 2008.
- **[DK09]** V. Diekert, M. Kufleitner. *Fragments of first-order logic
  over infinite words.* STACS 2009.
- **[KA26]** aut2ltl, *The k-anchor algorithm* (construction note,
  `aut2ltl/kanchor/algorithm.md`), 2026.
- **[Kam68]** H. Kamp. *Tense Logic and the Theory of Linear Order.* PhD
  thesis, UCLA, 1968.
- **[KR65]** K. Krohn, J. Rhodes. *Algebraic theory of machines I.* Trans.
  AMS 116 (1965).
- **[Mal10]** O. Maler. *On the Krohn–Rhodes cascaded decomposition
  theorem.* In *Time for Verification* (Pnueli memorial), LNCS 6200, 2010.
- **[MP92]** Z. Manna, A. Pnueli. *The Temporal Logic of Reactive and
  Concurrent Systems: Specification.* Springer, 1992.
- **[Per84]** D. Perrin. *Recent results on automata and infinite words.*
  MFCS 1984.
- **[PP04]** D. Perrin, J.-É. Pin. *Infinite Words: Automata, Semigroups,
  Logic and Games.* Elsevier, 2004.
- **[PW13]** S. Preugschat, T. Wilke. *Effective characterizations of
  simple fragments of temporal logic using Carton–Michel automata.* LMCS
  9(2:08), 2013.
- **[SωS26]** Y. Thierry-Mieg, with Claude (Anthropic). *Constructing the
  syntactic ω-semigroup from a deterministic Emerson–Lei automaton.*
  Working draft, 2026.
- **[SωSL26]** Y. Thierry-Mieg, with Claude (Anthropic). *Learning the
  syntactic ω-semigroup.* Working draft, 2026.
- **[Tho79]** W. Thomas. *Star-free regular sets of ω-sequences.*
  Information and Control 42 (1979).
- **[Wil99]** T. Wilke. *Classifying discrete temporal properties.* STACS
  1999.
- ⟨TBD: Cohen–Perrin–Pin (TL[F]); Brzozowski–Simon (locally testable);
  Perles–Rabin–Shamir (definite); De Giacomo–Vardi (LTLf template);
  Landweber; Schützenberger; the certificate-note references.⟩
