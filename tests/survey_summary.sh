#!/usr/bin/env bash
#
# tests/survey_summary.sh — (re)build the cross-config SUMMARY.txt from the
# per-config CSVs already sitting in a sweep / reference dir.
#
# CSV-ONLY: it re-runs no tool, so it works on an OLD reference folder whose
# per-config .txt stdout logs were never kept — read the dense CSVs, print the
# token-compact table. survey_sweep.sh calls this for its final summary step, so
# a sweep's SUMMARY.txt and a regenerated one are byte-for-byte identical.
#
#   tests/survey_summary.sh tests/logs/reference/20260616
set -u
DIR="${1:?usage: survey_summary.sh <dir>}"

# Canonical config order (mirrors survey_sweep.sh USES -> name_of). Only labels
# whose CSV exists in DIR are emitted, so a partial dir summarises cleanly.
LABELS=(
  default
  acc             decompose+acc
  weak            decompose+weak
  buchi           decompose+buchi
  cobuchi         decompose+cobuchi
  bls             decompose+bls
  str             decompose+str
  sl              decompose+sl
  sl_driven+str   decompose+sl_driven+str
)

summary="$DIR/SUMMARY.txt"
{
  # CSV columns: 5 dag_nodes, 6 temporals, 9 build_s, 10 equiv (none preceded by
  # a comma-bearing field, so -F, is safe). answers = built (not declined / not a
  # build problem); totals are over answers only.
  printf "%-26s %5s %5s %5s %5s %5s %6s %5s %5s %9s %7s %8s\n" \
         config cases answ valid false decl bTO bCR unver DAGsum tempsum build
  total_false=0
  for label in "${LABELS[@]}"; do
    csv="$DIR/$label.csv"
    [ -f "$csv" ] || continue
    line=$(awk -F, 'NR>1 {
        n++; e=$10;
        if      (e=="True")            v++;
        else if (e=="FALSE")           f++;
        else if (e=="UNVERIFIED_SIZE") uv++;
        else if (e=="DECLINED")        d++;
        else if (e ~ /^BUILD_TIMEOUT/) bto++;
        else if (e ~ /^CRASH/)         bcr++;
        if (e=="True"||e=="FALSE"||e=="SPOT_TIMEOUT"||e=="UNVERIFIED_SIZE"||e ~ /^SPOT_ERR/) {
          ans++;
          if ($5 ~ /^[0-9]+$/)   dag+=$5;
          if ($6 ~ /^[0-9]+$/)   tmp+=$6;
          if ($9 ~ /^[0-9.]+$/)  bld+=$9;
        }
      } END {
        printf "%-26s %5d %5d %5d %5d %5d %6d %5d %5d %9d %7d %8.2f %d",
               L, n, ans, v, f, d, bto, bcr, uv, dag, tmp, bld, f
      }' L="$label" "$csv")
    f_count="${line##* }"
    printf "%s\n" "${line% *}"
    total_false=$((total_false + f_count))
  done
  echo
  [ "$total_false" -gt 0 ] && echo "FAIL" || echo "SUCCESS"
} | tee "$summary"
