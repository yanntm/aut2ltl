"""The counting family — the portable non-LTL certificate value.

A family samples lassos indexed by `n ≥ 0` in one of Arnold's two context
shapes and declares that membership toggles with `n mod period`:

    linear    sample(n) = u · vⁿ · x_prefix · (x_loop)^ω
    ω-power   sample(n) = u · (vⁿ · y)^ω

`pattern[i]` is the declared membership at phase `i = n mod period`; it is
non-constant and `period > 1`, so a validated family refutes aperiodicity of
the syntactic algebra — hence LTL-definability — by membership queries
alone, against any acceptor of the language. Words are `sosl.sos` words
(letter-mask tuples) over the invariant's alphabet.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

from sosl.sos import Lasso, Word


@dataclass(frozen=True)
class Family:
    """One counting family; exactly one of the two tail shapes is filled:
    linear (`x_prefix`/`x_loop`) or ω-power (`y`)."""

    period: int
    pattern: Tuple[bool, ...]
    u: Word
    v: Word
    x_prefix: Optional[Word] = None
    x_loop: Optional[Word] = None
    y: Optional[Word] = None

    @property
    def omega_power(self) -> bool:
        """True for the ω-power shape (the period rides inside the loop)."""
        return self.y is not None

    def sample(self, n: int) -> Lasso:
        """The `n`-th sample lasso of the family."""
        if self.y is not None:
            return Lasso(self.u, self.v * n + self.y)
        assert self.x_prefix is not None and self.x_loop is not None
        return Lasso(self.u + self.v * n + self.x_prefix, self.x_loop)

    def expected(self, n: int) -> bool:
        """The declared membership of the `n`-th sample."""
        return self.pattern[n % self.period]
