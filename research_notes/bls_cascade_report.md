# Cascade ladder — Findings ledger (`bls_cascade_report.md`)

Ledger for `bls_cascade_experiments.md` (K-series). Current-state only; git
holds history. Each finding: id, one-line claim, status
(`CONFIRMED | REFUTED | BUDGET | BLOCKED`), the exact command, and pointers to
git-tracked files only. `PAPER-EDIT:` flags a refuted prediction against its
draft location in `bls_cascade.md`.

**Machinery.** The config machine `M_k(R)` and the (C)/(B) decider (ALG-1/2/5/6)
live in `tests/cascade/config_machine.py`; probes in `tests/cascade/`. The
verdict oracle is `Val(s,d) = (M(s,π(d)),π(d)) ∈ P` off `sosl.sos.Invariant`.

## Status

- **K-E0 — gate: DONE, split verdict.** Step 5 (`G(a→F b)`) CONFIRMED; steps 1–3
  (the floor witness `GF(a∧X((!a∧!b)U a))`) REFUTED — `PAPER-EDIT` on C.3.
- **The paper edit landed** (theory thread, 2026-07-11): K-F2's read is
  confirmed — the old C.3 derivation ran in the profile monoid, whose four
  flagged profiles the syntactic quotient merges into a zero (10 → 7 classes,
  frozen terminal layer). Consequence drawn on paper: Conjecture C.12 (both
  halves) and C.17 are **refuted** by the floor witness (draft C.4,
  Theorem C.12′); `G(a→Fb)` is the new C.3 worked witness; the floor witness
  is C.5's fallback instance. Revised `bls_cascade.md` (banner, C.3–C.7),
  `bls_cascade_experiments.md` (K-E0 expectations, K-E1/E2/E4/E6/E7
  re-scoped), main paper `sos_toltl.md` §5.1/§8.
  **K-E1–K-E5: UNBLOCKED** under the revised spec.
- **K-E0 COMPLETE** — all six steps green: steps 1–3 (revised expectations, via
  the K-F2 paper edit), step 3 sandwich (K-F5), step 4 C3 (B)-cross (K-F6),
  step 5 (K-F1), step 6 saturation (K-F4). The decider is validated five
  independent ways.
- **K-E1 DONE + K-E7 census map** — K-F7, K-F8 below. Every C3-undecided layer
  decides under (C) at k≤3; no new floor inhabitant; no third verdict mechanism.
- **K-E2 DONE (step 3, the decisive one)** — K-F9: the Prop C.19 transfer
  specimen yields the **first moving-layer floor inhabitant** (verified genuine
  (C)-conflicts at k=0,1, ALG-7 toggle + non-conjugate). Floor is empty on the
  census frame, inhabited beyond it. Steps 1/2 subsumed by K-F7.
- **Next: K-E3** (one-sidedness stats, reuses the sweep), K-E4 (config-normal-
  form emitter — DAG-only, never stringify).

---

## K-F1 — `G(a→F b)` is the width-0 config-(C) witness (draft step 5) — CONFIRMED

`𝓘(G(a→F b))` has a **non-frozen** terminal layer `{2,4}`, 1-anchored, with
exactly the draft's six edges and `(C)` holding at **width 0** while plain `(B)`
fails; the accepting family and verdict pattern match C.3 step 5.

- Terminal layer `{2,4}`: `b`(=!a&b)→reset(2), `a`(=a&!b)→reset(4),
  `s`(=!a&!b)→neutral. With `A:=4` (a-target), `B:=2` (b-target) the six k=0
  edges are exactly `(A,a)→A,(A,s)→A,(A,b)→B,(B,b)→B,(B,s)→B,(B,a)→A` — the
  draft's predicted set.
- `decide(inv,{2,4},k=0)`: **(C) holds** (0 conflicts, 22 collected F), plain
  **(B) fails** (1 conflict). Minimal accepted sets `{(B,s)→B}`, `{(B,b)→B}`,
  `{(B,a)→A,(A,b)→B}`: single-class-`B`(=2) accept, single-class-`A`(=4)
  reject, two-class accept — the C.3 step-5 pattern.
- Membership of five hand-picked lassos matches `inv.member` (identity of `𝓘`
  and `L`).

