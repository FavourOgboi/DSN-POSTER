"""
Data-quality + comparability audit for the unified 302-row master dataset.
Run BEFORE any modeling decision -- non-positive CR rows are flagged, never
silently dropped here (each downstream analysis decides for itself whether
it can tolerate them, e.g. Arrhenius requires CR>0 for ln(CR)).

Run: python data_quality_audit.py
Outputs:
  - data_quality_audit.csv       (per-phase/per-study numeric summary)
  - comparability_matrix.csv     (explicit "what's shared vs different" table)
Also prints the "unit of independence" statement to console.
"""
from pathlib import Path
import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parent
master = pd.read_csv(OUT / "master_corrosion_dataset.csv")


def per_study_audit(df):
    rows = []
    for study, g in df.groupby("Study"):
        cr = g["CR_mm_yr"]
        rows.append(dict(
            Study=study,
            Phase_Group=g["Phase_Group"].iloc[0],
            n=len(g),
            n_missing_Temp_C=g["Temp_C"].isna().sum(),
            n_missing_Time_h=g["Time_h"].isna().sum(),
            n_missing_IE_percent=g["IE_percent"].isna().sum(),
            n_duplicate_rows=g.duplicated().sum(),
            n_CR_le_0=(cr <= 0).sum(),
            CR_min=cr.min(), CR_max=cr.max(), CR_mean=cr.mean(), CR_std=cr.std(),
            unique_Temp_levels=g["Temp_C"].dropna().nunique(),
            unique_Dose_levels=g["Dose_Value"].dropna().nunique(),
            unique_Time_levels=g["Time_h"].dropna().nunique(),
        ))
    out = pd.DataFrame(rows)
    out.to_csv(OUT / "data_quality_audit.csv", index=False)
    return out


def comparability_matrix():
    """Explicit, non-implied statement of what is/is not comparable across phases."""
    rows = [
        dict(Dimension="Material", P1="Mild steel", P2="Mild steel", P3="Mild steel", Comparable="Yes"),
        dict(Dimension="Corrosion target", P1="CR (mm/yr)", P2="CR (mm/yr)", P3="CR (mm/yr)", Comparable="Yes"),
        dict(Dimension="Measurement technique", P1="Weight loss", P2="Weight loss", P3="Tafel (electrochemical)", Comparable="Partial (P1/P2 only)"),
        dict(Dimension="Inhibitor system", P1="BL+PP+SW ternary blend", P2="Single green inhibitor", P3="Okro leaf extract", Comparable="No -- different chemistries"),
        dict(Dimension="Medium", P1="HCl (1M)", P2="HCl (0.5-1.5M)", P3="HCl and NaOH (1.0-2.5M)", Comparable="Partial (acid only across all 3)"),
        dict(Dimension="Temperature range", P1="40-80C", P2="30-70C", P3="30-60C", Comparable="Partial overlap (30-60C)"),
        dict(Dimension="Dose unit", P1="ppm (Temp/Time sub-studies) / mL_blend (DoE)", P2="ppm", P3="ppm", Comparable="No -- DoE not comparable to ppm studies"),
        dict(Dimension="Time range", P1="25-125h (Time sub-study)", P2="3-15h (Time sub-study)", P3="not varied (fixed/short)", Comparable="No -- different designs"),
        dict(Dimension="Sample size (n)", P1="~30-90 per sub-phase", P2="~90 per sub-phase", P3="17 per medium", Comparable="No -- P3 much smaller"),
        dict(Dimension="Role in study", P1="Core", P2="Core", P3="Stress test (measurement-regime shift)", Comparable="N/A -- hierarchical, not a comparability dimension"),
    ]
    out = pd.DataFrame(rows)
    out.to_csv(OUT / "comparability_matrix.csv", index=False)
    return out


if __name__ == "__main__":
    print(f"Master dataset: {len(master)} rows total\n")

    print("=== UNIT OF INDEPENDENCE ===")
    print(
        "Each row is one recorded measurement under a specific experimental condition\n"
        "(concentration/dose x temperature x time x medium), not an independently\n"
        "repeated full experiment. 302 rows therefore does NOT mean 302 independent\n"
        "pieces of evidence -- many rows share a Study/condition-design structure\n"
        "(e.g. P2-Temperature has 90 rows from 5 temps x 6 doses x 3 acid molarities,\n"
        "not 90 unrelated trials). Cross-validation in the modeling stage must respect\n"
        "this via grouped CV (group by condition), not plain random k-fold.\n"
    )

    print("=== PER-STUDY DATA QUALITY AUDIT ===")
    audit = per_study_audit(master)
    print(audit.to_string(index=False))

    print("\n=== NON-POSITIVE CR ROWS (flagged, not dropped) ===")
    bad = master[master["CR_mm_yr"] <= 0]
    if bad.empty:
        print("None found.")
    else:
        print(bad[["Study", "Dose_Value", "Temp_C", "CR_mm_yr"]].to_string(index=False))
        print(f"\nTotal: {len(bad)} rows, all in: {sorted(bad['Study'].unique())}")
        print("These are retained in master_corrosion_dataset.csv. Excluded ONLY from")
        print("analyses that mathematically require CR>0 (e.g. Arrhenius ln(CR)), with")
        print("the exclusion count reported by that analysis itself.")

    print("\n=== COMPARABILITY MATRIX (pooling != equivalence) ===")
    matrix = comparability_matrix()
    print(matrix.to_string(index=False))
