"""Render a Markdown algebra report for one or more inputs — the generic
diagnosis tool behind the paper's SoS figures.

For each input (an HOA file or an LTL/PSL formula) it reads off the canonical
syntactic ω-semigroup `S(L)₊` and emits a renderable Markdown section: the
deterministic form as an HOA block, the enriched monoid `EM(D)` with the
surjection onto `S(L)₊`, the canonical algebra (keyed classes, class
multiplication matrix, letter map, accepting linked pairs), and the `.sos`
serialization of the invariant `𝓘(L)` (with its optional residual trailer). A
leading fingerprint table compares all inputs at a glance. Nothing here is
example-specific — it summarizes whatever algebra the input automaton holds.

Usage (module run from repo root):
  python3 -m tests.sos.assemble OUT.md  <spec> [<spec> ...]
    where each <spec> is  `label=input`  or just  `input`
    and input is an HOA path or an LTL/PSL formula string.

Single pass, self-bound per input; a closure that blows the cap is reported in
the row and the section is skipped.
"""
from __future__ import annotations

import os
import sys
from typing import List, Optional, Tuple

from tests.probes.dg_common import DgData, quotient_of_hoa
from tests.sos.build_sos import (
    to_hoa_path,
    transition_monoid_has_group,
    certificate_or_formula,
    li_of_masks,
    em_surjection,
)
from sosl.objects import Invariant, Residuals, dump_invariant
from sosl.objects.alphabet import Letter
from sosl.objects.serialize import render_letter, render_word
from sosl.reference import reference_of_hoa, residuals_of_hoa


def md_table(header: List[str], rows: List[List[str]]) -> List[str]:
    """A GitHub-flavored Markdown table."""
    out = ["| " + " | ".join(header) + " |",
           "|" + "|".join("---" for _ in header) + "|"]
    out += ["| " + " | ".join(r) + " |" for r in rows]
    return out


def matrix_block(header: List[str], rows: List[List[str]]) -> List[str]:
    """A right-aligned fenced matrix (HOA/matrix-community style)."""
    w = [max(len(header[c]), *(len(r[c]) for r in rows)) for c in range(len(header))]
    out = ["```",
           "  ".join(h.rjust(w[c]) for c, h in enumerate(header))]
    for r in rows:
        out.append("  ".join(v.rjust(w[c]) for c, v in enumerate(r)))
    out.append("```")
    return out


def em_rows(data: DgData, inv: Invariant, surj: dict) -> List[List[str]]:
    mon = data.mon
    ab = inv.alphabet
    rows: List[List[str]] = []
    for ei in range(len(mon)):
        word = ";".join(data.names[li] for li in mon.rep[ei]) or "eps"
        st = "[" + " ".join(str(dst) for (dst, _m) in mon.elems[ei]) + "]"
        mk = "[" + " ".join(
            "{" + ",".join(map(str, sorted(m))) + "}" if m else "{}"
            for (_d, m) in mon.elems[ei]) + "]"
        rmul = " ".join(f"{mon.right[ei][li]}" for li in range(len(data.names)))
        hosted = " / ".join(
            f"{c} `{render_word(ab, inv.keys[c])}`" for c in surj[ei])
        rows.append([str(ei), f"`{word}`", st, mk, rmul, hosted])
    return rows


