## 5. Complexity

Two costs must be kept apart: building the invariant from an automaton, and
using it once built.

**Building.** The construction is dominated by the size of the enriched
semigroup: an enriched element is a vector of `|Q|` slots over the local
domain `Q × 2^Γ` (Definition 4.2), so

```
    |EM₊(D)| ≤ (|Q|·2^{|Γ|})^{|Q|},
```

and the `|Q|` in the exponent is the source of the explosion. That a wall
sits somewhere is a mathematical necessity, not an engineering apology:
deciding aperiodicity of a regular ω-language — the LTL read-off of §6 — is
PSPACE-complete, with hardness transferred from finite-word minimal-DFA
aperiodicity [CH91] and the ω upper bound from [DG08, Prop. 12.3]; the
surrounding classifications are no cheaper. Everything around the enriched
semigroup is benign by contrast: each generator acts slot-wise; the loop
verdicts cost one functional-graph walk per element; the residual partition
of the states and the congruence on the elements are two Moore refinements
over the closed table, polynomial in `|EM₊(D)|` and `|Q|`; and `P(D)` is one
lasso test per linked pair. The cost is entirely the size of
`EM₊(D)`, and that size is intrinsic to the problem, not to the construction.

**Using.** Once built, the sizes change meaning: `|𝒞|` is a function of `L`
alone (Theorem 4.11) — the intrinsic complexity of the language, the
ω-analogue of the syntactic monoid's size — where `|Q|` and `|EM₊(D)|` were
functions of a presentation. The serialized invariant is `O(|𝒞|²)` table
entries plus a pair set `P ⊆ 𝒞 × 𝒞`, and every operation of §6 is a scan of
that table. The presentation debt — determinization [Saf88], then `EM₊(D)` —
is paid once, at entry; nothing downstream ever revisits the automaton.

**Symbolic prospects.** On a more optimistic note, every object and operation
here is BDD-friendly and the redundancy is high, so a symbolic approach is
likely to alleviate much of this inherent complexity. The ingredients are all
Boolean — the alphabet `2^AP`, the mark sets over `Γ`, the positive-Boolean
`Acc` — and every step is a set operation, not an arithmetic one: closing
`EM₊(D)` under composition, the two right relations of §4.3, and the
partition refinement of §4.4 are all images, fixpoints, and quotients over
sets, native to decision diagrams.
