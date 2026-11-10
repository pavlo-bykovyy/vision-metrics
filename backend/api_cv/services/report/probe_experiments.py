"""
Diagnostic probe experiments on the 11D binary-classification metric profile
(stress-test reviewer analyses, e.g. 280,000 degraded scenarios):

    A. feature-set ablation with 5-fold GroupKFold, 95% group-bootstrap CI of Balanced
       Accuracy and a stable one-sided paired Wilcoxon test against the full 11D profile;
    B. linear (L2, L1) and non-linear (RF, HistGB, MLP) probe models on the full profile.

All heavy imports (scikit-learn, scipy) are lazy, because this module is imported by the
API container through `api_cv.services.report`, which has neither installed.
"""
from __future__ import annotations

import argparse
import math
import warnings
from pathlib import Path
from typing import Any, Optional

import numpy as np
import pandas as pd

DEFAULT_SEED = 20260822
TARGET_COL = "path_label"
GROUP_COL = "group_id"
REFERENCE_SET = "Full 11D profile (d=11)"

FULL_11D: list[str] = [
    "accuracy",
    "precision",
    "recall",
    "f1",
    "mcc",
    "balanced_accuracy",
    "specificity_derived",
    "roc_auc",
    "pr_auc",
    "log_loss",
    "brier_score",
]

FEATURE_SETS: dict[str, list[str]] = {
    REFERENCE_SET: FULL_11D,
    "Full panel minus derived metrics (d=9: no F1, no BA)": [
        "accuracy", "precision", "recall", "mcc", "specificity_derived",
        "roc_auc", "pr_auc", "log_loss", "brier_score",
    ],
    "Non-redundant orthogonal subset (d=6)": [
        "precision", "recall", "specificity_derived", "mcc", "roc_auc", "log_loss",
    ],
    "Threshold/confusion family (d=7)": [
        "accuracy", "precision", "recall", "f1", "mcc", "balanced_accuracy", "specificity_derived",
    ],
    "Minimal cross-family triad (d=3: MCC+ROC_AUC+Brier)": ["mcc", "roc_auc", "brier_score"],
    "Ranking-only family (d=2)": ["roc_auc", "pr_auc"],
    "Probability-only family (d=2)": ["log_loss", "brier_score"],
    "Single best correlation metric (d=1: MCC only)": ["mcc"],
    "Single best probabilistic metric (d=1: LogLoss only)": ["log_loss"],
}

COLUMN_ALIASES: dict[str, tuple[str, ...]] = {
    "f1": ("f1_score",),
    "log_loss": ("log_loss_value",),
    "specificity_derived": ("specificity",),
}


# ------------------------------------------------------------------
# Data preparation
# ------------------------------------------------------------------

def normalize_diagnostic_dataframe(
    df: pd.DataFrame,
    target_col: str = TARGET_COL,
    group_col: str = GROUP_COL,
    filter_positive_lambda: bool = True,
) -> pd.DataFrame:
    """
    Ensures standard 11D metric column names exist (resolving aliases such as
    `specificity` -> `specificity_derived`, `f1_score` -> `f1`, `log_loss_value` -> `log_loss`)
    and optionally filters to degraded scenarios (lambda > 0, where failure paths differ).
    """
    out = df.copy()

    if filter_positive_lambda:
        for lam_col in ("lambda", "lambda_val", "severity"):
            if lam_col in out.columns:
                out = out[out[lam_col] > 0].copy()
                break

    for canonical, aliases in COLUMN_ALIASES.items():
        if canonical not in out.columns:
            for alias in aliases:
                if alias in out.columns:
                    out[canonical] = out[alias]
                    break

    if "specificity_derived" not in out.columns:
        if "balanced_accuracy" in out.columns and "recall" in out.columns:
            out["specificity_derived"] = 2.0 * out["balanced_accuracy"] - out["recall"]

    missing = [col for col in FULL_11D if col not in out.columns]
    if missing:
        raise KeyError(f"Missing required 11D metric columns: {missing}")
    if target_col not in out.columns:
        raise KeyError(f"Target column '{target_col}' not found in DataFrame.")
    if group_col not in out.columns:
        raise KeyError(f"Group column '{group_col}' not found in DataFrame.")

    return out.reset_index(drop=True)


def feature_matrix(df: pd.DataFrame, cols: list[str]) -> np.ndarray:
    return df[cols].replace([np.inf, -np.inf], np.nan).fillna(0.0).to_numpy()


# ------------------------------------------------------------------
# Statistics
# ------------------------------------------------------------------

