"""Render the language-level study of the deduped corpus — the project's main
benchmark — as one markdown file. Distinct from `shapes_table.py`/`SHAPES.md`,
which report the *presentation* funnel per shape (still used by consumers that
read off the shape, not the SoS); this reports the *languages* that survive the
dedup passes (cross-shape union → unused-AP dropping → `B_k` relabeling fold),
bucketed by the origin shape encoded in each model's name.

    python3 genaut/flat_study.py                 # -> logs/genaut/corpus/flat_canon/STUDY.md

Pure post-processing of the built `corpus/flat_canon/` (+ its json and `flat/`
for the fixed-labeling reference); no rebuild.
"""
from __future__ import annotations

import json
import os
import re
import statistics
import sys
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, os.path.join(                         # for sosl.sos.classify.io
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sosl"))
from sosl.sos.classify.io import (                        # noqa: E402
    parse_cat, degree_sort_key, phi_pretty)

_CORPUS = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "corpus"))
# STUDY.md is written under the corpus write root, never the read root.
_OUT = os.path.normpath(
    os.path.join(os.path.dirname(__file__), os.pardir, "logs", "genaut", "corpus"))
_TAG_RE = re.compile(r"^(\d+)state(\d+)ap(\d+)acc(_parity)?$")
_TRIVIAL = {("0", "sigma"), ("0", "pi")}


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


def _categories(corpus: str) -> List[Dict]:
    """Read every `.cat` sidecar of `flat_canon/sos/` — one category per language:
    its LTL cut, stutter-invariance, Wagner degree `ϕ`, coordinates, class, and
    whether it is a `_c` complement. Empty if the corpus is not categorized yet."""
    sos = os.path.join(corpus, "flat_canon", "sos")
    out: List[Dict] = []
    for fname in sorted(os.listdir(sos)):
        if not fname.endswith(".cat"):
            continue
        cat = parse_cat(open(os.path.join(sos, fname)).read())
        cat["complement"] = fname[:-4].endswith("_c")
        out.append(cat)
    return out


