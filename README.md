# What Changes, and What Remains Consistent, When Corrosion Conditions Change?
## An Experimental and Machine Learning Study of Green Inhibitors for Mild Steel

Green plant-derived corrosion inhibitors are promising sustainable alternatives to toxic synthetic compounds, but their performance depends on operating conditions — temperature, exposure time, solution chemistry, and inhibitor dosage. When these conditions change, which aspects of corrosion behaviour remain consistent across different green inhibitor systems, and which aspects shift?

This study addresses that question by unifying three experimental phases from one in-house laboratory programme into a single analytical framework, combining Arrhenius activation-energy analysis (experimental/physical) with machine learning models (predictive/methodological) across a harmonized 302-observation dataset.

## Research Architecture

The work is organized as:

```text
                    UNIFIED STUDY
                         |
              +----------+----------+
              |                     |
        CORE EVIDENCE         STRESS TEST
           P1 + P2                P3
              |                     |
     Comparable gravimetric   Different experimental/
     inhibitor systems        measurement regime
              |                     |
              +----------+----------+
                         |
                         v
              302-observation harmonized dataset
                         |
              +----------+----------+----------+
              |          |          |          |
          Shared     Conditional  Predictive  Robustness
          physical   environmental behaviour  under regime
          behaviour  behaviour               shift
```

The phases are harmonized into one analytical framework, but they are not treated as statistically interchangeable. P1 and P2 form the **core evidence** for cross-system conclusions: both use gravimetric weight-loss measurement, comparable temperature ranges, and HCl media. P3 serves as a **measurement/experimental-regime stress test** that changes several things simultaneously — inhibitor system, measurement technique, medium, experimental structure, sample size, and studied ranges — making it unsuitable for equal-weight comparison with P1/P2 but valuable for probing the robustness of learned relationships under regime shift.

## Experimental Phases

### Phase 1: Ternary Green Inhibitor Blend

- **Inhibitor:** Bitter Leaf extract (BL), Plantain Peel extract (PP), and Snail Water (SW)
- **Technique:** Gravimetric weight loss
- **Sub-studies:**
  - Temperature: 40-80 °C
  - Time: 25-125 hours
  - DoE blend optimization using BL, PP, and SW volumes
- **DoE dosage unit:** mL of blend, not ppm
- **Standalone DoE result:** approximately 1.64 mm/year corrosion rate and 87.6% inhibition efficiency at the identified optimum

### Phase 2: Single Green Inhibitor

- **Inhibitor:** Single green inhibitor from the earlier screening phase
- **Technique:** Gravimetric weight loss
- **Medium:** HCl at 0.5M, 1.0M, and 1.5M
- **Sub-studies:**
  - Temperature: 30-70 °C
  - Time: 3-15 hours
- **Dosage:** ppm

### Phase 3: Okro Leaf Extract

- **Inhibitor:** Okro/okra leaf extract
- **Technique:** Tafel polarization with electrochemical measurements
- **Media:** HCl and NaOH
- **Temperature:** 30-60 °C
- **Dosage:** 50-200 ppm
- **Sample size:** 17 observations per medium
- **Role in the unified study:** Measurement/experimental-regime stress test. P3 changes inhibitor system, measurement technique, medium, experimental structure, sample size, and studied ranges/distributions simultaneously relative to P1/P2 — these factors are partly confounded. P3 is not used as equal-weight evidence alongside the gravimetric phases

## Research Questions

### RQ1: Scientific Convergence

Do independently tested green inhibitor systems exhibit consistent temperature-dependent corrosion behaviour?

The primary evidence is the Arrhenius activation-energy comparison between the two temperature-varying gravimetric phases, P1 and P2.

### RQ2: Environmental Drivers

How does the dominant predictor of corrosion rate change with temperature, exposure time, inhibitor concentration, and solution chemistry?

Predictor dominance is assessed using three layers:

1. Correlation analysis
2. Permutation importance
3. Feature ablation

Temperature is not claimed to be universally dominant. The three evidence layers agree for the P1 and P2 gravimetric temperature phases, while P3 produces mixed or inconclusive evidence.

### RQ3: Cross-Phase Generalization

Can a model trained on some experimental phases predict a phase that it has not seen?

This is tested using grouped cross-validation and leave-one-phase-out experiments.

