"""Validate the signed-perm HOA relabeler `genaut.gen.flatten.relabel_hoa`: the
HOA edit must agree with the algebra relabeling, i.e.

    canonize(relabel_hoa(det, sigma*)) == canonical_sos(native_sos)

byte-for-byte, so a language's det HOA and its `.sos` land in the same canonical
labeling. Run from the sosl/ root:

    python -m tests.genaut.hoa_relabel [id-substring]
"""
import os
import re
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(_REPO, "sosl"))
sys.path.insert(0, os.path.join(_REPO, "genaut", "gen"))
import spot                                                # noqa: E402
from flatten import relabel_hoa                            # noqa: E402
from sosl.sos.build.importer import canonical              # noqa: E402
from sosl.sos.core.quotient import invariant_of            # noqa: E402
from sosl.sos.io.serialize import dump_invariant, load_invariant  # noqa: E402
from sosl.sos.relabel import canonical_relabeling          # noqa: E402

DET = os.path.join(_REPO, "genaut", "corpus", "flat", "det")
SOS = os.path.join(_REPO, "genaut", "corpus", "flat", "sos")


def _cases(needle: str) -> list:
    ids = [f[:-4] for f in sorted(os.listdir(SOS)) if f.endswith(".sos")]
    if needle:
        return [i for i in ids if needle in i]
    # nontrivial-relabeling coverage: k>=2 slice + a few k=1 polarity cases
    k2 = [i for i in ids if i.startswith(("1state2ap", "1state3ap"))][::40]
    k1 = [i for i in ids if i.startswith("2state1ap1acc")][:3]
    return k2 + k1


def main(argv: list) -> int:
    cases = _cases(argv[0] if argv else "")
    ok = fail = 0
    for ident in cases:
        native_sos = open(os.path.join(SOS, ident + ".sos")).read()
        inv = load_invariant(native_sos)
        k = len(inv.alphabet.aps)
        sigma, canon_inv = canonical_relabeling(inv)
        canon_sos = dump_invariant(canon_inv)

        relabeled = relabel_hoa(open(os.path.join(DET, ident + ".hoa")).read(), sigma, k)
        via_hoa = dump_invariant(invariant_of(canonical(spot.automaton(relabeled))))
        if via_hoa == canon_sos:
            ok += 1
        else:
            fail += 1
            if fail <= 3:
                print(f"  MISMATCH {ident} k={k} sigma={sigma}")
    print(f"[hoa-relabel] canonize(relabel_hoa)==canonical_sos: {ok}/{ok + fail}")
    print("OK" if fail == 0 else "FAIL")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
