"""Residual SCC descriptors and witnessed loss of canonical cyclic distinctions."""
from __future__ import annotations

from typing import Any, TYPE_CHECKING

from sosl.sos.calculus import align
from sosl.teacher.exact_ref import HypothesisLanguage
from synomega.block import BlockLevel, strong_components
from synomega.calculus import residuals
from synomega.sos import SymbolAlphabet
from synomega.sos2block import to_block

if TYPE_CHECKING:
    from sosl.sos.hypothesis import Hypothesis
    from synomega.sos import OStamp
    from .adapter import StampTeacher


def graph_structure(obj: OStamp) -> dict[str, Any]:
    """Describe the actual residual graph through its public finite services."""
    graph = residuals(obj)
    components = strong_components(graph.delta)
    return dict(residual_states=graph.n, residual_sccs=components,
                strongly_connected=len(components) == 1)


def cyclic_distinction(obj: OStamp, hypothesis: Hypothesis,
                       teacher: StampTeacher) -> dict[str, Any] | None:
    """Find two equal hypothesis folds separated by a canonical cyclic stamp.

    Alignment covers every concrete word's pair of folds, so its finite keys
    suffice even when the hypothesis fold splits some reference classes.
    """
    local = to_block(obj, BlockLevel.SCC)
    aligned = align(HypothesisLanguage(hypothesis, teacher.member),
                    teacher.ref_table.language(teacher.ref_pairs))
    alphabet = obj.stamp.alphabet
    if not isinstance(alphabet, SymbolAlphabet):
        raise ValueError("Cyclic audit requires the effective symbolic input")
    source_names = alphabet.symbols
    indices = tuple(source_names.index(name) for name in teacher.alphabet.aps)
    for block in local.blocks:
        if block.stamp is None:
            continue
        seen: dict[int, tuple[int, tuple[int, ...], int]] = {}
        for (fold, ref_class), word in zip(aligned.nodes, aligned.keys):
            current_word = tuple(indices[a] for a in word)
            value = block.stamp.fold(current_word)
            previous = seen.get(fold)
            if previous is not None and previous[0] != value:
                return dict(block_vertices=block.vertices,
                    block_classes=block.stamp.class_count,
                    hypothesis_class=fold,
                    words=[previous[1], word],
                    reference_classes=[previous[2], ref_class],
                    local_classes=[previous[0], value],
                    local_keys=[block.stamp.representatives[previous[0]],
                                block.stamp.representatives[value]])
            seen.setdefault(fold, (value, word, ref_class))
    return None
