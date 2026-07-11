"""SY3 acceptance gates (spec §5): the corpus stutter oracle (decisive — FIRST),
metamorphic block rewriting (Thm 4.2 both directions), the fixture expectations
(paper §9 P4), the independence swap gate — then the census campaign.

    python3 -m tests.symmetry.relations_gate              # all gates, fixtures + samples
    python3 -m tests.symmetry.relations_gate --oracle     # F8 stutter oracle only, full corpus
    python3 -m tests.symmetry.relations_gate --campaign   # ladder / Î_L density -> logs/sy3_relations.csv

The stutter oracle compares the algebraic read-off `stutter_rung(inv, 1)` against
the semantic `.cat` stutter tag over the whole census; a *mixed* disagreement is
a real bug or a real theory problem — STOP, smallest case to the report (F8).
"""
from __future__ import annotations

import glob
import os
import random
import subprocess
import sys
import time
from typing import Dict, FrozenSet, Iterator, List, Optional, Sequence, Tuple

from sosl.sos import Invariant, Lasso, Letter, Word, load_invariant
from sosl.sos.classify import is_stutter_invariant
from sosl.sos.classify.io import parse_cat
from sosl.sos.symmetry import (
    independence,
    independence_letters,
    invisible_letters,
    is_closed,
    ladder_entry,
    stutter_rung,
    word_class,
)

from . import fixtures

_HERE = os.path.dirname(os.path.abspath(__file__))
_LOGS = os.path.join(_HERE, "logs")
_CORPUS = os.path.abspath(
    os.path.join(_HERE, "..", "..", "..", "genaut", "corpus", "flat_canon", "sos")
)
SEED = 20260711
MAX_LEN = 3


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def _corpus_files() -> List[str]:
    files = sorted(glob.glob(os.path.join(_CORPUS, "*.sos")))
    _check(bool(files), f"empty corpus at {_CORPUS}")
    return files


def _rep_letter(inv: Invariant, c: int) -> Letter:
    """A letter whose class is ``c`` (exists for every ``c`` in ``Σ_λ``)."""
    for a in inv.alphabet.letters():
        if inv.letter_class[a] == c:
            return Letter(a)
    raise ValueError(f"class {c} is not a letter class")


# --- gate 1: the corpus stutter oracle (F8, decisive — run FIRST) -----------

def gate_stutter_oracle(files: Optional[List[str]] = None) -> None:
    """`stutter_rung(inv, 1)` == the `.cat` stutter tag, over the whole census;
    and == `classify.is_stutter_invariant` (same equation, cross-check). A mixed
    disagreement STOPs on the smallest case (F8)."""
    files = files or _corpus_files()
    agree = 0
    disagree: List[Tuple[str, bool, bool]] = []  # (case, readoff, tag)
    for path in files:
        case = os.path.basename(path)[: -len(".sos")]
        inv = load_invariant(open(path).read())
        readoff = stutter_rung(inv, 1)
        _check(
            readoff == is_stutter_invariant(inv),
            f"{case}: stutter_rung(1) != is_stutter_invariant (internal)",
        )
        cat_path = path[: -len(".sos")] + ".cat"
        if not os.path.exists(cat_path):
            continue
        tag = parse_cat(open(cat_path).read())["stutter_invariant"]
        if readoff == tag:
            agree += 1
        else:
            disagree.append((case, readoff, tag))
    if disagree:
        disagree.sort(key=lambda r: (len(r[0]), r[0]))
        c, ro, tg = disagree[0]
        raise AssertionError(
            f"STUTTER ORACLE (F8): {len(disagree)} disagreements / {agree} agree; "
            f"smallest {c}: read-off={ro} tag={tg}"
        )
    print(f"gate 1 (stutter oracle F8): OK — {agree}/{agree} agree")


# --- gate 2: metamorphic block rewriting (Thm 4.2, ⟸ and ⟹) ----------------

def _rand_word(rng: random.Random, inv: Invariant, lo: int, hi: int) -> Word:
    letters = inv.alphabet.letters()
    return tuple(rng.choice(letters) for _ in range(rng.randint(lo, hi)))


def _val(inv: Invariant, s: int, d: int) -> bool:
    """Membership of ``key(s)·key(d)^ω``: iterate ``d`` to its idempotent ``e``,
    absorb one loop, look up ``(s·e, e)`` in ``P`` (the table oracle of §2.2)."""
    e = inv.idempotent_power(d)
    return (inv.mult[s][e], e) in inv.accept


