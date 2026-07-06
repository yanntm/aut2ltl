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
of `L` and failing on another. The walk carries exactly the *stem*
coordinate of the accepting pair, and provably not the *loop* coordinate —
no acceptance condition on recurring states or edges makes the class machine
a recognizer of `L`, the running example refuting both — so a second engine
transcribes the loop side from the recurring windows of the tail, with
`GF`/`FG` templates read off `P`: the stem and loop engines are Arnold's two
context shapes, met a third time. Nesting appears only
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
2. A presentation-independent transcription engine targeting the accepting
   pair `(s, e)`: the walk on the right Cayley graph of `S(L)₊¹` (layers =
   R-classes) transcribes the stem coordinate under an anchoring condition
   (A), and — the walk provably cannot carry the loop coordinate (Lemma
   5.2) — a window engine transcribes `e` under a determinacy condition
   (B); both conditions are equations on the object, and together they
   yield exactness by construction (§5).
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

**Lemma 5.2 (what the walk carries — and what it cannot).** (i) The walk
computes the full syntactic class of every prefix, `ψ(u) = [u]`; in
particular, for any Ramsey factorization `α = u·w₁w₂⋯` the *stem
coordinate* `s = [u·w₁⋯w_k]` of the accepting pair is a walk value. (ii)
The *loop coordinate* `e` is **not** a function of the walk, nor of any
inf-set acceptance on `Cay(L)`: no Muller condition on recurring states and
no Emerson–Lei condition on recurring edges makes `Cay(L)` a recognizer of
`L` in general.

*Proof.* (i) is the definition of `Cay(L)`. (ii) is refuted on `GF(aa)`
itself, at both levels, off the table of [SωS26, Table 3(a)]
(classes `0..5 = [ε], [!a], [a], [!a·a], [a·!a], [a·a]`; `P = {(5,5)}`).
*States:* `aa·(!a)^ω` and `aa·a^ω` have the identical prefix-class walk
`2, 5, 5, 5, …` (class `5` is absorbing), hence the same recurring-state
set `{5}`; their accepting pairs are `(5, [!a])` and `(5, [a·a])` — one
rejected, one accepted. *Edges:* the tails `(a·!a)^ω` and `(aa·!a)^ω`,
both read from class `5`, traverse the same recurring-edge set
`{(5, a), (5, !a)}`; their loop idempotents are `[a·!a]` and `[a·a]` —
verdicts again opposite. ∎

Lemma 5.2(ii) deserves a pause, because a first draft of this section
asserted the opposite ("the walk decides membership") and the running
example itself refutes it. It is [SωS26, Prop 3.4] reborn: the frozen class
`5` *is* that proposition's one-state automaton with trivial action, where
no amount of state bookkeeping recovers acceptance. There the repair was
enrichment — marks along runs. `Cay(L)` has no marks to enrich with; the
only letter-visible substitute is the **recurring window structure** of the
tail (which finite factors recur), and recovering `e` from it is possible
exactly on a stratum (Definition 5.6). The consequence is architectural,
and it sharpens rather than weakens the two-engine picture: **the
transcription target is the accepting pair `(s, e)` — the walk engine
transcribes `s`, and a window engine must transcribe `e`.** Acceptance is
*never* the walk's business, in any layer, frozen or moving.

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
| `GF(enter-window)` fairness | window recovery of the loop coordinate `e` — condition (B), Definition 5.6 |
| state-based colors `F_i` | **no counterpart** (Lemma 5.2(ii)) — acceptance lives on pairs, not classes |
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

Anchoring is the *stem-side* precondition: it makes the walk transcribable.
Lemma 5.2(ii) forces a second, independent precondition on the *loop side*:

**Definition 5.6 (window-determined acceptance).** A layer `R` is
**(B)-determined at width `k`** if for every stem class `s ∈ R` and any two
ω-tails confined to `R` from `s` whose sets of recurring length-`k` factors
are equal, the accepting pairs `(s, e)` and `(s, e')` they induce have equal
`P`-verdicts. (Equivalently: on tails confined to `R`, the loop coordinate's
verdict is a function of the recurring `k`-window set.)

