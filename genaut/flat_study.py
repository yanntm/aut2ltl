"""Render the language-level study of the deduped corpus — the project's main
benchmark — as one markdown file. Distinct from `shapes_table.py`/`SHAPES.md`,
which report the *presentation* funnel per shape (still used by consumers that
read off the shape, not the SoS); this reports the *languages* that survive the
dedup passes (cross-shape union → unused-AP dropping → `B_k` relabeling fold),
bucketed by the origin shape encoded in each model's name.

    python3 genaut/flat_study.py                 # -> corpus/flat_canon/STUDY.md

Pure post-processing of the built `corpus/flat_canon/` (+ its json and `flat/`
for the fixed-labeling reference); no rebuild.
"""
from __future__ import annotations

import json
import os
import re
import statistics
from typing import Dict, List, Optional, Tuple

_CORPUS = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "corpus"))
_TAG_RE = re.compile(r"^(\d+)state(\d+)ap(\d+)acc(_parity)?$")


def _origin_tag(fname: str) -> str:
    """The shape tag a model's name encodes: strip `.sos` and the trailing
    `_<id>` (ids are numeric; tags may end in `_parity`)."""
    return fname[:-4].rsplit("_", 1)[0]


def _parse_tag(tag: str) -> Optional[Tuple[int, int, int, str]]:
    m = _TAG_RE.match(tag)
    return (int(m.group(1)), int(m.group(2)), int(m.group(3)),
            "parity" if m.group(4) else "gba") if m else None


def _first_int(text: str, key: str) -> int:
    return int(re.search(key + r":\s*(\d+)", text).group(1))


def _dist(xs: List[int]) -> str:
    return f"{min(xs)} / {int(statistics.median(xs))} / {max(xs)}" if xs else "—"


def _per_shape(corpus: str) -> List[Dict]:
    """Per origin shape: language count and the states / |𝒞| distributions, read
    from `flat_canon/`. A shape is `sampled` iff it has no exhaustive `det/` tier."""
    canon = os.path.join(corpus, "flat_canon")
    acc: Dict[str, Dict] = {}
    for fname in sorted(os.listdir(os.path.join(canon, "sos"))):
        if not fname.endswith(".sos") or fname[:-4].endswith("_c"):
            continue                          # skip added complements: not shape-realized
        tag = _origin_tag(fname)
        parsed = _parse_tag(tag)
        if parsed is None:
            continue
        n, k, c, family = parsed
        d = acc.setdefault(tag, {"tag": tag, "n": n, "k": k, "c": c, "family": family,
                                 "exhaustive": os.path.isdir(os.path.join(corpus, "det", tag)),
                                 "states": [], "classes": []})
        d["states"].append(_first_int(open(os.path.join(canon, "det", fname[:-4] + ".hoa")).read(), "States"))
        d["classes"].append(_first_int(open(os.path.join(canon, "sos", fname)).read(), "classes"))
    return sorted(acc.values(),
                  key=lambda r: (0 if r["exhaustive"] else 1, r["n"], r["k"], r["c"],
                                 1 if r["family"] == "parity" else 0))


