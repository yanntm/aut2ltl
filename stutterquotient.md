# `stutterquotient`: A Stutter-Quotienting Leaf Translator for Deterministic SCCs

## Description

`stutterquotient` is a leaf translator that extends the deterministic L-partition approach of `partscc`/`daisystardet` to automata whose L-partition fails **solely due to universal stuttering letters**—letters that act as self-loops on every state of the SCC.

The insight is simple: if a letter does not change the state, its occurrences can be ignored when determining the phase sequence. The language is stutter-invariant (equiv. `X`-free LTL), so deleting or inserting such letters does not affect membership. After quotienting out these universal stuttering letters, the remaining L-partition often becomes deterministic, enabling a compact, exact read-off where the general fallback would produce an exponentially larger formula.

## Preconditions

The translator applies to an SCC `C` of a deterministic transition-based generalized Büchi automaton (TGBA) satisfying:

1.  **The SCC is a single strongly connected component** (the entire automaton for this leaf translator).
2.  **The SCC is stutter-invariant**: `spot::is_stutter_invariant(aut)` returns `true`.
3.  **The L-partition after stutter-quotienting is deterministic** (see Definition 2 below).

If these conditions hold, `stutterquotient` produces an exact LTL formula for the automaton. Otherwise, it returns `⊥`, deferring to `daisystar` or the general cascade.

## Key Concepts

### Deterministic L-Partition (Standard)

For each state `s`, define:
```
L(s) = { σ ∈ Σ | ∃ t. δ(t, σ) = s }
```
i.e., the set of letters that can enter `s` from some predecessor.

The family `{ L(s) }` is a **deterministic partition** if:
- For all `s ≠ t`, `L(s) ∩ L(t) = ∅`
- `⋃_s L(s) = Σ` (it is a partition of the alphabet)

This partition is the pre-condition for `partscc` and `daisystardet`.

### Universal Stuttering Letters

A letter `τ ∈ Σ` is a **universal stuttering letter** (or **stutter letter**) for SCC `C` if:
```
∀ s ∈ C . δ(s, τ) = s
```
That is, `τ` is a self-loop on every state of the SCC. Let:
```
Σ_τ = { τ | ∀ s ∈ C . δ(s, τ) = s }
```

### Quotient L-Partition

Remove the stutter letters from the entry labels:
```
L_τ(s) = L(s) \ Σ_τ
```

The quotient L-partition is **deterministic** if `{ L_τ(s) }` forms a partition of `Σ \ Σ_τ`.

## Algorithm

Given an SCC `C` with initial state `q₀` and acceptance sets `{F₁, ..., Fₖ}`:

**Step 1: Compute universal stutter letters.**
```
Σ_τ = { σ | ∀ s ∈ C . δ(s, σ) = s }
```

If `Σ_τ = ∅` and the standard L-partition is already deterministic, defer to `partscc`/`daisystardet`.

**Step 2: Compute quotient entry labels.**
```
L_τ(s) = { σ | σ ∉ Σ_τ and ∃ t ∈ C . δ(t, σ) = s }
```

If `{ L_τ(s) }` is not a partition of `Σ \ Σ_τ`, return `⊥`.

**Step 3: Build the quotient transition law on the reduced alphabet.**
For each state `s`, define:
```
O(s) = { σ | σ ∉ Σ_τ and δ(q₀, σ) = s }
        ∪ { τ | τ ∈ Σ_τ }
```
In practice, `O(s)` is the set of letters that can **start** from state `s` (including stutter letters).

The quotient transition law is:
```
law = ⋀_{s ∈ C} ( L_τ(s) → X O(s) )
```
This says: if the current letter is in `L_τ(s)`, then the next letter must be startable from `s`.

**Step 4: Determine the regime (staying vs. leaving).**

Let `Exit` be the set of quotient letters that leave the SCC:
```
Exit = { σ | σ ∉ Σ_τ and ∃ s ∈ C . δ(s, σ) ∉ C }
```

Let `Fair` be the acceptance sets for runs that stay in the SCC forever (relative to the quotient):
```
Fair = { F_i | ∃ s ∈ F_i ∩ C }
```

