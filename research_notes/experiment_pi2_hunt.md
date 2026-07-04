# Experimental protocol — hunt a minimal-form star-free counterexample (Π₂ recurrence)

*Handoff spec. Self-contained: you do NOT need the theory notes to run this. For a
code-focused session. Author of spec: Claude (Anthropic) + Yann Thierry-Mieg.*

## 0. One-paragraph background (all you need)

The BLS cascade translates a deterministic ω-automaton `D` to LTL by building, for
each configuration `C`, a sub-formula for "`C` is visited only finitely often"
(`Fin(C)`). This is correct when the *ground-truth* language of that sub-question —
`Inf(C)` = "the run visits `C` infinitely often" — is itself LTL-definable
(star-free). For an input whose **language is LTL** (star-free) and whose form is
**state-minimal**, we CONJECTURE every such sub-question is star-free, so the
cascade is sound. This experiment tries to **break that conjecture**: find a
state-minimal deterministic automaton whose language is LTL but which has a state
`q` (or config `C`) with `Inf(q)` NOT star-free. Finding one is a real result (the
tool can build a wrong sub-term on an LTL language at minimal form); an empty
tightened sweep with certificates is strong support for the conjecture.

## 1. Objective (the decidable predicate)

Search for an automaton `D` satisfying ALL of:

- **P1. Language is LTL / star-free.** `L(D)` is star-free. (Every LTL language is
  star-free, so a formula-generated corpus satisfies this by construction; for an
  enumerated automaton, TEST it.)
- **P2. Form is state-minimal.** `D` is minimal in state count within its
  acceptance class (sbacc Büchi, or the parity-sbacc form the pipeline actually
  builds). Certify with SAT-min, not just bisimulation reduction.
- **P3. Some sub-question is non-star-free.** There exists a state `q` (config `C`)
  such that `Inf(q)` = "run of `D` visits `q` infinitely often" is NOT star-free.

`P1 ∧ P2 ∧ P3` = the counterexample. **Report any hit immediately.**

Note the built-in consistency guard: because `L(D)` is star-free (P1), a genuine
"leak" (the sub-question discrepancy feeding into the language) is automatically
excluded — so you are NOT hunting a non-LTL language; you are hunting a non-star-free
RECURRENCE SUB-QUESTION inside an LTL language on a minimal form. That combination
is what `gfa_pad2` exhibits OFF-minimum (a padded form of `GFa`); the whole point is
whether minimality forbids it.

## 2. Tools (already in the repo — use, don't reread)

- `tests/probes/oracle_dump.py <hoa>` — SOSG definability oracle: exact star-free
  verdict + certificates + `det_generic_minimal` state count. This is your P1 and
  P3 judge (run it on `L(D)` for P1, and on each `Inf(q)` language for P3).
- `tests/probes/fin_ground.py <hoa>` — grounds every `Fin(C)` of the cascade against
  its exact `Inf(C)` ground-truth automaton AND reports the aperiodicity screen's
  reading of each ground-truth language. **This already computes P3 per config.**
  Your sweep is essentially: run this over a corpus and flag any run where the input
  language is star-free (P1) and some ground-truth `Inf(C)` reads non-aperiodic.
- `tests/probes/bls_ungated.py <hoa>` / `tests/probes/bls_padded.py <hoa> <ref>` —
  run the ungated cascade and check final-output equivalence. Use on a HIT to see
  whether the wrong sub-term actually corrupts the assembled formula (it may cancel).
