# Notation conventions (editors' note — not paper text)

The paper adopts [SωS26]'s notation wholesale and adds only the learner's own
objects. This file is the contract; every part obeys it.

## From [SωS26] (recalled in §2.2, used everywhere)

| Symbol | Meaning |
|---|---|
| `𝓘 = ⟨𝒮, P⟩` | invariant: stamp + pair set of accepting linked pairs |
| `𝒮 : Σ⁺ → 𝒞` | stamp — surjective semigroup morphism onto the finite class set `𝒞` |
| `(𝒞, λ, ·)` | finite presentation of a stamp: classes, letter map `λ = 𝒮\|_Σ`, table |
| `[u]` | the class of the word `u` (a name, not a set) |
| `[ε]`, `M = 𝒞 ∪ {[ε]}` | fresh adjoined identity; monoid completion |
| `c^π` | idempotent power (exponent `π` fixed once per stamp) |
| `(s, e)`, `P` | linked pair (`e² = e`, `s·e = s`); pair set |
| `≈_L`, `𝒮_L`, `𝒞_L` | Arnold's congruence; syntactic stamp; its class set |
| `𝓘(L) = ⟨𝒮_L, P(L)⟩` | the syntactic invariant — the learner's target |
| `Λ(d, f)`, `Ω(d)` | membership tests ([SωS26, Def 4.3]) |
| `N` | class count of the target, **identity included**: `N = \|𝒞_L\| + 1`, the serialized `classes:` line |

Pinpoints cited: Theorem I (canonicity/byte equality), Theorem III (the
construction, teacher-side only), Lemma 4.1 (rotation), Lemma 4.2 (tests
characterize `≈_L`), Lemma 4.3 (left invariance), Def 4.1 (denoting),
Def 4.2 (well-formed), Prop 4.1 (one lasso one verdict), Cor 4.2 (denoting
invariants live exactly at refinements; forced pair set), Thm 6.1
(aperiodicity read-off), §6.2 (serialization). **Theorem II is never
load-bearing** — the learner's proofs consume Theorem I and Cor 4.2 only.

## The learner's own objects (defined in §3)

| Symbol | Meaning |
|---|---|
| `T = (R, E_lin, E_ω)` | observation table: rows, linear columns `(x, y, t)`, ω-columns `(x, y)` |
| `≡_T` | table equivalence of rows |
| `𝒞_T` | the table's class set (kept apart from the target's `𝒞_L`) |
| `ψ`, `step`, `fold(d, u)` | letterwise fold; class transition; fold from an arbitrary start |
| `rep(c)`, `w_c` | shortlex-least row of class `c` |
| `𝓗 = (𝒞_T, λ, step, P)` | hypothesis in Cayley form (no products mid-learning) |
| exported table | `c·c' := fold(c, rep(c'))` — only at export (§5) |

## House rules

- **Algebra vs representation.** The syntactic ω-semigroup is the abstract
  algebra (Arnold's quotient with its acceptance); `𝓘(L)` is its *material
  representation* — never conflate. The learner's target is `𝓘(L)`;
  byte-equality claims are about the representation, isomorphism claims about
  the algebra.
- Shortlex uses the serialization's letter order: valuation bitvectors
  ascending, `!a < a`.
- The exported product is written `c·c'`; the letter `M` is reserved for the
  monoid completion, never for a multiplication table.
- Local numbering: Lemmas 4.1/4.2 (harvest), Theorem 4.3, Prop 4.4 (stall),
  Lemma 4.5 (sweep), Prop 4.6, Cor 4.7, Lemma 4.8; Theorem 5.1, Lemma 5.2,
  Theorem 5.3, Props 5.4–5.5. Collisions with [SωS26]'s internal numbers are
  fine — external cites always carry the key.
