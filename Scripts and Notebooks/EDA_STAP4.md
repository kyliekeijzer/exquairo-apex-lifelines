# EDA stap 4 — Missings / cleaning RULES inventory (raw, geen data-adaptatie)

Branch work for Tim / Team 1. Data: `data/raw/exquairo_ai_bootcamp_synth_dataset.csv` (`sep=';'`).

**Scope:** alleen inventaris van missings + **voorgestelde** cleaning-regels. Geen imputatie, geen winsorizing, geen nieuwe master-CSV. Collega's cleanen later.

Run: `uv run python 'Scripts and Notebooks/eda_stap4_tim.py'`

## Dataset
- Rijen × kolommen: **17960 × 100**
- Kolommen met NaN: **84 / 100**
- Kolommen met −8/−9: **2** (`METABOLIC_DISORDER_T1`, `METABOLIC_DISORDER_T2`)
- `HBAC_T2` waarden ≤0: **2** (implausibel voor %)

## Worst missingness (top 10)

| Column | % NaN | proposed_rule (kort) |
|--------|------:|----------------------|
| `TYPE2_DIABETES_FAMILY_FATHER` | 97.37% | high-NaN ≈ unchecked/no |
| `TYPE2_DIABETES_FAMILY_MOTHER` | 96.93% | high-NaN ≈ unchecked/no |
| `SLEEP_QUALITY` | 52.51% | team: keep/impute/drop |
| `ALT_T1` | 49.49% | keep+missing-indicator vs drop |
| `UZ_T1` | 49.49% | keep+missing-indicator vs drop |
| `BALB_T1` | 49.37% | keep+missing-indicator vs drop |
| `PREGNANCIES` | 43.85% | sex-linked missing (GENDER) |
| `SUMOFALCOHOL` | 34.85% | high missing — document |
| `SUMOFKCAL` | 34.78% | high missing; check zeros |
| `HB1C_T1` | 21.45% | prefer HBAC_% twin |

## Proposed cleaning rules (n=12) — document only

| rule_id | column(s) | rule | apply_when |
|---------|-----------|------|------------|
| R01 | MD_T1, MD_T2 | −8/−9 → missing; keep 0/1 | colleague later |
| R02 | MD_T3 | binary: 2→0; 1=yes | colleague later (in-memory) |
| R03 | HBAC_T* | ≤0 → missing | colleague later |
| R04 | FAMILY_FATHER/MOTHER | blank/NaN ≈ unchecked/no (opt. fill 0) | confirm + colleague |
| R05 | ALT/UZ/BALB_T1 | keep+missing-indicator **vs** drop | **team decision** |
| R06 | HB1C/TGL/ALT outliers | flag vs winsorize — propose, don't apply | clinical review |
| R07 | HB1C vs HBAC | prefer one unit; don't both blindly | stap 6+ shortlist |
| R08 | PREGNANCIES | missing by GENDER; don't impute 0 blindly | colleague later |
| R09 | SLEEP_QUALITY, SUMOF*, NSES, … | high-miss playbook | team |
| R10 | *_T3 / MD_T3 | **no T3 predictors for T1/T2** (leakage) | always |
| R11 | SUMOFKCAL | review zeros (sentinel?) | colleague later |
| R12 | all scripts | mask in-memory only until master | now |

## Figuren / tabellen
- `eda_outputs/stap4/missingness_by_column.csv`
- `eda_outputs/stap4/proposed_cleaning_rules.csv`
- `eda_outputs/stap4/missingness_heatmap_top40.png` (bar van top-40 % NaN)
- `eda_outputs/stap4/stap4_summary.json`

## Niet gedaan (bewust)
- Geen cleaned CSV / geen wijziging van `data/raw`
- Geen imputatie of outlier-winsorizing toegepast
- Geen bivariate (→ stap 5)