def compute_group_stats(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    groups: np.ndarray,
    n_boot: int = 1000,
    seed: int = DEFAULT_SEED,
) -> tuple[np.ndarray, float, float]:
    """
    Per-group Balanced Accuracy (mean recall over the classes present in the group) and a
    95% bootstrap CI over independent groups. Groups are sorted, so the score order is the
    same for every configuration, which the paired Wilcoxon test relies on.
    """
    y_true = np.asarray(y_true)
    df_tmp = pd.DataFrame({
        "g": np.asarray(groups),
        "y": y_true,
        "correct": (y_true == np.asarray(y_pred)).astype(np.float64),
    })
    group_scores = (
        df_tmp.groupby(["g", "y"], sort=True)["correct"].mean()
        .groupby(level=0, sort=True).mean()
        .to_numpy()
    )

    rng = np.random.default_rng(seed)
    n = len(group_scores)
    boots = np.empty(n_boot)
    for i in range(n_boot):
        boots[i] = group_scores[rng.integers(0, n, size=n)].mean()
    ci_low, ci_high = np.percentile(boots, [2.5, 97.5])
    return group_scores, float(ci_low), float(ci_high)


def _wilcoxon_z(diffs: np.ndarray) -> float:
    """Normal-approximation z of the signed-rank statistic (zero_method='wilcox', tie-corrected, no continuity)."""
    d = diffs[np.isfinite(diffs) & (diffs != 0)]
    n = d.size
    ranks = pd.Series(np.abs(d)).rank(method="average").to_numpy()
    r_plus = ranks[d > 0].sum()
    _, ties = np.unique(np.abs(d), return_counts=True)
    var = n * (n + 1) * (2 * n + 1) / 24.0 - (ties**3 - ties).sum() / 48.0
    return float((r_plus - n * (n + 1) / 4.0) / math.sqrt(var)) if var > 0 else float("nan")


def _log10_sf(z: float) -> float:
    """log10 P[Z >= z] without underflow (SciPy if available, else Mills-ratio asymptotics)."""
    try:
        from scipy.stats import norm

        return float(norm.logsf(z) / math.log(10.0))
    except ImportError:
        if z < 5:
            return math.log10(max(0.5 * math.erfc(z / math.sqrt(2.0)), 1e-300))
        return (-z * z / 2.0 - math.log(z * math.sqrt(2.0 * math.pi))) / math.log(10.0)


def stable_wilcoxon_greater(reference_scores, reduced_scores) -> dict[str, Any]:
    """
    One-sided paired Wilcoxon (reference > reduced), asymptotic method.

    With thousands of paired groups real p-values underflow to 0.0, so log10(p) is computed
    in log-space and a manuscript-safe string is produced (e.g. "p < 1e-100").
    """
    reference_scores = np.asarray(reference_scores, dtype=float)
    reduced_scores = np.asarray(reduced_scores, dtype=float)
    if reference_scores.shape != reduced_scores.shape:
        raise ValueError("Paired Wilcoxon inputs must have identical shapes.")

    diffs = reference_scores - reduced_scores
    if not np.any(np.isfinite(diffs) & (diffs != 0)):
        return {"W": np.nan, "z": np.nan, "p_raw": np.nan, "log10_p": np.nan,
                "p_report": "n/a (all paired differences are zero)"}

    try:
        from scipy.stats import wilcoxon

        res = wilcoxon(reference_scores, reduced_scores, alternative="greater",
                       zero_method="wilcox", correction=False, method="approx")
        W, p_raw = float(res.statistic), float(res.pvalue)
        z = float(getattr(res, "zstatistic", np.nan))
    except ImportError:
        d = diffs[np.isfinite(diffs) & (diffs != 0)]
        ranks = pd.Series(np.abs(d)).rank(method="average").to_numpy()
        W, z = float(ranks[d > 0].sum()), _wilcoxon_z(diffs)
        p_raw = 0.5 * math.erfc(z / math.sqrt(2.0)) if np.isfinite(z) else np.nan
    if not np.isfinite(z):  # older SciPy does not expose zstatistic
        z = _wilcoxon_z(diffs)

    if np.isfinite(z):
        log10_p = _log10_sf(z)
    elif np.isfinite(p_raw) and p_raw > 0:
        log10_p = float(np.log10(p_raw))
    else:
        log10_p = -np.inf

    if np.isfinite(log10_p) and log10_p < -100:
        p_report = "p < 1e-100"
    elif np.isfinite(p_raw) and p_raw > 0:
        p_report = f"p = {p_raw:.3e}"
    elif np.isfinite(log10_p):
        p_report = f"p ≈ 10^({log10_p:.1f})"
    else:
        p_report = "p < 1e-300"

    return {"W": W, "z": z, "p_raw": p_raw, "log10_p": log10_p, "p_report": p_report}


