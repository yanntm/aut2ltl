"""X0/X1 — classify a census of automata and record an enriched per-input ledger.

    python3 -m tests.sosl.classify_census <folder-or-file> [...] \
        [--limit N] [--budget SECONDS] [--logs DIR]

For every input — an `.hoa` presentation (`genaut/corpus/tgba/<tag>/` or the
canonical `genaut/corpus/det/<tag>/`, or a named triptych / stall / `Fork`
specimen) or an `.sos` file (`genaut/corpus/sos/<tag>/`, a canonical,
`𝓘`-deduplicated language consumed directly) — this builds the reference
invariant, classifies it (`sosl.sos.classify.classify`), and runs the gates. It
writes one JSON line per input carrying everything the profile aggregator
(`classify_profile`) needs: the language identity `ihash` (SHA-1 of the
canonical `𝓘` dump — [SωS26 Thm. 5.1] equality, the dedup key), the
`shape_family` (the enumeration tag), the `acceptance_family` read off the
*canonical* deterministic-complete presentation (not the tag), the algebra
sizes, the four chain/superchain integers, the Wagner degree `phi`, and the
build-vs-classify wall split.

Two gates run inline. The **duality gate** classifies the complement and asserts
the C section 7 swaps. The **spectrum cross-check** (C section 11, Prop. 11.1)
is a Spot-vs-algebra reconciliation: an HOA whose canonical presentation is
generalized-Büchi (or trivial `t`) — the DBA-realizable acceptance Spot's
determinization independently found — must classify with `m⁺ <= 0`. A
disagreement is a MISMATCH (spec harness 4.6 / exit 4): Spot's determinization
and the Carton–Perrin chain algebra, two independent engines, cannot both be
right. `.sos` inputs carry no presentation, so this gate is inapplicable.

Per-input budget (default 15s, the repo cap) via a real-time alarm: a build or
classification that overruns is a BUDGET verdict, not a failure — the ceiling is
the construction, not the classifier (spec X3/F3). Verdicts per input:
SOUND (classified, both gates hold), PARTIAL (gamma needs the derivative),
MISMATCH (duality, an internal law, or the spectrum law broke — a bug),
BUDGET (overran or the construction raised). Self-terminating; run large
buckets in the background, then aggregate with `classify_profile`.
"""
from __future__ import annotations

import hashlib
import json
import os
import signal
import sys
import time
from collections import Counter
from typing import Dict, List, Optional, Tuple

import spot

from sosl.sos import Invariant, dump_invariant, load_invariant
from sosl.sos.build import ReferenceError
from sosl.sos.build.importer import canonical
from sosl.sos.core.quotient import invariant_of
from sosl.sos.classify import classify, record_to_dict
from sosl.sos.classify.primitives import idempotents
from sosl.sos.classify.readoff import in_gen_buchi_spectrum

_LOGS = os.path.join(os.path.dirname(__file__), "logs", "classify_census")
_FLIP = {"sigma": "pi", "pi": "sigma", "delta": "delta", "PARTIAL": "PARTIAL"}


def _acc_family(acc: "spot.acc_cond") -> str:
    """The acceptance family of a *canonical* (deterministic complete generic)
    automaton, read off its acceptance condition — not the corpus tag. This is
    the language's minimal deterministic acceptance: `t` (universal), `gen-buchi`
    (`⋀ Inf`, the DBA-realizable languages), `co-buchi`, `parity`, or a residual
    `generic` label."""
    if acc.is_t():
        return "t"
    if acc.is_f():
        return "f"
    if acc.is_generalized_buchi():          # includes plain Büchi (one Inf set)
        return "gen-buchi"
    if acc.is_co_buchi():
        return "co-buchi"
    if acc.is_parity():
        return "parity"
    return acc.name() or "generic"


class _Budget(Exception):
    pass


def _ihash(inv: Invariant) -> str:
    """The language identity: SHA-1 of the canonical `𝓘` serialization. Equal
    iff the languages are equal ([SωS26 Thm. 5.1]); the profile's dedup key."""
    return hashlib.sha1(dump_invariant(inv).encode()).hexdigest()[:16]


def _complement(inv: Invariant) -> Invariant:
    linked = inv.linked_pairs()
    return Invariant(inv.alphabet, inv.keys, inv.letter_class, inv.mult,
                     accept=frozenset(linked - inv.accept), identity=inv.identity)


def _duality_ok(inv: Invariant, a) -> bool:
    b = classify(_complement(inv))
    return (
        (a.m_plus, a.m_minus) == (b.m_minus, b.m_plus)
        and (a.n_plus, a.n_minus) == (b.n_minus, b.n_plus)
        and b.sign == _FLIP[a.sign]
        and (a.rungs.open, a.rungs.dba) == (b.rungs.closed, b.rungs.dca)
        and (a.rungs.closed, a.rungs.dca) == (b.rungs.open, b.rungs.dba)
        and a.rungs.weak == b.rungs.weak
        and str(a.gamma) == str(b.gamma)
    )


def _reference(path: str) -> Tuple[Invariant, Optional["spot.acc_cond"], Dict]:
    """Build the reference `Invariant` of one input and, when it is an HOA
    presentation, its canonical acceptance and raw structural flags.

    An `.sos` input is loaded directly — it *is* `𝓘(L)`, with no presentation,
    so no Spot cross-check is possible (`acc=None`). An `.hoa` input is brought
    to the canonical deterministic-complete-generic form D (`importer.canonical`)
    and the invariant is built from D; its acceptance condition is the language's
    minimal deterministic acceptance and the flags describe the *raw* stored
    automaton (how far Spot's census reduction left it from canonical)."""
    if path.endswith(".sos"):
        with open(path) as fh:
            inv = load_invariant(fh.read())
        inv.validate()
        return inv, None, {"presentation": "sos"}
    raw = spot.automaton(path)
    D = canonical(raw)
    inv = invariant_of(D)
    if inv is None:
        raise ReferenceError(f"algebra closure exceeded cap for {path}")
    flags = {"presentation": "hoa",
             "raw_deterministic": spot.is_deterministic(raw),
             "raw_complete": spot.is_complete(raw)}
    return inv, D.acc(), flags


