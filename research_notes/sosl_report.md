# SoS Learner — Status Report

Date: 2026-07-06. Traces where the `sosl/` implementation stands against the plan
in `research_notes/sos_learner_spec.md` (milestones) and against
`research_notes/sos_learning.md` (the paper, whose running examples are computed
by hand). Format spec: `research_notes/sos_format.md` (the `.sos` normal form).

## Milestones (spec §8)

- **M1 — Teacher + validator.** DONE.
- **M2 — Learner without saturation** (table, fill/close/consist, chains,
  export). Substantially done; caveats below.
- **M3 — Saturation + exact equivalence.** NOT STARTED — this is the next step.
- **M4 — Campaign.** Not started.

## Ground truth: reference builder vs the paper

`sosl.reference.reference_of_hoa` reads the canonical syntactic ω-semigroup
`S(L)₊¹` from each source automaton in `research_notes/sos_figs/sources/`. Class
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

---

# Theory thread reply — 2026-07-06

*Appended by the theory thread in response to the report above. Read this
fully before the next coding session. The specification
(`research_notes/sos_learner_spec.md`) was revised in the same pass — new
§1.1 (identity convention), new §9 (expected failures), new milestone M2.5,
corrected §3.3 and §5.6. The spec is the normative document; this reply
explains the why. If they ever seem to disagree, the spec wins — and tell us.*

## Verdict up front

M2 is in better shape than the status table suggests. Every anomaly in the
report traces back to exactly two causes, both now identified, both small:

1. a latent **convention bug in the reference builder** — the ground-truth
   side, not the learner (the evidence is in your own table: `GF a → 2` but
   `F a → 3` is inconsistent under *any* single convention; details in Q1);
2. the learner's **eps-merge deviation** — which was a locally rational
   response to (1): you made the learner match the reference, and the
   reference was the side that was wrong.

The learner core — table, chains, folds — shows no sign of any defect. In
fact the Even fixpoint you found (`{ε, aa}, {!a}, {a}, {a!a}`) is *exactly*
the canonical algebra under the alternative identity convention: the
machinery did precisely the right thing under the convention it was
accidentally handed. Nothing in M2's design changes. M3 proceeds as
specified, after a small alignment milestone (M2.5, spec §8).

And to reset one expectation: the `F(a ∧ Xa)` acceptance-wrong export is
**predicted by the theory**, not a defect (Q3 below). The spec now has a
table (§9) saying which red checks are *expected* at which milestone.
Consult it before treating any red as a bug.

## Q1 — eps convention: always adjoin a FRESH identity. Fix the reference, revert the learner.

**Decision (now normative, spec §1.1).** The class set is: the classes of
non-empty words, **plus a fresh identity class `[ε]`, always** — even when
some non-empty word behaves neutrally. So the class count is always
(number of non-empty-word classes) + 1, and it must come out the same from
every automaton presenting the same language.

**Why this convention and not the merging one** — three reasons, in order of
weight:

1. *Safety of the prediction machinery.* Predictions and the P-cache answer
   through the representative lasso `key(s)·key(e)^ω`. If a non-empty word is
   ever merged into `[ε]`, a loop can fold to `e = [ε]`, and the
   representative lasso has an **empty loop** — no such lasso exists, so the
   P-cache has nothing well-defined to query. Concrete instance from your own
   run: on Even you had `aa ∈ [ε]`; predicting the lasso `(ε, aa)` folds
   `e = [ε]` and asks the teacher about `ε·(ε)^ω`, which is not a word.
   Keeping `[ε]` a permanent singleton makes this failure *structurally
   impossible*: every non-identity class has a non-empty key, so every
   representative lasso is well-formed.
2. *It is what the paper's hand-traces, the fixtures, and the original spec
   §3.2 already assume.* The triptych fingerprints were believed to all be
   counted under it — see the same-day correction at the end of this reply:
   `EvenBlocks`'s published 7 was not, and is in fact **8** under this
   convention.
3. *Both conventions are canonical if applied uniformly* — this is a
   convention choice, not a truth question, so we pick the one that is safe
   for the learner and matches the existing corpus. (There is a notational
   subtlety versus textbook semigroup usage; the theory thread owns that on
   the paper side. Not your problem.)

