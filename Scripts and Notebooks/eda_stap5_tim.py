"""EDA stap 5 — bivariate / target associations (raw + in-memory masking only).

Run: uv run python 'Scripts and Notebooks/eda_stap5_tim.py'
Outputs: Scripts and Notebooks/eda_outputs/stap5/

Masks −8/−9→NaN for MD T1/T2 and maps MD T3 2→0 in-memory only.
Does NOT write cleaned CSV. Do NOT use T3 features to predict T1/T2 (leakage).
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
OUT = Path(__file__).resolve().parent / "eda_outputs" / "stap5"
OUT.mkdir(parents=True, exist_ok=True)

# Continuous shortlist for corr + associations (T1-focused; no T3 leakage)
CORR_SHORTLIST = [
    "AGE_T1",
    "BMI_T1",
    "WAIST_T1",
    "SBP_T1",
    "DBP_T1",
    "HBAC_T1",
    "GLU_T1",
    "CHO_T1",
    "HDC_T1",
    "LDC_T1",
    "TGL_T1",
    "ALT_T1",
]

# Broader continuous for MD association screen (T1 / non-T3)
ASSOC_CONT = [
    "AGE_T1",
    "BMI_T1",
    "BMI_T2",
    "WAIST_T1",
    "WEIGHT_T1",
    "HEIGHT_T1",
    "SBP_T1",
    "DBP_T1",
    "MAP_T1",
    "HBF_T1",
    "HBAC_T1",
    "HBAC_T2",
    "HB1C_T1",
    "GLU_T1",
    "CHO_T1",
    "HDC_T1",
    "LDC_T1",
    "TGL_T1",
    "BKR_T1",
    "ALT_T1",
    "BALB_T1",
    "UZ_T1",
    "LLDS",
    "SUMOFKCAL",
    "SUMOFALCOHOL",
    "NSES",
    "LTE_SUM_T1",
    "LDI_SUM_T1",
    "C_SUM_T1",
    "A_SUM_T1",
    "SC_SUM_T1",
    "I_SUM_T1",
    "E_SUM_T1",
    "SD_SUM_T1",
    "V_SUM_T1",
    "D_SUM_T1",
]

# Key binaries / categoricals (exclude T3 leakage features)
ASSOC_CAT = [
    "GENDER",
    "SMOKING",
    "SPORTS_T1",
    "WORK_T1",
    "CYCLE_COMMUTE_T1",
    "BURNOUT_T1",
    "DEPRESSION_T1",
    "HTN_MED_T1",
    "OSTEOARTHRITIS",
    "EDUCATION_LOWER_T1",
    "SLEEP_QUALITY",
    "VOLUNTEER_T1",
    "RESPIRATORY_DISEASE_T1",
    "TYPE2_DIABETES_FAMILY_FATHER",
    "TYPE2_DIABETES_FAMILY_MOTHER",
    "LOW_QUALITY_OF_LIFE_T1",
    "FINANCE_T1",
]


def md_binary(series: pd.Series, which: str) -> pd.Series:
    """In-memory target prep. Does not mutate source CSV."""
    s = pd.to_numeric(series, errors="coerce")
    if which in ("T1", "T2"):
        s = s.mask(s.isin([-8, -9]))
        # keep only 0/1
        s = s.where(s.isin([0, 1]))
        return s
    if which == "T3":
        s = s.map({1: 1, 2: 0})  # 2→0; others/NaN stay NaN
        return s
    raise ValueError(which)


def point_biserial(x: pd.Series, y: pd.Series) -> tuple[float, float, float, float, int]:
    """Return (mean0, mean1, smd, r_pb, n). Pairwise complete."""
    mask = x.notna() & y.notna()
    xv = x[mask].astype(float)
    yv = y[mask].astype(float)
    n = int(mask.sum())
    if n < 30 or yv.nunique() < 2:
        return (np.nan, np.nan, np.nan, np.nan, n)
    m0 = float(xv[yv == 0].mean()) if (yv == 0).any() else np.nan
    m1 = float(xv[yv == 1].mean()) if (yv == 1).any() else np.nan
    sd = float(xv.std(ddof=1))
    smd = (m1 - m0) / sd if sd and sd > 0 else np.nan
    # point-biserial = Pearson corr with binary y
    r = float(np.corrcoef(xv, yv)[0, 1]) if xv.std() > 0 else np.nan
    return (m0, m1, smd, r, n)


def main() -> None:
    df = pd.read_csv(CSV, sep=";")

    y1 = md_binary(df["METABOLIC_DISORDER_T1"], "T1")
    y2 = md_binary(df["METABOLIC_DISORDER_T2"], "T2")
    y3 = md_binary(df["METABOLIC_DISORDER_T3"], "T3")

    # --- Continuous vs MD ---
    cont_rows = []
    for c in ASSOC_CONT:
        if c not in df.columns:
            continue
        # Leakage guard: skip any *T3* continuous if present
        if c.endswith("_T3") or "_T3_" in c:
            continue
        x = pd.to_numeric(df[c], errors="coerce")
        if c.startswith("HBAC"):
            x = x.mask(x <= 0)  # in-memory only
        for label, y in [("MD_T1", y1), ("MD_T2", y2)]:
            m0, m1, smd, r, n = point_biserial(x, y)
            cont_rows.append(
                {
                    "feature": c,
                    "target": label,
                    "n_pairwise": n,
                    "mean_md0": round(m0, 4) if pd.notna(m0) else None,
                    "mean_md1": round(m1, 4) if pd.notna(m1) else None,
                    "smd": round(smd, 4) if pd.notna(smd) else None,
                    "point_biserial_r": round(r, 4) if pd.notna(r) else None,
                    "abs_r": abs(r) if pd.notna(r) else None,
                }
            )
    cont_assoc = pd.DataFrame(cont_rows)
    cont_assoc.to_csv(OUT / "continuous_vs_md_associations.csv", index=False)

    top_t1 = (
        cont_assoc[cont_assoc["target"] == "MD_T1"]
        .dropna(subset=["abs_r"])
        .sort_values("abs_r", ascending=False)
    )
    top_t1.head(25).to_csv(OUT / "top_associations_md_t1.csv", index=False)

    top_t2 = (
        cont_assoc[cont_assoc["target"] == "MD_T2"]
        .dropna(subset=["abs_r"])
        .sort_values("abs_r", ascending=False)
    )
    top_t2.head(25).to_csv(OUT / "top_associations_md_t2.csv", index=False)

    # --- Categorical vs MD_T1 ---
    cat_rows = []
    for c in ASSOC_CAT:
        if c not in df.columns:
            continue
        # For family diabetes: treat NaN as 0 (unchecked/no) only for rate comparison in-memory
        raw = df[c]
        if c in (
            "TYPE2_DIABETES_FAMILY_FATHER",
            "TYPE2_DIABETES_FAMILY_MOTHER",
        ):
            # report both raw and "NaN→0" view
            variants = [
                ("raw", pd.to_numeric(raw, errors="coerce")),
                ("nan_as_0", pd.to_numeric(raw, errors="coerce").fillna(0)),
            ]
        else:
            variants = [("raw", pd.to_numeric(raw, errors="coerce"))]

        for vname, x in variants:
            mask = x.notna() & y1.notna()
            if mask.sum() < 30:
                continue
            # rate of MD among each level (top levels)
            levels = x[mask].value_counts().head(6).index
            for lev in levels:
                sub = mask & (x == lev)
                n_lev = int(sub.sum())
                rate = float(y1[sub].mean()) if n_lev else np.nan
                cat_rows.append(
                    {
                        "feature": c,
                        "coding": vname,
                        "level": lev,
                        "n": n_lev,
                        "md_t1_rate": round(rate, 4) if pd.notna(rate) else None,
                        "md_t1_overall_rate": round(float(y1[mask].mean()), 4),
                        "rate_diff_vs_overall": round(rate - float(y1[mask].mean()), 4)
                        if pd.notna(rate)
                        else None,
                    }
                )
    cat_df = pd.DataFrame(cat_rows)
    cat_df.to_csv(OUT / "categorical_vs_md_t1_rates.csv", index=False)

    # Simple binary rate-diff summary (level==1 vs level==0 where both exist)
    bin_rows = []
    for c in ASSOC_CAT:
        if c not in df.columns:
            continue
        x = pd.to_numeric(df[c], errors="coerce")
        if c.startswith("TYPE2_DIABETES_FAMILY"):
            x = x.fillna(0)
        mask = x.notna() & y1.notna() & x.isin([0, 1, 2])  # GENDER is 1/2
        if mask.sum() < 50:
            continue
        levels = sorted(x[mask].unique())
        if len(levels) != 2:
            # still compute if binary-ish 0/1
            if not set(levels).issubset({0, 1, 2}):
                continue
        rates = {}
        for lev in levels:
            rates[lev] = float(y1[mask & (x == lev)].mean())
        if len(rates) == 2:
            a, b = levels[0], levels[1]
            bin_rows.append(
                {
                    "feature": c,
                    "level_a": a,
                    "level_b": b,
                    "rate_a": round(rates[a], 4),
                    "rate_b": round(rates[b], 4),
                    "rate_diff_b_minus_a": round(rates[b] - rates[a], 4),
                    "n": int(mask.sum()),
                }
            )
    pd.DataFrame(bin_rows).to_csv(OUT / "categorical_binary_rate_diffs_md_t1.csv", index=False)

    # --- Correlation heatmap shortlist (pairwise complete) ---
    cols = [c for c in CORR_SHORTLIST if c in df.columns]
    sub = df[cols].apply(pd.to_numeric, errors="coerce")
    if "HBAC_T1" in sub.columns:
        sub["HBAC_T1"] = sub["HBAC_T1"].mask(sub["HBAC_T1"] <= 0)
    corr = sub.corr(method="pearson", min_periods=30)

    fig, ax = plt.subplots(figsize=(9, 7.5))
    im = ax.imshow(corr.values, cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")
    ax.set_xticks(range(len(cols)))
    ax.set_yticks(range(len(cols)))
    ax.set_xticklabels(cols, rotation=45, ha="right", fontsize=8)
    ax.set_yticklabels(cols, fontsize=8)
    for i in range(len(cols)):
        for j in range(len(cols)):
            val = corr.values[i, j]
            if pd.notna(val):
                ax.text(j, i, f"{val:.2f}", ha="center", va="center", fontsize=6)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    ax.set_title("Stap 5 — correlation heatmap (pairwise complete, raw+mask)")
    fig.tight_layout()
    fig.savefig(OUT / "corr_heatmap_shortlist.png", dpi=140)
    plt.close()
    corr.to_csv(OUT / "corr_shortlist_matrix.csv")

    # --- Bar: top |assoc| with MD_T1 ---
    plot_df = top_t1.head(15)
    fig, ax = plt.subplots(figsize=(9, 6))
    colors = ["#E45756" if r > 0 else "#4C78A8" for r in plot_df["point_biserial_r"]]
    ax.barh(plot_df["feature"], plot_df["point_biserial_r"], color=colors)
    ax.axvline(0, color="black", lw=0.8)
    ax.invert_yaxis()
    ax.set_xlabel("point-biserial r with MD_T1 (in-memory masked)")
    ax.set_title("Stap 5 — top continuous associations with METABOLIC_DISORDER_T1")
    fig.tight_layout()
    fig.savefig(OUT / "md_t1_assoc_top.png", dpi=140)
    plt.close()

    # Prevalence after masking
    def prev(y: pd.Series) -> dict:
        v = y.dropna()
        return {
            "n_valid": int(len(v)),
            "n_pos": int((v == 1).sum()),
            "n_neg": int((v == 0).sum()),
            "prevalence": round(float(v.mean()), 4) if len(v) else None,
        }

    top10 = top_t1.head(10)[
        ["feature", "point_biserial_r", "smd", "mean_md0", "mean_md1", "n_pairwise"]
    ].to_dict(orient="records")

    summary = {
        "n_rows": len(df),
        "target_primary": "METABOLIC_DISORDER_T1",
        "md_t1_after_mask": prev(y1),
        "md_t2_after_mask": prev(y2),
        "md_t3_after_map": prev(y3),
        "top10_features_associated_with_MD_T1": top10,
        "n_continuous_screened": int(top_t1.shape[0]),
        "corr_shortlist": cols,
        "leakage_note": "Do NOT use T3 features (or MD_T3) to predict MD_T1/T2",
        "cleaned_dataset_written": False,
        "masking": "MD T1/T2: −8/−9→NaN in-memory; MD T3: 2→0 in-memory; HBAC≤0 masked for assoc",
    }
    (OUT / "stap5_summary.json").write_text(json.dumps(summary, indent=2, default=str))
    print(json.dumps(summary, indent=2, default=str))
    print("Wrote", OUT)


if __name__ == "__main__":
    main()
