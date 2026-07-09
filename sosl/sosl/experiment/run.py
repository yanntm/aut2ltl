"""One instrumented learner run: drive the learner against a teacher under a
configuration and return the `RunStats`, the exported invariant, and the split
ledger.

This is the campaign's single source of per-run truth. It reuses the learner
procedures unchanged (`_stabilize` / `saturate` / `process_counterexample` /
`export`) behind a phase-tagged, counting `member` wrapper — the promotion of
the `m3_ledgers` counting loop and the `genaut_census` classification into one
package entry point. It never raises on a learner or teacher fault: a per-case
wall-clock budget turns a runaway into a `BUDGET` verdict, and any other
exception is captured into the record's `detail`, so one case can never kill a
campaign.
"""
from __future__ import annotations

import itertools
import signal
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from sosl.contract import Counterexample
from sosl.experiment.stats import RunStats
from sosl.learn.columns import Column, LinCol
from sosl.learn.export import export
from sosl.learn.learner import (
    _build_hypothesis,
    _stabilize,
    process_counterexample,
)
from sosl.learn.partition import Partition
from sosl.learn.saturate import saturate
from sosl.learn.table import Table
from sosl.sos import Lasso, dump_invariant, load_invariant
from sosl.sos.alphabet import Word, shortlex_key
from sosl.sos.build import ReferenceError, reference_of_hoa
from sosl.sos.hypothesis import Hypothesis, loop_reps
from sosl.sos.invariant import Invariant
from sosl.sos.io.serialize import render_word
from sosl.teacher import HoaTeacher
from sosl.teacher.equiv import resolve_prediction
from sosl.teacher.exact import ExactTooLarge


@dataclass
class Config:
    """One learner configuration: the axes the campaign sweeps.

    ``config_id`` names the row in the CSV; ``saturation`` toggles the two-sided
    sweep (off = the M2 / E2 ablation); ``eq_mode`` selects the teacher's
    equivalence oracle (``bounded`` / ``exact``); ``cex_policy`` is recorded
    verbatim (only ``minimal`` is wired before E5). Budgets are per case.
    """

    config_id: str
    saturation: bool = True
    eq_mode: str = "bounded"        # bounded | exact
    eq_bound: int = 8
    cex_policy: str = "minimal"     # minimal | first | padded:<k>
    seed: int = 0
    budget_seconds: int = 60
    acceptor_bound: int = 3


@dataclass
class LedgerRow:
    """One top-level split: its trigger (counterexample / saturation), the chain
    that minted the column, the minted column rendered as a context, the class
    count before/after, and which class(es) tore apart."""

    trigger: str
    chain: str
    column: str
    before_n: int
    after_n: int
    split: str


@dataclass
class Signature:
    """The final signature matrix (E4, companion to the paper's Tables 6/8):
    column contexts as ``header``, and one ``(class key, bit row)`` per class in
    shortlex-key order — the class keys against the discovered columns."""

    header: List[str]
    rows: List[Tuple[str, Tuple[bool, ...]]]


@dataclass
class RunResult:
    """The whole outcome of a run: metrics, the exported invariant (``None`` on a
    budget/error run), the split ledger, and the final signature matrix."""

    stats: RunStats
    invariant: Optional[Invariant] = None
    ledger: List[LedgerRow] = field(default_factory=list)
    signature: Optional[Signature] = None


class _Budget(Exception):
    """Raised by the wall-clock alarm to abort a runaway run."""


def _norm(sos_text: str) -> str:
    """Normalize a `.sos` dump for byte-comparison: drop trailing blank lines and
    trailing whitespace per line (a stored file may carry a final newline the
    in-memory dump does not)."""
    return "\n".join(line.rstrip() for line in sos_text.rstrip().splitlines())