Call anchoring **condition (A)** and window-determinacy **condition (B)**.
The two automaton-level productions of the portfolio split precisely along
this line, which neither could state: kanchor obtains (B) *for free* by
restricting itself to state-based acceptance — colors sit on states, states
are phases, so (A) implies acceptance is window-visible; its own document
records the price ("transition-level marks on self-loops leave no
letter-visible trace" [KA26, §1]). Daisy, conversely, is (B) at width 1 —
per-petal transition marks — for a component where (A) is trivial (one
state). On the algebra the two conditions come apart cleanly, both as
properties of `(𝒞, λ, M, P)`, and the exactness theorem needs both:
condition (A) on every layer the walk traverses, condition (B) on every
layer a run can remain in forever.

**The bricks, transported.** For a 1-anchored layer `R` with anchor targets
`t(a)` per reset letter and stutter sets `N(c)` per class ⟨TBD: full label,
following [KA26, §4.3] with: `sojourn(c) = N(c) W (moves out of c)`, the
anchored law `G(a → X sojourn(t(a)))` per reset letter, parks as linked-pair
lookups in `P`, exits to memoized class children; then the graded version
following [KA26, §6–7]⟩. One brick does *not* transport unchanged: kanchor's
fairness `GF(⋁ anchors into F_i)` presumes state-carried colors, which
Lemma 5.2(ii) rules out here. Its replacement is the window fairness of
Definition 5.6: under condition (B) at width `k'`, the `STAY∞` acceptance of
a final layer is a Boolean combination of `GF(window)` terms over the
length-`k'` windows, selected by which recurring-window sets induce
accepting pairs ⟨TBD: the exact selection — per recurring-set stratum, a
conjunction `⋀ GF(wᵢ) ∧ ⋀ FG(¬wⱼ)` normal form; sizes⟩. Exactness then
transports leg by leg: the walk is deterministic on `Cay(L)` *by
construction*, so the uniqueness leg of [KA26, §10] is immediate; the
completeness/soundness legs are unchanged for the law and leave bricks
(the licence for eager triggers [KA26, §5.4] carries verbatim), and the
fairness leg is exactly condition (B) ⟨TBD: the two-condition exactness
theorem, stated and proved: (A) on traversed layers + (B) on final layers
⟹ the flat label defines `L`⟩.

### 5.3 Anchoring is a property of the language

The automaton-level production is honest about its form-dependence: its
preconditions are tested on one presentation, "an input can pass in one
automaton form and fail in another" [KA26, §12]. On `Cay(L)` the tests are
evaluated on the canonical object, so *our* pass/fail is a function of `L` —
by fiat. The substantive claims are the two comparisons:

**Claim 5.7 (soundness of the finer phase).** Conditions (A) and (B) are
evaluated on the canonical object, so their verdicts are functions of `L`;
when they hold, the transcription is exact for `L` with no reference to any
presentation (the two-condition exactness theorem of §5.2). The claim is
that nothing more is ever needed: the syntactic class is the finest phase,
and `P` the complete acceptance datum.

**Conjecture 5.8 (the automaton tests approximate a language property).**
If *some* deterministic presentation of `L` passes the automaton-level
preconditions at width `k` on a component, then the corresponding layers of
`Cay(L)` pass (A) at width `⟨TBD: k? f(k)?⟩` and, for state-based input,
(B) at a related width. ⟨TBD: this is the delicate direction, and the
comparison must *unbundle* the two conditions, because the automaton
productions bundle them differently — kanchor folds (B) into its state-based
acceptance restriction, daisy isolates (B) at width 1. Note also that class
phases and state phases are incomparable in general: two words reaching the
same state share a residual but not necessarily a class, and conversely
states may duplicate residuals — so neither direction of the conjecture is
trivial. §5.4's specimen shows the algebra can be strictly *easier* (width
1 against 2); whether the reverse occurs is a census question. Settle
empirically: run both, tabulate agreements and the direction of every
disagreement.⟩

If Conjecture 5.8 holds in a usable form, the paper's statement is clean:
the automaton production was computing an approximation, on one
presentation, of an equational property of the syntactic algebra — and the
algebra computes the property itself. If it fails, the failure is itself a
finding (a genuinely presentation-bound transcription), and Claim 5.7 stands
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
Relates to Conjecture 5.8.⟩

