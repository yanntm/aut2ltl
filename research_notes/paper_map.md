# Paper map — what lives in `research_notes/`

One entry per paper. Two lines of scope, drawn from the paper's own abstract,
plus the files that belong to it.

**Naming convention.** A paper is `p.md`; its engineering/experiment
specification is `p_spec.md`; the engineering report answering that spec is
`p_report.md`; a figure commission, where one exists, is `p_figures.md`. A paper
with no experimental side has no spec and no report. Working notes that are not
papers live in `notes/`, not here.

---

## The core

### `sos_constructed` — Constructing the Syntactic ω-Semigroup from a Deterministic Emerson–Lei Automaton

The canonical algebra of an ω-regular language, built from an automaton for the
first time: the acceptance-enriched monoid `EM(D)` supplies a recognizer that
remembers acceptance along runs, and a rotation lemma collapses Arnold's
two-sided congruence into right multiplications alone.
The output is the exportable invariant `𝓘(L) = (𝒞, λ, M, P)` — the semantic
benchmark every other paper here reads from, and whose finite-word
specialization is the classical syntactic monoid.

*Files:* `sos_constructed.md`, `sos_constructed_figures.md`; shared figure
artifacts in `sos_figs/`. Cited elsewhere as **[SωS26]**.

---

## Reading the invariant

### `sos_toltl` — The LTL Frontier from the Syntactic ω-Semigroup

Both sides of the aperiodicity verdict, from the invariant alone: on the non-LTL
side a portable counting certificate checkable by membership queries against any
acceptor; on the LTL side a defining formula transcribed from the invariant's own
right Cayley graph rather than by the explosive Diekert–Gastin induction.
Anchoring and window-determinacy give an exactness theorem for the width-1
engine, with a graded extension above it; a census maps both frontiers and shows
neither certificate shape is universal.

*Files:* `sos_toltl.md`, `sos_toltl_spec.md`, `sos_toltl_report.md`,
`sos_toltl_figures.md`, artifacts in `sos_toltl_figs/`.

### `sos_classification` — Classifying an ω-Regular Language from its Syntactic ω-Semigroup

The classical taxonomy turned into decision procedures on the one object:
identity, the aperiodic (LTL) cut, the safety–progress/topological ladder, the
acceptance index, and the exact Wagner degree, each a finite search in the
multiplication table, polynomial in `|𝒞|`.
Wagner's derivative resists algebraic transport (no re-marking computes it) yet
stays a table computation; a reference catalogue of 6220 small languages yields
the first measured Wagner-degree profile of the class.

*Files:* `sos_classification.md`, `sos_classification_spec.md`,
`sos_classification_report.md`.

### `sos_symmetry` — Symmetries on the Syntactic ω-Semigroup

The symmetry questions model checkers *consume* but no tool *computes*: alphabet
symmetries as automorphisms of the invariant (stabilizer search, minimal witness
lasso on failure), and closure under factor rewritings — stutter invariance,
letter invisibility, the maximal independence relation — as table equations.
The groups hidden inside the invariant form a canonical group spectrum refining
the LTL frontier, with canonical LTL bounds `L♭ ⊆ L ⊆ L♯`.

*Files:* `sos_symmetry.md`, `sos_symmetry_spec.md`, `sos_symmetry_report.md`,
`sos_symmetry_figures.md`.

### `sos_measure` — Measure, Distance, and Entropy on the Syntactic ω-Semigroup

The quantitative layer, resting on a generic-verdict theorem: under any
full-support Bernoulli measure (or Markov source) almost every word is absorbed
into a bottom SCC of the right-Cayley graph, its verdict a single canonical bit
read at a kernel idempotent.
Measure `μ_p(L)` is then one exact rational linear system; a shadow surgery makes
every language null-equivalent to a canonical open one (up to measure, all of
ω-regularity is co-safety), and entropy is one Perron eigenvalue.

*Files:* `sos_measure.md`, `sos_measure_spec.md`, `sos_measure_report.md`,
`sos_measure_figures.md`.

---

## Operating on the invariant

### `sos_calculus` — A Calculus on the Syntactic ω-Semigroup: Align, Operate, Reduce

The invariant as a computational substrate for the everyday ω-automata toolbox:
**align** two invariants on a common table (the only product-priced move),
**operate** by surgery on the pair set `P` (nearly always free), **reduce** to
canonical form (polynomial).
Complement is a bit-flip, equivalence is byte equality, the safety/liveness hulls
are one scan; the exponentials do not vanish but concentrate at the ω-rational
constructors — a pay-canonicity-once economy.

*Files:* `sos_calculus.md`, `sos_calculus_spec.md`, `sos_calculus_report.md`;
queued sections in `sos_calculus_extensions.md`. Cited as **[SωSC26]**.

### `sos_giventhat` — Choosing the Simplest Property Given Prior Knowledge, Canonically

Verifying `S ⊨ φ` when `K` is already known: the freedom interval of [DPT25],
navigated heuristically on automata, becomes an exactly represented finite
lattice on the invariant — the powerset of the conjugacy classes of `ℒ(¬K)` on
one aligned table.
Exact polynomial existence tests for a safety (co-safety, obligation, recurrence,
persistence) property equivalent to `¬φ` given `K`; stutter invariance is the
technical heart, where the natural quotient test is sound but provably
incomplete.

