# The Verdict Distribution of a Specification
### satisfaction, agreement and conformance on the syntactic ω-semigroup

**Yann Thierry-Mieg** — with significant inputs from **Claude (Anthropic)**

*Skeleton. Sections carry bullets, not prose. `sos_measure.md` stays as it is:
nothing here deletes it, and anything this outline drops remains available
there. Each section is tagged with its provenance —* **[have]** *= already
written and proved in `sos_measure.md`,* **[new]** *= to write,* **[open]** *=
a theorem we do not have yet.*

---

## The point, in one paragraph

Two ω-regular languages held as invariants — a **model** `M` (the behaviour a
system is allowed to exhibit) and a **spec** `S` (the behaviour it must
exhibit) — yield an exact probability: resolve the model's nondeterminism
uniformly at random and ask how likely the result is to satisfy the spec.
One alignment, one walk, one linear system, one fraction. The i.i.d. random
word — the whole of the classical setup — is the *degenerate corner* `M = Σ^ω`,
where liveness is free and every interesting spec reads 0 or 1. The paper is
about what happens when the second object is a real one.

## Research questions

- **RQ1 — the object.** Can the syntactic ω-semigroup carry probability, and
  is there a *single* object from which satisfaction, similarity and
  conformance all follow?
- **RQ2 — the source.** What do the probabilities depend on, and how much
  information do they carry?
- **RQ3 — the identification.** Which specifications does a probability
  identify, and is that identification canonical and decidable?

## The three numbers (everything the paper delivers)

| | what the user hears | formally |
|---|---|---|
| **satisfaction** | "under this model, your spec holds with probability 5/8" | `Pr_M(S)` |
| **agreement** | "under this model, your two specs are indistinguishable" | `A_M(S₁,S₂) = 1 − Pr_M(S₁ Δ S₂)` |
| **verdict distribution** | "40% satisfy both, 12% only the spec, …" | `ν` on `{0,1}^k`, `Σν = 1` |

---

## 1. Introduction  **[new]**

- The qualitative calculus answers yes/no. Three questions it cannot answer:
  *how likely is my spec to hold? how far did my rewrite move it? how often
  does my model step outside it?*
- The naive quantitative move — sample words i.i.d. — is **degenerate random
  sampling**: liveness patterns read 1, safety patterns read 0. Show it in
  three lines (`G(p→Fq)`, `Fp`, `Gp`), and use it to motivate the second
  object rather than as a result.
- Nor can an assumption be imposed by **conditioning**: a safety assumption is
  a null set (`0/0`), a fairness assumption is co-null (changes nothing). The
  hypothesis must become a *source*.
- The move: the second language's own invariant **is** the source. Uniform
  resolution of the model's nondeterminism.
- Contributions:
  - **C1** generic-verdict theorem — the a.s. verdict of an absorbing
    component is *one* table lookup at a kernel idempotent (proved once, for
    an arbitrary source).
  - **C2** the **verdict distribution**: θ is a Boolean homomorphism on pair
    sets, absorption is language-free ⇒ one linear solve yields the whole
    Boolean lattice of `k` specs. Satisfaction, agreement and conformance are
    contractions of one distribution.
  - **C3** the source is the model's invariant — align, walk the live part,
    solve. No external chain formalism in the core. Uniform resolution of
    nondeterminism is what makes the question well-posed *without* MDPs.
  - **C4** what a probability identifies: agreement-1 is decidable and
    `p`-free; the identified class has a canonical least member; the LTL
    frontier moves.
  - **C5** evaluation on (model, spec) pairs.
- Outline paragraph.

## 2. Background  **[have — §2 of `sos_measure.md`, trimmed]**

- 2.1 the invariant, `Val`, linked pairs, the strong factoring theorem, the
  conjugacy law, `reduce`/byte-canonicity, the right-Cayley graph and its
  bottom SCCs. *(verbatim reuse)*
- 2.2 finite semigroups: kernel, `H(k)`, division, aperiodicity ⇒ LTL.
  *(verbatim reuse)*
- 2.3 measures on `Σ^ω`, labelled Markov chains, the classical
  probabilistic-verification recipe [CY95]. **Keep the transition-emitting
  embedding remark** — the model-induced walk needs it (letters sit on the
  Cayley edges).

