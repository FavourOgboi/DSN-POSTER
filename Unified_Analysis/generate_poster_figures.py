"""
Poster-ready figure generation for the unified green corrosion inhibitor study.

Reads CSV outputs from the Unified_Analysis pipeline and generates 7 publication-
quality figures with consistent professional styling suitable for conference posters.

Figures are saved with 'poster_' prefix to preserve original notebook-generated
versions. All figures use 300 DPI, a cohesive academic colour palette, and
annotations that tell the scientific story at a glance.

Run: python generate_poster_figures.py
Outputs: Unified_Analysis/figures/poster_*.png  (7 files)
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# ---------------------------------------------------------------------------
# Global style configuration
# ---------------------------------------------------------------------------
OUT = Path(__file__).resolve().parent
FIG_DIR = OUT / "figures"
FIG_DIR.mkdir(exist_ok=True)

# Colour palette -- colorblind-safe, poster-readable
TEAL      = "#0D7377"
CORAL     = "#E85D4A"
SLATE     = "#4A5568"
GOLD      = "#D4A843"
DEEP_BLUE = "#2B6CB0"
SOFT_GREY = "#A0AEC0"
MINT      = "#38A89D"
WARM_RED  = "#C53030"

PHASE_COLOURS = {
    "P1": TEAL,
    "P2": CORAL,
    "P3": SLATE,
}

PHASE_COLOURS_FULL = {
    "P1-Temperature": TEAL,
    "P1-Time": MINT,
    "P1-DoE-Blend": DEEP_BLUE,
    "P2-Temperature": CORAL,
    "P2-Time": GOLD,
    "P3-Okro-Acid": SLATE,
    "P3-Okro-Basic": SOFT_GREY,
}

MODEL_COLOURS = {
    "Ridge": SOFT_GREY,
    "RandomForest": MINT,
    "XGBoost": CORAL,
    "CatBoost": TEAL,
}

def apply_poster_style():
    """Set global matplotlib rcParams for poster aesthetics."""
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "font.size": 14,
        "axes.titlesize": 18,
        "axes.titleweight": "bold",
        "axes.labelsize": 15,
        "axes.labelweight": "bold",
        "xtick.labelsize": 12,
        "ytick.labelsize": 12,
        "legend.fontsize": 12,
        "figure.dpi": 300,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.3,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.alpha": 0.25,
        "grid.linestyle": "--",
        "axes.facecolor": "#FAFAFA",
        "figure.facecolor": "white",
    })

apply_poster_style()


# ===================================================================
# Figure 1: Correlation by phase
# ===================================================================
def fig01_correlation_by_phase():
    df = pd.read_csv(OUT / "correlation_comparison.csv")
    
    studies_temp = ["P1-Temperature", "P2-Temperature", "P3-Okro-Acid", "P3-Okro-Basic"]
    studies_time = ["P1-Time", "P2-Time"]
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), gridspec_kw={"width_ratios": [2, 1]})
    
    # --- Panel A: Temperature-varying phases ---
    ax = axes[0]
    labels_t = []
    r_temp = []
    r_dose = []
    colors_t = []
    for s in studies_temp:
        row = df[df["Study"] == s].iloc[0]
        labels_t.append(s.replace("P3-Okro-", "P3-"))
        r_temp.append(row["r_CR_vs_Temp"] if pd.notna(row["r_CR_vs_Temp"]) else 0)
        r_dose.append(row["r_CR_vs_Dose"] if pd.notna(row["r_CR_vs_Dose"]) else 0)
        colors_t.append(PHASE_COLOURS_FULL[s])
    
    x = np.arange(len(labels_t))
    w = 0.35
    bars1 = ax.bar(x - w/2, r_temp, w, label="r(CR, Temp)", color=[PHASE_COLOURS_FULL[s] for s in studies_temp], edgecolor="white", linewidth=1.2)
    bars2 = ax.bar(x + w/2, r_dose, w, label="r(CR, Dose)", color=[PHASE_COLOURS_FULL[s] for s in studies_temp], edgecolor="white", linewidth=1.2, alpha=0.5, hatch="//")
    
    for bar, val in zip(bars1, r_temp):
        if abs(val) > 0.01:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02 * np.sign(val),
                    f"{val:.2f}", ha="center", va="bottom" if val > 0 else "top",
                    fontsize=11, fontweight="bold")
    for bar, val in zip(bars2, r_dose):
        if abs(val) > 0.01:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02 * np.sign(val),
                    f"{val:.2f}", ha="center", va="bottom" if val > 0 else "top",
                    fontsize=10, color=SLATE)
    
    ax.set_xticks(x)
    ax.set_xticklabels(labels_t, rotation=15, ha="right")
    ax.set_ylabel("Pearson r with CR")
    ax.set_title("A) Temperature-Varying Phases")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.legend(loc="upper right", framealpha=0.9)
    ax.set_ylim(-0.55, 1.1)
    
    # --- Panel B: Time-varying phases ---
    ax = axes[1]
    labels_tm = []
    r_time_vals = []
    r_dose_vals = []
    for s in studies_time:
        row = df[df["Study"] == s].iloc[0]
        labels_tm.append(s)
        r_time_vals.append(row["r_CR_vs_Time"] if pd.notna(row["r_CR_vs_Time"]) else 0)
        r_dose_vals.append(row["r_CR_vs_Dose"] if pd.notna(row["r_CR_vs_Dose"]) else 0)
    
    x2 = np.arange(len(labels_tm))
    bars3 = ax.bar(x2 - w/2, r_time_vals, w, label="r(CR, Time)", color=[PHASE_COLOURS_FULL[s] for s in studies_time], edgecolor="white", linewidth=1.2)
    bars4 = ax.bar(x2 + w/2, r_dose_vals, w, label="r(CR, Dose)", color=[PHASE_COLOURS_FULL[s] for s in studies_time], edgecolor="white", linewidth=1.2, alpha=0.5, hatch="//")
    
    for bar, val in zip(bars3, r_time_vals):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02 * np.sign(val) if val != 0 else 0.02,
                f"{val:.2f}", ha="center", va="bottom" if val >= 0 else "top",
                fontsize=11, fontweight="bold")
    for bar, val in zip(bars4, r_dose_vals):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() - 0.04,
                f"{val:.2f}", ha="center", va="top",
                fontsize=10, color=SLATE)
    
    ax.set_xticks(x2)
    ax.set_xticklabels(labels_tm, rotation=15, ha="right")
    ax.set_ylabel("Pearson r with CR")
    ax.set_title("B) Time-Varying Phases")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.legend(loc="lower left", framealpha=0.9)
    ax.set_ylim(-0.85, 0.15)
    
    fig.suptitle("Correlation of CR with Environmental Variables by Phase",
                 fontsize=20, fontweight="bold", y=1.02)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "poster_01_correlation_by_phase.png")
    plt.close(fig)
    print("  [OK] poster_01_correlation_by_phase.png")


# ===================================================================
# Figure 2: Ea Convergence Headline
# ===================================================================
def fig02_ea_convergence():
    ec = pd.read_csv(OUT / "ea_comparison.csv")
    
    fig, ax = plt.subplots(figsize=(8, 7))
    
    means = [ec["P1_Ea_mean"].iloc[0], ec["P2_Ea_mean"].iloc[0]]
    sds   = [ec["P1_Ea_std"].iloc[0],  ec["P2_Ea_std"].iloc[0]]
    labels = ["P1 — Ternary Blend\n(Weight Loss)", "P2 — Single Inhibitor\n(Weight Loss)"]
    colors = [TEAL, CORAL]
    
    bars = ax.bar(labels, means, yerr=sds, capsize=10, color=colors,
                  edgecolor="white", linewidth=2, width=0.55,
                  error_kw={"linewidth": 2.5, "capthick": 2.5, "ecolor": SLATE})
    
    # Annotate bars with Ea values
    for bar, m, sd in zip(bars, means, sds):
        ax.text(bar.get_x() + bar.get_width()/2, m + sd + 2.5,
                f"{m:.1f} ± {sd:.1f}\nkJ/mol",
                ha="center", va="bottom", fontsize=14, fontweight="bold")
    
    # Add statistical annotation bracket
    p_welch = ec["welch_p_value"].iloc[0]
    p_mw    = ec["mannwhitney_p_value"].iloc[0]
    d_cohen = ec["cohens_d"].iloc[0]
    
    bracket_y = max(means[0] + sds[0], means[1] + sds[1]) + 18
    ax.plot([0, 0, 1, 1], [bracket_y - 2, bracket_y, bracket_y, bracket_y - 2],
            color=SLATE, linewidth=2)
    ax.text(0.5, bracket_y + 1,
            f"Δ = {ec['difference_kJ_mol'].iloc[0]:.1f} kJ/mol   |   "
            f"Welch p = {p_welch:.2f}   |   M-W p = {p_mw:.2f}\n"
            f"Cohen's d = {d_cohen:.2f} (small-moderate)   →   NOT statistically distinguishable",
            ha="center", va="bottom", fontsize=11, color=SLATE,
            fontstyle="italic",
            bbox=dict(boxstyle="round,pad=0.4", facecolor="#F7FAFC", edgecolor=SOFT_GREY, alpha=0.9))
    
    ax.set_ylabel("Activation Energy Ea (kJ/mol)")
    ax.set_title("Activation Energy Convergence: P1 vs P2\n(Core Evidence — Headline Finding)", pad=15)
    ax.set_ylim(0, bracket_y + 30)
    ax.yaxis.set_major_locator(mticker.MultipleLocator(10))
    
    fig.tight_layout()
    fig.savefig(FIG_DIR / "poster_02_ea_convergence_headline.png")
    plt.close(fig)
    print("  [OK] poster_02_ea_convergence_headline.png")


# ===================================================================
# Figure 3: Ea Jackknife Sensitivity
# ===================================================================
def fig03_ea_sensitivity():
    es = pd.read_csv(OUT / "ea_sensitivity.csv")
    ec = pd.read_csv(OUT / "ea_comparison.csv")
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=True)
    
    for i, (phase, colour, full_mean) in enumerate([
        ("P1-Temperature", TEAL, ec["P1_Ea_mean"].iloc[0]),
        ("P2-Temperature", CORAL, ec["P2_Ea_mean"].iloc[0]),
    ]):
        ax = axes[i]
        sub = es[es["Phase"] == phase].sort_values("excluded_index")
        x = range(len(sub))
        
        ax.bar(x, sub["jackknife_mean_Ea"], color=colour, edgecolor="white",
               linewidth=1.5, alpha=0.85, width=0.7)
        
        # Full-data mean line
        ax.axhline(full_mean, color=colour, linewidth=2.5, linestyle="--", alpha=0.7,
                   label=f"Full mean: {full_mean:.1f}")
        
        # Annotate excluded values
        for j, (_, row) in enumerate(sub.iterrows()):
            ax.text(j, row["jackknife_mean_Ea"] + 0.5,
                    f"{row['jackknife_mean_Ea']:.1f}",
                    ha="center", va="bottom", fontsize=10, fontweight="bold")
            ax.text(j, row["jackknife_mean_Ea"] - 2.5,
                    f"(excl {row['excluded_value']:.0f})",
                    ha="center", va="top", fontsize=8, color=SLATE)
        
        jk_min = sub["jackknife_mean_Ea"].min()
        jk_max = sub["jackknife_mean_Ea"].max()
        ax.set_title(f"{phase}\nRange: {jk_min:.1f}–{jk_max:.1f} kJ/mol")
        ax.set_xlabel("Dose group excluded")
        ax.set_xticks(list(x))
        ax.set_xticklabels([f"#{int(r)}" for r in sub["excluded_index"]], fontsize=10)
        ax.legend(loc="lower left", framealpha=0.9)
    
    axes[0].set_ylabel("Jackknife Mean Ea (kJ/mol)")
    fig.suptitle("Ea Sensitivity: Leave-One-Dose-Group-Out\n(No single dose group drives the convergence)",
                 fontsize=18, fontweight="bold", y=1.03)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "poster_03_ea_jackknife_sensitivity.png")
    plt.close(fig)
    print("  [OK] poster_03_ea_jackknife_sensitivity.png")


# ===================================================================
# Figure 4: Permutation Importance by Phase
# ===================================================================
def fig04_permutation_importance():
    pa = pd.read_csv(OUT / "predictor_ablation.csv")
    
    # Select the temperature-varying + P3 phases for the main comparison
    phases = ["P1-Temperature", "P2-Temperature", "P3-Okro-Acid", "P3-Okro-Basic"]
    features_of_interest = ["Temp_C", "Dose_Value", "Molarity_M"]
    
    fig, axes = plt.subplots(1, len(phases), figsize=(16, 6), sharey=False)
    
    for i, phase in enumerate(phases):
        ax = axes[i]
        sub = pa[(pa["Study"] == phase) & (pa["Feature"].isin(features_of_interest))]
        sub = sub.sort_values("permutation_importance", ascending=True)
        
        colour = PHASE_COLOURS_FULL.get(phase, SLATE)
        bars = ax.barh(sub["Feature"], sub["permutation_importance"],
                       color=colour, edgecolor="white", linewidth=1.5, height=0.55)
        
        for bar, val in zip(bars, sub["permutation_importance"]):
            ax.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height()/2,
                    f"{val:.2f}", va="center", fontsize=11, fontweight="bold")
        
        short_name = phase.replace("P3-Okro-", "P3-")
        ax.set_title(short_name, fontsize=14)
        ax.set_xlabel("Permutation\nImportance")
        if i == 0:
            ax.set_ylabel("Feature")
        
        ax.set_xlim(0, max(sub["permutation_importance"].max() * 1.35, 0.1))
    
    fig.suptitle("Permutation Importance by Phase\n(Temperature dominates P1 & P2; P3 is mixed)",
                 fontsize=18, fontweight="bold", y=1.04)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "poster_04_permutation_importance_by_phase.png")
    plt.close(fig)
    print("  [OK] poster_04_permutation_importance_by_phase.png")


# ===================================================================
# Figure 5: Standard vs Grouped CV
# ===================================================================
def fig05_standard_vs_grouped_cv():
    lb = pd.read_csv(OUT / "model_leaderboard.csv")
    
    configs = ["A_P1", "B_P2", "D_P1P2", "E_P1P2P3"]
    config_labels = {"A_P1": "P1 Only", "B_P2": "P2 Only",
                     "D_P1P2": "P1+P2", "E_P1P2P3": "P1+P2+P3"}
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    x_positions = []
    x_labels = []
    pos = 0
    
    for cfg in configs:
        sub = lb[lb["Config"] == cfg]
        models_in_cfg = sub["Model"].unique()
        
        for model in sorted(models_in_cfg):
            std_row = sub[(sub["Model"] == model) & (sub["CV_scheme"] == "standard_5fold")]
            grp_row = sub[(sub["Model"] == model) & (sub["CV_scheme"] == "grouped_5fold")]
            
            if std_row.empty or grp_row.empty:
                continue
            
            std_r2 = std_row["R2_mean"].iloc[0]
            grp_r2 = grp_row["R2_mean"].iloc[0]
            
            # Standard CV bar
            ax.bar(pos - 0.18, std_r2, width=0.32, color=DEEP_BLUE, alpha=0.75,
                   edgecolor="white", linewidth=1)
            # Grouped CV bar
            ax.bar(pos + 0.18, grp_r2, width=0.32, color=WARM_RED, alpha=0.75,
                   edgecolor="white", linewidth=1)
            
            # Arrow showing the drop
            if std_r2 > grp_r2:
                mid_y = (std_r2 + grp_r2) / 2
                drop = std_r2 - grp_r2
                if drop > 0.3:
                    ax.annotate("", xy=(pos + 0.18, grp_r2), xytext=(pos - 0.18, std_r2),
                                arrowprops=dict(arrowstyle="->", color=SLATE, lw=1.5, alpha=0.5))
            
            x_positions.append(pos)
            x_labels.append(f"{model[:3]}")
            pos += 1
        
        # Config separator
        if cfg != configs[-1]:
            ax.axvline(pos - 0.5, color=SOFT_GREY, linewidth=0.8, linestyle=":")
            pos += 0.3
    
    # Config group labels
    group_starts = [0, 4.3, 8.6, 12.9]
    for gs, cfg in zip(group_starts, configs):
        label = config_labels[cfg]
        n_models = len(lb[(lb["Config"] == cfg)]["Model"].unique())
        mid = gs + (n_models - 1) / 2
        ax.text(mid, ax.get_ylim()[1] if ax.get_ylim()[1] > 0 else 1.05,
                label, ha="center", fontsize=13, fontweight="bold", color=SLATE)
    
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_xticks(x_positions)
    ax.set_xticklabels(x_labels, rotation=45, ha="right", fontsize=10)
    ax.set_ylabel("R² (5-fold CV)")
    ax.set_title("Standard CV vs Grouped CV: The Leakage Effect\n(Random CV inflates R² by 0.3–1.2 across configurations)",
                 pad=20)
    
    # Legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=DEEP_BLUE, alpha=0.75, label="Standard CV"),
        Patch(facecolor=WARM_RED, alpha=0.75, label="Grouped CV"),
    ]
    ax.legend(handles=legend_elements, loc="upper right", framealpha=0.9, fontsize=13)
    
    fig.tight_layout()
    fig.savefig(FIG_DIR / "poster_05_standard_vs_grouped_cv.png")
    plt.close(fig)
    print("  [OK] poster_05_standard_vs_grouped_cv.png")


# ===================================================================
# Figure 6: Leave-One-Phase-Out Transfer
# ===================================================================
def fig06_leave_one_phase_out():
    lopo = pd.read_csv(OUT / "leave_one_phase_out_results.csv")
    
    directions = [
        ("P1+P2", "P3"),
        ("P1+P3", "P2"),
        ("P2+P3", "P1"),
    ]
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Panel A: R² by direction
    ax = axes[0]
    dir_labels = []
    best_r2 = []
    dir_colours = []
    for train, test in directions:
        sub = lopo[lopo["Train_phases"] == train]
        best = sub.loc[sub["R2"].idxmax()]
        dir_labels.append(f"{train} → {test}")
        best_r2.append(best["R2"])
        dir_colours.append(PHASE_COLOURS.get(test, SLATE))
    
    bars = ax.bar(dir_labels, best_r2, color=dir_colours, edgecolor="white",
                  linewidth=2, width=0.55)
    
    for bar, r2 in zip(bars, best_r2):
        y = r2 + 0.02 if r2 >= 0 else r2 - 0.06
        va = "bottom" if r2 >= 0 else "top"
        ax.text(bar.get_x() + bar.get_width()/2, y,
                f"R² = {r2:.2f}", ha="center", va=va,
                fontsize=13, fontweight="bold")
    
    ax.axhline(0, color="black", linewidth=1)
    ax.set_ylabel("Best R² (Leave-One-Phase-Out)")
    ax.set_title("A) Cross-Phase Transfer R²")
    ax.set_ylim(-0.45, 0.75)
    
    # Annotation for worst direction
    ax.annotate("Unseen medium +\ntechnique shift",
                xy=(0, best_r2[0] - 0.02), xytext=(0.3, -0.35),
                fontsize=10, color=WARM_RED, fontstyle="italic",
                arrowprops=dict(arrowstyle="->", color=WARM_RED, lw=1.5))
    
    # Panel B: MAE by direction
    ax = axes[1]
    best_mae = []
    for train, test in directions:
        sub = lopo[lopo["Train_phases"] == train]
        best = sub.loc[sub["R2"].idxmax()]
        best_mae.append(best["MAE"])
    
    bars = ax.bar(dir_labels, best_mae, color=dir_colours, edgecolor="white",
                  linewidth=2, width=0.55)
    
    for bar, mae in zip(bars, best_mae):
        ax.text(bar.get_x() + bar.get_width()/2, mae + 1.5,
                f"MAE = {mae:.1f}", ha="center", va="bottom",
                fontsize=13, fontweight="bold")
    
    ax.set_ylabel("Best MAE (mm/yr)")
    ax.set_title("B) Cross-Phase Transfer MAE")
    
    fig.suptitle("Leave-One-Phase-Out: Transfer is Direction-Dependent",
                 fontsize=18, fontweight="bold", y=1.02)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "poster_06_leave_one_phase_out_transfer.png")
    plt.close(fig)
    print("  [OK] poster_06_leave_one_phase_out_transfer.png")


# ===================================================================
# Figure 7: Error by Phase / Segment
# ===================================================================
def fig07_error_by_phase():
    es = pd.read_csv(OUT / "error_stratification.csv")
    
    fig, axes = plt.subplots(1, 3, figsize=(16, 6))
    
    # Panel A: By Phase
    ax = axes[0]
    phase_data = es[es["Stratify_by"] == "Phase_Group"].sort_values("MAE")
    colours_p = [PHASE_COLOURS.get(v, SLATE) for v in phase_data["Value"]]
    bars = ax.bar(phase_data["Value"], phase_data["MAE"],
                  yerr=phase_data["MAE_std"], capsize=6,
                  color=colours_p, edgecolor="white", linewidth=1.5, width=0.5,
                  error_kw={"linewidth": 2, "capthick": 2, "ecolor": SLATE})
    for bar, mae in zip(bars, phase_data["MAE"]):
        ax.text(bar.get_x() + bar.get_width()/2, mae + phase_data["MAE_std"].max() * 0.1 + 3,
                f"{mae:.1f}", ha="center", va="bottom", fontsize=12, fontweight="bold")
    ax.set_ylabel("MAE (mm/yr)")
    ax.set_title("A) By Phase")
    
    # Panel B: By Technique / Medium
    ax = axes[1]
    tech_data = es[es["Stratify_by"] == "Technique"]
    med_data  = es[es["Stratify_by"] == "Medium_Type"]
    combined = pd.concat([tech_data, med_data])
    labels_c = [f"{row['Stratify_by']}\n{row['Value']}" for _, row in combined.iterrows()]
    colours_c = [TEAL, CORAL, DEEP_BLUE, WARM_RED]
    bars = ax.bar(range(len(combined)), combined["MAE"],
                  yerr=combined["MAE_std"], capsize=6,
                  color=colours_c[:len(combined)], edgecolor="white", linewidth=1.5, width=0.55,
                  error_kw={"linewidth": 2, "capthick": 2, "ecolor": SLATE})
    ax.set_xticks(range(len(combined)))
    ax.set_xticklabels(labels_c, fontsize=9, rotation=15, ha="right")
    for bar, mae in zip(bars, combined["MAE"]):
        ax.text(bar.get_x() + bar.get_width()/2, mae + 5,
                f"{mae:.1f}", ha="center", va="bottom", fontsize=12, fontweight="bold")
    ax.set_title("B) By Technique / Medium")
    
    # Panel C: By Temperature Bin
    ax = axes[2]
    temp_data = es[es["Stratify_by"] == "temp_bin"]
    temp_order = ["<=40C", "40-60C", ">60C"]
    temp_data = temp_data.set_index("Value").loc[temp_order].reset_index()
    colours_t = [MINT, GOLD, WARM_RED]
    bars = ax.bar(temp_data["Value"], temp_data["MAE"],
                  yerr=temp_data["MAE_std"], capsize=6,
                  color=colours_t, edgecolor="white", linewidth=1.5, width=0.5,
                  error_kw={"linewidth": 2, "capthick": 2, "ecolor": SLATE})
    for bar, mae in zip(bars, temp_data["MAE"]):
        ax.text(bar.get_x() + bar.get_width()/2, mae + 5,
                f"{mae:.1f}", ha="center", va="bottom", fontsize=12, fontweight="bold")
    ax.set_title("C) By Temperature")
    
    fig.suptitle("Error Stratification: Where the Pooled Model Fails\n(Error concentrates in P3 / Tafel / Basic / High Temperature)",
                 fontsize=17, fontweight="bold", y=1.04)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "poster_07_error_by_phase.png")
    plt.close(fig)
    print("  [OK] poster_07_error_by_phase.png")


# ===================================================================
# Main
# ===================================================================
if __name__ == "__main__":
    print("Generating poster-ready figures...")
    print(f"Output directory: {FIG_DIR}\n")
    
    fig01_correlation_by_phase()
    fig02_ea_convergence()
    fig03_ea_sensitivity()
    fig04_permutation_importance()
    fig05_standard_vs_grouped_cv()
    fig06_leave_one_phase_out()
    fig07_error_by_phase()
    
    print(f"\nAll 7 poster figures saved to {FIG_DIR}/poster_*.png")
    print("Original figures (01_*.png - 07_*.png) are preserved.")
