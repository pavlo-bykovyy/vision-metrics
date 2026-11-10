"""
Monte Carlo summaries, failure signatures, metric-family ablation, leave-one-prevalence-out
validation, invariance checks and manuscript tables (stress test v4).
"""
from __future__ import annotations

from typing import Any, Optional

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from api_cv.services.stress_test.config import (
    ALL_DIAGNOSTIC_METRICS,
    FAILURE_PATHS,
    METRIC_FAMILIES,
    SEVERITY_BAND_NAMES,
    StressTestConfig,
)

SUMMARY_GROUP_COLS = ["failure_mode", "direction", "path_label", "prevalence_target", "severity"]


def _linear_probe() -> Pipeline:
    return Pipeline([
        ("scale", StandardScaler()),
        ("clf", LogisticRegression(max_iter=3000, class_weight="balanced")),
    ])


def _features(data: pd.DataFrame, features: list[str]) -> pd.DataFrame:
    return data[features].replace([np.inf, -np.inf], np.nan).fillna(0.0)


def _scores(y_true, y_pred) -> dict[str, float]:
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "balanced_accuracy": balanced_accuracy_score(y_true, y_pred),
        "macro_f1": f1_score(y_true, y_pred, average="macro"),
    }


DEFAULT_BAND_EDGES: tuple[float, float] = StressTestConfig().severity_band_edges


def _fmt_severity(v: float) -> str:
    """0.1 -> '0.1', 1.0 -> '1.0', 0.25 -> '0.25' (matches the article labels)."""
    s = f"{v:.2f}".rstrip("0")
    return s + "0" if s.endswith(".") else s


def _band_index(v: float, edges: tuple[float, float]) -> int:
    if v <= edges[0] + 1e-9:
        return 0
    if v <= edges[1] + 1e-9:
        return 1
    return 2


def severity_band_labels(
    severities, edges: tuple[float, float] = DEFAULT_BAND_EDGES
) -> dict[float, str]:
    """
    Maps every lambda > 0 to its band label "<name>_<min>_<max>", where min/max are the
    severities actually present in the band. The article grid with edges (0.3, 0.7) gives
    mild_0.1_0.3, moderate_0.4_0.7 and severe_0.8_1.0.
    """
    nonzero = sorted({float(v) for v in severities if v > 0})
    members: dict[int, list[float]] = {}
    for v in nonzero:
        members.setdefault(_band_index(v, edges), []).append(v)

    labels = {}
    for idx, values in members.items():
        label = f"{SEVERITY_BAND_NAMES[idx]}_{_fmt_severity(values[0])}_{_fmt_severity(values[-1])}"
        labels.update({v: label for v in values})
    return labels


def _degraded(raw: pd.DataFrame, band_edges: tuple[float, float] = DEFAULT_BAND_EDGES) -> pd.DataFrame:
    """lambda=0 is excluded: every failure path is identical there by construction."""
    data = raw[raw["severity"] > 0].copy()
    labels = severity_band_labels(data["severity"].unique(), band_edges)
    data["severity_band"] = data["severity"].astype(float).map(labels)
    return data


# ------------------------------------------------------------------
# Summaries
# ------------------------------------------------------------------

def summarize_results(raw: pd.DataFrame) -> pd.DataFrame:
    """Long table: mean / sd / median / 95% MC interval per path, prevalence, severity, metric."""
    chunks = []
    for metric in ALL_DIAGNOSTIC_METRICS:
        g = raw.groupby(SUMMARY_GROUP_COLS, dropna=False)[metric]
        x = g.agg(mean="mean", sd="std", median="median", n_rep="count").reset_index()

        q = g.quantile([0.025, 0.975]).unstack()
        q.columns = ["p025", "p975"]
        x = x.merge(q.reset_index(), on=SUMMARY_GROUP_COLS, how="left")
        x.insert(len(SUMMARY_GROUP_COLS), "metric", metric)
        chunks.append(x)
    return pd.concat(chunks, ignore_index=True)


