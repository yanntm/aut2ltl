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
                            surjection each element -> its S(L)+ class;
  * the Table-3 block     — the canonical algebra S(L)+1 (keyed classes,
                            letter map, class multiplication table, accepting
                            linked pairs);
  * the .sosg export      — an HOA-like ASCII serialization of the invariant
                            I(L) = (keyed classes, letter map, mult table,
                            accepting-pair set), written to `--sosg PATH`.

Usage (module run from repo root):
  python3 -m tests.sosg.build_sosg <file.hoa | 'LTL/PSL formula'> [--sosg OUT]

Single input, self-bound; a closure that blows the cap is reported and exits 2.
No verdict logic of its own beyond what the pipeline returns.
"""
from __future__ import annotations

import os
import sys
import time
from typing import List, Optional, Tuple

import spot

from tests.probes.dg_common import DgData, quotient_of_hoa
from aut2ltl.bls.definability.generators import extract_generators
from aut2ltl.bls.definability.oracle.profile import profile
from aut2ltl.bls.definability.oracle.residuals import state_classes
from aut2ltl.bls.definability.oracle.quotient import find_group
from aut2ltl.bls.definability.oracle.refine import chase
from aut2ltl.bls.definability.oracle.family import assemble
from aut2ltl.bls.definability.dg.synth import DgDecline, synthesize


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


def elem_class(data: DgData, ei: int) -> int:
    """The canonical S(L)+ class of EM element `ei`: fold its representative
    word through the frozen algebra's tables."""
    return data.alg.word_cls(data.mon.rep[ei])


def print_figure1(data: DgData) -> None:
    print("# Figure 1 — deterministic form")
    print(f"  |Q| = {data.aut.num_states()}   letters = {data.names}   "
          f"init = {data.init}   acc = {data.aut.get_acceptance()}")


def print_table1(data: DgData) -> None:
    print("\n# Table 1 — fingerprint row")
    print(f"  |Q|             = {data.aut.num_states()}")
    print(f"  |EM1|           = {len(data.mon)}")
    print(f"  |S(L)+1|        = {len(data.alg)}")
    print(f"  group in TM?    = {transition_monoid_has_group(data)}")
    print(f"  group in S(L)+? = {data.group is not None}")
    print(f"  LTL?            = {data.group is None}")
    print(f"  evidence        = {certificate_or_formula(data)}")


def print_table2(data: DgData) -> None:
    mon = data.mon
    n = data.aut.num_states()
    print("\n# Table 2 — EM(D): (st, mk) vectors, right-mult, surjection")
    print(f"  {'id':>3}  {'word':<10} {'st-vector':<{3*n+2}} "
          f"{'mk-vector':<{4*n+2}} -> class")
    for ei in range(len(mon)):
        word = ";".join(data.names[li] for li in mon.rep[ei]) or "eps"
        st = "[" + " ".join(str(dst) for (dst, _m) in mon.elems[ei]) + "]"
        mk = "[" + " ".join(
            "{" + ",".join(map(str, sorted(m))) + "}" if m else "{}"
            for (_d, m) in mon.elems[ei]) + "]"
        cid = elem_class(data, ei)
        print(f"  {ei:>3}  {word:<10} {st:<{3*n+2}} {mk:<{4*n+2}} -> "
              f"{cid} [{data.alg.key(cid)}]")
    # right multiplication by each letter, on EM element ids.
    print("  right-mult by letter (rows = element id):")
    print("       " + "   ".join(data.names))
    for ei in range(len(mon)):
        row = "   ".join(f"{mon.right[ei][li]}" for li in range(len(data.names)))
        print(f"    {ei:>3}: {row}")


def print_table3(data: DgData) -> None:
    alg = data.alg
    k = len(alg)
    print("\n# Table 3 — S(L)+1: canonical algebra")
    print("  classes (id: key [idem]):")
    for i in range(k):
        tag = "  idempotent" if alg.idem[i] else ""
        print(f"    {i}: {alg.key(i)}{tag}")
    print("  letters: " + "  ".join(
        f"{data.names[li]}->{alg.letter_cls[li]}"
        for li in range(len(data.names))))
    print("  mult (row i . col j):")
    print("      " + " ".join(f"{j}" for j in range(k)))
    for i in range(k):
        print(f"    {i} " + " ".join(f"{alg.mult[i][j]}" for j in range(k)))
    lp = alg.linked_pairs()
    ap = alg.accepting_pairs()
    print(f"  linked pairs ({len(lp)}): "
          + " ".join(f"({s},{e})" for (s, e) in lp))
    print(f"  accepting pairs ({len(ap)}): "
          + " ".join(f"([{alg.key(s)}],[{alg.key(e)}])" for (s, e) in ap))


def sosg_text(data: DgData) -> str:
    """The .sosg export: an HOA-like ASCII serialization of I(L)."""
    alg = data.alg
    k = len(alg)
    out: List[str] = []
    out.append("SOSG: v1")
    out.append("alphabet: " + " ".join(data.names))
    out.append(f"classes: {k}")
    out.append("# id  key(shortlex-least word; ';'-joined; eps=empty)  [idem]")
    for i in range(k):
        tag = "  idem" if alg.idem[i] else ""
        out.append(f"{i}   {alg.key(i)}{tag}")
    out.append("letters: " + "  ".join(
        f"{data.names[li]}->{alg.letter_cls[li]}"
        for li in range(len(data.names))))
    out.append("mult:")
    out.append("     " + " ".join(f"{j}" for j in range(k)))
    for i in range(k):
        out.append(f"  {i}  " + " ".join(f"{alg.mult[i][j]}" for j in range(k)))
    out.append("accept:            # accepting linked pairs (s,e): e idem, s.e=s")
    for (s, e) in alg.accepting_pairs():
        out.append(f"  ({s},{e})")
    return "\n".join(out) + "\n"


def main(argv: List[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 1
    inp = argv[1]
    sosg_out: Optional[str] = None
    if "--sosg" in argv:
        sosg_out = argv[argv.index("--sosg") + 1]

    scratch = os.path.join(os.path.dirname(__file__), "logs")
    path = to_hoa_path(inp, scratch)
    data = quotient_of_hoa(path)
    if data is None:
        print("closure : blew the cap")
        return 2

    print(f"## input: {inp}")
    print_figure1(data)
    print_table1(data)
    print_table2(data)
    print_table3(data)
    print("\n# .sosg export")
    text = sosg_text(data)
    print(text, end="")
    if sosg_out is not None:
        with open(sosg_out, "w") as fh:
            fh.write(text)
        print(f"(written to {sosg_out})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
