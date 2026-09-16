"""EDA stap 3 — univariate (raw, no cleaning).

Run: uv run python 'Scripts and Notebooks/eda_stap3_tim.py'
Outputs: Scripts and Notebooks/eda_outputs/stap3/
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
OUT = Path(__file__).resolve().parent / "eda_outputs" / "stap3"
FIG = OUT / "figures"
OUT.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)

CONT = [
    "AGE_T1",
    "BMI_T1",
    "BMI_T2",
    "WAIST_T1",
    "WEIGHT_T1",
    "HEIGHT_T1",
    "SBP_T1",
    "DBP_T1",
    "HBAC_T1",
    "HBAC_T2",
    "HBAC_T3",
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
]
BINISH = [
    "GENDER",
    "SMOKING",
    "SPORTS_T1",
    "WORK_T1",
    "CYCLE_COMMUTE_T1",
    "BURNOUT_T1",
    "DEPRESSION_T1",
    "HTN_MED_T1",
    "OSTEOARTHRITIS",
    "METABOLIC_DISORDER_T1",
    "METABOLIC_DISORDER_T2",
    "METABOLIC_DISORDER_T3",
    "EDUCATION_LOWER_T1",
    "SLEEP_QUALITY",
    "VOLUNTEER_T1",
]


def main() -> None:
    df = pd.read_csv(CSV, sep=";")
    cont = [c for c in CONT if c in df.columns]
    binish = [c for c in BINISH if c in df.columns]

    rows = []
    for c in cont:
        s = pd.to_numeric(df[c], errors="coerce")
        q = s.quantile([0, 0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99, 1]).to_dict()
        note = ""
        if c.startswith("HBAC") and (s.dropna() <= 0).any():
            note = "≤0 unlikely for HbA1c % — treat as missing"
        elif s.notna().any() and s.max() > s.quantile(0.99) * 3:
            note = "extreme max vs p99 — check outliers"
        rows.append(
            {
                "variable": c,
                "n": int(s.notna().sum()),
                "pct_nan": round(100 * s.isna().mean(), 2),
                "mean": round(float(s.mean()), 3) if s.notna().any() else None,
                "std": round(float(s.std()), 3) if s.notna().any() else None,
                "min": q.get(0.0),
                "p01": q.get(0.01),
                "p05": q.get(0.05),
                "p25": q.get(0.25),
                "p50": q.get(0.5),
                "p75": q.get(0.75),
                "p95": q.get(0.95),
                "p99": q.get(0.99),
                "max": q.get(1.0),
                "n_le0": int((s.dropna() <= 0).sum()),
                "cleaning_note": note,
            }
        )
    cont_sum = pd.DataFrame(rows)
    cont_sum.to_csv(OUT / "univariate_continuous_summary.csv", index=False)

    cat_rows = []
    for c in binish:
        vc = df[c].value_counts(dropna=False)
        for val, n in vc.items():
            cat_rows.append(
                {
                    "variable": c,
                    "value": val,
                    "n": int(n),
                    "pct": round(100 * n / len(df), 2),
                }
            )
    pd.DataFrame(cat_rows).to_csv(OUT / "univariate_categorical_counts.csv", index=False)

    n = len(cont)
    ncols = 4
    nrows = int(np.ceil(n / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(14, 3.2 * nrows))
    axes = np.array(axes).reshape(-1)
    for i, c in enumerate(cont):
        ax = axes[i]
        s = pd.to_numeric(df[c], errors="coerce").dropna()
        ax.hist(s, bins=40, color="#4C78A8", edgecolor="white", linewidth=0.3)
        ax.set_title(c, fontsize=9)
        ax.tick_params(labelsize=7)
    for j in range(i + 1, len(axes)):
        axes[j].axis("off")
    fig.suptitle("Stap 3 — univariate histograms (raw, no cleaning)", fontsize=12)
    fig.tight_layout()
    fig.savefig(FIG / "histograms_continuous.png", dpi=140)
    plt.close()

    labs = [
        c
        for c in [
            "HBAC_T1",
            "HBAC_T2",
            "HBAC_T3",
            "BMI_T1",
            "WAIST_T1",
            "SBP_T1",
            "GLU_T1",
            "CHO_T1",
            "TGL_T1",
        ]
        if c in df.columns
    ]
    fig, axes = plt.subplots(1, len(labs), figsize=(2.2 * len(labs), 4))
    for ax, c in zip(axes, labs):
        s = pd.to_numeric(df[c], errors="coerce").dropna()
        ax.boxplot(s, orientation="vertical", widths=0.6)
        ax.set_title(c, fontsize=8)
        ax.tick_params(labelsize=7)
    fig.suptitle("Stap 3 — boxplots key labs/anthro (raw)", fontsize=11)
    fig.tight_layout()
    fig.savefig(FIG / "boxplots_key.png", dpi=140)
    plt.close()

    fig, axes = plt.subplots(3, 5, figsize=(14, 8))
    axes = axes.reshape(-1)
    for i, c in enumerate(binish):
        ax = axes[i]
        vc = df[c].value_counts(dropna=False).head(8)
        ax.bar([str(x) for x in vc.index], vc.values, color="#F58518")
        ax.set_title(c, fontsize=8)
        ax.tick_params(axis="x", labelsize=6, rotation=45)
        ax.tick_params(axis="y", labelsize=6)
    for j in range(i + 1, len(axes)):
        axes[j].axis("off")
    fig.suptitle("Stap 3 — categorical / binary counts (raw)", fontsize=11)
    fig.tight_layout()
    fig.savefig(FIG / "bars_categorical.png", dpi=140)
    plt.close()

    flags = cont_sum[cont_sum["cleaning_note"].astype(str).str.len() > 0][
        ["variable", "min", "max", "n_le0", "cleaning_note"]
    ]
    flags.to_csv(OUT / "flags_for_cleaning_colleague.csv", index=False)
    miss = cont_sum.nlargest(10, "pct_nan")[["variable", "pct_nan"]]
    summary = {
        "n_rows": len(df),
        "n_continuous_profiled": len(cont),
        "n_categorical_profiled": len(binish),
        "top_missing_continuous": miss.to_dict(orient="records"),
        "cleaning_flags": flags.to_dict(orient="records"),
    }
    (OUT / "stap3_summary.json").write_text(json.dumps(summary, indent=2, default=str))
    print(json.dumps(summary, indent=2, default=str))
    print("Wrote", OUT)


if __name__ == "__main__":
    main()
