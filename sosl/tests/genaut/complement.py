"""Complement in two ways and cross-check, then report flat_canon's closure under
complement. Run from the sosl/ root:

    python -m tests.genaut.complement [id-substring]

(1) Agreement: for a sample, `spot.dualize(det)` (De Morgan on the acceptance)
    yields the same language as flipping `P` in the invariant — i.e.
    canonize(dualize(det)) == the P-flip `.sos`, up to relabeling.
(2) Closure: for every catalogued language, is its complement (the P-flip, which
    is already canonical since σ* is complement-invariant) also catalogued? Counts
    present / missing / self-dual, and the size the corpus would reach once closed.
"""
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(_REPO, "sosl"))
import spot                                                # noqa: E402
from sosl.sos.build.importer import canonical              # noqa: E402
from sosl.sos.core.quotient import invariant_of            # noqa: E402
from sosl.sos.invariant import Invariant                   # noqa: E402
from sosl.sos.io.serialize import dump_invariant, load_invariant  # noqa: E402
from sosl.sos.relabel import canonical_sos                 # noqa: E402

DET = os.path.join(_REPO, "genaut", "corpus", "flat_canon", "det")
SOS = os.path.join(_REPO, "genaut", "corpus", "flat_canon", "sos")


def complement(inv: Invariant) -> Invariant:
    """Flip P against the linked pairs — the SoS complement ([SωS26 §5])."""
    return Invariant(alphabet=inv.alphabet, keys=inv.keys,
                     letter_class=inv.letter_class, mult=inv.mult,
                     accept=frozenset(inv.linked_pairs() - inv.accept),
                     identity=inv.identity)


def main(argv: list) -> int:
    needle = argv[0] if argv else ""
    idents = sorted(f[:-4] for f in os.listdir(SOS) if f.endswith(".sos") and needle in f)

    # (1) det-dualize agrees with P-flip on a sample.
    agree = fail = 0
    for ident in idents[::max(1, len(idents) // 40)]:
        inv = load_invariant(open(os.path.join(SOS, ident + ".sos")).read())
        via_flip = canonical_sos(dump_invariant(complement(inv)))
        Dc = canonical(spot.dualize(spot.automaton(open(os.path.join(DET, ident + ".hoa")).read())))
        via_dual = canonical_sos(dump_invariant(invariant_of(Dc)))
        if via_flip == via_dual:
            agree += 1
        else:
            fail += 1
            if fail <= 3:
                print(f"  DISAGREE {ident}")
    print(f"[agreement] dualize(det) == flip(P): {agree}/{agree + fail}")

    # (2) closure of the whole catalogue (P-flip is already canonical).
    stored = {open(os.path.join(SOS, f)).read().strip()
              for f in os.listdir(SOS) if f.endswith(".sos")}
    present = missing = self_dual = 0
    for s in stored:
        comp = dump_invariant(complement(load_invariant(s))).strip()
        if comp == s:
            self_dual += 1
        elif comp in stored:
            present += 1
        else:
            missing += 1
    n = len(stored)
    print(f"[closure] catalogue={n}  complement present={present}  "
          f"missing={missing}  self-dual={self_dual}")
    print(f"          closed size would be {n + missing} "
          f"({'even' if (n + missing) % 2 == 0 else 'ODD -> ' + str(self_dual) + ' self-dual'})")
    print("OK" if fail == 0 else "FAIL")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