**The walk, alone, is not the language — and the example proves it twice.**
The walk reaching layer `{5}` says "an `aa` has occurred", and `GF(aa)` is
not "eventually `aa`": Lemma 5.2(ii)'s two refutation instances live in this
very layer. Acceptance turns on what recurs after the walk freezes — the
single accepting pair `([a·a], [a·a])` demands a tail whose recurring loop
idempotent is `[a·a]` — and condition (B) holds here at width 2: among
tails confined to `{5}`, the recurring 2-window set determines the verdict
(the window `aa` recurs iff the loop idempotent is `[a·a]` ⟨TBD: two-line
check⟩), yielding the frozen-layer brick `GF(a ∧ Xa)`. The moving layers,
by contrast, are *rejecting* as final layers — no pair off class `5` is in
`P` — so their `STAY∞` branches are `false` by the same degeneracy that
[KA26, §8] gets for free, and only their `LEAVE` chains survive.
*Predicted output*, then, for the whole extraction of `GF(aa)`: `LEAVE`
chains through `{1,3}` / `{2,4}` into the memoized child at `5`, whose
label is `GF(a ∧ Xa)` — an `F(…)`-shaped reach wrapper around the child —
and since the reach wrapper is implied by the child (recurrence implies
occurrence), the simplified form is `GF(a ∧ Xa)` exactly. A
prefix-independence read-off (one residual ⟹ the reach wrapper is always
redundant ⟨TBD: prove as a simplification rule⟩) would emit it directly.
The experiment suite checks this prediction end to end (E0 in the companion
spec).

### 5.5 The window engine is Arnold's second shape

Lemma 5.2(ii) assigns every acceptance decision to a second engine; the
*frozen* layer — all letters neutral, the walk stabilized — is only that
engine's purest case, where nothing else remains. This is not a corner
case; it is a theorem-shaped fact:

**Proposition 5.9 (the division of labor).** The transcription target is
the accepting pair `(s, e)`. The walk engine computes exactly the stem
coordinate `s` (Lemma 5.2(i)); every acceptance decision — the `STAY∞`
fairness of a final layer, every park verdict, every frozen tail — is a
property of the loop coordinate `e`, which no function of the walk
determines (Lemma 5.2(ii)) and which the word exposes only through its
recurring window structure, recoverable under condition (B). ⟨TBD: precise
statement and proof.⟩

*Remark (the Arnold echo).* This is not literally the `~lin`/`~ω` split of
[SωS26, §4] — `~lin` compares residuals, and the walk computes classes,
which are finer — but it is its exact operational echo: Arnold's linear
shape constrains what stems can do, his ω-power shape what loops can do,
and the extraction splits its labor the same way, stems to the walk, loops
to the windows. The construction computed the two shapes as two relations
[SωS26], the learner harvested them as two column sorts [SωSL26], and here
they are two engines. For a prefix-independent `L` (one residual, [SωS26,
Prop 4.6]) the stem side carries no membership information at all — the
walk still runs (classes move even when residuals do not: `GF(aa)` has one
residual and four layers), but every `STAY∞` and every reach wrapper it
emits is either `false` or redundant, and the language lives entirely in
the window engine.

**The no-recursion trap.** The frozen tail language at a frozen class `c` is
`T_c = {α : (c, e(α)) ∈ P}` — prefix-independent by construction ⟨TBD:
well-definedness lemma: all Ramsey idempotents of the same tail give one
verdict against a fixed `c`⟩. It is tempting to "recurse" on `T_c` — build
its invariant, extract, wrap. The temptation must be resisted, and `GF(aa)`
shows why: there `T_5 = GF(aa) = L` itself. Prefix-independent languages
are fixed points of the walk-then-tail decomposition; the frozen engine is
not a recursive call, it is the *other base case*, and it needs its own
method:

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

- **(B) holds at width `k`** — the verdict is a function of the recurring
  `k`-window set, and the label is a Boolean combination of `GF(window)`
  terms (equivalently `FG(¬window)` for the forbidden ones), shaped by the
  ladder rung of `P` restricted to `c × idempotents`: recurrence rungs give
  positive `GF` shapes (`GF(aa)`: accept iff the window `aa` recurs —
  `GF(a ∧ Xa)`), persistence rungs the dual `FG`, reactivity the general
  Boolean combination. ⟨TBD: the general window read-off — from the
  accepting idempotents at `c`, derive the window set and the normal form;
  bound the needed width by ⟨the layer's local definiteness degree?⟩; align
  the (B)-stratum with the locally-(threshold-)testable ω-varieties
  (Beauquier–Pin / Wilke, cite-TBD) so the stratum is a known class with
  our operational reading.⟩