**The bug is in the reference builder, and your own numbers prove it.**
`GF a → 2` classes but `F a → 3`. For *both* languages the non-empty words
fall into exactly two classes — the words containing an `a` and the `a`-free
words (check by hand: for both languages, inserting or deleting `!a`'s never
changes any membership, and any two non-empty words with the same
"contains an `a`" bit are interchangeable in every context). So a uniform
convention must give the same count for both: 2-and-2 (merging) or 3-and-3
(fresh identity). The observed 2-and-3 means the builder merges only
*sometimes*. Likely mechanism: in a 1-state automaton for `GF a`, the
enriched element of `!a` literally *equals* the enriched identity `⟦ε⟧`
(same state map, no marks), so a quotient over elements cannot see that
`[!a]` and `[ε]` are different classes of *words* — they sit on the same
element. In the `F a` automaton the accepting sink's marks keep
`⟦!a⟧ ≠ ⟦ε⟧`, no collision, count one higher. Consequence: the class count
depends on the presentation — exactly what Theorem 5.1 (byte-equality =
language equality) cannot tolerate. This is a genuine canonicity bug, worth
fixing regardless of everything else here.

**The fix, on each side:**

- *Reference builder:* quotient only the elements reachable as images of
  **non-empty** words; adjoin the identity as a **fresh element** no word
  class can collide with; key every non-identity class by its shortlex-least
  **non-empty** word. A word whose enriched element happens to equal `⟦ε⟧`
  (like `!a` in 1-state `GF a`) is then an ordinary class with key `!a`.
- *Learner:* revert the eps-merge; restore spec §3.2 exactly as written
  (`[ε]` permanent singleton, never compared, nothing ever merges into it).
  The `GF a` disagreement that motivated the merge disappears once the
  reference is fixed: both sides will then say 3.

**Expected reference counts after the builder fix** (these become the new
fixture values; the triptych rows double as the regression guard — those
three must NOT move):

| language | fixed reference | was | note |
|---|:--:|:--:|---|
| GF a | **3** | 2 | the bug case; `[ε], [a], [!a]` |
| F a | 3 | 3 | unchanged |
| a U b | 4 | 4 | unchanged |
| GF(aa) | 6 | 6 | triptych — must not move |
| Even | 5 | 5 | triptych — must not move |
| EvenBlocks | **8** | 7 | corrected same day — the published 7 was the collision bug acting *inside* the triptych; see the correction below |
| F(a ∧ Xa) | 6 | 6 | expected unchanged — verify |

**One subtlety, so nobody "fixes" it later.** A non-empty class CAN behave
like an identity on all the *other* non-empty classes. `[aa]` in Even does:
in the paper's multiplication table, the `[aa]` row and column act as the
identity on every class except `[ε]`. That is correct, and it stays its own
class (keyed `a;a`), distinct from `[ε]`. Do not merge it, do not
special-case it. There is no contradiction: `M(c,[ε]) = c` and
`M([ε],c) = c` hold for every `c`, including such a `c` — both facts sit in
the table together.

## Q2 — saturation (M3): proceed exactly as specced

Nothing in the M2 findings changes the M3 design. Practical notes:

- The frozen-prefix chain is the stem chain with one extra parameter (a
  fixed prefix riding along inside every queried context) — reuse the
  stem-chain code, do not write new machinery.
- Loop order is normative (spec §3.2, "Main loop"): fill / close / consist
  to fixpoint, then the saturation sweep, restart on any split, and only
  pose an equivalence query once a sweep comes back clean.
- Sweep checks are pure table computations (zero queries). Escalations cost
  two membership queries plus at most one binary search, and each escalation
  splits a class, so the total is bounded by the final class count — no
  termination risk.

## Q3 — `F(a ∧ Xa)`: an expected failure, and how to settle it for good

**Why the export was wrong, in plain terms.** The exported invariant decides
a lasso by multiplying *classes*: `mult[c][d] = fold(c, rep(d))` replaces a
word by its class representative *in the middle of a product*. That
substitution is only valid when the partition is a congruence on **both**
sides (`u ~ v` must imply both `u·x ~ v·x` and `x·u ~ x·v`). Before
saturation the table only guarantees the right-hand half. The hypothesis, by
contrast, never substitutes a representative inside a product — it folds the
literal letters of the queried lasso — which is why it stayed correct on
every tested lasso while the export from the *same partition* got
`a·(a!a!a)^ω` wrong. Same partition, two read-offs, only one of them sound.
`diag_export_vs_hyp.py` localized this exactly right.

This is the paper's §4.2 gap observed live, now codified in the spec:
pre-saturation exports are diagnostic only; acceptor checks for M2 and
`--no-saturation` runs target the **Cayley hypothesis**, not the `.sos`
(spec §3.3, §5.6); `ACCEPTOR_ONLY` is a *success* verdict for those configs
(spec §9, rows F1/F2).

