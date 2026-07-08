"""Check that a corpus tier's det HOA and its `.sos` denote the same language —
per file, `canonize(det)` should reproduce the stored `.sos`. Reports, over a
tier folder with `det/` and `sos/` siblings:

    strict   : canonize(det) == stored .sos            (built from one D)
    relabel  : canonize(det) ≡ stored .sos up to B_k   (same language, twin polarity)
    broken   : neither                                 (different languages)

Run from the sosl/ root, giving a folder that contains det/ and sos/:

    python -m tests.genaut.source_consistency genaut/corpus/flat
    python -m tests.genaut.source_consistency genaut/corpus/sampled/2state1ap2acc_parity__seed0
"""
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(_REPO, "sosl"))
import spot                                                # noqa: E402
from sosl.sos.build.importer import canonical              # noqa: E402
from sosl.sos.core.quotient import invariant_of            # noqa: E402
from sosl.sos.io.serialize import dump_invariant           # noqa: E402
from sosl.sos.relabel import canonical_sos                 # noqa: E402


def main(argv: list) -> int:
    if not argv:
        print(__doc__)
        return 2
    base = os.path.join(_REPO, argv[0]) if not os.path.isabs(argv[0]) else argv[0]
    det_dir, sos_dir = os.path.join(base, "det"), os.path.join(base, "sos")
    idents = sorted(f[:-4] for f in os.listdir(sos_dir) if f.endswith(".sos"))

    strict = relabel = broken = 0
    examples = []
    for ident in idents:
        sos = open(os.path.join(sos_dir, ident + ".sos")).read()
        det_sos = dump_invariant(invariant_of(canonical(
            spot.automaton(open(os.path.join(det_dir, ident + ".hoa")).read()))))
        if det_sos == sos:
            strict += 1
        elif canonical_sos(det_sos) == canonical_sos(sos):
            relabel += 1
            if len(examples) < 3:
                examples.append(("relabel-twin", ident))
        else:
            broken += 1
            if len(examples) < 3:
                examples.append(("BROKEN", ident))
    n = len(idents)
    print(f"[{argv[0]}]  files={n}")
    print(f"    strict (det==sos):            {strict}")
    print(f"    relabel-twin (same lang):     {relabel}")
    print(f"    broken (different languages):  {broken}")
    for kind, ident in examples:
        print(f"    e.g. {kind}: {ident}")
    print("OK" if broken == 0 else "FAIL")
    return 0 if broken == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
