"""EDA stap 4 — missings / cleaning RULES inventory (raw, no data adaptation).

Run: uv run python 'Scripts and Notebooks/eda_stap4_tim.py'
Outputs: Scripts and Notebooks/eda_outputs/stap4/

Does NOT write cleaned CSV or modify data/raw. Rules are documented only.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "data/raw/exquairo_ai_bootcamp_synth_dataset.csv"
OUT = Path(__file__).resolve().parent / "eda_outputs" / "stap4"
OUT.mkdir(parents=True, exist_ok=True)

# Columns where ≤0 is clinically implausible / sentinel-like
LE0_RELEVANT = {
    "HBAC_T1",
    "HBAC_T2",
    "HBAC_T3",
    "HB1C_T1",
    "HB1C_T2",
    "HB1C_T3",
    "GLU_T1",
    "GLU_T2",
    "GLU_T3",
    "BMI_T1",
    "BMI_T2",
    "WEIGHT_T1",
    "WEIGHT_T2",
    "WEIGHT_T3",
    "HEIGHT_T1",
    "HEIGHT_T2",
    "HEIGHT_T3",
    "WAIST_T1",
    "WAIST_T2",
    "WAIST_T3",
    "SBP_T1",
    "SBP_T2",
    "DBP_T1",
    "DBP_T2",
    "CHO_T1",
    "CHO_T2",
    "CHO_T3",
    "HDC_T1",
    "HDC_T2",
    "HDC_T3",
    "LDC_T1",
    "LDC_T2",
    "LDC_T3",
    "TGL_T1",
    "TGL_T2",
    "TGL_T3",
    "ALT_T1",
    "BKR_T1",
    "BKR_T2",
    "BALB_T1",
    "UZ_T1",
    "SUMOFKCAL",
}

MD_T12 = {"METABOLIC_DISORDER_T1", "METABOLIC_DISORDER_T2"}
MD_T3 = {"METABOLIC_DISORDER_T3"}
FAMILY = {"TYPE2_DIABETES_FAMILY_FATHER", "TYPE2_DIABETES_FAMILY_MOTHER"}
HIGH_MISS_LABS = {"ALT_T1", "UZ_T1", "BALB_T1"}
OUTLIER_CANDIDATES = {"HB1C_T1", "TGL_T1", "ALT_T1", "HBAC_T2"}


def propose_rule(col: str, pct_nan: float, n_neg8: int, n_neg9: int, n_le0: int) -> str:
    if col in MD_T12:
        return "mask −8/−9→NaN for analysis; keep 0/1"
    if col in MD_T3:
        return "for binary modeling map 2→0 in-memory; keep 1=yes"
    if col in FAMILY:
        return "high-NaN ≈ unchecked/no (confirm); optional fill 0"
    if col.startswith("HBAC") and n_le0 > 0:
        return "≤0 → missing (implausible %)"
    if col in HIGH_MISS_LABS:
        return "team: keep+missing-indicator vs drop (~49% NaN)"
    if col in OUTLIER_CANDIDATES:
        return "flag extremes vs winsorize (do not apply yet)"
    if col == "SLEEP_QUALITY" and pct_nan > 40:
        return "high missing; team decision keep/impute/drop"
    if col == "PREGNANCIES" and pct_nan > 40:
        return "likely sex-linked missing (males); mask/skip by GENDER"
    if col.startswith("HB1C") and pct_nan > 15:
        return "prefer HBAC_% twin; high miss vs HBAC"
    if pct_nan >= 30:
        return "high missing — document; colleague decides impute/drop"
    if n_neg8 or n_neg9:
        return "has −8/−9 — treat as missing in analysis"
    if col in LE0_RELEVANT and n_le0 > 0:
        return "n≤0 present — review sentinel vs true zero"
    if pct_nan > 0:
        return "standard NaN; pairwise/complete-case later"
    return "no missing observed"


def main() -> None:
    df = pd.read_csv(CSV, sep=";")
    n = len(df)

    rows = []
    for c in df.columns:
        s = pd.to_numeric(df[c], errors="coerce")
        # For object-like that failed: still count true NaN from original
        n_nan = int(df[c].isna().sum())
        # Also count values that are literally -8/-9 in numeric sense
        n_neg8 = int((s == -8).sum()) if s.notna().any() or (df[c] == -8).any() else 0
        n_neg9 = int((s == -9).sum()) if s.notna().any() or (df[c] == -9).any() else 0
        # Prefer exact match on original for sentinels
        try:
            n_neg8 = int((pd.to_numeric(df[c], errors="coerce") == -8).sum())
            n_neg9 = int((pd.to_numeric(df[c], errors="coerce") == -9).sum())
        except Exception:
            pass
        le0_relevant = c in LE0_RELEVANT
        if le0_relevant:
            n_le0 = int((s.dropna() <= 0).sum())
        else:
            n_le0 = ""
        pct_nan = round(100 * n_nan / n, 2)
        n_le0_int = int(n_le0) if n_le0 != "" else 0
        rows.append(
            {
                "column": c,
                "n_nan": n_nan,
                "pct_nan": pct_nan,
                "n_neg8": n_neg8,
                "n_neg9": n_neg9,
                "n_le0": n_le0 if le0_relevant else "",
                "proposed_rule": propose_rule(c, pct_nan, n_neg8, n_neg9, n_le0_int),
            }
        )

    miss_df = pd.DataFrame(rows).sort_values("pct_nan", ascending=False)
    miss_df.to_csv(OUT / "missingness_by_column.csv", index=False)

    # Proposed cleaning rules (document only — apply_when = colleague later)
    rules = [
        {
            "rule_id": "R01",
            "columns": "METABOLIC_DISORDER_T1, METABOLIC_DISORDER_T2",
            "rule": "Recode −8 and −9 to missing (NaN); retain 0/1",
            "rationale": "Bootcamp composite coding; −8/−9 not valid binary outcomes (stap 1–2)",
            "apply_when": "colleague later — analysis masking only until master clean",
        },
        {
            "rule_id": "R02",
            "columns": "METABOLIC_DISORDER_T3",
            "rule": "For binary modeling map 2→0; keep 1=yes; leave NaN as missing",
            "rationale": "Starter notebook / stap 2: T3 uses 1=yes, 2=no (≠ T1/T2 coding)",
            "apply_when": "colleague later — in-memory for modeling only",
        },
        {
            "rule_id": "R03",
            "columns": "HBAC_T1, HBAC_T2, HBAC_T3",
            "rule": "Values ≤0 → missing",
            "rationale": "HbA1c % cannot be ≤0; stap3 flagged HBAC_T2 n≤0=2",
            "apply_when": "colleague later",
        },
        {
            "rule_id": "R04",
            "columns": "TYPE2_DIABETES_FAMILY_FATHER, TYPE2_DIABETES_FAMILY_MOTHER",
            "rule": "Treat blank/NaN as unchecked/no (optional fill 0); confirmed 1=yes",
            "rationale": "Bootcamp TXT: 1=yes, blank=no; ~97% NaN matches unchecked pattern",
            "apply_when": "colleague later — confirm with Tim/bootcamp before fill",
        },
        {
            "rule_id": "R05",
            "columns": "ALT_T1, UZ_T1, BALB_T1",
            "rule": "TEAM DECISION: keep with missing-indicator feature OR drop from model",
            "rationale": "~49% NaN each — high risk of bias if listwise-deleted or naively imputed",
            "apply_when": "colleague + team decision before master",
        },
        {
            "rule_id": "R06",
            "columns": "HB1C_T1, TGL_T1, ALT_T1 (and similar labs)",
            "rule": "Outliers: FLAG for review vs winsorize at p01/p99 — propose, do not apply yet",
            "rationale": "Stap3: extreme max vs p99 (HB1C max 155, TGL 12.56, ALT 451)",
            "apply_when": "colleague later after clinical review",
        },
        {
            "rule_id": "R07",
            "columns": "HB1C_T* vs HBAC_T*",
            "rule": "Prefer one unit for modeling (HBAC=% or HB1C=mmol/mol); do not both blindly",
            "rationale": "Same construct, different units; HB1C_T1 has ~21% NaN vs HBAC_T1 ~0.7%",
            "apply_when": "feature shortlist (stap 6+)",
        },
        {
            "rule_id": "R08",
            "columns": "PREGNANCIES",
            "rule": "Interpret missing by GENDER (likely N/A for males); do not impute as 0 blindly",
            "rationale": "~44% NaN; sex-linked structural missingness",
            "apply_when": "colleague later",
        },
        {
            "rule_id": "R09",
            "columns": "SLEEP_QUALITY, SUMOFKCAL, SUMOFALCOHOL, NSES (and other ≥30% NaN)",
            "rule": "Document high missing; decide impute / missing-indicator / drop per use-case",
            "rationale": "Material missingness; stap1–3 flagged",
            "apply_when": "colleague + team",
        },
        {
            "rule_id": "R10",
            "columns": "FEATURE_T3 / *_T3 when predicting MD_T1 or MD_T2",
            "rule": "Do NOT use T3 features (or MD_T3) as predictors of T1/T2 — leakage",
            "rationale": "Temporal leakage: T3 measured after T1/T2 outcomes",
            "apply_when": "always for T1/T2 prediction pipelines",
        },
        {
            "rule_id": "R11",
            "columns": "SUMOFKCAL",
            "rule": "Review zeros (stap3: 2×0) — true zero vs sentinel before imputing",
            "rationale": "Implausible daily kcal=0 for most adults",
            "apply_when": "colleague later",
        },
        {
            "rule_id": "R12",
            "columns": "all analysis scripts",
            "rule": "Until master clean exists: mask sentinels in-memory only; never overwrite data/raw",
            "rationale": "Team process — colleagues produce new master after inventory",
            "apply_when": "now and until master CSV delivered",
        },
    ]
    rules_df = pd.DataFrame(rules)
    rules_df.to_csv(OUT / "proposed_cleaning_rules.csv", index=False)

    # Top-40 missingness bar chart
    top40 = miss_df.head(40)
    fig, ax = plt.subplots(figsize=(10, 10))
    y = np.arange(len(top40))
    ax.barh(y, top40["pct_nan"].values, color="#4C78A8")
    ax.set_yticks(y)
    ax.set_yticklabels(top40["column"].values, fontsize=7)
    ax.invert_yaxis()
    ax.set_xlabel("% NaN (raw)")
    ax.set_title("Stap 4 — top 40 columns by missingness (raw, no cleaning)")
    fig.tight_layout()
    fig.savefig(OUT / "missingness_heatmap_top40.png", dpi=140)
    plt.close()

    # Also a simple matrix-style heatmap for top40 (row = col, single column of pct)
    # Keep filename as requested; bar is primary.

    summary = {
        "n_rows": n,
        "n_cols": df.shape[1],
        "n_cols_with_nan": int((miss_df["n_nan"] > 0).sum()),
        "n_cols_with_neg8_or_neg9": int(
            ((miss_df["n_neg8"] > 0) | (miss_df["n_neg9"] > 0)).sum()
        ),
        "worst_missing_top10": miss_df.head(10)[["column", "pct_nan"]].to_dict(
            orient="records"
        ),
        "n_proposed_rules": len(rules),
        "rule_ids": [r["rule_id"] for r in rules],
        "hbac_t2_n_le0": int(
            (pd.to_numeric(df["HBAC_T2"], errors="coerce").dropna() <= 0).sum()
        ),
        "md_t1_n_neg8": int((pd.to_numeric(df["METABOLIC_DISORDER_T1"], errors="coerce") == -8).sum()),
        "md_t1_n_neg9": int((pd.to_numeric(df["METABOLIC_DISORDER_T1"], errors="coerce") == -9).sum()),
        "note": "NO cleaned CSV written; rules inventory only",
        "cleaned_dataset_written": False,
    }
    (OUT / "stap4_summary.json").write_text(json.dumps(summary, indent=2, default=str))
    print(json.dumps(summary, indent=2, default=str))
    print("Wrote", OUT)


if __name__ == "__main__":
    main()
