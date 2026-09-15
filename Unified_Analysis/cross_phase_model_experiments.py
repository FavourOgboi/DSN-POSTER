"""
Cross-phase ML architecture: Models A-G, grouped/leakage-resistant CV,
leave-one-phase-out generalization, and a 4-model sweep (Ridge/RF/XGBoost/
CatBoost) so no conclusion depends on a single algorithm.

Target: CR_mm_yr (only fully-populated target across all 302 rows).
Non-positive CR rows (5, all P3-Okro-Basic) are RETAINED here -- they are
valid recorded measurements; only the Arrhenius analysis excluded them
because ln(CR) strictly requires CR>0.

Model configs:
  A = P1 only          B = P2 only          C = P3 only
  D = P1+P2            E = P1+P2+P3
  F = P1+P2   (no Technique/Medium_Type/Inhibitor_System -- phase-identity ablation of D)
  G = P1+P2+P3 (same ablation of E)

Validation:
  - standard 5-fold CV (baseline)
  - grouped 5-fold CV (GroupKFold on a rounded condition-group key, so near-
    duplicate/repeated experimental conditions never split across train/test)
  - leave-one-phase-out: train on two Phase_Groups, test entirely on the
    third (never seen during training) -- the real cross-phase transfer test

Run: python cross_phase_model_experiments.py
Outputs:
  - model_leaderboard.csv
  - phase_identity_ablation.csv
  - leave_one_phase_out_results.csv
  - p1p2_vs_p1p2p3.csv
"""
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupKFold, KFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBRegressor
from catboost import CatBoostRegressor

OUT = Path(__file__).resolve().parent
master = pd.read_csv(OUT / "master_corrosion_dataset.csv")
RNG = 42

NUMERIC = ["Dose_Value", "Temp_C", "Time_h", "Molarity_M"]
IDENTITY_CATS = ["Technique", "Medium_Type", "Inhibitor_System"]

MODELS = {
    "Ridge": lambda: Ridge(alpha=1.0, random_state=RNG),
    "RandomForest": lambda: RandomForestRegressor(n_estimators=300, random_state=RNG),
    "XGBoost": lambda: XGBRegressor(n_estimators=300, random_state=RNG, verbosity=0),
    "CatBoost": lambda: CatBoostRegressor(iterations=300, random_state=RNG, verbose=False),
}

CONFIGS = {
    "A_P1": (["P1"], True), "B_P2": (["P2"], True), "C_P3": (["P3"], True),
    "D_P1P2": (["P1", "P2"], True), "E_P1P2P3": (["P1", "P2", "P3"], True),
    "F_P1P2_noIdentity": (["P1", "P2"], False), "G_P1P2P3_noIdentity": (["P1", "P2", "P3"], False),
}


def subset(phases):
    return master[master["Phase_Group"].isin(phases)].dropna(subset=["CR_mm_yr"]).reset_index(drop=True)


def build_preprocessor(use_identity):
    cats = IDENTITY_CATS if use_identity else []
    transformers = [("num", Pipeline([("impute", SimpleImputer(strategy="median", add_indicator=True)),
                                       ("scale", StandardScaler())]), NUMERIC)]
    if cats:
        transformers.append(("cat", OneHotEncoder(handle_unknown="ignore"), cats))
    return ColumnTransformer(transformers)


def condition_group_key(df):
    """Rounded (Study, Dose, Temp, Time) tuple -- the leakage-resistant grouping key."""
    return (df["Study"].astype(str) + "_" +
            df["Dose_Value"].round(-1).fillna(-999).astype(str) + "_" +
            df["Temp_C"].fillna(-999).round(0).astype(str) + "_" +
            df["Time_h"].fillna(-999).round(0).astype(str))


