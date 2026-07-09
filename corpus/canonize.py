"""Build `corpus/{det,sos}/` — the language tier over the benchmark's inputs.

`samples/benchmark/inputs/` is a *presentation* corpus: LTL formulas and HOA
automata, many of which denote the same ω-language (`Fa` and `F F a`; a Kinská
automaton and a formula for it). This stage carries every input through the sosl
construction to the two canonical tiers, keeping **one representative per distinct
language**:

    det/   the deterministic, complete, transition-based, generic automaton D
           (`sosl ... importer.canonical`) as HOA — one per distinct language.
    sos/   the syntactic ω-semigroup 𝓘(L) as `.sos` — one per distinct language,
           the compact canonical form downstream runs consume directly.

Structurally this is `genaut/corpus/flat/` (see `genaut/README.md`), with the same
dedup notion — **language identity up to a fixed AP labeling**, the `.sos` `𝓘` key
([SωS26 Thm. 5.1]: byte-equal ⟺ equal language). `GF(a)` and `GF(!a)` stay
distinct, as do a language over `{a}` and the same language over `{a,b}` (a
different alphabet is a different canonical D); folding those is the `B_k` orbit
fold `genaut/corpus/flat_canon/` performs, and is deliberately not done here.

The catalogue is then **closed under complement**: for every language whose dual is
not itself catalogued, `<ident>_c` is added — the `.sos` by `Invariant.complement`
(the free flip of `P`), the det by `spot.dualize`, the two cross-checked against
each other. No language equals its own complement, so the closed catalogue is even.

Naming traces a language to the input that first realized it: `<category>_<stem>`
for an HOA file, `<category>_<stem>_L<line>` for one line of an LTL list, and
`<primal>_c` for an added dual.

This tier lives outside `samples/`, beside it, for two reasons. It is *derived*
(regenerable from `inputs/`, whereas `samples/` is the hand-curated source of
truth), and the survey harness recurses whatever folder it is given — a `det/`
of 460 HOA files under `samples/benchmark/` would silently join the bench's own
input set and move its committed results.

Three budgets bound the build, and an input that trips one is **recorded as skipped
in `census.md`, never dropped silently**: the `|EM1|` closure `--cap`, a per-input
`--timeout`, and `--max-sos`, which rejects a language whose `.sos` dump is too
large to carry as a committed test input (the benchmark's largest counting automata
dump tens of MiB). Each budget is disabled by `0`, so `--max-sos 0 --cap 0
--timeout 0` admits every language the inputs realize. `--max-sos` gates a language
and its dual **together** — they share an algebra, so their dumps differ only in the
`P` block, and admitting one without the other would break complement closure.

    python3 corpus/canonize.py                  # (re)build det/ + sos/
    python3 corpus/canonize.py --timeout 30     # per-input wall clock
    python3 corpus/canonize.py --max-sos 0      # admit the multi-MiB algebras
    python3 corpus/canonize.py --no-complement  # primals only
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import signal
import sys
from collections import Counter
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, Iterator, List, NamedTuple, Optional

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.abspath(os.path.join(_HERE, os.pardir))
_INPUTS = os.path.join(_REPO, "samples", "benchmark", "inputs")
for _p in (_REPO, os.path.join(_REPO, "sosl")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import spot  # noqa: E402

from sosl.sos import dump_invariant  # noqa: E402
from sosl.sos.build.importer import canonical  # noqa: E402
from sosl.sos.core.quotient import invariant_of  # noqa: E402
from survey.discovery.scan import discover  # noqa: E402
from survey.example import Example  # noqa: E402
from survey.normalize.sos import sos_key  # noqa: E402


class Budget(Exception):
    """One input outran its per-input wall clock."""


@contextmanager
def _deadline(seconds: float) -> "Iterator[None]":
    """Raise `Budget` if the body outlasts `seconds` (0 disables). SIGALRM-based:
    main thread only, one nesting level."""
    if seconds <= 0:
        yield
        return

    def _fire(signum: int, frame: object) -> None:
        raise Budget()

    prev = signal.signal(signal.SIGALRM, _fire)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, prev)


class Entry(NamedTuple):
    """One catalogued language: its name, canonical D (as HOA text), `𝓘` dump, and
    the dump of its complement — carried alongside because the size cap admits a
    language and its dual atomically (see `build`), so the closure reuses it."""
    ident: str
    hoa: str
    sos: str
    comp_sos: str


def ident_of(example: "Example", inputs: str) -> str:
    """`<category>_<stem>` for an HOA file, `<category>_<stem>_L<line>` for one
    line of an LTL list — the input's path under `inputs/`, flattened. The `_L<n>`
    suffix keeps a formula line from colliding with a same-named `.hoa`."""
    src = example.source
    path, _, line = src.rpartition(":") if example.kind == "ltl" else (src, "", "")
    rel = os.path.relpath(path, inputs)
    stem = os.path.splitext(rel)[0].replace(os.sep, "_")
    return f"{stem}_L{int(line):02d}" if line else stem


def automaton_of(example: "Example") -> "spot.twa_graph":
    """The input as a Spot automaton: an HOA file is parsed, an LTL formula is
    translated. Neither is reduced — `canonical` determinizes and normalizes."""
    if example.is_hoa:
        return spot.automaton(example.value)
    return spot.translate(spot.formula(example.value))


class Funnel:
    """The per-source contribution tally: how many inputs a file contributed, and
    how many of them were the first to realize their language."""

    def __init__(self) -> None:
        self.rows: Dict[str, Counter] = {}
        self.order: List[str] = []

    def bump(self, source: str, field: str) -> None:
        if source not in self.rows:
            self.rows[source] = Counter()
            self.order.append(source)
        self.rows[source][field] += 1

    def as_list(self, inputs: str) -> List[Dict]:
        out: List[Dict] = []
        cumulative = 0
        for source in self.order:
            c = self.rows[source]
            cumulative += c["new"]
            rel = os.path.relpath(source, inputs)
            out.append({
                "source": rel, "category": rel.split(os.sep)[0],
                "scanned": c["scanned"], "new_langs": c["new"],
                "collapsed": c["collapsed"], "capped": c["capped"],
                "timeout": c["timeout"], "oversize": c["oversize"],
                "error": c["error"], "cumulative": cumulative,
            })
        return out


def build(inputs: str, out_dir: str, timeout: float,
          complement: bool, cap: int, max_sos: int) -> Dict:
    """Walk `inputs/`, canonize each input, keep one representative per distinct
    language, then close the catalogue under complement. Returns the record."""
    det_dir, sos_dir = os.path.join(out_dir, "det"), os.path.join(out_dir, "sos")
    for d in (det_dir, sos_dir):
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d, exist_ok=True)

    eff_cap = cap if cap > 0 else sys.maxsize      # 0 = no closure cap
    seen: Dict[str, str] = {}                 # 𝓘 key -> owning ident
    oversize: Dict[str, str] = {}             # 𝓘 key -> ident that first hit the cap
    primals: List[Entry] = []
    funnel = Funnel()
    skipped: List[Dict] = []

    for example in discover([Path(inputs)]):
        source = example.source.rpartition(":")[0] if example.kind == "ltl" \
            else example.source
        funnel.bump(source, "scanned")
        ident = ident_of(example, inputs)
        try:
            with _deadline(timeout):
                D = canonical(automaton_of(example))
                inv = invariant_of(D, cap=eff_cap)
        except Budget:
            funnel.bump(source, "timeout")
            skipped.append({"ident": ident, "input": example.display,
                            "reason": f"timeout (>{timeout}s)"})
            continue
        except Exception as exc:                       # a malformed input
            funnel.bump(source, "error")
            skipped.append({"ident": ident, "input": example.display,
                            "reason": f"{type(exc).__name__}: {exc}"})
            continue
        if inv is None:                                # algebra closure hit the cap
            funnel.bump(source, "capped")
            skipped.append({"ident": ident, "input": example.display,
                            "reason": f"capped (|EM1| > {eff_cap})"})
            continue

        dump = dump_invariant(inv)
        key = sos_key(dump)
        if key in seen:                                # an earlier input owns it
            funnel.bump(source, "collapsed")
            continue
        if key in oversize:                            # already rejected, once is enough
            funnel.bump(source, "oversize")
            continue

        # The size gate gates the *pair*. `I(L)` and `I(L-bar)` share the algebra
        # and differ only in the `P` block, so the two dumps are near the same
        # size — but not equal, and admitting one without the other would leave
        # the catalogue not complement-closed. Decide on the larger of the two.
        comp_dump = dump_invariant(inv.complement())
        pair_bytes = max(len(dump.encode()), len(comp_dump.encode()))
        if max_sos and pair_bytes > max_sos:
            oversize[key] = ident
            funnel.bump(source, "oversize")
            skipped.append({"ident": ident, "input": example.display,
                            "reason": f"oversize (|.sos| = {_mib(pair_bytes)} > "
                                      f"{_mib(max_sos)})"})
            continue

        seen[key] = ident
        funnel.bump(source, "new")
        primals.append(Entry(ident, D.to_str("hoa"), dump, comp_dump))

    for e in primals:
        _write(det_dir, e.ident + ".hoa", e.hoa)
        _write(sos_dir, e.ident + ".sos", e.sos)

    duals = _close(primals, seen, det_dir, sos_dir, eff_cap) if complement else 0

    record = {
        "corpus": "corpus", "inputs": os.path.relpath(inputs, _REPO),
        "scanned": sum(r["scanned"] for r in funnel.as_list(inputs)),
        "primal_langs": len(primals), "dual_langs": duals,
        "total_langs": len(primals) + duals,
        "complement_closed": complement,
        "cap": cap, "timeout": timeout, "max_sos": max_sos,
        "skipped": skipped,
        "rows": funnel.as_list(inputs),
    }
    record["by_category"] = dict(_tally(record["rows"], "category"))
    _write_census(out_dir, record)
    _write(out_dir, "corpus.json", json.dumps(record, indent=2) + "\n")
    return record


def _close(primals: List[Entry], seen: Dict[str, str],
           det_dir: str, sos_dir: str, cap: int) -> int:
    """Add `<ident>_c` for every primal whose dual is not itself catalogued. The
    `.sos` is the free `P`-flip (`Invariant.complement`, computed with the primal);
    the det is `spot.dualize` of the primal's D. The two are cross-checked — a
    disagreement convicts one of them and is raised, never silently preferred."""
    duals = 0
    for e in primals:
        key = sos_key(e.comp_sos)
        if key in seen:                                # the dual is itself a primal
            continue
        Dc = canonical(spot.dualize(spot.automaton(e.hoa)))
        check = invariant_of(Dc, cap=cap)
        if check is None or dump_invariant(check) != e.comp_sos:
            raise AssertionError(
                f"{e.ident}: spot.dualize disagrees with the P-flip")
        seen[key] = e.ident + "_c"
        _write(det_dir, e.ident + "_c.hoa", Dc.to_str("hoa"))
        _write(sos_dir, e.ident + "_c.sos", e.comp_sos)
        duals += 1
    return duals


def _mib(nbytes: float) -> str:
    """A byte count as a human-readable size, `B` / `KiB` / `MiB`."""
    for unit in ("B", "KiB", "MiB"):
        if nbytes < 1024 or unit == "MiB":
            return f"{nbytes:.0f} B" if unit == "B" else f"{nbytes:.1f} {unit}"
        nbytes /= 1024.0
    raise AssertionError("unreachable")


def _write(directory: str, name: str, content: str) -> None:
    with open(os.path.join(directory, name), "w") as fh:
        fh.write(content)


def _tally(rows: List[Dict], field: str) -> Counter:
    t: Counter = Counter()
    for r in rows:
        t[r[field]] += r["new_langs"]
    return t


def _write_census(out_dir: str, r: Dict) -> None:
    """The automated census: the presentation -> language funnel, per source."""
    lines: List[str] = []
    lines.append("# corpus — the language tier (`det/` + `sos/`)\n")
    lines.append(
        f"**{r['total_langs']}** languages: **{r['primal_langs']}** distinct ones "
        f"realized by the {r['scanned']} inputs of `{r['inputs']}/`"
        + (f", plus **{r['dual_langs']}** complements added to close the catalogue "
           f"under complement" if r["complement_closed"] else "")
        + ". One `det/*.hoa` (the canonical deterministic D) and one `sos/*.sos` "
        f"(the syntactic `𝓘`) per language, deduped by the `𝓘` key "
        f"([SωS26 Thm. 5.1]: byte-equal ⟺ equal language) — **up to a fixed AP "
        f"labeling**, so `GF(a)` and `GF(!a)` are two entries, as are a language "
        f"over `{{a}}` and the same over `{{a,b}}`. Each language is named for the "
        f"**first input that realized it** (`<category>_<stem>[_L<line>]`); each "
        f"added dual is `<primal>_c`.\n")
    limits = [f"an algebra closure past the `|EM1| > {r['cap']}` cap" if r["cap"] else "",
              f"a `>{r['timeout']}s` per-input budget" if r["timeout"] else "",
              f"a `.sos` dump over the `{_mib(r['max_sos'])}` size cap"
              if r["max_sos"] else ""]
    lines.append(
        "Inputs that produced no language are listed under *Skipped* below — "
        + ", or ".join(x for x in limits if x) + ". Those are **not** failures of "
        "the construction, only of this build's budget: each is a genuine language "
        "whose syntactic algebra is simply large. Every one of them is rebuildable "
        "— `python3 corpus/canonize.py --max-sos 0 --cap 0 --timeout 0` admits them "
        "all — but the largest dumps tens of MiB, too big to carry as a committed "
        "test input, so they are **discarded here by policy, not missing**.\n")

    lines.append("\n## Composition\n")
    lines.append("| category | languages first seen here |")
    lines.append("|---|--:|")
    for cat, v in sorted(r["by_category"].items()):
        lines.append(f"| `{cat}/` | {v} |")
    lines.append(f"| **primals** | **{r['primal_langs']}** |")
    if r["complement_closed"]:
        lines.append(f"| complements added | {r['dual_langs']} |")
        lines.append(f"| **total (closed)** | **{r['total_langs']}** |")

    lines.append("\n## Contribution by source file (walk order)\n")
    lines.append("A source's `new` is the languages first realized there — those an "
                 "earlier input did not already own. `collapsed` counts inputs whose "
                 "language was already catalogued.\n")
    lines.append("| # | source | scanned | new | collapsed | capped | timeout | "
                 "oversize | cumulative |")
    lines.append("|--:|---|--:|--:|--:|--:|--:|--:|--:|")
    for i, row in enumerate(r["rows"], 1):
        lines.append(
            f"| {i} | `{row['source']}` | {row['scanned']} | {row['new_langs']} | "
            f"{row['collapsed']} | {row['capped']} | {row['timeout']} | "
            f"{row['oversize']} | {row['cumulative']} |")

    if r["skipped"]:
        lines.append("\n## Skipped\n")
        lines.append("| input | reason |")
        lines.append("|---|---|")
        for s in r["skipped"]:
            shown = s["input"] if len(s["input"]) <= 60 else s["input"][:57] + "…"
            # the reasons carry `|EM1|` / `|.sos|`, which would split the cell
            reason = s["reason"].replace("|", "\\|")
            lines.append(f"| `{shown}` | {reason} |")

    lines.append("\nBuilt by `python3 corpus/canonize.py`.\n")
    _write(out_dir, "census.md", "\n".join(lines))


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        description="Build corpus/{det,sos}/ — one per distinct language.")
    ap.add_argument("--inputs", default=_INPUTS,
                    help="the presentation corpus to canonize")
    ap.add_argument("--out", default=_HERE, help="where det/ + sos/ land")
    ap.add_argument("--timeout", type=float, default=15.0,
                    help="per-input wall clock, seconds (0 disables)")
    ap.add_argument("--cap", type=int, default=20000,
                    help="the |EM1| closure cap handed to invariant_of")
    ap.add_argument("--max-sos", type=int, default=1 << 20,
                    help="reject a language whose .sos (or its dual's) exceeds "
                         "this many bytes; 0 admits every size")
    ap.add_argument("--no-complement", dest="complement", action="store_false",
                    help="skip the complement closure (primals only)")
    args = ap.parse_args(argv)

    r = build(args.inputs, args.out, args.timeout, args.complement,
              args.cap, args.max_sos)
    skipped = len(r["skipped"])
    print(f"[corpus] {r['scanned']} inputs -> {r['primal_langs']} distinct "
          f"languages (+{r['dual_langs']} complements = {r['total_langs']}) "
          f"-> corpus/{{det,sos}}/"
          + (f"; {skipped} skipped (see census.md)" if skipped else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
