"""
Reviewer-requested robustness analyses on the Monte Carlo results.

Blocks A (ablation + Wilcoxon) and B (alternative probes) live in
`api_cv.services.report.probe_experiments`; this module adds C (PCA), D (metric
redundancy), E (zero-shot transfer to non-Gaussian score distributions) and the
audit / manuscript outputs.
"""
from __future__ import annotations

import warnings
from typing import Any, Callable, Optional

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.metrics import balanced_accuracy_score
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler

from api_cv.services.report.probe_experiments import (
    FULL_11D,
    GROUP_COL,
    TARGET_COL,
    build_base_linear_probe,
    build_hgb_probe,
    build_mlp_probe,
    feature_matrix,
    normalize_diagnostic_dataframe,
    run_ablation_study,
    run_diagnostic_model_comparison,
)
from api_cv.services.stress_test.config import (
    FAILURE_PATHS,
    NON_GAUSSIAN_DISTRIBUTIONS,  # noqa: F401  (re-exported for callers/tests)
    StressTestConfig,
)
from api_cv.services.stress_test.simulation import (
    apply_failure_mode,
    calculate_metrics_platform_binary,
    generate_non_gaussian_baseline,
)

def _split_link(link: str) -> tuple[str, str]:
    """'GitHub: https://...' -> ('GitHub', 'https://...'); a bare URL has no label."""
    label, sep, url = link.partition(": ")
    return (label.strip(), url.strip()) if sep and "://" not in label else ("", link.strip())


def _reproducibility_row(cfg: StressTestConfig) -> tuple[str, str, str]:
    links = [_split_link(link) for link in cfg.public_links]
    labels = [label for label, _ in links if label]
    evidence = f"fixed random seed {cfg.seed}"
    if labels:
        evidence = f"{' + '.join(labels)}; {evidence}"
    output = " | ".join(url for _, url in links) if links else "no public links configured"
    return ("Public reproducibility", evidence[0].upper() + evidence[1:], output)

ProgressFn = Callable[[str], None]


def prepare_diagnostic_dataset(raw: pd.DataFrame) -> pd.DataFrame:
    """lambda>0 rows with canonical 11D column names (see probe_experiments.COLUMN_ALIASES)."""
    return normalize_diagnostic_dataframe(raw, target_col=TARGET_COL, group_col=GROUP_COL)


def profile_vector(metrics: dict) -> list[float]:
    """Maps a calculate_metrics_platform_binary() dict to the FULL_11D order."""
    canonical = {**metrics, "f1": metrics["f1_score"], "log_loss": metrics["log_loss_value"]}
    return [canonical[c] for c in FULL_11D]


# Metric names used by the notebook in the PCA / correlation outputs (its COL_MAP keys).
NOTEBOOK_METRIC_NAMES: dict[str, str] = {c: c for c in FULL_11D} | {"specificity_derived": "specificity"}
NOTEBOOK_11D: list[str] = [NOTEBOOK_METRIC_NAMES[c] for c in FULL_11D]


def run_pca(df_diag: pd.DataFrame, n_loadings: int = 3) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Block C: explained variance of the standardized 11 metrics and first-component loadings."""
    pca = PCA().fit(StandardScaler().fit_transform(feature_matrix(df_diag, FULL_11D)))
    cum_var = np.cumsum(pca.explained_variance_ratio_)
    df_pca = pd.DataFrame({
        "Component": [f"PC{i + 1}" for i in range(len(FULL_11D))],
        "Explained_Variance_%": np.round(pca.explained_variance_ratio_ * 100, 2),
        "Cumulative_Variance_%": np.round(cum_var * 100, 2),
    })
    k = min(n_loadings, len(FULL_11D))
    df_loadings = pd.DataFrame(
        pca.components_[:k].T, index=NOTEBOOK_11D, columns=[f"PC{i + 1}_loading" for i in range(k)]
    ).round(3)
    return df_pca, df_loadings


def run_redundancy(
    df_diag: pd.DataFrame, rho_threshold: float = 0.9
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Block D: Spearman matrix, cosine similarity of standardized metrics (equivalent to
    Pearson for centred columns) and pairs with |rho| > threshold.
    """
    corr = df_diag[FULL_11D].corr(method="spearman")
    corr.index = corr.columns = NOTEBOOK_11D
    X_scaled = StandardScaler().fit_transform(feature_matrix(df_diag, FULL_11D))
    df_cos = pd.DataFrame(cosine_similarity(X_scaled.T), index=NOTEBOOK_11D, columns=NOTEBOOK_11D)

    pairs = [
        {"metric_1": a, "metric_2": b, "spearman_rho": round(float(corr.loc[a, b]), 4)}
        for i, a in enumerate(NOTEBOOK_11D)
        for b in NOTEBOOK_11D[i + 1:]
        if abs(corr.loc[a, b]) > rho_threshold
    ]
    df_redundant = pd.DataFrame(pairs, columns=["metric_1", "metric_2", "spearman_rho"])
    if len(df_redundant):
        df_redundant = df_redundant.reindex(
            df_redundant["spearman_rho"].abs().sort_values(ascending=False).index
        )
    return corr, df_cos, df_redundant


