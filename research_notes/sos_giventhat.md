# Given-That on the Syntactic ω-Semigroup — Directions

*Exploratory memo, 2026-07-10. Not a paper; a map of candidate results for
one. Companion to `sos_calculus.md` (notation, the invariant, the hulls of
§3.6) and to [DPT25], the automata-side original this ports:
`papers/DuretLutz_Poitrenaud_ThierryMieg_2025_ICATPN.pdf`.*

## 0. Premise

[DPT25] verifies `S ⊨ φ` given prior knowledge `K` (an over-approximation
`ℒ(S) ⊆ ℒ(K)`) by replacing `A_{¬φ}` in the product with any automaton `B`
whose language sits in the interval

    ℒ(¬φ) ∩ ℒ(K)  ⊆  ℒ(B)  ⊆  ℒ(¬φ) ∪ ℒ(¬K)          (Theorem 1 there)

and then navigates that freedom heuristically on the *presentation*:
endpoint automata (§4), per-transition Boolean bands `[f ∧ TG, f ∨ ¬SG]`
simplified by Minato's algorithm (§5), stutter-insensitivization within the
bands (§6). On the MCC'22-derived benchmark, the endpoint checks alone kill
half the problems.

The port's thesis: on the invariant, the interval is not a search space to
be probed through label rewrites — it is an **exactly represented finite
lattice** of saturated pair sets on one aligned table, whose endpoints are
free surgeries, whose decisive checks are two scans, and whose "is there a
simpler `B`" questions become closed-form read-offs through the hull
machinery (CAL5). The system `S` never enters the calculus; only the two
spec-sized objects `𝓘(¬φ)` and `𝓘(K)` pay entry.

## 1. The interval as a lattice (D1 — mostly free)

Align `𝓘(¬φ)` and `𝓘(K)` once. Then:

- `P_min = P_{¬φ} ∩ P_K` and `P_max = P_{¬φ} ∪ P_K^c` are surgeries; the
  legal `B`s are exactly the saturated pair sets `Q` with
  `P_min ⊆ Q ⊆ P_max` (byte-canonical after one `reduce` each).
- **The two decisive checks are one scan each.** `L(P_min) = ∅ ⟺ K ⊨ φ`
  (verdict: property holds, no model checker run); `L(P_max) = Σ^ω ⟺
  K ⊨ ¬φ` (verdict: every run of the nonempty `S` is a counterexample).
  [DPT25] must dodge the second — universality is exponential on TGBA and
  their workaround needs the formula for `φ`; here it is emptiness of a
  complement, one flip away, symmetric with the first. The half-of-MCC
  kill rate should reproduce as exactly these two scans.
- **Certificates throughout**: a failed endpoint check returns the minimal
  witness lasso (Prop 3.2 of the calculus paper) — "K does not settle φ,
  and here is the shortest behavior it leaves open".

Nothing in D1 needs new theory; it is an afternoon on top of the calculus
package (a `given_that(pair_neg_phi, pair_K)` module returning the interval
object + the two decisions).

## 2. Exact "simpler class" existence tests (D2 — the CAL5 payoff)

[DPT25]'s goals are automaton-shaped (fewer states, weaker strength class,
stutter-insensitive, fewer APs). The language-shaped versions become exact
questions about the interval, because the hulls are least/greatest
fixpoints:

- **∃ safety `B`** ⟺ `safety_closure(P_min) ⊆ P_max`, and then
  `B = safety_closure(P_min)` is the canonical witness — the least safety
  language above `P_min`, one `O(n²)` scan on the aligned table. Reading:
  *given `K`, the model check reduces to a safety check*, decided exactly,
  checker handed over.
- **∃ co-safety `B`** ⟺ `P_min ⊆ interior(P_max)`, witness
  `interior(P_max)`, dually.
