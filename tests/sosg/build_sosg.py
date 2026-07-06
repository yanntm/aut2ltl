"""Build every figure/table part for ONE input language — the collection
driver behind `research_notes/sosg_figures.md`.

Input is either an HOA file or an LTL/PSL formula string; both are reduced to
the canonical deterministic form and run through the definability pipeline
(`aut2ltl/bls/definability`). The script prints, for that one language:

  * the Figure-1 line     — |Q|, letters, acceptance of the deterministic form;
  * the Table-1 row       — |Q|, |EM1|, |S(L)+1|, group in the transition
                            monoid?, group in S(L)+?, LTL?, and either the DG
                            formula's DAG/flat-tree metrics (when LTL) or the
                            refuting certificate's shape/serialization;
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
                            (`sosl.objects.dump_invariant`), written to
                            `--sos PATH`; with `--residuals` the export carries
                            the optional right-congruence trailer (on for
                            figures, off elsewhere).

The algebra (Tables 2-3, the export) is sourced from `sosl.reference`, the
fixed fresh-identity builder; the EM(D) element dump and the fingerprint's
`|Q|`/`|EM1|`/group columns come from the definability pipeline.

Usage (module run from repo root):
  python3 -m tests.sosg.build_sosg <file.hoa | 'LTL/PSL formula'> [--sos OUT] [--residuals]

Single input, self-bound; a closure that blows the cap is reported and exits 2.
No verdict logic of its own beyond what the pipeline returns.
"""
from __future__ import annotations

import os
import sys
import time
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

import spot

from tests.probes.dg_common import DgData, quotient_of_hoa
from aut2ltl.bls.definability.generators import extract_generators
from aut2ltl.bls.definability.oracle.profile import profile
from aut2ltl.bls.definability.oracle.residuals import state_classes
from aut2ltl.bls.definability.oracle.quotient import find_group
from aut2ltl.bls.definability.oracle.refine import chase
from aut2ltl.bls.definability.oracle.family import assemble
from aut2ltl.bls.definability.dg.synth import DgDecline, synthesize

from sosl.objects import Invariant, dump_invariant
from sosl.objects.alphabet import Alphabet, Letter
from sosl.objects.serialize import render_letter, render_word
from sosl.reference import reference_of_hoa, residuals_of_hoa


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


def transition_monoid_has_group(data: DgData) -> bool:
    """Whether the transition monoid of `D` — the state maps of `EM(D)` with
    the marks forgotten — carries a nontrivial group (some element of power
    period `> 1`)."""
    smaps = {tuple(dst for (dst, _m) in el) for el in data.mon.elems}
    return any(state_map_period(t) > 1 for t in smaps)


def certificate_or_formula(data: DgData) -> str:
    """The Table-1 evidence cell. When `S(L)+` is aperiodic, synthesize the DG
    formula and report its DAG node count and flat-tree size (the raw formula
    is not human-sized); otherwise assemble the refuting family and report its
    shape (`F1` linear / `F2` ω-power) and serialization."""
    if data.group is None:
        t0 = time.time()
        try:
            ast, root, n_nodes = synthesize(data.alg, max_nodes=2000)
        except DgDecline as e:
            return f"LTL, DG declined: {e}"
        tree = ast.tree_size(root)
        return (f"LTL — DG DAG {n_nodes} nodes / flat tree {tree:,} "
                f"({time.time() - t0:.3f}s)")
    # non-LTL: rebuild the oracle seed and assemble the certificate.
    aut = data.aut
    gens, _masks, valuations = extract_generators(aut)
    st_cls = state_classes(aut)
    lin = [tuple(st_cls[st] for (st, _m) in el) for el in data.mon.elems]
    acc = aut.acc()
    prof = [profile(acc, el) for el in data.mon.elems]
    seed = list(zip(lin, prof))
    group = find_group(data.mon, data.cls)
    assert group is not None
    b = chase(data.mon, seed, group.powers[group.a - 1], group.powers[group.a])
    if b is None:
        return "NOT LTL — certificate chase FAILED"
    w = assemble(aut, gens, valuations, data.mon, lin, prof, group, b)
    if w is None:
        return "NOT LTL — certificate assembly FAILED"
    shape = "F2 (ω-power)" if w.omega_power else "F1 (linear)"
    return f"NOT LTL — {shape}, {w.serialize()}"


