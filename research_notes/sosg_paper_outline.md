# Paper outline — the Syntactic ω-Semigroup, constructed

*Structural blueprint. Not prose. Fixes the thesis, the arc, the red threads, the
theorems to prove, and what each reference anchors. The "fill-in" pass writes
against this.*

---

## The reframe (thesis)

**Old framing (draft 1):** a tool that decides LTL-definability and synthesizes
LTL. Tool-centric, application-first.

**New framing:** the paper's object is the **syntactic ω-semigroup `S(L)`** — the
canonical algebra of an ω-regular language — which we **construct from an
automaton for the first time**. Everything else (deciding LTL, refuting it with a
witness, synthesizing LTL, a canonical automaton, a language-equality hash) are
*exports* of having the object. The contribution is the object and the two keys
that unlock its construction.

**The "no tool" test (the premise the user set):** remove every mention of an
implementation. Is there still a paper? Yes — the paper is (i) the object, (ii)
the theorem that our enriched-monoid quotient *is* `S(L)`, (iii) the
Arnold-decomposition that makes the two-sided congruence right-computable, (iv)
the exports as corollaries. The tool is one instantiation; the mathematics stands
without it. This test is the guardrail for altitude: anything that only makes
sense "because we coded it" is cut.

**Why it wasn't constructed before (the real hook, beyond size):** `S(L)` was
*defined* by Arnold (1985) and sits at the center of ω-language theory, yet — unlike
the finite-word syntactic monoid, computed routinely for decades — it was never
materialized from an automaton. Not (only) because it can be large: because
computing it needs two things the literature had *separately* and never combined
into a procedure —
  1. a recognizer that remembers **acceptance along runs**, not just transitions
     (Carton–Perrin–Pin have the matrices; nobody quotients them by a procedure);
  2. a way to compute the **two-sided** syntactic congruence **without quantifying
     over two-sided contexts** (Maler–Staiger split it finitary × infinitary but
     compute no quotient).
Our two keys — the acceptance-enriched monoid `EM`, and the Arnold decomposition
collapsed to *residual equality + right-invariant profiles* via a rotation lemma —
supply exactly (1) and (2). That is the interesting theoretical content.

---

## What to DROP / DEMOTE / ELEVATE (explicit)