def fit_ood_probes(df_diag: pd.DataFrame, cfg: StressTestConfig = StressTestConfig()) -> dict[str, Any]:
    """LR / HistGB / MLP probes trained on the full Gaussian dataset (inputs of block E)."""
    X_train = feature_matrix(df_diag, FULL_11D)
    y_train = df_diag[TARGET_COL].astype(str).to_numpy()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return {
            "LR_BA (Zero-Shot)": build_base_linear_probe(cfg.seed).fit(X_train, y_train),
            "HistGB_BA (Zero-Shot)": build_hgb_probe(cfg.seed).fit(X_train, y_train),
            "MLP_BA (Zero-Shot)": build_mlp_probe(cfg.seed).fit(X_train, y_train),
        }


def run_ood_transfer(
    df_diag: pd.DataFrame,
    cfg: StressTestConfig = StressTestConfig(),
    distributions: Optional[list[str]] = None,
    probes: Optional[dict[str, Any]] = None,
) -> pd.DataFrame:
    """
    Block E (Table 11): probes trained on the full Gaussian dataset are applied zero-shot to
    profiles generated from non-Gaussian baselines with the same failure modes.
    """
    probes = probes or fit_ood_probes(df_diag, cfg)
    rng = np.random.default_rng(cfg.seed)
    rows = []
    for dist in distributions or cfg.ood_distributions:
        X_ood, y_ood = [], []
        for prevalence in cfg.ood_prevalences:
            for _ in range(cfg.ood_replicates):
                yb, pb = generate_non_gaussian_baseline(dist, cfg.n, prevalence, rng)
                for failure_mode, direction in FAILURE_PATHS:
                    for lam in cfg.nonzero_severities:
                        p_stressed = apply_failure_mode(pb, lam, failure_mode, direction, cfg)
                        X_ood.append(profile_vector(calculate_metrics_platform_binary(yb, p_stressed)))
                        y_ood.append(f"{failure_mode}:{direction}")
        X_ood = np.nan_to_num(np.asarray(X_ood, dtype=float), nan=0.0)
        rows.append({
            "Non-Gaussian Test Distribution": dist,
            "Scenarios": len(y_ood),
            **{name: round(balanced_accuracy_score(y_ood, model.predict(X_ood)), 4)
               for name, model in probes.items()},
        })
    return pd.DataFrame(rows)


# ------------------------------------------------------------------
# Optional independent cross-check of Table 11 (last OOD cell of the notebook)
# ------------------------------------------------------------------

def _crosscheck_degradation(p: np.ndarray, path_label: str, lam: float, cfg: StressTestConfig) -> np.ndarray:
    """Paper equations (8)-(15) written directly from the path label, independently of apply_failure_mode."""
    from scipy.special import expit, logit

    lam = float(lam)
    eps = np.finfo(float).eps
    z = logit(np.clip(p, eps, 1.0 - eps))
    pl = path_label.lower()

    if "collapse" in pl and "pos" in pl:
        return (1.0 - lam) * p + lam * cfg.collapse_positive_target
    if "collapse" in pl and "neg" in pl:
        return (1.0 - lam) * p + lam * cfg.collapse_negative_target
    if "bias" in pl and "pos" in pl:
        return expit(z + cfg.max_logit_bias * lam)
    if "bias" in pl and "neg" in pl:
        return expit(z - cfg.max_logit_bias * lam)
    if "calib" in pl and "over" in pl:
        return expit(z / (1.0 - (1.0 - cfg.min_temperature) * lam))
    if "calib" in pl and "under" in pl:
        return expit(z / (1.0 + (cfg.max_temperature - 1.0) * lam))
    if "inversion" in pl:
        return (1.0 - lam) * p + lam * (1.0 - p)
    raise ValueError(f"Unknown path_label: {path_label}")


