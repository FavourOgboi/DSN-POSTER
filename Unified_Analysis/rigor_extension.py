"""
Extended rigor audit (items 23-30 of the expanded reviewer-challenge list):
  23. Experimental-series / replicate structure verification
  24. Interpolation vs extrapolation characterization (per leave-one-phase-out direction)
  25. Target-construction / leakage audit (does IE_percent mathematically derive from CR_mm_yr?)
  27. Null / permutation sanity check
  28. Repeated validation (multiple random seeds)
  29. Error stratification (by phase / temperature / dose / medium / technique)
  30. Model-simplicity test (Ridge vs complex models, "meaningful gain" threshold = 0.05 R2)

Run: python rigor_extension.py
Outputs:
  - replicate_structure.csv
  - interpolation_extrapolation.csv
  - target_leakage_audit.csv
  - permutation_null_test.csv
  - repeated_cv_stability.csv
  - error_stratification.csv
  - model_simplicity_test.csv
"""
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold, KFold
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, r2_score

import cross_phase_model_experiments as cpe

OUT = Path(__file__).resolve().parent
master = cpe.master
RNG = cpe.RNG


# ---------------------------------------------------------------------------
# 23. Experimental-series / replicate structure verification
# ---------------------------------------------------------------------------
def replicate_structure():
    rows = []
    for study, g in master.groupby("Study"):
        key = cpe.condition_group_key(g)
        counts = key.value_counts()
        rows.append(dict(
            Study=study, n_rows=len(g), n_condition_groups=len(counts),
            n_groups_with_replicates=(counts > 1).sum(),
            max_replicates_in_a_group=counts.max(),
            mean_rows_per_group=counts.mean(),
        ))
    out = pd.DataFrame(rows)
    out.to_csv(OUT / "replicate_structure.csv", index=False)
    return out


# ---------------------------------------------------------------------------
# 24. Interpolation vs extrapolation (per leave-one-phase-out direction)
# ---------------------------------------------------------------------------
def interpolation_extrapolation():
    directions = [(["P1", "P2"], "P3"), (["P1", "P3"], "P2"), (["P2", "P3"], "P1")]
    rows = []
    for train_phases, test_phase in directions:
        train_df = cpe.subset(train_phases)
        test_df = cpe.subset([test_phase])
        for col in cpe.NUMERIC:
            tr = train_df[col].dropna()
            te = test_df[col].dropna()
            if te.empty or tr.empty:
                continue
            is_interp = (te.min() >= tr.min()) and (te.max() <= tr.max())
            rows.append(dict(
                Train="+".join(train_phases), Test=test_phase, Variable=col,
                Train_min=tr.min(), Train_max=tr.max(), Test_min=te.min(), Test_max=te.max(),
                Classification="interpolation" if is_interp else "extrapolation",
            ))
        train_media = set(train_df["Medium_Type"].unique())
        test_media = set(test_df["Medium_Type"].unique())
        unseen_media = test_media - train_media
        rows.append(dict(
            Train="+".join(train_phases), Test=test_phase, Variable="Medium_Type",
            Train_min=np.nan, Train_max=np.nan, Test_min=np.nan, Test_max=np.nan,
            Classification=f"extrapolation (unseen media: {unseen_media})" if unseen_media else "interpolation",
        ))
    out = pd.DataFrame(rows)
    out.to_csv(OUT / "interpolation_extrapolation.csv", index=False)
    return out


# ---------------------------------------------------------------------------
# 25. Target-construction / leakage audit
# ---------------------------------------------------------------------------
def target_leakage_audit():
    """Verify IE_percent is mathematically derived from CR_mm_yr (via comparison
    to a blank/control CR at the same condition) using P2's raw data, which
    retains explicit Control rows. If confirmed, IE_percent must never be used
    as an input feature when predicting CR_mm_yr (it already isn't -- see
    cross_phase_model_experiments.NUMERIC, which excludes it)."""
    p2_path = cpe.master  # already-merged; re-derive blank comparison from master itself
    rows = []
    for study in ["P2-Temperature", "P2-Time"]:
        g = master[master.Study == study].copy()
        group_cols = ["Molarity_M"] + (["Temp_C"] if study == "P2-Temperature" else ["Time_h"])
        for _, sub in g.groupby(group_cols):
            blank = sub[sub["Dose_Value"] == 0]
            if blank.empty:
                continue
            cr_blank = blank["CR_mm_yr"].iloc[0]
            for _, r in sub[sub["Dose_Value"] > 0].iterrows():
                predicted_ie = (cr_blank - r["CR_mm_yr"]) / cr_blank * 100 if cr_blank else np.nan
                if pd.notna(r["IE_percent"]) and pd.notna(predicted_ie):
                    rows.append(dict(Study=study, Dose_Value=r["Dose_Value"],
                                      actual_IE=r["IE_percent"], predicted_IE_from_CR=predicted_ie,
                                      abs_diff=abs(r["IE_percent"] - predicted_ie)))
    out = pd.DataFrame(rows)
    out.to_csv(OUT / "target_leakage_audit.csv", index=False)
    return out


