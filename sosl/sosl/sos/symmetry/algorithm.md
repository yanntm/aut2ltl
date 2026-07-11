# The symmetry checks — algorithm and conventions

Normative math: the symmetry paper §3 (Thm 3.1). This file fixes the
encodings and states the algorithms the code transcribes.

## Conventions

**Minterms vs masks.** A letter is a minterm over the invariant's AP
list, stored as a bitmask in the `sosl.sos.alphabet` convention: AP
index `i` (in the invariant's stored, canonically sorted order)
occupies mask bit `n−1−i` — first proposition on the most significant
bit. All `SignedPerm` components are indexed by AP *index*; the
conversion to mask bits happens only inside the action.

**The action.** `σ = (perm, flip)` sends the minterm `m` to the
minterm `σ(m)` with, for every AP index `i`:

    (σ·m)[perm[i]] = m[i] XOR flip[i]

i.e. the truth value of AP `i`, possibly negated, is moved to
position `perm[i]`. On words and lassos the action is letterwise.

**Composition.** `compose(σ, τ) = σ ∘ τ` applies `τ` first:

    perm[i] = σ.perm[τ.perm[i]]
    flip[i] = τ.flip[i] XOR σ.flip[τ.perm[i]]

The inverse satisfies `perm⁻¹[perm[i]] = i` and
`flip⁻¹[perm[i]] = flip[i]`. These equations (plus the pin
`swap_ab ∘ flip_a = flip_b ∘ swap_ab` at `n = 2`) are gate-enforced;
they, not prose, define the convention.

## `apply_perm(inv, σ) → Invariant`

1. Assert `len(σ.perm) = |AP|` (a mismatch is a caller error).
2. Rewire the letter map: `λ'(m) := λ(σ(m))` — the free inverse
   substitution of the calculus along `σ` as a letter function. Same
   classes, same multiplication, same accepting pairs; the result
   presents `𝓘(σ⁻¹L)` (which of `σ`/`σ⁻¹` is immaterial to every
   check below; the membership contract
   `member(apply_perm(inv,σ), u·v^ω) = member(inv, σ(u)·σ(v)^ω)`
   is gate-pinned).
3. `reduce`. Since `σ` permutes `Σ`, `λ'(Σ) = λ(Σ)` as a set: the
   generators are unchanged, no re-quotient can occur, the reduce is
   keying only. The class count is asserted preserved — a merge
   convicts the input (not syntactic) or `reduce`, never the theory.

Cost: `O(2^n)` for the rewire plus one keying pass.

## The checks

- `is_symmetry(inv, σ)` — byte equality of the canonical
  serializations of `apply_perm(inv, σ)` and `inv`. Sound and
  complete by the canonical-form theorem: byte-equal `.sos` iff equal
  languages, and `σL = L ⟺ σ⁻¹L = L`. Requires `inv` canonical
  (the corpus and fixtures are).
- `is_antisymmetry(inv, σ)` — same against `inv.complement()` (the
  free `P`-flip; complementation preserves canonical keying because
  keys depend only on the congruence, which `L` and `L^c` share).
  Never an automaton-level complement.
- `in_kernel(inv, σ)` — the fiber read-off `∀m: λ(σ(m)) = λ(m)`.
  Sufficient only (`in_kernel ⟹ is_symmetry`, the kernel law): a
  symmetry may permute the fibers of `λ` nontrivially. It runs
  *beside* the full check as a law, never instead of it.
- `inert_aps(inv)` — `{i : in_kernel(inv, polarity_flip(n, i))}`:
  propositions the language is semantically blind to, visible as
  polarity flips inside the kernel.
- `anti_possible(inv)` — the pair-count obstruction: an
  anti-symmetry bijects `P` onto `linked ∖ P`, so
  `2·|P| ≠ |linked|` refutes every anti-candidate at once. A law
  (`is_antisymmetry ⟹ anti_possible`) and the only sanctioned
  fast path: when False the anti checks may be skipped wholesale.

## Enumeration

`generators_b_ap(n)` — the `n(n−1)/2` transpositions and `n` flips,
in deterministic order. `all_b_ap(n)` — all `2^n · n!` elements,
guarded to `n ≤ 3` (48 elements); the larger-`n` policy belongs to
the group milestone and the guard is not to be lifted.
