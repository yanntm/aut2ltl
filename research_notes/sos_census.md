# A Census of Syntactic ω-Semigroups: Enumerating the Small ω-Regular Languages

**Yann Thierry-Mieg**

With significant inputs from
**Claude (Anthropic)**

*Skeleton draft — 2026-07-07 — placeholders marked `⟨TBD: …⟩`*

## Abstract

Exhaustive censuses of small ω-automata enumerate *machines*: many
presentations per language, and every frontier they map is polluted by
presentation artifacts — the spurious groups, the lucky forms. The
syntactic ω-semigroup is complete and canonical [SωS26, Thm 5.1], so a
census of invariants `𝓘 = (𝒞, λ, M, P)` by size `|𝒞|` enumerates
*languages*: one item each, byte-distinct iff distinct. We define the
census in two constructions that validate each other — *derived* (push an
automata census through the construction, deduplicate by byte equality;
the deduplication ratio is itself a measurement of presentation
redundancy) and *intrinsic* (enumerate reduced admissible invariants
directly, with the construction's own quotient as the reducedness
filter) — and we ventilate it by the classifications that are read-offs
of the object [SωS26, §7]: the safety–progress rung, the acceptance
index, the Wagner degree, aperiodicity, and the extraction strata of
[SωSX26]. The yield is a genre of statement no automata census can make:
*presentation-free threshold theorems* ("no non-LTL language exists below
canonical size 5 over one letter pair"), *density laws* (the partition
function of ω-regular languages by canonical size, per class — each
ventilation an integer sequence that has never been computed, because the
object was never built), the *cost of canonicity* (canonical size against
best presentation size, joined through the derived census), and a *basis*
(the languages irreducible under the calculus of [SωSC26], from which the
rest of the small world is assembled). The census is also the family's
proving ground: every construction run, every learner run, every
extraction conformance check lands, or fails to land, on a census row.
⟨TBD: headline numbers once the intrinsic census runs.⟩

---

## 1. Introduction

⟨TBD: full pass. The arc: censuses of small structures are a standard
instrument (small groups, small semigroups, small automata) and their
value is always the same — thresholds, densities, counterexample hunts,
test oracles. For ω-regular languages the instrument never existed,
because the canonical object per *language* was never computable; census
work therefore counted machines and could not separate the language
content from the presentation noise. [SωS26] changes the ground: the
invariant is constructible, canonical, and byte-comparable. Contributions:
(1) the two census constructions and their cross-validation (§3); (2) the
admissibility + reducedness characterization of "an invariant of size N"
(§3.2–3.3); (3) the ventilated measurements and the theorems they license
(§4); (4) ⟨TBD: the computed census itself, with tables⟩.⟩

## 2. Background

⟨TBD: compressed recall of [SωS26]: the invariant, linked pairs, the
membership rule `Val(c,d) = [(c·d^π, d^π) ∈ P]`, byte-equality
completeness, shortlex keying; the two-shape congruence used below as the
reducedness test. Alphabet convention: the census is primary over an
*abstract* quotient alphabet of `m` letters (λ injective); the AP
ventilation is derived — a language needs `k` atomic propositions iff its
letter quotient has `m ≤ 2^k` classes, and every abstract `m`-letter item
is realizable over `⌈log₂ m⌉` APs.⟩

## 3. The two censuses

### 3.1 The derived census

Push every automaton of an exhaustive machine census (e.g. all complete
deterministic 2-state, 1-AP, 1-acceptance-set automata, the `genaut`
corpus) through the construction of [SωS26]; canonically key; deduplicate
by byte equality. The result is *the language content of that machine
class*, and two measurements come with it:

- **The deduplication ratio** — machines per language, the exact measure
  of presentation redundancy the machine census carries. ⟨TBD: number.⟩
- **The reach map** — which canonical sizes `|𝒞|` occur for languages
  presentable with `n` states: the first empirical view of the
  size relation between presentations and the canonical object, in both
  directions (small machines with large algebras; large machines wasted
  on small languages).

The derived census is cheap, bounded by the machine corpus, and — its
main defect — *not intrinsically complete*: it enumerates the languages
presentable at machine size `n`, not the languages of canonical size `N`.
A language of canonical size 6 whose smallest deterministic presentation
has 4 states is invisible to a 2-state machine census. Completeness in
the language metric needs the second construction.

### 3.2 The intrinsic census: what "an invariant of size N" is

An item of the intrinsic census at parameters `(N, m)` is a tuple
`𝓘 = (𝒞, λ, M, P)` with `|𝒞| = N`, `|Σ_λ| = m`, satisfying:

1. **Table axioms.** `M` associative on `𝒞` with identity `[ε]`; the
   identity *fresh*: `M(c, c′) ≠ [ε]` for `c, c′ ≠ [ε]` (products of
   nonempty words are nonempty — the [SωS26, §2] convention); the
   non-identity part *generated* by the letter classes
   `λ(a₁), …, λ(a_m)` (every class is a product of letters: reachability
   of every `c ≠ [ε]` in the right Cayley graph).
