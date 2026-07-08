"""sos2ltl_dg recipe — the E4(b) DG baseline, raw (no simplifier).

The naive dg local-divisor transcription of `aut2ltl/sos2ltl/`, without the
walk+window engine and without a final simplifier: its flat form is the
paper's §3 size explosion, kept unsimplified so a size ledger sees the raw
DAG and flat-tree counts against the sos2ltl engine. Aperiodic-only — a
group-bearing input declines (the certificate side is not this baseline).
"""
from __future__ import annotations

from typing import Optional

from aut2ltl.options import Options
from aut2ltl.translator import Translator


def sos2ltl_dg_recipe(options: Optional[Options] = None) -> Translator:
    """The raw dg baseline translator (no `hi`; options unused)."""
    from aut2ltl.sos2ltl.translator import sos2ltl_dg
    return sos2ltl_dg


__all__ = ["sos2ltl_dg_recipe"]
