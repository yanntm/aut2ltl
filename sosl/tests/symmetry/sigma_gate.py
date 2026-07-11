"""SY1 acceptance gates (spec §3.5): the action laws, the direction pin, the
kernel law, the metamorphic check, anti/complement commutation, the product
cross-oracle — then the corpus campaign.

    python3 -m tests.symmetry.sigma_gate                # gates 1–6, fixtures + samples
    python3 -m tests.symmetry.sigma_gate --one CASE     # one campaign case, verbose
    python3 -m tests.symmetry.sigma_gate --campaign     # full census -> logs/sy1_generators.csv

The campaign writes one CSV row per corpus case (checkpointed, restartable;
per-case budget 15 s, a blown budget is recorded and skipped, never waited
on). Gate failures raise immediately — a kernel-law or class-count violation
convicts upstream code, not the theory (spec §8 K1/K2).
"""
from __future__ import annotations

import glob
import os
import random
import subprocess
import sys
import time
from typing import Dict, FrozenSet, Iterator, List, Optional, Sequence, Tuple

from sosl.sos import Alphabet, Invariant, Lasso, Letter, Word, dump_invariant, load_invariant
from sosl.sos.calculus import Table, align, equivalent
from sosl.sos.symmetry import (
    SignedPerm,
    all_b_ap,
    anti_possible,
    apply_perm,
    generators_b_ap,
    in_kernel,
    inert_aps,
    is_antisymmetry,
    is_symmetry,
)

from . import fixtures

_HERE = os.path.dirname(os.path.abspath(__file__))
_LOGS = os.path.join(_HERE, "logs")
_CORPUS = os.path.abspath(
    os.path.join(_HERE, "..", "..", "..", "genaut", "corpus", "flat_canon", "sos")
)
SEED = 20260711
CASE_BUDGET_S = 15.0
MAX_LASSO_LEN = 3


def _gen_name(g: SignedPerm) -> str:
    """`t<i><j>` for a transposition, `f<i>` for a flip (generator naming of
    the campaign CSV)."""
    moved = [i for i in range(g.n) if g.perm[i] != i]
    if moved:
        return f"t{moved[0]}{moved[1]}"
    return f"f{g.flip.index(True)}"


def _lassos(alphabet: Alphabet) -> Iterator[Tuple[Word, Word]]:
    """Every (stem, loop) with lengths ≤ MAX_LASSO_LEN (loop non-empty)."""
    letters = alphabet.letters()
    words: List[List[Word]] = [[()]]
    for k in range(MAX_LASSO_LEN):
        words.append([w + (a,) for w in words[k] for a in letters])
    stems = [w for tier in words for w in tier]
    loops = [w for tier in words[1:] for w in tier]
    for u in stems:
        for v in loops:
            yield u, v


# --- the fixture truth tables (paper §9 P1–P3, spec §3.4) -------------------

def _b2(perm: Tuple[int, int], fa: bool = False, fb: bool = False) -> SignedPerm:
    return SignedPerm(perm, (fa, fb))


_ID1 = SignedPerm.identity(1)
_FLIP_A1 = SignedPerm.polarity_flip(1, 0)
_ID2 = SignedPerm.identity(2)
_SWAP = SignedPerm.transposition(2, 0, 1)
_FLIP_A2 = SignedPerm.polarity_flip(2, 0)
_FLIP_B2 = SignedPerm.polarity_flip(2, 1)

# name -> (|C|, |P|, |linked|, symmetric set, anti set, inert AP set, anti_possible)
EXPECTED: Dict[str, Tuple[int, int, int, FrozenSet[SignedPerm], FrozenSet[SignedPerm], FrozenSet[int], bool]] = {
    "FIX_A": (3, 1, 3, frozenset({_ID2, _FLIP_B2}), frozenset(), frozenset({1}), False),
    "FIX_B": (5, 1, 9, frozenset({_ID2, _SWAP}), frozenset(), frozenset(), False),
    "FIX_C": (3, 2, 4, frozenset({_ID1}), frozenset({_FLIP_A1}), frozenset(), True),
}