def _crosscheck_profile(y_true: np.ndarray, p_prob: np.ndarray) -> list[float]:
    """The 11 metrics in FULL_11D order, computed directly with scikit-learn."""
    from sklearn.metrics import (
        accuracy_score, average_precision_score, brier_score_loss, confusion_matrix, f1_score,
        log_loss, matthews_corrcoef, precision_score, recall_score, roc_auc_score,
    )

    y_score = np.asarray(p_prob).reshape(-1)
    y_pred = (y_score > 0.5).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    m = {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, average="binary", zero_division=0),
        "recall": recall_score(y_true, y_pred, average="binary", zero_division=0),
        "f1": f1_score(y_true, y_pred, average="binary", zero_division=0),
        "mcc": matthews_corrcoef(y_true, y_pred),
        "balanced_accuracy": balanced_accuracy_score(y_true, y_pred),
        "specificity_derived": tn / (tn + fp) if (tn + fp) > 0 else 0.0,
        "roc_auc": roc_auc_score(y_true, y_score),
        "pr_auc": average_precision_score(y_true, y_score),
        "log_loss": log_loss(y_true, y_score, labels=[0, 1]),
        "brier_score": brier_score_loss(y_true, y_score),
    }
    return [float(m[c]) for c in FULL_11D]


def run_ood_crosscheck(
    df_diag: pd.DataFrame,
    cfg: StressTestConfig = StressTestConfig(),
    probes: Optional[dict[str, Any]] = None,
) -> pd.DataFrame:
    """
    Rebuilds Table 11 with an independent degradation / metric implementation and a fresh RNG
    with the same seed; it should reproduce reviewer_non_gaussian_ood_transfer.csv exactly.
    """
    probes = probes or fit_ood_probes(df_diag, cfg)
    labels = sorted(df_diag[TARGET_COL].astype(str).unique())
    rng = np.random.default_rng(cfg.seed)
    rows = []
    for dist in cfg.ood_distributions:
        X_ood, y_ood = [], []
        for prevalence in cfg.ood_prevalences:
            for _ in range(cfg.ood_replicates):
                yb, pb = generate_non_gaussian_baseline(dist, cfg.n, prevalence, rng)
                for label in labels:
                    for lam in cfg.nonzero_severities:
                        X_ood.append(_crosscheck_profile(yb, _crosscheck_degradation(pb, label, lam, cfg)))
                        y_ood.append(label)
        X_ood = np.nan_to_num(np.asarray(X_ood, dtype=float), nan=0.0)
        rows.append({
            "Non-Gaussian Test Distribution": dist,
            "Scenarios": len(y_ood),
            **{name: round(balanced_accuracy_score(y_ood, model.predict(X_ood)), 4)
               for name, model in probes.items()},
        })
    return pd.DataFrame(rows)