### RQ4: Measurement Robustness

How does changing from gravimetric weight loss to Tafel electrochemical measurement affect predictive reliability?

P3 is used to test measurement-regime shift and transferability. Poor P3 model performance is not interpreted as proof that Okro extract is an inferior inhibitor.

## Unified Dataset

The master dataset contains 302 observations across seven sub-phases:

| Sub-phase | Observations |
|---|---:|
| P1-Temperature | 30 |
| P1-Time | 30 |
| P1-DoE-Blend | 28 |
| P2-Temperature | 90 |
| P2-Time | 90 |
| P3-Okro-Acid | 17 |
| P3-Okro-Basic | 17 |
| **Total** | **302** |

### Dose Schema

The schema prevents invalid comparisons between mL and ppm:

| Field | Meaning |
|---|---|
| `Dose_Value` | Original numeric dose value in its native unit |
| `Dose_Unit` | `ppm` or `mL_blend` |
| `Concentration_ppm` | Populated only for ppm-based observations |
| `Phase_Group` | `P1`, `P2`, or `P3` |

P1-DoE rows retain their blend volume in `Dose_Value` with `Dose_Unit = mL_blend`; they have no manufactured ppm equivalent. The code excludes them from ppm-based dosage-efficiency rankings.

## Main Findings

### Activation-Energy Convergence

The two temperature-varying gravimetric phases produced:

| Phase | Mean Ea | Dose groups |
|---|---:|---:|
| P1 ternary blend | 61.1 ± 10.6 kJ/mol | 6 |
| P2 single inhibitor | 66.5 ± 16.6 kJ/mol | 6 |

Formal comparison:

- Difference: 5.4 kJ/mol
- Welch's t-test: p = 0.52
- Mann-Whitney U test: p = 0.70
- Cohen's d: -0.39

The estimates are not statistically distinguishable within the uncertainty of the fitted dose-group estimates. This convergence is described as consistent with a surface-coverage or adsorption-dominated interpretation, not as proof of a mechanism because adsorption-isotherm data were not collected.

P3 activation-energy fits are reported separately but excluded from the headline convergence claim because they are unstable:

- P3 acidic: 11.2 ± 9.7 kJ/mol
- P3 basic: -180.2 ± 513.4 kJ/mol

### Predictor Behaviour

- Temperature dominates the P1 and P2 temperature-varying gravimetric phases.
- Dose/concentration dominates the P1 and P2 time-varying phases.
- P3 predictor evidence is mixed and no universal dominant factor is claimed.

### Validation Leakage

Standard random cross-validation substantially overestimates performance because structured experimental conditions and replicate measurements can be split across training and validation sets.

Grouped validation produces more conservative results. For example:

| Configuration | Model | Standard CV R² | Grouped CV R² |
|---|---|---:|---:|
| P1 | XGBoost | 0.983 | 0.372 |
| P2 | Random Forest | 0.965 | -0.236 |
| P1 + P2 | CatBoost | 0.971 | 0.421 |
| P1 + P2 + P3 | CatBoost | 0.608 | 0.041 |

Grouped CV is the more defensible basis for generalization claims.

### Cross-Phase Transfer

Leave-one-phase-out results are direction-dependent:

| Training phases | Held-out phase | Best observed R² | Best observed MAE |
|---|---|---:|---:|
| P1 + P2 | P3 | -0.24 | 83.7 |
| P1 + P3 | P2 | 0.40 | 40.0 |
| P2 + P3 | P1 | 0.57 | 34.2 |

The P1 + P2 → P3 direction requires extrapolation in molarity and an entirely unseen medium (NaOH), combined with a different measurement technique, inhibitor system, and experimental structure. Cross-phase generalization is therefore not equivalent to universal prediction of arbitrary unseen inhibitor chemistries. The P3 transfer result is best understood as a stress test of learned relationships under regime shift, not as a measure of core model adequacy.

### Adding P3 to the Pooled Model

Adding P3 to P1 + P2 decreases performance in most model and validation combinations. This is interpreted as evidence of experimental and measurement-regime shift — reflecting the multiple simultaneous differences between P3 and the gravimetric phases — not as a failure of the analysis pipeline.

### Error Concentration

Pooled-model error is not evenly distributed:

