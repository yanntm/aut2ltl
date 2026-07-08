"""Build `corpus/flat/` — the cross-shape union of distinct languages.

Every shape's `det/`+`sos/` tier is language-deduped *within* that shape, but the
same language recurs across shapes: a bigger shape emits a superset of a smaller
one's languages (more states / colours / a parity acceptance over the same
alphabet). This stage folds that redundancy into a single pool, keeping **one**
representative per language — the one from the **smallest** shape that emits it, so
the kept `<tag>_<id>` filename traces the language to its minimal setting.

    corpus/flat/det/   the canonical D (HOA) of each distinct language, one file,
                       named for the smallest shape that emits it.
    corpus/flat/sos/   the paired syntactic 𝓘 (.sos), same basename.
    corpus/flat/census.md + flat.json   the composition report.

Dedup notion. **Language identity up to a fixed AP labeling**: the `.sos` key of
`survey.normalize.sos` ([SωS26, Thm. 5.1]: byte-equal ⟺ equal language). `GF(a)`
and `GF(!a)` stay distinct — folding relabel/polarity twins is a *later* work item
(README "Polarity / relabeling"). Cross-`k` languages never collide (a different
alphabet is a different canonical D, hence a different `.sos`).

Traversal order. Shapes are visited in a linear extension of the subset order —
`(n, k, c, family)` ascending with `gba < parity` — so the first appearance of a
language is at its minimal shape. The **exhaustive** census shapes come first;
the **sampled** (non-exhaustive, beyond-the-wall) folders are appended last and
contribute only languages no exhaustive shape reached.

    python3 genaut/gen/flatten.py                 # (re)build corpus/flat/
    python3 genaut/gen/flatten.py --exclude 2state2ap0acc  # (default) drop dominators
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from collections import Counter
from typing import Dict, List, NamedTuple, Optional, Tuple

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
from survey.normalize.sos import sos_key                   # noqa: E402

_CORPUS = os.path.normpath(
    os.path.join(os.path.dirname(__file__), os.pardir, "corpus"))

# Heavy shapes whose sheer language count dominates any composition read (their
# large-alphabet blow-up is a separate concern); excluded from flat by default.
_DEFAULT_EXCLUDE = ("2state2ap0acc",)

_TAG_RE = re.compile(r"^(\d+)state(\d+)ap(\d+)acc(_parity)?$")


class Source(NamedTuple):
    """One tier folder feeding flat: its shape tag, sort key, and the paired
    det/sos directories to walk."""
    tag: str
    n: int
    k: int
    c: int
    family: str                # "gba" | "parity"
    exhaustive: bool
    det_dir: str
    sos_dir: str

    @property
    def order(self) -> Tuple[int, int, int, int, int]:
        """Linear extension of the subset order: smaller shape first, gba before
        parity, and every exhaustive source before every sampled one."""
        fam = 1 if self.family == "parity" else 0
        return (0 if self.exhaustive else 1, self.n, self.k, self.c, fam)


def _parse_tag(tag: str) -> Optional[Tuple[int, int, int, str]]:
    m = _TAG_RE.match(tag)
    if not m:
        return None
    return int(m.group(1)), int(m.group(2)), int(m.group(3)), \
        ("parity" if m.group(4) else "gba")


def discover(corpus: str, exclude: Tuple[str, ...]) -> List[Source]:
    """Every exhaustive shape (`corpus/det/<tag>`) plus every sampled folder
    (`corpus/sampled/<tag>__seed*/`), as `Source`s in traversal order."""
    out: List[Source] = []
    det_root = os.path.join(corpus, "det")
    for tag in sorted(os.listdir(det_root)):
        if tag in exclude or not os.path.isdir(os.path.join(det_root, tag)):
            continue
        parsed = _parse_tag(tag)
        if parsed is None:
            continue
        n, k, c, family = parsed
        out.append(Source(tag, n, k, c, family, True,
                          os.path.join(det_root, tag),
                          os.path.join(corpus, "sos", tag)))
    sampled_root = os.path.join(corpus, "sampled")
    if os.path.isdir(sampled_root):
        for name in sorted(os.listdir(sampled_root)):
            base = os.path.join(sampled_root, name)
            tag = name.split("__seed", 1)[0]
            parsed = _parse_tag(tag)
            if parsed is None or not os.path.isdir(os.path.join(base, "sos")):
                continue
            if tag in exclude:
                continue
            n, k, c, family = parsed
            out.append(Source(name, n, k, c, family, False,
                              os.path.join(base, "det"),
                              os.path.join(base, "sos")))
    return sorted(out, key=lambda s: s.order)


def flatten(corpus: str, exclude: Tuple[str, ...]) -> Dict:
    """Copy one representative per distinct language into `corpus/flat/`, keeping
    the smallest-shape source, and return the composition record."""
    flat_det = os.path.join(corpus, "flat", "det")
    flat_sos = os.path.join(corpus, "flat", "sos")
    for d in (flat_det, flat_sos):
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d, exist_ok=True)

    sources = discover(corpus, exclude)
    seen: Dict[str, str] = {}                 # language key -> owning source tag
    rows: List[Dict] = []                     # per-source contribution
    total = 0
    for src in sources:
        sos_files = sorted(f for f in os.listdir(src.sos_dir) if f.endswith(".sos"))
        new = 0
        for fname in sos_files:
            ident = fname[:-4]                # <tag>_<id>
            with open(os.path.join(src.sos_dir, fname)) as fh:
                key = sos_key(fh.read())
            if key in seen:
                continue                      # a smaller shape already owns it
            det_src = os.path.join(src.det_dir, ident + ".hoa")
            if not os.path.isfile(det_src):
                continue                      # unpaired sos — skip defensively
            seen[key] = src.tag
            shutil.copyfile(det_src, os.path.join(flat_det, ident + ".hoa"))
            shutil.copyfile(os.path.join(src.sos_dir, fname),
                            os.path.join(flat_sos, ident + ".sos"))
            new += 1
        total += new
        rows.append({
            "source": src.tag, "n": src.n, "k": src.k, "c": src.c,
            "family": src.family, "exhaustive": src.exhaustive,
            "scanned": len(sos_files), "new_langs": new, "cumulative": total,
        })

    record = {
        "corpus": "flat",
        "excluded": list(exclude),
        "sources": len(sources),
        "total_langs": total,
        "rows": rows,
        "by_family": dict(_tally(rows, "family")),
        "by_exhaustive": {"exhaustive": sum(r["new_langs"] for r in rows if r["exhaustive"]),
                          "sampled": sum(r["new_langs"] for r in rows if not r["exhaustive"])},
        "by_colours": dict(_tally(rows, "c")),
    }
    _write_census(os.path.join(corpus, "flat"), record)
    with open(os.path.join(corpus, "flat", "flat.json"), "w") as fh:
        json.dump(record, fh, indent=2)
    return record


def _tally(rows: List[Dict], field: str) -> Counter:
    t: Counter = Counter()
    for r in rows:
        t[r[field]] += r["new_langs"]
    return t


def _write_census(flat_dir: str, r: Dict) -> None:
    """The automated census + composition report for the flat pool."""
    lines: List[str] = []
    lines.append("# flat — cross-shape union of distinct languages\n")
    lines.append(
        f"One representative per distinct language ({r['total_langs']} in all), "
        f"pooled from {r['sources']} shape sources and deduped by language "
        f"identity (the `.sos` `𝓘` key, [SωS26 Thm. 5.1], up to a fixed AP "
        f"labeling — relabel/polarity twins are kept, a later work item). Each "
        f"language is kept from the **smallest** shape that emits it, so the "
        f"`<tag>_<id>` filename traces it to its minimal setting.\n")
    if r["excluded"]:
        lines.append(
            f"Excluded (alphabet-blow-up dominators): "
            f"{', '.join('`' + e + '`' for e in r['excluded'])}.\n")

    lines.append("\n## Composition\n")
    lines.append("| axis | bucket | languages |")
    lines.append("|---|---|--:|")
    for fam, v in sorted(r["by_family"].items()):
        lines.append(f"| acceptance family | `{fam}` | {v} |")
    for kind, v in r["by_exhaustive"].items():
        lines.append(f"| provenance | {kind} | {v} |")
    for c, v in sorted(r["by_colours"].items(), key=lambda kv: int(kv[0])):
        lines.append(f"| acceptance colours | c={c} | {v} |")
    lines.append(f"| **total** | | **{r['total_langs']}** |")

    lines.append("\n## Contribution by source (traversal order)\n")
    lines.append("A source's `new` is the languages first seen there — those a "
                 "smaller shape did not already own.\n")
    lines.append("| # | source | n | k | c | family | tier | scanned | new | cumulative |")
    lines.append("|--:|---|--:|--:|--:|---|---|--:|--:|--:|")
    for i, row in enumerate(r["rows"], 1):
        tier = "exhaustive" if row["exhaustive"] else "**sampled**"
        lines.append(
            f"| {i} | `{row['source']}` | {row['n']} | {row['k']} | {row['c']} | "
            f"{row['family']} | {tier} | {row['scanned']} | {row['new_langs']} | "
            f"{row['cumulative']} |")

    lines.append("\nBuilt by `python3 genaut/gen/flatten.py`.\n")
    with open(os.path.join(flat_dir, "census.md"), "w") as fh:
        fh.write("\n".join(lines))


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Build corpus/flat/ (cross-shape language union).")
    ap.add_argument("--corpus", default=_CORPUS, help="corpus root (default genaut/corpus)")
    ap.add_argument("--exclude", nargs="*", default=list(_DEFAULT_EXCLUDE),
                    help="shape tags to omit (default: the alphabet-blow-up dominators)")
    args = ap.parse_args(argv)
    rec = flatten(args.corpus, tuple(args.exclude))
    print(f"[flat] {rec['total_langs']} distinct languages from {rec['sources']} sources "
          f"(exhaustive {rec['by_exhaustive']['exhaustive']}, "
          f"sampled {rec['by_exhaustive']['sampled']}); "
          f"excluded {rec['excluded']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
