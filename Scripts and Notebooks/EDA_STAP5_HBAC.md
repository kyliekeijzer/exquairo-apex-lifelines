# EDA stap 5 — Features vs **HBAC (HbA1c %)** target

Branch work for Tim / Team 1. Data: `data/raw/exquairo_ai_bootcamp_synth_dataset.csv` (`sep=';'`).

**Primary target:** `HBAC_T1` (continuous %). Values `HBAC <= 0` treated as missing **in-memory only**.  
**Supersedes** the MD-focused stap 5 for modeling shortlist purposes (see pointer in `EDA_STAP5.md`).

Run: `uv run python 'Scripts and Notebooks/eda_stap5_hbac_tim.py'`  
Outputs: `eda_outputs/stap5_hbac/`

## Scope & exclusions (team decision)

**Excluded from feature analysis:** pregnancies, `SLEEP_QUALITY`, `UZ_T1`, `ALT_T1`, `BALB_T1`, `SUMOFALCOHOL`, `SUMOFKCAL`, `METABOLIC_DISORDER_*`, `HB1C_*`.

**Included candidates:** demografie (AGE/GENDER/HEIGHT/WEIGHT/BMI/WAIST), BP (SBP/DBP), labs light (GLU/CHO/HDC/LDC/TGL/BKR), lifestyle binaries (VOLUNTEER/WORK/CYCLE/SMOKING/SPORTS/HTN_MED), diagnoses (fibro/CFS/IBS), family T2DM (NaN→0 in-memory for assoc), scores (LLDS, NSES, LTE_SUM_T1, LDI_SUM_T1).

## Leakage (explicit)

- When predicting **`HBAC_T1`**, use **T1 features only**.
- Do **not** use `HBAC_T2` / `HBAC_T3`, `HB1C_*`, `METABOLIC_DISORDER_*`, or other **T3** columns as predictors for T1.
- No cleaned CSV written; raw file untouched.

## Target descriptive (after ≤0 → NaN)

| Wave | n valid | missing/≤0 | mean % | sd | %>6.5 | %>7.0 |
|------|--------:|-----------:|-------:|---:|------:|------:|
| HBAC_T1 | 17836 | 124 | 5.55 | 0.43 | 1.54% | 0.78% |
| HBAC_T2 | 17341 | 619 | 5.49 | 0.43 | 2.12% | 1.03% |
| HBAC_T3 | 17122 | 838 | 5.64 | 0.51 | 3.84% | 2.21% |

## Continuous features vs HBAC_T1 (Pearson)

Pairwise complete. Top by |r|:

| Rank | Feature | r | n |
|-----:|---------|--:|--:|
| 1 | `GLU_T1` | **0.628** | 17788 |
| 2 | `AGE_T1` | 0.298 | 17836 |
| 3 | `WAIST_T1` | 0.219 | 17836 |
| 4 | `BMI_T1` | 0.205 | 17836 |
| 5 | `WEIGHT_T1` | 0.138 | 17836 |
| 6 | `SBP_T1` | 0.129 | 17829 |
| 7 | `TGL_T1` | 0.127 | 17836 |
| 8 | `CHO_T1` | 0.122 | 17836 |
| 9 | `LDC_T1` | 0.118 | 17836 |
| 10 | `DBP_T1` | 0.088 | 17829 |

Weaker / near-null: HEIGHT (−0.06), LDI (−0.06), LLDS (+0.06), HDC (−0.05), BKR, LTE, NSES (~0).

**Note:** GLU–HBAC is expected clinically (same glycaemic axis). For stap 6 shortlist, treat GLU as strong but partially redundant with the target construct; keep AGE + anthro (prefer WAIST *or* BMI) + BP/lipids as usable signals.

Brief check vs later waves: same ranking holds directionally for `HBAC_T2`/`HBAC_T3` (see `pearson_vs_hbac_all_waves.csv`); do not use those waves as *features* for T1 models.

## Binary / group means vs HBAC_T1

Mean HBAC when feature = 0 vs 1 (GENDER: 1 vs 2). Family diabetes: **NaN→0** only in-memory (assumption: unchecked = no).