- **DROP:** the transition-monoid aperiodicity *screen*. It is an optimization of
  a tool, not mathematics of the object. Aperiodicity is read off the quotient,
  full stop. (Keep the *fact* "aperiodicity is inherited upward through the
  enrichment" only if it earns its place as a lemma about `EM`; otherwise cut.)
- **DEMOTE:** canonical-LTL (same language ⟹ same formula). It over-emphasizes the
  synthesis. Mention once, in passing, as a property of one export.
- **ELEVATE:** the **reified `S(L)` as a complete, canonical, exportable semantic
  representation of an ω-language — LTL or not.** This is the headline deliverable.
  Practically a canonical semantic object ("a new kind of HOA"), reusable across
  workflows, from which the exports fall out. What you *do* with it is downstream
  of *having* it.
- **ELEVATE:** the **finite-word specialization**. The construction is uniform over
  `Σ^∞`; restricted to `Σ*` it yields the classical syntactic monoid — the object
  the finite-word learning/algebra community already builds on. New audience,
  near-zero extra cost.

---

## Red threads (two simple examples, woven through every section)

- **`GF(aa)` := `GF(a ∧ Xa)`** — "infinitely many `aa`-factors." *LTL.* Its natural
  2-state presentation can encode letter `a` as a transposition, so the transition
  monoid carries a spurious `Z₂`. Job of the red thread: show `EM` and the quotient
  **collapsing the fake group** (parity words are Arnold-equivalent — at infinity
  modular counts become thresholds), the positive decision, the synthesis, and the
  canonical automaton. The example that says "a group in a presentation is not a
  group in the language."
- **`Even` := `(aa)*·b·Σ^ω`** — "an even number of `a`'s, then `b`, then anything."
  *Non-LTL* (counts `a`'s mod 2 before the first `b`). Canonical mod-2. Job: show a
  **real** group in the quotient, the negative decision, and the **linear (`F₁`)
  counting-family** certificate `n ↦ [aⁿ·b·⊤ ∈ Even] = [n even]`, period 2.
- *(secondary, only where prefix-independence needs illustrating)* the
  prefix-independent mod-2 "every `a`-block eventually even": the residual
  congruence is **blind** (one class), so its certificate is necessarily the
  **ω-power (`F₂`)** shape — the two-shapes-are-both-load-bearing point. Bring in
  only if Section on the decomposition needs the blindness beat.

Weaving rule: every technical object is introduced *and then immediately shown on
`GF(aa)` and `Even`*. The reader never meets a definition without seeing it act on
the two threads.

---

## Section arc

### 1. Introduction — the object nobody builds
- The finite-word template the reader already trusts: the **syntactic monoid** is
  canonical, computable, and the workhorse under Schützenberger (star-free =
  aperiodic), learning, and classification. [Schützenberger 65; Pin]
- The ω-analogue **exists in theory** — Arnold's syntactic congruence [Arn85],
  `S(L)` the canonical algebra — **and is not built in practice** from automata.
- Thesis sentence: *we construct `S(L)` from an ω-automaton, via two keys, and
  reify it as a complete, canonical, exportable representation; the LTL questions
  are exports.*
- The "beyond explosion" hook (above), stated crisply.
- Contributions, object-first: (a) the construction (`EM` + rotation-collapsed
  congruence) with the theorem `EM/~ = S(L)`; (b) the reified representation as a
  complete invariant; (c) the exports — decide / refute-with-witness / synthesize /
  Cayley automaton / equality-hash; (d) uniform over `Σ^∞`: finite words for free.
- Red threads announced.

### 2. The object, precisely (context = narrative, related work interleaved)
Definitions with citation-grade precision; no hand-waving.
- **ω-semigroups, the infinite product, linked pairs** (Ramsey): every `w ∈ Σ^ω`
  addressed by a linked pair `(s,e)`, `se=s`, `e²=e`. [PP04 ch. II; CPP08]
- **The syntactic congruence of an ω-language** and its **two context shapes**
  (linear `x·_·y·t^ω`, ω-power `x·(_·y)^ω`); `S(L)` = its quotient, the coarsest
  saturating congruence; presentation-independent. [Arn85; PP04]
- **star-free = FO[<] = LTL = aperiodic `S(L)`** — cite, do not re-prove.
  [Tho79; Per84; Kamp68; DG08]
- Interleave, *as we define*: Carton–Perrin–Pin's recognizing matrices (the object
  is recognizable, computed only to brute-force triple saturation) [CPP08];
  Maler–Staiger's finitary × infinitary split (the decomposition exists, no
  quotient) [MS97]. The gap is stated as the negative space these leave.
- Show on threads: the linked pairs of `GF(aa)` and `Even`; what "a group in
  `S(L)`" means for each (fake vs real).

### 3. Key 1 — the acceptance-enriched monoid `EM`
- **Definition.** `w ↦ (q ↦ (δ(q,w), marks along w))`; monoid on `Q×2^C`.
  [our object; the deterministic Emerson–Lei specialization of CPP08's matrices —
  say so precisely]
- **Theorem (skeleton lemma).** Same enriched element ⟹ interchangeable in every
  ω-context ⟹ the syntactic morphism factors through `EM`, and `S(L)` is a
  quotient of `EM`. **Prove it** (determinism + marks-along-run pin the acceptance
  of every surrounding ω-word).
- **Why the enrichment is necessary (proved, not asserted):** two words with equal
  state maps but different marks are separated by an ω-power context ⟹ the plain
  transition monoid does not recognize `L`. Corollary: a transition-monoid group is
  not a language group — the exact reason the `GF(aa)` presentation's `Z₂` is
  spurious. (This is where the dropped "screen" fact belongs *if* it belongs: as a
  remark that transition-monoid aperiodicity is only *sufficient*, inherited upward
  — one sentence, not a subsection.)
