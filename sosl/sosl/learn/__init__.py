"""sosl.learn — the pure query learner. Re-exports; see README.md / algorithm.md.

Depends on sosl.contract + sosl.sos only (no spot, no reference, no aut2ltl):
its sole knowledge of L is the teacher interface.
"""
from sosl.learn.learner import learn

__all__ = ["learn"]
