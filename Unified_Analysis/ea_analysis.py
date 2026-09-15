"""
Formal Ea comparison (P1 vs P2 ONLY -- P3 explicitly excluded, reported
separately with a reliability flag) + sensitivity to dose-group selection.

Run: python ea_analysis.py
Outputs:
  - ea_comparison.csv         (P1 vs P2 formal statistical comparison)
  - ea_sensitivity.csv        (leave-one-dose-group-out jackknife per phase)
"""
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

OUT = Path(__file__).resolve().parent
ea_table = pd.read_csv(OUT / "arrhenius_activation_energy.csv")
ea_table["Ea_values_kJ_mol"] = ea_table["Ea_values_kJ_mol"].apply(eval)

p1_vals = np.array(ea_table.loc[ea_table["Study"] == "P1-Temperature", "Ea_values_kJ_mol"].iloc[0])
p2_vals = np.array(ea_table.loc[ea_table["Study"] == "P2-Temperature", "Ea_values_kJ_mol"].iloc[0])


def cohens_d(a, b):
    n1, n2 = len(a), len(b)
    pooled_std = np.sqrt(((n1 - 1) * a.std(ddof=1) ** 2 + (n2 - 1) * b.std(ddof=1) ** 2) / (n1 + n2 - 2))
    return (a.mean() - b.mean()) / pooled_std


def formal_comparison():
    t_stat, t_p = stats.ttest_ind(p1_vals, p2_vals, equal_var=False)  # Welch's t-test
    u_stat, u_p = stats.mannwhitneyu(p1_vals, p2_vals, alternative="two-sided")
    d = cohens_d(p1_vals, p2_vals)
    diff = p2_vals.mean() - p1_vals.mean()
    se_diff = np.sqrt(p1_vals.var(ddof=1) / len(p1_vals) + p2_vals.var(ddof=1) / len(p2_vals))
    row = dict(
        P1_Ea_mean=p1_vals.mean(), P1_Ea_std=p1_vals.std(ddof=1), P1_n_dose_groups=len(p1_vals),
        P2_Ea_mean=p2_vals.mean(), P2_Ea_std=p2_vals.std(ddof=1), P2_n_dose_groups=len(p2_vals),
        difference_kJ_mol=diff, SE_of_difference=se_diff,
        welch_t_stat=t_stat, welch_p_value=t_p,
        mannwhitney_u_stat=u_stat, mannwhitney_p_value=u_p,
        cohens_d=d,
        conclusion=(
            "Not statistically distinguishable within the uncertainty of the fitted "
            "estimates (p > 0.05 by both Welch's t-test and Mann-Whitney U)"
            if t_p > 0.05 and u_p > 0.05 else
            "Estimates differ beyond what sampling variability alone would suggest "
            "(p <= 0.05 by at least one test) -- interpret cautiously given n=6 per phase"
        ),
    )
    out = pd.DataFrame([row])
    out.to_csv(OUT / "ea_comparison.csv", index=False)
    return out


def sensitivity(vals, label):
    """Leave-one-dose-group-out jackknife: how much does mean Ea shift if any
    single dose-group's fitted Ea is excluded?"""
    rows = []
    for i in range(len(vals)):
        remaining = np.delete(vals, i)
        rows.append(dict(Phase=label, excluded_index=i, excluded_value=vals[i],
                          jackknife_mean_Ea=remaining.mean(), n_remaining=len(remaining)))
    return pd.DataFrame(rows)


if __name__ == "__main__":
    print("=== P3 Ea -- reported separately, NOT included in the P1 vs P2 comparison ===")
    for study in ["P3-Okro-Acid", "P3-Okro-Basic"]:
        row = ea_table.loc[ea_table["Study"] == study]
        if not row.empty:
            print(f"{study}: Ea = {row['Ea_mean_kJ_mol'].iloc[0]:.1f} +/- {row['Ea_std_kJ_mol'].iloc[0]:.1f} kJ/mol "
                  f"(n={row['n_dose_groups'].iloc[0]} dose groups) -- FLAGGED UNRELIABLE: small n, "
                  f"noisy/near-zero Tafel currents in some conditions. Excluded from headline "
                  f"convergence claim because its own per-dose-group fit variance is too large "
                  f"to trust, not because it disagrees with P1/P2.")

    print("\n=== FORMAL P1 vs P2 Ea COMPARISON ===")
    comp = formal_comparison()
    for col in comp.columns:
        print(f"{col}: {comp[col].iloc[0]}")

    print("\n=== Ea SENSITIVITY (leave-one-dose-group-out jackknife) ===")
    sens = pd.concat([sensitivity(p1_vals, "P1-Temperature"), sensitivity(p2_vals, "P2-Temperature")],
                      ignore_index=True)
    sens.to_csv(OUT / "ea_sensitivity.csv", index=False)
    print(sens.to_string(index=False))
    print(f"\nP1 jackknife mean range: {sens[sens.Phase=='P1-Temperature'].jackknife_mean_Ea.min():.1f} - "
          f"{sens[sens.Phase=='P1-Temperature'].jackknife_mean_Ea.max():.1f} kJ/mol")
    print(f"P2 jackknife mean range: {sens[sens.Phase=='P2-Temperature'].jackknife_mean_Ea.min():.1f} - "
          f"{sens[sens.Phase=='P2-Temperature'].jackknife_mean_Ea.max():.1f} kJ/mol")