- P1 grouped-CV MAE: approximately 15.4 mm/year
- P2 grouped-CV MAE: approximately 30.3 mm/year
- P3 grouped-CV MAE: approximately 91.2 mm/year
- Basic-medium MAE: approximately 119.0 mm/year
- Tafel-measurement MAE: approximately 91.2 mm/year
- Above 60 °C MAE: approximately 131.3 mm/year

## Repository Contents

### Main Documentation

- [ABSTRACT.md](ABSTRACT.md) - formal abstract for poster submission, covering motivation, methodology, key results, and contributions
- [FINDINGS.md](FINDINGS.md) - comprehensive results document tracing every numerical claim to its source CSV file
- [Unified_Corrosion_Study_Walkthrough.ipynb](Unified_Analysis/Unified_Corrosion_Study_Walkthrough.ipynb) - end-to-end narrative notebook with tables, results, interpretations, and saved visual outputs

### Unified Analysis Scripts

- [build_master_dataset.py](Unified_Analysis/build_master_dataset.py) - harmonizes all seven sub-phases and enforces the dose schema
- [data_quality_audit.py](Unified_Analysis/data_quality_audit.py) - missingness, duplicates, invalid CR values, independence statement, and comparability matrix
- [ea_analysis.py](Unified_Analysis/ea_analysis.py) - formal P1/P2 activation-energy comparison and sensitivity analysis
- [predictor_ablation.py](Unified_Analysis/predictor_ablation.py) - correlation support, permutation importance, ablation, and interaction analysis
- [cross_phase_model_experiments.py](Unified_Analysis/cross_phase_model_experiments.py) - Models A-G, grouped CV, phase-identity ablation, model comparison, and leave-one-phase-out testing
- [rigor_extension.py](Unified_Analysis/rigor_extension.py) - replicate structure, interpolation/extrapolation, target leakage, null testing, repeated validation, error stratification, and model simplicity
- [generate_poster_figures.py](Unified_Analysis/generate_poster_figures.py) - poster-ready figure generation with professional styling, consistent colour palette, and 300 DPI output

### Key Data Outputs

- [master_corrosion_dataset.csv](Unified_Analysis/master_corrosion_dataset.csv)
- [data_quality_audit.csv](Unified_Analysis/data_quality_audit.csv)
- [comparability_matrix.csv](Unified_Analysis/comparability_matrix.csv)
- [correlation_comparison.csv](Unified_Analysis/correlation_comparison.csv)
- [arrhenius_activation_energy.csv](Unified_Analysis/arrhenius_activation_energy.csv)
- [ea_comparison.csv](Unified_Analysis/ea_comparison.csv)
- [ea_sensitivity.csv](Unified_Analysis/ea_sensitivity.csv)
- [model_leaderboard.csv](Unified_Analysis/model_leaderboard.csv)
- [leave_one_phase_out_results.csv](Unified_Analysis/leave_one_phase_out_results.csv)
- [permutation_null_test.csv](Unified_Analysis/permutation_null_test.csv)
- [repeated_cv_stability.csv](Unified_Analysis/repeated_cv_stability.csv)
- [error_stratification.csv](Unified_Analysis/error_stratification.csv)
- [model_simplicity_test.csv](Unified_Analysis/model_simplicity_test.csv)

### Saved Figures

All seven notebook figures are saved in [Unified_Analysis/figures/](Unified_Analysis/figures/), with poster-quality versions prefixed `poster_`:

1. Correlation by phase
2. Ea convergence headline figure
3. Ea jackknife sensitivity
4. Permutation importance by phase
5. Standard versus grouped cross-validation
6. Leave-one-phase-out transfer
7. Error by phase

Poster-ready versions use a consistent academic colour palette, 300 DPI resolution, annotated statistics, and bold typography suitable for conference presentation. Generate them with `python generate_poster_figures.py`.

## Reproducibility

From the repository root, configure a Python environment with the required packages:

```powershell
python -m pip install pandas numpy scipy scikit-learn statsmodels matplotlib openpyxl xgboost catboost jupyter nbconvert
```

Then run the unified pipeline:

```powershell
Set-Location Unified_Analysis
python build_master_dataset.py
python data_quality_audit.py
python ea_analysis.py
python predictor_ablation.py
python cross_phase_model_experiments.py
python rigor_extension.py
```