def _reference(hoa_path: str, reference_sos: Optional[str]) -> Tuple[str, Invariant]:
    """The reference ``(sos_dump, invariant)`` — read from a precomputed `.sos`
    file when given, else built from the HOA. Raises `ReferenceError` if the HOA
    has no SoS reference.

    The invariant is both the byte-equality yardstick and the decision structure
    the teacher's exact oracle runs against, so a run that has a `.sos` never
    rebuilds the algebra from the automaton."""
    if reference_sos is not None:
        with open(reference_sos, encoding="utf-8") as fh:
            text = fh.read()
        return text, load_invariant(text)
    ref = reference_of_hoa(hoa_path)
    return dump_invariant(ref), ref


def _alarm(_sig: int, _frame: object) -> None:
    raise _Budget()


# -- ledger rendering (shared with the E4 report renderer) -------------------


def _render_col(ab: object, col: Column) -> str:
    """A minted column as the context it drops a candidate ``[]`` into."""
    def w(word: Word) -> str:
        return render_word(ab, word)
    if isinstance(col, LinCol):
        return f"{w(col.x)}·[]·{w(col.y)} , ({w(col.t)})^ω"
    return f"{w(col.x)}·([]·{w(col.y)})^ω"


def _describe_split(ab: object, before: Partition, after: Partition) -> str:
    """Each class of ``before`` that ``after`` tore apart, as ``src -> a, b`` in
    shortlex reps (``;``-joined; one mint can split several classes), or
    ``(no split)`` if the class count did not grow."""
    parts: List[str] = []
    for c in range(before.n):
        words = before.members[c]
        buckets: Dict[int, List[Word]] = {}
        for wd in words:
            ac = after.class_of.get(wd)
            if ac is not None:
                buckets.setdefault(ac, []).append(wd)
        if len(buckets) > 1:
            src = min(words, key=shortlex_key)
            pieces = sorted((min(ws, key=shortlex_key) for ws in buckets.values()),
                            key=shortlex_key)
            parts.append(f"{render_word(ab, src)} -> "
                         + ", ".join(render_word(ab, p) for p in pieces))
    return " ; ".join(parts) if parts else "(no split)"


# -- acceptor checks (spec §3.3 / §9 P1, F2) ---------------------------------


def _lassos_upto(ab: object, stem_max: int, loop_max: int):
    """Every lasso with ``|stem| <= stem_max`` and ``1 <= |loop| <= loop_max``."""
    letters = ab.letters()
    for slen in range(stem_max + 1):
        for stem in itertools.product(letters, repeat=slen):
            for llen in range(1, loop_max + 1):
                for loop in itertools.product(letters, repeat=llen):
                    yield Lasso(tuple(stem), tuple(loop))


def hyp_acceptor_ok(teacher: HoaTeacher, hyp: Hypothesis, bound: int = 3) -> bool:
    """Spec §9 P1: the Cayley hypothesis' own predictions agree with the teacher
    over all lassos up to ``bound``. MUST hold at any fixpoint."""
    loops = loop_reps(hyp)
    for la in _lassos_upto(teacher.alphabet, bound, bound):
        if resolve_prediction(teacher.member, hyp, la, loops) != teacher.member(la):
            return False
    return True


def inv_acceptor_ok(inv: Invariant, teacher: HoaTeacher, bound: int = 3) -> bool:
    """Spec §9 F2: the exported invariant's read-off agrees with the teacher over
    all lassos up to ``bound`` (may legitimately fail on a non-saturated run)."""
    for la in _lassos_upto(teacher.alphabet, bound, bound):
        if inv.member(la) != teacher.member(la):
            return False
    return True


# -- the instrumented run ----------------------------------------------------


