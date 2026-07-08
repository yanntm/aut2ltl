"""Faithfulness test: does the sampler's per-combo chain reproduce the census?

For every id the exhaustive corpus kept (its filename), decode the id with the
sampler's combo_of, run the SAME build -> reduce -> canonical -> 𝓘 chain, and
compare the resulting `.sos` byte-for-byte with the corpus's stored reference for
that id. A full match proves the sampler is missing no pipeline step; any
remaining sampled-vs-corpus divergence in a full run is then a representative
choice (which polarity of a language happened to be kept), not a defect.

    python3 genaut/tests/sample_subset.py [shape]   # default 2,1,1
"""
import glob
import os
import sys

_GEN = os.path.join(os.path.dirname(__file__), os.pardir, "gen")
sys.path.insert(0, os.path.abspath(_GEN))
import spot                                        # noqa: E402
from build import build_aut, reduce_aut           # noqa: E402
from sample import combo_of                        # noqa: E402
from enumerate import parse_shape                  # noqa: E402

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
sys.path.insert(0, os.path.join(_REPO, "sosl"))
from sosl.sos import dump_invariant                # noqa: E402
from sosl.sos.build.importer import canonical      # noqa: E402
from sosl.sos.core.quotient import invariant_of    # noqa: E402


def main() -> int:
    token = sys.argv[1] if len(sys.argv) > 1 else "2,1,1"
    shape = parse_shape(token)
    det_dir = os.path.join(_REPO, "genaut", "corpus", "det", shape.tag)
    sos_dir = os.path.join(_REPO, "genaut", "corpus", "sos", shape.tag)
    bdict = spot.make_bdd_dict()

    files = sorted(glob.glob(os.path.join(det_dir, f"{shape.tag}_*.hoa")))
    match = mismatch = 0
    for f in files:
        ident = os.path.basename(f)[:-4]
        idx = int(ident.rsplit("_", 1)[1])
        red = reduce_aut(build_aut(shape, combo_of(shape, idx), bdict))
        dump = dump_invariant(invariant_of(canonical(red)))
        with open(os.path.join(sos_dir, f"{ident}.sos")) as fh:
            ref = fh.read()
        if dump == ref:
            match += 1
        else:
            mismatch += 1
            if mismatch <= 3:
                print(f"  MISMATCH {ident}")
    print(f"{shape.tag}: {match} match / {mismatch} mismatch over {len(files)} "
          f"corpus ids")
    print("FAITHFUL — sampler chain reproduces the census per id"
          if mismatch == 0 else "DIVERGENCE — the chain differs from canonize")
    return 1 if mismatch else 0


if __name__ == "__main__":
    raise SystemExit(main())
