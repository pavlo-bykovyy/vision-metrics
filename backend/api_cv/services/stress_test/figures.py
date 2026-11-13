"""
Publication figures (Figure_01 ... Figure_12) built from the CSV outputs of the stress test.
matplotlib is imported lazily because it is not part of any container's requirements.
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable, Iterable, Optional

import numpy as np
import pandas as pd

from api_cv.services.stress_test.config import ALL_DIAGNOSTIC_METRICS, PATH_LABELS, SEVERITY_BAND_NAMES

METRIC_LABELS = {
    "accuracy": "Accuracy",
    "precision": "Precision",
    "recall": "Recall",
    "specificity_derived": "Specificity",
    "f1_score": "F1-score",
    "balanced_accuracy": "Balanced Accuracy",
    "mcc": "MCC",
    "roc_auc": "ROC AUC",
    "pr_auc": "AP",  # average precision (sklearn.average_precision_score), as in the paper
    "log_loss_value": "Log Loss",
    "brier_score": "Brier Score",
}

FAILURE_LABELS = {
    "calibration_drift:over": "Calibration drift\n(overconfidence)",
    "calibration_drift:under": "Calibration drift\n(underconfidence)",
    "collapse:negative": "Negative-class\ncollapse",
    "collapse:positive": "Positive-class\ncollapse",
    "score_bias:negative": "Negative\nscore bias",
    "score_bias:positive": "Positive\nscore bias",
    "score_inversion:none": "Score\ninversion",
}

FAMILY_ORDER = ["full_panel", "threshold_confusion", "ranking_only", "probability_only"]
FAMILY_LABELS = {
    "full_panel": "Full multi-metric panel",
    "threshold_confusion": "Threshold / confusion",
    "ranking_only": "Ranking only",
    "probability_only": "Probability only",
}

FAILURE_ORDER = sorted(PATH_LABELS)
CHANCE_7 = 1 / 7
TRAJECTORY_PREVALENCE = 0.30


def _pyplot():
    try:
        import matplotlib
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise ImportError(
            "matplotlib is required for figures: pip install matplotlib"
        ) from exc
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({
        "font.size": 11,
        "axes.titlesize": 14,
        "axes.labelsize": 12,
        "legend.fontsize": 10,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "figure.dpi": 150,
    })
    return plt


class _FigureWriter:
    def __init__(self, fig_dir: Path, formats: Iterable[str], dpi: int, titles: bool = False):
        self.fig_dir = fig_dir
        self.formats = tuple(formats)
        self.dpi = dpi
        self.titles = titles
        self.saved: list[Path] = []
        fig_dir.mkdir(parents=True, exist_ok=True)

    def title(self, ax, text: str) -> None:
        """In-figure titles are off by default: the MDPI captions already carry them."""
        if self.titles:
            ax.set_title(text)

    def save(self, plt, fig, name: str) -> None:
        for ext in self.formats:
            path = self.fig_dir / f"{name}.{ext}"
            fig.savefig(path, dpi=self.dpi if ext == "png" else "figure", bbox_inches="tight")
            self.saved.append(path)
        plt.close(fig)


def _heatmap_axes(ax, matrix: pd.DataFrame, x_labels: dict, y_labels: dict, rotate_x: bool = True):
    ax.set_xticks(np.arange(len(matrix.columns)))
    ax.set_xticklabels([x_labels.get(c, c) for c in matrix.columns],
                       rotation=45 if rotate_x else 0, ha="right" if rotate_x else "center")
    ax.set_yticks(np.arange(len(matrix.index)))
    ax.set_yticklabels([y_labels.get(v, v) for v in matrix.index])


def _metric_by_failure(df: pd.DataFrame, values: str) -> pd.DataFrame:
    m = df.pivot_table(index="path_label", columns="metric", values=values)
    m = m.reindex(columns=[c for c in ALL_DIAGNOSTIC_METRICS if c in m.columns])
    return m.reindex([x for x in FAILURE_ORDER if x in m.index])


def _band_rank(label: str) -> int:
    name = str(label).split("_", 1)[0]
    return SEVERITY_BAND_NAMES.index(name) if name in SEVERITY_BAND_NAMES else len(SEVERITY_BAND_NAMES)


def _band_tick(label: str) -> str:
    """'mild_0.1_0.3' -> 'Mild\\nλ = 0.1–0.3' (single-severity band -> 'λ = 0.5')."""
    parts = str(label).split("_")
    if len(parts) != 3:
        return str(label)
    name, lo, hi = parts
    return f"{name.capitalize()}\nλ = {lo}" + ("" if lo == hi else f"–{hi}")


def _trajectory_prevalence(summary: pd.DataFrame) -> Optional[float]:
    """The article's 0.30 when it was simulated, otherwise the closest prevalence of the run."""
    available = summary["prevalence_target"].dropna().unique()
    if len(available) == 0:
        return None
    return float(min(available, key=lambda p: abs(p - TRAJECTORY_PREVALENCE)))


