"""HOA→digest bridge gate (`sos_sdd.hoa.digest_twa`, the C2 parser half).

Two directions, both ending in the engine's own byte gate:

- round-trip: an existing digest (triptych / mod3 / stem) is written as
  HOA (conformance_test.to_hoa), parsed back with spot.automaton,
  digested, and the engine's `.sos` from the round-tripped digest must
  byte-equal the `.sos` from the original digest;
- corpus: a `genaut/corpus/flat_canon/det/*.hoa` instance is digested
  and built, and the emitted `.sos` must byte-equal the precomputed
  `flat_canon/sos/<name>.sos` (det and sos tiers are a self-consistent
  pair) — the E1-shaped conformance check, no reference run needed.

A refusal probe asserts nondeterministic input is refused loudly. A
single case name as argv runs just that case; streams land in
tests/sos_sdd/logs/."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import spot  # noqa: E402

from conformance_test import to_hoa  # noqa: E402
from e0_triptych import TRIPTYCH  # noqa: E402
from phase2_test import MOD3  # noqa: E402
from residuals_test import STEM  # noqa: E402

from sos_sdd import Automaton, Engine  # noqa: E402
from sos_sdd.hoa import digest_twa  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
CORPUS = REPO / "genaut" / "corpus" / "flat_canon"
LOGS = Path(__file__).resolve().parent / "logs"


def build_sos(aut: Automaton, tag: str) -> str:
    log = LOGS / f"hoa_bridge_{tag}.jsonl"
    return Engine(square="off", stats=str(log)).build(aut, until_phase=6).to_sos()


def check_roundtrip(aut: Automaton) -> None:
    want = build_sos(aut, f"{aut.name}_direct")
    hoa = LOGS / f"hoa_bridge_{aut.name}.hoa"
    hoa.write_text(to_hoa(aut))
    back = digest_twa(spot.automaton(str(hoa)), aut.name)
    got = build_sos(back, f"{aut.name}_bridged")
    assert got == want, (f"{aut.name}: bridged .sos diverges from direct\n"
                         f"bridged:\n{got}\ndirect:\n{want}")
    print(f"{aut.name}: round-trip .sos byte-identical "
          f"({len(back.trans)} cubes from {len(aut.trans)})")


def check_corpus(name: str) -> None:
    dig = digest_twa(spot.automaton(str(CORPUS / "det" / f"{name}.hoa")), name)
    want = (CORPUS / "sos" / f"{name}.sos").read_text()
    got = build_sos(dig, name)
    if got != want:
        for i, (g, w) in enumerate(zip(got.splitlines(), want.splitlines())):
            if g != w:
                raise AssertionError(f"{name}: first diff at line {i}:\n"
                                     f"  engine {g!r}\n  corpus {w!r}")
        raise AssertionError(f"{name}: texts diverge in length only:\n"
                             f"engine:\n{got}\ncorpus:\n{want}")
    print(f"{name}: .sos byte-identical to the corpus reference")


def case_refuse() -> None:
    # Two initial edges on the same letter: not deterministic.
    nd = spot.automaton("""HOA: v1
States: 2
Start: 0
AP: 1 "a"
Acceptance: 1 Inf(0)
--BODY--
State: 0
[0] 0 {0}
[0] 1
State: 1
[t] 1
--END--
""")
    try:
        digest_twa(nd, "nd")
        raise AssertionError("nondeterministic input was not refused")
    except ValueError:
        print("refuse: nondeterministic input refused loudly")


CASES = {
    "gf_aa_parity": lambda: check_roundtrip(
        next(a for a, _ in TRIPTYCH if a.name == "gf_aa_parity")),
    "evenblocks": lambda: check_roundtrip(
        next(a for a, _ in TRIPTYCH if a.name == "evenblocks")),
    "mod3": lambda: check_roundtrip(MOD3),
    "stem": lambda: check_roundtrip(STEM),
    "corpus_0acc": lambda: check_corpus("1state1ap0acc_0"),
    "corpus_gba": lambda: check_corpus("1state1ap1acc_06"),
    "corpus_parity": lambda: check_corpus("1state1ap2acc_parity_018"),
    "corpus_compl": lambda: check_corpus("1state2ap0acc_01_c"),
    "refuse": case_refuse,
}


def main() -> None:
    LOGS.mkdir(exist_ok=True)
    for name in (sys.argv[1:] or CASES):
        CASES[name]()
    print("SUCCESS")


if __name__ == "__main__":
    main()
