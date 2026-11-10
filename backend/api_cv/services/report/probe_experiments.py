"""
Diagnostic probe experiments (Cross-Validation with GroupKFold, 95% Bootstrap CI,
paired Wilcoxon signed-rank test, feature-family ablation, and non-linear probe models)
on the 11D binary-classification metric profile (e.g., 280,000 degraded scenarios).

Note: All heavy ML/statistical imports (scikit-learn, scipy) are lazy-loaded inside
functions so this module remains safe under the API container's import isolation rules.
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Any, Optional

import numpy as np
import pandas as pd

DEFAULT_SEED = 20260822
TARGET_COL = "degradation_class"
GROUP_COL = "group_id"

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
    "Full 11D profile (d=11)": FULL_11D,
    "Non-redundant subset (d=6)": [
        "precision",
        "recall",
        "specificity_derived",
        "mcc",
        "roc_auc",
        "log_loss",
    ],
    "Threshold/confusion family (d=7)": [
        "accuracy",
        "precision",
        "recall",
        "f1",
        "mcc",
        "balanced_accuracy",
        "specificity_derived",
    ],
    "Minimal cross-family triad (d=3: MCC+ROC_AUC+Brier)": [
        "mcc",
        "roc_auc",
        "brier_score",
    ],
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


def normalize_diagnostic_dataframe(
    df: pd.DataFrame,
    target_col: str = TARGET_COL,
    group_col: str = GROUP_COL,
    filter_positive_lambda: bool = True,
) -> pd.DataFrame:
    """
    Ensures standard 11D metric column names exist (resolving aliases such as
    `specificity` -> `specificity_derived`, `f1_score` -> `f1`, `log_loss_value` -> `log_loss`)
    and optionally filters to degraded scenarios (lambda > 0).
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

    return out


def compute_group_stats(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    groups: np.ndarray,
    n_boot: int = 1000,
    seed: int = DEFAULT_SEED,
) -> tuple[np.ndarray, float, float]:
    """
    Computes per-group accuracy (equal to group Balanced Accuracy when all 7 degradation
    classes are equally represented in each group) and 95% Bootstrap CI across independent groups.
    """
    df_tmp = pd.DataFrame(
        {
            "correct": (np.asarray(y_true) == np.asarray(y_pred)).astype(np.float64),
            "group": np.asarray(groups),
        }
    )
    group_scores = df_tmp.groupby("group", sort=True)["correct"].mean().to_numpy()

    rng = np.random.default_rng(seed)
    n_groups = len(group_scores)
    boot_indices = rng.integers(0, n_groups, size=(n_boot, n_groups))
    boot_means = group_scores[boot_indices].mean(axis=1)
    ci_low, ci_high = np.percentile(boot_means, [2.5, 97.5])
    return group_scores, float(ci_low), float(ci_high)


def _paired_wilcoxon(
    ref_scores: np.ndarray,
    other_scores: np.ndarray,
    alternative: str = "greater",
) -> tuple[float, float]:
    """Runs paired Wilcoxon signed-rank test (with normal approximation fallback if scipy is absent)."""
    try:
        from scipy.stats import wilcoxon

        stat, p_val = wilcoxon(ref_scores, other_scores, alternative=alternative, zero_method="wilcox")
        return float(stat), float(p_val)
    except ImportError:
        diff = np.asarray(ref_scores, dtype=np.float64) - np.asarray(other_scores, dtype=np.float64)
        diff = diff[diff != 0.0]
        n = len(diff)
        if n == 0:
            return 0.0, 1.0
        abs_diff = np.abs(diff)
        ranks = pd.Series(abs_diff).rank(method="average").to_numpy()
        w_plus = float(ranks[diff > 0].sum())
        mean_w = n * (n + 1.0) / 4.0
        std_w = math.sqrt(n * (n + 1.0) * (2.0 * n + 1.0) / 24.0)
        if std_w == 0.0:
            return w_plus, 1.0
        z = (w_plus - mean_w) / std_w
        if alternative == "greater":
            p_val = 0.5 * math.erfc(z / math.sqrt(2.0))
        elif alternative == "less":
            p_val = 0.5 * math.erfc(-z / math.sqrt(2.0))
        else:
            p_val = math.erfc(abs(z) / math.sqrt(2.0))
        return w_plus, float(p_val)


