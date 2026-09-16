# EDA stap 3 — Univariate (raw, geen cleaning)

Branch work for Tim / Team 1. Data: `data/raw/exquairo_ai_bootcamp_synth_dataset.csv` (`sep=';'`).

**Scope:** alleen verdelingen + flags. Cleaning (missings, −8/−9, outliers) blijft bij collega.

Run: `uv run python 'Scripts and Notebooks/eda_stap3_tim.py'`

## Wat is geprofileerd
- **27 continuous** (anthro, labs, sums, scores)
- **15 categorical/binary** (incl. MD targets)
- Rijen: **17960**

## Key continuous (ruw)

| Variable | % NaN | mean | median | range |
|----------|------:|-----:|-------:|------|
| `AGE_T1` | 0.0% | 46.569 | 47.0 | 18.0–80.0 |
| `BMI_T1` | 0.0% | 25.859 | 25.3 | 13.4–56.6 |
| `HBAC_T1` | 0.69% | 5.552 | 5.5 | 3.9–16.4 |
| `HBAC_T2` | 3.44% | 5.491 | 5.5 | 0.0–13.6 |
| `HBAC_T3` | 4.67% | 5.643 | 5.6 | 3.5–15.0 |
| `SBP_T1` | 0.04% | 125.336 | 124.0 | 84.0–223.0 |
| `GLU_T1` | 0.66% | 5.003 | 4.9 | 2.7–20.5 |
| `ALT_T1` | 49.49% | 23.037 | 19.0 | 1.0–451.0 |

## Top missing (continuous shortlist)

| Variable | % NaN |
|----------|------:|
| `ALT_T1` | 49.49% |
| `UZ_T1` | 49.49% |
| `BALB_T1` | 49.37% |
| `NSES` | 45.14% |
| `SUMOFALCOHOL` | 34.85% |
| `SUMOFKCAL` | 34.78% |
| `HB1C_T1` | 21.45% |
| `LLDS` | 11.62% |
| `HBAC_T3` | 4.67% |
| `HBAC_T2` | 3.44% |

## Flags voor cleaning-collega

| Variable | min | max | n≤0 | Note |
|----------|----:|----:|----:|------|
| `HBAC_T2` | 0.0 | 13.6 | 2 | ≤0 unlikely for HbA1c % — treat as missing |
| `HB1C_T1` | 19.0 | 155.0 | 0 | extreme max vs p99 — check outliers |
| `TGL_T1` | 0.2 | 12.56 | 0 | extreme max vs p99 — check outliers |
| `ALT_T1` | 1.0 | 451.0 | 0 | extreme max vs p99 — check outliers |

Extra (geen auto-flag, wel handig):
- `SUMOFKCAL`: 2× `0` — check of echte zero of sentinel.
- `SUMOFALCOHOL`: veel `0` (verwacht bij non-drinkers) + ~35% NaN.
- `NSES`: ~45% NaN; scores rond 0 (negatief/positief).

## MD prevalentie (ruw, zelfde coding-aannames als stap 2)
- `METABOLIC_DISORDER_T1`: 0.0: 17465 (97.24%); 1.0: 452 (2.52%); -9.0: 24 (0.13%); -8.0: 15 (0.08%); nan: 4 (0.02%)
- `METABOLIC_DISORDER_T2`: 0.0: 17180 (95.66%); 1.0: 731 (4.07%); -9.0: 24 (0.13%); -8.0: 21 (0.12%); nan: 4 (0.02%)
- `METABOLIC_DISORDER_T3`: 2.0: 14261 (79.4%); nan: 3368 (18.75%); 1.0: 331 (1.84%)

## Figuren
- `eda_outputs/stap3/figures/histograms_continuous.png`
- `eda_outputs/stap3/figures/boxplots_key.png`
- `eda_outputs/stap3/figures/bars_categorical.png`

## Tabellen
- `univariate_continuous_summary.csv`
- `univariate_categorical_counts.csv`
- `flags_for_cleaning_colleague.csv`
- `stap3_summary.json`

## Niet gedaan (bewust)
- Geen imputatie / winsorizing / −8/−9-mapping (collega)
- Geen bivariate / target-associaties (stap 5)
- Geen feature-shortlist freeze (stap 6)