def _one(tag: str, path: str, budget: int) -> Dict:
    """Classify one input (`.hoa` or `.sos`) under the alarm budget; return its
    enriched JSON record (see the module docstring for the fields)."""
    rec: Dict = {"case": os.path.basename(path), "shape_family": tag}
    t0 = time.time()
    signal.setitimer(signal.ITIMER_REAL, budget)
    try:
        inv, acc, flags = _reference(path)
        t_built = time.time()
        r = classify(inv)
        t_classified = time.time()
        doc = record_to_dict(r)
        dual = _duality_ok(inv, r)
        # Spot-vs-algebra cross-check (C§11): a canonical generalized-Büchi (or
        # trivial `t`) presentation forces the language into the gen-Büchi degree
        # spectrum (m⁺ <= 0). Only an HOA presentation carries this gate.
        acc_family = _acc_family(acc) if acc is not None else "sos"
        gate_gba = acc is not None and (acc.is_generalized_buchi() or acc.is_t())
        spectrum = (not gate_gba or
                    in_gen_buchi_spectrum(r.m_plus, r.m_minus, r.n_plus, r.n_minus))
        signal.setitimer(signal.ITIMER_REAL, 0)
        if not dual:
            verdict, err = "MISMATCH", "duality"
        elif not spectrum:
            verdict, err = "MISMATCH", "spectrum law"
        elif r.gamma_partial:
            verdict, err = "PARTIAL", None
        else:
            verdict, err = "SOUND", None
        rec.update(flags)
        rec.update(
            acceptance_family=acc_family, gate_gba=gate_gba,
            ihash=_ihash(inv), classes=inv.n,
            n_idempotents=len(idempotents(inv)),
            n_linked_pairs=len(inv.linked_pairs()),
            aperiodic=r.aperiodic,
            m_plus=r.m_plus, m_minus=r.m_minus,
            n_plus=r.n_plus, n_minus=r.n_minus,
            rungs=doc["rungs"], phi=doc["phi"], gamma_partial=r.gamma_partial,
            boolean_level=r.boolean_level,
            parity_length=r.parity_length, co_parity_length=r.co_parity_length,
            build_wall=round(t_built - t0, 4),
            classify_wall=round(t_classified - t_built, 4),
            verdict=verdict,
        )
        if err:
            rec["error"] = err
    except _Budget:
        rec.update(verdict="BUDGET", error="timeout")
    except (ReferenceError, MemoryError) as exc:
        rec.update(verdict="BUDGET", error=f"{type(exc).__name__}: {exc}")
    except AssertionError as exc:
        rec.update(verdict="MISMATCH", error=f"internal law: {exc}")
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
    rec["wall"] = round(time.time() - t0, 3)
    return rec


_EXTS = (".hoa", ".sos")


def _inputs(args: List[str]) -> List[Tuple[str, str]]:
    """`(tag, path)` pairs over `.hoa` and `.sos` inputs. A directory
    contributes its inputs under the directory's basename as tag (the shape /
    enumeration label); a bare file is tagged by its parent directory's
    basename. An `.sos` folder — the canonical, `𝓘`-deduplicated corpus — is
    consumed the same way, only far faster (no presentation to reduce)."""
    files: List[Tuple[str, str]] = []
    for a in args:
        if os.path.isdir(a):
            tag = os.path.basename(os.path.normpath(a))
            files += sorted((tag, os.path.join(a, f)) for f in os.listdir(a)
                            if f.endswith(_EXTS))
        elif a.endswith(_EXTS):
            tag = os.path.basename(os.path.dirname(os.path.abspath(a)))
            files.append((tag, a))
    return files


def run(argv: List[str]) -> int:
    args, limit, budget, logs = [], None, 15, _LOGS
    it = iter(argv)
    for a in it:
        if a == "--limit":
            limit = int(next(it))
        elif a == "--budget":
            budget = int(next(it))
        elif a == "--logs":
            logs = next(it)
        else:
            args.append(a)

    def _alarm(signum, frame):
        raise _Budget()
    signal.signal(signal.SIGALRM, _alarm)

    files = _inputs(args)
    if limit is not None:
        files = files[:limit]
    if not files:
        print("no HOA inputs found", file=sys.stderr)
        return 1

    os.makedirs(logs, exist_ok=True)
    out = os.path.join(logs, "records.jsonl")
    verdicts: Counter = Counter()
    languages: Dict[str, str] = {}
    phis: Counter = Counter()

    with open(out, "w") as fh:
        for tag, path in files:
            rec = _one(tag, path, budget)
            fh.write(json.dumps(rec) + "\n")
            verdicts[rec["verdict"]] += 1
            if rec["verdict"] in ("SOUND", "PARTIAL"):
                languages[rec["ihash"]] = rec["phi"] and tuple(rec["phi"])
                phis[tuple(rec["phi"])] += 1

    n = len(files)
    print(f"=== census: {n} inputs -> {out} ===")
    print("verdicts:", dict(verdicts))
    print("distinct languages (𝓘-hash):", len(languages))
    print("distinct phi:", len(phis), "  top:", phis.most_common(6))
    print("aggregate the full profile with:  python3 -m tests.sosl.classify_profile",
          out)
    return 0 if verdicts["MISMATCH"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(run(sys.argv[1:]))
