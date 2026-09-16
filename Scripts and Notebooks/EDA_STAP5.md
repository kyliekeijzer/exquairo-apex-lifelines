# EDA stap 5 — Bivariate / target (raw + in-memory masking)

Branch work for Tim / Team 1. Data: `data/raw/exquairo_ai_bootcamp_synth_dataset.csv` (`sep=';'`).

**Scope:** associaties met metabolic disorder op **ruwe** data. Masking alleen in-memory:
- MD T1/T2: −8/−9 → NaN; analyse op 0/1
- MD T3: 2→0 voor binary (niet opgeslagen)
- HBAC ≤0 → gemaskeerd voor assoc

**Leakage:** gebruik **geen** T3-features (noch MD_T3) om MD_T1/T2 te voorspellen.

Run: `uv run python 'Scripts and Notebooks/eda_stap5_tim.py'`

## Target prevalentie (na in-memory mask)

| Target | n valid | n pos | prevalence |
|--------|--------:|------:|-----------:|
| `METABOLIC_DISORDER_T1` | 17917 | 452 | **2.52%** |
| `METABOLIC_DISORDER_T2` | 17911 | 731 | **4.08%** |
| `METABOLIC_DISORDER_T3` (2→0) | 14592 | 331 | **2.27%** |

Primary focus: **MD_T1** (ook T2 gerapporteerd).

## Top continuous associations with MD_T1

Point-biserial *r* + standardized mean difference (SMD = (mean₁−mean₀)/sd). Pairwise complete.

| Rank | Feature | r (pb) | SMD | mean MD=0 | mean MD=1 |
|-----:|---------|-------:|----:|----------:|----------:|
| 1 | `GLU_T1` | 0.596 | 3.79 | 4.92 | 7.80 |
| 2 | `HB1C_T1` | 0.516 | 3.25 | 36.77 | 51.76 |
| 3 | `HBAC_T1` | 0.505 | 3.21 | 5.51 | 6.85 |
| 4 | `HBAC_T2` | 0.492 | 3.16 | 5.45 | 6.81 |
| 5 | `WAIST_T1` | 0.180 | 1.15 | 89.51 | 103.11 |
| 6 | `BMI_T1` | 0.168 | 1.07 | 25.75 | 30.08 |
| 7 | `BMI_T2` | 0.139 | 0.89 | 25.90 | 29.58 |
| 8 | `WEIGHT_T1` | 0.129 | 0.82 | 78.81 | 90.82 |
| 9 | `AGE_T1` | 0.124 | 0.79 | 46.35 | 55.38 |
| 10 | `UZ_T1` | 0.093 | 0.61 | 0.29 | 0.33 |

**Interpretatie (kort):** glucose / HbA1c domineren (deels definitie-gerelateerd aan metabolic disorder — feature-keuze later kritisch). Anthro (waist, BMI, weight, age) matig positief. Labs met ~49% missing (`UZ`) zwakkere *r* op kleinere n.

## Categorical / binary vs MD_T1 (rate differences)

| Feature | contrast | rate diff (grof) | note |
|---------|----------|-----------------:|------|
| `HTN_MED_T1` | 1 vs 0 | **+9.7 pp** | sterkste binary signal |
| `TYPE2_DIABETES_FAMILY_MOTHER` | 1 vs 0 (NaN→0) | +3.2 pp | past bij familie-aanname |
| `TYPE2_DIABETES_FAMILY_FATHER` | 1 vs 0 (NaN→0) | +2.5 pp | idem |
| `WORK_T1` | 1 vs 0 | −2.8 pp | werkenden iets lager MD-rate |
| `OSTEOARTHRITIS` | 1 vs 0 | +2.2 pp | |
| `EDUCATION_LOWER_T1` | 1 vs 0 | +2.1 pp | |
| `SPORTS_T1` | 1 vs 0 | −1.2 pp | sport iets lager |
| `GENDER` | 2 vs 1 | −1.1 pp | vrouwen iets lager |

## Correlation shortlist (pairwise complete)

Features: AGE, BMI, WAIST, SBP, DBP, HBAC, GLU, CHO, HDC, LDC, TGL, ALT (T1).  
Figuur: `corr_heatmap_shortlist.png`. Verwachte clusters: BMI–WAIST, SBP–DBP, lipids (CHO/LDC/TGL), HBAC–GLU.

## Figuren / tabellen
- `eda_outputs/stap5/continuous_vs_md_associations.csv`
- `eda_outputs/stap5/top_associations_md_t1.csv` / `_md_t2.csv`
- `eda_outputs/stap5/categorical_vs_md_t1_rates.csv`
- `eda_outputs/stap5/categorical_binary_rate_diffs_md_t1.csv`
- `eda_outputs/stap5/corr_heatmap_shortlist.png`
- `eda_outputs/stap5/md_t1_assoc_top.png`
- `eda_outputs/stap5/stap5_summary.json`

## Niet gedaan (bewust)
- Geen cleaned CSV
- Geen T3-features in assoc-screen voor T1/T2
- Geen multivariate model / shortlist freeze (stap 6+)
