"""survey.discovery.read — turn a classified file into runnable Example(s).

An HOA or sos file yields one Example (the file is the input); an LTL list yields
one Example per non-blank, non-comment line. Each carries provenance.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterator

from survey.example import Example


def read(path: Path, kind: str) -> Iterator[Example]:
    if kind in ("hoa", "sos"):
        yield Example(kind, str(path), path.name, source=str(path))
        return
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        formula = line.split("#", 1)[0].strip()
        if formula:
            yield Example("ltl", formula, formula, source=f"{path}:{i}")
