# aut2ltl.roundtrip — source map

One idea at four scopes: hand a labeler a **fresh presentation** of the same
ω-language (re-describe a faithful-but-ugly formula, or a located subformula) and let
it re-derive a smaller equivalent one — faithful by construction, never post-hoc.
Each entry has its own `algorithm.md`; read those for the construction.

## Package map

| entry | kind | scope re-presented | details |
|---|---|---|---|
| `roundtrip.py` | Rewriter | one located node | `algorithm.md` |
| `roundtrip_decomp/` | Rewriter | a located node's operands | `roundtrip_decomp/algorithm.md` |
| `roundtrip_deep/` | Rewriter | the whole formula DAG, bottom-up | `roundtrip_deep/algorithm.md` |
| `roundtrip_top/` | Translator | the whole input language | `roundtrip_top/algorithm.md` |

All four are re-exported from `__init__`, so callers import them from
`aut2ltl.roundtrip` regardless of where each lives.

Shared by the two finder-driven Rewriters (`roundtrip`, `roundtrip_decomp`):

- `finder.py` — the `Finder` node-locator contract.
- `cutpoints/` — concrete finders (`root`, `toplevel`).
- `subst.py` — hash-cons-identity substitution.

`roundtrip_deep` and `roundtrip_top` share none of these — a bottom-up descent, resp. a
language seed, stands in for the finder.

## Two levels

The three **Rewriters** (`LTLResult → LTLResult`) re-present the structure of a formula
already in hand. The one **Translator** (`Language → Label`, `Roundtrip`) re-presents a
language with no formula yet — it seeds one from a child labeler, then relabels the
re-description.