- **(B) fails at every affordable width** — the genuine nesting case: the
  recurring windows do not determine the verdict, because acceptance hangs
  on *order* among recurring factors, the classical separator between
  `FO[<]` and locally testable (`FO[+1]`, Thérien–Weiss; cite-TBD). Here
  and only here does a DG-style descent survive, demoted to "the engine
  inside one frozen layer" and scoped to that layer's tail algebra ⟨TBD:
  which is not smaller in general — `T_c = L` above — so the honest
  statement is: this stratum is where extraction still pays DG's price,
  and the census measures how rare it is; an ω-specific descent that beats
  DG on this stratum is the paper's main open problem⟩.

The architecture, assembled — the paper's picture:

```
extract(𝓘):
  0. aperiodicity scan — group ⟹ certificate (§4), stop
  1. quotient the alphabet by λ; choose L or L̄ by P-shape (cheaper side)
  2. ladder read-off: safety/co-safety/obligation ⟹ finite-word extraction
     of the class-defined prefix language + fixed template, stop
  2.5 combinators (§5.6): OR-split P by final layer; AND-split by subdirect
      factorization; re-canonicalize each piece (a divisor — never leaves
      LTL, Prop 5.10), recurse on pieces whose read-offs improved, combine
      with ∨ / ∧
  3. walk engine (stem side): descend the R-order of Cay(L); per layer:
       (A) at k ≤ cap  ⟹ flat law/leave bricks, exits to memoized class
                          children
       (A) fails       ⟹ ⟨TBD: layer-internal decomposition; DG local
                          division as last resort, scoped to the layer⟩
  4. window engine (loop side), on every layer a run can end in:
       (B) at k' ≤ cap ⟹ GF/FG window combination read off P (STAY∞,
                          parks) — includes every frozen layer
       (B) fails       ⟹ DG on the tail algebra: the residual stratum,
                          measured, not hidden
  5. finite-word sub-extractor (shared with step 2): the same rules one
     level down on S(L)₊'s finite part — the LTLf story of [SωS26, §6]
  output: class-indexed formula DAG; render flat or definitional (§6)
```

*Step 2, validated.* For co-safety `L` the good-prefix set
`W = {u : u·Σ^ω ⊆ L}` is a union of `≈_L`-classes — whether *every*
continuation of `u` is accepted is a property of `[u]` alone, since each
continuation's pair is `([u]·s', e')` — so `W` is recognized by the finite
part of the algebra, the finite-word extractor (step 5) applies to it, and
the wrapper is the standard strong/weak insertion of a finite-word formula
into LTL over ω-words ("some prefix satisfies `φ_W`": strong next in
positive positions, weak under negation ⟨TBD: cite the LTLf/RV lineage,
De Giacomo–Vardi and the weak-next tradition⟩). Safety is the dual through
`P ↦ P^c`; obligation, Boolean combinations of the two.

### 5.6 Combinators: the portfolio's decompositions, on the invariant