- Threads: the `EM` of `GF(aa)` (10 elements) and of `Even`.

### 4. Key 2 — the Arnold decomposition, made right-computable
The theoretical heart. **Prove everything here.**
- **The collapse lemma.** Linear-context acceptance depends on a prefix only
  through the single state it reaches (prefix marks are finite, never in the
  inf-set). ⟹ the linear half is **pointwise residual equality**; the ω half is
  **right-invariant acceptance-profile equality**. **Prove** the factorization
  `~ = ~lin ∧ ~ω`.
- **The rotation lemma.** A left factor acts on the seed only by re-indexing a slot
  (determinism for `~lin`; conjugacy `(aeb)^ω = a(eba)^ω` for `~ω`). ⟹ the
  **two-sided** syntactic congruence is computable with **right moves alone**.
  **Prove it** — this is the lemma that unlocks the whole construction; it is the
  contribution against Maler–Staiger (who have the split, not this).
- **Main Theorem.** `EM/~ = S(L)`, with `~ = ~lin ∧ ~ω` the right-computable
  congruence; hence `S(L)` is materialized by (residual classes on `Q`) + (profiles
  on `EM`) + (one right-refinement to fixpoint). State the construction as a
  theorem, not a procedure.
- **Prefix-independence as a theorem, not a case.** One residual class ⟺
  prefix-independent ⟺ `~lin` blind ⟺ only `F₂` can witness. (Cite Angluin–Fisman
  2021: LTL languages with trivial right congruence — `FG(a∨Xa)` — the same fact
  from the learning side; the profile half is the repair.) [AF21; MS97]
- Threads: `Even`'s real group survives the quotient; `GF(aa)`'s fake one dies
  (10→6 classes, all periods 1).

### 5. The reified object and what it is
The elevated headline.
- **`S(L)` as a complete invariant.** Classes (keyed by shortlex-least
  representative — a language invariant) + multiplication table + letter map +
  **accepting linked-pair set** (needed to tell `L` from its complement) determine
  `L` exactly. **Theorem:** two ω-regular languages over the same `AP` are equal iff
  these tables coincide. Holds for *all* ω-regular `L`, aperiodic or not.
- **Exportable — a canonical semantic representation.** A serialization of these
  tables is a presentation-independent artifact ("a new kind of HOA"): what a
  minimal deterministic automaton would be if one existed — which it does not for
  ω-words. The point that no automaton-level route can match: *canonical exactly
  where the automata are not.*
- **Reusable across workflows** — the object first, uses second. Set up the exports
  as consumers of one artifact.

### 6. Exports (each short; all downstream of §5)
- **6.1 Deciding LTL** — aperiodicity of the quotient, exact both directions. One
  paragraph. [the DROP note: no screen.]
