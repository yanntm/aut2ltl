# Materializing the Syntactic ω-Semigroup: a Canonical Representation of Regular ω-Languages

**Yann Thierry-Mieg**

With significant inputs from
**Claude (Anthropic)**

*Working draft — 2026-07-15*

## Abstract

- The syntactic ω-semigroup: canonical, complete, defined since Arnold 1985,
  never built.
- Contribution 1: the object itself, reified as an invariant `𝓘 = ⟨𝒮, P⟩` — a
  stamp `𝒮 : Σ⁺ → C` classifying the finite words and an acceptance layer `P`
  of linked pairs over it — with a standalone lasso-membership semantics: a
  canonical normal form for ω-regular languages, which the domain has never
  had.
- Contribution 2: the rotation lemma — the two-sided syntactic congruence is
  computable by right multiplications alone; the structural fact missing from
  40 years of literature.
- Contribution 3: the construction from any deterministic Emerson–Lei
  automaton, assembling the two, with correctness `𝓘(D) = 𝓘(L(D))` proved
  against the semantics.

## 1. Introduction

- Finite words have a normal form (the minimal DFA) and forty years of tooling
  on it; ω-words have none — no minimal deterministic automaton, every
  pipeline manipulates presentations, never languages.
- Arnold's syntactic ω-semigroup is the canonical algebra in principle and a
  phantom in practice: defined everywhere, built nowhere.
- The obstruction is structural (recognizers forget acceptance along runs; the
  congruence is two-sided) — the bridge to the construction.
- Contributions restated: the object and its canonicity (§3), the construction
  with the rotation lemma at its core (§4), what the invariant unlocks (§6).
- The three running examples announced — `GF(aa)`, `Even`, `EvenBlocks` — met
  first as tables, only later as automata.
