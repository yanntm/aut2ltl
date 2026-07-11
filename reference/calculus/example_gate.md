date: 2026-07-11
git: 1a0ec1d44
seed: n/a (deterministic, no sampling)
corpus: n/a (the example is built from its LTL formula)

# E-CAL-EX — the running example, mechanically

Every value the paper hand-computes for `a*·b^ω` (§2.3), its alignment with
`GF a` (§3.3) and its hulls and degree (§6) checked against a construction the
calculus never sees. Gate: `sosl/tests/calculus/example_gate.py` (one shot, no
argv); reproduce with

    cd sosl && python3 -m tests.calculus.example_gate

## Provenance of the answer key

The encoding is the paper's: one AP `p`, letter `a = ¬p`, letter `b = p`, so
`a*·b^ω = (¬p) U (G p)` and `GF a = GF ¬p`.

- **Both invariants come from Spot**, via `sos.build.reference_of_ltl`
  (Spot determinizes the formula, `core.quotient` canonicalizes). The calculus
  reads off an algebra it did not build. Both are already reduced: the dump of
  `reduce(table, P)` is byte-identical to the dump of the construction.
- **The multiplication table is generated, not transcribed**: the gate predicts
  each of the 25 cells from the word model `{ε, a⁺, b⁺, a⁺b⁺, dead}` and
  compares. Classes are located by *role* (identity, the two letter classes,
  `A·B`, `B·A`), never by key string.
- **The Wagner coordinates are checked twice**: against `sos.classify` (an
  obligation read-off independent of `calculus.surgery`'s) and against the
  committed `.cat` sidecar of the corpus row that holds this language —
  `2state1ap1acc_16898`, the answer key the calculus never sees.

## The nine checks — all green

| # | claim (paper) | expected | machine |
|---|---|---|---|
| 1 | `𝓘(a*·b^ω)` (§2.3) | 5 classes; `A²=A`, `B²=B`, `A·B=C`, `C·B=C`, `B·A=C·A=C²=D`, `D` absorbing; 6 linked pairs; `P = {(B,B), (C,B)}` | ✅ full table = word model |
| 2 | stutter read-off (§2.3) | true (both letter classes idempotent) | ✅ |
| 3 | rootings (§2.3) | `P_A = P` (`a⁻¹L = L`); `P_B = {(B,B)}` (`= {b^ω}`) | ✅ |
| 4 | hulls (§6) | `Live = 𝒞 \ {D}`; closure adds exactly `(A,A)`; interior `= ∅`; A–S liveness factor `= P ∪ {(D,A),(D,B),(D,D)}` | ✅ (+ `closure ∩ liveness = P`) |
| 5 | degree (§6) | obligation, `(n⁺, n⁻) = (1, 2)` | ✅ `classify` coords `(m⁺ m⁻ n⁺ n⁻) = (0, 0, 1, 2)`, and the corpus row `2state1ap1acc_16898`'s `.cat` sidecar, both agree |
| 6 | `𝓘(GF a)` (§3.3) | 3 classes; `P₂ = {(α, α)}`, all and only the `a`-loop cells accept | ✅ |
| 7 | alignment (§3.3) | 5 nodes of `5 × 3`, ratio `5/15 = 0.333` | ✅ |
| 8 | intersection | EMPTY, no witness | ✅ |
| 9 | inclusion | `a*·b^ω ⊆ FG ¬a` HOLDS; reverse FAILS on `ba·b^ω` | ✅ witness verbatim: `included cell=(4,2) stem=p;!p loop=p bit=1`, i.e. `ba·(b)^ω` — theory's discipline-order prediction, on the nose |

The counterexample replays both ways: `ba·b^ω ∈ FG ¬a` and `∉ a*·b^ω`.

## Class map (as the tool numbers them)

    class  key      role
    0      ε        identity
    1      ¬p       A = a⁺
    2      p        B = b⁺
    3      ¬p;p     C = a⁺b⁺        (= A·B)
    4      p;¬p     D = dead        (= B·A, absorbing)

`P = {(2,2), (3,2)}`; the six linked pairs are `(A,A) (D,A) (B,B) (C,B) (D,B)
(D,D)`.

## Notes

- **The corpus row is `2state1ap1acc_16898`** — the smallest shape that emits
  the language (2 states, 1 AP, 1 acceptance set), `.cat` reading
  `ltl: yes | stutter: invariant | phi: 2,sigma | coords: 0 0 1 2 |
  class: properly Σ₂`. Looking it up requires the corpus's *own* identity, and
  two traps sit on the way (both hit, both now encoded in `corpus_row`): the
  `flat_canon` files are not raw `𝓘` dumps but the **`B_k` orbit-min** of the
  invariant (genaut's `canon_key`: `remove_free_aps` → orbit representative →
  dump), and those canonical bytes carry the **AP's name**, which the corpus
  spells `a` and the paper spells `p`. Compare raw dumps, or compare across
  namings, and a present language reads as absent.
- **Finding F-EX1** (report): the hand-built reference that
  `tests/calculus/obligation_oracle.py` opened with carried **4** classes — it
  merged `A·B` into `B` and so accepted `(ab)^ω ∉ a*·b^ω`. The paper's 5-class
  table is right and the 4-class one was not an invariant of this language.
  Corrected in place; the degree read-off is `(1, 2)` either way, so no CAL5
  corpus number moves.