def run_reviewer_analyses(
    raw: pd.DataFrame,
    cfg: StressTestConfig = StressTestConfig(),
    n_jobs: int = -1,
    progress: Optional[ProgressFn] = None,
) -> dict[str, Any]:
    """Runs blocks A-E; keys are output filenames (DataFrames, plus the manuscript .txt as str)."""
    say = progress or (lambda _msg: None)
    df_diag = prepare_diagnostic_dataset(raw)
    say(f"Diagnostic dataset: {df_diag.shape}, {df_diag[GROUP_COL].nunique()} groups")

    common = dict(n_splits=cfg.cv_splits, n_boot=cfg.n_boot, seed=cfg.seed, n_jobs=n_jobs)
    say("Block A: extended ablation + Wilcoxon")
    df_ablation, df_wilcoxon = run_ablation_study(df_diag, **common)
    say("Block B: alternative probes")
    df_probes = run_diagnostic_model_comparison(df_diag, **common)
    say("Block C: PCA")
    df_pca, df_loadings = run_pca(df_diag)
    say("Block D: redundancy")
    corr, df_cos, df_redundant = run_redundancy(df_diag)
    say("Block E: zero-shot OOD transfer")
    ood_probes = fit_ood_probes(df_diag, cfg)
    df_ood = run_ood_transfer(df_diag, cfg, probes=ood_probes)
    df_ood_check = None
    if cfg.ood_crosscheck:
        say("Block E: independent cross-check of Table 11")
        df_ood_check = run_ood_crosscheck(df_diag, cfg, probes=ood_probes)

    audit = pd.DataFrame([
        ("95% bootstrap confidence intervals + paired Wilcoxon tests",
         f"Group-level bootstrap ({cfg.n_boot} resamples) and paired one-sided Wilcoxon across "
         f"{df_diag[GROUP_COL].nunique()} groups",
         "reviewer_table8_extended_ablation.csv; reviewer_wilcoxon_full_vs_reduced.csv"),
        ("9D ablation / redundancy analysis",
         "11D profile compared with 9D panel excluding F1 and Balanced Accuracy plus 6D/3D/1D baselines",
         "reviewer_table8_extended_ablation.csv"),
        ("Correlation + PCA",
         "Spearman matrix, cosine similarity, redundant pairs, PCA explained variance and loadings",
         "reviewer_spearman_correlation_matrix.csv; reviewer_cosine_similarity_matrix.csv; "
         "reviewer_pca_dimensionality.csv; reviewer_pca_loadings.csv"),
        ("Random Forest / HistGradientBoosting / MLP",
         f"Alternative probes evaluated on the exact same {cfg.cv_splits}-fold GroupKFold partitions",
         "reviewer_alternative_probes.csv"),
        ("OOD transfer",
         "Zero-shot transfer to: " + "; ".join(cfg.ood_distributions),
         "reviewer_non_gaussian_ood_transfer.csv"),
        _reproducibility_row(cfg),
    ], columns=["Reviewer-requested item", "Notebook evidence", "Generated output"])

    manuscript = "\n".join([
        "VISIONMETRICS — MANUSCRIPT-READY VALUES",
        "=" * 72,
        "",
        "TABLE 8 — ABLATION / BOOTSTRAP / WILCOXON",
        df_ablation.to_string(index=False),
        "",
        "DETAILED WILCOXON (includes stable log10 p-values)",
        df_wilcoxon.to_string(index=False),
        "",
        "TABLE 9 — ALTERNATIVE DIAGNOSTIC PROBES",
        df_probes.to_string(index=False),
        "",
        "PCA",
        df_pca.to_string(index=False),
        "",
        "HIGH SPEARMAN CORRELATIONS (|rho| > 0.90)",
        df_redundant.to_string(index=False) if len(df_redundant) else "None",
        "",
        "TABLE 11 — ZERO-SHOT OOD",
        df_ood.to_string(index=False),
        *([""] + list(cfg.public_links) if cfg.public_links else []),
    ])

    outputs = {
        "reviewer_table8_extended_ablation.csv": df_ablation,
        "reviewer_wilcoxon_full_vs_reduced.csv": df_wilcoxon,
        "reviewer_alternative_probes.csv": df_probes,
        "reviewer_pca_dimensionality.csv": df_pca,
        "reviewer_pca_loadings.csv": df_loadings,
        "reviewer_spearman_correlation_matrix.csv": corr,
        "reviewer_cosine_similarity_matrix.csv": df_cos,
        "reviewer_redundant_metric_pairs.csv": df_redundant,
        "reviewer_non_gaussian_ood_transfer.csv": df_ood,
        "reviewer_revision_audit_summary.csv": audit,
        "manuscript_ready_values.txt": manuscript,
    }
    if df_ood_check is not None:
        outputs["reviewer_non_gaussian_ood_transfer_crosscheck.csv"] = df_ood_check
    return outputs