- `python3 -m survey.diff.ltl_diff` — containment direction + witness word between
  two formulas/languages (for characterizing a hit's error).
- SAT-min + spot (`decompose_aut` entry) — your P2 certifier and the producer of the
  exact form the pipeline feeds the cascade.
- `genaut/` census (see `genaut/logs/`) — the existing exhaustive small-automata
  generator; extend its per-instance check with P3 (it previously tested only final
  equivalence).

Respect the repo's discipline: ≤15s per example, one input per probe invocation,
redirect long output to `tests/**/logs/`, no `/tmp`, no manual process management.

## 3. Three generation strategies (run all; they cover different risk)

### 3A. Formula-driven random sweep (cheapest, run first)
1. Generate random LTL formulas in the **recurrence-expressible** class — those
   whose language is deterministic-Büchi-recognizable (Gδ). Practically: random LTL
   over 2–3 atoms, keep `φ` where spot reports the language is DBA-recognizable
   (e.g. it determinizes to a Büchi/`Inf`-type acceptance without needing full
   parity). Bias toward `GF`, `FG`, nested `GF(a ∧ X b)`, `GF(a ∧ XF b)`, boolean
   combinations — these are where detection memory (and thus groups) can appear.
2. Build the **minimal sbacc DBA** `D_φ` (spot minimize + SAT-min certify, P2).
3. Run `fin_ground.py` on `D_φ`. Flag if any ground-truth `Inf(C)` is non-star-free
   (P3) while `L(D_φ)` is star-free (P1, automatic here).
4. Budget: thousands of formulas, sizes up to ~8 states, ≤15s each.

### 3B. Extend the genaut exhaustive census (systematic, small sizes)
1. For every automaton in the census that is (a) minimal (P2) and (b) has a
   star-free language (P1 — run `oracle_dump.py`), run `fin_ground.py` and test P3.
2. This is EXHAUSTIVE under the census bound — an empty result here is the strongest
   evidence, and its coverage bound (max states, max alphabet) is the headline
   number to report.

### 3C. Directed construction (highest hit-probability if the object exists)
The object we want: an order-`p` group orbit in `D`'s transition monoid that is
**invisible to the language** but read **set-differently** by a recurrence question.
Recipe (iterate with the oracle judging each step):
1. Pick a base recurrence language that genuinely needs detection memory, e.g.
   `GF(b ∧ Xb)` (needs to detect `bb`).
2. Introduce a second letter `a` that acts as an order-`p` **group** permuting a
   set of otherwise-language-equivalent states (a "phase"). Keep `a`'s action
   **language-invisible**: the residual language must be unchanged across phases
   (check: `oracle_dump.py` must still report the intended star-free `L`, and
   `det_generic_minimal` state count must not collapse the phases away).
3. Wire a lasso word `ℓ` so that the `p` phase-images fall into **≥2 distinct
   `ℓ`-attractor cycles** (so some state `q0` is visited i.o. from one phase, not
   another) — this is the "set-different twin."
4. Place the acceptance marks so that all `ℓ`-attractors share the SAME
   accept/reject status (dodge the leak; forced anyway if `L` stays star-free —
   use it as a check that you have not accidentally left the star-free class).
5. Certify P2 (SAT-min: the phase must NOT be sheddable — the group is genuinely
   needed at min size). Then test P3 via `fin_ground.py`.

Prior attempts ("stags", see theory note) all died by either collapsing to a
smaller language (P2 fails) or leaking (P1 fails). The NEW guidance: do NOT try to
make the group "sheddable-but-present" — a size-optimal group is fine and expected;
aim squarely at (P2 holds) ∧ (set-different recurrence) ∧ (star-free language).

## 4. What to record

For EACH hit (`P1 ∧ P2 ∧ P3`):
- the HOA of `D` (save under `samples/fixtures/hoa/…`),
- the offending state/config `q`/`C`, and the `Inf(q)` ground-truth automaton,
- the oracle certificate that `Inf(q)` is non-star-free (the counting witness
  family, ideally of the form `u vⁿ ℓ^ω` toggling with `n mod p`),
- the SAT-min certificate for P2 (and the state count vs. any smaller candidate),
- **the assembled-output check:** run `bls_ungated.py`; report whether the final
  formula is equivalent to `L(D)` or wrong, with containment direction + witness
  (`ltl_diff`). (A wrong sub-term with a still-correct output = the errors cancel;
  a wrong output = the tool is unsound at minimal form — the stronger finding.)

For the EMPTY outcome (no hit):
- the exact bound swept (max states, alphabet size, #formulas / census coverage),
- the count of instances that passed P1 ∧ P2 (the real denominator),
- the **death histogram**: for near-misses (some `Inf(q)` looked group-bearing),
  classify why it is NOT a counterexample — `Inf(q)` turned out star-free after all
  (set-equal / benign group), or P2 failed (a smaller form existed), or P1 failed
  (language not actually star-free). These certificates are what we need to turn the
  empty sweep into a direct proof.

## 5. Interpretation (hand back to the theory session)

- **A hit** refutes the Π₂ conjecture: state-minimality is NOT sufficient, and the
  tool's soundness must rest on more than "minimized" (the specific normalization,
  or a per-sub-term definability screen). Bring the HOA — it goes straight into the
  theory as the object to dissect.
- **An empty tightened sweep** (3B exhaustive under a solid bound, 3A broad, 3C
  design attempts all dying) is strong support and, more usefully, the death
  histogram tells us WHY minimality forbids the pattern — that is the scaffold for
  the direct "recurrent set is phase-invariant" proof we owe.

## 6. Explicit non-goals

- Do NOT try to fix the tool or the gate in this session — this is a pure hunt.
- Do NOT chase non-LTL inputs (mod3-style) — those are known and irrelevant; P1
  (star-free language) is a hard filter.
- Do NOT rely on bisimulation-minimality for P2 — it is too weak (a fat form can
  survive it); SAT-min is required.
- Keep spot bounded-or-skipped; a timeout is a reported finding, not a failure.