def _degree_section(cats: List[Dict]) -> List[str]:
    """The Wagner-degree profile of the complement-closed catalogue: distinct
    languages per degree `ϕ = (γ, s)`, weakest-first with the trivial pair set
    apart, each row carrying its coordinates, class, the non-LTL count (the cut),
    and the primal (shape-realized) count."""
    per: Dict[Tuple[str, str], Dict] = {}
    for c in cats:
        phi = c["phi"]
        d = per.setdefault(phi, {"n": 0, "nonltl": 0, "primal": 0, "stutter": 0,
                                 "coords": c["coords"], "class": c["class"]})
        d["n"] += 1
        d["nonltl"] += 0 if c["ltl"] else 1
        d["primal"] += 0 if c["complement"] else 1
        d["stutter"] += 1 if c["stutter_invariant"] else 0

    order = sorted(per, key=degree_sort_key)
    triv = [p for p in order if p in _TRIVIAL]
    proper = [p for p in order if p not in _TRIVIAL]
    partial = sum(1 for c in cats if c["phi"][1] == "PARTIAL")

    def row(phi: Tuple[str, str]) -> str:
        d = per[phi]
        m0, m1, n0, n1 = d["coords"]
        return (f"| {phi_pretty(phi)} | ({m0}, {m1}, {n0}, {n1}) | {d['class']} "
                f"| {d['n']} | {d['nonltl']} | {d['stutter']} | {d['primal']} |")

    L: List[str] = []
    L.append("\n## Wagner-degree profile (classified, complement-closed)\n")
    L.append(
        "Each language's **category**, read off its syntactic invariant `𝓘(L)` "
        "into a `.cat` sidecar (a pure table search — no automaton, no Spot) and "
        "aggregated here. `ϕ = (γ, s)` is the Wagner degree (`γ` the ordinal "
        "depth, `s ∈ {σ, π, δ}` the side); `(m⁺, m⁻, n⁺, n⁻)` the chain/superchain "
        "coordinates; `non-LTL` the count in that row that is **not** "
        "LTL-definable; `stutter-inv` the count that is stutter-invariant; "
        "`primals` the shape-realized share (the rest are added complements). "
        "Because the catalogue is closed under complement, the profile is "
        "**exactly duality-symmetric**: every `(γ, σ)` row matches its `(γ, π)` "
        "dual, and the self-dual `δ` rows stand alone.\n")
    L.append("| `ϕ = (γ, s)` | `(m⁺, m⁻, n⁺, n⁻)` | class | languages | non-LTL | stutter-inv | primals |")
    L.append("|---|---|---|--:|--:|--:|--:|")
    for phi in triv:
        L.append(row(phi))
    if triv and proper:
        tl = sum(per[p]["n"] for p in triv)
        L.append(f"| *— trivial pair (weakest), set apart —* | | | *{tl}* | | | |")
    for phi in proper:
        L.append(row(phi))

    tail = ("no language reaches Wagner's derivative (`γ = μ` throughout, "
            "Prop. 11.1)" if partial == 0 else f"**{partial}** languages hit the "
            "derivative regime (`PARTIAL`)")
    L.append(f"\nDegrees span `(0, σ)` (trivial) up to `(ω², ·)` (parity-`{{0,1,2}}`); "
             f"{tail}. The degree is a language invariant — a `.cat` says the same "
             "for a language however many shapes, states, or colours presented it.")
    return L


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

    cats = _categories(corpus)
    ltl = sum(1 for c in cats if c["ltl"])
    nonltl = len(cats) - ltl
    prim_ltl = sum(1 for c in cats if c["ltl"] and not c["complement"])
    prim_nonltl = primal - prim_ltl
    si = sum(1 for c in cats if c["stutter_invariant"])
    prim_si = sum(1 for c in cats if c["stutter_invariant"] and not c["complement"])

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

    if cats:
        L.append("## The LTL cut\n")
        L.append(
            f"The dividing line everyone asks about first — is the language "
            f"**LTL-definable** (equivalently, star-free / first-order / aperiodic "
            f"syntactic ω-semigroup) or does it genuinely **count**? Read off each "
            f"language's `.cat` (aperiodicity of `𝓘(L)`), over the "
            f"complement-closed catalogue:\n")
        L.append("| definability | languages |")
        L.append("|---|--:|")
        L.append(f"| **LTL-definable** (aperiodic) | **{ltl}** |")
        L.append(f"| **non-LTL** (genuine ω-counting) | **{nonltl}** |")
        L.append(f"| total (`flat_canon/`) | {len(cats)} |")
        L.append(
            f"\nSo **{100*nonltl/len(cats):.0f}%** of the small ω-languages are "
            f"beyond LTL. The cut is complement-invariant (aperiodicity is a "
            f"property of the semigroup, not of `accept`), so it splits the primals "
            f"the same way: {prim_ltl} LTL / {prim_nonltl} non-LTL of {primal}. It "
            f"cuts *across* the Wagner degrees below — depth and countability are "
            f"independent axes.\n")

        L.append("### Stutter-invariant — the X-free refinement of LTL\n")
        L.append(
            f"A language is **stutter-invariant** iff its syntactic monoid keeps no "
            f"letter apart from its square (`M(λa, λa) = λa` for every `a`) — the "
            f"read-off sitting beside aperiodicity in each `.cat`. This is a "
            f"*subclass* of LTL (stutter-invariant `≡` LTL without `X`), so it lands "
            f"entirely inside the aperiodic column; a language that genuinely counts "
            f"letters cannot be stutter-blind. Over the catalogue:\n")
        L.append("| sub-class of LTL | languages | of LTL |")
        L.append("|---|--:|--:|")
        L.append(f"| **stutter-invariant** (X-free) | **{si}** | {100*si/ltl:.0f}% |")
        L.append(f"| stutter-sensitive but LTL | {ltl - si} | {100*(ltl-si)/ltl:.0f}% |")
        L.append(f"| (non-LTL — all stutter-sensitive) | {nonltl} | — |")
        L.append(
            f"\nSo **{100*si/len(cats):.0f}%** of the catalogue ({si} of {len(cats)}) "
            f"is stutter-invariant, i.e. **{100*si/ltl:.0f}%** of the {ltl} "
            f"LTL-definable languages drop the `X` operator. Like the LTL cut it is "
            f"complement-invariant, splitting the primals {prim_si} / {primal}. The "
            f"per-degree `stutter-inv` column below shows how it distributes over the "
            f"Wagner ladder.\n")

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
    if cats:
        L.append(f"| definability | LTL (aperiodic) | {prim_ltl} |")
        L.append(f"| definability | &nbsp;&nbsp;— stutter-invariant (X-free ⊆ LTL) | {prim_si} |")
        L.append(f"| definability | non-LTL | {prim_nonltl} |")
    L.append(f"| **primals** | | **{primal}** |")
    L.append(f"| + complements (dual acceptance) | | {dual} |")
    L.append(f"| **complement-closed total** | | **{closed}** |")

    if cats:
        L += _degree_section(cats)

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

    L.append("\nGenerated by `python3 genaut/flat_study.py` from `corpus/flat_canon/` "
             "(the LTL cut, stutter refinement, and Wagner-degree profile aggregate "
             "the per-language `.cat` sidecars). For the per-shape *presentation* "
             "funnel (automata, not languages) see `SHAPES.md`.\n")
    return "\n".join(L)


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="flat_study")
    ap.add_argument("--corpus", default=_CORPUS, help="corpus root to READ")
    ap.add_argument("--out", default=_OUT, help="corpus root to WRITE STUDY.md under")
    args = ap.parse_args(argv)
    out = os.path.join(args.out, "flat_canon", "STUDY.md")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as fh:
        fh.write(build_study(args.corpus))
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    import sys; raise SystemExit(main(sys.argv[1:]))
