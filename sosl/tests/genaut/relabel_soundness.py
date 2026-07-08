"""Soundness of the B_k AP-relabeling canonical form (`sosl.sos.relabel`) over the
genaut flat corpus, plus the measured fold. Run from the sosl/ root:

    python -m tests.genaut.relabel_soundness [id-substring]

Checks (all must pass): identity-relabel reproduces the already-canonical input
bytes; canon is idempotent; membership is faithful under every non-identity
relabeling (so canonicalization never merges non-equivalent languages). Then it
prints the distinct-up-to-relabeling counts per k.
"""
import os
import random
import re
import sys
import time

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(_REPO, "sosl"))
from sosl.sos.alphabet import Letter                       # noqa: E402
from sosl.sos.io.serialize import dump_invariant, load_invariant  # noqa: E402
from sosl.sos.lasso import Lasso                           # noqa: E402
from sosl.sos.relabel import (canonical_sos, mask_perms,   # noqa: E402
                              relabel_invariant)

SOS = os.path.join(_REPO, "genaut", "corpus", "flat", "sos")
_TAG = re.compile(r"^(\d+)state(\d+)ap(\d+)acc")


def _files(needle: str) -> list:
    return sorted(f for f in os.listdir(SOS)
                  if f.endswith(".sos") and needle in f)


def main(argv: list) -> int:
    needle = argv[0] if argv else ""
    files = _files(needle)
    random.seed(0)

    # 1. identity-relabel reproduces the canonical input bytes.
    bad = 0
    for f in files:
        inv = load_invariant(open(os.path.join(SOS, f)).read())
        _, rho_id = next(mask_perms(len(inv.alphabet.aps)))
        if dump_invariant(relabel_invariant(inv, rho_id)) != dump_invariant(inv):
            bad += 1
            if bad <= 3:
                print(f"  identity mismatch: {f}")
    print(f"[identity]   reproduces input: {len(files) - bad}/{len(files)}")

    # 2. idempotence on a slice.
    idem = tot = 0
    for f in files[::37]:
        c1 = canonical_sos(open(os.path.join(SOS, f)).read())
        idem += canonical_sos(c1) == c1
        tot += 1
    print(f"[idempotent] canon(canon)=canon: {idem}/{tot}")

    # 3. faithfulness: member agrees under every non-identity relabeling.
    checks = mism = 0
    faithful_set = [f for f in files if f.startswith(("1state2ap", "1state3ap"))][::5]
    for f in faithful_set:
        inv = load_invariant(open(os.path.join(SOS, f)).read())
        size = inv.alphabet.size
        for _sigma, rho in list(mask_perms(len(inv.alphabet.aps)))[1:]:
            ri = relabel_invariant(inv, rho)
            for _ in range(10):
                stem = tuple(Letter(random.randrange(size)) for _ in range(random.randint(0, 3)))
                loop = tuple(Letter(random.randrange(size)) for _ in range(random.randint(1, 3)))
                w = Lasso(stem, loop)
                wr = Lasso(tuple(Letter(rho[a]) for a in stem),
                           tuple(Letter(rho[a]) for a in loop))
                checks += 1
                mism += inv.member(w) != ri.member(wr)
    print(f"[faithful]   member agrees under relabeling: {checks - mism}/{checks}")

    # 4. the measured B_k fold.
    t0 = time.time()
    seen, per_k = set(), {}
    for f in files:
        k = int(_TAG.match(f).group(2))
        canon = canonical_sos(open(os.path.join(SOS, f)).read())
        per_k.setdefault(k, [0, set()])
        per_k[k][0] += 1
        per_k[k][1].add(canon)
        seen.add(canon)
    print(f"[fold] files={len(files)}  distinct-up-to-relabeling={len(seen)}  "
          f"({time.time() - t0:.1f}s)")
    for k in sorted(per_k):
        print(f"    k={k}: files={per_k[k][0]:5d}  orbit-distinct={len(per_k[k][1]):5d}")

    ok = bad == 0 and idem == tot and mism == 0
    print("OK" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
