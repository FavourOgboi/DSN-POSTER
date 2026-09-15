"""
Unified merge of the three in-house corrosion-inhibitor experiments into ONE
long-format master dataset, plus cross-study scientific analyses that only
become possible once the data is pooled.

Dose schema (fixed): each row carries `Dose_Value` (always populated, in its
OWN native unit) + `Dose_Unit` ('ppm' or 'mL_blend') + `Concentration_ppm`
(populated ONLY where Dose_Unit=='ppm'). P1-DoE-Blend is dosed in mL of blend,
not ppm, and is NEVER converted or merged into a ppm-based ranking -- no
verified mg/mL active-ingredient equivalence exists.

Run: python build_master_dataset.py
Outputs (written into Unified_Analysis/):
  - master_corrosion_dataset.csv
  - correlation_comparison.csv
  - arrhenius_activation_energy.csv
  - dosage_efficiency_index.csv (ppm-dosed studies only, enforced in code)
"""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent
R_GAS = 8.314  # J/(mol.K)

P1 = ROOT / "Machine learning for predicting corrosion rate and inhibitor efficiency of an optimized ternary inhibitor blend under variable temperatures"
P2 = ROOT / "Machine learning prediction of corrosion rate and inhibition efficiency of a green inhibitor in a multi PH and multi temperatre chemical environment"
P3 = ROOT / "Predictive Modeling and Performance Optimization of Okro leaf extract as a corrosion inhibitor in Acidic and Basic Media Using Machine Learning"

COLS = ["Study", "Phase_Group", "Inhibitor_System", "Technique", "Medium_Type", "Molarity_M",
        "Dose_Value", "Dose_Unit", "Concentration_ppm", "Temp_C", "Time_h", "CR_mm_yr", "IE_percent"]


def _row(study, system, technique, medium, molarity, dose_value, dose_unit, temp, time_h, cr, ie):
    phase = study.split("-")[0]  # P1 / P2 / P3
    conc_ppm = dose_value if dose_unit == "ppm" else np.nan
    return dict(Study=study, Phase_Group=phase, Inhibitor_System=system, Technique=technique,
                Medium_Type=medium, Molarity_M=molarity, Dose_Value=dose_value, Dose_Unit=dose_unit,
                Concentration_ppm=conc_ppm, Temp_C=temp, Time_h=time_h, CR_mm_yr=cr, IE_percent=ie)


def _clean_ppm(series):
    """'blank' rows represent the 0-ppm control measurement."""
    return pd.to_numeric(series.astype(str).str.replace("blank", "0", case=False), errors="coerce")


def load_p1_temp():
    df = pd.read_excel(P1 / "Different Temperature" / "data_difftime.xlsx")
    temp = df["Temperature"].astype(str).str.extract(r"(\d+)").astype(float)[0]
    ppm = _clean_ppm(df["concentration (ppm)"])
    rows = []
    for i, r in df.iterrows():
        rows.append(_row("P1-Temperature", "Ternary Blend (BL+PP+SW)", "Weight loss",
                          "Acid", 1.0, ppm[i], "ppm", temp[i], np.nan,
                          r["Corrosion rate(mm/y)"], r["inhibitor efficiency"]))
    return pd.DataFrame(rows)


def load_p1_time():
    df = pd.read_excel(P1 / "Different Time" / "corrosion_raw.xlsx")
    ppm = _clean_ppm(df["concentration (ppm)"])
    rows = []
    for i, r in df.iterrows():
        rows.append(_row("P1-Time", "Ternary Blend (BL+PP+SW)", "Weight loss",
                          "Acid", 1.0, ppm[i], "ppm", np.nan, r["Time (Hours)"],
                          r["Corrosion rate(mm/y)"], r["inhibitor efficiency"]))
    return pd.DataFrame(rows)


def load_p1_doe():
    """Dose is in mL of blend (BL+PP+SW), NOT ppm -- kept in its own Dose_Unit
    so it can never be silently merged into a ppm-based ranking."""
    df = pd.read_csv(P1 / "parent Experiment" / "doe_data.csv")
    rows = []
    for _, r in df.iterrows():
        total_vol = r["BL"] + r["PP"] + r["SW"]
        rows.append(_row("P1-DoE-Blend", "Ternary Blend (BL+PP+SW)", "Weight loss",
                          "Acid", np.nan, total_vol, "mL_blend", np.nan, r["Time"],
                          r["CR"], r["IE"]))
    return pd.DataFrame(rows)


def load_p2_temp():
    df = pd.read_csv(P2 / "Temperature" / "all_temp_cleaned.csv")
    df = df[pd.to_numeric(df["conc_ppm"], errors="coerce").notna() | (df["conc_ppm"] == "Control")]
    ppm = df["conc_ppm"].replace("Control", 0).astype(float)
    rows = []
    for i, r in df.reset_index(drop=True).iterrows():
        rows.append(_row("P2-Temperature", "Single Green Inhibitor", "Weight loss",
                          "Acid", r["acid_m"], ppm[i], "ppm", r["temp_c"], r["time_h"],
                          r["cr_mm_yr"], r["ie_percent"]))
    return pd.DataFrame(rows)


def load_p2_time():
    df = pd.read_csv(P2 / "Time" / "all_no_temp_cleaned.csv")
    df = df[pd.to_numeric(df["conc_ppm"], errors="coerce").notna() | (df["conc_ppm"] == "Control")]
    ppm = df["conc_ppm"].replace("Control", 0).astype(float)
    rows = []
    for i, r in df.reset_index(drop=True).iterrows():
        rows.append(_row("P2-Time", "Single Green Inhibitor", "Weight loss",
                          "Acid", r["acid_m"], ppm[i], "ppm", np.nan, r["time_h"],
                          r["cr_mm_yr"], r["ie_percent"]))
    return pd.DataFrame(rows)


