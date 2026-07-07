"""Build every figure/table part for ONE input language — the collection
driver behind `research_notes/sos_figures.md`.

Input is either an HOA file or an LTL/PSL formula string; both are reduced to
the canonical deterministic form and run through the SoS construction
(`sosl.sos.core`). The script prints, for that one language:

  * the Figure-1 line     — |Q|, letters, acceptance of the deterministic form;
  * the Table-1 row       — |Q|, |EM1|, |S(L)+1|, and whether the transition
                            monoid carries a group (a presentation property of
                            the state maps, marks forgotten);
  * the Table-2 block     — every EM element as its (st, mk) vector, the
                            right-multiplication-by-letter table, and the
                            surjection each element -> its S(L)+1 class(es) (the
                            identity element hosts two under the fresh-identity
                            convention: [eps] and any neutral non-empty class);
  * the Table-3 block     — the canonical algebra S(L)+1 (keyed classes,
                            letter map, class multiplication table, accepting
                            linked pairs);
  * the .sos export       — the canonical serialization of the invariant
                            I(L), produced by the sole SoS exporter
                            (`sosl.sos.dump_invariant`), written to
                            `--sos PATH`; with `--residuals` the export carries
                            the optional right-congruence trailer (on for
                            figures, off elsewhere).

Everything — the EM(D) element dump, the fingerprint sizes, the algebra and the
export — is sourced from `sosl.sos` (the core construction and its fresh-identity
freeze). The LTL-definability verdict and its defining-formula / refuting
certificate are NOT computed here: that decision belongs to the definability
engine (`aut2ltl`), and the paper's fingerprint table curates it by hand.

Usage (module run from `sosl/` subtree root):
  python3 -m tests.sos.build_sos <file.hoa | 'LTL/PSL formula'> [--sos OUT] [--residuals]

Single input, self-bound; a closure that blows the cap is reported and exits 2.
No verdict logic of its own beyond what the pipeline returns.
"""
from __future__ import annotations

import os
import sys
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

import spot

from sosl.sos import Invariant, dump_invariant
from sosl.sos.alphabet import Alphabet, Letter
from sosl.sos.io.serialize import render_letter, render_word
from sosl.sos.build import import_hoa, residuals_of_hoa
from sosl.sos.core import SosData, pipeline, freeze


StateMap = Tuple[int, ...]


def to_hoa_path(arg: str, scratch_dir: str) -> str:
    """Return an HOA path for `arg`: itself if it is a file, else the
    deterministic translation of the LTL/PSL formula it denotes, materialized
    under `scratch_dir` (canonicity makes the choice of D irrelevant)."""
    if os.path.isfile(arg):
        return arg
    aut = spot.translate(spot.formula(arg),
                         "deterministic", "generic", "complete")
    os.makedirs(scratch_dir, exist_ok=True)
    path = os.path.join(scratch_dir, "_input.hoa")
    with open(path, "w") as fh:
        fh.write(aut.to_str("hoa"))
    return path


def state_map_period(t: StateMap) -> int:
    """The period of the power sequence of one state transformation `t`
    (`t[q] = δ(q, w)`), under `w ↦ w²` composition. Period `1` means `t` is
    aperiodic; period `> 1` is a group cycle of that length."""
    seen: dict = {}
    cur: StateMap = t
    k: int = 1
    while cur not in seen:
        seen[cur] = k
        cur = tuple(t[cur[q]] for q in range(len(t)))
        k += 1
    return k - seen[cur]


def transition_monoid_has_group(data: SosData) -> bool:
    """Whether the transition monoid of `D` — the state maps of `EM(D)` with
    the marks forgotten — carries a nontrivial group (some element of power
    period `> 1`)."""
    smaps = {tuple(dst for (dst, _m) in el) for el in data.mon.elems}
    return any(state_map_period(t) > 1 for t in smaps)


def letter_names(ab: Alphabet) -> List[str]:
    """Each letter of `ab` as its cube string (`!a`, `a&!b`, `t`), mask order."""
    return [render_letter(ab, Letter(a)) for a in range(ab.size)]


def em_surjection(data: SosData, inv: Invariant) -> Dict[int, List[int]]:
    """Each EM(D) element id -> the final S(L)+1 classes it hosts. A singleton
    for every element except the identity, which — under the fresh-identity
    convention — hosts both `[eps]` and any neutral non-empty class whose
    enriched element coincides with it (e.g. `[eps]` and `[a;a]` in EvenBlocks).

    Built by folding each final class's key word back to its enriched element
    and grouping the classes by that element's congruence class (`data.cls`) —
    a one-to-many relation exactly at the identity element (`[eps]`'s empty key
    folds to element 0, as does every neutral class's key). The monoid and the
    invariant share one alphabet mask order, so no letter remapping is needed."""
    finals_of_cls: Dict[int, List[int]] = defaultdict(list)
    for c in range(inv.n):
        e = 0
        for a in inv.keys[c]:
            e = data.mon.right[e][a]
        finals_of_cls[data.cls[e]].append(c)
    return {ei: finals_of_cls.get(data.cls[ei], [])
            for ei in range(len(data.mon))}