## 3. The generic verdict  **[have — but restructured]**

- **Prove it once, for an arbitrary source.** Today `sos_measure.md` proves
  the Bernoulli form (Thm 3.4) and then relativizes to the Markov form
  (Thm 3.5) — the same argument twice. Here: one theorem, kernel taken in the
  **cycle semigroup** `T` of the absorbing component; Bernoulli is the
  instance `T = S`.
- Lemma A (doubled-word cut): a.e. run factors over an idempotent `k` of the
  kernel of `T`. *(= Lemma 3.1 / step (ii)–(iii) of Thm 3.5)*
- Lemma B (stem invariance): `Val(·, k)` is constant on the achievable stems —
  the `H(k)`-orbit conjugacy argument. *(= Lemma 3.2 / step (iv))*
- Lemma C (canonicity): independent of entry class, of the kernel idempotent,
  and of the source's choice of base state. *(= Lemma 3.3 / step (v))*
- **Theorem (generic verdict).** `1_{α ∈ S} = θ_B` a.s. on absorption in `B`,
  `θ_B = Val(c, k)` — one lookup.
- The ℤ/2 example and Figures 2–3 (the doubled-word cut on a sampled word; the
  kernel group and the phase contrast). *(reuse verbatim)*
- Remark: the phase inside `H(k)` is invisible at infinity — this is where the
  algebra, not the automaton, is doing the work. *(candidate: state the
  probabilistic version — the kernel group **equidistributes**. Nice-to-have,
  not required.)*

## 4. The verdict distribution  **[new — the core of the paper]**

- 4.1 **The absorption distribution.** Over the bottom SCCs of the (aligned)
  right-Cayley graph, `Pr[absorption in C]` sums to exactly 1 and depends only
  on the *table and the source* — not on any language carried by it.
