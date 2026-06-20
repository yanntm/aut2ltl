"""survey.discovery — find the examples survey can run under given paths.

Re-export only; the logic lives in the small concern modules (walk / detect /
read) composed by scan.discover.
"""
from survey.discovery.scan import discover
from survey.example import Example

__all__ = ["discover", "Example"]
