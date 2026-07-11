"""`sos.minimize.remove_free_aps` — dropping the APs a language ignores.

Four laws, on a durable fixture (the invariant of a real k=3 sampled language
whose first proposition is free — the one that tripped `flatten --canon`'s
complement cross-check) plus a control that is already minimal:

  1. **detects and drops** — the free AP leaves the alphabet, and the result is
     itself minimal (`free_aps` empty);
  2. **idempotent** — minimizing again is a no-op (returns the same object);
  3. **commutes with complement** — `remove_free_aps(inv.complement())` equals
     `remove_free_aps(inv).complement()`. This is the property that makes
     "complement = flip P" hold at the minimal alphabet, so flip-P and
     `spot.dualize` agree once both sides are minimized;
  4. **leaves a minimal invariant untouched** — no free AP ⇒ same object back.

Also reports how many committed `flat_canon` languages carry a free AP, to size
whether the tracked corpus is already alphabet-minimal.

Run: ``python3 -m tests.sos.test_minimize`` from ``sosl/``.
"""
from __future__ import annotations

import glob
import os
import sys

_SOSL = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
if _SOSL not in sys.path:
    sys.path.insert(0, _SOSL)

from sosl.sos.io.serialize import dump_invariant, load_invariant   # noqa: E402
from sosl.sos.minimize import free_aps, remove_free_aps            # noqa: E402

# A real k=3 sampled language (2state3ap1acc_parity) whose proposition `a` is
# free: every minterm and its `a`-toggle map to the same class in `letters`.
FREE_A = """SOS v1
ap: a b c
classes: 4
0 eps
1 !a&!b&!c
2 !a&!b&c
3 !a&b&!c
letters: !a&!b&!c->1 !a&!b&c->2 !a&b&!c->3 !a&b&c->1 a&!b&!c->1 a&!b&c->2 a&b&!c->3 a&b&c->1
mult:
0: 0 1 2 3
1: 1 1 1 1
2: 2 1 2 2
3: 3 1 2 3
accept:
1 1
1 2
1 3
2 2
"""


def main() -> int:
    fails = 0

    inv = load_invariant(FREE_A)
    assert free_aps(inv) == (0,), free_aps(inv)          # `a` is the free one
    m = remove_free_aps(inv)
    m.validate()

    # 1. detects and drops
    if "a" in m.alphabet.aps or free_aps(m) != ():
        print(f"FAIL detect/drop: aps={m.alphabet.aps} free={free_aps(m)}"); fails += 1
    else:
        print(f"OK   drop free AP: {inv.alphabet.aps} -> {m.alphabet.aps}")

    # 2. idempotent
    if remove_free_aps(m) is not m:
        print("FAIL idempotence: second pass changed the invariant"); fails += 1
    else:
        print("OK   idempotent")

    # 3. commutes with complement (why flip-P == dualize after minimizing)
    lhs = remove_free_aps(inv.complement())
    rhs = m.complement()
    if dump_invariant(lhs) != dump_invariant(rhs):
        print("FAIL complement-commute: minimize∘complement != complement∘minimize")
        fails += 1
    else:
        print("OK   minimize commutes with complement")

    # 4. an already-minimal invariant is returned untouched
    if remove_free_aps(m) is not m:
        print("FAIL minimal-unchanged"); fails += 1
    else:
        print("OK   minimal invariant untouched")

    # Corpus census: how many committed flat_canon languages are non-minimal?
    corpus = os.path.join(_SOSL, os.pardir, "genaut", "corpus", "flat_canon", "sos")
    files = sorted(glob.glob(os.path.join(corpus, "*.sos")))
    nonmin = [os.path.basename(f) for f in files
              if free_aps(load_invariant(open(f).read()))]
    print(f"\nflat_canon: {len(nonmin)}/{len(files)} languages carry a free AP "
          f"(non-minimal)")
    for name in nonmin[:10]:
        print(f"  - {name}")

    print("\nPASS" if not fails else f"\nFAIL ({fails})")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
