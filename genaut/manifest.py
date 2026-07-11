"""genaut/manifest.py — the bench manifest, parsed from the corpus census reports.

The rev.2 classifier report (`research_notes/sos_classification_spec.md` §5) requires a
**bench manifest**: one row per censused shape × acceptance family, tracing the
reduction funnel and carrying the enumeration abundance and the algebra-size
spread. Every number here is already exported at build time — this script only
parses and joins, it recomputes nothing:

  corpus/tgba/<tag>/census.md   the generation funnel: combos (generator-id space)
                                -> byte-distinct (md5, post Spot reduce) -> kept
                                (AP-canonical survivors);  gen/enumerate.py.
  corpus/det/<tag>/census.md    the language dedup: kept -> distinct languages (the
                                syntactic `𝓘` key), the collapse ratio, the
                                per-language enumeration abundance (median / max),
                                and the `N = |𝒞|` spread (min / median / max);
                                gen/canonize.py.
  corpus/sampled/<tag>__seed<label>/   a non-exhaustive folder past the
                                tractability wall. A raw probe carries a
                                sample.json (id-space size, draws spent, cap); a
                                curated selection adopted from a campaign
                                (label `curated`) has none, so its row carries
                                only the language count. The folder is
                                authoritative for the live count (sample.json's
                                `languages` is an in-run checkpoint).

The acceptance family is the tag suffix (`_parity`), the bare tag being generalized
Büchi (`gba`). Output is a Markdown table (SHAPES.md's idiom), written to
`logs/genaut/corpus/MANIFEST.md` and echoed to stdout.

  python3 genaut/manifest.py            # -> logs/genaut/corpus/MANIFEST.md
"""
from __future__ import annotations

import glob
import json
import os
import re
from typing import Dict, List, Optional

HERE = os.path.dirname(__file__)
_CORPUS = os.path.join(HERE, "corpus")
# A generated report is not source: beside the corpus, under the write root.
_OUT = os.path.normpath(os.path.join(HERE, os.pardir, "logs", "genaut", "corpus"))

_TAG = re.compile(r"(\d+)state(\d+)ap(\d+)acc(?:_(\w+))?")

# tgba/<tag>/census.md — the generation funnel.
_GEN = {
    "n": r"nstates=(\d+)", "k": r"naps=(\d+)", "c": r"nacc=(\d+)",
    "combos": r"combos \(generator-id space N\):\s*(\d+)",
    "byte": r"byte-distinct \(md5[^)]*\):\s*(\d+)",
    "kept": r"kept \(AP-canonical survivors\):\s*(\d+)",
}
# det/<tag>/census.md — the language dedup + shape descriptors.
_LANG = {
    "langs": r"distinct languages \(syntactic[^)]*\):\s*(\d+)",
    "ab_med": r"abundance per language: median (\d+)",
    "ab_max": r"abundance per language:[^,]*, max (\d+)",
    "n_min": r"over languages:\s*(\d+)\s*/\s*\d+\s*/\s*\d+",
    "n_med": r"over languages:\s*\d+\s*/\s*(\d+)\s*/\s*\d+",
    "n_max": r"over languages:\s*\d+\s*/\s*\d+\s*/\s*(\d+)",
}


def _grab(text: str, pats: Dict[str, str], where: str) -> Dict[str, int]:
    """Apply every named pattern to `text`; missing field is a hard error."""
    out: Dict[str, int] = {}
    for name, pat in pats.items():
        m = re.search(pat, text)
        if not m:
            raise ValueError(f"{where}: field {name!r} not found")
        out[name] = int(m.group(1))
    return out


def acc_family(tag: str) -> str:
    """The acceptance family a tag carries: its suffix, or `gba` when bare."""
    m = _TAG.match(tag)
    return m.group(4) if (m and m.group(4)) else "gba"


def exhaustive_rows(corpus: str) -> List[Dict[str, object]]:
    """One joined row per censused shape (tgba funnel + det dedup)."""
    rows: List[Dict[str, object]] = []
    for path in glob.glob(os.path.join(corpus, "tgba", "*", "census.md")):
        tag = os.path.basename(os.path.dirname(path))
        row: Dict[str, object] = {"tag": tag, "acc": acc_family(tag)}
        row.update(_grab(open(path).read(), _GEN, path))
        det = os.path.join(corpus, "det", tag, "census.md")
        if os.path.isfile(det):
            row.update(_grab(open(det).read(), _LANG, det))
        rows.append(row)
    rows.sort(key=lambda r: (r["n"], r["k"], r["c"], r["acc"]))
    return rows