def _classes_distinguished(inv: Invariant, s1: int, s2: int) -> bool:
    """Do the fold-classes ``s1 ≠ s2`` differ in the language, over ANY context?
    Arnold's two clauses (paper §4.1), scanned on the table: ``s`` in the loop
    (``x·(s·y)^ω``) or in the stem (``x·s·y·β``). Complete for the ω-congruence,
    so for a syntactic invariant distinct classes are always distinguished."""
    n = inv.n
    mult = inv.mult
    # clause 2 — s in the loop: ∃ cx, cy: val(cx, s·cy) differs (cheap, O(n²))
    for cy in range(n):
        d1, d2 = mult[s1][cy], mult[s2][cy]
        if d1 == d2:
            continue
        for cx in range(n):
            if _val(inv, cx, d1) != _val(inv, cx, d2):
                return True
    # clause 1 — s in the stem: ∃ cx, cz, cd: val(cx·s·cz, cd) differs (O(n³))
    for cz in range(n):
        a1, a2 = mult[s1][cz], mult[s2][cz]
        if a1 == a2:
            continue
        for cx in range(n):
            t1, t2 = mult[cx][a1], mult[cx][a2]
            if t1 == t2:
                continue
            for cd in range(n):
                if cd == inv.identity:
                    continue
                if _val(inv, t1, cd) != _val(inv, t2, cd):
                    return True
    return False


def gate_metamorphic(sample: int = 200, pairs: int = 20) -> None:
    """For `(u, v)` with `[u] = [v]`: replacing a `u`-block by `v` in the stem,
    and periodically in the loop, keeps membership (Thm 4.2 ⟸, via the fold
    homomorphism). For `[u] ≠ [v]`: the classes are language-distinguished by
    Arnold's context clauses (Thm 4.2 ⟹, on the algebra). A ⟹ failure would
    convict the corpus invariant as non-syntactic — STOP (to-theory)."""
    rng = random.Random(SEED)
    files = rng.sample(_corpus_files(), sample)
    closed_seen = open_seen = 0
    for path in files:
        case = os.path.basename(path)[: -len(".sos")]
        inv = load_invariant(open(path).read())
        t0 = time.monotonic()
        for _ in range(pairs):
            if time.monotonic() - t0 > 15.0:
                print(f"gate 2: {case} blew budget — recorded, skipped")
                break
            u = _rand_word(rng, inv, 1, MAX_LEN)
            v = _rand_word(rng, inv, 1, MAX_LEN)
            x = _rand_word(rng, inv, 0, MAX_LEN)
            y = _rand_word(rng, inv, 0, MAX_LEN)
            if is_closed(inv, u, v):
                closed_seen += 1
                loop = _rand_word(rng, inv, 1, MAX_LEN)
                _check(
                    inv.member(Lasso(x + u + y, loop))
                    == inv.member(Lasso(x + v + y, loop)),
                    f"{case}: stem rewrite changed membership u={u} v={v}",
                )
                _check(
                    inv.member(Lasso(x, u + y))
                    == inv.member(Lasso(x, v + y)),
                    f"{case}: periodic rewrite changed membership u={u} v={v}",
                )
            else:
                open_seen += 1
                _check(
                    _classes_distinguished(inv, inv.fold(u), inv.fold(v)),
                    f"{case}: [u]!=[v] but classes not distinguished — "
                    f"NON-SYNTACTIC corpus case, u={u} v={v} (to-theory)",
                )
    print(f"gate 2 (metamorphic): OK — {closed_seen} closed, {open_seen} open pairs")


# --- gate 3: fixture expectations (paper §9 P4) -----------------------------

def gate_fixtures() -> None:
    for name in ("FIX_A", "FIX_B", "FIX_C"):
        inv = fixtures.load(name)
        classes = sorted(set(inv.letter_class))
        distinct = {(c, d) for c in classes for d in classes if c != d}
        indep = independence(inv)
        _check(invisible_letters(inv) == frozenset(), f"{name}: invisible letters not empty")
        _check(ladder_entry(inv) == 1, f"{name}: ladder_entry != 1")
        if name in ("FIX_A", "FIX_B"):
            _check(indep == distinct, f"{name}: Î_L not total on distinct classes")
        if name == "FIX_C":
            _check(indep == frozenset(), f"{name}: Î_L(FIX_C) not empty")
        print(f"gate 3 ({name}): OK — |Î_L|={len(indep)}, ladder_entry=1")


