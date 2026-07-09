"""Failure taxonomy of the engine: findings (budget exhaustion — data for
the experiment ledgers, meant to be caught) versus defects (invariant
violations — never caught-and-ledgered). The C++ core raises these through
the binding's exception translation; they are defined here so the
pure-Python layer stands without a built extension."""

from typing import List, Tuple

# One kept-layer row of the closure: (layer index, cardinality by model
# count, live diagram nodes).
LayerRow = Tuple[int, int, int]


class Finding(Exception):
    """A budget exhaustion: a datum, not an error. Carries the phase that
    was running and the layer profile accumulated before the budget fired,
    so a killed run still yields its measurement."""

    def __init__(self, phase: int, layer_profile: List[LayerRow], message: str = "") -> None:
        super().__init__(message or f"budget exhausted in phase {phase}")
        self.phase: int = phase
        self.layer_profile: List[LayerRow] = layer_profile


class DiagramBudget(Finding):
    """Live diagram nodes exceeded the configured node budget."""


class TimeBudget(Finding):
    """Wall time exceeded the configured time budget."""


class StopTheLine(Exception):
    """An internal invariant of the construction was violated: squaring vs
    general pairing disagree, a composition-shaped relation was applied
    where the rotation lemma forbids it, the closure ran on a membership
    query, or an orbit walk appeared in the profile/residual phases. By
    definition a defect in the engine — file it, never ledger it."""