Command: `python3 -m tests.cascade.k_e0 gaFb` and
`python3 -m tests.cascade.k_e0_probe gaFb` and
`python3 -m tests.cascade.k_e0_verify gaFb`.
Logs: `tests/cascade/logs/k_e0_gaFb.txt`,
`tests/cascade/logs/k_e0_probe_gaFb.txt`,
`tests/cascade/logs/k_e0_verify_gaFb.txt`.

## K-F2 — the floor witness has a FROZEN terminal layer; (C) does NOT hold at width 0 — REFUTED

`PAPER-EDIT:` `bls_cascade.md` C.3 "The residual floor witness, worked"
(≈ lines 377–407), and C.0/§5.1's use of `GF(a∧X((!a∧!b)U a))` as *the*
config-normal-form floor witness at rung 0.

The canonical invariant `𝓘(GF(a∧X((!a∧!b)U a)))` diverges from the draft's
hand derivation at step 1:

- **Draft C.3:** terminal layer `R={A,B}`, two classes, 1-anchored non-frozen
  (`a`→const A, `b`→const B, `s`→identity), (C) at **width 0**, emitting
  `GF A_{(A,a)}` "with no descent of any kind."
- **Tool:** 7 classes, **prefix-independent**; `accept P={(6,6)}`; layers
  `{0}|{1}|{2,4}|{3,5}|{6}`. The terminal layer is the **single frozen class
  `{6}`** — every quotient letter (`s`,`b`,`a`) is *neutral* (a self-loop),
  `An=St=` all letters. `decide` gives **(C) fails at k=0** (2 conflicts, 7
  collected F) **and k=1** (16 conflicts); k=2 blows the 40 000-state budget.

The draft's non-frozen 2-class `{A,B}` machine *does* exist in `𝓘` — but as the
**transient** layers `{2,4}` and `{3,5}` (both →`{6}`), never terminal. Because
`L` is prefix-independent the pending-`a`/`b` bit washes out of the absorbing
class, leaving a frozen singleton. On a frozen layer `M_k(R)=SR_k` and the class
coordinate is absent, so (C) at width `k` = (B) at width `k+1` (draft Lemma
C.10 / C.6(2)); combined with §5.1's presupposed "(B̃) fails at every width",
(C) fails at **every** width. The config ladder never rescues this witness.

**Read (for the author to judge):** the two §5.1 witnesses' structural roles
are swapped. The six-edge non-frozen `{A,B}` config machine of C.3 is
`𝓘(G(a→F b))` (K-F1), the genuine width-0 config-(C) success; the
prefix-independent `GF(a∧X((!a∧!b)U a))` is a frozen-layer/window language the
config ladder does not decide. C.3's floor-witness derivation, C.9's
"residual floor witness below instantiates every hypothesis", and §10's
open-problem restatement all depend on this and need revisiting.

Commands: `python3 -m tests.cascade.k_e0 floor`,
`python3 -m tests.cascade.k_e0_probe floor`,
`python3 -m tests.cascade.k_e0_verify floor`.
Logs: `tests/cascade/logs/k_e0_floor.txt`,
`tests/cascade/logs/k_e0_probe_floor.txt`,
`tests/cascade/logs/k_e0_verify_floor.txt`.

## K-F3 — the (C)/(B) decider is cross-validated — CONFIRMED

The ALG-1/2/5/6 implementation reproduces the draft on the witness whose
structural model matches `𝓘` (`G(a→F b)`: (C)@0 holds, plain (B) fails), and
agrees with the C3/F13 fact that `G(a→F b)`'s terminal layer fails plain (B).
Membership round-trips on both witnesses confirm `𝓘 = L`. This bounds K-F2:
the floor divergence is the draft's, not a decider artifact.

## K-F4 — saturation reproduces raw exploration; CL(x) is closed (step 6) — CONFIRMED

At every entry cone / full-memory base of both witnesses' final layers, raw
ALG-5 `CL(x)` is closed under `(F₁,d₁),(F₂,d₂) ↦ (F₁∪F₂, M(d₁,d₂))`, and
saturating its **first-return loops** reproduces `CL(x)` exactly — the ALG-5
saturation route is sound. Checked on `gaFb` `{2,4}` k=0, and `floor` `{6}`
k=0 (|CL|=17) and k=1 (|CL| up to 262). (`first_returns` is the correct
generator set; a naïve edge-set-only prime extraction under-generates.)

