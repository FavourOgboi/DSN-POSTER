# Unified Green Corrosion Inhibitor Study

A unified machine-learning and corrosion-science analysis of three experimental phases conducted within one in-house laboratory research programme.

The project investigates which corrosion relationships remain consistent across experiments, which depend on environmental conditions, and how measurement technique and experimental structure affect machine-learning reliability.

## Research Architecture

The work is organized as:

```text
Three experimental phases
        |
        v
302-observation harmonized dataset
        |
        +--> Shared physical behaviour
        |    Arrhenius activation-energy comparison
        |
        +--> Conditional environmental behaviour
        |    Temperature, time, dose, and medium analyses
        |
        +--> Predictive and measurement behaviour
             Cross-phase ML, grouped validation, and held-out phases
```

The phases are harmonized into one analytical framework, but they are not treated as statistically interchangeable. The programme preserves differences in inhibitor chemistry, dosage units, measurement technique, medium, temperature range, exposure time, and sample size.

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
- **Role in the unified study:** Exploratory measurement and cross-phase generalization stress test, not equal-weight validation of the gravimetric phases

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

The P1 + P2 to P3 direction requires extrapolation in molarity and an unseen basic medium. Cross-phase generalization is therefore not equivalent to universal prediction of arbitrary unseen inhibitor chemistries.

### Adding P3 to the Pooled Model

Adding P3 to P1 + P2 decreases performance in most model and validation combinations. This is interpreted as evidence of measurement and distribution shift, not as a failure of the analysis pipeline.

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

- [POSTER_RESEARCH_SYNTHESIS.md](POSTER_RESEARCH_SYNTHESIS.md) - research framing, methodology, findings, poster structure, and conclusions
- [REVIEWER_CHALLENGES.md](REVIEWER_CHALLENGES.md) - reviewer-question and resolution audit with evidence status, scripts, outputs, and limitations
- [Unified_Corrosion_Study_Walkthrough.ipynb](Unified_Analysis/Unified_Corrosion_Study_Walkthrough.ipynb) - end-to-end narrative notebook with tables, results, interpretations, and saved visual outputs

### Unified Analysis Scripts

- [build_master_dataset.py](Unified_Analysis/build_master_dataset.py) - harmonizes all seven sub-phases and enforces the dose schema
- [data_quality_audit.py](Unified_Analysis/data_quality_audit.py) - missingness, duplicates, invalid CR values, independence statement, and comparability matrix
- [ea_analysis.py](Unified_Analysis/ea_analysis.py) - formal P1/P2 activation-energy comparison and sensitivity analysis
- [predictor_ablation.py](Unified_Analysis/predictor_ablation.py) - correlation support, permutation importance, ablation, and interaction analysis
- [cross_phase_model_experiments.py](Unified_Analysis/cross_phase_model_experiments.py) - Models A-G, grouped CV, phase-identity ablation, model comparison, and leave-one-phase-out testing
- [rigor_extension.py](Unified_Analysis/rigor_extension.py) - replicate structure, interpolation/extrapolation, target leakage, null testing, repeated validation, error stratification, and model simplicity

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

All seven notebook figures are saved in [Unified_Analysis/figures/](Unified_Analysis/figures/):

1. Correlation by phase
2. Ea convergence headline figure
3. Ea jackknife sensitivity
4. Permutation importance by phase
5. Standard versus grouped cross-validation
6. Leave-one-phase-out transfer
7. Error by phase

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

## Evidence Tiers and Limitations

### Tier 1: P1 and P2 Gravimetric Evidence

Used for the strongest cross-system conclusions, especially activation-energy convergence and the temperature/concentration regime comparison.

### Tier 2: P3 Electrochemical Evidence

Used as exploratory evidence and a measurement/generalization stress test. P3 has only 17 observations per medium, a different measurement technique, a different medium structure, and five non-positive corrosion-rate values in the basic dataset.

### Important Limitations

- The three phases use different inhibitor chemistries and cannot establish a universal inhibitor law.
- P1-DoE blend volume cannot be converted to ppm without validated composition/concentration data.
- P3 sample size is small and its Tafel-derived corrosion-rate distribution is unstable in basic media.
- Phase, inhibitor chemistry, and measurement technique are partly confounded in leave-one-phase-out testing.
- Cross-phase generalization is not the same as universal prediction of unseen inhibitor chemistries.
- No adsorption isotherm or adsorption thermodynamic data were collected, so mechanistic claims remain interpretation-consistent rather than proven.
- No claim is made about extrapolating beyond the studied temperature, time, dose, molarity, or medium ranges.

## Final Research Position

The contribution of this work is not simply that machine learning can predict corrosion rate. The unified analysis identifies:

1. A formally tested activation-energy convergence between two independently formulated gravimetric inhibitor systems.
2. Conditional environmental-driver behaviour: temperature dominates in temperature-varying gravimetric phases, while dose dominates in time-varying phases.
3. The magnitude of validation leakage caused by structured experimental conditions and replicates.
4. Direction-dependent cross-phase transfer and the role of extrapolation and measurement shift.
5. The specific experimental regions where the pooled model fails, rather than hiding those failures behind one global score.

All claims should be read together with [REVIEWER_CHALLENGES.md](REVIEWER_CHALLENGES.md), which records whether each major claim is supported, conditional, not comparable, or out of scope.
