"""Read-only aggregation of the two E1 reference CSVs.

Joins `reference/e1_census.csv` with `reference/e1_covariates.csv` on
instance name and prints the paper-bound readings (no engine runs):

1. F22 mark upward-closure: the pooled fraction over all non-empty
   `(slot, dst)` families (the number the paper cites).
2. Compression correlates: Spearman rank correlation of the compression
   ratio `nodes_final / cells` against the candidate covariates.
3. Pre-quotient closure depth: distribution of `depth` against `|EM1|`
   and the class count (the section-5 depth question).

Instance names are not parsed: their acc tokens are source-GBA
provenance, never an analysis variable (report F23).

Usage: python3 tests/sos_sdd/e1_readoff.py   (from the repo root)
"""

import pandas as pd

CENSUS: str = "tests/sos_sdd/reference/e1_census.csv"
COVARIATES: str = "tests/sos_sdd/reference/e1_covariates.csv"


def main() -> None:
    census = pd.read_csv(CENSUS)
    cov = pd.read_csv(COVARIATES)
    df = census.merge(cov, on="name", suffixes=("", "_cov"))
    print(f"joined rows: {len(df)} (census {len(census)}, cov {len(cov)})")

    print("\n== 1. F22 upward-closure (pooled) ==")
    up, tot = df["upclosed_pairs"].sum(), df["mark_pairs"].sum()
    print(f"pooled: {up} / {tot} = {up / tot:.4f}")

    print("\n== 2. compression ratio and its correlates (Spearman) ==")
    df["cells_chk"] = df["em1"] * df["states_cov"]
    mism = (df["cells"] != df["cells_chk"]).sum()
    print(f"cells == em1*slots on all rows: {'yes' if mism == 0 else f'NO ({mism})'}")
    df["ratio"] = df["nodes_final"] / df["cells"]
    print("ratio quantiles:")
    print(df["ratio"].quantile([0.05, 0.25, 0.5, 0.75, 0.95, 1.0]).to_string(
        float_format=lambda v: f"{v:.4f}"))
    df["sharing"] = df["distinct_cells"] / df["cells"]
    df["upfrac"] = df["upclosed_pairs"] / df["mark_pairs"]
    df["letters_frac"] = df["letter_classes"] / (2 ** df["n_ap"])
    cols = ["states", "n_ap", "marks", "letter_classes", "letters_frac",
            "em1", "depth", "sharing", "upfrac", "const_slots"]
    corr = df[cols + ["ratio"]].corr(method="spearman")["ratio"].drop("ratio")
    print("spearman(covariate, ratio):")
    print(corr.to_string(float_format=lambda v: f"{v:+.3f}"))

    print("\n== 3. pre-quotient closure depth ==")
    print("depth quantiles:")
    print(df["depth"].quantile([0.5, 0.9, 0.99, 1.0]).to_string(
        float_format=lambda v: f"{v:.1f}"))
    print(f"max depth: {df['depth'].max()} at em1={df.loc[df['depth'].idxmax(), 'em1']}")
    print(f"depth <= classes on {(df['depth'] <= df['classes']).mean():.4f} of rows"
          f" (classes = quotient size)")
    print(f"depth / em1 quantiles:")
    print((df["depth"] / df["em1"]).quantile([0.5, 0.9, 1.0]).to_string(
        float_format=lambda v: f"{v:.4f}"))
    big = df.nlargest(5, "em1")[["name", "em1", "depth", "classes",
                                 "nodes_final", "ratio"]]
    print("5 largest algebras:")
    print(big.to_string(index=False, float_format=lambda v: f"{v:.4f}"))


if __name__ == "__main__":
    main()