# ---------------------------------------------------------------------------
# 27. Null / permutation sanity check  +  28. Repeated validation
# ---------------------------------------------------------------------------
def permutation_and_repeats(configs=("D_P1P2", "E_P1P2P3"), model_name="RandomForest", n_repeats=5, n_perms=20):
    perm_rows, repeat_rows = [], []
    for cfg_name in configs:
        phases, use_identity = cpe.CONFIGS[cfg_name]
        df = cpe.subset(phases)
        X = df[cpe.NUMERIC + (cpe.IDENTITY_CATS if use_identity else [])]
        y = df["CR_mm_yr"]
        groups = cpe.condition_group_key(df)
        n_splits = min(5, pd.Series(groups).nunique())

        # --- repeated validation (n_repeats shuffles) ---
        # GroupKFold has no random_state; its fold assignment depends on row
        # order, so each "repeat" shuffles row order to get a genuinely
        # different fold assignment rather than an identical deterministic split.
        real_r2s = []
        for seed in range(n_repeats):
            shuffled_idx = X.sample(frac=1.0, random_state=seed).index
            X_s, y_s, groups_s = X.loc[shuffled_idx], y.loc[shuffled_idx], groups.loc[shuffled_idx]
            gkf = GroupKFold(n_splits=n_splits)
            fold_r2 = []
            for train_idx, test_idx in gkf.split(X_s, y_s, groups=groups_s):
                pre = cpe.build_preprocessor(use_identity)
                pipe = Pipeline([("pre", pre), ("model", cpe.MODELS[model_name]())])
                pipe.fit(X_s.iloc[train_idx], y_s.iloc[train_idx])
                pred = pipe.predict(X_s.iloc[test_idx])
                fold_r2.append(r2_score(y_s.iloc[test_idx], pred))
            real_r2s.append(np.mean(fold_r2))
        repeat_rows.append(dict(Config=cfg_name, Model=model_name, n_repeats=n_repeats,
                                 repeat_R2_mean=np.mean(real_r2s), repeat_R2_std=np.std(real_r2s),
                                 repeat_R2_min=np.min(real_r2s), repeat_R2_max=np.max(real_r2s)))

        # --- permutation null test ---
        null_r2s = []
        rng = np.random.RandomState(RNG)
        for i in range(n_perms):
            y_shuffled = y.sample(frac=1.0, random_state=rng.randint(0, 1_000_000)).reset_index(drop=True)
            gkf = GroupKFold(n_splits=n_splits)
            fold_r2 = []
            for train_idx, test_idx in gkf.split(X, y_shuffled, groups=groups):
                pre = cpe.build_preprocessor(use_identity)
                pipe = Pipeline([("pre", pre), ("model", cpe.MODELS[model_name]())])
                pipe.fit(X.iloc[train_idx], y_shuffled.iloc[train_idx])
                pred = pipe.predict(X.iloc[test_idx])
                fold_r2.append(r2_score(y_shuffled.iloc[test_idx], pred))
            null_r2s.append(np.mean(fold_r2))
        real_mean = np.mean(real_r2s)
        empirical_p = (np.sum(np.array(null_r2s) >= real_mean) + 1) / (n_perms + 1)
        perm_rows.append(dict(Config=cfg_name, Model=model_name, n_perms=n_perms,
                               real_R2_mean=real_mean, null_R2_mean=np.mean(null_r2s),
                               null_R2_std=np.std(null_r2s), null_R2_95th_pct=np.percentile(null_r2s, 95),
                               empirical_p_value=empirical_p))
    perm_out = pd.DataFrame(perm_rows)
    repeat_out = pd.DataFrame(repeat_rows)
    perm_out.to_csv(OUT / "permutation_null_test.csv", index=False)
    repeat_out.to_csv(OUT / "repeated_cv_stability.csv", index=False)
    return perm_out, repeat_out


