"""Smoke the instrumented run (`sosl.experiment.run.run_case`) on a few sources.

    python3 -m tests.sosl.experiment_run [<hoa> ...]

Default cases exercise the two configs the campaign leans on: the default
(saturation on, bounded equivalence) on the triptych/specimens, and the M2
ablation (saturation off, exact equivalence) on the two proven-permanent
specimens. Prints the compact stats and asserts the expected verdict per case.
"""
from __future__ import annotations

import sys
from typing import List, Tuple

from sosl.experiment.run import Config, run_case
from sosl.experiment.stats import csv_row, CSV_FIELDS

DEFAULT = Config("default", saturation=True, eq_mode="bounded")
ABLATE = Config("no-sat-exact", saturation=False, eq_mode="exact")

# (case_id, hoa, config, expected verdict)
CASES: List[Tuple[str, str, Config, str]] = [
    ("gf_aa", "samples/gf_aa_parity.hoa", DEFAULT, "SOUND"),
    ("even", "samples/even.hoa", DEFAULT, "SOUND"),
    ("evenblocks", "samples/evenblocks.hoa", DEFAULT, "SOUND"),
    ("a_once", "samples/a_once.hoa", DEFAULT, "SOUND"),
    ("a_implies_xa", "samples/a_implies_xa.hoa", DEFAULT, "SOUND"),
    ("a_once", "samples/a_once.hoa", ABLATE, "ACCEPTOR_ONLY"),
    ("a_implies_xa", "samples/a_implies_xa.hoa", ABLATE, "ACCEPTOR_ONLY"),
]


def main(argv: List[str]) -> int:
    if argv:
        cases = [(argv_path.rsplit("/", 1)[-1].rsplit(".", 1)[0], argv_path,
                  DEFAULT, None) for argv_path in argv]
    else:
        cases = CASES

    ok = True
    for case_id, path, cfg, expect in cases:
        res = run_case(case_id, path, cfg)
        s = res.stats
        flag = ""
        if expect is not None and s.verdict != expect:
            flag = f"  !! expected {expect}"
            ok = False
        print(f"{case_id:<14} {cfg.config_id:<13} "
              f"ref={s.ref_classes} init={s.n_classes_initial} "
              f"learned={s.learned_classes} splits={s.n_splits} "
              f"mem={s.n_member_total}(f{s.n_member_fill}/h{s.n_member_harvest}/"
              f"s{s.n_member_saturation}/p{s.n_member_pcache}) "
              f"eq={s.n_equiv} sat={s.n_saturation_escalations} "
              f"cert={s.eq_certification} stall={s.stall_class} "
              f"-> {s.verdict}{flag}")

    sample = run_case("even", "samples/even.hoa", DEFAULT).stats
    print("\nCSV header:", ",".join(CSV_FIELDS))
    print("sample row:", ",".join(csv_row(sample)))
    print("\nALL OK" if ok else "\nFAILURES")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