Open the walkthrough notebook in VS Code or Jupyter:

```powershell
jupyter notebook Unified_Corrosion_Study_Walkthrough.ipynb
```

The scripts write derived CSV outputs into `Unified_Analysis/`. The notebook reads those outputs, displays the tables and interpretations, and saves poster-ready PNG figures into `Unified_Analysis/figures/`.

**Pipeline authority:** The Python scripts listed above are the authoritative reproducible analysis pipeline. All numerical claims in this repository's documentation are derived from these scripts and their CSV outputs. The walkthrough notebook ([Unified_Corrosion_Study_Walkthrough.ipynb](Unified_Analysis/Unified_Corrosion_Study_Walkthrough.ipynb)) provides a narrative presentation of the same results and is useful for understanding the analysis flow, but should be treated as a companion walkthrough rather than the primary reproducibility mechanism.

## Evidence Tiers and Limitations

### Core Evidence: P1 and P2 Gravimetric Phases

P1 and P2 provide the core evidence for cross-system conclusions. Both use gravimetric weight-loss measurement in HCl at comparable temperature ranges (P1: 40–80°C, P2: 30–70°C, overlapping 40–70°C), enabling the strongest claims: activation-energy convergence, temperature/concentration regime comparison, and conditional environmental-driver behaviour.

### Stress Test: P3 Electrochemical/Experimental-Regime Shift

P3 serves as a stress test for the robustness of relationships established from the core P1/P2 evidence. P3 differs from P1/P2 in multiple simultaneous ways:

- **Inhibitor system:** Okro leaf extract (vs ternary blend and single green inhibitor)
- **Measurement technique:** Tafel polarization (vs gravimetric weight loss)
- **Medium:** HCl and NaOH (vs HCl only)
- **Experimental structure:** Different factorial design
- **Sample size:** 17 observations per medium (vs ~30–90 per P1/P2 sub-study)
- **Studied ranges/distributions:** Different molarity, temperature, and dose ranges

These differences are partly confounded, so P3's lower transfer performance cannot be attributed to any single factor. P3 has five non-positive corrosion-rate values in the basic dataset, further limiting its reliability for quantitative conclusions.

### Important Limitations

- The three phases use different inhibitor chemistries and cannot establish a universal inhibitor law.
- P1-DoE blend volume cannot be converted to ppm without validated composition/concentration data.
- P3 sample size is small and its Tafel-derived corrosion-rate distribution is unstable in basic media.
- Phase, inhibitor chemistry, and measurement technique are partly confounded in leave-one-phase-out testing.
- Cross-phase generalization is not the same as universal prediction of unseen inhibitor chemistries.
- No adsorption isotherm or adsorption thermodynamic data were collected, so mechanistic claims remain interpretation-consistent rather than proven.
- No claim is made about extrapolating beyond the studied temperature, time, dose, molarity, or medium ranges.

## Final Research Position

The contribution of this work is not simply that machine learning can predict corrosion rate. The unified analysis answers a two-part question: *"What remains consistent when corrosion conditions change, and what shifts?"*

**What remains consistent** (from the core evidence, P1 + P2):

1. **Activation energy converges** — two independently formulated green inhibitor systems produce statistically indistinguishable apparent activation energies (~61–67 kJ/mol, Welch's t p = 0.52), the strongest single result.
2. **Environmental-driver patterns are reproducible** — temperature dominates in temperature-varying gravimetric phases, concentration dominates in time-varying phases, confirmed by three independent evidence layers (correlation, permutation importance, ablation).
3. **Validation leakage is systematic** — structured experimental replicates inflate standard CV by 0.5–1.2 R² units in every configuration, a methodological insight applicable beyond this specific study.

**What changes** (from the stress test, P3, and conditional analysis):

4. **Predictor dominance shifts** with experimental design — the "most important factor" is not universal but depends on which variable was varied.
5. **Cross-phase transfer is direction-dependent** — models trained on gravimetric data fail on Tafel data (R² = −0.24), while the reverse direction transfers moderately (R² = 0.57).
6. **Error concentrates in specific regimes** — P3, basic medium, Tafel measurement, and high temperature produce the largest prediction failures, reported transparently rather than hidden behind one global score.

All claims should be read together with the [FINDINGS.md](FINDINGS.md) document, which traces every numerical result to its source CSV file.