- **∃ obligation `B`** — one scan too, by Theorem 3.10's structure. A
  hull-generated `B` is an `R`-class-constant verdict `θ`, and any
  `R`-class-constant assignment is automatically saturated (conjugacy
  preserves the stem's `R`-class). The interval constrains `θ` pointwise:
  a pair of `P_min` with stem in `R`-class `r` forces `θ(r) = 1`; a linked
  pair outside `P_max` with stem in `r` forces `θ(r) = 0`. **Claim
  (easy proposition): an obligation `B` exists iff no `R`-class is forced
  both ways** — checkable in `O(|linked|)` after the SCC pass, greedy
  witness for free (unforced classes: pick anything, e.g. minimize the
  alternation depth of Prop 3.11 while at it).
- **Degree/strength minimization** (open): the minimal Wagner degree /
  Carton–Perrin acceptance index achievable in the interval. The band
  cases above are the first rungs; whether the general question has a
  read-off or needs search over the lattice is a real research question
  (Q3). Same for the [DPT25]-native objective "minimal `|𝒞|` after
  reduce" — plausibly NP-hard in general, worth settling.

## 3. Stutterization as a quotient (D3 — the technical heart)

§6 of [DPT25] spends the interval freedom to make `B` stutter-insensitive,
heuristically and within bounds. Algebraic reformulation: stutter-invariant
languages over `Σ` are exactly those recognized through the **stutter
quotient** — the image of the table under the smallest congruence forcing
`λ(a)·λ(a) = λ(a)` for every letter (Prop 3.3 of the calculus paper says
this is the right cut). Conjectured test:

> ∃ stutter-invariant `B` in the interval ⟺ the stutter-closure of
> `L(P_min)` (pull `P_min` through the quotient and back) stays `⊆ P_max`.

The work is in the closure direction: the quotient can merge
verdict-distinct pairs, and that is exactly the "no" case; what must be
proved is that the pulled-back saturation of `P_min`'s image is the *least*
stutter-invariant language above `L(P_min)` (a Galois adjunction between
the table and its stutter quotient). If it goes through, §6's bounded
heuristic becomes an exact one-quotient test with a canonical witness. Q2.

## 4. LTL-given-that, end to end (D4 — the application Spot cannot offer)

When `φ` and `K` are both LTL, both tables are aperiodic, the aligned table
is aperiodic (a submonoid of a product of aperiodics is aperiodic), and
therefore **every `B` in the interval is LTL-definable** — the lattice
never leaves the variety (Prop 5.11 of [SωSX26] specialized to this
setting). So once `sos2ltl` (the extraction implementation of [SωSX26])
lands, the pipeline closes at the formula level:

    φ, K  →  enter  →  choose B in the lattice (D1–D3 criteria)
          →  reduce  →  sos2ltl  →  a *formula* ψ, simpler than ¬φ,
                                     equivalent to it given K

i.e. **LTL simplification given prior knowledge**, formula in, formula out
— the operation [DPT25] explicitly cannot reach (its own ledger: Spot has
no automaton→LTL path), and arguably the cleanest headline of the port.
Simplification metric to fix: extracted formula size vs `|𝒞|` vs Wagner
degree — the D2 criteria give the knobs. Dependency: the `sos2ltl` tool;
everything else in this memo is buildable today.

## 5. AP-shedding (D5 — stays approximate, say so)

[DPT25]'s `QE(P, K)` drops `K`-only atomic propositions by existential
quantification, over-approximated on subformulas. The exact operation is
the §3.4 frontier (`remove_ap`), on our side too. The algebraic tool is the
letter-merging inverse substitution (free), which yields a *different*
over-approximation: `π⁻¹(π-closure)` along the merge. Whether the algebraic
over-approximation dominates the syntactic one (or is incomparable) is a
small self-contained question (Q4); either way the port keeps [DPT25]'s
honest "over-approximation of knowledge is still knowledge" argument —
any `K' ⊇ K` is legal knowledge, so approximation costs precision, never
soundness.

## 6. What stays on the automata side

`B` must finally meet `S` as an automaton, and its quality as a *product
partner* — label economy, determinism-in-practice, transition count — is a
presentation property. The exit acceptor of the chosen `B` (calculus paper
§4, `O(|P|·n)` stem–loop) still deserves [DPT25]'s §5 grooming: SG/TG bands
against `A_K` and Minato covers apply verbatim to it. The port sits above
§5, not instead of it: choose the language exactly, then present it well.
(And the endpoint kills of D1 need no `B` at all.)

## 7. Evaluation plan

Reuse the [DPT25] benchmark (MCC'22-derived, third-party): reproduce the
endpoint kill rate as the two scans; report the D2 hit rates (how often a
safety / co-safety / obligation `B` exists where the original `A_{¬φ}` was
stronger — each hit is a strength-class drop the model checker feels);
entry-price accounting per case (spec-sized, expected small — the V1c
methodology transfers); with `sos2ltl`, a table of formula-level
simplifications `¬φ ⇝ ψ` with sizes. House rules as in CAL4 (§8.1 of the
spec): per-case budget, checkpoint campaigns, validated outputs to
`reference/`, `.cat`/CSV only.

## 8. What would make it the paper

1. D1 + D2 with the two easy propositions proved (safety/co-safety
   adjunction — one paragraph each off Prop 3.5/Cor 3.6; the obligation
   forcing argument of §2 above).
2. The stutter-quotient theorem (Q2) — the technical contribution.
3. The degree/size minimization landscape (Q3) settled at least to
   "read-off vs NP-hard" granularity.
4. The end-to-end LTL-given-that demonstrator (D4, needs `sos2ltl`).
5. The benchmark section (§7).

Title shape: *"Choosing the Simplest Property Given Prior Knowledge,
Canonically"*. Dependencies: the calculus package incl. CAL5 (done),
`sos2ltl` for D4 only; nothing on the learner.

## References (delta over the calculus paper)

- [DPT25] Duret-Lutz, Poitrenaud, Thierry-Mieg. *Simplifying LTL Model
  Checking Given Prior Knowledge.* Petri Nets 2025, LNCS, pp. 433–456.
- [MD15] Michaud, Duret-Lutz. *Practical stutter-invariance checks for
  ω-regular languages.* SPIN 2015. (the `cl`/`sl` closures §3/D3 replaces)
- [SωS26], [SωSX26]: as in `sos_calculus.md`.
