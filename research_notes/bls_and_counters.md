# BLS and counters — what the cascade actually needs (2026-07-04)

Where the Boker–Lehtinen–Sickert construction really uses counter-freeness,
what the implemented cascade (`aut2ltl/bls/`) does on group-bearing inputs, and
what that means for the definability gate. Investigation over three small
inputs, fully reproducible (pointers below).

## Direction

The kr cascade is fronted by a gate (`aut2ltl/bls/gate/`) that admits an input
only behind a proved-aperiodic reading of one deterministic form's transition
monoid. Two established facts set up the tension:

- the ungated cascade translates `gf_aa_parity` — an *LTL* language,
  `GF(a & Xa)`, deliberately encoded with a Z2 in its transition monoid —
  **correctly**, on the very form the gate declines
  (`tests/probes/bls_ungated.py`);
- the ungated cascade emits a confident **wrong** formula on `mod3_a`, a
  genuinely non-LTL (mod-3 counting) language — the silent unsoundness the
  gate exists to stop.

Both deterministic forms of `gf_aa_parity` (generic-minimal and the
parity-sbacc the cascade builds from) carry the Z2
(`tests/probes/form_aperiodic.py`), so no form-level aperiodicity screen can
separate these two cases. The question: what *does* separate them — what is
the exact border of what the cascade can cover?

## What the paper actually assumes

Reading `aut2ltl/bls/paper/Automata2LTL.txt` (digest:
`aut2ltl/bls/paper/automata-to-ltl-construction.md`):

- Counter-freeness is load-bearing in **exactly one place**: Proposition 6
  (Krohn–Rhodes–Holonomy), the *existence* guarantee that a counter-free
  semiautomaton is homomorphic to a **reset** cascade.
- The entire technical core is unconditional given that object: Lemma 4 (the
  five reachability formulas match their intended semantics) and Lemma 7
  (`Fin(C)`) are stated for *arbitrary* reset cascades; Props. 7/8 need only
  the homomorphism (cover) π.

So the construction's real soundness premise is "a genuine reset cascade,
covered, with acceptance lifted" — counter-freeness is only the ticket that
buys it. On a non-counter-free input the paper is silent (precondition unmet),
not negative.

## Hypothesis

The construction is sound whenever it is *semantically* aperiodic — i.e. the
operators are well-formed in the presence of an aperiodic **syntactic
ω-semigroup** (= the language is LTL), regardless of groups in the
presentation. Counter-freeness of the form is a presentation-dependent proxy
the authors could prove inside, not the real barrier. (Consistent with
benchmark experience: with the gate skipped, on formula-derived inputs the
cascade never answered inaccurately where checkable.)

## Experiment 1 — which paper premise breaks (`tests/probes/casc_cover_check.py`)

The probe decomposes one HOA and checks the two premises separately on the
resulting cascade: (a) every level is a reset semiautomaton (per combined
letter: identity or constant), (b) the cover π commutes with the true lifted
dynamics.

| input | cover π | reset premise | cascade output |
|---|---|---|---|
| `gf_aa` (LTL, aperiodic form) | holds | holds | correct — on-theorem |
| `gf_aa_parity` (LTL, Z2 form) | holds | **violated**: one letter, top level ⟨a, lower=1⟩ = transposition {1↔2} | correct — off-theorem |
| `mod3_a` (non-LTL) | holds | **violated**: one letter, level 1 ⟨a, below=(2,)⟩ = 3-cycle (1 3 2) | wrong |

Findings: SgpDec's cover is genuine in all cases — the break is *only* the
reset property, at exactly one group letter each. The parser labels those
levels `kind=reset` unchecked (`LevelInfo.kind` is asserted, not verified), so
`Cascade.has_nontrivial_groups()` reads no groups: the "group misread as
reset" of the gate's docstring is real but is a *labeling* gap, not a
corrupted cover. Crucially, the violation is structurally identical in the
correct and the wrong case — **no local structural test on the cascade can
delineate coverage**.

## Experiment 2 — grounding every Fin(C) sub-term (`tests/probes/fin_ground.py`)

For each reachable config C, the probe builds the cascade's `Fin(C)`
sub-formula and compares it against its exact Lemma-7 semantics: the
configuration automaton with `Fin(0)` acceptance, marks on transitions leaving
C. (Config-level ground truth matters: on `mod3_a` the cover is not injective —
6 reachable configs over 5 states — so state-level ground truth is wrong for
the doubled state.) It also reports the aperiodicity screen's reading of each
ground-truth language.

