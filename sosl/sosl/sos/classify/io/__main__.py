"""Write a `.cat` sidecar next to every `.sos` in a folder.

    python3 -m sosl.sos.classify.io <sos-folder>
"""
from __future__ import annotations

import sys
from typing import List, Optional

from .writer import write_cats


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) != 1:
        print(__doc__, file=sys.stderr)
        return 2
    n = write_cats(argv[0])
    print(f"wrote {n} .cat sidecars in {argv[0]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