def run_case(case_id: str, hoa_path: str, config: Config,
             reference_sos: Optional[str] = None) -> RunResult:
    """Learn ``hoa_path`` under ``config`` and return the full `RunResult`.

    The reference (for the class count and byte-equality) is a precomputed `.sos`
    file when ``reference_sos`` is given — the census fast path, avoiding a
    per-case reference rebuild — otherwise it is built from ``hoa_path``. Then it
    drives the learner under a wall-clock budget and classifies the verdict from
    byte-equality, the two acceptor checks, and the certifying strategy.
    """
    stats = RunStats(case_id=case_id, config_id=config.config_id, seed=config.seed,
                     cex_policy=config.cex_policy)
    start = time.perf_counter()
    signal.signal(signal.SIGALRM, _alarm)
    signal.alarm(config.budget_seconds)
    try:
        try:
            ref_dump, ref_inv = _reference(hoa_path, reference_sos)
        except ReferenceError as exc:
            stats.verdict = "MISMATCH"
            stats.detail = f"NONDEF: {exc}"
            return RunResult(stats)
        teacher = HoaTeacher.of_hoa(hoa_path, eq_mode=config.eq_mode,
                                    reference=ref_inv)
        teacher.eq_bound = config.eq_bound
        teacher.cex_policy = config.cex_policy
        stats.ap_count = len(teacher.alphabet.aps)
        stats.ref_classes = ref_inv.n

        result = _drive(teacher, config, stats)
        table, p, inv, ledger, eq_cert = result

        stats.learned_classes = inv.n
        stats.eq_certification = eq_cert
        n_lin = sum(isinstance(c, LinCol) for c in table.columns)
        stats.n_columns_lin = n_lin
        stats.n_columns_om = len(table.columns) - n_lin
        stats.n_splits = inv.n - stats.n_classes_initial

        byte_equal = _norm(ref_dump) == _norm(dump_invariant(inv))
        p1_ok = hyp_acceptor_ok(teacher, _build_hypothesis(table, p),
                                config.acceptor_bound)
        stats.stall_class = _classify_stall(stats, byte_equal, config.saturation)
        stats.verdict, stats.detail = _classify_verdict(
            byte_equal, p1_ok, config, stats)
        return RunResult(stats, inv, ledger, _signature(table, p))
    except _Budget:
        stats.verdict = "BUDGET"
        return RunResult(stats)
    except ExactTooLarge as exc:
        # The exact oracle could not build its closure — a capability limit, not
        # a soundness failure (the learner never produced a wrong byte here).
        stats.verdict = "OVERSIZE"
        stats.detail = f"OVERSIZE:{exc}"
        return RunResult(stats)
    except Exception as exc:  # noqa: BLE001 -- a run records its own fault, never aborts
        stats.verdict = "MISMATCH"
        stats.detail = f"ERROR:{type(exc).__name__}: {exc}"
        return RunResult(stats)
    finally:
        signal.alarm(0)
        stats.wall_seconds = time.perf_counter() - start


