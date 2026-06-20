"""survey.techniques — resolve the requested --use set.

survey is agnostic to technique VALUES: requested names are passed through to
the front end opaquely (never enumerated or validated here). The sole token this
module interprets is "all", which must expand — via runtime discovery from the
portfolio registry — to every available technique. No technique name is ever
hardcoded in this package.
"""
from __future__ import annotations

from typing import List, Optional, Sequence


def resolve(uses: Sequence[str]) -> List[Optional[str]]:
    """Map the requested --use values to the list of runs:

        []        -> [None]    (the default technique only)
        [a, b]    -> [a, b]    (pass-through, one run each)
        [..."all"] -> NotImplementedError (needs runtime technique discovery)
    """
    if not uses:
        return [None]
    if "all" in uses:
        raise NotImplementedError(
            "--use all needs runtime technique discovery (see survey/README.md TODO)")
    return list(uses)
