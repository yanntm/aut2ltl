"""survey.normalize.sos — the dedup key for a `.sos` syntactic-ω-semigroup dump.

A `.sos` file is the canonical serialization `𝓘(L)` of a regular ω-language: by
[SωS26, Thm. 5.1] two dumps are **byte-equal iff the languages are equal**, so the
dedup key of a `.sos` file is simply its (whitespace-stripped) content — no parse,
no oracle. This is the language identity *up to a fixed AP labeling*: `GF(a)` and
`GF(!a)` are two distinct keys here.

Folding relabel/polarity twins (`GF(a) ≡ GF(!a)`) is a **stronger** notion — the
AP-relabeling canonical form of the dump — and is deliberately NOT done here yet
(it needs the `2^k·k!` relabeling search over the invariant); this module is the
seam where that canonicalization will land. For the HOA/LTL AP-canonical key see
`survey.normalize.dedup.default_key`.
"""
from __future__ import annotations


def is_sos_text(text: str) -> bool:
    """Whether `text` is a `.sos` dump (its magic first line)."""
    return text.lstrip().startswith("SOS v")


def sos_key(text: str) -> str:
    """The language dedup key of a `.sos` dump: its canonical content, stripped of
    trailing whitespace. Byte-equal keys ⟺ equal languages ([SωS26, Thm. 5.1])."""
    return text.strip()