def _check(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


# --- gate 1: group law + convention pin (§3.5.1) ----------------------------

def gate_group_law() -> None:
    rng = random.Random(SEED)
    for n in range(1, 6):
        for _ in range(100):
            def rand() -> SignedPerm:
                p = list(range(n))
                rng.shuffle(p)
                return SignedPerm(tuple(p), tuple(rng.random() < 0.5 for _ in range(n)))

            sigma, tau = rand(), rand()
            m = Letter(rng.randrange(1 << n))
            _check(sigma.compose(tau)(m) == sigma(tau(m)), f"compose law n={n}")
            _check(
                sigma.inverse().compose(sigma) == SignedPerm.identity(n),
                f"inverse law n={n}",
            )
        for i in range(n):
            f = SignedPerm.polarity_flip(n, i)
            _check(f.compose(f) == SignedPerm.identity(n), "flip involution")
            for j in range(i + 1, n):
                t = SignedPerm.transposition(n, i, j)
                _check(t.compose(t) == SignedPerm.identity(n), "transposition involution")
    # The pin at n = 2: swap_ab ∘ flip_a == flip_b ∘ swap_ab on all minterms.
    left, right = _SWAP.compose(_FLIP_A2), _FLIP_B2.compose(_SWAP)
    for m in range(4):
        _check(left(Letter(m)) == right(Letter(m)), "convention pin swap∘flip_a = flip_b∘swap")
    print("gate 1 (group law + pin): OK")


# --- gates 2–4 on the fixture triple (§3.5.2–4, truth tables §3.4) ----------

def gate_fixtures() -> None:
    for name, (nc, np_, nl, sym_exp, anti_exp, inert_exp, ap_exp) in EXPECTED.items():
        t0 = time.monotonic()
        inv = fixtures.load(name)
        n = len(inv.alphabet.aps)
        _check(inv.n == nc, f"{name}: |C| {inv.n} != {nc}")
        _check(len(inv.accept) == np_, f"{name}: |P| {len(inv.accept)} != {np_}")
        _check(len(inv.linked_pairs()) == nl, f"{name}: |linked| != {nl}")
        _check(anti_possible(inv) == ap_exp, f"{name}: anti_possible != {ap_exp}")
        _check(inert_aps(inv) == inert_exp, f"{name}: inert != {sorted(inert_exp)}")

        dump_l = dump_invariant(inv)
        dump_c = dump_invariant(inv.complement())
        lassos = list(_lassos(inv.alphabet))
        for sigma in all_b_ap(n):
            moved = apply_perm(inv, sigma)
            d = dump_invariant(moved)
            sym, anti = d == dump_l, d == dump_c
            # every truth-table cell (§9 P2)
            _check(sym == (sigma in sym_exp), f"{name}/{sigma}: symmetry {sym}")
            _check(anti == (sigma in anti_exp), f"{name}/{sigma}: anti {anti}")
            # kernel law (§3.5.3) and obstruction law (§3.5.5)
            _check(not in_kernel(inv, sigma) or sym, f"{name}/{sigma}: KERNEL LAW (K1)")
            _check(not anti or anti_possible(inv), f"{name}/{sigma}: obstruction law")
            # direction pin (§3.5.2): member crosses the rewire boundary
            for u, v in lassos:
                _check(
                    moved.member(Lasso(u, v))
                    == inv.member(Lasso(sigma.act_word(u), sigma.act_word(v))),
                    f"{name}/{sigma}: direction pin at {u}/{v}",
                )
            # metamorphic (§3.5.4)
            if sym:
                for u, v in lassos:
                    _check(
                        inv.member(Lasso(u, v))
                        == inv.member(Lasso(sigma.act_word(u), sigma.act_word(v))),
                        f"{name}/{sigma}: metamorphic at {u}/{v}",
                    )
            else:
                cex = next(
                    (
                        (u, v)
                        for u, v in lassos
                        if inv.member(Lasso(u, v))
                        != inv.member(Lasso(sigma.act_word(u), sigma.act_word(v)))
                    ),
                    None,
                )
                _check(cex is not None, f"{name}/{sigma}: no disagreeing lasso found")
                if sigma in generators_b_ap(n):
                    u, v = cex
                    print(
                        f"  {name}/{_gen_name(sigma)} not a symmetry; witness "
                        f"lasso stem={u} loop={v} (letters as {inv.alphabet.aps}-masks)"
                    )
        # the two-level separation (§3.4)
        if name == "FIX_A":
            _check(in_kernel(inv, _FLIP_B2), "FIX_A: flip_b not in kernel")
        if name == "FIX_B":
            _check(not in_kernel(inv, _SWAP), "FIX_B: swap unexpectedly in kernel")
            _check(is_symmetry(inv, _SWAP), "FIX_B: swap not a symmetry")
        print(f"gate 2–4 ({name}): OK ({time.monotonic() - t0:.1f}s)")


# --- gates 5–6: anti/complement commutation + product cross-oracle ----------

def _sample_corpus(count: int) -> List[str]:
    files = sorted(glob.glob(os.path.join(_CORPUS, "*.sos")))
    _check(bool(files), f"empty corpus at {_CORPUS}")
    return random.Random(SEED).sample(files, count)


def gate_laws_sampled() -> None:
    cases: List[Tuple[str, Invariant]] = [(n, fixtures.load(n)) for n in EXPECTED]
    for path in _sample_corpus(50):
        cases.append((os.path.basename(path), load_invariant(open(path).read())))
    for name, inv in cases:
        t0 = time.monotonic()
        n = len(inv.alphabet.aps)
        comp = inv.complement()
        for sigma in generators_b_ap(n):
            # commutation: complement-then-apply == apply-then-complement
            _check(
                dump_invariant(apply_perm(comp, sigma))
                == dump_invariant(apply_perm(inv, sigma).complement()),
                f"{name}/{_gen_name(sigma)}: anti/complement commutation",
            )
            # anti via both routes, plus the obstruction law
            r1 = is_antisymmetry(inv, sigma)
            r2 = dump_invariant(apply_perm(comp, sigma)) == dump_invariant(inv)
            _check(r1 == r2, f"{name}/{_gen_name(sigma)}: anti route disagreement")
            _check(not r1 or anti_possible(inv), f"{name}/{_gen_name(sigma)}: obstruction law")
            # cross-oracle (§3.5.6): keying route vs the aligned product route
            moved = apply_perm(inv, sigma)
            eq, _ = equivalent(
                align(
                    Table.of(inv).language(inv.accept),
                    Table.of(moved).language(moved.accept),
                )
            )
            _check(
                eq == is_symmetry(inv, sigma),
                f"{name}/{_gen_name(sigma)}: product oracle disagrees (STOP)",
            )
        if time.monotonic() - t0 > CASE_BUDGET_S:
            print(f"gate 5–6: {name} blew the budget — finding, reported")
    print(f"gate 5–6 (commutation + cross-oracle, {len(cases)} cases): OK")


# --- gate 7: the corpus campaign (§3.5.7) -----------------------------------

def _case_row(path: str) -> Tuple[str, str]:
    """One campaign case -> (case name, CSV row). Kernel/obstruction laws are
    asserted on every candidate; violations raise (K1)."""
    case = os.path.basename(path)[: -len(".sos")]
    t0 = time.monotonic()
    inv = load_invariant(open(path).read())
    n = len(inv.alphabet.aps)
    dump_l = dump_invariant(inv)
    dump_c = dump_invariant(inv.complement())
    inert = inert_aps(inv)
    ap_ok = anti_possible(inv)
    status = "ok"

    def verdicts(sigma: SignedPerm) -> Tuple[bool, bool]:
        d = dump_invariant(apply_perm(inv, sigma))
        sym, anti = d == dump_l, (d == dump_c if ap_ok else False)
        _check(not in_kernel(inv, sigma) or sym, f"{case}/{sigma}: KERNEL LAW (K1)")
        _check(not anti or ap_ok, f"{case}/{sigma}: obstruction law")
        return sym, anti

    sym_hits: List[str] = []
    anti_hits: List[str] = []
    for g in generators_b_ap(n):
        if time.monotonic() - t0 > CASE_BUDGET_S:
            status = "budget"
            break
        sym, anti = verdicts(g)
        if sym:
            sym_hits.append(_gen_name(g))
        if anti:
            anti_hits.append(_gen_name(g))

    sym_full = anti_full = -1
    if status == "ok" and n <= 3:
        sym_full = anti_full = 0
        for sigma in all_b_ap(n):
            if time.monotonic() - t0 > CASE_BUDGET_S:
                status = "budget"
                break
            sym, anti = verdicts(sigma)
            sym_full += sym
            anti_full += anti

    wall_ms = (time.monotonic() - t0) * 1000.0
    row = ",".join(
        [
            case,
            str(n),
            str(inv.n),
            ";".join(str(i) for i in sorted(inert)),
            ";".join(sym_hits),
            ";".join(anti_hits),
            "1" if ap_ok else "0",
            str(sym_full),
            str(anti_full),
            status,
            f"{wall_ms:.1f}",
        ]
    )
    return case, row


_COLUMNS = (
    "case,n_aps,n_classes,inert_set,sym_generator_hits,anti_generator_hits,"
    "anti_possible,sym_full_count,anti_full_count,status,wall_ms"
)


def _header(corpus: str) -> str:
    rev = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True
    ).stdout.strip()
    return (
        f"# date: {time.strftime('%Y-%m-%d')}\n"
        f"# git-rev: {rev}\n"
        f"# seed: {SEED}\n"
        f"# corpus: {os.path.relpath(corpus, os.path.join(_HERE, '..', '..', '..'))}\n"
    )


