# tests/sosg/

Tools that read the **syntactic ω-semigroup `S(L)₊`** (the SOSG) off a
deterministic automaton and present it — the collection campaign behind the
paper [`research_notes/sosg_constructed.md`](../../research_notes/sosg_constructed.md)
and its figures folder [`research_notes/sosg_figs/`](../../research_notes/sosg_figs).

Everything runs as a module from the repo root (see [`../README.md`](../README.md)
for the import discipline); each is single-input and self-bound.

## Source map

| script | reads | produces |
|---|---|---|
| `build_sosg.py` | one HOA file **or** LTL/PSL formula | plain-text dump of *every* table part for that one language — the Figure-1 line, the Table-1 fingerprint row, the `EM(D)` elements with `(st, mk)` vectors and their surjection onto `S(L)₊`, the canonical algebra `S(L)₊¹`, and (with `--sosg PATH`) the `.sosg` invariant serialization. Also exports the reusable compute helpers the other scripts import. |
| `assemble.py` | one or more `label=input` specs | a single renderable **Markdown** algebra report (a leading fingerprint table + one section per input). Reuses `build_sosg.py`; the generic "what algebra does this automaton hold" diagnosis tool, and the raw material `figures.md` is curated from. |
| `render_svg.py` | one HOA file **or** formula | the automaton drawn as Spot draws it: `.svg` (Spot's own `_repr_svg_`) or `.png` (rasterized by `rsvg-convert` to a fixed, page-safe width, aspect preserved). |

Dependency edge: `assemble.py` → `build_sosg.py` → `tests/probes/dg_common.py`
(the shared pipeline preamble: deterministic form → `EM(D)` closure → refined
quotient → frozen canonical algebra `Alg`).

## Inputs and outputs

- **Fixtures** consumed/produced: `samples/fixtures/hoa/sosg/` — the four HOA
  automata (`gf_aa_parity`, `gf_aa_reset`, `even`, `evenblocks`) and their
  committed `.sosg` invariants.
- **Deliverable** these feed: `research_notes/sosg_figs/` — `figures.md` (curated,
  with PNGs under `img/`) and `reproduction.md` (the exact command sequence).
- **`logs/`** — scratch output (gitignored): the generic `assemble.py` report,
  probe transcripts, and `render_svg.py`'s formula-input scratch HOAs.

## Related probes (in `tests/probes/`)

`oracle_dump.py` (pipeline stations + certificate family), `dg_dump.py` (the
frozen algebra table by table), `dg_probe.py` (synthesize the defining LTL
formula and verify it Spot-equivalent). `build_sosg.py` subsumes their table
content for a single-shot summary; the probes remain the finer-grained windows.