The automaton portfolio's workhorses, beyond its per-component productions,
are three *decomposition combinators*: split by accepting SCC (mark one SCC
solo-accepting, drop the rest, translate, OR the results), split by
strength (Spot's terminal/weak/strong decomposition, OR), and split by
acceptance (translate each conjunct of the Emerson–Lei condition, AND —
"good for `GFa ∧ FGb`, necessary almost", at the price of determinization).
All three transport to the invariant, and each lands on a named algebraic
operation that is cleaner than its automaton original. The common
foundation is Theorem 5.1 of [SωS26] read as a *calculus*: on a fixed table
`(𝒞, λ, M)`, **every pair set is a language**, so union, intersection and
complement of same-table languages are Boolean operations on `P` — and any
restriction can then be *re-canonicalized* by re-running the construction's
quotient with the new pair set, yielding the piece's own, smaller algebra.

**(1) The accepting-SCC OR is restriction of `P` to a final layer.** Every
word's stem class `s` lies in exactly one final layer, so

```
    L  =  ⊎_{R final layer}  L_R,      L_R recognized by (𝒞, λ, M, P|_R),
    P|_R = { (s, e) ∈ P : s ∈ R }
```

— a *disjoint* union, exact by construction, with none of the automaton
version's surgery (no re-marking, no dropped-part reachability caveats).
Two properties the automaton combinator cannot state:

**Proposition 5.10 (decomposition never leaves LTL).** Any language
recognized by `(𝒞, λ, M)` with *any* pair set — every `L_R`, every
single-pair piece, every Boolean combination — has a syntactic ω-semigroup
dividing `M`. In particular if `L` is LTL, so is every piece, and every
re-canonicalized piece algebra is no larger than `𝓘(L)`'s.

*Proof.* The syntactic morphism of `L` recognizes the piece (membership
depends only on the pair), and the syntactic algebra of any language
divides each of its recognizers. Divisors of aperiodic monoids are
aperiodic. ∎

*The guard.* Pieces can climb the *Wagner* ladder even while staying LTL
(a single-pair piece asserts "the pair is exactly `(s, e)`", which can sit
strictly higher than `L` itself — the pair split is the finest granularity
and should be reserved for the window engine's interior). The combinator
therefore splits by final layer first, and — the operational gain over the
portfolio — *checks the read-offs of each re-canonicalized piece before
extracting anything*: `|𝒞'|`, ladder rung, (A)/(B) widths. Try-and-see
becomes read-and-decide.

**(2) The strength OR is the (B)-stratification, per layer.** Spot's
terminal/weak/strong split transports to a classification of final layers
that the engine of §5.2–5.5 already dispatches on: *terminal* = commitment
(the stem class `s` satisfies `(s·x, f) ∈ P` for every linked
continuation — step 2's co-safety template, localized); *weak* = condition
(B) holds at width 0 (all idempotent verdicts at the layer agree —
acceptance is "stay here", no window needed); *strong* = the genuine
window engine. On the algebra this is not a decomposition producing
automaton copies; it is a per-layer read-off selecting the template — the
strength combinator was the automaton shadow of the engine's own case
analysis.

**(3) The acceptance AND is subdirect decomposition.** The automaton
combinator splits `Acc = Acc₁ ∧ Acc₂` and intersects the two languages —
sound only on a deterministic form, hence "requiring determinization". On
the algebra, determinization is free (the object *is* its canonical
deterministic form), and the operation has its classical name. An
**ω-congruence** `θ` on the invariant is a monoid congruence on `(𝒞, M)`
⟨TBD: plus the pair-saturation condition making `P` θ-definable⟩; a
factorization

```
    P = P₁ ∩ P₂,   Pᵢ saturated by θᵢ,   θ₁ ∩ θ₂ = Δ
```

gives `L = L(P₁) ∩ L(P₂)` with each factor recognized by the *proper
quotient* `M/θᵢ` — a subdirect representation in Birkhoff's sense, each
factor strictly smaller, each factor's own invariant obtained by
re-canonicalization. `GFa ∧ FGb` is the type specimen: its table factors
onto a `GFa`-quotient (forget `b`) and an `FGb`-quotient (forget `a`), and
the extraction of each factor is a one-layer window brick. ⟨TBD: (i) the
pair-saturation definition and the proof that the factorization is exactly
the AND-split; (ii) existence — Birkhoff guarantees subdirect
representations of the monoid, the `P`-compatible version needs its own
statement, with the honest fallback "no proper factorization exists" (the
subdirectly irreducible case); (iii) algorithmics — the congruence lattice
of a census-sized monoid is enumerable, and the search wants maximal
proper congruences first; (iv) the worked `GFa ∧ FGb` factorization,
tables shown.⟩

The combinators compose (OR of ANDs, complement flips via `P^c` choosing
the cheaper side), they all commute with re-canonicalization, and
Proposition 5.10 makes the whole combinator layer safe: no move ever
leaves LTL or grows the algebra. They slot into the architecture as step
2.5, between the ladder templates and the walk engine.

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
| stem-transcribable, k = 1 | (A): identity-or-reset per layer | flat bricks, depth O(R-depth) | step 3 |
| stem-transcribable, k ≤ K | (A): local k-definiteness mod stutter | graded windows, same depth | step 3 |
| loop-transcribable | (B) at width k′ ⟨TBD: align with local ω-testability⟩ | `GF`/`FG` window combinations | step 4 |
| residual | (A) or (B) fails at every affordable width | genuine nesting; until-rank certifies | steps 3–4 fallback |

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
optimality gaps; (v) Conjecture 5.8 tested: automaton-form anchoring vs.
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
lifting. The portfolio's decomposition combinators (accepting-SCC,
strength, and acceptance splits — `aut2ltl/decomp`) are the automaton
shadows of §5.6's `P`-restriction, (B)-stratification, and subdirect
factorization respectively. This paper is the third member of a family in
which the same two-shape structure was constructed [SωS26] and learned
[SωSL26].

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
