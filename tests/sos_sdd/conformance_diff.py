"""Diagnostic: print the engine's and the reference's `.sos` side by side
for one named conformance case (argv). Not a gate — a probe for C7
divergences."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from conformance_test import CASES, LOGS, to_hoa  # noqa: E402
from e0_triptych import TRIPTYCH  # noqa: E402
from phase2_test import MOD3  # noqa: E402
from residuals_test import DUPE, STEM  # noqa: E402

from sos_sdd import Automaton, Engine  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "sosl"))

from sosl.sos.build import reference_of_hoa  # noqa: E402
from sosl.sos.io.serialize import dump_invariant  # noqa: E402

AUTS = {a.name: a for a, _ in TRIPTYCH}
AUTS.update({"mod3": MOD3, "dupe": DUPE, "stem": STEM})


def main() -> None:
    LOGS.mkdir(exist_ok=True)
    aut = AUTS[sys.argv[1]]
    hoa = LOGS / f"conformance_{aut.name}.hoa"
    hoa.write_text(to_hoa(aut))
    want = dump_invariant(reference_of_hoa(str(hoa)))
    got = Engine(square="off").build(aut, until_phase=6).to_sos()
    print("=== engine ===")
    print(got)
    print("=== reference ===")
    print(want)


if __name__ == "__main__":
    main()