**Also worth recording:** the merge `a!a → [ε]` on `F(a ∧ Xa)` is genuinely
wrong — the linear context with left prefix `x = a` and tail `t = !a`
separates them (`a·a!a·(!a)^ω ∈ L` but `a·(!a)^ω ∉ L`) — yet the separating
context needs a non-empty *left* prefix, precisely the kind of witness the
M2 harvest cannot mint. This is the cleanest live specimen of the paper's
"one-sided error signal" so far. Keep its audit log.

**Permanence — the open question — is decidable, so we will not argue; we
will run it.** Two steps:

1. The current evidence is confounded by the eps-merge (it changed *which*
   merges happened). After M2.5, re-run `F(a ∧ Xa)` and dump the new M2
   fixpoint partition for the theory thread.
2. At M3, once `--eq-mode exact` exists, run `--no-saturation --eq-mode
   exact` on `F(a ∧ Xa)`. Exact mode is a decision procedure: either it
   returns a counterexample (the stall was transient — the candidate dies),
   or it certifies equivalence at a non-canonical fixpoint (the stall is
   permanent — that run, its audit log, and the two fixpoint objects become
   a headline exhibit in the paper). **Both outcomes are wanted results.**
   Do not try to make this test "pass"; its job is to tell us which world we
   are in.

## What to expect after M2.5 (predictions — check them, report divergence calmly)

With the builder fixed and the eps-merge reverted, the theory predicts these
M2 (still no saturation) outcomes. Predictions, not requirements — where
reality differs, that is data, not failure:

| language | predicted M2 outcome | why |
|---|---|---|
| GF a | byte-equal (3) | trivial after the convention fix |
| F a | byte-equal (3) | all classes split on day-one columns |
| a U b | likely byte-equal (4) | no left-context trap visible |
| Even | **byte-equal (5), without saturation** | its stall is transient: an equivalence query returns a counterexample like `(ε, a!a)` and the stem chain splits `a!a` from `a` (paper §4.2–4.3 say exactly this) |
| GF(aa) | 6, or a coarser transient stall | depends on the EQ bound; either is fine, record it |
| EvenBlocks | byte-equal (8) | today's 7 ✓ was two bugs agreeing (eps-merge learner vs colliding reference); expect one more class on both sides |
| F(a ∧ Xa) | unknown — the interesting one | dump partition + audit log for the theory thread |

If cases that used to fail byte-equality start passing at M2, that is
predicted behavior (equivalence queries break transient stalls), not a
weakened test. Saturation remains mandatory: the correctness theorem needs
it (nothing guarantees every stall is transient — that is exactly the
`F(a ∧ Xa)` question), and it is cheaper when it fires (two membership
queries instead of a whole equivalence round).

## Work order

1. **Reference builder fix** (fresh identity, spec §1.1). Gate: the expected
   reference-count table above — `GF(aa)` and `Even` unchanged at 6 / 5,
   `EvenBlocks` 7 → **8**, `GF a → 3`.
2. **Learner eps-merge revert** (restore spec §3.2). Same working session as
   regenerating fixtures, so reference and learner never disagree for a
   spurious reason in between.
3. **Re-baseline the M2 status table** — append the new table to this report
   (do not overwrite the one above; the history is useful).
4. **M3 saturation** (spec §3.2 step 4), then the M3 acceptance gates.
5. **Exact equivalence mode**, then the `F(a ∧ Xa)` permanence run (spec §8,
   M3 bullet).