Command: `python3 -m tests.cascade.k_e0_sat gaFb 0 | floor 0 | floor 1`.
Logs: `tests/cascade/logs/k_e0_sat_*.txt`.

## K-F5 — the sandwich scan detects both mechanisms (step 3) — CONFIRMED

The K-E7 sandwich scan over ALG-5's idempotent loop classes detects both
mandatory positive controls:

- **floor witness** (`{6}`, aperiodic): `absorption` — `e·z·e = z <_J e`, `e` an
  unflagged idempotent, `z=6` the zero (6 absorption + 2 non-splitting `other`
  at k=0; the mandatory absorption control fires).
- **`EvenBlocks`** (`{6}`, non-aperiodic): every failing pair is `group` —
  `f·z·f = z` (29 fails at k=2, 178 at k=3).

Mechanism (final classifier, K-F8): non-aperiodic ⟹ `group`; aperiodic with the
idempotent pair 𝒥-**comparable** (one dominates) ⟹ `absorption`; aperiodic with
the pair 𝒥-**equivalent** yet the sandwich still dropping ⟹ `other` (the
third-mechanism candidate, meaningful only when verdict-splitting). Scan is
`O(|E_id|²)` per `(x,F)` — piggybacks K-E1/E2.

Command: `python3 -m tests.cascade.k_e7_controls floor 0|floor 1|evenblocks 2|evenblocks 3`.
Logs: `tests/cascade/logs/k_e7_*.txt`.

## K-F6 — (B)-mode agrees with C3 wherever C3 decides (step 4) — CONFIRMED

The config decider's (B)-mode (window-projection grouping) matches C3
(`windows.realizable_verdicts`) at matching window width `k`: `GF(aa)` `{5}`
k=1 both FAIL, k=2 both PASS with **all 6 window-sets agreeing at the verdict
map level**; the floor `{6}` and `G(a→F b)` `{2,4}` layers both FAIL at k=0,1
on both sides. No disagreement; the F1 cap-false-PASS divergence (a known C3
limitation) does not arise on these layers.

Command: `python3 -m tests.cascade.k_e0_bcross`. Log:
`tests/cascade/logs/k_e0_bcross.txt`.

## K-F7 — every C3-undecided layer decides under (C) at k≤3 — CONFIRMED

Over the `flat_canon` census (4248 languages), C3 leaves **1164** final-layer
readings `UNDECIDED` (cap/budget guard tripped). The exact config (C)-decider
settles **all 1164** at width k≤3, **0 CONFLICT, 0 BUDGET**:

| decided width | aperiodic | non-aperiodic |
|---|---|---|
| k=0 | 438 | 476 |
| k=1 |  94 |  62 |
| k=2 |  94 |   0 |

The stratum is **not** all frozen: 322 have `|R|=1` (frozen), 842 are moving
(`|R|`=2..5). So dropping C3's window-grouping and running the exact loop-class
closure relieves the cap everywhere — no census-undecided layer is a genuine
(C)-conflict, so **Theorem C.12′'s floor is not extended by this stratum**. (Per
C.7 §8: the coverage bullet is 1164/1164.)

Command: `python3 -m tests.cascade.k_e1_sweep tests/cascade/logs/census_flat_canon.jsonl genaut/corpus/flat_canon/sos --out tests/cascade/logs/k_e1.csv`
(census regenerable by `python3 -m tests.sos2ltl.census_build genaut/corpus/flat_canon/sos --out tests/cascade/logs/census_flat_canon.jsonl`).
Output: `tests/cascade/logs/k_e1.csv` (regenerable).

## K-F8 — K-E7 census map: only absorption + group; no third verdict mechanism — CONFIRMED

The sandwich scan piggybacked on every K-E1 layer, with both mandatory controls
green (K-F5). Over the 1164-layer stratum:

- **absorption** present on 234 layers (aperiodic, one idempotent 𝒥-below the
  other — the floor-witness mechanism); **group** on 90 (non-aperiodic).
- **`other`** (aperiodic, 𝒥-equivalent idempotents whose sandwich still drops)
  present on 234 layers — but **0 of them verdict-splitting**. A non-splitting
  sandwich failure is not a (C)-conflict ("the identity is stronger than (C)",
  draft C.4); these are ordinary aperiodic 𝒥-class drops, not a verdict
  mechanism.