| input | Fin(C) | build vs ground truth | GT language |
|---|---|---|---|
| `gf_aa_parity` | (1,1) | correct | LTL (certified by match) — *screen reads "group"* |
| `gf_aa_parity` | (1,2), (2,1) | correct | LTL, screen aperiodic |
| `mod3_a` | (1,1,2), (1,2,2), (1,3,2), (1,4,2) | correct | LTL, screen aperiodic |
| `mod3_a` | (1,1,1), (2,1,1) | **wrong** — pure under-approximations | non-LTL (see below) |

Findings:

- `gf_aa_parity` is correct **at every sub-term**. The earlier
  "limit-cancellation" theory (individually wrong Fins whose errors cancel in
  the acceptance combination) is refuted — the operators compute correct
  reachability over the group-carrying cascade.
- `mod3_a` breaks in exactly two sub-terms, and both target languages are
  genuinely non-LTL: in mod3's config graph the Z3 cycle
  {(1,1,2),(1,3,2),(1,2,2)} exits to (1,1,1) only from position (1,1,2) on
  `!a`, so "visits (1,1,1) finitely often" is decided by the count of `a`'s
  **mod 3** — properly non-star-free. The formulas' missed witnesses are
  `a; cycle{!a}` and `a;a;a; cycle{!a}`: an LTL formula for a non-LTL target
  must err somewhere, and it errs *exactly on the words whose truth is the
  modular count*.
- The screen over-reads at sub-term granularity too: parity's Fin((1,1))
  screens "group" yet is built correctly (its language is star-free — the
  benign-group phenomenon recurring one level down).

## The law, and an unexpected consequence

**Empirical law (9/9 sub-terms):** the cascade builds a sub-term correctly iff
that sub-term's target language is LTL. Groups in the presentation are
harmless per se; what breaks the operators is a genuinely *modular question*,
never a group in the carrier. This confirms the hypothesis — and sharpens it
from per-input to per-sub-term.

The sharpening cuts back, though: correctness is governed by LTL-ness of the
**form's sub-problems**, not of the input language. The two can diverge in
principle: pad an LTL language's automaton with a redundant mod-3 counter
(product with a counter the acceptance ignores) and some "visits C finitely
often" becomes modular — a non-LTL sub-term inside an LTL input, so the
cascade should *lie on an LTL language*. If such forms are reachable, the
language-level oracle alone is NOT a sufficient gate. What plausibly protects
the practice: `decompose_aut` normalizes to a *minimized* sbacc parity form,
which strips redundant counters before the operators see them. Hence the crux:

> **For a minimal deterministic form of an LTL language, is every Fin(C)
> (and every reach sub-problem) itself LTL-definable?**

Yes ⟹ minimized input + language-LTL ⟹ cascade correct: the semantic
(oracle) gate is exactly right and the form screen is provably replaceable.
No ⟹ the gate genuinely needs form-level information, and the benchmark
record is luck of a characterizable kind.

## Reproduction

All probes are single-input, seconds each (GAP + SgpDec required, see
`install_gap.sh`):

```
python3 tests/probes/casc_cover_check.py samples/fixtures/hoa/definability/gf_aa_parity.hoa
python3 tests/probes/casc_cover_check.py samples/fixtures/hoa/definability/gf_aa.hoa
python3 tests/probes/casc_cover_check.py samples/fixtures/hoa/various/mod3_a.hoa
python3 tests/probes/fin_ground.py      samples/fixtures/hoa/definability/gf_aa_parity.hoa
python3 tests/probes/fin_ground.py      samples/fixtures/hoa/various/mod3_a.hoa
python3 tests/probes/bls_ungated.py     samples/fixtures/hoa/definability/gf_aa_parity.hoa
```

## Where to take it

1. **The crux question, adversarially:** hunt a *minimal* deterministic form
   of an LTL language with a group whose phases are limit-distinguishable
   per-state (making some Fin(C) non-LTL). The padded-counter trick produces
   non-minimal ones only; the question is whether minimality forbids the
   pattern. Finding one refutes the pure-semantic gate; failing to find one
   points at a theorem.
2. **The crux question, theoretically:** "run visits q infinitely often" is a
   linked-pair condition in the ω-semigroup; look for a short argument that
   for a minimal recognizer of a star-free ω-language these per-state
   recurrence languages stay star-free (Carton–Perrin–Pin and
   Preugschat–Wilke, in `papers/`, are the places to look — Preugschat–Wilke
   in particular decomposes definability testing per-SCC/per-state).
3. **Honest labeling regardless:** the parse should stop asserting
   `kind=reset` — record the actual per-letter action class so
   `has_nontrivial_groups()` tells the truth; the reset premise is checkable
   in milliseconds (Experiment 1's check).
4. **Gate consequence to draft once 1/2 settles:** if the theorem holds, the
   gate's decline on group readings can be replaced by the language-level
   oracle for *minimized* forms; if the counterexample exists, the gate needs
   a per-sub-term screen (Experiment 2's ground-truth automata are exactly the
   objects to screen).
