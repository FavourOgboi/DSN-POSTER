# Reviewer Challenge & Resolution Framework

*A living audit trail: every major scientific/methodological question a critical reviewer could raise about this unified corrosion-inhibitor study, mapped to the specific analysis that answers it (or the explicit limitation that admits it can't be answered yet). Status is only marked IMPLEMENTED once the Result/Conclusion fields below are filled with real numbers from the scripts in `Unified_Analysis/` -- no placeholder is left as a final answer.*

**Programme summary**: three experimental phases (P1 = ternary blend BL+PP+SW, weight loss; P2 = single green inhibitor, weight loss; P3 = Okro leaf extract, Tafel electrochemical) run within one in-house lab programme, harmonized into a 302-row master dataset (`Unified_Analysis/master_corrosion_dataset.csv`).

---

## 1. Why combine P1, P2, and P3 at all?

**Status:** IMPLEMENTED
**Script:** `Unified_Analysis/data_quality_audit.py`
**Output:** `comparability_matrix.csv`
**Result:** An explicit comparability matrix (Material / Corrosion target / Measurement technique / Inhibitor system / Medium / Temperature range / Dose unit / Time range / Sample size) rates each dimension as Comparable / Partial / Not comparable across P1/P2/P3 rather than assuming equivalence.
**Conclusion:** Pooling does not imply equivalence. The three phases share material, target variable, and general corrosion mechanism, but differ in inhibitor chemistry, technique, and dosage units -- the analysis pipeline treats each dimension explicitly rather than assuming interchangeability.

---

## 2. Are we comparing inhibitor chemistry, or measurement methodology?

**Status:** IMPLEMENTED
**Script:** `Unified_Analysis/cross_phase_model_experiments.py`
**Output:** `model_leaderboard.csv`, `leave_one_phase_out_results.csv`
**Result:** Technique is retained as an explicit categorical feature. P3 (Tafel) is evaluated separately from P1/P2 (weight loss) throughout -- Config C_P3 alone produces negative R² for every model/CV scheme (e.g. CatBoost standard R²=-1.61, grouped R²=-5.10), while P1/P2 individually reach R²=0.94-0.98 (standard CV; see leakage caveat in Q9).
**Conclusion:** Poor P3 performance is interpreted in the context of measurement regime and sample size (n=17/medium vs n~90), not as evidence that Okro extract is a weaker inhibitor. This is the explicit subject of Q19/RQ4.

---

## 3. Are the P1/P2 activation energies genuinely comparable?

**Status:** IMPLEMENTED
**Script:** `Unified_Analysis/ea_analysis.py`
**Output:** `ea_comparison.csv`, `ea_sensitivity.csv`
**Result:** P1 Ea = 61.1 ± 10.6 kJ/mol (n=6 dose groups), P2 Ea = 66.5 ± 16.6 kJ/mol (n=6 dose groups). Difference = 5.4 kJ/mol, SE of difference = 8.0. Welch's t-test: t=-0.67, p=0.52. Mann-Whitney U: p=0.70. Cohen's d = -0.39 (small-to-moderate effect). Leave-one-dose-group-out jackknife: P1 mean Ea stable at 59.1-64.8 kJ/mol across exclusions, P2 stable at 61.7-70.7 kJ/mol -- convergence is not driven by a single outlier dose group.
**Conclusion:** The two estimates are **not statistically distinguishable within the uncertainty of the fitted estimates** (formal test, not just "CIs overlap"), and this holds up under dose-group sensitivity analysis. Both phases were run in HCl at comparable temperature ranges (P1: 40-80°C, P2: 30-70°C, overlapping 40-70°C), both via weight loss -- reasonably aligned protocols support mechanistic interpretation.

---

## 4. Why is P3 excluded from the Ea convergence claim?

**Status:** IMPLEMENTED
**Script:** `Unified_Analysis/ea_analysis.py`
**Output:** `arrhenius_activation_energy.csv`
**Result:** P3-Okro-Acid Ea = 11.2 ± 9.7 kJ/mol (n=4 dose groups, individual fits: [5.46, -0.64, 15.27, 24.81] kJ/mol). P3-Okro-Basic Ea = -180.2 ± 513.4 kJ/mol (n=3 dose groups, individual fits: [76.43, 279.75, -896.75] kJ/mol) -- a physically nonsensical negative-mean/huge-variance result.
**Conclusion:** P3 is excluded from the headline convergence claim **because its own per-dose-group fit variance is too large to trust** (confirmed by the wildly inconsistent per-group Ea values above), not because it happens to disagree with P1/P2. This is reported transparently, not hidden.

---

## 5. Does similar Ea prove the same inhibition mechanism?

**Status:** IMPLEMENTED (by policy, not by additional data)
**Script:** N/A -- language/claim discipline, enforced in `POSTER_RESEARCH_SYNTHESIS.md`
**Output:** N/A
**Result:** No adsorption isotherm (e.g. Langmuir ΔG_ads) was measured in any of the three phases.
**Conclusion:** The Ea convergence is stated as: *"consistent with an inhibition mechanism dominated by surface coverage/adsorption rather than a substantial alteration of the apparent corrosion reaction barrier."* This is the maximum claim strength the data supports -- no stronger mechanistic claim (e.g. "proves adsorption") is made.

---

## 6. Is temperature really the dominant predictor?

**Status:** IMPLEMENTED
**Script:** `Unified_Analysis/predictor_ablation.py`
**Output:** `predictor_ablation.csv`
**Result:** 3-layer check (correlation / permutation importance / ablation R²-drop) per phase:
- **P1-Temperature**: all 3 layers agree -> Temp_C (r=0.907, permutation importance=1.88, R² drop when removed=3.74). **AGREE.**
- **P2-Temperature**: all 3 layers agree -> Temp_C (r=0.770, permutation importance=1.80, R² drop=3.78). **AGREE.**
- **P3-Okro-Acid**: layers disagree (correlation and ablation point to Dose_Value, permutation importance points to Temp_C). **MIXED.**
- **P3-Okro-Basic**: layers disagree (correlation/permutation point to Temp_C, ablation points to Molarity_M). **MIXED.**
**Conclusion:** Temperature dominance is only claimed for the two temperature-varying **gravimetric** phases (P1, P2), where all three evidence layers agree. For P3, the result is explicitly reported as mixed/inconclusive -- temperature is never called a "universal" driver.

---

## 7. Is correlation being mistaken for causation?

**Status:** IMPLEMENTED (methodological safeguard)
**Script:** `Unified_Analysis/predictor_ablation.py`
**Output:** `predictor_ablation.csv`, `interaction_effects.csv`
**Result:** Predictor-dominance claims require agreement across correlation (association only) AND permutation importance AND ablation (predictive contribution within a model), not correlation alone. An interaction check (`Dose_Value x Temp_C` OLS term) was also run: P1-Temperature interaction p=0.62, P2-Temperature interaction p=0.55 -- neither significant.
**Conclusion:** No causal claim is made from correlation. Conclusions are phrased as predictive/associational. Concentration does not significantly modify the temperature effect in either gravimetric temperature phase (interaction not significant), so a simple additive interpretation is used rather than implying a more complex causal interaction.

---

## 8. Are the 302 observations actually 302 independent experiments?

**Status:** IMPLEMENTED
**Script:** `Unified_Analysis/data_quality_audit.py`
**Output:** console "UNIT OF INDEPENDENCE" statement, `data_quality_audit.csv`
**Result:** Explicit statement: each row is one measurement under a specific condition (dose x temperature x time x medium), not an independently repeated full experiment (e.g. P2-Temperature's 90 rows come from 5 temps x 6 doses x 3 acid molarities, a structured design, not 90 unrelated trials).
**Conclusion:** 302 is not used as evidence of 302 independent samples. This directly motivates the grouped-CV design in Q9.

---

## 9. Could data leakage inflate the reported ML performance?

**Status:** IMPLEMENTED -- and it materially changed the headline numbers
**Script:** `Unified_Analysis/cross_phase_model_experiments.py`
**Output:** `model_leaderboard.csv`
**Result:** Standard random 5-fold CV vs grouped 5-fold CV (grouped by rounded Study+Dose+Temp+Time condition key) for the same model/config:
| Config | Model | Standard CV R² | Grouped CV R² |
|---|---|---|---|
| A_P1 | XGBoost | 0.983 | 0.372 |
| B_P2 | RandomForest | 0.965 | -0.236 |
| D_P1P2 | CatBoost | 0.971 | 0.421 |
| E_P1P2P3 | CatBoost | 0.608 | 0.041 |
**Conclusion:** Standard random-split CV **substantially overestimates** performance once experimental-condition leakage is removed. This is a materially important finding: any historical R² figures from the original per-project notebooks (e.g. R²=0.9995) almost certainly reflect the same optimistic-CV effect and should be read with this caveat. Grouped CV is the more defensible number for any generalization claim.

---

## 10. Is the model learning corrosion physics, or just which phase generated the row?

**Status:** IMPLEMENTED
**Script:** `Unified_Analysis/cross_phase_model_experiments.py`
**Output:** `phase_identity_ablation.csv`, `phase_identity_permutation_share.csv`
**Result:** Removing `Technique`/`Medium_Type`/`Inhibitor_System` from the P1+P2 model (D vs F) changes R² by less than 0.01 in nearly every model/CV combination. Removing them from the P1+P2+P3 model (E vs G) causes larger, model-dependent swings (e.g. CatBoost standard CV: R² drops from 0.608 to 0.353 when identity is removed; XGBoost grouped CV: R² drops from 0.052 to -0.330). Permutation-importance share held by identity features: 1.2% for P1+P2, 6.0% for P1+P2+P3.
**Conclusion:** For P1+P2 (same technique, same acid family), identity features contribute almost nothing -- the model is learning from real environmental variables. Once P3 (a different measurement technique) is added, identity features become moderately more informative, most plausibly because they help the model recognize/calibrate for the very different Tafel measurement scale rather than because the model is "cheating" on inhibitor identity per se. This nuance -- not a blanket yes/no -- is the honest answer.

---

## 11. Does P3 actually add predictive information, or just noise?

**Status:** IMPLEMENTED
**Script:** `Unified_Analysis/cross_phase_model_experiments.py`
**Output:** `p1p2_vs_p1p2p3.csv`
**Result:** Comparing P1+P2 vs P1+P2+P3 across all 4 models and both CV schemes: R² change from adding P3 is negative in 6 of 8 comparisons (e.g. XGBoost standard CV: 0.964 -> 0.364, a -0.600 change; CatBoost grouped CV: 0.421 -> 0.041, a -0.380 change). Only RandomForest under grouped CV shows a (small, low-base) positive change (+0.226, from -0.169 to +0.057).
**Conclusion:** Adding P3 mostly **hurts** pooled predictive performance -- consistent with P3 representing a genuine distribution/measurement-regime shift rather than transferable additional signal. Reported neutrally: this is itself a valid, informative result, not a failure of the pipeline.

---

## 12. Can a model trained on some phases predict an unseen phase (leave-one-phase-out)?

**Status:** IMPLEMENTED
**Script:** `Unified_Analysis/cross_phase_model_experiments.py`
**Output:** `leave_one_phase_out_results.csv`
**Result:**
| Train | Test | Best model | R² | MAE |
|---|---|---|---|---|
| P1+P2 | P3 | CatBoost | -0.24 | 83.7 |
| P1+P3 | P2 | XGBoost | 0.40 | 40.0 |
| P2+P3 | P1 | Ridge | 0.57 | 34.2 |
Every direction has `Test_has_unseen_Inhibitor_System=True` (the held-out phase's inhibitor chemistry was never seen in training).
**Conclusion:** Cross-phase transfer is **direction-dependent**: training on gravimetric data and predicting Tafel data (P1+P2→P3) fails outright (negative R² for all 4 models); training that includes P3 and predicting a gravimetric phase (P1+P3→P2, P2+P3→P1) achieves moderate transfer. This asymmetry itself is informative about which direction of measurement-regime shift is more severe.

---

## 13. Does cross-phase prediction mean the study can predict a completely new/unseen inhibitor chemistry?

**Status:** LIMITATION -- explicitly out of scope
**Script:** N/A
**Output:** N/A
**Result:** All three leave-one-phase-out experiments held out a phase whose `Inhibitor_System` was entirely absent from training (confirmed via the `Test_has_unseen_Inhibitor_System` flag in Q12's output) -- so in a narrow sense every LOPO test already involves an unseen inhibitor. However, each phase = exactly one inhibitor system, so "cross-phase" and "cross-inhibitor" are fully confounded here; the design cannot isolate whether poor/good transfer is due to the new chemistry, the new technique, or both at once.
**Conclusion:** **Cross-phase generalization (tested) is not equivalent to a controlled test of unseen-inhibitor-chemistry generalization (not isolated in this design).** Stated explicitly as a scope limitation, not implied to be solved.

---

## 14. Why these four models (Ridge/RandomForest/XGBoost/CatBoost) -- why not just Random Forest?

**Status:** IMPLEMENTED
**Script:** `Unified_Analysis/cross_phase_model_experiments.py`
**Output:** `model_leaderboard.csv`
**Result:** All 7 configs (A-G) run identically across all 4 models and both CV schemes -- 56 leaderboard rows total. The leakage effect (Q9), the P3-hurts-pooling effect (Q11), and the phase-identity nuance (Q10) all hold directionally across all 4 algorithms, not just one.
**Conclusion:** Conclusions in this study are checked for consistency across model families before being stated as findings; no claim rests on Random Forest (or any single algorithm) alone. Where models disagree in magnitude (they sometimes do), the leaderboard reports each one rather than picking a favorite.

---

## 15. Is R² alone a sufficient metric?

**Status:** IMPLEMENTED
**Script:** `Unified_Analysis/cross_phase_model_experiments.py`, `ea_analysis.py`
**Output:** `model_leaderboard.csv` (R²+MAE+RMSE+fold SD for every config/model/CV-scheme), `leave_one_phase_out_results.csv` (R²+MAE+RMSE), `ea_comparison.csv` (mean+SD+formal test, not a bare estimate)
**Result:** Every reported model result in this study includes R², MAE, RMSE, and fold-to-fold standard deviation (or train/test SD for LOPO) -- never a bare R².
**Conclusion:** Satisfied by construction; no bare-R² claim exists anywhere in the pipeline's outputs.

---

## 16. Can mL of blend (P1-DoE) be directly compared with ppm (P2/P3)?

**Status:** RESOLVED BY DESIGN (structurally prevented, not just discouraged)
**Script:** `Unified_Analysis/build_master_dataset.py`
**Output:** `master_corrosion_dataset.csv` schema: `Dose_Value` + `Dose_Unit` (`'ppm'`/`'mL_blend'`) + `Concentration_ppm` (populated only where `Dose_Unit=='ppm'`)
**Result:** P1-DoE-Blend rows have `Dose_Unit='mL_blend'` and `Concentration_ppm=NaN` by construction. `dosage_efficiency()` filters explicitly on `Dose_Unit=='ppm'` before computing anything -- confirmed: `dosage_efficiency_index.csv` contains zero P1-DoE-Blend rows.
**Conclusion:** No conversion is invented. The dosage-efficiency ranking structurally cannot include mL-dosed rows -- this is enforced in code, not just prose.

---

## 17. Are the ppm-based dosage-efficiency rankings themselves valid?

**Status:** IMPLEMENTED
**Script:** `Unified_Analysis/build_master_dataset.py`
**Output:** `dosage_efficiency_index.csv`
**Result:** P1-Time=0.729 IE%/ppm, P1-Temperature=0.339, P2-Time=0.323, P2-Temperature=0.241 (all ppm-dosed only).
**Conclusion:** Valid for the ppm-dosed studies being ranked against each other (same unit). P1-DoE-Blend's own optimization result (CR≈1.64 mm/yr, IE≈87.6%) is reported as a standalone finding in its native units, never folded into this ranking.

---

## 18. Is n=17 (per medium) enough for P3 machine learning?

**Status:** LIMITATION, acknowledged directly in results
**Script:** `Unified_Analysis/cross_phase_model_experiments.py`
**Output:** `model_leaderboard.csv` (Config C_P3 rows)
**Result:** C_P3 alone: R² is negative for every one of the 4 models under both CV schemes (range: -1.6 to -20.6).
**Conclusion:** P3 is explicitly Tier 2/exploratory. Its ML results are not presented with the same confidence as P1/P2, and are used primarily to test measurement-regime robustness and cross-phase transfer (Q2, Q12), not as a standalone predictive claim.

---

## 19. Does P3's poor ML performance prove electrochemical/Tafel data is bad for ML in general?

**Status:** IMPLEMENTED (claim explicitly bounded)
**Script:** N/A -- interpretive discipline
**Output:** N/A
**Result:** P3 performance is interpreted jointly with n=17/medium, the measurement technique, and the phase distribution -- not treated as a general statement about electrochemical measurements.
**Conclusion:** The conclusion is limited to the present P3 dataset. No general claim about Tafel/electrochemical data quality is made.

---

## 20. Are the ML conclusions robust to model choice?

**Status:** IMPLEMENTED
**Script:** `Unified_Analysis/cross_phase_model_experiments.py`
**Output:** `model_leaderboard.csv`, `p1p2_vs_p1p2p3.csv`
**Result:** See Q14 -- the leakage effect (Q9), the P3-hurts-pooling direction (Q11, negative in 6/8 model×CV-scheme combinations), and P3-alone failure (Q18) all hold across Ridge/RandomForest/XGBoost/CatBoost.
**Conclusion:** Key conclusions are robust across model families. Where magnitude differs across models, this is reported rather than glossed over (e.g. RandomForest is the one case where adding P3 under grouped CV doesn't hurt).

---

## 21. Are results robust to preprocessing/data-cleaning choices?

**Status:** IMPLEMENTED
**Script:** `Unified_Analysis/data_quality_audit.py`
**Output:** `data_quality_audit.csv`
**Result:** Full pre-model audit: per-study N, missingness, duplicate rows (0 found), CR≤0 count (5, all P3-Okro-Basic, listed individually with values), CR min/max/mean/SD, unique temp/dose/time levels.
**Conclusion:** Non-positive CR rows are retained in the master dataset and flagged, not blanket-deleted. They are excluded only from analyses that mathematically require CR>0 (Arrhenius's ln(CR)), with the exact excluded rows/count stated in that analysis's own output (Q4).

---

## 22. What genuinely new information comes from unifying the three phases (vs analyzing them separately)?

**Status:** IMPLEMENTED
**Script:** all of the above
**Result:** Four cross-phase outputs that no single phase's original analysis could produce:
1. Ea convergence across two independently generated inhibitor systems (Q3).
2. A quantified, direct answer to "how much does naive CV overestimate performance" (Q9) -- not visible from analyzing any one phase alone with its own historical CV setup.
3. A quantified test of whether pooling helps or hurts (Q11), and in which direction transfer works better (Q12).
4. A quantified, not just qualitative, measurement-regime robustness contrast (weight-loss vs Tafel R², matched features/methodology for the first time).
**Conclusion:** The contribution is not "ML predicts corrosion rate" -- it is identifying which conclusions survive experimental-system changes (Ea), which are conditional (temperature dominance only in gravimetric phases), and which are measurement-dependent (predictive reliability), using a single consistent methodology across all three.

---

## 23. What if the combined (P1+P2+P3) model performs worse than P1+P2 alone?

**Status:** IMPLEMENTED -- this is in fact what was observed
**Script:** `Unified_Analysis/cross_phase_model_experiments.py`
**Output:** `p1p2_vs_p1p2p3.csv`
**Result:** See Q11 -- performance drops in 6 of 8 model×CV-scheme comparisons when P3 is added.
**Conclusion:** This is interpreted as evidence that P3 introduces distribution/measurement shift not sufficiently represented by the available features -- not hidden, not treated as a pipeline failure. Combining datasets was never assumed to help; the experiment determined the answer.

---

## 24. Final evidence hierarchy

**Status:** IMPLEMENTED (policy applied throughout this document)
**Tier 1 (strongest evidence):** P1 + P2 weight-loss results -- used for Ea convergence, temperature/concentration behaviour, core corrosion conclusions.
**Tier 2 (exploratory evidence):** P3 Tafel results -- used for measurement robustness, distribution-shift, cross-phase stress-testing. Never used to independently validate or invalidate a Tier 1 claim.
**Computational evidence:** Models A-G, grouped CV, leave-one-phase-out -- used to evaluate predictive relationships, generalization, and feature contribution, reported neutrally (no assumption that more data = better).
**Limitations:** Stated explicitly wherever the current experimental design cannot support a stronger claim (Q13, Q18, Q19).

**Scope-limitation statement (applies throughout this study and the accompanying `POSTER_RESEARCH_SYNTHESIS.md`):**
> Cross-phase generalization (tested via leave-one-phase-out) is not equivalent to universal prediction of unseen inhibitor chemistries (not tested, and confounded with technique change in this design -- see Q13).

---

## 25. Are observations really independent, or do experimental series/replicates create hidden structure?

**Status:** IMPLEMENTED
**Script:** `Unified_Analysis/rigor_extension.py`
**Output:** `replicate_structure.csv`
**Result:** P1-Temperature and P1-Time have zero replicates (30 unique conditions each). **P2-Temperature and P2-Time are each built from exactly 30 unique conditions × 3 replicate measurements = 90 rows** — a highly structured repeated design. P1-DoE-Blend has heavy replication (7 condition groups, up to 9 rows in one group). P3-Acid/Basic have partial replication (9 condition groups, up to 5 rows in one group).
**Conclusion:** This confirms the grouped-CV design (Q9) was not a theoretical precaution but a necessity — P2 in particular would have leaked replicate measurements of the same condition across train/test under naive random CV.

---

## 26. Is the study testing interpolation or extrapolation?

**Status:** IMPLEMENTED
**Script:** `Unified_Analysis/rigor_extension.py`
**Output:** `interpolation_extrapolation.csv`
**Result:** Per leave-one-phase-out direction, per variable:
- **P1+P2 → P3**: Dose and Temperature are interpolation; **Molarity is extrapolation** (test 1.0–2.5M vs train 0.5–1.5M); **Medium is extrapolation** (Basic/NaOH never seen in training). This is the direction that failed outright (negative R² for all 4 models) — now explained by simultaneous molarity and medium extrapolation, not just "distribution shift."
- **P1+P3 → P2**: Dose, Time, and Molarity are extrapolation; only Temperature and Medium are interpolation.
- **P2+P3 → P1**: Temperature and Time are extrapolation; Dose, Molarity, and Medium are interpolation. (Best-performing LOPO direction, R²=0.57 with Ridge.)
**Conclusion:** No claim in this study extends beyond the tested experimental design space. The LOPO R² pattern (Q12) is now directly explained by which variables required extrapolation in each direction, not asserted as an unexplained "measurement shift."

---

## 27. Is `IE_percent` mathematically derived from `CR_mm_yr` (target-construction leakage risk)?

**Status:** IMPLEMENTED — confirmed leakage risk, already avoided in the modeling design
**Script:** `Unified_Analysis/rigor_extension.py`
**Output:** `target_leakage_audit.csv`
**Result:** Using P2's retained blank/control rows, `IE_percent = (CR_blank − CR) / CR_blank × 100` was recomputed and compared against the recorded `IE_percent` column across 150 comparisons: mean absolute difference = **0.073 percentage points** — essentially an exact match.
**Conclusion:** `IE_percent` is definitionally derived from `CR_mm_yr` (via the blank-comparison formula standard to weight-loss corrosion studies). It must never be used as an input feature when predicting `CR_mm_yr`. This is already satisfied by construction: `cross_phase_model_experiments.py`'s `NUMERIC` feature list (`Dose_Value`, `Temp_C`, `Time_h`, `Molarity_M`) never includes `IE_percent`.

---

## 28. Could the reported model performance occur by chance given this sample size and validation design?

**Status:** IMPLEMENTED
**Script:** `Unified_Analysis/rigor_extension.py`
**Output:** `permutation_null_test.csv`
**Result:** Target-permutation test (20 shuffles, grouped CV, RandomForest): for D_P1P2, real grouped R²=-0.174 vs null distribution mean=-0.583 (SD=0.247, 95th percentile=-0.385) — empirical p=0.048. For E_P1P2P3, real R²=0.019 vs null mean=-0.488 — empirical p=0.048.
**Conclusion:** Both pooled configurations score better than the 95th percentile of their own null (shuffled-target) distribution under the identical small-sample grouped-CV design — the real signal is not attributable to chance, even though the raw grouped-CV R² values themselves are modest. This distinguishes "the model isn't very accurate yet" from "the model is not doing anything at all," which are different, easily-conflated claims.

---

## 29. Are the grouped-CV results stable, or an artifact of one particular fold split?

**Status:** IMPLEMENTED
**Script:** `Unified_Analysis/rigor_extension.py`
**Output:** `repeated_cv_stability.csv`
**Result:** Repeating grouped CV 5 times with different row-order shuffles (GroupKFold has no native random_state, so fold assignment was varied via row-order shuffling): D_P1P2 R² = -0.174 ± 0.005 (range -0.180 to -0.165); E_P1P2P3 R² = 0.019 ± 0.025 (range -0.002 to 0.056).
**Conclusion:** Both configurations are stable across different fold assignments — the grouped-CV conclusion is not an artifact of one lucky/unlucky split.

---

## 30. Does apparently strong global performance hide systematic failure in specific regions?

**Status:** IMPLEMENTED
**Script:** `Unified_Analysis/rigor_extension.py`
**Output:** `error_stratification.csv`
**Result:** Out-of-fold error from the pooled E_P1P2P3 CatBoost grouped-CV model, stratified:
| Stratification | Worst segment | MAE |
|---|---|---|
| Phase | P3 | 91.2 (vs P1: 15.4, P2: 30.3) |
| Temperature | >60°C | 131.3 (vs ≤40°C: 45.3, 40-60°C: 37.0) |
| Dose | 100-250 ppm | 46.9 (vs ≤100: 22.2, >250: 27.9) |
| Medium | Basic | 119.0 (vs Acid: 27.7) |
| Technique | Tafel | 91.2 (vs Weight loss: 25.4) |
**Conclusion:** Error is highly concentrated in P3/Tafel/Basic-medium/high-temperature conditions — the pooled model's moderate global performance is not evenly distributed; it is substantially worse specifically where the measurement regime and medium differ most from the majority (P1/P2, weight-loss, acid) of the training data.

---

## 31. Does the added complexity of RF/XGBoost/CatBoost provide meaningful improvement over a simple Ridge baseline?

**Status:** IMPLEMENTED
**Script:** `Unified_Analysis/rigor_extension.py`
**Output:** `model_simplicity_test.csv`
**Result:** Complex models beat Ridge by >0.05 R² (the "meaningful gain" threshold) in 13 of 14 config×CV-scheme combinations. The single exception is **C_P3 under grouped CV**, where neither Ridge (-5.06) nor the best complex model (CatBoost, -5.10) works — added complexity provides no meaningful gain because P3 alone is simply not predictable with these features at this sample size, regardless of model choice.
**Conclusion:** Model complexity is generally justified for this problem (the corrosion-rate relationships are genuinely non-linear), except where the underlying data (P3 alone) cannot support any model.

---

## 32. Final claim audit table

**Status:** IMPLEMENTED (applied throughout this document and `POSTER_RESEARCH_SYNTHESIS.md`)

| Original claim | Evidence | Status |
|---|---|---|
| Temperature is the universal dominant driver of CR | 3-layer evidence (Q6): agrees for P1/P2, disagrees for P3 | **Conditional** — supported for P1/P2 gravimetric phases only |
| P1 and P2 have convergent activation energies | Formal Welch's t-test p=0.52, Mann-Whitney p=0.70, stable jackknife sensitivity (Q3) | **Supported** (not statistically distinguishable within uncertainty) |
| P3's activation energy also converges with P1/P2 | Per-dose-group Ea fits for P3 are wildly inconsistent (Q4) | **Not supported** — excluded from the convergence claim by design |
| Ternary blend outperforms single inhibitor | DoE uses mL dosage, others use ppm; no validated conversion (Q16-17) | **Not comparable** — DoE reported as standalone result only |
| Tafel/P3 performs worse due to measurement technique | P3 alone: negative R² regardless of model (Q18, Q31); error stratification shows Tafel/Basic segments dominate pooled-model error (Q30) | **Supported**, but confounded with small sample size (n=17/medium) — cannot fully separate technique effect from sample-size effect |
| Combining P1+P2+P3 improves prediction over P1+P2 alone | R² decreases in 6/8 model×CV-scheme comparisons (Q11) | **Not supported** — adding P3 generally hurts pooled performance |
| ML models generalize across experimental phases | Leave-one-phase-out R² ranges from -0.24 (P1+P2→P3) to 0.57 (P2+P3→P1), explained by interpolation/extrapolation structure (Q12, Q26) | **Conditional** — direction-dependent, tied to which variables require extrapolation |
| Reported model performance could be due to chance given small n | Permutation/null test: real grouped-CV R² exceeds the 95th percentile of the shuffled-target null distribution (Q28) | **Supported (not due to chance)** — though absolute magnitude remains modest for some configs |
| Model complexity (RF/XGBoost/CatBoost) is justified over simple Ridge | Meaningful (>0.05 R²) gain in 13/14 config×CV combinations (Q31) | **Supported**, except where data itself is unpredictable (P3 alone) |
| The model is learning corrosion physics, not phase identity | Identity-feature ablation + permutation-importance share (Q10): ~1% for P1+P2, ~6% for P1+P2+P3 | **Mostly supported** — identity features contribute more once a different measurement technique (P3) is present, most plausibly as a scale/regime indicator |
| Cross-phase generalization ⇒ can predict any unseen inhibitor chemistry | Every LOPO test's held-out phase has an unseen `Inhibitor_System` by construction — phase and inhibitor chemistry are fully confounded here (Q13) | **Not supported / out of scope** — explicitly stated as a design limitation |

**Rule applied**: every claim above is backed by a specific script and output file, or is explicitly downgraded to "conditional," "not supported," or "out of scope" where the evidence does not fully support it.

---

**Final rule for this entire document**: no result in this study is promoted to a headline finding unless the corresponding reviewer challenge above has an explicit answer with real numbers, not prose alone.