def _trajectories(plt, w, summary, path_label, metrics, title, xlabel, name, inversion=False):
    prevalence = _trajectory_prevalence(summary)
    if prevalence is None:
        return
    if not np.isclose(prevalence, TRAJECTORY_PREVALENCE):
        title = f"{title} (prevalence = {prevalence:g})"
    df = summary[
        (summary["path_label"] == path_label)
        & np.isclose(summary["prevalence_target"], prevalence)
        & summary["metric"].isin(metrics)
    ]
    fig, ax = plt.subplots(figsize=(9, 6))
    for metric in metrics:
        xdf = df[df["metric"] == metric].sort_values("severity")
        ax.plot(xdf["severity"], xdf["mean"], marker="o", linewidth=2, label=METRIC_LABELS[metric])
    if inversion:
        ax.axvline(0.5, linestyle="--", linewidth=1.5, label="Complete uncertainty at λ = 0.5")
        ax.axhline(0.5, linestyle=":", linewidth=1)
    else:
        ax.axhline(0.5, linestyle="--", linewidth=1)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Monte Carlo mean")
    w.title(ax, title)
    ax.legend(ncol=2)
    ax.grid(alpha=0.2)
    fig.tight_layout()
    w.save(plt, fig, name)


def _calibration(plt, w, summary, metric, ylabel, name):
    df = (
        summary[(summary["failure_mode"] == "calibration_drift") & (summary["metric"] == metric)]
        .groupby(["direction", "severity"], as_index=False)
        .agg(mean=("mean", "mean"))
    )
    fig, ax = plt.subplots(figsize=(8, 5.5))
    for direction, label in (("over", "Overconfidence"), ("under", "Underconfidence")):
        xdf = df[df["direction"] == direction].sort_values("severity")
        ax.plot(xdf["severity"], xdf["mean"], marker="o", linewidth=2, label=label)
    ax.set_xlabel("Calibration degradation severity λ")
    ax.set_ylabel(ylabel)
    w.title(ax, f"{ylabel} response to probability calibration degradation")
    ax.legend()
    ax.grid(alpha=0.2)
    fig.tight_layout()
    w.save(plt, fig, name)