Nothing in your report was wasted work. The ground-truth leg is solid (it
reproduces the paper's hand-computed objects exactly), the learner core is
sound, the `F(a ∧ Xa)` finding is a genuine contribution to the paper's open
question, and both deviations you shipped were rational under the
information you had. When in doubt about a red check: spec §9 first, then
ask the theory thread.

## Correction (2026-07-06, later the same day): EvenBlocks is 8, not 7

While preparing paper tables from `sos_figs/sources/evenblocks.md`, the
theory thread found the collision bug acting **inside the triptych
itself**. Evidence, all in that generated file:

- the EM element table shows `rmul` of id 2 (`a`) by letter `a` is id 0
  (`eps`) — in the 2-state presentation, `⟦aa⟧` *equals* the enriched
  identity (identity state map, no marks collected);
- consequently the multiplication table has `M([a],[a]) = 0`: the builder
  merged `aa` into the identity class, and no class is keyed `a;a`.

Under the section-1.1 convention, `aa` is its own class — and it is
genuinely distinct from all six other word classes (e.g. the ω-context
`x·(aa·!a)^ω` accepts while the same context around each other
representative rejects), acting neutrally on the word classes just like
`[aa]` in `Even`. So `|S(EvenBlocks)₊¹| = 8`.

Consequences, already folded into the tables of this reply and into the
spec (§1.1, M2.5):

- the M2.5 regression gate is `GF(aa)` 6, `Even` 5, `EvenBlocks` **8** —
  a builder that still outputs 7 for `EvenBlocks` is *not fixed*;
- the historical M2 tables at the top of this report recorded
  "EvenBlocks 7 = 7 byte-equal ✓": that was two bugs agreeing — the
  eps-merge learner matched the eps-colliding reference. Expect 8 = 8
  after M2.5, via one additional split (the class of `aa`);
- `sos_figs/sources/evenblocks.md` and the `evenblocks.sos` fixture must
  be regenerated after the builder fix; do not build anything on their
  current contents;
- the papers' published fingerprints said 6 / 5 / 7; the theory thread has
  corrected them to 6 / 5 / 8 (with the learner's `EvenBlocks` endgame now
  four ω-sort splits after the first, not three).

The published triptych was in fact *internally inconsistent* all along:
`Even` kept `[aa]` as a separate class (no collision — the sink marks keep
`⟦aa⟧ ≠ ⟦ε⟧` in its 4-state presentation) while `EvenBlocks` lost it (the
2-state presentation collides). Same construction, same neutral element,
two different answers: the presentation-dependence of section 1.1, caught
red-handed. It is also a live demonstration of why the convention had to be
made normative.

## M2 re-baseline (2026-07-06, post-M2.5) — append-only

The M2.5 alignment landed: reference builder on the fresh-identity convention
(spec §1.1) and the learner eps-merge reverted to the §3.2 singleton rule.
Measured M2 outcomes (`tests.sosl.paper_examples`
and `reference_vs_learner`), still **no saturation**:

| language | reference | learned | acceptor | vs reference | learner stats |
|---|---|---|---|---|---|
| GF a       | 3 | 3 | correct | **byte-equal** | member 6,  equiv 1, cex 0 |
| GF(aa)     | 6 | 6 | correct | **byte-equal** | member 63, equiv 4, cex 3 |
| Even       | 5 | 5 | correct | **byte-equal** | member 40, equiv 3, cex 2 |
| EvenBlocks | 8 | 8 | correct | **byte-equal** | member 80, equiv 4, cex 3 |

Headline: **all four are byte-equal at M2, without saturation.** Every stall
turned out transient — the equivalence queries broke each one and the stem
chains split the coarse classes back to canonical. This meets the optimistic
end of the predictions above (§"What to expect after M2.5"): `Even` and
`GF a` as predicted byte-equal; `GF(aa)` landed byte-equal rather than the
hedged "coarser transient stall"; `EvenBlocks` byte-equal (8) via the one
extra split (the class of `aa`), exactly as the correction section foretold.

Convention checks, all confirmed: `[eps] = {eps}` in every stall dump (the
fresh identity is a permanent singleton, no non-empty word merges in);
`EvenBlocks` is 8 on both legs; `GF a` is 3 on both legs (the old `GF a → 2`
eps-merge bug is gone).

Nothing here needs M3 to be correct at M2 — but it does mean the M3 saturation
work starts from an already-canonical M2 baseline on the triptych, so M3's job
narrows to the languages whose stalls are *not* transient (the `F(a ∧ Xa)`
permanence specimen, spec §8).

## Q3 step 1 reply — `F(a ∧ Xa)` M2 fixpoint (2026-07-06)

At M2 (no saturation, default equivalence mode) the learner and the reference
agree byte-equal on `F(a ∧ Xa)`. The fixpoint, for the theory thread:

    SOS v1
    ap: a
    classes: 6
    0 eps
    1 !a
    2 a
    3 !a;a
    4 a;!a
    5 a;a
    letters: !a->1 a->2
    mult:
    0: 0 1 2 3 4 5
    1: 1 1 3 3 1 5
    2: 2 4 5 2 5 5
    3: 3 1 5 3 5 5
    4: 4 4 2 2 4 5
    5: 5 5 5 5 5 5
    accept:
    5 1
    5 3
    5 4
    5 5

- acceptor-correct on the exhaustive 210-lasso check (`|stem|,|loop| <= 3`);
- exported invariant, hypothesis, and teacher agree on every checked lasso;
- cost: 62 membership, 4 equivalence, 3 counterexamples.

The `F(a ∧ Xa)` permanence decision under `--no-saturation --eq-mode exact` is
the M3 item (exact mode not yet built).
