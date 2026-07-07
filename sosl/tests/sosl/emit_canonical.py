"""Write the canonical form D of an input automaton to stdout as HOA.

    python3 -m tests.sosl.emit_canonical <hoa>

Emits the deterministic, complete, transition-based, generic-acceptance form the
sos import layer reads (``sos.build.import_hoa``) — the only automaton form that
belongs in ``research_notes/`` for a selected specimen, regardless of how the
source was presented.
"""
from __future__ import annotations

import sys

from sosl.sos.build import import_hoa


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: emit_canonical <hoa>", file=sys.stderr)
        return 2
    print(import_hoa(sys.argv[1]).to_str("hoa"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
