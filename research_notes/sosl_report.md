# SoS Learner — Status Report

Date: 2026-07-06. Traces where the `sosl/` implementation stands against the plan
in `research_notes/sos_learner_spec.md` (milestones) and against
`research_notes/sos_learning.md` (the paper, whose running examples are computed
by hand). Format spec: `research_notes/sosg_format.md` (the `.sos` normal form).

## Milestones (spec §8)

- **M1 — Teacher + validator.** DONE.
- **M2 — Learner without saturation** (table, fill/close/consist, chains,
  export). Substantially done; caveats below.
- **M3 — Saturation + exact equivalence.** NOT STARTED — this is the next step.
- **M4 — Campaign.** Not started.

## Ground truth: reference builder vs the paper

`sosl.reference.reference_of_hoa` reads the canonical syntactic ω-semigroup
`S(L)₊¹` from each source automaton in `research_notes/sosg_figs/sources/`. Class
counts match the paper's fingerprint tables **exactly**:

| example | source HOA | paper `\|S(L)₊¹\|` | reference |
|---|---|:--:|:--:|
| GF(aa) | `gf_aa_parity.hoa` | 6 | 6 ✓ |
| Even | `even.hoa` | 5 | 5 ✓ |
| EvenBlocks | `evenblocks.hoa` | 7 | 7 ✓ |

Fixture: `tests/sosl/paper_examples.py`. **The reference (ground-truth) leg is on
track** — it reproduces the paper's hand-computed canonical objects.

## M2 learner status (no saturation)

| language | canonical | learned | acceptance | vs reference |
|---|:--:|:--:|---|---|
| GF a | 2 | 2 | correct | byte-equal ✓ |
| F a | 3 | 2 | correct | coarser stall |
| a U b | 4 | 3 | correct | coarser stall |
| GF(aa) | 6 | 5 | correct | coarser stall |
| Even | 5 | 4 | correct | coarser stall |
| EvenBlocks | 7 | 7 | correct | byte-equal ✓ |
| F(a ∧ Xa) | 6 | 5 | **WRONG** | coarser + acceptance-wrong |

`EvenBlocks` already reaches the canonical object at M2 — its congruence is
carried by the ω-columns, the paper's "the right congruence is not the seed"
point made concrete. `GF a` also lands canonical. The other coarser cases are
acceptance-correct but non-canonical, awaiting saturation. `F(a ∧ Xa)` is the
sole acceptance-wrong export (see below).

## Does the observed stall match the paper? (Even) — NO, not word-for-word

Both agree on the canonical **endpoint** (5 classes: ε, !a, a, a!a, aa all
distinct). They disagree on the intermediate **M2 stall**:

- **Paper** (§4.3, by hand): 4 classes `{ε}, {a, a!a}, {!a}, {aa}` — `a!a`
  merged into `[a]`; `ε` a permanent singleton; `aa` its own class.
- **Ours** (M2 fixpoint, `tests/sosl/paper_examples.py`): the identity class
  absorbs `aa` (`aa ↦ [ε]`); final 4-class `{ε, aa}, {!a}, {a}, {a!a}`.

Two root causes:

1. **eps-merge** — our deviation from spec §3.2 ("ε is a permanent singleton").
   Introduced last session so that `GF a → 2` classes (matching the reference).
   It lets `ε` absorb right-congruent non-empty words (`aa ↦ [ε]` for Even),
   changing *which* words collapse at the stall. The paper never merges into `ε`.
2. **No saturation** — the paper's stall is resolved by the §4.3 left-saturation
   sweep (splits `a!a` from `a` via a frozen-prefix column). We have no such
   phase, so we cannot reproduce that split; M2 relies on counterexample harvest
   alone. Whether our coarser Even fixpoint is *permanent* or would be broken by
   a longer counterexample is unverified beyond the teacher's bound 8.

## The `F(a ∧ Xa)` finding: acceptance-wrong export / candidate permanent stall

This is the one case where the exported invariant is **acceptance-WRONG**, not
merely non-canonical. The M2 fixpoint merges `a·!a` into the identity class. The
equivalence oracle assents — the *hypothesis* folds the literal loop letters and
stays correct to bound 8 — but `Invariant.member` reduces a lasso through the
class multiplication table `mult[c][d] = fold(c, rep[d])`, which is only
well-defined for a **two-sided** congruence. At M2 the partition is a *right*
congruence only, so the exported algebra is wrong. Concretely on
`a·(a!a!a)^ω`: hypothesis → True (matches the teacher), exported invariant →
False.

This is exactly the paper's §4.2 gap, *"acceptance-correct is not
algebra-correct."* The paper's Even / EvenBlocks stalls are **transient** (an
equivalence query eventually catches them). `F(a ∧ Xa)` is a candidate for the
**permanent** stall the paper flags as an open exhibit (§4.2; §5 `⟨TBD⟩`).
Permanence is *not* proven — only acceptance-equivalence of the hypothesis to
bound 8. Diagnosed by `tests/sosl/diag_export_vs_hyp.py`, which localizes the
divergence to the two-sided read-off (export), not the learner core: on
`F(a ∧ Xa)` the hypothesis agrees with the teacher on every tested lasso while
the exported invariant disagrees on 4.

The fix for every coarser/wrong case above is **M3 saturation (§4.3)**: the
left-context split that turns the right congruence into the two-sided syntactic
one, after which the exported invariant is well-defined and canonical.

## Open questions to resolve with / before M3

1. **eps convention.** Is the canonical identity a permanently-adjoined singleton
   (spec §3.2, paper hand-traces) or merged with identity-acting words (our
   reference builder, e.g. `GF a → 2`)? The reference matches the paper on all
   three running examples (no letter acts as identity there), so the conflict
   only bites on languages like `GF a`. This decides whether the eps-merge stays,
   and whether our Even/`GF(aa)` stalls can ever match the paper's trajectory.
2. **Implement §4.3 left-saturation** — the missing M2→M3 step.
3. **Confirm/refute `F(a ∧ Xa)`** as a permanent §4.2 stall (needs a proof or an
   algebraic / larger-bound argument, not just bounded search).

## Probes (all under `tests/sosl/`)

- `paper_examples.py` — the three paper examples from their source HOA; reference
  size check vs the fingerprint tables, learned status, and a dump of the M2
  stall partition for word-for-word comparison against the hand traces.
- `reference_vs_learner.py` — per-formula reference-vs-learned byte compare plus a
  budgeted acceptor check (exhaustive when the lasso space ≤ 20k, else a
  deterministic sample — never a 10⁸ loop on a large alphabet).
- `diag_export_vs_hyp.py` — isolates export-vs-hypothesis divergence; the tool
  that proved the `F(a ∧ Xa)` bug is in the two-sided read-off, not the core.
