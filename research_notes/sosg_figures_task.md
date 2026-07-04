# Task — collect & tabulate the figures/tables for "The SOSG, Constructed"

*For a code-focused session. Produce the companion artifact the paper
[`sosg_constructed.md`](sosg_constructed.md) points at, replacing its `[Figure N]` /
`[Table N]` placeholders with real, verified content. You edit only the figures file;
do **not** touch the paper prose.*

## Deliverable

One markdown file `research_notes/sosg_figures.md` (split into a `sosg_figures/` dir
only if it grows unwieldy), containing Figures 1–2 and Tables 1–3 below, each under a
stable heading the paper can link to (`## Figure 1`, `## Table 2`, …). Each item is
**paper-facing** — clean caption, no tool talk in the caption itself — but carries a
one-line *provenance* footer (`<!-- from: <probe> <hoa> -->`) so it can be
regenerated. Also commit the three HOA fixtures you build (paths noted per example).

## The three running examples — build and verify each

Build the deterministic Emerson–Lei form, save as HOA, and **verify it recognizes the
intended language** (Spot equivalence against the source) before tabulating.

| name | language | PSL/SERE source | build / note |
|---|---|---|---|
| `GF(aa)` | `GF(a ∧ Xa)`, infinitely many `aa` | `G F (a & X a)` | **two presentations:** (a) the run-parity form = existing `samples/fixtures/hoa/definability/gf_aa_parity.hoa` (carries the `Z₂`); (b) a minimal reset form via `ltl2tgba -D`. Both needed (Table 3 uses (a); the §5 canonicity check needs both). |
| `Even` | `(aa)*·b·Σ^ω` — even #`a`, then `b`, then anything | prefix matches SERE `{a[*2]}[*] ; b` | build from the SERE via the PSL front end; if the operator semantics differ, fall back to the hand automaton: states `q0(even)/q1(odd)/acc/rej`, `a: q0↔q1`, `b: q0→acc,q1→rej`, `acc/rej` sinks, accept = reach `acc`. Save under `samples/fixtures/hoa/sosg/even.hoa`. |
| `EvenBlocks` | ∞ many `b`, eventually every completed `a`-block even | `GF b ∧ FG {a[*2]}·b`-style over blocks | build via the front end; **prefix-independent**, `Fin∧Inf`. Save `samples/fixtures/hoa/sosg/evenblocks.hoa`. If awkward to pin, report back and propose an alternative prefix-independent mod-2 rather than guessing. |

## Numbers → which probe produces them

Run single-input, ≤15 s each, long output to `tests/**/logs/`:

- `tests/probes/oracle_dump.py <hoa>` → `|EM¹|`, residual classes on `Q`, seed classes,
  `|S(L)₊¹|`, the aperiodic/group verdict, and (on non-LTL) the certificate family
  `(u, v, x|y, p)` with its shape `F₁`/`F₂`.
- `tests/probes/dg_dump.py <hoa>` → the keyed class list, the multiplication table, the
  letter map, `P` (accepting linked pairs), and the linked-pair enumeration.
- `tests/probes/dg_probe.py <hoa>` → the synthesized LTL formula + its Spot-equivalence
  check (for the `GF(aa)` formula cell).

## Figures & tables to produce (map to the paper placeholders)

- **Figure 1** — the three `D`, as fenced HOA blocks: `GF(aa)` (run-parity form),
  `Even`, `EvenBlocks`. Caption states `|Q|`, the letters, and the acceptance for each.
- **Table 1** — fingerprints, one row per example. Columns:
  `example | PSL/SERE | |Q| | |EM¹| | |S(L)₊¹| | group in transition monoid? | group in
  S(L)₊? | LTL? | certificate shape or synthesized formula`.
- **Table 2** — `EM(GF(aa))` (run-parity form): the `⟦·⟧ = (st, mk)` vectors of all
  elements, the right-multiplication table, and the surjection onto the `S(L)₊` classes.
  Paper prose says **10 elements → 6 classes**; if the dump disagrees, that is a finding
  to report, not to overwrite.
- **Table 3** — `S(GF(aa))₊`: the keyed classes (`[ε],[¬a],[a],[¬a·a],[a·¬a],[a·a]`),
  the multiplication table, and the accepting linked pair (expected `([a·a],[a·a])`).
  Add a companion column/table for `S(Even)₊` showing the class that **retains period 2**
  (the surviving `Z₂`).
- **Figure 2** — the exportable invariant `𝓘(GF(aa))`: a "semantic HOA" block listing
  keyed classes, letter map, multiplication table, accepting-pair set — the
  serialization two tools would compare byte-for-byte.

## Cross-checks (report any failure as a finding, do not paper over)

1. **Canonicity (headline).** `𝓘(GF(aa))` from presentation (a) and from (b) must be
   **identical** after canonical keying. `tests/probes/dg_canon.py` does exactly this
   assertion — run it; a mismatch is a real problem to flag.
2. **Verdicts.** `GF(aa)` → LTL (aperiodic quotient) with a synthesized formula
   Spot-equivalent to `G F (a & X a)`. `Even`, `EvenBlocks` → NOT_LTL. Expected
   certificate shapes: `Even` → `F₁` (linear); `EvenBlocks` → `F₂` (ω-power). If either
   comes back the other shape, flag it — it contradicts §6.2's prose.
3. **Sanity.** `|S(L)₊¹| ≤ |EM¹|` in every row; `Even`/`EvenBlocks` residual counts
   consistent with prefix-independence (`EvenBlocks` should show **one** residual class).
4. **Language identity.** Each built HOA Spot-equivalent to its PSL/SERE source.

## Rules

- The figures file is paper-facing prose + tables; keep probe/tool names out of
  captions (they live only in the provenance footers).
- Do not invent or round numbers. Every value traces to a probe run whose log you keep.
- Any discrepancy between a probe and the paper's stated numbers (e.g. `10 → 6`) is a
  **finding** reported back to the theory session — the paper prose may be what needs
  fixing, and that is our call, not yours.
- Discipline per `CLAUDE.md`: single-input probes, ≤15 s, logs under `tests/**/logs/`,
  no `/tmp`.
