# sosl.sos.symmetry — symmetries of a language, read off its invariant

Signed permutations of the atomic propositions act on the alphabet
`Σ = 2^AP`; this package decides, on the canonical invariant
`𝓘(L) = (𝒞, λ, M, P)` and exactly, whether a candidate `σ` is a
symmetry (`σ(L) = L`) or an anti-symmetry (`σ(L) = L^c`), and reads
off the kernel-level facts (fiber-preserving candidates, inert
propositions, the pair-count obstruction to anti-symmetries).

Every check is product-free: one `O(2^n)` rewire of the letter map,
one keying-only `reduce`, one byte comparison of the canonical `.sos`
serializations. No automaton, no language query, no alignment.

## Services

- **`SignedPerm`** — an element of the signed permutation group
  `B_n = (Z/2)^n ⋊ S_n`: a position permutation plus per-proposition
  polarity flips, acting on letters, words and lassos. Composition,
  inverse, and the standard generators (transpositions, flips).
- **`apply_perm`** — the free inverse substitution of the calculus
  along `σ`, reduced back to canonical form; presents `𝓘(σ⁻¹L)` on
  the *same* class set (the class count is asserted unchanged).
- **The checks** — `is_symmetry` / `is_antisymmetry` by canonical-key
  byte equality; `in_kernel` (the sufficient fiber read-off
  `λ∘σ = λ`); `inert_aps` (propositions whose polarity flip is in the
  kernel); `anti_possible` (the pair-count obstruction
  `2·|P| = |linked|`, a licence to skip all anti checks when False).
- **Candidate enumeration** — `generators_b_ap(n)` (all
  transpositions and flips) and `all_b_ap(n)` (the full group,
  guarded to `n ≤ 3`).
- **Relational read-offs** (`relations`) — which factor rewritings
  `u ↔ v` the language tolerates, all instances of the one block
  equality `[u] = [v]` (Thm 4.2): `is_closed`; `invisible_letters`
  (`[c] = 1`, padding letters); `stutter_rung` / `ladder_entry` (the
  `k`-block stutter ladder, `[v] = [vv]`); `independence` /
  `independence_letters` (the tolerated commutation relation `Î_L`,
  `[cd] = [dc]`, Thm 4.4).

Commissioned but not yet built (see the spec): the full group
computation with asymmetry witnesses and symmetrization (SY2,
`stabilizer.py`), the group spectrum and the LTL hull/kernel (SY4,
`spectrum.py` / `reflect.py`).

## Orientation map

    sigma       SignedPerm and its action; apply_perm; is_symmetry /
                is_antisymmetry / in_kernel / inert_aps /
                anti_possible; generator and group enumeration
    relations   the block-substitution read-offs: is_closed,
                invisible_letters, stutter_rung / ladder_entry,
                independence / independence_letters

## Layering

Imports `sosl.sos` (objects, io), `sosl.sos.calculus` (Table, reduce,
surgery, decide) and — for the later milestones — `sosl.sos.classify`;
NOTHING else in the repo. Never `sosl.learn`, `sosl.teacher`,
`sosl.experiment`, `tests.*`. Acceptance gates live in
`sosl/tests/symmetry/` and may import what they need.

## See also

`algorithm.md` — conventions (the AP-index/mask-bit correspondence,
the action and composition equations) and the check algorithms with
their correctness facts. Specification of record:
`research_notes/sos_symmetry_spec.md`; normative math:
`research_notes/sos_symmetry.md` (the symmetry paper, §3).