# ---------------------------------------------------------------------------
# 29. Error stratification
# ---------------------------------------------------------------------------
def error_stratification(cfg_name="E_P1P2P3", model_name="CatBoost"):
    phases, use_identity = cpe.CONFIGS[cfg_name]
    df = cpe.subset(phases).reset_index(drop=True)
    X = df[cpe.NUMERIC + (cpe.IDENTITY_CATS if use_identity else [])]
    y = df["CR_mm_yr"]
    groups = cpe.condition_group_key(df)
    n_splits = min(5, pd.Series(groups).nunique())
    gkf = GroupKFold(n_splits=n_splits)
    oof_pred = np.full(len(df), np.nan)
    for train_idx, test_idx in gkf.split(X, y, groups=groups):
        pre = cpe.build_preprocessor(use_identity)
        pipe = Pipeline([("pre", pre), ("model", cpe.MODELS[model_name]())])
        pipe.fit(X.iloc[train_idx], y.iloc[train_idx])
        oof_pred[test_idx] = pipe.predict(X.iloc[test_idx])
    df = df.copy()
    df["oof_pred"] = oof_pred
    df["abs_error"] = (df["CR_mm_yr"] - df["oof_pred"]).abs()
    df["temp_bin"] = pd.cut(df["Temp_C"], bins=[-1, 40, 60, 100], labels=["<=40C", "40-60C", ">60C"])
    df["dose_bin"] = pd.cut(df["Dose_Value"], bins=[-1, 100, 250, 1000], labels=["<=100", "100-250", ">250"])

    rows = []
    for by_col in ["Phase_Group", "temp_bin", "dose_bin", "Medium_Type", "Technique"]:
        for val, sub in df.groupby(by_col, observed=True):
            sub = sub.dropna(subset=["abs_error"])
            if sub.empty:
                continue
            rows.append(dict(Stratify_by=by_col, Value=val, n=len(sub),
                              MAE=sub["abs_error"].mean(), MAE_std=sub["abs_error"].std(),
                              CR_mean=sub["CR_mm_yr"].mean()))
    out = pd.DataFrame(rows)
    out.to_csv(OUT / "error_stratification.csv", index=False)
    return out


# ---------------------------------------------------------------------------
# 30. Model-simplicity test
# ---------------------------------------------------------------------------
def model_simplicity_test(leaderboard):
    rows = []
    for (cfg, cv), sub in leaderboard.groupby(["Config", "CV_scheme"]):
        ridge_r2 = sub.loc[sub.Model == "Ridge", "R2_mean"]
        others = sub[sub.Model != "Ridge"]
        if ridge_r2.empty or others.empty:
            continue
        ridge_r2 = ridge_r2.iloc[0]
        best_other = others.loc[others.R2_mean.idxmax()]
        gain = best_other.R2_mean - ridge_r2
        rows.append(dict(Config=cfg, CV_scheme=cv, Ridge_R2=ridge_r2,
                          Best_complex_model=best_other.Model, Best_complex_R2=best_other.R2_mean,
                          R2_gain_over_Ridge=gain,
                          meaningful_gain=gain > 0.05))
    out = pd.DataFrame(rows)
    out.to_csv(OUT / "model_simplicity_test.csv", index=False)
    return out


if __name__ == "__main__":
    print("=== 23. Experimental-series / replicate structure ===")
    rep = replicate_structure()
    print(rep.to_string(index=False))

    print("\n=== 24. Interpolation vs extrapolation (leave-one-phase-out directions) ===")
    ie = interpolation_extrapolation()
    print(ie.to_string(index=False))

    print("\n=== 25. Target-construction / leakage audit (IE_percent vs CR_mm_yr, P2) ===")
    leak = target_leakage_audit()
    if leak.empty:
        print("No blank/control rows found for comparison.")
    else:
        print(f"n comparisons = {len(leak)}, mean abs diff (actual IE vs CR-derived IE) = {leak.abs_diff.mean():.3f}")
        print(leak.head(10).to_string(index=False))

    print("\n=== 27+28. Permutation null test + repeated CV stability ===")
    perm, repeat = permutation_and_repeats()
    print(perm.to_string(index=False))
    print(repeat.to_string(index=False))

    print("\n=== 29. Error stratification (E_P1P2P3, CatBoost, grouped-CV out-of-fold predictions) ===")
    err = error_stratification()
    print(err.to_string(index=False))

    print("\n=== 30. Model-simplicity test (Ridge vs best complex model) ===")
    leaderboard = pd.read_csv(OUT / "model_leaderboard.csv")
    simplicity = model_simplicity_test(leaderboard)
    print(simplicity.to_string(index=False))