def campaign() -> None:
    os.makedirs(_LOGS, exist_ok=True)
    csv_path = os.path.join(_LOGS, "sy1_generators.csv")
    ckpt_path = os.path.join(_LOGS, "sy1_checkpoint.txt")
    done = set()
    if os.path.exists(ckpt_path):
        done = set(open(ckpt_path).read().split())
    fresh = not done
    files = sorted(glob.glob(os.path.join(_CORPUS, "*.sos")))
    print(f"campaign: {len(files)} cases, {len(done)} already done")
    with open(csv_path, "a") as csv, open(ckpt_path, "a") as ckpt:
        if fresh:
            csv.write(_header(_CORPUS))
            csv.write(_COLUMNS + "\n")
        for i, path in enumerate(files):
            case = os.path.basename(path)[: -len(".sos")]
            if case in done:
                continue
            _, row = _case_row(path)
            csv.write(row + "\n")
            ckpt.write(case + "\n")
            if i % 500 == 0:
                csv.flush()
                ckpt.flush()
                print(f"  ... {i}/{len(files)}")
    print(f"campaign: done -> {csv_path}")


def main(argv: Sequence[str]) -> int:
    if "--one" in list(argv):
        path = argv[list(argv).index("--one") + 1]
        if not os.path.exists(path):
            path = os.path.join(_CORPUS, path + ".sos")
        case, row = _case_row(path)
        print(_COLUMNS)
        print(row)
        return 0
    if "--campaign" in argv:
        campaign()
        return 0
    gate_group_law()
    gate_fixtures()
    gate_laws_sampled()
    print("SY1 gates 1–6: ALL OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
