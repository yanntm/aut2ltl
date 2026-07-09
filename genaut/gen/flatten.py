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


def relabel_hoa(text: str, sigma: "Tuple[Tuple[int, ...], int]", k: int) -> str:
    """Apply a signed AP permutation `sigma = (pi, flips)` to a det HOA. `sigma`
    is stated over the **sorted** AP name-slots (the `.sos` alphabet convention):
    new slot `j` is old slot `pi[j]`, negated iff `flips` has bit `k-1-j` set. The
    slots are the AP names in lexicographic order, which may differ from the HOA's
    own AP-declaration order (and be non-contiguous, e.g. `a, c`, when the language
    drops an AP) — so HOA indices are mapped through the names. AP names are
    preserved (kept in sorted order, as the `.sos` keeps them); only bracketed
    guards are touched."""
    if k == 0:
        return text                                        # B_0 is trivial (no APs)
    pi, flips = sigma
    hm = re.search(r'AP:\s*\d+((?:\s+"[^"]*")+)', text)
    names = re.findall(r'"([^"]*)"', hm.group(1))          # HOA index i -> names[i]
    ordered = sorted(names)                                # slot j -> ordered[j]
    slot_of = {i: ordered.index(names[i]) for i in range(len(names))}
    inv_pi = [0] * k
    for j in range(k):
        inv_pi[pi[j]] = j                                  # old slot -> new slot
    newidx = {i: inv_pi[slot_of[i]] for i in range(len(names))}
    flip = {i: (flips >> (k - 1 - newidx[i])) & 1 for i in range(len(names))}

    def lit(m: "re.Match[str]") -> str:
        tok = m.group(0)
        neg = tok.startswith("!")
        oi = int(tok[1:] if neg else tok)
        positive = (not neg) ^ bool(flip[oi])              # flipped AP: true<->false
        return ("" if positive else "!") + str(newidx[oi])

    def guard(m: "re.Match[str]") -> str:
        return "[" + re.sub(r"!?\d+", lit, m.group(1)) + "]"

    out = re.sub(r"\[([^\]]*)\]", guard, text)
    header = 'AP: %d %s' % (k, " ".join('"%s"' % n for n in ordered))
    return re.sub(r'AP:\s*\d+(?:\s+"[^"]*")+', header, out)

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
            # Sampled tiers exist only for beyond-the-wall shapes. A sample of an
            # already-exhaustive shape (e.g. the sampler-validation `2state1ap1acc`
            # draw) is redundant — every one of its languages is in the exhaustive
            # tier — and mixing acceptance families on a shared id space (`_parity`
            # is load-bearing) only injects mislabeled provenance. Skip it.
            if os.path.isdir(os.path.join(det_root, tag)):
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