def li_of_masks(data: DgData, alphabet: Alphabet) -> List[int]:
    """Map each sosl letter mask to the pipeline's own letter index `li` (the
    valuations of `extract_generators` are in `li` order)."""
    _gens, _masks, valuations = extract_generators(data.aut)
    out: List[int] = [0] * alphabet.size
    for li, val in enumerate(valuations):
        trues = [ap for ap, truth in val.items() if truth]
        out[alphabet.letter_of(trues)] = li
    return out


def em_surjection(data: DgData, inv: Invariant,
                  li_of_mask: List[int]) -> Dict[int, List[int]]:
    """Each EM(D) element id -> the final S(L)+1 classes it hosts. A singleton
    for every element except the identity, which — under the fresh-identity
    convention — hosts both `[eps]` and any neutral non-empty class whose
    enriched element coincides with it (e.g. `[eps]` and `[a;a]` in EvenBlocks).
    Built by grouping the final classes by the *old* algebra class of their key
    word, a one-to-many relation exactly at the identity element."""
    finals_of_old: Dict[int, List[int]] = defaultdict(list)
    for c in range(inv.n):
        lis = tuple(li_of_mask[m] for m in inv.keys[c])
        finals_of_old[data.alg.word_cls(lis)].append(c)
    return {ei: finals_of_old.get(data.alg.word_cls(data.mon.rep[ei]), [])
            for ei in range(len(data.mon))}


def print_figure1(data: DgData) -> None:
    print("# Figure 1 — deterministic form")
    print(f"  |Q| = {data.aut.num_states()}   letters = {data.names}   "
          f"init = {data.init}   acc = {data.aut.get_acceptance()}")


def print_table1(data: DgData, inv: Invariant) -> None:
    print("\n# Table 1 — fingerprint row")
    print(f"  |Q|             = {data.aut.num_states()}")
    print(f"  |EM1|           = {len(data.mon)}")
    print(f"  |S(L)+1|        = {inv.n}")
    print(f"  group in TM?    = {transition_monoid_has_group(data)}")
    print(f"  group in S(L)+? = {data.group is not None}")
    print(f"  LTL?            = {data.group is None}")
    print(f"  evidence        = {certificate_or_formula(data)}")


def print_table2(data: DgData, inv: Invariant, surj: Dict[int, List[int]]) -> None:
    mon = data.mon
    n = data.aut.num_states()
    ab = inv.alphabet
    print("\n# Table 2 — EM(D): (st, mk) vectors, right-mult, surjection")
    print(f"  {'id':>3}  {'word':<10} {'st-vector':<{3*n+2}} "
          f"{'mk-vector':<{4*n+2}} -> class")
    for ei in range(len(mon)):
        word = ";".join(data.names[li] for li in mon.rep[ei]) or "eps"
        st = "[" + " ".join(str(dst) for (dst, _m) in mon.elems[ei]) + "]"
        mk = "[" + " ".join(
            "{" + ",".join(map(str, sorted(m))) + "}" if m else "{}"
            for (_d, m) in mon.elems[ei]) + "]"
        hosted = " / ".join(
            f"{c} {render_word(ab, inv.keys[c])}" for c in surj[ei])
        print(f"  {ei:>3}  {word:<10} {st:<{3*n+2}} {mk:<{4*n+2}} -> {hosted}")
    # right multiplication by each letter, on EM element ids.
    print("  right-mult by letter (rows = element id):")
    print("       " + "   ".join(data.names))
    for ei in range(len(mon)):
        row = "   ".join(f"{mon.right[ei][li]}" for li in range(len(data.names)))
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
    data = quotient_of_hoa(path)
    if data is None:
        print("closure : blew the cap")
        return 2
    inv = reference_of_hoa(path)
    surj = em_surjection(data, inv, li_of_masks(data, inv.alphabet))

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
