"""EDA stap 1+2 — run with: uv run python 'Scripts and Notebooks/eda_stap1_2_tim.py'
Or open outputs in eda_outputs/ after running.
"""
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "data/raw/exquairo_ai_bootcamp_synth_dataset.csv"
OUT = Path(__file__).resolve().parent / "eda_outputs"
OUT.mkdir(exist_ok=True)

df = pd.read_csv(CSV, sep=";")
print("=== STAP 1 ===")
print("shape", df.shape)
print("memory_mb", round(df.memory_usage(deep=True).sum() / 1e6, 2))
print(df.dtypes.value_counts())

nan = df.isna().sum().sort_values(ascending=False)
print("\nTop NaN:\n", nan.head(15))

print("\n=== STAP 2: MD value counts ===")
for c in ["METABOLIC_DISORDER_T1", "METABOLIC_DISORDER_T2", "METABOLIC_DISORDER_T3"]:
    print(c, df[c].value_counts(dropna=False).head(10).to_dict())

print("\nSee EDA_STAP1_2.md and eda_outputs/ for dictionary roles.")
