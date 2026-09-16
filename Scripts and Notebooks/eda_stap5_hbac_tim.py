"""EDA stap 5 — associations with HBAC (HbA1c %) as TARGET.

Run: uv run python 'Scripts and Notebooks/eda_stap5_hbac_tim.py'
Outputs: Scripts and Notebooks/eda_outputs/stap5_hbac/

Primary target: HBAC_T1 (continuous %). HBAC <= 0 treated as missing (in-memory).
Does NOT write cleaned CSV. Do NOT use HBAC_T2/T3 or other T3 as features for HBAC_T1.
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
OUT = Path(__file__).resolve().parent / "eda_outputs" / "stap5_hbac"
OUT.mkdir(parents=True, exist_ok=True)

# Continuous feature candidates vs HBAC_T1 (team shortlist; excludes ALT/UZ/BALB etc.)
CONT_FEATURES = [
    "AGE_T1",
    "HEIGHT_T1",
    "WEIGHT_T1",
    "BMI_T1",
    "WAIST_T1",
    "SBP_T1",
    "DBP_T1",
    "GLU_T1",
    "CHO_T1",
    "HDC_T1",
    "LDC_T1",
    "TGL_T1",
    "BKR_T1",
    "LLDS",
    "NSES",
    "LTE_SUM_T1",
    "LDI_SUM_T1",
]

# Lab + anthro shortlist for correlation matrix (incl. target)
LAB_CORR_COLS = [
    "AGE_T1",
    "BMI_T1",
    "WAIST_T1",
    "SBP_T1",
    "DBP_T1",
    "GLU_T1",
    "CHO_T1",
    "HDC_T1",
    "LDC_T1",
    "TGL_T1",
    "BKR_T1",
    "HBAC_T1",
]

# Binary / 0-1 features for group means of HBAC
BINARY_FEATURES = [
    "GENDER",  # coded 1/2 — treat as two-level
    "VOLUNTEER_T1",
    "WORK_T1",
    "CYCLE_COMMUTE_T1",
    "SMOKING",
    "SPORTS_T1",
    "HTN_MED_T1",
    "DIAG_FIBROMYALGIA_ACR",
    "DIAG_CFS_CDC",
    "DIAG_IBS_ROME3",
    "TYPE2_DIABETES_FAMILY_FATHER",
    "TYPE2_DIABETES_FAMILY_MOTHER",
]

FAMILY_COLS = (
    "TYPE2_DIABETES_FAMILY_FATHER",
    "TYPE2_DIABETES_FAMILY_MOTHER",
)

CUTOFFS = (7.0, 6.5)


def hbac_valid(series: pd.Series) -> pd.Series:
    """Numeric HBAC; values <= 0 → NaN (in-memory only)."""
    s = pd.to_numeric(series, errors="coerce")
    return s.mask(s <= 0)


def pearson_pair(x: pd.Series, y: pd.Series) -> tuple[float, int]:
    mask = x.notna() & y.notna()
    n = int(mask.sum())
    if n < 30:
        return (np.nan, n)
    xv = x[mask].astype(float)
    yv = y[mask].astype(float)
    if xv.std(ddof=1) == 0 or yv.std(ddof=1) == 0:
        return (np.nan, n)
    r = float(np.corrcoef(xv, yv)[0, 1])
    return (r, n)


def high_low_label(s: pd.Series, cutoff: float) -> pd.Series:
    """Return 'high' / 'low' / 'missing' for HBAC vs cutoff."""
    out = pd.Series("missing", index=s.index, dtype=object)
    valid = s.notna()
    out.loc[valid & (s > cutoff)] = "high"
    out.loc[valid & (s <= cutoff)] = "low"
    return out


def transition_counts(df: pd.DataFrame, cutoff: float) -> pd.DataFrame:
    t1 = high_low_label(hbac_valid(df["HBAC_T1"]), cutoff)
    t2 = high_low_label(hbac_valid(df["HBAC_T2"]), cutoff)
    t3 = high_low_label(hbac_valid(df["HBAC_T3"]), cutoff)
    rows = []
    # Marginal counts per wave
    for wave, lab in [("T1", t1), ("T2", t2), ("T3", t3)]:
        vc = lab.value_counts()
        for state in ("high", "low", "missing"):
            rows.append(
                {
                    "cutoff": cutoff,
                    "kind": "marginal",
                    "from_wave": wave,
                    "to_wave": wave,
                    "from_state": state,
                    "to_state": state,
                    "n": int(vc.get(state, 0)),
                }
            )
    # Pairwise transitions T1→T2 and T2→T3
    for (w_from, a), (w_to, b) in [(("T1", t1), ("T2", t2)), (("T2", t2), ("T3", t3))]:
        ct = pd.crosstab(a, b)
        for fs in ("high", "low", "missing"):
            for ts in ("high", "low", "missing"):
                rows.append(
                    {
                        "cutoff": cutoff,
                        "kind": "transition",
                        "from_wave": w_from,
                        "to_wave": w_to,
                        "from_state": fs,
                        "to_state": ts,
                        "n": int(ct.loc[fs, ts]) if fs in ct.index and ts in ct.columns else 0,
                    }
                )
    # Full path T1→T2→T3 (high/low/missing)
    path = t1.astype(str) + "→" + t2.astype(str) + "→" + t3.astype(str)
    for p, n in path.value_counts().items():
        parts = p.split("→")
        rows.append(
            {
                "cutoff": cutoff,
                "kind": "path_t1_t2_t3",
                "from_wave": "T1",
                "to_wave": "T3",
                "from_state": parts[0],
                "to_state": "→".join(parts[1:]),
                "n": int(n),
                "path": p,
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    df = pd.read_csv(CSV, sep=";")
    y1 = hbac_valid(df["HBAC_T1"])
    y2 = hbac_valid(df["HBAC_T2"])
    y3 = hbac_valid(df["HBAC_T3"])

    # --- Pearson continuous vs HBAC_T1 ---
    pearson_rows = []
    for c in CONT_FEATURES:
        if c not in df.columns:
            continue
        x = pd.to_numeric(df[c], errors="coerce")
        r, n = pearson_pair(x, y1)
        pearson_rows.append(
            {
                "feature": c,
                "pearson_r": round(r, 4) if pd.notna(r) else None,
                "abs_r": abs(r) if pd.notna(r) else None,
                "n": n,
                "target": "HBAC_T1",
            }
        )
        # brief T2/T3 if useful
        for label, y in [("HBAC_T2", y2), ("HBAC_T3", y3)]:
            r2, n2 = pearson_pair(x, y)
            pearson_rows.append(
                {
                    "feature": c,
                    "pearson_r": round(r2, 4) if pd.notna(r2) else None,
                    "abs_r": abs(r2) if pd.notna(r2) else None,
                    "n": n2,
                    "target": label,
                }
            )
    pearson_df = pd.DataFrame(pearson_rows)
    pearson_t1 = (
        pearson_df[pearson_df["target"] == "HBAC_T1"]
        .dropna(subset=["abs_r"])
        .sort_values("abs_r", ascending=False)
    )
    pearson_t1.to_csv(OUT / "pearson_vs_hbac_t1.csv", index=False)
    pearson_df.to_csv(OUT / "pearson_vs_hbac_all_waves.csv", index=False)

    # --- Group means for binaries ---
    group_rows = []
    for c in BINARY_FEATURES:
        if c not in df.columns:
            continue
        x = pd.to_numeric(df[c], errors="coerce")
        note = ""
        if c in FAMILY_COLS:
            x = x.fillna(0)
            note = "NaN→0 (in-memory assumption)"
        # GENDER is 1/2
        levels = sorted(x.dropna().unique())
        if c == "GENDER":
            # report mean HBAC for 1 vs 2
            mask = x.notna() & y1.notna()
            if mask.sum() < 50:
                continue
            m_by = {float(lev): float(y1[mask & (x == lev)].mean()) for lev in levels}
            n_by = {float(lev): int((mask & (x == lev)).sum()) for lev in levels}
            if len(m_by) == 2:
                a, b = levels[0], levels[1]
                group_rows.append(
                    {
                        "feature": c,
                        "level_0_or_a": a,
                        "level_1_or_b": b,
                        "mean_hbac_a": round(m_by[float(a)], 4),
                        "mean_hbac_b": round(m_by[float(b)], 4),
                        "delta_b_minus_a": round(m_by[float(b)] - m_by[float(a)], 4),
                        "n_a": n_by[float(a)],
                        "n_b": n_by[float(b)],
                        "n_total": int(mask.sum()),
                        "note": "GENDER 1 vs 2",
                    }
                )
            continue
        # Expect 0/1
        mask = x.notna() & y1.notna() & x.isin([0, 1])
        if mask.sum() < 50:
            continue
        m0 = float(y1[mask & (x == 0)].mean()) if (mask & (x == 0)).any() else np.nan
        m1 = float(y1[mask & (x == 1)].mean()) if (mask & (x == 1)).any() else np.nan
        n0 = int((mask & (x == 0)).sum())
        n1 = int((mask & (x == 1)).sum())
        group_rows.append(
            {
                "feature": c,
                "level_0_or_a": 0,
                "level_1_or_b": 1,
                "mean_hbac_a": round(m0, 4) if pd.notna(m0) else None,
                "mean_hbac_b": round(m1, 4) if pd.notna(m1) else None,
                "delta_b_minus_a": round(m1 - m0, 4) if pd.notna(m0) and pd.notna(m1) else None,
                "n_a": n0,
                "n_b": n1,
                "n_total": int(mask.sum()),
                "note": note,
            }
        )
    group_df = pd.DataFrame(group_rows)
    group_df["abs_delta"] = group_df["delta_b_minus_a"].abs()
    group_df = group_df.sort_values("abs_delta", ascending=False)
    group_df.to_csv(OUT / "group_means_vs_hbac_t1.csv", index=False)

    # --- Lab correlation matrix ---
    cols = [c for c in LAB_CORR_COLS if c in df.columns]
    sub = df[cols].apply(pd.to_numeric, errors="coerce")
    sub["HBAC_T1"] = hbac_valid(sub["HBAC_T1"])
    corr = sub.corr(method="pearson", min_periods=30)
    corr.to_csv(OUT / "lab_corr_matrix.csv")

    # High |corr| pairs (exclude diagonal, upper triangle)
    high_pairs = []
    for i, a in enumerate(cols):
        for j, b in enumerate(cols):
            if j <= i:
                continue
            val = corr.loc[a, b]
            if pd.notna(val) and abs(val) >= 0.5:
                high_pairs.append({"a": a, "b": b, "r": round(float(val), 4)})
    high_pairs = sorted(high_pairs, key=lambda d: -abs(d["r"]))

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
    ax.set_title("Stap 5 HBAC — lab/anthro Pearson corr (+ HBAC_T1)")
    fig.tight_layout()
    fig.savefig(OUT / "lab_corr_heatmap.png", dpi=140)
    plt.close()

    # --- Top association bar (|r| continuous + |delta| binary combined visual) ---
    # Primary: top |r| continuous
    plot_df = pearson_t1.head(12).copy()
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.5))
    ax = axes[0]
    colors = ["#E45756" if r > 0 else "#4C78A8" for r in plot_df["pearson_r"]]
    ax.barh(plot_df["feature"], plot_df["pearson_r"], color=colors)
    ax.axvline(0, color="black", lw=0.8)
    ax.invert_yaxis()
    ax.set_xlabel("Pearson r with HBAC_T1")
    ax.set_title("Top continuous |r| vs HBAC_T1")

    ax2 = axes[1]
    gplot = group_df.head(10)
    colors2 = ["#E45756" if d > 0 else "#4C78A8" for d in gplot["delta_b_minus_a"]]
    labels = [
        f"{f}" + (" (G)" if f == "GENDER" else "")
        for f in gplot["feature"]
    ]
    ax2.barh(labels, gplot["delta_b_minus_a"], color=colors2)
    ax2.axvline(0, color="black", lw=0.8)
    ax2.invert_yaxis()
    ax2.set_xlabel("Δ mean HBAC (level_b − level_a)")
    ax2.set_title("Top binary Δ mean HBAC_T1")
    fig.tight_layout()
    fig.savefig(OUT / "top_assoc_bar.png", dpi=140)
    plt.close()

    # --- Visuals: boxplots HBAC by key binaries + scatter BMI/GLU ---
    key_bins = [
        c
        for c in [
            "SMOKING",
            "WORK_T1",
            "SPORTS_T1",
            "HTN_MED_T1",
            "TYPE2_DIABETES_FAMILY_MOTHER",
            "TYPE2_DIABETES_FAMILY_FATHER",
        ]
        if c in df.columns
    ]
    fig, axes = plt.subplots(2, 3, figsize=(12, 8))
    axes = axes.ravel()
    for i, c in enumerate(key_bins):
        ax = axes[i]
        x = pd.to_numeric(df[c], errors="coerce")
        if c in FAMILY_COLS:
            x = x.fillna(0)
        plot_data = pd.DataFrame({"group": x, "hbac": y1}).dropna()
        plot_data = plot_data[plot_data["group"].isin([0, 1])]
        groups = [plot_data.loc[plot_data["group"] == g, "hbac"].values for g in (0, 1)]
        bp = ax.boxplot(groups, tick_labels=["0", "1"], showfliers=False, patch_artist=True)
        for patch in bp["boxes"]:
            patch.set_facecolor("#9ecae1")
        ax.set_title(c.replace("TYPE2_DIABETES_FAMILY_", "FAM_"), fontsize=9)
        ax.set_ylabel("HBAC_T1 %" if i % 3 == 0 else "")
    for j in range(len(key_bins), len(axes)):
        axes[j].axis("off")
    fig.suptitle("HBAC_T1 by binary groups (outliers hidden)", y=1.01)
    fig.tight_layout()
    fig.savefig(OUT / "boxplots_key_features_vs_hbac.png", dpi=140, bbox_inches="tight")
    plt.close()

    # Extra scatter panel: BMI & GLU vs HBAC
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))
    for ax, feat, color in zip(axes, ["BMI_T1", "GLU_T1"], ["#4C78A8", "#E45756"]):
        x = pd.to_numeric(df[feat], errors="coerce")
        mask = x.notna() & y1.notna()
        # hexbin for density
        hb = ax.hexbin(x[mask], y1[mask], gridsize=40, cmap="Blues", mincnt=1)
        ax.set_xlabel(feat)
        ax.set_ylabel("HBAC_T1 %")
        r, n = pearson_pair(x, y1)
        ax.set_title(f"{feat} vs HBAC_T1 (r={r:.3f}, n={n})")
        fig.colorbar(hb, ax=ax, fraction=0.046)
    fig.tight_layout()
    fig.savefig(OUT / "scatter_bmi_glu_vs_hbac.png", dpi=140)
    plt.close()

    # --- Longitudinal high/low counts ---
    long_frames = [transition_counts(df, c) for c in CUTOFFS]
    long_df = pd.concat(long_frames, ignore_index=True)
    long_df.to_csv(OUT / "hbac_longitudinal_counts.csv", index=False)

    # Stacked bar: marginal high/low/missing per wave for both cutoffs
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5), sharey=True)
    for ax, cutoff in zip(axes, CUTOFFS):
        marg = long_df[(long_df["cutoff"] == cutoff) & (long_df["kind"] == "marginal")]
        waves = ["T1", "T2", "T3"]
        highs = [int(marg[(marg["from_wave"] == w) & (marg["from_state"] == "high")]["n"].iloc[0]) for w in waves]
        lows = [int(marg[(marg["from_wave"] == w) & (marg["from_state"] == "low")]["n"].iloc[0]) for w in waves]
        miss = [int(marg[(marg["from_wave"] == w) & (marg["from_state"] == "missing")]["n"].iloc[0]) for w in waves]
        x = np.arange(len(waves))
        ax.bar(x, lows, label="low", color="#4C78A8")
        ax.bar(x, highs, bottom=lows, label="high", color="#E45756")
        ax.bar(x, miss, bottom=np.array(lows) + np.array(highs), label="missing", color="#bbbbbb")
        ax.set_xticks(x)
        ax.set_xticklabels(waves)
        ax.set_title(f"HbA1c high vs low (cutoff >{cutoff}%)")
        ax.set_ylabel("n participants")
        # annotate high counts
        for i, h in enumerate(highs):
            ax.text(i, lows[i] + h / 2, str(h), ha="center", va="center", fontsize=8, color="white", fontweight="bold")
        ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "hbac_longitudinal_stacked.png", dpi=140)
    plt.close()

    # Simple transition flow table highlight (T1→T2→T3 persistence)
    def path_summary(cutoff: float) -> dict:
        paths = long_df[(long_df["cutoff"] == cutoff) & (long_df["kind"] == "path_t1_t2_t3")]
        # persistence high
        hh_h = paths[paths["path"] == "high→high→high"]["n"].sum() if not paths.empty else 0
        ll_l = paths[paths["path"] == "low→low→low"]["n"].sum() if not paths.empty else 0
        # new high at T3 from low
        lh = int(
            paths[paths["path"].str.startswith("low→") & paths["path"].str.endswith("→high")]["n"].sum()
        ) if "path" in paths.columns else 0
        marg = long_df[(long_df["cutoff"] == cutoff) & (long_df["kind"] == "marginal")]
        return {
            "cutoff": cutoff,
            "n_high_t1": int(marg[(marg["from_wave"] == "T1") & (marg["from_state"] == "high")]["n"].iloc[0]),
            "n_high_t2": int(marg[(marg["from_wave"] == "T2") & (marg["from_state"] == "high")]["n"].iloc[0]),
            "n_high_t3": int(marg[(marg["from_wave"] == "T3") & (marg["from_state"] == "high")]["n"].iloc[0]),
            "path_high_high_high": int(hh_h),
            "path_low_low_low": int(ll_l),
            "paths_ending_high_from_low_t1": lh,
        }

    long_summaries = [path_summary(c) for c in CUTOFFS]

    # Target descriptive
    def y_desc(y: pd.Series) -> dict:
        v = y.dropna()
        return {
            "n_valid": int(len(v)),
            "n_missing_or_le0": int(y.isna().sum()),
            "mean": round(float(v.mean()), 4) if len(v) else None,
            "sd": round(float(v.std(ddof=1)), 4) if len(v) else None,
            "pct_gt_65": round(float((v > 6.5).mean()), 4) if len(v) else None,
            "pct_gt_70": round(float((v > 7.0).mean()), 4) if len(v) else None,
        }

    top5 = pearson_t1.head(5)[["feature", "pearson_r", "n"]].to_dict(orient="records")
    top_bin = group_df.head(5)[
        ["feature", "mean_hbac_a", "mean_hbac_b", "delta_b_minus_a", "n_total", "note"]
    ].to_dict(orient="records")

    summary = {
        "n_rows": len(df),
        "target_primary": "HBAC_T1",
        "target_unit": "%",
        "hbac_t1": y_desc(y1),
        "hbac_t2": y_desc(y2),
        "hbac_t3": y_desc(y3),
        "top5_pearson_vs_HBAC_T1": top5,
        "top5_binary_delta_vs_HBAC_T1": top_bin,
        "high_corr_pairs_abs_ge_0_5": high_pairs,
        "longitudinal": long_summaries,
        "excluded_from_feature_analysis": [
            "pregnancies/PREGNANCIES",
            "SLEEP_QUALITY",
            "UZ_T1",
            "ALT_T1",
            "BALB_T1",
            "SUMOFALCOHOL",
            "SUMOFKCAL",
            "METABOLIC_DISORDER_*",
            "HB1C_*",
        ],
        "family_nan_as_0": True,
        "leakage_note": (
            "Do NOT use HBAC_T2/T3, HB1C_*, METABOLIC_DISORDER_*, or other T3 features "
            "as predictors when modeling HBAC_T1. T1 features only for T1 target."
        ),
        "cleaned_dataset_written": False,
        "masking": "HBAC <= 0 → NaN in-memory only; family diabetes NaN→0 for association only",
    }
    (OUT / "stap5_hbac_summary.json").write_text(json.dumps(summary, indent=2, default=str))
    print(json.dumps(summary, indent=2, default=str))
    print("Wrote", OUT)


if __name__ == "__main__":
    main()
