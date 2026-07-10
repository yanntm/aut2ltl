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
  Per the spec decision rule (§4, K-E0 *Decision*), a mismatch stops K-E1–K-E5
  pending the paper edit. **K-E1–K-E5: BLOCKED on the C.3 revision.**
- Steps 4 (C3 (B)-mode cross-check) and 6 (saturation/raw agreement) not yet
  run; the decider is already cross-validated indirectly (K-F1 vs K-F3).

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
the floor divergence is the draft's, not a decider artifact. (Direct C3
(B)-mode cross-check — K-E0 step 4 — and the saturation/raw agreement — step 6
— still pending, but not load-bearing for the K-F2 attribution.)