def build_study(corpus: str) -> str:
    canon_json = json.load(open(os.path.join(corpus, "flat_canon", "flat_canon.json")))
    flat_json = json.load(open(os.path.join(corpus, "flat", "flat.json")))
    shapes = _per_shape(corpus)
    fixed = flat_json["total_langs"]
    primal = canon_json["primal_langs"]
    dual = canon_json["dual_langs"]
    closed = canon_json["total_langs"]
    exhaustive = sum(len(s["states"]) for s in shapes if s["exhaustive"])
    sampled = primal - exhaustive
    all_states = [x for s in shapes for x in s["states"]]
    all_classes = [x for s in shapes for x in s["classes"]]

    L: List[str] = []
    L.append("# genaut language benchmark — the deduped corpus, by language\n")
    L.append(
        "The project's reference benchmark: every ω-language a small automaton "
        "realizes, **each counted once**. Built by exhaustively enumerating tiny "
        "automata per shape and, past the tractability wall, **sampling** from the "
        "id space, then removing every redundancy — the same language re-presented "
        "across shapes, carrying an unused atomic proposition, or written under a "
        "different naming/polarity of its propositions. What remains is the "
        "language catalogue; this file studies it.\n")
    L.append(
        "> **Scope.** Exhaustive over the shapes below the wall (every language of "
        "those shapes is present); **sampled**, hence *non-exhaustive*, for the "
        "beyond-wall shapes (present languages are real, but absence proves "
        "nothing). Rows are tagged accordingly. The alphabet dominator "
        f"`2state2ap0acc` is excluded. Provenance is read off each model's name, "
        "which is kept from the **smallest shape** that realizes the language.\n")

    L.append("## Headline\n")
    L.append("| catalogue | languages |")
    L.append("|---|--:|")
    L.append(f"| fixed AP labeling (`flat/`, distinct `.sos`) | {fixed} |")
    L.append(f"| distinct up to renaming symbols (primals) | {primal} |")
    L.append(f"| &nbsp;&nbsp;— from exhaustive shapes | {exhaustive} |")
    L.append(f"| &nbsp;&nbsp;— from sampled shapes (non-exhaustive) | {sampled} |")
    L.append(f"| + complements added to close under complement | {dual} |")
    L.append(f"| **complement-closed total (`flat_canon/`)** | **{closed}** |")
    L.append(f"\nThe relabeling + unused-AP fold takes {fixed} fixed-labeling "
             f"`.sos` to {primal} languages up to renaming "
             f"({100*(fixed-primal)/fixed:.0f}% were relabel/polarity twins or "
             f"carried a redundant AP); closing under complement (no language is "
             f"its own, so the total is even) adds {dual}, reaching {closed}. "
             f"Primal automaton states: {_dist(all_states)} (min / median / max); "
             f"algebra size `|𝒞|`: {_dist(all_classes)}.\n")

    L.append("## Composition (primals — the shape-realized languages; +"
             f" {dual} complements close the set)\n")
    L.append("| axis | bucket | languages |")
    L.append("|---|---|--:|")
    for fam, v in sorted(canon_json["by_family"].items()):
        L.append(f"| acceptance family | `{fam}` | {v} |")
    # Provenance by model NAME (smallest realizing shape), consistent with the
    # headline and the per-shape table — this can differ from the build's
    # first-seen source: a language named for an exhaustive shape may have been
    # first materialized from that shape's sample (see STUDY note).
    L.append(f"| provenance | exhaustive | {exhaustive} |")
    L.append(f"| provenance | sampled | {sampled} |")
    for cc, v in sorted(canon_json["by_colours"].items(), key=lambda kv: int(kv[0])):
        L.append(f"| acceptance colours | c={cc} | {v} |")
    L.append(f"| **primals** | | **{primal}** |")
    L.append(f"| + complements (dual acceptance) | | {dual} |")
    L.append(f"| **complement-closed total** | | **{closed}** |")

    L.append("\n## By origin shape\n")
    L.append("Each language attributed to the smallest shape realizing it (its "
             "model name). `states` is the canonical deterministic automaton's "
             "state count; `|𝒞|` the syntactic-semigroup size — both min / median "
             "/ max over the shape's languages.\n")
    L.append("| shape | n | k | c | family | tier | languages | states | algebra `𝒞` |")
    L.append("|---|--:|--:|--:|---|---|--:|---|---|")
    for s in shapes:
        tier = "exhaustive" if s["exhaustive"] else "**sampled**"
        L.append(f"| `{s['tag']}` | {s['n']} | {s['k']} | {s['c']} | {s['family']} | "
                 f"{tier} | {len(s['states'])} | {_dist(s['states'])} | "
                 f"{_dist(s['classes'])} |")

    L.append("\nGenerated by `python3 genaut/flat_study.py` from `corpus/flat_canon/`. "
             "For the per-shape *presentation* funnel (automata, not languages) see "
             "`SHAPES.md`.\n")
    return "\n".join(L)


def main() -> int:
    out = os.path.join(_CORPUS, "flat_canon", "STUDY.md")
    with open(out, "w") as fh:
        fh.write(build_study(_CORPUS))
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
