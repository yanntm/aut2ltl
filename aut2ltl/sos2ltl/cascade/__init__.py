"""The decomposition fallback — see README.md / algorithm.md in this folder."""
from .machine import ScopedAcceptor, SeamRecord, StemCascade, scoped_acceptor, stem_cascade
from .loop import LoopDecline, LoopEmission, loop_acceptance
from .stem import StemEmission, stem_label

__all__ = [
    "ScopedAcceptor", "SeamRecord", "StemCascade", "scoped_acceptor",
    "stem_cascade", "LoopDecline", "LoopEmission", "loop_acceptance",
    "StemEmission", "stem_label",
]
