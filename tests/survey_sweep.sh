#!/usr/bin/env bash
#
# tests/survey_sweep.sh — sweep the front-end survey across --use configurations,
# one log per configuration, at a single point in time.
#
# Each configuration is a distinct --use citation passed straight through to the
# tool (tests/survey.py -> python3 -m aut2ltl --use ...), so the sweep compares
# techniques/flags head-to-head on the same corpus. The log NAME is the citation
# itself: the comma-separated flags joined with '+' in CITED ORDER (so
# 'decompose,str' -> decompose+str), or 'default' for the no-citation portfolio.
# Per config we keep:
#   $OUTDIR/<name>.csv   the dense per-formula CSV (DAG/tree/equiv/...)
#   $OUTDIR/<name>.txt   the survey's own stdout report
# and finally a cross-config SUMMARY.txt (printed too) — read THAT at a glance.
#
# We test every main producer method (acc/weak/buchi/cobuchi/bls/str/sl) both
# bare AND under the decompose (strength) wrapper; sl_driven is its own method
# (the sl-driven core over the integrated cascade str), likewise with/without
# decompose. 'str' is the integrated default cascade (make_hierarchy_class).
#
# Day-to-day this writes a throwaway dir under tests/logs/ (gitignored). For a
# RELEASE reference, point it at the tracked reference dir so the CSVs are
# committed (see .gitignore re-include of tests/logs/reference/*.csv):
#
#   tests/survey_sweep.sh                         # full corpus, throwaway dir
#   tests/survey_sweep.sh tests/logs/reference    # the committed release reference
#   tests/survey_sweep.sh tests/logs/quick "Ga" "GFa & GFb"   # a few formulas, all configs
#
# A full sweep is slow (configs x corpus x per-phase budgets) — that is expected;
# it is a data-collection run, not a gate.
set -u
cd "$(dirname "$0")/.."   # project root

OUTDIR="${1:-tests/logs/sweep_$(date -u +%Y%m%d)}"
[ "$#" -gt 0 ] && shift   # remaining args (if any) are formulas for survey.py
FORMULAS=("$@")           # empty => the curated corpus
mkdir -p "$OUTDIR"

# The --use citations to sweep, in run order. Empty = the hand-tuned default.
# decompose is cited LEFT of the method (wraps it); cited order is preserved in
# both behaviour and the derived log name.
USES=(
  ""                              # default portfolio (no --use)
  "acc"             "decompose,acc"
  "weak"            "decompose,weak"
  "buchi"           "decompose,buchi"
  "cobuchi"         "decompose,cobuchi"
  "bls"             "decompose,bls"
  "str"             "decompose,str"
  "sl"              "decompose,sl"
  "sl_driven,str"   "decompose,sl_driven,str"
)

name_of() { [ -z "$1" ] && echo "default" || echo "${1//,/+}"; }

echo "=== survey sweep -> $OUTDIR  (${#USES[@]} configs) ==="
for use in "${USES[@]}"; do
  label="$(name_of "$use")"
  csv="$OUTDIR/$label.csv"
  rep="$OUTDIR/$label.txt"
  echo "--- $label  (--use ${use:-<default>}) ---"
  if [ -n "$use" ]; then
    KR_SURVEY_CSV="$csv" python3 tests/survey.py --use "$use" "${FORMULAS[@]}" > "$rep" 2>&1
  else
    KR_SURVEY_CSV="$csv" python3 tests/survey.py "${FORMULAS[@]}" > "$rep" 2>&1
  fi
  tail -n 2 "$rep"
done

# Dense cross-config summary. equiv is CSV column 9, dag_nodes column 5; neither
# is preceded by a comma-bearing field, so -F, is safe here.
summary="$OUTDIR/SUMMARY.txt"
{
  printf "%-26s %5s %5s %6s %8s %7s %6s %9s\n" \
         config cases True FALSE TIMEOUT UNVER other DAGsum
  total_false=0
  for use in "${USES[@]}"; do
    label="$(name_of "$use")"
    csv="$OUTDIR/$label.csv"
    [ -f "$csv" ] || continue
    line=$(awk -F, 'NR>1 {
        n++;
        if      ($9=="True")            t++;
        else if ($9=="FALSE")           f++;
        else if ($9=="SPOT_TIMEOUT")    to++;
        else if ($9=="UNVERIFIED_SIZE") uv++;
        else                            ot++;
        if ($5 ~ /^[0-9]+$/) dag+=$5;
      } END {
        printf "%-26s %5d %5d %6d %8d %7d %6d %9d %d", L, n, t, f, to, uv, ot, dag, f
      }' L="$label" "$csv")
    f_count="${line##* }"
    printf "%s\n" "${line% *}"
    total_false=$((total_false + f_count))
  done
  echo
  if [ "$total_false" -gt 0 ]; then
    echo "*** WARNING: $total_false verified-FALSE result(s) across the sweep — true failures ***"
  else
    echo "no verified-FALSE results across the sweep."
  fi
} | tee "$summary"

echo
echo "logs: $OUTDIR   summary: $summary"
