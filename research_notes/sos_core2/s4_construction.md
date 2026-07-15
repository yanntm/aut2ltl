## 4. The construction: from an automaton to `𝓘(L)`

*Placeholder — port the legacy `../sos_core.md` §4 prose (it is fully drafted
there), applying:*

- the **enriched stamp**: `w ↦ ⟨w⟩` restricted to `Σ⁺` is a surjective
  semigroup morphism onto `EM₊(D)`; `⟨ε⟩` is the same free completion on the
  automaton side.
- notation conventions (`notation.md`); keys become `u_s, u_e`
  (shortlex-least *nonempty* members — total by surjectivity).
- key-testing in Definition 4.10 explicitly labeled the *computation* of `P`,
  correctness delegated to canonicity (Theorem 3.10).
- Theorem 4.11 restated at canonicity's altitude: `⟨u⟩ ∼ ⟨v⟩ ⟺ u ≈_L v`,
  `𝓘(D)` and `𝓘(L)` equal up to the unique isomorphism commuting with the
  stamps — the identity under shortlex naming.
