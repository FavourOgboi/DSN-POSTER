# What Changes, and What Remains Consistent, When Corrosion Conditions Change? An Experimental and Machine Learning Study of Green Inhibitors for Mild Steel

**Author:** Favour Ogboi  
**Affiliation:** Data Science Nigeria (DSN) AI Bootcamp 2026 — Poster Submission  
**Repository:** [GitHub — DSN Poster](https://github.com/FavourOgboi/DSN-POSTER)

---

## Abstract

Green plant-derived corrosion inhibitors offer a sustainable alternative to toxic synthetic compounds for protecting mild steel in aggressive chemical environments, but their performance depends on operating conditions — temperature, exposure time, solution chemistry, and inhibitor dosage. When these conditions change, which aspects of corrosion behaviour remain consistent across different green inhibitor systems, and which aspects shift? Most machine learning studies in this domain examine a single inhibitor under one experimental condition using one measurement technique, making it impossible to answer this question: apparent accuracy may reflect genuine physical understanding or merely memorization of a single experimental regime. This study addresses that gap by unifying three experimental phases — a ternary blend of bitter leaf, plantain peel, and snail water extracts (P1); a single green inhibitor screened from our earlier work (P2); and an okro (okra) leaf extract tested electrochemically (P3) — all conducted within one in-house laboratory programme on mild steel, into a harmonized 302-observation dataset spanning seven sub-phases.

The headline answer to "what remains consistent" is a formally tested activation-energy convergence between the two gravimetric phases: P1 and P2 independently yield apparent Arrhenius activation energies of 61.1 ± 10.6 kJ/mol and 66.5 ± 16.6 kJ/mol respectively — a difference of only 5.4 kJ/mol that is not statistically distinguishable (Welch's t-test p = 0.52, Mann–Whitney U p = 0.70, Cohen's d = −0.39), and remains stable under leave-one-dose-group-out jackknife sensitivity analysis (P1 range: 59.1–64.8 kJ/mol; P2 range: 61.7–70.7 kJ/mol). This convergence around 61–67 kJ/mol, despite the two systems using entirely different inhibitor chemistries, is consistent with a surface-coverage or adsorption-dominated inhibition mechanism — though no adsorption isotherm data were collected, so no stronger mechanistic claim is made.

The answer to "what changes" emerges from three additional lines of evidence. First, **conditional environmental-driver behaviour**: temperature dominates corrosion rate prediction in the temperature-varying gravimetric phases (Pearson r = 0.907 for P1, r = 0.770 for P2), while inhibitor concentration dominates in the time-varying phases (r = −0.696 for P1, r = −0.587 for P2) — the "most important factor" is not universal but shifts with experimental design, each confirmed independently by correlation analysis, permutation importance, and feature ablation, with all three layers required to agree before a factor is declared dominant. Second, **validation leakage quantification**: standard random cross-validation dramatically overestimates model performance (e.g., XGBoost R² drops from 0.983 to 0.372 on P1, Random Forest from 0.965 to −0.236 on P2) when replaced by grouped cross-validation that prevents structured experimental replicates from leaking across train–test splits — a methodological finding relevant to any ML study built on structured laboratory data. Third, **cross-phase transfer asymmetry**: leave-one-phase-out experiments reveal that generalization is direction-dependent (P2+P3 → P1: R² = 0.57; P1+P3 → P2: R² = 0.40; P1+P2 → P3: R² = −0.24), with the worst direction requiring simultaneous extrapolation into an unseen medium (NaOH) and a different measurement technique (Tafel polarization).

The electrochemical phase (P3) is deliberately positioned as a measurement and experimental-regime stress test rather than equal-weight evidence: it changes inhibitor system, measurement technique, medium, experimental structure, sample size, and studied ranges simultaneously relative to the gravimetric phases, making its lower transfer performance attributable to the cumulative regime shift rather than any single factor. P3's own Arrhenius fits are too unstable for inclusion in the convergence claim (basic-medium per-dose-group Ea values range from −897 to +280 kJ/mol), and are reported transparently rather than suppressed.

All analyses are reproducible from a public GitHub repository containing the harmonized dataset, seven Python pipeline scripts, 22 CSV output files, and a narrative Jupyter notebook, with every numerical claim traceable to its source file and a 32-question reviewer-challenge audit documenting the evidence status of each conclusion.

---

## Keywords

Green corrosion inhibitors · Mild steel · Machine learning · Arrhenius activation energy · Cross-phase generalization · Grouped cross-validation · Validation leakage · Weight-loss gravimetric · Tafel polarization · Design of Experiments

---

## 1. Motivation and Problem Context

Industrial infrastructure — pipelines, heat exchangers, reaction vessels, storage tanks — suffers accelerated corrosion when exposed to acidic or basic media under fluctuating temperature and variable exposure duration. The annual global cost of corrosion exceeds $2.5 trillion (NACE International), and mild steel, the most widely used structural alloy, is particularly vulnerable.

Conventional synthetic inhibitors (chromates, phosphates, nitrites) are effective but environmentally toxic, increasingly regulated, and difficult to dispose of safely. **Green, plant-derived inhibitors** — extracts of bitter leaf (*Vernonia amygdalina*), plantain peel (*Musa paradisiaca*), snail water (*Achatina fulica*), and okro/okra leaf (*Abelmoschus esculentus*) — represent a sustainable alternative, but their protective performance is highly sensitive to operating conditions:

- **Temperature**: inhibitor films degrade above critical thresholds, drastically reducing efficiency
- **Exposure time**: prolonged contact may exhaust adsorbed inhibitor layers
- **Solution chemistry**: acid vs. base medium, and concentration, alter the corrosion mechanism
- **Inhibitor dosage**: optimal dose depends on the interaction of all the above

The fundamental engineering question is: *when conditions change, can we still trust the inhibitor — and the model that predicts its performance?*

Most published ML-for-corrosion studies answer this question in one narrow setting: one inhibitor, one medium, one measurement technique, one validation scheme. This makes it impossible to distinguish whether a model's apparent accuracy reflects genuine physical understanding or merely memorization of a single experimental regime.

---

## 2. What This Study Does Differently

This work unifies **three experimental phases** from one continuous in-house laboratory programme into a single analytical framework, deliberately structured as **core evidence** plus a **stress test**:

### Core Evidence: P1 + P2 (Gravimetric Weight-Loss Phases)

| | Phase 1: Ternary Blend | Phase 2: Single Green Inhibitor |
|---|---|---|
| **Inhibitor** | Bitter Leaf + Plantain Peel + Snail Water (3-component blend) | Single green inhibitor from earlier screening |
| **Technique** | Gravimetric weight loss | Gravimetric weight loss |
| **Medium** | 1M HCl | HCl at 0.5M, 1.0M, 1.5M |
| **Temperature** | 40–80 °C | 30–70 °C |
| **Time** | 25–125 hours | 3–15 hours |
| **Dosage** | ppm (temp/time sub-studies); mL blend (DoE) | ppm |
| **Observations** | 88 (across 3 sub-studies) | 180 (across 2 sub-studies) |

These two phases use the **same measurement technique** (weight loss) in the **same class of medium** (HCl) at **overlapping temperature ranges** (40–70 °C overlap), enabling the strongest cross-system comparison.

### Stress Test: P3 (Electrochemical Phase)

| | Phase 3: Okro Leaf Extract |
|---|---|
| **Inhibitor** | Okro (okra) leaf extract |
| **Technique** | Tafel polarization (electrochemical) |
| **Medium** | HCl *and* NaOH (1.0–2.5M) |
| **Temperature** | 30–60 °C |
| **Dosage** | 50–200 ppm |
| **Observations** | 34 (17 per medium) |

P3 changes **six things simultaneously** relative to P1/P2: inhibitor system, measurement technique, medium, experimental structure, sample size, and studied ranges. These differences are partly confounded — P3's results cannot be attributed to any single factor, which is precisely why it functions as a **regime-shift stress test** rather than a third piece of equivalent evidence.

### The Unified Dataset

302 observations across 7 sub-phases, harmonized with a schema that structurally separates mL-blend dosage from ppm dosage (preventing invalid cross-unit comparisons), flags non-positive corrosion rates rather than silently deleting them, and preserves every experimental identifier needed for grouped validation.

---

## 3. Research Questions

**RQ1 — Scientific Convergence:** Do independently tested green inhibitor systems exhibit consistent temperature-dependent corrosion behaviour?

**RQ2 — Environmental Drivers:** How does the dominant predictor of corrosion rate change across experimental conditions? Is temperature always the most important factor?

**RQ3 — Cross-Phase Generalization:** Can a model trained on some experimental phases predict a phase it has never seen?

**RQ4 — Measurement Robustness:** How does switching from gravimetric weight-loss to Tafel electrochemical measurement affect predictive reliability?

---

## 4. Methodology

### 4.1 Data Harmonization

Raw weight-loss tables and Tafel polarization data from all three phases were merged into one 302-row master dataset via a reproducible Python pipeline (`build_master_dataset.py`). The schema enforces:

- **Dose separation**: `Dose_Value` + `Dose_Unit` (`ppm` or `mL_blend`), with `Concentration_ppm` populated only for ppm-based observations — the DoE blend volumes are never manufactured into fake ppm equivalents
- **Phase identity**: `Phase_Group`, `Inhibitor_System`, `Technique`, `Medium_Type` retained as explicit features
- **Quality flags**: missing values, duplicates, and non-positive corrosion rates documented in a data-quality audit (5 non-positive CR values in P3 basic-medium data are flagged, not deleted)

### 4.2 Activation-Energy Analysis (RQ1)

Arrhenius fits (ln(CR) vs. 1/T) computed per dose group within each temperature-varying phase. P1 and P2 formally compared via:

- Welch's t-test and Mann–Whitney U test (parametric + non-parametric)
- Cohen's d effect size
- Leave-one-dose-group-out jackknife sensitivity (does any single dose group drive the convergence?)

P3 Arrhenius fits computed but reported separately due to fit instability.

### 4.3 Predictor Dominance (RQ2)

Three independent evidence layers, all required to agree before a factor is called "dominant":

1. **Pearson correlation** of CR with each environmental variable
2. **Permutation importance** from fitted Random Forest models
3. **Feature ablation** — R² drop when each variable is removed

Plus an OLS interaction term (`Dose × Temperature`) to test whether concentration modifies the temperature effect.

### 4.4 Machine Learning Models (RQ3, RQ4)

Four model families: Ridge, Random Forest, XGBoost, CatBoost — tested across seven configurations (Models A–G):

- **A**: P1 alone | **B**: P2 alone | **C**: P3 alone
- **D**: P1+P2 | **E**: P1+P2+P3
- **F**: P1+P2 without identity features | **G**: P1+P2+P3 without identity features

Each evaluated under **standard 5-fold CV** and **grouped CV** (groups defined by rounded Study+Dose+Temp+Time condition, preventing near-duplicate structured replicates from splitting across train/test).

**Leave-one-phase-out (LOPO):** train on two phases, test entirely on the unseen third — the most stringent generalization test.

### 4.5 Extended Rigor Checks

- Replicate structure verification (P2's 90 rows = 30 conditions × 3 replicates each)
- Interpolation vs. extrapolation classification for each LOPO direction
- Target leakage confirmation (IE% is mathematically derived from CR — verified to within 0.28 pp on 150 P2 comparisons)
- Permutation null test (shuffled-target sanity check, empirical p ≈ 0.048)
- Repeated CV stability (5 reshuffled fold assignments)
- Error stratification by phase, technique, medium, and temperature band
- Model complexity justification (Ridge baseline comparison)

---

## 5. Key Results

### 5.1 Activation-Energy Convergence (The Headline Finding)

| Phase | Mean Ea (kJ/mol) | SD | Dose Groups |
|---|---:|---:|---:|
| P1 — Ternary Blend | 61.1 | 10.6 | 6 |
| P2 — Single Green Inhibitor | 66.5 | 16.6 | 6 |

- **Difference**: 5.4 kJ/mol (SE = 8.0)
- **Welch's t-test**: p = 0.52 (not statistically distinguishable)
- **Mann–Whitney U**: p = 0.70
- **Cohen's d**: −0.39 (small-to-moderate effect)
- **Jackknife stability**: P1 range 59.1–64.8, P2 range 61.7–70.7 — no single dose group drives the convergence

**Interpretation**: Two independently formulated green inhibitor systems, tested via the same measurement technique under comparable conditions, produce statistically indistinguishable apparent activation energies. This is consistent with adsorption-dominated inhibition, but no adsorption isotherm data were collected, so no mechanistic proof is claimed.

### 5.2 Conditional Predictor Dominance

| Phase | Dominant Factor | All 3 Layers Agree? |
|---|---|---|
| P1-Temperature | Temperature (r = 0.907) | ✓ |
| P2-Temperature | Temperature (r = 0.770) | ✓ |
| P1-Time | Concentration (r = −0.696) | ✓ |
| P2-Time | Concentration (r = −0.587) | ✓ |
| P3-Acid | Mixed | ✗ — no claim made |
| P3-Basic | Mixed | ✗ — no claim made |

Temperature dominance is **not universal** — it is conditional on the experimental phase. The study's own data does not support a blanket "temperature is always the most important factor" claim.

### 5.3 Validation Leakage (A Methodological Warning)

| Config | Model | Standard CV R² | Grouped CV R² | R² Inflation |
|---|---|---:|---:|---:|
| P1 | XGBoost | 0.983 | 0.372 | +0.611 |
| P2 | Random Forest | 0.965 | −0.236 | +1.201 |
| P1+P2 | CatBoost | 0.971 | 0.421 | +0.550 |
| P1+P2+P3 | CatBoost | 0.608 | 0.041 | +0.567 |

Standard random CV leaks structured experimental replicates and near-duplicate conditions across train–test splits, inflating apparent performance by **0.5–1.2 R² units**. This is not a quirk of this dataset — it is a systematic risk in any ML study built on structured factorial laboratory data.

### 5.4 Cross-Phase Transfer (Direction-Dependent)

| Training Phases | Held-Out Phase | Best R² | Best MAE |
|---|---|---:|---:|
| P2 + P3 → | P1 | 0.57 | 34.2 |
| P1 + P3 → | P2 | 0.40 | 40.0 |
| P1 + P2 → | P3 | −0.24 | 83.7 |

The asymmetry is explained by interpolation/extrapolation analysis:

- **P1+P2 → P3 fails** because it must extrapolate into an entirely unseen medium (NaOH) and higher molarity range, combined with a different measurement technique
- **P2+P3 → P1 succeeds best** because it only requires temperature and time extrapolation, not medium or dose extrapolation

### 5.5 Error Concentration (Where the Model Fails)

| Region | MAE (mm/yr) | Multiplier vs. Best |
|---|---:|---:|
| P1 (gravimetric, core) | 15.4 | 1.0× (baseline) |
| P2 (gravimetric, core) | 30.3 | 2.0× |
| P3 (Tafel, stress test) | 91.2 | 5.9× |
| Basic medium only | 119.0 | 7.7× |
| Above 60 °C | 131.3 | 8.5× |

Global performance metrics hide these systematic regional weaknesses. The study reports them transparently.

---

## 6. What This Means (The Contribution)

This study does **not** simply claim "ML can predict corrosion rate." It answers a two-part question: *what remains consistent when corrosion conditions change, and what shifts?*

### What Remains Consistent

1. **A physically meaningful cross-system convergence** — two different green inhibitor chemistries produce statistically indistinguishable activation energies (61–67 kJ/mol) under comparable gravimetric conditions, the strongest single result
2. **Reproducible environmental-driver patterns** — temperature dominates only in the temperature-varying gravimetric phases; concentration dominates elsewhere; this conditional pattern is confirmed independently in both P1 and P2
3. **Systematic validation leakage** — standard CV inflates corrosion-ML performance by 0.5–1.2 R² units whenever structured replicates are present, a finding that holds across all model families and configurations

### What Changes

4. **Predictor dominance is conditional, not universal** — the "most important factor" shifts from temperature to concentration depending on which variable was varied in the experimental design
5. **Cross-phase transfer is direction-dependent** — models trained on gravimetric data fail on Tafel data (R² = −0.24), while the reverse direction transfers moderately (R² = 0.57)
6. **Error concentrates in specific regimes** — the specific regions where models fail (Tafel, basic medium, high temperature) are identified and reported transparently, not hidden behind one global score
7. **P3 serves as a stress test** — demonstrating what happens when the experimental and measurement regime shifts, rather than pretending all three phases are equivalent

---

## 7. Limitations (Stated Honestly)

- The three phases use **different inhibitor chemistries** — activation-energy convergence does not establish a universal inhibitor law
- P1-DoE blend volumes (**mL**) cannot be converted to **ppm** without validated composition data — the DoE result stands alone
- P3 has only **17 observations per medium** with **5 non-positive CR values** in basic media — too small and unstable for strong conclusions
- Phase, inhibitor chemistry, and measurement technique are **partly confounded** in leave-one-phase-out testing — cross-phase generalization ≠ unseen-inhibitor-chemistry generalization
- **No adsorption isotherm** or thermodynamic data were collected — mechanistic claims remain consistent interpretations, not proofs
- No claim is made about extrapolation beyond studied temperature, time, dose, molarity, or medium ranges

---

## 8. Reproducibility

The entire analysis is reproducible from the public GitHub repository:

```
pip install pandas numpy scipy scikit-learn statsmodels matplotlib xgboost catboost

cd Unified_Analysis
python build_master_dataset.py          # → master_corrosion_dataset.csv (302 rows)
python data_quality_audit.py            # → data_quality_audit.csv, comparability_matrix.csv
python ea_analysis.py                   # → arrhenius_activation_energy.csv, ea_comparison.csv, ea_sensitivity.csv
python predictor_ablation.py            # → correlation_comparison.csv, predictor_ablation.csv, interaction_effects.csv
python cross_phase_model_experiments.py # → model_leaderboard.csv, leave_one_phase_out_results.csv, + 5 more CSVs
python rigor_extension.py              # → replicate_structure.csv, error_stratification.csv, + 5 more CSVs
```

Every numerical claim in this abstract traces to a specific CSV output file. The [FINDINGS.md](FINDINGS.md) document maps each result to its source data.

---

## 9. Future Work

- Combined temperature × time × medium factorial design to decouple currently confounded variables
- Increased Tafel replicates before attempting P3-specific activation-energy or ML claims
- Adsorption isotherm studies to move from "consistent with adsorption" to mechanistic proof
- Field/pilot-scale validation under real industrial conditions
- A study design that decouples "new phase" from "new inhibitor chemistry" for a true unseen-inhibitor generalization test

---

*This abstract was prepared for submission to the Data Science Nigeria (DSN) AI Bootcamp 2026 poster track. The full reproducible analysis, harmonized dataset, pipeline scripts, and reviewer-challenge audit are available at the linked GitHub repository.*