2. **Admissible pair set.** `P` is a set of linked pairs
   (`e² = e`, `s·e = s`, both non-identity) closed under **conjugacy**:
   for `x, y ∈ 𝒞¹` with `e = x·y`, the pair `(s·x, y·x)` — when
   `(y·x)² = y·x` makes it linked — names the same lassos as `(s, e)`,
   and membership must not depend on the naming, so `P` is a union of
   conjugacy classes. ⟨TBD: verify the exact conjugacy statement and its
   sufficiency for a well-defined ω-language against [PP04] (library
   copy) — the claim to pin: the membership rule evaluates every
   representation `u·v^ω` of the same ω-word to one verdict iff `P` is
   conjugacy-saturated.⟩
3. **Reducedness.** The tuple is a fixpoint of the construction's own
   quotient: the two-shape syntactic congruence of the language `𝓘`
   defines — computable *purely on the table* by the class-quantified
   context scans of [SωSX26, §4.2] (linear contexts `(x, y, t)`,
   ω-power contexts `(x, y)`, verdicts through `Val`) — is the
   *equality* on `𝒞`. A non-reduced candidate recognizes a language
   whose true invariant is smaller: it is a duplicate of an earlier
   census row, and the filter discards it.
4. **Canonical form.** Classes keyed shortlex-least and serialized per
   the `.sos` format; two ventilation policies, both reported: *labeled*
   (letters are distinguishable — the census of specifications) and
   *up to letter renaming* (quotient by the `Sym(m)` action on
   generators — the census of abstract languages). ⟨TBD: decide which is
   primary; the renaming quotient also merges mirror-image languages,
   record the orbit sizes.⟩

Reducedness is the load-bearing clause: with it, the intrinsic census is
in **bijection with the ω-regular languages of syntactic size `N`** —
the census *is* the partition of the ω-regular world by the canonical
size measure. And the filter is not new machinery: it is [SωS26]'s
quotient, re-run on the candidate's own Cayley presentation — the tool
validating the census that validates the tool.

### 3.3 Enumeration, feasibility, cross-validation

⟨TBD: the algorithm section — the sketch to develop:⟩

- Enumerate monoid tables with fresh identity by standard
  isomorph-rejecting search (the semigroup-enumeration literature is the
  reference point ⟨TBD: library request — small-semigroup enumeration,
  Distler et al.?⟩), *pruned by generation*: the `m` letter classes are
  chosen first and the table must be generated by them — a strong
  constraint that cuts the classical explosion.
- Per table: enumerate linked pairs, compute conjugacy classes once,
  enumerate `P` over unions of conjugacy classes (`2^{#classes}`,
  small in practice at census sizes ⟨TBD: measure⟩).
- Per candidate: reducedness scan (polynomial, §3.2.3); canonical keying;
  emit.
- **Cross-validation, both directions.** Every derived-census item must
  appear in the intrinsic census at its size (else the enumerator is
  incomplete); every intrinsic item of size reachable by the machine
  corpus must be hit by some machine (else the construction is buggy) —
  the two censuses are each other's test suite, and both are oracles for
  the learner [SωSL26] (learn every census item from its own membership
  oracle; the hypothesis must converge to the byte-identical row).
- Feasibility wall: the semigroup explosion bounds `N` to single digits
  and `m` to 2–3 — exactly the regime where the frontier questions of
  §4 live. ⟨TBD: measured counts per (N, m).⟩

## 4. What the census measures

Every column below is a read-off of the object [SωS26, §7], so the
ventilation costs one scan per row.

### 4.1 Threshold theorems, presentation-free

For each property `X` (non-aperiodicity; each safety–progress rung; each
acceptance index; each Wagner degree; each inner-frontier stratum of
[SωSX26, §7] — (A)-failure at every width, (B)-failure, until-rank `r`):
the least `N` at which `X` occurs over `m` letters, with the witness row
as *the* canonical minimal specimen. These are statements about the
language class — "below canonical size `N₀`, every ω-regular language
over `m` letters is LTL" — that a machine census can only approximate
("presentable with `n` states"), because machine size does not measure
the language. The known small examples calibrate: `GF(aa)` sits at
`N = 6`, `Even` at `5`, `EvenBlocks` at `8` [SωS26, Table 1] ⟨TBD:
confirm these are minimal at their properties, or exhibit smaller census
rows — either answer is a finding⟩.

### 4.2 Density: the partition function of ω-regular languages

`#{L : |𝒞(L)| = N}`, ventilated by class — the aperiodic fraction, the
rung distribution, the Wagner spectrum, the strata of the extraction. Each
ventilation is an integer sequence indexed by `N` (per `m`), none of which
has ever been computed ⟨TBD: compute; consider OEIS submission — the
unventilated sequence "number of ω-regular languages of syntactic size N"
is a natural invariant of the theory⟩. The shape questions: how fast does
the non-LTL fraction grow; is the residual stratum of [SωSX26] (genuine
nesting) measure-zero at small sizes, as predicted; do prefix-independent
languages dominate (every absorbing class forces one frozen layer)?

### 4.3 The cost of canonicity

