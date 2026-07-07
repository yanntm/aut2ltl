"""sos2ltl — read an LTL formula off a canonical `.sos` invariant.

The bridge from the SoS learner's world to aut2ltl: every module here consumes
a `sosl.sos.Invariant`. `sosl` lives in a sibling subtree (`<repo>/sosl/`, the
learner's own project root, package one level down at `<repo>/sosl/sosl/`), not
on the default import path when working from the aut2ltl repo root. Rather than
require an editable install, this package puts that subtree on `sys.path` on
import — so `import sosl` resolves to the real package for any code reached
through `aut2ltl.sos2ltl`. Consumers outside this package (e.g. a test script)
must import `aut2ltl.sos2ltl` — or any submodule of it — before `sosl`.
"""
from __future__ import annotations

import os
import sys

# <repo>/sosl is the learner's project root; its `sosl/` package sits inside.
# Insert at the front so the real package wins over the same-named project dir
# that shadows it as a namespace package when the cwd is the repo root.
_SOSL_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "sosl"))
if _SOSL_ROOT not in sys.path:
    sys.path.insert(0, _SOSL_ROOT)