def build_canon(corpus: str, exclude: Tuple[str, ...]) -> Dict:
    """Materialize `corpus/flat_canon/` — one representative per distinct language
    **up to AP relabeling** (`B_k` orbit-min, `sosl.sos.relabel`). Each kept
    language's det HOA and `.sos` are relabeled into the same canonical labeling
    (σ* applied to both), so the pair is consumable as-is; the smallest-shape
    `<tag>_<id>` name is preserved. Heavier than `flatten` (it runs the sosl
    construction per language), so it imports sosl lazily."""
    sys.path.insert(0, os.path.join(_REPO, "sosl"))
    import spot                                            # noqa: E402
    from sosl.sos.build.importer import canonical          # noqa: E402
    from sosl.sos.core.quotient import invariant_of        # noqa: E402
    from sosl.sos.io.serialize import dump_invariant, load_invariant  # noqa: E402
    from sosl.sos.relabel import canonical_relabeling      # noqa: E402

    det_dir = os.path.join(corpus, "flat_canon", "det")
    sos_dir = os.path.join(corpus, "flat_canon", "sos")
    for d in (det_dir, sos_dir):
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d, exist_ok=True)

    sources = discover(corpus, exclude)
    seen: Dict[str, str] = {}                 # canonical .sos bytes -> owning tag
    primal_idents: List[str] = []             # the shape-realized languages, in order
    rows: List[Dict] = []
    total = 0
    for src in sources:
        sos_files = sorted(f for f in os.listdir(src.sos_dir) if f.endswith(".sos"))
        new = 0
        for fname in sos_files:
            ident = fname[:-4]
            det_src = os.path.join(src.det_dir, ident + ".hoa")
            if not os.path.isfile(det_src):
                continue
            # The det, canonicalized and alphabet-minimized, is the ground truth.
            # `remove_unused_ap` sheds every AP no edge mentions (spot only folds
            # the all-`t` case on its own; a declared-but-unused AP otherwise
            # stays — cf. aut2ltl/language.py), so a language recurs at exactly one
            # alphabet size: `GF a` over `{a}` and over `{a,b}` fold together, and
            # `universal` collapses to 0 APs. We key off this, never the stored
            # .sos, which a sampled entry may leave non-minimal.
            D0 = canonical(spot.automaton(open(det_src).read()))
            D0.remove_unused_ap()
            inv = invariant_of(D0)
            sigma, canon_inv = canonical_relabeling(inv)
            canon_sos = dump_invariant(canon_inv)
            if canon_sos in seen:
                continue                      # a smaller shape owns this orbit
            relabeled = relabel_hoa(D0.to_str("hoa"), sigma, len(inv.alphabet.aps))
            D = canonical(spot.automaton(relabeled))
            if dump_invariant(invariant_of(D)) != canon_sos:
                raise AssertionError(f"relabel_hoa disagrees with algebra on {ident}")
            seen[canon_sos] = src.tag
            primal_idents.append(ident)
            with open(os.path.join(det_dir, ident + ".hoa"), "w") as fh:
                fh.write(D.to_str("hoa"))
            with open(os.path.join(sos_dir, ident + ".sos"), "w") as fh:
                fh.write(canon_sos)
            new += 1
        total += new
        rows.append({
            "source": src.tag, "n": src.n, "k": src.k, "c": src.c,
            "family": src.family, "exhaustive": src.exhaustive,
            "scanned": len(sos_files), "new_langs": new, "cumulative": total,
        })

    # Complement closure. No language equals its own complement, so the closed
    # catalogue is even. For each primal whose complement is not itself a primal,
    # materialize the dual under `<ident>_c` (same shape provenance): the `.sos` by
    # flipping P (already canonical), the det by dualizing (De Morgan on the
    # acceptance) — the two agree, an asserted cross-check.
    dual = 0
    for ident in primal_idents:
        inv = load_invariant(open(os.path.join(sos_dir, ident + ".sos")).read())
        # `Invariant.complement` flips P and keeps the algebra, so the dual of a
        # `B_k`-canonical invariant is `B_k`-canonical too: σ* is chosen on the
        # (complement-invariant) semigroup core.
        comp_sos = dump_invariant(inv.complement())
        if comp_sos in seen:
            continue                          # the dual is itself a catalogued primal
        Dc = canonical(spot.dualize(spot.automaton(
            open(os.path.join(det_dir, ident + ".hoa")).read())))
        if dump_invariant(invariant_of(Dc)) != comp_sos:
            raise AssertionError(f"dualize disagrees with flip-P on {ident}")
        seen[comp_sos] = "complement"
        with open(os.path.join(det_dir, ident + "_c.hoa"), "w") as fh:
            fh.write(Dc.to_str("hoa"))
        with open(os.path.join(sos_dir, ident + "_c.sos"), "w") as fh:
            fh.write(comp_sos)
        dual += 1

    # Categorize: one `.cat` sidecar per language (LTL cut + Wagner degree),
    # read off the `.sos` — covers both the sos and the det HOA of that basename.
    sys.path.insert(0, os.path.dirname(__file__))
    from categorize import write_cats                      # noqa: E402
    write_cats(sos_dir)

    record = {
        "corpus": "flat_canon", "excluded": list(exclude), "sources": len(sources),
        "primal_langs": total, "dual_langs": dual, "total_langs": total + dual,
        "rows": rows,
        "by_family": dict(_tally(rows, "family")),
        "by_exhaustive": {"exhaustive": sum(r["new_langs"] for r in rows if r["exhaustive"]),
                          "sampled": sum(r["new_langs"] for r in rows if not r["exhaustive"])},
        "by_colours": dict(_tally(rows, "c")),
    }
    _write_canon_census(os.path.join(corpus, "flat_canon"), record)
    with open(os.path.join(corpus, "flat_canon", "flat_canon.json"), "w") as fh:
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


