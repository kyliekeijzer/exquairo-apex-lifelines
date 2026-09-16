# EDA stap 1 + 2 — ExquAIro synth dataset

Branch work for Tim / Team 1. Data: `data/raw/exquairo_ai_bootcamp_synth_dataset.csv` (`sep=';'`).

## Stap 1 — Laden & eerste check

| Check | Resultaat |
|-------|-----------|
| Rijen × kolommen | **17960 × 100** |
| Geheugen (deep) | ~**15.4 MB** |
| Dtypes | 90× float64, 9× int64, 1× string |
| Kolommen met NaN | **84 / 100** |
| Kolommen met −8/−9 | **2** (`METABOLIC_DISORDER_T1/T2`) |

### Grootste NaN-aandelen (top)
- `TYPE2_DIABETES_FAMILY_FATHER` / `_MOTHER` — ~97% NaN (waarschijnlijk blank=nee)
- `SLEEP_QUALITY` — ~52% NaN
- Labs T1 subset (`UZ_T1`, `ALT_T1`, `BALB_T1`) — ~49% NaN
- `METABOLIC_DISORDER_T3` — ~19% NaN
- `HB1C_T1` — ~21% NaN (meer missing dan `HBAC_T1`)

Artifacts: `eda_outputs/stap1_*.csv|json`

## Stap 2 — Dictionary / rollen / aannames

### Rollen (werkhypothese)
| Rol | n | Voorbeelden |
|-----|---|-------------|
| TARGET_CANDIDATE | 3 | `METABOLIC_DISORDER_T1/T2/T3` |
| HBA1C_PERCENT | 3 | `HBAC_T*` |
| HBA1C_MMOLMOL | 3 | `HB1C_T*` (zelfde stof, andere eenheid) |
| FEATURE_T2 | 21 | latere meting |
| FEATURE_T3 leakage-risk | 10 | niet gebruiken als je eerdere uitkomst voorspelt |
| FEATURE | 60 | baseline / overig |

### Open aannames (nog bevestigen met bootcamp/Tim)
1. **MD T1/T2:** `1=ja`, `0=nee`, `−8/−9=missing` (bootcamp-composiet; niet op wiki onder die naam).
2. **MD T3:** `1=ja`, `2=nee` (starter-notebook mapped `2→0`); **andere coding dan T1/T2**.
3. **`HBAC`** = %; **`HB1C`** = mmol/mol — niet allebei blind als features.
4. Familie-diabetes: hoge NaN ≈ “niet aangevinkt / nee” per TXT.
5. HbA1c `≤0` (gezien op T2) → behandelen als missing.

Artifacts: `eda_outputs/stap2_dictionary_roles.csv`, `stap2_open_assumptions.csv`, `stap2_md_value_counts.json`

## MD prevalentie (ruw)
- T1: 452× `1` / 17465× `0` (+ −8/−9/NaN)
- T2: 731× `1` / 17180× `0`
- T3: 331× `1` / 14261× `2` / 3368 NaN

## Volgende (stap 3+)
Univariate plots, missingness-regels vastzetten, target-definitie freezen, shortlist features zonder T3-leakage.