- 4.2 **θ is a Boolean homomorphism.** `θ_C(P) = [(c·k, k) ∈ P]` — the
  indicator of one *fixed* linked cell. Hence `θ(P₁ ∩ P₂) = θ(P₁) ∧ θ(P₂)`,
  and likewise for `∪`, `\`, `xor`, complement. Three lines.
- 4.3 **Definition + theorem.** For `S₁ … S_k` on one aligned table, push
  absorption forward along `Θ(C) = (θ_C(P₁), …, θ_C(P_k))`:
  `ν(b) := Σ_{C : Θ(C) = b} Pr[absorption in C]` is a probability
  distribution on `{0,1}^k`, and **for every Boolean `f`**:
  `Pr(f(S₁,…,S_k)) = Σ_b f(b)·ν(b)`.
  *One SCC pass, one kernel idempotent, one linear system → the whole Boolean
  lattice.* This is the quantitative twin of "complement is a bit-flip".
- 4.4 **The read-offs.** satisfaction (`k = 1`); **agreement**
  `A = ν(0,0) + ν(1,1)`, a similarity in `[0,1]`, `1 −` a pseudometric;
  conformance ratios (violation rate, precision, recall) as conditionals of `ν`.
- 4.5 **Worked example, end to end** — the `sos_measure.md` §4.1 example
  ("first `b` at an even position", `μ = 2/3`) **extended to two languages**, so
  Figure 1 displays a `2×2` verdict distribution rather than a single fraction.
- Corollaries: rationality (Gaussian elimination); the certificate is the
  θ-labelled component map plus the linear system; a checker replays it.

## 5. The source: the model is the second invariant  **[C3 — new framing, `[have]` machinery]**

- 5.1 **Why i.i.d. is the degenerate corner.** `M = Σ^ω`, the empty
  hypothesis. Liveness is free, safety is null, the trichotomy is `p`-free —
  useful for *triage* ("your spec cannot be falsified by random testing") and
  nothing else.
- 5.2 **Why conditioning fails.** Any assumption with content is null
  (safety, `0/0`) or co-null (fairness, no change). An environment hypothesis
  cannot be imposed by conditioning; it must become a source. **[new — state it
  as a proposition, it is the hinge of the paper.]**
- 5.3 **The model-induced walk.** Take `I(M)`'s live classes; at each, choose
  among the letters that stay live, weighted by `p` and renormalized. For a
  safety `M` the walk stays inside `M` forever (`Pr(M) = 1`), so it is a source
  with support exactly `M`. Rational, exact, end to end; `M = Σ^ω` gives back
  `p`. The operational reading is the one an engineer means: *the model picks a
  legal move.*
- 5.4 **The product IS `align`.** Aligned classes are pairs `(c_S, c_M)`; the
  walk's state *is* the `M`-component. So the "product of a chain with the
  spec's invariant" is the calculus's `align`, restricted to the `M`-live part.
  **No external chain formalism in the core.** One alignment, one walk, one
  solve.
- 5.5 **Uniform resolution of nondeterminism** — and why this is the principled
  reason MDPs stay out of scope: we do not optimize over schedulers, we fix the
  uniform one. Turns the old non-goal into a positive argument.
- 5.6 **Sharpness — how much do the fractions carry?** **[new, two-line proof]**
  `Pr_M(S₁) = Pr_M(S₂)` for *every* finite labelled chain `M` **iff**
  `S₁ = S₂`: the lasso chain emits `u·v^ω` with probability 1, and ω-regular
  languages are fixed by their ultimately periodic words. So agreement across
  all sources is exact equality — the identification of §6 is a property of
  *one* source, not of the fractions in general. (Witness: the `{(ab)^ω}` vs
  `∅` pair.)
- 5.7 **Importing a model from outside** (optional, small): the `.mc` reader — a
  restricted PRISM subset, exact rationals — so a chain that came from a model
  checker can be used as the source. An *import path*, not the machinery.
  *(engineering exists; PRISM will not parse cube label names — sanitize on
  export.)*

## 6. What a probability identifies  **[6.1–6.4 have; 6.5 OPEN]**

*Framing: "when the agreement number saturates, what exactly is being
identified?"*

- 6.1 `A = 1` **iff** the aligned xor's θ-profile is all-zero — decidable,
  `p`-free, **no arithmetic at all**. *(have)*
- 6.2 The **shadow** as the construction (demoted from a contribution to a
  lemma): `D` = the union of `θ = 1` bottom SCCs is a right ideal, `sh(S)` is
  the open language it generates, `A(S, sh S) = 1`. Plus the warning: the
  shadow is sufficient, not complete. *(have — Prop 4.1)*
- 6.3 The **residual-measure series** characterizes the class; its syntactic
  congruence gives `M_x`, which **divides every member's syntactic monoid**;
  `ess(S)` realizes it; agreement-1 becomes a **byte test**; and the whole
  construction is measure-independent. *(have — Prop 4.3, Thm 4.4, Prop 4.5.
  The strongest mathematics in the corpus; needs no new work.)*
- 6.4 Corollaries: up to null sets everything is **co-safety** — the
  topological hierarchies are a null phenomenon; and the **LTL frontier moves**,
  decidably (aperiodicity of `M_x`). *(have — Cor 4.2, Thm 4.4(3))*
- 6.5 **[OPEN — the theorem to prove next, and it is the one that matters.]**
  §6.1–6.4 are all relative to the *degenerate* source. The equivalence a user
  wants is **agreement under the model**: `Pr_M(S₁ Δ S₂) = 0` — "these two
  specs are the same, *for this model*". Conjecture: the whole of 6.3
  relativizes, because the model-induced source lives on the **same monoid**
  (the aligned table) — so the residual-`Pr` series still factors through
  classes, the congruence is still two-sided, and Thm 4.4's proof has somewhere
  to stand. If it goes through, §6 becomes *the canonical form of a spec
  relative to a model*, which is the version anyone would want. If it does not,
  §6.1–6.4 stay and must be honestly labelled as the `Σ^ω` corner.

## 7. Evaluation  **[new — its own benchmark]**

- **The benchmark is (model, spec) pairs.** Not the 6222-language census —
  that is the classification framework's population, and it lives on here only
  as the exhaustive *probe* suite that argues the engine is correct and stable
  (flip law, oracle agreement, measure-independence, the product gates). It is
  pointed at, never reported as a result.
- Population: the canonical **property specification patterns** (Dwyer /
  Corbett / Avrunin) × scopes, instantiated over 2–3 propositions — every
  element is a formula a human wrote — paired with **models**: protocol-shaped
  safety constraints, hand-built and small.
- **E1 (RQ1).** The three numbers are computable, exactly, as fractions, on
  real specs. Report `|I(S)|`, `|I(M)|`, the aligned size, and the cost. One
  paragraph, not a performance section: the entry cost is the invariant (an
  owned frontier); the quantitative layer is one `O(n³)` rational solve.
- **E2 (RQ2).** *The source is a modelling commitment and the number moves with
  it.* Same specs under (a) the empty model `Σ^ω` — liveness reads 1, safety
  reads 0, nothing is learned; (b) a real model — the fractions are interior
  and interpretable. This is the experiment that carries the paper's argument.
- **E3 (RQ3).** Agreement under a model: which syntactically distinct patterns
  become **the same specification** once the model is fixed. Control: a sound
  LTL simplifier must give `A = 1` exactly (a red convicts us). Illustration:
  `GF p` vs `FG p` must sit at `A = 0`.
- **E4 (RQ3, the frontier).** How many of the paired specs are LTL *up to a
  null set of the model*.
- Reproducibility: every number a row in `sos_quant_report.md`, regenerable.

## 8. Related work  **[have, retargeted — READING IS GATING]**

- **Probabilistic verification**: [Var85], [CY95], [BK08 ch.10], PRISM. We
  change none of the asymptotics and do not intend to; the contribution is
  *which object sits on both sides* and that the product is the calculus's
  `align`.
- **Fair correctness / measure-1 semantics**: [VV06]. Currently one throwaway
  sentence — it is the nearest neighbour and must be read properly.
- **The algebraic line**: [PP04], [CP97/99], [SW08]; the claim "first
  probabilistic exploitation of the syntactic algebra" is exactly the sentence
  a referee checks. **Novelty must be established by reading, not asserted.**
  Two placeholder citations are still unread (PRISM CAV'11,
  Chatterjee–Doyen–Henzinger ToCL'10) — no citation until they are in
  `papers/` and read.
- Uniform resolution of nondeterminism / uniform schedulers: locate the prior
  art before claiming the construction.

## 9. Conclusion  **[new]**

- Probability localizes in the **kernel**: one canonical bit per absorbing
  component, one lookup. That statement cannot be made on an automaton.
- Two invariants in, one fraction out; the product is `align`; the whole
  Boolean lattice is one solve.
- Open directions, one line each: the **model-relative essential form** (§6.5);
  the **weighted/semiring** invariant (semiring-valued `Val` under the conjugacy
  law); the **finite-word case** — the same table with a *class-set* acceptance,
  where the walk's transient law gives densities as its limit law gives
  measures, and Schützenberger makes the same aperiodicity scan decide LTLf.
- Non-goals, stated once: MDPs (we fix the uniform scheduler rather than
  optimize over them, §5.5); performance (the entry cost is the invariant, an
  owned frontier — the quantitative layer is one linear solve).

---

## Provenance ledger (what has to be written vs. what is already proved)

| section | status | note |
|---|---|---|
| §2 | **have** | trim §2.4 out |
| §3 | **have**, restructured | prove once for a general source; Bernoulli is `T = S` |
| §4.1–4.4 | **new writing**, small code | the homomorphism lemma is three lines; `ν` is ~20 lines on the existing aligned-table + absorption code |
| §4.5 | **new** | extend the existing worked example to two languages |
| §5.1, 5.3–5.5 | **new framing** | machinery exists (align, live scan, product) |
| §5.2 | **new** | the conditioning-is-degenerate proposition — the hinge |
| §5.6 | **new**, two-line proof | tested witness already exists |
| §6.1–6.4 | **have** | reuse verbatim, reframed as "when agreement saturates" |
| §6.5 | **OPEN** | the theory item that now outranks everything else |
| §7 | **new** | new benchmark; the census is demoted to probes |
| §8 | **gating** | read [VV06] and the two placeholders before claiming novelty |