def print_figure1(data: SosData) -> None:
    print("# Figure 1 — deterministic form")
    print(f"  |Q| = {data.aut.num_states()}   "
          f"letters = {letter_names(data.alphabet)}   "
          f"init = {data.init}   acc = {data.aut.get_acceptance()}")


def print_table1(data: SosData, inv: Invariant) -> None:
    print("\n# Table 1 — fingerprint row")
    print(f"  |Q|          = {data.aut.num_states()}")
    print(f"  |EM1|        = {len(data.mon)}")
    print(f"  |S(L)+1|     = {inv.n}")
    print(f"  group in TM? = {transition_monoid_has_group(data)}")


def print_table2(data: SosData, inv: Invariant, surj: Dict[int, List[int]]) -> None:
    mon = data.mon
    n = data.aut.num_states()
    ab = inv.alphabet
    names = letter_names(ab)
    print("\n# Table 2 — EM(D): (st, mk) vectors, right-mult, surjection")
    print(f"  {'id':>3}  {'word':<10} {'st-vector':<{3*n+2}} "
          f"{'mk-vector':<{4*n+2}} -> class")
    for ei in range(len(mon)):
        word = render_word(ab, mon.rep[ei])
        st = "[" + " ".join(str(dst) for (dst, _m) in mon.elems[ei]) + "]"
        mk = "[" + " ".join(
            "{" + ",".join(map(str, sorted(m))) + "}" if m else "{}"
            for (_d, m) in mon.elems[ei]) + "]"
        hosted = " / ".join(
            f"{c} {render_word(ab, inv.keys[c])}" for c in surj[ei])
        print(f"  {ei:>3}  {word:<10} {st:<{3*n+2}} {mk:<{4*n+2}} -> {hosted}")
    # right multiplication by each letter, on EM element ids.
    print("  right-mult by letter (rows = element id):")
    print("       " + "   ".join(names))
    for ei in range(len(mon)):
        row = "   ".join(f"{mon.right[ei][a]}" for a in range(ab.size))
        print(f"    {ei:>3}: {row}")


def print_table3(inv: Invariant) -> None:
    ab = inv.alphabet
    k = inv.n
    print("\n# Table 3 — S(L)+1: canonical algebra")
    print("  classes (id: key [idem]):")
    for i in range(k):
        tag = "  idempotent" if inv.mult[i][i] == i else ""
        print(f"    {i}: {render_word(ab, inv.keys[i])}{tag}")
    print("  letters: " + "  ".join(
        f"{render_letter(ab, Letter(a))}->{inv.letter_class[a]}"
        for a in range(ab.size)))
    print("  mult (row i . col j):")
    print("      " + " ".join(f"{j}" for j in range(k)))
    for i in range(k):
        print(f"    {i} " + " ".join(f"{inv.mult[i][j]}" for j in range(k)))
    lp = sorted(inv.linked_pairs())
    ap = sorted(inv.accept)
    print(f"  linked pairs ({len(lp)}): "
          + " ".join(f"({s},{e})" for (s, e) in lp))
    print(f"  accepting pairs ({len(ap)}): " + " ".join(
        f"([{render_word(ab, inv.keys[s])}],[{render_word(ab, inv.keys[e])}])"
        for (s, e) in ap))


def main(argv: List[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 1
    inp = argv[1]
    sos_out: Optional[str] = None
    if "--sos" in argv:
        sos_out = argv[argv.index("--sos") + 1]
    with_residuals = "--residuals" in argv

    scratch = os.path.join(os.path.dirname(__file__), "logs")
    path = to_hoa_path(inp, scratch)
    data = pipeline(import_hoa(path))
    if data is None:
        print("closure : blew the cap")
        return 2
    inv = freeze(data)
    surj = em_surjection(data, inv)

    print(f"## input: {inp}")
    print_figure1(data)
    print_table1(data, inv)
    print_table2(data, inv, surj)
    print_table3(inv)
    print("\n# .sos export")
    res = residuals_of_hoa(path) if with_residuals else None
    text = dump_invariant(inv, residuals=res)
    print(text, end="")
    if sos_out is not None:
        with open(sos_out, "w") as fh:
            fh.write(text)
        print(f"(written to {sos_out})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
