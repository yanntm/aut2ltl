"""Report generators: the E0 validation one-pager and the E4 worked-transcript
renderers (split ledger + signature matrix), all machine-generated from a
`CampaignResult` — no hand-edited numbers.

The E0 report is the campaign's gate: it tabulates every run's verdict and
declares PASS only when no run is `MISMATCH` or `BUDGET` and every
permanent-stall specimen certified `ACCEPTOR_ONLY` under a no-saturation config
(spec §9 P4/F5). The E4 renderers reproduce the paper's ledger format and the
signature matrix (companion to Tables 6/8) for a single run.
"""
from __future__ import annotations

from typing import List, Optional

from sosl.experiment.driver import CampaignResult
from sosl.experiment.manifest import MANIFEST_VERSION
from sosl.experiment.run import RunResult
from sosl.experiment.stats import RunStats


def _byte_flag(s: RunStats) -> str:
    """The byte-equality reading implied by the verdict (SOUND = byte-equal)."""
    if s.verdict == "SOUND":
        return "yes"
    if s.verdict in ("ACCEPTOR_ONLY", "MISMATCH"):
        return "no"
    return "-"


def e0_gate(campaign: CampaignResult) -> Optional[str]:
    """``None`` if E0 passes, else a one-line reason it failed."""
    bad = [s for s in campaign.stats if s.verdict in ("MISMATCH", "BUDGET")]
    if bad:
        return (f"{len(bad)} run(s) MISMATCH/BUDGET: "
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
    mismatch = sum(s.verdict == "MISMATCH" for s in campaign.stats)
    budget = sum(s.verdict == "BUDGET" for s in campaign.stats)
    total_mem = sum(max(0, s.n_member_total) for s in campaign.stats)
    total_eq = sum(max(0, s.n_equiv) for s in campaign.stats)
    lines.append(f"**Totals.** {sound} SOUND · {acc} ACCEPTOR_ONLY · "
                 f"{mismatch} MISMATCH · {budget} BUDGET. "
                 f"Query budget used: {total_mem} membership, {total_eq} equivalence.")
    lines.append("")
    reason = e0_gate(campaign)
    if reason is None:
        lines.append("**E0 gate: PASS** — zero mismatches, zero budget overruns; "
                     "the permanent specimens certify ACCEPTOR_ONLY under "
                     "no-saturation (spec §9 P4/F5).")
    else:
        lines.append(f"**E0 gate: FAIL** — {reason}.")
    lines.append("")
    return "\n".join(lines)


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
