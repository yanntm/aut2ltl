# genaut language benchmark — the deduped corpus, by language

The project's reference benchmark: every ω-language a small automaton realizes, **each counted once**. Built by exhaustively enumerating tiny automata per shape and, past the tractability wall, **sampling** from the id space, then removing every redundancy — the same language re-presented across shapes, carrying an unused atomic proposition, or written under a different naming/polarity of its propositions. What remains is the language catalogue; this file studies it.

> **Scope.** Exhaustive over the shapes below the wall (every language of those shapes is present); **sampled**, hence *non-exhaustive*, for the beyond-wall shapes (present languages are real, but absence proves nothing). Rows are tagged accordingly. The alphabet dominator `2state2ap0acc` is excluded. Provenance is read off each model's name, which is kept from the **smallest shape** that realizes the language.

## Headline

| catalogue | languages |
|---|--:|
| fixed AP labeling (`flat/`, distinct `.sos`) | 3790 |
| distinct up to renaming symbols (primals) | 2007 |
| &nbsp;&nbsp;— from exhaustive shapes | 1764 |
| &nbsp;&nbsp;— from sampled shapes (non-exhaustive) | 243 |
| + complements added to close under complement | 1931 |
| **complement-closed total (`flat_canon/`)** | **3938** |

The relabeling + unused-AP fold takes 3790 fixed-labeling `.sos` to 2007 languages up to renaming (47% were relabel/polarity twins or carried a redundant AP); closing under complement (no language is its own, so the total is even) adds 1931, reaching 3938. Primal automaton states: 1 / 5 / 9 (min / median / max); algebra size `|𝒞|`: 2 / 15 / 121.

## The LTL cut

The dividing line everyone asks about first — is the language **LTL-definable** (equivalently, star-free / first-order / aperiodic syntactic ω-semigroup) or does it genuinely **count**? Read off each language's `.cat` (aperiodicity of `𝓘(L)`), over the complement-closed catalogue:

| definability | languages |
|---|--:|
| **LTL-definable** (aperiodic) | **2240** |
| **non-LTL** (genuine ω-counting) | **1698** |
| total (`flat_canon/`) | 3938 |

So **43%** of the small ω-languages are beyond LTL. The cut is complement-invariant (aperiodicity is a property of the semigroup, not of `accept`), so it splits the primals the same way: 1142 LTL / 865 non-LTL of 2007. It cuts *across* the Wagner degrees below — depth and countability are independent axes.

### Stutter-invariant — the X-free refinement of LTL

A language is **stutter-invariant** iff its syntactic monoid keeps no letter apart from its square (`M(λa, λa) = λa` for every `a`) — the read-off sitting beside aperiodicity in each `.cat`. This is a *subclass* of LTL (stutter-invariant `≡` LTL without `X`), so it lands entirely inside the aperiodic column; a language that genuinely counts letters cannot be stutter-blind. Over the catalogue:

| sub-class of LTL | languages | of LTL |
|---|--:|--:|
| **stutter-invariant** (X-free) | **648** | 29% |
| stutter-sensitive but LTL | 1592 | 71% |
| (non-LTL — all stutter-sensitive) | 1698 | — |

So **16%** of the catalogue (648 of 3938) is stutter-invariant, i.e. **29%** of the 2240 LTL-definable languages drop the `X` operator. Like the LTL cut it is complement-invariant, splitting the primals 336 / 2007. The per-degree `stutter-inv` column below shows how it distributes over the Wagner ladder.

## Composition (primals — the shape-realized languages; + 1931 complements close the set)

| axis | bucket | languages |
|---|---|--:|
| acceptance family | `gba` | 1744 |
| acceptance family | `parity` | 263 |
| provenance | exhaustive | 1764 |
| provenance | sampled | 243 |
| acceptance colours | c=0 | 1393 |
| acceptance colours | c=1 | 329 |
| acceptance colours | c=2 | 285 |
| acceptance colours | c=3 | 0 |
| definability | LTL (aperiodic) | 1142 |
| definability | &nbsp;&nbsp;— stutter-invariant (X-free ⊆ LTL) | 336 |
| definability | non-LTL | 865 |
| **primals** | | **2007** |
| + complements (dual acceptance) | | 1931 |
| **complement-closed total** | | **3938** |

## Wagner-degree profile (classified, complement-closed)

Each language's **category**, read off its syntactic invariant `𝓘(L)` into a `.cat` sidecar (a pure table search — no automaton, no Spot) and aggregated here. `ϕ = (γ, s)` is the Wagner degree (`γ` the ordinal depth, `s ∈ {σ, π, δ}` the side); `(m⁺, m⁻, n⁺, n⁻)` the chain/superchain coordinates; `non-LTL` the count in that row that is **not** LTL-definable; `stutter-inv` the count that is stutter-invariant; `primals` the shape-realized share (the rest are added complements). Because the catalogue is closed under complement, the profile is **exactly duality-symmetric**: every `(γ, σ)` row matches its `(γ, π)` dual, and the self-dual `δ` rows stand alone.