def generate_publication_figures(
    results_dir: Path,
    fig_dir: Optional[Path] = None,
    formats: Iterable[str] = ("png", "pdf", "svg"),
    dpi: int = 600,
    log: Callable[[str], None] = lambda _msg: None,
    titles: bool = False,
) -> list[Path]:
    """Draws every figure whose source CSV exists in `results_dir`; returns saved paths.
    In-figure titles are omitted unless `titles=True` (MDPI captions duplicate them)."""
    plt = _pyplot()
    results_dir = Path(results_dir)
    w = _FigureWriter(fig_dir or results_dir / "publication_figures", formats, dpi, titles)

    def read(name: str, **kw) -> Optional[pd.DataFrame]:
        path = results_dir / name
        if not path.exists():
            log(f"skip: {name} not found")
            return None
        return pd.read_csv(path, **kw)

    # Figure 1 — baseline metric behavior under class imbalance
    df = read("publication_table_baseline_prevalence.csv")
    if df is not None:
        df = df.sort_values("prevalence")
        fig, ax = plt.subplots(figsize=(9, 6))
        for metric in ["accuracy", "f1_score", "balanced_accuracy", "mcc", "roc_auc", "pr_auc"]:
            if metric in df.columns:
                ax.plot(df["prevalence"], df[metric], marker="o", linewidth=2, label=METRIC_LABELS[metric])
        ax.set_xlabel("Positive-class prevalence")
        ax.set_ylabel("Metric value")
        ax.set_ylim(0, 1)
        ax.set_xticks(sorted(df["prevalence"].unique()))
        w.title(ax, "Baseline metric behavior under changing class prevalence")
        ax.legend(frameon=True, ncol=2)
        ax.grid(alpha=0.2)
        fig.tight_layout()
        w.save(plt, fig, "Figure_01_baseline_prevalence_effect")

    # Figure 2 — diagnostic performance vs failure severity
    df = read("publication_table_diagnostic_performance_by_severity.csv")
    if df is not None:
        df = df.assign(_band=df["scope"].map(_band_rank)).sort_values("_band")
        x = np.arange(len(df))
        fig, ax = plt.subplots(figsize=(8, 5.5))
        ax.plot(x, df["balanced_accuracy"], marker="o", linewidth=2.5, label="Balanced Accuracy")
        ax.plot(x, df["macro_f1"], marker="s", linewidth=2.5, label="Macro-F1")
        ax.axhline(CHANCE_7, linestyle="--", linewidth=1.5, label="Chance level (1/7)")
        ax.set_xticks(x)
        ax.set_xticklabels([_band_tick(s) for s in df["scope"]])
        ax.set_ylim(0, 1)
        ax.set_xlabel("Failure severity")
        ax.set_ylabel("Cross-validated performance")
        w.title(ax, "Diagnostic distinguishability increases with failure severity")
        ax.legend()
        ax.grid(axis="y", alpha=0.2)
        fig.tight_layout()
        w.save(plt, fig, "Figure_02_diagnostic_performance_by_severity")

    # Figure 3 — metric-family ablation (5-fold mean BA ± SD)
    folds = read("metric_family_cv_folds.csv")
    if folds is not None:
        stats = folds.groupby("metric_family", as_index=False).agg(
            mean=("balanced_accuracy", "mean"), sd=("balanced_accuracy", "std")
        )
        stats["metric_family"] = pd.Categorical(stats["metric_family"], categories=FAMILY_ORDER, ordered=True)
        stats = stats.sort_values("metric_family")
        x = np.arange(len(stats))
        fig, ax = plt.subplots(figsize=(9, 6))
        bars = ax.bar(x, stats["mean"], yerr=stats["sd"].fillna(0), capsize=6)
        ax.axhline(CHANCE_7, linestyle="--", linewidth=1.5, label="Chance level (1/7)")
        ax.set_xticks(x)
        ax.set_xticklabels([FAMILY_LABELS.get(str(v), str(v)) for v in stats["metric_family"]],
                           rotation=15, ha="right")
        ax.set_ylim(0, 1)
        ax.set_ylabel("5-fold cross-validated Balanced Accuracy")
        ax.set_xlabel("Metric family")
        w.title(ax, "Diagnostic contribution of complementary metric families")
        for bar, mean, sd in zip(bars, stats["mean"], stats["sd"]):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.03,
                    f"{mean:.3f}\n±{sd:.3f}", ha="center", va="bottom", fontsize=9)
        ax.legend()
        ax.grid(axis="y", alpha=0.2)
        fig.tight_layout()
        w.save(plt, fig, "Figure_03_metric_family_ablation")

    # Figures 4-5 — leave-one-prevalence-out
    loo = read("leave_one_prevalence_out.csv")
    if loo is None:
        loo = read("publication_table_leave_one_prevalence_out.csv")
    if loo is not None:
        if "scope" in loo.columns:
            loo = loo[loo["scope"] == "overall"]

        fig, ax = plt.subplots(figsize=(9, 6))
        for family in FAMILY_ORDER:
            xdf = loo[loo["metric_family"] == family].sort_values("heldout_prevalence")
            if len(xdf):
                ax.plot(xdf["heldout_prevalence"], xdf["balanced_accuracy"], marker="o",
                        linewidth=2, label=FAMILY_LABELS[family])
        ax.axhline(CHANCE_7, linestyle="--", linewidth=1.5, label="Chance level (1/7)")
        ax.set_xlabel("Held-out positive-class prevalence")
        ax.set_ylabel("Balanced Accuracy on unseen prevalence")
        ax.set_ylim(0, 1)
        ax.set_xticks(sorted(loo["heldout_prevalence"].unique()))
        w.title(ax, "Generalization of failure diagnostics to unseen class prevalence")
        ax.legend()
        ax.grid(alpha=0.2)
        fig.tight_layout()
        w.save(plt, fig, "Figure_04_leave_one_prevalence_out")

        matrix = loo.pivot_table(index="metric_family", columns="heldout_prevalence", values="balanced_accuracy")
        matrix = matrix.reindex([f for f in FAMILY_ORDER if f in matrix.index])
        fig, ax = plt.subplots(figsize=(8, 5))
        im = ax.imshow(matrix.values, aspect="auto", vmin=0, vmax=1)
        ax.set_xticks(np.arange(len(matrix.columns)))
        ax.set_xticklabels([f"{v:.2f}" for v in matrix.columns])
        ax.set_yticks(np.arange(len(matrix.index)))
        ax.set_yticklabels([FAMILY_LABELS.get(v, v) for v in matrix.index])
        ax.set_xlabel("Held-out positive-class prevalence")
        ax.set_ylabel("Metric family")
        w.title(ax, "Out-of-prevalence diagnostic robustness")
        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[1]):
                value = matrix.iloc[i, j]
                if not np.isnan(value):
                    ax.text(j, i, f"{value:.3f}", ha="center", va="center", fontsize=9)
        fig.colorbar(im, ax=ax).set_label("Balanced Accuracy")
        fig.tight_layout()
        w.save(plt, fig, "Figure_05_LOPO_heatmap")

    summary = read("metric_summary.csv")

    # Figures 6-7 — calibration drift
    if summary is not None:
        _calibration(plt, w, summary, "log_loss_value", "Log Loss", "Figure_06_calibration_log_loss")
        _calibration(plt, w, summary, "brier_score", "Brier Score", "Figure_07_calibration_brier_score")

    # Figure 8 — failure signature heatmap
    sig = read("failure_signature_matrix.csv")
    if sig is not None:
        normalized = "mean_normalized_response" in sig.columns
        matrix = _metric_by_failure(sig, "mean_normalized_response" if normalized else "mean_effect_z")
        fig, ax = plt.subplots(figsize=(13, 6.5))
        im = ax.imshow(matrix.values, aspect="auto", **({"vmin": -1, "vmax": 1} if normalized else {}))
        _heatmap_axes(ax, matrix, METRIC_LABELS, FAILURE_LABELS)
        ax.set_xlabel("Evaluation metric")
        ax.set_ylabel("Failure mode")
        w.title(ax, "Multi-metric diagnostic signatures of classifier failure modes")
        fig.colorbar(im, ax=ax).set_label(
            "Normalized endpoint response" if normalized else "Standardized response"
        )
        fig.tight_layout()
        w.save(plt, fig, "Figure_08_failure_signature_heatmap")

    # Figure 9 — cross-validated failure-mode confusion matrix
    cm = read("failure_mode_confusion_matrix.csv", index_col=0)
    if cm is not None:
        cm = cm.apply(pd.to_numeric, errors="coerce").fillna(0)
        raw = cm.to_numpy(dtype=float)
        row_sums = raw.sum(axis=1, keepdims=True)
        norm = np.divide(raw, row_sums, out=np.zeros_like(raw), where=row_sums != 0)
        fig, ax = plt.subplots(figsize=(9, 8))
        im = ax.imshow(norm, aspect="auto", vmin=0, vmax=1)
        _heatmap_axes(ax, cm, FAILURE_LABELS, FAILURE_LABELS)
        for i in range(norm.shape[0]):
            for j in range(norm.shape[1]):
                ax.text(j, i, f"{norm[i, j]:.2f}", ha="center", va="center", fontsize=8)
        ax.set_xlabel("Predicted failure mode")
        ax.set_ylabel("True failure mode")
        w.title(ax, "Cross-validated distinguishability of classifier failure modes")
        fig.colorbar(im, ax=ax).set_label("Row-normalized proportion")
        fig.tight_layout()
        w.save(plt, fig, "Figure_09_failure_mode_confusion_matrix")

    # Figure 10 — Spearman sensitivity heatmap (rho averaged over prevalence)
    sens = read("metric_sensitivity.csv")
    if sens is not None:
        avg = sens.groupby(["path_label", "metric"], as_index=False).agg(spearman_rho=("spearman_rho", "mean"))
        matrix = _metric_by_failure(avg, "spearman_rho")
        fig, ax = plt.subplots(figsize=(13, 6.5))
        im = ax.imshow(matrix.values, aspect="auto", vmin=-1, vmax=1)
        _heatmap_axes(ax, matrix, METRIC_LABELS, FAILURE_LABELS)
        ax.set_xlabel("Metric")
        ax.set_ylabel("Failure mode")
        w.title(ax, "Monotonic sensitivity of evaluation metrics to failure severity")
        fig.colorbar(im, ax=ax).set_label("Mean Spearman correlation with severity λ")
        fig.tight_layout()
        w.save(plt, fig, "Figure_10_metric_sensitivity_heatmap")

    # Figures 11-12 — trajectories at prevalence 0.30
    if summary is not None:
        _trajectories(
            plt, w, summary, "collapse:positive",
            ["precision", "recall", "specificity_derived", "f1_score", "balanced_accuracy", "mcc"],
            "Metric disagreement during progressive positive-class collapse",
            "Positive-collapse severity λ", "Figure_11_positive_collapse_trajectories",
        )
        _trajectories(
            plt, w, summary, "score_inversion:none",
            ["accuracy", "balanced_accuracy", "mcc", "roc_auc", "pr_auc"],
            "Transition from discrimination to systematic score inversion",
            "Score-inversion severity λ", "Figure_12_score_inversion_trajectories", inversion=True,
        )

    return w.saved