Join the two censuses: per language, canonical size `|𝒞|` against the
smallest deterministic presentation in the machine corpus (and, where
computable, the smallest nondeterministic one). The distribution of the
ratio is the honest price tag of the calculus's "pay canonicity once"
economy [SωSC26, §3.4]: how often the canonical object is the *same*
size as a good presentation, how heavy the tail is, and whether the heavy
cases correlate with a class (the conjecture worth testing: the blowup
concentrates where the ω-rational constructors concentrate it —
concatenation-shaped languages). ⟨TBD: state the conjecture properly;
measure.⟩

### 4.4 Hunts

Standing open questions become census queries, each a scan:

- **H5 of [SωSX26]** — a non-LTL row all of whose ω-power patterns are
  constant (linear-only witness): existence settles the dual blindness
  question; exhaustion at census sizes is evidence toward "F₂ always
  available".
- **(A)/(B) frontier specimens** — the smallest anchoring failure, the
  smallest window-determinacy failure (the paper's "order beyond
  windows" figure), the smallest DG-fallback invocation.
- **Calculus irreducibles** — see §4.5.
- ⟨TBD: the standing-hunt list will grow; the census is the family's
  standard instrument for "does a small counterexample exist".⟩

### 4.5 The basis: irreducibles under the calculus

Call a census row **irreducible** if it is not produced from strictly
smaller rows by the operations of [SωSC26] — Boolean combinations on an
aligned table, rootings, inverse substitutions, and the subdirect
AND-split of [SωSX26, §5.6] (no proper `P`-compatible factorization). The
irreducible rows are the *basis of the small ω-regular world*: everything
else is assembled from them by the calculus, and the census-with-closure
— which sizes are generated, which are genuinely new — is the algebraic
version of the census. Measurements: the fraction of irreducible rows per
size (does it thin out — is the world mostly combinations?); whether
irreducibility correlates with subdirect irreducibility of `(𝒞, M)`
alone; the smallest language *not* reachable from strictly smaller ones
even with the exponential constructors admitted. ⟨TBD: the closure
computation is itself calculus-powered — generate, reduce, look up; a
nice fixpoint over the census as a database.⟩

### 4.6 The census as the family's proving ground

Every tool in the family is tested against the census as an oracle:
construction runs must land on rows (derived ⊆ intrinsic); learner runs
must converge to rows byte-exactly; extraction conformance re-derives
rows from emitted formulas; calculus operations must map rows to rows
(closure). A discrepancy anywhere is a stop-the-line bug with a minimal
specimen attached — the census turns "the tools agree with the theory"
from a hope into a regression suite.

## 5. The enumeration algorithm

⟨TBD: develop §3.3's sketch into pseudocode + isomorph-rejection details
+ the generation-pruned search; complexity accounting; the `.sos`
database format and its indices (by size, class, ventilation columns).⟩

## 6. Evaluation

⟨TBD: after implementation — the census tables per (N, m); the
ventilations; the threshold theorems extracted; the cross-validation
report; runtime and where the wall actually sits.⟩

## 7. Related work

⟨TBD: skeleton — small-structure enumeration lineage (small groups;
small semigroups/monoids — library requests: Distler et al.?; small
automata censuses and the `genaut` corpus); Wagner-hierarchy computations
[CP97, CP99, SW08]; the position claim: censuses of *machines* exist,
censuses of *languages* do not, because the canonical per-language object
was never buildable before [SωS26].⟩

## 8. Conclusion

⟨TBD: the arc — one canonical object per language makes "how many
ω-regular languages are there, of each kind, at each size" a computable
question for the first time; the answers are threshold theorems, density
laws, price tags, and a basis; and the census doubles as the family's
regression oracle. The calculus [SωSC26] operates on the universe; this
paper counts it.⟩

---

## References

- **[CP97]** O. Carton, D. Perrin. *Chains and superchains for
  ω-rational sets…* IJAC, 1997. ⟨TBD: verify entry against library copy.⟩
- **[CP99]** O. Carton, D. Perrin. IJAC, 1999. ⟨TBD: complete entry.⟩
- **[PP04]** D. Perrin, J.-É. Pin. *Infinite Words: Automata, Semigroups,
  Logic and Games.* Elsevier, 2004.
- **[SW08]** V. Selivanov, K. Wagner. Fund. Inform., 2008. ⟨TBD:
  complete entry.⟩
- **[SωS26]** Y. Thierry-Mieg, with Claude (Anthropic). *Constructing the
  syntactic ω-semigroup from a deterministic Emerson–Lei automaton.*
  Working draft, 2026.
- **[SωSL26]** Y. Thierry-Mieg, with Claude (Anthropic). *Learning the
  syntactic ω-semigroup.* Working draft, 2026.
- **[SωSX26]** Y. Thierry-Mieg, with Claude (Anthropic). *The LTL
  frontier from the syntactic ω-semigroup.* Working draft, 2026.
- **[SωSC26]** Y. Thierry-Mieg, with Claude (Anthropic). *A calculus on
  the syntactic ω-semigroup.* Working draft, 2026.
- ⟨TBD: small-semigroup enumeration (Distler et al.?) and the machine
  census lineage — library requests for the biblio sweep.⟩