| `ϕ = (γ, s)` | `(m⁺, m⁻, n⁺, n⁻)` | class | languages | non-LTL | stutter-inv | primals |
|---|---|---|--:|--:|--:|--:|
| (0, σ) | (-1, 0, -1, 0) | empty — trivial open | 1 | 0 | 1 | 1 |
| (0, π) | (0, -1, 0, -1) | universal — trivial closed | 1 | 0 | 1 | 1 |
| *— trivial pair (weakest), set apart —* | | | *2* | | | |
| (1, δ) | (0, 0, 0, 0) | clopen — properly Δ₁ | 62 | 0 | 2 | 36 |
| (1, σ) | (0, 0, 0, 1) | properly open — guarantee | 1356 | 678 | 31 | 4 |
| (1, π) | (0, 0, 1, 0) | properly closed — safety | 1356 | 678 | 31 | 1356 |
| (2, σ) | (0, 0, 1, 2) | properly Σ₂ | 4 | 0 | 2 | 4 |
| (2, π) | (0, 0, 2, 1) | properly Π₂ | 4 | 0 | 2 | 1 |
| (ω, σ) | (0, 1, -1, 0) | properly Gδ — DBA-proper | 466 | 98 | 280 | 365 |
| (ω, π) | (1, 0, 0, -1) | properly Fσ — DCA-proper | 466 | 98 | 280 | 128 |
| (ω·2, σ) | (1, 1, 0, 1) | one Rabin pair — σ side | 12 | 12 | 0 | 0 |
| (ω·2, π) | (1, 1, 1, 0) | one Rabin pair — π side | 12 | 12 | 0 | 12 |
| (ω², σ) | (1, 2, -1, 0) | parity {0,1,2} — proper | 99 | 61 | 9 | 99 |
| (ω², π) | (2, 1, 0, -1) | co-parity {0,1,2} — proper | 99 | 61 | 9 | 0 |

Degrees span `(0, σ)` (trivial) up to `(ω², ·)` (parity-`{0,1,2}`); no language reaches Wagner's derivative (`γ = μ` throughout, Prop. 11.1). The degree is a language invariant — a `.cat` says the same for a language however many shapes, states, or colours presented it.

## By origin shape

Each language attributed to the smallest shape realizing it (its model name). `states` is the canonical deterministic automaton's state count; `|𝒞|` the syntactic-semigroup size — both min / median / max over the shape's languages.

| shape | n | k | c | family | tier | languages | states | algebra `𝒞` |
|---|--:|--:|--:|---|---|--:|---|---|
| `1state1ap0acc` | 1 | 1 | 0 | gba | exhaustive | 3 | 1 / 1 / 2 | 2 / 2 / 3 |
| `1state1ap1acc` | 1 | 1 | 1 | gba | exhaustive | 1 | 1 / 1 / 1 | 3 / 3 / 3 |
| `1state1ap2acc` | 1 | 1 | 2 | gba | exhaustive | 1 | 1 / 1 / 1 | 4 / 4 / 4 |
| `1state1ap2acc_parity` | 1 | 1 | 2 | parity | exhaustive | 1 | 1 / 1 / 1 | 3 / 3 / 3 |
| `1state2ap0acc` | 1 | 2 | 0 | gba | exhaustive | 4 | 2 / 2 / 2 | 3 / 3 / 3 |
| `1state2ap1acc` | 1 | 2 | 1 | gba | exhaustive | 10 | 1 / 2 / 2 | 3 / 4 / 4 |
| `1state2ap2acc` | 1 | 2 | 2 | gba | exhaustive | 21 | 1 / 1 / 2 | 4 / 5 / 6 |
| `1state2ap2acc_parity` | 1 | 2 | 2 | parity | exhaustive | 19 | 1 / 1 / 2 | 3 / 4 / 5 |
| `1state3ap0acc` | 1 | 3 | 0 | gba | exhaustive | 20 | 2 / 2 / 2 | 3 / 3 / 3 |
| `1state3ap1acc` | 1 | 3 | 1 | gba | exhaustive | 225 | 1 / 2 / 2 | 3 / 4 / 4 |
| `2state1ap0acc` | 2 | 1 | 0 | gba | exhaustive | 21 | 3 / 3 / 4 | 3 / 6 / 12 |
| `2state1ap1acc` | 2 | 1 | 1 | gba | exhaustive | 93 | 2 / 3 / 6 | 3 / 8 / 21 |
| `3state1ap0acc` | 3 | 1 | 0 | gba | exhaustive | 1345 | 4 / 6 / 8 | 4 / 22 / 121 |
| `2state1ap2acc_parity` | 2 | 1 | 2 | parity | **sampled** | 243 | 2 / 4 / 9 | 3 / 11 / 31 |

Generated by `python3 genaut/flat_study.py` from `corpus/flat_canon/` (the LTL cut, stutter refinement, and Wagner-degree profile aggregate the per-language `.cat` sidecars). For the per-shape *presentation* funnel (automata, not languages) see `SHAPES.md`.
