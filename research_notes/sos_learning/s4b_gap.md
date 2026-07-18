### 4.2 The gap: acceptance-correct is not algebra-correct

The harvest reacts to *membership* disagreements — and membership's error signal
is structurally one-sided. Predictions fold the **literal** words of the queried
lasso; they never consult the class of a row *embedded under a left context*. So
if two rows `u, v` with `u ≉_L v` are merged, and no harvested column happens to carry
the separating prefix `x`, nothing observable ever goes wrong: every prediction
is computed from literal prefixes, every lasso verdict can be correct, the
equivalence oracle assents — and the learner stops with a table **coarser than
the syntactic congruence**. The fixpoint object is then a
right-congruence-flavored acceptor: an FDFA in algebraic clothing. This is the obstruction of
[AF21] reborn one level up — the table's *columns* are two-sided, but its *error
signal* is not — and it is, we believe, the true reason no observation-table
route to the syntactic algebra existed: the missing ingredient is not a cleverer
column format, but a repair that lives outside the counterexample loop. Neither running specimen realizes the stall *permanently* — in
both, the wrong merge eventually poisons some prediction, and a later
equivalence query catches it (a transient stall). But the permanent stall is
not a hypothetical, and it does not take an exotic language: an exhaustive
census of the smallest automaton shapes (nondeterministic transition-based
Büchi over one atomic proposition, §6.1; at one state every fixpoint is
canonical, so two states are the smallest possible) finds it already at
`a → Xa`.

**Proposition 4.4 (the stall, realized).** Let `L = L(a → Xa)` — if the first
letter is `a`, so is the second — over `Σ = {a, !a}`. The saturation-free
learner reaches, before its first equivalence query, a closed and consistent
four-class table — `[ε]`, the singleton `[a]`, a committed-in class
`C₁ = !a·Σ* ∪ aa·Σ*`, a committed-out class `C₀ = a!a·Σ*` — whose hypothesis
language is exactly `L`. Every equivalence oracle therefore assents, bounded
or exact; the fixpoint is strictly coarser than the syntactic congruence —
four classes against `N = 5`: the two accepting idempotents `[!a]` and `[aa]`,
right-indistinguishable but separated by the left context `x = a`, stay merged
inside `C₁` — and the export is broken as an algebra: its multiplication table
is not associative, and its membership read-off is not even
presentation-invariant — it accepts `a^ω` written as the lasso `(ε, a)` and
rejects the same ω-word written `(a, a)`.

*Proof.* Membership of an ω-word depends only on its first two letters, so on
lassos it is a function of the *commitment* of the literal prefix: every word
of `C₁` begins a member, every word of `C₀` begins a non-member, and the only
uncommitted non-empty word is the single letter `a` — the class `[a]` is a
singleton. The four-class partition is closed and consistent (`C₁` and `C₀`
absorb both letters; `a` steps into one or the other), and the learner
provably lands on it: every pre-equivalence column has prefix `x = ε` — the
initial column does, and consistency mints preserve the prefix
(Definition 3.2) — and an `x = ε` context evaluates any word of length ≥ 2 by
its commitment alone, so no such column can split `C₁` or `C₀`; conversely
the inconsistency of `a` against `!a` at `(ε, ε)` (their `!a`-successors'
bits differ) forces the mint `(ε, !a)` that isolates `[a]`. Now take any
lasso `w·z^ω` with predicting pair
`s = ψ(w·z^k)`, `e = ψ(z^k)`. The stem `w·z^k` can never be the word `a`:
either it is longer than one letter, or `w = ε` and `z = a` — and there
`k = 1` fails the stabilization test (`ψ(a) = [a]` but `ψ(aa) = C₁`), so
normalization takes `k = 2` and the stem is `aa`. Hence `s ∈ {C₁, C₀}`
always, and the prediction — the teacher's bit on `w_s·(w_e)^ω`, with
`w_{C₁} = !a` and `w_{C₀} = a!a` — equals the commitment of `s`, which equals
the truth of the queried lasso. No counterexample exists. ∎

The census's second specimen, `a ∧ XG¬a` — the language of the single ω-word
`a·(!a)^ω` — stalls the same way one step deeper, and the same argument
proves it permanent: the canonical `[!a·a]` stays
merged into `[!a]`, again separated only by `x = a`. There the alive class
`{a·!a^m}` squares to the dead class, so the loop idempotent `e` is always
dead, and the stem class `s` stays alive only when the literal `w·z^k` is of
the form `a·!a^m` — which forces a pure-`!a` loop, on which the representative
lasso `a·(!a)^ω` answers correctly; any stray `a` in the loop drags `s` to
dead through the literal fold before the faulty merge can matter — every
predicting pair again answers with the truth, and no counterexample exists.
Two exhibits, one mechanism, and both minimal:

| specimen | `N` | stalled fixpoint | merged pair | separated by | export error (read as `(a, a)`) |
|---|:--:|---|---|:--:|---|
| `a → Xa` | 5 | **4 — zero counterexamples** | `[!a] = [aa]`, both accepting idempotents | `x = a` only | rejects `a^ω` |
| `a ∧ XG¬a` | 4 | 3 — one counterexample | `[!a] = [!a·a]` | `x = a` only | accepts `a^ω` |

"One class short" undersells the defect. Export the stalled fixpoint of
`a → Xa` by §5's recipe, `c·c' := fold(c, rep(c'))`, next to the
canonical algebra of the language:

```
    canonical table  (5 classes)           stalled export  (4 classes)
    ·      ε    !a   a    a!a  aa          ·      ε    !a   a    a!a
    ε      ε    !a   a    a!a  aa          ε      ε    !a   a    a!a
    !a     !a   !a   !a   !a   !a          !a     !a   !a   !a   !a
    a      a    a!a  aa   aa   aa          a      a    a!a  !a   !a
    a!a    a!a  a!a  a!a  a!a  a!a         a!a    a!a  a!a  a!a  a!a
    aa     aa   aa   aa   aa   aa
```

(cells name classes by their keys; in the stalled table `[!a]` is the merged
`C₁` and `[a!a]` is `C₀`). The stalled table is **not associative**:
`([a]·[a])·[a] = [!a]·[a] = [!a]`, but `[a]·([a]·[a]) = [a]·[!a] = [a!a]`.
The first bracketing folds the literal word `aaa` and lands where it should;
the second substitutes the merged class's representative `!a` into the middle
of the product — and substituting a representative mid-product is exactly what
a merely-right congruence does not license. The hypothesis is immune, because
it folds the literal letters of the queried lasso and never substitutes — that
is how one partition carries a correct acceptor and a broken algebra at once.
Broken means broken downstream: on a non-associative table the linked-pair
reduction is bracketing-dependent, so the export does not even define a
*language* — its verdict depends on how the lasso is written. On
[SωS26]'s ladder the defect sits below the bottom rung: not associative, the
export is not a stamp, hence not an invariant that could be well-formed or
not [SωS26, Defs 3.1, 4.2] — and its read-off visibly breaks the one law an
invariant's semantics must obey, one lasso one verdict [SωS26, Prop 4.1].
Read `a^ω` as
the lasso `(ε, a)`: `e = [a]² = [!a]`, `s = [ε]·e = [!a]`, the pair
`([!a],[!a])` — accept, agreeing with the teacher. Read the same ω-word as
`(a, a)`: the stem class now multiplies the merged idempotent,
`s = [a]·[!a] = [a!a]`, pair `([a!a],[!a])` — reject. The exhibit table
reports this second reading, the shortlex-least divergence from the teacher.
On the second specimen the same defect points the other way: the canonical
algebra of `a ∧ XG¬a` keeps `[a]·[a] = [!a·a]` as its own non-accepting
idempotent, the stalled export merges it into `[!a]`, and the `(a, a)`
reading of `a^ω` lands on the accepting pair `([a], [!a])` — the bit of
`a·(!a)^ω`, the one word the language contains — while its `(ε, a)` reading
agrees with the teacher: one ω-word, two verdicts, no language.

Both languages are LTL-definable and utterly plain: the flagship stall is a
two-letter implication, on which the saturation-free learner converges and is
certified by a *complete* equivalence oracle. (Mechanically confirmed: the exact oracle of §2.3
certifies both stalled fixpoints — these permanence proofs turn those two runs
into fixtures for the oracle itself, a counterexample there being an oracle bug —
and with saturation on, both reach their canonical algebras, byte-equal to
the reference.) Canonicity is therefore beyond counterexample-guided
refinement: the CEGAR loop that carries L\* — and every ω-learner since — has
no error signal left to react to, and what breaks the stall must be a query
the learner poses on its own initiative. The repair below is that query — not
an optimization but the difference between the algebra and an acceptor. (§5
closes the account: by Theorem 5.3 *every* exactly-certified stall is like
these two — its partition is never a congruence, so there is no algebra on
its classes to mis-export.)
