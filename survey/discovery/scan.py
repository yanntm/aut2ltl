"""survey.discovery.scan — compose walk + detect + read into discover().

The package's public entry: walk the PATHs into candidate files, classify each,
and read it into Example(s). Unreadable / unrecognized files are silently
skipped.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, Iterator

from survey.discovery.detect import detect
from survey.discovery.read import read
from survey.discovery.walk import walk
from survey.example import Example


def discover(paths: Iterable[Path]) -> Iterator[Example]:
    for f in walk(paths):
        kind = detect(f)
        if kind is not None:
            yield from read(f, kind)