def build_base_linear_probe(seed: int = DEFAULT_SEED):
    """Returns the conservative linear probe (StandardScaler + Multinomial LogisticRegression)."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler

    return Pipeline(
        [
            ("scaler", StandardScaler()),
            (
                "clf",
                LogisticRegression(
                    max_iter=3000,
                    class_weight="balanced",
                    random_state=seed,
                ),
            ),
        ]
    )


def build_probe_models(seed: int = DEFAULT_SEED, n_jobs: int = -1) -> dict[str, Any]:
    """Returns the dictionary of linear and non-linear diagnostic probe models for Experiment B."""
    from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
    from sklearn.neural_network import MLPClassifier
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler

    return {
        "Multinomial Logistic Regression (Linear probe)": build_base_linear_probe(seed=seed),
        "Random Forest (max_depth=12)": RandomForestClassifier(
            n_estimators=150,
            max_depth=12,
            class_weight="balanced",
            n_jobs=n_jobs,
            random_state=seed,
        ),
        "HistGradientBoosting (Tree ensemble)": HistGradientBoostingClassifier(
            max_iter=200,
            learning_rate=0.1,
            random_state=seed,
        ),
        "MLP Neural Network (64x32)": Pipeline(
            [
                ("scaler", StandardScaler()),
                (
                    "clf",
                    MLPClassifier(
                        hidden_layer_sizes=(64, 32),
                        max_iter=100,
                        early_stopping=True,
                        random_state=seed,
                    ),
                ),
            ]
        ),
    }


def run_ablation_study(
    df_diag: pd.DataFrame,
    feature_sets: Optional[dict[str, list[str]]] = None,
    target_col: str = TARGET_COL,
    group_col: str = GROUP_COL,
    n_splits: int = 5,
    n_boot: int = 1000,
    seed: int = DEFAULT_SEED,
    n_jobs: int = -1,
) -> pd.DataFrame:
    """
    Experiment A: Evaluates stronger baselines & feature subsets with 5-fold GroupKFold,
    computing Balanced Accuracy, 95% Bootstrap CI, Macro-F1, and paired Wilcoxon p-values
    against the Full 11D profile.
    """
    from sklearn.metrics import balanced_accuracy_score, f1_score
    from sklearn.model_selection import GroupKFold, cross_val_predict

    df_clean = normalize_diagnostic_dataframe(df_diag, target_col=target_col, group_col=group_col)
    sets_to_run = feature_sets or FEATURE_SETS

    gkf = GroupKFold(n_splits=n_splits)
    y = df_clean[target_col].to_numpy()
    groups = df_clean[group_col].to_numpy()
    base_probe = build_base_linear_probe(seed=seed)

    ablation_results: list[dict[str, Any]] = []
    oof_group_scores: dict[str, np.ndarray] = {}

    for name, cols in sets_to_run.items():
        X_sub = df_clean[cols].to_numpy()
        oof_preds = cross_val_predict(base_probe, X_sub, y, groups=groups, cv=gkf, n_jobs=n_jobs)

        ba = balanced_accuracy_score(y, oof_preds)
        mf1 = f1_score(y, oof_preds, average="macro")
        grp_scores, ci_l, ci_h = compute_group_stats(y, oof_preds, groups, n_boot=n_boot, seed=seed)
        oof_group_scores[name] = grp_scores

        ablation_results.append(
            {
                "Feature Set": name,
                "d": len(cols),
                "Balanced Accuracy": round(float(ba), 4),
                "95% CI (BA)": f"[{ci_l:.4f}, {ci_h:.4f}]",
                "Macro-F1": round(float(mf1), 4),
            }
        )

    df_ablation = pd.DataFrame(ablation_results)
    ref_name = next(iter(sets_to_run.keys()))
    ref_scores = oof_group_scores[ref_name]

    p_vals: list[str] = []
    for name in df_ablation["Feature Set"]:
        if name == ref_name:
            p_vals.append("Reference")
        else:
            _, p_val = _paired_wilcoxon(ref_scores, oof_group_scores[name], alternative="greater")
            p_vals.append(f"{p_val:.2e}")

    df_ablation["Wilcoxon p-value (vs 11D)"] = p_vals
    return df_ablation


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
    """
    Experiment B: Compares linear and non-linear diagnostic probe models
    (LogisticRegression, RandomForest, HistGradientBoosting, MLP) on the Full 11D profile.
    """
    from sklearn.metrics import balanced_accuracy_score, f1_score
    from sklearn.model_selection import GroupKFold, cross_val_predict

    df_clean = normalize_diagnostic_dataframe(df_diag, target_col=target_col, group_col=group_col)
    cols = feature_cols or FULL_11D
    probe_models = models or build_probe_models(seed=seed, n_jobs=n_jobs)

    gkf = GroupKFold(n_splits=n_splits)
    X_full = df_clean[cols].to_numpy()
    y = df_clean[target_col].to_numpy()
    groups = df_clean[group_col].to_numpy()

    model_results: list[dict[str, Any]] = []
    for m_name, model in probe_models.items():
        oof_preds = cross_val_predict(model, X_full, y, groups=groups, cv=gkf, n_jobs=n_jobs)
        ba = balanced_accuracy_score(y, oof_preds)
        mf1 = f1_score(y, oof_preds, average="macro")
        _, ci_l, ci_h = compute_group_stats(y, oof_preds, groups, n_boot=n_boot, seed=seed)

        model_results.append(
            {
                "Diagnostic Probe Model": m_name,
                "Balanced Accuracy": round(float(ba), 4),
                "95% CI (BA)": f"[{ci_l:.4f}, {ci_h:.4f}]",
                "Macro-F1": round(float(mf1), 4),
            }
        )

    return pd.DataFrame(model_results)


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
    """Runs both Experiment A (Ablation Study) and Experiment B (Probe Model Comparison)."""
    if verbose:
        print("Запуск розширеного Ablation Study...")
    df_ablation = run_ablation_study(
        df_diag,
        target_col=target_col,
        group_col=group_col,
        n_splits=n_splits,
        n_boot=n_boot,
        seed=seed,
        n_jobs=n_jobs,
    )
    if verbose:
        print("\n=== ОНОВЛЕНА ТАБЛИЦЯ 8 (Ablation + Baselines + CI + p-values) ===")
        print(df_ablation.to_string(index=False))
        print("\nЗапуск порівняння альтернативних діагностичних моделей на 11D профілі...")

    df_models = run_diagnostic_model_comparison(
        df_diag,
        target_col=target_col,
        group_col=group_col,
        n_splits=n_splits,
        n_boot=n_boot,
        seed=seed,
        n_jobs=n_jobs,
    )
    if verbose:
        print("\n=== НОВА ТАБЛИЦЯ: ПОРІВНЯННЯ ДІАГНОСТИЧНИХ МОДЕЛЕЙ (Full 11D) ===")
        print(df_models.to_string(index=False))

    return {"ablation": df_ablation, "models": df_models}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run 11D diagnostic probe ablation and model comparison experiments."
    )
    parser.add_argument(
        "--data",
        type=Path,
        required=True,
        help="Path to the synthetic diagnostic dataset (.csv or .parquet, e.g. 280k rows).",
    )
    parser.add_argument("--target-col", type=str, default=TARGET_COL)
    parser.add_argument("--group-col", type=str, default=GROUP_COL)
    parser.add_argument("--n-splits", type=int, default=5)
    parser.add_argument("--n-boot", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--n-jobs", type=int, default=-1)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Optional directory to save table8_ablation.csv and probe_models_comparison.csv.",
    )
    args = parser.parse_args()

    if args.data.suffix.lower() in (".parquet", ".pq"):
        df = pd.read_parquet(args.data)
    else:
        df = pd.read_csv(args.data)

    results = run_all_experiments(
        df,
        target_col=args.target_col,
        group_col=args.group_col,
        n_splits=args.n_splits,
        n_boot=args.n_boot,
        seed=args.seed,
        n_jobs=args.n_jobs,
        verbose=True,
    )

    if args.output_dir is not None:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        results["ablation"].to_csv(args.output_dir / "table8_ablation.csv", index=False)
        results["models"].to_csv(args.output_dir / "probe_models_comparison.csv", index=False)


if __name__ == "__main__":
    main()
