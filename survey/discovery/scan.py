"""survey.discovery.scan — compose walk + detect + read into discover().

The package's public entry: walk the PATHs into candidate files, classify each,
and read it into Example(s). Unreadable / unrecognized files are silently
skipped. An optional `keep` restricts the yielded kinds — a client that runs one
format only (e.g. an sos-only tool) passes `keep={"sos"}` and never sees the
rest.
"""
from __future__ import annotations

from pathlib import Path
from typing import AbstractSet, Iterable, Iterator, Optional

from survey.discovery.detect import detect
from survey.discovery.read import read
from survey.example import Example
from survey.discovery.walk import walk


def discover(paths: Iterable[Path],
             keep: Optional[AbstractSet[str]] = None) -> Iterator[Example]:
    for f in walk(paths):
        kind = detect(f)
        if kind is not None and (keep is None or kind in keep):
            yield from read(f, kind)