def sensitivity_table(summary: pd.DataFrame) -> pd.DataFrame:
    """Spearman rho between severity and the MC mean, plus endpoint delta (lambda=1 minus lambda=0)."""
    rows = []
    keys = ["failure_mode", "direction", "path_label", "prevalence_target", "metric"]
    for k, g in summary.groupby(keys):
        g = g.sort_values("severity")
        x = g["severity"].to_numpy()
        y = g["mean"].to_numpy()

        if np.nanstd(y) < 1e-14:
            rho, pval = np.nan, np.nan
        else:
            rho, pval = spearmanr(x, y, nan_policy="omit")

        y0 = g.loc[np.isclose(g["severity"], 0), "mean"].iloc[0]
        y1 = g.loc[np.isclose(g["severity"], 1), "mean"].iloc[0]
        rows.append({
            **dict(zip(keys, k)),
            "spearman_rho": rho,
            "spearman_p": pval,
            "endpoint_delta": y1 - y0,
        })
    return pd.DataFrame(rows)


def build_signature_matrix(summary: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Endpoint response relative to lambda=0, normalized per metric by the max |delta| across
    all paths and prevalences, so it is bounded in [-1, 1]. Used only as a response-profile
    visualization, not as a new performance metric.
    Returns (per-prevalence table, table averaged over prevalence).
    """
    endpoint = summary[np.isclose(summary["severity"], 1.0)]
    baseline = summary[np.isclose(summary["severity"], 0.0)]

    base = baseline[["path_label", "prevalence_target", "metric", "mean"]].rename(
        columns={"mean": "baseline_mean"}
    )
    ep = endpoint[
        ["failure_mode", "direction", "path_label", "prevalence_target", "metric", "mean"]
    ].rename(columns={"mean": "endpoint_mean"})

    x = ep.merge(base, on=["path_label", "prevalence_target", "metric"], how="left")
    x["raw_delta"] = x["endpoint_mean"] - x["baseline_mean"]

    scale = (
        x.groupby("metric")["raw_delta"]
        .apply(lambda s: max(float(np.nanmax(np.abs(s))), 1e-15))
        .rename("metric_max_abs_delta")
        .reset_index()
    )
    x = x.merge(scale, on="metric", how="left")
    x["normalized_response"] = x["raw_delta"] / x["metric_max_abs_delta"]

    agg = x.groupby(["failure_mode", "direction", "path_label", "metric"], as_index=False).agg(
        mean_raw_delta=("raw_delta", "mean"),
        mean_normalized_response=("normalized_response", "mean"),
    )
    return x, agg


# ------------------------------------------------------------------
# Failure-mode distinguishability + metric-family ablation
# ------------------------------------------------------------------

def grouped_cv_predictions(
    data: pd.DataFrame, features: list[str], n_splits: int = 5
) -> tuple[pd.Series, pd.DataFrame]:
    """Out-of-fold path predictions with GroupKFold by baseline replicate."""
    X = _features(data, features)
    y = data["path_label"].astype(str)
    groups = data["group_id"].astype(str)

    pred = pd.Series(index=data.index, dtype="object")
    fold_scores = []
    for fold, (tr, te) in enumerate(GroupKFold(n_splits=n_splits).split(X, y, groups=groups), start=1):
        model = _linear_probe().fit(X.iloc[tr], y.iloc[tr])
        p = model.predict(X.iloc[te])
        pred.iloc[te] = p
        fold_scores.append({"fold": fold, **_scores(y.iloc[te], p)})
    return pred, pd.DataFrame(fold_scores)


def evaluate_predictions(data: pd.DataFrame, pred: pd.Series, family: str) -> pd.DataFrame:
    tmp = data.assign(predicted_path=pred)
    scopes = [("overall", tmp), *tmp.groupby("severity_band")]
    return pd.DataFrame([
        {
            "metric_family": family,
            "scope": scope,
            "n": len(g),
            **_scores(g["path_label"], g["predicted_path"]),
        }
        for scope, g in scopes
    ])


def run_metric_family_ablation(
    raw: pd.DataFrame,
    n_splits: int = 5,
    band_edges: tuple[float, float] = DEFAULT_BAND_EDGES,
) -> dict[str, pd.DataFrame]:
    """
    Keys: performance (pooled, overall + per severity band), folds (per-fold scores),
    confusion_matrix and classification_report (full panel only).
    """
    data = _degraded(raw, band_edges)

    all_perf, all_folds = [], []
    full_pred = None
    for family, features in METRIC_FAMILIES.items():
        pred, folds = grouped_cv_predictions(data, features, n_splits=n_splits)
        all_perf.append(evaluate_predictions(data, pred, family))
        folds.insert(0, "metric_family", family)
        all_folds.append(folds)
        if family == "full_panel":
            full_pred = pred

    classes = sorted(data["path_label"].unique())
    cm = confusion_matrix(data["path_label"], full_pred, labels=classes)
    report = classification_report(
        data["path_label"], full_pred, labels=classes, output_dict=True, zero_division=0
    )
    return {
        "performance": pd.concat(all_perf, ignore_index=True),
        "folds": pd.concat(all_folds, ignore_index=True),
        "confusion_matrix": pd.DataFrame(cm, index=classes, columns=classes),
        "classification_report": (
            pd.DataFrame(report).T.reset_index().rename(columns={"index": "class"})
        ),
    }


def leave_one_prevalence_out_validation(
    raw: pd.DataFrame,
    prevalences: Optional[list[float]] = None,
    band_edges: tuple[float, float] = DEFAULT_BAND_EDGES,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Train on all but one prevalence, test on the unseen one, for every metric family.
    Checks that signatures generalize across class prevalence.
    Returns (performance, predictions).
    """
    data = _degraded(raw, band_edges)
    prevalences = prevalences or sorted(data["prevalence_target"].unique(), reverse=True)

    performance_rows, prediction_rows = [], []
    for heldout in prevalences:
        is_test = np.isclose(data["prevalence_target"], heldout)
        train, test = data[~is_test], data[is_test]

        for family, features in METRIC_FAMILIES.items():
            model = _linear_probe().fit(_features(train, features), train["path_label"].astype(str))
            pred = model.predict(_features(test, features))

            result = test[
                ["replicate", "group_id", "prevalence_target", "severity", "severity_band", "path_label"]
            ].copy()
            result["metric_family"] = family
            result["predicted_path"] = pred
            prediction_rows.append(result)

            for scope, g in [("overall", result), *result.groupby("severity_band")]:
                performance_rows.append({
                    "heldout_prevalence": heldout,
                    "metric_family": family,
                    "scope": scope,
                    "n": len(g),
                    **_scores(g["path_label"], g["predicted_path"]),
                })

    return pd.DataFrame(performance_rows), pd.concat(prediction_rows, ignore_index=True)


# ------------------------------------------------------------------
# Validation checks and manuscript tables
# ------------------------------------------------------------------

def theoretical_invariance_checks(summary: pd.DataFrame) -> pd.DataFrame:
    """
    Temperature scaling must not change hard decisions, ROC AUC or AP; score bias must keep
    ROC AUC/AP while altering hard predictions. Reports the max span of each MC-mean trajectory.
    """
    rows = []
    paths = ["calibration_drift:over", "calibration_drift:under", "score_bias:positive", "score_bias:negative"]
    metrics = ["roc_auc", "pr_auc", "accuracy", "balanced_accuracy", "log_loss_value", "brier_score"]
    for path in paths:
        for metric in metrics:
            g = summary[(summary["path_label"] == path) & (summary["metric"] == metric)]
            max_span = (
                g.groupby("prevalence_target")["mean"]
                .agg(lambda s: float(np.nanmax(s) - np.nanmin(s)))
                .max()
            )
            rows.append({
                "path_label": path,
                "metric": metric,
                "max_trajectory_span_across_prevalence": max_span,
            })
    return pd.DataFrame(rows)


def build_publication_tables(
    raw: pd.DataFrame,
    fold_performance: pd.DataFrame,
    family_performance: pd.DataFrame,
    loo_performance: pd.DataFrame,
    invariance: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    """Compact tables to copy into the manuscript, keyed by output filename."""
    ablation_cv = fold_performance.groupby("metric_family", as_index=False).agg(
        accuracy_mean=("accuracy", "mean"),
        accuracy_sd=("accuracy", "std"),
        balanced_accuracy_mean=("balanced_accuracy", "mean"),
        balanced_accuracy_sd=("balanced_accuracy", "std"),
        macro_f1_mean=("macro_f1", "mean"),
        macro_f1_sd=("macro_f1", "std"),
    )
    pooled = family_performance.loc[
        family_performance["scope"] == "overall",
        ["metric_family", "accuracy", "balanced_accuracy", "macro_f1"],
    ].rename(columns={
        "accuracy": "accuracy_pooled",
        "balanced_accuracy": "balanced_accuracy_pooled",
        "macro_f1": "macro_f1_pooled",
    })
    ablation_cv = ablation_cv.merge(pooled, on="metric_family", how="left")

    baseline_raw = raw[(raw["path_label"] == "collapse:positive") & np.isclose(raw["severity"], 0.0)]
    baseline_table = (
        baseline_raw.groupby("prevalence_target")[ALL_DIAGNOSTIC_METRICS]
        .mean()
        .reset_index()
        .rename(columns={"prevalence_target": "prevalence"})
        .sort_values("prevalence")
    )

    return {
        "publication_table_metric_family_ablation.csv": ablation_cv,
        "publication_table_leave_one_prevalence_out.csv": loo_performance[
            loo_performance["scope"] == "overall"
        ].copy(),
        "publication_table_diagnostic_performance_by_severity.csv": family_performance[
            (family_performance["metric_family"] == "full_panel")
            & (family_performance["scope"] != "overall")
        ].copy(),
        "publication_table_calibration_invariance.csv": invariance[
            invariance["path_label"].isin(["calibration_drift:over", "calibration_drift:under"])
        ].copy(),
        "publication_table_baseline_prevalence.csv": baseline_table,
    }


def _severity_grid_text(severities) -> str:
    """'0.0 to 1.0; step 0.1' for an even grid (notebook wording), else the number of levels."""
    sev = np.asarray(severities, dtype=float)
    head = f"{sev.min()} to {sev.max()}"
    steps = np.diff(sev)
    if len(steps) and np.allclose(steps, steps[0], atol=1e-9):
        return f"{head}; step {round(float(steps[0]), 6):g}"
    return f"{head}; {len(sev)} levels"


def simulation_design_table(cfg: StressTestConfig) -> pd.DataFrame:
    """The notebook's v4 design rows (same order and wording), then the settings it did not record."""
    rows: list[tuple[str, Any]] = [
        ("Sample size per replicate", cfg.n),
        ("Monte Carlo repetitions", cfg.replicates),
        ("Positive-class prevalence", ", ".join(map(str, cfg.prevalences))),
        ("Severity", _severity_grid_text(cfg.severities)),
        ("VisionMetrics binary threshold", "0.5"),
        ("Binary threshold rule", "y_pred_probs > 0.5"),
        ("PR AUC implementation", "sklearn.average_precision_score"),
        ("Number of failure paths", len(FAILURE_PATHS)),
        ("Primary cross-validation", f"{cfg.cv_splits}-fold GroupKFold by baseline replicate"),
        ("Out-of-prevalence validation", "Leave-one-prevalence-out"),
        ("Metric-family ablation", ", ".join(METRIC_FAMILIES)),
        # --- not in the notebook table ---
        ("Random seed", cfg.seed),
        ("Severity bands (upper bounds)",
         f"mild <= {cfg.severity_mild_max}, moderate <= {cfg.severity_moderate_max}, severe > {cfg.severity_moderate_max}"),
        ("Collapse targets (positive / negative)",
         f"{cfg.collapse_positive_target} / {cfg.collapse_negative_target}"),
    ]
    return pd.DataFrame({"factor": [r[0] for r in rows], "value": [str(r[1]) for r in rows]})
