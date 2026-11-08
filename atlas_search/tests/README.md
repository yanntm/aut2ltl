# Experiment receipts

`logs/` contains regenerable selections, one-input JSON outcomes and bounded
child logs. Scientific controls and useful witnesses are retained explicitly
with their commands in the parent README or a report. These are experimental
results, not an additional unit-test suite.

`summarize_minimum.py` audits the full saved population and letter-order coverage
below three classes, combines those receipts, and checks the three-class
witness's six orders plus exact-oracle/saturation controls before retaining its
aggregate. It reads the raw runs under `logs/` and the retained earlier results.