*Files:* `sos_giventhat.md`, `sos_giventhat_spec.md`, `sos_giventhat_report.md`,
`sos_giventhat_figures.md`.

### `sos_learning` — Learning the Syntactic ω-Semigroup

An active-learning (MAT) algorithm whose queries are memberships of
ultimately-periodic words and whose limit is the language's own algebra — to our
knowledge the first such learner for the full ω-regular class, where the FDFA
approach learns acceptors instead.
Two results carry it: a harvest theorem (any erring lasso surrenders a separating
column) and the finding that two-sided columns are still not enough — membership's
error signal is one-sided — repaired by a query-free left-saturation sweep.

*Files:* `sos_learning.md`, `sos_learning_spec.md`, `sos_learning_report.md`.
Cited as **[SωSL26]**.

---

## Building the invariant at scale

### `sos_symbolic` — A Symbolic Engine for the Syntactic ω-Semigroup

Where the wall actually is: the construction is dominated by `EM(D)`, size
`(|Q|·2^{|C|})^{|Q|}`, and PSPACE-completeness makes some wall necessary — but
everything else is symbolic, because the rotation lemma says exactly that every
iterated relation is **slot-local**.
The monoid is a reachability set, closure a least fixpoint, the congruence a
greatest-fixpoint partition refinement; on an abstract decision-diagram engine
the whole pipeline is native.

*Files:* `sos_symbolic.md`, `sos_symbolic_spec.md`, `sos_symbolic_report.md`;
companion `sos_symbolic_hom.md` (the same seven phases re-expressed in the
homomorphism/saturation idiom of libDDD/libITS — equations only, no repeated
justification). Cited as **[SωSD26]**.

### `sos_census` — A Census of Syntactic ω-Semigroups: Enumerating the Small ω-Regular Languages

Automata censuses enumerate *machines*, so every frontier they map is polluted by
presentation artifacts; a census of canonical invariants by size `|𝒞|` enumerates
*languages* — one item each, byte-distinct iff distinct.
Two mutually validating constructions (derived and intrinsic) yield
presentation-free threshold theorems, density laws, the cost of canonicity, a
basis under the calculus, and an atlas with an optimal-formula column.

*Files:* `sos_census.md`, `sos_census_spec.md` (no report yet — the intrinsic
enumerator is pending). Cited as **[SωSN26]**.

---

## Standalone theory (no experimental side)

### `prophetic_counterfree` — Counter-Free Prophetic Automata Characterize Star-Free ω-Languages

Over finite words, star-free = counter-free minimal DFA; over infinite words the
bridge breaks, since a minimal-size automaton of a star-free ω-language need not
be counter-free (forward determinism can force in a parity bit).
The bridge is restored by replacing the nonexistent minimal DFA with the
canonical prophetic (Carton–Michel) automaton: `A_S` is counter-free iff `S₊` is
aperiodic.

*Files:* `prophetic_counterfree.md`.

### `syntactic_omega_semigroup_ltl` — Deciding and Constructing LTL over the Syntactic ω-Semigroup

The original single-engine draft: compute the syntactic ω-semigroup, decide
LTL-definability by aperiodicity, extract a replayable counting certificate on
the negative side, run Diekert–Gastin synthesis on the materialized quotient on
the positive side.
Largely superseded — its construction half became `sos_constructed`, its LTL half
`sos_toltl`; kept as the lineage record.

*Files:* `syntactic_omega_semigroup_ltl.md`.

### `bls_cascade` — The cascade ladder: the loop side beyond windows and parks

A section draft toward `sos_toltl.md` (proposed §5′, numbered `C.*` throughout),
carrying the loop side past the window and park engines, over the
Boker–Lehtinen–Sickert translation [BLS22] as implemented in `aut2ltl/bls`.
It has its own experiment series (K-E0..E7); the K-E0 gate refuted the first
draft's completeness conjecture C.12 and its sandwich reduction C.17.

*Files:* `bls_cascade.md`, `bls_cascade_spec.md`, `bls_cascade_report.md`.

---

## Companion material (not papers)

- `sos_toltl_engines.md` — working quarry for `sos_toltl.md` §5: the imported
  vocabulary, laws, and proof discipline of the two automaton-level engines.
- `sos_calculus_extensions.md` — sections the calculus paper should grow,
  sketched far enough that a session can draft them cold.
- `sos_quantitative.md` — the exploratory memo that preceded `sos_measure.md`.
  Superseded for the math; kept as the map of candidate results.
- `genaut_corpus.md` — working reference on how the genaut census turns an
  enumeration of presentations into an irredundant catalogue of languages.
- `non_ltl_certificates.md` — research note distilling the "name the kernel"
  thread of `aut2ltl`.
- `sos_usecase.md` — prospective catalog of what the SoS is for.

Older investigation notes and one-off experiment logs (the pi2 hunt, the
round-trip experiments, the BLS counter investigation, the definability novelty
survey, the witness log, …) were demoted to `notes/` and are not maintained.