def load_p3(medium):
    folder, fname, mcol = (("Acidic", "cleaned_HCL_tafel_data.csv", "HCl_M") if medium == "Acid"
                            else ("Basic", "cleaned_NAOH_tafel_data.csv", "NaOH_M"))
    sub = "cleaned data hcl" if medium == "Acid" else "cleaned data naoh"
    df = pd.read_csv(P3 / folder / sub / fname)
    rows = []
    for _, r in df.iterrows():
        rows.append(_row(f"P3-Okro-{medium}", "Okro Leaf Extract", "Tafel (electrochemical)",
                          medium, r[mcol], r["Inhibitor_ppm"], "ppm", r["Temp_C"], np.nan,
                          r["CR_mm_yr"], np.nan))
    return pd.DataFrame(rows)


def build_master():
    parts = [load_p1_temp(), load_p1_time(), load_p1_doe(),
             load_p2_temp(), load_p2_time(),
             load_p3("Acid"), load_p3("Basic")]
    master = pd.concat(parts, ignore_index=True)[COLS]
    OUT.mkdir(exist_ok=True)
    master.to_csv(OUT / "master_corrosion_dataset.csv", index=False)
    return master


def correlations(master):
    """Uses Dose_Value (native units per study) rather than Concentration_ppm,
    so P1-DoE-Blend's mL dose is still correlated within its own study/units."""
    rows = []
    for study, g in master.groupby("Study"):
        g = g.dropna(subset=["CR_mm_yr"])
        n = len(g)
        r_temp = g["Temp_C"].corr(g["CR_mm_yr"]) if g["Temp_C"].nunique() > 1 else np.nan
        r_time = g["Time_h"].corr(g["CR_mm_yr"]) if g["Time_h"].nunique() > 1 else np.nan
        r_dose = g["Dose_Value"].corr(g["CR_mm_yr"]) if g["Dose_Value"].nunique() > 1 else np.nan
        rows.append(dict(Study=study, n=n, r_CR_vs_Temp=r_temp, r_CR_vs_Time=r_time,
                          r_CR_vs_Dose=r_dose, Dose_Unit=g["Dose_Unit"].iloc[0]))
    out = pd.DataFrame(rows)
    out.to_csv(OUT / "correlation_comparison.csv", index=False)
    return out


def arrhenius(master):
    """Fit ln(CR) = ln(A) - Ea/R * (1/T_K) per (Study, dose group), average Ea per Study."""
    rows = []
    for study, g in master.groupby("Study"):
        g = g.dropna(subset=["Temp_C", "CR_mm_yr"])
        g = g[g["CR_mm_yr"] > 0]
        if g["Temp_C"].nunique() < 2:
            continue
        eas = []
        group_keys = ["Dose_Value"] if not study.startswith("P3") else ["Molarity_M", "Dose_Value"]
        for _, sub in g.groupby(group_keys):
            if sub["Temp_C"].nunique() < 2:
                continue
            t_k = sub["Temp_C"].astype(float) + 273.15
            x = 1.0 / t_k
            y = np.log(sub["CR_mm_yr"].astype(float))
            if x.nunique() < 2:
                continue
            slope, _ = np.polyfit(x, y, 1)
            ea_kjmol = -slope * R_GAS / 1000.0
            eas.append(ea_kjmol)
        if eas:
            rows.append(dict(Study=study, n_dose_groups=len(eas),
                              Ea_mean_kJ_mol=np.mean(eas), Ea_std_kJ_mol=np.std(eas),
                              Ea_values_kJ_mol=[round(e, 2) for e in eas]))
    out = pd.DataFrame(rows)
    out.to_csv(OUT / "arrhenius_activation_energy.csv", index=False)
    return out


def dosage_efficiency(master):
    """ppm-dosed studies ONLY -- enforced here, not just by convention, so a
    mL-dosed row can never silently enter a ppm-based efficiency ranking."""
    ppm_only = master[master["Dose_Unit"] == "ppm"]
    rows = []
    for study, g in ppm_only.groupby("Study"):
        g = g.dropna(subset=["IE_percent", "Concentration_ppm"])
        g = g[g["Concentration_ppm"] > 0]
        if g.empty:
            continue
        idx = (g["IE_percent"] / g["Concentration_ppm"])
        rows.append(dict(Study=study, n=len(g),
                          mean_IE_percent=g["IE_percent"].mean(),
                          mean_ppm_tested=g["Concentration_ppm"].mean(),
                          efficiency_index_IE_per_ppm=idx.mean()))
    out = pd.DataFrame(rows).sort_values("efficiency_index_IE_per_ppm", ascending=False)
    out.to_csv(OUT / "dosage_efficiency_index.csv", index=False)
    return out


if __name__ == "__main__":
    master = build_master()
    print(f"Master dataset: {master.shape[0]} rows x {master.shape[1]} cols -> "
          f"{OUT / 'master_corrosion_dataset.csv'}")
    print("\nRows per study:")
    print(master["Study"].value_counts().to_string())
    print("\nDose_Unit check (mL_blend rows must equal P1-DoE-Blend row count only):")
    print(master.groupby(["Dose_Unit", "Study"]).size().to_string())

    print("\n=== Correlation comparison (CR vs Temp/Time/Dose) ===")
    corr = correlations(master)
    print(corr.to_string(index=False))

    print("\n=== Arrhenius activation energy per study (kJ/mol) ===")
    ea = arrhenius(master)
    print(ea.to_string(index=False))

    print("\n=== Dosage efficiency index (mean IE% per ppm) -- ppm-dosed studies only ===")
    eff = dosage_efficiency(master)
    print(eff.to_string(index=False))