**Step 5: Construct the formula.**

The generalized deterministic SCC formula is:
```
O(q₀) ∧ ( (law U (Exit ∧ φ_child)) ∨ ( G(law) ∧ ⋀_{F ∈ Fair} GF( ⋁_{s ∈ F} L_τ(s) ) ) )
```

Where:
- `φ_child` is the formula of the target SCC reached on exit (provided by the assembler).
- If `Exit = ∅` (terminal SCC), the `U`-branch is false, yielding the `partscc` formula.
- If `Fair = ∅` (rejecting SCC), the `G`-branch is false, yielding the `daisystardet` formula.
- If both are non-empty (accepting with exits), the `∨` captures both behaviors.

**Step 6: Return the formula.**

## Correctness Argument

**Lemma 1 (Stutter deletion preserves acceptance):**  
Let `w ∈ Σ^ω` and let `w'` be obtained by deleting all occurrences of letters from `Σ_τ`. Because every `τ ∈ Σ_τ` is a self-loop on every state, the sequence of states visited by the automaton on `w` and `w'` differs only in the number of consecutive repetitions of the same state. Since the language is stutter-invariant (precondition), `w ∈ L(aut)` iff `w' ∈ L(aut)`.

**Lemma 2 (Quotient law is exact):**  
On the reduced alphabet `Σ \ Σ_τ`, the entry labels `L_τ(s)` form a deterministic partition. Therefore, the transition law:
```
G( ⋀_s ( L_τ(s) → X O(s) ) )
```
is an exact characterisation of the phase evolution on the reduced alphabet.

**Theorem (Correctness of `stutterquotient`):**  
Let `aut` be a deterministic TGBA satisfying the preconditions. Let `φ` be the formula produced by Step 5. Then `L(φ) = L(aut)`.

*Proof sketch:* By Lemma 1, it suffices to show the formula is exact on the reduced alphabet. Lemma 2 gives the exact transition law. The `U` branch captures exactly the runs that eventually leave the SCC, and the `G` branch captures exactly the runs that stay forever and satisfy the fairness condition. The `∨` is exhaustive, and the two branches are mutually exclusive on the reduced alphabet. The `O(q₀)` anchor ensures the first letter is valid. Thus the formula is semantically equivalent to the automaton. ∎

## Complexity

- **Stutter letter computation:** `O(|C| * |Σ|)` time.
- **L-partition construction:** `O(|C| * |Σ|)` time.
- **Formula size:** Linear in `|C|` and `|Σ|` (after BDD simplification), avoiding the exponential blowup of the general cascade.

## Discussion

### Relationship to `partscc` and `daisystardet`

`stutterquotient` generalizes both translators by treating stutter letters as phase-invisible. If `Σ_τ = ∅`, the quotient reduces to the standard L-partition, and the algorithm specializes to the existing deterministic cases. Thus `stutterquotient` is a strict superset of `partscc`/`daisystardet` for stutter-invariant languages.

### When It Fails

The translator returns `⊥` if:
- The SCC is not stutter-invariant (Spot's `is_stutter_invariant` returns `false`).
- The quotient L-partition remains non-deterministic.
- The SCC is not a single SCC (handled by the assembler).

In such cases, the tool falls back to `daisystar` or the general cascade.

### Practical Impact

Many real-world LTL specifications are stutter-invariant (e.g., response, fairness, persistence). The automata for these formulas often have universal stutter letters that break the deterministic L-partition. `stutterquotient` recovers the exact compact read-off, significantly reducing formula size and translation time for this common class of properties.

## References & Comments

- The stutter-invariance check uses `spot::is_stutter_invariant(aut)` (Spot library).
- The quotienting idea was developed in collaboration with DeepSeek (2025-2026). The key insight is that universal stuttering letters are phase-invisible and can be safely projected out, reducing the problem to the deterministic L-partition case.

---

*This document describes a new leaf translator proposed for integration into `aut2ltl`. It fills the gap between the deterministic fragment (`partscc`/`daisystardet`) and the general fallback, providing exact, compact LTL reconstruction for a practically significant class of stutter-invariant automata.*