**No verdict-splitting `other` anywhere ⟹ no third mechanism in this stratum**
— consistent with C.4's two known mechanisms (group cancellation, zero
absorption). The `other_split` column is the third-mechanism flag for K-E2.

Command: same sweep as K-F7 (`other`, `other_split` columns).
Triage: `python3 -m tests.cascade.k_e7_triage <id> <layer> <k> other`.

## K-F9 — Prop C.19 transfer specimen: first moving-layer floor inhabitant — CONFIRMED

The transfer language `π₁⁻¹(GF(a∧X((!a&!b)U a))) ∩ π₂⁻¹(G(c→F d))` — over disjoint
AP sets, the conjunction `(GF(a∧X((!a&!b)U a))) ∧ (G(c→F d))` over `{a,b,c,d}` —
builds `𝓘` with 25 classes, aperiodic, and a **moving, 1-anchored terminal
layer `{21,24}`** (the predicted `{(z,2),(z,4)}`: the floor's frozen `z`
coordinate times `G(c→F d)`'s moving `{2,4}`).

The (C)-decider **conflicts at width 0 and width 1** (early-exit finder;
`|F|=2` then `6`, both based at class 21). ALG-7 verification on each: the two
reconstructed lassos share the recurring edge set yet **`inv.member` toggles**
(one accepts, one rejects — independent of the closure) and the induced linked
pairs are **non-conjugate** (Lemma C.11) — a **genuine** (C)-conflict, not a
closure bug. So the moving layer has no clean (C) width: **the first
moving-layer floor inhabitant**, confirming Prop C.19 and the transfer of the
floor witness's zero-absorption onto a moving layer.

k=2,3 hit BUDGET (|Σ_λ|=9, covered-set explosion) — a tooling limit; the
conflict is the window-blind `a·s^*·a` mechanism (Theorem C.12′) decorated by a
fixed `G(c→F d)` recurrence, so it persists at every width structurally.

Command: `python3 -m tests.cascade.k_e2_transfer`. Log:
`tests/cascade/logs/k_e2_transfer.txt`.

*(K-E2 steps 1/2 — the census frozen/moving stratum — are subsumed by K-F7: 0
conflicts over the 1164 census-undecided layers. The floor is thus **empty on
the census frame, inhabited beyond it** by the C.19 construction.)*

## K-F10 — Cor C.9 stratum empty: prefix-independence forces a frozen final layer — CONFIRMED

`PAPER-EDIT` (settles a ⟨TBD⟩, not a refutation): C.3's ⟨TBD⟩ "prefix-independence
forces the final layer frozen" and Cor C.9's applicability.

Decider-free scan of all 4248 census languages: of the **132 prefix-independent**
ones, **0 have a non-frozen final layer** — every prefix-independent language's
terminal layer is a frozen (all-neutral) SCC. So the Cor C.9 gating stratum
(prefix-independent ∧ terminal 1-anchored **non-frozen** final layer ∧
upward-closed ∧ parked-rejecting) is **empty on the census**: C.9's global bare-`Π₂`
form has no instances, and the config ladder's one-sided win (Cor C.8) is
confined to **non-prefix-independent** languages (e.g. `G(a→F b)`, K-F1). This is
the K-F2 mechanism generalized: the pending bit cannot survive in a
prefix-independent language's absorbing class.

One-sidedness of the moving final layers that *are* (C)-decided (56 with a
≥2-class collected `F`): **13 upward, 13 downward, 18 both, 12 neither** —
**balanced, not "predominantly upward"** as E3/C.8 predicted. (The precise E3
claim is about the `P|_R` recurrence rung; a rung-stratified recount is TODO,
but the raw distribution does not support upward-dominance.)

Commands: `python3 -m tests.cascade.k_e3_sweep tests/cascade/logs/census_flat_canon.jsonl genaut/corpus/flat_canon/sos --out tests/cascade/logs/k_e3.csv`
and `python3 -m tests.cascade.k_e3_pfxind tests/cascade/logs/census_flat_canon.jsonl genaut/corpus/flat_canon/sos`.
Logs: `tests/cascade/logs/k_e3.csv` (regenerable), `tests/cascade/logs/k_e3_pfxind.txt`.