def section(label: str, inp: str, data: DgData, inv: Invariant,
            res: Residuals) -> List[str]:
    """The full Markdown section for one input."""
    ab = inv.alphabet
    k = inv.n
    surj = em_surjection(data, inv, li_of_masks(data, ab))
    out: List[str] = [f"## {label}", ""]
    out.append(f"*Input:* `{inp}`")
    out.append("")

    out.append("### Deterministic form `D`")
    out.append("")
    out.append("```hoa")
    # 't' forces transition-based acceptance in the dump, so a terminal-Büchi
    # form (state-representable, which Spot would otherwise print state-based)
    # still shows its marks on transitions — consistent with EM(D) reading
    # marks along runs, and with the other examples.
    out.append(data.aut.to_str("hoa", "t").rstrip())
    out.append("```")
    out.append("")

    out.append("### Enriched monoid `EM(D)` → `S(L)₊`")
    out.append("")
    out.append(f"`|EM¹| = {len(data.mon)}` elements folding onto "
               f"`|S(L)₊¹| = {k}` classes. `rmul` is right-multiplication by "
               f"each letter ({', '.join('`'+n+'`' for n in data.names)}), as "
               "`EM` element ids. The identity element hosts two classes "
               "(`[eps]` and any neutral non-empty class).")
    out.append("")
    out += md_table(["id", "word", "st", "mk", "rmul", "→ class"],
                    em_rows(data, inv, surj))
    out.append("")

    out.append("### Canonical algebra `S(L)₊¹`")
    out.append("")
    cls_rows = [[str(i), f"`{render_word(ab, inv.keys[i])}`",
                 "✓" if inv.mult[i][i] == i else ""] for i in range(k)]
    out += md_table(["class", "key (shortlex-least word)", "idem"], cls_rows)
    out.append("")
    out.append("*Letter map:* " + ", ".join(
        f"`{render_letter(ab, Letter(a))}` → {inv.letter_class[a]}"
        for a in range(ab.size)) + ".")
    out.append("")
    out.append("*Multiplication* (row `i` · col `j`):")
    out.append("")
    mheader = ["·"] + [str(j) for j in range(k)]
    mrows = [[str(i)] + [str(inv.mult[i][j]) for j in range(k)] for i in range(k)]
    out += matrix_block(mheader, mrows)
    out.append("")
    ap = sorted(inv.accept)
    out.append(f"*Accepting linked pairs* ({len(ap)} of {len(inv.linked_pairs())}): "
               + (", ".join(f"`([{render_word(ab, inv.keys[s])}],"
                            f"[{render_word(ab, inv.keys[e])}])`" for (s, e) in ap)
                  or "none") + ".")
    out.append("")

    out.append("### Invariant `𝓘(L)` — `.sos` serialization")
    out.append("")
    out.append("```")
    out.append(dump_invariant(inv, residuals=res).rstrip())
    out.append("```")
    out.append("")
    return out


def parse_spec(spec: str) -> Tuple[str, str]:
    """`label=input` → (label, input); a bare input derives a label from it."""
    if "=" in spec and not os.path.isfile(spec):
        label, inp = spec.split("=", 1)
        return label.strip(), inp.strip()
    if os.path.isfile(spec):
        return os.path.splitext(os.path.basename(spec))[0], spec
    return spec, spec


def main(argv: List[str]) -> int:
    if len(argv) < 3:
        print(__doc__)
        return 1
    out_path = argv[1]
    specs = [parse_spec(s) for s in argv[2:]]

    scratch = os.path.join(os.path.dirname(__file__), "logs")
    built: List[Tuple[str, str, Optional[DgData], Optional[Invariant],
                      Optional[Residuals]]] = []
    for i, (label, inp) in enumerate(specs):
        # a distinct scratch file per formula input so they do not clobber.
        sub = os.path.join(scratch, f"_in{i}")
        path = to_hoa_path(inp, sub) if not os.path.isfile(inp) else inp
        data = quotient_of_hoa(path)
        inv = reference_of_hoa(path) if data is not None else None
        res = residuals_of_hoa(path) if data is not None else None
        built.append((label, inp, data, inv, res))

    names = ", ".join(label for label, *_ in built)
    doc: List[str] = [f"# SoS algebra summary — {names}", ""]
    doc.append("Canonical syntactic ω-semigroup `S(L)₊` read off each input "
               "automaton. `TM` = transition monoid; a group in `TM` may be a "
               "presentation artifact, a group in `S(L)₊` is intrinsic "
               "(⇔ not LTL-definable).")
    doc.append("")
    doc.append("## Fingerprints")
    doc.append("")
    fp_rows: List[List[str]] = []
    for label, _inp, data, inv, _res in built:
        if data is None:
            fp_rows.append([label, "—", "cap", "—", "—", "—", "—", "closure blew the cap"])
            continue
        fp_rows.append([
            label,
            str(data.aut.num_states()),
            str(len(data.mon)),
            str(inv.n),
            "yes" if transition_monoid_has_group(data) else "no",
            "yes" if data.group is not None else "no",
            "yes" if data.group is None else "no",
            certificate_or_formula(data),
        ])
    doc += md_table(
        ["input", "\\|Q\\|", "\\|EM¹\\|", "\\|S(L)₊¹\\|",
         "grp TM", "grp S(L)₊", "LTL?", "evidence"],
        fp_rows)
    doc.append("")

    for label, inp, data, inv, res in built:
        if data is None:
            doc += [f"## {label}", "", f"*Input:* `{inp}` — closure blew the cap.", ""]
            continue
        doc += section(label, inp, data, inv, res)

    with open(out_path, "w") as fh:
        fh.write("\n".join(doc) + "\n")
    print(f"wrote {out_path}  ({len(built)} inputs)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
