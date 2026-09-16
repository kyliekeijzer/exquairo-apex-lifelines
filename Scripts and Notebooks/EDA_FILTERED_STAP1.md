# EDA stap 1 — filtered dataset (`df_filtered.xlsx`)

Branch work for Tim / Team 1. Data: `data/processed/df_filtered.xlsx` (openpyxl).  
**No cleaning / mutation of the xlsx.** Stap 2+ not in scope.

Reproduce:

```bash
uv run python 'Scripts and Notebooks/eda_filtered_stap1_tim.py'
```

## Stap 1 — Laden & eerste check

| Check | Resultaat |
|-------|-----------|
| Rijen × kolommen | **17960 × 56** |
| Geheugen (deep) | ~**8.05 MB** |
| Dtypes | 49× float64, 7× int64 |
| Kolommen met NaN | **46 / 56** |
| Kolommen met −8/−9 | **0** (MD-targetkolommen zitten niet in de filtered set) |

### vs oude raw CSV
- Raw: **17960 × 100** → filtered: **17960 × 56** (zelfde rijen, 44 kolommen weg)
- Targets / MD (`METABOLIC_DISORDER_T*`), dual HbA1c-units (`HB1C_T*`), en vele T3-/extra labs o.a. verdwenen uit deze slice
- Volledige droplist: `eda_outputs/filtered_stap1/dropped_vs_raw.csv`

### Grootste NaN-aandelen (top 10)

| Kolom | % missing |
|-------|-----------|
| `TYPE2_DIABETES_FAMILY_FATHER` | 97.37% |
| `TYPE2_DIABETES_FAMILY_MOTHER` | 96.93% |
| `DIAG_FIBROMYALGIA_ACR` | 15.43% |
| `DIAG_CFS_CDC` | 14.33% |
| `DIAG_IBS_ROME3` | 14.24% |
| `CYCLE_COMMUTE_T1` | 13.24% |
| `LLDS` | 11.62% |
| `WORK_T1` | 11.15% |
| `NSES` | 9.85% |
| `EDUCATION_LOWER_T2` | 9.13% |

### Suspicious codes

**−8 / −9:** geen treffers in de 56 filtered kolommen (verwacht: `METABOLIC_DISORDER_T1/T2` zaten in raw, niet hier).

**`HBAC_*` waarden ≤ 0:**

| Kolom | n ≤ 0 | detail | NaN |
|-------|------:|--------|----:|
| `HBAC_T1` | 0 | — | 124 |
| `HBAC_T2` | **2** | beide exact `0.0` | 617 |
| `HBAC_T3` | 0 | — | 838 |

**`NSES` parse:**
- In **xlsx**: dtype **float64**; **true NaN = 1769 (9.85%)**; **0** multi-dot / unparseable strings remaining
- In **raw CSV** (ter vergelijking): 1769 lege/NaN + **6338** multi-dot strings (bijv. `-1.957.918.992`) die `to_numeric` niet aankan
- Conclusie: multi-dot is **upstream opgelost** bij het bouwen van `df_filtered.xlsx`; de filtered file toont nette floats + dezelfde blank-NaN-count

### Surprises / aandachtspunten
1. Geen −8/−9 meer zichtbaar — omdat MD-kolommen weg zijn, niet omdat codes “gecleaned” zijn elders.
2. Familie-diabetes nog ~97% NaN (zelfde patroon als raw; waarschijnlijk blank≈nee).
3. `HBAC_T2` heeft nog 2× `0.0` (kandidaat-missing, zelfde issue als eerdere stap-1 op raw).
4. `NSES` is al numeriek in xlsx — geen string-reparatie meer nodig op dit bestand.

## Artifacts

`Scripts and Notebooks/eda_outputs/filtered_stap1/`

- `missingness.csv`
- `meta.json`
- `suspicious_codes.json`
- `suspicious_codes_minus8_9.csv`
- `suspicious_codes_hbac_le0.csv`
- `dropped_vs_raw.csv` (optioneel overzicht)

## Volgende (niet in deze PR)
Stap 2+: dictionary/rollen, univariate, missingness-regels, target-definitie — op filtered set.
