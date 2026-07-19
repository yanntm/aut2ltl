"""io — (de)serialization of sos data structures in the .sos text format."""
from .serialize import (
    dump_invariant,
    load_invariant,
)

__all__ = ["dump_invariant", "load_invariant"]
