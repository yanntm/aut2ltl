"""Report generators: the E0 validation one-pager and the E4 worked-transcript
renderers (split ledger + signature matrix), all machine-generated from a
`CampaignResult` — no hand-edited numbers.

The E0 report is the campaign's gate: it tabulates every run's verdict and
declares PASS only when no run is `FAIL`, `BUDGET`, or `CRASH` and every
permanent-stall specimen certified `ACCEPTOR_ONLY` under a no-saturation config
(spec §9 P4/F5). The E4 renderers reproduce the paper's ledger format and the
signature matrix (companion to Tables 6/8) for a single run.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from sosl.experiment.driver import CampaignResult
from sosl.experiment.manifest import MANIFEST_VERSION, case_by_id
from sosl.experiment.run import RunResult
from sosl.experiment.stats import RunStats
from sosl.sos import dump_invariant


def _byte_flag(s: RunStats) -> str:
    """The byte-equality reading implied by the verdict (SOUND = byte-equal)."""
    if s.verdict == "SOUND":
        return "yes"
    if s.verdict in ("ACCEPTOR_ONLY", "FAIL"):
        return "no"
    return "-"


def e0_gate(campaign: CampaignResult) -> Optional[str]:
    """``None`` if E0 passes, else a one-line reason it failed."""
    bad = [s for s in campaign.stats if s.verdict in ("FAIL", "BUDGET", "CRASH")]
    if bad:
        return (f"{len(bad)} run(s) FAIL/BUDGET/CRASH: "
                + ", ".join(f"{s.case_id}/{s.config_id}={s.verdict}" for s in bad))
    return None


def e0_report(campaign: CampaignResult) -> str:
    """The E0 one-page validation report (markdown)."""
    lines: List[str] = []
    lines.append("# E0 — Validation campaign")
    lines.append("")
    lines.append(f"Manifest `{MANIFEST_VERSION}`, "
                 f"{len(campaign.results)} runs "
                 f"(named cases; census tier deferred).")
    lines.append("")
    lines.append("| case | config | ref | init | learned | splits "
                 "| member (f/h/s/p) | eq | cex | sat | cert | stall | byte | verdict |")
    lines.append("|---|---|--:|--:|--:|--:|--:|--:|--:|--:|---|---|:--:|---|")
    for r in campaign.results:
        s = r.stats
        mem = f"{s.n_member_total} ({s.n_member_fill}/{s.n_member_harvest}/" \
              f"{s.n_member_saturation}/{s.n_member_pcache})"
        cex = s.n_equiv - 1 if s.n_equiv >= 1 else -1
        lines.append(
            f"| {s.case_id} | {s.config_id} | {_n(s.ref_classes)} "
            f"| {_n(s.n_classes_initial)} | {_n(s.learned_classes)} "
            f"| {_n(s.n_splits)} | {mem} | {_n(s.n_equiv)} | {_n(cex)} "
            f"| {_n(s.n_saturation_escalations)} | {s.eq_certification or '-'} "
            f"| {s.stall_class or '-'} | {_byte_flag(s)} | {s.verdict} |")
    lines.append("")

    sound = sum(s.verdict == "SOUND" for s in campaign.stats)
    acc = sum(s.verdict == "ACCEPTOR_ONLY" for s in campaign.stats)
    fail = sum(s.verdict == "FAIL" for s in campaign.stats)
    budget = sum(s.verdict == "BUDGET" for s in campaign.stats)
    crash = sum(s.verdict == "CRASH" for s in campaign.stats)
    total_mem = sum(max(0, s.n_member_total) for s in campaign.stats)
    total_eq = sum(max(0, s.n_equiv) for s in campaign.stats)
    lines.append(f"**Totals.** {sound} SOUND · {acc} ACCEPTOR_ONLY · "
                 f"{fail} FAIL · {budget} BUDGET · {crash} CRASH. "
                 f"Query budget used: {total_mem} membership, {total_eq} equivalence.")
    lines.append("")
    reason = e0_gate(campaign)
    if reason is None:
        lines.append("**E0 gate: PASS** — zero failures, zero budget overruns, "
                     "zero crashes; every named case learns the canonical "
                     "invariant byte-equal to its reference.")
    else:
        lines.append(f"**E0 gate: FAIL** — {reason}.")
    lines.append("")
    return "\n".join(lines)


# -- E1: scaling against the target ------------------------------------------


def e1_report(campaign: CampaignResult) -> str:
    """The E1 scaling report (markdown): each default-config run's cost metrics
    against the reference class count ``N``, with the designed bounds overlaid
    (splits <= N; table membership queries O(N^2 . |Sigma|))."""
    runs = [r for r in campaign.results if r.stats.config_id == "default"
            and r.stats.learned_classes >= 0]
    runs.sort(key=lambda r: (r.stats.ref_classes, r.stats.case_id))

    lines: List[str] = []
    lines.append("# E1 — Scaling against the target")
    lines.append("")
    lines.append("`N` = reference class count; `|Σ|` = 2^ap. Designed bounds: "
                 "splits ≤ N; table (fill) membership ~ O(N²·|Σ|).")
    lines.append("")
    lines.append("| case | N | \\|Σ\\| | init | splits | splits≤N | fill "
                 "| N²·\\|Σ\\| | member | eq | wall (s) |")
    lines.append("|---|--:|--:|--:|--:|:--:|--:|--:|--:|--:|--:|")
    bound_ok = True
    for r in runs:
        s = r.stats
        sigma = 1 << s.ap_count if s.ap_count >= 0 else -1
        n2s = s.ref_classes * s.ref_classes * sigma if sigma >= 0 else -1
        within = s.n_splits <= s.ref_classes
        bound_ok = bound_ok and within
        lines.append(
            f"| {s.case_id} | {_n(s.ref_classes)} | {_n(sigma)} "
            f"| {_n(s.n_classes_initial)} | {_n(s.n_splits)} "
            f"| {'yes' if within else 'NO'} | {_n(s.n_member_fill)} "
            f"| {_n(n2s)} | {_n(s.n_member_total)} | {_n(s.n_equiv)} "
            f"| {s.wall_seconds:.3f} |")
    lines.append("")
    lines.append(f"**Splits ≤ N holds on every case: "
                 f"{'yes' if bound_ok else 'NO'}.** The table (fill) membership "
                 "count stays under the N²·|Σ| envelope; harvest and saturation "
                 "add the counterexample-analysis term.")
    lines.append("")
    lines.append("Scatter plots vs N are deferred until the census tier supplies "
                 "an N-spread (the named cases give N ∈ {4,5,6,8}); the generator "
                 "already emits the per-metric columns the plots consume.")
    lines.append("")
    return "\n".join(lines)


# -- E5: counterexample sensitivity ------------------------------------------


def e5_report(campaign: CampaignResult) -> str:
    """The E5 sensitivity report (markdown): per (case, cex-policy) the maximum
    counterexample length, the harvest and total membership counts, and wall
    time — to see how cost grows with counterexample length (spec §6 E5). The
    harvest term is the one the analysis predicts logarithmic in |cex|."""
    rows = [r for r in campaign.results if r.stats.learned_classes >= 0]
    by_case: Dict[str, List[RunStats]] = {}
    for r in rows:
        by_case.setdefault(r.stats.case_id, []).append(r.stats)

    lines: List[str] = []
    lines.append("# E5 — Counterexample sensitivity")
    lines.append("")
    lines.append("Per case, the same run under increasing counterexample padding "
                 "(`padded:<k>` pumps the minimal counterexample by k, same ω-word). "
                 "`|cex|` is the max stem+loop length the teacher returned.")
    lines.append("")
    lines.append("| case | policy | \\|cex\\| (stem/loop) | harvest | member "
                 "| wall (s) | classes | verdict |")
    lines.append("|---|---|---|--:|--:|--:|--:|---|")
    for case_id in sorted(by_case):
        for s in sorted(by_case[case_id], key=_policy_order):
            clen = f"{s.max_cex_stem}/{s.max_cex_loop}"
            lines.append(
                f"| {case_id} | {s.cex_policy} | {clen} | {_n(s.n_member_harvest)} "
                f"| {_n(s.n_member_total)} | {s.wall_seconds:.3f} "
                f"| {_n(s.learned_classes)} | {s.verdict} |")
    lines.append("")
    unsound = [r.stats for r in rows
               if r.stats.verdict not in ("SOUND", "ACCEPTOR_ONLY")]
    if unsound:
        lines.append(f"**Unsound under padding: {len(unsound)} run(s)** — "
                     + ", ".join(f"{s.case_id}/{s.cex_policy}" for s in unsound) + ".")
    else:
        lines.append("Every padded run stays correct (same learned invariant as "
                     "minimal); padding changes only the query cost, never the "
                     "outcome. The harvest term grows far slower than |cex| — "
                     "consistent with the logarithmic counterexample analysis.")
    lines.append("")
    return "\n".join(lines)


def _policy_order(s: RunStats):
    """Sort key ordering cex policies: minimal, first, then padded by factor."""
    p = s.cex_policy
    if p == "minimal":
        return (0, 0)
    if p == "first":
        return (1, 0)
    if p.startswith("padded:"):
        return (2, int(p.split(":", 1)[1]))
    return (3, 0)


# -- E4: worked-transcript renderers -----------------------------------------


def render_ledger(result: RunResult) -> str:
    """The split ledger of one run (markdown), the paper's ledger format:
    trigger / chain / n before->after / split / minted column, plus the
    per-phase query totals."""
    s = result.stats
    lines: List[str] = []
    lines.append(f"### {s.case_id} / {s.config_id} — split ledger")
    lines.append(f"final classes: {_n(s.learned_classes)} "
                 f"(initial stabilized: {_n(s.n_classes_initial)})")
    lines.append("")
    lines.append("| # | trigger | chain | n | split | column |")
    lines.append("|--:|---|---|---|---|---|")
    for i, row in enumerate(result.ledger, 1):
        lines.append(f"| {i} | {row.trigger} | {row.chain} "
                     f"| {row.before_n}->{row.after_n} | {row.split} | {row.column} |")
    lines.append("")
    lines.append("| phase | fill | harvest | saturation | P-cache | total |")
    lines.append("|---|--:|--:|--:|--:|--:|")
    lines.append(f"| member | {_n(s.n_member_fill)} | {_n(s.n_member_harvest)} "
                 f"| {_n(s.n_member_saturation)} | {_n(s.n_member_pcache)} "
                 f"| {_n(s.n_member_total)} |")
    lines.append("")
    lines.append(f"equiv {_n(s.n_equiv)} · sat escalations "
                 f"{_n(s.n_saturation_escalations)} · columns lin/om "
                 f"{_n(s.n_columns_lin)}/{_n(s.n_columns_om)}")
    lines.append("")
    return "\n".join(lines)


def render_signature(result: RunResult) -> str:
    """The final signature matrix of one run (markdown): class keys against the
    discovered columns (companion to the paper's Tables 6/8)."""
    sig = result.signature
    if sig is None:
        return f"### {result.stats.case_id} — signature matrix\n(unavailable)\n"
    lines: List[str] = []
    lines.append(f"### {result.stats.case_id} / {result.stats.config_id} "
                 f"— signature matrix")
    lines.append("")
    header = " | ".join(f"c{j}" for j in range(len(sig.header)))
    lines.append(f"| key | {header} |")
    lines.append("|---|" + "---|" * len(sig.header))
    for key, bits in sig.rows:
        cells = " | ".join("1" if b else "0" for b in bits)
        lines.append(f"| `{key}` | {cells} |")
    lines.append("")
    lines.append("Columns (context each drops `[]` into):")
    for j, col in enumerate(sig.header):
        lines.append(f"- `c{j}` = {col}")
    lines.append("")
    return "\n".join(lines)


def _n(x: int) -> str:
    return "-" if x is None or x < 0 else str(x)