def sample_rows(corpus: str) -> List[Dict[str, object]]:
    """One row per `sampled/<tag>__seed<label>/` folder, its live language count
    read off the folder (authoritative — sample.json's own count is an in-run
    checkpoint). Probe statistics (id-space, draws, cap) come from sample.json
    when present; a curated selection has no sample.json and keeps only the
    count."""
    rows: List[Dict[str, object]] = []
    for folder in glob.glob(os.path.join(corpus, "sampled", "*")):
        name = os.path.basename(folder)
        tag, sep, label = name.partition("__seed")
        m = _TAG.match(tag)
        if not (os.path.isdir(folder) and sep and m):
            continue
        row: Dict[str, object] = {
            "tag": tag, "seed": label, "acc": acc_family(tag),
            "n": int(m.group(1)), "k": int(m.group(2)), "c": int(m.group(3)),
            "langs_live": len(glob.glob(os.path.join(folder, "sos", "*.sos"))),
        }
        sj = os.path.join(folder, "sample.json")
        if os.path.isfile(sj):
            j = json.load(open(sj))
            row.update({
                "combos": j.get("num_combos"), "draws": j.get("draws"),
                "langs_json": j.get("languages"), "capped": j.get("capped"),
                "exhaustive": j.get("exhaustive"),
            })
        rows.append(row)
    rows.sort(key=lambda r: (r["n"], r["k"], r["c"], r["acc"], str(r["seed"])))
    return rows


def _cell(row: Dict[str, object], key: str, fmt: str = "{}") -> str:
    v = row.get(key)
    return "—" if v is None else fmt.format(v)


def render(corpus: str) -> str:
    ex = exhaustive_rows(corpus)
    sa = sample_rows(corpus)
    out: List[str] = [
        "# genaut bench manifest — the reduction funnel per shape × acceptance family",
        "",
        "Parsed from the corpus census reports by `python3 genaut/manifest.py` "
        "(recomputes nothing — see the script's doc for the sources). `collapse` is "
        "`kept / langs`, the automaton→language compression the `𝓘` dedup achieves; "
        "`abundance` is how many enumerated automata realise one language "
        "(median / max); `N = |𝒞|` is the syntactic-algebra size spread over the "
        "shape's languages.",
        "",
        "## Exhaustive census (small shapes, every language)",
        "",
        "| shape | n | k | c | acc | combos | byte-distinct | kept | langs "
        "| collapse | abundance med/max | N min/med/max |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in ex:
        langs = r.get("langs")
        collapse = (f"{r['kept'] / langs:.2f}x"
                    if isinstance(langs, int) and langs else "—")
        ab = ("—" if "ab_med" not in r
              else f"{r['ab_med']} / {r['ab_max']}")
        nsz = ("—" if "n_min" not in r
               else f"{r['n_min']} / {r['n_med']} / {r['n_max']}")
        out.append(
            f"| `{r['tag']}` | {r['n']} | {r['k']} | {r['c']} | {r['acc']} "
            f"| {r['combos']} | {r['byte']} | {r['kept']} | {_cell(r, 'langs')} "
            f"| {collapse} | {ab} | {nsz} |")

    if sa:
        out += [
            "",
            "## Non-exhaustive samples (past the tractability wall)",
            "",
            "A uniform random probe of the id space (rows with probe stats), or a "
            "curated selection adopted from a campaign (`seed` = `curated`, no "
            "probe stats) — never a complete census. `langs` is the live folder "
            "count.",
            "",
            "| shape | seed | acc | id-space | draws | langs (live) | capped |",
            "|---|---|---|---|---|---|---|",
        ]
        for r in sa:
            out.append(
                f"| `{r['tag']}` | {_cell(r, 'seed')} | {r['acc']} "
                f"| {_cell(r, 'combos')} | {_cell(r, 'draws')} "
                f"| {r['langs_live']} | {_cell(r, 'capped')} |")
    return "\n".join(out) + "\n"


def main(argv=None) -> None:
    import argparse
    ap = argparse.ArgumentParser(prog="manifest")
    ap.add_argument("--corpus", default=_CORPUS, help="corpus root to READ")
    ap.add_argument("--out", default=_OUT, help="corpus root to WRITE MANIFEST.md under")
    args = ap.parse_args(argv)
    os.makedirs(args.out, exist_ok=True)
    out_path = os.path.join(args.out, "MANIFEST.md")
    table = render(args.corpus)
    with open(out_path, "w") as f:
        f.write(table)
    print(table)
    print(f"[wrote {out_path}]")


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