- **6.2 Refuting LTL with a portable witness** — the counting family (`F₁`/`F₂`),
  extracted from a group cycle by the chase; **soundness** (representation-free) and
  **completeness** (Arnold's two shapes, no third) as theorems; replay against `L`.
  Frame as *a use case*, not the point. Certifying-algorithms framing. [Arn85;
  MMNS11] Thread: `Even` → `F₁`; the prefix-independent variant → `F₂`.
- **6.3 Synthesizing LTL** — the Diekert–Gastin local-divisor induction runs on the
  aperiodic quotient (the first runnable rendering; note the `XU` erratum).
  Canonical-formula property mentioned in one sentence (DEMOTED). [DG08; PP04 for
  the linked-pair calculus] Thread: `GF(aa)` synthesized back.
- **6.4 A canonical counter-free automaton** — the right-Cayley automaton of the
  quotient: transition monoid = right-regular representation, so **counter-free iff
  LTL**; forward, deterministic, constructible. The open point: the acceptance
  condition from profiles via linked pairs (Maler–Staiger the entry; residual
  quotient provably too coarse). The forward mirror of the co-deterministic
  prophetic form. [MS97] Keep this as a flagged *sequel*, honest about the gap.
- **6.5 Language-equality hash** — §5's invariant put to work; many-to-many
  identity (corpus dedup) where pairwise equivalence is quadratic.

### 7. Finite words — the same object, a waiting audience
- The construction is uniform over `Σ^∞`; **restricted to `Σ*` it is the classical
  syntactic monoid** (the ω-part degenerates, profiles vanish, `~lin` alone). State
  the specialization precisely.
- Position for the **finite-word learning / algebra community**: FDFAs are the
  machine model of families of right congruences [Klarlund; AF16; ABF18; AF21;
  ROLL]; our object is the two-sided syntactic invariant they approximate with
  right-only machinery, and it exports as a syntactic FDFA in all but serialization.
  The finite-word syntactic monoid is *their* workhorse; we hand them the uniform
  `Σ^∞` object and the ω-extension. [tie to §2's finite-word template — the paper
  closes the loop it opened.]

### 8. Feasibility (short, honest)
- PSPACE-complete decision [CH91 transfer; DG08 Prop 12.3]; `|EM| ≤ (|Q|·2^{|C|})^{|Q|}`;
  the explosion is intrinsic, a cap is a necessity not an apology. The symbolic
  opening (slot-local right-multiplications) as one forward sentence. No economy
  claim.

### 9. Conclusion
- The object, newly constructible, canonical, complete, exportable. The two keys.
- The exports as corollaries; the finite-word bridge; the one open lemma (Cayley
  acceptance). "The syntactic ω-semigroup is not just definable — it is buildable,
  and worth building."

---

## Related work — interleaving map (no standalone dump)

| where it lands | paper | what it anchors |
|---|---|---|
| §1, §7 | Schützenberger 65; AMoRE; Pin | finite-word syntactic monoid: canonical, computed, the template |
| §2 | Arnold 85 | the syntactic congruence + two context shapes = the object |
| §2 | PP04; CPP08 | ω-semigroups, linked pairs, the recognizing matrices (no quotient procedure) |
| §2, §6.1 | Tho79; Per84; Kamp68; DG08 | the characterization chain (cited, not re-proved) |
| §4 | MS97 | the split (finitary × infinitary) — we add the right-computable quotient + rotation |
| §4, §7 | AF21; AF16; ABF18; Klarlund; ROLL | trivial-right-congruence blindness; FDFA = right-congruence machine model |
| §4, §6.4 | PW13 | co-deterministic finitary × infinitary (fragments only, LTL-ness as precondition) |
| §6.2 | MMNS11 | certifying algorithms → negative-side, language-level witness |
| §6.3 | DG08 §8; PP04 | the synthesis + the ω-class conjugacy calculus |
| §8 | CH91; DG08 Prop 12.3 | PSPACE-completeness |

---

## Open decisions for the fill-in (flag, don't guess)

1. **Title.** Candidates: "The Syntactic ω-Semigroup, Constructed"; "Reifying the
   Canonical Algebra of an ω-Regular Language"; "A Constructible, Complete Invariant
   for ω-Regular Languages." Pick at fill-in.
2. **Where the finite-word section sits** — its own §7, or folded into §1/§5 as a
   running "and this specializes" thread. Leaning standalone §7 for the learning
   audience's visibility.
3. **How much of §6.4 (Cayley)** to include given its open acceptance lemma —
   flagged sequel vs. full subsection. Leaning: a crisp subsection that states the
   counter-free theorem and *names* the open lemma, no more.
4. **Whether `Even` or the prefix-independent variant is the primary non-LTL
   thread.** Leaning `Even` primary (linear/`F₁`, cleanest), prefix-independent as
   the one-beat cameo for `F₂`/blindness.
