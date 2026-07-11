"""Phase 6 (C7) conformance gate — spec §3: on every instance where the
explicit reference construction terminates, the engine's emitted `.sos`
must be BYTE-IDENTICAL to the reference's. The digest is written out as
HOA, `sosl.sos.build.reference_of_hoa` (Spot-backed, bounded by the
per-case timeout) builds the reference invariant, and the two texts are
compared as bytes — any difference is printed with its first diverging
line.

Cases: the triptych, mod3, stem; refusal probes (products and
quotient="symbolic" are refused at phase 6). `dupe` documents the one
recorded exclusion: its language is empty, Spot's postprocess strips the
unused AP on import, so the reference answers a different-AP
presentation — byte parity is only defined over the same AP set (the
format's own equality clause); the case asserts the AP drop and that the
engine still emits a well-formed empty-accept table. A single case name
as argv runs just that case. HOA scratch and stats streams land in
tests/sos_sdd/logs/."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from e0_triptych import TRIPTYCH  # noqa: E402
from e2_async import product as eb_product  # noqa: E402
from phase2_test import MOD3  # noqa: E402
from residuals_test import DUPE, STEM  # noqa: E402

from sos_sdd import Automaton, Engine  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "sosl"))

from sosl.sos.build import reference_of_hoa  # noqa: E402
from sosl.sos.io.serialize import dump_invariant  # noqa: E402

LOGS = Path(__file__).resolve().parent / "logs"


def to_hoa(aut: Automaton) -> str:
    """The digest as HOA text (transition-based marks, explicit labels)."""
    idx = {name: i for i, name in enumerate(aut.ap)}
    lines = ["HOA: v1", f"States: {aut.states}", f"Start: {aut.init}",
             "AP: " + " ".join([str(len(aut.ap))] + [f'"{a}"' for a in aut.ap]),
             f"Acceptance: {aut.marks} {aut.acceptance}", "--BODY--"]
    for q in range(aut.states):
        lines.append(f"State: {q}")
        for t in aut.trans:
            if t.src != q:
                continue
            label = ("t" if t.cube == "1" else
                     "&".join(f"!{idx[l[1:]]}" if l.startswith("!") else
                              str(idx[l]) for l in t.cube.split("&")))
            marks = (" {" + " ".join(str(m) for m in sorted(t.marks)) + "}"
                     if t.marks else "")
            lines.append(f"[{label}] {t.dst}{marks}")
    lines.append("--END--")
    return "\n".join(lines) + "\n"


def check(aut: Automaton) -> None:
    hoa = LOGS / f"conformance_{aut.name}.hoa"
    hoa.write_text(to_hoa(aut))
    want = dump_invariant(reference_of_hoa(str(hoa)))

    log = LOGS / f"conformance_{aut.name}.jsonl"
    s = Engine(square="off", stats=str(log)).build(aut, until_phase=6)
    got = s.to_sos()

    if got != want:
        for i, (g, w) in enumerate(zip(got.splitlines(), want.splitlines())):
            if g != w:
                raise AssertionError(
                    f"{aut.name}: first diff at line {i}:\n"
                    f"  engine    {g!r}\n  reference {w!r}")
        raise AssertionError(f"{aut.name}: texts diverge in length only:\n"
                             f"engine:\n{got}\nreference:\n{want}")
    print(f"{aut.name}: .sos byte-identical to the reference "
          f"({s.n_classes()} classes)")


def case_triptych(name: str) -> None:
    check(next(a for a, _ in TRIPTYCH if a.name == name))


def case_dupe() -> None:
    hoa = LOGS / f"conformance_{DUPE.name}.hoa"
    hoa.write_text(to_hoa(DUPE))
    want = dump_invariant(reference_of_hoa(str(hoa)))
    assert "\nap: \n" in want, f"AP drop expected in reference:\n{want}"
    got = Engine(square="off").build(DUPE, until_phase=6).to_sos()
    assert "\nap: a\n" in got and got.rstrip().endswith("accept:"), got
    print("dupe: recorded exclusion confirmed (reference strips the "
          "unused AP; engine emits the empty-accept table over 'a')")


def case_refuse() -> None:
    # Products and the symbolic quotient are refused at phase 6.
    try:
        Engine(square="off").build(eb_product(2), until_phase=6)
        raise AssertionError("product .sos emission was not refused")
    except NotImplementedError:
        pass
    try:
        Engine(square="off", quotient="symbolic").build(DUPE, until_phase=6)
        raise AssertionError("quotient=symbolic was not refused")
    except NotImplementedError:
        pass


CASES = {
    "gf_aa_parity": lambda: case_triptych("gf_aa_parity"),
    "even": lambda: case_triptych("even"),
    "evenblocks": lambda: case_triptych("evenblocks"),
    "mod3": lambda: check(MOD3),
    "dupe": case_dupe,
    "stem": lambda: check(STEM),
    "refuse": case_refuse,
}


def main() -> None:
    LOGS.mkdir(exist_ok=True)
    for name in (sys.argv[1:] or CASES):
        CASES[name]()
    print("SUCCESS")


if __name__ == "__main__":
    main()
