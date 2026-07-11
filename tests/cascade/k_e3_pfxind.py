"""K-E3 airtight check: does any prefix-independent language have a non-frozen
final layer? (Cheap — C1/C2 only, no decider, so it covers the budget-skips.)

    python3 -m tests.cascade.k_e3_pfxind <census.jsonl> <corpus/sos DIR>

The Cor C.9 gating stratum needs a prefix-independent language with a terminal
1-anchored NON-frozen final layer. The draft's C.3 ⟨TBD⟩ suspects none exists.
This scans every corpus language and reports the count (and any instances).
"""
from __future__ import annotations

import json
import sys
from typing import List

from aut2ltl.sos2ltl.cayley import build  # noqa: F401 (puts sosl on sys.path)
from aut2ltl.sos2ltl.anchoring import analyze_layer
from aut2ltl.sos2ltl.readoffs import is_prefix_independent
from sosl.sos import load_invariant


def main(argv: List[str]) -> int:
    census, sos_dir = argv[0], argv[1].rstrip("/")
    ids = [json.loads(l)["id"] for l in open(census) if '"id"' in l]

    n_pi = 0
    hits: List[str] = []
    for lang_id in ids:
        with open(f"{sos_dir}/{lang_id}.sos") as f:
            inv = load_invariant(f.read())
        if not is_prefix_independent(inv):
            continue
        n_pi += 1
        cay = build(inv)
        fid = len(cay.layers) - 1
        anc = analyze_layer(cay, fid)
        frozen = all(k == "neutral" for k in anc.letter_kind.values())
        if not frozen:
            hits.append(lang_id)

    print(f"K-E3 pfxind check: {len(ids)} languages, {n_pi} prefix-independent")
    print(f"  prefix-independent with NON-frozen final layer: {len(hits)}")
    if hits:
        print(f"  INSTANCES (Cor C.9 candidates!): {hits[:12]}")
    else:
        print("  => C.9 gating stratum empty on the census: "
              "prefix-independence forces a frozen final layer (C.3 ⟨TBD⟩ settled)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