# ------------------------------------------------------------------
# Probe models
# ------------------------------------------------------------------

def build_base_linear_probe(seed: int = DEFAULT_SEED):
    """StandardScaler + multinomial L2 LogisticRegression (the conservative linear probe)."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler

    return Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(max_iter=3000, class_weight="balanced", random_state=seed)),
    ])


def build_hgb_probe(seed: int = DEFAULT_SEED):
    from sklearn.ensemble import HistGradientBoostingClassifier

    return HistGradientBoostingClassifier(max_iter=200, learning_rate=0.1, random_state=seed)


def build_mlp_probe(seed: int = DEFAULT_SEED):
    from sklearn.neural_network import MLPClassifier
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler

    return Pipeline([
        ("scaler", StandardScaler()),
        ("clf", MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=80,
                              early_stopping=True, random_state=seed)),
    ])


def build_probe_models(seed: int = DEFAULT_SEED) -> dict[str, Any]:
    """Linear and non-linear diagnostic probe models for Experiment B."""
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler

    return {
        "Multinomial Logistic Regression (L2, linear baseline)": build_base_linear_probe(seed),
        "Multinomial Logistic Regression (L1/Lasso, C=0.1)": Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(penalty="l1", solver="saga", C=0.1, max_iter=1500,
                                       class_weight="balanced", random_state=seed)),
        ]),
        # n_jobs=1: parallelism comes from cross_val_predict
        "Random Forest (n_estimators=150, max_depth=12)": RandomForestClassifier(
            n_estimators=150, max_depth=12, class_weight="balanced", n_jobs=1, random_state=seed
        ),
        "HistGradientBoosting (Boosted Trees)": build_hgb_probe(seed),
        "MLP Neural Network (64x32, ReLU)": build_mlp_probe(seed),
    }


# ------------------------------------------------------------------
# Experiments
# ------------------------------------------------------------------

def run_ablation_study(
    df_diag: pd.DataFrame,
    feature_sets: Optional[dict[str, list[str]]] = None,
    target_col: str = TARGET_COL,
    group_col: str = GROUP_COL,
    n_splits: int = 5,
    n_boot: int = 1000,
    seed: int = DEFAULT_SEED,
    n_jobs: int = -1,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Experiment A (Table 8). The first feature set is the reference for the Wilcoxon tests.
    Returns (ablation table, detailed Wilcoxon table with W, z and stable log10 p).
    """
    from sklearn.metrics import balanced_accuracy_score, f1_score
    from sklearn.model_selection import GroupKFold, cross_val_predict

    df_clean = normalize_diagnostic_dataframe(df_diag, target_col=target_col, group_col=group_col)
    sets_to_run = feature_sets or FEATURE_SETS
    ref_name = next(iter(sets_to_run))

    cv = GroupKFold(n_splits=n_splits)
    y = df_clean[target_col].astype(str).to_numpy()
    groups = df_clean[group_col].to_numpy()
    probe = build_base_linear_probe(seed)

    rows, group_scores = [], {}
    for name, cols in sets_to_run.items():
        preds = cross_val_predict(probe, feature_matrix(df_clean, cols), y,
                                  groups=groups, cv=cv, n_jobs=n_jobs)
        g_scores, ci_l, ci_h = compute_group_stats(y, preds, groups, n_boot=n_boot, seed=seed)
        group_scores[name] = g_scores
        rows.append({
            "Configuration": name,
            "d": len(cols),
            "BA": round(float(balanced_accuracy_score(y, preds)), 4),
            "95% Group-bootstrap CI (BA)": f"[{ci_l:.4f}, {ci_h:.4f}]",
            "Macro-F1": round(float(f1_score(y, preds, average="macro")), 4),
        })
    df_ablation = pd.DataFrame(rows)

    wilcoxon_rows = []
    for name in df_ablation["Configuration"]:
        if name == ref_name:
            stats = {"W": np.nan, "z": np.nan, "p_raw": np.nan, "log10_p": np.nan, "p_report": "Reference"}
        else:
            stats = stable_wilcoxon_greater(group_scores[ref_name], group_scores[name])
        wilcoxon_rows.append({
            "Configuration": name,
            "Wilcoxon_W": stats["W"],
            "Wilcoxon_z_approx": stats["z"],
            "p_raw": stats["p_raw"],
            "log10_p": stats["log10_p"],
            "p_for_manuscript": stats["p_report"],
        })
    df_wilcoxon = pd.DataFrame(wilcoxon_rows)
    df_ablation["Wilcoxon p vs 11D"] = df_wilcoxon["p_for_manuscript"].to_numpy()

    # A publishable table must never contain a blank significance result.
    if not df_ablation["Wilcoxon p vs 11D"].astype(str).str.len().gt(0).all():
        raise RuntimeError("Blank Wilcoxon result in ablation table")
    return df_ablation, df_wilcoxon


