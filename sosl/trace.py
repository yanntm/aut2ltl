"""Env-gated tracing that stays in shipped code at zero cost when off.

Guard every call site with the module constant `TRACE_ON`, so when tracing is
disabled nothing is evaluated — no message string is built, no call is made,
CPython simply skips the branch:

    from sosl.trace import TRACE_ON, trace
    if TRACE_ON:
        trace("learn", f"round {r}: classes={p.n} cols={len(table.columns)}")

`TRACE_ON` is set once from the environment at import:

    TRACE_ON=1            enable every tag
    TRACE_ON=learn,chain  enable only these tags

When ``TRACE_ON`` is unset the constant is ``False`` and the guarded block is
dead. When it is set, `trace` additionally filters by tag, so with several tags
enabled only the requested ones print (to stderr). The call-site guard is what
makes leaving these calls in permanently free; the tag filter is a convenience
for when tracing is already on.
"""
from __future__ import annotations

import os
import sys

_spec = os.environ.get("TRACE_ON", "").strip()

# The call-site guard: True iff any tracing was requested. Keep every trace()
# behind `if TRACE_ON:` so nothing is built when off.
TRACE_ON = bool(_spec)

_ALL = _spec in ("1", "all", "*")
_TAGS = frozenset() if (not _spec or _ALL) else frozenset(
    t.strip() for t in _spec.split(",") if t.strip()
)


def trace(tag: str, msg: str) -> None:
    """Print ``msg`` on stderr under ``tag`` if that tag is enabled. Only call
    inside an ``if TRACE_ON:`` guard — that guard, not this test, is what keeps
    the message string from being built when tracing is off."""
    if _ALL or tag in _TAGS:
        sys.stderr.write(f"[{tag}] {msg}\n")
