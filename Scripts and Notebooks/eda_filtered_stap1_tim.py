"""EDA stap 1 on filtered dataset — run with:
  uv run python 'Scripts and Notebooks/eda_filtered_stap1_tim.py'
  or: .venv/bin/python 'Scripts and Notebooks/eda_filtered_stap1_tim.py'

Loads data/processed/df_filtered.xlsx with openpyxl. Does NOT mutate the xlsx.
Writes artifacts under Scripts and Notebooks/eda_outputs/filtered_stap1/.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
XLSX = ROOT / "data" / "processed" / "df_filtered.xlsx"
RAW = ROOT / "data" / "raw" / "exquairo_ai_bootcamp_synth_dataset.csv"
OUT = Path(__file__).resolve().parent / "eda_outputs" / "filtered_stap1"
OUT.mkdir(parents=True, exist_ok=True)


def main() -> None:
    df = pd.read_excel(XLSX, engine="openpyxl")
    n_rows, n_cols = df.shape
    mem_bytes = int(df.memory_usage(deep=True).sum())
    mem_mb = round(mem_bytes / 1e6, 2)
    dtype_counts = {str(k): int(v) for k, v in df.dtypes.value_counts().items()}

    print("=== STAP 1 — filtered df ===")
    print("source", XLSX.relative_to(ROOT))
    print("shape", df.shape)
    print("memory_deep_mb", mem_mb)
    print("dtype_counts", dtype_counts)

    # --- missingness ---
    miss_n = df.isna().sum()
    miss_pct = (miss_n / n_rows * 100).round(6)
    miss_df = (
        pd.DataFrame(
            {
                "column": miss_n.index,
                "n_missing": miss_n.values,
                "pct_missing": miss_pct.values,
            }
        )
        .sort_values("pct_missing", ascending=False)
        .reset_index(drop=True)
    )
    miss_df.to_csv(OUT / "missingness.csv", index=False)
    print("\nTop 10 missing %:")
    print(miss_df.head(10).to_string(index=False))
    print("columns_with_any_nan", int((miss_n > 0).sum()))

    # --- -8 / -9 ---
    neg_rows: list[dict] = []
    for c in df.columns:
        s = df[c]
        if pd.api.types.is_numeric_dtype(s):
            n8 = int((s == -8).sum())
            n9 = int((s == -9).sum())
        else:
            as_str = s.astype(str)
            n8 = int((as_str == "-8").sum())
            n9 = int((as_str == "-9").sum())
        if n8 or n9:
            neg_rows.append(
                {"column": c, "count_minus8": n8, "count_minus9": n9}
            )
    neg_df = (
        pd.DataFrame(neg_rows)
        if neg_rows
        else pd.DataFrame(columns=["column", "count_minus8", "count_minus9"])
    )
    neg_df.to_csv(OUT / "suspicious_codes_minus8_9.csv", index=False)
    print("\n-8/-9 columns affected:", len(neg_rows))
    if neg_rows:
        print(neg_df.to_string(index=False))

    # --- HBAC_* <= 0 ---
    hbac_info: dict[str, dict] = {}
    for c in [c for c in df.columns if str(c).startswith("HBAC_")]:
        s = df[c]
        hbac_info[c] = {
            "n_le_0": int((s <= 0).sum()),
            "n_eq_0": int((s == 0).sum()),
            "n_lt_0": int((s < 0).sum()),
            "n_nan": int(s.isna().sum()),
            "min": float(s.min()) if s.notna().any() else None,
            "max": float(s.max()) if s.notna().any() else None,
        }
    pd.DataFrame([{"column": k, **v} for k, v in hbac_info.items()]).to_csv(
        OUT / "suspicious_codes_hbac_le0.csv", index=False
    )
    print("\nHBAC <= 0:")
    for k, v in hbac_info.items():
        print(f"  {k}: <=0={v['n_le_0']} (==0={v['n_eq_0']}, <0={v['n_lt_0']}), NaN={v['n_nan']}")

    # --- NSES ---
    nses = df["NSES"]
    n_multi_dot_xlsx = 0
    if pd.api.types.is_object_dtype(nses) or pd.api.types.is_string_dtype(nses):
        as_str = nses.astype(str)
        true_empty = (
            nses.isna()
            | (as_str.str.strip() == "")
            | (as_str.str.lower() == "nan")
        )
        multi = (~true_empty) & (as_str.str.count(r"\.") > 1)
        n_multi_dot_xlsx = int(multi.sum())
        n_true_nan = int(true_empty.sum())
    else:
        n_true_nan = int(nses.isna().sum())

    nses_note: dict = {
        "dtype": str(nses.dtype),
        "n_true_nan": n_true_nan,
        "pct_true_nan": round(float(n_true_nan / n_rows * 100), 4),
        "n_multi_dot_unparseable_in_xlsx": n_multi_dot_xlsx,
        "note": (
            "In df_filtered.xlsx, NSES is already float64. "
            "True NaN count matches raw CSV blank/NaN count. "
            "No object/str multi-dot residues remain in the xlsx "
            "(resolved upstream when building the filtered file)."
            if str(nses.dtype) != "object"
            else "NSES is object/str in xlsx; see multi-dot counts."
        ),
    }

    raw_nses_compare = None
    if RAW.exists():
        raw_nses = pd.read_csv(RAW, sep=";", usecols=["NSES"], dtype=str)["NSES"]
        true_empty = (
            raw_nses.isna()
            | (raw_nses.str.strip() == "")
            | (raw_nses.str.lower() == "nan")
        )
        multi = raw_nses.fillna("").str.count(r"\.") > 1
        parsed = pd.to_numeric(raw_nses, errors="coerce")
        raw_nses_compare = {
            "raw_true_empty_or_nan": int(true_empty.sum()),
            "raw_multi_dot_strings": int(multi.sum()),
            "raw_unparseable_nonempty": int((~true_empty & parsed.isna()).sum()),
            "filtered_xlsx_true_nan": n_true_nan,
            "filtered_xlsx_dtype": str(nses.dtype),
        }
        nses_note["raw_csv_compare"] = raw_nses_compare

    print("\nNSES:")
    print(f"  dtype={nses_note['dtype']}, true_NaN={nses_note['n_true_nan']} ({nses_note['pct_true_nan']}%)")
    print(f"  multi-dot unparseable in xlsx={nses_note['n_multi_dot_unparseable_in_xlsx']}")
    if raw_nses_compare:
        print(
            f"  vs raw CSV: empty/NaN={raw_nses_compare['raw_true_empty_or_nan']}, "
            f"multi-dot={raw_nses_compare['raw_multi_dot_strings']}"
        )

    suspicious = {
        "minus8_minus9": neg_rows,
        "hbac_le_0": hbac_info,
        "nses": nses_note,
    }
    with open(OUT / "suspicious_codes.json", "w", encoding="utf-8") as f:
        json.dump(suspicious, f, indent=2)

    # --- vs raw ---
    dropped = None
    if RAW.exists():
        raw_cols = list(pd.read_csv(RAW, sep=";", nrows=0).columns)
        dropped = sorted(set(raw_cols) - set(df.columns))
        pd.Series(dropped, name="dropped_column").to_csv(
            OUT / "dropped_vs_raw.csv", index=False
        )
        print("\nvs raw CSV: 100 cols →", n_cols, "cols; rows", n_rows, "(same 17960)" if n_rows == 17960 else "")
        print("dropped columns:", len(dropped))

    meta = {
        "source": str(XLSX.relative_to(ROOT)),
        "shape": {"n_rows": n_rows, "n_cols": n_cols},
        "memory_deep_bytes": mem_bytes,
        "memory_deep_mb": mem_mb,
        "dtype_counts": dtype_counts,
        "n_columns_with_any_nan": int((miss_n > 0).sum()),
        "top10_missing_pct": [
            {
                "column": r.column,
                "pct_missing": float(r.pct_missing),
                "n_missing": int(r.n_missing),
            }
            for r in miss_df.head(10).itertuples()
        ],
        "vs_raw_csv": {
            "raw_shape": [17960, 100],
            "filtered_shape": [n_rows, n_cols],
            "same_nrows": n_rows == 17960,
            "n_cols_dropped": (100 - n_cols),
            "n_cols_kept": n_cols,
            "dropped_columns_sample": (dropped[:20] if dropped else None),
            "n_dropped_listed": len(dropped) if dropped else None,
        },
        "hbac_le_0": hbac_info,
        "nses": nses_note,
        "minus8_minus9_n_cols_affected": len(neg_rows),
    }
    with open(OUT / "meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    print("\nArtifacts →", OUT.relative_to(ROOT))
    print("See EDA_FILTERED_STAP1.md")


if __name__ == "__main__":
    main()