| Feature | mean @0 (or G=1) | mean @1 (or G=2) | Δ | n |
|---------|-----------------:|-----------------:|--:|--:|
| `HTN_MED_T1` | 5.52 | 5.77 | **+0.24** | 17783 |
| `WORK_T1` | 5.64 | 5.53 | −0.11 | 15851 |
| `TYPE2_DIABETES_FAMILY_MOTHER` | 5.55 | 5.64 | +0.09 | 17836 |
| `SPORTS_T1` | 5.59 | 5.53 | −0.06 | 16708 |
| `TYPE2_DIABETES_FAMILY_FATHER` | 5.55 | 5.61 | +0.06 | 17836 |
| `VOLUNTEER_T1` | 5.54 | 5.59 | +0.04 | 14941 |
| `DIAG_IBS_ROME3` | 5.56 | 5.52 | −0.04 | 15312 |
| `SMOKING` | 5.56 | 5.52 | −0.04 | 17599 |
| `GENDER` | 5.57 (1) | 5.54 (2) | −0.03 | 17836 |

Diagnoses fibro/CFS and cycle-commute: negligible Δ.

## Lab / anthro collinearity

Pearson among continuous shortlist + HBAC_T1 (`lab_corr_heatmap.png`, `lab_corr_matrix.csv`).

**High |r| ≥ 0.5 pairs (flag for stap 6):**

| Pair | r |
|------|--:|
| `CHO_T1`–`LDC_T1` | **0.92** |
| `BMI_T1`–`WAIST_T1` | **0.81** |
| `SBP_T1`–`DBP_T1` | **0.69** |
| `GLU_T1`–`HBAC_T1` | **0.63** |

→ Prefer one of CHO/LDC; one of BMI/WAIST; optionally one BP measure or both with care.

## Longitudinal HbA1c (T1→T2→T3)

Cutoffs: **>7.0%** (Tim prior Sankeys) and optional **>6.5%**. No MD required in these flows. Counts in `hbac_longitudinal_counts.csv`; stacked bars: `hbac_longitudinal_stacked.png`. Prior presentation Sankeys live under `/workspace/outbox/cursus/sankey-presentatie/` (reference only).

| Cutoff | high T1 | high T2 | high T3 | path high→high→high | path low→low→low |
|-------:|--------:|--------:|--------:|--------------------:|-----------------:|
| >7.0% | 140 | 179 | 379 | 57 | 16041 |
| >6.5% | 275 | 367 | 658 | 156 | 15766 |

**Finding:** high HbA1c is rare at T1 but **grows over waves** (≈2.7× from T1→T3 at 7%; ≈2.4× at 6.5%). Most of the cohort stays low→low→low; of T1-high at 7%, 84/140 remain high at T2; many new highs appear later (e.g. low→high T1→T2: 95 at 7%). Persistence of the high state is incomplete — useful for longitudinal modeling later, but **not** as T1 predictors.

## Figures / tables

- `eda_outputs/stap5_hbac/pearson_vs_hbac_t1.csv`
- `eda_outputs/stap5_hbac/group_means_vs_hbac_t1.csv`
- `eda_outputs/stap5_hbac/lab_corr_matrix.csv` + `lab_corr_heatmap.png`
- `eda_outputs/stap5_hbac/top_assoc_bar.png`
- `eda_outputs/stap5_hbac/boxplots_key_features_vs_hbac.png`
- `eda_outputs/stap5_hbac/scatter_bmi_glu_vs_hbac.png`
- `eda_outputs/stap5_hbac/hbac_longitudinal_counts.csv` + `hbac_longitudinal_stacked.png`
- `eda_outputs/stap5_hbac/stap5_hbac_summary.json`

## Top usable signals for stap 6 shortlist

1. **`GLU_T1`** — strongest continuous (glycaemic; watch redundancy with target)
2. **`AGE_T1`** — clear positive assoc
3. **Anthro:** `WAIST_T1` *or* `BMI_T1` (collinear; waist slightly stronger here)
4. **`SBP_T1`** (and/or DBP; collinear pair)
5. **Lipids:** `TGL_T1` and one of `CHO_T1`/`LDC_T1`
6. **Binaries:** `HTN_MED_T1`, family T2DM (mother/father, with NaN→0 noted), optionally `WORK_T1` / `SPORTS_T1`

## Niet gedaan (bewust)

- Geen cleaned CSV / geen mutatie van `data/raw`
- Geen MD in longitudinal plots
- Geen multivariate model / shortlist freeze (stap 6+)
