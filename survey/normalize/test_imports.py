"""Guard the package's public surface the way its clients import it: the
installed package path `from survey.normalize import ...`.

Run (from the repo root): python3 -m survey.normalize.test_imports   (OK / raises)
"""
from __future__ import annotations

from survey.normalize import (
    _is_hoa_text,
    normalize_hoa,
    normalize_ltl,
    polarity_normalize_hoa,
    polarity_normalize_ltl,
)

assert normalize_ltl("p & q") == "a & b"
assert polarity_normalize_ltl("!p & q") == "p & q"
assert _is_hoa_text("HOA: v1\n")
assert callable(normalize_hoa) and callable(polarity_normalize_hoa)

print("OK")
