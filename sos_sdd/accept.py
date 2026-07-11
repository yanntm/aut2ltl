"""HOA acceptance formulas evaluated on inf-mark sets. The digest keeps
the acceptance condition as text; this module grounds it into the numeric
form the engine consumes: the set of accepting mark masks (Phase 3's
`Acc` predicate is a membership test against that table).

Grammar (the HOA subset the digests use): `t`, `f`, `Inf(n)`, `Fin(n)`,
`&`, `|`, parentheses — `&` binds tighter than `|`. Anything else (e.g.
negated marks `Inf(!n)`) is refused loudly."""

import re
from typing import List, Tuple

_TOKEN = re.compile(r"\s*(Inf|Fin|[tf&|()]|\d+)")


def _tokens(formula: str) -> List[str]:
    out: List[str] = []
    pos = 0
    while pos < len(formula):
        m = _TOKEN.match(formula, pos)
        if m is None:
            raise ValueError(f"unsupported acceptance syntax at {formula[pos:]!r}")
        out.append(m.group(1))
        pos = m.end()
    return out


def eval_acceptance(formula: str, mask: int) -> bool:
    """Evaluate `formula` on the inf-set `mask` (bit m set = mark m seen
    infinitely often): `Inf(m)` reads bit m, `Fin(m)` its negation."""
    toks = _tokens(formula)
    pos = 0

    def peek() -> str:
        return toks[pos] if pos < len(toks) else ""

    def take(expected: str) -> None:
        nonlocal pos
        if peek() != expected:
            raise ValueError(f"acceptance formula {formula!r}: expected "
                             f"{expected!r} at token {pos}")
        pos += 1

    def atom() -> bool:
        nonlocal pos
        t = peek()
        if t == "(":
            take("(")
            v = disj()
            take(")")
            return v
        if t in ("Inf", "Fin"):
            pos += 1
            take("(")
            m = peek()
            if not m.isdigit():
                raise ValueError(f"acceptance formula {formula!r}: mark "
                                 f"expected, got {m!r}")
            pos += 1
            take(")")
            bit = bool(mask & (1 << int(m)))
            return bit if t == "Inf" else not bit
        if t in ("t", "f"):
            pos += 1
            return t == "t"
        raise ValueError(f"acceptance formula {formula!r}: unexpected {t!r}")

    def conj() -> bool:
        v = atom()
        while peek() == "&":
            take("&")
            v &= atom()
        return v

    def disj() -> bool:
        v = conj()
        while peek() == "|":
            take("|")
            v |= conj()
        return v

    result = disj()
    if pos != len(toks):
        raise ValueError(f"acceptance formula {formula!r}: trailing tokens")
    return result


def accept_masks(formula: str, n_marks: int) -> Tuple[int, ...]:
    """Every mark mask over `n_marks` marks the formula accepts, sorted —
    the numeric acceptance table a slot model carries."""
    return tuple(m for m in range(1 << n_marks) if eval_acceptance(formula, m))