def run_diagnostic_model_comparison(
    df_diag: pd.DataFrame,
    models: Optional[dict[str, Any]] = None,
    feature_cols: Optional[list[str]] = None,
    target_col: str = TARGET_COL,
    group_col: str = GROUP_COL,
    n_splits: int = 5,
    n_boot: int = 1000,
    seed: int = DEFAULT_SEED,
    n_jobs: int = -1,
) -> pd.DataFrame:
    """Experiment B (Table 9): probe models on the same GroupKFold partitions as Experiment A."""
    from sklearn.metrics import balanced_accuracy_score, f1_score
    from sklearn.model_selection import GroupKFold, cross_val_predict

    df_clean = normalize_diagnostic_dataframe(df_diag, target_col=target_col, group_col=group_col)
    X = feature_matrix(df_clean, feature_cols or FULL_11D)
    y = df_clean[target_col].astype(str).to_numpy()
    groups = df_clean[group_col].to_numpy()
    cv = GroupKFold(n_splits=n_splits)

    rows = []
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")  # MLP ConvergenceWarning
        for name, model in (models or build_probe_models(seed)).items():
            preds = cross_val_predict(model, X, y, groups=groups, cv=cv, n_jobs=n_jobs)
            _, ci_l, ci_h = compute_group_stats(y, preds, groups, n_boot=n_boot, seed=seed)
            rows.append({
                "Diagnostic Model": name,
                "BA": round(float(balanced_accuracy_score(y, preds)), 4),
                "95% Group-bootstrap CI (BA)": f"[{ci_l:.4f}, {ci_h:.4f}]",
                "Macro-F1": round(float(f1_score(y, preds, average="macro")), 4),
            })
    return pd.DataFrame(rows)


def run_all_experiments(
    df_diag: pd.DataFrame,
    target_col: str = TARGET_COL,
    group_col: str = GROUP_COL,
    n_splits: int = 5,
    n_boot: int = 1000,
    seed: int = DEFAULT_SEED,
    n_jobs: int = -1,
    verbose: bool = True,
) -> dict[str, pd.DataFrame]:
    """Runs Experiments A and B; keys: ablation, wilcoxon, models."""
    kwargs = dict(target_col=target_col, group_col=group_col, n_splits=n_splits,
                  n_boot=n_boot, seed=seed, n_jobs=n_jobs)
    df_ablation, df_wilcoxon = run_ablation_study(df_diag, **kwargs)
    if verbose:
        print("\n=== TABLE 8: ABLATION + 95% GROUP-BOOTSTRAP CI + WILCOXON ===")
        print(df_ablation.to_string(index=False))

    df_models = run_diagnostic_model_comparison(df_diag, **kwargs)
    if verbose:
        print("\n=== TABLE 9: ALTERNATIVE DIAGNOSTIC PROBES (FULL 11D) ===")
        print(df_models.to_string(index=False))

    return {"ablation": df_ablation, "wilcoxon": df_wilcoxon, "models": df_models}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run 11D diagnostic probe ablation and model comparison experiments."
    )
    parser.add_argument("--data", type=Path, required=True,
                        help="Diagnostic dataset (.csv, .csv.gz or .parquet), e.g. "
                             "monte_carlo_raw_results.csv.gz from the stress test.")
    parser.add_argument("--target-col", type=str, default=TARGET_COL)
    parser.add_argument("--group-col", type=str, default=GROUP_COL)
    parser.add_argument("--n-splits", type=int, default=5)
    parser.add_argument("--n-boot", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--n-jobs", type=int, default=-1)
    parser.add_argument("--output-dir", type=Path, default=None,
                        help="Optional directory for the reviewer_*.csv tables.")
    args = parser.parse_args()

    if args.data.suffix.lower() in (".parquet", ".pq"):
        df = pd.read_parquet(args.data)
    else:
        df = pd.read_csv(args.data)

    results = run_all_experiments(
        df, target_col=args.target_col, group_col=args.group_col, n_splits=args.n_splits,
        n_boot=args.n_boot, seed=args.seed, n_jobs=args.n_jobs, verbose=True,
    )

    if args.output_dir is not None:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        results["ablation"].to_csv(args.output_dir / "reviewer_table8_extended_ablation.csv", index=False)
        results["wilcoxon"].to_csv(args.output_dir / "reviewer_wilcoxon_full_vs_reduced.csv", index=False)
        results["models"].to_csv(args.output_dir / "reviewer_alternative_probes.csv", index=False)


if __name__ == "__main__":
    main()