def _drive(teacher: HoaTeacher, config: Config, stats: RunStats):
    """The instrumented main loop; fills ``stats`` counters in place and returns
    ``(table, partition, invariant, ledger, eq_certification)``."""
    ab = teacher.alphabet
    counts: Dict[str, int] = defaultdict(int)
    phase = ["fill"]
    max_word = [0]

    def member(la: Lasso) -> bool:
        counts[phase[0]] += 1
        if len(la.stem) > max_word[0]:
            max_word[0] = len(la.stem)
        if len(la.loop) > max_word[0]:
            max_word[0] = len(la.loop)
        return teacher.member(la)

    table = Table(ab, member)
    ledger: List[LedgerRow] = []
    pending: Optional[tuple] = None       # (trigger, chain, column, before_partition)
    n_equiv = n_cex = n_sat = n_sat_checks = 0
    n_initial: Optional[int] = None
    max_cex_stem = max_cex_loop = 0
    eq_cert = ""

    while True:
        phase[0] = "fill"
        p = _stabilize(table)
        if n_initial is None:
            n_initial = p.n
        if pending is not None:
            trig, chain, col, before = pending
            ledger.append(LedgerRow(trig, chain, _render_col(ab, col),
                                    before.n, p.n, _describe_split(ab, before, p)))
            pending = None

        if config.saturation:
            phase[0] = "saturation"
            n_sat_checks += 1
            lbl = saturate(table, p)
            if lbl is not None:
                n_sat += 1
                pending = ("saturation", lbl, table.columns[-1], p)
                continue

        n_equiv += 1
        res = teacher.equiv(_build_hypothesis(table, p))
        if not isinstance(res, Counterexample):
            eq_cert = res.strategy
            break
        n_cex += 1
        max_cex_stem = max(max_cex_stem, len(res.lasso.stem))
        max_cex_loop = max(max_cex_loop, len(res.lasso.loop))
        phase[0] = "harvest"
        chain = process_counterexample(table, p, res.lasso)
        pending = ("cex " + _lasso_repr(ab, res.lasso), chain, table.columns[-1], p)

    phase[0] = "pcache"
    inv = export(p, member)

    stats.n_classes_initial = n_initial
    stats.n_member_fill = counts.get("fill", 0)
    stats.n_member_harvest = counts.get("harvest", 0)
    stats.n_member_saturation = counts.get("saturation", 0)
    stats.n_member_pcache = counts.get("pcache", 0)
    stats.n_member_total = sum(counts.values())
    stats.n_equiv = n_equiv
    stats.n_saturation_checks = n_sat_checks
    stats.n_saturation_escalations = n_sat
    stats.max_cex_stem = max_cex_stem
    stats.max_cex_loop = max_cex_loop
    stats.max_query_word_len = max_word[0]
    return table, p, inv, ledger, eq_cert


def _lasso_repr(ab: object, la: Lasso) -> str:
    return f"({render_word(ab, la.stem)}, {render_word(ab, la.loop)})"


def _signature(table: Table, p: Partition) -> Signature:
    """The final signature matrix: each class (shortlex-key order) against the
    discovered columns, read straight off the closed table's bit rows."""
    ab = table.alphabet
    header = [_render_col(ab, col) for col in table.columns]
    keys = sorted((p.rep[c] for c in range(p.n)), key=shortlex_key)
    rows = [(render_word(ab, key), table.bit_row(key)) for key in keys]
    return Signature(header, rows)


def _classify_stall(stats: RunStats, byte_equal: bool, saturation: bool) -> str:
    """Spec §7 / §9 P6 stall class — a **per-language** property read from the
    **no-saturation + exact** leg alone. A saturation-on run does not exhibit a
    stall, so it is ``n/a`` (never ``transient``/``permanent`` — that mislabel
    contradicts Proposition 4.4 when E2 aggregates). Under no saturation: a
    surviving (non-byte-equal) fixpoint is ``permanent`` (trustworthy only when
    ``eq_certification`` is exact); a byte-equal run is ``transient`` if a coarser
    fixpoint preceded the canonical one, else ``none``."""
    if saturation:
        return "n/a"
    if not byte_equal:
        return "permanent"
    if 0 <= stats.n_classes_initial < stats.learned_classes:
        return "transient"
    return "none"


def _classify_verdict(byte_equal: bool, p1_ok: bool, config: Config,
                      stats: RunStats):
    """The run verdict (spec §7): ``SOUND`` on byte-equality; ``ACCEPTOR_ONLY``
    for a non-saturated run whose Cayley hypothesis is still acceptance-correct;
    ``MISMATCH`` otherwise (a P1 failure, or a byte mismatch the config does not
    excuse). Returns ``(verdict, detail)``."""
    if byte_equal:
        return ("SOUND", "") if p1_ok else ("MISMATCH", "byte-equal but P1 red (bug)")
    if not p1_ok:
        return "MISMATCH", "P1 red: hypothesis predictions disagree with teacher"
    if not config.saturation:
        return "ACCEPTOR_ONLY", "non-saturated fixpoint: export byte-differs, hypothesis sound"
    return "MISMATCH", "byte-differs under saturation (expected byte-equal)"