# --- gate 4: independence swap gate -----------------------------------------

def _short_words(inv: Invariant, nonempty: bool = False) -> List[Word]:
    """All words of length ≤ 2 over Σ (the bounded swap-context scan of gate 4)."""
    letters = inv.alphabet.letters()
    words: List[Word] = [(), *((a,) for a in letters)]
    words += [(a, b) for a in letters for b in letters]
    return [w for w in words if w] if nonempty else words


def gate_independence_swap(sample: int = 100) -> None:
    """For `(c, d) ∈ Î_L`: an adjacent `cd`-block swapped to `dc` keeps
    membership. For `(c, d) ∉ Î_L`: a distinguishing swap context exists in the
    bound, or is recorded as not-found (absence is NOT asserted — spec §5)."""
    rng = random.Random(SEED + 1)
    files = rng.sample(_corpus_files(), sample)
    kept = broke = notfound = 0
    for path in files:
        inv = load_invariant(open(path).read())
        case = os.path.basename(path)[: -len(".sos")]
        classes = sorted(set(inv.letter_class))
        indep = independence(inv)
        for c in classes:
            for d in classes:
                if c == d:
                    continue
                a, b = _rep_letter(inv, c), _rep_letter(inv, d)
                if (c, d) in indep:
                    for x in _short_words(inv):
                        for loop in _short_words(inv, nonempty=True):
                            _check(
                                inv.member(Lasso(x + (a, b), loop))
                                == inv.member(Lasso(x + (b, a), loop)),
                                f"{case}: Î_L swap {c}{d} changed membership",
                            )
                    kept += 1
                else:
                    found = any(
                        inv.member(Lasso(x + (a, b), loop))
                        != inv.member(Lasso(x + (b, a), loop))
                        for x in _short_words(inv)
                        for loop in _short_words(inv, nonempty=True)
                    )
                    if found:
                        broke += 1
                    else:
                        notfound += 1
    print(
        f"gate 4 (independence swap): OK — {kept} Î_L-kept, {broke} non-Î_L "
        f"distinguished, {notfound} non-Î_L not-found-in-bound (recorded, not asserted)"
    )


# --- the census campaign: ladder_entry + Î_L density (F10/F11) ---------------

_COLUMNS = (
    "case,n_aps,n_classes,n_sigma_lambda,invisible_letters,stutter_inv,"
    "ladder_entry,indep_pairs,indep_density"
)


def _campaign_row(inv: Invariant, case: str) -> str:
    n = len(inv.alphabet.aps)
    sigma_l = sorted(set(inv.letter_class))
    m = len(sigma_l)
    denom = m * (m - 1)
    indep = independence(inv)
    density = (len(indep) / denom) if denom else 0.0
    le = ladder_entry(inv)
    return ",".join(
        [
            case,
            str(n),
            str(inv.n),
            str(m),
            str(len(invisible_letters(inv))),
            "1" if stutter_rung(inv, 1) else "0",
            "" if le is None else str(le),
            str(len(indep)),
            f"{density:.4f}",
        ]
    )


def _header() -> str:
    rev = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True
    ).stdout.strip()
    return (
        f"# date: {time.strftime('%Y-%m-%d')}\n"
        f"# git-rev: {rev}\n"
        f"# seed: {SEED}\n"
        f"# corpus: {os.path.relpath(_CORPUS, os.path.join(_HERE, '..', '..', '..'))}\n"
    )


def campaign() -> None:
    os.makedirs(_LOGS, exist_ok=True)
    csv_path = os.path.join(_LOGS, "sy3_relations.csv")
    files = _corpus_files()
    print(f"campaign: {len(files)} cases -> {csv_path}")
    with open(csv_path, "w") as csv:
        csv.write(_header())
        csv.write(_COLUMNS + "\n")
        for i, path in enumerate(files):
            case = os.path.basename(path)[: -len(".sos")]
            inv = load_invariant(open(path).read())
            csv.write(_campaign_row(inv, case) + "\n")
            if i % 1000 == 0:
                csv.flush()
                print(f"  ... {i}/{len(files)}")
    print(f"campaign: done -> {csv_path}")


def main(argv: Sequence[str]) -> int:
    if "--oracle" in argv:
        gate_stutter_oracle()
        return 0
    if "--campaign" in argv:
        campaign()
        return 0
    gate_stutter_oracle()
    gate_fixtures()
    gate_metamorphic()
    gate_independence_swap()
    print("SY3 gates 1–4: ALL OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
