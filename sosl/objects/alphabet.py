"""Letters over a set of atomic propositions, and the alphabet Sigma = 2^AP.

A letter is a valuation of AP: which propositions hold. It is encoded as a
bitmask over the alphabet's canonical proposition order, with the **first**
proposition on the **most significant** bit: ``aps[i]`` occupies bit
``k-1-i`` (``k = |AP|``). This makes the integer value of a mask equal to the
canonical letter *rank* — letters ordered by their characteristic tuple
``(chi(a_1), ..., chi(a_k))`` lexicographically with absent (0) < present (1),
``a_1`` most significant (for a single ``a``: ``!a`` < ``a``). Integer order on
masks is therefore the canonical letter order used for shortlex, matching the
serialization format in research_notes/sos_format.md.

A word is a tuple of letters; the empty word is the empty tuple. Word
concatenation and repetition are ordinary tuple ``+`` and ``*``.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, NewType, Tuple

# A letter is a bitmask over an Alphabet's aps; distinct type, zero runtime cost.
Letter = NewType("Letter", int)
Word = Tuple[Letter, ...]

# The empty word (the identity; the class of the adjoined monoid unit).
EMPTY: Word = ()


def shortlex_key(word: Word) -> Tuple[int, Word]:
    """Sort key realizing shortlex order: length first, then letterwise by rank
    (a letter's rank is its mask value). Least word of a set is
    ``min(words, key=shortlex_key)``."""
    return (len(word), word)


@dataclass(frozen=True)
class Alphabet:
    """The alphabet Sigma = 2^AP for a fixed, canonically ordered ``aps``.

    Holds the proposition names in canonical (sorted, de-duplicated) order and
    converts between the three letter views: the bitmask (`Letter`), the set of
    true propositions (a name list), and enumeration of all 2^|AP| letters.
    """

    aps: Tuple[str, ...]

    @classmethod
    def of(cls, names: Iterable[str]) -> "Alphabet":
        """Build from arbitrary proposition names, imposing the canonical order
        (sorted, duplicates removed)."""
        return cls(tuple(sorted(set(names))))

    @property
    def size(self) -> int:
        """The number of letters, 2^|AP|."""
        return 1 << len(self.aps)

    def letters(self) -> List[Letter]:
        """All letters in canonical (mask/rank) order."""
        return [Letter(m) for m in range(self.size)]

    def true_aps(self, a: Letter) -> List[str]:
        """The propositions true in letter ``a``, in canonical order (``aps[i]``
        sits on bit ``k-1-i``)."""
        k = len(self.aps)
        return [name for i, name in enumerate(self.aps) if (a >> (k - 1 - i)) & 1]

    def letter_of(self, trues: Iterable[str]) -> Letter:
        """The letter whose true propositions are exactly ``trues`` (which must
        all be alphabet propositions)."""
        k = len(self.aps)
        index = {name: i for i, name in enumerate(self.aps)}
        mask = 0
        for name in trues:
            mask |= 1 << (k - 1 - index[name])
        return Letter(mask)