def _write_canon_census(canon_dir: str, r: Dict) -> None:
    """Census + composition for the AP-relabeling-folded pool."""
    lines: List[str] = []
    lines.append("# flat_canon — distinct languages up to AP relabeling, complement-closed\n")
    lines.append(
        f"**{r['total_langs']}** languages: **{r['primal_langs']}** distinct up to "
        f"AP relabeling (the `B_k` orbit-min of `flat/`, folding the signed "
        f"permutations of the atomic propositions — `GF(a) ≡ GF(!a)`, `a↔b` twins) "
        f"plus **{r['dual_langs']}** complements added to close the catalogue under "
        f"complement. Both the det HOA and the `.sos` are relabeled into the orbit's "
        f"canonical labeling (σ* applied to both — a self-consistent pair); primals "
        f"keep the smallest-shape `<tag>_<id>` name, each added dual is `<primal>_c`. "
        f"σ* is chosen on the semigroup core alone, so `L` and `L̄` pick the same "
        f"labeling (`𝓘(L̄)` = `𝓘(L)` with `accept` flipped, byte-exact) — the "
        f"complement is the trivial P-flip, cross-checked against `dualize(det)`. No "
        f"language is its own complement, so the closed count is even.\n")
    if r["excluded"]:
        lines.append(f"Excluded: {', '.join('`' + e + '`' for e in r['excluded'])}.\n")

    lines.append("\n## Composition (primals — the shape-realized languages)\n")
    lines.append("| axis | bucket | languages |")
    lines.append("|---|---|--:|")
    for fam, v in sorted(r["by_family"].items()):
        lines.append(f"| acceptance family | `{fam}` | {v} |")
    for kind, v in r["by_exhaustive"].items():
        lines.append(f"| provenance | {kind} | {v} |")
    for c, v in sorted(r["by_colours"].items(), key=lambda kv: int(kv[0])):
        lines.append(f"| acceptance colours | c={c} | {v} |")
    lines.append(f"| **primals** | | **{r['primal_langs']}** |")
    lines.append(f"| complements added | | {r['dual_langs']} |")
    lines.append(f"| **total (closed)** | | **{r['total_langs']}** |")

    lines.append("\n## Contribution by source (traversal order)\n")
    lines.append("| # | source | n | k | c | family | tier | scanned | new | cumulative |")
    lines.append("|--:|---|--:|--:|--:|---|---|--:|--:|--:|")
    for i, row in enumerate(r["rows"], 1):
        tier = "exhaustive" if row["exhaustive"] else "**sampled**"
        lines.append(
            f"| {i} | `{row['source']}` | {row['n']} | {row['k']} | {row['c']} | "
            f"{row['family']} | {tier} | {row['scanned']} | {row['new_langs']} | "
            f"{row['cumulative']} |")

    lines.append("\nBuilt by `python3 genaut/gen/flatten.py --canon`.\n")
    with open(os.path.join(canon_dir, "census.md"), "w") as fh:
        fh.write("\n".join(lines))


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Build corpus/flat/ (cross-shape language union).")
    ap.add_argument("--corpus", default=_CORPUS, help="corpus root (default genaut/corpus)")
    ap.add_argument("--exclude", nargs="*", default=list(_DEFAULT_EXCLUDE),
                    help="shape tags to omit (default: the alphabet-blow-up dominators)")
    ap.add_argument("--canon", action="store_true",
                    help="also materialize corpus/flat_canon/ (B_k relabeling fold)")
    args = ap.parse_args(argv)
    rec = flatten(args.corpus, tuple(args.exclude))
    print(f"[flat] {rec['total_langs']} distinct languages from {rec['sources']} sources "
          f"(exhaustive {rec['by_exhaustive']['exhaustive']}, "
          f"sampled {rec['by_exhaustive']['sampled']}); "
          f"excluded {rec['excluded']}")
    if args.canon:
        crec = build_canon(args.corpus, tuple(args.exclude))
        print(f"[flat_canon] {crec['primal_langs']} languages up to AP relabeling "
              f"(from {rec['total_langs']} fixed-labeling) + {crec['dual_langs']} "
              f"complements = {crec['total_langs']} complement-closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