def cv_metrics(df, use_identity, model_fn, groups=None):
    X = df[NUMERIC + (IDENTITY_CATS if use_identity else [])]
    y = df["CR_mm_yr"]
    n_splits = min(5, df.shape[0] // 4) if groups is None else min(5, pd.Series(groups).nunique())
    n_splits = max(n_splits, 2)
    splitter = KFold(n_splits=n_splits, shuffle=True, random_state=RNG) if groups is None \
        else GroupKFold(n_splits=n_splits)
    r2s, maes, rmses = [], [], []
    split_iter = splitter.split(X, y) if groups is None else splitter.split(X, y, groups=groups)
    for train_idx, test_idx in split_iter:
        pre = build_preprocessor(use_identity)
        pipe = Pipeline([("pre", pre), ("model", model_fn())])
        pipe.fit(X.iloc[train_idx], y.iloc[train_idx])
        pred = pipe.predict(X.iloc[test_idx])
        r2s.append(r2_score(y.iloc[test_idx], pred))
        maes.append(mean_absolute_error(y.iloc[test_idx], pred))
        rmses.append(np.sqrt(mean_squared_error(y.iloc[test_idx], pred)))
    return dict(R2_mean=np.mean(r2s), R2_std=np.std(r2s),
                MAE_mean=np.mean(maes), MAE_std=np.std(maes),
                RMSE_mean=np.mean(rmses), RMSE_std=np.std(rmses), n_folds=len(r2s))


def run_leaderboard():
    rows = []
    for cfg_name, (phases, use_identity) in CONFIGS.items():
        df = subset(phases)
        if len(df) < 8:
            continue
        groups = condition_group_key(df)
        for model_name, model_fn in MODELS.items():
            std_cv = cv_metrics(df, use_identity, model_fn, groups=None)
            grp_cv = cv_metrics(df, use_identity, model_fn, groups=groups)
            rows.append(dict(Config=cfg_name, Model=model_name, n=len(df),
                              CV_scheme="standard_5fold", **std_cv))
            rows.append(dict(Config=cfg_name, Model=model_name, n=len(df),
                              CV_scheme="grouped_5fold", **grp_cv))
    out = pd.DataFrame(rows)
    out.to_csv(OUT / "model_leaderboard.csv", index=False)
    return out


def phase_identity_ablation(leaderboard):
    """Compare D vs F and E vs G: does removing Technique/Medium_Type/Inhibitor_System
    change performance? Also report permutation importance of identity features
    within the full (D/E) RandomForest model."""
    rows = []
    for full_cfg, reduced_cfg in [("D_P1P2", "F_P1P2_noIdentity"), ("E_P1P2P3", "G_P1P2P3_noIdentity")]:
        for cv in ["standard_5fold", "grouped_5fold"]:
            for model in MODELS:
                full_row = leaderboard[(leaderboard.Config == full_cfg) & (leaderboard.Model == model) &
                                        (leaderboard.CV_scheme == cv)]
                red_row = leaderboard[(leaderboard.Config == reduced_cfg) & (leaderboard.Model == model) &
                                       (leaderboard.CV_scheme == cv)]
                if full_row.empty or red_row.empty:
                    continue
                rows.append(dict(
                    Full_config=full_cfg, Reduced_config=reduced_cfg, Model=model, CV_scheme=cv,
                    Full_R2=full_row.R2_mean.iloc[0], Reduced_R2=red_row.R2_mean.iloc[0],
                    R2_drop_from_removing_identity=full_row.R2_mean.iloc[0] - red_row.R2_mean.iloc[0],
                ))
    out = pd.DataFrame(rows)

    # Permutation importance of identity features in the full D/E RandomForest model
    perm_rows = []
    for cfg_name, phases in [("D_P1P2", ["P1", "P2"]), ("E_P1P2P3", ["P1", "P2", "P3"])]:
        df = subset(phases)
        X = df[NUMERIC + IDENTITY_CATS]
        y = df["CR_mm_yr"]
        pre = build_preprocessor(True)
        X_trans = pre.fit_transform(X)
        rf = RandomForestRegressor(n_estimators=300, random_state=RNG).fit(X_trans, y)
        feat_names = pre.get_feature_names_out()
        perm = permutation_importance(rf, X_trans, y, n_repeats=15, random_state=RNG, scoring="r2")
        identity_mask = [any(f"cat__{c}" in name for c in IDENTITY_CATS) for name in feat_names]
        identity_importance = perm.importances_mean[identity_mask].sum()
        total_importance = perm.importances_mean.sum()
        perm_rows.append(dict(Config=cfg_name,
                               identity_feature_importance_share=identity_importance / total_importance
                               if total_importance != 0 else np.nan))
    perm_out = pd.DataFrame(perm_rows)

    out.to_csv(OUT / "phase_identity_ablation.csv", index=False)
    perm_out.to_csv(OUT / "phase_identity_permutation_share.csv", index=False)
    return out, perm_out


def leave_one_phase_out():
    directions = [(["P1", "P2"], "P3"), (["P1", "P3"], "P2"), (["P2", "P3"], "P1")]
    rows = []
    for train_phases, test_phase in directions:
        train_df = subset(train_phases)
        test_df = subset([test_phase])
        X_train = train_df[NUMERIC + IDENTITY_CATS]
        y_train = train_df["CR_mm_yr"]
        X_test = test_df[NUMERIC + IDENTITY_CATS]
        y_test = test_df["CR_mm_yr"]
        for model_name, model_fn in MODELS.items():
            pre = build_preprocessor(True)
            pipe = Pipeline([("pre", pre), ("model", model_fn())])
            pipe.fit(X_train, y_train)
            pred = pipe.predict(X_test)
            rows.append(dict(
                Train_phases="+".join(train_phases), Test_phase=test_phase, Model=model_name,
                Train_n=len(train_df), Test_n=len(test_df),
                R2=r2_score(y_test, pred), MAE=mean_absolute_error(y_test, pred),
                RMSE=np.sqrt(mean_squared_error(y_test, pred)),
                Train_CR_mean=y_train.mean(), Train_CR_std=y_train.std(),
                Test_CR_mean=y_test.mean(), Test_CR_std=y_test.std(),
                Test_has_unseen_Inhibitor_System=test_df["Inhibitor_System"].iloc[0] not in
                    train_df["Inhibitor_System"].unique(),
            ))
    out = pd.DataFrame(rows)
    out.to_csv(OUT / "leave_one_phase_out_results.csv", index=False)
    return out


def p1p2_vs_p1p2p3(leaderboard):
    rows = []
    for cv in ["standard_5fold", "grouped_5fold"]:
        for model in MODELS:
            d = leaderboard[(leaderboard.Config == "D_P1P2") & (leaderboard.Model == model) & (leaderboard.CV_scheme == cv)]
            e = leaderboard[(leaderboard.Config == "E_P1P2P3") & (leaderboard.Model == model) & (leaderboard.CV_scheme == cv)]
            if d.empty or e.empty:
                continue
            rows.append(dict(Model=model, CV_scheme=cv,
                              P1P2_R2=d.R2_mean.iloc[0], P1P2P3_R2=e.R2_mean.iloc[0],
                              P1P2_MAE=d.MAE_mean.iloc[0], P1P2P3_MAE=e.MAE_mean.iloc[0],
                              R2_change_from_adding_P3=e.R2_mean.iloc[0] - d.R2_mean.iloc[0],
                              MAE_change_from_adding_P3=e.MAE_mean.iloc[0] - d.MAE_mean.iloc[0]))
    out = pd.DataFrame(rows)
    out.to_csv(OUT / "p1p2_vs_p1p2p3.csv", index=False)
    return out


if __name__ == "__main__":
    print("=== Building model leaderboard: 7 configs (A-G) x 4 models x 2 CV schemes ===")
    leaderboard = run_leaderboard()
    print(leaderboard.to_string(index=False))

    print("\n=== Phase-identity ablation (D vs F, E vs G) ===")
    ablation, perm_share = phase_identity_ablation(leaderboard)
    print(ablation.to_string(index=False))
    print("\nShare of total permutation importance held by identity features (Technique/Medium_Type/Inhibitor_System):")
    print(perm_share.to_string(index=False))

    print("\n=== Leave-one-phase-out generalization ===")
    lopo = leave_one_phase_out()
    print(lopo.to_string(index=False))

    print("\n=== P1+P2 vs P1+P2+P3: does adding P3 help or hurt? ===")
    comparison = p1p2_vs_p1p2p3(leaderboard)
    print(comparison.to_string(index=False))
