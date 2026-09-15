"""
3-layer evidence for predictor dominance (Layer 1 correlation already exists
in correlation_comparison.csv) + interaction-effect check.

Layer 2: permutation importance from a RandomForest fit per phase.
Layer 3: ablation -- full feature set vs full-minus-one-feature, per phase,
         reporting the R2/MAE change from removing each feature.
Interaction check: OLS with a Dose_Value x Temp_C interaction term for the
two temperature-varying gravimetric phases (P1-Temperature, P2-Temperature).

A predictor is only called "dominant" if correlation, permutation importance,
and ablation all agree -- otherwise the result is reported as mixed/unclear.

Run: python predictor_ablation.py
Outputs:
  - predictor_ablation.csv
  - interaction_effects.csv
"""
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.model_selection import KFold, cross_val_score

OUT = Path(__file__).resolve().parent
master = pd.read_csv(OUT / "master_corrosion_dataset.csv")

RNG = 42
TEMP_PHASES = ["P1-Temperature", "P2-Temperature", "P3-Okro-Acid", "P3-Okro-Basic"]
TIME_PHASES = ["P1-Time", "P2-Time"]
FEATURES = ["Dose_Value", "Temp_C", "Time_h", "Molarity_M"]


def _prepare_xy(study):
    g = master[master["Study"] == study].dropna(subset=["CR_mm_yr"]).copy()
    X = g[FEATURES].copy()
    non_empty = [c for c in FEATURES if X[c].notna().any()]
    X = X[non_empty]
    imputer = SimpleImputer(strategy="median")
    X_imp = pd.DataFrame(imputer.fit_transform(X), columns=non_empty, index=X.index)
    # keep only columns that actually vary (a constant column adds no info / breaks importance)
    varying = [c for c in non_empty if X_imp[c].nunique() > 1]
    return X_imp[varying], g["CR_mm_yr"], varying


def layer2_layer3(study):
    X, y, feats = _prepare_xy(study)
    if len(feats) == 0 or len(X) < 8:
        return []
    rf = RandomForestRegressor(n_estimators=300, random_state=RNG)
    rf.fit(X, y)
    cv = KFold(n_splits=min(5, len(X)), shuffle=True, random_state=RNG)
    full_r2 = cross_val_score(rf, X, y, cv=cv, scoring="r2").mean()

    perm = permutation_importance(rf, X, y, n_repeats=20, random_state=RNG, scoring="r2")
    perm_imp = dict(zip(feats, perm.importances_mean))

    rows = []
    for feat in feats:
        reduced_feats = [f for f in feats if f != feat]
        if not reduced_feats:
            r2_drop = np.nan
        else:
            rf2 = RandomForestRegressor(n_estimators=300, random_state=RNG)
            r2_reduced = cross_val_score(rf2, X[reduced_feats], y, cv=cv, scoring="r2").mean()
            r2_drop = full_r2 - r2_reduced
        rows.append(dict(Study=study, Feature=feat, n=len(X),
                          full_model_R2=full_r2, permutation_importance=perm_imp[feat],
                          R2_drop_when_removed=r2_drop))
    return rows


def interaction_check(study):
    g = master[master["Study"] == study].dropna(subset=["CR_mm_yr", "Temp_C", "Dose_Value"]).copy()
    if g["Temp_C"].nunique() < 2 or g["Dose_Value"].nunique() < 2:
        return None
    model = smf.ols("CR_mm_yr ~ Dose_Value * Temp_C", data=g).fit()
    interact_term = "Dose_Value:Temp_C"
    return dict(Study=study, n=len(g),
                interaction_coef=model.params.get(interact_term, np.nan),
                interaction_p_value=model.pvalues.get(interact_term, np.nan),
                interaction_significant=(model.pvalues.get(interact_term, 1.0) < 0.05),
                model_R2=model.rsquared)


if __name__ == "__main__":
    print("=== LAYER 2+3: permutation importance + ablation (temperature-varying phases) ===")
    all_rows = []
    for study in TEMP_PHASES + TIME_PHASES:
        all_rows.extend(layer2_layer3(study))
    ablation = pd.DataFrame(all_rows)
    ablation.to_csv(OUT / "predictor_ablation.csv", index=False)
    print(ablation.to_string(index=False))

    print("\n=== 3-LAYER AGREEMENT CHECK (per temperature-varying phase) ===")
    corr = pd.read_csv(OUT / "correlation_comparison.csv")
    for study in TEMP_PHASES:
        sub = ablation[ablation.Study == study]
        if sub.empty:
            print(f"{study}: insufficient data for Layer 2/3")
            continue
        top_feat_l3 = sub.loc[sub.R2_drop_when_removed.idxmax(), "Feature"] if sub.R2_drop_when_removed.notna().any() else None
        top_feat_l2 = sub.loc[sub.permutation_importance.idxmax(), "Feature"]
        r_temp = corr.loc[corr.Study == study, "r_CR_vs_Temp"].iloc[0]
        r_dose = corr.loc[corr.Study == study, "r_CR_vs_Dose"].iloc[0]
        top_feat_l1 = "Temp_C" if abs(r_temp) > abs(r_dose) else "Dose_Value"
        agree = len({top_feat_l1, top_feat_l2, top_feat_l3}) == 1
        print(f"{study}: L1(corr)={top_feat_l1}  L2(perm-imp)={top_feat_l2}  L3(ablation)={top_feat_l3}  "
              f"-> {'AGREE - temperature dominance supported' if agree else 'MIXED - do not call one factor dominant'}")

    print("\n=== INTERACTION CHECK: Dose_Value x Temp_C (OLS) ===")
    interactions = [r for r in (interaction_check(s) for s in ["P1-Temperature", "P2-Temperature"]) if r]
    inter_df = pd.DataFrame(interactions)
    inter_df.to_csv(OUT / "interaction_effects.csv", index=False)
    print(inter_df.to_string(index=False))
